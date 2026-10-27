package taxonomy.service

import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import org.mockito.Mockito.verifyNoInteractions
import org.mockito.Mockito.`when`
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.dataset.ModelEvalStore
import taxonomy.model.GraphNode
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomyOperations
import taxonomy.utils.TaxonomyPerformanceTracker
import java.io.File

/**
 * JUDGE-WIRING guard: the production Mistral judge path is byte-identical when the recipe keys are
 * absent.
 *
 * The golden (`src/test/resources/judge_wiring/mistral_path_golden.json`) was RECORDED AT THE PARENT
 * COMMIT of the JUDGE-WIRING change with this same test in record mode
 * (`-DrecordMistralGolden=true`), before `TracePreparation` or the recipe branch existed. It pins the
 * exact (system, user order 1, user order 2) strings `evaluateWithPrecomputedTraces` hands to
 * `queryModelStructured` for a fixed node / query / traces (non-ASCII, a `\r`, an em dash, a trailing
 * blank line in the rubric), plus the serialized `DomainEvaluation` list under the runner's Json
 * settings. Any drift in the v1 templates, the option block, the combination rule or the
 * serialized shape (an `encodeDefaults` flip would add `judgeCalls: []`) fails here.
 */
class MistralJudgePathUnchangedTest {

    @Serializable
    data class Golden(val system: String, val user1: String, val user2: String, val evaluationsJson: String)

    private val goldenFile = File("src/test/resources/judge_wiring/mistral_path_golden.json")

    private class CapturingClient : TaxonomyLlmClient {
        val calls = mutableListOf<Pair<String?, String>>()
        override suspend fun generateClusterLabel(prompt: String): String = ""
        override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String =
            error("queryModel must not be used on the structured judge path")
        override suspend fun queryModelStructured(modelName: String, systemPrompt: String?, userPrompt: String, schema: JsonSchema): String {
            synchronized(calls) { calls.add(systemPrompt to userPrompt) }
            // Order 1 (trace A first) votes Model A at 0.9; order 2 votes Model B (= A) at 0.8: a consistent A win.
            return if (userPrompt.indexOf("TRACE-ALPHA") < userPrompt.indexOf("TRACE-BETA"))
                """{"critique_a":"a","critique_b":"b","comparison":"c","winner":"Model A","confidence":0.9}"""
            else
                """{"critique_a":"a","critique_b":"b","comparison":"c","winner":"Model B","confidence":0.8}"""
        }
        override fun setMaxParallel(limit: Int) {}
    }

    @Test
    fun `mistral judge path prompts and evaluation shape are byte-identical to the parent-commit golden`() = runBlocking {
        val config = TaxonomyConfig()                       // recipe absent: nothing new may execute
        config.llm.judgeModel = "Mistral-Large-3"
        config.llm.judgeOptionMode = "OPTIONS"

        val node = GraphNode(id = "leaf-golden", label = "Thermodynamics — cycles", depth = 2)
        node.judgePrompt = "You are an expert evaluator of thermodynamics (Carnot, Otto — cycles)."
        node.judgeRubric = "Grade on: (1) correct state functions; (2) sign convention kept; (3) units.\n"

        val taxonomyService = mock(TaxonomyService::class.java)
        `when`(taxonomyService.getGraph()).thenReturn(node)
        val embeddingCache = mock(EmbeddingCache::class.java)
        val ops = mock(TaxonomyOperations::class.java)
        val evalStore = mock(ModelEvalStore::class.java)
        val rankingService = mock(TaxonomyRankingService::class.java)
        val client = CapturingClient()

        val service = TaxonomyArenaService(
            config, taxonomyService, client, embeddingCache, ops, evalStore, rankingService, TaxonomyPerformanceTracker()
        )
        val evals = service.evaluateWithPrecomputedTraces(
            query = "A Carnot engine runs between 500 K and 300 K. What is its efficiency – to 1 dp?",
            options = listOf("40.0%", "60.0%", "25.0%", "η = 1 − T_c/T_h ≈ 0.4"),
            modelA = "alpha",
            traceA = "TRACE-ALPHA: η = 1 − 300/500 = 0.4.\r\nThe answer is (A).",
            modelB = "beta",
            traceB = "TRACE-BETA: efficiency is 60% — the answer is (B).\n\n[This model's selected answer: (B) 60.0%]",
            assignedLeafIds = listOf(node.id),
            condition = "MAIN"
        )

        assertEquals(2, client.calls.size)
        // order 1 puts TRACE-ALPHA under [Model A's Response]; pick by content so the golden is dispatch-order independent
        val order1 = client.calls.first { it.second.indexOf("TRACE-ALPHA") < it.second.indexOf("TRACE-BETA") }
        val order2 = client.calls.first { it.second.indexOf("TRACE-ALPHA") > it.second.indexOf("TRACE-BETA") }
        assertEquals(order1.first, order2.first, "both orders share the system prompt")
        val runnerJson = Json { prettyPrint = true; ignoreUnknownKeys = true }   // HeadlessBenchmarkRunner's settings
        val observed = Golden(
            system = order1.first ?: "",
            user1 = order1.second,
            user2 = order2.second,
            evaluationsJson = runnerJson.encodeToString(evals)
        )
        verifyNoInteractions(rankingService)
        assertEquals("Model A", evals.single().winner)

        val goldenJson = Json { prettyPrint = true }
        if (System.getProperty("recordMistralGolden") == "true") {
            goldenFile.parentFile.mkdirs()
            goldenFile.writeText(goldenJson.encodeToString(observed), Charsets.UTF_8)
            println("[GOLDEN] recorded ${goldenFile.path}")
        }
        assertTrue(goldenFile.isFile, "golden missing: record it at the parent commit with -DrecordMistralGolden=true")
        val expected = goldenJson.decodeFromString<Golden>(goldenFile.readText(Charsets.UTF_8))
        assertEquals(expected.system, observed.system, "system prompt drifted from the parent-commit golden")
        assertEquals(expected.user1, observed.user1, "order-1 user prompt drifted")
        assertEquals(expected.user2, observed.user2, "order-2 user prompt drifted")
        assertEquals(expected.evaluationsJson, observed.evaluationsJson, "serialized DomainEvaluation shape drifted")
    }
}
