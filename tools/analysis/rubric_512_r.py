"""RUBRIC-512-R — cell-rubric value for the REASONING judge (docs/judge_improvement_proposals.md,
"Launch records 2026-09-09 (late)"; registered before any call).

As RUBRIC-512 (R3's 1,980 matches; CELL = bareq512_s42 leaf rubric via routeReserved; GENERIC =
production GENERIC_JUDGE text; byte-identical v1 templates) with judge = grok-4-1-fast-reasoning
and BOTH arms judged fresh in the same session, interleaved per match (cell then generic).
REGISTERED PRIMARY: cell > generic on key-decidable, paired McNemar p < 0.05. SECONDARY: gain >
Mistral's RUBRIC-512 gain (+1.8pp). Prediction: +0 to +2pp n.s.; secondary FAILS.

  python tools/analysis/rubric_512_r.py [--pilot N] [--workers N]
  python tools/analysis/rubric_512_r.py --analyze
"""
import os, sys, time, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rubric_value_contrast as rc
import rubric_p8 as p8
import rubric_512 as r512

TREE = "bareq512_s42"
OUT_DIR = os.path.join(ROOT, "experiment_results", "rubric_512")
CACHES = {arm: os.path.join(OUT_DIR, "grok_reasoning_%s.db" % arm) for arm in ("cell", "generic")}


def open_cache(arm):
    con = sqlite3.connect(CACHES[arm])
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, qid INTEGER, model_a TEXT, model_b TEXT, leaf TEXT, anchor TEXT, "
                "vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, invalid INTEGER, tokens INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)")
    con.commit()
    return con


def run(pilot, workers):
    rr.PROVIDER = "azure"; rr.load_env()
    snap, nodes, route, anchor, sample = r512.setup(TREE)
    if pilot: sample = sample[:pilot]
    caches = {arm: open_cache(arm) for arm in CACHES}
    done = {arm: {r[0] for r in caches[arm].execute("SELECT match_id FROM verdicts")} for arm in CACHES}
    todo = [(m, arm) for m in sample for arm in ("cell", "generic") if m[0] not in done[arm]]
    evals = rj.load_eval_rows([int(m[1]) for m, _ in todo], {m[2] for m, _ in todo} | {m[3] for m, _ in todo})
    generic = rc.build_generic_system_prompt()
    print("RUBRIC-512-R (%s): jobs %d (%d calls) | workers %d" % (rr.JUDGE_MODEL, len(todo), 2 * len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(m, arm):
        mid, qid, a, b, *_ = m; qid = int(qid)
        ra, rb = evals.get((qid, a)), evals.get((qid, b))
        if ra is None or rb is None: return None
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        leaf = route[qid]; system = rj.build_system_prompt(nodes[leaf]) if arm == "cell" else generic
        raw1, _, t1, _ = rr.call_judge(system, rj.build_user_prompt(ra[0], ta, tb)); raw2, _, t2, _ = rr.call_judge(system, rj.build_user_prompt(ra[0], tb, ta))
        raw1, raw2 = rr.strip_think(raw1), rr.strip_think(raw2)
        v1, _ = rj.parse_judge(raw1); v2, _ = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return arm, (mid, qid, a, b, leaf, anchor(leaf), v1, v2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), (t1 or 0) + (t2 or 0), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m, arm): (m, arm) for m, arm in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                res = f.result()
            except Exception as e:
                err += 1; print("  ERROR match %s/%s: %s" % (futs[f][0][0], futs[f][1], str(e)[:120]), flush=True); continue
            if res is None: skip += 1; continue
            arm, row = res
            with lock:
                caches[arm].execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 15), row); caches[arm].commit()
            ok += 1
            if i % 50 == 0 or i == len(todo):
                print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    arms = {arm: {r[0]: (r[1], r[2]) for r in open_cache(arm).execute("SELECT match_id, winner, anchor FROM verdicts WHERE invalid=0")} for arm in CACHES}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    meta = {m[0]: (int(m[1]), m[2], m[3]) for m in rc.matches_for("grok")}
    rows = {}
    for mid, (q, a, b) in meta.items():
        if mid not in arms["cell"] or mid not in arms["generic"]: continue
        ca, cb = G.get((q, a)), G.get((q, b))
        if ca is None or cb is None or ca == cb: continue
        d = a if ca else b
        rows[mid] = (arms["cell"][mid][0] == d, arms["generic"][mid][0] == d, arms["cell"][mid][1], a in rj.TOP_CLUSTER and b in rj.TOP_CLUSTER)
    def stats(keys):
        n = len(keys); pc = sum(rows[k][0] for k in keys) / max(1, n); pg = sum(rows[k][1] for k in keys) / max(1, n)
        b = sum(rows[k][0] and not rows[k][1] for k in keys); c = sum(rows[k][1] and not rows[k][0] for k in keys)
        return n, pc, pg, b, c, p8.mcn(b, c)
    keys = list(rows); n, pc, pg, b, c, p = stats(keys)
    print("=== RUBRIC-512-R (%s): clean-tree leaf rubric vs generic, BOTH fresh, %d key-decidable paired matches ===" % (rr.JUDGE_MODEL, n))
    print("  ALL           cell %.3f vs generic %.3f (%+.3f) | %d:%d | p=%.4f -> PRIMARY %s" % (pc, pg, pc - pg, b, c, p, "PASS" if (pc > pg and p < 0.05) else "FAIL"))
    print("  SECONDARY (gain > Mistral's +0.018): %s" % ("PASS" if (pc - pg) > 0.018 else "FAIL"))
    n, pc, pg, b, c, p = stats([k for k in keys if rows[k][3]])
    print("  TOP-CLUSTER   cell %.3f vs generic %.3f (%+.3f) | %d:%d | p=%.4f" % (pc, pg, pc - pg, b, c, p))
    for lab, ks in (("discursive", [k for k in keys if rows[k][2] in p8.DISCURSIVE]), ("quantitative", [k for k in keys if rows[k][2] not in p8.DISCURSIVE])):
        n, pc, pg, b, c, p = stats(ks)
        print("  %-13s n=%4d cell %.3f vs generic %.3f (%+.3f) %d:%d p=%.4f" % (lab, n, pc, pg, pc - pg, b, c, p))
    by = defaultdict(list)
    for k in keys: by[rows[k][2]].append(k)
    for anc in sorted(by, key=lambda a: -(stats(by[a])[1] - stats(by[a])[2])):
        n, pc, pg, b, c, p = stats(by[anc])
        print("     %-18s n=%3d  gain %+.3f  (%d:%d)" % (anc[:18], n, pc - pg, b, c))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze: analyze()
    else: run(a.pilot, a.workers); analyze()
