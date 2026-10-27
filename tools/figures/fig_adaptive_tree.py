"""Radial view of an adaptive-bar taxonomy run (default: the p50 tree).

Usage: python tools/figures/fig_adaptive_tree.py [run_seed_dir] [out.png]
Reads the run's final dag snapshot; leaf dots sized by question mass, filled if
the leaf has a frozen-tree counterpart (cos(vmfMu) >= 0.95, greedy matching),
hollow if it is new/moved structure. Anchors labeled on the rim with their
per-anchor bar. Style follows tools/figures/PLAN.md conventions (ink structure,
single accent, near-white card, direct labels, no legend-only encodings).
"""
import json, math, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, "experiment_results", "h9_adaptive_p50", "seed_42")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
    ROOT, "figures", "exploratory", "p50_adaptive_tree.png")
FROZEN = os.path.join(ROOT, "experiment_results", "freeze_mcs55", "seed_42")
BARS = os.path.join(ROOT, "experiment_configs", "adaptive_bars_p50.json")

INK, MUTED, ACCENT, PAPER = "#23292B", "#8a8983", "#2F6B4F", "#fcfcfb"


def last_snapshot(run):
    last = None
    with open(os.path.join(run, "dag_snapshots.jsonl"), encoding="utf-8") as f:
        for line in f:
            last = line
    return json.loads(last)


def cos(u, v):
    return sum(a * b for a, b in zip(u, v))


def main():
    snap = last_snapshot(RUN)
    nodes = {n["id"]: n for n in snap["nodes"]}
    children = {nid: [nodes[c] for c in n.get("childIds", []) if c in nodes]
                for nid, n in nodes.items()}
    root = next(n for n in snap["nodes"] if n["depth"] == 0)
    anchors = sorted((n for n in snap["nodes"] if n["depth"] == 1),
                     key=lambda n: -n["subtreeQueries"])
    bars = json.load(open(BARS, encoding="utf-8"))

    frozen = last_snapshot(FROZEN)
    frozen_leaves = [n for n in frozen["nodes"] if n["isLeaf"]]
    used = set()

    def has_counterpart(leaf):
        best, bi = -1.0, None
        for i, f in enumerate(frozen_leaves):
            if i in used:
                continue
            s = cos(leaf["vmfMu"], f["vmfMu"])
            if s > best:
                best, bi = s, i
        if best >= 0.95:
            used.add(bi)
            return True
        return False

    # angular allocation: anchors get spans proportional to leaf count (min span floor)
    def leaves_under(n):
        if n["isLeaf"]:
            return [n]
        out = []
        for c in children[n["id"]]:
            out.extend(leaves_under(c))
        return out

    total_leaves = sum(max(1, len(leaves_under(a))) for a in anchors)
    fig, ax = plt.subplots(figsize=(11, 11), dpi=200, subplot_kw={"projection": "polar"})
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    ax.set_axis_off()
    ax.set_ylim(0, 1.42)

    max_depth = max(n["depth"] for n in snap["nodes"])
    def radius(depth):
        return 0.12 + 0.78 * (depth / max_depth)

    theta_cursor = [0.0]
    pos = {}

    def place(n, t0, t1):
        my_leaves = leaves_under(n)
        if n["isLeaf"]:
            th = (t0 + t1) / 2
            pos[n["id"]] = (th, radius(max(n["depth"], 1)))
            return th
        spans, tot = [], sum(max(1, len(leaves_under(c))) for c in children[n["id"]])
        t = t0
        ths = []
        for c in children[n["id"]]:
            w = max(1, len(leaves_under(c))) / tot * (t1 - t0)
            ths.append(place(c, t, t + w))
            t += w
        th = sum(ths) / len(ths)
        pos[n["id"]] = (th, radius(n["depth"]) if n["depth"] > 0 else 0.0)
        return th

    gap = 2 * math.pi * 0.004
    t = 0.0
    for a in anchors:
        w = max(1, len(leaves_under(a))) / total_leaves * (2 * math.pi - gap * len(anchors))
        place(a, t, t + w)
        t += w + gap
    pos[root["id"]] = (0.0, 0.0)

    # edges
    for nid, n in nodes.items():
        for c in children[nid]:
            th1, r1 = pos[nid]
            th2, r2 = pos[c["id"]]
            ax.plot([th1, th2], [r1, r2], color=MUTED, lw=0.9, alpha=0.75, zorder=1)

    # nodes
    for n in snap["nodes"]:
        th, r = pos[n["id"]]
        if n["depth"] == 0:
            ax.plot([th], [r], "o", ms=5, color=INK, zorder=3)
        elif n["isLeaf"]:
            mass = n["subtreeQueries"]
            ms = 4 + 14 * math.sqrt(mass / 950.0)
            if has_counterpart(n):
                ax.plot([th], [r], "o", ms=ms, color=ACCENT, mec=INK, mew=0.4,
                        alpha=0.9, zorder=3)
            else:
                ax.plot([th], [r], "o", ms=ms, mfc="none", mec=ACCENT, mew=1.4, zorder=3)
        else:
            ax.plot([th], [r], "o", ms=3.5, color=INK, zorder=3)

    # anchor labels + bars on the rim; narrow sectors get staggered radii so the
    # small unsplit anchors (History, Philosophy, Business...) cannot collide.
    narrow_idx = 0
    for a in sorted(anchors, key=lambda a: pos[a["id"]][0]):
        th, _ = pos[a["id"]]
        deg = math.degrees(th)
        rot = deg - 90 if 0 <= deg <= 180 else deg + 90
        nl = len(leaves_under(a))
        span = max(1, nl) / total_leaves * 360
        if span < 18:
            r_lab = 1.22 + 0.11 * (narrow_idx % 2)
            narrow_idx += 1
        else:
            r_lab = 1.24
        split = "unsplit" if a["isLeaf"] else "%d leaves" % nl
        ax.text(th, r_lab, "%s\n(bar %.3f · %s)" % (a["label"], bars.get(a["label"], 0), split),
                rotation=rot, rotation_mode="anchor", ha="center", va="center",
                fontsize=8.2, color=INK, fontweight="bold" if not a["isLeaf"] else "normal",
                alpha=1.0 if not a["isLeaf"] else 0.62)

    n_leaves = sum(1 for n in snap["nodes"] if n["isLeaf"])
    fig.suptitle("The p50 adaptive-bar taxonomy", y=0.975, fontsize=17,
                 fontweight="bold", color=INK)
    ax.set_title(
        "%d leaves · every split clears its anchor's median texture null · held-out Top-1 0.755 (inside the seed floor)\n"
        "filled dot = leaf with a frozen-tree counterpart (cos ≥ 0.95, %d of %d) · hollow = new or moved structure · dot size = question mass"
        % (n_leaves, 63, n_leaves), fontsize=9.3, color=MUTED, pad=26)
    fig.text(0.5, 0.015,
             "run: experiment_results/h9_adaptive_p50/seed_42 · bars: adaptive_bars_p50.json (within-node null p50 per anchor, d72bcd6) · exploratory — the frozen 87-leaf instrument stands",
             ha="center", fontsize=7.4, color=MUTED)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight", facecolor=PAPER)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
