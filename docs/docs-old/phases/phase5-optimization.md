# Phase 5: Optimize (Structural Refinement)

*Implemented in `TaxonomyMerger.kt`*

Optimize polishes the DAG topology by pruning dead nodes, merging semantically redundant siblings, creating polyhierarchical cross-links, collapsing passthrough nodes, and enforcing transitive reduction. The operations run in a fixed sequence to preserve topological consistency.

```
optimizeHierarchy:
  1. pruneUnrelevantNodes
  2. mergeSimilarSiblings
  3. evaluateCrossLinks (ancestorMap built once)
  4. prunePassthroughNodes (repeat until stable)
  5. pruneUnrelevantNodes (second pass)
  6. removeStaleParentRefs
  7. transitiveReduction (ancestorMap rebuilt)
```

---

## 1. Starvation Pruning (`pruneUnrelevantNodes`)

A child node is pruned from its parent if it satisfies any of:

| Condition | Rule |
|-----------|------|
| Truly dead | `branchQueryCount == 0` |
| Starved leaf | `isLeaf` and `branchQueryCount < max(5, 0.2 × siblingAvg)` |
| Empty internal | `!isLeaf` and `children.isEmpty()` |

Safety guard: a node is never pruned if doing so would leave its parent with ≤ 1 child (would create a passthrough). Queries from pruned nodes are absorbed back into the parent.

---

## 2. Sibling Merge (`mergeSimilarSiblings`)

For every internal node, all pairs of siblings \((A, B)\) are evaluated with the vMF JS-divergence at their common minimum dimension:

\[
d_{\text{common}} = \min(d_A, d_B), \quad D_{JS}^{vMF}(A, B; d_{\text{common}}) < \varepsilon_{\text{sep}}
\]

Pairs below the separation threshold are connected with Union-Find and their connected components are fused into single nodes. The fused vMF parameters are computed as a query-count-weighted blend of means and concentrations:

\[
\boldsymbol{\mu}_{\text{fused}} = \operatorname{normalize}\!\left(n_A\boldsymbol{\mu}_A + n_B\boldsymbol{\mu}_B\right), \qquad \kappa_{\text{fused}} = \frac{n_A\kappa_A + n_B\kappa_B}{n_A + n_B}
\]

The fused node receives an LLM-generated label from the union of representative queries.

---

## 3. Polyhierarchical Cross-Linking (`evaluateCrossLinks`)

For each node \(v\) with at least `minClusterSize` direct queries, the system evaluates every potential additional parent \(P\) (not already an ancestor) using a **majority vote** over \(v\)'s direct queries:

\[
\text{votes}(P) = \left|\left\{q \in v.\text{queries} : \cos(q, \boldsymbol{\mu}_P) - \cos(q, \boldsymbol{\mu}_v) > 0.05\right\}\right|
\]

A cross-link edge \(P \to v\) is created iff \(\text{votes}(P) \geq |v.\text{queries}|/2\). Cross-links are stored in `P.crossLinkChildren` — **not** in `P.children` — so that `isLeaf = children.isEmpty()` remains accurate and the trickler routes to all real leaf nodes without distortion.

Eligibility constraints on \(P\): not an existing ancestor of \(v\); not a descendant of \(v\); depth \(\leq\) depth of \(v\); depth difference \(\leq 3\); \(P\) is under a different depth-1 domain branch than \(v\).

---

## 4. Passthrough Collapse (`prunePassthroughNodes`)

A node \(v\) is a passthrough if it has exactly one tree child \(c\) and:

\[
D_{JS}^{vMF}(v, c) < \varepsilon_{\text{sep}} \quad \text{and} \quad v.\text{queries.size} < N_{\min}
\]

Passthroughs are bypassed: the grandchild \(c\) is re-parented directly under \(v\)'s parent, depths are recomputed, and `PHASE_VMF_FIT` is cleared on nodes whose `sliceDim` changes so they are refitted in the next iteration. This loop repeats until no more passthroughs remain.

---

## 5. Stale Reference Cleanup and Transitive Reduction

**Stale refs:** any `node.parents` pointer to a node no longer in the DAG (removed by pruning or merging) is deleted.

**Transitive reduction:** for every node \(v\), a parent \(P_1\) is redundant if there exists another parent \(P_2\) such that \(P_1 \in \text{ancestors}(P_2)\). Redundant parents are severed from both `children` and `crossLinkChildren`. The primary tree parent (`treeParentId`) is always protected from removal.

The ancestorMap is rebuilt after all structural changes and before transitive reduction to ensure fresh data.
