# Generates the frozen-instrument figure: the single construction artifact
# every arena result in this thesis is attributed to, drawn as a HORIZONTAL
# icicle -- anchors as rows, depth as columns -- so that the fourteen anchor
# names are readable left to right instead of rotated, and so that depth and
# routed query mass are both visible at once.
#
# REAL DATA ONLY. The tree is read from the frozen snapshot and every
# structural statistic drawn or annotated is asserted against the values the
# arena runs recorded, before any drawing happens; on mismatch the script
# raises and emits no PDF.
#
# Primary sources:
#   snapshots.db, snapshot 20260727_042523_Headless_Run_Auto_ge (read-only)
#       graph JSON: nodes with id, label, depth, childIds, queryIds
#   {law_baseline,philosophy,history,psychology,engineering}_secured/
#       MAIN_thesis_metrics.csv -- the totalNodes / leafNodes / maxDepth /
#       avgLeafDepth the runs themselves recorded against this snapshot.
#
# CONVENTIONS:
#   Mass        A node's ROW HEIGHT is its subtree's routed query mass = the
#               number of queryIds in its descendant leaves. Only leaves carry
#               queryIds; internal nodes carry none, so mass is summed upward.
#               Leaf masses are disjoint and sum to the corpus total (asserted).
#   Depth       A cell's COLUMN is its depth. A subtree that stops early leaves
#               its remaining columns blank; the ragged right edge is therefore
#               the depth distribution, not a drawing artifact.
#   Order       Anchors, and children within an anchor, are drawn in the
#               snapshot's own childIds order, NOT sorted by mass. Sorting
#               would produce a different picture from the same artifact, so
#               the order is named rather than chosen.
#   Shading     Greys fade with DEPTH, redundantly with the column position, so
#               that the ragged right edge reads as "shallower" at a glance.
#               Nothing is encoded by hue; the figure is greyscale.
#   Roster      None. This figure contains no model data and no judge verdict.
#               The six anchors that ran as arenas are marked so the reader can
#               place the later results on the instrument, not because any
#               model number enters here.
#
# Run from anywhere:  python report/Figures/make_frozen_tree.py
import csv
import json
import os
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "frozen_tree.pdf")
SNAP_DB = os.path.join(ROOT, "snapshots.db")
SNAP_ID = "20260727_042523_Headless_Run_Auto_ge"

# Structural values this script MUST reproduce.
PUB_NODES = 154
PUB_LEAVES = 87
PUB_MAX_DEPTH = 6
PUB_ANCHORS = 14
PUB_AVG_LEAF_DEPTH = 3.6206896551724137
PUB_QUERIES = 9141
ARENA_ANCHORS = {"Math", "Physics", "Law", "Philosophy", "History",
                 "Psychology", "Engineering", "Computer science"}
SECURED = ["law_baseline", "philosophy", "history", "psychology", "engineering"]

print("VERIFYING the frozen snapshot against what the runs recorded\n")
db = sqlite3.connect("file:%s?mode=ro" % SNAP_DB.replace("\\", "/"), uri=True)
row = db.execute("select graph from snapshots where id = ?", (SNAP_ID,)).fetchone()
db.close()
if row is None:
    raise SystemExit("snapshot %s not found" % SNAP_ID)
graph = json.loads(row[0])
nodes = {n["id"]: n for n in graph["nodes"]}
root_id = graph["rootId"]

leaves = [n for n in nodes.values() if not n.get("childIds")]
max_depth = max(n["depth"] for n in nodes.values())
avg_leaf_depth = sum(n["depth"] for n in leaves) / len(leaves)
anchors = nodes[root_id]["childIds"]

if len(nodes) != PUB_NODES or len(leaves) != PUB_LEAVES:
    raise SystemExit("MISMATCH: %d nodes / %d leaves, published %d / %d"
                     % (len(nodes), len(leaves), PUB_NODES, PUB_LEAVES))
if max_depth != PUB_MAX_DEPTH or len(anchors) != PUB_ANCHORS:
    raise SystemExit("MISMATCH: depth %d / %d anchors, published %d / %d"
                     % (max_depth, len(anchors), PUB_MAX_DEPTH, PUB_ANCHORS))
if abs(avg_leaf_depth - PUB_AVG_LEAF_DEPTH) > 1e-9:
    raise SystemExit("MISMATCH avg leaf depth: %.10f, published %.10f"
                     % (avg_leaf_depth, PUB_AVG_LEAF_DEPTH))


def mass(nid):
    n = nodes[nid]
    if not n.get("childIds"):
        return len(n["queryIds"])
    return sum(mass(c) for c in n["childIds"])


def leaf_count(nid):
    n = nodes[nid]
    if not n.get("childIds"):
        return 1
    return sum(leaf_count(c) for c in n["childIds"])


total = mass(root_id)
leaf_sum = sum(len(n["queryIds"]) for n in leaves)
if total != leaf_sum:
    raise SystemExit("MISMATCH: subtree mass %d != leaf mass sum %d"
                     % (total, leaf_sum))
if total != PUB_QUERIES:
    raise SystemExit("MISMATCH: %d routed queries, published %d"
                     % (total, PUB_QUERIES))
if sum(leaf_count(a) for a in anchors) != PUB_LEAVES:
    raise SystemExit("MISMATCH: anchor leaf counts do not sum to %d" % PUB_LEAVES)
