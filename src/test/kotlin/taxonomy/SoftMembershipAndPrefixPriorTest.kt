package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.service.DomainEvaluation
import taxonomy.model.QueryBenchmarkResult
import taxonomy.service.ValidationService

class SoftMembershipAndPrefixPriorTest {

    @Test
    fun testSoftAdaptedBtScoresWithWeightedMemberships() {
        val models = listOf("Model-A", "Model-B", "Model-C")
        
        // Build 5 queries to satisfy the 5.0 comparisons threshold
        val results = mutableListOf<QueryBenchmarkResult>()
        for (i in 1..5) {
            val eval = DomainEvaluation("Leaf-1", "Model A", "Model A wins", 1.0, false, "Leaf-1")
            results.add(
                QueryBenchmarkResult(
                    query = "Query $i",
                    gtCategory = "Category-1",
                    gtCorrectAnswer = "A",
                    modelAnswers = mapOf("Model-A" to "A", "Model-B" to "B", "Model-C" to "A"),
                    modelCorrect = mapOf("Model-A" to true, "Model-B" to false, "Model-C" to true),
                    matchedLeafLabels = listOf("Leaf-1"),
                    hadJudge = true,
                    domainEvaluations = listOf(eval),
                    pairEvaluations = mapOf("Model-A_vs_Model-B" to listOf(eval)),
                    judgeAccuracyAgreement = mapOf("Model-A_vs_Model-B" to true),
                    secondaryMemberships = emptyMap()
                )
            )
        }

        // We run computeSoftAdaptedBtScores
        val softBtScores = ValidationService.computeSoftAdaptedBtScores(results, models)
        
        // Verify that the fitter executes and produces scores for the models
        assertTrue(softBtScores.containsKey("Model-A"))
        assertTrue(softBtScores.containsKey("Model-B"))
        assertTrue(softBtScores.containsKey("Model-C"))
    }
}
