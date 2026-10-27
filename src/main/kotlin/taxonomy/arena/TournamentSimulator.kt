package taxonomy.arena

import kotlinx.serialization.Serializable
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.model.GraphNode
import taxonomy.service.AgentRating
import taxonomy.service.LeaderboardGroup
import taxonomy.service.TaxonomyRankingService
import taxonomy.service.TaxonomyService
import java.sql.DriverManager
import kotlin.random.Random

@Serializable
data class SimulationResult(
    val matchmaking: String,
    val totalMatches: Int,
    val kendallTauHistory: List<Double>,
    val finalLeaderboard: List<LeaderboardGroup>
)

@Service
class TournamentSimulator(
    private val rankingService: TaxonomyRankingService,
    private val taxonomyService: TaxonomyService
) {
    private val log = LoggerFactory.getLogger("taxonomy.TournamentSimulator")
    private val drawMargin = 0.1

    // Predefined synthetic agent true skill profiles mapping domain categories to true mu
    // True sigma is assumed to be 0 for the ground truth comparisons.
    private val trueSkills = mapOf(
        "Model-Alpha" to mapOf(
            "math" to 36.0, "physics" to 34.0, "computer_science" to 34.0,
            "law" to 14.0, "history" to 16.0, "business" to 22.0, "economics" to 24.0, "global" to 25.7
        ),
        "Model-Beta" to mapOf(
            "math" to 14.0, "physics" to 16.0, "computer_science" to 16.0,
            "law" to 37.0, "history" to 35.0, "business" to 33.0, "economics" to 30.0, "global" to 25.9
        ),
        "Model-Gamma" to mapOf(
            "math" to 29.0, "physics" to 29.0, "computer_science" to 29.0,
            "law" to 29.0, "history" to 29.0, "business" to 29.0, "economics" to 29.0, "global" to 29.0
        ),
        "Model-Delta" to mapOf(
            "math" to 17.0, "physics" to 17.0, "computer_science" to 17.0,
            "law" to 17.0, "history" to 17.0, "business" to 17.0, "economics" to 17.0, "global" to 17.0
        ),
        "Model-Epsilon" to mapOf(
            "math" to 26.0, "physics" to 23.0, "computer_science" to 39.0,
            "law" to 21.0, "history" to 20.0, "business" to 24.0, "economics" to 25.0, "global" to 25.4
        )
    )

    private val agents = trueSkills.keys.toList()

    /**
     * Gets the true skill rating for a model, walking up the taxonomy node lineage if needed.
     */
    fun getTrueSkill(agent: String, domainLabel: String): Double {
        val agentSkills = trueSkills[agent] ?: return 25.0
        
        // Normalize label to match our predefined categories
        val normalized = domainLabel.trim().lowercase()
        
        // Direct category lookup
        agentSkills[normalized]?.let { return it }

        // Walk up parents using active DAG if loaded
        val root = taxonomyService.getGraph()
        if (root != null) {
            val matchedNode = findNodeInGraph(root, domainLabel)
            if (matchedNode != null) {
                var current: GraphNode? = matchedNode
                val visited = mutableSetOf<String>()
                while (current != null && visited.add(current.id)) {
                    val label = current.label
                    if (label != null) {
                        val labelNormalized = label.trim().lowercase()
                        agentSkills[labelNormalized]?.let { return it }
                    }
                    val treeParentId = current.treeParentId
                    current = current.parents.find { it.id == treeParentId }
                }
            }
        }

        return agentSkills["global"] ?: 25.0
    }

    private fun findNodeInGraph(root: GraphNode, label: String, visited: MutableSet<String> = mutableSetOf()): GraphNode? {
        if (root.label == label) return root
        if (!visited.add(root.id)) return null
        for (child in root.children) {
            val found = findNodeInGraph(child, label, visited)
            if (found != null) return found
        }
        return null
    }

    /**
     * Runs a simulated tournament over MMLU Pro queries.
     * @param numMatches Total number of matches to simulate.
     * @param strategy Matchmaking strategy: "ig" (Information-Gain) or "random" (Random).
     */
    suspend fun runSimulation(numMatches: Int, strategy: String = "ig"): SimulationResult {
        log.info("Starting Simulated Tournament ($numMatches matches) using '$strategy' matchmaking...")
        val rng = Random(42)
        
        // Reset ratings in database to defaults for a clean experiment run
        resetDatabaseRatings()

        val queries = loadCachedQueries(numMatches)
        if (queries.isEmpty()) {
            log.warn("MMLU Pro database cache is empty. Using generic fallback queries.")
        }

        val tauHistory = mutableListOf<Double>()
        
        // Ground truth global ranking order based on true global values
        val groundTruthGlobal = agents.sortedByDescending { trueSkills[it]?.get("global") ?: 25.0 }

        for (matchIdx in 1..numMatches) {
            // 1. Select Query and Route it to a Domain Node
            val queryText = if (queries.isNotEmpty()) queries[(matchIdx - 1) % queries.size].first else "Generic query $matchIdx"
            val categoryName = if (queries.isNotEmpty()) queries[(matchIdx - 1) % queries.size].second else "global"
            
            // Route query using trickle-routing
            val matchedDomain = routeQueryToDomain(queryText)

            // 2. Matchmaking (IG or Random)
            val (agentA, agentB) = if (strategy.lowercase() == "ig") {
                findInformationGainMatch(matchedDomain)
            } else {
                findRandomMatch(rng)
            }

            // 3. Simulate Match Outcome based on True Skills
            val skillA = getTrueSkill(agentA, matchedDomain)
            val skillB = getTrueSkill(agentB, matchedDomain)

            // Logistic probability: P(A wins) = 1 / (1 + exp(-(skillA - skillB) / 8.0))
            val pA = 1.0 / (1.0 + Math.exp(-(skillA - skillB) / 8.0))
            val rand = rng.nextDouble()
            
            val (winner, loser, isTie) = when {
                rand < pA - (drawMargin / 2.0) -> Triple(agentA, agentB, false)
                rand > pA + (drawMargin / 2.0) -> Triple(agentB, agentA, false)
                else -> Triple(agentA, agentB, true)
            }

            // 4. Record Match & Update Bayesian Ratings
            rankingService.recordMatch(queryText, matchedDomain, winner, loser, isTie)

            // 5. Measure Convergence against Ground Truth (every 10 matches)
            if (matchIdx % 10 == 0 || matchIdx == numMatches) {
                val currentGlobalLeaderboard = rankingService.getLeaderboard("global")
                    .flatMap { it.agents }
                    .map { it.agentName }
                val tau = calculateKendallsTau(groundTruthGlobal, currentGlobalLeaderboard)
                tauHistory.add(tau)
            }
        }

        val finalLeaderboard = rankingService.getLeaderboard("global")
        log.info("Tournament simulation finished. Final Kendall's Tau: ${tauHistory.lastOrNull() ?: 1.0}")
        
        return SimulationResult(strategy, numMatches, tauHistory, finalLeaderboard)
    }

    private fun resetDatabaseRatings() {
        try {
            rankingService.clearDatabaseForTest()
            agents.forEach { agent ->
                rankingService.saveRating(AgentRating(agent, "global"))
            }
        } catch (e: Exception) {
            log.error("Failed to clear ratings for simulation.", e)
        }
    }

    private fun loadCachedQueries(limit: Int): List<Pair<String, String>> {
        val list = mutableListOf<Pair<String, String>>()
        try {
            DriverManager.getConnection("jdbc:sqlite:mmlu_pro_dataset_cache_v2.db?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000").use { conn ->
                conn.prepareStatement("SELECT question, category FROM mmlu_pro ORDER BY RANDOM() LIMIT ?").use { pstmt ->
                    pstmt.setInt(1, limit)
                    val rs = pstmt.executeQuery()
                    while (rs.next()) {
                        list.add(rs.getString("question") to rs.getString("category"))
                    }
                }
            }
        } catch (e: Exception) {
            // Fallback if DB doesn't exist yet
        }
        return list
    }

    private suspend fun routeQueryToDomain(text: String): String {
        // Uses the real TaxonomyService matching route if loaded, otherwise falls back to a category name
        return try {
            val responses = taxonomyService.getGraph()?.let {
                // If taxonomy is loaded, perform a mock route
                val matched = taxonomyService.queryTaxonomy(text)
                matched.firstOrNull()?.label
            }
            responses ?: "global"
        } catch (e: Exception) {
            "global"
        }
    }

    private fun findRandomMatch(rng: Random): Pair<String, String> {
        val a = agents.random(rng)
        var b = agents.random(rng)
        while (a == b) {
            b = agents.random(rng)
        }
        return a to b
    }

    private fun findInformationGainMatch(domain: String): Pair<String, String> {
        val ordinals = agents.associateWith { rankingService.getRating(it, domain).ordinal }
        return agents.flatMap { a -> agents.map { b -> Pair(a, b) } }
            .filter { (a, b) -> a < b }
            .minByOrNull { (a, b) ->
                -calculateMatchQuality(
                    rankingService.getRating(a, domain),
                    rankingService.getRating(b, domain)
                )
            }!!
    }

    private fun calculateMatchQuality(ratingA: AgentRating, ratingB: AgentRating, gamma: Double = 4.167): Double {
        val varA = ratingA.sigma * ratingA.sigma
        val varB = ratingB.sigma * ratingB.sigma
        val totalVar = varA + varB + 2.0 * gamma * gamma
        val diff = ratingA.mu - ratingB.mu
        
        val exponent = - (diff * diff) / (2.0 * totalVar)
        val factor = Math.sqrt(2.0 * gamma * gamma / totalVar)
        
        return Math.exp(exponent) * factor
    }

    private fun calculateKendallsTau(trueOrder: List<String>, estimatedOrder: List<String>): Double {
        val estimatedIndex = estimatedOrder.mapIndexed { idx, name -> name to idx }.toMap()
        val trueIndex = trueOrder.mapIndexed { idx, name -> name to idx }.toMap()
        
        val common = trueOrder.filter { it in estimatedIndex }
        if (common.size < 2) return 1.0
        
        var concordant = 0
        var discordant = 0
        
        for (i in 0 until common.size) {
            for (j in i + 1 until common.size) {
                val u = common[i]
                val v = common[j]
                
                val trueSign = Math.signum((trueIndex[u] ?: 0) - (trueIndex[v] ?: 0).toDouble())
                val estSign = Math.signum((estimatedIndex[u] ?: 0) - (estimatedIndex[v] ?: 0).toDouble())
                
                if (trueSign == estSign) {
                    concordant++
                } else {
                    discordant++
                }
            }
        }
        
        val total = concordant + discordant
        if (total == 0) return 1.0
        return (concordant - discordant).toDouble() / total
    }
}
