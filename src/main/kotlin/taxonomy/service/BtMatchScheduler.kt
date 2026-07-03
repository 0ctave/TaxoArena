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

    // Returns a flat priority queue of all schedulable (leaf, mA, mB) triples
    private fun buildQueue(
        targetNodes: List<GraphNode>,
        btStates: Map<String, NodeBtState>,
        pairStats: Map<String, List<NodePairStats>>,
        models: List<String>,
        leafModelMatches: Map<String, Map<String, Int>>
    ): PriorityQueue<MatchCandidate> {
        // Max-heap: highest utility first
        val queue = PriorityQueue<MatchCandidate>(compareByDescending { it.utility })

        for (node in targetNodes) {
            // Converged leaves contribute no utility — skip entirely
            if (stoppingPolicy.isLeafConverged(node.id, btStates, pairStats, models)) continue

            val state = btStates[node.id]
            val nodePairs = pairStats[node.id] ?: emptyList()
            val leafMatches = leafModelMatches[node.id] ?: emptyMap()

            val candidates = models.flatMapIndexed { i, mA -> models.drop(i + 1).map { mB -> mA to mB } }
            for ((mA, mB) in candidates) {
                val ps = nodePairs.firstOrNull {
                    (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
                }
                val budget = pairBudget(mA, mB, state, ps)
                val already = ps?.totalComparisons ?: 0
                if (already >= budget) continue  // exhausted

                val u = computeEntropy(mA, mB, state, leafMatches, already)
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
        // Leaf-local match counts (leaf-local, not cross-leaf)
        val leafModelMatches = targetNodes.associate { node ->
            node.id to models.associateWith { model ->
                (pairStats[node.id] ?: emptyList())
                    .filter { it.modelA == model || it.modelB == model }
                    .sumOf { it.totalComparisons }
            }
        }

        val queue = buildQueue(targetNodes, btStates, pairStats, models, leafModelMatches)

        val tasks = mutableListOf<BtMatchTask>()
        // Per-node model load: a model should appear at most once per leaf per batch
        val nodeModelLoad = mutableMapOf<String, MutableMap<String, Int>>()
        // Global: a model should not dominate the entire batch
        val globalModelLoad = mutableMapOf<String, Int>()
        val globalModelCap = targetNodes.size  // can appear on every leaf once

        while (tasks.size < batchSize && queue.isNotEmpty()) {
            val candidate = queue.poll()!!
            val (nodeId, mA, mB) = Triple(candidate.nodeId, candidate.modelA, candidate.modelB)

            // Per-node cap: each model appears at most once per leaf per batch
            val nodeLoad = nodeModelLoad.getOrPut(nodeId) { mutableMapOf() }
            if ((nodeLoad[mA] ?: 0) >= 1) continue
            if ((nodeLoad[mB] ?: 0) >= 1) continue

            // Global cap: prevents one model from eating the whole batch
            if ((globalModelLoad[mA] ?: 0) >= globalModelCap) continue
            if ((globalModelLoad[mB] ?: 0) >= globalModelCap) continue

            // Find the next unseen query slice for this pair
            val nodeQueryIds = (nodeToQueries[nodeId] ?: emptyList()).sorted()
            val available = resultsMatrix.keys.intersect(nodeQueryIds.toSet()).sorted()
            if (available.isEmpty()) continue

            val offset = pairQueryOffsets.getOrDefault(candidate.pairKey,
                (pairStats[nodeId]?.firstOrNull {
                    (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
                }?.totalComparisons ?: 0))

            val slice = available.drop(offset).take(BATCH_STEP_SIZE)
            if (slice.isEmpty()) continue

            pairQueryOffsets[candidate.pairKey] = offset + slice.size

            tasks += BtMatchTask(
                nodeId = nodeId, modelA = mA, modelB = mB,
                queryIds = slice.map { it.toString() },
                priority = candidate.utility,
                batchId = UUID.randomUUID().toString()
            )
            nodeLoad[mA] = (nodeLoad[mA] ?: 0) + 1
            nodeLoad[mB] = (nodeLoad[mB] ?: 0) + 1
            globalModelLoad[mA] = (globalModelLoad[mA] ?: 0) + 1
            globalModelLoad[mB] = (globalModelLoad[mB] ?: 0) + 1
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
