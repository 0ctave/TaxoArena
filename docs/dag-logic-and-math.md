# Construction — logic and mathematics (current specification)

Status: **current** as of 2026-07-27, branch `tree-only`, commit `c381211`. This is the
authoritative mathematical reference for the construction pipeline as implemented.
`dag-construction-mechanisms.md` carries the design rationale, the failure archaeology, and
the polyhierarchy negative result.

**Naming.** The system is a **tree**, not a DAG. Cross-linking was removed at `334b95d` and
the polyhierarchy result is reported as a negative one
(`dag-construction-mechanisms.md` §7). The `dag` in file names, `DagMode` and
`computeDagSeparationJ` is historical and has not been renamed; read "DAG" as "the induced
hierarchy" throughout. `GraphNode.crossLinkChildren` still exists and is **permanently
empty** — with no generator, `children + crossLinkChildren` is exactly `children`.

Corpus: MMLU-Pro, **8299** construction queries at the frozen artifact
(`testRatio = 0.3`, `seed = 42`), embedded and consumed as L2-normalised vectors on the unit
sphere `S^{d-1}` with `d = 256` (MRL truncation of 4096-dim embeddings; `dimForDepth`
returns a flat 256 at every depth and keeps a deliberately unused depth argument so that a
width change stays a one-place edit across its 11 call sites). Earlier documents quote 8353
construction queries; that is a different split of the same corpus and the two must not be
mixed in one table.

---

## 1. Objects and invariants

**Node** `v`: label, depth, children `C(v)`, parent, soft assignment `w_v : queries ->
[0,1]`, residual pool `R(v)`, and a fitted von Mises-Fisher component `(mu_v, kappa_v)`:

```
p(x | mu, kappa) = C_d(kappa) * exp(kappa <mu, x>),    x, mu in S^{d-1},  kappa >= 0
```

**Leaf**: `C(v)` empty. **Root** at depth 0; 14 domain anchors at depth 1, unprunable
(constraint C4); emergent concepts below.

**Invariants**, checked on every proposal and exported per run:

* **Mass conservation** `sum_v sum_q w_v(q) = N`, with residual-retained queries carrying
  weight 1 at their pool node, and per-query total weight `<= 1 + eps`. This check runs on
  *every* proposal, deliberately: it is cheap next to the full re-route it follows, and it
  is what caught the corpus-swallowing fusion, the `maxOf` weight destruction and the
  `mass > q_dir` excesses — all of which lived in iterations 2..N.
* **C3**: an internal node holds hard queries iff they are residual-flagged.
* Acyclicity, no orphans.

---

## 2. vMF estimation

Per node, on its routed population (`kappa` excludes residual-flagged queries; `mu`
includes them):

* `rbar = ||sum x_i|| / n`,  `mu = sum x_i / ||sum x_i||`.
* `kappa` by the Banerjee closed form `kappa_0 = rbar (d - rbar^2)/(1 - rbar^2)` followed by
  up to 5 Newton-Raphson steps on `A_d(kappa) = rbar`, `A_d = I_{d/2}/I_{d/2-1}`.
* **Hornik-Grün shrinkage** `rbar <- rbar (n-1)/(n+d-2)`. The raw MLE overestimates `kappa`
  at small `n/d`.
* Parent-anchored empirical-Bayes blend for thin nodes: weight 0 at `rho = d/n <= 2`, ramping
  to 1 at `rho >= 10`.

**The shrinkage is why density comparisons are forbidden in routing.** It scales with `n`,
so parents — fitted on larger populations — are systematically sharper than their children.
A density-based descent gate mis-residualised 56% of the corpus at the anchors. See §8.

`kappa` never reaches bit-identity between iterations. It converges asymptotically and
drifts at ~1e-13 forever, on 138 of 139 measured sites, while every gate outcome stays
fixed. This is a load-bearing fact for the proposal memo (§6) and for the certificate (§9).

---

## 3. One separation score for every gate

For a partition of a query set into cells `S_c` (sums of unit vectors):

```
W(S)   = |S|^2 - ||sum_{x in S} x||^2                        (within-scatter)
E      = W(total) * sum_c n_c(n_c - 1) / (n(n - 1))          (expected within-scatter of a
                                                              uniformly random partition
                                                              into the same sizes)
score  = 1 - sum_c W(S_c) / E
```

