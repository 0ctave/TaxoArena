# Generates the settled-batch validity scatter (V-1 of the figure review):
# one point per (domain, model pair), the key's accuracy gap against the
# arena's Bradley-Terry score difference, with the decidability band drawn.
#
# The claim it carries: the arena's ordering tracks the key wherever the key
# can see, and all four misses sit where the key is nearly indifferent. The
# table (tab:settled-recovery) proves the count; this proves the shape.
#
# REAL DATA ONLY. The published counts (224 pairs, 200 decidable, 196
# recovered, 4 misses) are asserted before drawing; on mismatch the script
# raises and emits no PDF.
#
# Sources: experiment_results/r8/<dom>/ratings_r8_<dom>.db (match_history,
# MAIN) and mmlu_pro_dataset_cache_v2.db (eval_results, roster-restricted,
# question_id joined as TEXT -- the id-space traps are real).
#
# Run from anywhere:  python report/Figures/make_settled_validity_scatter.py
import math
import os
import sqlite3
import itertools

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "settled_validity_scatter.pdf")
CACHE = os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db")
DOMS = ["math", "physics", "law", "engineering",
        "psychology", "philosophy", "history", "cs"]

PUB_PAIRS = 224
PUB_DECIDABLE = 200
PUB_RECOVERED = 196
PUB_MISSES = 4


def bt(models, wins, it=900):
    idx = {m: i for i, m in enumerate(models)}
    K = len(models)
    w = [[0.0] * K for _ in range(K)]
    for (a, b), v in wins.items():
        w[idx[a]][idx[b]] += v
    s = [0.0] * K
    for _ in range(it):
        new = list(s)
        for i in range(K):
            Wi = sum(w[i])
            if Wi <= 0:
                continue
            den = sum((w[i][j] + w[j][i]) / (math.exp(s[i]) + math.exp(s[j]))
                      for j in range(K) if j != i and (w[i][j] + w[j][i]) > 0)
            if den > 0:
                new[i] = math.log(Wi / den)
        mean = sum(new) / K
        new = [x - mean for x in new]
        if max(abs(a - b) for a, b in zip(new, s)) < 1e-12:
            return dict(zip(models, new))
        s = new
    return dict(zip(models, s))


cc = sqlite3.connect("file:%s?mode=ro" % CACHE.replace(os.sep, "/"), uri=True)
pts = []           # (key_gap, signed_theta_diff, decidable, domain)
for slug in DOMS:
    db = os.path.join(ROOT, "experiment_results", "r8", slug,
                      "ratings_r8_%s.db" % slug).replace(os.sep, "/")
    c = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    rs = list(c.execute("select eval_question_id,model_a,model_b,winner,is_tie"
                        " from match_history where condition='MAIN'"))
    ms = sorted({m for r in rs for m in (r[1], r[2])})
    qs = sorted({str(r[0]) for r in rs})
    N = len(qs)
    ph = ",".join("?" * len(ms))
    qh = ",".join("?" * len(qs))
    acc = {m: ok / n for m, n, ok in cc.execute(
        "select model_name,count(*),sum(is_correct) from eval_results"
        " where model_name in (%s) and question_id in (%s)"
        " group by model_name" % (ph, qh), ms + qs)}
    wins = {}
    for q, a, b, w, t in rs:
        if t:
            wins[(a, b)] = wins.get((a, b), 0) + .5
            wins[(b, a)] = wins.get((b, a), 0) + .5
        else:
            lo = b if w == a else a
            wins[(w, lo)] = wins.get((w, lo), 0) + 1.
    th = bt(ms, wins)
    for a, b in itertools.combinations(ms, 2):
        # orient so the key's better model is first: agreement = positive y
        hi, lo_ = (a, b) if acc[a] >= acc[b] else (b, a)
        gap = acc[hi] - acc[lo_]
        dec = gap > 2 * math.sqrt(acc[hi] * (1 - acc[hi]) / N
                                  + acc[lo_] * (1 - acc[lo_]) / N)
        pts.append((gap, th[hi] - th[lo_], dec, slug))

