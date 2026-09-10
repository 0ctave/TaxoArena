"""LEAF-SHRINK — does partial pooling rescue the leaf profile? (zero calls; follows LEAF-POWER)

Same synthetic arena as leaf_profile_power.py (clean bareq512_s42 tree, 12 arena models, 50/50 split
per leaf, ORACLE and NOISY judges, V verdicts per (leaf, model)). Estimator under test: the leaf
profile as the ANCHOR profile plus a shrunken deviation — theta_leaf = theta_anchor + lambda *
(theta_leaf_free - theta_anchor), lambda in {0, 0.25, 0.5, 0.75, 1} (0 = anchor only, 1 = LEAF-POWER's
separately fitted leaf). Scored on the held-out questions exactly as LEAF-POWER.
REGISTERED (2026-09-10, before running): partial pooling RESCUES the leaf profile iff some lambda in
(0, 1) beats lambda = 0 on held-out log-loss in >= 4/5 seeds at V = 54 (R2's budget) for the NOISY
judge; reported for all V. Prediction: a small lambda (0.25) wins at V >= 120 with the oracle and
nowhere at V = 54 with the noisy judge — the leaf deviation is real but under-determined at R2's budget.

  python tools/analysis/leaf_profile_shrink.py [--seeds 5]
"""
import os, sys, random, argparse
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import leaf_profile_evidence as lpe
import leaf_profile_power as lpp

LAMBDAS = [0.0, 0.25, 0.5, 0.75, 1.0]
BUDGETS = [54, 120, 400]


def main(seeds):
    models_all, G, qs, leaf, anc = lpe.assign_leaves()
    models = [m for m in lpp.ARENA12 if m in G]
    by_leaf = defaultdict(list)
    for q in qs: by_leaf[leaf[q]].append(q)
    leaves = {l: v for l, v in by_leaf.items() if len(v) >= 60}
    anchor_of = {l: anc[v[0]] for l, v in leaves.items()}
    print("LEAF-SHRINK: %d leaves, %d models, budgets %s, lambdas %s, seeds %d" % (len(leaves), len(models), BUDGETS, LAMBDAS, seeds))
    res = {mode: {V: {lam: [] for lam in LAMBDAS} for V in BUDGETS} for mode in ("ORACLE", "NOISY")}
    for seed in range(seeds):
        rng = random.Random(1000 + seed)
        train, held = {}, {}
        for l, v in leaves.items():
            v = v[:]; rng.shuffle(v); h = len(v) // 2; held[l] = v[:h]; train[l] = v[h:]
        for mode in ("ORACLE", "NOISY"):
            for V in BUDGETS:
                agg_leaf = {l: defaultdict(lambda: [0.0, 0.0]) for l in leaves}
                agg_anchor = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))
                for l in leaves:
                    for _ in range(V * len(models) // 2):
                        a, b = rng.sample(models, 2); q = train[l][rng.randrange(len(train[l]))]
                        ca, cb = G[a][q], G[b][q]
                        if ca == cb:
                            wa = 0.5
                            if mode == "NOISY" and rng.random() < 0.8: wa = float(rng.random() < 0.5)
                        else:
                            wa = 1.0 if ca else 0.0
                            if mode == "NOISY" and rng.random() < lpp.NOISE: wa = 1.0 - wa
                        key = (a, b) if a < b else (b, a); w = wa if key[0] == a else 1.0 - wa
                        agg_leaf[l][key][0] += w; agg_leaf[l][key][1] += 1
                        agg_anchor[anchor_of[l]][key][0] += w; agg_anchor[anchor_of[l]][key][1] += 1
                th_anchor = {a: lpp.fit(ag, models) for a, ag in agg_anchor.items()}
                th_free = {l: lpp.fit(agg_leaf[l], models) for l in leaves}
                for lam in LAMBDAS:
                    ll = 0.0; t1 = 0
                    for l in leaves:
                        ta = th_anchor[anchor_of[l]]; tf = th_free[l]
                        th = {m: ta[m] + lam * (tf[m] - ta[m]) for m in models}
                        s = lpp.heldout_score(th, held[l], G, models); ll += s[0]; t1 += s[1]
                    res[mode][V][lam].append((ll / len(leaves), t1 / len(leaves)))
        print("  seed %d done" % seed, flush=True)
    for mode in ("ORACLE", "NOISY"):
        print("\n== %s judge: held-out log-loss by shrinkage lambda (0 = anchor only, 1 = free leaf) ==" % mode)
        for V in BUDGETS:
            base = np.array([r[0] for r in res[mode][V][0.0]])
            line = "  V=%4d:" % V
            best = None
            for lam in LAMBDAS:
                r = np.array(res[mode][V][lam]); wins = int(np.sum(r[:, 0] < base)) if lam > 0 else 0
                line += "  λ=%.2f %.4f (top-1 %.2f, beats λ=0 in %d/%d)" % (lam, r[:, 0].mean(), r[:, 1].mean(), wins, len(r))
                if 0 < lam < 1 and wins * 5 >= 4 * len(r) and (best is None or r[:, 0].mean() < best[1]): best = (lam, r[:, 0].mean())
            print(line)
            if mode == "NOISY" and V == 54:
                print("  LEAF-SHRINK REGISTERED (NOISY, V=54, some 0<λ<1 beats λ=0 in >= 4/5 seeds): %s" % ("RESCUED at λ=%.2f" % best[0] if best else "NOT RESCUED"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seeds", type=int, default=5); a = ap.parse_args()
    main(a.seeds)