Properties: 1 for a perfect partition, ~0 for a random one, negative for anti-clustered, and
**exactly 0 at k = 1**, so a wrapper (non-separating) candidate can never clear a positive
threshold. The chance correction is ARI-style; it removes the mechanical dependence of the
raw within/total ratio on `k` and on cell sizes. **It is not Dasgupta's (2016) LCA cost and
must not be cited as such** — the persisted field name `dasguptaDeltaNorm` is historical.

**Global objective** `J = computeDagSeparationJ(root, allEmbeddings)`: the same score over
the full corpus with one cell per leaf (soft weights) plus one cell per internal node's
residual pool. `J` is the single number every structural proposal is judged against.

Note what `J` is and is not: an **in-sample geometric** criterion. It does not measure
evaluative usefulness, and the two have disagreed at least twice — `proposalSeparationBar`
0.020 vs 0.025 (J favoured 0.020, held-out Top-1 favoured 0.025), and the router correction
(J +20.4% while median per-cell reliability fell). *Corrected 2026-07-30: the reliability
figures once quoted here, 0.842 -> 0.745, were computed with the wrong constant and are
withdrawn (`measurement-discipline.md`). The disagreement between J and reliability is a
real one and is why it is worth stating; its magnitude is not currently measured.*

---

## 4. Trickle routing (per query, top-down)

At each internal node `v` with children `C(v)`:

**(1) Descent-vs-residual gate.**

```
descend  iff   max_{c} <mu_c, x>  >=  (rbar_v - delta) * <mu_v, x>
```

where `rbar_v = ||sum_c w_m(c) mu_c||` in [0,1] is the resultant length of the children's
mass-weighted centroid mix (`GraphNode.childCentroidShrinkage`, recomputed after every
structural change) and `delta = descentMargin`.

*Rationale.* The parent's direction is approximately the **normalised** mean of its
children's, so the raw parent dot overstates what the children can collectively achieve by
exactly `1/rbar_v`. Multiplying by `rbar_v` makes the comparison the tight (Jensen) bound
`max dot >= weighted-mean dot`. At `delta = 0` a query is residual only when its best child
does worse than the children's own weighted-average alignment — genuinely unexplained mass,
with no free parameter.

`delta` is a **mode selector**, not a tuned nuisance parameter: `delta = 0.12` is
routing-optimal with discovery off (the frozen artifact, zero residuals anywhere);
`delta ~ 0` turns discovery on at 756 residuals = 9.1% of the corpus and about 5 points of
routing degradation. See `incremental-taxonomy.md`.

**(2) Sibling competition — direction only, shared concentration, additive cosine beam.**

```
kappa_bar = mean_c kappa_c
f_c       = kappa_bar * <mu_c, x>
beam      = { c : <mu_c, x> >= max_c' <mu_c', x> - gamma },   gamma = routingBeamGamma
```

Per-child `kappa` and per-child normalisers are **excluded**, so a child cannot win queries
by concentration bookkeeping — only by direction. Relative-to-best is scale-free and adapts
to the realised competition: a 0.50/0.50 split keeps both children, a decisive win drops the
tail. The argmax always survives, so the beam is never empty. Transition probabilities are a
softmax of `f_c` renormalised over the beam.

This is the corrected form. The per-child density form
`logC_d(kappa_c) + kappa_c <mu_c, x>` is wrong for a cross-node decision and biases
assignment toward the concentrated sibling by tens of nats at `d = 256`. It has appeared
twice in this codebase; see `router-shared-kappa-correction.md`.

**(3) Path bookkeeping.** Walk all beam children accumulating log path mass. Paths below
absolute posterior 1e-4 are abandoned — a **purely numerical** guard with no membership
semantics.

**(4) Final membership share.** Memberships normalise over the destinations actually
reached; a leaf counts iff it holds at least `membershipFloor` of *that query's own*
membership. Self-normalised, hence invariant to depth and fan-out. If nothing clears the
share the single best destination is kept: tail-trimming is this floor's job, residual
declaration is the gate's. `maxLeafAssignments` caps arena-time judge cost only;
construction membership is unbounded.

**Residual retention.** A query reaching no leaf is retained at the node the walk converged
to, with full weight, its embedding, and a residual flag. Mass is conserved, C3 holds by
construction, and `getAllQueriesInRegion` can see the embedding — which is what lets the
residual-split gate carve children out of coherent residual mass. Recording a naked id
instead leaked 130-330 mass per iteration and made residual splitting unreachable.

---

## 5. Split operator (`TaxonomySplitter`)

Proposal by clustering; acceptance in routing geometry.

