# DAG Construction Mechanisms — Current Design (2026-07-23, rev. 3)

Authoritative description of the construction pipeline's decision mechanisms after the
2026-07-23 redesign and its same-day evolution: direction-only sibling competition,
Jensen-tight descent gate, global-J proposal gating of all structural edits (rev. 2),
and the restoration of **cross-linking as a J-gated growth edit** — the first version of
the pipeline that produces a genuine polyhierarchy (rev. 3). Supersedes the
corresponding sections of `evolutionary-pipeline/discovery-optimization.md` (kept for
history).

Milestone runs (seed 42, full 8,353-query MMLU-Pro corpus):
- **rev. 2 (strict tree)**: converged GED +0/−0, zero C3 violations, all leaves ≥
  minClusterSize, no wrapper chains, ECE 0.22–0.32 — but 0 bridges, 439 residual
  queries (240 at Psychology alone).
- **rev. 3 (cross-links)**: converged at iteration 15 (streak 5/5) with **9 bridge
  nodes**, residuals 439 → 285 (Psychology 240 → 16), 56 leaves, acyclic, 0 orphans,
  purity statistically unchanged (0.710 vs 0.720), ECE 0.229. The proposal gate accepted
  4 of 48 generated cross-links — selective, not permissive.

## 1. One separation score for every structural gate

All structural accept/reject decisions use a single **chance-corrected separation
score** (`StatisticsUtils.chanceCorrectedSeparation`):

```
W(S)  = |S|² − ‖Σx‖²                    (total pairwise cosine dissimilarity)
E     = W(total) · Σ_c n_c(n_c−1) / (n(n−1))   (exact expectation of within-cluster
                                                scatter under a uniformly random
                                                partition into the same sizes)
score = 1 − Σ_c W(S_c) / E
```

Properties: 1 for a perfect partition, ≈ 0 for a random one, negative for
anti-clustered, and **exactly 0 for k = 1** — a non-separating (wrapper) candidate can
never clear a positive threshold. The chance correction removes the mechanical
dependence of the raw within/total ratio on k and on cluster sizes, so one
`separationEpsilon` means the same thing for:

- split acceptance (`TaxonomySplitter`),
- k-selection inside vMF-EM (`performVmfKMeans` marginal improvement),
- sibling merging (`TaxonomyMerger`, computed on branch-query sufficient statistics),
- sibling distinctness of new children,
- residual-split viability,
- and, lifted to the whole DAG, the **global objective J**
  (`StatisticsUtils.computeDagSeparationJ`): the same chance-corrected score computed
  over the full corpus with one cell per leaf plus one cell per internal node's
  residual pool. J is the single number every structural proposal is judged against
  (§5).

It replaced two broken gates: the old "Dasgupta delta" `1 − Σ(n−n_c)W_c/(nW)` measured
the *remaining*-cost fraction (~0.82 for every real split, leaving any ε below that
inert), and the κ-scaled vMF divergence surrogate `½(κ_A A_d(κ_A)+κ_B A_d(κ_B))(1−cosθ)`
grew with κ and became unsatisfiable exactly where merge/collapse mattered (11 collapses
and 0 merges per 35-iteration run). The score is an ARI-style adjustment-for-chance; it
is *not* the canonical Dasgupta (2016) LCA cost and must not be called that.

## 2. Trickle routing: three independent criteria (`TaxonomyTrickler`)

The old design overloaded one absolute `membershipFloor` with three jobs; the flat
product-vs-floor test mathematically forbade balanced structure below depth 2 (a
balanced 4-way split gives ~0.25/level; 0.25 × 0.3 < 0.10), which *forced* chains of
~1.0-responsibility dominant children — the swallow/wrapper churn. The three jobs are
now separated:

1. **Descent-vs-residual gate (parameter-free, Jensen-tight).** At each internal node,
   descend iff `max_c ⟨μ_c, x⟩ ≥ r̄_p · ⟨μ_p, x⟩`, where
   `r̄_p = ‖Σ_c w_c μ_c‖ ∈ [0,1]` is the resultant length of the children's weighted
   centroid mix (`GraphNode.childCentroidShrinkage`, recomputed after every structural
   change). Since the parent's direction is (approximately) the *normalized* mean of
   its children's, the raw parent dot overstates what the children can collectively
   achieve by exactly the factor 1/r̄_p; multiplying by r̄_p makes the comparison the
   tight bound `max_c dot ≥ weighted-mean dot`. A query is residual only when its best
   child does worse than the children's own weighted-average alignment — genuine
   unexplained mass, not an artifact. Directions, not densities: the Hornik–Grün
   shrinkage `(n−1)/(n+d−2)` scales with n, so parents are fitted systematically
   sharper than children and density comparisons carry tens of nats of bias (measured:
   56 % of the corpus residualized at anchors under the density form; the un-tightened
   direction form still over-rejected ~40 %).
