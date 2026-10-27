package taxonomy.operations

import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
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
 * ANCHOR-FREE (registered 2026-09-16, docs/judge_v2_program.md) — two proofs on the synthetic
 * mini construction of [ConstructionOrderInertnessTest] (same corpus, same config recipe, same
 * two-iteration loop, same topology digest):
 *
 *  1. INERTNESS. With the flag absent, the anchored bootstrap reproduces that test's golden
 *     topology hash byte for byte. The flag's call sites (the merger's anchor-protection rules,
 *     the splitter's never-relabel rule, the engine's bootstrap branch) all read
 *     `formalism.anchorDepth`, which is the historical literal 1 when the flag is absent.
 *
 *  2. THE FLAG DOES WHAT THE REGISTRATION SAYS. With the flag on, the bootstrap places every
 *     query at the root (no category grouping), the root is a leaf holding the whole corpus,
 *     the split pass admits it as a GROW site under the standard gate, and after the loop the
 *     root has children, none of which carries `originalCategory` (no node is a label anchor).
 */
class AnchorFreeInertnessTest {

    companion object {
        private const val DIM = 64
    }

    private var savedWidth = 0
    private lateinit var tmp: File

    @BeforeEach
    fun setUp() {
        savedWidth = EmbeddingSlice.width
        tmp = Files.createTempDirectory("anchor-free-inertness").toFile()
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

    /** ConstructionOrderInertnessTest.canonicalConfig, verbatim, plus the flag under test. */
    private fun canonicalConfig(anchorFree: Boolean): TaxonomyConfig =
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
            formalism.constructionOrderShuffleSeed = null
            formalism.anchorFree = anchorFree
        }

    private fun ops(config: TaxonomyConfig): TaxonomyOperations {
        val fitter = TaxonomyFitter(config)
        val fetcher = MMLUDatasetFetcher(config, "", File(tmp, "corpus-${System.nanoTime()}.db").absolutePath)
        return TaxonomyOperations(
            fitter,
            TaxonomyTrickler(config),
            TaxonomySplitter(config, NoLlm, fetcher, fitter),
            TaxonomyMerger(config, NoLlm, fetcher),
            config
        )
    }

    // ── synthetic corpus: 3 anchors x 2 vMF-like sub-modes, 100 points each (verbatim) ──────
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

