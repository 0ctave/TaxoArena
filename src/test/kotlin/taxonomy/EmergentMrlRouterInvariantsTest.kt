package taxonomy

import taxonomy.*
import taxonomy.model.*
import taxonomy.config.*
import taxonomy.operations.*
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest

@SpringBootTest(
    classes = [org.eclipse.lmos.arc.app.TaxoAdaptApplication::class],
    properties = [
        "taxoadapt.execution.enable-tui=false",
        "taxoadapt.execution.run-batch=false",
        "taxoadapt.execution.start-service=false"
    ]
)
class EmergentMrlRouterInvariantsTest {

    @Autowired
    private lateinit var config: TaxonomyConfig

    @Autowired
    private lateinit var ops: TaxonomyOperations

    @Autowired
    private lateinit var trickler: TaxonomyTrickler

    @Autowired
    private lateinit var fitter: TaxonomyFitter

    @Autowired
    private lateinit var splitter: TaxonomySplitter

    @Test
    fun `Test 1 - Leaves do not swallow all queries`() {
        val root = GraphNode(label = "Root", depth = 0)
        val leafA = GraphNode(label = "Leaf A", depth = 1).apply { treeParentId = root.id }
        val leafB = GraphNode(label = "Leaf B", depth = 1).apply { treeParentId = root.id }
        root.children.addAll(listOf(leafA, leafB))
        leafA.parents.add(root)
        leafB.parents.add(root)

        // Set distinct vMF centroids for separation
        val d = 128
        leafA.vmfMu = FloatArray(d) { if (it == 0) 1.0f else 0.0f }
        leafA.vmfKappa = 100.0
        leafA.sliceDim = d
        leafB.vmfMu = FloatArray(d) { if (it == 1) 1.0f else 0.0f }
        leafB.vmfKappa = 100.0
        leafB.sliceDim = d

        // Query closer to A
        val vecA = FloatArray(d) { if (it == 0) 0.99f else if (it == 1) 0.01f else 0.0f }
        val embA = Embedding("Query A", "Query A", vecA, "A")
        GraphNode.registerEmbedding(embA)

        // Route
        val routeResult = trickler.routeQuery(embA, root, currentIteration = 2)
        val destinations = routeResult.leaves.keys.toList()

        assertTrue(destinations.contains(leafA))
        assertFalse(destinations.contains(leafB))
    }

    @Test
    fun `Test 2 - Internal ancestors hold no hard membership`() {
        val root = GraphNode(label = "Root", depth = 0)
        val mid = GraphNode(label = "Mid", depth = 1).apply { treeParentId = root.id }
        val leaf = GraphNode(label = "Leaf", depth = 2).apply { treeParentId = mid.id }

        root.children.add(mid)
        mid.parents.add(root)
        mid.children.add(leaf)
        leaf.parents.add(mid)

        val d = 128
        mid.sliceDim = d
        mid.vmfMu = FloatArray(d) { if (it == 0) 1.0f else 0.0f }
        mid.vmfKappa = 50.0
        leaf.sliceDim = d
        leaf.vmfMu = FloatArray(d) { if (it == 0) 1.0f else 0.0f }
        leaf.vmfKappa = 50.0

        val emb = Embedding("Test Query", "Test Query", FloatArray(d) { if (it == 0) 1.0f else 0.0f }, "")
        GraphNode.registerEmbedding(emb)

        // Reassign
        kotlinx.coroutines.runBlocking {
            ops.reassignQueries(root, listOf(emb), groundTruthMap = emptyMap(), currentIteration = 2)
        }

        // Mid and root queries lists must be empty (leaf-only ownership)
        assertTrue(mid.queries.isEmpty(), "Internal mid node queries must be empty")
        assertTrue(root.queries.isEmpty(), "Root queries must be empty")
        assertTrue(leaf.queries.contains(emb), "Leaf must hold the query")
    }

    @Test
    fun `Test 3 - Internal fit still sees descendant mass`() {
        val root = GraphNode(label = "Root", depth = 0)
        val mid = GraphNode(label = "Mid", depth = 1).apply { treeParentId = root.id }
        val leaf = GraphNode(label = "Leaf", depth = 2).apply { treeParentId = mid.id }

        root.children.add(mid)
        mid.parents.add(root)
        mid.children.add(leaf)
        leaf.parents.add(mid)

        val d = 128
        mid.sliceDim = d
        leaf.sliceDim = d
        leaf.vmfMu = FloatArray(d) { if (it == 0) 1.0f else 0.0f }
        leaf.vmfKappa = 50.0

        val emb = Embedding("Test Query", "Test Query", FloatArray(d) { if (it == 0) 1.0f else 0.0f }, "")
        GraphNode.registerEmbedding(emb)

        leaf.queryWeights[emb.rawText] = 0.8
        leaf.queries.add(emb)

        // Region query weights of mid should collect the leaf's query weights
        val method = fitter.javaClass.getDeclaredMethod("getRegionQueryWeights", GraphNode::class.java)
        method.isAccessible = true
        @Suppress("UNCHECKED_CAST")
        val weights = method.invoke(fitter, mid) as Map<String, Double>

        assertEquals(0.8, weights[emb.rawText])
        assertEquals(1, mid.getRecursiveQueryCount())
    }

