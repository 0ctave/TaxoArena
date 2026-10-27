package taxonomy.operations

import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
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
 * K-SELECTION (registered 2026-09-19, docs/judge_v2_program.md L8224-L8390) — the inertness
 * proof (registration "inert I1") and the flag's mechanism on the synthetic mini construction of
 * [ConstructionOrderInertnessTest] (same corpus, same config recipe, same two-iteration loop,
 * same topology digest):
 *
 *  1. INERTNESS. With the key absent (`proposalAcceptMultiplier` at its class default 1.0) the
 *     construction reproduces that test's golden topology hash byte for byte; an explicit 1.0
 *     does too. The flag's two call sites (the coarsening loop's weak-pair test and the min-pair
 *     gate in TaxonomySplitter.splitSingleNode) read `acceptEps`, which at 1.0 IS `requiredEps`
 *     (the same reference, no multiplication), so the flag-absent path is the historical one by
 *     construction.
 *
 *  2. THE FLAG DOES WHAT THE REGISTRATION SAYS. With the bar re-positioned so that the anchors'
 *     own k = 2 proposals sit in [1.00, 1.05) x bar, the key absent accepts them (the tree grows)
 *     and 1.05 refuses them (the tree stays at the bootstrap), the refusals are recorded in
 *     proposals.csv as `min_pair_sep_below_bar(...,bar_eff=...)`, and the flag-absent run's
 *     proposals.csv carries no `bar_eff` token (the diagnostics surface is inert too).
 *
 *  3. THE MANIFEST KEY. DiagnosticsBundle.recordProposalAcceptMultiplier writes
 *     `proposal_accept_multiplier` as a JSON number.
 */
class KSelectionInertnessTest {

    companion object {
        private const val DIM = 64
        private const val RECIPE_BAR = 0.025
    }

    private var savedWidth = 0
    private lateinit var tmp: File

