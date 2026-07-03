package taxonomy.service

import taxonomy.model.*
import taxonomy.dataset.ModelEvalResult
import java.util.UUID
import kotlin.math.abs
import kotlin.math.exp

class BtMatchScheduler(
    val minQueriesForBenchmark: Int = 1,
    val queriesPerPair: Int = 20,
    val budgetPerPair: Int = 100,
    val closeMatchThreshold: Double = 0.15,
    val stoppingPolicy: BtStoppingPolicy      // injected — no convergence logic here
) {
    private val log = org.slf4j.LoggerFactory.getLogger("taxonomy.service.BtMatchScheduler")
    private val pairQueryOffsets = mutableMapOf<String, Int>()

    fun selectTargetNodes(
        allNodes: List<GraphNode>,
        btStates: Map<String, NodeBtState>,
        nodeToQueries: Map<String, List<Int>>,
        maxNodes: Int = 100
    ): List<GraphNode> {
        return allNodes
            .filter { it.children.isEmpty() && (nodeToQueries[it.id]?.size ?: 0) >= minQueriesForBenchmark }
            .sortedWith(
                compareByDescending<GraphNode> { node ->
                    val state = btStates[node.id]
                    val started = (state?.totalComparisons ?: 0) > 0
                    !started
                }.thenByDescending { node ->
                    nodeToQueries[node.id]?.size ?: 0
                }.thenByDescending { node ->
                    val state = btStates[node.id]
                    state?.stdErrors?.values?.average() ?: 10.0
                }
            )
            .take(maxNodes)
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
        val tasks = mutableListOf<BtMatchTask>()
        val batchModelLoad = mutableMapOf<String, Int>()

        // Delegate convergence check entirely to the policy
        val leafConverged = targetNodes.associate { node ->
            node.id to stoppingPolicy.isLeafConverged(node.id, btStates, pairStats, models)
        }

        // Per-leaf match counts (leaf-local, not cross-leaf)
        val leafModelMatches = targetNodes.associate { node ->
            node.id to models.associateWith { model ->
                (pairStats[node.id] ?: emptyList())
                    .filter { it.modelA == model || it.modelB == model }
                    .sumOf { it.totalComparisons }
            }
        }

        // Unconverged leaves first, sorted by mean SE descending
        val prioritizedNodes = targetNodes
            .filter { leafConverged[it.id] != true }
            .sortedByDescending { node ->
                btStates[node.id]?.stdErrors?.values?.average() ?: 10.0
            }

        for (node in prioritizedNodes) {
            if (tasks.size >= batchSize) break

            val state = btStates[node.id]
            val nodePairs = pairStats[node.id] ?: emptyList()
            val nodeQueryIds = (nodeToQueries[node.id] ?: emptyList()).sorted()
            val available = resultsMatrix.keys.intersect(nodeQueryIds.toSet()).sorted()
            if (available.isEmpty()) continue

            val leafMatches = leafModelMatches[node.id] ?: emptyMap()
            val candidates = models.flatMapIndexed { i, mA -> models.drop(i + 1).map { mB -> mA to mB } }

            candidates
                .map { (mA, mB) -> Triple(mA, mB, computeUtility(mA, mB, state, nodePairs, leafMatches)) }
                .sortedByDescending { it.third }
                .forEach { (mA, mB, utility) ->
                    if (tasks.size >= batchSize) return@forEach
                    if ((batchModelLoad[mA] ?: 0) >= maxConcurrentPerModel) return@forEach
                    if ((batchModelLoad[mB] ?: 0) >= maxConcurrentPerModel) return@forEach

                    val ps = nodePairs.firstOrNull {
                        (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
                    }
                    val budget = pairBudget(mA, mB, state, ps)
                    val needed = budget - (ps?.totalComparisons ?: 0)
                    if (needed <= 0) return@forEach

                    val pairKey = "${node.id}|${minOf(mA, mB)}|${maxOf(mA, mB)}"
                    val offset = pairQueryOffsets.getOrDefault(pairKey, ps?.totalComparisons ?: 0)
                    val slice = available.drop(offset).take(minOf(needed, BATCH_STEP_SIZE))
                    if (slice.isEmpty()) return@forEach

                    pairQueryOffsets[pairKey] = offset + slice.size
                    tasks += BtMatchTask(
                        nodeId = node.id, modelA = mA, modelB = mB,
                        queryIds = slice.map { it.toString() },
                        priority = utility, batchId = UUID.randomUUID().toString()
                    )
                    batchModelLoad[mA] = (batchModelLoad[mA] ?: 0) + 1
                    batchModelLoad[mB] = (batchModelLoad[mB] ?: 0) + 1
                }
        }
        return tasks
    }

    private fun pairBudget(mA: String, mB: String, state: NodeBtState?, ps: NodePairStats?): Int {
        if (state == null || ps == null) return queriesPerPair
        val si = state.btScores[mA] ?: 0.0
        val sj = state.btScores[mB] ?: 0.0
        val pij = exp(si) / (exp(si) + exp(sj)).coerceAtLeast(1e-300)
        return if (abs(pij - 0.5) < closeMatchThreshold)
            (queriesPerPair * 2).coerceAtMost(budgetPerPair)
        else queriesPerPair
    }

    fun computeUtility(
        mA: String, mB: String,
        state: NodeBtState?,
        nodePairs: List<NodePairStats>,
        leafModelMatches: Map<String, Int>
    ): Double {
        if ((leafModelMatches[mA] ?: 0) == 0 || (leafModelMatches[mB] ?: 0) == 0)
            return 10000.0 + ((state?.stdErrors?.get(mA) ?: 10.0) + (state?.stdErrors?.get(mB) ?: 10.0))

        val ps = nodePairs.firstOrNull {
            (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
        }
        val nij = ps?.totalComparisons ?: 0
        if (nij < 4) return 5000.0 + (4 - nij) * 100.0

        val si = state?.btScores?.get(mA) ?: 0.0
        val sj = state?.btScores?.get(mB) ?: 0.0
        val pij = exp(si) / (exp(si) + exp(sj)).coerceAtLeast(1e-300)
        val fishInfo = pij * (1.0 - pij)   // maximised at 0.25 when p=0.5
        val seSum = ((state?.stdErrors?.get(mA) ?: 1.0).coerceAtMost(9.0)) +
                    ((state?.stdErrors?.get(mB) ?: 1.0).coerceAtMost(9.0))
        val repeatPenalty = (nij.toDouble() / budgetPerPair).coerceAtMost(1.0)

        return fishInfo * seSum - 0.1 * repeatPenalty
    }

    companion object {
        const val BATCH_STEP_SIZE = 5
    }
}