1. **Target population**: the node's local soft assignment (for an internal node this *is*
   its residual pool), in deterministic queryId-sorted order.
2. **Feasibility**: `mass >= 2 * minClusterSize`, and `mass <= |targetQueries|`.
3. **Proposal**: PCA to 32/64/128 dims by population size, via power iteration with a seeded
   init; vMF k-means (`performVmfKMeans`) at the requested `k`, every EM cluster at least
   `minClusterFrac = minClusterSize / n` of the population. `runVmfEm` has **no randomness**:
   `mu_1` is the normalised centroid and `mu_2..k` are deterministic farthest-point maximin.
   (The `k-means++` comment on it is a misnomer.)
4. **Routing sustainability + coarsening.** Proposal vMFs are refitted at 256 dims and every
   target query is re-assigned by `routeToVmfs`, which scores with the **shared** `kappa_bar`
   exactly as the trickler does. Under-floor fragments are not fatal: their components are
   **dropped** and every query is re-routed among the survivors, the same winner-take-all
   posterior, so nothing is force-assigned. Each pass removes at least one component,
   terminating at `k' >= 2` or rejection. The coarser partition must still clear the same
   acceptance bar below.
   *Why this exists:* without a routed-population check, children were born with the
   clustering's population and starved under routing within 1-2 iterations (63% of pruned
   nodes died within 2 iterations of birth). *Why the coarsening exists:* the all-or-nothing
   floor check vetoed whole splits forever on partitions like History `[147,164,1,28]` and
   Engineering `[306,193,120,25]`.
   *Residual difference, stated:* `routeToVmfs` is a hard argmax while the trickler is soft
   with a beam, so a child's production population is **>=** its hard-argmax population here.
   The check is conservative in the right direction; it is not exact equivalence.
5. **Separation gate**: chance-corrected separation of the **routed** partition
   `>= proposalSeparationBar`, a **LEVEL**. The min-pair statistic is the only separation
   gate; the joint k-way gate was removed at `58f4aed` after rejecting nothing in 5682
   opportunities (at routed `k = 2` the two statistics are computed from identical sufficient
   statistics and are the same number).
6. **Global gate** (§6).

### k-fallback (`e3c4b2c`)

Every `k` in `2..maxK` is offered in **ascending** order and the first one the objective
accepts is taken (`TaxonomyOperations`, `splitSingleNode(node, forcedK = k)`).

Before this, EM picked one `k` and a node whose single candidate failed any downstream gate
stayed an unsplit leaf with no recourse — which made `maxK` a **structural determinant**
rather than a cost cap: raising it 4 -> 6 collapsed the tree to 36 leaves and J 0.181169.

**Selection is lowest-k-first, not `argmax dJ`.** A maximum over several noisy `dJ` estimates
carries the same optimisation bias that rules out argmax-separation for choosing `k`: with 3
candidates the max is biased upward even when all three are equivalent, and the winner is
disproportionately whichever one's bootstrap SE happened to land low. Every candidate has
independently cleared the **same** gate, so the ordering only breaks ties among edits that
are each individually supported. Parsimony is the conservative tie-break, and it is
deterministic, which `argmax` is not.

*Why the fallback works — a mechanism, not a patch.* **EM at higher `k` followed by
coarsening is a better two-way splitter than EM at `k = 2` directly.** `k = 2` may route
`[95, 5]` and fail the floor, while `k = 3` routes `[40, 35, 25]` and coarsens to `[65, 35]`.
Priced at roughly 10 leaves and `dJ ~ 0.011`.

*Consequence:* `k = 2` rose from 58% to 80% of splits and trees became deeper — a binary
cascade. That is the selection rule working as specified; each extra level passed the gate on
its own evidence.

*Cost:* `performVmfKMeans` fans out over `2..maxK` internally and the fallback calls it once
per `k`, so EM work is `O(maxK^2)` — predicted 2.0x at `maxK = 4` and 3.0x at 6, observed
2.5x and 4.0x, the gap being PCA re-running per candidate. One call returning all candidates
is the fix; not done.

*Guards:* the memo fingerprint carries `k` (`proposalKey = "k$k"`), or a rejected `k = 2`
would memo-skip `k = 3` and record it `REJECTED` unevaluated. Coarsening can map different
`k` onto the same routed partition; duplicates are not deduplicated (dedup needs the routed
assignment, which is only known after `splitSingleNode` has mutated the node) and cost one
extra evaluation each.

### `marginalEps` vs `proposalSeparationBar`

