package taxonomy

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import taxonomy.config.TaxonomyConfig
import taxonomy.model.Embedding
import taxonomy.model.EmbeddingSlice
import taxonomy.model.GraphNode
import taxonomy.operations.MemoKey
import taxonomy.operations.MemoMode
import taxonomy.operations.ProposalMemo
import taxonomy.operations.ProposalType
import taxonomy.utils.StatisticsUtils

/**
 * PERF-8: the exact memo's key is a pure function of every input that determines a proposal,
 * and nothing else. Each named mutation below is applied and then undone: the key must differ
 * after the apply AND return to the original after the undo, so a "mutation" that does not
 * actually mutate is caught rather than silently passing.
 *
 * The lossy fingerprint memo's false-hit incident (a rejected k=2 memo-skipping k=3) is the
 * class of bug this test exists to make impossible for the exact memo: omit an input from the
 * key and the corresponding row here fails.
 */
class ProposalMemoKeyTest {

    private val dim = 8
    private var prevWidth = 256
    private lateinit var config: TaxonomyConfig
    private lateinit var root: GraphNode
    private lateinit var leafA: GraphNode
    private lateinit var leafB: GraphNode
    private lateinit var corpus: List<Embedding>
    private lateinit var gt: Map<String, List<String>>
    private val memo = ProposalMemo()

    private fun unit(vararg v: Double): FloatArray {
        val n = kotlin.math.sqrt(v.sumOf { it * it })
        return FloatArray(dim) { i -> if (i < v.size) (v[i] / n).toFloat() else 0f }
    }