2. **Direction-only sibling competition with a cosine beam (`routingBeamGamma`).**
   Siblings are scored `κ̄ · ⟨μ_c, x⟩` with the *shared mean* κ̄ of the level — per-child
   κ and normalizers are excluded from the competition, so a child cannot win queries by
   concentration bookkeeping, only by direction. A child stays on the beam iff
   `⟨μ_c, x⟩ ≥ max_sibling dot − γ` (an additive cosine margin). Relative-to-best is
   scale-free and adapts to the realized competition: 0.50/0.50 sharing keeps both
   children, decisive wins drop the tail. The argmax always passes, so the beam is never
   empty. Transition probabilities renormalize over the beam.
3. **Final membership share (`membershipFloor` — semantics changed).**
   After the walk, memberships are normalized over the leaves the query actually
   reached; a leaf counts iff it holds ≥ membershipFloor of *that query's own*
   membership. Self-normalized → invariant to depth and fan-out. If nothing clears the
   share (very diffuse query), the single best leaf is kept: tail-trimming is this
   floor's job, residual declaration is the gate's.

Cumulative path pruning is a **purely numerical guard** (abandon paths below 1e−4
absolute posterior) with no membership semantics. `maxLeafAssignments` is enforced only
at arena/inference time (judge-call cost bound); construction membership is unbounded —
applying the cap during construction ranked leaves by joint path probability, which
mechanically penalizes depth and starved every newborn's children out of the global
top-k.

**DAG semantics.** With `enableBridging` on (implied by `dagMode = DAG_MAX`), the
competition set at each node is `children + crossLinkChildren`: a cross-link child
competes for descent and beam membership exactly like a tree child. A node reached
through several parents accumulates its path masses by log-sum-exp, so a bridged leaf's
membership is the sum over all its incoming paths. `isLeaf` is
`children.isEmpty() && crossLinkChildren.isEmpty()` — **parent count is deliberately
irrelevant**. (The previous definition also required `!isBridge && parents.size ≤ 1`,
which silently evicted every cross-link target from the leaf set the moment it gained a
second parent — the link would orphan its own destination. Likewise, `isBridge`-marked
internal nodes are no longer excluded from residual-destination candidacy: a domain
hosting a cross-link must keep its residual pool routable.)

## 3. Residual queries are retained, never dropped (`TaxonomyOperations.reassignQueries`)

A query that reaches no leaf is attributed to the node the walk converged to with
**full weight + its embedding + a residualQueries flag**: mass stays conserved, the C3
invariant ("internal hard queries are legal iff residual-flagged") holds by
construction, and `getAllQueriesInRegion` can see the embedding — which is what lets
the residual-split gate carve new children out of coherent residual mass. The previous
implementation recorded only a naked ID: the weight vanished (≈130–330 mass leaked per
iteration) and the residual-split mechanism could never recover the queries. With
residual routing enabled, internal nodes holding residual pools are also legitimate
membership destinations (`TrickleResult.leaves(enableResidual)`), and each pool counts
as its own cell in the global objective J — residual mass is measured, not ignored.
Residual pools are also the **fuel of the cross-link generator** (§6).

## 4. Split proposal vs. split acceptance (`TaxonomySplitter`)

EM clustering in a PCA subspace (32/64/128 dims by size) only *proposes* children.
Acceptance and population are decided in **routing geometry**: proposal vMFs are fitted
at 256 dims, every target query is re-assigned by the same level-local vMF posterior
the trickler uses, and the split is rejected unless **every child holds ≥
minClusterSize under that routed assignment** ("not routing-sustainable"). Children are
then refitted on their routed populations, and the separation gate + sibling
distinctness evaluate the routed partition. Without this, children were born with the
clustering's population and starved under routing within 1–2 iterations (63 % of pruned
nodes died ≤ 2 iterations after birth; ~60 spawned/~40 pruned per iteration,
permanently). The in-pass "macro-concept decomposition" recursion was removed for the
same reason: oversized children are re-evaluated next iteration under full
trickle/collapse/refit feedback.

## 5. Global-J proposal gating of every structural edit (`tryProposal`)

Structural refinement never applies edits by local rules alone. Every candidate edit is
a **proposal**, evaluated empirically against the global objective J:

1. snapshot the DAG state (`GraphStateBackup` — topology incl. cross-links, parameters,
   populations);
2. apply the edit tentatively, recompute shrinkages, clear and fully **re-route every
   query** through the modified DAG;
