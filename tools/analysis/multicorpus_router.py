"""Stage 2 — key-only router regret on the multi-corpus DB (docs/multi_corpus_design.md §4; zero LLM calls).

  python tools/analysis/multicorpus_router.py [--db multicorpus_cache_v1.db] [--ratio 0.3] [--seed 42] [--boots 200]

Registered readout (2026-09-11): with a per-(source, domain) stratified split, the best model by TRAIN-side
accuracy at three granularities (global = best single model; per source; per source/domain), evaluated on the
RESERVED side: routed accuracy vs best single vs per-question oracle, with a question-level bootstrap SE.
The router has something to route iff routed-by-source beats best-single by more than 2 SE. Also reported: the
argmax model per source and per domain, and the model x source interaction (does the best model change?).
"""
import os, sys, random, sqlite3, argparse
from collections import defaultdict, Counter
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(db, ratio, seed, boots):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    Q = {q: (s, d) for q, s, d in con.execute("SELECT question_id, source, domain FROM corpus_questions")}
    models = [m for (m,) in con.execute("SELECT DISTINCT model_name FROM eval_results ORDER BY model_name")]
    G = defaultdict(dict)
    for q, m, c in con.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        G[q][m] = int(c)
    qs = sorted(q for q in Q if len(G[q]) == len(models))
    print("multi-corpus router: %d questions with all %d models | sources %s" % (len(qs), len(models), dict(Counter(Q[q][0] for q in qs))))
    rng = random.Random(seed); train, test = [], []
    by_stratum = defaultdict(list)
    for q in qs: by_stratum[Q[q]].append(q)
    for k, v in sorted(by_stratum.items()):
        v = v[:]; rng.shuffle(v); n = int(round(len(v) * ratio)); test += v[:n]; train += v[n:]
    print("split ratio %.2f seed %d: train %d / reserved %d across %d (source, domain) strata" % (ratio, seed, len(train), len(test), len(by_stratum)))

    def best(qs_):
        return max(models, key=lambda m: sum(G[q][m] for q in qs_)) if qs_ else None
    g_best = best(train)
    s_best = {s: best([q for q in train if Q[q][0] == s]) for s in {Q[q][0] for q in train}}
    d_best = {k: best([q for q in train if Q[q] == k]) for k in by_stratum}
    print("\nbest single model (train): %s" % g_best)
    print("best model per source (train):")
    for s in sorted(s_best): print("  %-9s %s" % (s, s_best[s]))
    changes = sum(1 for k in d_best if d_best[k] != s_best[k[0]])
    print("domains whose best model differs from their source's best: %d / %d" % (changes, len(d_best)))

    def score(sel):
        n = len(sel)
        return (sum(G[q][g_best] for q in sel) / n,
                sum(G[q][s_best.get(Q[q][0], g_best)] for q in sel) / n,
                sum(G[q][d_best.get(Q[q], s_best.get(Q[q][0], g_best))] for q in sel) / n,
                sum(max(G[q].values()) for q in sel) / n)
    obs = score(test)
    bs = np.array([score([test[rng.randrange(len(test))] for _ in range(len(test))]) for _ in range(boots)])
    se = bs.std(axis=0, ddof=1)
    names = ["best single", "routed by source", "routed by source/domain", "oracle"]
    print("\nRESERVED side (n=%d):" % len(test))
    for i, nm in enumerate(names): print("  %-26s %.3f ± %.3f" % (nm, obs[i], se[i]))
    gain_s = obs[1] - obs[0]; se_s = np.std(bs[:, 1] - bs[:, 0], ddof=1)
    gain_d = obs[2] - obs[0]; se_d = np.std(bs[:, 2] - bs[:, 0], ddof=1)
    print("  router gain by source: %+.3f ± %.3f (%s) | by source/domain: %+.3f ± %.3f (%s)" % (
        gain_s, se_s, "REAL" if gain_s > 2 * se_s else "not resolved", gain_d, se_d, "REAL" if gain_d > 2 * se_d else "not resolved"))
    print("\nper source on the reserved side: best single vs routed-by-domain vs oracle")
    for s in sorted(s_best):
        sel = [q for q in test if Q[q][0] == s]; o = score(sel)
        print("  %-9s n=%5d | single %.3f | by-domain %.3f | oracle %.3f | source best %s" % (s, len(sel), o[0], o[2], o[3], s_best[s]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.path.join(ROOT, "multicorpus_cache_v1.db")); ap.add_argument("--ratio", type=float, default=0.3)
    ap.add_argument("--seed", type=int, default=42); ap.add_argument("--boots", type=int, default=200)
    a = ap.parse_args(); main(a.db, a.ratio, a.seed, a.boots)
