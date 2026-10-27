"""ROUTER-REGRET-MMLU + ORACLE-BOARD (registered 2026-09-11 01:30, docs/judge_v2_program.md; zero calls).

  python tools/analysis/router_regret.py

ROUTER-REGRET: key-oracle profiles on the TRAIN side of the promoted tree (nearest-centroid routing, bareq512_s42),
policy evaluated on the RESERVED side: routed-by-leaf, routed-by-anchor, best single model, per-question oracle.
ORACLE-BOARD: the x12 schedule re-scored with the key as verdict -> the ceiling board.
"""
import os, sys, random, sqlite3
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import free_tests_f4_f7 as ff
import rubric_p8 as p8
import rejudge_grok as rj
import judge_free_tests as jf
import stack_judge as sj

RUN_DIR = "experiment_results/promoted/bareq512_s42/seed_42"


def main():
    models, G, cat, text, qs = ff.keyed_questions()
    leaves = ff.tree_leaves(RUN_DIR); dim = len(leaves[0][1])
    vec = ff.embed_matrix(ff.EMB_DB, list(text.values()), dim)
    qq = [q for q in qs if text[q] in vec]
    Q = np.stack([vec[text[q]] for q in qq]); M = np.stack([mu / (np.linalg.norm(mu) or 1) for _, mu, _ in leaves])
    idx = np.argmax(Q @ M.T, axis=1)
    leaf = {q: leaves[i][0] for q, i in zip(qq, idx)}; anc = {q: leaves[i][2] for q, i in zip(qq, idx)}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id='p2dca21ab5f4ef3ae'")}
    train = [q for q in qq if q not in pool]; test = [q for q in qq if q in pool]
    print("ROUTER-REGRET-MMLU: %d keyed questions routed (train %d / reserved %d), %d leaves, %d anchors" % (len(qq), len(train), len(test), len(leaves), len(set(anc.values()))))
    rng = random.Random(42)

    def policy_eval(roster, tag):
        by_leaf = defaultdict(list); by_anc = defaultdict(list)
        for q in train: by_leaf[leaf[q]].append(q); by_anc[anc[q]].append(q)
        best_leaf = {l: max(roster, key=lambda m: sum(G[m][q] for q in v)) for l, v in by_leaf.items()}
        best_anc = {a: max(roster, key=lambda m: sum(G[m][q] for q in v)) for a, v in by_anc.items()}
        best_single = max(roster, key=lambda m: sum(G[m][q] for q in train))

        def score(qs_):
            r_leaf = sum(G[best_leaf.get(leaf[q], best_single)][q] for q in qs_) / len(qs_)
            r_anc = sum(G[best_anc.get(anc[q], best_single)][q] for q in qs_) / len(qs_)
            single = sum(G[best_single][q] for q in qs_) / len(qs_)
            oracle = sum(max(G[m][q] for m in roster) for q in qs_) / len(qs_)
            return r_leaf, r_anc, single, oracle
        obs = score(test); boots = [score([test[rng.randrange(len(test))] for _ in range(len(test))]) for _ in range(200)]
        se = np.std(np.array(boots), axis=0, ddof=1)
        print("  %-18s best single %-28s %.3f | routed by anchor %.3f (gain %+.3f ± %.3f) | routed by leaf %.3f (gain %+.3f ± %.3f) | oracle %.3f"
              % (tag, best_single, obs[2], obs[1], obs[1] - obs[2], np.sqrt(se[1] ** 2 + se[2] ** 2), obs[0], obs[0] - obs[2], np.sqrt(se[0] ** 2 + se[2] ** 2), obs[3]))
        print("     anchors where the best model is not %s: %s" % (best_single, sorted(a for a, m in best_anc.items() if m != best_single)))
    policy_eval([m for m in p8.ARENA12 if m in G], "12-model roster")
    policy_eval(models, "%d-model roster" % len(models))

    # ORACLE-BOARD
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    x12 = sj.all_x12_matches()
    Gk = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    rows = []
    for r in x12:
        q, a, b = int(r[1]), r[2], r[3]; ca, cb = Gk.get((q, a)), Gk.get((q, b))
        if ca is None or cb is None: continue
        rows.append(dict(a=a, b=b, w=("TIE" if ca == cb else (a if ca else b))))
    ms = sorted({r["a"] for r in rows} | {r["b"] for r in rows}); acc, _ = jf.gt_and_lengths(set(ms)); gt = sorted(sj.TOP4, key=lambda m: -acc[m])
    th = jf.board_from(jf.current_votes(rows), ms); th4 = jf.board_from(jf.current_votes([r for r in rows if r["a"] in sj.TOP4 and r["b"] in sj.TOP4]), sj.TOP4)
    o, pv, _ = jf.violations(th4, gt)
    print("\nORACLE-BOARD (key as verdict on the x12 schedule, %d matches): rho %.4f | top-4 %s (%d violations; key %s)" % (len(rows), jf.rho(th, acc, ms), " > ".join(o), pv, " > ".join(gt)))
    print("  for comparison: x12 v1 rho 0.951 / 2 violations; ARENA-V2 (STACK-v2) 0.972 / 1")


if __name__ == "__main__":
    main()
