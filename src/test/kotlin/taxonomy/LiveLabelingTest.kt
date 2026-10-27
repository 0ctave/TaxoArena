package taxonomy

import taxonomy.*
import taxonomy.arena.*
import taxonomy.prompts.*
import taxonomy.utils.*
import taxonomy.config.*
import taxonomy.model.*
import taxonomy.controller.*
import taxonomy.service.*
import taxonomy.dataset.*
import taxonomy.operations.*
import taxonomy.tui.*
import taxonomy.runner.*

import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomySplitter
import taxonomy.operations.TaxonomyFitter
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import dev.langchain4j.model.chat.request.json.JsonSchema

class LiveLabelingTest {

    class TestLlmClient : TaxonomyLlmClient {
        override suspend fun generateClusterLabel(prompt: String): String = ""
        override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String = ""
        override suspend fun queryModelStructured(
            modelName: String,
            systemPrompt: String?,
            userPrompt: String,
            schema: JsonSchema
        ): String {
            return """{"label": "Mocked Post-Pass Concept"}"""
        }
        override fun setMaxParallel(limit: Int) {}
    }

    @Test
    fun testPostPassLabelingFlow() = kotlinx.coroutines.runBlocking {
        // 1. Create dependencies
        val config = TaxonomyConfig()

        val llmClient = TestLlmClient()
        val datasetFetcher = mock(MMLUDatasetFetcher::class.java)
        val fitter = mock(TaxonomyFitter::class.java)

        val splitter = TaxonomySplitter(config, llmClient, datasetFetcher, fitter)

        // 2. Create a mock taxonomy hierarchy with temporary labels
        val root = GraphNode(id = "root", label = "Universal Knowledge", depth = 0)
        val parent = GraphNode(id = "parent", label = "Parent Concept", depth = 1)
        val child = GraphNode(id = "child", label = "Emergent Concept #1", depth = 2).apply {
            queries.add(Embedding("What is computer science?", "What is computer science?", FloatArray(4) { 0.1f }))
            queries.add(Embedding("How does CPU work?", "How does CPU work?", FloatArray(4) { 0.2f }))
        }
        root.children.add(parent)
        parent.parents.add(root)
        parent.children.add(child)
        child.parents.add(parent)

        // 3. Run post-pass labeling
        splitter.resetConceptCounter()
        splitter.generateLabelsPostPass(root)

        // 4. Verify the node label got updated to the mocked LLM response
        assertEquals("Mocked Post-Pass Concept", child.label)
    }

    @Test
    fun testDeduplicatedRecursiveQueryCount() {
        val root = GraphNode(id = "root", label = "Universal Knowledge", depth = 0)
        val child1 = GraphNode(id = "child1", label = "Child 1", depth = 1)
        val child2 = GraphNode(id = "child2", label = "Child 2", depth = 1)
        
        root.children.addAll(listOf(child1, child2))
        child1.parents.add(root)
        child2.parents.add(root)

        // Create query objects. Same raw text, duplicate/distinct instances.
        val q1 = Embedding("CPU Scheduling", "CPU Scheduling", FloatArray(4))
        val q2 = Embedding("CPU Scheduling", "CPU Scheduling", FloatArray(4))
        val q3 = Embedding("Operating Systems", "Operating Systems", FloatArray(4))

        child1.queries.addAll(listOf(q1, q3))
        child2.queries.add(q2)

        // Assign query IDs
        assignQueryIds(root)

        // Verify counts
        assertEquals(2, child1.getRecursiveQueryCount())
        assertEquals(1, child2.getRecursiveQueryCount())
        assertEquals(2, root.getRecursiveQueryCount()) // 2 unique queries overall, not 3
    }
}
