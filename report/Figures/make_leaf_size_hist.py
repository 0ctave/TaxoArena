# Generates the leaf-size histogram (frozen snapshot, 87 leaves) for the
# thesis appendix.
#
# REAL DATA ONLY. Leaf query counts are read from the frozen snapshot's graph
# in snapshots.db (snapshot 20260727_042523, 154 nodes / 87 leaves) and every
# published statistic is asserted before any drawing happens; on mismatch the
# script raises and emits no PDF.
#
# Published values reproduced here:
#   87 leaves, median 88, IQR [71, 118], min 54, max 396;
#   exactly one leaf below the birth floor n_min = 55.
# Quartiles: statistics.quantiles(..., n=4) (exclusive method), which is the
# convention that yields the published [71, 118].
#
# Run from anywhere:  python report/Figures/make_leaf_size_hist.py
import json
import os
import sqlite3
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "leaf_size_hist.pdf")
SNAP_DB = os.path.join(ROOT, "snapshots.db")
SNAP_ID = "20260727_042523_Headless_Run_Auto_ge"

N_MIN = 55            # birth floor (minClusterSize)

# ------------------------------------------------------------------ recompute
db = sqlite3.connect(SNAP_DB)
graph_json, = db.execute(
    "select graph from snapshots where id = ?", (SNAP_ID,)).fetchone()
db.close()
g = json.loads(graph_json)
nodes = g["nodes"]
sizes = sorted(len(n["queryIds"]) for n in nodes if not n.get("childIds"))

med = statistics.median(sizes)
q1, _, q3 = statistics.quantiles(sizes, n=4)          # exclusive method
below = [s for s in sizes if s < N_MIN]

# ---------------------------------------------------------------- verification
assert len(nodes) == 154, f"expected 154 nodes, found {len(nodes)}"
assert len(sizes) == 87, f"expected 87 leaves, found {len(sizes)}"
assert med == 88, f"median {med} != published 88"
assert (q1, q3) == (71, 118), f"IQR [{q1}, {q3}] != published [71, 118]"
assert sizes[0] == 54 and sizes[-1] == 396, (
    f"min/max {sizes[0]}/{sizes[-1]} != published 54/396")
assert below == [54], f"below-floor leaves {below} != published [54]"

print("VERIFIED against published values:")
print(f"  snapshot {SNAP_ID}: {len(nodes)} nodes, {len(sizes)} leaves")
print(f"  median {med:.0f}, IQR [{q1:.0f}, {q3:.0f}], "
      f"min {sizes[0]}, max {sizes[-1]}")
print(f"  leaves below the birth floor n_min = {N_MIN}: {below}")

# ---------------------------------------------------------------------- plot
# GREYSCALE ONLY -- the thesis prints in monochrome. The one exceptional leaf
# is distinguished by a hatch and a leader label, not by hue.
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
    "font.size": 9, "pdf.fonttype": 42,
})

fig, ax = plt.subplots(figsize=(6.4, 2.9))
ax.set_axisbelow(True)
ax.grid(axis="y", color="0.90", lw=0.6)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)

# Log-spaced bins so the long right tail is not compressed into an empty
# two-thirds of a linear axis (figure-review fix). The first bin [50, 55)
# is exactly the below-floor leaf; every later edge is geometric from the
# birth floor to 400.
bins = [50.0] + [N_MIN * (400.0 / N_MIN) ** (i / 14.0) for i in range(15)]
counts, edges, _ = ax.hist(sizes, bins=bins, color="0.72", edgecolor="white",
                           linewidth=0.8, zorder=3)
assert counts[0] == len(below) == 1, "first bin must be the below-floor leaf"

# the single below-floor leaf (n = 54): redraw its unit hatched so the
# exception is visible without colour.
ax.bar(edges[0], 1, width=edges[1] - edges[0], align="edge",
       facecolor="white", edgecolor="black", hatch="////", linewidth=0.9,
       zorder=4)

# reference lines: the birth floor (dashed) and the median (solid)
ax.axvline(N_MIN, color="black", lw=1.0, ls=(0, (4, 3)), zorder=5)
ax.axvline(med, color="black", lw=1.2, zorder=5)

ymax = counts.max()
ax.set_ylim(0, ymax * 1.30)
ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
ax.annotate(f"median {med:.0f}", xy=(med, ymax * 1.26), xytext=(4, 0),
            textcoords="offset points", ha="left", va="top", fontsize=8)
# two annotations only (figure-review fix); median/IQR/provenance live in
# the caption
ax.annotate(f"one leaf (hatched) ended below the birth floor\n"
            f"(dashed, $n_\\mathrm{{min}} = {N_MIN}$) after later merges: "
            f"{below[0]} queries",
            xy=(N_MIN, ymax * 1.055), xytext=(150, ymax * 1.06),
            ha="left", va="center", fontsize=8, linespacing=1.45,
            arrowprops=dict(arrowstyle="-", lw=0.7, color="0.35",
                            shrinkA=3, shrinkB=3))
ax.annotate(f"the largest leaf holds {sizes[-1]} queries —\n"
            f"{sizes[-1] / med:.1f}$\\times$ the median, so the arena's\n"
            f"per-cell power is far from uniform",
            xy=(sizes[-1], 1.4), xytext=(150, ymax * 0.55),
            ha="left", va="center", fontsize=8, linespacing=1.45,
            arrowprops=dict(arrowstyle="-", lw=0.7, color="0.35",
                            shrinkA=3, shrinkB=3))

ax.set_xscale("log")
ax.set_xlim(47, 430)
ax.set_xticks([50, 70, 100, 140, 200, 280, 400])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
ax.set_xlabel("queries assigned to the leaf at construction (log scale)")
ax.set_ylabel("number of leaves")
ax.tick_params(length=0)

fig.subplots_adjust(left=0.098, right=0.985, top=0.930, bottom=0.165)
fig.savefig(OUT)
print("wrote", OUT)
