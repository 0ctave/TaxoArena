# Generates the whole frozen taxonomy as ONE labelled dendrogram on ONE page
# (tree_full.pdf): every anchor, every leaf, nothing else.
#
# WHAT THIS DELIBERATELY OMITS. No query counts, no depth axis, no membership
# figures, no node ids. The figure carries structure and names only -- the
# quantities live in the icicle (make_frozen_tree.py) and in the prose.
#
# HOW 87 LEAVES FIT ON ONE PAGE. The binding constraint is vertical: 87 leaf
# rows inside a 582pt \textheight leaves ~6pt per row once the caption is
# allowed for, so the labels must be set at 5.2pt. That is small, but it also
# solves the horizontal problem -- the 81-character longest label needs ~205pt
# at 5.2pt against ~215pt of available label column, where at 6.4pt it needed
# more than the whole page width. Shrinking to fit vertically is what makes it
# fit horizontally.
#
# REAL DATA ONLY. The tree is read from the frozen snapshot and every
# structural statistic is asserted before any drawing happens; on mismatch the
# script raises and emits no PDF.
#
# Primary source:
#   snapshots.db, snapshot 20260727_042523_Headless_Run_Auto_ge (read-only)
#
# Run from anywhere:  python report/Figures/make_tree_full.py
import collections
import json
import os
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SNAP_DB = os.path.join(ROOT, "snapshots.db")
SNAP_ID = "20260727_042523_Headless_Run_Auto_ge"
OUT = os.path.join(HERE, "tree_full.pdf")

PUB_NODES = 154
PUB_LEAVES = 87
PUB_ANCHORS = 14
PUB_MAX_DEPTH = 6

PAGE_W = 393.17 / 72.0   # in, = \textwidth exactly, so no \includegraphics scaling
PAGE_H = 7.55            # in, the figure gets nearly the whole \textheight (8.09in);
                         # the caption takes the rest
LEAF_PT = 5.2
ANCHOR_PT = 6.0
LINESPACING = 1.02

db = sqlite3.connect("file:%s?mode=ro" % SNAP_DB.replace(os.sep, "/"), uri=True)
row = db.execute("select graph from snapshots where id = ?", (SNAP_ID,)).fetchone()
if row is None:
    raise SystemExit("snapshot %s not found" % SNAP_ID)
G = json.loads(row[0])
db.close()

nodes = {n["id"]: n for n in G["nodes"]}
root = G["rootId"]
kids = lambda nid: [c for c in nodes[nid]["childIds"] if c in nodes]


def leaves_of(nid):
    if not kids(nid):
        return [nid]
    return [x for c in kids(nid) for x in leaves_of(c)]


anchors = kids(root)
all_leaves = leaves_of(root)

# ---- assertions, before any drawing ------------------------------------
for got, want, what in [(len(nodes), PUB_NODES, "nodes"),
                        (len(all_leaves), PUB_LEAVES, "leaves"),
                        (len(anchors), PUB_ANCHORS, "anchors"),
                        (max(n["depth"] for n in nodes.values()), PUB_MAX_DEPTH,
                         "max depth")]:
    if got != want:
        raise SystemExit("MISMATCH: %s = %d, published %d" % (what, got, want))

# Anchors ordered by size so the figure reads from the most to the least
# subdivided region, matching how the corpus is discussed in the text.
ordered = sorted(anchors, key=lambda a: (-len(leaves_of(a)), nodes[a]["label"]))

plt.rcParams.update({
    "font.size": 7,
    "font.family": "serif",
    "pdf.fonttype": 42,
})

LINE = "#3a3a3a"
TEXT = "#111111"
BAND = "#f0f0f0"

fig = plt.figure(figsize=(PAGE_W, PAGE_H))
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
ax.set_axis_off()

# Vertical layout: leaves at integer rows, in anchor order, with a blank row
# between anchors so the fourteen groups separate without needing rules.
GAP = 0.9
ypos, y = {}, 0.0
blocks = []
for ai, aid in enumerate(ordered):
    lv = leaves_of(aid)
    y0 = y
    for lid in lv:
        ypos[lid] = y
        y += 1.0
    blocks.append((aid, y0 - 0.5, y - 0.5))
    y += GAP
total_rows = y - GAP

X_TREE0 = 0.0                      # dendrogram starts here (anchor node)
X_TREE1 = 1.0                      # ... and ends here; depth is mapped into it
X_LABEL = 1.03


