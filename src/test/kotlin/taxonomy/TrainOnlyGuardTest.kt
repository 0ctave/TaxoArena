package taxonomy

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.dataset.EvalQuestionLink
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.ModelEvalLoader
import taxonomy.dataset.ModelEvalStore
import taxonomy.dataset.SplitSide
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.TrainOnlyGuard
import taxonomy.service.TaxonomyPersistence
import taxonomy.service.TaxonomySnapshotManager
import taxonomy.utils.TaxonomyPerformanceTracker
import java.io.File
import java.nio.file.Files
import java.sql.DriverManager

/**
 * TRAIN-only tree state by content (FRAMEWORK guard 3, item 18): an EVAL-keyed text is counted
 * wherever it sits, in node.queries, only in queryWeights, only in residualQueries (by query id),
 * or under a cross-link child; each once per node; a clean tree counts 0. saveSnapshot with an
 * expected pool refuses the dirty tree and accepts the clean one, and the FunctionStamp
 * round-trips through the snapshot settings. Temp dataset DB; the snapshot DB is the test one.
 */
class TrainOnlyGuardTest {

    private val evalText = "Which planet is known as the red planet?"
    private val evalKeys = setOf(SplitSide.stemKey(evalText))

    private fun emb(text: String, id: Int = -1) = Embedding(rawText = text, distilledText = text, values = floatArrayOf(0.1f, 0.2f), queryId = id)

    private fun cleanTree(): GraphNode {
        val root = GraphNode(id = "root", label = "Root", depth = 0)
        val leaf = GraphNode(id = "leaf", label = "Leaf", depth = 1)
        root.children.add(leaf); leaf.parents.add(root)
        leaf.queries.add(emb("What is 2+2?")); leaf.queries.add(emb("Name a noble gas."))
        return root
    }

    @Test
    fun `an EVAL text is counted in every member slot, once per node`() {
        val root = cleanTree()
        val leaf = root.children.first()
        // (a) in queries
        leaf.queries.add(emb("  which PLANET is known as the red planet?  "))
        assertEquals(1, TrainOnlyGuard.evalMembers(root, evalKeys).count)
        // (b) only in queryWeights, another node
        val w = GraphNode(id = "w", label = "W", depth = 1); root.children.add(w); w.parents.add(root)
        w.queryWeights[evalText] = 0.7
        assertEquals(2, TrainOnlyGuard.evalMembers(root, evalKeys).count)
        // (c) only in residualQueries, by query id resolved through the registry
        val r = GraphNode(id = "r", label = "R", depth = 1); root.children.add(r); r.parents.add(root)
        GraphNode.registerEmbedding(emb(evalText, id = 4242))
        r.residualQueries.add("4242")
        assertEquals(3, TrainOnlyGuard.evalMembers(root, evalKeys).count)
        // (d) under a cross-link child only
        val x = GraphNode(id = "x", label = "X", depth = 2); r.crossLinkChildren.add(x); x.parents.add(r)
        x.queries.add(emb(evalText))
        val report = TrainOnlyGuard.evalMembers(root, evalKeys)
        assertEquals(4, report.count)
        assertEquals(4, report.nodesHit)
        assertEquals(1, report.distinctKeys)
        // The same text in two slots of ONE node counts once for that node.
        x.queryWeights[evalText] = 1.0
        assertEquals(4, TrainOnlyGuard.evalMembers(root, evalKeys).count)
        val e = assertThrows(IllegalStateException::class.java) { TrainOnlyGuard.assertNone(report, "test") }
        assertTrue(e.message!!.startsWith("[TRAIN-ONLY] test: 4 EVAL items are members of 4 nodes"), e.message)
    }

    @Test
    fun `a clean tree counts 0 and acknowledgement needs the exact count`() {
        val report = TrainOnlyGuard.evalMembers(cleanTree(), evalKeys)
        assertEquals(0, report.count)
        assertTrue(report.clean)
        TrainOnlyGuard.assertNone(report, "clean")
        assertTrue(TrainOnlyGuard.acknowledged(listOf("snap:37"), "snap", 37))
        assertTrue(!TrainOnlyGuard.acknowledged(listOf("snap:36"), "snap", 37))
        assertTrue(!TrainOnlyGuard.acknowledged(listOf("snap:37"), "other", 37))
        assertTrue(!TrainOnlyGuard.acknowledged(listOf("snap:37"), null, 37))
    }

    // ── saveSnapshot with an expected pool ───────────────────────────────────────────────

    private lateinit var tmp: File
    private var originalReserved: String? = null
    private val reservedFile = File("reserved_test_queries.json")

    @BeforeEach
    fun keepRootFile() {
        tmp = Files.createTempDirectory("train-only").toFile()
        originalReserved = if (reservedFile.exists()) reservedFile.readText() else null
    }

    @AfterEach
    fun restoreRootFile() {
        if (originalReserved != null) reservedFile.writeText(originalReserved!!) else reservedFile.delete()
        tmp.deleteRecursively()
    }

    private fun manager(): Pair<TaxonomySnapshotManager, String> {
        val dbPath = File(tmp, "dataset.db").absolutePath
        val store = ModelEvalStore(dbPath = dbPath)
        DriverManager.getConnection("jdbc:sqlite:$dbPath").use { c ->
            c.createStatement().use { s ->
                s.execute("CREATE TABLE IF NOT EXISTS mmlu_pro (id INTEGER PRIMARY KEY, question TEXT, category TEXT, cot_content TEXT, options TEXT, answer TEXT)")
                s.execute("INSERT INTO mmlu_pro (id, question, category, cot_content, options, answer) VALUES (7, '$evalText', 'astronomy', '', '[]', 'A')")
            }
        }
        store.saveLinks(listOf(EvalQuestionLink(7007, 7, evalText, true)))
        val poolIds = mapOf("astronomy" to listOf(7007))
        val poolId = store.recordReservedPool(poolIds)
        reservedFile.writeText("""{ "astronomy": [7007] }""")
        val config = TaxonomyConfig()
        val loader = ModelEvalLoader(store, mock(MMLUDatasetFetcher::class.java), dbPath, File(tmp, "emb.db").absolutePath, File(tmp, "r.json").absolutePath)
        val persistence = TaxonomyPersistence(config, mock(EmbeddingCache::class.java))
        return TaxonomySnapshotManager(config, persistence, loader, TaxonomyPerformanceTracker()) to poolId
    }

    @Test
    fun `saveSnapshot refuses a tree holding an EVAL text and accepts a clean one with the stamp`() {
        val (mgr, poolId) = manager()
        val dirty = cleanTree().also { it.children.first().queries.add(emb(evalText)) }
        val e = assertThrows(IllegalStateException::class.java) { mgr.saveSnapshot(dirty, "dirty", expectedPoolId = poolId) }
        assertTrue(e.message!!.startsWith("[TRAIN-ONLY] saveSnapshot($poolId): 1 EVAL items"), e.message)

        val snap = mgr.saveSnapshot(cleanTree(), "clean", expectedPoolId = poolId)
        try {
            assertEquals(SplitSide.stamp(poolId), snap.settings.splitFunction)
            val stored = mgr.listSnapshots().first { it.id == snap.id }
            assertNotNull(stored.settings.splitFunction)
            assertEquals(poolId, stored.settings.splitFunction!!.poolId)
            assertEquals("norm-v1", stored.settings.splitFunction!!.normaliserVersion)
            assertTrue(stored.settings.splitFunction!!.sameFunctionAs(SplitSide.stamp(null)))
        } finally {
            mgr.deleteSnapshot(snap.id)
        }
    }
}
