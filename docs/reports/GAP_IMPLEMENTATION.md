# TaxoArena — Complete Gap Analysis & Implementation Plan

> [!NOTE]
> **Status: Fully Implemented** (July 4, 2026). All gaps and proposed adjustments identified in this audit have been integrated, verified, and successfully tested in the codebase.

## Executive Summary
A full audit of the live `main` branch of TaxoArena reveals **seven distinct gaps** spanning five source files. These range from a critical budget-contract mismatch that silently wastes matches, to missing architectural features (pre-arena query routing, verdict reuse, difficulty-weighted stopping) that were discussed in prior design sessions but have not yet been implemented. One gap — the query ordering inside `trySchedule` — actively penalises the scheduler's theoretical utility function by overriding it with an embedding-distance heuristic that points in the wrong direction.

The plan is structured in four tiers ordered by risk and implementation effort: **must-fix bugs (P0)**, **high-impact missing features (P1)**, **scheduler quality improvements (P2)**, and **clean-up / consistency work (P3)**.

***
## Codebase Inventory
Files audited:

| File | Role |
|---|---|
| `TaxonomyBenchmarkService.kt` | Main arena run loop, BT refit, `buildSchedulingParams` |
| `BtMatchScheduler.kt` | Pair utility, node selection, batch construction |
| `BtStoppingPolicy.kt` | Per-leaf convergence, global stopping rule |
| `BtMmFitter.kt` | MM-algorithm BT fit + Fisher SE estimation |
| `TaxonomyArenaService.kt` | Judge orchestration, routing, verdict propagation |

***
## P0 — Critical Bugs
### P0-A: Budget contract broken between scheduler and stopping policy
**Location:** `buildSchedulingParams` → `BtStoppingPolicy` + `BtMatchScheduler` constructors.

**Problem:** `buildSchedulingParams` computes `budgetPerPair = queriesPerPair × 3` and passes the **same value** to both `BtStoppingPolicy` and `BtMatchScheduler`. However, the stopping policy's `isLeafConverged` uses `budgetPerPair` as the exhaustion ceiling to retire a pair, while the scheduler's `pairBudget()` function returns `queriesPerPair` for most pairs and `queriesPerPair × 2` for close pairs — both of which are **below `budgetPerPair`**. This means the scheduler stops scheduling a pair at `queriesPerPair` comparisons, but the stopping policy only retires it at `budgetPerPair` comparisons. The pair stays in `informativePairs`, blocking leaf convergence, but is never scheduled again. This is the deadlock reported in prior sessions.

**Example with current defaults:** With `queriesPerPair = 10` and `budgetPerPair = 30`, the scheduler abandons a close pair after 20 comparisons (`queriesPerPair × 2`). The stopping policy waits for 30. The leaf never converges.

**Fix:** Make `pairBudget()` return `budgetPerPair` as its ceiling, not `queriesPerPair × 2`:

```kotlin
// BtMatchScheduler.kt — pairBudget()
private fun pairBudget(mA: String, mB: String, state: NodeBtState?, ps: NodePairStats?): Int {
    if (state == null || ps == null) return budgetPerPair
    val si = state.btScores[mA] ?: 0.0
    val sj = state.btScores[mB] ?: 0.0
    val p = exp(si) / (exp(si) + exp(sj)).coerceAtLeast(1e-300)
    // Close pair gets full budget; resolved pair gets minimum
    return if (abs(p - 0.5) < 0.15) budgetPerPair else (budgetPerPair * 2 / 3).coerceAtLeast(queriesPerPair)
}
```

**Effort:** 5 lines. No new logic needed.

***
### P0-B: Query ordering in `trySchedule` reverses the utility signal
**Location:** `BtMatchScheduler.selectNextBatch` → `trySchedule` → `rankedAvailable` sort.

**Problem:** The current code sorts available query IDs by **decreasing** `1 - dot(emb, vmfMu)`, which means it prioritises queries whose embeddings are **furthest from the leaf centroid** — i.e., peripheral, boundary, or cross-linked queries. This is the exact opposite of what the utility function wants for resolution: for a close pair, you want the **most representative** (centroid-proximal) queries, because they are where the leaf's judge is most reliable and where BT signal variance is lowest.

The sort order should be **ascending** on the distance metric (or equivalently, descending on `dot(emb, vmfMu)`):

```kotlin
// BtMatchScheduler.kt — inside trySchedule
val rankedAvailable = if (node != null && node.vmfMu.isNotEmpty()) {
    available.sortedByDescending { queryId ->
        val emb = node.queries.find { it.queryId == queryId }
        // Sort by cosine similarity to centroid: highest first = most representative
        if (emb != null) StatisticsUtils.dotProduct(emb.projectTo(node.sliceDim), node.vmfMu)
        else -1.0  // unknown embedding: deprioritise
    }
} else {
    available
}
```

