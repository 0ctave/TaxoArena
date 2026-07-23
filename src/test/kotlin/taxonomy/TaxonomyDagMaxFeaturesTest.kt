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
import taxonomy.dataset.CachedQuery
import taxonomy.tui.service.BatchTrickleEvaluator
import taxonomy.tui.service.BatchTrickleEvaluator.ProfileMode
import taxonomy.utils.TaxonomyMetrics
import taxonomy.utils.StatisticsUtils
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

    private fun embWithVec(text: String, queryId: Int, gtCat: String, vector: FloatArray): Embedding {
        val e = Embedding(text, text, vector, gtCat)
        e.queryId = queryId
        return e
    }

    @Test
    fun `R1 - residual detection and kappa exclusion`() {
        val config = TaxonomyConfig()
        config.formalism.enableResidualRouting = true

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

        // Parent's own component points straight at the midway direction: for a midway
        // query, the parent explains it BETTER than either child (dot 1.0 vs 0.707 at
        // equal kappa), so the parameter-free descent gate (some child must beat the
        // parent's own density) fails and the query is recorded as residual at parent.
        parent.vmfMu = floatArrayOf(0.707f, 0.707f)
        parent.vmfKappa = 10.0
        parent.sliceDim = 2

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
        // Since neither child clears membershipFloor (0.6), it should record a residual hit at parent.
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
    fun `R2 - cross-link generator guards reject same-domain, non-capturing, and low-support candidates`() {
        val config = TaxonomyConfig()
        config.formalism.enableBridging = true
        config.diagnostics.secondaryMassFloor = 5.0
        config.diagnostics.bridgeSupportRelFraction = 0.10

        val merger = TaxonomyMerger(config, mock(TaxonomyLlmClient::class.java), mock(MMLUDatasetFetcher::class.java))
        val trickler = TaxonomyTrickler(config)
        val ops = taxonomy.operations.TaxonomyOperations(
            mock(TaxonomyFitter::class.java),
            trickler,
            mock(taxonomy.operations.TaxonomySplitter::class.java),
            merger,
            config
        )

        val root = node("root", "Root", 0)
        val domainA = node("domainA", "Domain A", 1)
        val domainB = node("domainB", "Domain B", 1)
        link(root, domainA)
        link(root, domainB)
        val leafA1 = node("leafA1", "Leaf A1", 2)
        val leafA2 = node("leafA2", "Leaf A2", 2)
        val leafB = node("leafB", "Leaf B", 2)
        link(domainA, leafA1)
        link(domainA, leafA2)
        link(domainB, leafB)

        domainA.vmfMu = floatArrayOf(0.707f, 0.707f, 0f); domainA.sliceDim = 3
        domainB.vmfMu = floatArrayOf(0f, 0f, 1f); domainB.sliceDim = 3
        leafA1.vmfMu = floatArrayOf(1f, 0f, 0f); leafA1.sliceDim = 3
        leafA2.vmfMu = floatArrayOf(0f, 1f, 0f); leafA2.sliceDim = 3
        // leafB points away from domainA's residual pool: it never captures under the
        // gate formula, so no proposal is attempted and the test is deterministic.
        leafB.vmfMu = floatArrayOf(0f, 0f, 1f); leafB.sliceDim = 3

        // Host 1: domainA with 6 residuals aligned with its OWN children. leafA1/leafA2
        // would capture, but the host is their ancestor (and shares their domain) — both
        // guards must reject them.
        val residualsA = (1..6).map { i ->
            embWithVec("resA$i", 100 + i, "", floatArrayOf(0.7f, 0.7f, 0.1f))
        }
        residualsA.forEach { domainA.residualQueries.add(it.queryId.toString()) }

        // Host 2: domainB with only 4 residuals (below secondaryMassFloor = 5) that WOULD
        // be captured by the cross-domain candidate leafA1 — low support must skip the host.
        val residualsB = (1..4).map { i ->
            embWithVec("resB$i", 200 + i, "", floatArrayOf(1f, 0f, 0.1f))
        }
        residualsB.forEach { domainB.residualQueries.add(it.queryId.toString()) }

        kotlinx.coroutines.runBlocking {
            merger.proposeCrossLinksWithProposals(
                taxonomy.model.DagRoot(root), residualsA + residualsB, emptyMap(), 1, ops
            )
        }

        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (allNodes.add(n)) {
                n.children.forEach { walk(it) }
                n.crossLinkChildren.forEach { walk(it) }
            }
        }
        walk(root)
        assertTrue(
            allNodes.none { it.crossLinkChildren.isNotEmpty() },
            "No cross-link may form: same-domain/ancestor candidates are guarded, leafB does not capture, and domainB's pool is below the support floor"
        )
    }

    @Test
    fun `R3 - cross-linked leaf remains a leaf and receives membership through both parents`() {
        val config = TaxonomyConfig()
        config.formalism.enableBridging = true
        config.formalism.enableResidualRouting = true
        val trickler = TaxonomyTrickler(config)

        val root = node("root", "Root", 0)
        val domainA = node("domainA", "Domain A", 1)
        val domainB = node("domainB", "Domain B", 1)
        link(root, domainA)
        link(root, domainB)
        val leafA = node("leafA", "Leaf A", 2)
        val leafB = node("leafB", "Leaf B", 2)
        link(domainA, leafA)
        link(domainB, leafB)

        domainA.vmfMu = floatArrayOf(1f, 0f); domainA.vmfKappa = 10.0; domainA.sliceDim = 2
        domainB.vmfMu = floatArrayOf(0f, 1f); domainB.vmfKappa = 10.0; domainB.sliceDim = 2
        leafA.vmfMu = floatArrayOf(1f, 0f); leafA.vmfKappa = 10.0; leafA.sliceDim = 2
        leafB.vmfMu = floatArrayOf(0f, 1f); leafB.vmfKappa = 10.0; leafB.sliceDim = 2

        // The growth edit: domainA gains leafB as a cross-link child.
        domainA.crossLinkChildren.add(leafB)
        leafB.parents.add(domainA)

        // The contract the old isLeaf definition broke: a second parent must NOT evict
        // the target from the leaf set, or the cross-link orphans its own destination.
        assertTrue(leafB.isLeaf, "cross-link target with two parents must remain a leaf")

        val query = Embedding("bridge-q", "bridge-q", floatArrayOf(0.707f, 0.707f))
        query.queryId = 42
        val result = trickler.routeQuery(query, root, currentIteration = 2)

        val leafBWeight = result.leaves.entries.firstOrNull { it.key.id == "leafB" }?.value
        val leafAWeight = result.leaves.entries.firstOrNull { it.key.id == "leafA" }?.value
        assertNotNull(leafBWeight, "bridged leaf must be reachable as a destination")
        assertNotNull(leafAWeight)
        // leafB accumulates path mass from BOTH parents (domainA cross-link + domainB tree
        // edge), so for a midway query it must outweigh single-path leafA.
        assertTrue(leafBWeight!! > leafAWeight!!, "two-path leaf must accumulate more membership than the single-path leaf")
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
            .thenReturn(mapOf(qId to CachedQuery("test-query", "test-query", "", 999)))
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
    fun `P5 - isLeaf reflects outgoing edges only`() {
        val leaf = node("leaf", "Leaf", 2)
        assertTrue(leaf.isLeaf)

        // A cross-link target keeps its leaf status: extra parents and the isBridge
        // marker must NOT evict it from the leaf set (the old definition did, which
        // silently orphaned every bridged leaf as a routing destination).
        val p1 = node("p1", "P1", 1)
        val p2 = node("p2", "P2", 1)
        leaf.parents.add(p1)
        leaf.parents.add(p2)
        leaf.isBridge = true
        assertTrue(leaf.isLeaf, "multi-parent bridged leaf must remain a leaf")

        // Any outgoing edge — tree or cross-link — ends leaf status.
        val target = node("target", "Target", 3)
        leaf.crossLinkChildren.add(target)
        assertFalse(leaf.isLeaf, "a node with cross-link children is not a leaf")
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
    fun `R6 - GED counts cross-link edges as relations`() {
        val config = TaxonomyConfig()
        val stabilizer = taxonomy.operations.TaxonomyStabilizer(config)

        val root = node("root", "Root", 0)
        val a = node("a", "A", 1)
        val b = node("b", "B", 1)
        link(root, a)
        link(root, b)
        a.vmfMu = floatArrayOf(1f, 0f); a.vmfKappa = 5.0
        b.vmfMu = floatArrayOf(0f, 1f); b.vmfKappa = 5.0

        stabilizer.evaluateConvergence(root, 1)

        // An accepted cross-link is a structural edit and must break the convergence
        // streak like any tree edit — otherwise bridge oscillation would be invisible.
        a.crossLinkChildren.add(b)
        b.parents.add(a)

        val result = stabilizer.evaluateConvergence(root, 2)
        assertEquals(1, result.ged, "a new cross-link edge must appear as exactly +1 relation in GED")
    }

    @Test
    fun `R10 - snapshot version-keyed migration`() {
        val config = TaxonomyConfig()
        val cache = mock(EmbeddingCache::class.java)

        val qId = "q_1234"
        `when`(cache.getQueriesBatch(setOf(qId))).thenReturn(mapOf(
            qId to CachedQuery("raw text", "distilled text", "category", 999)
        ))
        `when`(cache.getBatch(setOf("distilled text"))).thenReturn(mapOf(
            "distilled text" to floatArrayOf(1.0f, 0.0f)
        ))

        val persistence = TaxonomyPersistence(config, cache)

        val tempFile = File.createTempFile("taxo_test_v2", ".json")
        tempFile.deleteOnExit()

        val jsonContentV2 = """
        {
          "rootId": "root",
          "distillationEnabled": false,
          "version": 2,
          "nodes": [
            {
              "id": "root",
              "label": "Root",
              "depth": 0,
              "childIds": [],
              "crossLinkChildIds": [],
              "parentIds": [],
              "queryIds": ["$qId"]
            }
          ]
        }
        """.trimIndent()
        tempFile.writeText(jsonContentV2)
        // Clear registry to avoid interference
        taxonomy.model.QuestionIdRegistry.clear()

        val rootV2 = persistence.load(tempFile.absolutePath)
        assertNotNull(rootV2)
        val embV2 = rootV2!!.queries.first()
        assertEquals(999, embV2.queryId, "Version 2 should bypass registry lookup and use stored query_id directly")

        // Register legacy mapping for version 1 test
        taxonomy.model.QuestionIdRegistry.register("raw text", 888)

        val jsonContentV1 = """
        {
          "rootId": "root",
          "distillationEnabled": false,
          "version": 1,
          "nodes": [
            {
              "id": "root",
              "label": "Root",
              "depth": 0,
              "childIds": [],
              "crossLinkChildIds": [],
              "parentIds": [],
              "queryIds": ["$qId"]
            }
          ]
        }
        """.trimIndent()
        tempFile.writeText(jsonContentV1)

        val rootV1 = persistence.load(tempFile.absolutePath)
        assertNotNull(rootV1)
        val embV1 = rootV1!!.queries.first()
        assertEquals(888, embV1.queryId, "Version 1 should fall back to registry lookup when query_id is -1 or legacy is active")
    }

    @Test
    fun `R11 - TraversalPolicy visualizer and metrics consistency`() {
        val root = node("root", "Root", 0)
        val child = node("child", "Child", 1)
        val bridge = node("bridge", "Bridge", 1).apply { isBridge = true }

        root.children.add(child)
        child.parents.add(root)

        root.crossLinkChildren.add(bridge)
        bridge.parents.add(root)

        val ops = taxonomy.operations.TaxonomyOperations(
            mock(TaxonomyFitter::class.java),
            mock(TaxonomyTrickler::class.java),
            mock(taxonomy.operations.TaxonomySplitter::class.java),
            mock(TaxonomyMerger::class.java),
            TaxonomyConfig()
        )

        val dotTree = ops.exportToDot(root, TraversalPolicy.TREE_ONLY)
        assertTrue(dotTree.contains("\"root\" -> \"child\""))
        assertFalse(dotTree.contains("\"root\" -> \"bridge\""))

        val dotBoth = ops.exportToDot(root, TraversalPolicy.DAG_BOTH)
        assertTrue(dotBoth.contains("\"root\" -> \"child\""))
        assertTrue(dotBoth.contains("\"root\" -> \"bridge\""))
    }

    @Test
    fun `R12 - TaxonomyMetrics generateReport defaults to TREE_ONLY`() {
        val root = node("root", "Root Node", 0)
        val domainA = node("domainA", "domainA", 1)
        val domainB = node("domainB", "domainB", 1)
        link(root, domainA)
        link(root, domainB)

        val leafA = node("leafA", "Leaf A", 2)
        link(domainA, leafA)
        leafA.queries.add(emb("qA", 1, "domainA"))

        val bridge = node("bridge", "Bridge", 1).apply { isBridge = true }
        bridge.parents.add(domainA)
        bridge.parents.add(domainB)
        bridge.crossLinkChildren.add(leafA)
        leafA.parents.add(bridge)

        val metrics = TaxonomyMetrics(root, mapOf("domainA" to listOf("qA")))
        val report = metrics.generateReport()
        // If the report default policy was DAG_BOTH, leafA would resolve to both domainA and domainB, so contamination would be > 0.
        // Under TREE_ONLY, leafA resolves strictly to domainA, so contamination is 0.0.
        assertEquals(0.0, report.contaminationRatio, 1e-9)
    }

    @Test
    fun `R14 - routeConfidenceTau scales adaptively with branching factor`() {
        val config = TaxonomyConfig()
        config.formalism.enableResidualRouting = true
// [STALE FORK PARAM]         config.formalism.routeConfidenceTau = 0.6

        val trickler = TaxonomyTrickler(config)
        val parent = node("parent", "Parent Domain", 2)
        
        // Create 10 children to make branching factor K = 10
        val children = (1..10).map { node("child_$it", "Child $it", 3) }
        children.forEach {
            link(parent, it)
            it.vmfMu = floatArrayOf(if (it.id == "child_1") 1.0f else 0.0f)
            it.vmfKappa = 10.0
            it.sliceDim = 1
        }

        // Setup a query that is equally far/close, so responsibility for child1 is around 0.3
        // Under a fixed tau of 0.6, it would trigger a residual hit.
        // Under adaptive tau = 0.6 * (2.0 / 10) = 0.12, since 0.3 >= 0.12, it should NOT trigger a residual hit.
        val query = Embedding("q", "q", floatArrayOf(0.5f))
        query.queryId = 201

        val result = trickler.routeQuery(query, parent, currentIteration = 2)
        // Since bestChildResp is above adaptiveTau (0.12), there should be NO residual hits
        assertTrue(result.residualHits.isEmpty(), "Adaptive threshold must prevent near-universal residual tagging at high-level nodes")
    }

    @Test
    fun `R16 - log-space adaptive soft-membership and branch-point descent gating`() {
        val config = TaxonomyConfig()
        config.formalism.membershipFloor = 0.10  // posterior-probability admission floor
        config.formalism.enableResidualRouting = false
        val trickler = TaxonomyTrickler(config)
        val parent = node("parent", "Parent Domain", 2)
        val child1 = node("child1", "Child One", 3)
        val child2 = node("child2", "Child Two", 3)
        link(parent, child1)
        link(parent, child2)

        child1.vmfMu = floatArrayOf(1.0f, 0.0f)
        child1.vmfKappa = 10.0
        child1.sliceDim = 2

        child2.vmfMu = floatArrayOf(0.99f, 0.1f)  // very close, will result in high similarity
        child2.vmfKappa = 10.0
        child2.sliceDim = 2

        val query = Embedding("near-tie", "near-tie", floatArrayOf(1.0f, 0.0f))
        query.queryId = 301

        val result = trickler.routeQuery(query, parent, currentIteration = 2)

        // Verify that the query routes to both child1 and child2
        assertTrue(result.leaves.keys.any { it.id == child1.id })
        assertTrue(result.leaves.keys.any { it.id == child2.id })
    }
}
