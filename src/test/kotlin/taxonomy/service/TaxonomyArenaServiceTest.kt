package taxonomy.service

import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`
import dev.langchain4j.model.chat.request.json.JsonSchema
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.dataset.ModelEvalStore
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomyOperations

class TaxonomyArenaServiceTest {

    private fun isModelAAlpha(userPrompt: String): Boolean {
        val indexA = userPrompt.indexOf("[Model A's Response]")
        val indexB = userPrompt.indexOf("[Model B's Response]")
        val indexTraceA = userPrompt.indexOf("trace for A")
        return indexTraceA in indexA..indexB
    }

    @Test
    fun testPairwiseTieBreakerLogic() = runBlocking {
        // Arrange
        val config = TaxonomyConfig()
        config.llm.judgeModel = "test-judge-model"

        val node = GraphNode(id = "node-1", label = "Test Concept", depth = 0)
        node.judgePrompt = "Judge this please"
        node.judgeRubric = """{"criteria":[],"failure_modes":[]}"""

        val mockTaxonomyService = mock(TaxonomyService::class.java)
        `when`(mockTaxonomyService.getGraph()).thenReturn(node)

        val mockEmbeddingCache = mock(EmbeddingCache::class.java)
        val queryText = "What is 1+1?"
        `when`(mockEmbeddingCache.getOrCreate(queryText)).thenReturn(floatArrayOf(0.1f, 0.2f))

        val mockOps = mock(TaxonomyOperations::class.java)
        val expectedEmb = Embedding(queryText, queryText, floatArrayOf(0.1f, 0.2f))
        `when`(mockOps.routeQuery(expectedEmb, node, 2, null)).thenReturn(mapOf(node to 1.0))

        val mockEvalStore = mock(ModelEvalStore::class.java)
        val mockRankingService = mock(TaxonomyRankingService::class.java)

        // Mock LLM Client that tracks prompts and acts as our judge
        val promptQueries = mutableListOf<String>()
        val mockLlmClient = object : TaxonomyLlmClient {
            override suspend fun generateClusterLabel(prompt: String): String = ""
            override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String = ""

            override suspend fun queryModelStructured(
                modelName: String,
                systemPrompt: String?,
                userPrompt: String,
                schema: JsonSchema
            ): String {
                promptQueries.add(userPrompt)
                return if (isModelAAlpha(userPrompt)) {
                    // Trial 1: Alpha is A, Beta is B. Voted Model A (Alpha) with confidence 0.9.
                    """{"winner": "Model A", "rationale": "Alpha is very clear", "confidence": 0.9}"""
                } else {
                    // Trial 2: Beta is A, Alpha is B. Voted Model A (Beta) with confidence 0.7.
                    """{"winner": "Model A", "rationale": "Beta is okay", "confidence": 0.7}"""
                }
            }

            override fun setMaxParallel(limit: Int) {}
        }

        val service = TaxonomyArenaService(
            config,
            mockTaxonomyService,
            mockLlmClient,
            mockEmbeddingCache,
            mockOps,
            mockEvalStore,
            mockRankingService
        )

        // Act
        val evaluations = service.evaluateWithPrecomputedTraces(
            query = "What is 1+1?",
            options = listOf("2", "3"),
            modelA = "alpha",
            traceA = "trace for A",
            modelB = "beta",
            traceB = "trace for B"
        )

        // Assert
        assertEquals(1, evaluations.size)
        val eval = evaluations.first()
        assertEquals("Test Concept", eval.domainLabel)
        assertEquals("TIE", eval.winner) // Position flip resolved as TIE
        assertTrue(eval.rationale.contains("Split verdict (position flip)"))
        assertEquals(0.5, eval.confidence)

        // Should have called LLM exactly 2 times (both directions run once)
        assertEquals(2, promptQueries.size)

        // Verify the instructions within prompt queries
        assertTrue(promptQueries[0].contains("If both models are genuinely equivalent, output winner: \"TIE\" with confidence ≤ 0.5."))
    }

    @Test
    fun testPairwiseNoTieBreakerWhenFirstTrialWins() = runBlocking {
        // Arrange
        val config = TaxonomyConfig()
        config.llm.judgeModel = "test-judge-model"

        val node = GraphNode(id = "node-1", label = "Test Concept", depth = 0)
        node.judgePrompt = "Judge this please"
        node.judgeRubric = """{"criteria":[],"failure_modes":[]}"""

        val mockTaxonomyService = mock(TaxonomyService::class.java)
        `when`(mockTaxonomyService.getGraph()).thenReturn(node)

        val mockEmbeddingCache = mock(EmbeddingCache::class.java)
        val queryText = "What is 1+1?"
        `when`(mockEmbeddingCache.getOrCreate(queryText)).thenReturn(floatArrayOf(0.1f, 0.2f))

        val mockOps = mock(TaxonomyOperations::class.java)
        val expectedEmb = Embedding(queryText, queryText, floatArrayOf(0.1f, 0.2f))
        `when`(mockOps.routeQuery(expectedEmb, node, 2, null)).thenReturn(mapOf(node to 1.0))

        val mockEvalStore = mock(ModelEvalStore::class.java)
        val mockRankingService = mock(TaxonomyRankingService::class.java)

        // Mock LLM Client that resolves immediately
        val promptQueries = mutableListOf<String>()
        val mockLlmClient = object : TaxonomyLlmClient {
            override suspend fun generateClusterLabel(prompt: String): String = ""
            override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String = ""

            override suspend fun queryModelStructured(
                modelName: String,
                systemPrompt: String?,
                userPrompt: String,
                schema: JsonSchema
            ): String {
                promptQueries.add(userPrompt)
                return if (isModelAAlpha(userPrompt)) {
                    // Trial 1: Alpha is A, Beta is B. Voted Model A (Alpha).
                    """{"winner": "Model A", "rationale": "A is better", "confidence": 0.9}"""
                } else {
                    // Trial 2: Beta is A, Alpha is B. Voted Model B (Alpha).
                    """{"winner": "Model B", "rationale": "Alpha dominates", "confidence": 0.9}"""
                }
            }

            override fun setMaxParallel(limit: Int) {}
        }

        val service = TaxonomyArenaService(
            config,
            mockTaxonomyService,
            mockLlmClient,
            mockEmbeddingCache,
            mockOps,
            mockEvalStore,
            mockRankingService
        )

        // Act
        val evaluations = service.evaluateWithPrecomputedTraces(
            query = "What is 1+1?",
            options = listOf("2", "3"),
            modelA = "alpha",
            traceA = "trace for A",
            modelB = "beta",
            traceB = "trace for B"
        )

        // Assert
        assertEquals(1, evaluations.size)
        val eval = evaluations.first()
        assertEquals("Model A", eval.winner)
        assertEquals("A is better", eval.rationale)
        assertEquals(0.9, eval.confidence)

        // Should have called LLM exactly 2 times
        assertEquals(2, promptQueries.size)
    }

    @Test
    fun testPairwiseJudgeParsingWithLatexEscapes() = runBlocking {
        // Arrange
        val config = TaxonomyConfig()
        config.llm.judgeModel = "test-judge-model"

        val node = GraphNode(id = "node-1", label = "Test Concept", depth = 0)
        node.judgePrompt = "Judge this please"
        node.judgeRubric = """{"criteria":[],"failure_modes":[]}"""

        val mockTaxonomyService = mock(TaxonomyService::class.java)
        `when`(mockTaxonomyService.getGraph()).thenReturn(node)

        val mockEmbeddingCache = mock(EmbeddingCache::class.java)
        val queryText = "Solve limits"
        `when`(mockEmbeddingCache.getOrCreate(queryText)).thenReturn(floatArrayOf(0.1f, 0.2f))

        val mockOps = mock(TaxonomyOperations::class.java)
        val expectedEmb = Embedding(queryText, queryText, floatArrayOf(0.1f, 0.2f))
        `when`(mockOps.routeQuery(expectedEmb, node, 2, null)).thenReturn(mapOf(node to 1.0))

        val mockEvalStore = mock(ModelEvalStore::class.java)
        val mockRankingService = mock(TaxonomyRankingService::class.java)

        // Mock LLM Client returning LaTeX escaped chars in JSON
        val mockLlmClient = object : TaxonomyLlmClient {
            override suspend fun generateClusterLabel(prompt: String): String = ""
            override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String = ""

            override suspend fun queryModelStructured(
                modelName: String,
                systemPrompt: String?,
                userPrompt: String,
                schema: JsonSchema
            ): String {
                val winner = if (isModelAAlpha(userPrompt)) "Model A" else "Model B"
                return """
                {
                  "critique_a": "Model A correctly identifies potential limit \( L \) by assuming convergence.",
                  "critique_b": "Model B concludes that the sequence does not converge.",
                  "comparison": "The difference is \( L = 1/2 \) vs incorrect.",
                  "winner": "$winner",
                  "confidence": 0.8
                }
                """.trimIndent()
            }

            override fun setMaxParallel(limit: Int) {}
        }

        val service = TaxonomyArenaService(
            config,
            mockTaxonomyService,
            mockLlmClient,
            mockEmbeddingCache,
            mockOps,
            mockEvalStore,
            mockRankingService
        )

        // Act & Assert (Should not throw JsonDecodingException)
        val evaluations = service.evaluateWithPrecomputedTraces(
            query = "Solve limits",
            options = listOf("2", "3"),
            modelA = "alpha",
            traceA = "trace for A",
            modelB = "beta",
            traceB = "trace for B"
        )

        assertEquals(1, evaluations.size)
        val eval = evaluations.first()
        assertEquals("Model A", eval.winner)
        assertEquals(0.8, eval.confidence)
    }

    @Test
    fun testHardenedParsingWithRegexFallback() = runBlocking {
        // Arrange
        val config = TaxonomyConfig()
        config.llm.judgeModel = "test-judge-model"

        val node = GraphNode(id = "node-1", label = "Test Concept", depth = 0)
        node.judgePrompt = "Judge this please"
        node.judgeRubric = """{"criteria":[],"failure_modes":[]}"""

        val mockTaxonomyService = mock(TaxonomyService::class.java)
        `when`(mockTaxonomyService.getGraph()).thenReturn(node)

        val mockEmbeddingCache = mock(EmbeddingCache::class.java)
        val queryText = "Solve limits"
        `when`(mockEmbeddingCache.getOrCreate(queryText)).thenReturn(floatArrayOf(0.1f, 0.2f))

        val mockOps = mock(TaxonomyOperations::class.java)
        val expectedEmb = Embedding(queryText, queryText, floatArrayOf(0.1f, 0.2f))
        `when`(mockOps.routeQuery(expectedEmb, node, 2, null)).thenReturn(mapOf(node to 1.0))

        val mockEvalStore = mock(ModelEvalStore::class.java)
        val mockRankingService = mock(TaxonomyRankingService::class.java)

        // Mock LLM Client returning malformed JSON (unescaped quotes inside double quotes)
        val mockLlmClientMalformed = object : TaxonomyLlmClient {
            override suspend fun generateClusterLabel(prompt: String): String = ""
            override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String = ""

            override suspend fun queryModelStructured(
                modelName: String,
                systemPrompt: String?,
                userPrompt: String,
                schema: JsonSchema
            ): String {
                val winner = if (isModelAAlpha(userPrompt)) "Model A" else "Model B"
                return """
                {
                  "comparison": "He said "yes" and won.",
                  "winner": "$winner",
                  "confidence": 0.95
                }
                """.trimIndent()
            }

            override fun setMaxParallel(limit: Int) {}
        }

        val service = TaxonomyArenaService(
            config,
            mockTaxonomyService,
            mockLlmClientMalformed,
            mockEmbeddingCache,
            mockOps,
            mockEvalStore,
            mockRankingService
        )

        // Act & Assert (Should succeed using regex fallback)
        val evaluations = service.evaluateWithPrecomputedTraces(
            query = "Solve limits",
            options = listOf("2", "3"),
            modelA = "alpha",
            traceA = "trace for A",
            modelB = "beta",
            traceB = "trace for B"
        )

        assertEquals(1, evaluations.size)
        val eval = evaluations.first()
        assertEquals("Model A", eval.winner)
        assertEquals(0.95, eval.confidence)
    }
}
