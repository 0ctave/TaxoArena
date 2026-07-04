package taxonomy.service

import taxonomy.model.*
import taxonomy.dataset.ModelEvalResult
import taxonomy.utils.StatisticsUtils
import java.util.UUID
import java.util.PriorityQueue
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.pow

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

    private fun isMatchInformative(
        mA: String, mB: String,
        state: NodeBtState?,
        ps: NodePairStats?,
        minMatches: Int = 2
    ): Boolean {
        // Always play if either model is unseen (bootstrap guarantee)
        val nij = ps?.totalComparisons ?: 0
        if (nij < minMatches) return true

        // No BT state yet → informative by default
        if (state == null) return true

        val si = state.btScores[mA] ?: 0.0
        val sj = state.btScores[mB] ?: 0.0
        val seA = state.stdErrors[mA] ?: 10.0
        val seB = state.stdErrors[mB] ?: 10.0
        val gap = abs(si - sj)
        val combinedSE = seA + seB

        // Skip if the gap is > 3 combined SEs — outcome is already certain
        // BT p_{ij} > 0.95 when gap > 3.0 logits → H(p) < 0.20 → negligible info
        // Using 3*SE rather than 3.0 logits to adapt to current estimation uncertainty
        return gap < 3.0 * combinedSE
    }

    private fun leafConvergenceDebt(
        nodeId: String,
        state: NodeBtState?,
        pairs: List<NodePairStats>,
        models: List<String>,
        nodeToQueries: Map<String, List<Int>>
    ): Int {
        if (state == null) return models.size * (models.size - 1) / 2
        val allPairs = models.flatMapIndexed { i, mA -> models.drop(i + 1).map { mB -> mA to mB } }
        return allPairs.count { (mA, mB) ->
            val ps = pairs.firstOrNull {
                (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
            }
            val nij = ps?.totalComparisons ?: 0
            if (nij >= budgetPerPair) return@count false  // budget-exhausted: skip
            if (nij < 2) return@count true
            val si = state.btScores[mA] ?: 0.0
            val sj = state.btScores[mB] ?: 0.0
            val seA = state.stdErrors[mA] ?: 10.0
            val seB = state.stdErrors[mB] ?: 10.0
            abs(si - sj) < 3.0 * (seA + seB)
        }
    }

    // Returns a flat priority queue of all schedulable (leaf, mA, mB) triples
    private fun buildQueue(
        targetNodes: List<GraphNode>,
        btStates: Map<String, NodeBtState>,
        pairStats: Map<String, List<NodePairStats>>,
        models: List<String>,
        leafModelMatches: Map<String, Map<String, Int>>,
        nodeToQueries: Map<String, List<Int>>
    ): PriorityQueue<MatchCandidate> {
        // Max-heap: highest utility first
        val queue = PriorityQueue<MatchCandidate>(compareByDescending { it.utility })

        for (node in targetNodes) {
            // Converged leaves contribute no utility — skip entirely
            if (stoppingPolicy.isLeafConverged(node.id, btStates, pairStats, models, nodeToQueries)) continue

            val state = btStates[node.id]
            val nodePairs = pairStats[node.id] ?: emptyList()
            val leafMatches = leafModelMatches[node.id] ?: emptyMap()
            val debt = leafConvergenceDebt(node.id, state, nodePairs, models, nodeToQueries)

            val candidates = models.flatMapIndexed { i, mA -> models.drop(i + 1).map { mB -> mA to mB } }
            for ((mA, mB) in candidates) {
                val ps = nodePairs.firstOrNull {
                    (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
                }
                if (!isMatchInformative(mA, mB, state, ps, minMatches = 2)) continue // skip certain pairs

                val budget = pairBudget(mA, mB, state, ps)
                val already = ps?.totalComparisons ?: 0
                if (already >= budget) continue  // exhausted

                val isBlockingPair = isMatchInformative(mA, mB, state, ps) && already < (budgetPerPair - 5) // not near budget
                val convergenceBonus = if (debt <= 5 && isBlockingPair) 1.5 else 1.0  // last-mile boost

                val u = computeUtility(mA, mB, state, leafMatches, already) * convergenceBonus
                val pairKey = "${node.id}|${minOf(mA, mB)}|${maxOf(mA, mB)}"
                queue.add(MatchCandidate(node.id, mA, mB, u, pairKey))
            }
        }
        return queue
    }

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

        val nodesMap = targetNodes.associateBy { it.id }

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

        fun trySchedule(
            nodeId: String, mA: String, mB: String, utility: Double,
            ignoreFairShare: Boolean = false,
            ignoreGlobalCap: Boolean = false
        ): Boolean {
            if (tasks.size >= batchSize) return false
            val pk = pairKey(mA, mB)
            if (!ignoreFairShare && (pairBatchCount[pk] ?: 0) >= fairSharePerPair) return false

            val nodeLoad = nodeModelLoad.getOrPut(nodeId) { mutableMapOf() }
            if ((nodeLoad[mA] ?: 0) >= 1) return false
            if ((nodeLoad[mB] ?: 0) >= 1) return false

            if (!ignoreGlobalCap) {
                if ((globalModelLoad[mA] ?: 0) >= maxConcurrentPerModel) return false
                if ((globalModelLoad[mB] ?: 0) >= maxConcurrentPerModel) return false
            }

            val ps = (pairStats[nodeId] ?: emptyList()).firstOrNull {
                (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
            }
            val budget = pairBudget(mA, mB, btStates[nodeId], ps)
            if ((ps?.totalComparisons ?: 0) >= budget) return false

            val nodeQueryIds = (nodeToQueries[nodeId] ?: emptyList()).sorted()
            val available = resultsMatrix.keys.intersect(nodeQueryIds.toSet()).sorted()
            if (available.isEmpty()) return false

            val node = nodesMap[nodeId]
            val rankedAvailable = if (node != null && node.vmfMu.isNotEmpty()) {
                available.sortedByDescending { queryId ->
                    val emb = node.queries.find { it.queryId == queryId }
                    if (emb != null) {
                        val slicedX = emb.projectTo(node.sliceDim)
                        1.0 - StatisticsUtils.dotProduct(slicedX, node.vmfMu)
                    } else {
                        0.5
                    }
                }
            } else {
                available
            }

            val offset = pairQueryOffsets.getOrDefault("$nodeId|$pk", ps?.totalComparisons ?: 0)
            val slice = rankedAvailable.drop(offset).take(BATCH_STEP_SIZE)
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
            !stoppingPolicy.isLeafConverged(it.id, btStates, pairStats, models, nodeToQueries)
        }
        val pairsSortedByDeficit = allPairs.sortedBy { (mA, mB) -> globalPairCounts[mA to mB] ?: 0 }

        // One slot per pair per node — iterate pairs in deficit order, nodes in SE-desc order
        for ((mA, mB) in pairsSortedByDeficit) {
            if (tasks.size >= batchSize) break

            // Skip uninformative pairs even in coverage pass (after bootstrap)
            val globalPs = targetNodes.flatMap { pairStats[it.id] ?: emptyList() }
                .firstOrNull { (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA) }
            val globalNij = globalPs?.totalComparisons ?: 0
            if (globalNij >= 2) {  // bootstrap done — apply info filter
                val anyState = btStates.values.firstOrNull { it.btScores.containsKey(mA) && it.btScores.containsKey(mB) }
                    ?: btStates.values.firstOrNull()
                val ps = targetNodes.flatMap { node -> (pairStats[node.id] ?: emptyList()) }
                    .firstOrNull { (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA) }
                if (!isMatchInformative(mA, mB, anyState, ps, minMatches = 2)) continue
            }

            val nodesForPair = unconvergedNodes.sortedByDescending { node ->
                btStates[node.id]?.stdErrors?.values?.average() ?: 10.0
            }
            for (node in nodesForPair) {
                if (tasks.size >= batchSize) break
                trySchedule(node.id, mA, mB, LN2 + 1.0,
                    ignoreFairShare = false,
                    ignoreGlobalCap = true) // bootstrap/coverage always wins
            }
        }

        // --- Phase 2: Entropy queue for remaining budget ---
        // Build heap only for remaining capacity, using true H(p) / varSum scores
        if (tasks.size < batchSize) {
            val heap = buildQueue(unconvergedNodes, btStates, pairStats, models, leafModelMatches, nodeToQueries)

            val remainingCandidates = mutableListOf<MatchCandidate>()
            while (tasks.size < batchSize && heap.isNotEmpty()) {
                val c = heap.poll()!!
                val success = trySchedule(c.nodeId, c.modelA, c.modelB, c.utility,
                    ignoreFairShare = false,
                    ignoreGlobalCap = false)
                if (!success) {
                    remainingCandidates.add(c)
                }
            }
            if (tasks.size < batchSize) {
                for (c in remainingCandidates) {
                    if (tasks.size >= batchSize) break
                    trySchedule(c.nodeId, c.modelA, c.modelB, c.utility,
                        ignoreFairShare = true,
                        ignoreGlobalCap = false)
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
    private fun computeAlpha(state: NodeBtState?, totalModels: Int): Double {
        if (state == null) return 1.0  // no state: pure structure bootstrap

        // Maturity: ratio of current avg SE to prior SE (10.0)
        val avgSE = state.stdErrors.values.average().coerceAtLeast(1e-6)
        val maturity = (1.0 - avgSE / 10.0).coerceIn(0.0, 1.0)

        // Alpha decays from 0.8 -> 0.15 as maturity grows
        return 0.15 + 0.65 * exp(-3.0 * maturity)
    }

    private fun structureScore(mA: String, mB: String, state: NodeBtState): Double {
        val scores = state.btScores
        if (scores.size < 3) return 1.0

        val si = scores[mA] ?: 0.0
        val sj = scores[mB] ?: 0.0
        val mid = (si + sj) / 2.0
        val allScores = scores.values.sorted()
        val globalMid = allScores[allScores.size / 2]

        // How many models lie between mA and mB in score space?
        val bracketed = scores.values.count { s ->
            s in minOf(si, sj)..maxOf(si, sj)
        }.toDouble()

        // Normalised by total models — peaks for pairs that split the field
        val splitValue = bracketed / scores.size.toDouble()

        val seA = state.stdErrors[mA] ?: 1.0
        val seB = state.stdErrors[mB] ?: 1.0
        val medianProximity = exp(-0.5 * ((mid - globalMid) / (seA + seB).coerceAtLeast(1e-6)).pow(2.0))

        return splitValue * 0.6 + medianProximity * 0.4
    }

    private fun densityAwarePairWeight(mA: String, mB: String, state: NodeBtState): Double {
        val si = state.btScores[mA] ?: 0.0
        val sj = state.btScores[mB] ?: 0.0
        val seA = state.stdErrors[mA] ?: 1.0
        val seB = state.stdErrors[mB] ?: 1.0
        val gap = abs(si - sj)
        val combinedSE = seA + seB

        // Suppress if already separated beyond 4 SE
        if (gap >= 4.0 * combinedSE) return 0.0

        // Suppress if the gap is below the noise floor (e.g. 0.15 * combinedSE)
        val noiseFloor = 0.15 * combinedSE
        if (gap < noiseFloor) {
            return if (noiseFloor > 0.0) gap / noiseFloor else 0.0
        }

        return 1.0
    }

    private fun resolveScore(mA: String, mB: String, state: NodeBtState, nij: Int): Double {
        val si = state.btScores[mA] ?: 0.0
        val sj = state.btScores[mB] ?: 0.0
        val denom = exp(si) + exp(sj)
        val p = if (denom == 0.0) 0.5 else exp(si) / denom

        val h = if (p <= 0.0 || p >= 1.0) 0.0
                else -p * ln(p) - (1.0 - p) * ln(1.0 - p)

        val seA = state.stdErrors[mA] ?: 1.0
        val seB = state.stdErrors[mB] ?: 1.0
        val varSum = (seA * seA + seB * seB).coerceAtLeast(1e-6)

        val hNorm = h / varSum
        val w = densityAwarePairWeight(mA, mB, state)
        return hNorm * w
    }

    private fun computeUtility(
        mA: String, mB: String,
        state: NodeBtState?,
        leafModelMatches: Map<String, Int>,
        nij: Int
    ): Double {
        // Bootstrap: unseen model -> maximum priority
        if ((leafModelMatches[mA] ?: 0) == 0 || (leafModelMatches[mB] ?: 0) == 0)
            return LN2 + 1.0 + (10.0 - minOf(nij, 10)) * 0.1

        if (state == null) return LN2

        val alpha = computeAlpha(state, state.btScores.size)
        val sScore = structureScore(mA, mB, state)
        val rScore = resolveScore(mA, mB, state, nij)

        val repeatDiscount = (nij.toDouble() / budgetPerPair).coerceAtMost(1.0)
        return (alpha * sScore + (1.0 - alpha) * rScore) * (1.0 - 0.3 * repeatDiscount)
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
        pairStats: Map<String, List<NodePairStats>> = emptyMap(),
        models: List<String> = emptyList(),
        maxNodes: Int = 100
    ): List<GraphNode> {
        val candidates = allNodes.filter { node ->
            node.children.isEmpty()
            && (nodeToQueries[node.id]?.size ?: 0) >= minQueriesForBenchmark
            && !stoppingPolicy.isLeafConverged(node.id, btStates, pairStats, models, nodeToQueries)
        }

        data class SortCandidate(
            val node: GraphNode,
            val isBootstrap: Boolean,
            val convergenceDebt: Int,
            val avgStdError: Double,
            val queryCount: Int
        )

        return candidates.map { node ->
            val state = btStates[node.id]
            val isBootstrap = (state?.totalComparisons ?: 0) == 0
            val avgStdError = state?.stdErrors?.values?.let { if (it.isEmpty()) 10.0 else it.average() } ?: 10.0
            val queryCount = nodeToQueries[node.id]?.size ?: 0
            val debt = leafConvergenceDebt(node.id, state, pairStats[node.id] ?: emptyList(), models, nodeToQueries)
            SortCandidate(node, isBootstrap, debt, avgStdError, queryCount)
        }
        .sortedWith(
            compareByDescending<SortCandidate> { it.isBootstrap }
                .thenByDescending { it.convergenceDebt }
                .thenByDescending { it.avgStdError }
                .thenByDescending { it.queryCount }
        )
        .map { it.node }
        .take(maxNodes)
    }

    companion object {
        const val BATCH_STEP_SIZE = 5
        val LN2 = ln(2.0)
    }
}
