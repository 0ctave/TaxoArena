package taxonomy.operations

import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.diagnostics.DiagnosticsBundle
import taxonomy.model.Embedding
import taxonomy.model.EmbeddingSlice
import taxonomy.model.GraphNode
import taxonomy.model.projectTo
import taxonomy.runner.HeadlessCliConfig
import taxonomy.utils.StatisticsUtils
import java.io.File
import java.nio.file.Files
import kotlin.math.sqrt

/**
 * K-SELECTION (registered 2026-09-19, docs/judge_v2_program.md L8224-L8390): the registration's
 * unit tests (i)-(iii) on a synthetic node, no Spring, no DB, no LLM.
 *
 * The bar is positioned RELATIVE to the node's own measured min-pair separation: the node is
 * split once against an unreachable bar (the min-pair gate refuses, but `dasguptaDeltaNorm` has
 * already been written with the routed k = 2 separation, which at k = 2 IS the min-pair value),
 * then `proposalSeparationBar = sep / ratio` places the proposal at exactly `ratio` x bar.
 *
 *  (i)   ratio 1.02: accepted with the key absent (1.0), refused at 1.05;
 *  (ii)  1.05 refuses ratio 1.006 (R1's n00000004 case) and accepts ratio 2.2 (the k = 3 case);
 *  (iii) HeadlessCliConfig refuses 0.9, 2.5 and the key on a run that constructs nothing
 *        (the "abc" and mis-spelled-key refusals need the TOML parser and live in ConfigParsesTest).
 *
 * Plus the second creation-side read: a k = 3 proposal whose WEAK pair sits at 1.02 x bar is
 * kept at k = 3 with the key absent and coarsened to k = 2 at 1.05 (the coarsening loop's
 * weak-pair test reads the same effective level).
 */
class KSelectionTest {

    companion object {
        private const val DIM = 64
        private const val MODE_SIZE = 100
    }

    private var savedWidth = 0
    private lateinit var tmp: File

