"""MC-E2E + MC-SEEDS — the DEPLOYED multi-corpus router (registered 2026-09-13, docs/multi_corpus_design.md).

  python tools/analysis/multicorpus_router_e2e.py [--seeds 42,137,2048] [--boots 200] [--min-leaf 20]

Stage 2 indexed the model policy by each question's TRUE (source, domain) — metadata a deployed router does not
have. Here the same policies are applied through the taxonomy's own prediction: stage 1c's flatLeaf rule, i.e. the
nearest centroid over ALL leaves of the six federated per-corpus trees (each leaf carries its "<SOURCE>/<domain>"
anchor). Arms, all learned on the train side of a per-(source, domain) 0.30 split and scored on the reserved side:

  best single | by TRUE source | by TRUE (source,domain)   <- oracle metadata (= stage 2)
              | by PRED source | by PRED (source,domain)   <- deployed
              | by PRED leaf (train also routed; < min-leaf train questions falls back to the predicted domain)
              | per-question oracle

REGISTERED: (1) the deployed router (PRED source/domain) beats best single by > 2 SE in all three seeds;
(2) metadata cost = oracle-cell gain - predicted-cell gain, per seed; (3) the deployed gain's across-seed spread
is smaller than its within-seed SE. Zero LLM calls.
"""
import os, sys, random, sqlite3, argparse
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import free_tests_f4_f7 as ff

MATHFIX = False
CLEANPOOL = None   # --clean: restrict the reserved side to the TREE's own held-out pool. The python split
                   # here is re-derived with random.Random(seed) and overlaps the tree's held-out pool only
                   # at chance (~30%), so by default ~70% of the questions scored below were TRAINING data
                   # for the taxonomy that routes them. Found by the ledger audit 2026-09-14.
UNION_DB = os.path.join(ROOT, "multicorpus_cache_v1.db")


def clean_pool():
    con = sqlite3.connect("file:%s?mode=ro" % UNION_DB, uri=True)
    import pool_guard; pid = pool_guard.assert_frozen_pool(con, pool_guard.UNION_POOL)   # the union pool of record, by id
    return pid, {q for (q,) in con.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (pid,))}
CORPORA = ["mmlu_pro_lb", "bbh", "math", "gpqa", "musr", "ifeval"]
ARMS = ["best single", "TRUE source", "TRUE source/domain", "PRED source", "PRED source/domain", "PRED leaf", "oracle"]


def load(db):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    Q = {q: (s, d, t) for q, s, d, t in con.execute("SELECT question_id, source, domain, text FROM corpus_questions")}
    models = [m for (m,) in con.execute("SELECT DISTINCT model_name FROM eval_results ORDER BY model_name")]
    G = defaultdict(dict)
    for q, m, c in con.execute("SELECT question_id, model_name, is_correct FROM eval_results"): G[q][m] = int(c)
    if MATHFIX:   # --mathfix: overlay the tolerant MATH extractor's corrected column (docs: MATH-FIX)
        n = 0
        for q, m, c in con.execute("SELECT question_id, model_name, is_correct FROM eval_results_mathfix"):
            if q in G and m in G[q] and G[q][m] != int(c): G[q][m] = int(c); n += 1
        print("MATH-FIX overlay: %d corrected (question, model) cells" % n)
    return Q, models, G


def federated_leaves():
    """(leaf_id, unit-norm centroid, source, domain) over the six per-corpus trees = stage 1c's flatLeaf leaf set."""
    out = []
    for c in CORPORA:
        for lid, mu, anchor in ff.tree_leaves(os.path.join("experiment_results", "multicorpus", "%s_s42" % c, "seed_42")):
            src, _, dom = anchor.partition("/")
            n = np.linalg.norm(mu)
            out.append(("%s:%s" % (c, lid), mu / (n or 1.0), src, dom))
    return out


