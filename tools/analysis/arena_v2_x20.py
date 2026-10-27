"""ARENA-V2-X20 — eight more models on the ARENA-V2 board (registered 2026-09-10 20:45, docs/judge_v2_program.md).

  python tools/analysis/arena_v2_x20.py --schedule            # build the deterministic schedule (zero calls)
  python tools/analysis/arena_v2_x20.py --judge [--pilot N] [--workers N]
  python tools/analysis/arena_v2_x20.py --analyze [--nperm 1000]

Schedule mirrors x12 MAIN: per-leaf share as x12's, questions from x12's own reserved questions of that leaf,
pairs uniform over the 124 NEW pairs (8 new x 12 old + 28 new-new), 100 matches per new pair. Judge = STACK-v2
exactly as ARENA-V2; the 12-model verdicts come from ARENA-V2's cache.
"""
import os, sys, math, time, random, sqlite3, argparse, threading
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reference as rref
import rubric_p8 as p8
import judge_free_tests as jf
import stack_judge as sj

NEW = ["arx_3", "claude-3-5-sonnet-20241022", "gpt-4o-mini", "claude-3-5-haiku-20241022", "Qwen1.5-110B",
       "Mixtral-8x7B-Instruct-v0.1", "Qwen1.5-14B-Chat", "gemma-7b"]
OLD = sorted(set(p8.ARENA12))
TOP6 = ["gemini-3.1-pro_5-shots", "arx_0314", "iask_pro", "arx_3", "claude-3-5-sonnet-20241022", "gpt-4o-2024-08-06"]
PER_PAIR = 100
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2_promptv2_x20.db")
X12ALL = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2_promptv2_x12all.db")


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS schedule (match_id INTEGER PRIMARY KEY, qid INTEGER, model_a TEXT, model_b TEXT, node_id TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER, anchor TEXT, "
                "ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)")
    con.commit(); return con


def build_schedule():
    con = open_cache()
    if con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]:
        print("schedule exists: %d matches" % con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]); return
    x12 = sj.all_x12_matches()   # id, qid, a, b, nid, winner, is_tie
    by_leaf_q = defaultdict(set); per_leaf = Counter()
    for r in x12:
        by_leaf_q[r[4]].add(int(r[1])); per_leaf[r[4]] += 1
    pairs = [(a, b) for a in NEW for b in OLD] + [(NEW[i], NEW[j]) for i in range(len(NEW)) for j in range(i + 1, len(NEW))]
    total = PER_PAIR * len(pairs)
    n_x12 = sum(per_leaf.values())
    rng = random.Random(42)
    # per-leaf share as x12's; pairs dealt round-robin from a shuffled deck so every pair gets exactly PER_PAIR
    deck = [p for p in pairs for _ in range(PER_PAIR)]; rng.shuffle(deck)
    leaves = sorted(per_leaf); quota = {l: int(round(total * per_leaf[l] / n_x12)) for l in leaves}
    diff = total - sum(quota.values()); quota[leaves[0]] += diff
    rows = []; k = 0; mid = 10_000_000
    for l in leaves:
        qs = sorted(by_leaf_q[l])
        for _ in range(quota[l]):
            a, b = deck[k]; k += 1
            if rng.random() < 0.5: a, b = b, a
            rows.append((mid, qs[rng.randrange(len(qs))], a, b, l)); mid += 1
    con.executemany("INSERT INTO schedule VALUES (?,?,?,?,?)", rows); con.commit()
    pc = Counter(tuple(sorted((r[2], r[3]))) for r in rows)
    print("schedule: %d matches | %d leaves | %d new pairs (per pair min/max %d/%d) | %d distinct questions" % (len(rows), len(leaves), len(pc), min(pc.values()), max(pc.values()), len({r[1] for r in rows})))


