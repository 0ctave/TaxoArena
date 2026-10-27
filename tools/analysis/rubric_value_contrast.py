"""Rubric-value contrast: do cell-specific judge rubrics beat a generic judge?

REGISTERED DESIGN (frozen at commit time, before any generic-arm verdict exists).

WHY (2026-09-06). The thesis's C5 arm found the rubric changes decisiveness, not
ranking, and its committed-accuracy comparison was confounded: arms with different
abstention rates commit on different question sets, so "committed accuracy" embeds a
selection effect, attributed in the thesis to the arm bundle. This experiment removes
every confound the paired harness can remove: SAME matches, SAME questions, SAME
traces, SAME judge model, SAME two-order protocol — the ONLY difference between arms
is the system prompt's rubric content (the cell's judgePrompt/judgeRubric vs the
production GENERIC_JUDGE branch text, both rendered through the identical template).

ARMS (2 x 2, paired on match slots):
  Mistral-Large-3 x cell rubric   = the x12 run itself (ratings_x12.db, 9,144 matches)
  Mistral-Large-3 x generic       = NEW, judged here on ALL 9,144 x12 matches
  grok-4-1-fast   x cell rubric   = the R3 re-judge cache (1,980 stratified matches)
  grok-4-1-fast   x generic       = NEW, judged here on the same 1,980 matches

REGISTERED PRIMARY (adjudicating; Mistral pair, full 9,144 matches): on key-decidable
matches (exactly one of the pair's models answered correctly), an arm's verdict is
CORRECT iff it names the GT-correct model — TIE and INVALID count as not correct, so
decisiveness is part of quality and no committed-only selection occurs. Test: exact
McNemar (two-sided binomial on discordant slots). The thesis claim "specific rubrics
make a better judge" is SUPPORTED iff cell-rubric correct-rate > generic AND
p_mcnemar < 0.05. The opposite significant direction, or a null, is reported as-is.

REGISTERED SECONDARIES (descriptive): (a) tie/decisiveness rates per arm (clean
re-test of the thesis 13.0% vs 10.9% finding); (b) committed-only agreement, for
continuity with the thesis metric, labeled as selection-prone; (c) the 12-model BT
ordering under each Mistral arm (full 9,144 slots): Spearman and adjacent swaps —
the thesis "rubric changes decisiveness, not ranking" claim at 12 models; (d) the
grok pair as a cross-family replication of the primary's direction.

DURABILITY: verdicts land in rubric_contrast.db immediately, keyed
(match_id, judge, rubric); reruns skip completed work, arms are restart-safe.

Usage:
  python tools/analysis/rubric_value_contrast.py --arm mistral --pilot 12
  python tools/analysis/rubric_value_contrast.py --arm mistral      # full 9,144
  python tools/analysis/rubric_value_contrast.py --arm grok         # R3 sample
  python tools/analysis/rubric_value_contrast.py --analyze
"""
import argparse
import json
import math
import os
import sqlite3
import sys
import threading
import time
import urllib.request
import urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rejudge_grok as rj  # template extraction, trace prep, parsing, combination

ROOT = rj.ROOT
X12_DB = rj.X12_DB
R3_DB = rj.CACHE_DB
CACHE_DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rubric_contrast.db")

# The production GENERIC_JUDGE branch text, verbatim from
# TaxonomyArenaService.buildJudgeSystemPrompt(useGeneric = true).
GENERIC_SYSTEM = ("You are an expert academic evaluator. Analyze the two responses "
                  "and grade them based on overall correctness and reasoning quality.")
GENERIC_RUBRIC = "Grade the response based on domain correctness, precision, and logical reasoning."

JUDGES = {
    # concurrency chosen per endpoint: Mistral francecentral throttles near 3 req/s
    # (the arena's measured limit); grok tolerated 12 workers with zero 429s in R3.
    "mistral": {"model": "Mistral-Large-3", "key_env": "AZURE_AI_API_KEY", "conc": 10},
    "grok": {"model": "grok-4-1-fast-non-reasoning", "key_env": "AZURE_GROK_API_KEY", "conc": 12},
}


def build_generic_system_prompt():
    base = (rj.SYSTEM_TEMPLATE
            .replace("$systemPrompt", GENERIC_SYSTEM)
            .replace("$rubric", GENERIC_RUBRIC))
    return base + "\n\n" + rj.SCHEMA_INSTRUCTION


def load_env():
    kv = {}
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        line = line.strip().replace("\r", "")
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            kv[k] = v
    return kv


