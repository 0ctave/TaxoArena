package taxonomy.service

import taxonomy.model.NodeBtState

class BtStoppingPolicy(
    val minComparisons: Int = 30,
    val stabilityRounds: Int = 3,
    val separationThreshold: Double = 2.0,
    val maxRounds: Int = 20
) {
    private val rankHistoryByNode = mutableMapOf<String, MutableList<List<String>>>()

    fun shouldStop(
        btStates: Map<String, NodeBtState>,
        round: Int,
        rootNodeId: String
    ): Boolean {
        if (round >= maxRounds) return true

        // 1. Root node rank is stable across last N rounds
        val rootState = btStates[rootNodeId] ?: return false
        if (rootState.totalComparisons < minComparisons) return false

        val rootHistory = rankHistoryByNode.getOrPut(rootNodeId) { mutableListOf() }
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

        return false
    }
}
