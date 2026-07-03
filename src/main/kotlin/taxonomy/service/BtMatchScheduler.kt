package taxonomy.service

import taxonomy.model.*
import taxonomy.dataset.ModelEvalResult
import java.util.UUID
import java.util.PriorityQueue
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.ln

data class MatchCandidate(
    val nodeId: String,
    val modelA: String,
    val modelB: String,
    val utility: Double,
    val pairKey: String
)

class BtMatchScheduler(
    val minQueriesForBenchmark: Int = 1,
    val queriesPerPair: Int = 20,
    val budgetPerPair: Int = 100,
    val stoppingPolicy: BtStoppingPolicy
) {
    private val log = org.slf4j.LoggerFactory.getLogger("taxonomy.service.BtMatchScheduler")
    private val pairQueryOffsets = mutableMapOf<String, Int>()

    fun selectNextBatch(
        targetNodes: List<GraphNode>,
        btStates: Map<String, NodeBtState>,
        pairStats: Map<String, List<NodePairStats>>,
        models: List<String>,
        resultsMatrix: Map<Int, Map<String, ModelEvalResult>>,
        nodeToQueries: Map<String, List<Int>>,
        batchSize: Int,
        maxConcurrentPerModel: Int = maxOf(2, models.size - 1)
    ): List<BtMatchTask> {
        val leafModelMatches = targetNodes.associate { node ->
            node.id to models.associateWith { model ->
                (pairStats[node.id] ?: emptyList())
                    .filter { it.modelA == model || it.modelB == model }
                    .sumOf { it.totalComparisons }
            }
        }

        // --- Phase 1: Pair coverage pass ---
        // Any pair that has ZERO comparisons on ANY leaf gets one slot before queue runs.
        // This guarantees every pair appears at least once per batch when budget allows.
        val allPairs = models.flatMapIndexed { i, mA -> models.drop(i + 1).map { mB -> mA to mB } }
        val globalPairCounts = allPairs.associateWith { (mA, mB) ->
            targetNodes.sumOf { node ->
                (pairStats[node.id] ?: emptyList()).firstOrNull {
                    (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
                }?.totalComparisons ?: 0
            }
        }

        val tasks = mutableListOf<BtMatchTask>()
        val nodeModelLoad = mutableMapOf<String, MutableMap<String, Int>>()
        val globalModelLoad = mutableMapOf<String, Int>()
        // Global cap: each pair gets AT MOST batchSize/numPairs slots → spread budget evenly
        val numPairs = allPairs.size
        val fairSharePerPair = (batchSize / numPairs).coerceAtLeast(1)
        val pairBatchCount = mutableMapOf<String, Int>()

        fun pairKey(mA: String, mB: String) = "${minOf(mA, mB)}|${maxOf(mA, mB)}"

        fun trySchedule(nodeId: String, mA: String, mB: String, utility: Double, ignoreFairShare: Boolean = false): Boolean {
            if (tasks.size >= batchSize) return false
            val pk = pairKey(mA, mB)
            if (!ignoreFairShare && (pairBatchCount[pk] ?: 0) >= fairSharePerPair) return false

            val nodeLoad = nodeModelLoad.getOrPut(nodeId) { mutableMapOf() }
            if ((nodeLoad[mA] ?: 0) >= 1) return false
            if ((nodeLoad[mB] ?: 0) >= 1) return false

            if ((globalModelLoad[mA] ?: 0) >= maxConcurrentPerModel) return false
            if ((globalModelLoad[mB] ?: 0) >= maxConcurrentPerModel) return false

            val ps = (pairStats[nodeId] ?: emptyList()).firstOrNull {
                (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
            }
            val budget = pairBudget(mA, mB, btStates[nodeId], ps)
            if ((ps?.totalComparisons ?: 0) >= budget) return false

            val nodeQueryIds = (nodeToQueries[nodeId] ?: emptyList()).sorted()
            val available = resultsMatrix.keys.intersect(nodeQueryIds.toSet()).sorted()
            if (available.isEmpty()) return false

            val offset = pairQueryOffsets.getOrDefault("$nodeId|$pk", ps?.totalComparisons ?: 0)
            val slice = available.drop(offset).take(BATCH_STEP_SIZE)
            if (slice.isEmpty()) return false

            pairQueryOffsets["$nodeId|$pk"] = offset + slice.size
            tasks += BtMatchTask(
                nodeId = nodeId, modelA = mA, modelB = mB,
                queryIds = slice.map { it.toString() },
                priority = utility, batchId = UUID.randomUUID().toString()
            )
            nodeLoad[mA] = (nodeLoad[mA] ?: 0) + 1
            nodeLoad[mB] = (nodeLoad[mB] ?: 0) + 1
            globalModelLoad[mA] = (globalModelLoad[mA] ?: 0) + 1
            globalModelLoad[mB] = (globalModelLoad[mB] ?: 0) + 1
            pairBatchCount[pk] = (pairBatchCount[pk] ?: 0) + 1
            return true
        }

        // Coverage pass: pairs with fewest global comparisons go first (round-robin by deficit)
        val unconvergedNodes = targetNodes.filter {
            !stoppingPolicy.isLeafConverged(it.id, btStates, pairStats, models)
        }
        val pairsSortedByDeficit = allPairs.sortedBy { (mA, mB) -> globalPairCounts[mA to mB] ?: 0 }

        // One slot per pair per node — iterate pairs in deficit order, nodes in SE-desc order
        for ((mA, mB) in pairsSortedByDeficit) {
            if (tasks.size >= batchSize) break
            val nodesForPair = unconvergedNodes.sortedByDescending { node ->
                btStates[node.id]?.stdErrors?.values?.average() ?: 10.0
            }
            for (node in nodesForPair) {
                if (tasks.size >= batchSize) break
                trySchedule(node.id, mA, mB, LN2 + 1.0, ignoreFairShare = false)
            }
        }

        // --- Phase 2: Entropy queue for remaining budget ---
        // Build heap only for remaining capacity, using true H(p) scores
        if (tasks.size < batchSize) {
            val heap = PriorityQueue<MatchCandidate>(compareByDescending { it.utility })
            for (node in unconvergedNodes) {
                val state = btStates[node.id]
                val nodePairs = pairStats[node.id] ?: emptyList()
                val leafMatches = leafModelMatches[node.id] ?: emptyMap()
                for ((mA, mB) in allPairs) {
                    val ps = nodePairs.firstOrNull {
                        (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
                    }
                    val nij = ps?.totalComparisons ?: 0
                    val u = computeEntropy(mA, mB, state, leafMatches, nij)
                    heap.add(MatchCandidate(node.id, mA, mB, u, "${node.id}|${pairKey(mA, mB)}"))
                }
            }

            val remainingCandidates = mutableListOf<MatchCandidate>()
            while (tasks.size < batchSize && heap.isNotEmpty()) {
                val c = heap.poll()!!
                val success = trySchedule(c.nodeId, c.modelA, c.modelB, c.utility, ignoreFairShare = false)
                if (!success) {
                    remainingCandidates.add(c)
                }
            }
            if (tasks.size < batchSize) {
                for (c in remainingCandidates) {
                    if (tasks.size >= batchSize) break
                    trySchedule(c.nodeId, c.modelA, c.modelB, c.utility, ignoreFairShare = true)
                }
            }
        }

        return tasks
    }

    /**
     * Information entropy score for one comparison under BT.
     * H(Y_ij | θ̂) = -p log p - (1-p) log(1-p)
     * Maximised at p = 0.5 (pure uncertainty), = 0 when p → 0 or 1.
     *
     * Bootstrap guard: if either model is unseen on this leaf,
     * return max entropy (ln 2) + bonus so bootstrap always wins.
     */
    private fun computeEntropy(
        mA: String, mB: String,
        state: NodeBtState?,
        leafModelMatches: Map<String, Int>,
        nij: Int
    ): Double {
        // Bootstrap: unseen model → maximum priority
        if ((leafModelMatches[mA] ?: 0) == 0 || (leafModelMatches[mB] ?: 0) == 0)
            return LN2 + 1.0 + (10.0 - minOf(nij, 10)) * 0.1

        if (state == null) return LN2  // no BT state yet → full uncertainty

        val si = state.btScores[mA] ?: 0.0
        val sj = state.btScores[mB] ?: 0.0
        val denom = exp(si) + exp(sj)
        val p = if (denom == 0.0) 0.5 else exp(si) / denom

        // Binary entropy H(p) — the canonical information-theoretic score
        val h = if (p <= 0.0 || p >= 1.0) 0.0
                else -p * ln(p) - (1.0 - p) * ln(1.0 - p)

        // Diminishing-returns penalty for over-sampled pairs
        val repeatDiscount = (nij.toDouble() / budgetPerPair).coerceAtMost(1.0)
        return h * (1.0 - 0.3 * repeatDiscount)
    }

    private fun pairBudget(mA: String, mB: String, state: NodeBtState?, ps: NodePairStats?): Int {
        if (state == null || ps == null) return queriesPerPair
        val si = state.btScores[mA] ?: 0.0
        val sj = state.btScores[mB] ?: 0.0
        val p = exp(si) / (exp(si) + exp(sj)).coerceAtLeast(1e-300)
        return if (abs(p - 0.5) < 0.15)
            (queriesPerPair * 2).coerceAtMost(budgetPerPair)
        else queriesPerPair
    }

    fun selectTargetNodes(
        allNodes: List<GraphNode>,
        btStates: Map<String, NodeBtState>,
        nodeToQueries: Map<String, List<Int>>,
        maxNodes: Int = 100
    ): List<GraphNode> {
        return allNodes
            .filter { it.children.isEmpty() && (nodeToQueries[it.id]?.size ?: 0) >= minQueriesForBenchmark }
            .sortedWith(
                compareByDescending<GraphNode> { node -> (btStates[node.id]?.totalComparisons ?: 0) == 0 }
                    .thenByDescending { node -> nodeToQueries[node.id]?.size ?: 0 }
                    .thenByDescending { node -> btStates[node.id]?.stdErrors?.values?.average() ?: 10.0 }
            )
            .take(maxNodes)
    }

    companion object {
        const val BATCH_STEP_SIZE = 5
        val LN2 = ln(2.0)
    }
}
