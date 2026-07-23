# DAG Chain-Formation Investigation — Handoff Notes

## Purpose of this document

This is a handoff for whoever picks up the "deep single-child chain" investigation next.
Six distinct fix attempts have been tried and reverted over one long session; each had a
plausible, carefully-reasoned mechanism and each still broke construction convergence.
This document exists so the next attempt starts from the accumulated evidence instead of
re-deriving it, and — more importantly — so it doesn't repeat an attempt that's already
been tried and disproven.

**Read this before touching `TaxonomyMerger.kt`, `TaxonomyFitter.kt`, or
`GraphNode.dimForDepth`.** All six attempts below modified one of those three.

## System context

TaxoArena builds a self-organizing hierarchical DAG taxonomy from MMLU-Pro query
embeddings (von Mises-Fisher clustering on the unit hypersphere), then runs a pairwise
LLM "arena" evaluation within each taxonomy leaf. This document is about the **DAG
construction** side only.

Construction is a per-iteration loop (`TaxonomyEngine.adaptTaxonomy`, iterations `i > 1`),
in this exact order:

1. **Trickle** (`TaxonomyOperations.reassignQueries` → `TaxonomyTrickler.trickle`): every
   query is cleared and re-routed top-down from root, using each level's *current* vMF
   fit. A child is a genuine destination iff its softmax posterior responsibility clears
   `membershipFloor` (a single probability threshold — this design already replaced an
   older margin/temperature-scaling scheme earlier in the same session, see git log
   around commit range mentioning `constructionMargin`/`kappaAdaptive` removal).
2. **Phase 3c — passthrough collapse** (`TaxonomyMerger.prunePassthroughNodes`, single
   pass, not fixed-point, called once here).
3. **Discover/Split** (`TaxonomySplitter.splitNodesRecursive`): every node is evaluated
   for whether to partition its current queries into k∈{2,3,4} children via vMF k-means,
   accepted iff the local Dasgupta-cost-delta proxy `N_S² − ‖sumS‖²` clears
   `separationEpsilon`, **and** every resulting cluster meets `minClusterSize` (enforced
   directly via `minClusterFrac = minClusterSize / targetQueries.size` fed into the EM's
   own viability check — split-time floor enforcement is NOT the bug, see below).
4. **Optimize, `learningPhase=true`** (`TaxonomyMerger.optimizeHierarchy`): in this
   in-loop mode it's just `pruneUnrelevantNodes → prunePassthroughNodes (again) →
   pruneUnrelevantNodes → removeStaleParentRefs`. **`mergeSimilarSiblings`, bridging,
   `mergeRedundantNodes`, and `transitiveReduction` do NOT run during the loop** — they
   only run once, at the very end, in the `learningPhase=false` finalization pass. Don't
   assume they're in play while diagnosing in-loop churn.
5. **Refit** (`TaxonomyFitter.fitNodeRecursive`): full bottom-up vMF/NiW refit using the
   *current* (post-split/prune) topology and query assignment.
6. **Convergence check** (`TaxonomyStabilizer.evaluateConvergence`): Graph Edit Distance
   (node/edge set difference) between consecutive iterations, relative to total edge
   count, must be ≤ `gedThreshold` for 5 consecutive iterations (past a
   `minIterations = 0.8 × domainCount` floor) to trigger early stop. **GED only counts
   topology (node/edge identity), not which queries are assigned where** — so minor
   per-iteration query-reassignment noise doesn't by itself block convergence; only
   actual node/edge churn does.

Key empirical-Bayes fitting detail (`TaxonomyFitter.fitSingleNode`,
`dOverNAlpha`): κ is fit as `(1-α)·κ_MLE + α·κ0Parent`, where **`κ0Parent` is the
average κ of the node's *direct* parent(s)**, and
`α = 0` for `ρ=dim/n ≤ 2`, ramps linearly to `α = 1` at `ρ = 10`. With
`fitDim=256` fixed at every depth and `minClusterSize=50`, a node right at the size
floor has `ρ=5.12 → α=0.39` — **substantial shrinkage weight right at the size floor
the system itself defines as "smallest acceptable."** This is real and quantifiable,
but attempts to exploit/fix it directly (Attempt 5, Attempt 6 below) both failed.

## The problem, concretely

Run the single-domain diagnostic (see "Reproduction setup" below) and inspect the final,
*converged* DAG (12 nodes total, converges cleanly at iteration 71 in the proven-stable
baseline). It contains this exact chain:

```
depth=1  Math          subtreeQ=943  kappa=180.14
depth=2  #135          subtreeQ=835  kappa=180.18   (1 of 3 children of Math)
depth=3  #158          subtreeQ=798  kappa=180.60   ← single child of #135
depth=4  #176          subtreeQ=798  kappa=180.60   ← single child of #158
depth=5  #201          subtreeQ=798  kappa=180.60   ← single child of #176
depth=6  #217          subtreeQ=798  kappa=180.60   ← single child of #201
depth=7  #230          subtreeQ=798  kappa=180.60   ← single child of #217
depth=8  #233 (LEAF)   directQ=798   kappa=180.60   ← single child of #230, at maxDepth
```

Five consecutive nodes (`#158` through `#230`) wrap the *exact same* 798 queries with
**identical κ to two decimal places**, differing only in reported depth. This is
cosmetically ugly and inflates `avgLeafDepth`, but critically: **mass is fully
conserved, there are no C3 invariant violations, and routing is unaffected** — every
query that reaches `#158` reaches `#233` with probability 1 at every intermediate hop
(a single-child node's softmax always gives its one child responsibility 1.0 — there's
nothing to compete against). This is a quality/interpretability issue, not a
correctness bug.

