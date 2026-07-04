package taxonomy.controller

import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.Json
import org.springframework.web.bind.annotation.*
import taxonomy.service.AgentRating
import taxonomy.service.LeaderboardGroup
import taxonomy.arena.SimulationResult
import taxonomy.service.TaxonomyRankingService
import taxonomy.arena.TournamentSimulator
import taxonomy.model.BenchmarkReport
import taxonomy.model.BenchmarkRequest
import taxonomy.service.ArenaResult
import taxonomy.service.TaxonomyBenchmarkService
import taxonomy.service.TaxonomyArenaService
import java.io.File

@RestController
@RequestMapping("/api/taxonomy/arena")
class TaxonomyArenaController(
    private val arenaService: TaxonomyArenaService,
    private val rankingService: TaxonomyRankingService,
    private val tournamentSimulator: TournamentSimulator,
    private val benchmarkService: TaxonomyBenchmarkService
) {

    @PostMapping("/benchmark")
    suspend fun runBenchmark(@RequestBody req: BenchmarkRequest): BenchmarkReport {
        return benchmarkService.runBenchmark(req)
    }

    @PostMapping("/compare")
    suspend fun compareModels(@RequestBody request: ArenaRequest): ArenaResult {
        val result = arenaService.compareModels(request.query, request.modelA, request.modelB)
        
        // Propagate result to ranking service for all matched domains passing the confidence gate
        result.domainEvaluations.forEach { eval ->
            if (eval.confidence >= 0.65) {
                val winner = when (eval.winner) {
                    "Model A" -> request.modelA
                    "Model B" -> request.modelB
                    else -> "Tie"
                }
                val loser = when (eval.winner) {
                    "Model A" -> request.modelB
                    "Model B" -> request.modelA
                    else -> "Tie"
                }
                val isDraw = winner == "Tie"
                
                rankingService.recordMatch(
                    query = request.query,
                    domain = eval.domainLabel,
                    winner = if (isDraw) request.modelA else winner,
                    loser = if (isDraw) request.modelB else loser,
                    isTie = isDraw,
                    confidence = eval.confidence
                )
            }
        }
        
        return result
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
    suspend fun runSimulation(
        @RequestParam(defaultValue = "100") numMatches: Int,
        @RequestParam(defaultValue = "ig") strategy: String
    ): SimulationResult {
        return tournamentSimulator.runSimulation(numMatches, strategy)
    }

    @GetMapping("/test-queries")
    fun getTestQueries(): Map<String, List<String>> {
        val file = File("reserved_test_queries.json")
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