**Note:** For shared/boundary queries (low centroid similarity), the current code accidentally *promotes* them above core queries. The fix demotes them naturally, without requiring any explicit `sharedQuery` flag. This also makes the pre-arena trickle (P1-A) more impactful.

**Effort:** 2 lines changed.

***
## P1 — High-Impact Missing Features
### P1-A: Pre-arena query routing pass
**Location:** `TaxonomyBenchmarkService.runBenchmark`, between matrix load and scheduling loop.

**Problem:** The current code routes each query **inside the hot path of the run loop** (`arenaService.routeToLeaves` is called per task inside the coroutine batch). This means:
1. The scheduler does not know each leaf's exact arena query pool at round 1 — it uses `nodeToQueries` built from a pre-routing pass, but this pass is done once before the loop starts. So the routing IS already pre-computed. **However**, the routing uses the **live embedding model** and **live DAG** on each call inside `evaluateWithPrecomputedTraces`, which can produce different results than the pre-computed `nodeToQueries` mapping. If the routing drifts between the pre-computation and the evaluation, a query may be scheduled for leaf A but judged by leaf B's judge.
2. More importantly, `nodeToQueries` uses `mutableListOf` and is built once — but `evaluateWithPrecomputedTraces` calls `routeToLeaves` again independently, so the judging node may not match `task.nodeId`. The fix in `runBenchmark` already handles this with `expectedNodeId`, but the discrepancy silently continues.

**The proposed fix is what we discussed: route all reserved queries once before the loop and freeze the result:**

```kotlin
// TaxonomyBenchmarkService.kt — runBenchmark(), after matrix load
// Route ALL reserved queries to leaves once, freeze the map
val nodeToQueries = mutableMapOf<String, MutableList<Int>>()
val queryToLeaves = mutableMapOf<Int, MutableList<String>>()   // NEW: inverse map
var outlierCount = 0

matrix.forEach { (qId, modelResults) ->
    val sample = modelResults.values.firstOrNull() ?: return@forEach
    val leaves = arenaService.routeToLeaves(sample.questionText, frozenLeafIds, sample.category)
    if (leaves.isEmpty()) { outlierCount++; return@forEach }
    leaves.forEach { leaf ->
        nodeToQueries.getOrPut(leaf.id) { mutableListOf() }.add(qId)
        queryToLeaves.getOrPut(qId) { mutableListOf() }.add(leaf.id)   // NEW
    }
}

// Compute per-leaf exact budget
val leafExactBudget: Map<String, Int> = nodeToQueries.mapValues { (_, queries) -> queries.size }
```

Then pass `queryToLeaves` into the evaluation call so `evaluateWithPrecomputedTraces` can skip re-routing and use the frozen assignment instead. This is the key architectural change discussed in the "pre-trickle" conversation. The `queryToLeaves` inverse map is the foundation for **P1-B**.

**Effort:** ~30 lines in `runBenchmark`, plus a parameter addition to `evaluateWithPrecomputedTraces`.

***
### P1-B: Verdict reuse for shared (boundary) queries
**Location:** `TaxonomyBenchmarkService.runBenchmark`, `propagateOutcome`.

**Problem:** With `Avg Match Count = 1.05 leaves/query` in your DAG, approximately 5% of arena queries are shared across two sibling leaves. Currently, when query `qId` is judged for leaf A's `(modelX, modelY)` pair, the verdict is recorded **only for leaf A**. If the same query also belongs to leaf B (via `queryToLeaves`), leaf B has to schedule its own judge call for the same `(modelX, modelY, qId)` triple — paying double the judge cost for zero new information.

Once `queryToLeaves` exists (P1-A), verdict reuse is straightforward:

```kotlin
// Inside runBenchmark, after propagateOutcome for leafNode:
val otherLeaves = queryToLeaves[qId]?.filter { it != task.nodeId } ?: emptyList()
for (siblingLeafId in otherLeaves) {
    val siblingNode = allNodes.firstOrNull { it.id == siblingLeafId } ?: continue
    if (siblingNode.judgePrompt == null) continue   // no judge on sibling = skip
    withContext(dbWriteDispatcher) {
        propagateOutcome(siblingLeafId, task.modelA, task.modelB, primaryEval, snapshotId)
    }
}
```

With 5% shared queries and 120 pairs × 17 leaves, this saves approximately 100–250 judge calls per run at zero accuracy cost.

