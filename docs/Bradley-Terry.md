# TaxoArena — Bradley-Terry Matchmaking & Ranking: Implementation Blueprint

## Executive Summary

This document is a complete, code-oriented implementation blueprint for integrating Bradley-Terry (BT) ranking and active matchmaking into TaxoArena's arena benchmark pipeline. It maps every new component to the existing framework — `TaxonomyRankingService`, `ArenaBenchmarkService`, `GraphNode`, `DomainEvaluation`, and the TUI — and specifies the exact data model, algorithm, parallelism contract, and stopping rules needed for a working implementation.

The core architectural decision is that BT ranking is maintained **per DAG node**, not as a single global leaderboard. Each node accumulates pairwise evidence only from queries that were trickled into its subtree. A single reserved MMLU-Pro query contributes its pairwise outcome to the destination leaf and to every ancestor up to the root. The matchmaking scheduler targets nodes and model pairs with the highest uncertainty, avoiding wasteful exhaustive round-robin comparisons.[^1][^2]

***

## 1. How It Fits Into the Existing Framework

### 1.1 Current Pipeline

The existing pipeline runs as follows:

1. Reserved MMLU-Pro queries are loaded from the dataset cache.
2. Each query is trickled through the DAG to a destination leaf node.
3. All model pairs are evaluated pairwise at that leaf using the leaf's induced judge (`evaluatePairwise`).
4. `DomainEvaluation` objects are collected per pair per query.
5. `TaxonomyRankingService` currently aggregates raw wins/losses/ties.

The main gap is that **all pairs are evaluated for every query** (round-robin), there is **no per-node BT model**, and the scheduler has no concept of "which comparisons are still informative."[^3][^1]

### 1.2 New Components

The new system adds four components that slot into the existing pipeline without replacing it:

| New Component | Role | Fits Into |
|---|---|---|
| `NodePairStats` | Accumulated win/loss/tie counts per (node, modelA, modelB) | `GraphNode` data model |
| `NodeBtRanker` | Fits BT scores + uncertainty per node from `NodePairStats` | `TaxonomyRankingService` |
| `BtMatchScheduler` | Selects next informative (node, pair) batch | `ArenaBenchmarkService` |
| `BtLeaderboard` | Per-node ranked model list with confidence intervals | TUI analysis panel |

### 1.3 Data Flow

```
Reserved Query
    │
    ▼
TaxonomyTrickler ──► leaf node id + path to root
    │
    ▼
evaluatePairwise (only scheduled pairs) ──► DomainEvaluation (winner / TIE, confidence)
    │
    ▼
NodePairStatsStore.accumulate(leafId, modelA, modelB, outcome)
    │
    ▼ (propagate to every ancestor)
NodePairStatsStore.propagate(pathToRoot, modelA, modelB, outcome)
    │
    ▼
NodeBtRanker.refit(dirtyNodes) ──► btScore, stdErr per (nodeId, modelId)
    │
    ▼
BtMatchScheduler.selectNextBatch() ──► next (node, pair) list
    │
    ▼
BtLeaderboard ──► TUI per-node ranking
```

***

## 2. Data Model

### 2.1 NodePairStats

```kotlin
data class NodePairStats(
    val nodeId: String,
    val modelA: String,
    val modelB: String,
    var winsA: Double = 0.0,      // Double to support 0.5 for BT ties
    var winsB: Double = 0.0,
    var ties: Int = 0,             // raw tie count (position flips)
    var totalComparisons: Int = 0,
    var positionFlips: Int = 0,
    var lastUpdated: Long = 0L,
)
```

Ties from `DomainEvaluation.winner == "TIE"` (position flips) contribute `winsA += 0.5`, `winsB += 0.5` for BT purposes — the half-win encoding is the standard approach for handling ties in Bradley-Terry.[^4][^1]

### 2.2 NodeBtState

