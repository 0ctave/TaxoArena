# TaxoArena DAG Construction — Logic and Mathematics (2026-07-23)

Definitive specification of the construction pipeline as implemented. Supersedes
`dag-construction-mechanisms.md` (rev. 3) as the mathematical reference; that document
retains the redesign history and failure-mode archaeology.

Corpus: MMLU-Pro, 8,353 construction queries (70 % stratified split, seed-controlled),
embedded and consumed as L2-normalized vectors on the unit sphere `S^{d-1}`, `d = 256`
(MRL truncation; `dimForDepth` is flat). One converged run builds the canonical
polyhierarchy in ~2.5 min (~8.6 s/iteration steady-state).

---

## 1. Objects

**Node** `v`: label, depth, tree children `C(v)`, cross-link children `X(v)`, parents
`P(v)` (both edge types), soft assignment `w_v : queries → [0,1]`, residual pool
`R(v)` (query ids), and a fitted von Mises–Fisher component `(μ_v, κ_v)`:

```
p(x | μ, κ) = C_d(κ) · exp(κ ⟨μ, x⟩),   x, μ ∈ S^{d-1}, κ ≥ 0
```

**Leaf**: `C(v) = ∅ ∧ X(v) = ∅`. Parent count is irrelevant — a cross-link target with
several parents remains a leaf (routing destination, arena unit, J-cell).

**DAG**: single root (depth 0), 14 domain anchors (depth 1), emergent concepts below.
Tree edges (`C`) span every node; cross-link edges (`X`) add second parents. Acyclicity
is an enforced invariant, checked by guards at edge creation and validated per run.

**Invariants** (checked every proposal / exported per run):
- **Mass conservation**: `Σ_v Σ_q w_v(q) = N` (residual-retained queries carry weight 1
  at their pool node); per-query total weight ≤ 1 + ε.
- **C3**: an internal node holds hard queries iff they are residual-flagged.
- **Acyclicity**, no orphan nodes, no duplicate bridges.

## 2. vMF estimation

Per node, on its routed population (κ excludes residual-flagged queries; μ includes
them):

- Resultant length `r̄ = ‖Σ x_i‖ / n`, `μ = Σ x_i / ‖Σ x_i‖`.
- κ by Banerjee closed form `κ₀ = r̄(d − r̄²)/(1 − r̄²)` + ≤ 5 Newton–Raphson steps on
  `A_d(κ) = r̄` where `A_d = I_{d/2}/I_{d/2−1}`.
- **Hornik–Grün shrinkage** `r̄ ← r̄·(n−1)/(n+d−2)`: the raw MLE overestimates κ
  systematically at small `n/d`; the correction scales with n, which is exactly why
  **density comparisons across levels are forbidden** in routing (parents, fitted on
  larger n, always look sharper — measured 56 % of the corpus mis-residualized under a
  density gate).
- Parent-anchored empirical-Bayes blend for thin nodes: weight 0 at `ρ = d/n ≤ 2` → 1
  at `ρ ≥ 10` toward the parent's κ.

## 3. One separation score for every gate

All structural accept/reject decisions use the **chance-corrected separation score**.
For a partition of a query set into cells `S_c` (sums of unit vectors):

```
W(S)   = |S|² − ‖Σ_{x∈S} x‖²                          (within-scatter)
E      = W(total) · Σ_c n_c(n_c−1) / (n(n−1))          (expected within-scatter of a
                                                        uniformly random partition
                                                        into the same sizes)
score  = 1 − Σ_c W(S_c) / E
```