`marginalEps` is a **DIFFERENCE** of separations ("does `k+1` buy enough over `k`?");
`proposalSeparationBar` is a **LEVEL** ("is this partition separated at all?"). One constant
served both until `e3c4b2c`. They are now independent config fields, both inert at their
defaults (`marginalEps = -1.0` means "fall back to the bar"). `marginalEps = 0` was measured
and **rejected**: 83 leaves, J 0.230247, and it relocates the threshold onto `maxK`.

---

## 6. The proposal gate — every structural edit is measured, not predicted

```
snapshot state (GraphStateBackup: topology, parameters, assignments)
apply edit tentatively
if the edit changed no edges: restore, reject                    (early exit, no re-route)
[first proposal per phase: restore, re-route, J -> baseline; re-apply]
recompute shrinkages; clear and fully re-route every query; assert mass; J' := J(T')
dJ := J' - J ;  dV := |V'| - |V|
capture cell assignments before and after; SE(dJ) := JBootstrap.pairedDeltaSe(before, after)
accept iff  dJ > max(tau, z * SE(dJ))      when SE(dJ) > 0
       or   dV < 0                         when SE(dJ) = 0
else restore
```

**Why paired.** Both sides share a corpus draw, so the paired bootstrap answers the question
the gate is actually asking — is this `dJ` distinguishable from zero — which `tau`, a float
tolerance, cannot.

**Why the `SE(dJ) = 0` clause is not a loophole.** `SE(dJ) = 0` identifies a **pure
structural** edit that moves no query's cell (a passthrough dissolution), for which `dJ` is
exactly 0 and `z` is undefined. Without the clause those edits could never commit and
wrapper nodes would accumulate through construction. There is an invariant check on this: if
`SE(dJ) = 0` while `dJ != 0`, the before/after capture points are inconsistent and every `z`
is being computed against the wrong baseline. It logs `[DJ-SE INVARIANT]`.

**Legacy arm.** `acceptanceZ = 0` selects the lexicographic rule `(J, -|V|)` against `tau`,
retained so the gate change is attributable.

**Termination.** Under either arm, `J` is bounded above and every accepted edit either
strictly increases `J` beyond `tau` or strictly decreases `|V|` at unchanged `J`, so no
infinite sequence of accepted edits exists. (Restoring this one-paragraph argument was the
substantive reason cross-linking's three-objective rule was removed; see
`dag-construction-mechanisms.md` §7.)

**Proposal sites**: node splits (GROW, one per `k`), starved-leaf handling (a three-way
argmax over keep / prune-absorb into parent / fuse into nearest sibling), sibling merging,
redundant fusion (`mu`-cosine above `fusionSimilarityThreshold` as a cheap pre-filter, `J` as
the judge), and upward dissolution of sole children (depth <= 1 exempt). Starved-leaf
detection uses the flat `branch < minClusterSize` floor, symmetric with the split floor: big
enough to be born, big enough to live.

### The proposal memo (`9a0aab2`, `a7fdf7d`)

A memo existed for years and had **never fired** — zero `[MEMOIZED REJECTION]` lines in any
run in the repository. The cause was the fingerprint, not the caching. It keyed on the raw
`Double` bits of every membership weight and on `site.vmfKappa`, both of which are re-derived
every iteration and neither of which ever reaches bit-identity.

Instrumenting a full canonical run over iterations 5..10 — after growth stops, when nothing
should move — measured which components are actually stable across 139 sites:

| component | constant on |
|---|---|
| key-set hash | 139/139 |
| node size `n` | 139/139 |
| `mu.contentHashCode` | 139/139 |
| `mu` quantised | 139/139 |
| weight bits | 51/139 |
| weights at 1e-6 | 52/139 |
| **`kappa` bits** | **1/139** |
| **`kappa` at 1e-6** | **1/139** |

`kappa` is constant on **one site in 139**, and quantising does not rescue it. The
fingerprint is now `(subtree key set, mu, n, mass quantised at 1e-3)`.

Dropping `kappa` and the weight *values* is sound rather than a tolerance fudge: `kappa` is
**fitted** from this node's population and direction, so conditioning on `(keys, mu, n)` pins
it up to fit noise, and its only consumer in the split path is a `vmfKappa < 0.5` diffuse
test against observed values of 130-200. Weights enter only through the mass/ESS feasibility
thresholds. Both are guarded rather than trusted: a site within 0.05 of the feasibility or
diffuse-mass thresholds, with `kappa < 1.0`, or at the depth limit is exempted from
memoization entirely (`boundarySkips`, observed 0).