```kotlin
data class NodeBtState(
    val nodeId: String,
    val btScores: Map<String, Double>,        // modelId → log-strength
    val stdErrors: Map<String, Double>,       // modelId → std error
    val fitVersion: Int,
    val totalComparisons: Int,
    val lastFitAt: Long,
)
```

### 2.3 BtMatchTask

```kotlin
data class BtMatchTask(
    val nodeId: String,
    val modelA: String,
    val modelB: String,
    val queryIds: List<String>,               // reserved queries routed to this node
    val priority: Double,                     // computed utility score
    val batchId: String,
)
```

### 2.4 DomainEvaluation (updated)

Add two fields to the existing class:

```kotlin
data class DomainEvaluation(
    val domain: String,
    val winner: String,           // "Model A", "Model B", or "TIE"
    val rationale: String,
    val confidence: Double,
    val positionFlip: Boolean = false,   // NEW: position bias detected
    val nodeId: String? = null,          // NEW: leaf node id for DAG propagation
)
```

***

## 3. Bradley-Terry Fitting Algorithm

### 3.1 Model

For a set of models \(\{1, \ldots, K\}\), each model \(i\) has a latent strength \(s_i \in \mathbb{R}\). The probability that model \(i\) beats model \(j\) is:[^3][^1]

\[ P(i \succ j) = \frac{e^{s_i}}{e^{s_i} + e^{s_j}} \]

Ties are handled via half-win encoding: a tie contributes 0.5 to `winsA` and 0.5 to `winsB` before fitting. This is the simplest correct approach and avoids introducing a separate Davidson tie parameter in the first implementation.[^1][^4]

### 3.2 Maximum Likelihood via Iterative Scaling (MM Algorithm)

The MM (Minorization-Maximization) update for BT is closed-form and guaranteed to converge:[^5][^1]

\[ s_i^{(t+1)} = \log \left( \frac{W_i}{\sum_{j \neq i} \frac{n_{ij}}{e^{s_i^{(t)}} + e^{s_j^{(t)}}}} \right) \]

where \(W_i = \sum_j w_{ij}\) is the total weighted wins for model \(i\), and \(n_{ij} = w_{ij} + w_{ji}\) is the total comparisons between \(i\) and \(j\).

After convergence, normalize so \(\sum_i s_i = 0\).

```kotlin
object BtMmFitter {

    fun fit(
        models: List<String>,
        pairStats: List<NodePairStats>,
        maxIter: Int = 200,
        tol: Double = 1e-6,
    ): Map<String, Double> {
        if (models.size < 2) return models.associateWith { 0.0 }

        val idx = models.withIndex().associate { (i, m) -> m to i }
        val K = models.size
        val w = Array(K) { DoubleArray(K) }   // w[i][j] = winsA when i=modelA, j=modelB

        for (ps in pairStats) {
            val i = idx[ps.modelA] ?: continue
            val j = idx[ps.modelB] ?: continue
            w[i][j] += ps.winsA
            w[j][i] += ps.winsB
        }

        var s = DoubleArray(K) { 0.0 }

        repeat(maxIter) {
            val sNew = DoubleArray(K)
            for (i in 0 until K) {
                val Wi = (0 until K).sumOf { j -> w[i][j] }
                if (Wi == 0.0) { sNew[i] = s[i]; return@repeat }
                val denom = (0 until K).filter { j -> j != i }
                    .sumOf { j ->
                        val nij = w[i][j] + w[j][i]
                        if (nij == 0.0) 0.0
                        else nij / (Math.exp(s[i]) + Math.exp(s[j]))
                    }
                sNew[i] = if (denom == 0.0) s[i] else Math.log(Wi / denom)
            }
            // normalize
            val mean = sNew.average()
            for (i in 0 until K) sNew[i] -= mean

            val delta = sNew.zip(s.toList()).maxOf { (a, b) -> Math.abs(a - b) }
            s = sNew
            if (delta < tol) return@repeat
        }

        return models.zip(s.toList()).toMap()
    }
}
```