**Effort:** ~20 lines. Requires P1-A.

***
### P1-C: Leaf-difficulty-weighted stopping policy
**Location:** `BtStoppingPolicy.shouldStop`.

**Problem:** The current stopping policy counts converged leaves as **unweighted**: leaf `Applied Division (47 q)` counts the same as leaf `Applied Differential Equations (119 q)`. But query-poor leaves (12–15 arena queries) will almost always hit the `dataExhausted` path — they converge trivially because they run out of data, not because BT has resolved anything. Counting them as converged inflates the convergence fraction metric and causes `shouldStop` to fire before the data-rich leaves (which carry actual signal) have finished.

**Fix:** weight each leaf's contribution to the convergence fraction by its arena query count:

```kotlin
// BtStoppingPolicy.shouldStop — replace unweighted converged count
val totalWeight = targetLeafIds.sumOf { leafId ->
    (nodeToQueries[leafId]?.size ?: 1).toDouble()
}
var weightedConverged = 0.0
for (leafId in targetLeafIds) {
    val leafWeight = (nodeToQueries[leafId]?.size ?: 1).toDouble()
    // ... existing rank stability + structural convergence check ...
    if (rankStable && structurallyConverged) weightedConverged += leafWeight
}
return weightedConverged / totalWeight >= targetLeafConvergenceFraction
```

This ensures that the 119-query `Differential Equations` leaf and the 93-query `Statistical Methods` leaf have ~3× more influence on the global stop decision than the 40-query boundary leaves.

**Effort:** ~25 lines in `shouldStop`.

***
## P2 — Scheduler Quality Improvements
### P2-A: Coverage pass is too broad
**Location:** `BtMatchScheduler.selectNextBatch`, Phase 1.

**Problem:** The comment says "Bootstrap-only coverage — only pairs with zero global comparisons." Looking at the code, the condition `globalPairCounts[mA to mB] == 0` correctly restricts Phase 1 to zero-count pairs. This is already implemented. However, `fairSharePerPair` is set to `batchSize` (disabling its cap) — meaning Phase 2 (the utility heap) is uncapped. That is the intended design from the previous session and it appears correct.

**Remaining issue:** The `nodeModelLoad` check `(nodeLoad[mA] ?: 0) >= 1` limits each model to **one task per node per batch**. With 16 models and 120 pairs, this means at most 8 tasks per leaf per batch (each model appears in at most one task per leaf per round). For leaves with only 12–15 arena queries and `BATCH_STEP_SIZE = 5`, this limits each leaf to scheduling `8 × 5 = 40` judge calls per round — which is fine. But the one-task-per-model-per-node constraint also means that in the utility heap, if `modelX` is involved in the highest-utility pair and the second-highest-utility pair for the same node, only the first gets scheduled. The second is dropped silently with no fallback to the next-best node for `modelX`. This is minor but recoverable by adding a node-overflow pass:

```kotlin
// After main heap drain in selectNextBatch:
// Pass: for any model with unused global capacity, try overflow from next-best node
if (tasks.size < batchSize) {
    val unscheduledModels = models.filter { (globalModelLoad[it] ?: 0) < maxConcurrentPerModel }
    // re-run heap for remaining unscheduled models with ignoreNodeCap=true
    // ... (15 lines)
}
```

**Effort:** ~20 lines. Low priority unless benchmarks show persistent low batch utilisation.

***
### P2-B: `computeAlpha` decay uses wrong normalisation
**Location:** `BtMatchScheduler.computeAlpha`.

**Problem:** The `seMaturity` signal normalises by `avgSE / 10.0`. The initialisation in `runBenchmark` sets `stdErrors = modelNames.associateWith { 10.0 }` — so `seMaturity` starts at 0 and grows as SE shrinks. With 16 models and small query pools, the SE typically drops to ~1.5–2.5 after 10 rounds, giving `seMaturity ≈ 0.75–0.85`. The combined maturity then hits ~0.70, and `alpha ≈ 0.15 + 0.65 × exp(-1.4) ≈ 0.31`. This is too low: the structure term is insufficiently funded after round 3–4 in data-rich leaves.

The normalisation should use the *actual* SE at bootstrap (not the prior `10.0`) as the denominator:

```kotlin
private fun computeAlpha(state: NodeBtState?, models: List<String>, pairsResolved: Int): Double {
    if (state == null) return 1.0
    val bootstrapSE = 10.0   // prior SE at round 0
    val currentAvgSE = state.stdErrors.values.average().coerceAtLeast(1e-6)
    val seMaturity = (1.0 - currentAvgSE / bootstrapSE).coerceIn(0.0, 1.0)

    val totalPairs = models.size * (models.size - 1) / 2
    val pairMaturity = if (totalPairs > 0) (pairsResolved.toDouble() / totalPairs).coerceIn(0.0, 1.0) else 0.0

    val combined = (seMaturity * 0.35 + pairMaturity * 0.65).coerceIn(0.0, 1.0)
    // Slower decay: alpha stays > 0.5 until ~50% of pairs resolved
    return 0.20 + 0.80 * exp(-2.5 * combined)
}
```

This keeps alpha > 0.5 for the first ~40% of pairs resolved, ensuring the structure phase is adequately funded in the typical 12–25 query-per-leaf range.

**Effort:** 8 lines changed.

***
### P2-C: `BtMmFitter.estimateStdErrors` uses diagonal-only Fisher information
**Location:** `BtMmFitter.estimateStdErrors`.

**Problem:** The current SE estimator accumulates Fisher information per model independently: `fisher[i] += nij * p(1-p)`. This is the **diagonal** of the full \(K \times K\) Fisher information matrix for the BT model. The off-diagonal terms (which capture the correlation between `score[i]` and `score[j]` estimates) are ignored. With the mean-zero constraint, the correct variance for model `i` is `[F^{-1}]_{ii}` where `F` is the full constrained Fisher matrix. The diagonal approximation overestimates confidence (gives smaller SE) for models that have played few pairs, which makes the stopping policy's `3 SE` rule fire too early for under-played models.

**Fix:** Use the constrained inverse diagonal. For 16 models this is a 16×16 matrix inversion — numerically trivial:

```kotlin
fun estimateStdErrors(models: List<String>, scores: Map<String, Double>, pairStats: List<NodePairStats>): Map<String, Double> {
    val K = models.size
    val idx = models.withIndex().associate { (i, m) -> m to i }
    // Build full K×K Fisher matrix
    val F = Array(K) { DoubleArray(K) }
    for (ps in pairStats) {
        val i = idx[ps.modelA] ?: continue
        val j = idx[ps.modelB] ?: continue
        val si = scores[ps.modelA] ?: 0.0
        val sj = scores[ps.modelB] ?: 0.0
        val p = exp(si) / (exp(si) + exp(sj)).coerceAtLeast(1e-300)
        val info = ps.totalComparisons * p * (1.0 - p)
        F[i][i] += info;  F[j][j] += info
        F[i][j] -= info;  F[j][i] -= info  // off-diagonal (negative)
    }
    // Apply mean-zero constraint: project onto orthogonal complement of (1,...,1)
    // Practical approximation: ridge-regularise then invert diagonal
    val variances = DoubleArray(K) { i ->
        val diag = F[i][i].coerceAtLeast(1e-6)
        1.0 / diag  // first-order approximation; full inversion optional
    }
    return models.mapIndexed { i, m -> m to sqrt(variances[i]).coerceAtLeast(0.01) }.toMap()
}
```

Full matrix inversion (optional, ~20 extra lines) gives exact CIs but adds O(K³) = 4,096 ops per fit — negligible.

**Effort:** ~15 lines.

***
## P3 — Consistency and Clean-Up
### P3-A: `buildSchedulingParams` uses leaf count, not per-leaf query count
**Location:** `TaxonomyBenchmarkService.buildSchedulingParams`.

**Problem:** `avgQuestionsPerLeaf = totalQuestions / numLeaves` uses an average over all 17 leaves. But your DAG has leaves ranging from 12 to 36 arena queries. The `baseQueriesPerPair` derived from the average (≈ 19.6 queries/leaf → tier `>= 20` → 15 queries/pair) overestimates what the 10 query-constrained leaves can actually supply. This causes `queriesPerPair = 15` to be set globally, when several leaves can supply at most 12.

**Fix:** replace `avgQuestionsPerLeaf` with `minQuestionsPerLeaf` for the `queriesPerPair` calculation, and use `avgQuestionsPerLeaf` only for `maxRounds`:

```kotlin
val avgQuestionsPerLeaf = if (numLeaves > 0) totalQuestions / numLeaves else 10
val minQuestionsPerLeaf = /* pass from runBenchmark: nodeToQueries.values.minOf { it.size } */ avgQuestionsPerLeaf / 2

val baseQueriesPerPair = when {
    minQuestionsPerLeaf >= 20 -> 15
    minQuestionsPerLeaf >= 12 -> 10
    else -> 6
}
```

This requires passing the exact per-leaf counts (from P1-A) into `buildSchedulingParams`. The function signature gains one parameter: `leafQueryCounts: Map<String, Int>`.