print("  %d nodes, %d leaves, max depth %d, %d anchors, "
      "mean leaf depth %.4f, %s routed queries"
      % (len(nodes), len(leaves), max_depth, len(anchors), avg_leaf_depth,
         f"{total:,}"))

# cross-check against what the arena runs themselves recorded
for name in SECURED:
    path = os.path.join(ROOT, "%s_secured" % name, "MAIN_thesis_metrics.csv")
    if not os.path.exists(path):
        continue
    got = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            got[r["MetricName"]] = float(r["Value"])
    checks = (("totalNodes", PUB_NODES), ("leafNodes", PUB_LEAVES),
              ("maxDepth", PUB_MAX_DEPTH),
              ("avgLeafDepth", PUB_AVG_LEAF_DEPTH))
    for k, want in checks:
        if abs(got[k] - want) > 1e-9:
            raise SystemExit("MISMATCH %s run recorded %s = %s, snapshot gives %s"
                             % (name, k, got[k], want))
    print("  %-12s run agrees: 154 / 87 / depth 6 / mean leaf depth 3.6207"
          % name)

missing = ARENA_ANCHORS - {nodes[a]["label"] for a in anchors}
if missing:
    raise SystemExit("arena anchors absent from the tree: %s" % sorted(missing))
print("\nStructure reproduces. Plotting.\n")

# ------------------------------------------------------------------- the plot
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
    "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "pdf.fonttype": 42,
})

fig, ax = plt.subplots(figsize=(7.0, 4.8))
SHADE = {1: "0.68", 2: "0.76", 3: "0.82", 4: "0.87", 5: "0.90", 6: "0.92"}
GAP = 55.0          # blank query-mass units between adjacent anchor rows


def draw(nid, y0, depth):
    """Draw the subtree rooted at nid occupying [y0, y0 + mass) at `depth`."""
    m = mass(nid)
    ax.add_patch(plt.Rectangle((depth, y0), 0.94, m,
                               facecolor=SHADE[depth], edgecolor="white",
                               lw=0.55, zorder=2))
    y = y0
    for c in nodes[nid].get("childIds", []):
        draw(c, y, depth + 1)
        y += mass(c)
    return m


y = 0.0
row_mid, row_meta = {}, {}
for k, aid in enumerate(anchors):
    m = draw(aid, y, 1)
    label = nodes[aid]["label"]
    row_mid[label] = y + m / 2.0
    row_meta[label] = (leaf_count(aid), m)
    y += m + GAP
span = y - GAP

# anchor names on the left, horizontal; arena anchors set in bold with a rule
for k, aid in enumerate(anchors):
    label = nodes[aid]["label"]
    n_leaf, m = row_meta[label]
    is_arena = label in ARENA_ANCHORS
    ax.text(0.93, row_mid[label], label, ha="right", va="center",
            fontsize=8.2, weight="bold" if is_arena else "normal",
            color="black" if is_arena else "0.35")
    ax.text(max_depth + 1.10, row_mid[label],
            "%2d leaves   %s queries" % (n_leaf, f"{m:,}"),
            ha="left", va="center", fontsize=7.2, color="0.35")
    if is_arena:
        ax.plot([0.99, 0.99], [row_mid[label] - m / 2, row_mid[label] + m / 2],
                color="black", lw=2.4, solid_capstyle="butt", zorder=5)

# depth axis along the top, where the reader meets it first
TOP = span * 0.030          # blank strip above the first anchor row
BOT = span * 0.120          # blank strip below the last, for the key
ax.set_xlim(0.02, max_depth + 2.55)
ax.set_ylim(-TOP, span + BOT)
ax.invert_yaxis()
ax.xaxis.set_ticks_position("top")
ax.xaxis.set_label_position("top")
ax.set_xticks([d + 0.47 for d in range(1, max_depth + 1)])
ax.set_xticklabels(["depth %d" % d for d in range(1, max_depth + 1)])
ax.tick_params(axis="x", length=0, pad=3)
ax.set_yticks([])
for side in ("left", "right", "top", "bottom"):
    ax.spines[side].set_visible(False)

# what the two axes mean, said on the figure
ax.text(0.93, -TOP * 0.52, "14 anchors", ha="right", va="center",
        fontsize=7.5, style="italic", color="0.35")
ax.text(max_depth + 1.10, -TOP * 0.52,
        "row height $\\propto$ routed queries", ha="left", va="center",
        fontsize=7.5, style="italic", color="0.35")
key_y = span + BOT * 0.36
ax.plot([0.99, 0.99], [key_y - BOT * 0.12, key_y + BOT * 0.12], color="black",
        lw=2.4, solid_capstyle="butt")
ax.text(1.14, key_y, "ran as an arena (8 of 14)",
        ha="left", va="center", fontsize=7.5, color="0.20")
ax.text(0.99, span + BOT * 0.78,
        "a row that stops short has no deeper cells: "
        "mean leaf depth %.2f, maximum %d"
        % (avg_leaf_depth, max_depth),
        ha="left", va="center", fontsize=7.5, color="0.35")

ax.set_title("One frozen tree carries every result in this thesis: "
             "%d nodes, %d of them leaves, %s routed queries\n"
             "snapshot %s; children in the snapshot's own order, not sorted "
             "by size"
             % (len(nodes), len(leaves), f"{total:,}", SNAP_ID[:15]),
             fontsize=8.6, loc="left", pad=26, linespacing=1.6, x=-0.135)

fig.subplots_adjust(left=0.135, right=0.795, top=0.845, bottom=0.020)
fig.savefig(OUT)
print("wrote %s" % OUT)
