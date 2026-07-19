package taxonomy

import ch.qos.logback.classic.Level
import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.spi.ILoggingEvent
import ch.qos.logback.core.read.ListAppender
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.slf4j.LoggerFactory
import taxonomy.model.GraphNode
import taxonomy.model.NodeBtState
import taxonomy.model.NodePairStats
import taxonomy.service.BtMatchScheduler
import taxonomy.service.BtMmFitter
import taxonomy.service.BtStoppingPolicy
import taxonomy.utils.StatisticsUtils
import taxonomy.dataset.ModelEvalResult
import kotlin.math.abs

/**
 * Formula verification test suite covering:
 * 1. vMF correctedKappa (Hornik & Grün 2014, Eq. 9 bias correction).
 * 2. Bradley-Terry MM fitter updates (Hunter 2004 MM denominator & convergence).
 * 3. Scheduler uncertainty sign (high standard error / variance prioritization).
 */
class KappaBiasCorrectionTest {

    @Test
    fun high_dimension_low_n_removes_positive_bias() {
        val rBar = 0.8
        val d = 1024
        val n = 20
        
        // Execute the correctedKappa calculation
        val corrected = StatisticsUtils.correctedKappa(rBar, d, n)
        
        val kappaML = rBar * (d - rBar * rBar) / (1.0 - rBar * rBar)
        val expectedShrinkage = (n - 1).toDouble() / (n + d - 2).toDouble().coerceAtLeast(1.0)
        val expected = (kappaML * expectedShrinkage).coerceIn(1e-3, 1e4)
        
        assertEquals(expected, corrected, 1e-6)
        assertTrue(corrected < kappaML, "Bias correction must reduce the MLE, got $corrected vs $kappaML")
    }

    @Test
    fun extreme_ratio_emits_warning() {
        val logger = LoggerFactory.getLogger("taxonomy.Statistics") as Logger
        val appender = ListAppender<ILoggingEvent>().apply { start() }
        logger.addAppender(appender)
        try {
            StatisticsUtils.resetUnreliableKappaCount()
            // d/N = 1024/5 = 204.8 > 10 -> WARN log
            StatisticsUtils.correctedKappa(0.95, 1024, 5)
        } finally {
            logger.detachAppender(appender)
        }

        val warned = appender.list.any { it.level == Level.WARN && it.formattedMessage.contains("[VMF]") }
        assertTrue(warned, "d/N > 10 must emit a WARN log")
    }

    @Test
    fun testBradleyTerryMmFitterConvergence() {
        val models = listOf("Model-A", "Model-B", "Model-C")
        
        // Simulate a tournament where:
        // A beats B 4 times, B beats A 1 time
        // B beats C 3 times, C beats B 2 times
        // A beats C 5 times, C beats A 0 times
        val pairStats = listOf(
            NodePairStats("test-node", "Model-A", "Model-B", winsA = 4.0, winsB = 1.0, ties = 0, totalComparisons = 5),
            NodePairStats("test-node", "Model-B", "Model-C", winsA = 3.0, winsB = 2.0, ties = 0, totalComparisons = 5),
            NodePairStats("test-node", "Model-A", "Model-C", winsA = 5.0, winsB = 0.0, ties = 0, totalComparisons = 5)
        )
        
        val fitScores = BtMmFitter.fit(models, pairStats, maxIter = 100, tol = 1e-6)
        
        val scoreA = fitScores["Model-A"] ?: 0.0
        val scoreB = fitScores["Model-B"] ?: 0.0
        val scoreC = fitScores["Model-C"] ?: 0.0
        
        // A > B > C must be strictly preserved
        assertTrue(scoreA > scoreB, "A must have a higher score than B")
        assertTrue(scoreB > scoreC, "B must have a higher score than C")
        
        // Assert scores sum to 0.0 due to mean normalization
        assertEquals(0.0, scoreA + scoreB + scoreC, 1e-9)
    }