Properties: 1 = perfect, ≈ 0 = random, < 0 = anti-clustered, and **exactly 0 for
k = 1** — a wrapper (non-separating split) can never clear a positive floor. The
chance correction (ARI-style) removes the mechanical dependence on k and cell sizes,
so a single `separationEpsilon` has the same meaning at every site: split acceptance,
EM k-selection, sibling merging, sibling distinctness, residual-split viability.
(This is *not* Dasgupta's LCA cost and must not be cited as such.)

**Global objective** `J = computeDagSeparationJ`: the same score over the full corpus
with one cell per leaf (soft weights) plus one cell per internal node's residual pool.
J is the single number every structural proposal is judged against.

## 4. Trickle routing (per query, top-down)

At each internal node with competition set `K = C(v) ∪ X(v)` (cross-links compete
exactly like tree children):

1. **Descent-vs-residual gate (Jensen-tight, one optional slack knob).** Descend iff
   ```
   max_{c∈K} ⟨μ_c, x⟩ ≥ (r̄_v − δ) · ⟨μ_v, x⟩
   ```
   where `r̄_v = ‖Σ_c wₘ(c)·μ_c‖ ∈ [0,1]` is the resultant length of the tree
   children's mass-weighted centroid mix (`childCentroidShrinkage`, recomputed after
   every structural change) and `δ = descentMargin ≥ 0` (default 0). Rationale: the
   parent's direction is approximately the *normalized* mean of its children's, so the
   raw parent dot overstates what children can collectively achieve by the factor
   `1/r̄_v`; multiplying by `r̄_v` makes the test the tight bound
   `max dot ≥ weighted-mean dot`. At `δ = 0` a query is residual only when its best
   child is worse than the children's own weighted-average alignment — genuinely
   unexplained mass. `δ > 0` trades measured residuals for softer leaf populations
   (and starves the cross-link generator, §7 — measured at δ=0.05: residuals −38 %,
   bridges 11 → 4, purity −1.9 pts).
   Directions only, never densities (§2).
2. **Sibling competition, direction-only with an additive cosine beam.** Scores
   `f_c = κ̄·⟨μ_c, x⟩` with the *shared mean* `κ̄` of the level (per-child κ excluded —
   no winning by concentration bookkeeping). The beam keeps
   `{c : ⟨μ_c,x⟩ ≥ max_c' ⟨μ_c',x⟩ − γ}`, `γ = routingBeamGamma`; the argmax always
   survives. Transition probabilities renormalize over the beam
   (`softmax` of `f_c` restricted to the beam).
3. **Path bookkeeping.** Walk all beam children, accumulating log path mass; a node
   reached by several paths log-sum-exps them (leaves accumulate multi-parent mass — a
   bridged leaf's membership is the sum over its incoming paths). Paths below absolute
   posterior 1e−4 are abandoned (numerical guard only, no membership semantics); a
   within-walk cycle guard bounds re-descent.
4. **Final membership share.** Memberships normalize over the destinations actually
   reached; a leaf counts iff it holds ≥ `membershipFloor` of *that query's own*
   membership (self-normalized ⇒ invariant to depth/fan-out). If nothing clears the
   floor, the single best destination is kept — tail-trimming is this floor's job,
   residual declaration is the gate's. `maxLeafAssignments` caps arena-time judge
   cost only; construction membership is unbounded.

**Residual retention.** A query that reaches no leaf is retained at the node the walk
converged to with full weight + embedding + residual flag: mass is conserved, C3 holds
by construction, pools are measurable, routable destinations, J-cells — and the fuel
of the cross-link generator.

## 5. Split operator (`TaxonomySplitter`)

Proposal by clustering, acceptance in routing geometry:

1. Target population: the node's local soft assignment (for internal nodes this *is*
   the residual pool), in deterministic (queryId-sorted) order.
2. PCA to 32/64/128 dims (size-dependent) via power iteration with **seeded init**
   (reproducibility, §9); vMF k-means with k ∈ {2..4} selected by chance-corrected
   marginal improvement ≥ ε; every EM cluster ≥ `minClusterSize`.
3. **Routing-sustainability**: proposal vMFs are refitted at 256 d; every target query
   is re-assigned by the same level-local posterior the trickler uses; reject unless
   every child holds ≥ `minClusterSize` under that routed assignment. (Without this,
   63 % of pruned nodes died ≤ 2 iterations after birth — permanent churn.)
4. Chance-corrected separation of the *routed* partition ≥ ε (2ε for small
   populations) + distinctness ≥ ε against every existing sibling branch.