### 3.3 Uncertainty Estimation

Standard errors come from the diagonal of the inverse Fisher information matrix (Hessian of the log-likelihood). For a practical approximation sufficient for matchmaking:[^2][^4]

\[ \text{SE}(s_i) \approx \left( \sum_{j \neq i} \frac{n_{ij} \cdot P_{ij}(1 - P_{ij})}{1} \right)^{-1/2} \]

where \(P_{ij} = e^{s_i} / (e^{s_i} + e^{s_j})\).

```kotlin
fun estimateStdErrors(
    models: List<String>,
    scores: Map<String, Double>,
    pairStats: List<NodePairStats>,
): Map<String, Double> {
    val idx = models.withIndex().associate { (i, m) -> m to i }
    val K = models.size
    val fisher = DoubleArray(K)

    for (ps in pairStats) {
        val i = idx[ps.modelA] ?: continue
        val j = idx[ps.modelB] ?: continue
        val si = scores[ps.modelA] ?: 0.0
        val sj = scores[ps.modelB] ?: 0.0
        val pij = Math.exp(si) / (Math.exp(si) + Math.exp(sj))
        val nij = ps.winsA + ps.winsB
        val info = nij * pij * (1.0 - pij)
        fisher[i] += info
        fisher[j] += info
    }

    return models.mapIndexed { i, m ->
        m to if (fisher[i] > 0.0) 1.0 / Math.sqrt(fisher[i]) else Double.MAX_VALUE
    }.toMap()
}
```

***

## 4. Matchmaking Scheduler

### 4.1 Pair Utility Function

For each candidate pair \((i, j)\) at node \(n\), compute:[^6][^2]

\[ U(n, i, j) = \alpha \cdot \text{closeness}(n, i, j) + \beta \cdot \text{uncertainty}(n, i, j) - \gamma \cdot \text{repeatPenalty}(n, i, j) \]

where:

- **Closeness**: \(\text{closeness} = 1 - |P_{ij} - 0.5| \cdot 2\) — highest when \(P_{ij} \approx 0.5\)[^6][^2]
- **Uncertainty**: \(\text{uncertainty} = \text{SE}(s_i) + \text{SE}(s_j)\) — high when either model's score is poorly estimated[^7][^4]
- **RepeatPenalty**: \(\text{repeatPenalty} = n_{ij} / \text{budgetPerPair}\) — penalizes over-sampling the same pair

Recommended defaults: `α = 0.5`, `β = 0.4`, `γ = 0.1`. These can be exposed as config parameters.

### 4.2 Node Selection

Before selecting pairs, select the most informative nodes:

```kotlin
fun selectTargetNodes(
    allNodes: List<GraphNode>,
    btStates: Map<String, NodeBtState>,
    maxNodes: Int = 5,
): List<GraphNode> {
    return allNodes
        .filter { it.isLeaf && it.queries.size >= minQueriesForBenchmark }
        .sortedByDescending { node ->
            val state = btStates[node.id] ?: return@sortedByDescending Double.MAX_VALUE
            // Nodes where ranking is most uncertain = highest avg stdErr
            state.stdErrors.values.average()
        }
        .take(maxNodes)
}
```

### 4.3 Batch Selection