### Why it forms (confirmed by tracing the full construction log)

This is **not** simple one-time sibling death. Tracing node IDs `#158`→`#176`→`#201`→
`#217`→`#230`→`#233` through `headless_run.log` shows a real, repeated pattern: at each
level, a **genuine multi-way split succeeds** (k=2, k=4, k=3, k=4, k=4, all with solid
Dasgupta deltas ≈0.80–0.83, well above threshold), producing several children — most of
which survive as the small, distinctive leaves you can see elsewhere in the same tree
(55q, 62q, 73q). But the *bulk* of the population remains large and only weakly
separable, gets wrapped by a new single-surviving-child node, and gets tried again one
level deeper. This looks like legitimate **progressive "peeling"** of a genuinely skewed
semantic distribution (a large, only-loosely-substructured core population repeatedly
shedding smaller distinctive niches) — the chain is the visible trail of that process.
It terminates only because `maxDepth=8` cuts it off, not because splitting failed.

### Why the existing collapse mechanism doesn't clean it up

`TaxonomyMerger.prunePassthroughNodes` is meant to bypass exactly this kind of
single-child wrapper. Its (currently active, proven-stable) gate:

```kotlin
div < config.formalism.separationEpsilon && child.queries.size < config.formalism.minClusterSize
```

where `div = StatisticsUtils.vmfJsDivergence(...)`, a **κ-weighted** JS-divergence:
`div ≈ 0.5·(κ_A·A_d(κ_A) + κ_B·A_d(κ_B))·(1−cosθ)`, which for large κ (A_d(κ)→1) is
approximately `≈ κ·(1−cosθ)`. At the κ≈150–180 these deep, well-fit wrapper nodes reach,
clearing `separationEpsilon=0.01` requires `cosθ > 0.99993` — under 0.7° of angular
tolerance. This is essentially never satisfied by ordinary fitting noise between two
independently-refit nodes, **even when they describe the literally identical
population** — which is exactly what's observed above (five nodes, identical κ to 2
decimals, presumably *not* identical past that). The gate was implicitly calibrated for
*low-κ, newly-formed* nodes at split/merge time, where the same absolute-nats threshold
corresponds to a much looser angular tolerance. Reusing it for deep, high-κ wrapper
collapse makes the bar nearly unreachable — which is why the proven-stable baseline
almost never collapses anything.

## Six failed attempts (chronological within this session)

All six were validated on the 4-domain diagnostic (`experiment_configs/diag_domains.toml`,
`domains=["Computer Science","Math","History","Philosophy"]`, `numIterations=80`) unless
noted; the working baseline for comparison converges cleanly by iteration 34–43 with GED
locked at 0/0 for 5+ consecutive iterations, node count and mass flat.

