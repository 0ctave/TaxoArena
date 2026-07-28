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
BLUE = "#2a78d6"
BLUE_LIGHT = "#cde2fb"
ORANGE = "#eb6834"
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Latin Modern Roman", "CMU Serif", "Times New Roman",
                   "DejaVu Serif"],
    "font.size": 9,
    "pdf.fonttype": 42,
    "text.color": INK,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
})

fig, ax = plt.subplots(figsize=(5.9, 2.9))
ax.set_axisbelow(True)
ax.grid(axis="y", color=GRID, lw=0.6)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)

bins = list(range(50, 410, 10))
counts, edges, patches = ax.hist(
    sizes, bins=bins, color=BLUE, edgecolor="white", linewidth=0.8, zorder=3)

# highlight the single below-floor leaf (n = 54): it is one unit of the first
# bin -- redraw that unit in orange so the exception is visible.
first_bin = next(i for i in range(len(edges) - 1)
                 if edges[i] <= below[0] < edges[i + 1])
ax.bar(edges[first_bin], 1, width=edges[first_bin + 1] - edges[first_bin],
       align="edge", color=ORANGE, edgecolor="white", linewidth=0.8, zorder=4)

# IQR band and median / floor reference lines.
ax.axvspan(q1, q3, color=BLUE_LIGHT, alpha=0.45, zorder=1)
ax.axvline(med, color=INK, lw=1.1, zorder=5)
ax.axvline(N_MIN, color=ORANGE, lw=1.1, ls=(0, (4, 3)), zorder=5)

ymax = counts.max()
ax.set_ylim(0, ymax * 1.28)
ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
ax.text(med + 4, ymax * 1.24, f"median {med:.0f}",
        ha="left", va="top", fontsize=8, color=INK)
ax.text(q3 + 4, ymax * 1.02, f"IQR [{q1:.0f}, {q3:.0f}]",
        ha="left", va="top", fontsize=8, color=MUTED)
ax.text(N_MIN - 3.5, ymax * 0.66, f"birth floor $n_\\mathrm{{min}}$ = {N_MIN}",
        ha="right", va="center", fontsize=8, color=ORANGE, rotation=90)
ax.text(edges[first_bin] - 2, 0.5, str(below[0]), ha="right", va="center",
        fontsize=7.5, color=ORANGE)
ax.text(232, ymax * 0.40,
        f"one leaf sits below the floor\n({below[0]} queries, in orange)",
        ha="left", va="bottom", fontsize=8, color=INK)
ax.text(sizes[-1], 1.6, f"max {sizes[-1]}", ha="center", va="bottom",
        fontsize=7.5, color=MUTED)

ax.set_xlim(40, 410)
ax.set_xlabel("queries per leaf (construction assignment)")
ax.set_ylabel("leaves")
ax.set_title(f"{len(sizes)} leaves, frozen snapshot", fontsize=9,
             loc="left", pad=8)
ax.tick_params(length=0)

fig.tight_layout(pad=0.4)
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