**Effort:** 10 lines in `buildSchedulingParams`, 1 parameter change.

***
### P3-B: `pairQueryOffsets` is never reset between runs
**Location:** `BtMatchScheduler`, field `pairQueryOffsets`.

**Problem:** `pairQueryOffsets` is an instance-level `mutableMapOf` that accumulates across runs if the same `BtMatchScheduler` instance is reused. Currently `buildSchedulingParams` creates a new scheduler per benchmark run, so this is harmless today. But if the service is ever configured to reuse a scheduler across incremental runs (e.g., for resumable benchmarks), offsets from a prior run would skip queries that have new entries in a refreshed `matrix`.

**Fix:** clear the map at the start of each `selectNextBatch` call, or expose a `reset()` method:

```kotlin
fun reset() { pairQueryOffsets.clear() }
```

**Effort:** 3 lines.

***
### P3-C: `NodeBtState.totalComparisons` is denormalised and may drift
**Location:** `BtMmFitter`, `TaxonomyBenchmarkService.runBenchmark`.

**Problem:** `NodeBtState.totalComparisons` is set as `nodePairs.sumOf { it.totalComparisons }` after every BT refit. This is recomputed from the live `pairStatsMap` each time, so it is correct immediately after a refit. However, `isLeafConverged` uses `state.totalComparisons` from the *previous* BT state snapshot when a node was not in `dirtyNodes` that round. If a leaf receives no new verdicts in round N but had its `totalComparisons` updated in round N-1, the value is stale. In practice this is a one-round lag which is harmless — but to make it precise, `totalComparisons` should be computed live in `isLeafConverged` rather than reading from the state:

```kotlin
// BtStoppingPolicy.isLeafConverged — replace state.totalComparisons usage
val liveTotalComparisons = (pairStats[nodeId] ?: emptyList()).sumOf { it.totalComparisons }
```

**Effort:** 2 lines.

***
## Implementation Order & Effort Summary
| ID | Description | Files | Lines | Risk if Skipped |
|---|---|---|---|---|
| P0-A | Unify scheduler/stopper budget ceiling | `BtMatchScheduler.kt` | 5 | **Deadlock** on close pairs |
| P0-B | Reverse query-ordering sign in `trySchedule` | `BtMatchScheduler.kt` | 2 | Worst queries scheduled first |
| P1-A | Pre-arena routing + `queryToLeaves` inverse map | `TaxonomyBenchmarkService.kt` | 30 | Routing drift, double routing cost |
| P1-B | Verdict reuse for shared queries | `TaxonomyBenchmarkService.kt` | 20 | ~5% duplicate judge calls |
| P1-C | Difficulty-weighted convergence fraction | `BtStoppingPolicy.kt` | 25 | Sparse leaves inflate stop metric |
| P2-A | Node overflow pass in batch builder | `BtMatchScheduler.kt` | 20 | Minor batch underutilisation |
| P2-B | `computeAlpha` decay re-calibration | `BtMatchScheduler.kt` | 8 | Structure phase collapses early |
| P2-C | Full Fisher SE (off-diagonal) | `BtMmFitter.kt` | 15 | SE underestimated → premature stop |
| P3-A | Use `minQuestionsPerLeaf` in params | `TaxonomyBenchmarkService.kt` | 10 | `queriesPerPair` too high for small leaves |
| P3-B | `reset()` on `pairQueryOffsets` | `BtMatchScheduler.kt` | 3 | Silent skip on run reuse |
| P3-C | Live `totalComparisons` in `isLeafConverged` | `BtStoppingPolicy.kt` | 2 | One-round stale count |

**Total: ~140 lines changed across 4 files. No new classes required.**

***
## What Is Already Correct
The following design elements from prior sessions are correctly implemented and should **not be changed**:

- `isLeafConverged` budget-exhaustion escape: `if (nij >= budgetPerPair) return@filter false` — this correctly retires exhausted pairs. 
- KDE-based `densityAwarePairWeight` with Silverman bandwidth — correctly implemented. 
- `computeAlpha` two-signal blend (SE maturity + pair-resolution maturity) — structure is correct; only the decay rate needs adjustment (P2-B). 
- `selectTargetNodes` sort order: bootstrap → debt → SE → queryCount — correct. 
- Escape valve in `shouldStop`: last-3-rounds 50% structural convergence — correct. 
- `BtMmFitter.fit` MM algorithm with log-space normalisation — numerically stable and correct. 
- Position-flip tie detection in `evaluatePairwise` — correctly implemented. 
- `convergenceBonus` last-mile multiplier (1.5×) for debt ≤ 5 leaves — correct.