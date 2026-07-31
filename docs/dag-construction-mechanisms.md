# Construction mechanisms — design rationale and failure archaeology

Status: **current** as of 2026-07-27, branch `tree-only`. This document records *why* each
mechanism has the shape it has, and what failed before it. The mathematical specification is
`dag-logic-and-math.md`; the frozen numbers are in `frozen-artifact.md`.

Earlier revisions of this file (rev. 1-3, 2026-07-23) described a **polyhierarchy** built by
J-gated cross-linking. That design was removed. §7 reports it as a negative result rather
than deleting it, because the removal is itself a finding.

Every design decision below encodes a bug class that was actually hit. That is the point of
keeping this file: the decisions look arbitrary without the failure they answer.

---

## 1. One separation score for every structural gate

All structural accept/reject decisions use a single chance-corrected separation score
(`StatisticsUtils.chanceCorrectedSeparation`; formula in `dag-logic-and-math.md` §3). It is
1 for a perfect partition, ~0 for a random one, and **exactly 0 at k = 1**, so a wrapper
candidate can never clear a positive threshold.

It replaced two broken gates:

* the old "Dasgupta delta" `1 - sum(n - n_c) W_c / (n W)`, which measured the *remaining*
  cost fraction — about 0.82 for every real split, leaving any epsilon below that inert;
* the kappa-scaled vMF divergence surrogate
  `0.5 (kappa_A A_d(kappa_A) + kappa_B A_d(kappa_B))(1 - cos theta)`, which **grows with
  kappa** and so became unsatisfiable exactly where merge and collapse mattered — 11
  collapses and 0 merges per 35-iteration run.

The second failure is the first instance of the **threshold-reuse defect class**
(`transferable-findings.md` §3): the same absolute-nats constant meant ~8.1 degrees of
angular tolerance at the `kappa ~ 10-50` of freshly split nodes and under **0.7 degrees** at
the `kappa ~ 150-180` of deep wrapper nodes.

**Caveat that must survive into the thesis:** this score is an ARI-style
adjustment-for-chance. It is *not* Dasgupta's (2016) LCA cost and must not be cited as such,
notwithstanding the persisted field name `dasguptaDeltaNorm`.

**A second caveat, on what the score cannot see.** `J` is a scatter-reduction criterion with
a random-partition correction, so cutting an **elongated unimodal** cloud along its principal
axis scores well above an isotropic null without any discrete structure being present. That
is why `proposalSeparationBar` sits between two nulls rather than at the isotropic floor, and
why the within-node null is the honest second test. See `separation_null_by_size.md`.

---

## 2. Routing: three jobs that were once one parameter

The original design overloaded a single absolute `membershipFloor` with three jobs. The flat
product-vs-floor test mathematically **forbade balanced structure below depth 2** — a
balanced 4-way split gives ~0.25 per level, and 0.25 x 0.3 < 0.10 — which *forced* chains of
~1.0-responsibility dominant children. The swallow/wrapper churn was a consequence of the
gate's arithmetic, not of the data.

The three jobs are now separated into the descent gate (parameter-free at delta = 0), the
sibling beam (`routingBeamGamma`), and the final membership share (`membershipFloor`,
self-normalised). Specification in `dag-logic-and-math.md` §4.

**The direction-only rule is the most important thing in this document.** Densities were
tried at all three sites and failed at all three, in the same direction, for the same reason:

| site | density form's failure | measured |
|---|---|---|
| descent gate | Hornik-Grün shrinkage scales with `n`, so parents look sharper | 56% of corpus mis-residualised at anchors; the un-tightened direction form still over-rejected ~40% |
| sibling competition | concentrated siblings absorb their neighbours | four ground-truth domains killed |
| split routing-sustainability | biases `min(routed child)`, the gated quantity | 750 -> 42 rejections, J +20.4% (`c381211`) |

The third of these survived the redesign that fixed the second, in a function whose comment
claimed it used "the same posterior the trickler uses". See
`router-shared-kappa-correction.md` for the general form.

