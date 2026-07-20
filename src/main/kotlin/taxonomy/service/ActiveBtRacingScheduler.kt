package taxonomy.service

import taxonomy.model.*
import taxonomy.dataset.ModelEvalResult
import java.util.UUID
import kotlin.math.abs
import kotlin.math.ln
import kotlin.math.sqrt

// ─── Common types ──────────────────────────────────────────────────────────

typealias PairKey = Pair<String, String>

fun ordered(a: String, b: String): PairKey = if (a < b) a to b else b to a

enum class LeafState { ACTIVE, RESOLVED, EXHAUSTED }

class PairStats(var sumX: Double = 0.0, var n: Int = 0)

/**
 * One per-leaf arena. predictions is model -> query -> extracted pred.
 */
class LeafArena(
    val leafId: String,
    val modelIds: List<String>,
    val queryIds: List<Int>,
    val predictions: Map<String, Map<Int, String>>,
    val pairBudget: Int,                      // hard cap per pair (B_max)
) {
    val pairs: List<PairKey> = modelIds.flatMapIndexed { i, a ->
        modelIds.drop(i + 1).map { b -> ordered(a, b) }
    }
    val stats = HashMap<PairKey, PairStats>()
    val reserved = HashMap<PairKey, HashSet<Int>>()
    val completed = HashMap<PairKey, HashSet<Int>>()
    val pairExhausted = HashMap<PairKey, Boolean>()   // hit pairBudget unresolved, or no query left
    var state: LeafState = LeafState.ACTIVE

    fun used(key: PairKey): Set<Int> =
        (reserved[key] ?: emptySet()) + (completed[key] ?: emptySet())
}

// ─── Active BT Racing Scheduler ──────────────────────────────────────────────

