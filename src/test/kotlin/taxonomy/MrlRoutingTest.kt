package org.eclipse.lmos.arc.app.taxonomy

import org.eclipse.lmos.arc.app.taxonomy.operations.TaxonomyTrickler
import org.eclipse.lmos.arc.app.taxonomy.TaxonomyOperations
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest

@SpringBootTest(properties = [
    "taxoadapt.execution.enable-tui=false",
    "taxoadapt.execution.run-batch=false",
    "taxoadapt.execution.start-service=false",
    "taxoadapt.llm.judge-model=qwen3.6:27b",
    "taxoadapt.llm.labeling-model=gemma4:e4b"
])
class MrlRoutingTest {

    @Autowired
    private lateinit var config: TaxonomyConfig

    @Autowired
    private lateinit var trickler: TaxonomyTrickler

    @Autowired
    private lateinit var ops: TaxonomyOperations

    @Test
    fun testMrlConfigDefaults() {
        assertEquals(384, config.formalism.fixedMrlDimension)
        assertEquals(0.05, config.formalism.collapseMarginalRatio)
        assertEquals("qwen3.6:27b", config.llm.judgeModel)
        assertEquals("gemma4:e4b", config.llm.labelingModel)
    }

    @Test
    fun testTrickleRoutingWithFixedDimensions() {
        val originalFixedDim = config.formalism.fixedMrlDimension
        
        try {
            // Setup a 4-dimensional query embedding
            val embedding = Embedding(
                rawText = "test text",
                distilledText = "test text",
                values = floatArrayOf(1.0f, 2.0f, 3.0f, 4.0f)
            )

            // Setup a simple GMM with mean=0 and variance=1
            val component = GmmComponent(
                mean = doubleArrayOf(0.0, 0.0, 0.0, 0.0),
                diagonalCovariance = doubleArrayOf(1.0, 1.0, 1.0, 1.0),
                weight = 1.0,
                sampleCount = 10
            )
            val gmm = GmmParams(components = listOf(component), empiricalThreshold = 100.0)

            // Create a node at depth 0
            val rootNode = GraphNode(
                label = "Root",
                depth = 0,
                distribution = gmm
            )

            // Test 1: fixedMrlDimension = 4 (uses all 4 dimensions)
            // Distance = (1^2 + 2^2 + 3^2 + 4^2) / 4 = 30 / 4 = 7.5
            config.formalism.fixedMrlDimension = 4
            
            val resultsFull = mutableMapOf<GraphNode, Double>()
            trickler.trickleQuery(embedding, rootNode, resultsFull)
            
            assertTrue(resultsFull.containsKey(rootNode))
            val expectedFullD2 = 7.5 / config.formalism.inclusionScalingFactor
            assertEquals(expectedFullD2, resultsFull[rootNode]!!, 0.001)

            // Test 2: fixedMrlDimension = 2 (uses first 2 dimensions)
            // Distance = (1^2 + 2^2) / 2 = 5 / 2 = 2.5
            config.formalism.fixedMrlDimension = 2
            
            val resultsFixed = mutableMapOf<GraphNode, Double>()
            trickler.trickleQuery(embedding, rootNode, resultsFixed)
            
            assertTrue(resultsFixed.containsKey(rootNode))
            val expectedFixedD2 = 2.5 / config.formalism.inclusionScalingFactor
            assertEquals(expectedFixedD2, resultsFixed[rootNode]!!, 0.001)

        } finally {
            config.formalism.fixedMrlDimension = originalFixedDim
        }
    }

    @Test
    fun testNodeCollapsingMarginalSiblingQueries() {
        val originalCollapseRatio = config.formalism.collapseMarginalRatio
        config.formalism.collapseMarginalRatio = 0.05

        try {
            val root = GraphNode(label = "Root", depth = 0)
            val parent = GraphNode(label = "Parent", depth = 1)
            root.children.add(parent)
            parent.parents.add(root)

            val child1 = GraphNode(label = "Child1", depth = 2)
            val child2 = GraphNode(label = "Child2", depth = 2)

            parent.children.add(child1)
            parent.children.add(child2)
            child1.parents.add(parent)
            child2.parents.add(parent)

            // Add 100 queries to child1
            repeat(100) {
                child1.queries.add(Embedding(rawText = "c1_$it", distilledText = "", values = floatArrayOf()))
            }
            // Add 1 query to child2 (marginal: 1 < 100 * 0.05 = 5)
            child2.queries.add(Embedding(rawText = "c2_0", distilledText = "", values = floatArrayOf()))

            ops.collapseMarginalNodes(root)

            // Assert Child2 is collapsed and queries merged to Parent
            assertFalse(parent.children.contains(child2))
            assertTrue(child2.parents.isEmpty())
            assertEquals(1, parent.queries.size)
            assertEquals("c2_0", parent.queries[0].rawText)

            // Assert Child1 is retained since it is not marginal
            assertTrue(parent.children.contains(child1))
            assertEquals(100, child1.queries.size)
        } finally {
            config.formalism.collapseMarginalRatio = originalCollapseRatio
        }
    }
}
