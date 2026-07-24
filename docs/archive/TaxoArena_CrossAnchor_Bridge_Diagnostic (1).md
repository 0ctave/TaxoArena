# Diagnosing Cross-Top-Domain Bridges: Geometry-Limited or Threshold-Limited?

Verified against repo commit `f9f2bd5`. Everything here is **read-only**: it measures
an already-built, frozen DAG snapshot and never modifies construction, so it cannot
break DAG coherency by definition. No engine code is touched; the script is a
standalone analysis tool consistent with the no-code-changes rule.

---

## The question, made precise

You observe only same-anchor (`SourceA`) bridges — `SourceB_Count = 0` in every
tuning run. You want to know: **are cross-top-domain bridges genuinely impossible
under this embedding geometry, or merely suppressed by the current fusion
threshold — and could you admit some without over-merging within-domain structure?**

## Why the code makes this the right question (mechanism recap)

Bridge admission (`TaxonomyMerger.mergeRedundantNodes` → `fuseNodes`) fuses two
nodes A, B iff:
1. both have non-empty parents;
2. neither is an ancestor of the other (cycle guard);
3. `cos(vmfMu_A, vmfMu_B) > fusionSimilarityThreshold` (locked at **0.92**).

There is **no same-anchor constraint** — the code will build a cross-anchor bridge
if two leaves under different depth-1 anchors clear 0.92. `fuseNodes` keeps the
target's parents and redirects the source's parents onto it, so a fused node
inherits parents from both lineages. So cross-anchor bridges are *structurally
permitted*; their absence is entirely about whether cross-anchor leaf pairs reach
0.92. Since `dimForDepth` returns a fixed 256 at every depth, all `vmfMu` vectors
are already the same dimension and directly comparable — no re-projection needed.

**Therefore the whole question reduces to one measurable distribution:** how similar
do cross-anchor leaf pairs actually get, relative to same-anchor pairs and the 0.92
line? That is a pure measurement on a frozen snapshot.

---

## What you need: one canonical DAG snapshot

Any frozen snapshot works; the canonical one is best. It is a JSON file written by
`TaxonomyPersistence.save()` (offloaded from `snapshots.db`). Each node serializes
as a `SerialNode` with exactly the fields this diagnostic reads:
- `id`, `depth`, `label`, `parentIds` (List<String>), `vmfMu` (List<Float>, the
  unit-norm mean direction), `isBridge`, `childIds`, `crossLinkChildIds`.

The **anchor** of a leaf = the `label` (or `originalCategory`) of its depth-1
ancestor, reached by walking `parentIds` up to `depth == 1`. (Anchors are the 14
immutable MMLU-Pro domains.)

If you only have the `.db` and not a JSON export, load and re-save one snapshot to
JSON via the existing `TaxonomyPersistence.save(root, path)` — that is an existing,
supported call, not a code change.

---

## Diagnostic 1 — cross-anchor vs. same-anchor similarity distribution (RUN THIS FIRST)

This single measurement answers the core question. Compute, over all leaf pairs in
one snapshot, the cosine similarity of their `vmfMu`, split into two populations:
same-anchor and different-anchor. Compare both against 0.92.

**Interpretation:**
- Cross-anchor distribution has a right tail reaching toward 0.92 (mass above ~0.85)
  → **threshold-limited**: lowering `fusionSimilarityThreshold` slightly would
  surface cross-anchor bridges. Proceed to Diagnostic 2 to find a safe value.
- Cross-anchor distribution bunched low (nothing above ~0.75) while same-anchor
  pairs cluster near/above 0.92 → **geometry-limited**: the embedding space places
  these domains too far apart; no threshold admits cross-anchor bridges without
  also merging things that shouldn't merge. This is a real, publishable finding,
  not a failure — it strengthens the coherency story.

## Diagnostic 2 — threshold sweep as a MEASUREMENT (not a config change)

On the *same frozen snapshot*, count — purely in analysis code — how many
cross-anchor vs. same-anchor leaf pairs *would* fuse at candidate thresholds
{0.80, 0.85, 0.88, 0.90, 0.92}. This traces the coherency trade-off directly:
same-anchor fuse-count is your **coherency proxy** (spurious within-domain merges),
cross-anchor fuse-count is your **target gain**. Look for a threshold window where
cross-anchor bridges appear *before* same-anchor merges explode. If no such window
exists, that is proof the two are inseparable at this geometry.

## Diagnostic 3 — anchor-pair resolution (semantic sanity)

For the cross-anchor pairs closest to 0.92, print which anchors they bridge. If
semantically plausible (Physics↔Engineering, Math↔Economics), the mechanism is
finding real overlap and just needs a threshold nudge. If random, the closeness is
noise — do not chase it.

---

## Ready-to-run script (read-only, standalone)

Save as `tools/analysis/cross_anchor_bridge_diag.py` (new file, analysis-only —
does not touch `src/`). Run: `python cross_anchor_bridge_diag.py path/to/snapshot.json`

```python
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
```

---

## How to read the output → decision

1. **Run Diagnostic 1 first.** The VERDICT line and the two histograms tell you
   geometry-limited vs. threshold-limited immediately.
2. **If threshold-limited**, read the sweep table: find the highest threshold where
   `cross-fuse > 0` while `same-fuse` stays near its 0.92 value (i.e., you gain
   cross-anchor bridges without a spike in same-anchor merges). That candidate is
   your coherency-preserving threshold. Validate it with a single real construction
   run at that `fusionSimilarityThreshold` (a config change for ONE probe run, not a
   commit) and confirm same-anchor quality metrics (WLP, silhouette) hold.
3. **If geometry-limited**, stop — do not lower the threshold. Write the finding:
   cross-anchor bridging is mechanistically available but the MMLU-Pro editorial-
   domain geometry rarely licenses it at any threshold preserving within-domain
   coherence; observed bridges are predominantly intra-anchor refinements. This is
   consistent with your stable `CrossAnchorMigrationRate ~0.24` and strengthens,
   not weakens, the coherency claim.

## Coherency guarantee (why none of this is risky)

Diagnostics 1–3 read a frozen snapshot and compute statistics; they never call the
splitter, merger, or trickler, and never write a snapshot. The only step that could
affect coherency is the *optional* single validation run in decision-step 2, and
that is gated behind an explicit geometry finding (only done if threshold-limited)
and measured against your existing same-anchor quality metrics. So the coherency
question is answered by measurement before any construction parameter is ever
touched.

## Thesis framing (either outcome is a result)

- **Geometry-limited** → "Cross-anchor bridging is available in the mechanism but
  suppressed by embedding geometry; the DAG does not manufacture cross-links the
  geometry does not support." (Coherency-positive.)
- **Threshold-limited, safe window found** → "Cross-anchor bridges emerge at
  threshold T without degrading within-domain purity, demonstrating tunable
  polyhierarchy depth." (Capability-positive.)
- **Threshold-limited, no safe window** → "Cross-anchor bridges are attainable only
  at thresholds that also over-merge within-domain structure; the canonical
  threshold deliberately trades cross-domain coverage for coherence." (Honest
  trade-off, directly feeds the Ch7 discussion.)
```