Cumulative path pruning (below 1e-4 absolute posterior) is a **purely numerical** guard with
no membership semantics — a distinction that matters because it was once read as one.
`maxLeafAssignments` is enforced only at arena time: applying the cap during construction
ranked leaves by joint path probability, which mechanically penalises depth and starved every
newborn's children out of the global top-k.

---

## 3. Residual queries are retained, never dropped

A query that reaches no leaf is attributed to the node the walk converged to with **full
weight + its embedding + a residual flag**. The previous implementation recorded only a naked
id: the weight vanished (130-330 mass leaked per iteration) and the residual-split mechanism
could never recover the queries, because `getAllQueriesInRegion` could not see an embedding.

In the frozen artifact this mechanism is **dormant** — at `descentMargin = 0.12` every node
carries zero residuals. It is not vestigial: it is the machinery the incremental mode runs
on, and it is live at `delta ~ 0` (756 residuals, 9.1% of the corpus). See
`incremental-taxonomy.md`.

Two consequences of the dormancy that must be stated wherever residual-dependent behaviour is
described: the diffuse-residual split branch is unreachable, and with it the doubled
small-node separation bar (`bar=0.0500` appears 0 times in the logs against 5628 of
`bar=0.0250`). See `known-defects.md`.

---

## 4. Split proposal vs. split acceptance

**Proposal is clustering; acceptance is routing geometry.** EM in a PCA subspace only
*proposes* children. Acceptance and population are decided by re-assigning every target query
through the level-local posterior the trickler uses, and rejecting unless every child holds
`minClusterSize` under that routed assignment.

Without this, children were born with the clustering's population and starved under routing
within 1-2 iterations: 63% of pruned nodes died within 2 iterations of birth, with roughly 60
spawned and 40 pruned per iteration, permanently. The in-pass "macro-concept decomposition"
recursion was removed for the same reason — oversized children are re-evaluated next
iteration under full trickle/collapse/refit feedback, rather than being peeled inside a
single pass with no feedback. That recursion was the confirmed chain factory (see §8).

**Two refinements were added in 2026-07 and both are mechanisms, not patches:**

*Coarsening instead of veto.* An all-or-nothing floor check vetoed entire splits forever on
partitions like History `[147, 164, 1, 28]`. Under-floor fragments now have their components
**dropped** and the queries re-routed among survivors — the same winner-take-all posterior, so
nothing is force-assigned, and the coarser partition must still clear the same bar. An
incoherent merge fails separation and dies exactly as before.

*k-fallback.* Every `k` in `2..maxK` is offered in ascending order; first acceptance wins.
The mechanism finding underneath it: **EM at higher `k` followed by coarsening is a better
two-way splitter than EM at `k = 2` directly** — `k = 2` may route `[95, 5]` and fail the
floor while `k = 3` routes `[40, 35, 25]` and coarsens to `[65, 35]`. Priced at ~10 leaves and
`dJ ~ 0.011`. Selection is lowest-k-first rather than `argmax dJ`, for the optimisation-bias
reason in `dag-logic-and-math.md` §5.

Consequence to state rather than hide: `k = 2` rose from 58% to 80% of splits and trees became
deeper — a binary cascade. Each extra level passed the gate on its own evidence.

---

## 5. Global-J proposal gating

Structural refinement never applies edits by local rules alone. Every candidate edit is a
**proposal**: snapshot, apply tentatively, re-route the whole corpus, measure `J`, restore,
and commit only if the measured improvement survives the acceptance rule.

The acceptance rule itself changed twice, and both changes matter:

**From `epsilon * pi_S` to `(J, -|V|)`.** The earlier design scaled the threshold by
`pi_S = n_S(n_S - 1) / sum_cells n_c(n_c - 1)`, the site's share of within-cell pairs, on the
reasoning that a global constant is unreachable for small sites and trivial for large ones.
For *splits* the toll was removed entirely: quality is already gated locally, and a positive
toll double-charges through a diluted lens. Global `J` measures cells against the whole-corpus
expectation, so refining an already-tight region gains about an order of magnitude less
globally than its local separation indicates. Measured: Business, 620 queries, local
separation 0.058 = 5.8x epsilon, `dJ` +0.00148, rejected every iteration at a bar of 0.00208 —
domains stayed childless and depth stalled at 3.

