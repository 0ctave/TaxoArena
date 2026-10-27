"""LEAF-POWERED — the cancelled leaf-vs-anchor rubric comparison, properly powered (registered 2026-09-14).

  python tools/analysis/leaf_powered.py --schedule
  python tools/analysis/leaf_powered.py --judge [--pilot N] [--workers 8]
  python tools/analysis/leaf_powered.py --analyze

ANCHOR rubric (the deployed STACK-v2 configuration) versus the promoted tree's own induced LEAF rubric, on the
four anchors where per-anchor cell-context gains exceeded 6pp. Matches are drawn only where the two models
DISAGREE on their own predicted answers (the shipped matchFilter rule), which lifts the decidable rate so that
~270 matches per anchor buy the ~215 decidable pairs 80% power at 6pp needs. Nothing is induced: all 87 leaves
already carry a judgeRubric.
"""
import os, sys, time, random, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import prompt_v2

ANCHORS = ["Philosophy", "Business", "Biology", "Chemistry"]
PER_ANCHOR = 270
SINGLE = False   # --single-order: one call per match instead of two (registered amendment 2026-09-14)
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "leaf_powered.db")


def setup():
    snap = r512.snapshot_id("bareq512_s42"); nodes = r512.load_graph(snap)
    route = r512.primary_routing("bareq512_s42"); anchor_of = r512.anchor_fn(nodes)
    leaf_rub = {n["id"]: (n.get("judgeRubric") or "") for n in nodes.values() if not n.get("childIds")}
    leaf_lbl = {n["id"]: (n.get("label") or n["id"]) for n in nodes.values() if not n.get("childIds")}
    anch_rub = sj.anchor_rubrics()
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id='p2dca21ab5f4ef3ae'")}
    P = defaultdict(dict); K = defaultdict(dict)
    for q, m, p, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in p8.ARENA12: P[q][m] = (p or "").strip().upper()[:1]; K[q][m] = int(c or 0)
    return route, anchor_of, leaf_rub, leaf_lbl, anch_rub, pool, P, K


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS schedule (mid INTEGER PRIMARY KEY, anchor TEXT, leaf TEXT, qid INTEGER, model_a TEXT, model_b TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (mid INTEGER, arm TEXT, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL, PRIMARY KEY (mid, arm))")
    con.commit(); return con


def build():
    route, anchor_of, leaf_rub, leaf_lbl, anch_rub, pool, P, K = setup()
    con = open_cache()
    if con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]:
        print("schedule exists: %d" % con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]); return
    models = [m for m in p8.ARENA12]
    pairs = [(models[i], models[j]) for i in range(len(models)) for j in range(i + 1, len(models))]
    rng = random.Random(42); rows = []; mid = 50_000_000
    for anc in ANCHORS:
        cand = []
        for q in sorted(pool):
            if q not in route or anchor_of(route[q]) != anc or q not in P: continue
            for a, b in pairs:
                pa, pb = P[q].get(a, ""), P[q].get(b, "")
                if pa and pb and pa != pb: cand.append((q, a, b))
        rng.shuffle(cand)
        take = cand[:PER_ANCHOR]
        for q, a, b in take:
            rows.append((mid, anc, route[q], q, a, b)); mid += 1
        dec = sum(1 for q, a, b in take if K[q][a] != K[q][b])
        print("  %-12s %5d disagreeing candidates -> %3d scheduled | key-decidable among them %3d (%.0f%%)"
              % (anc, len(cand), len(take), dec, 100 * dec / max(1, len(take))))
    con.executemany("INSERT INTO schedule VALUES (?,?,?,?,?,?)", rows); con.commit()
    print("scheduled %d matches over %d anchors (x2 arms = %d matches, %d calls)" % (len(rows), len(ANCHORS), 2 * len(rows), 4 * len(rows)))