    private fun leaf(label: String, parent: GraphNode, axis: Int, id: String? = null): GraphNode =
        (if (id == null) GraphNode(label = label, depth = parent.depth + 1)
         else GraphNode(id = id, label = label, depth = parent.depth + 1)).apply {
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

    private fun buildDag(): Triple<GraphNode, GraphNode, GraphNode> {
        GraphNode.resetIdCounter()
        // Explicit ids with one String.hashCode ("Aa" and "BB" collide, so every 4-char
        // combination of them does): the three nodes share a ConcurrentHashMap bin, which the
        // edge walk-order rows of the mutation test rely on. Everything else is unaffected.
        val r = GraphNode(id = "AaAa", label = "Root", depth = 0)
        val a = leaf("A", r, 0, id = "AaBB")
        val b = leaf("B", r, 1, id = "BBAa")
        // 12 unit-norm embeddings, 6 per leaf, deterministic.
        val rng = java.util.Random(7)
        val embs = (0 until 12).map { i ->
            val axis = if (i < 6) 0 else 1
            val v = DoubleArray(dim) { d -> (if (d == axis) 1.0 else 0.0) + 0.05 * rng.nextGaussian() }
            Embedding(rawText = "q$i", distilledText = "q$i", values = unit(*v), queryId = i)
        }
        embs.forEach { GraphNode.registerEmbedding(it) }
        for ((i, e) in embs.withIndex()) {
            val leaf = if (i < 6) a else b
            leaf.queryWeights[e.rawText] = 1.0
            leaf.queries.add(e)
        }
        r.updateAllShrinkages()
        corpus = embs
        return Triple(r, a, b)
    }

    @BeforeEach
    fun setUp() {
        prevWidth = EmbeddingSlice.width
        EmbeddingSlice.width = dim
        config = TaxonomyConfig().apply {
            formalism.embeddingSliceDim = dim
            formalism.enableGtWarmStart = false
        }
        val (r, a, b) = buildDag()
        root = r; leafA = a; leafB = b
        gt = corpus.associate { it.rawText to listOf(if (it.queryId < 6) "A" else "B") }
        memo.reset(MemoMode.ON)
    }

    @AfterEach
    fun tearDown() {
        EmbeddingSlice.width = prevWidth
    }

    private fun key(
        site: GraphNode = leafA, type: ProposalType = ProposalType.GROW, actionId: String = "k2",
        iter: Int = 2, corpusList: List<Embedding> = corpus
    ): MemoKey = memo.keyFor(root, corpusList, gt, config, iter, site, type, actionId)

    @Test
    fun `digest is a pure function of state`() {
        val k1 = key()
        val k2 = key()
        assertEquals(k1, k2, "two keys on an untouched DAG must be equal")
        assertEquals(64, k1.stateDigest.length)

        // An independently constructed identical DAG (same ids via resetIdCounter) keys the same.
        val (r2, a2, _) = buildDag()
        val k3 = memo.keyFor(r2, corpus, gt, config, 2, a2, ProposalType.GROW, "k2")
        assertEquals(k1, k3, "an identical DAG built independently must key identically")
    }

    private class Mutation(val name: String, val apply: () -> Unit, val undo: () -> Unit)

    @Test
    fun `every mutated input changes the key and restoring it restores the key`() {
        val k0 = key()
        val wKey = leafA.queryWeights.keys.first()
        val w0 = leafA.queryWeights[wKey]!!
        val bKey = leafB.queryWeights.keys.first()
        val b0 = leafB.queryWeights[bKey]!!
        val mu0 = leafA.vmfMu[0]
        val kappa0 = leafA.vmfKappa
        val logN0 = leafA.vmfLogNormalizer
        val shrink0 = root.childCentroidShrinkage
        val depth0 = leafA.depth
        val slice0 = leafA.sliceDim
        val label0 = leafA.label
        val lambda0 = leafA.niwLambda[0]
        val tau0 = config.formalism.tau
        val mcs0 = config.formalism.minClusterSize
        val bars0 = config.formalism.adaptiveBars
        val width0 = EmbeddingSlice.width
        val prof0 = config.diagnostics.enableProfiling
        val dasgupta0 = leafA.dasguptaDeltaNorm
        val extraQ = Embedding(rawText = "extra", distilledText = "extra", values = unit(1.0, 1.0), queryId = 99)
        val removedQ = corpus[3]
        val removedIdx = leafA.queries.indexOf(removedQ)
        val q0 = leafA.queries[0]
        lateinit var extraChild: GraphNode

        val mutations = listOf(
            Mutation("weight +1 ulp", { leafA.queryWeights[wKey] = Math.nextUp(w0) }, { leafA.queryWeights[wKey] = w0 }),
            Mutation("weight on an unrelated leaf +1 ulp", { leafB.queryWeights[bKey] = Math.nextUp(b0) }, { leafB.queryWeights[bKey] = b0 }),
            Mutation("weight 0.0 -> -0.0",
                { leafA.queryWeights[wKey] = 0.0; leafA.queryWeights[wKey] = -0.0 },
                { leafA.queryWeights[wKey] = w0 }).let {
                // The two keys must differ from each other too: raw bits, not numeric equality.
                leafA.queryWeights[wKey] = 0.0; val kz = key()
                leafA.queryWeights[wKey] = -0.0; val knz = key()
                leafA.queryWeights[wKey] = w0
                assertNotEquals(kz, knz, "0.0 and -0.0 must key differently")
                it
            },
            Mutation("add a query to a leaf",
                { leafA.queryWeights[extraQ.rawText] = 1.0; leafA.queries.add(extraQ) },
                { leafA.queryWeights.remove(extraQ.rawText); leafA.queries.remove(extraQ) }),
            Mutation("remove a query",
                { leafA.queryWeights.remove(removedQ.rawText); leafA.queries.remove(removedQ) },
                // Re-insert at the original index: the list order is in the key (see below).
                { leafA.queryWeights[removedQ.rawText] = 1.0; leafA.queries.add(removedIdx, removedQ) }),
            Mutation("vmfMu component +1 ulp", { leafA.vmfMu[0] = Math.nextUp(mu0) }, { leafA.vmfMu[0] = mu0 }),
            Mutation("vmfKappa +1 ulp", { leafA.vmfKappa = Math.nextUp(kappa0) }, { leafA.vmfKappa = kappa0 }),
            Mutation("vmfLogNormalizer", { leafA.vmfLogNormalizer = logN0 + 1.0 }, { leafA.vmfLogNormalizer = logN0 }),
            Mutation("childCentroidShrinkage", { root.childCentroidShrinkage = shrink0 * 0.5 }, { root.childCentroidShrinkage = shrink0 }),
            Mutation("depth", { leafA.depth = depth0 + 1 }, { leafA.depth = depth0 }),
            Mutation("sliceDim", { leafA.sliceDim = slice0 - 1 }, { leafA.sliceDim = slice0 }),
            Mutation("label", { leafA.label = "A'" }, { leafA.label = label0 }),
            Mutation("isBridge", { leafA.isBridge = true }, { leafA.isBridge = false }),
            Mutation("add a residualQuery", { leafA.residualQueries.add("5") }, { leafA.residualQueries.remove("5") }),
            Mutation("residualConfidence value",
                { leafA.residualQueries.add("5"); leafA.residualConfidences["5"] = 0.25 },
                { leafA.residualConfidences.remove("5"); leafA.residualQueries.remove("5") }),
            Mutation("add a child node",
                { extraChild = leaf("C", leafA, 2) },
                { leafA.children.remove(extraChild); extraChild.parents.clear() }),
            Mutation("add a crossLinkChild",
                { root.crossLinkChildren.add(leafA) },
                { root.crossLinkChildren.remove(leafA) }),
            Mutation("add a parent edge",
                { leafA.parents.add(leafB) },
                { leafA.parents.remove(leafB) }),
            // Edge WALK ORDER is load-bearing (updateChildCentroidShrinkage accumulates over
            // children + crossLinkChildren in iteration order; the trickler and every branch
            // walk iterate children in iteration order). The edge collections are
            // ConcurrentHashMap key sets, whose order within a hash bin is insertion order; the
            // fixture ids collide (see buildDag), so re-inserting the same two children in the
            // other order is a content-identical set walked in the other order — and that must
            // be a different key (the sorted-id digest this row replaced could not tell).
            Mutation("re-insert the root's two children in the other order (same set, other walk order)",
                { root.children.clear(); root.children.add(leafB); root.children.add(leafA) },
                { root.children.clear(); root.children.add(leafA); root.children.add(leafB) }),
            Mutation("re-insert a node's parents in the other order",
                { leafA.parents.clear(); leafA.parents.add(leafB); leafA.parents.add(root) },
                { leafA.parents.clear(); leafA.parents.add(root) }).let {
                // Pure order check: {root, B} inserted root-first vs B-first must key differently.
                leafA.parents.add(leafB); val kP1 = key()
                leafA.parents.clear(); leafA.parents.add(leafB); leafA.parents.add(root); val kP2 = key()
                leafA.parents.clear(); leafA.parents.add(root)
                assertNotEquals(kP1, kP2, "parents walk order must be in the key")
                assertEquals(k0, key())
                it
            },
            // `queries` CONTENT is in the key even when queryWeights and the size are unchanged
            // (its rawTexts are digested as a sorted multiset) ...
            Mutation("replace one entry of queries, queryWeights untouched",
                { leafA.queries[0] = extraQ }, { leafA.queries[0] = q0 }),
            Mutation("niwLambda component", { leafA.niwLambda[0] = Math.nextUp(lambda0) }, { leafA.niwLambda[0] = lambda0 }),
            Mutation("dasguptaDeltaNorm (persisted, written by every evaluated split)",
                { leafA.dasguptaDeltaNorm = dasgupta0 + 0.01 }, { leafA.dasguptaDeltaNorm = dasgupta0 }),
            Mutation("config.formalism.tau", { config.formalism.tau = tau0 * 2 }, { config.formalism.tau = tau0 }),
            Mutation("config.formalism.minClusterSize", { config.formalism.minClusterSize = mcs0 + 1 }, { config.formalism.minClusterSize = mcs0 }),
            Mutation("adaptiveBars entry", { config.formalism.adaptiveBars = mapOf("A" to 0.03) }, { config.formalism.adaptiveBars = bars0 }),
            Mutation("EmbeddingSlice.width", { EmbeddingSlice.width = width0 + 1 }, { EmbeddingSlice.width = width0 }),
            Mutation("enableProfiling", { config.diagnostics.enableProfiling = !prof0 }, { config.diagnostics.enableProfiling = prof0 }),
        )
        // Precondition of the walk-order rows: the colliding fixture ids really share a bin, so
        // re-insertion in the other order really reverses the walk (not vacuous if CHM changes).
        run {
            val before = root.children.map { it.id }
            root.children.clear(); root.children.add(leafB); root.children.add(leafA)
            val after = root.children.map { it.id }
            root.children.clear(); root.children.add(leafA); root.children.add(leafB)
            assertEquals(before.reversed(), after, "fixture ids must share a hash bin so insertion order is walk order")
            assertEquals(before, root.children.map { it.id })
            assertEquals(k0, key())
        }
        // ... but its list ORDER is deliberately not: reassignQueries appends concurrently in
        // arrival order, so the order is a scheduling artifact that would defeat every
        // cross-iteration hit (see ProposalMemo class doc, item 1).
        run {
            java.util.Collections.swap(leafA.queries, 0, 1)
            assertEquals(k0, key(), "queries list order is a scheduling artifact and must NOT be in the key")
            java.util.Collections.swap(leafA.queries, 0, 1)
        }
        for (m in mutations) {
            m.apply()
            val kMut = key()
            assertNotEquals(k0, kMut, "mutation '${m.name}' must change the key")
            m.undo()
            val kBack = key()
            assertEquals(k0, kBack, "undoing '${m.name}' must restore the key exactly (the mutation or its undo is wrong)")
        }
    }

    @Test
    fun `corpus content is an input - a list with one value changed keys differently`() {
        val k0 = key()
        val changed = corpus.toMutableList()
        val e = changed[0]
        val v = e.values.copyOf().also { it[0] = Math.nextUp(it[0]) }
        changed[0] = Embedding(rawText = e.rawText, distilledText = e.distilledText, values = v, queryId = e.queryId)
        assertNotEquals(k0, key(corpusList = changed), "one embedding value +1 ulp must change the key")
        // The queryId sequence is re-hashed on every call (assignQueryIds rewrites it), even on
        // the same list identity.
        val id0 = corpus[0].queryId
        corpus[0].queryId = id0 + 1000
        assertNotEquals(k0, key(), "a queryId change on the same list must change the key")
        corpus[0].queryId = id0
        assertEquals(k0, key())
    }

    @Test
    fun `the iteration number is not an input, but the gt-bias regime is`() {
        // Without gt warm start, iteration 2 vs 3 is the same regime.
        assertEquals(key(iter = 2), key(iter = 3))
        // With it, iteration 1 (bias on) differs from iteration 2 (bias off).
        config.formalism.enableGtWarmStart = true
        assertNotEquals(key(iter = 1), key(iter = 2))
        assertEquals(key(iter = 2), key(iter = 3))
        config.formalism.enableGtWarmStart = false
    }

    @Test
    fun `site, type and actionId discriminate`() {
        val keys = listOf(
            key(leafA, ProposalType.GROW, "k2"),
            key(leafA, ProposalType.GROW, "k3"),
            key(leafB, ProposalType.GROW, "k2"),
            key(leafA, ProposalType.SHRINK, "passthrough:x"),
            key(root, ProposalType.SHRINK, "fuse:a+b"),
            key(root, ProposalType.SHRINK, "fuse:a+c"),
        )
        for (i in keys.indices) for (j in i + 1 until keys.size) {
            assertNotEquals(keys[i], keys[j], "keys $i and $j must differ")
        }
        // Same state digest throughout: the discrimination is in the proposal identity.
        assertEquals(1, keys.map { it.stateDigest }.distinct().size)
    }

    @Test
    fun `excluded diagnostics do not change the key`() {
        // muResultantCosine is recomputed from mu and the children by updateChildCentroidShrinkage,
        // read only by an engine log line and never persisted; it is the ONE field deliberately
        // left out. Everything the persistence layer writes (dasguptaDeltaNorm, phaseCompleted,
        // dOverN, ...) is IN the key — see the mutation test above for dasguptaDeltaNorm.
        val k0 = key()
        val c0 = root.muResultantCosine
        root.muResultantCosine = 0.123
        assertEquals(k0, key(), "muResultantCosine is excluded by design")
        root.muResultantCosine = c0
    }

    @Test
    fun `persisted diagnostics are in the key`() {
        val k0 = key()
        leafA.phaseCompleted = leafA.phaseCompleted or 16
        assertNotEquals(k0, key(), "phaseCompleted is persisted, so it is in the key")
        leafA.phaseCompleted = leafA.phaseCompleted and 16.inv()
        assertEquals(k0, key())
        leafA.dOverN = 3.5
        assertNotEquals(k0, key(), "dOverN is persisted, so it is in the key")
        leafA.dOverN = 0.0
        assertEquals(k0, key())
    }

    @Test
    fun `lookup drops every entry of a different state and counts it`() {
        val k0 = key()
        memo.store(k0, taxonomy.operations.MemoEntry(taxonomy.operations.ProposalOutcome.REJECTED, 2, 2, 2, null, null, null))
        memo.store(k0.copy(actionId = "k3"), taxonomy.operations.MemoEntry(taxonomy.operations.ProposalOutcome.NO_PROPOSAL, 0, 0, 2, null, null, null))
        assertEquals(2, memo.size)
        assertEquals(k0, key())
        assertEquals(taxonomy.operations.ProposalOutcome.REJECTED, memo.lookup(k0)!!.outcome)
        assertEquals(0, memo.misses)
        // Mutate the state: the next lookup drops both entries.
        leafB.vmfKappa = Math.nextUp(leafB.vmfKappa)
        assertEquals(null, memo.lookup(key()))
        assertEquals(0, memo.size)
        assertEquals(2, memo.invalidations)
        assertEquals(1, memo.stateChanges)
        // A bare lookup counts no miss: the hot path records one only after the lossy
        // fingerprint memo declined to answer (a lossy-answered absence is lossyShadowed).
        assertEquals(0, memo.misses)
        memo.recordMiss()
        assertEquals(1, memo.misses)
        // reset clears everything, counters included.
        memo.reset(MemoMode.ON)
        assertEquals(0, memo.size)
        assertEquals(0, memo.hits + memo.misses + memo.invalidations + memo.stateChanges)
    }

    @Test
    fun `mode parsing is strict`() {
        assertEquals(MemoMode.OFF, MemoMode.parse("off"))
        assertEquals(MemoMode.SHADOW, MemoMode.parse(" Shadow "))
        assertEquals(MemoMode.ON, MemoMode.parse("on"))
        org.junit.jupiter.api.assertThrows<IllegalArgumentException> { MemoMode.parse("onn") }
        org.junit.jupiter.api.assertThrows<IllegalArgumentException> { MemoMode.parse("") }
    }
}