Two further corrections that the memo's first real hits exposed immediately:

* `populationHash` was a plain sum of `hashCode`s — order-independent, which is right, but it
  collides whenever a site loses query X and gains query Y with equal hashes at unchanged
  `n`, and the failure mode is a stale memo silently recorded as `REJECTED`. Now mixed by
  `0x9E3779B97F4A7C15`. This matters more than it looks, because **`site.vmfMu` is stale
  during phase 4** — the refit runs at end-of-iteration — so `muHash` discriminates *across*
  iterations but not *within* one, leaving the population hash, `n` and quantised mass as the
  real within-iteration discriminators.
* The fingerprint **degenerated on internal nodes**. Internal nodes hold no direct queries,
  so a site-local hash collapses to `(nodeId, staleMuHash)` for every SHRINK proposal —
  precisely the proposals whose outcome depends on their children's drifting populations.
  Latent while the cache never hit; live the moment it did. The hash now walks the subtree.

`NO_PROPOSAL` outcomes are cached too, not only rejections: they were the numerous class (314
rows per run, 42 distinct, 86.6% exact repeats), each paying backup + PCA + EM + restore to
re-derive an unmoved answer.

Measured against the same commit without the fix: `phase4_split` 107,920 -> 95,835 ms,
`phase5_optimize` 22,651 -> 1,963 ms, total 133,942 -> 98,701 ms (**26%**). Excluding
`phase3_trickle`, which varies run to run (3371 / 3087 / 5415 / 903 ms) and is not
attributable to this change, the saving is 25% — the headline does not rest on it.
Verification after each step: leaf partition, all 50 accepted-split separations to 9 dp,
node/leaf counts, depth histogram, leaf size distribution and `J = 0.229418` identical to the
then-frozen artifact.

---

## 7. Shrink operators (`TaxonomyMerger`)

* **Starved-leaf three-way argmax**: leaf branch below `minClusterSize` -> evaluate
  {keep, prune-absorb into parent, fuse into nearest sibling} by measured `J`.
* **Sibling fusion**: pairwise chance-corrected separation of branch statistics below the
  bar -> union-find clusters fused, `J`-gated.
* **Redundant fusion**: non-sibling pairs with `<mu_A, mu_B>` above
  `fusionSimilarityThreshold` as a cheap pre-filter; `J` decides. Parent edges are redirected
  **type-preservingly**.
* **Upward dissolution of sole children**: a parent's only child separates nothing (score is
  identically 0 at `k = 1`); grandchildren are hoisted and queries residual-flagged upward.
  Depth <= 1 exempt (anchor invariance, C4).
* **Transitive reduction**: not reached in the canonical tree (gated on
  `!enableResidualRouting`, which `DAG_MAX` sets true) but live under `TREE_BASELINE`
  calibration configs, where it severs real edges. See `known-defects.md`.

---

## 8. Why routing is direction-only, restated as a standing rule

Three separate mechanisms in this pipeline were once density-based and all three were wrong
in the same direction:

| mechanism | density form's failure | measured |
|---|---|---|
| descent gate | parents fitted on larger `n` look sharper under Hornik-Grün | 56% of corpus mis-residualised at anchors |
| sibling competition (trickler) | concentrated sibling absorbs its neighbours | four ground-truth domains killed |
| routing-sustainability (splitter) | depresses `min(routed child)`, the gated quantity | 750 -> 42 rejections, J +20.4% (`c381211`) |

The general form and its corollaries: `router-shared-kappa-correction.md`.

---

## 9. Convergence, certification and determinism

**Fixed-point certificate.** Four terms, all against `tau = 1e-6`: `edits delta` (the
structural gate accepted no edit), `trickle delta` (re-routing reproduced the same
partition), `max 1-cos(mu)` and `max rel d kappa` (the refit moved no node's direction or
concentration). The refit terms are not decoration: held-out queries route through
`(mu, kappa)`, so a certificate over structure and objective alone would not cover the
object being frozen.

Two of the four are **bounded, not reproducible** — see `known-defects.md`. The certificate
certifies *this* artifact; it is not a claim that the loop terminates from an arbitrary
start.

**Determinism.** With a fixed seed the pipeline is reproducible on every decision-bearing
quantity. Sources fixed historically: PCA power-iteration init seeded from the problem shape
(previously `ThreadLocalRandom` — identical-code seed-42 runs produced 66-69 leaves); EM
inputs sorted by `queryId` (`ConcurrentHashMap` iteration order is
insertion-history-dependent, and float-sum order flips decisions at boundaries);
representative-query sampling seeded. Residual last-bit nondeterminism from parallel
reduction order survives and shows up only in the two drifting certificate residuals.