class ActiveBtRacingScheduler(
    private val alpha: Double = 0.05,        // confidence level
    private val nMin: Int = 5,                // per-pair warm-start guard
) {

    /** Hoeffding radius with union bound over P pairs and Bmax peeks. */
    fun epsilon(n: Int, k: Int, bMax: Int): Double {
        if (n <= 0) return Double.POSITIVE_INFINITY
        val p = k * (k - 1) / 2
        return sqrt(ln(2.0 * p * bMax / alpha) / (2.0 * n))
    }

    /** Rank by Copeland (win-count) — optimal up to constants (Heckel 2018). */
    fun ranking(a: LeafArena): List<String> {
        val score = a.modelIds.associateWith { 0.0 }.toMutableMap()
        for ((key, s) in a.stats) {
            val (x, y) = key
            if (s.n == 0) continue
            val phat = s.sumX / s.n
            score[x] = score.getValue(x) + phat
            score[y] = score.getValue(y) + (1.0 - phat)
        }
        return score.toList().sortedByDescending { it.second }.map { it.first }
    }

    fun pairStatus(a: LeafArena, key: PairKey): String {
        if (a.pairExhausted[key] == true) return "PAIR_EXHAUSTED"
        val s = a.stats.getOrPut(key) { PairStats() }
        val eps = epsilon(s.n, a.modelIds.size, a.pairBudget)
        val resolved = (s.n >= nMin) && (abs((if (s.n > 0) s.sumX / s.n else 0.5) - 0.5) > eps)
        if (resolved) return "RESOLVED"
        if (s.n >= a.pairBudget) { 
            a.pairExhausted[key] = true
            return "PAIR_EXHAUSTED" 
        }
        return "UNRESOLVED"
    }

    /**
     * Warm start: until every pair has >=1 comparison, pick globally least-sampled.
     * After: rank-adjacent largest-overlap pair.
     */
    fun pickPair(a: LeafArena): PairKey? {
        if (a.state != LeafState.ACTIVE) return null
        if (a.modelIds.size < 2) { 
            a.state = LeafState.RESOLVED
            return null 
        }

        // Warm start tournament pass
        val unseeded = a.pairs.filter { (a.stats[it]?.n ?: 0) == 0 && a.pairExhausted[it] != true }
        if (unseeded.isNotEmpty()) return unseeded.first()
        if (a.pairs.any { (a.stats[it]?.n ?: 0) == 0 }) {
            a.state = LeafState.EXHAUSTED
            return null
        }

        val ranked = ranking(a)
        var best: PairKey? = null
        var bestOverlap = Double.NEGATIVE_INFINITY
        var allResolved = true

        for (k in 0 until ranked.size - 1) {
            val key = ordered(ranked[k], ranked[k + 1])
            when (pairStatus(a, key)) {
                "RESOLVED" -> { /* keep */ }
                "PAIR_EXHAUSTED" -> { allResolved = false }
                else -> {
                    allResolved = false
                    val s = a.stats.getValue(key)
                    val eps = epsilon(s.n, a.modelIds.size, a.pairBudget)
                    val phat = if (s.n > 0) s.sumX / s.n else 0.5
                    val overlap = if (s.n < nMin) Double.POSITIVE_INFINITY else eps - abs(phat - 0.5)
                    if (overlap > bestOverlap) { 
                        bestOverlap = overlap
                        best = key 
                    }
                }
            }
        }
        if (best == null) {
            a.state = if (allResolved) LeafState.RESOLVED else LeafState.EXHAUSTED
        }
        return best
    }

    /** Disagreement first, then unused. answer-key-blind. */
    fun pickQuery(a: LeafArena, key: PairKey): Int? {
        val used = a.used(key)
        val (x, y) = key
        val predX = a.predictions[x] ?: emptyMap()
        val predY = a.predictions[y] ?: emptyMap()
        val disagree = a.queryIds.filter { q -> q !in used && predX[q] != predY[q] && !predX[q].isNullOrBlank() && !predY[q].isNullOrBlank() }
        val pool = disagree.ifEmpty { a.queryIds.filter { it !in used } }
        return pool.minOrNull()
    }

    fun debt(a: LeafArena): Double {
        if (a.state != LeafState.ACTIVE) return 0.0
        if (a.pairs.any { (a.stats[it]?.n ?: 0) == 0 }) return Double.POSITIVE_INFINITY
        val ranked = ranking(a)
        var d = 0.0
        for (k in 0 until ranked.size - 1) {
            val key = ordered(ranked[k], ranked[k + 1])
            if (pairStatus(a, key) != "UNRESOLVED") continue
            val s = a.stats.getValue(key)
            val eps = epsilon(s.n, a.modelIds.size, a.pairBudget)
            val phat = if (s.n > 0) s.sumX / s.n else 0.5
            d += (eps - abs(phat - 0.5)).coerceAtLeast(0.0)
        }
        return d
    }

    fun selectNextBatch(
        targetNodes: List<GraphNode>,
        pairStats: Map<String, List<NodePairStats>>,
        models: List<String>,
        resultsMatrix: Map<Int, Map<String, ModelEvalResult>>,
        nodeToQueries: Map<String, List<Int>>,
        batchSize: Int,
        completedResults: List<QueryBenchmarkResult>,
        budgetPerPair: Int
    ): List<BtMatchTask> {
        // Build LeafArenas
        val arenas = targetNodes.map { node ->
            val leafId = node.id
            val queryIds = nodeToQueries[node.id] ?: emptyList()
            val predictions = models.associateWith { model ->
                queryIds.associateWith { qId ->
                    resultsMatrix[qId]?.get(model)?.pred ?: ""
                }
            }
            val leafArena = LeafArena(leafId, models, queryIds, predictions, budgetPerPair)

            // Populate completed
            for (qr in completedResults) {
                val qId = qr.queryId
                for ((pairKeyStr, evals) in qr.pairEvaluations) {
                    val pairModels = pairKeyStr.split("_vs_")
                    if (pairModels.size != 2) continue
                    val key = ordered(pairModels[0], pairModels[1])
                    if (evals.any { it.nodeId == leafId }) {
                        leafArena.completed.getOrPut(key) { hashSetOf() }.add(qId)
                    }
                }
            }

            // Populate stats
            val nodePairs = pairStats[node.id] ?: emptyList()
            for (ps in nodePairs) {
                val key = ordered(ps.modelA, ps.modelB)
                val stats = leafArena.stats.getOrPut(key) { PairStats() }
                val isModelA = key.first == ps.modelA
                val winsFirst = if (isModelA) ps.winsA else ps.winsB
                stats.sumX = winsFirst + 0.5 * ps.ties
                stats.n = ps.totalComparisons.toInt()
            }

            leafArena
        }

        val tasks = ArrayList<BtMatchTask>()
        while (tasks.size < batchSize) {
            val active = arenas.filter { it.state == LeafState.ACTIVE }
                .sortedByDescending { debt(it) }
            if (active.isEmpty()) break
            var progressed = false
            for (leaf in active) {
                if (tasks.size >= batchSize) break
                val key = pickPair(leaf) ?: continue
                val q = pickQuery(leaf, key)
                if (q == null) {
                    leaf.pairExhausted[key] = true
                    progressed = true
                    continue
                }
                leaf.reserved.getOrPut(key) { hashSetOf() }.add(q)
                tasks.add(
                    BtMatchTask(
                        nodeId = leaf.leafId,
                        modelA = key.first,
                        modelB = key.second,
                        queryIds = listOf(q.toString()),
                        priority = debt(leaf),
                        batchId = UUID.randomUUID().toString()
                    )
                )
                progressed = true
            }
            if (!progressed) break
        }
        return tasks
    }
}