    /** The engine's anchored bootstrap: one depth-1 node per category, weight 1.0. */
    private fun bootstrapAnchored(data: Map<String, List<Embedding>>): Pair<GraphNode, List<Embedding>> {
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

    /**
     * The engine's ANCHOR-FREE bootstrap: no grouping, every query at the root with weight 1.0
     * (TaxonomyEngine.adaptTaxonomy, `if (config.formalism.anchorFree)` branch — the same
     * placement the hold-out branch gives a withheld query).
     */
    private fun bootstrapAnchorFree(data: Map<String, List<Embedding>>): Pair<GraphNode, List<Embedding>> {
        GraphNode.resetIdCounter()
        GraphNode.EmbeddingRegistry.clear()
        val root = GraphNode(label = "ROOT", depth = 0)
        val all = ArrayList<Embedding>()
        for ((_, embs) in data) {
            for (q in embs) {
                GraphNode.registerEmbedding(q)
                if (!root.queryWeights.containsKey(q.rawText)) {
                    root.queryWeights[q.rawText] = 1.0
                    root.queries.add(q)
                }
                all += q
            }
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

    private fun allNodes(root: GraphNode): List<GraphNode> {
        val seen = linkedMapOf<String, GraphNode>()
        fun walk(n: GraphNode) {
            if (seen.containsKey(n.id)) return
            seen[n.id] = n
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)
        return seen.values.toList()
    }

    private class Run(
        val root: GraphNode, val all: List<Embedding>, val ops: TaxonomyOperations,
        val sha: String, val nodes: Int, val leaves: Int
    )

    private fun runMini(anchorFree: Boolean, iterations: Int = 2, diagnosticsDir: File? = null): Run = runBlocking {
        val config = canonicalConfig(anchorFree)
        val o = ops(config)
        val (root, all) = if (anchorFree) bootstrapAnchorFree(corpus()) else bootstrapAnchored(corpus())
        val gt = all.groupBy({ it.rawText }, { it.groundTruthCategory })
        val dag = DagRoot(root)
        if (diagnosticsDir != null) DiagnosticsBundle.open(diagnosticsDir, null, "anchor-free-harness")
        o.fitNodeRecursive(root)
        for (i in 1..iterations) {
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
        val nodes = allNodes(root)
        Run(root, all, o, topologySha256(root), nodes.size, nodes.count { it.isLeaf })
    }

    @Test
    fun `flag absent reproduces the construction-order golden topology hash`() {
        val run = runMini(anchorFree = false)
        println("[ANCHOR-FREE] flag absent: nodes=${run.nodes} leaves=${run.leaves} sha256=${run.sha}")
        assertTrue(run.nodes > 4, "the mini construction must split something for the golden to mean anything (nodes=${run.nodes})")
        assertEquals(ConstructionOrderInertnessTest.GOLDEN_TOPOLOGY_SHA256, run.sha,
            "the flag-absent (anchored) construction path changed: the golden was pinned on the engine before either flag existed")
        // Every depth-1 node is an anchor on this path.
        val depth1 = allNodes(run.root).filter { it.depth == 1 }
        assertEquals(3, depth1.size, "three anchors seeded, three anchors kept")
        assertTrue(depth1.all { it.originalCategory != null }, "anchored depth-1 nodes carry originalCategory")
    }

    @Test
    fun `flag on splits the root and no node carries originalCategory`() {
        val dir = File(tmp, "af").apply { mkdirs() }
        val run = runMini(anchorFree = true, diagnosticsDir = dir)
        val nodes = allNodes(run.root)
        val depth1 = nodes.filter { it.depth == 1 }
        println("[ANCHOR-FREE] flag on: nodes=${run.nodes} leaves=${run.leaves} depth1=${depth1.size} " +
            "maxDepth=${nodes.maxOf { it.depth }} sha256=${run.sha}")
        assertTrue(run.root.children.isNotEmpty(), "the root must be split (it is the only GROW site at iteration 1)")
        assertTrue(run.root.children.size >= 2, "a split produces at least two children, got ${run.root.children.size}")
        assertTrue(nodes.none { it.originalCategory != null }, "no node may carry originalCategory on an anchor-free build")
        assertTrue(depth1.all { it.label!!.startsWith("Emergent Concept") }, "depth-1 nodes are emergent, not categories: ${depth1.map { it.label }}")
        // The root was offered as a GROW site under the standard ascending-k rule and accepted.
        val rows = File(dir, "diagnostics/proposals.csv").readLines().drop(1).map { it.split(",") }
        val rootGrow = rows.filter { it[0] == "1" && it[1] == "GROW" && it[2] == run.root.id }
        assertTrue(rootGrow.isNotEmpty(), "iteration 1 must record a GROW proposal at the root; sites=${rows.filter { it[0] == "1" }.map { it[2] }.distinct()}")
        // Standard gate, no special-cased acceptance (review 2026-09-16): the accepted root row
        // carries a measured dJ against the one-cell base (J = 0), exactly like any other GROW.
        val accepted = rootGrow.filter { it[8] == "ACCEPTED" }
        assertEquals(1, accepted.size, "exactly one root GROW is accepted at iteration 1 (ascending k, first acceptance wins): ${rootGrow.map { it[8] to it[9] }}")
        val dJ = accepted.single()[4].toDoubleOrNull()
        assertTrue(dJ != null && dJ > 0.0, "the accepted root split must carry a positive measured dJ, got '${accepted.single()[4]}'")
        // Ascending k: no k was skipped before the accepted one.
        val decisionsBeforeAccept = rootGrow.takeWhile { it[8] != "ACCEPTED" }.map { it[8] }
        assertTrue(decisionsBeforeAccept.all { it == "REJECTED" || it == "NO_PROPOSAL" }, "rows before the acceptance: $decisionsBeforeAccept")
        // Mass conservation under the engine's own invariant: every query is still in the tree.
        val weighted = nodes.flatMap { it.queryWeights.keys }.toSet()
        assertEquals(600, weighted.size, "all 600 queries stay in the tree")
        run.ops.assertMassConservation(run.root, run.all)
        assertNotEquals(ConstructionOrderInertnessTest.GOLDEN_TOPOLOGY_SHA256, run.sha, "the anchor-free tree is a different tree")
    }

    @Test
    fun `flag on is deterministic run-to-run`() {
        val a = runMini(anchorFree = true)
        val b = runMini(anchorFree = true)
        assertEquals(a.sha, b.sha, "two anchor-free runs in one JVM must agree")
    }

    private fun assertNotEquals(unexpected: String, actual: String, message: String) =
        org.junit.jupiter.api.Assertions.assertNotEquals(unexpected, actual, message)
}
