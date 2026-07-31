# Where do the questions each domain arena judges actually come from?
#
# CLAIM. The cells are built out of one subject (74% of a cell's construction
# queries carry its dominant MMLU-Pro category) but the held-out questions routed
# into them at arena time mostly do not (39% pooled). In five of the eight run
# domains the arena judges questions drawn overwhelmingly from other subjects,
# under a rubric induced entirely on the cell's own subject.
#
# REAL DATA ONLY. Recomputed here from the frozen snapshot, the taxonomy query
# store, the eval cache and the eight r8 ratings databases; every published value
# is asserted before any drawing happens; on mismatch the script raises and emits
# no PDF.
#
# Published values reproduced here:
#   pooled on-subject routing rate 37.2% (609 / 1637 routed questions); per-domain
#   on-subject counts law 245/276, psychology 172/265, history 74/131, physics
#   38/229, engineering 23/158, math 34/291, cs 13/158, philosophy 10/129;
#   mean cell construction purity 73.8%; 52 cells.
#
# Run from anywhere:  python report/Figures/make_routing_provenance.py
import json
import os
import sqlite3
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "routing_provenance.pdf")
SNAP_ID = "20260727_042523_Headless_Run_Auto_ge"
DOMS = ["math", "physics", "law", "engineering",
        "psychology", "philosophy", "history", "cs"]
PRETTY = {"cs": "computer sci."}

def ro(name):
    path = os.path.join(ROOT, name).replace("\\", "/")
    return sqlite3.connect("file:%s?mode=ro" % path, uri=True)

# ------------------------------------------------------------------ recompute
db = ro("snapshots.db")
graph, = db.execute("select graph from snapshots where id = ?", (SNAP_ID,)).fetchone()
db.close()
g = json.loads(graph)
leaves = {n["id"]: n for n in g["nodes"] if not n.get("childIds")}

ec = ro("embeddings_cache.db")
qcat = {i: c for i, c in ec.execute("select id, ground_truth_category from queries")}
ec.close()

cc = ro("mmlu_pro_dataset_cache_v2.db")
cat = {str(q): c for q, c in cc.execute(
    "select distinct question_id, category from eval_results")}
cc.close()

# each cell's dominant construction subject, and how pure the cell is in it
dominant, purity = {}, {}
for lid, n in leaves.items():
    c = Counter(qcat.get(q, "?") for q in n["queryIds"])
    if not c:
        continue
    top, k = c.most_common(1)[0]
    dominant[lid] = top.lower()
    purity[lid] = k / sum(c.values())

routed = defaultdict(list)
for d in DOMS:
    r = ro("experiment_results/r8/%s/ratings_r8_%s.db" % (d, d))
    for nid, q in r.execute(
            "select distinct node_id, eval_question_id "
            "from match_history where condition = 'MAIN'"):
        routed[(d, nid)].append(str(q))
    r.close()

stat = {}
for d in DOMS:
    on = tot = 0
    pur = []
    for (dd, nid), qs in routed.items():
        if dd != d or nid not in dominant:
            continue
        pur.append(purity[nid])
        for q in qs:
            c = cat.get(q)
            if c is None:
                continue
            tot += 1
            on += (c.lower() == dominant[nid])
    stat[d] = (on, tot, sum(pur) / len(pur))

cells = len({nid for (_, nid) in routed if nid in dominant})
tot_on = sum(v[0] for v in stat.values())
tot_n = sum(v[1] for v in stat.values())
mean_pur = sum(purity[nid] for (_, nid) in routed if nid in dominant) / cells

# ---------------------------------------------------------------- verification
EXPECT = {"law": (245, 276), "psychology": (172, 265), "history": (74, 131),
          "physics": (38, 229), "engineering": (23, 158), "math": (34, 291),
          "cs": (13, 158), "philosophy": (10, 129)}
for d, (on, tot) in EXPECT.items():
    assert stat[d][:2] == (on, tot), \
        "%s on-subject %s != published %s" % (d, stat[d][:2], (on, tot))
