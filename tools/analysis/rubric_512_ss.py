"""RUBRIC-512-SS — same-session GENERIC control for RUBRIC-512 (docs/incident_reserved_pool_mismatch_2026-09-09.md,
registered before any call).

Re-judges the production GENERIC arm (rubric_value_contrast.build_generic_system_prompt, byte-identical
templates) on the same 1,980 R3 matches with Mistral-Large-3, today, and compares RUBRIC-512's CELL verdicts
(experiment_results/rubric_512/bareq512_s42.db, judged 2026-09-09 21:35–22:30) against this FRESH generic
instead of the earlier session's cache. Also reports fresh-vs-cached generic (the session drift itself).
REGISTERED: the rubric-value claim is publishable as significant iff cell > fresh generic at p < 0.05
(paired McNemar, key-decidable, ties wrong). Secondary: discursive gain > quantitative gain.
Prediction: +1pp, p > 0.1.

  python tools/analysis/rubric_512_ss.py [--pilot N] [--workers N]
  python tools/analysis/rubric_512_ss.py --analyze
"""
import os, sys, time, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_value_contrast as rc
import rubric_p8 as p8
import rubric_512 as r512

OUT_DIR = os.path.join(ROOT, "experiment_results", "rubric_512")
CACHE = os.path.join(OUT_DIR, "generic_ss.db")


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, qid INTEGER, model_a TEXT, model_b TEXT, "
                "vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)")
    con.commit()
    return con


def run(pilot, workers):
    p8.load_env()
    sample = rc.matches_for("grok")
    if pilot: sample = sample[:pilot]
    cache = open_cache()
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    todo = [m for m in sample if m[0] not in done]
    evals = rj.load_eval_rows([int(m[1]) for m in todo], {m[2] for m in todo} | {m[3] for m in todo})
    generic = rc.build_generic_system_prompt()
    print("RUBRIC-512-SS: R3 sample %d | jobs %d (%d calls) | workers %d" % (len(sample), len(todo), 2 * len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(m):
        mid, qid, a, b, *_ = m; qid = int(qid)
        ra, rb = evals.get((qid, a)), evals.get((qid, b))
        if ra is None or rb is None: return None
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        raw1 = p8.call(generic, rj.build_user_prompt(ra[0], ta, tb)); raw2 = p8.call(generic, rj.build_user_prompt(ra[0], tb, ta))
        v1, _ = rj.parse_judge(raw1); v2, _ = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, qid, a, b, v1, v2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m): m for m in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except Exception as e:
                err += 1; print("  ERROR match %s: %s" % (futs[f][0], str(e)[:120]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 12), row); cache.commit()
            ok += 1
            if i % 50 == 0 or i == len(todo):
                print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    fresh = {r[0]: r[1] for r in open_cache().execute("SELECT match_id, winner FROM verdicts WHERE invalid=0")}
    cached = r512.generic_cached()
    cell_db = sqlite3.connect("file:%s?mode=ro" % os.path.join(OUT_DIR, "bareq512_s42.db"), uri=True)
    cell = {r[0]: (r[1], r[2]) for r in cell_db.execute("SELECT match_id, winner, anchor FROM verdicts WHERE invalid=0")}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    meta = {m[0]: (int(m[1]), m[2], m[3]) for m in rc.matches_for("grok")}
    rows = {}
    for mid, (q, a, b) in meta.items():
        if mid not in fresh or mid not in cell or mid not in cached: continue
        ca, cb = G.get((q, a)), G.get((q, b))
        if ca is None or cb is None or ca == cb: continue
        d = a if ca else b
        rows[mid] = {"cell": cell[mid][0] == d, "fresh": fresh[mid] == d, "cached": cached[mid] == d, "anchor": cell[mid][1]}
    def stats(keys, x, y):
        n = len(keys); px = sum(rows[k][x] for k in keys) / max(1, n); py = sum(rows[k][y] for k in keys) / max(1, n)
        b = sum(rows[k][x] and not rows[k][y] for k in keys); c = sum(rows[k][y] and not rows[k][x] for k in keys)
        return n, px, py, b, c, p8.mcn(b, c)
    keys = list(rows)
    print("=== RUBRIC-512-SS: %d key-decidable matches with cell, fresh-generic and cached-generic verdicts ===" % len(keys))
    for lab, x, y in (("CELL vs FRESH generic (REGISTERED PRIMARY)", "cell", "fresh"), ("CELL vs CACHED generic (RUBRIC-512, same rows)", "cell", "cached"),
                      ("FRESH vs CACHED generic (session drift)", "fresh", "cached")):
        n, px, py, b, c, p = stats(keys, x, y)
        tag = "  -> %s" % ("PASS" if (px > py and p < 0.05) else "FAIL") if "PRIMARY" in lab else ""
        print("  %-48s %s %.3f vs %s %.3f (%+.3f) | %d:%d | p=%.4f%s" % (lab, x, px, y, py, px - py, b, c, p, tag))
    disc = [k for k in keys if rows[k]["anchor"] in p8.DISCURSIVE]; quant = [k for k in keys if rows[k]["anchor"] not in p8.DISCURSIVE]
    gd = stats(disc, "cell", "fresh"); gq = stats(quant, "cell", "fresh")
    print("  discursive   n=%4d cell %.3f vs fresh %.3f (%+.3f) %d:%d p=%.4f" % (gd[0], gd[1], gd[2], gd[1] - gd[2], gd[3], gd[4], gd[5]))
    print("  quantitative n=%4d cell %.3f vs fresh %.3f (%+.3f) %d:%d p=%.4f" % (gq[0], gq[1], gq[2], gq[1] - gq[2], gq[3], gq[4], gq[5]))
    print("  SECONDARY (discursive gain > quantitative gain): %s" % ("PASS" if (gd[1] - gd[2]) > (gq[1] - gq[2]) else "FAIL"))
    by = defaultdict(list)
    for k in keys: by[rows[k]["anchor"]].append(k)
    for anc in sorted(by, key=lambda a: -(stats(by[a], "cell", "fresh")[1] - stats(by[a], "cell", "fresh")[2])):
        n, px, py, b, c, p = stats(by[anc], "cell", "fresh")
        print("     %-18s n=%3d  gain %+.3f  (%d:%d)" % (anc[:18], n, px - py, b, c))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze: analyze()
    else: run(a.pilot, a.workers); analyze()
