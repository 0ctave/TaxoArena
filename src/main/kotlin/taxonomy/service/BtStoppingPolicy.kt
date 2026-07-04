package taxonomy.service

import taxonomy.model.NodeBtState
import taxonomy.model.NodePairStats
import kotlin.math.abs

class BtStoppingPolicy(
    val maxRounds: Int = 20,
    val minComparisonsPerLeaf: Int = 8,
    val targetLeafConvergenceFraction: Double = 0.70,
    val stabilityRounds: Int = 3,
    val separationThreshold: Double = 1.5,
    val minTotalComparisons: Int = 20,
    val budgetPerPair: Int = 18
) {
    private val leafRankHistory = mutableMapOf<String, ArrayDeque<List<String>>>()

    // PUBLIC — called by both shouldStop() and BtMatchScheduler
    fun isLeafConverged(
        nodeId: String,
        btStates: Map<String, NodeBtState>,
        pairStats: Map<String, List<NodePairStats>>,
        models: List<String>,
        nodeToQueries: Map<String, List<Int>> = emptyMap()
    ): Boolean {
        val state = btStates[nodeId] ?: return false

        val numPairs = models.size * (models.size - 1) / 2
        val available = nodeToQueries[nodeId]?.size ?: 0
        val maxPossible = if (available > 0) available * numPairs else 0
        val targetLimit = if (maxPossible > 0) {
            minOf(budgetPerPair * numPairs / 2, (maxPossible * 0.9).toInt())
        } else {
            budgetPerPair * numPairs / 2
        }

        val dataExhausted = state.totalComparisons >= targetLimit
        if (dataExhausted) return true

        if (state.totalComparisons < minComparisonsPerLeaf) return false

        val allPairs = models.flatMapIndexed { i, mA -> models.drop(i + 1).map { mB -> mA to mB } }

        val informativePairs = allPairs.filter { (mA, mB) ->
            val ps = (pairStats[nodeId] ?: emptyList()).firstOrNull {
                (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
            }
            val nij = ps?.totalComparisons ?: 0
            if (nij < 2) return@filter true  // bootstrap not done -> still informative
            val si = state.btScores[mA] ?: 0.0
            val sj = state.btScores[mB] ?: 0.0
            val seA = state.stdErrors[mA] ?: 10.0
            val seB = state.stdErrors[mB] ?: 10.0
            abs(si - sj) < 3.0 * (seA + seB)
        }

        // All remaining informative pairs resolved -> leaf is done
        if (informativePairs.isEmpty()) return true

        // Coverage check only on informative pairs
        val minPerPair = (minComparisonsPerLeaf / models.size).coerceAtLeast(1)
        val informativePairsCovered = informativePairs.all { (mA, mB) ->
            val ps = (pairStats[nodeId] ?: emptyList()).firstOrNull {
                (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
            }
            (ps?.totalComparisons ?: 0) >= minPerPair
        }
        if (!informativePairsCovered) return false

        // Top-2 separation
        val ranked = state.btScores.entries.sortedByDescending { it.value }
        if (ranked.size < 2) return true
        val gap = ranked[0].value - ranked[1].value
        val combinedSE = (state.stdErrors[ranked[0].key] ?: 10.0) +
                         (state.stdErrors[ranked[1].key] ?: 10.0)
        return gap > separationThreshold * combinedSE
    }

    fun shouldStop(
        btStates: Map<String, NodeBtState>,
        pairStats: Map<String, List<NodePairStats>>,
        targetLeafIds: Set<String>,
        models: List<String>,
        round: Int,
        totalComparisons: Int,
        nodeToQueries: Map<String, List<Int>> = emptyMap()
    ): Boolean {
        if (round >= maxRounds) return true
        if (totalComparisons < minTotalComparisons) return false
        if (targetLeafIds.isEmpty()) return false

        var converged = 0
        for (leafId in targetLeafIds) {
            val state = btStates[leafId] ?: continue

            // Rank stability check
            val currentRank = state.btScores.entries.sortedByDescending { it.value }.map { it.key }
            val history = leafRankHistory.getOrPut(leafId) { ArrayDeque() }
            history.addLast(currentRank)
            if (history.size > stabilityRounds) history.removeFirst()

            val rankStable = history.size >= stabilityRounds && history.all { it == currentRank }
            val structurallyConverged = isLeafConverged(leafId, btStates, pairStats, models, nodeToQueries)

            if (rankStable && structurallyConverged) converged++
        }

        return converged.toDouble() / targetLeafIds.size >= targetLeafConvergenceFraction
    }
}
