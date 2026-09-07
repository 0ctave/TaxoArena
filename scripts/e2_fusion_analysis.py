#!/usr/bin/env python3
"""P6 fusion analysis: paired per-question contrasts of held-out routing fit.

Reads the per-question score CSVs written by E2FusionRunner (--e2-fusion-config) for
the three conditions T (frozen tree), F (top-3 cross-anchor E1 twin pairs fused),
Pf (size-matched placebo fusions, seed 999) and computes, per the FROZEN P6
registration (docs/v2_validation_plan.md):

  PRIMARY (two-sided): D = (F-T) - (Pf-T) per question, full pool.
    "Fusion helps" iff mean D > 0 with the seeded 10,000-fold bootstrap 95% CI
    excluding 0 AND exact sign test p < 0.05. Anything else closes the overlap
    program with soft routing vindicated.
  SECONDARY: same summaries on the AFFECTED subset (ll or top1 differs from T in
    at least one fused condition).
  DESCRIPTIVE: per-pair breakdown via the hit_real / hit_placebo columns (pair
    ranks whose surviving pair leaves were in T's admitted membership set).

Usage: python scripts/e2_fusion_analysis.py experiment_results/e2_fusion
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
                "top1": r["top1_id"],
                "top1_label": r["top1_label"],
                "no_leaf": r["no_leaf"] == "1",
                "hit_real": set(int(x) for x in r["hit_real"].split("|") if x),
                "hit_placebo": set(int(x) for x in r["hit_placebo"].split("|") if x),
            }
    return rows


def sign_test(deltas, eps=1e-12):
    pos = sum(1 for d in deltas if d > eps)
    neg = sum(1 for d in deltas if d < -eps)
    n = pos + neg
    if n == 0:
        return pos, neg, 1.0
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
    F = read_scores(outdir / "e2_scores_F.csv")
    P = read_scores(outdir / "e2_scores_Pf.csv")
    qids = sorted(set(T) & set(F) & set(P))
    assert len(qids) == len(T) == len(F) == len(P), "condition CSVs cover different question sets"
    print(f"pool: {len(qids)} questions (identical across T/F/Pf)")

    dF = [F[q]["ll"] - T[q]["ll"] for q in qids]
    dP = [P[q]["ll"] - T[q]["ll"] for q in qids]
    dD = [F[q]["ll"] - P[q]["ll"] for q in qids]

    print("\n== Full pool: held-out log-likelihood deltas ==")
    summarize("F  - T          ", dF)
    summarize("Pf - T          ", dP)
    mean, lo, hi, p = summarize("(F-T) - (Pf-T)  ", dD)

    print("\n== REGISTERED VERDICT (frozen P6 criteria) ==")
    helps = mean > 0 and lo > 0 and p < 0.05
    print(f"  mean D = {mean:+.6f}, CI [{lo:+.6f}, {hi:+.6f}], sign p = {p:.4g}")
    print(f"  -> {'FUSION HELPS' if helps else 'NULL / soft routing vindicated (overlap program closes)'}")

    eps = 1e-12
    affF = [q for q in qids if abs(F[q]["ll"] - T[q]["ll"]) > eps or F[q]["top1"] != T[q]["top1"]]
    affP = [q for q in qids if abs(P[q]["ll"] - T[q]["ll"]) > eps or P[q]["top1"] != T[q]["top1"]]
    affected = sorted(set(affF) | set(affP))
    print(f"\n== Affected subset (secondary) ==")
    print(f"  affected by F: {len(affF)}  affected by Pf: {len(affP)}  union: {len(affected)}")
    if affected:
        summarize("F  - T (affected)", [F[q]["ll"] - T[q]["ll"] for q in affected])
        summarize("Pf - T (affected)", [P[q]["ll"] - T[q]["ll"] for q in affected])
        summarize("F  - Pf (affected)", [F[q]["ll"] - P[q]["ll"] for q in affected])

    print("\n== Per-pair breakdown (descriptive; subset = T admitted the pair's leaves) ==")
    ranks = sorted({r for q in qids for r in T[q]["hit_real"]} | {1, 2, 3})
    for r in ranks:
        qs_r = [q for q in qids if r in T[q]["hit_real"]]
        qs_p = [q for q in qids if r in T[q]["hit_placebo"]]
        if qs_r:
            mF = sum(F[q]["ll"] - T[q]["ll"] for q in qs_r) / len(qs_r)
            mD = sum(F[q]["ll"] - P[q]["ll"] for q in qs_r) / len(qs_r)
            print(f"  real pair #{r}:    n={len(qs_r):4d}  mean(F-T) {mF:+.6f}  mean(F-Pf) {mD:+.6f}")
        else:
            print(f"  real pair #{r}:    n=   0")
        if qs_p:
            mP = sum(P[q]["ll"] - T[q]["ll"] for q in qs_p) / len(qs_p)
            print(f"  placebo pair #{r}: n={len(qs_p):4d}  mean(Pf-T) {mP:+.6f}")
        else:
            print(f"  placebo pair #{r}: n=   0")

    print("\n== Top-1 agreement with T / routing health ==")
    for name, C in (("F ", F), ("Pf", P)):
        agree = sum(1 for q in qids if C[q]["top1"] == T[q]["top1"])
        print(f"  {name}: top1 agreement {agree}/{len(qids)} = {agree / len(qids):.4f}")
    for name, C in (("T ", T), ("F ", F), ("Pf", P)):
        nomatch = sum(1 for q in qids if C[q]["no_leaf"])
        hit_r = sum(1 for q in qids if C[q]["hit_real"])
        hit_p = sum(1 for q in qids if C[q]["hit_placebo"])
        print(f"  {name}: NoMatch/residual {nomatch}/{len(qids)} = {nomatch / len(qids):.4f}  "
              f"admitted-real-pair-leaf {hit_r}  admitted-placebo-pair-leaf {hit_p}")

    print("\n== Per-domain mean (F-T) vs (Pf-T) ==")
    domains = sorted({T[q]["domain"] for q in qids})
    rows = []
    for d in domains:
        qs = [q for q in qids if T[q]["domain"] == d]
        mf = sum(F[q]["ll"] - T[q]["ll"] for q in qs) / len(qs)
        mp = sum(P[q]["ll"] - T[q]["ll"] for q in qs) / len(qs)
        rows.append((d, len(qs), mf, mp))
    for d, n, mf, mp in sorted(rows, key=lambda r: -abs(r[2])):
        print(f"  {d:20s} n={n:5d}  F-T {mf:+.6f}   Pf-T {mp:+.6f}")

    out = outdir / "e2_fusion_contrasts.csv"
    setF, setP = set(affF), set(affP)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["question_id", "domain", "ll_T", "ll_F", "ll_Pf", "dF", "dPf", "D",
                    "top1_T", "top1_F", "top1_Pf", "affected_F", "affected_Pf",
                    "hit_real_T", "hit_placebo_T"])
        for q in qids:
            w.writerow([q, T[q]["domain"], T[q]["ll"], F[q]["ll"], P[q]["ll"],
                        F[q]["ll"] - T[q]["ll"], P[q]["ll"] - T[q]["ll"], F[q]["ll"] - P[q]["ll"],
                        T[q]["top1"], F[q]["top1"], P[q]["top1"],
                        int(q in setF), int(q in setP),
                        "|".join(str(x) for x in sorted(T[q]["hit_real"])),
                        "|".join(str(x) for x in sorted(T[q]["hit_placebo"]))])
    print(f"\nper-question contrasts written to {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "experiment_results/e2_fusion")