assert (tot_on, tot_n) == (609, 1637), \
    "pooled %s != published (609, 1637)" % ((tot_on, tot_n),)
assert cells == 52, "cells %d != published 52" % cells
assert abs(mean_pur - 0.7381) < 5e-4, \
    "mean construction purity %.4f != published 0.7381" % mean_pur

print("VERIFIED against published values:")
print("  %d cells, %d routed questions with a resolvable category" % (cells, tot_n))
print("  pooled on-subject routing %d/%d = %.1f%%" % (tot_on, tot_n, 100 * tot_on / tot_n))
print("  mean cell construction purity %.1f%%" % (100 * mean_pur))
for d in DOMS:
    on, tot, pur = stat[d]
    print("    %-12s routed on-subject %3d/%3d = %5.1f%%   cell purity %5.1f%%"
          % (d, on, tot, 100 * on / tot, 100 * pur))

# ---------------------------------------------------------------------- plot
# GREYSCALE ONLY -- the thesis prints in monochrome. The two shares are told
# apart by fill and hatch, never by hue; the construction-side reference is a
# marker, not a second colour.
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
    "font.size": 9, "pdf.fonttype": 42,
})

order = sorted(DOMS, key=lambda d: -stat[d][0] / stat[d][1])
fig, ax = plt.subplots(figsize=(6.4, 3.5))
ax.set_axisbelow(True)
ax.grid(axis="x", color="0.90", lw=0.6)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)

for i, d in enumerate(order):
    on, tot, pur = stat[d]
    frac = 100.0 * on / tot
    ax.barh(i, 100, height=0.56, facecolor="white", edgecolor="0.78",
            linewidth=0.7, hatch="....", zorder=2)
    ax.barh(i, frac, height=0.56, facecolor="0.66", edgecolor="white",
            linewidth=0.8, zorder=3)
    # value inside the bar where it fits, outside where it does not
    if frac >= 22:
        ax.annotate("%.0f%%" % frac, xy=(frac, i), xytext=(-5, 0),
                    textcoords="offset points", va="center", ha="right",
                    fontsize=8, color="white", zorder=6)
    else:
        ax.annotate("%.0f%%" % frac, xy=(frac, i), xytext=(5, 0),
                    textcoords="offset points", va="center", ha="left",
                    fontsize=8, color="0.15", zorder=6)
    ax.plot([100 * pur], [i], marker="D", ms=5.2, mfc="white", mec="black",
            mew=1.0, zorder=7)

ax.axvline(100 * tot_on / tot_n, color="black", lw=1.0, ls=(0, (4, 3)), zorder=4)
ax.set_yticks(range(len(order)))
ax.set_yticklabels([PRETTY.get(d, d) for d in order])
ax.set_ylim(-1.35, len(order) - 0.35)
ax.invert_yaxis()
ax.set_xlim(0, 101)
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.set_xticklabels(["0", "20", "40", "60", "80", "100%"])
ax.set_xlabel("share of the cell's judged questions carrying the cell's own subject")
ax.tick_params(length=0)

ax.annotate("pooled %.0f%%" % (100 * tot_on / tot_n),
            xy=(100 * tot_on / tot_n, -1.25), xytext=(4, 0),
            textcoords="offset points", ha="left", va="top", fontsize=8,
            color="0.25")
ax.annotate("$\\diamond$  the same cells are %.0f%% pure in that subject on the\n"
            "     construction side, which is what the rubric was induced from"
            % (100 * mean_pur),
            xy=(0.0, 1.02), xycoords="axes fraction", ha="left", va="bottom",
            fontsize=8, color="0.25", linespacing=1.45)

ax.set_title("Five of the eight arenas mostly judge questions from other subjects\n"
             "held-out questions routed into each domain's cells, "
             "frozen snapshot %s" % SNAP_ID[:15],
             fontsize=8.6, loc="left", pad=34, linespacing=1.6)

fig.subplots_adjust(left=0.165, right=0.985, top=0.745, bottom=0.135)
fig.savefig(OUT)
print("wrote", OUT)