```kotlin
fun selectNextBatch(
    targetNodes: List<GraphNode>,
    btStates: Map<String, NodeBtState>,
    pairStats: Map<String, List<NodePairStats>>,   // nodeId → pairs
    models: List<String>,
    batchSize: Int,
    maxConcurrentPerModel: Int = 2,
): List<BtMatchTask> {

    val tasks = mutableListOf<BtMatchTask>()
    val modelLoad = mutableMapOf<String, Int>()   // how many active tasks per model

    for (node in targetNodes) {
        if (tasks.size >= batchSize) break
        val state = btStates[node.id]
        val nodePairs = pairStats[node.id] ?: emptyList()
        val availableQueries = node.getReservedQueriesForBenchmark()
        if (availableQueries.isEmpty()) continue

        // Generate all candidate pairs
        val candidates = models.flatMapIndexed { i, mA ->
            models.drop(i + 1).map { mB -> mA to mB }
        }

        candidates
            .sortedByDescending { (mA, mB) -> computeUtility(node, mA, mB, state, nodePairs) }
            .forEach { (mA, mB) ->
                if (tasks.size >= batchSize) return@forEach
                // Per-model concurrency cap
                if ((modelLoad[mA] ?: 0) >= maxConcurrentPerModel) return@forEach
                if ((modelLoad[mB] ?: 0) >= maxConcurrentPerModel) return@forEach

                val querySlice = availableQueries.take(queriesPerPair)
                tasks += BtMatchTask(
                    nodeId   = node.id,
                    modelA   = mA,
                    modelB   = mB,
                    queryIds = querySlice.map { it.id },
                    priority = computeUtility(node, mA, mB, state, nodePairs),
                    batchId  = UUID.randomUUID().toString(),
                )
                modelLoad[mA] = (modelLoad[mA] ?: 0) + 1
                modelLoad[mB] = (modelLoad[mB] ?: 0) + 1
            }
    }

    return tasks
}
```

### 4.4 Adaptive Question Budget per Pair

Do not allocate the full query pool to every pair upfront. Use a small block first, then extend only uncertain pairs:[^8][^9]

```kotlin
const val INITIAL_QUESTIONS_PER_PAIR = 20
const val EXTENSION_QUESTIONS = 20
const val MAX_QUESTIONS_PER_PAIR = 100

fun shouldExtendPair(ps: NodePairStats, scores: Map<String, Double>): Boolean {
    val si = scores[ps.modelA] ?: return false
    val sj = scores[ps.modelB] ?: return false
    val pij = Math.exp(si) / (Math.exp(si) + Math.exp(sj))
    // Only extend if still close to 50/50 and under budget
    return Math.abs(pij - 0.5) < 0.15
        && ps.totalComparisons < MAX_QUESTIONS_PER_PAIR
}
```

***

## 5. Propagation: Leaf → Root

### 5.1 Why Propagation Matters

A single trickled query produces evidence at the destination leaf but also implicitly provides evidence at every ancestor domain node. A model's score in "Mathematics" should reflect all queries routed to any leaf under "Mathematics."[^3][^1]

### 5.2 Propagation Algorithm

```kotlin
fun propagateOutcome(
    leafId: String,
    pathToRoot: List<String>,   // [leafId, parentId, grandparentId, ..., rootId]
    modelA: String,
    modelB: String,
    outcome: DomainEvaluation,
    store: NodePairStatsStore,
) {
    val (wA, wB) = when (outcome.winner) {
        "Model A" -> 1.0 to 0.0
        "Model B" -> 0.0 to 1.0
        "TIE"     -> 0.5 to 0.5
        else      -> return
    }

    for (nodeId in pathToRoot) {
        store.accumulate(
            nodeId    = nodeId,
            modelA    = modelA,
            modelB    = modelB,
            winsA     = wA,
            winsB     = wB,
            isTie     = outcome.winner == "TIE",
            isFlip    = outcome.positionFlip,
        )
    }
}
```

The root node leaderboard is thus naturally the global ranking across all domains. Intermediate nodes give per-domain rankings. Leaf nodes give the finest-grained evidence.[^1]

### 5.3 Getting Path to Root

Add a helper to `GraphNode`:

```kotlin
fun GraphNode.pathToRoot(): List<String> {
    val path = mutableListOf(this.id)
    var current: GraphNode? = this.parents.firstOrNull()
    while (current != null) {
        path += current.id
        current = current.parents.firstOrNull()
    }
    return path
}
```

