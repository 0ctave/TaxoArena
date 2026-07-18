package taxonomy.service

import taxonomy.model.NodeBtState
import taxonomy.model.NodePairStats
import kotlin.math.abs

class BtStoppingPolicy(
    val maxRounds: Int = 20,
    val minComparisonsPerLeaf: Int = 8,
    val targetLeafConvergenceFraction: Double = 0.65,
    val stabilityRounds: Int = 2,
    val separationThreshold: Double = 1.0,
    val minTotalComparisons: Int = 20,
    val budgetPerPair: Int
) {
    private val leafRankHistory = mutableMapOf<String, ArrayDeque<List<String>>>()
    val globallyResolvedPairs = mutableSetOf<String>()
    val pairCustomBudgets = mutableMapOf<String, Int>()

    // PUBLIC — called by both shouldStop() and BtMatchScheduler
    fun isLeafConverged(
        nodeId: String,
        btStates: Map<String, NodeBtState>,
        pairStats: Map<String, List<NodePairStats>>,
        models: List<String>,
        nodeToQueries: Map<String, List<Int>> = emptyMap(),
        condition: String = "MAIN"
    ): Boolean {
        val numPairs = models.size * (models.size - 1) / 2
        val available = nodeToQueries[nodeId]?.size ?: 0
        val maxPossible = if (available > 0) available * numPairs else 0

        if (condition.equals("ROUND_ROBIN", ignoreCase = true) || condition.equals("RANDOM_SCHEDULER", ignoreCase = true)) {
            val liveTotalComparisons = (pairStats[nodeId] ?: emptyList()).sumOf { it.totalComparisons }
            return liveTotalComparisons >= maxPossible
        }

        val state = btStates[nodeId] ?: return false

        val targetLimit = if (maxPossible > 0) {
            maxOf(1, minOf(kotlin.math.ceil(budgetPerPair.toDouble() * numPairs / 2.0).toInt(), (maxPossible * 0.9).toInt()))
        } else {
            maxOf(1, kotlin.math.ceil(budgetPerPair.toDouble() * numPairs / 2.0).toInt())
        }

        val liveTotalComparisons = (pairStats[nodeId] ?: emptyList()).sumOf { it.totalComparisons }
        val dataExhausted = liveTotalComparisons >= targetLimit
        if (dataExhausted) return true

        if (liveTotalComparisons < minComparisonsPerLeaf) return false

        val allPairs = models.flatMapIndexed { i, mA -> models.drop(i + 1).map { mB -> mA to mB } }
        val informativePairs = allPairs.filter { (mA, mB) ->
            val pairKey = "${minOf(mA, mB)}|${maxOf(mA, mB)}"
            if (globallyResolvedPairs.contains(pairKey)) return@filter false

            val ps = (pairStats[nodeId] ?: emptyList()).firstOrNull {
                (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
            }
            val nij = ps?.totalComparisons ?: 0
            if (nij < 2) return@filter true  // bootstrap not done -> still informative

            // NEW: if this pair has exhausted its budget, it's resolved regardless of gap
            val budget = pairCustomBudgets.getOrDefault("${nodeId}|$pairKey", budgetPerPair).coerceAtLeast(1)
            if (nij >= budget) return@filter false  // budget-exhausted → accepted as resolved

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
        nodeToQueries: Map<String, List<Int>> = emptyMap(),
        condition: String = "MAIN",
        mainConditionTotalComparisons: Int = 72
    ): Boolean {
        if (condition.equals("RANDOM_SCHEDULER", ignoreCase = true)) {
            return totalComparisons >= mainConditionTotalComparisons
        }
        if (round >= maxRounds) return true
        if (condition.equals("ROUND_ROBIN", ignoreCase = true)) return false
        if (totalComparisons < minTotalComparisons) return false
        if (targetLeafIds.isEmpty()) return false

        if (round >= maxRounds - 3) {
            // Last 3 rounds: stop if at least 50% are structurally converged
            // (even without rank stability) — prevents infinite runs
            val structConv = targetLeafIds.count { leafId ->
                isLeafConverged(leafId, btStates, pairStats, models, nodeToQueries, condition)
            }
            if (structConv.toDouble() / targetLeafIds.size >= 0.50) return true
        }

        val totalWeight = targetLeafIds.sumOf { leafId ->
            (nodeToQueries[leafId]?.size ?: 1).toDouble()
        }
        var weightedConverged = 0.0
        for (leafId in targetLeafIds) {
            val state = btStates[leafId] ?: continue

            // Rank stability check
            val currentRank = state.btScores.entries.sortedByDescending { it.value }.map { it.key }
            val history = leafRankHistory.getOrPut(leafId) { ArrayDeque() }
            history.addLast(currentRank)
            if (history.size > stabilityRounds) history.removeFirst()

            val rankStable = history.size >= stabilityRounds && history.all { it == currentRank }
            val structurallyConverged = isLeafConverged(leafId, btStates, pairStats, models, nodeToQueries, condition)

            val allPairs = models.flatMapIndexed { i, mA -> models.drop(i + 1).map { mB -> mA to mB } }
            // NEW: irresolvable-only leaf — rank noise from tie pairs should not block
            val allPairsResolved = allPairs.all { (mA, mB) ->
                val pk = "${minOf(mA, mB)}|${maxOf(mA, mB)}"
                globallyResolvedPairs.contains(pk) ||
                (pairStats[leafId] ?: emptyList()).firstOrNull {
                    (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
                }?.let { ps ->
                    ps.totalComparisons >= pairCustomBudgets.getOrDefault("$leafId|$pk", budgetPerPair)
                } ?: false
            }

            val leafWeight = (nodeToQueries[leafId]?.size ?: 1).toDouble()
            if ((rankStable || allPairsResolved) && structurallyConverged) {
                weightedConverged += leafWeight
            }
        }

        return if (totalWeight > 0.0) weightedConverged / totalWeight >= targetLeafConvergenceFraction else false
    }
}