    @BeforeEach
    fun setUp() {
        savedWidth = EmbeddingSlice.width
        EmbeddingSlice.width = DIM
        tmp = Files.createTempDirectory("k-selection").toFile()
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

    /** The ConstructionOrderInertnessTest recipe, with the bar and the multiplier under test. */
    private fun config(bar: Double, multiplier: Double?): TaxonomyConfig =
        TaxonomyConfig().apply {
            formalism.maxDepth = 8
            formalism.minClusterSize = 30
            formalism.proposalSeparationBar = bar
            formalism.embeddingSliceDim = DIM
            formalism.splitDropTopPcs = 0
            formalism.splitWhiten = false
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
            // null = the key absent = the class default 1.0; a value = the key declared.
            multiplier?.let { formalism.proposalAcceptMultiplier = it }
        }

    private fun splitter(config: TaxonomyConfig): Pair<TaxonomySplitter, TaxonomyFitter> {
        val fitter = TaxonomyFitter(config)
        val fetcher = MMLUDatasetFetcher(config, "", File(tmp, "corpus-${System.nanoTime()}.db").absolutePath)
        return TaxonomySplitter(config, NoLlm, fetcher, fitter) to fitter
    }

    private fun unit(v: DoubleArray): DoubleArray {
        var n = 0.0
        for (x in v) n += x * x
        n = sqrt(n)
        return DoubleArray(v.size) { v[it] / n }
    }

    /**
     * One leaf node under a root, holding [modes] vMF-like clouds. Each mode is a unit vector
     * with entries on the given axes ("axis -> weight"); the same seed every call, so every
     * split in one test sees the same population.
     */
    private fun node(modes: List<Map<Int, Double>>, noise: Double = 0.22): GraphNode {
        GraphNode.resetIdCounter()
        GraphNode.EmbeddingRegistry.clear()
        val rng = java.util.Random(20260919L)
        val root = GraphNode(label = "ROOT", depth = 0)
        val n = GraphNode(label = "site", depth = 1)
        n.originalCategory = "site"
        n.parents.add(root)
        root.children.add(n)
        for ((m, axes) in modes.withIndex()) {
            val mu = unit(DoubleArray(DIM) { i -> axes[i] ?: 0.0 })
            for (p in 0 until MODE_SIZE) {
                val v = unit(DoubleArray(DIM) { i -> mu[i] + noise * rng.nextGaussian() })
                val key = "mode$m/q$p"
                val e = Embedding(
                    rawText = key, distilledText = key,
                    values = FloatArray(DIM) { v[it].toFloat() },
                    groundTruthCategory = "site"
                )
                n.queries.add(e)
                n.queryWeights[key] = 1.0
                GraphNode.registerEmbedding(e)
            }
        }
        return n
    }

    private class Outcome(val accepted: Boolean, val sep: Double, val children: Int)

    private fun split(modes: List<Map<Int, Double>>, bar: Double, multiplier: Double?, forcedK: Int, noise: Double = 0.22): Outcome = runBlocking {
        val cfg = config(bar, multiplier)
        val (sp, fitter) = splitter(cfg)
        val n = node(modes, noise)
        fitter.fitSingleNode(n)
        val accepted = sp.splitSingleNode(n, forcedK = forcedK)
        Outcome(accepted, n.dasguptaDeltaNorm, n.children.size)
    }

    private val twoModes = listOf(mapOf(0 to 1.0, 2 to 0.9), mapOf(1 to 1.0, 3 to 0.9))

    /** The node's own routed k = 2 min-pair separation, read off a refused split at an unreachable bar. */
    private fun measuredSep(modes: List<Map<Int, Double>>, forcedK: Int): Double {
        val o = split(modes, bar = 10.0, multiplier = null, forcedK = forcedK)
        assertFalse(o.accepted, "an unreachable bar must refuse the split")
        assertTrue(o.sep > 0.0, "the refused split must still have written the routed separation")
        return o.sep
    }

    @Test
    fun `(i) a proposal at 1_02 x bar is accepted with the key absent and refused at 1_05`() {
        val sep = measuredSep(twoModes, forcedK = 2)
        val bar = sep / 1.02
        println("[K-SELECTION] k=2 min-pair sep=$sep bar=$bar (1.02x)")
        val absent = split(twoModes, bar, multiplier = null, forcedK = 2)
        assertTrue(absent.accepted, "key absent: 1.02 x bar clears the nominal gate")
        assertEquals(2, absent.children, "the accepted proposal spawns two children")
        assertEquals(sep, absent.sep, 0.0, "the same population gives the same routed separation")
        val explicitOne = split(twoModes, bar, multiplier = 1.0, forcedK = 2)
        assertTrue(explicitOne.accepted, "an explicit 1.0 is the key absent")
        val primed = split(twoModes, bar, multiplier = 1.05, forcedK = 2)
        assertFalse(primed.accepted, "1.05: 1.02 x bar is below 1.05 x bar and is refused")
        assertEquals(0, primed.children, "a refused proposal spawns nothing")
        assertEquals(sep, primed.sep, 0.0, "the multiplier changes the gate, not the statistic")
    }

    @Test
    fun `(ii) 1_05 refuses 1_006 x bar and accepts 2_2 x bar`() {
        val sep = measuredSep(twoModes, forcedK = 2)
        val r1 = split(twoModes, sep / 1.006, multiplier = 1.05, forcedK = 2)
        assertFalse(r1.accepted, "R1's case: 1.006 x bar is refused at 1.05")
        assertTrue(split(twoModes, sep / 1.006, multiplier = null, forcedK = 2).accepted, "...and accepted with the key absent")
        val k3 = split(twoModes, sep / 2.2, multiplier = 1.05, forcedK = 2)
        assertTrue(k3.accepted, "the k = 3 case: 2.2 x bar is accepted at 1.05")
        assertEquals(2, k3.children)
        // The acceptance edge of the rule itself: 1.06 x bar clears 1.05 x bar.
        assertTrue(split(twoModes, sep / 1.06, multiplier = 1.05, forcedK = 2).accepted, "1.06 x bar clears the 1.05 gate")
        // And the maximum of the registered range refuses what 1.05 accepts.
        assertFalse(split(twoModes, sep / 1.5, multiplier = 2.0, forcedK = 2).accepted, "2.0: 1.5 x bar is refused")
    }

    /** The weakest routed pair among the children an accepted split produced. */
    private fun weakestPair(children: Collection<GraphNode>): Double {
        val stats = children.map { c ->
            val sum = DoubleArray(DIM)
            for (e in c.queries) { val v = e.projectTo(DIM); for (i in 0 until DIM) sum[i] += v[i] }
            StatisticsUtils.ClusterStats(c.queries.size.toDouble(), sum)
        }
        var weak = Double.MAX_VALUE
        for (i in stats.indices) for (j in i + 1 until stats.size) {
            weak = minOf(weak, StatisticsUtils.chanceCorrectedSeparation(listOf(stats[i], stats[j])))
        }
        return weak
    }

    @Test
    fun `the coarsening loop reads the same level - a k=3 weak pair at 1_02 x bar is kept absent and merged at 1_05`() {
        // Two close modes (axis 0; axes 0+1) and one far mode (axis 2), at a noise the k = 3 EM
        // resolves (at 0.22 its deterministic init leaves a sub-floor fragment and emK falls to 2).
        val NOISE3 = 0.12
        val threeModes = listOf(
            mapOf(0 to 1.0, 3 to 0.9),
            mapOf(0 to 1.0, 1 to 1.0, 4 to 0.9),
            mapOf(2 to 1.0, 5 to 0.9)
        )
        // Accept everything once to read the routed k = 3 pair structure.
        val cfg = config(1e-9, null)
        val (sp, fitter) = splitter(cfg)
        val n = node(threeModes, NOISE3)
        fitter.fitSingleNode(n)
        runBlocking { assertTrue(sp.splitSingleNode(n, forcedK = 3), "k = 3 must be feasible at a negligible bar") }
        println("[K-SELECTION] k=3 negligible bar: accepted children sizes=${n.children.map { it.queries.size }}")
        assertEquals(3, n.children.size, "three routed children at a negligible bar")
        val weak = weakestPair(n.children)
        val bar = weak / 1.02
        println("[K-SELECTION] k=3 weakest routed pair=$weak bar=$bar (1.02x); joint sep=${n.dasguptaDeltaNorm}")
        val absent = split(threeModes, bar, multiplier = null, forcedK = 3, noise = NOISE3)
        assertTrue(absent.accepted, "key absent: the weak pair at 1.02 x bar survives the coarsening test")
        assertEquals(3, absent.children, "key absent: k = 3 is kept")
        val primed = split(threeModes, bar, multiplier = 1.05, forcedK = 3, noise = NOISE3)
        assertTrue(primed.accepted, "1.05: the coarsened k = 2 partition still clears the gate")
        assertEquals(2, primed.children, "1.05: the weak pair at 1.02 x bar is merged, k 3 -> 2")
    }

    @Test
    fun `(iii) HeadlessCliConfig refuses 0_9, 2_5, and the key on a run that constructs nothing`() {
        fun refused(build: () -> HeadlessCliConfig): String {
            val e = assertThrows(IllegalArgumentException::class.java) { build() }
            assertTrue(e.message!!.contains("proposalAcceptMultiplier"), "refusal must name the key: ${e.message}")
            return e.message!!
        }
        refused { HeadlessCliConfig(models = emptyList(), runPipeline = true, proposalAcceptMultiplier = 0.9) }
        refused { HeadlessCliConfig(models = emptyList(), runPipeline = true, proposalAcceptMultiplier = 2.5) }
        refused { HeadlessCliConfig(models = emptyList(), runPipeline = true, proposalAcceptMultiplier = Double.NaN) }
        refused { HeadlessCliConfig(models = emptyList(), runPipeline = false, proposalAcceptMultiplier = 1.05) }
        refused { HeadlessCliConfig(models = emptyList(), runPipeline = true, proposalAcceptMultiplier = 1.05, unionSnapshots = listOf("x")) }
        // The registered value, the two edges of the range, and the key absent all construct.
        assertEquals(1.05, HeadlessCliConfig(models = emptyList(), runPipeline = true, proposalAcceptMultiplier = 1.05).proposalAcceptMultiplier)
        assertEquals(1.0, HeadlessCliConfig(models = emptyList(), runPipeline = true, proposalAcceptMultiplier = 1.0).proposalAcceptMultiplier)
        assertEquals(2.0, HeadlessCliConfig(models = emptyList(), runPipeline = true, proposalAcceptMultiplier = 2.0).proposalAcceptMultiplier)
        assertEquals(null, HeadlessCliConfig(models = emptyList(), runPipeline = false).proposalAcceptMultiplier)
        // The class default is 1.0, so a config that never mentions the key runs the production gate.
        assertEquals(1.0, TaxonomyConfig().formalism.proposalAcceptMultiplier, 0.0)
    }
}
