"""RUBRIC-512 — cell vs generic rubric on a CLEAN promoted tree (docs/incident_reserved_pool_mismatch_2026-09-09.md,
option D; registered before any call).

Tree: a promoted build made with reservedPoolFile = p2dca (default bareq512_s42), so none of the
arena questions were in construction or rubric induction. Matches: the R3 stratified sample
(1,980 matches). Arms: CELL = the leaf the question routes to in that tree (`routeReserved`
primary assignment), Mistral-Large-3, byte-identical v1 templates; GENERIC = the cached Mistral
generic verdict (rubric_contrast.db). REGISTERED PRIMARY: cell > generic, paired McNemar p < 0.05 on
key-decidable matches. SECONDARY: gain in discursive anchors > gain in quantitative anchors.
Prediction: +1 to +2pp, NOT significant.

  python tools/analysis/rubric_512.py [--tree bareq512_s42] [--pilot N] [--workers N]
  python tools/analysis/rubric_512.py --analyze
"""
import os, sys, re, csv, json, time, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_value_contrast as rc
import rubric_p8 as p8

PROMOTED = os.path.join(ROOT, "experiment_results", "promoted")
SNAP_DB = os.path.join(ROOT, "snapshots.db")
OUT_DIR = os.path.join(ROOT, "experiment_results", "rubric_512")


def snapshot_id(tree):
    log = os.path.join(PROMOTED, tree, "seed_42", "headless_run.log")
    ids = re.findall(r"Snapshot ID: (\S+)", open(log, encoding="utf-8", errors="replace").read())
    return ids[-1]


def load_graph(snap_id):
    c = sqlite3.connect("file:%s?mode=ro" % SNAP_DB, uri=True)
    g = json.loads(c.execute("SELECT graph FROM snapshots WHERE id=?", (snap_id,)).fetchone()[0])
    lst = g["nodes"]; lst = lst if isinstance(lst, list) else list(lst.values())
    return {n["id"]: n for n in lst}


def primary_routing(tree):
    best = {}
    with open(os.path.join(PROMOTED, "%s_reserved_leaf_assignments.csv" % tree), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            q = int(row["question_id"]); w = float(row["weight"].replace(",", "."))
            if q not in best or w > best[q][0]:
                best[q] = (w, row["leaf_id"], row["category"])
    return {q: v[1] for q, v in best.items()}


def anchor_fn(nodes):
    parent = {c: n["id"] for n in nodes.values() for c in n.get("childIds", [])}
    def anchor(nid):
        n = nodes[nid]
        while n["depth"] > 1: n = nodes[parent[n["id"]]]
        return n["label"]
    return anchor


def open_cache(tree):
    os.makedirs(OUT_DIR, exist_ok=True)
    con = sqlite3.connect(os.path.join(OUT_DIR, "%s.db" % tree))
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, qid INTEGER, model_a TEXT, model_b TEXT, leaf TEXT, anchor TEXT, "
                "vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)")
    con.commit()
    return con


def generic_cached():
    con = sqlite3.connect("file:%s?mode=ro" % rc.CACHE_DB, uri=True)
    return {r[0]: r[1] for r in con.execute("SELECT match_id, winner FROM verdicts WHERE judge='mistral' AND rubric='generic' AND invalid=0")}


def setup(tree):
    snap = snapshot_id(tree); nodes = load_graph(snap); route = primary_routing(tree); anchor = anchor_fn(nodes)
    sample = rc.matches_for("grok")  # exactly the R3 sample
    missing = [m for m in sample if int(m[1]) not in route]
    leaves = {route[int(m[1])] for m in sample if int(m[1]) in route}
    with_rubric = sum(1 for l in leaves if nodes[l].get("judgeRubric"))
    print("RUBRIC-512 tree %s snapshot %s: %d nodes | R3 sample %d | unrouted %d | routed leaves %d (%d with induced rubric)"
          % (tree, snap, len(nodes), len(sample), len(missing), len(leaves), with_rubric), flush=True)
    assert len(missing) <= 0.01 * len(sample), "routing CSV does not cover the R3 questions"
    assert with_rubric >= 0.9 * len(leaves), "promoted tree lacks induced rubrics (labeling/induction did not run)"
    return snap, nodes, route, anchor, [m for m in sample if int(m[1]) in route]


