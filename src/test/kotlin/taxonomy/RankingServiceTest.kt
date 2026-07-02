package taxonomy

import taxonomy.service.*

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import java.sql.DriverManager

class RankingServiceTest {

    private lateinit var rankingService: TaxonomyRankingService

    @BeforeEach
    fun setUp() {
        rankingService = TaxonomyRankingService()
        rankingService.clearDatabaseForTest()
    }

    @Test
    fun testInitialRating() {
        val rating = rankingService.getRating("Agent-A", "math")
        assertEquals(25.0, rating.mu, 0.01)
        assertEquals(8.333, rating.sigma, 0.01)
        assertEquals(25.0 - 2.0 * 8.333, rating.ordinal, 0.01)
    }

    @Test
    fun testPairwiseMatchUpdate() {
        // Record a match where Agent-A wins against Agent-B
        rankingService.recordMatch("What is 2+2?", "math", "Agent-A", "Agent-B", false)

        val ratingA = rankingService.getRating("Agent-A", "math")
        val ratingB = rankingService.getRating("Agent-B", "math")

        // Agent-A should have higher mu than Agent-B, and their uncertainties (sigma) should have decreased
        assertTrue(ratingA.mu > 25.0)
        assertTrue(ratingB.mu < 25.0)
        assertTrue(ratingA.sigma < 8.333)
        assertTrue(ratingB.sigma < 8.333)
    }

    @Test
    fun testTarjanSccAndTopologicalSort() {
        // We will simulate a cyclic preference loop:
        // Agent-A dominates Agent-B
        // Agent-B dominates Agent-C
        // Agent-C dominates Agent-A
        // Agent-D is dominated by Agent-C (no cycle for D)

        // Agent-A vs Agent-B (Agent-A wins 2 times, Agent-B wins 0)
        rankingService.recordMatch("q1", "global", "Agent-A", "Agent-B", false)
        rankingService.recordMatch("q2", "global", "Agent-A", "Agent-B", false)

        // Agent-B vs Agent-C (Agent-B wins 2 times, Agent-C wins 0)
        rankingService.recordMatch("q3", "global", "Agent-B", "Agent-C", false)
        rankingService.recordMatch("q4", "global", "Agent-B", "Agent-C", false)

        // Agent-C vs Agent-A (Agent-C wins 2 times, Agent-A wins 0)
        rankingService.recordMatch("q5", "global", "Agent-C", "Agent-A", false)
        rankingService.recordMatch("q6", "global", "Agent-C", "Agent-A", false)

        // Agent-C vs Agent-D (Agent-C wins 2 times, Agent-D wins 0)
        rankingService.recordMatch("q7", "global", "Agent-C", "Agent-D", false)
        rankingService.recordMatch("q8", "global", "Agent-C", "Agent-D", false)

        val leaderboard = rankingService.getLeaderboard("global")
        
        // Assert that we have leaderboard groups
        assertFalse(leaderboard.isEmpty())

        // Group 1 (best) should contain Agent-A, Agent-B, and Agent-C (collapsed due to cyclic loop)
        val firstGroup = leaderboard.first()
        val firstGroupNames = firstGroup.agents.map { it.agentName }
        assertEquals(3, firstGroupNames.size)
        assertTrue(firstGroupNames.contains("Agent-A"))
        assertTrue(firstGroupNames.contains("Agent-B"))
        assertTrue(firstGroupNames.contains("Agent-C"))
        assertEquals(1, firstGroup.rank)

        // Group 2 should contain Agent-D (which is dominated by Agent-C and has no cycle)
        val secondGroup = leaderboard.last()
        val secondGroupNames = secondGroup.agents.map { it.agentName }
        assertEquals(1, secondGroupNames.size)
        assertTrue(secondGroupNames.contains("Agent-D"))
        assertEquals(4, secondGroup.rank) // 1 + 3 members from previous group
    }
}
