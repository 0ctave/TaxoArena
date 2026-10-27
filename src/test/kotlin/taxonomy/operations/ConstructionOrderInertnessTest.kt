package taxonomy.operations

import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.diagnostics.DiagnosticsBundle
import taxonomy.model.DagRoot
import taxonomy.model.Embedding
import taxonomy.model.EmbeddingSlice
import taxonomy.model.GraphNode
import java.io.File
import java.nio.file.Files
import java.security.MessageDigest
import kotlin.math.sqrt

/**
 * H9-REM inertness proof for the construction-order shuffle flag.
 *
 * A synthetic, in-JVM mini construction (no Spring, no DB, no LLM): three ground-truth
 * anchors, each a mixture of two vMF sub-modes, bootstrapped exactly as TaxonomyEngine
 * seeds its anchors, then two iterations of the production split pass + hierarchy
 * optimisation + refit. The topology hash is the sorted "id<-parents->children" line set
 * the engine's own cycle detector builds, plus the leaf ids, digested with SHA-256.
 *
 * GOLDEN. [GOLDEN_TOPOLOGY_SHA256] was computed on the engine BEFORE the flag's call sites
 * were edited (same harness, same synthetic corpus). The flag-absent path must still
 * reproduce it after the edit: that is the byte-identity proof for every run that does
 * not declare `constructionOrderShuffleSeed`. If the engine's construction loop changes
 * on purpose, recompute the golden with the flag absent and say so in the commit.
 */
class ConstructionOrderInertnessTest {

    companion object {
        /**
         * Computed on the unmodified engine (HEAD eece8b0, 2026-09-16) with the flag absent,
         * before ConstructionOrder was wired into TaxonomyOperations / TaxonomyMerger:
         * 18 nodes, 10 leaves after two iterations on the synthetic corpus.
         */
        const val GOLDEN_TOPOLOGY_SHA256 = "c0fb70a1efc83c80f9c417ed0dbaa253605cfa4c4968e780590b932db4a36ace"
        private const val DIM = 64
    }

    private var savedWidth = 0
    private lateinit var tmp: File

    @BeforeEach
    fun setUp() {
        savedWidth = EmbeddingSlice.width
        tmp = Files.createTempDirectory("h9-order-inertness").toFile()
    }

    @AfterEach
    fun tearDown() {
        EmbeddingSlice.width = savedWidth
        if (DiagnosticsBundle.isOpen()) DiagnosticsBundle.close("test-teardown")
        tmp.deleteRecursively()
    }

