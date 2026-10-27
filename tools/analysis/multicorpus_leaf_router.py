"""Stage 2b — does the GROWN taxonomy route better than the designed (source, domain) strata? (zero calls)

  python tools/analysis/multicorpus_leaf_router.py [--run experiment_results/multicorpus/mc6_s42/seed_42] [--min-leaf 20]

Same split rule as multicorpus_router.py (per-(source, domain), ratio 0.30, seed 42). Reserved queries are routed to
the nearest leaf centroid of the union tree (MRL slice = the tree's vmfMu width); per-leaf best model from the
TRAIN side (leaves with < min-leaf train questions fall back to their domain's best). REGISTERED READOUT (written
before running): routed-by-leaf minus routed-by-domain on the reserved side with a query-level bootstrap SE;
the taxonomy adds routing value iff the difference exceeds 2 SE. Prediction: within +-1pp of domain routing
(LEAF-POWER on MMLU-Pro found leaf profiles under-supported; the union has 147 leaves for 15k train questions).
"""
import os, sys, random, sqlite3, argparse
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import free_tests_f4_f7 as ff


CLEAN = False


def main(run, min_leaf, db, ratio, seed, boots):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    Q = {q: (s, d, t) for q, s, d, t in con.execute("SELECT question_id, source, domain, text FROM corpus_questions")}
    models = [m for (m,) in con.execute("SELECT DISTINCT model_name FROM eval_results ORDER BY model_name")]
    G = defaultdict(dict)
    for q, m, c in con.execute("SELECT question_id, model_name, is_correct FROM eval_results"): G[q][m] = int(c)
    qs = sorted(q for q in Q if len(G[q]) == len(models))
    leaves = ff.tree_leaves(os.path.relpath(run, ROOT)); dim = len(leaves[0][1])
    vec = ff.embed_matrix(ff.EMB_DB, [Q[q][2] for q in qs], dim)
    qq = [q for q in qs if Q[q][2] in vec]
    X = np.stack([vec[Q[q][2]] for q in qq]); M = np.stack([mu / (np.linalg.norm(mu) or 1) for _, mu, _ in leaves])
    idx = np.argmax(X @ M.T, axis=1); leaf = {q: leaves[i][0] for q, i in zip(qq, idx)}; anc = {q: leaves[i][2] for q, i in zip(qq, idx)}
    print("union tree %s: %d leaves (dim %d) | %d of %d questions embedded and routed" % (os.path.basename(os.path.dirname(run)), len(leaves), dim, len(qq), len(qs)))
    rng = random.Random(seed); strata = defaultdict(list)
    for q in qq: strata[(Q[q][0], Q[q][1])].append(q)
    train, test = [], []
    for k, v in sorted(strata.items()):
        v = v[:]; rng.shuffle(v); n = int(round(len(v) * ratio)); test += v[:n]; train += v[n:]
    if CLEAN:
        # The split above is re-derived here and coincides with the TREE's held-out pool only at chance, so
        # by default ~70% of the reserved side was training data for the tree that routes it (ledger audit
        # 2026-09-14). Restrict the reserved side to the union pool of record, by explicit id (no active pool).
        con2 = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
        import pool_guard; pid = pool_guard.assert_frozen_pool(con2, pool_guard.UNION_POOL)
        pool = {q for (q,) in con2.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (pid,))}
        before = len(test); test = [q for q in test if q in pool]
        print("CLEAN: reserved side pinned to %s, %d of %d kept (%.1f%%)" % (pid, len(test), before, 100.0*len(test)/max(1,before)))
    best = lambda sel: max(models, key=lambda m: sum(G[q][m] for q in sel)) if sel else None
    gb = best(train); sb = {s: best([q for q in train if Q[q][0] == s]) for s in {Q[q][0] for q in train}}
    db_ = {k: best([q for q in train if (Q[q][0], Q[q][1]) == k]) for k in strata}
    tl = defaultdict(list)
    for q in train: tl[leaf[q]].append(q)
    lb = {l: best(v) for l, v in tl.items() if len(v) >= min_leaf}
    print("split: train %d / reserved %d | leaves with >= %d train questions: %d of %d | anchors routed: %d" % (len(train), len(test), min_leaf, len(lb), len(leaves), len(set(anc.values()))))
    def canon(a): return a.replace("MMLU_PRO_LB/", "MMLU_PRO/")
    print("routed anchor == designed (source/domain): %.3f | routed source == true source: %.3f" % (
        sum(1 for q in test if canon(anc[q]) == "%s/%s" % (Q[q][0], Q[q][1])) / len(test),
        sum(1 for q in test if canon(anc[q]).split("/")[0] == Q[q][0]) / len(test)))
    cross = Counter((Q[q][0], canon(anc[q]).split("/")[0]) for q in test if canon(anc[q]).split("/")[0] != Q[q][0])
    print("cross-source routing (true -> routed, top 6): %s" % cross.most_common(6))

    def score(sel):
        n = len(sel)
        return (sum(G[q][gb] for q in sel) / n, sum(G[q][sb[Q[q][0]]] for q in sel) / n,
                sum(G[q][db_[(Q[q][0], Q[q][1])]] for q in sel) / n,
                sum(G[q][lb.get(leaf[q], db_[(Q[q][0], Q[q][1])])] for q in sel) / n,
                sum(max(G[q].values()) for q in sel) / n)
    o = score(test); bs = np.array([score([test[rng.randrange(len(test))] for _ in range(len(test))]) for _ in range(boots)])
    for nm, i in (("best single", 0), ("routed by source", 1), ("routed by source/domain", 2), ("routed by taxonomy leaf", 3), ("oracle", 4)):
        print("  %-26s %.3f ± %.3f" % (nm, o[i], bs[:, i].std(ddof=1)))
    d = o[3] - o[2]; se = np.std(bs[:, 3] - bs[:, 2], ddof=1)
    print("  leaf minus domain: %+.3f ± %.3f -> %s" % (d, se, "taxonomy ADDS routing value" if d > 2 * se else ("taxonomy LOSES vs domains" if d < -2 * se else "not resolved (within 2 SE)")))
    print("\nper source: domain-routed vs leaf-routed on the reserved side")
    for s in sorted(sb):
        sel = [q for q in test if Q[q][0] == s]; oo = score(sel)
        print("  %-12s n=%5d | by domain %.3f | by leaf %.3f (%+.3f) | leaves used %d" % (s, len(sel), oo[2], oo[3], oo[3] - oo[2], len({leaf[q] for q in sel})))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=os.path.join(ROOT, "experiment_results", "multicorpus", "mc6_s42", "seed_42"))
    ap.add_argument("--min-leaf", type=int, default=20); ap.add_argument("--db", default=os.path.join(ROOT, "multicorpus_cache_v1.db"))
    ap.add_argument("--clean", action="store_true"); ap.add_argument("--ratio", type=float, default=0.3); ap.add_argument("--seed", type=int, default=42); ap.add_argument("--boots", type=int, default=200)
    a = ap.parse_args(); CLEAN = a.clean; main(a.run, a.min_leaf, a.db, a.ratio, a.seed, a.boots)