**From `(J, -|V|)` to the z-gate.** A float tolerance cannot answer "is this `dJ`
distinguishable from zero", and on this corpus `SE(dJ)` spans 13.1x p10-p90. See
`transferable-findings.md` §2 for the calibration argument and for the two refuted
corroborations. The `(J, -|V|)` arm is retained at `acceptanceZ = 0` so the change is
attributable.

**Termination survives both changes**: `J` is bounded above, and every accepted edit either
strictly increases `J` beyond `tau` or strictly decreases `|V|` at unchanged `J`.

---

## 6. Memoization, and why a cache that never fires is worse than none

The proposal memo existed for a long time and **had never once fired**. Its fingerprint keyed
on raw `Double` bits of membership weights and on `kappa`, neither of which reaches
bit-identity between iterations — `kappa` is constant on 1 site in 139 and drifts at ~1e-13
forever.

Two things are worth carrying into the thesis from this:

1. **Instrument stability before designing a key.** The fix came from measuring which
   components are constant across iterations 5-10 (table in `dag-logic-and-math.md` §6), not
   from reasoning about which ought to be.
2. **A latent bug in a cold cache goes live the moment the cache warms.** The fingerprint
   degenerated to `(nodeId, staleMuHash)` on internal nodes — precisely the nodes whose
   proposals depend on their children's drifting populations. It was invisible while the memo
   never hit and appeared in the *first* batch of `MEMOIZED` rows once it did. The
   `decision=MEMOIZED` audit rows are what made it visible; the earlier version incremented a
   counter and emitted nothing.

---

## 7. Polyhierarchy — reported as a negative result

Cross-linking was the intended polyhierarchy operator: a node `N` gains a **second parent**
`P` because `P`'s residual queries demonstrably fit `N`. A biostatistics question sits between
Math and Biology; under a strict tree it can only pick one branch, fail to specialise there,
and residualise at the domain anchor.

It worked, in the sense that it ran and produced bridges. Rev. 3 converged at iteration 15
with 9 bridge nodes, residuals 439 -> 285 (Psychology 240 -> 16), 56 leaves, acyclic, zero
orphans, purity statistically unchanged (0.710 against a 0.720 tree baseline), and a selective
gate: 4 of 48 generated cross-links accepted. Generation used the trickler's own descent
formula, so "captured" meant "will actually descend here once the edge exists" rather than a
proxy similarity, and three guards (acyclicity, no grandparent/redundant edges, cross-domain
requirement) each corresponded to a bug class already hit.

**It was removed at `334b95d`, and the removal was verified behaviour-neutral**: seed 42
reproduced the canonical build exactly — J = 0.26697, 177 nodes (112 leaves / 65 internal),
mass 8353.00, multi-leaf rate 0.1518, held-out Top-1 73.72% [72.25, 75.13], Top-10 95.37%.
Every figure matched the pre-removal run. That is the negative result: **with a converged
tree, the polyhierarchy operator changed nothing measurable.**

The substantive reason for removal was the acceptance rule. Cross-linking required a
per-type exemption:

```
proposalType == BRIDGE  -> deltaJ >= -tau
deltaJ > tau            -> true
abs(deltaJ) <= tau      -> if (deltaB > 0) true else if (deltaB == 0 && deltaV < 0) ...
```

Three objectives, an exemption, and a tie-breaker that **manufactured cross-links whenever J
was indifferent**. Removing it restores two objectives with no exemptions and the
one-paragraph termination proof (§5), against a non-monotone bridge count that needed a
bounded-phase argument instead.

**What remains.** `GraphNode.crossLinkChildren` and its consumers (persistence,
`GraphStateBackup`, GED, metrics, arena and judge services, two TUI panels) were kept. With no
generator the collection is permanently empty, so `children + crossLinkChildren` is exactly
`children` — dead weight, not incorrect. Deleting the field changes the on-disk snapshot format
and breaks round-tripping of existing snapshots, so it wants its own change with a deliberate
migration. The full implementation is preserved on branch
`dag/bridge-selection-and-topo-router`. 19 cross-linking test suites were removed with it.

