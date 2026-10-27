"""M3 — synthetic arena scaling (docs/m_series_registration.md, registered before running).
Verdict oracle = the key (ORACLE) or a Mistral-like noisy judge (NOISY). Zero calls.

  python tools/analysis/synthetic_arena_scaling.py [--seeds 5]
"""
import os, sys, math, random, sqlite3, argparse
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj

SIZES = [8, 16, 24, 32, 46]


def load():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    nq = ev.execute("SELECT COUNT(DISTINCT question_id) FROM eval_results").fetchone()[0]
    models = sorted(m for m, n in ev.execute("SELECT model_name, COUNT(DISTINCT question_id) FROM eval_results GROUP BY model_name")
                    if n >= 0.95 * nq and m != "Meta-Llama-3-70B-Instruct")
    C = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in models:
            C[m][q] = int(c or 0)
    qs = sorted(set.intersection(*[set(C[m]) for m in models]))
    acc = {m: sum(C[m][q] for q in qs) / len(qs) for m in models}
    return models, qs, C, acc


class Arena:
    def __init__(self, models, qs, C, noisy, rng):
        self.models, self.qs, self.C, self.noisy, self.rng = models, qs, C, noisy, rng
        self.agg = defaultdict(lambda: [0.0, 0.0])
        self.spent = 0

    def match(self, a, b):
        q = self.qs[self.rng.randrange(len(self.qs))]
        ca, cb = self.C[a][q], self.C[b][q]
        if ca != cb:
            wa = 1.0 if ca else 0.0
            if self.noisy and self.rng.random() < 0.12:
                wa = 1.0 - wa
        else:
            wa = 0.5
            if self.noisy and self.rng.random() < 0.8:
                wa = float(self.rng.random() < 0.5)
        x, y = (a, b) if a < b else (b, a)
        if a > b:
            wa = 1.0 - wa
        rec = self.agg[(x, y)]
        rec[0] += wa; rec[1] += 1.0
        self.spent += 1

    def fit(self, roster):
        agg = {k: tuple(v) for k, v in self.agg.items() if k[0] in roster and k[1] in roster}
        if not agg:
            return {m: 0.0 for m in roster}
        return rj.mm_fit(agg, sorted(roster))


def insert(arena, roster, newcomer, per_anchor, n_anchors=4):
    """bisection placement: anchor = current board's middle, then move up/down by outcome."""
    theta = arena.fit(roster)
    order = sorted(roster, key=lambda m: theta[m])          # ascending
    lo, hi = 0, len(order) - 1
    used = []
    for _ in range(n_anchors):
        mid = (lo + hi) // 2
        anchor = order[mid]
        if anchor in used:
            # pick the nearest unused index
            cands = [i for i in range(len(order)) if order[i] not in used]
            if not cands:
                break
            mid = min(cands, key=lambda i: abs(i - mid)); anchor = order[mid]
        used.append(anchor)
        wins = 0.0
        for _ in range(per_anchor):
            before = arena.agg[(min(anchor, newcomer), max(anchor, newcomer))][0]
            arena.match(newcomer, anchor)
            after = arena.agg[(min(anchor, newcomer), max(anchor, newcomer))][0]
            wins += (after - before) if newcomer < anchor else (1.0 - (after - before))
        if wins / per_anchor > 0.5:
            lo = mid + 1
        else:
            hi = mid - 1
        if lo > hi:
            break
    return arena.fit(roster | {newcomer})


def rank_error(theta, acc, roster, m):
    est = sorted(roster, key=lambda x: -theta[x]).index(m)
    gt = sorted(roster, key=lambda x: -acc[x]).index(m)
    return abs(est - gt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    a = ap.parse_args()
    models, qs, C, acc = load()
    print("M3 synthetic arena: %d models, %d keyed questions | oracle = key; noisy = 12%% flips + 80%% coin flips on non-decidable" % (len(models), len(qs)))
    for noisy in (False, True):
        for per_anchor in (25, 50, 100):
            band = defaultdict(list)   # size band -> list of (rank_err, spent_for_newcomer)
            rhos = defaultdict(list)
            for seed in range(a.seeds):
                rng = random.Random(1000 + seed)
                arena = Arena(models, qs, C, noisy, rng)
                order = models[:]; rng.shuffle(order)
                roster = set(order[:8])
                for x in roster:
                    for y in roster:
                        if x < y:
                            for _ in range(100):
                                arena.match(x, y)
                theta = arena.fit(roster)
                rhos[8].append(rj.spearman([theta[m] for m in roster], [acc[m] for m in roster]))
                for newcomer in order[8:]:
                    s0 = arena.spent
                    theta = insert(arena, roster, newcomer, per_anchor)
                    roster = roster | {newcomer}
                    err = rank_error(theta, acc, roster, newcomer)
                    size = len(roster)
                    b = min(s for s in SIZES if size <= s)
                    band[b].append((err, arena.spent - s0))
                    if size in SIZES:
                        rhos[size].append(rj.spearman([theta[m] for m in roster], [acc[m] for m in roster]))
            print("\n-- %s judge | %d matches per newcomer (4 anchors x %d) --" % ("NOISY" if noisy else "ORACLE", 4 * per_anchor, per_anchor))
            print("   roster<= | newcomer rank error median (p75) | within +-1 rank | matches/newcomer | board rho (median over seeds)")
            for b in SIZES:
                if b == 8:
                    print("   %8d | %s | %s | %s | %.3f" % (8, "base", "-", "-", float(np.median(rhos[8]))))
                    continue
                errs = [e for e, _ in band[b]]; sp = [s for _, s in band[b]]
                if not errs:
                    continue
                print("   %8d | %5.1f (%4.1f) | %5.0f%% | %6.0f | %.3f" % (
                    b, float(np.median(errs)), float(np.percentile(errs, 75)), 100 * sum(e <= 1 for e in errs) / len(errs),
                    float(np.mean(sp)), float(np.median(rhos[b])) if rhos[b] else float("nan")))
    # joint baseline at 400 matches per model, roster 46
    print("\n-- JOINT round-robin baseline, 46 models, same total budget as 400/newcomer (46*400 = 18,400 matches) --")
    for noisy in (False, True):
        r = []
        for seed in range(a.seeds):
            rng = random.Random(2000 + seed)
            arena = Arena(models, qs, C, noisy, rng)
            pairs = [(x, y) for x in models for y in models if x < y]
            per_pair = max(1, 18400 // len(pairs))
            for x, y in pairs:
                for _ in range(per_pair):
                    arena.match(x, y)
            th = arena.fit(set(models))
            r.append(rj.spearman([th[m] for m in models], [acc[m] for m in models]))
        print("   %s: rho median %.3f (per pair %d matches)" % ("NOISY" if noisy else "ORACLE", float(np.median(r)), per_pair))


if __name__ == "__main__":
    main()
