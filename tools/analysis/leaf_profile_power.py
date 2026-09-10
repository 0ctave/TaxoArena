"""LEAF-POWER — how many verdicts per (leaf, model) until a leaf-level profile beats the anchor-level
profile on held-out prediction? (zero calls; synthetic arena with the key as oracle, M3 machinery)

Design (registered 2026-09-10, before running): clean bareq512_s42 tree (leaf = nearest centroid), the
12 arena models, per anchor a 50/50 question split (held-out half never judged). Matches are sampled
uniformly within leaves on the train half; the verdict is the key (ORACLE) or the key flipped with
probability 0.228 (NOISY: Mistral's key-decidable error rate, 1 − 0.772) on decidable pairs; on
non-decidable pairs the key gives 0.5, and the NOISY judge instead returns a random winner with
probability 0.8 (M3's model of Mistral's 20% tie rate).
At budget V verdicts per (leaf, model) cell we fit BT per leaf (penalised, 0.5 pseudo-counts as the
atlas does) and BT per anchor, then score BOTH on the held-out questions of each leaf: the per-question
"who wins" log-loss of the key-decidable held-out pairs under P(a beats b) = sigma(theta_a - theta_b),
and top-1 agreement (does the profile's best model in the leaf match the key's best model in that
leaf on held-out questions?). Curve over V in {10, 20, 35, 54, 80, 120, 200, 400}, 5 seeds.
REGISTERED READOUT: V* = the smallest V at which leaf-level held-out log-loss beats anchor-level in
>= 4/5 seeds (ORACLE and NOISY separately); R2's actual median is 54. Prediction: ORACLE V* ~ 80–120;
NOISY V* ~ 200–400 (4x more, as M3's noise clause found).

  python tools/analysis/leaf_profile_power.py [--seeds 5]
"""
import os, sys, math, random, argparse
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import leaf_profile_evidence as lpe
import profile_atlas as pa
import rubric_p8 as p8

ARENA12 = p8.ARENA12
BUDGETS = [10, 20, 35, 54, 80, 120, 200, 400]
NOISE = 0.228


def fit(agg, models):
    return pa.mm_fit({k: (v[0], v[1]) for k, v in agg.items()}, models) if agg else {m: 0.0 for m in models}


def heldout_score(theta, held, G, models):
    """(log-loss over key-decidable held-out pairs, top-1 hit) for one leaf under strengths theta."""
    ll = 0.0; n = 0
    for q in held:
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                ca, cb = G[a][q], G[b][q]
                if ca == cb: continue
                pa_ = 1 / (1 + math.exp(-(theta[a] - theta[b]))); pa_ = min(max(pa_, 1e-6), 1 - 1e-6)
                ll -= math.log(pa_ if ca else 1 - pa_); n += 1
    best_key = max(models, key=lambda m: sum(G[m][q] for q in held))
    best_prof = max(models, key=lambda m: theta[m])
    return ll / max(1, n), int(best_key == best_prof)


def main(seeds):
    models_all, G, qs, leaf, anc = lpe.assign_leaves()
    models = [m for m in ARENA12 if m in G]
    by_leaf = defaultdict(list)
    for q in qs: by_leaf[leaf[q]].append(q)
    leaves = {l: v for l, v in by_leaf.items() if len(v) >= 60}
    anchor_of = {l: anc[v[0]] for l, v in leaves.items()}
    print("LEAF-POWER: %d leaves (>= 60 keyed questions), %d models, budgets %s, seeds %d" % (len(leaves), len(models), BUDGETS, seeds))
    res = {mode: {V: [] for V in BUDGETS} for mode in ("ORACLE", "NOISY")}
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
                    n_matches = V * len(models) // 2
                    for _ in range(n_matches):
                        a, b = rng.sample(models, 2); q = train[l][rng.randrange(len(train[l]))]
                        ca, cb = G[a][q], G[b][q]
                        if ca == cb:
                            wa = 0.5
                            if mode == "NOISY" and rng.random() < 0.8: wa = float(rng.random() < 0.5)
                        else:
                            wa = 1.0 if ca else 0.0
                            if mode == "NOISY" and rng.random() < NOISE: wa = 1.0 - wa
                        key = (a, b) if a < b else (b, a); w = wa if key[0] == a else 1.0 - wa
                        agg_leaf[l][key][0] += w; agg_leaf[l][key][1] += 1
                        agg_anchor[anchor_of[l]][key][0] += w; agg_anchor[anchor_of[l]][key][1] += 1
                th_anchor = {a: fit(ag, models) for a, ag in agg_anchor.items()}
                ll_l = ll_a = 0.0; t1_l = t1_a = 0
                for l in leaves:
                    th_l = fit(agg_leaf[l], models)
                    s_l = heldout_score(th_l, held[l], G, models); s_a = heldout_score(th_anchor[anchor_of[l]], held[l], G, models)
                    ll_l += s_l[0]; ll_a += s_a[0]; t1_l += s_l[1]; t1_a += s_a[1]
                res[mode][V].append((ll_l / len(leaves), ll_a / len(leaves), t1_l / len(leaves), t1_a / len(leaves)))
        print("  seed %d done" % seed, flush=True)
    for mode in ("ORACLE", "NOISY"):
        print("\n== %s judge: held-out log-loss (lower is better) and top-1 agreement with the key, leaf-level vs anchor-level profile ==" % mode)
        vstar = None
        for V in BUDGETS:
            r = np.array(res[mode][V]); wins = int(np.sum(r[:, 0] < r[:, 1]))
            print("  V=%4d per (leaf, model): log-loss leaf %.4f vs anchor %.4f (leaf better in %d/%d seeds) | top-1 leaf %.2f vs anchor %.2f"
                  % (V, r[:, 0].mean(), r[:, 1].mean(), wins, len(r), r[:, 2].mean(), r[:, 3].mean()))
            if vstar is None and wins * 5 >= 4 * len(r): vstar = V
        print("  V* (leaf beats anchor in >= 4/5 seeds): %s  [R2's actual median: 54]" % (vstar if vstar is not None else "> %d" % BUDGETS[-1]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seeds", type=int, default=5); a = ap.parse_args()
    main(a.seeds)