3. compute `J = computeDagSeparationJ(root, allEmbeddings)`;
4. restore the snapshot; commit only if `ΔJ > threshold · π_S`, where
   `π_S = n_S(n_S−1) / Σ_cells n_c(n_c−1)` is the proposal site's share of all
   within-cell pairs (capped at 1). π-scaling makes the bar proportional to the mass
   the edit can actually move — a global constant would be unreachable for small sites
   and trivial for large ones.

The **sign of the threshold encodes the edit's direction**:

- **Shrink edits** (starved-leaf prune/merge, sibling merges, redundant fusions, upward
  dissolution of sole children) pass `−separationEpsilon`: they simplify the graph and
  are accepted unless they *hurt* J beyond the hysteresis.
- **Growth edits** (splits, cross-links) pass `+separationEpsilon`: added complexity
  must *strictly improve* J beyond the noise floor.

Proposal sites: node splits, starved-leaf handling (three-way argmax: keep /
prune-absorb into parent / fuse into nearest sibling), sibling merging, redundant
fusions (`μ` cosine > `fusionSimilarityThreshold` as a cheap pre-filter, J as the
judge), upward dissolution of sole children (children re-parented up, queries
residual-flagged upward, GT anchors keep identity, bridged children and depth ≤ 1
excluded), and cross-link insertion (§6). Starved-leaf detection uses the flat
`branch < minClusterSize` floor — symmetric with the split floor: big enough to be
born ⇒ big enough to live.

## 6. Cross-linking: the polyhierarchy growth edit (`TaxonomyMerger.proposeCrossLinksWithProposals`)

The pipeline distinguishes two multi-parent mechanisms that were historically conflated:

- **Fusion** (`fuseNodes`) is a *shrink* edit: it destroys one node identity, unions its
  queries into the survivor, and redirects the dead node's parents — a bridge appears
  only as a side effect. In the old pipeline this was the *only* source of multi-parent
  nodes, triggered by raw cosine alone (which produced the grandparent-bridge
  degeneracy). It survives today strictly as a J-gated shrink proposal.
- **Cross-linking** is a *growth* edit and the intended polyhierarchy operator: both
  identities survive, and a node N gains a **second parent** P because P's residual
  queries demonstrably fit N. A biostatistics question sits between Math and Biology;
  under a strict tree it can only pick one branch, fail to specialize there, and
  residualize at the domain anchor. The cross-link gives it a legitimate second path.

**Generation (cheap, no re-routing).** For each host P (internal, depth ≥ 1, residual
pool ≥ `secondaryMassFloor`), each candidate N is scored by how many of P's residuals
it *captures*, where capture uses the trickler's own descent-gate formula:
`⟨μ_N, x⟩ ≥ r̄_P · ⟨μ_P, x⟩`. "Captured" therefore means "will actually descend at P
once the edge exists" — not a proxy similarity. A candidate survives iff it captures
≥ `secondaryMassFloor` queries AND ≥ `bridgeSupportRelFraction` of P's pool; the top 3
per host go to the J gate.

**Guards** (each corresponds to a bug class already hit):
- *Acyclicity*: N must not be an ancestor of P (checked against the ancestor map,
  rebuilt after every acceptance).
- *No redundant/grandparent edges*: P must not be an ancestor or descendant of N or of
  any existing parent of N — the degeneracy that once bridged a node to its own
  grandparent.
- *Cross-domain requirement*: P and N must live under disjoint depth-1 tree ancestors.
  The operator means "concept shared across domains"; the intra-branch case is
  eliminated by construction (it is what transitive reduction exists to kill).

