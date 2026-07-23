# DAG Construction Mechanisms — Current Design (2026-07-23)

Authoritative description of the construction pipeline's decision mechanisms after the
2026-07-23 redesign. Supersedes the corresponding sections of
`evolutionary-pipeline/discovery-optimization.md` (kept for history). Validated by the
first fully converged canonical run (seed 42): GED reached +0/−0 with the convergence
streak starting at iteration 34, **zero** C3 invariant violations across the whole run,
all 45 leaves ≥ minClusterSize, no wrapper chains, ECE a calibrated 0.22–0.32.

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
- sibling merging (`TaxonomyMerger.mergeSimilarSiblings`, computed on branch-query
  sufficient statistics),
- sibling distinctness of new children,
- residual-split viability.

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

1. **Descent-vs-residual gate (parameter-free).** At each internal node, descend iff
   some child's mean direction matches the query at least as well as the node's own:
   `max_c ⟨μ_c, x⟩ ≥ ⟨μ_p, x⟩`. This is the parent-vs-children Bayes factor at
   threshold 1 in the shared-concentration limit. Directions, not densities: the
   Hornik–Grün shrinkage `(n−1)/(n+d−2)` scales with n, so parents are fitted
   systematically sharper than children and density comparisons carry tens of nats of
   bias (measured: 56 % of the corpus residualized at anchors under the density form).
   Queries at a region's own center that no child specializes in stay at the parent as
   residuals — the honest residual semantics.
2. **Per-level relative beam (`routingBeamGamma`, default 0.15).** A child stays on the
   beam iff its responsibility is ≥ γ × the best sibling's. Relative-to-best is
   scale-free and concentration-adaptive: 0.50/0.50 sharing keeps both children,
   0.90/0.05 drops the tail — an absolute floor cannot distinguish those. The argmax
   always passes, so the beam is never empty. Transition probabilities renormalize over
   the beam.
3. **Final membership share (`membershipFloor`, default 0.10 — semantics changed).**
   After the walk, memberships are normalized over the leaves the query actually
   reached; a leaf counts iff it holds ≥ membershipFloor of *that query's own*
   membership. Self-normalized → invariant to depth and fan-out. If nothing clears the
   share (very diffuse query), the single best leaf is kept: tail-trimming is this
   floor's job, residual declaration is the gate's.

Cumulative path pruning is now a **purely numerical guard** (abandon paths below 1e−4
absolute posterior) with no membership semantics. `maxLeafAssignments` is enforced only
at arena/inference time (judge-call cost bound); construction membership is unbounded,
exactly as the config always documented — applying the cap during construction ranked
leaves by joint path probability, which mechanically penalizes depth and starved every
newborn's children out of the global top-k.

## 3. Residual queries are retained, never dropped (`TaxonomyOperations.reassignQueries`)

A query that reaches no leaf is attributed to the node the walk converged to with
**full weight + its embedding + a residualQueries flag**: mass stays conserved, the C3
invariant ("internal hard queries are legal iff residual-flagged") holds by
construction, and `getAllQueriesInRegion` can see the embedding — which is what lets
the residual-split gate carve new children out of coherent residual mass. The previous
implementation recorded only a naked ID: the weight vanished (≈130–330 mass leaked per
iteration) and the residual-split mechanism could never recover the queries.

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

## 5. Upward dissolution of sole children (`TaxonomyMerger.prunePassthroughNodes`)

A parent's **only** tree child separates no pair of queries its parent doesn't already
separate — inserting it changes the hierarchy objective by exactly zero, however many
children it has. Such a child is dissolved upward: its children are hoisted to the
parent, its queries move up (residual-flagged while the parent stays internal), and the
loop repeats while exactly one tree child remains, so whole chains flatten in one pass.
This subsumes the old chain-middle bypass and — critically — removes the "swallow"
wrapper (a generalist child that captured 100 % of its parent's population, observed as
`Business → #107 (0/690)`), while preserving the parent's identity (GT anchors keep
their label and anchor role). Bridged children (multiple parents) and depth ≤ 1 are
left alone. Starvation pruning uses the flat `branch < minClusterSize` floor —
symmetric with the split floor: big enough to be born ⇒ big enough to live.

## 6. Supporting changes

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

## 7. Parameters after the redesign

| Parameter | Meaning | Canonical |
|---|---|---|
| `separationEpsilon` | Min chance-corrected separation for any structural accept | 0.01 (calibrate) |
| `routingBeamGamma` | Per-level beam width as fraction of best sibling responsibility | 0.15 (calibrate) |
| `membershipFloor` | Min share of a query's own membership for a leaf to count | 0.10 (calibrate) |
| `minClusterSize` | Birth floor (routed) and survival floor, same number | 50 |

Removed entirely: `emaAlpha`, `routingSoftmaxTau`, `tauKappaScalingFactor`,
`assignmentCosineGap`, `deltaAssign`, dynamic-temperature γ, κ-adaptive margins.
The descent gate has no parameter.

## 8. Known open items

- **Residual volume (design fork, undecided):** at the converged equilibrium ~45 % of
  the corpus rests as residuals at internal nodes — the direction gate's honest verdict
  that domain centers don't decompose. Option A (current): tight specialist leaves,
  ~55 % arena coverage. Option B: drop the gate, descend always, let beam + share floor
  spread central queries; restore residuals later as an explicit outlier test.
- The parent's μ fit includes its residual-flagged queries (κ excludes them); this
  feedback slightly favors re-residualizing the same queries.
- Sibling merging has fired 0 times at `sep < ε = 0.01`; the merge threshold likely
  needs its own (higher) calibrated value.
- The convergence streak needs `numIterations` ≥ ~45 to complete after the structure
  stabilizes (~iteration 33).
