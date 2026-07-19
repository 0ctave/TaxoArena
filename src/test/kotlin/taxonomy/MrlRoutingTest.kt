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

import taxonomy.operations.TaxonomyTrickler
import taxonomy.operations.TaxonomyOperations
import taxonomy.utils.StatisticsUtils
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest

@SpringBootTest(
    classes = [org.eclipse.lmos.arc.app.TaxoAdaptApplication::class],
    properties = [
        "taxoadapt.execution.enable-tui=false",
        "taxoadapt.execution.run-batch=false",
        "taxoadapt.execution.start-service=false",
        "taxoadapt.llm.judge-model=qwen3.6:27b",
        "taxoadapt.llm.labeling-model=gemma4:e4b"
    ]
)
class MrlRoutingTest {

    @Autowired
    private lateinit var config: TaxonomyConfig

    @Autowired
    private lateinit var trickler: TaxonomyTrickler

    @Autowired
    private lateinit var ops: TaxonomyOperations

    @Test
    fun testMrlConfigDefaults() {
        assertEquals(0.02, config.formalism.separationEpsilon)
        assertEquals("qwen3.6:27b", config.llm.judgeModel)
        assertEquals("gemma4:e4b", config.llm.labelingModel)
    }

    @Test
    fun testTrickleRoutingWithFixedDimensions() {
        val root = GraphNode(label = "Root", depth = 0)
        val child = GraphNode(label = "Child", depth = 1).apply {
            vmfMu = FloatArray(128) { 0.0f }.apply { this[0] = 1.0f }
            vmfKappa = 10.0
            vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(128, 10.0)
            niwM0 = FloatArray(128) { 0.0f }.apply { this[0] = 1.0f }
            niwKappa0 = 10.0
            niwNu0 = 130.0
            niwLambda = FloatArray(128) { 1.0f }
        }
        root.children.add(child)
        child.parents.add(root)

        // Setup a query embedding with 128 elements (all 0s except first element)
        val vals = FloatArray(128) { 0.0f }.apply { this[0] = 2.0f } // non-unit norm
        val embedding = Embedding(
            rawText = "test text",
            distilledText = "test text",
            values = vals
        )

        // 1. Verify projectTo normalizes correctly
        val projected = embedding.projectTo(128)
        var norm = 0.0
        for (v in projected) norm += v * v
        assertEquals(1.0, kotlin.math.sqrt(norm), 1e-5)
        assertEquals(1.0, projected[0], 1e-5)

        // 2. Verify routeQuery matches child or root
        val results = trickler.routeQuery(embedding, root, currentIteration = 2)
        assertTrue(results.leaves.isNotEmpty())
    }

}
