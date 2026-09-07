#!/usr/bin/env python3
"""E2 bridge analysis: paired per-question contrasts of held-out routing fit.

Reads the per-question score CSVs written by E2BridgeRunner (--e2-config) for the three
conditions T (frozen tree), B (E1-pair bridges), P (placebo bridges) and computes:

  - paired deltas d_B = ll_B - ll_T and d_P = ll_P - ll_T per question,
  - the decision contrast d_B - d_P (equivalently ll_B - ll_P),
  - sign tests (exact binomial on nonzero deltas) and seeded bootstrap CIs of the means,
  - Top-1 agreement with T, NoMatch (residual) rates, bridged-leaf reach counts,
  - the same summaries restricted to the AFFECTED subset (questions whose routing
    differs from T in at least one bridged condition), since K=8 edges can only
    touch a small part of the pool and the full-pool mean dilutes the effect.

Usage: python scripts/e2_bridge_analysis.py experiment_results/e2_bridges_smoke
"""
import csv
import math
import random
import sys
from pathlib import Path


def read_scores(path):
    rows = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            qid = int(r["question_id"])
            rows[qid] = {
                "domain": r["domain"],
                "ll": float(r["ll"]) if r["ll"] != "" else math.nan,
                "ll_leaves": float(r["ll_leaves"]) if r["ll_leaves"] != "" else math.nan,
                "top1": r["top1_id"],
                "top1_label": r["top1_label"],
                "no_leaf": r["no_leaf"] == "1",
                "reached_bridged": r["reached_bridged"] == "1",
                "top1_bridged": r["top1_bridged"] == "1",
                "n_leaves": int(r["n_leaves"]),
            }
    return rows


def sign_test(deltas, eps=1e-12):
    pos = sum(1 for d in deltas if d > eps)
    neg = sum(1 for d in deltas if d < -eps)
    n = pos + neg
    if n == 0:
        return pos, neg, 1.0
    # exact two-sided binomial test at p=0.5
    from math import comb
    k = max(pos, neg)
    tail = sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return pos, neg, min(1.0, 2 * tail)


def bootstrap_ci(deltas, n_boot=10000, seed=42, alpha=0.05):
    if not deltas:
        return (math.nan, math.nan, math.nan)
    rng = random.Random(seed)
    n = len(deltas)
    means = []
    for _ in range(n_boot):
        s = 0.0
        for _ in range(n):
            s += deltas[rng.randrange(n)]
        means.append(s / n)
    means.sort()
    lo = means[int(alpha / 2 * n_boot)]
    hi = means[int((1 - alpha / 2) * n_boot) - 1]
    return (sum(deltas) / n, lo, hi)


def summarize(name, deltas):
    mean, lo, hi = bootstrap_ci(deltas)
    pos, neg, p = sign_test(deltas)
    zero = len(deltas) - pos - neg
    print(f"  {name}: n={len(deltas)}  mean={mean:+.6f}  95% CI [{lo:+.6f}, {hi:+.6f}]")
    print(f"    sign test: +{pos} / -{neg} / ={zero}  p={p:.4g}")
    return mean, lo, hi, p


def main(outdir):
    outdir = Path(outdir)
    T = read_scores(outdir / "e2_scores_T.csv")
    B = read_scores(outdir / "e2_scores_B.csv")
    P = read_scores(outdir / "e2_scores_P.csv")
    qids = sorted(set(T) & set(B) & set(P))
    assert len(qids) == len(T) == len(B) == len(P), "condition CSVs cover different question sets"
    print(f"pool: {len(qids)} questions (identical across T/B/P)")

    dB = [B[q]["ll"] - T[q]["ll"] for q in qids]
    dP = [P[q]["ll"] - T[q]["ll"] for q in qids]
    dBP = [B[q]["ll"] - P[q]["ll"] for q in qids]

    print("\n== Full pool: held-out log-likelihood deltas ==")
    summarize("B - T           ", dB)
    summarize("P - T           ", dP)
    summarize("(B-T) - (P-T)   ", dBP)

    eps = 1e-12
    affected = [q for q in qids
                if abs(B[q]["ll"] - T[q]["ll"]) > eps or abs(P[q]["ll"] - T[q]["ll"]) > eps
                or B[q]["top1"] != T[q]["top1"] or P[q]["top1"] != T[q]["top1"]]
    affB = [q for q in qids if abs(B[q]["ll"] - T[q]["ll"]) > eps or B[q]["top1"] != T[q]["top1"]]
    affP = [q for q in qids if abs(P[q]["ll"] - T[q]["ll"]) > eps or P[q]["top1"] != T[q]["top1"]]
    print(f"\n== Affected subset ==")
    print(f"  affected by B: {len(affB)}  affected by P: {len(affP)}  union: {len(affected)}")
    if affected:
        summarize("B - T  (affected)", [B[q]["ll"] - T[q]["ll"] for q in affected])
        summarize("P - T  (affected)", [P[q]["ll"] - T[q]["ll"] for q in affected])
        summarize("B - P  (affected)", [B[q]["ll"] - P[q]["ll"] for q in affected])

    print("\n== Top-1 agreement with T / routing health ==")
    for name, C in (("B", B), ("P", P)):
        agree = sum(1 for q in qids if C[q]["top1"] == T[q]["top1"])
        print(f"  {name}: top1 agreement {agree}/{len(qids)} = {agree / len(qids):.4f}")
    for name, C in (("T", T), ("B", B), ("P", P)):
        nomatch = sum(1 for q in qids if C[q]["no_leaf"])
        reached = sum(1 for q in qids if C[q]["reached_bridged"])
        top1b = sum(1 for q in qids if C[q]["top1_bridged"])
        print(f"  {name}: NoMatch/residual {nomatch}/{len(qids)} = {nomatch / len(qids):.4f}  "
              f"reached-bridged-leaf {reached}  top1-bridged {top1b}")

    # per-domain mean deltas, largest movers first
    print("\n== Per-domain mean (B-T) vs (P-T) ==")
    domains = sorted({T[q]["domain"] for q in qids})
    rows = []
    for d in domains:
        qs = [q for q in qids if T[q]["domain"] == d]
        mb = sum(B[q]["ll"] - T[q]["ll"] for q in qs) / len(qs)
        mp = sum(P[q]["ll"] - T[q]["ll"] for q in qs) / len(qs)
        rows.append((d, len(qs), mb, mp))
    for d, n, mb, mp in sorted(rows, key=lambda r: -abs(r[2])):
        print(f"  {d:20s} n={n:5d}  B-T {mb:+.6f}   P-T {mp:+.6f}")

    # write a machine-readable summary next to the CSVs
    out = outdir / "e2_contrasts.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["question_id", "domain", "ll_T", "ll_B", "ll_P", "dB", "dP", "dBP",
                    "top1_T", "top1_B", "top1_P", "affected_B", "affected_P"])
        for q in qids:
            w.writerow([q, T[q]["domain"], T[q]["ll"], B[q]["ll"], P[q]["ll"],
                        B[q]["ll"] - T[q]["ll"], P[q]["ll"] - T[q]["ll"], B[q]["ll"] - P[q]["ll"],
                        T[q]["top1"], B[q]["top1"], P[q]["top1"],
                        int(q in set(affB)), int(q in set(affP))])
    print(f"\nper-question contrasts written to {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "experiment_results/e2_bridges_smoke")
