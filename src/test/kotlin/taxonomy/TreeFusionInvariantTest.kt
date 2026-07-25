package taxonomy

import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.model.GraphNode
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
}
