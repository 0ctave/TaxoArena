package taxonomy

import taxonomy.config.TaxonomyConfig
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.operations.TaxonomyTrickler
import taxonomy.operations.TrickleOptions
import taxonomy.utils.StatisticsUtils
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import kotlin.math.exp

/**
 * Guards the topological-order rewrite of [TaxonomyTrickler.trickle].
 *
 * The router used to be a DFS with backtracking, so it enumerated every root-to-node PATH
 * and accumulated arrival mass with logSumExp across those paths. It is now an O(V+E)
 * dynamic program over a topological order. The two agree only if the DP aggregates ALL
 * incoming edges before descending — the obvious failure mode of the rewrite is a
 * visit-once walk that keeps the first path's mass and silently drops the rest, which no
 * existing test would catch because every other test runs on trees, where paths == nodes.
 *
 * These cases are therefore built on a diamond, where the two routers can disagree.
 */
@SpringBootTest(
    classes = [org.eclipse.lmos.arc.app.TaxoAdaptApplication::class],
    properties = [
        "taxoadapt.execution.enable-tui=false",
        "taxoadapt.execution.run-batch=false",
        "taxoadapt.execution.start-service=false"
    ]
)
class TricklerMultiPathTest {

    @Autowired
    private lateinit var trickler: TaxonomyTrickler

    @Autowired
    private lateinit var config: TaxonomyConfig

    private val dim = 256

    /** A node whose mean direction is e_0, so every dot product against the probe is 1.0. */
    private fun node(label: String, depth: Int): GraphNode =
        GraphNode(label = label, depth = depth).apply {
            vmfMu = FloatArray(dim) { 0.0f }.apply { this[0] = 1.0f }
            vmfKappa = 10.0
            vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(dim, 10.0)
            // descentBar = (childCentroidShrinkage - descentMargin).coerceAtLeast(0.0) = 0,
            // so the Jensen gate never stops the walk and the test isolates aggregation.
            childCentroidShrinkage = 0.0
        }

    private fun probe() = Embedding(
        rawText = "probe",
        distilledText = "probe",
        values = FloatArray(dim) { 0.0f }.apply { this[0] = 1.0f }
    )

    private fun opts() = TrickleOptions(
        membershipFloor = 0.05,
        maxAssignments = Int.MAX_VALUE,
        readOnly = true,
        enableGtBias = false,
        originalCategories = null
    )

    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child)
        child.parents.add(parent)
    }

    private fun crossLink(parent: GraphNode, child: GraphNode) {
        parent.crossLinkChildren.add(child)
        child.parents.add(parent)
    }

    /**
     * Diamond:  root -> A -> L
     *           root -> B -> L (cross-link), B -> M
     *
     * All mean directions are identical, so every sibling set splits its mass uniformly:
     *   P(A) = P(B) = 1/2;  A's only child takes all of it;  B splits between L and M.
     *   P(L) = 1/2 + 1/2 * 1/2 = 3/4      P(M) = 1/2 * 1/2 = 1/4
     *
     * A visit-once DP that dropped B's contribution to L would instead give P(L) = 1/2 and
     * P(M) = 1/4, i.e. a 2:1 split after renormalisation rather than 3:1.
     */
    @Test
    fun multiPathArrivalMassIsSummedNotOverwritten() {
        assertTrue(config.formalism.enableBridging, "cross-link routing must be on for this test")

        val root = node("Root", 0)
        val a = node("A", 1)
        val b = node("B", 1)
        val l = node("L", 2)
        val m = node("M", 2)

        link(root, a); link(root, b)
        link(a, l)
        crossLink(b, l)
        link(b, m)

        val res = trickler.trickle(probe(), root, opts())
        val byLabel = res.memberships.entries.associate { (n, lp) -> n.label to exp(lp) }

        val pL = byLabel["L"] ?: fail("leaf L was never reached")
        val pM = byLabel["M"] ?: fail("leaf M was never reached")

        assertEquals(1.0, pL + pM, 1e-12, "memberships must normalise to 1")
        assertEquals(0.75, pL, 1e-12, "L must receive mass from BOTH the tree edge and the cross-link")
        assertEquals(0.25, pM, 1e-12)
    }

    /**
     * The same diamond, but the join node has its own children. The subtree below a join
     * must be fed the AGGREGATED mass exactly once — the enumerating walk re-descended it
     * once per incoming path, which is the cost the rewrite removes; the values must match.
     *
     *   P(L) = 3/4 split evenly over L1, L2 -> 3/8 each;  P(M) = 1/4.
     */
    @Test
    fun subtreeBelowAJoinReceivesAggregatedMassOnce() {
        val root = node("Root", 0)
        val a = node("A", 1)
        val b = node("B", 1)
        val l = node("L", 2)
        val m = node("M", 2)
        val l1 = node("L1", 3)
        val l2 = node("L2", 3)

        link(root, a); link(root, b)
        link(a, l)
        crossLink(b, l)
        link(b, m)
        link(l, l1); link(l, l2)

        val res = trickler.trickle(probe(), root, opts())
        val byLabel = res.memberships.entries.associate { (n, lp) -> n.label to exp(lp) }

        assertNull(byLabel["L"], "L has children, so it is no longer a leaf destination")
        assertEquals(0.375, byLabel["L1"] ?: fail("L1 unreached"), 1e-12)
        assertEquals(0.375, byLabel["L2"] ?: fail("L2 unreached"), 1e-12)
        assertEquals(0.25, byLabel["M"] ?: fail("M unreached"), 1e-12)
    }

    /**
     * On a tree the rewrite must be a no-op: paths == nodes, so DFS enumeration and the DP
     * visit each node exactly once and any divergence here would be a plain regression.
     */
    @Test
    fun treeRoutingIsUnchanged() {
        val root = node("Root", 0)
        val a = node("A", 1)
        val b = node("B", 1)
        val a1 = node("A1", 2)
        val a2 = node("A2", 2)

        link(root, a); link(root, b)
        link(a, a1); link(a, a2)

        val res = trickler.trickle(probe(), root, opts())
        val byLabel = res.memberships.entries.associate { (n, lp) -> n.label to exp(lp) }

        assertEquals(0.25, byLabel["A1"] ?: fail("A1 unreached"), 1e-12)
        assertEquals(0.25, byLabel["A2"] ?: fail("A2 unreached"), 1e-12)
        assertEquals(0.50, byLabel["B"] ?: fail("B unreached"), 1e-12)
    }
}