n_dec = sum(1 for p in pts if p[2])
n_rec = sum(1 for p in pts if p[2] and p[1] > 0)
if len(pts) != PUB_PAIRS or n_dec != PUB_DECIDABLE or n_rec != PUB_RECOVERED:
    raise SystemExit("MISMATCH: pairs=%d decidable=%d recovered=%d,"
                     " published %d/%d/%d"
                     % (len(pts), n_dec, n_rec,
                        PUB_PAIRS, PUB_DECIDABLE, PUB_RECOVERED))
misses = [p for p in pts if p[2] and p[1] <= 0]
if len(misses) != PUB_MISSES:
    raise SystemExit("MISMATCH: %d misses, published %d"
                     % (len(misses), PUB_MISSES))
print("verified: %d pairs, %d decidable, %d recovered, %d misses"
      % (len(pts), n_dec, n_rec, len(misses)))
print("  miss gaps: %s" % sorted(round(p[0], 3) for p in misses))
print("  smallest decidable-gap quartile bound: %.3f"
      % sorted(p[0] for p in pts if p[2])[n_dec // 4])

plt.rcParams.update({
    "font.size": 9, "axes.labelsize": 9,
    "font.family": "serif", "pdf.fonttype": 42,
    "axes.spines.top": False, "axes.spines.right": False,
})
fig, ax = plt.subplots(figsize=(6.6, 4.0))

# The decidability boundary is per-domain (it depends on N and the accuracy
# levels), so a single band cannot be exact; shade up to the largest gap that
# was UNdecidable anywhere, and state the convention in the caption.
band = max(p[0] for p in pts if not p[2])
ax.axvspan(0, band, color="0.92", zorder=0)
ax.axhline(0, color="0.45", lw=0.8, zorder=1)

ACCENT = "#3B6EA5"  # single muted-blue accent; misses stay identifiable in
                    # grayscale (only filled points at y <= 0, each labeled)
miss_set = {(p[0], p[1]) for p in misses}
for gap, dth, dec, dom in pts:
    if (gap, dth) in miss_set:
        continue  # drawn separately below, in the accent color
    if dec:
        ax.plot(gap, dth, "o", ms=3.4, mfc="black", mec="black", zorder=3)
    else:
        # undecidable pairs as small light-grey diamonds: the document
        # reserves filled-vs-hollow for arm identity (figs. tie-signature
        # and discordance-split), so decidability uses shape + value
        ax.plot(gap, dth, "D", ms=2.8, mfc="0.80", mec="0.45", mew=0.6,
                zorder=2)
# The four misses: accent fill, and leader-line labels stacked in the empty
# lower-middle region so they cannot collide (same-offset labels did).
label_ys = [-0.05, -0.35, -0.65, -0.95]
for (gap, dth, dec, dom), ylab in zip(
        sorted(misses, key=lambda p: -p[1]), label_ys):
    ax.plot(gap, dth, "o", ms=4.2, mfc=ACCENT, mec="white", mew=0.6,
            zorder=4)
    ax.annotate(dom, xy=(gap, dth), xytext=(0.26, ylab),
                textcoords="data", ha="left", va="center", fontsize=7,
                color="0.15", zorder=4,
                arrowprops=dict(arrowstyle="-", lw=0.6, color="0.55",
                                shrinkA=2, shrinkB=3))

ax.set_xlabel("ground-truth accuracy gap of the pair, $|p_1 - p_2|$")
ax.set_ylabel("arena score difference $\\theta_{\\mathrm{better}} - "
              "\\theta_{\\mathrm{worse}}$")
ax.annotate("undecidable\nsomewhere at\nthis gap", xy=(band * 0.45, 5.4),
            ha="center", va="top", fontsize=7.5, color="0.35",
            linespacing=1.4)
ax.annotate("$\\uparrow$ agreement with the key", xy=(0.98, 0.97),
            xycoords="axes fraction", ha="right", va="top", fontsize=8,
            color="0.25")
ax.annotate("the four misses, all at the\nsmallest decidable gaps",
            xy=(0.98, 0.05), xycoords="axes fraction", ha="right",
            va="bottom", fontsize=8, color="0.25", linespacing=1.4)

fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote %s" % OUT)
