package taxonomy

import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertNotNull
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
import taxonomy.operations.MemoMode
import taxonomy.operations.ProposalOutcome
import taxonomy.operations.ProposalType
import taxonomy.operations.TaxonomyFitter
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomyMerger
import taxonomy.operations.TaxonomyOperations
import taxonomy.operations.TaxonomySplitter
import taxonomy.operations.TaxonomyTrickler
import taxonomy.utils.StatisticsUtils
import java.io.File
import java.nio.file.Files

/**
 * PERF-8 through the real [TaxonomyOperations.tryProposal] on a synthetic two-cluster corpus.
 *
 * The action is a counting fake that does what a real split does to the counters — creates k
 * child GraphNodes under the site (consuming k ids) and consumes k concept labels — so the
 * replay of id/label consumption can be checked exactly against an off-mode run of the same
 * sequence. The off run is the reference for everything: final counter values, outcomes, and
 * the number of times the action ran.
 *
 * The lossy fingerprint memo stays first in every mode (it answers an identical repeat within
 * an iteration in off mode too, burning nothing). To isolate the exact memo most tests put the
 * site on a lossy-memo boundary (`maxDepth = 2`, site depth 1 => never fingerprinted); the
 * cross-iteration test instead clears the lossy memo with `invalidateCachedJ()` between the
 * calls, exactly as the engine does every iteration.
 */
class ProposalMemoReplayTest {

    private val dim = 8
    private var prevWidth = 256
    private lateinit var config: TaxonomyConfig
    private lateinit var corpus: List<Embedding>
    private lateinit var gt: Map<String, List<String>>