def run(tree, pilot, workers):
    p8.load_env()
    snap, nodes, route, anchor, sample = setup(tree)
    if pilot: sample = sample[:pilot]
    cache = open_cache(tree)
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    todo = [m for m in sample if m[0] not in done]
    evals = rj.load_eval_rows([int(m[1]) for m in todo], {m[2] for m in todo} | {m[3] for m in todo})
    print("  jobs %d (%d calls) | workers %d" % (len(todo), 2 * len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(m):
        mid, qid, a, b, *_ = m; qid = int(qid)
        ra, rb = evals.get((qid, a)), evals.get((qid, b))
        if ra is None or rb is None: return None
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        leaf = route[qid]; system = rj.build_system_prompt(nodes[leaf])
        raw1 = p8.call(system, rj.build_user_prompt(ra[0], ta, tb)); raw2 = p8.call(system, rj.build_user_prompt(ra[0], tb, ta))
        v1, _ = rj.parse_judge(raw1); v2, _ = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, qid, a, b, leaf, anchor(leaf), v1, v2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m): m for m in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except Exception as e:
                err += 1; print("  ERROR match %s: %s" % (futs[f][0], str(e)[:120]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 14), row); cache.commit()
            ok += 1
            if i % 50 == 0 or i == len(todo):
                print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze(tree):
    cache = open_cache(tree)
    gen = generic_cached()
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    rows = {}
    for mid, q, a, b, leaf, anc, w, inv in cache.execute("SELECT match_id, qid, model_a, model_b, leaf, anchor, winner, invalid FROM verdicts"):
        if inv or mid not in gen: continue
        ca, cb = G.get((q, a)), G.get((q, b))
        if ca is None or cb is None or ca == cb: continue
        d = a if ca else b
        rows[mid] = (w == d, gen[mid] == d, anc)
    def stats(keys):
        n = len(keys); oc = sum(rows[k][0] for k in keys); og = sum(rows[k][1] for k in keys)
        b = sum(rows[k][0] and not rows[k][1] for k in keys); c = sum(rows[k][1] and not rows[k][0] for k in keys)
        return n, oc / max(1, n), og / max(1, n), b, c, p8.mcn(b, c)
    n, pc, pg, b, c, p = stats(list(rows))
    print("=== RUBRIC-512 (%s): clean-tree leaf rubric vs cached generic, Mistral, R3 sample, %d key-decidable paired matches ===" % (tree, n))
    print("  correct-verdict rate: cell %.3f vs generic %.3f (%+.3f) | discordant %d:%d | McNemar p=%.4f -> %s (REGISTERED PRIMARY)"
          % (pc, pg, pc - pg, b, c, p, "PASS" if (pc > pg and p < 0.05) else "FAIL"))
    disc = [k for k in rows if rows[k][2] in p8.DISCURSIVE]; quant = [k for k in rows if rows[k][2] not in p8.DISCURSIVE]
    gains = {}
    for name, keys in (("discursive anchors", disc), ("quantitative anchors", quant)):
        n, pc, pg, b, c, p = stats(keys); gains[name] = pc - pg
        print("  %-21s n=%4d | cell %.3f vs generic %.3f (%+.3f) | %d:%d p=%.4f" % (name, n, pc, pg, pc - pg, b, c, p))
    print("  SECONDARY (discursive gain > quantitative gain): %s" % ("PASS" if gains["discursive anchors"] > gains["quantitative anchors"] else "FAIL"))
    by = defaultdict(list)
    for k in rows: by[rows[k][2]].append(k)
    for anc in sorted(by, key=lambda a: -(stats(by[a])[1] - stats(by[a])[2])):
        n, pc, pg, b, c, p = stats(by[anc])
        print("     %-18s n=%3d  gain %+.3f  (%d:%d)" % (anc[:18], n, pc - pg, b, c))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default="bareq512_s42")
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze:
        analyze(a.tree)
    else:
        run(a.tree, a.pilot, a.workers); analyze(a.tree)