    @Test
    fun testSchedulerPrioritizesHighUncertainty() {
        val stoppingPolicy = BtStoppingPolicy(budgetPerPair = 20)
        val scheduler = BtMatchScheduler(
            minQueriesForBenchmark = 2,
            queriesPerPair = 20,
            budgetPerPair = 20,
            stoppingPolicy = stoppingPolicy
        )

        val targetNodes = listOf(
            GraphNode(id = "leaf-high", label = "HighUncertainty", depth = 1),
            GraphNode(id = "leaf-low", label = "LowUncertainty", depth = 1)
        )
        val models = listOf("model-A", "model-B", "model-C")

        // leaf-high has high standard errors (1.5)
        val stateHigh = NodeBtState(
            nodeId = "leaf-high",
            btScores = mapOf("model-A" to 0.1, "model-B" to 0.0, "model-C" to -0.1),
            stdErrors = mapOf("model-A" to 1.5, "model-B" to 1.5, "model-C" to 1.5),
            fitVersion = 1,
            totalComparisons = 10,
            lastFitAt = System.currentTimeMillis()
        )

        // leaf-low has low standard errors (0.1)
        val stateLow = NodeBtState(
            nodeId = "leaf-low",
            btScores = mapOf("model-A" to 0.1, "model-B" to 0.0, "model-C" to -0.1),
            stdErrors = mapOf("model-A" to 0.1, "model-B" to 0.1, "model-C" to 0.1),
            fitVersion = 1,
            totalComparisons = 10,
            lastFitAt = System.currentTimeMillis()
        )

        val pairStats = mapOf(
            "leaf-high" to listOf(
                NodePairStats("leaf-high", "model-A", "model-B", totalComparisons = 2, ties = 0),
                NodePairStats("leaf-high", "model-B", "model-C", totalComparisons = 2, ties = 0),
                NodePairStats("leaf-high", "model-A", "model-C", totalComparisons = 2, ties = 0)
            ),
            "leaf-low" to listOf(
                NodePairStats("leaf-low", "model-A", "model-B", totalComparisons = 2, ties = 0),
                NodePairStats("leaf-low", "model-B", "model-C", totalComparisons = 2, ties = 0),
                NodePairStats("leaf-low", "model-A", "model-C", totalComparisons = 2, ties = 0)
            )
        )

        val nodeToQueries = mapOf(
            "leaf-high" to listOf(1, 2, 3, 4, 5),
            "leaf-low" to listOf(1, 2, 3, 4, 5)
        )

        val resultsMatrix = mapOf(
            1 to mapOf(
                "model-A" to ModelEvalResult(1, "model-A", "NLP", "query-1", listOf("A", "B"), "A", "A", "reasoning", true, true),
                "model-B" to ModelEvalResult(1, "model-B", "NLP", "query-1", listOf("A", "B"), "A", "A", "reasoning", true, true),
                "model-C" to ModelEvalResult(1, "model-C", "NLP", "query-1", listOf("A", "B"), "A", "A", "reasoning", true, true)
            ),
            2 to mapOf(
                "model-A" to ModelEvalResult(2, "model-A", "NLP", "query-2", listOf("A", "B"), "A", "A", "reasoning", true, true),
                "model-B" to ModelEvalResult(2, "model-B", "NLP", "query-2", listOf("A", "B"), "A", "A", "reasoning", true, true),
                "model-C" to ModelEvalResult(2, "model-C", "NLP", "query-2", listOf("A", "B"), "A", "A", "reasoning", true, true)
            ),
            3 to mapOf(
                "model-A" to ModelEvalResult(3, "model-A", "NLP", "query-3", listOf("A", "B"), "A", "A", "reasoning", true, true),
                "model-B" to ModelEvalResult(3, "model-B", "NLP", "query-3", listOf("A", "B"), "A", "A", "reasoning", true, true),
                "model-C" to ModelEvalResult(3, "model-C", "NLP", "query-3", listOf("A", "B"), "A", "A", "reasoning", true, true)
            ),
            4 to mapOf(
                "model-A" to ModelEvalResult(4, "model-A", "NLP", "query-4", listOf("A", "B"), "A", "A", "reasoning", true, true),
                "model-B" to ModelEvalResult(4, "model-B", "NLP", "query-4", listOf("A", "B"), "A", "A", "reasoning", true, true),
                "model-C" to ModelEvalResult(4, "model-C", "NLP", "query-4", listOf("A", "B"), "A", "A", "reasoning", true, true)
            ),
            5 to mapOf(
                "model-A" to ModelEvalResult(5, "model-A", "NLP", "query-5", listOf("A", "B"), "A", "A", "reasoning", true, true),
                "model-B" to ModelEvalResult(5, "model-B", "NLP", "query-5", listOf("A", "B"), "A", "A", "reasoning", true, true),
                "model-C" to ModelEvalResult(5, "model-C", "NLP", "query-5", listOf("A", "B"), "A", "A", "reasoning", true, true)
            )
        )

        val nextBatch = scheduler.selectNextBatch(
            targetNodes = targetNodes,
            btStates = mapOf("leaf-high" to stateHigh, "leaf-low" to stateLow),
            pairStats = pairStats,
            models = models,
            resultsMatrix = resultsMatrix,
            nodeToQueries = nodeToQueries,
            batchSize = 1,
            maxConcurrentPerModel = 2
        )

        assertEquals(1, nextBatch.size)
        val scheduledPair = nextBatch.first()
        assertEquals("leaf-high", scheduledPair.nodeId, "Should prioritize the leaf node with higher uncertainty (larger standard errors)")
    }
}