5. Global veto (§8): accepted iff `ΔJ > 0`.

## 6. Shrink operators (`TaxonomyMerger`)

- **Starved-leaf three-way argmax**: leaf branch < `minClusterSize` (birth floor =
  survival floor) → evaluate {keep, prune-absorb into parent, fuse into nearest
  sibling} by measured J; best wins under the shrink threshold.
- **Sibling fusion**: pairwise chance-corrected separation of branch statistics < ε →
  union-find clusters fused, J-gated.
- **Redundant fusion**: non-sibling pairs with `⟨μ_A, μ_B⟩ > fusionSimilarityThreshold`
  (cheap pre-filter; J decides). Fusion redirects the dead node's parent edges
  **type-preservingly** (a cross-link parent keeps a cross-link edge to the survivor;
  the historical bug that converted or leaked these edges produced routable ghost
  nodes).
- **Upward dissolution of sole children**: a parent's only tree child separates
  nothing (score ≡ 0 at k = 1); hoist grandchildren, residual-flag queries upward.
  Bridged children (|P| > 1) and depth ≤ 1 are exempt.
- **Transitive reduction**: removes parent edges implied by ancestry; tree edges
  (`treeParentId`) and bridge edges are protected.

Fusion is a *shrink* edit that destroys an identity; any multi-parent node it leaves
behind is a side effect. The intended polyhierarchy operator is §7.

## 7. Cross-link operator — the polyhierarchy growth edit

A node `n` gains a **second parent** `h` because `h`'s residual pool demonstrably fits
`n`. Under a strict tree, a genuinely cross-domain query (biostatistics between Math
and Biology) can only pick one branch, fail to specialize there, and residualize; the
cross-link gives it a legitimate second path.

**Generation** (cheap, no re-routing): for each host `h` (internal, pool ≥
`secondaryMassFloor`), each candidate `n` captures residual `x` iff

```
⟨μ_n, x⟩ ≥ (r̄_h − δ) · ⟨μ_h, x⟩
```

— *identical to the runtime descent gate*, so "captured" means "will actually descend
at h once the edge exists", not proxy similarity. Candidate survives iff captures ≥
`secondaryMassFloor` and ≥ `bridgeSupportRelFraction · |R(h)|`; top 3 per host proceed.

**Guards** (each mapped to an observed failure mode): acyclicity (`n` not an ancestor
of `h`); no grandparent/redundant edges (`h` not an ancestor/descendant of `n` or of
any existing parent of `n`); cross-domain requirement (disjoint depth-1 tree
ancestors); all re-checked against a rebuilt ancestor map after every acceptance.

**Acceptance**: proposal gate (§8) with the growth threshold and `site = n` (the
target): `ΔJ > ε·π_n`. π must scale with the mass the edit can actually move (n's
cell + the captured pool); host-mass scaling (π_h ≈ 0.2 for a domain) makes the bar
unreachable for any small concept regardless of merit (measured: ΔJ = +0.00037
rejected 7× under a host-scaled bar).

**Negative-result memo**: a rejected (h, n) pair with identical capture/pool counts
under an identical edge-topology fingerprint is skipped (deterministic outcome);
any topology change clears the memo.

## 8. The proposal gate — every structural edit is measured, not predicted

```
snapshot state (GraphStateBackup: topology incl. cross-links, parameters, assignments)
apply edit tentatively
if the edit changed no edges: restore, reject          (early exit — no re-route)
[first proposal per phase: restore, re-route, J → baseline; re-apply edit]
recompute shrinkages; clear and fully re-route every query; J' := J(DAG')
accept iff  ΔJ = J' − J  >  θ · π_S ;  else restore
```

with `π_S = n_S(n_S−1) / Σ_cells n_c(n_c−1)` (site's share of within-cell pairs,
capped at 1, multi-parent nodes deduplicated) and the **threshold sign encoding the
edit's direction**:

