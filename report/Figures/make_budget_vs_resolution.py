# Generates the budget-vs-resolution strip (V-3 of the figure review):
# achieved comparisons per model pair, one dot per cell, on a log axis
# against the ~143-per-pair resolution requirement, with identification
# cost (7-10 comparisons per cell) as the counterpoint.
#
# The claim of sec:res-cost: identification is nearly free; resolution is
# two orders of magnitude out of reach at this budget, in every cell of
# every domain. On a log axis the gap is one visible gulf.
#
# Interval policy: no CIs are drawn anywhere (per the thesis's no-interval
# rule; the BT variance machinery was repaired late and no interval is
# reported in the document).
#
# REAL DATA ONLY. Published bounds (52 cells; median comparisons/pair by
# domain within 1.6-5.0; identification 7-10) are asserted before drawing.
#
# Run from anywhere:  python report/Figures/make_budget_vs_resolution.py
import os
import sqlite3
import statistics
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "budget_vs_resolution.pdf")
DOMS = [("math", "mathematics"), ("physics", "physics"), ("law", "law"),
        ("engineering", "engineering"), ("psychology", "psychology"),
        ("philosophy", "philosophy"), ("history", "history"),
        ("cs", "computer science")]
PAIRS = 28
REQUIRED = 143
PUB_CELLS = 52
PUB_MED_LO, PUB_MED_HI = 1.6, 5.1
PUB_ID_LO, PUB_ID_HI = 7, 10

per_dom = {}
ident = []
n_cells = 0
for slug, label in DOMS:
    db = os.path.join(ROOT, "experiment_results", "r8", slug,
                      "ratings_r8_%s.db" % slug).replace(os.sep, "/")
    c = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    cells = defaultdict(list)
    for rid, nid, a, b in c.execute(
            "select rowid,node_id,model_a,model_b from match_history"
            " where condition='MAIN' order by rowid"):
        cells[nid].append((a, b))
    vals = []
    for nid, seq in cells.items():
        n_cells += 1
        vals.append(len(seq) / PAIRS)
        parent = {}

        def find(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        got = set()
        reached = None
        for i, (a, b) in enumerate(seq, 1):
            got.add(a)
            got.add(b)
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
            if len(got) == 8 and len({find(m) for m in got}) == 1:
                reached = i
                break
        ident.append(reached)
    per_dom[label] = vals

meds = [statistics.median(v) for v in per_dom.values()]
if n_cells != PUB_CELLS:
    raise SystemExit("MISMATCH: %d cells, published %d" % (n_cells, PUB_CELLS))
if not (PUB_MED_LO - 0.05 <= min(meds) and max(meds) <= PUB_MED_HI + 0.05):
    raise SystemExit("MISMATCH: domain medians %.1f-%.1f, published %.1f-%.1f"
                     % (min(meds), max(meds), PUB_MED_LO, PUB_MED_HI))
if None in ident or min(ident) < PUB_ID_LO or max(ident) > PUB_ID_HI:
    raise SystemExit("MISMATCH: identification %s-%s, published %d-%d"
                     % (min(ident), max(ident), PUB_ID_LO, PUB_ID_HI))
print("verified: %d cells, domain medians %.1f-%.1f cmp/pair,"
      " identification %d-%d comparisons"
      % (n_cells, min(meds), max(meds), min(ident), max(ident)))

plt.rcParams.update({
    "font.size": 9, "axes.labelsize": 9,
    "font.family": "serif", "pdf.fonttype": 42,
    "axes.spines.top": False, "axes.spines.right": False,
})
fig, ax = plt.subplots(figsize=(6.6, 3.4))

labels = list(per_dom)
# deterministic vertical stagger: sorted values get cycling offsets, so
# near-equal cells within a domain no longer print on top of each other
OFFS = [0.0, 0.13, -0.13, 0.26, -0.26]
for i, lab in enumerate(labels):
    y = len(labels) - i
    for k, v in enumerate(sorted(per_dom[lab])):
        ax.plot(v, y + OFFS[k % len(OFFS)], "o", ms=4, mfc="black",
                mec="black", alpha=0.75, zorder=3)
ax.axvline(REQUIRED, color="black", lw=1.2, ls=(0, (5, 3)), zorder=2)
ax.annotate("$\\sim$%d comparisons per pair\nneeded to resolve an\n"
            "adjacent pair" % REQUIRED,
            xy=(REQUIRED, len(labels) + 0.35), xytext=(-8, 0),
            textcoords="offset points", ha="right", va="top", fontsize=7.5,
            linespacing=1.4)
# identification band, in per-pair units (7-10 comparisons / 28 pairs)
ax.axvspan(min(ident) / PAIRS, max(ident) / PAIRS, color="0.90", zorder=0)
ax.annotate("identification:\nthe whole cell connects\nwithin %d-%d "
            "comparisons" % (min(ident), max(ident)),
            xy=(min(ident) / PAIRS * 1.05, 1.0), ha="left", va="bottom",
            fontsize=7.5, linespacing=1.4, color="0.35")

ax.set_xscale("log")
ax.set_yticks([len(labels) - i for i in range(len(labels))])
ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel("comparisons per model pair achieved in the cell (log scale);"
              " one dot per cell")
ax.set_xlim(0.2, 260)

fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote %s" % OUT)
