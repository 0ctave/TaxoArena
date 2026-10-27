"""BUDGET-LOMO — was leave-one-ANCHOR-out the wrong fold structure? (registered 2026-09-14, zero calls)

  python tools/analysis/budget_lomo.py

Three fold structures on the identical 891 edges, so they are directly comparable.

CORRECTED 2026-09-15 after the session review: (a) every wrong count carries its McNemar-established count,
which the first version omitted in the very commit that adopted the rule; (b) the NOTE about each edge being
scored twice under LOMO was wrong - oof[id(e)] is overwritten by the later fold, so each edge is scored once,
by whichever endpoint model sorts later; both conventions are now reported; (c) RAW_RATIO is labelled by the
convention it uses.
"""
import os, sys, math, random, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.stats import norm
import rubric_p8 as p8
import pool_guard
import systematic_budget as sb

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "budget_lomo.txt")
THRESH = 0.975
GAP = 0.02


def fold_eval(edges, folds, label, L, K, aq, keep="last"):
    oof = {}; b1s = []
    for name, tr, te in folds:
        if len(tr) < 100 or not te:
            continue
        f0, f1 = sb.fit(tr, x0=(-3.2326, 3.3133))
        b1s.append((name, f1))
        for e in te:
            if keep == "last" or id(e) not in oof:
                oof[id(e)] = sb.cbud(e, f0, f1)
    called = [e for e in edges if id(e) in oof and oof[id(e)] >= THRESH]
    wrong = [e for e in called if not e["right"]]
    est = sb.established(wrong, K, aq)
    nom = sum(1 - oof[id(e)] for e in called)
    L.append("  %-30s %7d %8d %6d(%d) %10.2f %9s %8.1f%%"
             % (label, len(oof), len(called), len(wrong), len(est), nom,
                ("%.1fx" % (len(wrong) / nom)) if nom > 0 else "-", 100.0 * len(called) / max(1, len(oof))))
    return called, wrong, est, nom, b1s


def main():
    L = []
    models, K, P, by, alle, anchor_qs = sb.build()
    edges = [e for e in alle if e["gap"] >= GAP]
    L.append("=== BUDGET-LOMO: three fold structures on the same %d edges (corrected 2026-09-15) ===" % len(edges))
    L.append("  wrong counts as all(McNemar-established) over the anchor's judged questions.")
    L.append("")
    L.append("  %-30s %7s %8s %9s %10s %9s %8s" % ("fold structure", "scored", "called", "wrong", "nominal", "ratio", "utility"))

    b0, b1 = sb.fit(edges)
    ins = [e for e in edges if sb.cbud(e, b0, b1) >= THRESH]
    insw = [e for e in ins if not e["right"]]
    insn = sum(1 - sb.cbud(e, b0, b1) for e in ins)
    L.append("  %-30s %7d %8d %6d(%d) %10.2f %9s %8.1f%%"
             % ("in sample (no holdout)", len(edges), len(ins), len(insw), len(sb.established(insw, K, anchor_qs)), insn,
                "%.1fx" % (len(insw) / insn) if insn else "-", 100.0 * len(ins) / len(edges)))
    rc = [e for e in edges if sb.craw(e) >= THRESH]; rw = [e for e in rc if not e["right"]]
    nom_g = sum(1 - float(norm.cdf(abs(e["m"]) / e["s"])) for e in rc)
    L.append("  %-30s %7d %8d %6d(%d) %10.2f %9s   (empirical called set, Gaussian nominal)"
             % ("raw certificate", len(edges), len(rc), len(rw), len(sb.established(rw, K, anchor_qs)), nom_g, "%.1fx" % (len(rw) / nom_g)))

    ancs = sorted({e["anchor"] for e in edges})
    loao = [(a, [e for e in edges if e["anchor"] != a], [e for e in edges if e["anchor"] == a]) for a in ancs]
    fold_eval(edges, loao, "leave-one-ANCHOR-out (14)", L, K, anchor_qs)
    pairs = sorted({tuple(sorted((e["a"], e["b"]))) for e in edges})
    lopo = [(str(p_), [e for e in edges if tuple(sorted((e["a"], e["b"]))) != p_],
             [e for e in edges if tuple(sorted((e["a"], e["b"]))) == p_]) for p_ in pairs]
    fold_eval(edges, lopo, "leave-one-PAIR-out (%d)" % len(pairs), L, K, anchor_qs)
    lomo = [(m, [e for e in edges if e["a"] != m and e["b"] != m],
             [e for e in edges if e["a"] == m or e["b"] == m]) for m in models]
    lc, lw, le, ln, b1s = fold_eval(edges, lomo, "leave-one-MODEL-out, last fold wins", L, K, anchor_qs, keep="last")
    fold_eval(edges, lomo, "leave-one-MODEL-out, first fold wins", L, K, anchor_qs, keep="first")
    L.append("  (under LOMO each edge touches two folds; oof keeps one score per edge, so scored = %d, not 2x)" % len(edges))

    ratio = len(lw) / ln if ln > 0 else float("nan")
    L.append("")
    L.append("=== (1) PRIMARY: does the calibration claim survive a MODEL-axis fold? ===")
    L.append("  LOMO: %d called, %d wrong (%d established) against %.2f nominal = %.1fx (all) / %.1fx (established)"
             % (len(lc), len(lw), len(le), ln, ratio, len(le) / ln if ln else float("nan")))
    L.append("  LOAO was 2.4x all-labels; the raw certificate %.1fx. The registered falsifier (LOMO worse than the raw" % (len(rw) / nom_g))
    L.append("  certificate) %s." % ("FIRES" if ratio >= len(rw) / nom_g else "does not fire"))

    L.append("")
    L.append("=== (2) DOES b1 SWING WHEN ONE MODEL IS WITHHELD? ===")
    vals = sorted(v for _, v in b1s)
    L.append("  b1 across the %d LOMO folds: min %+.4f | median %+.4f | max %+.4f | spread %.2fx"
             % (len(vals), vals[0], vals[len(vals) // 2], vals[-1], (vals[-1] / vals[0]) if vals[0] > 0 else float("nan")))
    for nm, v in sorted(b1s, key=lambda t: t[1]):
        L.append("      withhold %-30s b1 = %+.4f" % (nm[:30], v))
    L.append("  NOTE: b0 and b1 co-vary across folds (the review measured corr -0.99), so the swing in b1 alone")
    L.append("  overstates the swing in tau at mid agreement and understates it at low agreement. Neither")
    L.append("  'unstable parameter' nor 'stable calibration despite it' is established by this table.")

    L.append("")
    L.append("=== (3) UTILITY, and the parameter-free gate on the same edges ===")
    base_right = sum(1 for e in rc if e["right"])
    L.append("  budget under LOMO: %d called, %d wrong (%d est), %d correct surrendered"
             % (len(lc), len(lw), len(le), base_right - sum(1 for e in lc if e["right"])))
    for t in (0.60, 0.65, 0.70, 0.75, 0.80):
        g = [e for e in rc if e["agree"] < t]; gw = [e for e in g if not e["right"]]
        L.append("  gate A < %.2f: %d called, %d wrong (%d est), %d correct surrendered"
                 % (t, len(g), len(gw), len(sb.established(gw, K, anchor_qs)), base_right - sum(1 for e in g if e["right"])))

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