/**
 * Differential test: the production topological router vs the pre-rewrite path-enumerating
 * walk, on graphs that actually contain bridges.
 *
 * Both traversals call the same [TaxonomyTrickler.childTransitions], so scoring, the descent
 * gate and the beam are shared by construction and the ONLY difference under test is how
 * arrival mass is accumulated — plus where LOG_NEGLIGIBLE_PATH is applied (per path in the
 * reference, per summed node posterior in production).
 */
@SpringBootTest(
    classes = [org.eclipse.lmos.arc.app.TaxoAdaptApplication::class],
    properties = [
        "taxoadapt.execution.enable-tui=false",
        "taxoadapt.execution.run-batch=false",
        "taxoadapt.execution.start-service=false"
    ]
)
class TricklerRouterEquivalenceTest {

    @Autowired
    private lateinit var trickler: TaxonomyTrickler

    private val dim = 256
    private val rng = java.util.Random(42)

    private fun randUnit(): FloatArray {
        val v = FloatArray(dim)
        var n = 0.0
        for (i in 0 until dim) { val g = rng.nextGaussian().toFloat(); v[i] = g; n += g * g }
        val inv = (1.0 / kotlin.math.sqrt(n)).toFloat()
        for (i in 0 until dim) v[i] *= inv
        return v
    }

    private fun node(label: String, depth: Int) = GraphNode(label = label, depth = depth).apply {
        vmfMu = randUnit()
        vmfKappa = 20.0 + rng.nextDouble() * 100.0
        vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(dim, vmfKappa)
        childCentroidShrinkage = 0.0   // never let the descent gate stop the walk
    }

    /** A 4-level tree with [bridges] extra cross-links wired across branches. */
    private fun buildDag(bridges: Int): GraphNode {
        val root = node("Root", 0)
        val level1 = (0 until 4).map { node("D$it", 1) }
        val level2 = ArrayList<GraphNode>()
        val level3 = ArrayList<GraphNode>()
        for ((i, d) in level1.withIndex()) {
            root.children.add(d); d.parents.add(root)
            for (j in 0 until 3) {
                val c = node("C$i$j", 2); level2.add(c)
                d.children.add(c); c.parents.add(d)
                for (k in 0 until 2) {
                    val l = node("L$i$j$k", 3); level3.add(l)
                    c.children.add(l); l.parents.add(c)
                }
            }
        }
        // Cross-link level-2 concepts under a different depth-1 domain, creating genuine
        // multi-path arrivals into each bridged node's whole subtree.
        var added = 0
        var idx = 0
        while (added < bridges && idx < level2.size) {
            val cand = level2[idx]
            val host = level1[(idx + 1) % level1.size]
            if (cand.parents.none { it === host } && !host.children.contains(cand)) {
                host.crossLinkChildren.add(cand); cand.parents.add(host); added++
            }
            idx++
        }
        return root
    }

    private fun probe() = Embedding(rawText = "q", distilledText = "q", values = randUnit())

    private fun opts() = TrickleOptions(
        membershipFloor = 0.05,
        maxAssignments = Int.MAX_VALUE,
        readOnly = true,
        enableGtBias = false,
        originalCategories = null
    )

    @Test
    fun topologicalRouterMatchesPathEnumerationOnBridgedGraphs() {
        for (bridgeCount in intArrayOf(0, 1, 4, 8)) {
            val root = buildDag(bridgeCount)
            root.updateAllShrinkages()
            // updateAllShrinkages recomputes the descent bar; force it open again so this test
            // isolates mass accumulation rather than gate behaviour.
            fun openGates(n: GraphNode, seen: MutableSet<String> = mutableSetOf()) {
                if (!seen.add(n.id)) return
                n.childCentroidShrinkage = 0.0
                n.children.forEach { openGates(it, seen) }
                n.crossLinkChildren.forEach { openGates(it, seen) }
            }
            openGates(root)

            var maxDiff = 0.0
            var worst = ""
            repeat(40) {
                val q = probe()
                val dp = trickler.trickle(q, root, opts()).allNodes
                    .entries.associate { (n, lp) -> n.id to lp }
                val ref = trickler.trickleByPathEnumeration(q, root, opts())
                // Reference returns UNnormalised log-mass; normalise it the same way trickle does.
                val maxL = ref.values.maxOrNull() ?: 0.0
                val lse = maxL + kotlin.math.ln(ref.values.sumOf { kotlin.math.exp(it - maxL) })
                val refNorm = ref.mapValues { (_, v) -> v - lse }

                assertEquals(refNorm.keys, dp.keys,
                    "bridges=$bridgeCount: the two routers reached different node sets")
                for ((id, refVal) in refNorm) {
                    val d = kotlin.math.abs(refVal - (dp[id] ?: Double.NaN))
                    if (d > maxDiff) { maxDiff = d; worst = id }
                }
            }
            assertTrue(maxDiff < 1e-12,
                "bridges=$bridgeCount: max log-posterior divergence $maxDiff at '$worst' exceeds 1e-12")
        }
    }
}