| Edit | θ | Semantics |
|---|---|---|
| Split | `0` | **Veto**: quality is already gated locally (§5); global J only rejects degradation. A positive ε·π toll double-charges through a diluted lens — global J measures cells against the whole-corpus expectation, so refining a tight region gains ~an order less globally than its local separation indicates (measured: Business, 620 q, local sep 5.8ε, ΔJ +0.00148, permanently vetoed at toll 0.00208 — domains stayed childless and depth stalled). |
| Cross-link | `+ε`, site = target | Growth must strictly improve J beyond noise, scaled to the moved mass. |
| Prune / fusion / dissolution | `−ε` | Shrink edits simplify; accepted unless they *hurt* J beyond hysteresis. |

Accepted proposals update the cached baseline; the baseline is invalidated per phase.

## 9. Convergence and reproducibility

- **GED stabilizer**: per iteration, count node and relation adds/removes — **cross-link
  edges count as relations**, so bridge oscillation breaks the streak like tree churn.
  Convergence = 5 consecutive zero-GED iterations (after ≥ 0.8·|domains| iterations).
  Canonical runs converge at iteration ~15.
- **Determinism**: with a fixed seed the pipeline is reproducible. Sources fixed:
  PCA power-iteration init seeded from the problem shape (was `ThreadLocalRandom` —
  identical-code seed-42 runs previously produced 66–69 leaves / 94–275 residuals);
  EM inputs sorted by queryId (ConcurrentHashMap iteration order is
  insertion-history-dependent, and float-sum order flips decisions at boundaries);
  representative-query sampling seeded (labels). Residual last-bit float
  nondeterminism from parallel reduction order may survive; it does not select
  different structures in practice.
- **Performance** (8,353 queries, ~100 nodes): steady-state ~8.6 s/iteration. The unit
  cost is one full re-route (parallel trickle of the corpus); per-query projections
  are computed once and cached (`Embedding.projectTo`, flat 256 d); no-op proposals
  exit before re-routing; rejected cross-links are memoized per topology.

## 10. Parameters

| Parameter | Meaning | Canonical |
|---|---|---|
| `separationEpsilon` | Separation floor for splits/merges/distinctness; ±threshold magnitude of the proposal gate (§8) | 0.01 |
| `membershipFloor` | Min share of a query's own membership for a destination to count | 0.25 |
| `routingBeamGamma` | Additive cosine beam margin below the best sibling | 0.015 |
| `descentMargin` δ | Slack below the Jensen-tight descent bar; 0 = exact bound | 0.0 |
| `minClusterSize` | Birth floor (routed) = survival floor | 50 |
| `secondaryMassFloor` | Cross-link host pool floor and candidate capture floor | 2.0 |
| `bridgeSupportRelFraction` | Min fraction of the host pool a candidate must capture | 0.10 |
| `fusionSimilarityThreshold` | μ-cosine pre-filter for redundant-fusion proposals | 0.90 |
| `maxLeafAssignments` | Arena-time judge-cost cap (never construction) | 5 |
| `maxDepth` | Recursion cap (not binding; realized depth ≤ 4) | 8 |

The descent gate itself is parameter-free at δ = 0; the proposal gate has no
parameters of its own. All four factors currently under L9 sweep:
`descentMargin × minClusterSize × secondaryMassFloor × routingBeamGamma`
(`tools/tuning/sweep_spec.toml`, launcher `tune.bat`).

## 11. What a converged run looks like (seed 42, canonical config)

~100 nodes, ~57–69 leaves (median ~90 queries), depth ≤ 4, 7–12 bridge nodes
(J-accepted cross-links + type-preserved fusion survivors), residuals 119–275
(measured central/cross-domain mass, every pool having had its bridging options
J-evaluated), weighted leaf purity ~0.71 (tree baseline 0.72), routing ECE ~0.22–0.24,
acyclic, zero orphans, mass conserved. Two claims, kept distinct: query-level soft
multi-membership (~13 % of queries at > 1 leaf via the beam) and concept-level
polyhierarchy (nodes with parents in two domains) — the current pipeline demonstrates
both.

Known structural variance across seeds/configs (which borderline domain splits, where
residual hubs settle) is the subject of the sweep; per-seed determinism (§9) makes
those comparisons exact.