    private object NoLlm : TaxonomyLlmClient {
        override suspend fun generateClusterLabel(prompt: String): String = "stub"
        override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String) = "stub"
        override suspend fun queryModelStructured(
            modelName: String, systemPrompt: String?, userPrompt: String, schema: JsonSchema
        ): String = "{}"
        override fun setMaxParallel(limit: Int) {}
    }

    private class Stack(val ops: TaxonomyOperations, val splitter: TaxonomySplitter)

    private fun stack(): Stack {
        val fitter = TaxonomyFitter(config)
        val fetcher = MMLUDatasetFetcher(config, "")
        val splitter = TaxonomySplitter(config, NoLlm, fetcher, fitter)
        val ops = TaxonomyOperations(fitter, TaxonomyTrickler(config), splitter, TaxonomyMerger(config, NoLlm, fetcher), config)
        return Stack(ops, splitter)
    }

    private fun unit(v: DoubleArray): FloatArray {
        val n = kotlin.math.sqrt(v.sumOf { it * it })
        return FloatArray(dim) { i -> (v[i] / n).toFloat() }
    }

    private fun leaf(label: String, parent: GraphNode, axis: Int): GraphNode =
        GraphNode(label = label, depth = parent.depth + 1).apply {
            vmfMu = FloatArray(dim) { if (it == axis) 1f else 0f }
            vmfKappa = 20.0
            vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(dim, 20.0)
            niwM0 = vmfMu.copyOf()
            niwKappa0 = 1.0
            niwNu0 = (dim + 2).toDouble()
            niwLambda = FloatArray(dim) { 1f / dim }
            treeParentId = parent.id
            parent.children.add(this)
            parents.add(parent)
        }

    private class Dag(val root: GraphNode, val a: GraphNode, val b: GraphNode)

    /** Fresh JVM-like state: id and label counters reset, DAG rebuilt, corpus routed. */
    private fun freshDag(st: Stack): Dag {
        GraphNode.resetIdCounter()
        st.splitter.resetConceptCounter()
        val root = GraphNode(label = "Root", depth = 0)
        val a = leaf("A", root, 0)
        val b = leaf("B", root, 1)
        corpus.forEach { GraphNode.registerEmbedding(it) }
        runBlocking { st.ops.reassignQueries(DagRoot(root), corpus, gt, currentIteration = 2) }
        return Dag(root, a, b)
    }

    @BeforeEach
    fun setUp() {
        prevWidth = EmbeddingSlice.width
        EmbeddingSlice.width = dim
        config = TaxonomyConfig().apply {
            formalism.embeddingSliceDim = dim
            formalism.enableGtWarmStart = false
            formalism.acceptanceZ = 0.0
            formalism.tau = 1e-6
            formalism.minClusterSize = 5
            // depth 1 >= maxDepth - 1: the site sits on a lossy-memo boundary, so the lossy
            // memo never answers and every repeat reaches the exact memo (see class doc).
            formalism.maxDepth = 2
            formalism.enableResidualRouting = true
            formalism.enableStableQuestionIds = false
            diagnostics.enableProfiling = false
        }
        val rng = java.util.Random(2026)
        corpus = (0 until 60).map { i ->
            val axis = if (i < 30) 0 else 1
            val v = DoubleArray(dim) { d -> (if (d == axis) 1.0 else 0.0) + 0.08 * rng.nextGaussian() }
            Embedding(rawText = "q$i", distilledText = "q$i", values = unit(v), queryId = i)
        }
        gt = corpus.associate { it.rawText to listOf(if (it.queryId < 30) "A" else "B") }
    }

    @AfterEach
    fun tearDown() {
        EmbeddingSlice.width = prevWidth
        if (DiagnosticsBundle.isOpen()) DiagnosticsBundle.close("test-teardown")
    }

    /**
     * A split-like action: k children under [site] (k ids), k labels, returns true. Children
     * point away from the data (axes 2..), so the edit never improves J and is REJECTED, which
     * is the outcome class whose replay carries side effects. [invocations] counts executions.
     */
    private class FakeSplit(val site: GraphNode, val k: Int, val splitter: TaxonomySplitter) {
        var invocations = 0
        var extraOnSecond = false
        suspend fun run(): Boolean {
            invocations++
            val kk = if (extraOnSecond && invocations == 2) k + 1 else k
            for (i in 0 until kk) {
                val child = GraphNode(label = "Emergent Concept #${splitter.conceptCounterValue()}", depth = site.depth + 1).apply {
                    val d = site.vmfMu.size
                    vmfMu = FloatArray(d) { if (it == 2 + i) 1f else 0f }
                    vmfKappa = 20.0
                    vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(d, 20.0)
                    treeParentId = site.id
                }
                splitter.advanceConceptCounter(1)
                site.children.add(child)
                child.parents.add(site)
            }
            return true
        }
    }

    private fun propose(st: Stack, dag: Dag, fake: FakeSplit, iter: Int = 2, actionId: String = "k${fake.k}",
                        corpusList: List<Embedding> = corpus): ProposalOutcome =
        runBlocking {
            st.ops.tryProposal(
                DagRoot(dag.root), fake.site, corpusList, gt, iter, ProposalType.GROW,
                proposalKey = actionId, actionId = actionId
            ) { fake.run() }
        }

    private data class Counters(val ids: Long, val labels: Int)
    private fun counters(st: Stack) = Counters(GraphNode.idCounterValue(), st.splitter.conceptCounterValue())

    @Test
    fun `off mode never consults or fills the exact memo`() {
        val st = stack()
        st.ops.proposalMemo.reset(MemoMode.OFF)
        val dag = freshDag(st)
        val fake = FakeSplit(dag.a, 2, st.splitter)
        val o1 = propose(st, dag, fake)
        val o2 = propose(st, dag, fake)
        assertNotEquals(ProposalOutcome.ACCEPTED, o1)
        assertEquals(o1, o2)
        // First call: base J uncached -> the action runs twice; second: once.
        assertEquals(3, fake.invocations)
        val m = st.ops.proposalMemo.snapshot()
        assertEquals("off", m.mode)
        assertEquals(0L, m.hits + m.misses + m.invalidations + m.stateChanges + m.shadowHits + m.replayedIds)
        assertEquals(0, st.ops.proposalMemo.size)
    }

    /** The reference: the same two-call sequence in off mode. */
    private fun offReference(): Triple<Counters, List<ProposalOutcome>, Int> {
        val st = stack()
        st.ops.proposalMemo.reset(MemoMode.OFF)
        val dag = freshDag(st)
        val fake = FakeSplit(dag.a, 2, st.splitter)
        val outcomes = listOf(propose(st, dag, fake), propose(st, dag, fake))
        return Triple(counters(st), outcomes, fake.invocations)
    }

    @Test
    fun `on mode - identical proposal twice runs the action once and replays id and label consumption exactly`() {
        val (offCounters, offOutcomes, offInvocations) = offReference()
        assertEquals(3, offInvocations)

        val tmp = Files.createTempDirectory("memo-replay").toFile()
        try {
            DiagnosticsBundle.open(tmp, null, "resolved")
            val st = stack()
            st.ops.proposalMemo.reset(MemoMode.ON)
            val dag = freshDag(st)
            val fake = FakeSplit(dag.a, 2, st.splitter)
            val o1 = propose(st, dag, fake)
            val stored = st.ops.proposalMemo.size
            val o2 = propose(st, dag, fake)
            assertEquals(offOutcomes, listOf(o1, o2))
            assertEquals(1, stored, "the rejected proposal must be stored (its evaluation restored the state exactly)")
            assertEquals(2, fake.invocations, "the second call must be replayed, not evaluated")
            assertEquals(offCounters, counters(st), "id and label counters must land exactly where the off run's did")
            val m = st.ops.proposalMemo.snapshot()
            assertEquals(1L, m.hits); assertEquals(1L, m.misses)
            assertEquals(2L, m.replayedIds); assertEquals(2L, m.replayedLabels)
            assertNull(m.disabledReason)
            DiagnosticsBundle.close("completed")
            val rows = File(tmp, "diagnostics/proposals.csv").readLines().drop(1).filter { it.isNotBlank() }
            val memoized = rows.filter { ",MEMOIZED," in it }
            assertEquals(1, memoized.size, "exactly one MEMOIZED row — was:\n${rows.joinToString("\n")}")
            assertTrue(memoized[0].contains("exact_state(digest="), "reason prefix — was: ${memoized[0]}")
            assertTrue(memoized[0].contains("replayed=REJECTED"), memoized[0])
            assertTrue(memoized[0].contains("ids=+2,labels=+2"), memoized[0])
            assertTrue(memoized[0].contains("since_iter=2"), memoized[0])
        } finally {
            tmp.deleteRecursively()
        }
    }

    @Test
    fun `on mode - the uncached-base double execution is replayed and the base is primed`() {
        // The cross-iteration case proper: the lossy memo is ACTIVE (no boundary) and cleared
        // by invalidateCachedJ between the calls, as the engine does every iteration.
        config.formalism.maxDepth = 6
        // Reference: off. The second call then executes the action twice again.
        val offSt = stack(); offSt.ops.proposalMemo.reset(MemoMode.OFF)
        val offDag = freshDag(offSt)
        val offFake = FakeSplit(offDag.a, 2, offSt.splitter)
        propose(offSt, offDag, offFake)
        offSt.ops.invalidateCachedJ()
        propose(offSt, offDag, offFake)
        assertEquals(4, offFake.invocations)
        val offCounters = counters(offSt)
        assertTrue(offSt.ops.baseJCached)

        val st = stack(); st.ops.proposalMemo.reset(MemoMode.ON)
        val dag = freshDag(st)
        val fake = FakeSplit(dag.a, 2, st.splitter)
        propose(st, dag, fake)
        st.ops.invalidateCachedJ()
        assertFalse(st.ops.baseJCached)
        val o2 = propose(st, dag, fake, iter = 3)   // next iteration, bit-identical state
        assertEquals(ProposalOutcome.REJECTED, o2)
        assertEquals(2, fake.invocations, "the hit must not evaluate")
        assertTrue(st.ops.baseJCached, "the hit must prime the base J exactly as the unmemoized path would")
        assertEquals(offCounters, counters(st), "2k ids and 2k labels must be burned on an uncached-base hit")
        val m = st.ops.proposalMemo.snapshot()
        assertEquals(1L, m.hits)
        assertEquals(4L, m.replayedIds); assertEquals(4L, m.replayedLabels)
        assertEquals(0L, m.invalidations, "the state was bit-identical across the iteration boundary")
        // A third call in the same iteration: the hit replayed the lossy fingerprint add, so
        // the lossy memo now answers first — exactly as it would in the off run — burning nothing.
        propose(offSt, offDag, offFake)
        assertEquals(4, offFake.invocations)
        val before = counters(st)
        propose(st, dag, fake, iter = 3)
        assertEquals(2, fake.invocations)
        assertEquals(before, counters(st))
        assertEquals(counters(offSt), counters(st))
        assertEquals(1L, st.ops.proposalMemo.lossyShadowed)
        assertEquals(1L, st.ops.proposalMemo.hits, "the lossy-answered repeat is not an exact hit")
    }

    @Test
    fun `on mode - a lossy-memo hit is never stored in the exact memo`() {
        // No boundary: the lossy memo answers the identical repeat in the same iteration and
        // the exact memo must not record that unevaluated answer.
        config.formalism.maxDepth = 6
        val st = stack(); st.ops.proposalMemo.reset(MemoMode.ON)
        val dag = freshDag(st)
        val fake = FakeSplit(dag.a, 2, st.splitter)
        propose(st, dag, fake)
        assertEquals(1, st.ops.proposalMemo.size)
        st.ops.proposalMemo.reset(MemoMode.ON)   // forget the evaluated entry, keep the lossy one
        val before = counters(st)
        propose(st, dag, fake)
        assertEquals(2, fake.invocations, "the lossy memo answered")
        assertEquals(before, counters(st))
        assertEquals(0, st.ops.proposalMemo.size, "an unevaluated answer is never stored")
        assertEquals(1L, st.ops.proposalMemo.lossyShadowed)
    }

    @Test
    fun `a mutated input never hits`() {
        val st = stack(); st.ops.proposalMemo.reset(MemoMode.ON)
        val dag = freshDag(st)
        val fake = FakeSplit(dag.a, 2, st.splitter)
        propose(st, dag, fake)
        assertEquals(1, st.ops.proposalMemo.size)
        var expectedInvocations = 2

        fun expectMiss(name: String, expectInvalidation: Boolean, block: () -> ProposalOutcome) {
            val invBefore = st.ops.proposalMemo.invalidations
            val hitsBefore = st.ops.proposalMemo.hits
            val stored = st.ops.proposalMemo.size
            block()
            expectedInvocations += 1   // base J is cached after the first call: one execution per miss
            assertEquals(expectedInvocations, fake.invocations, "'$name' must be a miss (the action must run)")
            assertEquals(hitsBefore, st.ops.proposalMemo.hits, "'$name' must not hit")
            if (expectInvalidation) {
                assertEquals(invBefore + stored, st.ops.proposalMemo.invalidations,
                    "'$name' changes the state, so every stored entry must be dropped")
            } else {
                assertEquals(invBefore, st.ops.proposalMemo.invalidations, "'$name' leaves the state alone")
            }
        }

        // One weight on the UNRELATED leaf +1 ulp.
        expectMiss("unrelated leaf weight +1 ulp", expectInvalidation = true) {
            val k = dag.b.queryWeights.keys.first()
            dag.b.queryWeights[k] = Math.nextUp(dag.b.queryWeights[k]!!)
            propose(st, dag, fake)
        }
        // vmfKappa +1 ulp on an unrelated node.
        expectMiss("unrelated vmfKappa +1 ulp", expectInvalidation = true) {
            dag.b.vmfKappa = Math.nextUp(dag.b.vmfKappa)
            propose(st, dag, fake)
        }
        // One embedding value +1 ulp (a different corpus list).
        expectMiss("embedding value +1 ulp", expectInvalidation = true) {
            val changed = corpus.toMutableList()
            val e = changed[40]
            changed[40] = Embedding(e.rawText, e.distilledText, e.values.copyOf().also { it[1] = Math.nextUp(it[1]) }, queryId = e.queryId)
            propose(st, dag, fake, corpusList = changed)
        }
        // Back on the original corpus: a new state from the memo's point of view again.
        expectMiss("original corpus again", expectInvalidation = true) { propose(st, dag, fake) }
        // actionId k2 -> k3: same state, different action; nothing is invalidated.
        val fake3 = FakeSplit(dag.a, 3, st.splitter)
        run {
            val invBefore = st.ops.proposalMemo.invalidations
            val hitsBefore = st.ops.proposalMemo.hits
            propose(st, dag, fake3)
            assertEquals(1, fake3.invocations, "k3 must be evaluated, never answered by the k2 entry")
            assertEquals(hitsBefore, st.ops.proposalMemo.hits)
            assertEquals(invBefore, st.ops.proposalMemo.invalidations)
            assertEquals(2, st.ops.proposalMemo.size, "k2 and k3 entries coexist in the same state")
        }
        // config.tau.
        expectMiss("config.formalism.tau", expectInvalidation = true) {
            config.formalism.tau = config.formalism.tau * 2
            propose(st, dag, fake)
        }
        assertNull(st.ops.proposalMemo.disabledReason)
    }

    @Test
    fun `shadow mode skips nothing and reports zero mismatches`() {
        val (offCounters, offOutcomes, offInvocations) = offReference()
        val st = stack(); st.ops.proposalMemo.reset(MemoMode.SHADOW)
        val dag = freshDag(st)
        val fake = FakeSplit(dag.a, 2, st.splitter)
        val o1 = propose(st, dag, fake)
        val o2 = propose(st, dag, fake)
        assertEquals(offOutcomes, listOf(o1, o2))
        assertEquals(offInvocations, fake.invocations, "shadow must evaluate everything")
        assertEquals(offCounters, counters(st))
        val m = st.ops.proposalMemo.snapshot()
        assertEquals("shadow", m.mode)
        assertEquals(1L, m.shadowHits)
        assertEquals(0L, m.shadowMismatches)
        assertEquals(0L, m.hits)
        assertEquals(1L, m.misses)
        assertEquals(0L, m.replayedIds)
        assertNull(m.disabledReason)
    }

    @Test
    fun `shadow mode counts a stored rejection that the full evaluation now accepts as a mismatch`() {
        // The mismatch class an ON run could never observe: the entry says REJECTED for this
        // exact state, so ON would replay the rejection and never take the edit. Shadow must
        // count it rather than return on ACCEPTED before the comparison.
        //
        // The DAG carries an extra EMPTY leaf E (axis 6, no data there; it attracts nothing).
        // Call 1 (iter 2): the fake split of A -> REJECTED, stored. Call 2 (iter 3, bit-identical
        // state, same site/action identity): the action instead removes E — an exactly J-neutral
        // edit (empty cells are not counted by computeDagSeparationJ) with dV = -1, which the
        // lexicographic rule ACCEPTS.
        val st = stack(); st.ops.proposalMemo.reset(MemoMode.SHADOW)
        GraphNode.resetIdCounter()
        st.splitter.resetConceptCounter()
        val root = GraphNode(label = "Root", depth = 0)
        val a = leaf("A", root, 0)
        leaf("B", root, 1)
        val e = leaf("E", root, 6)
        corpus.forEach { GraphNode.registerEmbedding(it) }
        runBlocking { st.ops.reassignQueries(DagRoot(root), corpus, gt, currentIteration = 2) }
        assertTrue(e.queryWeights.isEmpty() && e.residualQueries.isEmpty(), "E must attract nothing: ${e.queryWeights.size}")
        val fake = FakeSplit(a, 2, st.splitter)
        var acceptNow = false
        var acceptRuns = 0
        val action: suspend () -> Boolean = {
            if (acceptNow) { acceptRuns++; root.children.remove(e); e.parents.remove(root); true } else fake.run()
        }
        fun call(iter: Int) = runBlocking {
            st.ops.tryProposal(DagRoot(root), a, corpus, gt, iter, ProposalType.GROW,
                proposalKey = "k2", actionId = "k2") { action() }
        }
        val logger = org.slf4j.LoggerFactory.getLogger("taxonomy.ProposalMemo") as ch.qos.logback.classic.Logger
        val appender = ch.qos.logback.core.read.ListAppender<ch.qos.logback.classic.spi.ILoggingEvent>().apply { start() }
        logger.addAppender(appender)
        try {
            assertEquals(ProposalOutcome.REJECTED, call(2))
            assertEquals(1, st.ops.proposalMemo.size, "the rejection must be stored")
            st.ops.invalidateCachedJ()   // next iteration, as the engine does
            acceptNow = true
            assertEquals(ProposalOutcome.ACCEPTED, call(3))
            assertEquals(2, acceptRuns, "base J uncached: the accepting action ran twice (fully evaluated)")
        } finally {
            logger.detachAppender(appender)
        }
        val m = st.ops.proposalMemo.snapshot()
        assertEquals(1L, m.shadowHits, "the second call was a would-be hit")
        assertEquals(1L, m.shadowMismatches, "REJECTED entry vs ACCEPTED evaluation must count as a mismatch")
        assertEquals(1L, m.misses)
        assertEquals(0L, m.hits)
        assertNull(m.disabledReason)
        val lines = appender.list.filter {
            it.level == ch.qos.logback.classic.Level.ERROR && it.formattedMessage.contains("[MEMO-X SHADOW MISMATCH]")
        }
        assertEquals(1, lines.size, "exactly one mismatch line — was: " +
            appender.list.joinToString(" | ") { it.formattedMessage })
        val msg = lines[0].formattedMessage
        assertTrue(msg.contains("outcome REJECTED (iter 2) vs ACCEPTED (iter 3)"), msg)
        assertTrue(msg.contains("site '${a.id}'") && msg.contains("GROW") && msg.contains("action='k2'"), msg)
    }

    @Test
    fun `memo self-disables on a counter invariant violation and falls back to full evaluation`() {
        val st = stack(); st.ops.proposalMemo.reset(MemoMode.ON)
        val dag = freshDag(st)
        val fake = FakeSplit(dag.a, 2, st.splitter).apply { extraOnSecond = true }
        propose(st, dag, fake)   // base uncached -> two executions, the second creates one more node
        assertEquals(2, fake.invocations)
        val reason = st.ops.proposalMemo.disabledReason
        assertNotNull(reason, "a consumption mismatch between the two executions must disable the memo")
        assertTrue(reason!!.contains("ids=3"), reason)
        assertFalse(st.ops.proposalMemo.active)
        assertEquals(0, st.ops.proposalMemo.size, "nothing may be stored after a violation")
        // Fail-closed: the same call again is a full evaluation.
        propose(st, dag, fake)
        assertEquals(3, fake.invocations)
        assertEquals(0L, st.ops.proposalMemo.hits)
        val m = st.ops.proposalMemo.snapshot()
        assertEquals(reason, m.disabledReason)
    }

    @Test
    fun `an action with unrestored side effects is never stored`() {
        // A fusion blends the target's NiW posterior and GraphStateBackup does not restore it.
        // Model that: the fake also bumps the site's niwKappa0. The evaluation then leaves the
        // state digest changed, the entry is refused, and the next identical call is a miss.
        val st = stack(); st.ops.proposalMemo.reset(MemoMode.ON)
        val dag = freshDag(st)
        val fake = FakeSplit(dag.a, 2, st.splitter)
        var invocations = 0
        val action: suspend () -> Boolean = { invocations++; dag.a.niwKappo0Bump(); fake.run() }
        val o1 = runBlocking {
            st.ops.tryProposal(DagRoot(dag.root), dag.a, corpus, gt, 2, ProposalType.GROW, proposalKey = "k2") { action() }
        }
        assertNotEquals(ProposalOutcome.ACCEPTED, o1)
        assertEquals(0, st.ops.proposalMemo.size)
        assertEquals(1L, st.ops.proposalMemo.notStoredSideEffects)
        runBlocking {
            st.ops.tryProposal(DagRoot(dag.root), dag.a, corpus, gt, 2, ProposalType.GROW, proposalKey = "k2") { action() }
        }
        assertEquals(3, invocations, "no hit is possible: the entry was never stored")
        assertEquals(0L, st.ops.proposalMemo.hits)
    }

    private fun GraphNode.niwKappo0Bump() { niwKappa0 += 1.0 }

    @Test
    fun `per-run reset drops entries`() {
        val st = stack(); st.ops.proposalMemo.reset(MemoMode.ON)
        val dag = freshDag(st)
        val fake = FakeSplit(dag.a, 2, st.splitter)
        propose(st, dag, fake)
        assertEquals(1, st.ops.proposalMemo.size)
        st.ops.proposalMemo.reset(MemoMode.ON)
        assertEquals(0, st.ops.proposalMemo.size)
        propose(st, dag, fake)
        assertEquals(3, fake.invocations, "after a reset the same call is a miss")
        val m = st.ops.proposalMemo.snapshot()
        assertEquals(0L, m.hits); assertEquals(1L, m.misses)
    }

    @Test
    fun `iteration 1 is never memoized`() {
        val st = stack(); st.ops.proposalMemo.reset(MemoMode.ON)
        val dag = freshDag(st)
        val fake = FakeSplit(dag.a, 2, st.splitter)
        propose(st, dag, fake, iter = 1)
        propose(st, dag, fake, iter = 1)
        assertEquals(3, fake.invocations)
        assertEquals(0, st.ops.proposalMemo.size)
        assertEquals(0L, st.ops.proposalMemo.misses)
    }
}
