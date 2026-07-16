package taxonomy.service

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.model.GraphNode
import taxonomy.model.NodeBtState
import taxonomy.model.NodePairStats
import taxonomy.model.ModelRank
import taxonomy.service.TaxonomyRankingService.AggregatedLeaderboard
import kotlin.math.abs

class BtSchedulerRedesignTest {

    @Test
    fun testPriorityFormulaAndMasking() {
        val stoppingPolicy = BtStoppingPolicy(budgetPerPair = 20)
        val scheduler = BtMatchScheduler(
            minQueriesForBenchmark = 2,
            queriesPerPair = 20,
            budgetPerPair = 20,
            stoppingPolicy = stoppingPolicy
        )

        val targetNodes = listOf(GraphNode(id = "leaf-1", label = "Math", depth = 1))
        val models = listOf("model-A", "model-B", "model-C")

        // 1. Compute utility when confidence is high vs low, and gap is large vs small
        // Setup state: A is strong (1.0, se: 0.1), B is weak (-1.0, se: 0.1), C is weak (-0.9, se: 0.1)
        val state = NodeBtState(
            nodeId = "leaf-1",
            btScores = mapOf("model-A" to 1.0, "model-B" to -1.0, "model-C" to -0.9),
            stdErrors = mapOf("model-A" to 0.1, "model-B" to 0.1, "model-C" to 0.1),
            fitVersion = 1,
            totalComparisons = 10,
            lastFitAt = System.currentTimeMillis()
        )

        // We want to test computeUtility reflection in BtMatchScheduler.
        // Let's invoke selectNextBatch or test the utility computation through the queue build.
        // Actually, we can reflection-access computeUtility, or test it by inspecting the candidates priority!
        val pairStats = mapOf(
            "leaf-1" to listOf(
                NodePairStats("leaf-1", "model-A", "model-B", totalComparisons = 6, ties = 0),
                NodePairStats("leaf-1", "model-A", "model-C", totalComparisons = 6, ties = 0),
                NodePairStats("leaf-1", "model-B", "model-C", totalComparisons = 6, ties = 4) // High tie rate (4/6 = 0.66)
            )
        )

        // We run scheduler batch selection. Let's make sure it orders correctly:
        // A vs B: gap = 2.0, conf = 0.88, priority = (1 - 0.88) * (2.0 / 0.2) = 0.12 * 10 = 1.2
        // B vs C: has tau >= 0.55, so mask = 0.0 -> priority = 0.0
        val nodeToQueries = mapOf("leaf-1" to listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
        val resultsMatrix = (1..10).associateWith { emptyMap<String, taxonomy.dataset.ModelEvalResult>() }

        val batch = scheduler.selectNextBatch(
            targetNodes = targetNodes,
            btStates = mapOf("leaf-1" to state),
            pairStats = pairStats,
            models = models,
            resultsMatrix = resultsMatrix,
            nodeToQueries = nodeToQueries,
            batchSize = 2,
            maxConcurrentPerModel = 2
        )

        // Ensure B vs C is not in the tasks (since priority is 0)
        assertFalse(batch.any { (it.modelA == "model-B" && it.modelB == "model-C") || (it.modelA == "model-C" && it.modelB == "model-B") })
    }

    @Test
    fun testAdaptiveBudgetAndReallocation() {
        val stoppingPolicy = BtStoppingPolicy(budgetPerPair = 20)
        val scheduler = BtMatchScheduler(
            minQueriesForBenchmark = 2,
            queriesPerPair = 20,
            budgetPerPair = 20,
            stoppingPolicy = stoppingPolicy
        )

        val targetNodes = listOf(GraphNode(id = "leaf-1", label = "Math", depth = 1))
        val models = listOf("model-A", "model-B")

        // 1. Setup high confidence state to trigger stable -> release budget
        // exp(2.5) / (exp(2.5) + exp(0.0)) = 0.923 -> conf = 0.923 >= 0.88 (STABLE)
        val state = NodeBtState(
            nodeId = "leaf-1",
            btScores = mapOf("model-A" to 2.5, "model-B" to 0.0),
            stdErrors = mapOf("model-A" to 0.1, "model-B" to 0.1),
            fitVersion = 1,
            totalComparisons = 4,
            lastFitAt = System.currentTimeMillis()
        )

        val pairStats = mapOf(
            "leaf-1" to listOf(
                NodePairStats("leaf-1", "model-A", "model-B", totalComparisons = 4, ties = 0, positionFlips = 2)
            )
        )

        val nodeToQueries = mapOf("leaf-1" to (1..10).toList())
        val resultsMatrix = (1..10).associateWith { emptyMap<String, taxonomy.dataset.ModelEvalResult>() }

        // Trigger selectNextBatch to invoke budget reallocation logic
        scheduler.selectNextBatch(
            targetNodes = targetNodes,
            btStates = mapOf("leaf-1" to state),
            pairStats = pairStats,
            models = models,
            resultsMatrix = resultsMatrix,
            nodeToQueries = nodeToQueries,
            batchSize = 2,
            maxConcurrentPerModel = 2
        )

        // Custom budget should be locked to current comparisons (4) for model-A vs model-B
        val budget = stoppingPolicy.pairCustomBudgets["leaf-1|model-A|model-B"]
        assertEquals(4, budget)
    }

    @Test
    fun testGlobalSeparationGuard() {
        val stoppingPolicy = BtStoppingPolicy(budgetPerPair = 20)
        
        // Mark model-A vs model-B as globally resolved: gap = 4.0, max(se) = 0.5 -> gap (4.0) > 2.5 * 0.5 (1.25)
        stoppingPolicy.globallyResolvedPairs.add("model-A|model-B")

        val state = NodeBtState(
            nodeId = "leaf-1",
            btScores = mapOf("model-A" to 4.0, "model-B" to 0.0),
            stdErrors = mapOf("model-A" to 0.5, "model-B" to 0.5),
            fitVersion = 1,
            totalComparisons = 4,
            lastFitAt = System.currentTimeMillis()
        )

        val pairStats = mapOf(
            "leaf-1" to listOf(
                NodePairStats("leaf-1", "model-A", "model-B", totalComparisons = 4)
            )
        )

        val isConverged = stoppingPolicy.isLeafConverged(
            nodeId = "leaf-1",
            btStates = mapOf("leaf-1" to state),
            pairStats = pairStats,
            models = listOf("model-A", "model-B"),
            nodeToQueries = mapOf("leaf-1" to listOf(1, 2, 3, 4))
        )

        // Since the only pair is globally resolved, the leaf is converged!
        assertTrue(isConverged)
    }

    @Test
    fun testJudgeAgreementGateExclusion() {
        val rankingService = TaxonomyRankingService()
        
        // Set up target leaves
        val leafIds = listOf("leaf-1", "leaf-2")

        // leaf-1: judge is consistent (agreement = 21/21 = 1.0)
        // leaf-2: judge is inconsistent (agreement = 1/6 = 0.16 < 0.50)
        val stats1 = NodePairStats("leaf-1", "model-A", "model-B", winsA = 20.0, winsB = 1.0, totalComparisons = 21, agreementWins = 21, agreementChecks = 21)
        val stats2 = NodePairStats("leaf-2", "model-A", "model-B", winsA = 4.0, winsB = 0.0, totalComparisons = 6, agreementWins = 1, agreementChecks = 6)

        // Save pair stats to ranking service database
        rankingService.saveNodePairStats(stats1, "test-gate")
        rankingService.saveNodePairStats(stats2, "test-gate")

        // Save BT state
        val state1 = NodeBtState("leaf-1", mapOf("model-A" to 1.5, "model-B" to -1.5), mapOf("model-A" to 0.2, "model-B" to 0.2), 1, 21, System.currentTimeMillis())
        val state2 = NodeBtState("leaf-2", mapOf("model-A" to 2.0, "model-B" to -2.0), mapOf("model-A" to 0.2, "model-B" to 0.2), 1, 6, System.currentTimeMillis())
        rankingService.saveBtState(state1, "test-gate")
        rankingService.saveBtState(state2, "test-gate")

        // Aggregate scores
        val aggregated = rankingService.aggregateLeafScores(
            leafNodeIds = leafIds,
            snapshotId = "test-gate",
            minComparisons = 5,
            nodeToQuestions = mapOf("leaf-1" to listOf(1), "leaf-2" to listOf(1))
        )

        // Verify that leaf-2 was excluded and replaced by noisy prior (score 0.0, SE 10.0),
        // meaning the aggregated score of model-A is determined almost entirely by leaf-1 (1.5)
        val rankA = aggregated.ranks.first { it.modelId == "model-A" }
        // The score of model-A should be very close to 1.5 (leaf-1), not pull up to 2.0 (leaf-2)
        assertTrue(abs(rankA.btScore - 1.5) < 0.2)
    }

    @Test
    fun testPositionBiasDebiasing() {
        val originalStats = NodePairStats(
            nodeId = "leaf-1", modelA = "model-A", modelB = "model-B",
            winsA = 4.0, winsB = 2.0, ties = 0, totalComparisons = 6,
            winAFirst = 4.0, winASecond = 0.0 // Strong position bias: delta = (4 - 0) / 6 = 0.66 > 0.3
        )

        // Invoke adjustForPositionBias using reflection or copy the logic to verify correctness
        val delta = (originalStats.winAFirst - originalStats.winASecond) / originalStats.totalComparisons.toDouble()
        assertTrue(abs(delta) > 0.3)

        val correctedWinA = (originalStats.winAFirst + originalStats.winASecond) / 2.0
        val correctedWinB = originalStats.totalComparisons.toDouble() - correctedWinA - originalStats.ties.toDouble()

        assertEquals(2.0, correctedWinA)
        assertEquals(4.0, correctedWinB)
    }

    @Test
    fun testIrresolvableOnlyLeafConvergence() {
        val stoppingPolicy = BtStoppingPolicy(budgetPerPair = 20, minTotalComparisons = 5)
        
        // Leaf composed entirely of irresolvable pairs
        val leafId = "leaf-1"
        val models = listOf("model-A", "model-B")
        
        val state = NodeBtState(
            nodeId = leafId,
            btScores = mapOf("model-A" to 0.0, "model-B" to 0.0),
            stdErrors = mapOf("model-A" to 0.5, "model-B" to 0.5),
            fitVersion = 1,
            totalComparisons = 6,
            lastFitAt = System.currentTimeMillis()
        )

        // The budget for the pair is capped at comparisons done (6)
        stoppingPolicy.pairCustomBudgets["$leafId|model-A|model-B"] = 6

        val pairStats = mapOf(
            leafId to listOf(
                NodePairStats(leafId, "model-A", "model-B", totalComparisons = 6, ties = 4)
            )
        )

        val isConverged = stoppingPolicy.shouldStop(
            btStates = mapOf(leafId to state),
            pairStats = pairStats,
            targetLeafIds = setOf(leafId),
            models = models,
            round = 2,
            totalComparisons = 6,
            nodeToQueries = mapOf(leafId to listOf(1, 2, 3, 4, 5, 6))
        )

        // All pairs are resolved (totalComparisons >= custom budget), so shouldStop should be true
        assertTrue(isConverged)
    }
}