For DAG nodes with multiple parents, propagate to all parent chains to ensure all ancestor subtree statistics are updated. Deduplication is handled by `NodePairStatsStore` using `(nodeId, modelA, modelB)` as the composite key.

***

## 6. Parallelism Contract

### 6.1 Batch Execution Loop

The main execution loop runs short rounds of parallel judging followed by BT refit:[^10][^2]

```kotlin
suspend fun runBtBenchmark(
    models: List<String>,
    reservedQueries: List<MmluQuery>,
    allNodes: List<GraphNode>,
    maxRounds: Int = 20,
) = coroutineScope {

    while (round < maxRounds && !stoppingPolicy.shouldStop(btStates)) {

        // 1. Select target nodes and pairs
        val targetNodes = scheduler.selectTargetNodes(allNodes, btStates)
        val batch = scheduler.selectNextBatch(targetNodes, btStates, pairStats, models, batchSize)

        // 2. Execute all tasks in the batch concurrently
        val results = batch.map { task ->
            async {
                val leafNode = graphNodeStore.get(task.nodeId)!!
                task.queryIds.map { queryId ->
                    val query = reservedQueries.first { it.id == queryId }
                    val traceA = modelRunner.run(task.modelA, query)
                    val traceB = modelRunner.run(task.modelB, query)
                    evaluatePairwise(leafNode, query.question, task.modelA, task.modelB, traceA, traceB)
                }
            }
        }.awaitAll().flatten()

        // 3. Propagate outcomes to leaf + ancestors
        for (eval in results) {
            val leaf = graphNodeStore.get(eval.nodeId!!) ?: continue
            propagateOutcome(leaf.id, leaf.pathToRoot(), eval.modelA, eval.modelB, eval, pairStatsStore)
        }

        // 4. Refit BT only for dirty nodes
        val dirtyNodes = results.flatMap { graphNodeStore.get(it.nodeId!!)?.pathToRoot() ?: emptyList() }.toSet()
        for (nodeId in dirtyNodes) {
            val nodePairs = pairStatsStore.getForNode(nodeId)
            val scores = BtMmFitter.fit(models, nodePairs)
            val stdErrors = estimateStdErrors(models, scores, nodePairs)
            btStates[nodeId] = NodeBtState(nodeId, scores, stdErrors, fitVersion++, nodePairs.sumOf { it.totalComparisons }, System.currentTimeMillis())
        }

        round++
    }
}
```

### 6.2 Concurrency Rules

| Rule | Value | Rationale |
|---|---|---|
| Max concurrent tasks per batch | `workerCount` (from config) | Matches judge slot pool |
| Max active tasks per model | 2 | Prevents one model monopolising the batch |
| Batch size | `workerCount` | Fill all slots every round |
| Refit frequency | After every batch | Cheap relative to LLM calls |
| Round size | Short (20–40 questions total) | Avoids stale scheduling from an old leaderboard snapshot[^10] |

***

## 7. Stopping Policy

Stop the benchmark when one or more of these conditions hold:[^8][^2]

```kotlin
class BtStoppingPolicy(
    val minComparisons: Int = 30,
    val stabilityRounds: Int = 3,
    val separationThreshold: Double = 2.0,    // std errors of separation
    val maxRounds: Int = 20,
) {
    private val rankHistoryByNode = mutableMapOf<String, MutableList<List<String>>>()

    fun shouldStop(btStates: Map<String, NodeBtState>): Boolean {
        // 1. Root node rank is stable across last N rounds
        val rootState = btStates["root"] ?: return false
        val rootHistory = rankHistoryByNode.getOrPut("root") { mutableListOf() }
        val currentRanking = rootState.btScores.entries.sortedByDescending { it.value }.map { it.key }
        rootHistory += currentRanking
        if (rootHistory.size >= stabilityRounds) {
            val stable = rootHistory.takeLast(stabilityRounds).all { it == currentRanking }
            if (stable) return true
        }

        // 2. Adjacent models are well-separated at root
        val scores = rootState.btScores
        val ses = rootState.stdErrors
        val ranked = scores.entries.sortedByDescending { it.value }
        val allSeparated = ranked.zipWithNext().all { (a, b) ->
            val gap = a.value - b.value
            val combinedSE = (ses[a.key] ?: 1.0) + (ses[b.key] ?: 1.0)
            gap > separationThreshold * combinedSE
        }
        if (allSeparated) return true

        // 3. No remaining pair has utility above threshold
        // (handled in scheduler — if batch is empty, stop)
        return false
    }
}
```