def y_of(nid):
    if nid in ypos:
        return ypos[nid]
    ys = [y_of(c) for c in kids(nid)]
    ypos[nid] = sum(ys) / len(ys)
    return ypos[nid]


texts, anchor_texts = [], []
for ai, (aid, top, bot) in enumerate(blocks):
    y_of(aid)
    lv = leaves_of(aid)
    # Depth is rescaled per anchor so every subtree spans the same width. The
    # absolute depth number is not shown, so a shared scale would only waste
    # horizontal room on the shallow anchors.
    d0 = nodes[aid]["depth"]
    dmax = max(nodes[l]["depth"] for l in lv)
    span = max(dmax - d0, 1)
    xof = lambda nid: X_TREE0 + (nodes[nid]["depth"] - d0) / span * (X_TREE1 - X_TREE0)

    if ai % 2 == 0:
        ax.add_patch(Rectangle((-0.60, top - 0.2), 1.63 + 0.60, (bot - top) + 0.4,
                               facecolor=BAND, edgecolor="none", zorder=0))

    def draw(nid):
        x = xof(nid)
        for c in kids(nid):
            cx, cy = xof(c), ypos[c]
            ax.plot([x, x], [ypos[nid], cy], color=LINE, lw=0.5, zorder=2)
            ax.plot([x, cx], [cy, cy], color=LINE, lw=0.5, zorder=2)
            draw(c)

    draw(aid)

    anchor_texts.append(
        ax.text(-0.04, (top + bot) / 2.0, nodes[aid]["label"], ha="right",
                va="center", fontsize=ANCHOR_PT, fontweight="bold", color=TEXT,
                zorder=3))

    for lid in lv:
        texts.append(ax.text(X_LABEL, ypos[lid], nodes[lid]["label"],
                             ha="left", va="center", fontsize=LEAF_PT,
                             color=TEXT, linespacing=LINESPACING, zorder=3))

ax.set_ylim(total_rows - 0.5, -0.7)

# Fit the x-range to the measured text on BOTH sides. The page is divided into
# three bands as fractions of the axes width: the anchor gutter (a), the
# dendrogram, and the leaf labels (t). Solving for the data limits from the
# measured widths is what keeps the 81-character Physics label on the page --
# fitting the right-hand side alone lands it exactly on the boundary, where the
# final glyph clips.
PAD = 0.02               # keep 2% of the width clear at each edge
ax.set_xlim(-0.62, 3.0)
fig.canvas.draw()
rend = fig.canvas.get_renderer()
W = ax.get_window_extent().width
t = max(x.get_window_extent(renderer=rend).width for x in texts) / W
a = max(x.get_window_extent(renderer=rend).width for x in anchor_texts) / W
tree_frac = 1.0 - a - t - 2 * PAD
if tree_frac <= 0.15:
    raise SystemExit("anchor names need %.0f%% and leaf labels %.0f%% of the "
                     "width, leaving %.0f%% for the tree; reduce LEAF_PT"
                     % (100 * a, 100 * t, 100 * tree_frac))
# data units per unit of axes fraction, given the tree spans X_TREE0..X_TREE1
scale = (X_TREE1 - X_TREE0) / tree_frac
xmin = X_TREE0 - (a + PAD) * scale
ax.set_xlim(xmin, xmin + scale)

# Row spacing must outrun the type it carries or the labels overprint -- a
# silent defect, since the PDF still builds and looks plausible when small.
row_pt = (PAGE_H * 72.0) / total_rows
if row_pt < LEAF_PT * LINESPACING * 1.02:
    raise SystemExit("row spacing %.2fpt is under the %.2fpt line height; "
                     "reduce LEAF_PT or raise PAGE_H"
                     % (row_pt, LEAF_PT * LINESPACING))

fig.savefig(OUT)          # no bbox_inches: the page must be exactly PAGE_W
print("wrote %s" % OUT)
print("  %d leaves, %d anchors, one page %.0fx%.0fpt"
      % (PUB_LEAVES, PUB_ANCHORS, PAGE_W * 72, PAGE_H * 72))
print("  row spacing %.2fpt, line height %.2fpt" % (row_pt, LEAF_PT * LINESPACING))
print("  width: anchors %.0f%%, tree %.0f%%, leaf labels %.0f%%"
      % (100 * a, 100 * tree_frac, 100 * t))
