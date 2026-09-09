"""J2 — verify-then-judge with an INDEPENDENT synthetic reference (docs/judge_improvement_proposals.md
J2, criteria frozen at 7a4391a; launch record added before the first call).

Re-judges the R3 1,980 matches with Mistral-Large-3 and the v1 prompts, byte-identical except
that the question block carries the judge's OWN answer from S1 (judge_solve/mistral.db — a
separate call that never saw the traces), inserted as "[Reference solution — may be wrong]".
The no-reference arm is the x12 MAIN verdict on the same match (as in J1).

  python tools/analysis/rejudge_reference.py [--pilot N] [--workers N]
  python tools/analysis/rejudge_reference.py --analyze
"""
import os, sys, re, json, time, math, sqlite3, argparse, threading, urllib.request, urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj

MODEL = "Mistral-Large-3"
SOLVE_DB = os.path.join(ROOT, "experiment_results", "judge_solve", "mistral.db")
CACHE_DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_mistral_reference.db")
TOP4 = {"iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06", "arx_0314"}
ENDPOINT = KEY = None


def load_env():
    global ENDPOINT, KEY
    kv = {}
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        line = line.strip().replace("\r", "")
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            kv[k] = v
    ENDPOINT = kv["AZURE_AI_ENDPOINT"].rstrip("/") + "/models/chat/completions?api-version=2024-05-01-preview"
    KEY = kv["AZURE_AI_API_KEY"]


def call(system, user, retries=6):
    body = json.dumps({"model": MODEL, "max_tokens": rj.MAX_TOKENS,
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode("utf-8")
    for attempt in range(retries):
        req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={"Content-Type": "application/json", "api-key": KEY})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                p = json.loads(r.read().decode("utf-8"))
            return p["choices"][0]["message"].get("content") or ""
        except urllib.error.HTTPError as e:
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(min(2 ** attempt * 3, 60)); continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt < retries - 1:
                time.sleep(min(2 ** attempt * 3, 60)); continue
            raise
    raise RuntimeError("unreachable")


def references():
    """qid -> (letter, option text, reference_correct) from S1's Mistral answers."""
    s = sqlite3.connect("file:%s?mode=ro" % SOLVE_DB, uri=True)
    ans = {q: (a, c) for q, a, c in s.execute("SELECT question_id, answer, correct FROM answers WHERE answer != ''")}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    out = {}
    for q, (a, c) in ans.items():
        r = ev.execute("SELECT options_json FROM eval_results WHERE question_id=? AND model_name='gpt-4o-2024-08-06'", (q,)).fetchone()
        opts = json.loads(r[0]) if r and r[0] else []
        i = "ABCDEFGHIJ".find(a)
        text = opts[i] if 0 <= i < len(opts) else ""
        out[q] = (a, text, bool(c))
    return out


def with_reference(query, ref):
    letter, text, _ = ref
    return query + "\n\n[Reference solution — produced independently, may be wrong]\n(%s) %s" % (letter, text)


def open_cache():
    con = sqlite3.connect(CACHE_DB)
    con.execute("""CREATE TABLE IF NOT EXISTS verdicts (
        match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER,
        mistral_winner TEXT, ref_letter TEXT, ref_correct INTEGER,
        vote1 TEXT, vote2_raw TEXT, ref_winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)""")
    con.commit()
    return con


def judge_one(match, nodes, evals, refs):
    mid, qid, ma, mb, nid, winner, is_tie = match
    qid = int(qid)
    ra, rb, ref = evals.get((qid, ma)), evals.get((qid, mb)), refs.get(qid)
    if ra is None or rb is None or ref is None:
        return None
    q = with_reference(ra[0], ref)
    ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
    system = rj.build_system_prompt(nodes[nid])
    raw1 = call(system, rj.build_user_prompt(q, ta, tb))
    raw2 = call(system, rj.build_user_prompt(q, tb, ta))
    v1, _ = rj.parse_judge(raw1)
    v2, _ = rj.parse_judge(raw2)
    w, flip, inv = rj.combine_orders(v1, v2)
    w_name = {"Model A": ma, "Model B": mb}.get(w, w)
    return (mid, ma, mb, nid, qid, "TIE" if is_tie else winner, ref[0], int(ref[2]), v1, v2, w_name, int(flip), int(inv), raw1, raw2, time.time())


def run(pilot, workers):
    load_env()
    nodes = rj.load_nodes()
    sample = rj.sample_matches()
    if pilot:
        sample = sample[:pilot]
    refs = references()
    cache = open_cache()
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    todo = [m for m in sample if m[0] not in done]
    print("J2 sample %d | cached %d | to judge %d (%d calls) | references %d | workers %d"
          % (len(sample), len(sample) - len(todo), len(todo), 2 * len(todo), len(refs), workers), flush=True)
    if not todo:
        return
    evals = rj.load_eval_rows([int(m[1]) for m in todo], {m[2] for m in todo} | {m[3] for m in todo})
    lock = threading.Lock()
    ok = skip = err = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(judge_one, m, nodes, evals, refs): m for m in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except Exception as e:
                err += 1
                print("  ERROR match %s: %s" % (futs[f][0], str(e)[:140]), flush=True)
                continue
            if row is None:
                skip += 1; continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 16), row)
                cache.commit()
            ok += 1
            if i % 50 == 0 or i == len(todo):
                print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def mcnemar_p(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2.0 * sum(math.comb(n, i) * 0.5 ** n for i in range(k + 1)))