One recorded anomaly with no mechanism: a `@Volatile` field with no consumer changed the tree
(`b5313ed`, builds A/B/C). Recorded in `transferable-findings.md`, not explained.

---

## 10. Parameters at the frozen artifact

From `experiment_configs/freeze_mcs55.toml`. Derivations — stated in the correct direction —
are in `frozen-artifact.md`.

| Parameter | Meaning | Frozen value |
|---|---|---|
| `minClusterSize` | Birth floor on the routed partition; also the starvation floor | **55** |
| `proposalSeparationBar` | LEVEL: min chance-corrected separation of a routed partition | **0.025** |
| `marginalEps` | DIFFERENCE: increment required from `k` to `k+1`; `-1.0` = fall back to the bar | -1.0 (inert) |
| `maxK` | Max `k` offered by the fallback; a cost bound `O(maxK^2)` | 4 |
| `acceptanceZ` | Structural acceptance in units of `SE(dJ)`; 0 selects the legacy rule | **2.0** |
| `tau` | Float tolerance: acceptance floor and fixed-point tolerance (overloaded) | 1e-6 |
| `descentMargin` | delta below the Jensen-tight descent bar; **mode selector** | **0.12** |
| `routingBeamGamma` | Additive cosine beam margin below the best sibling | 0.2 |
| `membershipFloor` | Min share of a query's own membership for a leaf to count | 0.25 |
| `maxDepth` | Recursion cap (not binding; realised depth 6) | 8 |
| `maxLeafAssignments` | Arena-time judge-cost cap; never applied during construction | 5 |
| `fusionSimilarityThreshold` | `mu`-cosine pre-filter for redundant fusion | 0.90 |
| `effectiveSupportFloor` | ESS floor in the feasibility test | 2.0 |
| `defaultKappaPrior` | EB fallback when no parent anchor exists | 10.0 |
| `numIterations` | Iteration budget (converged and certified at 10) | 50 |
| `enableRefitGate` | Refit-scoped proposal evaluation | false |
| `dagMode` | Sets `enableStableQuestionIds` / `enableResidualRouting` / `enableResidualSplitGate` as a block | `DAG_MAX` |

**Removed entirely** (do not cite from older documents): `emaAlpha`, `routingSoftmaxTau`,
`tauKappaScalingFactor`, `assignmentCosineGap`, `deltaAssign`, `constructionMargin`, dynamic
temperature, kappa-adaptive margins, `separationEpsilon` as a single unified constant,
`secondaryMassFloor`, `bridgeSupportRelFraction`, `bridgeSeparationCeiling`,
`minBridgeCoverage`, `bridgeParentBudget`, `bridgeMaxArity`, `maxBridgeNodes`,
`bridgeAmbiguityFloor`, `maxParentsPerNode`.

---

## 11. What a converged run looks like

Seed 42, `freeze_mcs55.toml`: 154 nodes / 87 leaves / maxDepth 6, mass 8299.00 conserved,
`J = 0.253129`, certified at iteration 10 with iterations 8-10 identical on every column of
`iteration_metrics.csv`. 87/87 leaves labelled and rubric-bearing. Zero residuals anywhere
(a consequence of `descentMargin = 0.12`). One leaf marginally below `minClusterSize` — the
floor is a birth constraint, not an invariant (`frozen-artifact.md`).

Do **not** quote leaf counts, purity, bridge counts, ECE or residual counts from earlier
revisions of this document; see `void-results.md`.

*Note on routing ECE (2026-07-30):* the metric **is** implemented and the frozen run
exported a real value, 0.2114. Its defect is that both export sites aggregate a domain's
leaf shares with `maxOf` rather than summing them — the same mass-destruction bug class
recorded in §2 of this document, occurring a second time. See `known-defects.md`.

*Note on the certificate (2026-07-30):* §9's certificate tests **period 1** only — it asks
whether iteration `i` equals iteration `i+1`. It cannot see a limit cycle at the tolerance
scale, which is exactly what the mcs=30 build does. The convergence rule feeding it is five
consecutive unchanged iterations **or** five consecutive with the objective inside
tolerance (`TaxonomyStabilizer.kt:25,100-118`; `TaxonomyEngine.kt:608-611,655-658`).
