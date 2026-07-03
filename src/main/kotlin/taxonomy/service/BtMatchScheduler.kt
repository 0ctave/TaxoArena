package taxonomy.service

import taxonomy.model.*
import taxonomy.dataset.ModelEvalResult
import java.util.UUID
import kotlin.math.abs
import kotlin.math.exp

class BtMatchScheduler(
    val minQueriesForBenchmark: Int = 1,
    val queriesPerPair: Int = 20,
    val alpha: Double = 0.5,
    val beta: Double = 0.4,
    val gamma: Double = 0.1,
    val budgetPerPair: Int = 100
) {

    private val log = org.slf4j.LoggerFactory.getLogger("taxonomy.service.BtMatchScheduler")

    fun selectTargetNodes(
        allNodes: List<GraphNode>,
        btStates: Map<String, NodeBtState>,
        nodeToQueries: Map<String, List<Int>>,
        maxNodes: Int = 5
    ): List<GraphNode> {
        return allNodes
            .filter { it.children.isEmpty() && (nodeToQueries[it.id]?.size ?: 0) >= minQueriesForBenchmark }
            .sortedByDescending { node ->
                val state = btStates[node.id] ?: return@sortedByDescending Double.MAX_VALUE
                state.stdErrors.values.average()
            }
            .take(maxNodes)
    }

    fun selectNextBatch(
        targetNodes: List<GraphNode>,
        btStates: Map<String, NodeBtState>,
        pairStats: Map<String, List<NodePairStats>>,   // nodeId -> pairs
        models: List<String>,
        resultsMatrix: Map<Int, Map<String, ModelEvalResult>>,
        nodeToQueries: Map<String, List<Int>>,
        batchSize: Int,
        maxConcurrentPerModel: Int = maxOf(2, models.size - 1)
    ): List<BtMatchTask> {
        val tasks = mutableListOf<BtMatchTask>()
        val modelLoad = mutableMapOf<String, Int>()
        val totalModelMatches = models.associateWith { model ->
            pairStats.values.flatten()
                .filter { it.modelA == model || it.modelB == model }
                .sumOf { it.totalComparisons }
        }

        for (node in targetNodes) {
            if (tasks.size >= batchSize) break
            val state = btStates[node.id]
            val nodePairs = pairStats[node.id] ?: emptyList()

            val nodeQuestionIds = mutableListOf<Int>()
            nodeQuestionIds.addAll(nodeToQueries[node.id] ?: emptyList())

            if (nodeQuestionIds.size < queriesPerPair) {
                val visited = mutableSetOf<String>(node.id)
                val queue = java.util.ArrayDeque<GraphNode>()
                queue.addAll(node.parents)
                while (queue.isNotEmpty() && nodeQuestionIds.size < queriesPerPair) {
                    val parent = queue.removeFirst()
                    if (visited.add(parent.id)) {
                        val descendants = mutableSetOf<GraphNode>()
                        fun walkDescendants(n: GraphNode) {
                            if (n.children.isEmpty()) {
                                descendants.add(n)
                            } else {
                                n.children.forEach { walkDescendants(it) }
                            }
                        }
                        walkDescendants(parent)
                        
                        for (desc in descendants) {
                            val descQueries = nodeToQueries[desc.id] ?: emptyList()
                            for (q in descQueries) {
                                if (q !in nodeQuestionIds) {
                                    nodeQuestionIds.add(q)
                                }
                            }
                        }
                        queue.addAll(parent.parents)
                    }
                }
            }

            val availableQueries = resultsMatrix.filter { it.key in nodeQuestionIds }
            if (availableQueries.isEmpty()) continue

            // Generate all candidate pairs
            val candidates = models.flatMapIndexed { i, mA ->
                models.drop(i + 1).map { mB -> mA to mB }
            }

            candidates
                .sortedByDescending { (mA, mB) -> computeUtility(node.id, mA, mB, state, nodePairs, totalModelMatches) }
                .forEach { (mA, mB) ->
                    if (tasks.size >= batchSize) return@forEach
                    if ((modelLoad[mA] ?: 0) >= maxConcurrentPerModel) return@forEach
                    if ((modelLoad[mB] ?: 0) >= maxConcurrentPerModel) return@forEach

                    // Filter queries that haven't been fully compared yet for this pair
                    val ps = nodePairs.firstOrNull { 
                        (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA) 
                    }
                    val limit = if (ps == null || ps.totalComparisons < queriesPerPair) {
                        queriesPerPair
                    } else {
                        if (shouldExtendPair(ps, state?.btScores ?: emptyMap())) {
                            (ps.totalComparisons + EXTENSION_QUESTIONS).coerceAtMost(MAX_QUESTIONS_PER_PAIR)
                        } else {
                            ps.totalComparisons
                        }
                    }
                    val needed = limit - (ps?.totalComparisons ?: 0)
                    if (needed <= 0) return@forEach

                    // Take a slice of available queries
                    val evaluatedCount = ps?.totalComparisons ?: 0
                    val querySlice = availableQueries.keys.drop(evaluatedCount).take(minOf(needed, BATCH_STEP_SIZE))
                    log.info("DEBUG: Scheduler at node ${node.label ?: node.id} for pair $mA vs $mB: evaluatedCount=$evaluatedCount, needed=$needed, limit=$limit, availableQueriesSize=${availableQueries.size}, querySlice=$querySlice")
                    if (querySlice.isEmpty()) return@forEach

                    tasks += BtMatchTask(
                        nodeId = node.id,
                        modelA = mA,
                        modelB = mB,
                        queryIds = querySlice.map { it.toString() },
                        priority = computeUtility(node.id, mA, mB, state, nodePairs, totalModelMatches),
                        batchId = UUID.randomUUID().toString()
                    )
                    modelLoad[mA] = (modelLoad[mA] ?: 0) + 1
                    modelLoad[mB] = (modelLoad[mB] ?: 0) + 1
                }
        }

        return tasks
    }

    fun computeUtility(
        nodeId: String,
        mA: String,
        mB: String,
        state: NodeBtState?,
        nodePairs: List<NodePairStats>,
        totalModelMatches: Map<String, Int> = emptyMap()
    ): Double {
        val matchesA = totalModelMatches[mA] ?: 0
        val matchesB = totalModelMatches[mB] ?: 0
        if (matchesA == 0 || matchesB == 0) {
            // Prioritize bootstrapping models with 0 matches
            return 10000.0 + (if (state != null) {
                val sei = state.stdErrors[mA] ?: 10.0
                val sej = state.stdErrors[mB] ?: 10.0
                sei + sej
            } else 10.0)
        }

        val ps = nodePairs.firstOrNull { 
            (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA) 
        }
        val nij = ps?.totalComparisons ?: 0

        // Closeness: highest when P(A beats B) is 0.5
        val closeness = if (state != null) {
            val si = state.btScores[mA] ?: 0.0
            val sj = state.btScores[mB] ?: 0.0
            val denom = exp(si) + exp(sj)
            val pij = if (denom == 0.0) 0.5 else exp(si) / denom
            1.0 - abs(pij - 0.5) * 2.0
        } else 1.0

        // Uncertainty: high when Standard Errors are high
        val uncertainty = if (state != null) {
            val sei = state.stdErrors[mA] ?: Double.MAX_VALUE
            val sej = state.stdErrors[mB] ?: Double.MAX_VALUE
            if (sei == Double.MAX_VALUE || sej == Double.MAX_VALUE) 10.0 else sei + sej
        } else 10.0

        val repeatPenalty = nij.toDouble() / budgetPerPair

        return alpha * closeness + beta * uncertainty - gamma * repeatPenalty
    }

    companion object {
        const val BATCH_STEP_SIZE = 2
        const val EXTENSION_QUESTIONS = 2
        const val MAX_QUESTIONS_PER_PAIR = 100

        fun shouldExtendPair(ps: NodePairStats, scores: Map<String, Double>): Boolean {
            val si = scores[ps.modelA] ?: return false
            val sj = scores[ps.modelB] ?: return false
            val denom = exp(si) + exp(sj)
            val pij = if (denom == 0.0) 0.5 else exp(si) / denom
            return abs(pij - 0.5) < 0.15 && ps.totalComparisons < MAX_QUESTIONS_PER_PAIR
        }
    }
}
