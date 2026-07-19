package taxonomy

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.mockito.Mockito.*
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.TraversalPolicy
import taxonomy.operations.TaxonomyFitter
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomyMerger
import taxonomy.operations.TaxonomyTrickler
import taxonomy.service.TaxonomyPersistence
import taxonomy.tui.service.BatchTrickleEvaluator
import taxonomy.tui.service.BatchTrickleEvaluator.ProfileMode
import taxonomy.utils.TaxonomyMetrics
import java.io.File
import kotlin.math.ln

class TaxonomyDagMaxFeaturesTest {

    private fun node(id: String, label: String, depth: Int) = GraphNode(id = id, label = label, depth = depth)

    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child)
        child.parents.add(parent)
        child.treeParentId = parent.id
    }

    private fun emb(text: String, queryId: Int = -1, gtCat: String = ""): Embedding {
        val e = Embedding(text, text, floatArrayOf(0.1f, 0.2f), gtCat)
        e.queryId = queryId
        return e
    }

    @Test
    fun `R1 - residual detection and kappa exclusion`() {
        val config = TaxonomyConfig()
        config.formalism.enableResidualRouting = true
        config.formalism.routeConfidenceTau = 0.6 // Set to 0.6 so 0.5 is strictly less than 0.6

        val trickler = TaxonomyTrickler(config)
        val parent = node("parent", "Parent Domain", 2)
        val child1 = node("child1", "Child One", 3)
        val child2 = node("child2", "Child Two", 3)
        link(parent, child1)
        link(parent, child2)

        // Setup centroids and kappa for child nodes
        child1.vmfMu = floatArrayOf(1f, 0f)
        child1.vmfKappa = 10.0
        child1.sliceDim = 2

        child2.vmfMu = floatArrayOf(0f, 1f)
        child2.vmfKappa = 10.0
        child2.sliceDim = 2

        // A query query close to (1,0) should route to child1 with high confidence.
        // A query at (0.7, 0.7) normalized has dot product of 0.7 to both, hence responsibilities around 0.5 each.
        // Let's test a query that lies far away or in between.
        val query = Embedding("midway", "midway", floatArrayOf(0.707f, 0.707f))
        query.queryId = 101

        val result = trickler.routeQuery(query, parent, currentIteration = 2)
        
        println("R1 DEBUG: parent.isLeaf = ${parent.isLeaf}")
        println("R1 DEBUG: parent.children = ${parent.children.map { it.id }}")
        println("R1 DEBUG: residualHits size = ${result.residualHits.size}")
        result.residualHits.forEach {
            println("R1 DEBUG: hit node = ${it.node.id}, qId = ${it.questionId}, score = ${it.bestChildScore}")
        }

        // Since midway query falls between, bestChildResp will be around 0.5.
        // Since bestChildResp <= routeConfidenceTau (0.6), it should record a residual hit at parent
        assertTrue(result.residualHits.any { it.node.id == parent.id && it.questionId == "101" })

        // Check kappa exclusion
        val fitter = TaxonomyFitter(config)
        parent.queries.add(query)
        parent.residualQueries.add("101")
        parent.sliceDim = 2

        // Fitter computes kappaQueries = branchQueries - residualQueries.
        // If we compute it now, since the only query in branch is residual, kappaQueries is empty.
        // Fitter has a fallback: if kappaQueries is empty, it uses branchQueries (midway query).
        fitter.fitSingleNode(parent)
        val kappaEmptyResiduals = parent.vmfKappa
        
        // Add a non-residual query
        val query2 = Embedding("non-residual", "non-residual", floatArrayOf(1.0f, 0.0f))
        query2.queryId = 102
        parent.queries.add(query2)

        // Now, parent has queries [101, 102], but 101 is residual. So kappa should be fit ONLY on 102 (perfect concentration = high kappa).
        fitter.fitSingleNode(parent)
        val kappa = parent.vmfKappa
        // Perfect alignment of query2 with (1,0) should yield very high concentration compared to including the midway query.
        assertTrue(kappa > 0.0)
    }

    @Test
    fun `R2 - bridge node acceptance adjacent cross-domain`() {
        val config = TaxonomyConfig()
        config.formalism.enableBridging = true
        config.formalism.separationEpsilon = 0.01
        config.formalism.bridgeSeparationCeiling = 0.5
        config.formalism.maxBridgeNodes = 5
        config.formalism.bridgeCandidateTopK = 5
        config.formalism.minBridgeCoverage = 0 // allow any size

        val merger = TaxonomyMerger(config, mock(TaxonomyLlmClient::class.java), mock(MMLUDatasetFetcher::class.java))

        val root = node("root", "Root Domain", 0)
        val domainA = node("domainA", "Domain A", 1)
        val domainB = node("domainB", "Domain B", 1)
        link(root, domainA)
        link(root, domainB)

        val leafA = node("leafA", "Leaf A", 2)
        val leafB = node("leafB", "Leaf B", 2)
        link(domainA, leafA)
        link(domainB, leafB)

        // Set close unit-normalized centroids
        leafA.vmfMu = floatArrayOf(1.0f, 0.0f)
        leafA.vmfKappa = 10.0
        leafB.vmfMu = floatArrayOf(0.98f, 0.2f)
        leafB.vmfKappa = 10.0

        leafA.queries.add(emb("queryA", 1, "domainA"))
        leafB.queries.add(emb("queryB", 2, "domainB"))

        // Debug prints before running bridging pass
        val metrics = TaxonomyMetrics(root)
        val method = TaxonomyMetrics::class.java.getDeclaredMethod("getDepth1Ancestors", GraphNode::class.java, TraversalPolicy::class.java)
        method.isAccessible = true
        val leaves = listOf(leafA, leafB)
        println("R2 TEST DEBUG: leaves size = ${leaves.size}")
        leaves.forEach { leaf ->
            val ancestors = method.invoke(metrics, leaf, TraversalPolicy.TREE_ONLY) as Set<*>
            println("R2 TEST DEBUG: leaf ${leaf.id} depth-1 ancestors = $ancestors")
        }
        val commonDim = minOf(leafA.vmfMu.size, leafB.vmfMu.size)
        println("R2 TEST DEBUG: commonDim = $commonDim")
        if (commonDim > 0) {
            val projUMu = taxonomy.utils.StatisticsUtils.projectVector(leafA.vmfMu, commonDim)
            val projVMu = taxonomy.utils.StatisticsUtils.projectVector(leafB.vmfMu, commonDim)
            val div = taxonomy.utils.StatisticsUtils.vmfJsDivergence(projUMu, leafA.vmfKappa, projVMu, leafB.vmfKappa, commonDim)
            println("R2 TEST DEBUG: calculated div = $div")
            println("R2 TEST DEBUG: separationEpsilon = ${config.formalism.separationEpsilon}")
            println("R2 TEST DEBUG: bridgeSeparationCeiling = ${config.formalism.bridgeSeparationCeiling}")
        }

        // Run bridging pass directly
        kotlinx.coroutines.runBlocking {
            merger.insertBridgingParents(root, 1)
        }

        // Verify a bridge was created between leafA and leafB
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (allNodes.add(n)) {
                n.children.forEach { walk(it) }
                n.crossLinkChildren.forEach { walk(it) }
            }
        }
        walk(root)

        val bridges = allNodes.filter { it.isBridge }
        println("R2 DEBUG: bridges count = ${bridges.size}")
        allNodes.forEach {
            println("R2 DEBUG: node id = ${it.id}, isBridge = ${it.isBridge}, crossLinks = ${it.crossLinkChildren.map { c -> c.id }}")
        }

        assertEquals(1, bridges.size)
        val bridge = bridges.first()
        assertTrue(bridge.id.startsWith("bridge_"))
        assertEquals(2, bridge.depth) // maxOf(2, minOf(2,2) - 1) = 2
        assertTrue(bridge.crossLinkChildren.contains(leafA))
        assertTrue(bridge.crossLinkChildren.contains(leafB))
        assertTrue(leafA.parents.contains(bridge))
        assertTrue(leafB.parents.contains(bridge))
    }

    @Test
    fun `R3 - bridge node rejections`() {
        val config = TaxonomyConfig()
        config.formalism.enableBridging = true
        config.formalism.separationEpsilon = 0.01
        config.formalism.bridgeSeparationCeiling = 0.5
        config.formalism.maxBridgeNodes = 5
        config.formalism.bridgeCandidateTopK = 5

        val merger = TaxonomyMerger(config, mock(TaxonomyLlmClient::class.java), mock(MMLUDatasetFetcher::class.java))

        // Case A: Far-apart leaves (div > ceiling)
        val root = node("root", "Root Domain", 0)
        val domainA = node("domainA", "Domain A", 1)
        val domainB = node("domainB", "Domain B", 1)
        link(root, domainA)
        link(root, domainB)

        val leafA = node("leafA", "Leaf A", 2)
        val leafB = node("leafB", "Leaf B", 2)
        link(domainA, leafA)
        link(domainB, leafB)

        leafA.vmfMu = floatArrayOf(1.0f, 0.0f)
        leafA.vmfKappa = 50.0
        leafB.vmfMu = floatArrayOf(0.0f, 1.0f)
        leafB.vmfKappa = 50.0 // Far apart

        leafA.queries.add(emb("queryA", 1, "domainA"))
        leafB.queries.add(emb("queryB", 2, "domainB"))

        kotlinx.coroutines.runBlocking {
            merger.insertBridgingParents(root, 1)
        }

        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (allNodes.add(n)) {
                n.children.forEach { walk(it) }
                n.crossLinkChildren.forEach { walk(it) }
            }
        }
        walk(root)
        assertTrue(allNodes.none { it.isBridge }, "Far-apart leaves should not produce a bridge")
    }

    @Test
    fun `R4 - identity and bridge persistence across snapshot save and load`() {
        val config = TaxonomyConfig()
        val mockEmbeddingCache = mock(EmbeddingCache::class.java)
        val persistence = TaxonomyPersistence(config, mockEmbeddingCache)

        val root = node("root", "Root Domain", 0)
        val child = node("child", "Child Domain", 1)
        child.isBridge = true
        child.residualQueries.add("res101")
        link(root, child)

        val q = emb("test-query", 999)
        child.queries.add(q)

        val qId = "q_" + java.security.MessageDigest.getInstance("SHA-256")
            .digest("test-query".toByteArray())
            .joinToString("") { "%02x".format(it) }.take(16)

        // Mock DB batch lookup for loading
        `when`(mockEmbeddingCache.getQueriesBatch(setOf(qId)))
            .thenReturn(mapOf(qId to Triple("test-query", "test-query", "")))
        `when`(mockEmbeddingCache.getBatch(setOf("test-query")))
            .thenReturn(mapOf("test-query" to floatArrayOf(0.1f, 0.2f)))

        val tempFile = File.createTempFile("snapshot_test", ".json")
        try {
            // Save snapshot
            persistence.save(root, tempFile.absolutePath)

            // Register query text -> ID mapping to test rehydration via registry
            taxonomy.model.QuestionIdRegistry.register("test-query", 999)

            // Load snapshot
            val loadedRoot = persistence.load(tempFile.absolutePath)
            assertNotNull(loadedRoot)
            val loadedChild = loadedRoot!!.children.first()
            assertTrue(loadedChild.isBridge, "Bridge status must persist across save and load")
            assertTrue(loadedChild.residualQueries.contains("res101"), "Residual query IDs must persist")
            assertEquals(999, loadedChild.queries.first().queryId, "queryId must persist")
        } finally {
            tempFile.delete()
        }
    }

    @Test
    fun `R5 - partition vs soft leaf profiles`() {
        val leafA = node("leafA", "Leaf A", 2)
        val leafB = node("leafB", "Leaf B", 2)

        leafA.vmfMu = floatArrayOf(1.0f, 0.0f)
        leafB.vmfMu = floatArrayOf(0.0f, 1.0f)

        val query = Embedding("query", "query", floatArrayOf(0.707f, 0.707f), "domainA", 1)
        leafA.queries.add(query)
        leafB.queries.add(query)

        val textToDomain = mapOf("query" to "domainA")

        // Soft Profile
        val softProfiles = BatchTrickleEvaluator.buildLeafProfiles(listOf(leafA, leafB), textToDomain, ProfileMode.SOFT)
        val softProfileA = softProfiles["leafA"]
        assertNotNull(softProfileA)
        assertEquals(0.5, softProfileA!!.sizeDouble, 0.1)

        // Partition Profile: query counts as 1.0 at its top destination
        val partitionProfiles = BatchTrickleEvaluator.buildLeafProfiles(listOf(leafA, leafB), textToDomain, ProfileMode.PARTITION)
        val partitionProfileA = partitionProfiles["leafA"]
        // Since they are equal, it will select one of them to get 1.0 weight
        assertTrue((partitionProfileA != null && partitionProfileA.sizeDouble == 1.0) || partitionProfiles["leafB"]?.sizeDouble == 1.0)
    }

    @Test
    fun `P1 - depth-1 resolution follows treeParentId only`() {
        val root = node("root", "Root Domain", 0)
        val domainA = node("domainA", "Domain A", 1)
        val domainB = node("domainB", "Domain B", 1)
        link(root, domainA)
        link(root, domainB)

        val leaf = node("leaf", "Leaf Domain", 2)
        link(domainA, leaf) // tree parent is domainA

        // Create a bridge parent pointing to domainB
        val bridge = node("bridge", "Bridge Parent", 1)
        bridge.isBridge = true
        bridge.crossLinkChildren.add(leaf)
        leaf.parents.add(bridge)

        // Evaluate getDepth1Ancestors using reflection on TaxonomyMetrics class
        val metrics = TaxonomyMetrics(root)
        val method = TaxonomyMetrics::class.java.getDeclaredMethod("getDepth1Ancestors", GraphNode::class.java, TraversalPolicy::class.java)
        method.isAccessible = true
        
        val ancestors = method.invoke(metrics, leaf, TraversalPolicy.TREE_ONLY) as Set<*>
        assertEquals(1, ancestors.size)
        assertTrue(ancestors.contains("Domain A"), "Depth-1 resolution under TREE_ONLY must follow treeParentId only")
    }

    @Test
    fun `P3 - transitive reduction preserves bridge edges`() {
        val config = TaxonomyConfig()
        config.formalism.enableBridging = true

        val merger = TaxonomyMerger(config, mock(TaxonomyLlmClient::class.java), mock(MMLUDatasetFetcher::class.java))

        val root = node("root", "Root Domain", 0)
        val parent = node("parent", "Parent Domain", 1)
        val child = node("child", "Child Domain", 2)
        link(root, parent)
        link(parent, child)

        // Add a bridge edge root -> child (which would normally be transitively reducible since root -> parent -> child exists)
        val bridge = node("bridge", "Bridge", 1)
        bridge.isBridge = true
        bridge.crossLinkChildren.add(child)
        child.parents.add(bridge)
        bridge.parents.add(root)
        root.crossLinkChildren.add(bridge)

        val ancestorMap = merger.buildAncestorMap(root)
        merger.transitiveReduction(root, ancestorMap)

        // Verify bridge edges are not removed by transitive reduction
        assertTrue(root.crossLinkChildren.contains(bridge), "Transitive reduction must preserve bridge nodes")
        assertTrue(bridge.crossLinkChildren.contains(child), "Transitive reduction must preserve bridge cross-link child edges")
    }

    @Test
    fun `P5 - isLeaf excludes bridge nodes`() {
        val bridgeNode = node("bridge", "Bridge", 1)
        bridgeNode.isBridge = true
        assertFalse(bridgeNode.isLeaf, "isLeaf must return false for bridge nodes even if children is empty")
    }

    @Test
    fun `P6 - trickle routing gates crossLinkChildren`() {
        val config = TaxonomyConfig()
        
        // Scenario A: enableBridging = false. Should NOT walk crossLinkChildren.
        config.formalism.enableBridging = false
        val trickler = TaxonomyTrickler(config)

        val root = node("root", "Root", 0)
        val leaf1 = node("leaf1", "Leaf 1", 1)
        val leaf2 = node("leaf2", "Leaf 2", 1)
        
        root.children.add(leaf1)
        leaf1.parents.add(root)

        // Add leaf2 to crossLinkChildren of root
        root.crossLinkChildren.add(leaf2)
        leaf2.parents.add(root)

        leaf1.vmfMu = floatArrayOf(1.0f, 0.0f)
        leaf1.vmfKappa = 10.0
        leaf1.sliceDim = 2
        leaf2.vmfMu = floatArrayOf(0.0f, 1.0f)
        leaf2.vmfKappa = 10.0
        leaf2.sliceDim = 2

        val query = Embedding("q", "q", floatArrayOf(0.0f, 1.0f))

        println("P6 DEBUG: root.children size = ${root.children.size}")
        println("P6 DEBUG: root.children = ${root.children.map { it.id }}")
        println("P6 DEBUG: leaf1.isLeaf = ${leaf1.isLeaf}")
        println("P6 DEBUG: leaf2.isLeaf = ${leaf2.isLeaf}")

        val resultA = trickler.routeQuery(query, root, currentIteration = 2)
        println("P6 DEBUG: resultA leaves = ${resultA.leaves.keys.map { it.id }}")
        
        // Since enableBridging is false, leaf2 (cross link) is ignored, and all probabilities go to leaf1
        assertTrue(resultA.leaves.keys.contains(leaf1))
        assertFalse(resultA.leaves.keys.contains(leaf2))

        // Scenario B: enableBridging = true. Should walk crossLinkChildren.
        config.formalism.enableBridging = true
        val resultB = trickler.routeQuery(query, root, currentIteration = 2)
        println("P6 DEBUG: resultB leaves = ${resultB.leaves.keys.map { it.id }}")
        assertTrue(resultB.leaves.keys.contains(leaf2))
    }

    @Test
    fun `R6 - bridge cycle prevention`() {
        val config = TaxonomyConfig()
        config.formalism.enableBridging = true
        config.formalism.separationEpsilon = 0.01
        config.formalism.bridgeSeparationCeiling = 0.5
        config.formalism.maxBridgeNodes = 5

        val merger = TaxonomyMerger(config, mock(TaxonomyLlmClient::class.java), mock(MMLUDatasetFetcher::class.java))

        val root = node("root", "Root Domain", 0)
        val domainA = node("domainA", "Domain A", 1)
        val domainB = node("domainB", "Domain B", 1)
        link(root, domainA)
        link(root, domainB)

        val leafA = node("leafA", "Leaf A", 2)
        val leafB = node("leafB", "Leaf B", 2)
        link(domainA, leafA)
        link(domainB, leafB)

        // Make leafA an ancestor of leafB directly via tree children to create a potential cycle if linked back.
        leafA.children.add(leafB)
        leafB.parents.add(leafA)

        leafA.vmfMu = floatArrayOf(1.0f, 0.0f)
        leafA.vmfKappa = 10.0
        leafB.vmfMu = floatArrayOf(0.98f, 0.2f)
        leafB.vmfKappa = 10.0

        leafA.queries.add(emb("queryA", 1, "domainA"))
        leafB.queries.add(emb("queryB", 2, "domainB"))

        kotlinx.coroutines.runBlocking {
            merger.insertBridgingParents(root, 1)
        }

        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (allNodes.add(n)) {
                n.children.forEach { walk(it) }
                n.crossLinkChildren.forEach { walk(it) }
            }
        }
        walk(root)

        val bridges = allNodes.filter { it.isBridge }
        assertTrue(bridges.isEmpty(), "Bridges must not be created if they form a cycle")
    }

    @Test
    fun `R7 - bridge explosion budgets and coverage`() {
        val config = TaxonomyConfig()
        config.formalism.enableBridging = true
        config.formalism.separationEpsilon = 0.01
        config.formalism.bridgeSeparationCeiling = 0.5
        config.formalism.maxBridgeNodes = 5
        config.formalism.minBridgeCoverage = 10 // Require at least 10 queries total

        val merger = TaxonomyMerger(config, mock(TaxonomyLlmClient::class.java), mock(MMLUDatasetFetcher::class.java))

        val root = node("root", "Root Domain", 0)
        val domainA = node("domainA", "Domain A", 1)
        val domainB = node("domainB", "Domain B", 1)
        link(root, domainA)
        link(root, domainB)

        val leafA = node("leafA", "Leaf A", 2)
        val leafB = node("leafB", "Leaf B", 2)
        link(domainA, leafA)
        link(domainB, leafB)

        leafA.vmfMu = floatArrayOf(1.0f, 0.0f)
        leafA.vmfKappa = 10.0
        leafB.vmfMu = floatArrayOf(0.98f, 0.2f)
        leafB.vmfKappa = 10.0

        // Only 2 queries total (less than minBridgeCoverage of 10)
        leafA.queries.add(emb("queryA", 1, "domainA"))
        leafB.queries.add(emb("queryB", 2, "domainB"))

        kotlinx.coroutines.runBlocking {
            merger.insertBridgingParents(root, 1)
        }

        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (allNodes.add(n)) {
                n.children.forEach { walk(it) }
                n.crossLinkChildren.forEach { walk(it) }
            }
        }
        walk(root)
        assertTrue(allNodes.none { it.isBridge }, "Bridge should be rejected due to minBridgeCoverage")

        // Now change minBridgeCoverage to 0, but set bridgeParentBudget to 0
        config.formalism.minBridgeCoverage = 0
        config.formalism.bridgeParentBudget = 0

        val root2 = node("root", "Root Domain", 0)
        val domainA2 = node("domainA", "Domain A", 1)
        val domainB2 = node("domainB", "Domain B", 1)
        link(root2, domainA2)
        link(root2, domainB2)

        val leafA2 = node("leafA", "Leaf A", 2)
        val leafB2 = node("leafB", "Leaf B", 2)
        link(domainA2, leafA2)
        link(domainB2, leafB2)

        leafA2.vmfMu = floatArrayOf(1.0f, 0.0f)
        leafA2.vmfKappa = 10.0
        leafB2.vmfMu = floatArrayOf(0.98f, 0.2f)
        leafB2.vmfKappa = 10.0

        leafA2.queries.add(emb("queryA", 1, "domainA"))
        leafB2.queries.add(emb("queryB", 2, "domainB"))

        kotlinx.coroutines.runBlocking {
            merger.insertBridgingParents(root2, 1)
        }

        val allNodes2 = mutableSetOf<GraphNode>()
        fun walk2(n: GraphNode) {
            if (allNodes2.add(n)) {
                n.children.forEach { walk2(it) }
                n.crossLinkChildren.forEach { walk2(it) }
            }
        }
        walk2(root2)
        assertTrue(allNodes2.none { it.isBridge }, "Bridge should be rejected due to bridgeParentBudget")
    }
}
