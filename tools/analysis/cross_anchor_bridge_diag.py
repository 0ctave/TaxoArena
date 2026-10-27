#!/usr/bin/env python3
"""
Cross-anchor bridge diagnostic for TaxoArena.
READ-ONLY: consumes one frozen DAG snapshot JSON, measures nothing about
construction. Reports whether cross-top-domain bridges are geometry-limited
or threshold-limited. Does not modify the engine or any snapshot.

Snapshot schema (from TaxonomyPersistence.SerialNode): each node has
id, depth, label, parentIds, vmfMu (list[float], unit-norm), isBridge.
"""
import json, sys, math
from itertools import combinations
from collections import defaultdict

FUSION_THRESHOLD = 0.92
SWEEP = [0.80, 0.85, 0.88, 0.90, 0.92]

def load(path):
    g = json.load(open(path))
    nodes = {n["id"]: n for n in g["nodes"]}
    return g["rootId"], nodes

def anchor_of(nid, nodes, cache):
    """Walk parentIds up to depth==1; return that node's label (the anchor)."""
    if nid in cache: return cache[nid]
    seen = set()
    stack = [nid]
    found = None
    while stack:
        cur = stack.pop()
        if cur in seen: continue
        seen.add(cur)
        n = nodes.get(cur)
        if n is None: continue
        if n["depth"] == 1:
            found = n.get("label") or n.get("originalCategory") or cur
            break
        stack.extend(n.get("parentIds", []))
    cache[nid] = found
    return found

def is_leaf(n):
    # mirror GraphNode.isLeaf: no tree children, not a bridge, <=1 parent
    return (not n.get("childIds")) and (not n.get("isBridge")) and len(n.get("parentIds", [])) <= 1

def cosine(a, b):
    # vmfMu are unit-norm by construction, but normalize defensively
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0: return 0.0
    return dot / (na * nb)

def hist(vals, lo=0.0, hi=1.0, bins=20):
    if not vals: return
    step = (hi - lo) / bins
    counts = [0]*bins
    for v in vals:
        i = min(bins-1, max(0, int((v-lo)/step)))
        counts[i] += 1
    mx = max(counts) or 1
    for i, c in enumerate(counts):
        left = lo + i*step
        bar = "#" * int(40*c/mx)
        mark = "  <-- 0.92" if left <= 0.92 < left+step else ""
        print(f"  [{left:.2f},{left+step:.2f})  {c:5d} |{bar}{mark}")

def main(path):
    root_id, nodes = load(path)
    cache = {}
    leaves = [n for n in nodes.values() if is_leaf(n) and n.get("vmfMu")]
    print(f"Snapshot: {path}")
    print(f"Total nodes: {len(nodes)}  |  leaves with vmfMu: {len(leaves)}")

    # attach anchor to each leaf
    for n in leaves:
        n["_anchor"] = anchor_of(n["id"], nodes, cache)
    by_anchor = defaultdict(int)
    for n in leaves: by_anchor[n["_anchor"]] += 1
    print(f"Anchors represented: {len(by_anchor)}")
    print("  leaves per anchor:", dict(sorted(by_anchor.items(), key=lambda x:-x[1])))

    same, cross = [], []
    cross_pairs = []  # (sim, anchorA, anchorB, labelA, labelB)
    for a, b in combinations(leaves, 2):
        if not a.get("vmfMu") or not b.get("vmfMu"): continue
        if len(a["vmfMu"]) != len(b["vmfMu"]): continue  # should not happen at d=256
        s = cosine(a["vmfMu"], b["vmfMu"])
        if a["_anchor"] == b["_anchor"]:
            same.append(s)
        else:
            cross.append(s)
            cross_pairs.append((s, a["_anchor"], b["_anchor"],
                                a.get("label"), b.get("label")))

    def stats(name, xs):
        if not xs:
            print(f"\n{name}: (none)"); return
        xs_sorted = sorted(xs)
        n = len(xs_sorted)
        p = lambda q: xs_sorted[min(n-1, int(q*n))]
        above = sum(1 for x in xs if x > FUSION_THRESHOLD)
        print(f"\n{name}: n={n}  max={max(xs):.4f}  "
              f"p50={p(0.5):.4f}  p90={p(0.9):.4f}  p99={p(0.99):.4f}  "
              f"count>{FUSION_THRESHOLD}={above}")

    stats("SAME-anchor leaf-pair cosine", same)
    stats("CROSS-anchor leaf-pair cosine", cross)

    print("\n--- SAME-anchor histogram ---");  hist(same)
    print("\n--- CROSS-anchor histogram ---"); hist(cross)

    # Diagnostic 2: threshold sweep (counts of would-fuse pairs)
    print("\n--- Threshold sweep (would-fuse pair counts) ---")
    print(f"{'thresh':>8} {'cross-fuse':>11} {'same-fuse':>10}")
    for t in SWEEP:
        cf = sum(1 for s in cross if s > t)
        sf = sum(1 for s in same if s > t)
        print(f"{t:8.2f} {cf:11d} {sf:10d}")

    # Diagnostic 3: top cross-anchor near-misses
    print("\n--- Top 15 cross-anchor pairs by similarity ---")
    for s, aA, aB, lA, lB in sorted(cross_pairs, reverse=True)[:15]:
        print(f"  {s:.4f}  [{aA} x {aB}]  {lA!r} <-> {lB!r}")

    # Verdict heuristic
    print("\n--- VERDICT ---")
    if cross:
        cmax = max(cross)
        if cmax > FUSION_THRESHOLD:
            print("THRESHOLD-LIMITED: some cross-anchor pairs already exceed 0.92.")
            print("  (If none became bridges, check the ancestor/cycle guard or")
            print("   that these leaves survived to the merge phase.)")
        elif cmax > 0.85:
            print(f"NEAR THRESHOLD: cross-anchor max={cmax:.4f} approaches 0.92.")
            print("  Likely threshold-limited. Use the sweep table above to find a")
            print("  threshold that admits cross-anchor bridges before same-fuse rises.")
        else:
            print(f"GEOMETRY-LIMITED: cross-anchor max={cmax:.4f}, far below 0.92.")
            print("  No threshold admits cross-anchor bridges without over-merging")
            print("  same-anchor structure. This is a coherency-preserving property,")
            print("  not a failure -- report it as such.")
    else:
        print("No cross-anchor leaf pairs found (single-anchor snapshot?).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: cross_anchor_bridge_diag.py <snapshot.json>"); sys.exit(1)
    main(sys.argv[1])