def analyze():
    cache = open_cache()
    rows = cache.execute("SELECT match_id, model_a, model_b, qid, mistral_winner, ref_winner, ref_correct, invalid, flip FROM verdicts").fetchall()
    if not rows:
        print("no verdicts"); return
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    valid = [r for r in rows if not r[7]]
    print("=== J2: Mistral + independent reference vs Mistral without (paired, %d judged, %d invalid, flips %.1f%%, ties ref %.1f%% vs base %.1f%%) ==="
          % (len(valid), len(rows) - len(valid), 100 * sum(r[8] for r in valid) / len(valid),
             100 * sum(r[5] == "TIE" for r in valid) / len(valid), 100 * sum(r[4] == "TIE" for r in valid) / len(valid)))

    def dec(r):
        ca, cb = G.get((r[3], r[1])), G.get((r[3], r[2]))
        return None if (ca is None or cb is None or ca == cb) else (r[1] if ca else r[2])
    for label, sub in (("ALL pairs", valid), ("TOP-CLUSTER pairs", [r for r in valid if r[1] in TOP4 and r[2] in TOP4]),
                       ("reference CORRECT", [r for r in valid if r[6]]), ("reference WRONG", [r for r in valid if not r[6]])):
        d = [(r, dec(r)) for r in sub]
        d = [(r, w) for r, w in d if w is not None]
        if not d:
            continue
        base = sum(r[4] == w for r, w in d); ref = sum(r[5] == w for r, w in d)
        b = sum(1 for r, w in d if r[5] == w and r[4] != w); c = sum(1 for r, w in d if r[4] == w and r[5] != w)
        print("  %-18s n_dec=%4d | with ref %.3f vs without %.3f (%+.3f) | discordant ref-only %d vs base-only %d | McNemar p=%.4f"
              % (label, len(d), ref / len(d), base / len(d), (ref - base) / len(d), b, c, mcnemar_p(b, c)))
    # registered: gain > 0 at p < 0.05 on all decidable AND the reference-wrong stratum loses less than the reference-correct stratum gains
    allr = [(r, dec(r)) for r in valid]; allr = [(r, w) for r, w in allr if w is not None]
    b = sum(1 for r, w in allr if r[5] == w and r[4] != w); c = sum(1 for r, w in allr if r[4] == w and r[5] != w)
    def gain(sub):
        d = [(r, dec(r)) for r in sub]; d = [(r, w) for r, w in d if w is not None]
        return (sum(r[5] == w for r, w in d) - sum(r[4] == w for r, w in d)) / max(1, len(d)), len(d)
    gc, nc = gain([r for r in valid if r[6]]); gw, nw = gain([r for r in valid if not r[6]])
    net = (gc * nc + gw * nw) / max(1, nc + nw)
    primary = b > c and mcnemar_p(b, c) < 0.05 and net > 0
    print("  REGISTERED J2 PRIMARY (gain > 0 at p<0.05 on all decidable; net of reference-correct gain and reference-wrong loss > 0): %s  [ref-correct %+.3f (n=%d), ref-wrong %+.3f (n=%d), net %+.3f]"
          % ("PASS" if primary else "FAIL", gc, nc, gw, nw, net))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze:
        analyze()
    else:
        run(a.pilot, a.workers)
        analyze()
