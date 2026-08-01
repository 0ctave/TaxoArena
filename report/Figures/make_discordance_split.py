# Generates the discordance-split figure (V-8 of the figure review): the RQ2
# item-level evidence in one view. Left panel: the eight per-domain tie-rate
# slopes (cell-scoped arm always above the generic arm). Right panel: the
# 11/26 split of both-committed discordant comparisons with its exact
# binomial 95% interval.
#
# The claim: the robust arm difference is decisiveness (8/8 domains); the
# accuracy difference conditional on committing rests on 37 comparisons and
# is significant pooled (p = 0.020) and in no single domain.
#
# REAL DATA ONLY. Published values asserted before drawing: per-domain tie
# rates match tab:c5-decisiveness to 0.1pp; discordant split is 11/26;
# two-sided exact binomial p = 0.020 (+-0.001).
#
# Run from anywhere:  python report/Figures/make_discordance_split.py
import math
import os
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "discordance_split.pdf")
CACHE = os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db")
DOMS = [("math", "mathematics"), ("physics", "physics"), ("law", "law"),
        ("engineering", "engineering"), ("psychology", "psychology"),
        ("philosophy", "philosophy"), ("history", "history"),
        ("cs", "computer science")]
PUB_TIES = {"math": (11.4, 9.5), "physics": (9.9, 7.9), "law": (15.3, 14.1),
            "engineering": (14.7, 10.7), "psychology": (12.5, 11.2),
            "philosophy": (14.8, 11.5), "history": (12.6, 9.4),
            "cs": (14.5, 11.7)}
PUB_MAIN_ONLY = 11
PUB_GEN_ONLY = 26
PUB_P = 0.020

cc = sqlite3.connect("file:%s?mode=ro" % CACHE.replace(os.sep, "/"), uri=True)
ties = {}
mo = co = 0
for slug, label in DOMS:
    db = os.path.join(ROOT, "experiment_results", "r8", slug,
                      "ratings_r8_%s.db" % slug).replace(os.sep, "/")
    c = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    A = {}
    for cond in ("MAIN", "C5"):
        for q, a, b, w, t in c.execute(
                "select eval_question_id,model_a,model_b,winner,is_tie"
                " from match_history where condition=?", (cond,)):
            A.setdefault((str(q), a, b), {})[cond] = (w, bool(t))
    ms = sorted({m for (q, a, b) in A for m in (a, b)})
    qs = sorted({q for (q, a, b) in A})
    ph = ",".join("?" * len(ms))
    qh = ",".join("?" * len(qs))
    corr = {(str(q), m): bool(o) for q, m, o in cc.execute(
        "select question_id,model_name,is_correct from eval_results"
        " where model_name in (%s) and question_id in (%s)" % (ph, qh),
        ms + qs)}
    dm = [0, 0]
    dc = [0, 0]
    for (q, a, b), d in A.items():
        if "MAIN" not in d or "C5" not in d:
            continue
        ca, cb = corr.get((q, a)), corr.get((q, b))
        if ca is None or cb is None or ca == cb:
            continue
        g = a if ca else b
        wM, tM = d["MAIN"]
        wC, tC = d["C5"]
        dm[0] += 1
        dm[1] += tM
        dc[0] += 1
        dc[1] += tC
        okm = (not tM) and wM == g
        okc = (not tC) and wC == g
        if tM or tC:
            continue
        if okm and not okc:
            mo += 1
        if okc and not okm:
            co += 1
    ties[slug] = (100.0 * dm[1] / dm[0], 100.0 * dc[1] / dc[0])

for slug, (m, c5) in ties.items():
    pm, pc = PUB_TIES[slug]
    if abs(m - pm) > 0.11 or abs(c5 - pc) > 0.11:
        raise SystemExit("MISMATCH ties %s: %.1f/%.1f vs published %.1f/%.1f"
                         % (slug, m, c5, pm, pc))
if (mo, co) != (PUB_MAIN_ONLY, PUB_GEN_ONLY):
    raise SystemExit("MISMATCH discordant: %d/%d vs %d/%d"
                     % (mo, co, PUB_MAIN_ONLY, PUB_GEN_ONLY))
n = mo + co
p = min(sum(math.comb(n, i) for i in range(min(mo, co) + 1)) / 2.0 ** n * 2, 1)
if abs(p - PUB_P) > 1e-3:
    raise SystemExit("MISMATCH p: %.4f vs %.3f" % (p, PUB_P))