**Two claims that must stay distinct in the thesis.** Query-level soft multi-membership — a
query reaching more than one leaf via the beam — is a live mechanism of the current tree.
(The measured rate of 0.1518 comes from the `334b95d` verification run and predates
`c381211`; re-measure it on the frozen artifact before quoting a number.) Concept-level
polyhierarchy — a node with parents in two domains — is **not** a property of the current
system: it was built, demonstrated, measured as behaviour-neutral, and removed. Conflating
them would claim the second on the first's evidence.

---

## 8. Single-child chains — resolved by removing the cause

The "deep single-child chain" investigation (`dag-chain-formation-handoff.md`) documented six
failed fix attempts. The chains are gone from the current pipeline, and not by any of them.

Two causes were removed structurally:

* the **in-pass macro-decomposition recursion** in `splitSingleNode`, which re-split any
  oversized child immediately, before any trickle, collapse or refit could intervene — a
  direct peeling loop terminated only by `maxDepth`;
* the **kappa-weighted collapse gate**, whose angular tolerance shrank to under 0.7 degrees at
  the kappa these wrappers reach, so it essentially never fired.

Upward dissolution of sole children is now a `J`-gated shrink proposal like any other, and the
`SE(dJ) = 0` clause in the acceptance rule exists specifically so that a wrapper dissolution —
which moves no query and therefore has `dJ` exactly 0 — can commit at all.

The handoff document is retained as archaeology. Its six disproven directions are still
disproven; its numbers, config values and code descriptions are all stale.

---

## 9. Supporting design decisions, with the failure each answers

* **Iteration 1 preserves the bootstrap.** Trickle reassignment is skipped at `i = 1`, so the
  ground-truth anchor assignment survives the first split/optimise/refit pass. Geometric
  reassignment starts at iteration 2. `enableGtWarmStart` stays off — no bias patch needed.
  (Note for the thesis: any description of "migration" as applying in the first construction
  iteration contradicts this skip.)
* **EMA centroid blending removed** — matched A/B runs showed it amplifies oscillation.
* **`dimForDepth` is flat 256** with a deliberately unused depth argument. It was once a
  per-depth MRL ladder (128/256/512/1024); flattening removed deep-slice vMF estimator
  instability. The argument is kept because the function is the single source of truth across
  11 call sites and inlining the literal would make a width change an 11-place edit.
* **pi-denominator deduplication**: the pairwise denominator walk deduplicates multi-parent
  nodes (a fused node under two parents was previously double-counted). Inert on a tree,
  retained because fusion can still produce them.
* **Mass conservation is asserted on every proposal**, on both the base and the post-edit
  side. Restricting it to iteration 1 would blind exactly the window where structural edits go
  wrong.

---

## 10. Open items

* **Re-derive the void quantities** on the frozen mcs=55 artifact: the within-node nulls, the
  lambda1/lambda-bar proxy, matched-k ARI, core/fringe, the maxK plateau. Methods survive,
  values do not (`void-results.md`).
* **A period-detecting certificate.** The current certificate tests period 1 and cannot
  distinguish "still moving" from "settled into a 2-cycle at the tolerance scale" — which is
  exactly what the mcs=30 observation does (`known-defects.md`).
* **One EM call returning all candidates.** The k-fallback currently pays `O(maxK^2)` because
  `performVmfKMeans` fans out internally and is called once per `k`.
* ~~**The null arm for the rubric-specificity measurement.**~~ **CLOSED 2026-07-28.** The
  within-arm null ran and link 2 has its control: Mann-Whitney one-sided
  **p = 1.21e-6**, 87 leaf rubrics against 13 size-matched random cells, median specificity
  **0.138 vs 0.012**, and terms appearing in >= 90% of rubrics **0 vs 6**. All four
  directional predictions fired in the registered direction
  (`prereg_rubric_specificity.md`, addendum 2026-07-28). The artifacts in `build/rubric_null/`
  are untracked, which is the one remaining reproducibility gap.
* **The hold-out-a-domain experiment**, at `descentMargin ~ 0` (`incremental-taxonomy.md`).
* Proposal evaluation is a full re-route per candidate edit. Fine at 8k queries; batch or
  cache if the corpus grows.
