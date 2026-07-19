package taxonomy.service

import taxonomy.model.*
import taxonomy.dataset.ModelEvalResult
import java.util.UUID

/**
 * Uniform random active leaf + uniform random unresolved pair + uniform random
 * unused query. No informativeness filter, no adaptive redistribution, no resolve
 * logic except hard budget/query exhaustion.
 */
class RandomTournamentScheduler(
    private val seed: Long = 42L
) {
    private val rng = java.util.Random(seed)

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
            val leafArena = LeafArena(leafId, models, queryIds, emptyMap(), budgetPerPair)

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
                stats.n = ps.totalComparisons
            }

            leafArena
        }

        val tasks = ArrayList<BtMatchTask>()
        while (tasks.size < batchSize) {
            val active = arenas.filter { it.state == LeafState.ACTIVE }
            if (active.isEmpty()) break
            val leaf = active[rng.nextInt(active.size)]
            val unresolved = leaf.pairs.filter { p ->
                leaf.pairExhausted[p] != true &&
                    (leaf.stats[p]?.n ?: 0) < leaf.pairBudget
            }
            if (unresolved.isEmpty()) {
                leaf.state = LeafState.EXHAUSTED
                continue
            }
            val key = unresolved[rng.nextInt(unresolved.size)]
            val usable = leaf.queryIds.filter { it !in leaf.used(key) }
            if (usable.isEmpty()) {
                leaf.pairExhausted[key] = true
                continue
            }
            val q = usable[rng.nextInt(usable.size)]
            leaf.reserved.getOrPut(key) { hashSetOf() }.add(q)
            tasks.add(
                BtMatchTask(
                    nodeId = leaf.leafId,
                    modelA = key.first,
                    modelB = key.second,
                    queryIds = listOf(q.toString()),
                    priority = 1.0,
                    batchId = UUID.randomUUID().toString()
                )
            )
        }
        return tasks
    }
}