# exact (Clopper-Pearson) 95% interval on the generic-only share
share = co / n
lo, hi = 0.0, 1.0
for _ in range(60):
    mid = (lo + hi) / 2
    tail = sum(math.comb(n, k) * mid ** k * (1 - mid) ** (n - k)
               for k in range(co, n + 1))
    lo, hi = (mid, hi) if tail < 0.025 else (lo, mid)
ci_lo = lo
lo, hi = 0.0, 1.0
for _ in range(60):
    mid = (lo + hi) / 2
    tail = sum(math.comb(n, k) * mid ** k * (1 - mid) ** (n - k)
               for k in range(0, co + 1))
    lo, hi = (lo, mid) if tail < 0.025 else (mid, hi)
ci_hi = hi
print("verified: ties all domains, discordant %d/%d, p=%.3f,"
      " generic share %.2f [%.2f, %.2f]" % (mo, co, p, share, ci_lo, ci_hi))

plt.rcParams.update({
    "font.size": 9, "axes.labelsize": 9,
    "font.family": "serif", "pdf.fonttype": 42,
    "axes.spines.top": False, "axes.spines.right": False,
})
fig, (axl, axr) = plt.subplots(1, 2, figsize=(6.6, 3.0),
                               gridspec_kw={"width_ratios": [1.15, 1.0]})

# left: tie-rate slopes
for slug, label in DOMS:
    m, c5 = ties[slug]
    axl.plot([0, 1], [m, c5], color="0.3", lw=1.0, zorder=2)
    axl.plot([0], [m], "o", ms=4, mfc="black", mec="black", zorder=3)
    axl.plot([1], [c5], "o", ms=4, mfc="white", mec="0.4", mew=1.0, zorder=3)
axl.set_xlim(-0.35, 1.35)
axl.set_xticks([0, 1])
axl.set_xticklabels(["cell-scoped", "generic"])
# name the two extreme domains so the unlabeled slopes have anchors
axl.annotate("law", xy=(1.06, ties["law"][1]), va="center", fontsize=7,
             color="0.3")
axl.annotate("physics", xy=(1.06, ties["physics"][1]), va="center",
             fontsize=7, color="0.3")
axl.set_ylabel("tie rate on decidable comparisons (%)")
axl.set_title("(a) the arm difference that is robust:\n"
              "decisiveness, all eight domains", fontsize=8.5, loc="left")

# right: the discordant split as a plain two-bar comparison (the earlier
# diverging bar put a count on a negative axis and read as "a number, not
# a picture"). Arm identity keeps the document-wide convention:
# cell-scoped = filled, generic = hollow.
axr.barh([2], [mo], color="0.2", height=0.55, zorder=2)
axr.barh([1], [co], color="white", edgecolor="0.35", lw=1.0, height=0.55,
         zorder=2)
axr.text(mo + 0.8, 2, "%d" % mo, va="center", ha="left", fontsize=8,
         color="0.15")
axr.text(ci_hi * n + 1.0, 1, "%d" % co, va="center", ha="left", fontsize=8,
         color="0.15")
# exact binomial 95% CI of the generic-only count, in counts
axr.plot([ci_lo * n, ci_hi * n], [1, 1], color="black", lw=1.1, zorder=3)
axr.plot([ci_lo * n] * 2, [0.86, 1.14], color="black", lw=1.1, zorder=3)
axr.plot([ci_hi * n] * 2, [0.86, 1.14], color="black", lw=1.1, zorder=3)
axr.axvline(n / 2, color="0.3", lw=0.8, ls=":", zorder=1)
axr.annotate("even split", xy=(n / 2, 2.55), ha="center", va="bottom",
             fontsize=7, color="0.3",
             bbox=dict(fc="white", ec="none", pad=1.2))
axr.annotate("whisker = exact 95%% CI of the generic-only\n"
             "count; $p = %.3f$ against the even split" % p,
             xy=(0, 0.30), ha="left", va="top", fontsize=7.5,
             linespacing=1.4, color="0.25")
axr.set_yticks([2, 1])
axr.set_yticklabels(["cell-scoped-\nonly correct", "generic-only\ncorrect"],
                    fontsize=8)
axr.tick_params(axis="y", length=0)
axr.set_ylim(-0.55, 2.95)
axr.set_xlim(0, n + 3)
axr.set_xticks([0, 10, 20, 30])
axr.spines["left"].set_visible(False)
# two lines: a one-line label was wider than the panel and matplotlib's
# tight bbox under-measures it, clipping the right edge of the PDF
axr.set_xlabel("both-committed discordant\ncomparisons ($n = %d$)" % n)
axr.set_title("(b) the accuracy difference is thin:\n"
              "significant pooled, in no single domain", fontsize=8.5,
              loc="left")

fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote %s" % OUT)
