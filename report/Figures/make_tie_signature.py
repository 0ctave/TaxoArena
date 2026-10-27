# Generates the tie-signature dumbbell figure (V-2 of the figure review):
# per domain, the judge's tie rate on key-decidable against key-undecidable
# comparisons, both arms, settled batch.
#
# The claim: abstention nearly doubles exactly where the key stops
# discriminating, in all eight domains, in both arms from different bases.
# Eight dumbbells all leaning the same way is the one-glance form of the two
# tables it complements (tab:tie-by-key, tab:c5-decisiveness).
#
# REAL DATA ONLY. Published pooled rates (MAIN 13.0->24.0, C5 10.9) are
# asserted before drawing; on mismatch the script raises and emits no PDF.
#
# Run from anywhere:  python report/Figures/make_tie_signature.py
import os
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "tie_signature.pdf")
CACHE = os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db")
DOMS = [("math", "mathematics"), ("physics", "physics"), ("law", "law"),
        ("engineering", "engineering"), ("psychology", "psychology"),
        ("philosophy", "philosophy"), ("history", "history"),
        ("cs", "computer science")]

PUB_MAIN_DEC = 13.0
PUB_MAIN_UND = 24.0
PUB_C5_DEC = 10.9

cc = sqlite3.connect("file:%s?mode=ro" % CACHE.replace(os.sep, "/"), uri=True)
rows = []   # (label, main_dec, main_und, c5_dec, c5_und)
tot = {("MAIN", True): [0, 0], ("MAIN", False): [0, 0],
       ("C5", True): [0, 0], ("C5", False): [0, 0]}
for slug, label in DOMS:
    db = os.path.join(ROOT, "experiment_results", "r8", slug,
                      "ratings_r8_%s.db" % slug).replace(os.sep, "/")
    c = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    vals = {}
    for cond in ("MAIN", "C5"):
        rs = list(c.execute("select eval_question_id,model_a,model_b,is_tie"
                            " from match_history where condition=?", (cond,)))
        ms = sorted({m for r in rs for m in (r[1], r[2])})
        qs = sorted({str(r[0]) for r in rs})
        ph = ",".join("?" * len(ms))
        qh = ",".join("?" * len(qs))
        corr = {(str(q), m): bool(o) for q, m, o in cc.execute(
            "select question_id,model_name,is_correct from eval_results"
            " where model_name in (%s) and question_id in (%s)" % (ph, qh),
            ms + qs)}
        d = [0, 0]
        u = [0, 0]
        for q, a, b, t in rs:
            ca, cb = corr.get((str(q), a)), corr.get((str(q), b))
            if ca is None or cb is None:
                continue
            tgt = d if ca != cb else u
            tgt[0] += 1
            tgt[1] += bool(t)
        vals[cond] = (100.0 * d[1] / d[0], 100.0 * u[1] / u[0])
        tot[(cond, True)][0] += d[0]
        tot[(cond, True)][1] += d[1]
        tot[(cond, False)][0] += u[0]
        tot[(cond, False)][1] += u[1]
    rows.append((label, *vals["MAIN"], *vals["C5"]))

pool = {k: 100.0 * v[1] / v[0] for k, v in tot.items()}
for got, pub, name in ((pool[("MAIN", True)], PUB_MAIN_DEC, "MAIN dec"),
                       (pool[("MAIN", False)], PUB_MAIN_UND, "MAIN und"),
                       (pool[("C5", True)], PUB_C5_DEC, "C5 dec")):
    if abs(got - pub) > 0.05:
        raise SystemExit("MISMATCH %s: %.2f vs published %.1f"
                         % (name, got, pub))
if not all(r[2] > r[1] and r[4] > r[3] for r in rows):
    raise SystemExit("MISMATCH: direction does not hold in all domains/arms")
print("verified: pooled MAIN %.1f->%.1f, C5 %.1f->%.1f; direction 8/8 both arms"
      % (pool[("MAIN", True)], pool[("MAIN", False)],
         pool[("C5", True)], pool[("C5", False)]))

plt.rcParams.update({
    "font.size": 9, "axes.labelsize": 9,
    "font.family": "serif", "pdf.fonttype": 42,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False,
})
fig, ax = plt.subplots(figsize=(6.6, 3.6))

order = rows + [("all eight domains",
                 pool[("MAIN", True)], pool[("MAIN", False)],
                 pool[("C5", True)], pool[("C5", False)])]
ys = list(range(len(order), 0, -1))
for y, (label, md, mu, cd, cu) in zip(ys, order):
    em = (label == "all eight domains")
    lw = 1.8 if em else 1.1
    ax.plot([md, mu], [y + 0.12, y + 0.12], color="black", lw=lw, zorder=2)
    ax.plot([md], [y + 0.12], "o", ms=5 if em else 4, mfc="black",
            mec="black", zorder=3)
    ax.plot([mu], [y + 0.12], ">", ms=5.5 if em else 4.5, mfc="black",
            mec="black", zorder=3)
    ax.plot([cd, cu], [y - 0.18, y - 0.18], color="0.55", lw=lw, zorder=2)
    ax.plot([cd], [y - 0.18], "o", ms=5 if em else 4, mfc="white",
            mec="0.4", mew=1.0, zorder=3)
    ax.plot([cu], [y - 0.18], ">", ms=5.5 if em else 4.5, mfc="white",
            mec="0.4", mew=1.0, zorder=3)
    # ratio labels in a fixed right-hand column so they align vertically.
    # Rounding rule harmonized with tab:tie-by-key: the table's ratio
    # column is the quotient of the 0.1pp-rounded rates (history:
    # 18.3/12.6 -> 1.5), so the figure divides the same rounded rates.
    ax.annotate("%.1f$\\times$" % (round(mu, 1) / round(md, 1)), xy=(31.2, y),
                va="center", fontsize=7.5,
                fontweight="bold" if em else "normal", color="0.15")

# a light rule separating the pooled row from the eight domain rows
ax.axhline(1.5, color="0.85", lw=0.7, zorder=1)

# domain labels as y tick labels (outside the axes), so the x axis can
# start at 0 instead of reaching into negative tie rates to make room
ax.set_yticks(ys)
ax.set_yticklabels([o[0] for o in order])
ax.tick_params(axis="y", length=0)
for tl, (label, *_ ) in zip(ax.get_yticklabels(), order):
    if label == "all eight domains":
        tl.set_fontweight("bold")
        tl.set_fontsize(8.5)
    else:
        tl.set_fontsize(8)
ax.set_xlim(0, 34)
ax.set_xticks([0, 5, 10, 15, 20, 25, 30])
ax.set_ylim(0.3, len(order) + 0.9)
ax.set_xlabel("tie rate (%): key-decidable comparisons "
              "$\\rightarrow$ key-undecidable")
ax.annotate("cell-scoped arm (filled)   /   generic arm (hollow)",
            xy=(0.995, 1.001), xycoords="axes fraction", ha="right",
            va="bottom", fontsize=7.5, color="0.3")

fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote %s" % OUT)
