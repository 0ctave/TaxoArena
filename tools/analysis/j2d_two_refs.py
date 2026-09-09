"""J2-D — two references on the DISAGREE stratum (docs/judge_v2_program.md; registered before any call).

Questions of the R3 sample where Mistral's S1 answer != the reasoning model's S1 answer. The
question carries BOTH candidate answers, labelled as disagreeing (reasoning model's first);
v1 prompt, frozen-tree cell system prompt (as J2-R), Mistral-Large-3, dual order. Comparator:
J2-R's cached verdict on the same match (reasoning reference only).
REGISTERED: key-decidable accuracy vs J2-R's on the stratum (0.774), paired McNemar p < 0.05,
either direction. Prediction: null or slightly negative.

  python tools/analysis/j2d_two_refs.py [--pilot N] [--workers N]
  python tools/analysis/j2d_two_refs.py --analyze
"""
import os, sys, json, time, sqlite3, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reference as rref
import rubric_p8 as p8

CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_mistral_two_refs.db")
J2R = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_mistral_reference_grok_reasoning.db")


def two_refs():
    rref.set_reference("mistral"); m = rref.references()
    rref.set_reference("grok-reasoning"); g = rref.references()
    return {q: (g[q], m[q]) for q in g if q in m and g[q][0] != m[q][0]}


def with_two(query, pair):
    (gl, gt, _), (ml, mt, _) = pair
    return (query + "\n\n[Two independent reference solutions — they DISAGREE; at most one of them is right, possibly neither]\n"
            "Reference 1: (%s) %s\nReference 2: (%s) %s" % (gl, gt, ml, mt))


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER, "
                "ref1 TEXT, ref1_correct INTEGER, ref2 TEXT, ref2_correct INTEGER, vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)")
    con.commit()
    return con


def run(pilot, workers):
    p8.load_env()
    nodes = rj.load_nodes(); refs = two_refs()
    sample = [m for m in rj.sample_matches() if int(m[1]) in refs]
    if pilot: sample = sample[:pilot]
    cache = open_cache()
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    todo = [m for m in sample if m[0] not in done]
    evals = rj.load_eval_rows([int(m[1]) for m in todo], {m[2] for m in todo} | {m[3] for m in todo})
    print("J2-D: disagree questions %d | matches %d | jobs %d (%d calls) | workers %d" % (len(refs), len(sample), len(todo), 2 * len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(m):
        mid, qid, a, b, nid, *_ = m; qid = int(qid)
        ra, rb = evals.get((qid, a)), evals.get((qid, b))
        if ra is None or rb is None: return None
        pair = refs[qid]; q = with_two(ra[0], pair)
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        system = rj.build_system_prompt(nodes[nid])
        raw1 = p8.call(system, rj.build_user_prompt(q, ta, tb)); raw2 = p8.call(system, rj.build_user_prompt(q, tb, ta))
        v1, _ = rj.parse_judge(raw1); v2, _ = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, a, b, nid, qid, pair[0][0], int(pair[0][2]), pair[1][0], int(pair[1][2]), v1, v2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m): m for m in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except Exception as e:
                err += 1; print("  ERROR match %s: %s" % (futs[f][0], str(e)[:120]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 17), row); cache.commit()
            ok += 1
            if i % 50 == 0 or i == len(todo):
                print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    two = {r[0]: r for r in open_cache().execute("SELECT match_id, model_a, model_b, qid, winner, invalid, ref1_correct, ref2_correct FROM verdicts")}
    j2 = {r[0]: r for r in sqlite3.connect("file:%s?mode=ro" % J2R, uri=True).execute("SELECT match_id, ref_winner, invalid, mistral_winner FROM verdicts")}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    rows = []
    for mid, r in two.items():
        if mid not in j2 or r[5] or j2[mid][2]: continue
        _, a, b, q, w2, _, r1c, r2c = r
        ca, cb = G.get((q, a)), G.get((q, b))
        if ca is None or cb is None or ca == cb: continue
        d = a if ca else b
        rows.append((w2 == d, j2[mid][1] == d, j2[mid][3] == d, bool(r1c), bool(r2c)))
    n = len(rows); p2 = sum(r[0] for r in rows) / max(1, n); p1 = sum(r[1] for r in rows) / max(1, n); p0 = sum(r[2] for r in rows) / max(1, n)
    b = sum(r[0] and not r[1] for r in rows); c = sum(r[1] and not r[0] for r in rows); p = p8.mcn(b, c)
    print("=== J2-D: two disagreeing references vs reasoning reference only (J2-R), Mistral, disagree stratum, %d key-decidable ===" % n)
    print("  two refs %.3f vs one ref %.3f (%+.3f) vs no ref %.3f | %d:%d | p=%.4f -> %s" % (p2, p1, p2 - p1, p0, b, c, p, "SIGNIFICANT" if p < 0.05 else "NULL"))
    for lab, f in (("reasoning ref correct", lambda r: r[3]), ("Mistral ref correct", lambda r: r[4]), ("neither correct", lambda r: not r[3] and not r[4])):
        s = [r for r in rows if f(r)]; k = len(s)
        if k: print("  %-22s n=%3d two %.3f vs one %.3f vs none %.3f" % (lab, k, sum(r[0] for r in s) / k, sum(r[1] for r in s) / k, sum(r[2] for r in s) / k))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze: analyze()
    else: run(a.pilot, a.workers); analyze()