***

## 8. TaxonomyRankingService Integration

The existing `TaxonomyRankingService` should be extended to expose per-node BT leaderboards:

```kotlin
// Existing method — keep, wire to root node BT state
fun getGlobalLeaderboard(): List<ModelRank>

// New methods
fun getNodeLeaderboard(nodeId: String): List<ModelRank>?
fun getDomainLeaderboard(domainLabel: String): List<ModelRank>?
fun getPositionFlipRate(nodeId: String, modelA: String, modelB: String): Double
fun getBtState(nodeId: String): NodeBtState?
```

Where `ModelRank` adds:

```kotlin
data class ModelRank(
    val modelId: String,
    val btScore: Double,
    val stdError: Double,
    val rank: Int,
    val confidenceIntervalLow: Double,   // btScore - 2*stdError
    val confidenceIntervalHigh: Double,  // btScore + 2*stdError
    val winsTotal: Double,
    val comparisonsTotal: Int,
)
```

***

## 9. TUI Integration

### 9.1 Benchmark Panel

The existing benchmark panel should show, per node/domain:

```
┌─ BENCHMARK LEADERBOARD — Mathematics ─────────────────────────────┐
│  Rank  Model               BT Score   95% CI          Comparisons │
│  1     Meta-Llama-3-70B    +1.24    [+0.91, +1.57]    183         │
│  2     Llama-2-70b-hf      +0.31    [-0.02, +0.64]    183         │
│  3     Meta-Llama-3-8B     -0.44    [-0.79, -0.09]    182         │
│  4     Llama-2-7b-hf       -1.11    [-1.48, -0.74]    183         │
│                                                                     │
│  Position flips: 12/549 (2.2%)   Active pairs: 2/6                │
│  Rounds: 4/20   Status: RUNNING                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 9.2 TUI State Updates

Add to `BenchmarkState`:

```kotlin
data class BenchmarkState(
    // ... existing fields ...
    val btLeaderboards: Map<String, List<ModelRank>> = emptyMap(),   // nodeId → ranked list
    val btRound: Int = 0,
    val positionFlipStats: Map<String, Int> = emptyMap(),            // nodeId → flip count
    val activePairs: List<BtMatchTask> = emptyList(),
    val isBtConverged: Boolean = false,
)
```

Expose via `TuiBenchmarkFacade` following the existing MVI pattern — no direct service calls from the panel.

***

## 10. Implementation Order

| Phase | Work Item | Dependencies |
|---|---|---|
| 1 | Add `NodePairStats`, `NodeBtState`, `BtMatchTask` data classes | None |
| 2 | Add `positionFlip` and `nodeId` fields to `DomainEvaluation` | `evaluatePairwise` |
| 3 | Implement `BtMmFitter.fit()` and `estimateStdErrors()` | Phase 1 |
| 4 | Implement `NodePairStatsStore` (in-memory + SQLite persistence) | Phase 1 |
| 5 | Implement `propagateOutcome()` + `GraphNode.pathToRoot()` | Phases 1, 2 |
| 6 | Implement `BtMatchScheduler` (node selection + batch selection) | Phases 1, 3 |
| 7 | Replace round-robin loop in `ArenaBenchmarkService` with BT batch loop | Phases 1–6 |
| 8 | Extend `TaxonomyRankingService` with per-node BT methods | Phases 3, 4 |
| 9 | Implement `BtStoppingPolicy` | Phase 3 |
| 10 | Wire to TUI: `BenchmarkState`, `TuiBenchmarkFacade`, leaderboard panel | Phases 7, 8 |

***

## 11. Key Design Decisions

### 11.1 Ties → Half-Win Encoding

Position flips from `evaluatePairwise` (where the two swap orderings disagree) become `winsA += 0.5`, `winsB += 0.5` in `NodePairStats`. This is the correct BT encoding for ties and avoids introducing a separate tie parameter in the first version. The raw flip count is tracked separately for diagnostics.[^4][^1]

### 11.2 No BT for Nodes with Fewer Than 3 Comparisons per Pair

BT fitting is numerically unstable with fewer than 3 observations per pair. Gate all fit calls:

```kotlin
if (pairStats.any { it.totalComparisons < 3 }) return bootstrapState(models)
```

Return a flat prior (all scores = 0, high stdErr) until sufficient evidence accumulates.

### 11.3 Score Anchoring

Always normalize BT scores so `mean(scores) = 0` after each fit. This makes scores interpretable across nodes and rounds without drift.

### 11.4 Precomputed vs Live Mode

The existing framework supports both precomputed benchmark answers and live arena generation. The BT matchmaker works identically in both modes — it schedules `(node, modelA, modelB, queryIds)` tasks, and whether those tasks call the model live or load cached traces is resolved downstream in the executor.[^11]

### 11.5 Multi-Parent DAG Propagation

For DAG nodes with multiple parents, `pathToRoot()` returns all paths. Propagate to every path to ensure no ancestor subtree is missed. `NodePairStatsStore.accumulate()` uses an additive model — evidence from multiple paths to the same ancestor is summed, not averaged. This is correct because each path represents an independent contribution to the ancestor's evidence pool.

***

## 12. Validation Checklist

Before shipping:

- [ ] `BtMmFitter.fit()` converges on a 3-model toy example with known ground truth
- [ ] `propagateOutcome()` correctly updates all ancestors for a 4-level DAG
- [ ] `BtMatchScheduler` never schedules more than `maxConcurrentPerModel` active tasks per model per batch
- [ ] Position flip rate is logged and visible in the TUI
- [ ] BT leaderboard at root matches qualitative expectations from existing round-robin benchmark results
- [ ] `BtStoppingPolicy` terminates within `maxRounds` even if convergence is not reached
- [ ] Persistence: `NodePairStats` and `NodeBtState` survive a TUI restart (SQLite)
- [ ] Half-win tie encoding: a pair with all ties produces `btScore ≈ 0.0` for both models

---

## References

1. [Recent advances in the Bradley–Terry Model: theory, algorithms ...](https://arxiv.org/html/2601.14727v1)

2. [[PDF] Experimental Design under the Bradley-Terry Model - IJCAI](https://www.ijcai.org/proceedings/2018/0304.pdf)

3. [[PDF] Lecture 24 — The Bradley-Terry model](https://web.stanford.edu/class/archive/stats/stats200/stats200.1172/Lecture24.pdf)

4. [[PDF] Efficient Bayesian Inference for Generalized Bradley-Terry Models](https://www.stats.ox.ac.uk/~doucet/caron_doucet_bayesianbradleyterry.pdf)

5. [[PDF] arXiv:2401.08463v2 [math.ST] 2 Apr 2024](https://arxiv.org/pdf/2401.08463.pdf)

6. [[PDF] A Hybrid Active Sampling Strategy for Pairwise Preference ...](https://proceedings.neurips.cc/paper_files/paper/2018/file/8b6a80c3cf2cbd5f967063618dc54f39-Paper.pdf)

7. [[PDF] Example of the Glicko-2 system - Mark Glickman](https://glicko.net/glicko/glicko2.pdf)

8. [[PDF] Active Ranking from Pairwise Comparisons and when Parametric ...](https://arxiv.org/pdf/1606.08842.pdf)

9. [Active Top-K Ranking from Noisy Comparisons](http://csuh.kaist.ac.kr/Suh_active_topK.pdf)

10. [[PDF] Batched Dueling Bandits](https://proceedings.mlr.press/v162/agarwal22a/agarwal22a.pdf) - Our algorithm in Theorem 1.1 proceeds by performing all pairwise comparisons in an active set of ban...

11. [taxoarena_space_memory.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_8224ef51-8907-4cd0-90c7-a5db9c3131f2/d37106db-40af-45a3-802b-379587b6ec9a/taxoarena_space_memory.md?AWSAccessKeyId=ASIA2F3EMEYEWOIF2CJF&Signature=NAzxx7gJ1FN2cFDtEG6iRNWAs7I%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEEAaCXVzLWVhc3QtMSJHMEUCIQDRRuozwqNHT5fdTqjfyCw6TA7k79dHkYd49yhqtuA%2BZgIgHoCQ4Wk6H2EHivgDMGMU%2F2%2BG5uEZzxhv%2Bbnr7aRa%2FlUq8wQICRABGgw2OTk3NTMzMDk3MDUiDLHIkkpohesuyD5W%2BSrQBPm2EbhbZfmSQCS6LtZsXMOLg8nR9hlObIfiKyUqi5X7u4RPKfYz6Hq%2BlchwpS%2Fw%2Fx9tGnC20nDHcdGthXVOX5IjJ%2FkNzTvfOW6fclqxtW%2BbTuFmbNenyNjJyvon03H8V%2BtdFnJ6jDgPKc4GQ4sNRjO6gIr98PCRnbAJ5KmnrcGHNyAATGUWZE6njo5VPayZs%2FiUl%2BEU3FADMfBHYyv5uUJgS51KTxJebPQ7LkdygUxK5%2FDHbgJa%2FlJ6v78PFrKlUaBq8BoU75dZ3xDcH3etgvJArZ592mqdXYEE6B28wl69c0Ok8ksbx8OBldhq11ZsDVdgA6GY5xu2ClRy7Bs8olACziiNHKXuGXCBjjtVq6ymwA8mtqbW0UIJrkVeJeUHFnKrAupKXpg8ZmROq5qn9sNb%2BgyrJsKyyLmsnJH0HQMG5uePZT%2FRnVdu4G0nB9OJu%2FiKPkziNlj6uGszEpAG2chX%2FHw6HGGxevq0EQ%2FFvj7zPTa36Ih3bj72Szd9Vj0GhNPRhxeaI350Q0qv6QNuR%2FTCIe7HH%2BxB%2FuAlSWlHZ4J7QU2Y9wJg7VGXUbm8Wic5w8%2F16%2FNxtMHLeD4hhhHIXkzhoetsUWIpr4N8duc98mJyEZM075i2VsqvkFkNDplMd23MWhTI9t2Kxdm7oJTpxaIXdEdNXurTgNna76rBAHswTrMYDo5CL6fyVasDozv8dCJoxGa8Qm5Frz70fJ17xuB4FV2vn%2BwpkRgwz3lAUNPUzYpz0JqTO8aioe3koo6zDimSQmm3gEdqb9RGbEOMSmgw0did0gY6mAGiP9DkOKkSzqFIjzn87XREeXijOUyQ664VOBLdRXqFn5oodYPPM1WtW91d1KKLQ016Gx1dSpLeBq9PRuenF5CS4ueYpiVGVxXDF23YDznttvwzBug2IgsTmfLh8nPXb%2BnICC%2FydD9Id7KJsek72R0rGhnPsX5wQeqG8LRASeHw8ZY4YkGq2SeT4OKDQBgI2jamWqJhmJBlQA%3D%3D&Expires=1783069220)

