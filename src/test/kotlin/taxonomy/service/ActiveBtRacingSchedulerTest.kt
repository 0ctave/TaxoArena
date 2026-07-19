package taxonomy.service

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.model.GraphNode
import taxonomy.model.NodePairStats
import taxonomy.dataset.ModelEvalResult

class ActiveBtRacingSchedulerTest {

    @Test
    fun testActiveBtRacingSchedulerHighTieExhaustion() {
        val scheduler = ActiveBtRacingScheduler(alpha = 0.05, nMin = 5)
        
        val targetNodes = listOf(GraphNode(id = "leaf-1", label = "Math", depth = 1))
        val models = listOf("model-A", "model-B")
        val nodeToQueries = mapOf("leaf-1" to listOf(1, 2, 3, 4, 5, 6))
        
        val pairStats = mapOf(
            "leaf-1" to listOf(
                NodePairStats(nodeId = "leaf-1", modelA = "model-A", modelB = "model-B", totalComparisons = 5, winsA = 0.0, winsB = 0.0, ties = 5)
            )
        )

        val resultsMatrix = (1..6).associateWith { qId ->
            mapOf(
                "model-A" to ModelEvalResult(questionId = qId, modelName = "model-A", category = "Math", questionText = "test", options = listOf("A"), gtAnswer = "A", pred = "A", modelOutput = "", isCorrect = true, isReserved = false),
                "model-B" to ModelEvalResult(questionId = qId, modelName = "model-B", category = "Math", questionText = "test", options = listOf("A"), gtAnswer = "A", pred = "A", modelOutput = "", isCorrect = true, isReserved = false)
            )
        }

        val batch = scheduler.selectNextBatch(
            targetNodes = targetNodes,
            pairStats = pairStats,
            models = models,
            resultsMatrix = resultsMatrix,
            nodeToQueries = nodeToQueries,
            batchSize = 2,
            completedResults = emptyList(),
            budgetPerPair = 5
        )

        assertTrue(batch.isEmpty(), "No queries should be scheduled for exhausted pair")
    }

    @Test
    fun testActiveBtRacingSchedulerAnswerKeyBlindness() {
        val scheduler = ActiveBtRacingScheduler()
        val targetNodes = listOf(GraphNode(id = "leaf-1", label = "Math", depth = 1))
        val models = listOf("model-A", "model-B")
        val nodeToQueries = mapOf("leaf-1" to listOf(1))

        val resultsMatrix = mapOf(
            1 to mapOf(
                "model-A" to ModelEvalResult(questionId = 1, modelName = "model-A", category = "Math", questionText = "test", options = listOf("A"), gtAnswer = "A", pred = "A", modelOutput = "", isCorrect = false, isReserved = false),
                "model-B" to ModelEvalResult(questionId = 1, modelName = "model-B", category = "Math", questionText = "test", options = listOf("A"), gtAnswer = "A", pred = "B", modelOutput = "", isCorrect = false, isReserved = false)
            )
        )

        val batch = scheduler.selectNextBatch(
            targetNodes = targetNodes,
            pairStats = emptyMap(),
            models = models,
            resultsMatrix = resultsMatrix,
            nodeToQueries = nodeToQueries,
            batchSize = 1,
            completedResults = emptyList(),
            budgetPerPair = 10
        )

        assertEquals(1, batch.size)
        assertEquals("1", batch.first().queryIds.first())
    }

    @Test
    fun testRandomTournamentSchedulerSeedDeterminism() {
        val scheduler1 = RandomTournamentScheduler(seed = 42L)
        val scheduler2 = RandomTournamentScheduler(seed = 42L)

        val targetNodes = listOf(GraphNode(id = "leaf-1", label = "Math", depth = 1))
        val models = listOf("model-A", "model-B", "model-C")
        val nodeToQueries = mapOf("leaf-1" to (1..50).toList())
        
        val resultsMatrix = (1..50).associateWith { qId ->
            mapOf(
                "model-A" to ModelEvalResult(questionId = qId, modelName = "model-A", category = "Math", questionText = "test", options = listOf("A"), gtAnswer = "A", pred = "A", modelOutput = "", isCorrect = true, isReserved = false),
                "model-B" to ModelEvalResult(questionId = qId, modelName = "model-B", category = "Math", questionText = "test", options = listOf("A"), gtAnswer = "A", pred = "A", modelOutput = "", isCorrect = true, isReserved = false),
                "model-C" to ModelEvalResult(questionId = qId, modelName = "model-C", category = "Math", questionText = "test", options = listOf("A"), gtAnswer = "A", pred = "A", modelOutput = "", isCorrect = true, isReserved = false)
            )
        }

        val batch1 = scheduler1.selectNextBatch(targetNodes, emptyMap(), models, resultsMatrix, nodeToQueries, 10, emptyList(), 20)
        val batch2 = scheduler2.selectNextBatch(targetNodes, emptyMap(), models, resultsMatrix, nodeToQueries, 10, emptyList(), 20)

        assertEquals(
            batch1.map { Triple(it.nodeId, ordered(it.modelA, it.modelB), it.queryIds) },
            batch2.map { Triple(it.nodeId, ordered(it.modelA, it.modelB), it.queryIds) }
        )
    }
}
