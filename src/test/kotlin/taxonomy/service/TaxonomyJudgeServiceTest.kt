package taxonomy.service

import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.mockito.Mockito.*
import dev.langchain4j.model.chat.request.json.JsonSchema
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.HFProRowData
import taxonomy.model.GraphNode
import taxonomy.operations.TaxonomyLlmClient

class TaxonomyJudgeServiceTest {

    class TestLlmClient : TaxonomyLlmClient {
        override suspend fun generateClusterLabel(prompt: String): String = ""
        override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String {
            // Return JSON containing prompt/rubric structure to avoid repair flow
            return """
                {
                    "judge_system_prompt": "This is a mock judge prompt for testing.",
                    "judge_rubric": {
                        "criteria": ["Accuracy"],
                        "failure_modes": []
                    }
                }
            """.trimIndent()
        }
        override suspend fun queryModelStructured(
            modelName: String,
            systemPrompt: String?,
            userPrompt: String,
            schema: JsonSchema
        ): String = ""

        override fun setMaxParallel(limit: Int) {}
    }

    @Test
    fun testBelongsToAnyDomainFiltering() {
        runBlocking {
            val mockDatasetFetcher = mock(MMLUDatasetFetcher::class.java)
            val llmClient = TestLlmClient()
            val config = TaxonomyConfig()
            val mockArenaService = mock(TaxonomyArenaService::class.java)

            // Set up judge domains filter
            config.llm.judgeDomains = listOf("Math", "Science")

            val service = TaxonomyJudgeService(
                mockDatasetFetcher,
                llmClient,
                config,
                mockArenaService
            )

            // Build mock DAG:
            // Root -> Math Node (Label: Math)
            // Root -> Literature Node (Label: Literature)
            val root = GraphNode(id = "root", label = "Root", depth = 0)
            val mathNode = GraphNode(id = "math", label = "Math", depth = 1)
            val litNode = GraphNode(id = "literature", label = "Literature", depth = 1)
            val algebraNode = GraphNode(id = "algebra", label = "Algebra", depth = 2)

            root.children.add(mathNode)
            mathNode.parents.add(root)

            root.children.add(litNode)
            litNode.parents.add(root)

            mathNode.children.add(algebraNode)
            algebraNode.parents.add(mathNode)

            // Setup queries for leaves so they get processed
            val q1 = taxonomy.model.Embedding("q1", "q1", floatArrayOf(0.1f))
            val q2 = taxonomy.model.Embedding("q2", "q2", floatArrayOf(0.2f))
            algebraNode.queries.add(q1)
            litNode.queries.add(q2)

            `when`(mockDatasetFetcher.getDetailsForQueries(listOf("q1"))).thenReturn(
                mapOf("q1" to HFProRowData(question = "q1", options = listOf("A", "B"), answer = "A", cot_content = "reasoning"))
            )
            `when`(mockDatasetFetcher.getDetailsForQueries(listOf("q2"))).thenReturn(
                mapOf("q2" to HFProRowData(question = "q2", options = listOf("A", "B"), answer = "A", cot_content = "reasoning"))
            )

            // Run generateJudgesForDag
            service.generateJudgesForDag(root, replaceExisting = true, maxGenerality = 2)

            // litNode ("Literature") should be filtered out, so it shouldn't call getDetailsForQueries for q2.
            // algebraNode ("Algebra", parent is "Math") matches "Math" domain filter, so it should call getDetailsForQueries for q1.
            // mathNode ("Math") matches "Math" domain filter, so it also calls getDetailsForQueries for q1 (because q1 is in its branch).
            verify(mockDatasetFetcher, times(2)).getDetailsForQueries(listOf("q1"))
            verify(mockDatasetFetcher, never()).getDetailsForQueries(listOf("q2"))
        }
    }
}