def main(db, seeds, boots, ratio, min_leaf):
    Q, models, G = load(db)
    qs = sorted(q for q in Q if len(G[q]) == len(models))
    leaves = federated_leaves(); dim = len(leaves[0][1])
    vec = ff.embed_matrix(ff.EMB_DB, [Q[q][2] for q in qs], dim)
    qq = [q for q in qs if Q[q][2] in vec]
    X = np.stack([vec[Q[q][2]] for q in qq]); M = np.stack([l[1] for l in leaves])
    idx = np.argmax(X @ M.T, axis=1)
    pleaf = {q: leaves[i][0] for q, i in zip(qq, idx)}
    psrc = {q: leaves[i][2] for q, i in zip(qq, idx)}; pdom = {q: leaves[i][3] for q, i in zip(qq, idx)}
    # the DB writes MMLU-Pro rows under source MMLU_PRO; the leaderboard tree's anchors say MMLU_PRO_LB
    canon = lambda s: "MMLU_PRO" if s == "MMLU_PRO_LB" else s
    src_ok = sum(1 for q in qq if canon(psrc[q]) == Q[q][0]) / len(qq)
    dom_ok = sum(1 for q in qq if canon(psrc[q]) == Q[q][0] and pdom[q] == Q[q][1]) / len(qq)
    print("MC-E2E: %d questions routed over %d federated leaves (dim %d) | predicted source %.3f | predicted source+domain %.3f"
          % (len(qq), len(leaves), dim, src_ok, dom_ok))
    print("arms: %s\n" % " | ".join(ARMS))
    per_seed = {}
    for seed in seeds:
        rng = random.Random(seed); strata = defaultdict(list)
        for q in qq: strata[(Q[q][0], Q[q][1])].append(q)
        train, test = [], []
        for k, v in sorted(strata.items()):
            v = v[:]; rng.shuffle(v); n = int(round(len(v) * ratio)); test += v[:n]; train += v[n:]
        best = lambda sel: max(models, key=lambda m: sum(G[q][m] for q in sel)) if sel else None
        gb = best(train)
        t_src = {s: best([q for q in train if Q[q][0] == s]) for s in {Q[q][0] for q in train}}
        t_dom = {k: best([q for q in train if (Q[q][0], Q[q][1]) == k]) for k in strata}
        p_src = {s: best([q for q in train if canon(psrc[q]) == s]) for s in {canon(psrc[q]) for q in train}}
        pd_groups = defaultdict(list)
        for q in train: pd_groups[(canon(psrc[q]), pdom[q])].append(q)
        p_dom = {k: best(v) for k, v in pd_groups.items()}
        pl_groups = defaultdict(list)
        for q in train: pl_groups[pleaf[q]].append(q)
        p_leaf = {l: best(v) for l, v in pl_groups.items() if len(v) >= min_leaf}

        def pick(q, arm):
            if arm == 0: return gb
            if arm == 1: return t_src.get(Q[q][0], gb)
            if arm == 2: return t_dom.get((Q[q][0], Q[q][1]), gb)
            if arm == 3: return p_src.get(canon(psrc[q]), gb)
            if arm == 4: return p_dom.get((canon(psrc[q]), pdom[q]), p_src.get(canon(psrc[q]), gb))
            return p_leaf.get(pleaf[q], p_dom.get((canon(psrc[q]), pdom[q]), gb))

        def score(sel):
            n = len(sel)
            return tuple([sum(G[q][pick(q, a)] for q in sel) / n for a in range(6)] + [sum(max(G[q].values()) for q in sel) / n])
        if CLEANPOOL is not None:
            before = len(test); test = [q for q in test if q in CLEANPOOL]
            print("  CLEAN: reserved side restricted to the tree's held-out pool, %d of %d kept (%.1f%%)"
                  % (len(test), before, 100.0 * len(test) / max(1, before)))
        o = score(test); bs = np.array([score([test[rng.randrange(len(test))] for _ in range(len(test))]) for _ in range(boots)])
        dep = o[4] - o[0]; se_dep = np.std(bs[:, 4] - bs[:, 0], ddof=1)
        orc = o[2] - o[0]; se_orc = np.std(bs[:, 2] - bs[:, 0], ddof=1)
        per_seed[seed] = dict(o=o, se=bs.std(axis=0, ddof=1), dep=dep, se_dep=se_dep, orc=orc, se_orc=se_orc, n=len(test))
        print("seed %d (reserved n=%d)" % (seed, len(test)))
        for i, nm in enumerate(ARMS): print("  %-20s %.4f ± %.4f" % (nm, o[i], per_seed[seed]["se"][i]))
        print("  DEPLOYED gain (PRED source/domain - best single): %+.4f ± %.4f -> %s" % (dep, se_dep, "REAL" if dep > 2 * se_dep else "not resolved"))
        print("  oracle-metadata gain %+.4f ± %.4f | METADATA COST %+.4f\n" % (orc, se_orc, orc - dep))
    print("== MC-SEEDS ==")
    deps = [per_seed[s]["dep"] for s in seeds]; spread = max(deps) - min(deps); mse = float(np.mean([per_seed[s]["se_dep"] for s in seeds]))
    print("  deployed gain per seed: %s | mean %+.4f | across-seed spread %.4f vs mean within-seed SE %.4f -> %s"
          % (", ".join("%+.4f" % d for d in deps), float(np.mean(deps)), spread, mse, "SEED-STABLE" if spread < mse else "seed-sensitive"))
    print("  REGISTERED (1) deployed > best single by > 2 SE in all seeds: %s" % ("PASS" if all(per_seed[s]["dep"] > 2 * per_seed[s]["se_dep"] for s in seeds) else "FAIL"))
    print("  REGISTERED (3) spread < within-seed SE: %s" % ("PASS" if spread < mse else "FAIL"))
    print("  metadata cost per seed: %s" % ", ".join("%+.4f" % (per_seed[s]["orc"] - per_seed[s]["dep"]) for s in seeds))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.path.join(ROOT, "multicorpus_cache_v1.db")); ap.add_argument("--clean", action="store_true"); ap.add_argument("--seeds", default="42,137,2048")
    ap.add_argument("--boots", type=int, default=200); ap.add_argument("--ratio", type=float, default=0.3); ap.add_argument("--min-leaf", type=int, default=20); ap.add_argument("--mathfix", action="store_true")
    a = ap.parse_args(); MATHFIX = a.mathfix
    if a.clean:
        pid, CLEANPOOL = clean_pool()
        print("CLEAN mode: reserved side restricted to the tree's active held-out pool %s (%d questions)" % (pid, len(CLEANPOOL)))
    main(a.db, [int(s) for s in a.seeds.split(",")], a.boots, a.ratio, a.min_leaf)