    @BeforeEach
    fun setUp() {
        savedWidth = EmbeddingSlice.width
        tmp = Files.createTempDirectory("k-selection-inertness").toFile()
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

    /** ConstructionOrderInertnessTest.canonicalConfig, verbatim, plus the bar and the key under test. */
    private fun canonicalConfig(bar: Double, multiplier: Double?): TaxonomyConfig =
        TaxonomyConfig().apply {
            formalism.maxDepth = 8
            formalism.minClusterSize = 30
            formalism.proposalSeparationBar = bar
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
            formalism.anchorFree = false
            // null = the key absent (the class default 1.0 is NOT touched); a value = the key declared.
            multiplier?.let { formalism.proposalAcceptMultiplier = it }
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

    /** The engine's anchored bootstrap: one depth-1 node per category, weight 1.0 (verbatim). */
    private fun bootstrap(data: Map<String, List<Embedding>>): Pair<GraphNode, List<Embedding>> {
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

    private class Run(val root: GraphNode, val sha: String, val nodes: Int, val leaves: Int)

    private fun runMini(bar: Double, multiplier: Double?, diagnosticsDir: File? = null): Run = runBlocking {
        val config = canonicalConfig(bar, multiplier)
        val o = ops(config)
        val (root, all) = bootstrap(corpus())
        val gt = all.groupBy({ it.rawText }, { it.groundTruthCategory })
        val dag = DagRoot(root)
        if (diagnosticsDir != null) DiagnosticsBundle.open(diagnosticsDir, null, "k-selection-harness")
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
        val nodes = allNodes(root)
        Run(root, topologySha256(root), nodes.size, nodes.count { it.isLeaf })
    }

    @Test
    fun `key absent reproduces the construction-order golden topology hash`() {
        assertEquals(1.0, TaxonomyConfig().formalism.proposalAcceptMultiplier, 0.0, "the class default is 1.0 (the key absent)")
        val run = runMini(RECIPE_BAR, multiplier = null)
        println("[K-SELECTION] key absent: nodes=${run.nodes} leaves=${run.leaves} sha256=${run.sha}")
        assertTrue(run.nodes > 4, "the mini construction must split something for the golden to mean anything (nodes=${run.nodes})")
        assertEquals(ConstructionOrderInertnessTest.GOLDEN_TOPOLOGY_SHA256, run.sha,
            "the key-absent construction path changed: the golden was pinned on the engine before any of the three flags existed")
    }

    @Test
    fun `an explicit 1_0 is the key absent`() {
        val run = runMini(RECIPE_BAR, multiplier = 1.0)
        assertEquals(ConstructionOrderInertnessTest.GOLDEN_TOPOLOGY_SHA256, run.sha, "proposalAcceptMultiplier = 1.0 must be byte-identical to the key absent")
    }

    @Test
    fun `at 1_05 proposals in the hysteresis band are refused, recorded with bar_eff, and the key-absent diagnostics carry no bar_eff`() {
        // Position the bar so the anchors' own k = 2 proposals sit at ~1.02 x bar: read each
        // anchor's routed separation off the golden-recipe run (dasguptaDeltaNorm is written at
        // split time) and set bar = min / 1.02. Every anchor then clears the nominal gate by at
        // least 2% and the weakest one fails the 1.05 gate.
        val reference = runMini(RECIPE_BAR, multiplier = null)
        val anchorSeps = reference.root.children.map { it.dasguptaDeltaNorm }
        assertTrue(anchorSeps.all { it > 0.0 }, "every anchor split on the recipe run: $anchorSeps")
        val bar = anchorSeps.min() / 1.02
        println("[K-SELECTION] anchor k=2 separations=$anchorSeps -> bar=$bar (weakest at 1.02x)")

        val absentDir = File(tmp, "absent").apply { mkdirs() }
        val primedDir = File(tmp, "primed").apply { mkdirs() }
        val absent = runMini(bar, multiplier = null, diagnosticsDir = absentDir)
        val primed = runMini(bar, multiplier = 1.05, diagnosticsDir = primedDir)
        println("[K-SELECTION] bar=$bar absent: nodes=${absent.nodes} leaves=${absent.leaves}; 1.05: nodes=${primed.nodes} leaves=${primed.leaves}")

        // The key absent accepts the anchors' proposals (they clear 1.0 x bar); 1.05 refuses the
        // weakest one at least, so the primed tree is strictly smaller and a different tree.
        assertTrue(absent.nodes > 4, "key absent at bar=$bar: the anchors must still split (nodes=${absent.nodes})")
        assertTrue(primed.nodes < absent.nodes, "1.05 must refuse at least the weakest anchor's proposal (absent ${absent.nodes} nodes, primed ${primed.nodes})")
        assertNotEquals(absent.sha, primed.sha, "the primed tree is a different tree")

        // proposals.csv: the primed run records the refusals with bar_eff beside bar; the
        // key-absent run's diagnostics never mention bar_eff (inert diagnostics surface).
        val absentRows = File(absentDir, "diagnostics/proposals.csv").readText()
        val primedRows = File(primedDir, "diagnostics/proposals.csv").readLines()
        assertFalse(absentRows.contains("bar_eff"), "the key-absent proposals.csv must carry no bar_eff token")
        val refused = primedRows.filter { it.contains("min_pair_sep_below_bar") }
        assertTrue(refused.isNotEmpty(), "1.05 must record at least one min-pair refusal; rows=${primedRows.take(8)}")
        assertTrue(refused.all { it.contains("bar_eff=") }, "every primed refusal carries bar_eff=: $refused")
        // The refused proposals sat in the hysteresis band: sep >= bar (the nominal gate would
        // have accepted) and sep < bar_eff = 1.05 x bar.
        val re = Regex("sep=([0-9.]+),bar=([0-9.]+),bar_eff=([0-9.]+)")
        val inBand = refused.mapNotNull { re.find(it) }.map { m -> Triple(m.groupValues[1].toDouble(), m.groupValues[2].toDouble(), m.groupValues[3].toDouble()) }
        assertTrue(inBand.isNotEmpty(), "the refusal reason must carry sep, bar and bar_eff: $refused")
        for ((sep, b, bEff) in inBand) {
            assertTrue(sep < bEff, "refused below the effective gate: sep=$sep bar_eff=$bEff")
            assertEquals(b * 1.05, bEff, 2e-5, "bar_eff is 1.05 x bar (5-decimal print): bar=$b bar_eff=$bEff")
        }
        assertTrue(inBand.any { (sep, b, _) -> sep >= b }, "at least one refusal would have passed the nominal gate (sep >= bar): $inBand")
    }

    @Test
    fun `the manifest records proposal_accept_multiplier as a number`() {
        val dir = File(tmp, "manifest").apply { mkdirs() }
        DiagnosticsBundle.open(dir, null, "k-selection-manifest")
        DiagnosticsBundle.recordProposalAcceptMultiplier(1.0)
        val absent = File(dir, "diagnostics/run_manifest.json").readText()
        DiagnosticsBundle.recordProposalAcceptMultiplier(1.05)
        val primed = File(dir, "diagnostics/run_manifest.json").readText()
        DiagnosticsBundle.close("completed")
        assertTrue(absent.contains("\"proposal_accept_multiplier\": 1.0"), "unprimed manifest states 1.0: $absent")
        assertTrue(primed.contains("\"proposal_accept_multiplier\": 1.05"), "primed manifest states 1.05: $primed")
    }
}