    @Test
    fun `Test 4 - No double-count under cross-links`() {
        val root = GraphNode(label = "Root", depth = 0)
        val parentA = GraphNode(label = "Parent A", depth = 1).apply { treeParentId = root.id }
        val parentB = GraphNode(label = "Parent B", depth = 1).apply { treeParentId = root.id }
        val leafShared = GraphNode(label = "Shared Leaf", depth = 2).apply { treeParentId = parentA.id }

        root.children.addAll(listOf(parentA, parentB))
        parentA.parents.add(root)
        parentB.parents.add(root)

        parentA.children.add(leafShared)
        leafShared.parents.add(parentA)

        // Cross-link parentB -> leafShared
        parentB.crossLinkChildren.add(leafShared)
        leafShared.parents.add(parentB)

        val d = 128
        leafShared.sliceDim = d
        val emb = Embedding("Query", "Query", FloatArray(d) { 0.0f }, "")
        GraphNode.registerEmbedding(emb)

        leafShared.queryWeights[emb.rawText] = 1.0
        leafShared.queries.add(emb)

        // Grandparent (root) region query weights should count the leaf exactly once
        val method = fitter.javaClass.getDeclaredMethod("getRegionQueryWeights", GraphNode::class.java)
        method.isAccessible = true
        @Suppress("UNCHECKED_CAST")
        val weights = method.invoke(fitter, root) as Map<String, Double>

        assertEquals(1.0, weights[emb.rawText])
    }

    @Test
    fun `Test 5 - Split conserves mass exactly`() {
        val parent = GraphNode(label = "Parent", depth = 1)
        val d = 128
        parent.sliceDim = d
        parent.vmfMu = FloatArray(d) { if (it == 0) 1.0f else 0.0f }
        parent.vmfKappa = 10.0

        // Add 90 queries to clear split gate
        val queries = (1..90).map {
            Embedding("Q$it", "Q$it", FloatArray(d) { idx -> if (idx == 0) 1.0f else 0.0f }, "")
        }
        queries.forEach {
            GraphNode.registerEmbedding(it)
            parent.queries.add(it)
            parent.queryWeights[it.rawText] = 1.0
        }

        // Run split
        kotlinx.coroutines.runBlocking {
            splitter.splitSingleNode(parent)
        }

        // If split occurred, assert that the sum of child weights + residual equals the original parent weight (90.0)
        if (parent.children.isNotEmpty()) {
            var sumChildWeights = 0.0
            queries.forEach { q ->
                val childSum = parent.children.sumOf { it.queryWeights[q.rawText] ?: 0.0 }
                val residual = parent.queryWeights[q.rawText] ?: 0.0
                assertEquals(1.0, childSum + residual, 1e-9)
                sumChildWeights += childSum + residual
            }
            assertEquals(90.0, sumChildWeights, 1e-9)
        }
    }

    @Test
    fun `Test 6 - Composite internal node is NOT split from region mass`() {
        val root = GraphNode(label = "Root", depth = 0)
        val mid = GraphNode(label = "Mid", depth = 1).apply { treeParentId = root.id }
        val leafA = GraphNode(label = "Leaf A", depth = 2).apply { treeParentId = mid.id }
        val leafB = GraphNode(label = "Leaf B", depth = 2).apply { treeParentId = mid.id }

        root.children.add(mid)
        mid.parents.add(root)
        mid.children.addAll(listOf(leafA, leafB))
        leafA.parents.add(mid)
        leafB.parents.add(mid)

        val d = 128
        mid.sliceDim = d
        leafA.sliceDim = d
        leafB.sliceDim = d

        // Populate leaves with queries (large region mass)
        val queries = (1..100).map {
            Embedding("Q$it", "Q$it", FloatArray(d) { 0.0f }, "")
        }
        queries.forEach {
            GraphNode.registerEmbedding(it)
            leafA.queries.add(it)
            leafA.queryWeights[it.rawText] = 1.0
        }

        // Mid itself has empty local residual bucket
        assertTrue(mid.queryWeights.isEmpty(), "Mid local queryWeights must be empty")

        // Try to split mid
        kotlinx.coroutines.runBlocking {
            splitter.splitSingleNode(mid)
        }

        // Mid must not split since its local queryWeights is empty
        assertTrue(mid.children.size == 2, "Mid children list size must remain 2 (no new children spawned)")
        assertTrue(mid.children.contains(leafA))
        assertTrue(mid.children.contains(leafB))
    }
}