**Acceptance** is the standard proposal gate with the growth-side threshold and —
critically — `site = N`, the **target**: `ΔJ > separationEpsilon · π_N`. π must scale
with the mass the edit can actually move (N's cell composition plus the captured pool).
Scaling by the whole host domain's mass (π_Psychology ≈ 0.24) makes the bar
unreachable for any small-concept link regardless of merit — measured live: a genuinely
positive ΔJ = 0.00037 was rejected 7× under a host-scaled bar before the fix. Every
attempt (accepted or not) is appended to `bridge_candidates.csv`
(iteration, edge, captured count, pool fraction, outcome).

**Interaction with the rest of the pipeline** (all pre-existing, verified):
`prunePassthroughNodes` refuses to dissolve multi-parent children; transitive reduction
exempts bridge edges; `GraphStateBackup` snapshots and restores cross-link topology;
`TaxonomyPersistence` round-trips `crossLinkChildIds`/`parentIds`; the **GED stabilizer
counts cross-link edges as relations**, so an accepted (or later removed) bridge breaks
the convergence streak like any tree edit — bridge oscillation cannot hide
(`TaxonomyStabilizer`, changed in rev. 3).

**Observed behavior (first converged run):** proposals fired exactly where the residual
analysis predicted (Psychology, Other, Biology hosts); the gate discriminated within a
host's candidate list (accepted the 12/47-capture candidate at Psychology while
rejecting its 9/47 and 8/47 siblings); accepted links drained their motivating pools
(Psychology 47 → 6 within one iteration of its first accept); 4/48 acceptance overall.
One residual hub remained (EC#58, 261 residuals across 11 domains) that the gate
consistently refused to bridge anywhere — correctly read as "belongs to no existing
leaf": a residual-split candidate, not a bridging candidate.

## 7. Supporting changes

- **Iteration 1 preserves the bootstrap**: trickle reassignment is skipped at i = 1, so
  the ground-truth anchor assignment (weight 1.0) survives the first
  split/optimize/refit pass; geometric reassignment starts at iteration 2.
  `enableGtWarmStart` stays off — no bias patch needed.
- **EMA centroid blending removed** (matched A/B runs: amplifies oscillation).
- **Kappa**: Banerjee closed form + up to 5 Newton–Raphson steps on `A_d(κ)=r̄` +
  Hornik–Grün shrinkage + parent-anchored EB blend (weight 0 at ρ=d/n≤2 → 1 at ρ≥10).
- **Routing ECE** computed at domain granularity: per query, real normalized leaf
  weights aggregated onto depth-1 ancestors, compared in category-string space (the old
  wiring hard-coded conf ≡ 1 vs mismatched label spaces → ECE pinned at exactly 1.0).
- **π-denominator correctness**: the pairwise denominator walk deduplicates multi-parent
  nodes (a fused node under two parents was previously double-counted).

## 8. Parameters after the redesign

| Parameter | Meaning | Canonical |
|---|---|---|
| `separationEpsilon` | Min chance-corrected separation for splits; ± threshold of the proposal gate (growth edits +ε·π, shrink edits −ε·π) | 0.01 (calibrate) |
| `routingBeamGamma` | Per-level beam: additive cosine margin below the best sibling's dot | 0.015 |
| `membershipFloor` | Min share of a query's own membership for a leaf to count | 0.25 |
| `minClusterSize` | Birth floor (routed) and survival floor, same number | 50 |
| `secondaryMassFloor` | Min residual pool for a cross-link host; min captured queries for a candidate | 2.0 (calibrate ↑) |
| `bridgeSupportRelFraction` | Min fraction of the host's pool a candidate must capture | 0.10 |
| `fusionSimilarityThreshold` | Cheap μ-cosine pre-filter for redundant-fusion proposals (J decides) | 0.90 |

Removed entirely: `emaAlpha`, `routingSoftmaxTau`, `tauKappaScalingFactor`,
`assignmentCosineGap`, `deltaAssign`, dynamic-temperature γ, κ-adaptive margins, and all
Source-A/B bridge knobs (`bridgeSeparationCeiling`, `minBridgeCoverage`,
`bridgeParentBudget`, `bridgeMaxArity`, `maxBridgeNodes`). The descent gate has no
parameter (`descentMargin` exists in config plumbing but is superseded by the
Jensen-tight `r̄_p` factor and unused). Proposal acceptance has no parameters of its
own — it reuses `separationEpsilon` and measures J directly.

## 9. Known open items

- **EC#58 residual hub**: 261 residuals across 11 domains that no cross-link can place —
  the dominant remaining residual mass. Next candidate mechanism: residual splitting at
  that node (the machinery exists; check why its pool has not carved children).
- **`secondaryMassFloor` = 2.0 is too permissive**: 2-capture proposals re-fire and
  re-reject every iteration (harmless but wasted J evaluations). Raise toward 5–10 in
  calibration.
- **Tree metrics under polyhierarchy**: dendrogram purity and ancestor-correct assume a
  tree; with real multi-parent nodes the defensible definition is *best-path* (any
  routing path has the correct ancestor), reported alongside the strict all-paths
  version. Decided before measuring, not after. Panel additions pending: bridge count,
  cross-domain bridge fraction, mean parents/node, residual rate.
- **Two claims, keep them distinct in the thesis**: query-level soft multi-membership
  (~12.7 % of queries at >1 leaf via the beam) vs concept-level polyhierarchy (a node
  with parents in two domains). Rev. 3 demonstrates both; earlier runs supported only
  the first.
- The parent's μ fit includes its residual-flagged queries (κ excludes them); this
  feedback slightly favors re-residualizing the same queries.
- Proposal evaluation is a full re-route per candidate edit (~200 ms at 8k queries) —
  fine at current scale, batch/cache if the corpus grows.