    private object NoLlm : TaxonomyLlmClient {
        override suspend fun generateClusterLabel(prompt: String): String = "stub"
        override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String) = "stub"
        override suspend fun queryModelStructured(
            modelName: String, systemPrompt: String?, userPrompt: String, schema: JsonSchema
        ): String = "{}"
        override fun setMaxParallel(limit: Int) {}
    }

    /** The canonicalConfig recipe of SeparationNullBySizeTest at a small slice width. */
    private fun canonicalConfig(shuffleSeed: Long?): TaxonomyConfig =
        TaxonomyConfig().apply {
            formalism.maxDepth = 8
            formalism.minClusterSize = 30
            formalism.proposalSeparationBar = 0.025
            formalism.embeddingSliceDim = DIM
            formalism.splitDropTopPcs = 0
            formalism.splitWhiten = false
            EmbeddingSlice.width = DIM
            formalism.tau = 1e-6
            formalism.acceptanceZ = 0.0
            formalism.enableRefitGate = false
            formalism.membershipFloor = 0.25
            formalism.routingBeamGamma = 0.2
            formalism.descentMargin = 0.12
            formalism.effectiveSupportFloor = 2.0
            formalism.defaultKappaPrior = 10.0
            formalism.maxLeafAssignments = 5
            formalism.fusionSimilarityThreshold = 0.90
            formalism.enableGtWarmStart = false
            formalism.enableResidualSplitGate = true
            formalism.enableResidualRouting = true
            formalism.enableStableQuestionIds = true
            formalism.constructionOrderShuffleSeed = shuffleSeed
        }

    private fun ops(config: TaxonomyConfig): TaxonomyOperations {
        val fitter = TaxonomyFitter(config)
        // A throw-away DB path: the fetcher's init creates its tables at construction time and
        // must never touch the repository's own corpus DB from a unit test.
        val fetcher = MMLUDatasetFetcher(config, "", File(tmp, "corpus-${System.nanoTime()}.db").absolutePath)
        return TaxonomyOperations(
            fitter,
            TaxonomyTrickler(config),
            TaxonomySplitter(config, NoLlm, fetcher, fitter),
            TaxonomyMerger(config, NoLlm, fetcher),
            config
        )
    }

    // ── synthetic corpus: 3 anchors x 2 vMF-like sub-modes, 100 points each ─────────
    private fun unit(v: DoubleArray): DoubleArray {
        var n = 0.0
        for (x in v) n += x * x
        n = sqrt(n)
        return DoubleArray(v.size) { v[it] / n }
    }

    private fun corpus(): Map<String, List<Embedding>> {
        val rng = java.util.Random(20260916L)
        val out = linkedMapOf<String, List<Embedding>>()
        for (a in 0 until 3) {
            val anchorAxis = a
            val list = ArrayList<Embedding>(200)
            for (m in 0 until 2) {
                val subAxis = 3 + 2 * a + m
                val mu = unit(DoubleArray(DIM) { i -> when (i) { anchorAxis -> 1.0; subAxis -> 0.9; else -> 0.0 } })
                for (p in 0 until 100) {
                    val v = unit(DoubleArray(DIM) { i -> mu[i] + 0.22 * rng.nextGaussian() })
                    val key = "anchor$a/mode$m/q$p"
                    list += Embedding(
                        rawText = key, distilledText = key,
                        values = FloatArray(DIM) { v[it].toFloat() },
                        groundTruthCategory = "anchor$a"
                    )
                }
            }
            out["anchor$a"] = list
        }
        return out
    }

    /** The engine's bootstrap: one depth-1 node per category, weight 1.0, then a full refit. */
    private fun bootstrap(config: TaxonomyConfig, data: Map<String, List<Embedding>>): Pair<GraphNode, List<Embedding>> {
        GraphNode.resetIdCounter()
        GraphNode.EmbeddingRegistry.clear()
        val root = GraphNode(label = "ROOT", depth = 0)
        val all = ArrayList<Embedding>()
        for ((name, embs) in data) {
            val node = GraphNode(label = name, depth = 1)
            node.originalCategory = name
            node.queries.addAll(embs)
            for (q in embs) {
                node.queryWeights[q.rawText] = 1.0
                GraphNode.registerEmbedding(q)
                all += q
            }
            node.parents.add(root)
            root.children.add(node)
        }
        return root to all
    }

    private fun topologySha256(root: GraphNode): String {
        val seen = linkedMapOf<String, GraphNode>()
        fun walk(n: GraphNode) {
            if (seen.containsKey(n.id)) return
            seen[n.id] = n
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)
        val lines = seen.values.map { n ->
            n.id + "<-" + n.parents.map { it.id }.sorted().joinToString(",") +
                "->" + (n.children + n.crossLinkChildren).map { it.id }.sorted().joinToString(",")
        }.sorted() + seen.values.filter { it.isLeaf }.map { "leaf:" + it.id }.sorted()
        val digest = MessageDigest.getInstance("SHA-256").digest(lines.joinToString("\n").toByteArray())
        return digest.joinToString("") { "%02x".format(it) }
    }

    private data class Run(val sha: String, val nodeLines: Int, val leaves: Int)

    private fun runMini(shuffleSeed: Long?, diagnosticsDir: File? = null): Run = runBlocking {
        val config = canonicalConfig(shuffleSeed)
        val o = ops(config)
        val (root, all) = bootstrap(config, corpus())
        val gt = all.groupBy({ it.rawText }, { it.groundTruthCategory })
        val dag = DagRoot(root)
        if (diagnosticsDir != null) DiagnosticsBundle.open(diagnosticsDir, null, "inertness-harness")
        o.fitNodeRecursive(root)
        for (i in 1..2) {
            if (i > 1) {
                o.invalidateCachedJ()
                o.clearGraphQueries(root)
                o.reassignQueries(dag, all, gt, i)
            }
            o.splitNodesRecursive(dag, all, gt, i)
            o.optimizeHierarchy(dag, all, gt, i, learningPhase = false)
            o.fitNodeRecursive(root, currentIteration = i)
        }
        if (diagnosticsDir != null) DiagnosticsBundle.close("completed")
        val leaves = mutableListOf<GraphNode>()
        fun walk(n: GraphNode, seen: MutableSet<String>) {
            if (!seen.add(n.id)) return
            if (n.isLeaf) leaves += n
            n.children.forEach { walk(it, seen) }
        }
        walk(root, mutableSetOf())
        Run(topologySha256(root), countNodes(root), leaves.size)
    }

    private fun countNodes(root: GraphNode): Int {
        val seen = mutableSetOf<String>()
        fun walk(n: GraphNode) { if (seen.add(n.id)) { n.children.forEach { walk(it) }; n.crossLinkChildren.forEach { walk(it) } } }
        walk(root)
        return seen.size
    }

    @Test
    fun `flag absent reproduces the golden topology hash`() {
        val run = runMini(null)
        println("[H9-ORDER] flag absent: nodes=${run.nodeLines} leaves=${run.leaves} sha256=${run.sha}")
        assertTrue(run.nodeLines > 4, "the mini construction must split something for the golden to mean anything (nodes=${run.nodeLines})")
        assertEquals(GOLDEN_TOPOLOGY_SHA256, run.sha,
            "the flag-absent construction path changed: the golden was pinned on the unmodified engine")
    }

    @Test
    fun `flag absent is deterministic run-to-run`() {
        val a = runMini(null)
        val b = runMini(null)
        assertEquals(a.sha, b.sha, "two flag-absent runs in one JVM must agree")
    }

    @Test
    fun `same shuffle seed reproduces the same topology`() {
        val a = runMini(1L)
        val b = runMini(1L)
        assertEquals(a.sha, b.sha, "the shuffle is a pure function of the seed")
    }

    @Test
    fun `shuffle changes the proposal order`() {
        fun growSites(dir: File): List<String> {
            val rows = File(dir, "diagnostics/proposals.csv").readLines().drop(1)
            return rows.map { it.split(",") }
                .filter { it[0] == "1" && it[1] == "GROW" }
                .map { it[2] }
        }
        val plainDir = File(tmp, "plain").apply { mkdirs() }
        val shuffledDir = File(tmp, "shuffled").apply { mkdirs() }
        runMini(null, plainDir)
        runMini(1L, shuffledDir)
        val plain = growSites(plainDir)
        val shuffled = growSites(shuffledDir)
        println("[H9-ORDER] GROW sites iter 1, plain=$plain shuffled=$shuffled")
        assertTrue(plain.size >= 2, "iteration 1 must offer at least two GROW sites, got $plain")
        assertEquals(plain.toSet(), shuffled.toSet(), "the shuffle permutes the sites; it must not add or drop one")
        assertNotEquals(plain, shuffled, "seed 1 must visit the iteration-1 split sites in a different order")
    }
}