def judge(pilot, workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    route, anchor_of, leaf_rub, leaf_lbl, anch_rub, pool, P, K = setup()
    rref.set_reference("grok-reasoning"); refs = rref.references()
    con = open_cache()
    sched = con.execute("SELECT mid, anchor, leaf, qid, model_a, model_b FROM schedule ORDER BY mid").fetchall()
    if pilot: sched = sched[:pilot]
    done = {(m, a) for m, a in con.execute("SELECT mid, arm FROM verdicts")}
    jobs = [(s, arm) for s in sched for arm in ("anchor", "leaf") if (s[0], arm) not in done]
    evals = rj.load_eval_rows([s[3] for s in sched], {s[4] for s in sched} | {s[5] for s in sched})
    print("LEAF-POWERED [%s]: %d matches x 2 arms | jobs %d (%d calls) | workers %d" % ("single order" if SINGLE else "dual order", len(sched), len(jobs), (1 if SINGLE else 2) * len(jobs), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(job):
        (mid, anc, leaf, qid, a, b), arm = job
        ra, rb, ref = evals.get((qid, a)), evals.get((qid, b)), refs.get(qid)
        if ra is None or rb is None or ref is None: return None
        if arm == "anchor":
            sp, rub = anch_rub[anc]
        else:
            sp, rub = anch_rub[anc][0], leaf_rub.get(leaf, "")
            if not rub.strip(): return None
        system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rub) + "\n\n" + rj.SCHEMA_INSTRUCTION
        q = rref.with_reference(ra[0], ref)
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        raw1 = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(q, ta, tb))[0])
        v1, _ = rj.parse_judge(raw1)
        if SINGLE:
            w = {"Model A": a, "Model B": b}.get(v1, "TIE")
            return (mid, arm, w, 0, int(v1 not in ("Model A", "Model B", "TIE")), raw1, "", time.time())
        raw2 = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(q, tb, ta))[0])
        v2, _ = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, arm, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, j): j for j in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s: %s" % (futs[f][0][0], str(e)[:100]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                con.execute("INSERT OR REPLACE INTO verdicts VALUES (?,?,?,?,?,?,?,?)", row); con.commit()
            ok += 1
            if i % 200 == 0 or i == len(jobs): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(jobs), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    route, anchor_of, leaf_rub, leaf_lbl, anch_rub, pool, P, K = setup()
    con = open_cache()
    sch = {m: (anc, leaf, q, a, b) for m, anc, leaf, q, a, b in con.execute("SELECT mid, anchor, leaf, qid, model_a, model_b FROM schedule")}
    V = defaultdict(dict)
    for m, arm, w, fl, inv in con.execute("SELECT mid, arm, winner, flip, invalid FROM verdicts"):
        if not inv: V[m][arm] = w
    rows = []
    for m, d in V.items():
        if "anchor" not in d or "leaf" not in d: continue
        anc, leaf, q, a, b = sch[m]
        if K[q][a] == K[q][b]: continue
        win = a if K[q][a] else b
        rows.append((anc, d["anchor"] == win, d["leaf"] == win))
    n = len(rows)
    pa = sum(1 for r in rows if r[1]) / n; pl = sum(1 for r in rows if r[2]) / n
    b = sum(1 for r in rows if r[1] and not r[2]); c = sum(1 for r in rows if r[2] and not r[1])
    print("=== LEAF-POWERED: leaf rubric vs anchor rubric, %d key-decidable paired matches ===" % n)
    print("  POOLED   anchor %.3f | leaf %.3f (%+.3f) | %d:%d | McNemar p=%.4f -> PRIMARY %s"
          % (pa, pl, pl - pa, b, c, p8.mcn(b, c), "PASS" if (pl - pa >= 0.02 and p8.mcn(b, c) < 0.05) else "FAIL"))
    per = []
    for anc in ANCHORS:
        s = [r for r in rows if r[0] == anc]
        if not s: continue
        x = sum(1 for r in s if r[1]) / len(s); y = sum(1 for r in s if r[2]) / len(s)
        bb = sum(1 for r in s if r[1] and not r[2]); cc = sum(1 for r in s if r[2] and not r[1])
        per.append((anc, len(s), x, y, y - x, bb, cc, p8.mcn(bb, cc)))
    per.sort(key=lambda t: t[7])
    print("  per anchor (Holm across %d):" % len(per))
    for i, (anc, k, x, y, d, bb, cc, p) in enumerate(per):
        thr = 0.05 / (len(per) - i)
        print("    %-12s n=%3d | anchor %.3f leaf %.3f (%+.3f) | %d:%d | p=%.4f vs Holm %.4f -> %s"
              % (anc, k, x, y, d, bb, cc, p, thr, "significant" if p < thr else "not significant"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--schedule", action="store_true"); ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=8); ap.add_argument("--single-order", action="store_true")
    a = ap.parse_args(); SINGLE = a.single_order
    if a.schedule: build()
    elif a.judge: build(); judge(a.pilot, a.workers)
    elif a.analyze: analyze()
