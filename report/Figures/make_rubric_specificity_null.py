# Generates the rubric-specificity null figure (single panel): the 87 induced
# cells' rubric specificity against 13 size-matched random cells put through
# the same induction procedure.
#
# HISTORY. This replaces panel (a) of make_rubric_specific_not_decisive.py.
# That script's panel (b) drew winner-agreement counts from the withdrawn
# pilot arena (Run A), whose verdicts are not evidence; the null analysis in
# this panel is offline -- rubric text against rubric text -- and involves no
# arena verdict, no judge call and no roster, so it survives the withdrawal
# untouched.
#
# REAL DATA ONLY. Every registered value is asserted before drawing; on
# mismatch the script raises and emits no PDF.
#
# Source: build/rubric_null/measures_all.json (the rubric-null harness export).
#
# Run from anywhere:  python report/Figures/make_rubric_specificity_null.py
import json
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "rubric_specificity_null.pdf")
MEASURES = os.path.join(ROOT, "build", "rubric_null", "measures_all.json")

# Registered values this script MUST reproduce.
PUB_LEAF = dict(n=87, median=0.138, positive=81)
PUB_RANDOM = dict(n=13, median=0.012, positive=7)
PUB_P = 1.21e-6
PUB_GE90 = {"leaf-87": 0, "random-cell": 6}

meas = json.load(open(MEASURES, encoding="utf-8"))
leaf = meas["leaf-87"]["raw_spec"]
rand = meas["random-cell"]["raw_spec"]

for arm, vals, pub in (("leaf-87", leaf, PUB_LEAF), ("random-cell", rand, PUB_RANDOM)):
    med = statistics.median(vals)
    pos = sum(1 for v in vals if v > 0)
    if len(vals) != pub["n"] or round(med, 3) != pub["median"] or pos != pub["positive"]:
        raise SystemExit("MISMATCH %s: n=%d med=%.4f pos=%d, registered %s"
                         % (arm, len(vals), med, pos, pub))
    if meas[arm]["ge90"] != PUB_GE90[arm]:
        raise SystemExit("MISMATCH %s ge90: %s vs %s"
                         % (arm, meas[arm]["ge90"], PUB_GE90[arm]))

p_val = mannwhitneyu(leaf, rand, alternative="greater", method="asymptotic").pvalue
if abs(p_val - PUB_P) / PUB_P > 0.01:
    raise SystemExit("MISMATCH Mann-Whitney p: got %.3e, registered %.3e"
                     % (p_val, PUB_P))
print("verified: medians %.3f / %.3f, p = %.3e"
      % (statistics.median(leaf), statistics.median(rand), p_val))

plt.rcParams.update({
    "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 9,
    "font.family": "serif", "pdf.fonttype": 42,
    "axes.spines.top": False, "axes.spines.right": False,
})

fig, axa = plt.subplots(figsize=(6.6, 3.2))


def ecdf(vals):
    v = sorted(vals)
    xs, ys = [], []
    for i, x in enumerate(v):
        xs += [x, x]
        ys += [i / len(v), (i + 1) / len(v)]
    return xs, ys


for vals, style, lab in ((leaf, dict(color="black", lw=1.5, ls="-"), "induced cells"),
                         (rand, dict(color="black", lw=1.2, ls=(0, (4, 2.5))),
                          "random cells")):
    xs, ys = ecdf(vals)
    axa.step(xs, [y * 100 for y in ys], where="post", **style, zorder=3)
    med = statistics.median(vals)
    axa.plot([med], [50], marker="o" if lab == "induced cells" else "s",
             ms=5.4, mfc="black" if lab == "induced cells" else "white",
             mec="black", mew=1.1, zorder=4)

axa.axvline(0.0, color="0.45", lw=0.9, ls=(0, (1, 2)), zorder=1)
axa.set_xlim(-0.10, 0.46)
axa.set_ylim(0, 104)
axa.set_xlabel("rubric specificity: own cell $-$ other cells "
               "(share of the rubric's content terms)\n"
               "0 = the rubric says no more about its own cell than about any "
               "other; further right = more particular",
               fontsize=8, linespacing=1.45)
axa.set_ylabel("cells at or below (%)")

axa.annotate("median $0.138$", xy=(statistics.median(leaf), 50),
             xytext=(9, -5), textcoords="offset points", ha="left", va="top",
             fontsize=7.5)
axa.annotate("median $0.012$", xy=(statistics.median(rand), 50),
             xytext=(-9, 4), textcoords="offset points", ha="right",
             va="bottom", fontsize=7.5)
axa.annotate("the 87 INDUCED cells\n(81 of 87 above zero)",
             xy=(0.225, 84), xytext=(0.262, 61), ha="left", va="center",
             fontsize=8, linespacing=1.4,
             arrowprops=dict(arrowstyle="-", lw=0.6, color="0.4",
                             shrinkA=3, shrinkB=3))
axa.annotate("13 size-matched RANDOM cells,\nsame induction procedure\n"
             "(7 of 13 above zero)",
             xy=(0.090, 97), xytext=(0.108, 101), ha="left", va="top",
             fontsize=8, linespacing=1.4,
             arrowprops=dict(arrowstyle="-", lw=0.6, color="0.4",
                             shrinkA=3, shrinkB=3))
axa.annotate("Mann-Whitney $U$, one-sided, asymptotic:  "
             "$p = 1.21\\times10^{-6}$",
             xy=(0.455, 3), ha="right", va="bottom", fontsize=7.5, color="0.20")

fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote %s" % OUT)