def call_judge(endpoint, key, model, system, user, retries=6):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "max_tokens": rj.MAX_TOKENS,
    }).encode("utf-8")
    for attempt in range(retries):
        req = urllib.request.Request(endpoint, data=body, method="POST", headers={
            "Content-Type": "application/json", "api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                payload = json.loads(r.read().decode("utf-8"))
            return payload["choices"][0]["message"]["content"] or ""
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(min(2 ** attempt * 2, 45))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < retries - 1:
                time.sleep(min(2 ** attempt * 2, 45))
                continue
            raise
    raise RuntimeError("unreachable")


def open_cache():
    con = sqlite3.connect(CACHE_DB)
    con.execute("""CREATE TABLE IF NOT EXISTS verdicts (
        match_id INTEGER, judge TEXT, rubric TEXT,
        model_a TEXT, model_b TEXT, node_id TEXT,
        vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL,
        winner TEXT, flip INTEGER, invalid INTEGER, ts REAL,
        PRIMARY KEY (match_id, judge, rubric))""")
    con.commit()
    return con


def matches_for(arm):
    con = sqlite3.connect("file:%s?mode=ro" % X12_DB, uri=True)
    rows = con.execute(
        "SELECT id, eval_question_id, model_a, model_b, node_id, winner, is_tie "
        "FROM match_history WHERE condition='MAIN' AND snapshot_id=? ORDER BY id",
        (rj.SNAP_MAIN,)).fetchall()
    con.close()
    if arm == "mistral":
        return rows
    # grok arm: exactly the R3 sample (paired with the existing grok cell-rubric cache)
    r3 = sqlite3.connect("file:%s?mode=ro" % R3_DB, uri=True)
    ids = {r[0] for r in r3.execute("SELECT match_id FROM verdicts")}
    r3.close()
    return [r for r in rows if r[0] in ids]


def judge_one(match, judge, endpoint, key, nodes, evals, generic_system):
    mid, qid, ma, mb, nid, _, _ = match
    qid = int(qid)
    ra = evals.get((qid, ma))
    rb = evals.get((qid, mb))
    if ra is None or rb is None:
        return None
    trace_a = rj.robust_trace(ra[2], ra[3], ra[1])
    trace_b = rj.robust_trace(rb[2], rb[3], rb[1])
    model = JUDGES[judge]["model"]
    raw1 = call_judge(endpoint, key, model, generic_system, rj.build_user_prompt(ra[0], trace_a, trace_b))
    raw2 = call_judge(endpoint, key, model, generic_system, rj.build_user_prompt(ra[0], trace_b, trace_a))
    v1, c1 = rj.parse_judge(raw1)
    v2_raw, c2 = rj.parse_judge(raw2)
    gw, flip, invalid = rj.combine_orders(v1, v2_raw)
    gw_name = {"Model A": ma, "Model B": mb}.get(gw, gw)
    return (mid, judge, "generic", ma, mb, nid, v1, v2_raw, c1, c2,
            gw_name, int(flip), int(invalid), time.time())


def run(arm, pilot=None):
    env = load_env()
    endpoint = env["AZURE_AI_ENDPOINT"].rstrip("/") + "/models/chat/completions?api-version=2024-05-01-preview"
    key = env[JUDGES[arm]["key_env"]]
    nodes = rj.load_nodes()
    generic_system = build_generic_system_prompt()
    sample = matches_for(arm)
    if pilot:
        sample = sample[:pilot]
    cache = open_cache()
    done = {r[0] for r in cache.execute(
        "SELECT match_id FROM verdicts WHERE judge=? AND rubric='generic'", (arm,))}
    todo = [m for m in sample if m[0] not in done]
    print("%s/generic: sample %d | cached %d | to judge %d (%d calls)"
          % (arm, len(sample), len(sample) - len(todo), len(todo), 2 * len(todo)))
    if not todo:
        return
    evals = rj.load_eval_rows([int(m[1]) for m in todo], {m[2] for m in todo} | {m[3] for m in todo})
    lock = threading.Lock()
    n_ok = n_skip = n_err = 0
    with ThreadPoolExecutor(max_workers=JUDGES[arm]["conc"]) as ex:
        futs = {ex.submit(judge_one, m, arm, endpoint, key, nodes, evals, generic_system): m
                for m in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                row = fut.result()
            except Exception as e:
                n_err += 1
                print("  ERROR match %s: %s" % (futs[fut][0], e))
                continue
            if row is None:
                n_skip += 1
                continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 14), row)
                cache.commit()
            n_ok += 1
            if i % 100 == 0 or i == len(todo):
                print("  %d/%d (ok %d, skipped %d, errors %d)" % (i, len(todo), n_ok, n_skip, n_err))
    print("done: ok %d, skipped %d, errors %d" % (n_ok, n_skip, n_err))


# ── Analysis ───────────────────────────────────────────────────────────────────

def gt_correct(question_ids, models):
    con = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    out = {}
    q = sorted(set(question_ids))
    for i in range(0, len(q), 500):
        chunk = q[i:i + 500]
        marks = ",".join("?" * len(chunk))
        for qid, m, ok in con.execute(
                "SELECT question_id, model_name, is_correct FROM eval_results "
                "WHERE question_id IN (%s)" % marks, chunk):
            if m in models:
                out[(qid, m)] = bool(ok)
    con.close()
    return out


def mcnemar_p(b, c):
    """Exact two-sided binomial test on discordant counts."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = 0.0
    for i in range(0, k + 1):
        tail += math.comb(n, i) * 0.5 ** n
    return min(1.0, 2.0 * tail)


def analyze():
    cache = open_cache()
    x12 = sqlite3.connect("file:%s?mode=ro" % X12_DB, uri=True)
    cell_m = {r[0]: ("TIE" if r[6] else r[5], r[1], r[2], r[3]) for r in x12.execute(
        "SELECT id, eval_question_id, model_a, model_b, node_id, winner, is_tie "
        "FROM match_history WHERE condition='MAIN' AND snapshot_id=?", (rj.SNAP_MAIN,))}
    x12.close()
    r3 = sqlite3.connect("file:%s?mode=ro" % R3_DB, uri=True)
    cell_g = {r[0]: r[1] for r in r3.execute(
        "SELECT match_id, grok_winner FROM verdicts WHERE grok_invalid=0")}
    r3.close()

    all_models = set()
    for _, (w, qid, ma, mb) in cell_m.items():
        all_models.update((ma, mb))
    gt = gt_correct([v[1] for v in cell_m.values()], all_models)

    def decidable_winner(qid, ma, mb):
        ca, cb = gt.get((int(qid), ma)), gt.get((int(qid), mb))
        if ca is None or cb is None or ca == cb:
            return None
        return ma if ca else mb

    for judge, cell_lookup in (("mistral", None), ("grok", cell_g)):
        gen = {r[0]: r[1] for r in cache.execute(
            "SELECT match_id, winner FROM verdicts WHERE judge=? AND rubric='generic' AND invalid=0",
            (judge,))}
        if not gen:
            print("[%s] no generic verdicts yet" % judge)
            continue
        both, b, c = 0, 0, 0     # b: cell correct & generic wrong; c: reverse
        cell_ok = gen_ok = 0
        cell_tie = gen_tie = 0
        n_dec = 0
        for mid, gw in gen.items():
            rec = cell_m.get(mid)
            if rec is None:
                continue
            cw = rec[0] if judge == "mistral" else cell_g.get(mid)
            if cw is None:
                continue
            qid, ma, mb = rec[1], rec[2], rec[3]
            both += 1
            if cw == "TIE":
                cell_tie += 1
            if gw == "TIE":
                gen_tie += 1
            dw = decidable_winner(qid, ma, mb)
            if dw is None:
                continue
            n_dec += 1
            cok = cw == dw
            gok = gw == dw
            cell_ok += cok
            gen_ok += gok
            if cok and not gok:
                b += 1
            if gok and not cok:
                c += 1
        p = mcnemar_p(b, c)
        print("=== %s: cell rubric vs generic (paired, %d matches, %d key-decidable) ===" % (judge, both, n_dec))
        print("  correct-verdict rate (ties count wrong): cell %.3f | generic %.3f | diff %+.3f"
              % (cell_ok / max(1, n_dec), gen_ok / max(1, n_dec), (cell_ok - gen_ok) / max(1, n_dec)))
        print("  discordant: cell-only-correct %d vs generic-only-correct %d | McNemar p = %.4f%s"
              % (b, c, p, "  <- REGISTERED PRIMARY" if judge == "mistral" else "  (robustness)"))
        print("  tie rate: cell %.3f | generic %.3f" % (cell_tie / both, gen_tie / both))

    # Secondary (c): full-board ordering under each Mistral arm.
    gen_m = {r[0]: r[1] for r in cache.execute(
        "SELECT match_id, winner FROM verdicts WHERE judge='mistral' AND rubric='generic' AND invalid=0")}
    if len(gen_m) > 1000:
        def fit(get_w):
            agg = defaultdict(lambda: [0.0, 0.0])
            ms = set()
            for mid, rec in cell_m.items():
                w = get_w(mid, rec)
                if w is None:
                    continue
                a, bb = min(rec[2], rec[3]), max(rec[2], rec[3])
                ms.update((a, bb))
                r = agg[(a, bb)]
                r[1] += 1
                if w == "TIE":
                    r[0] += 0.5
                elif w == a:
                    r[0] += 1.0
            models = sorted(ms)
            return rj.mm_fit({k: tuple(v) for k, v in agg.items()}, models), models
        th_cell, models = fit(lambda mid, rec: rec[0])
        th_gen, _ = fit(lambda mid, rec: gen_m.get(mid))
        rho = rj.spearman([th_cell[m] for m in models], [th_gen[m] for m in models])
        oc = sorted(models, key=lambda m: -th_cell[m])
        og = sorted(models, key=lambda m: -th_gen[m])
        print("=== Mistral 12-model ordering: cell vs generic rubric ===")
        print("  Spearman rho = %.3f | order identical: %s" % (rho, "YES" if oc == og else "no"))
        for m in oc:
            print("  %-30s cell %+7.3f   generic %+7.3f" % (m, th_cell[m], th_gen[m]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["mistral", "grok"])
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--analyze", action="store_true")
    args = ap.parse_args()
    if args.analyze:
        analyze()
    else:
        if not args.arm:
            ap.error("--arm required unless --analyze")
        run(args.arm, pilot=args.pilot)
