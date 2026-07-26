package taxonomy

import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.model.GraphNode
import taxonomy.operations.TaxonomyMerger
import taxonomy.operations.isTreeLegalFusionPair

/**
 * Guards the tree invariant of the redundant-fusion pass.
 *
 * The pass enumerates ALL node pairs in the graph, not just siblings. Because the fuse
 * redirects the source's parent edges onto the surviving target while the target keeps its
 * own, a cross-parent pair leaves the survivor with two parents — polyhierarchy created by
 * merge bookkeeping rather than by any bridge selector. These cases are what produced
 * BridgeCount=2 on the nominally strict-tree L9_007 screening cell.
 */
class TreeFusionInvariantTest {

    private fun node(label: String, depth: Int) = GraphNode(label = label, depth = depth)

    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child)
        child.parents.add(parent)
    }

    @Test
    fun `siblings under the same parent are fusable`() {
        val parent = node("Chemistry", 1)
        val a = node("A", 2)
        val b = node("B", 2)
        link(parent, a)
        link(parent, b)

        assertTrue(isTreeLegalFusionPair(a, b), "same-parent pairs must remain fusable")
    }

    @Test
    fun `nodes under different parents are not fusable`() {
        val chemistry = node("Chemistry", 1)
        val physics = node("Physics", 1)
        val a = node("A", 2)
        val b = node("B", 2)
        link(chemistry, a)
        link(physics, b)

        assertFalse(
            isTreeLegalFusionPair(a, b),
            "cross-parent fusion would union both lineages onto the survivor"
        )
    }

    @Test
    fun `fusing across parents would give the survivor two parents`() {
        // Reproduces the L9_007 iteration-3-to-4 transition in miniature: were the pair
        // admitted, fuseNodes' parent redirect would leave the target parented by both
        // depth-1 anchors, which is precisely what isBridge counts.
        val chemistry = node("Chemistry", 1)
        val physics = node("Physics", 1)
        val target = node("survivor", 2)
        val source = node("destroyed", 2)
        link(chemistry, source)
        link(physics, target)

        // The redirect step, in isolation: adopt the source's parents onto the target.
        source.parents.forEach { target.parents.add(it) }

        assertTrue(target.parents.size > 1, "redirect unions the lineages")
        assertFalse(
            isTreeLegalFusionPair(target, source),
            "the guard must reject exactly this pair before the redirect can run"
        )
    }

    @Test
    fun `a node is trivially fusable with itself and unaffected by child sets`() {
        val parent = node("Chemistry", 1)
        val a = node("A", 2)
        val b = node("B", 2)
        link(parent, a)
        link(parent, b)
        // Differing children must not affect the parent-set comparison.
        link(a, node("A-child", 3))

        assertTrue(isTreeLegalFusionPair(a, b), "eligibility depends on parents, not children")
    }

    @Test
    fun `orphans are not treated as a matching pair by the guard alone`() {
        // Both have empty parent sets, so the guard alone says "equal". The pass rejects
        // these earlier via its isEmpty check; this test documents the division of labour so
        // a later refactor does not drop that check believing this guard covers it.
        val a = node("A", 2)
        val b = node("B", 2)

        assertTrue(isTreeLegalFusionPair(a, b), "guard compares parent sets only")
        assertTrue(a.parents.isEmpty() && b.parents.isEmpty(), "the isEmpty check is what rejects orphans")
    }

    // ── End-to-end: run the REAL fuse and assert the resulting graph is a tree ──────────
    //
    // Every test above checks the admission guard in isolation. The polyhierarchy is not
    // created by the guard, though — it is created by fuseNodes' parent-redirect step
    // (TaxonomyMerger.kt, `target.parents.add(parent)`). So the guard could stay correct
    // while a change to the fuse reintroduced BridgeCount > 0, and nothing would notice.

    private fun merger(): TaxonomyMerger = TaxonomyMerger(
        // fuseNodes is pure graph/parameter manipulation; none of these collaborators are
        // reached, so mocks keep the test at unit cost with no Spring context.
        mock(TaxonomyConfig::class.java),
        mock(TaxonomyLlmClient::class.java),
        mock(MMLUDatasetFetcher::class.java)
    )

    private fun fittedNode(label: String, depth: Int, d: Int = 8): GraphNode =
        GraphNode(label = label, depth = depth).apply {
            sliceDim = d
            vmfMu = FloatArray(d) { if (it == 0) 1.0f else 0.0f }
            vmfKappa = 10.0
        }

    /** Every node reachable from [root] via tree edges. */
    private fun reachable(root: GraphNode): List<GraphNode> {
        val seen = LinkedHashMap<String, GraphNode>()
        fun walk(n: GraphNode) {
            if (seen.put(n.id, n) != null) return
            n.children.forEach { walk(it) }
        }
        walk(root)
        return seen.values.toList()
    }

    private fun assertIsTree(root: GraphNode, context: String) {
        reachable(root).forEach { n ->
            if (n.id != root.id) {
                assertTrue(
                    n.parents.size <= 1,
                    "$context: '${n.label ?: n.id}' has ${n.parents.size} parents — not a tree"
                )
            }
        }
        // A tree edge must be mirrored on both endpoints, or the structure diff walks a graph
        // the router does not see.
        reachable(root).forEach { p ->
            p.children.forEach { c ->
                assertTrue(c.parents.contains(p), "$context: '${c.label}' is missing its parent edge")
            }
        }
    }

    @Test
    fun `fusing every guard-admitted pair leaves the graph a tree`() {
        val m = merger()
        val root = fittedNode("root", 0)
        val chemistry = fittedNode("Chemistry", 1)
        val physics = fittedNode("Physics", 1)
        link(root, chemistry)
        link(root, physics)

        val c1 = fittedNode("Organic", 2)
        val c2 = fittedNode("Inorganic", 2)
        val p1 = fittedNode("Optics", 2)
        val p2 = fittedNode("Mechanics", 2)
        link(chemistry, c1); link(chemistry, c2)
        link(physics, p1); link(physics, p2)

        // Mirror the pass's own enumeration: all pairs at depth > 1, admitted by the guard.
        val nodes = reachable(root).filter { it.depth > 1 }
        var fused = 0
        for (i in nodes.indices) {
            for (j in i + 1 until nodes.size) {
                val a = nodes[i]
                val b = nodes[j]
                if (a.parents.isEmpty() || b.parents.isEmpty()) continue
                if (!isTreeLegalFusionPair(a, b)) continue
                m.fuseNodes(a, b)
                fused++
            }
        }

        assertTrue(fused > 0, "the fixture must actually exercise the fuse")
        assertIsTree(root, "after $fused guard-admitted fusions")
    }

    @Test
    fun `bypassing the guard does create a two-parent node`() {
        // Negative control. Without this, the test above could pass because the fixture never
        // reaches a dangerous pair rather than because the guard works.
        val m = merger()
        val root = fittedNode("root", 0)
        val chemistry = fittedNode("Chemistry", 1)
        val physics = fittedNode("Physics", 1)
        link(root, chemistry)
        link(root, physics)

        val survivor = fittedNode("survivor", 2)
        val destroyed = fittedNode("destroyed", 2)
        link(chemistry, survivor)
        link(physics, destroyed)

        assertFalse(isTreeLegalFusionPair(survivor, destroyed), "the guard would have refused this pair")
        m.fuseNodes(survivor, destroyed)   // forced through anyway

        assertTrue(
            survivor.parents.size > 1,
            "fuseNodes' parent-redirect is what creates the polyhierarchy, so assertIsTree can detect it"
        )
    }
}
