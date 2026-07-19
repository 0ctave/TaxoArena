package taxonomy

import taxonomy.arena.*
import taxonomy.model.*
import taxonomy.service.*

import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import java.sql.DriverManager

@SpringBootTest(
    classes = [org.eclipse.lmos.arc.app.TaxoAdaptApplication::class],
    properties = [
        "taxoadapt.execution.enable-tui=false",
        "taxoadapt.execution.run-batch=false",
        "taxoadapt.execution.start-service=false"
    ]
)
@org.springframework.test.annotation.DirtiesContext
class TournamentSimulatorTest {

    companion object {
        private lateinit var tmpDir: java.io.File

        @org.junit.jupiter.api.BeforeAll
        @JvmStatic
        fun beforeAll() {
            tmpDir = java.nio.file.Files.createTempDirectory("tournament-sim-test").toFile()
            System.setProperty("ranking.db.path", java.io.File(tmpDir, "ratings.db").absolutePath)
        }

        @org.junit.jupiter.api.AfterAll
        @JvmStatic
        fun afterAll() {
            System.clearProperty("ranking.db.path")
        }
    }

    @Autowired
    private lateinit var rankingService: TaxonomyRankingService

    @Autowired
    private lateinit var taxonomyService: TaxonomyService

    @Autowired
    private lateinit var tournamentSimulator: TournamentSimulator

    @BeforeEach
    fun setUp() {
        rankingService.clearDatabaseForTest()
        taxonomyService.setGraph(null)
    }

    @Test
    fun testSimulatedTournamentExecution() = runBlocking {
        // Run a simulation of 30 matches using Information-Gain matchmaking
        val result = tournamentSimulator.runSimulation(30, "ig")

        // Assertions
        assertEquals("ig", result.matchmaking)
        assertEquals(30, result.totalMatches)
        assertFalse(result.kendallTauHistory.isEmpty())
        assertFalse(result.finalLeaderboard.isEmpty())

        // The final leaderboard should contain our 5 synthetic agents (Model-Alpha, Model-Beta, etc.)
        val rankedAgents = result.finalLeaderboard.flatMap { it.agents }.map { it.agentName }
        assertEquals(5, rankedAgents.distinct().size)
        assertTrue(rankedAgents.contains("Model-Alpha"))
        assertTrue(rankedAgents.contains("Model-Beta"))
        assertTrue(rankedAgents.contains("Model-Gamma"))
        assertTrue(rankedAgents.contains("Model-Delta"))
        assertTrue(rankedAgents.contains("Model-Epsilon"))

        // Ratings should have evolved away from the default 25.0 mu / 8.333 sigma values
        val ratingAlpha = rankingService.getRating("Model-Alpha", "global")
        println("DEBUG: ratingAlpha mu=${ratingAlpha.mu}, sigma=${ratingAlpha.sigma}")
        assertTrue(ratingAlpha.sigma < 8.333)
    }

    @Test
    fun testRandomMatchmakingSimulatedTournament() = runBlocking {
        // Run a simulation of 30 matches using Random matchmaking
        val result = tournamentSimulator.runSimulation(30, "random")

        assertEquals("random", result.matchmaking)
        assertEquals(30, result.totalMatches)
        assertFalse(result.kendallTauHistory.isEmpty())
    }

    @Test
    fun testTrueSkillLineagePropagation() {
        // Build a mock taxonomy tree:
        // Root (MMLU Universal Knowledge) -> Business -> Valuation and Rate Analysis
        val root = GraphNode(label = "MMLU Universal Knowledge", depth = 0)
        val businessNode = GraphNode(label = "Business", depth = 1)
        val valuationNode = GraphNode(label = "Valuation and Rate Analysis", depth = 2)

        root.children.add(businessNode)
        businessNode.parents.add(root)
        businessNode.treeParentId = root.id
        businessNode.children.add(valuationNode)
        valuationNode.parents.add(businessNode)
        valuationNode.treeParentId = businessNode.id

        taxonomyService.setGraph(root)

        // Look up true skill for "Model-Alpha" in "Valuation and Rate Analysis"
        // There is no direct match for "valuation_and_rate_analysis" in trueSkills,
        // but its parent "Business" is predefined in trueSkills mapping to "business" -> 22.0.
        // It should walk up the parents to find "Business" and return 22.0!
        val trueSkillValuation = tournamentSimulator.getTrueSkill("Model-Alpha", "Valuation and Rate Analysis")
        assertEquals(22.0, trueSkillValuation)

        // Look up true skill for "Model-Alpha" in "MMLU Universal Knowledge"
        // It should fallback to the global default 25.7 since "mmlu_universal_knowledge" is not predefined
        val trueSkillRoot = tournamentSimulator.getTrueSkill("Model-Alpha", "MMLU Universal Knowledge")
        assertEquals(25.7, trueSkillRoot)
    }
}