### Attempt 1 — kappa-independent cosine-distance collapse gate
**Change:** In `prunePassthroughNodes`, replace the κ-weighted `vmfJsDivergence` check
with a raw `(1 − cosθ) < separationEpsilon` test (no κ term at all).
**Reasoning:** The κ-weighting was diagnosed as the reason the gate never fires; removing
it should let genuinely-similar wrappers collapse regardless of κ.
**Result:** Catastrophic non-convergence — node count and mass oscillated continuously
through all 80 iterations, never approaching GED=0.
**Diagnosed cause:** `separationEpsilon=0.01` as a *raw* cosine-distance threshold is
~8.1° of tolerance — but at the κ≈10–50 typical of *freshly split* nodes, the same
`0.01` nats value (via the original κ-weighted formula) corresponds to only ~1.3° of
tolerance in the Splitter's own sibling-uniqueness check
(`TaxonomySplitter.kt`'s `isUnique` gate, which reuses `separationEpsilon` the same way).
So the new collapse gate became ~6× looser than the standard the Splitter itself already
enforces — collapsing things the Splitter still considered meaningfully distinct, which
then got re-split next iteration. Classic split/collapse chatter.

### Attempt 2 — unconditional collapse for exactly-empty children
**Change:** Collapse any node with `treeChildren.size == 1 && depth > 1`, *unconditionally*,
when the child has zero direct hard queries **and** zero residual queries — no
divergence check, no size check.
**Reasoning:** Mathematically provable: with exactly one child, softmax responsibility is
always 1.0 (nothing to compete against), so a zero-query wrapper is a pure routing
no-op. Collapsing it cannot change any query's routing destination, so no similarity
judgment is needed at all — this isn't a heuristic, it's an exact structural
equivalence.
**Result:** Still failed to converge — comparable or worse oscillation than Attempt 1.
**Diagnosed cause:** The routing-equivalence proof is correct but incomplete: it only
covers the *instant* of collapse. Collapsing X into Y changes Y's *direct parent* from X
to X's former parent P. Since `κ0Parent` is anchored to the direct parent, Y's
empirical-Bayes shrinkage target jumps discontinuously on the very next Fit phase — not
because any query moved, but because the *statistical fitting context* changed. That
κ shift changes how Y competes in softmax scoring against its new siblings at P's level,
which can shift branch populations enough to starve a *different* sibling next
iteration — closing a feedback loop between `pruneUnrelevantNodes` (kills weak siblings)
and `prunePassthroughNodes` (collapses the resulting wrapper) that the original,
rarely-collapsing code never had.

### Attempt 3 — Attempt 2 + fit-continuity carry-over
**Change:** Same unconditional empty-child gate as Attempt 2, *plus*: at collapse time,
copy the collapsed node X's own `vmfMu`/`vmfKappa`/`vmfLogNormalizer`/NiW fields onto
the surviving child Y, instead of leaving Y's stale fit to be corrected a full iteration
later. Reasoning: X was fit on exactly Y's population (`getRegionQueryWeights` on a
childless-but-for-Y node walks the same subtree) and was *already* shrunk toward P (X's
own parent) — so X's fit already **is** "Y's distribution, pre-contextualized under P,"
making the transition atomic rather than lagged.
**Result:** Still failed to converge, though visibly less severe than Attempts 1–2.
**Diagnosed cause:** Not fully isolated before moving to Attempt 4 — the working
hypothesis is that closing this one discontinuity channel wasn't sufficient because
splitting and collapsing were still governed by two *independent* local criteria with no
shared objective (see Attempt 4's literature-grounded framing below), so some other
disagreement between them remained.

### Attempt 4 — literature-informed: unify split/collapse under global Dasgupta cost
A dedicated literature survey (control theory, Bayesian Hierarchical Clustering, DP-means,
HDBSCAN, RJMCMC — full citations available in conversation history if needed) confirmed
the failure pattern as "chattering"/"policy oscillation": two independently-thresholded
local decisions with no shared potential function, a recognized failure mode with
precedent in ISODATA and SMEM. The literature's core recommendation: gate **both**
operations on strict improvement of the *same* global, bounded-below objective, giving an
actual finite-termination proof (bounded-below + strictly-decreasing-by-≥ε ⇒ only
finitely many accepted edits are possible).

**Change actually made:** Proved, from first principles, that removing *any* single-child
node (regardless of its own query count) can never increase the tree's true Dasgupta
cost — for any query pair, its LCA either doesn't involve the collapsed node, or is
exactly that node today, in which case its post-collapse LCA sits strictly inside the
old subtree (proof by cases is in the reverted code's commit history / conversation log).
Made collapse fully unconditional for any single-child, `depth > 1` node on this basis —
no divergence check, no query-count restriction at all.
**Result:** Failed — oscillation comparable to Attempts 1–2, arguably worse (double-digit
GED deltas persisting past iteration 55).
**Diagnosed cause, important:** This attempt only implemented *half* of the literature's
recommendation. The Dasgupta-cost-safety proof is real and correct **for the collapse
side alone**, but Split's acceptance criterion (`TaxonomySplitter`'s local
`N_S² − ‖sumS‖²` proxy) was left completely untouched — it's a *local, snapshot-in-time*
recomputation with no persistent bookkeeping of a running global cost. The literature's
actual termination guarantee requires **both** decisions to reference the *same
incrementally-tracked* value that must monotonically improve — that was never built. A
genuine implementation of this fix needs real incremental global (or consistently-scoped
local) Dasgupta-cost tracking shared by both decisions, which is a substantial,
carefully-engineered undertaking (the literature review itself flagged incremental
recomputation as "an implementation detail to validate yourself, not a solved problem")
— not a small patch. **If picking this up again, this is the most promising unexplored
direction, but budget real engineering time for it, and it may still need the
fit-continuity mechanism from Attempt 3 layered on top.**

### Attempt 5 — reduce fixed embedding dimension 256 → 128
**Change:** `GraphNode.dimForDepth(depth) = 128` (was a flat `256` at every depth,
already itself a deliberate simplification from an even-older *depth-scaled*
128/256/512/1024 schedule — see commit `c66638d`, "eliminating deep-slice vMF estimator
instability"). Collapse mechanism left completely untouched (proven-stable baseline).
**Reasoning:** At `minClusterSize=50`, `fitDim=256` gives `ρ=5.12 → α=0.39` — freshly
split, minimum-sized leaves get 39% of their κ from the parent prior. Halving the
dimension would drop `ρ` to 2.56, `α` to 0.07 — much less shrinkage-driven volatility.
**Result:** Failed — never converged across a full 80-iteration budget (still churning
at iteration 80), *worse* than the 256-dim baseline's clean 34-iteration lock.
**Diagnosed cause:** The shrinkage-stability benefit was real but outweighed by lost
discriminative power: fewer dimensions make it harder for vMF-EM to tell
semantically-close-but-distinct sub-clusters apart, producing more marginal/borderline
splits that flip between "worth keeping" and "too similar, merge back" as noise
dominates in the smaller space.

### Attempt 6 — sibling-anchored κ0 prior (skip past single-child levels)
**Change:** In `TaxonomyFitter.fitSingleNode`, replace `κ0Parent = average(direct
parents' κ)` with: walk up the tree-parent chain past any single-child levels to the
*nearest ancestor with more than one child*, and average **that ancestor's other
children's** κ (`trueSiblingKappa0` helper). Falls back to `defaultKappaPrior` if no
such ancestor exists. Collapse mechanism left completely untouched.
**Reasoning:** Every node along a chain would reference the *same* real branching point,
so removing any wrapper level would change nothing about what any descendant shrinks
toward — closing the Attempt 2 discontinuity channel structurally rather than
approximately, without touching the collapse gate at all.
**Result:** Failed — broke the previously-clean single-domain baseline (12-node case)
even in complete isolation from any collapse change; never converged across 80
iterations, versus a clean 71-iteration convergence before this change.
**Diagnosed cause:** A user-flagged, correctly-anticipated precision trade-off. A direct
parent (fit on its *entire* subtree via `getRegionQueryWeights`) is a much
lower-variance reference than a node's real siblings, which — especially right after a
fresh split — are themselves still-unstable, small-sample nodes. Swapping to
sibling-anchoring made the prior itself noisier; since κ0 feeds directly into κ, which
directly drives trickle-routing scores, that noise propagated into routing volatility
and broke convergence. **This direction (sibling- or branch-point-anchored priors) is
now empirically disproven, not just untested — don't retry a variant of it without a
concrete plan for controlling the added variance.**

## What's provably NOT the problem

- **Split-time size enforcement is not naive.** `TaxonomySplitter.kt:169`,
  `minClusterFrac = minClusterSize / targetQueries.size`, is fed directly into the EM's
  own cluster-viability check (`StatisticsUtils.kt`, `minSoftCount = minClusterFrac * n`)
  — every split-created child is already required to clear the absolute floor at
  creation time.
- **~54% of freshly-split leaves eventually get pruned as starved** (measured on one
  4-domain run) — this sounds alarming but is present, at similar rates, in the
  proven-stable *working* baseline too, which still converges cleanly. It's normal
  adaptive churn (queries keep migrating as *other* parts of the tree keep re-fitting),
  not evidence of miscalibration by itself.
- **`sliceDim` is not depth-dependent** — `dimForDepth` returns a flat 256 (or whatever
  it's set to) at every depth; ruling out any theory involving cross-depth MRL-truncation
  mismatch between a chain node and its child.

## Reproduction setup

Use the **single-domain diagnostic**, not the 4-domain one, for any further
investigation — it's fast (~1 minute to converge), small enough to trace completely by
hand (12 nodes in the final stable state), and already reliably exhibits the chain.

```toml
# experiment_configs/diag_domains.toml
domains = ["Math"]
numIterations = 80
minClusterSize = 50
separationEpsilon = 0.01
membershipFloor = 0.10
enableProfiling = true   # required for the snapshot dumper below
```

```bash
rm -rf experiment_results/diag_domains
./gradlew bootRun --args="--config experiment_configs/diag_domains.toml" --rerun-tasks
```

**Important Windows/Git-Bash gotchas hit repeatedly this session:**
- `--args="--config=path"` (equals-joined) silently no-ops — the runner expects
  `--config` and the path as *separate* args:
  `--args="--config experiment_configs/diag_domains.toml"` (space-separated).
- `TaskStop`/killing the bash wrapper does **not** kill the forked JVM. Use:
  `powershell -Command "Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"`.
- A `run_in_background` Bash call whose command itself ends in `&` (manual backgrounding)
  causes the tracker to report "completed" as soon as the wrapper shell returns, while
  the actual `gradlew`/JVM process keeps running detached and untracked. Don't combine
  manual `&` with `run_in_background: true` — pass the foreground command directly.

## Tooling built this session

**`TaxonomyEngine.dumpIterationSnapshot()`** (private method, called once per iteration
right after `logNodeDiagnostics`, gated behind `config.diagnostics.enableProfiling`):
appends one JSON line per iteration to `<outputDir>/dag_snapshots.jsonl` — full node
list with id, label, depth, isLeaf, isBridge, kappa, direct/residual/subtree query
counts, and parent/child ids. Exists because the text log only prints a *full* tree dump
at iteration 1 and at the very end; every iteration in between is diff-only, making
"what did the DAG look like at iteration 40" hard to reconstruct from the log alone.

**`tools/analysis/analyze_dag_snapshots.py`**: reads that JSONL and reports, for a given
iteration (default: last): node/leaf counts, **automatic chain detection** (maximal runs
of consecutive single-tree-child, zero-query nodes, with depth range and κ range per
chain), leaf query-repartition stats (min/median/mean/max, Gini coefficient), and C3
invariant violations. Usage:
```bash
python tools/analysis/analyze_dag_snapshots.py --file experiment_results/diag_domains/seed_42/dag_snapshots.jsonl --iteration last
python tools/analysis/analyze_dag_snapshots.py --file <path> --iteration all   # every iteration
python tools/analysis/analyze_dag_snapshots.py --file <path> --list-iterations
```

## Current code state (fully reverted, proven-stable)

As of this handoff, all six attempts have been reverted. The live behavior is:
- `TaxonomyMerger.prunePassthroughNodes`: original κ-weighted `vmfJsDivergence` gate
  (`div < separationEpsilon && child.queries.size < minClusterSize`) — the one that
  rarely fires, chains persist, but convergence is clean.
- `TaxonomyMerger.pruneUnrelevantNodes`: **this one keeps a validated fix from earlier
  in the same session** (not one of the six reverted attempts) — a hard starved-leaf
  floor tied directly to `minClusterSize` (replacing an older relative
  `siblingAvg × 0.2` heuristic), plus removal of a `wouldLeaveParentSingleChild` veto
  that was causing a different deadlock. This fix is confirmed working and should stay.
- `GraphNode.dimForDepth`: flat `256` at every depth (Attempt 5 reverted).
- `TaxonomyFitter.fitSingleNode`: original parent-anchored `κ0Parent` (Attempt 6
  reverted); the only surviving change is a harmless refactor making `fitDim` call
  `dimForDepth(node.depth)` instead of a separately-hardcoded `256` literal (same value,
  single source of truth, zero behavior change).

## Standing constraints (apply to any future attempt)

These come directly from repeated, explicit direction across the session and should
govern any new attempt:

1. **No new free parameters.** Every fix attempted reused `separationEpsilon`,
   `minClusterSize`, or `defaultKappaPrior` rather than introducing a new tunable
   constant. This is a deliberate thesis-design requirement, not a soft preference.
2. **Reason from the math, verify empirically — don't copy old commit values as "the
   fix."** Several early-session bugs (before this document's scope) were traced to
   exactly that anti-pattern.
3. **Validate incrementally.** Single domain first, then 2, then 4, before trusting any
   result at scale. The single-domain case is fast and sufficient to falsify an attempt
   — every one of the six above was refuted (or at minimum strongly suggested to be
   wrong) using it.
4. **When a fix regresses, investigate with real log/trace evidence before reverting or
   guessing again** — don't just intuit a new fix. Every attempt above was diagnosed
   with actual log tracing (specific node IDs followed across iterations), not just
   aggregate GED numbers.
5. **Chains are a quality/interpretability issue, not a correctness bug.** Mass is
   conserved, C3 holds, routing is unaffected. Non-convergence, by contrast, *is* a
   correctness bug — the final DAG would just be an arbitrary iteration-N snapshot, not
   a genuine equilibrium. Never trade the latter for the former.

## Recommended next steps, in order of risk

1. **Lowest risk — display-only flattening. IMPLEMENTED AND VERIFIED (2026-07-23).**
   Leave the construction algorithm completely untouched. Collapse consecutive
   zero-query single-tree-child wrapper levels only in printing code, never in the live
   `GraphNode` tree used for routing or refitting. Cannot affect convergence because it
   never runs during construction. Addresses the *readability* complaint that motivated
   this whole investigation without touching anything that's been shown to be fragile.

   Implementation: `TaxonomyOperations.kt` — new private `isDisplayWrapper(node)`
   (single tree child, no cross-links, no direct/residual queries, `depth > 1`) and
   `collapseWrapperChain(start)` (walks forward through consecutive display-wrappers,
   returns the first real node plus hop count). Both `buildTreeStringCompact` and
   `buildTreeString` (the recursive helpers behind `printHierarchyCompact`/
   `printHierarchy`) gained a `chainSkipped: Int = 0` parameter and now call
   `collapseWrapperChain` on each non-cross-link child before recursing, printing a
   `[⋯ N wrapper level(s) collapsed]` annotation on the surviving node.

   Verified via a single-domain (Math) diagnostic run
   (`experiment_configs/diag_domains.toml`):
   - Rendering: the known chain now prints as one annotated hop instead of 4-5 nested
     identical-looking lines (e.g. `Emergent Concept #98 ... [⋯ 2 wrapper levels
     collapsed]`), final tree readable at 7 leaves under `Math`.
   - Live tree unaffected: `dag_snapshots.jsonl` (captured pre-finalization, from inside
     the loop) confirms the full wrapper chain (`#74→#98→#104→#108`) is still physically
     present with correct `parentIds`/`childIds`/κ — only the *printer* skips over it.
   - Convergence unaffected: same run converged cleanly at iteration 46 via the standard
     sustained-low-GED criterion, no oscillation.
   - Metrics unaffected: Dendrogram Purity / Weighted Leaf Purity / Edge F1 / Ancestor
     Correct all still compute as expected (the only "off" metric, `ECE=1.0`, is the
     pre-existing, separately-documented Routing ECE bug, unrelated to this change).

   This closes the *readability* complaint. It does **not** reduce actual node count in
   the persisted DAG or in metrics that operate on the raw tree — see option 2 below if
   that's later judged necessary.
2. **Higher risk, but the most theoretically sound remaining option — finish Attempt
   4 properly.** Build genuine incremental (not full O(M²) recompute) global Dasgupta
   cost tracking, and gate *both* split and collapse acceptance on strict improvement of
   that same tracked value by ≥`separationEpsilon`, not just collapse. This is real
   engineering work (incremental maintenance under arbitrary tree edits), likely still
   needs the Attempt-3 fit-continuity carry-over layered in, and should be validated on
   the single-domain case first, in complete isolation, before any 4-domain run. Not
   started as of the display-only fix landing — remains an open decision, not yet
   requested by the user.
3. **Do not retry:** any variant of sibling/branch-point-anchored κ priors (Attempt 6,
   now empirically disproven), reducing the fixed embedding dimension (Attempt 5,
   empirically disproven), or any collapse-gate change that isn't paired with a matching
   change to Split's acceptance criterion (Attempts 1–3 all failed this way).