def judge(pilot, workers):
    sj.PROMPT = "v2"
    p8.load_env(); rref.set_reference("grok-reasoning"); refs = rref.references()
    rubrics = sj.anchor_rubrics(); anchors = sj.routed_anchor()
    cache = open_cache()
    sched = cache.execute("SELECT match_id, qid, model_a, model_b, node_id FROM schedule ORDER BY match_id").fetchall()
    if pilot: sched = sched[:pilot]
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    todo = [m for m in sched if m[0] not in done]
    evals = rj.load_eval_rows([int(m[1]) for m in todo], {m[2] for m in todo} | {m[3] for m in todo})
    print("X20: schedule %d | jobs %d (%d calls) | workers %d" % (len(sched), len(todo), 2 * len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(m):
        mid, qid, a, b, nid = m; qid = int(qid)
        ra, rb, ref, anc = evals.get((qid, a)), evals.get((qid, b)), refs.get(qid), anchors.get(qid)
        if ra is None or rb is None or anc is None: return None
        q = rref.with_reference(ra[0], ref) if ref is not None else ra[0]
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        system = sj.system_for(anc, rubrics)
        raw1 = p8.call(system, rj.build_user_prompt(q, ta, tb)); raw2 = p8.call(system, rj.build_user_prompt(q, tb, ta))
        v1, c1 = rj.parse_judge(raw1); v2, c2 = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, a, b, nid, qid, anc, ref[0] if ref else "", int(ref[2]) if ref else -1, v1, v2, c1, c2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m): m for m in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR match %s: %s" % (futs[f][0], str(e)[:120]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 18), row); cache.commit()
            ok += 1
            if i % 200 == 0 or i == len(todo): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def kendall(order1, order2):
    pos1 = {m: i for i, m in enumerate(order1)}; pos2 = {m: i for i, m in enumerate(order2)}
    ms = [m for m in order1 if m in pos2]; c = d = 0
    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            s = (pos1[ms[i]] - pos1[ms[j]]) * (pos2[ms[i]] - pos2[ms[j]]); c += s > 0; d += s < 0
    return (c - d) / max(1, c + d)


def analyze(nperm):
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    x12 = {r[0]: r for r in sj.all_x12_matches()}
    old_v = [r for r in sj.open_cache().execute("SELECT match_id, model_a, model_b, qid, winner, invalid FROM verdicts") if not r[5] and r[0] in x12]
    new_v = [r for r in open_cache().execute("SELECT match_id, model_a, model_b, qid, winner, invalid, node_id FROM verdicts") if not r[5]]
    nodes = rj.load_nodes(); parent = {c: n["id"] for n in nodes.values() for c in n.get("childIds", [])}

    def anchor_of(nid):
        n = nodes[nid]
        while n["depth"] > 1: n = nodes[parent[n["id"]]]
        return n["label"]
    rows = [dict(q=int(r[3]), a=r[1], b=r[2], w=r[4], g=anchor_of(x12[r[0]][4]), new=False) for r in old_v] + \
           [dict(q=int(r[3]), a=r[1], b=r[2], w=r[4], g=anchor_of(r[6]), new=True) for r in new_v]
    models = OLD + NEW
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    acc, _ = jf.gt_and_lengths(set(models))
    th20 = jf.board_from(jf.current_votes(rows), models); rho = jf.rho(th20, acc, models)
    th12 = jf.board_from(jf.current_votes([r for r in rows if not r["new"]]), OLD)
    o20_old = sorted(OLD, key=lambda m: -th20[m]); o12 = sorted(OLD, key=lambda m: -th12[m]); tau = kendall(o12, o20_old)
    print("=== ARENA-V2-X20: 20-model board from %d verdicts (%d ARENA-V2 + %d new) ===" % (len(rows), len(old_v), len(new_v)))
    for m in sorted(models, key=lambda m: -th20[m]): print("  %-30s theta %+.3f | key acc %.3f %s" % (m, th20[m], acc[m], "NEW" if m in NEW else ""))
    newp = [r for r in rows if r["new"]]
    dec = [r for r in newp if G.get((r["q"], r["a"])) is not None and G.get((r["q"], r["b"])) is not None and G[(r["q"], r["a"])] != G[(r["q"], r["b"])]]
    accd = sum(r["w"] == (r["a"] if G[(r["q"], r["a"])] else r["b"]) for r in dec) / max(1, len(dec))
    gt6 = sorted(TOP6, key=lambda m: -acc[m])
    th6 = jf.board_from(jf.current_votes([r for r in rows if r["a"] in TOP6 and r["b"] in TOP6]), TOP6)
    o6 = sorted(TOP6, key=lambda m: -th6[m]); pos = {m: i for i, m in enumerate(o6)}
    viol6 = sum(1 for i in range(6) for j in range(i + 1, 6) if pos[gt6[i]] > pos[gt6[j]])
    # anchor LRT with question-level permutation (as analyze_arena)
    def ll(rows_, th):
        s = 0.0
        for r in rows_:
            pr = 1 / (1 + math.exp(-max(-30, min(30, th[r["a"]] - th[r["b"]])))); pr = min(max(pr, 1e-9), 1 - 1e-9)
            s += 0.5 * (math.log(pr) + math.log(1 - pr)) if r["w"] == "TIE" else (math.log(pr) if r["w"] == r["a"] else math.log(1 - pr))
        return s

    def lrt(rows_):
        th0 = jf.board_from(jf.current_votes(rows_), models); l0 = ll(rows_, th0); l1 = 0.0; by = defaultdict(list)
        for r in rows_: by[r["g"]].append(r)
        for g, sub in by.items(): l1 += ll(sub, th0) if len(sub) < 50 else ll(sub, jf.board_from(jf.current_votes(sub), models))
        return 2 * (l1 - l0)
    obs = lrt(rows); rng = random.Random(42); qs = sorted({r["q"] for r in rows}); qg = {r["q"]: r["g"] for r in rows}; labels = [qg[q] for q in qs]; null = []
    for _ in range(nperm):
        rng.shuffle(labels); m = dict(zip(qs, labels))
        for r in rows: r["g"] = m[r["q"]]
        null.append(lrt(rows))
    p = (sum(1 for v in null if v >= obs) + 1) / (nperm + 1)
    print("\n  per new pair (judge right on key-decidable):")
    pc = defaultdict(lambda: [0, 0])
    for r in dec:
        k = tuple(sorted((r["a"], r["b"]))); pc[k][1] += 1; pc[k][0] += r["w"] == (r["a"] if G[(r["q"], r["a"])] else r["b"])
    for k in sorted(pc, key=lambda k: pc[k][0] / max(1, pc[k][1]))[:10]: print("    %-30s vs %-30s %3d/%3d = %.2f" % (k[0], k[1], pc[k][0], pc[k][1], pc[k][0] / max(1, pc[k][1])))
    checks = [("(1) rho >= 0.95: %.4f" % rho, rho >= 0.95), ("(2) 12-model order kept in the 20-model board, tau >= 0.90: %.3f" % tau, tau >= 0.90),
              ("(3) key-decidable accuracy on new pairs >= 0.85: %.3f (n=%d)" % (accd, len(dec)), accd >= 0.85),
              ("(4) top-6 violations <= 3: %d [%s vs key %s]" % (viol6, " > ".join(o6), " > ".join(gt6)), viol6 <= 3),
              ("(5) anchor LRT p_perm < 0.05: LRT %.2f null p95 %.2f p=%.3f" % (obs, float(np.percentile(null, 95)), p), p < 0.05)]
    for lab, ok in checks: print("  %-90s %s" % (lab, "OK" if ok else "FAIL"))
    print("  ARENA-V2-X20 REGISTERED: %s" % ("PASS" if all(c[1] for c in checks) else "FAIL"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--schedule", action="store_true"); ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=12); ap.add_argument("--nperm", type=int, default=1000)
    a = ap.parse_args()
    if a.schedule: build_schedule()
    elif a.judge: build_schedule(); judge(a.pilot, a.workers)
    elif a.analyze: analyze(a.nperm)
