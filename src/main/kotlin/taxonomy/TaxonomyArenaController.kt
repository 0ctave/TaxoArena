package org.eclipse.lmos.arc.app.taxonomy

import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.Json
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/taxonomy/arena")
class TaxonomyArenaController(
    private val arenaService: TaxonomyArenaService,
    private val rankingService: TaxonomyRankingService,
    private val tournamentSimulator: TournamentSimulator
) {

    @PostMapping("/compare")
    fun compareModels(@RequestBody request: ArenaRequest): ArenaResult = runBlocking {
        val result = arenaService.compareModels(request.query, request.modelA, request.modelB)
        
        // Propagate result to ranking service if there is a clear outcome
        val topDomain = result.domainEvaluations.firstOrNull()
        if (topDomain != null && topDomain.winner != "Tie") {
            val winner = if (topDomain.winner == "Model A") request.modelA else request.modelB
            val loser = if (topDomain.winner == "Model A") request.modelB else request.modelA
            rankingService.recordMatch(request.query, topDomain.domainLabel, winner, loser, false)
        } else if (topDomain != null) {
            rankingService.recordMatch(request.query, topDomain.domainLabel, request.modelA, request.modelB, true)
        }
        
        result
    }

    @GetMapping("/leaderboard")
    fun getLeaderboard(@RequestParam(defaultValue = "global") domain: String): List<LeaderboardGroup> {
        return rankingService.getLeaderboard(domain)
    }

    @GetMapping("/rating")
    fun getRating(@RequestParam agent: String, @RequestParam(defaultValue = "global") domain: String): AgentRating {
        return rankingService.getRating(agent, domain)
    }

    @PostMapping("/simulate")
    fun runSimulation(
        @RequestParam(defaultValue = "100") numMatches: Int,
        @RequestParam(defaultValue = "ig") strategy: String
    ): SimulationResult = runBlocking {
        tournamentSimulator.runSimulation(numMatches, strategy)
    }

    @GetMapping("/test-queries")
    fun getTestQueries(): Map<String, List<String>> {
        val file = java.io.File("reserved_test_queries.json")
        if (!file.exists()) {
            return emptyMap()
        }
        return try {
            val content = file.readText()
            Json.decodeFromString<Map<String, List<String>>>(content)
        } catch (e: Exception) {
            emptyMap()
        }
    }
}

data class ArenaRequest(
    val query: String,
    val modelA: String,
    val modelB: String
)
