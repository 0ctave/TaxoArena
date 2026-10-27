package taxonomy.service

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.service.UnionRouting.Rule

/**
 * Stage 1c union root routing rules on a two-corpus synthetic graft, built so that the three
 * rules disagree on the same query: its nearest corpus ROOT is B, its nearest LEAF is under A.
 *
 *   union (d0)
 *   ├─ A (d1, mu = e1)        ├─ A/x (d2) ── A/x/leaf (d3, mu = e1)
 *   │                         └─ A/y (d2) ── A/y/leaf (d3, mu = 0.6 e1 + 0.8 e2)
 *   └─ B (d1, mu = e2)        └─ B/z (d2) ── B/z/leaf (d3, mu = e2)
 *
 *   query q = 0.5 e1 + 0.866 e2: cos to roots A 0.50 / B 0.87; cos to leaves 0.50 / 0.99 / 0.87.
 */
class UnionRoutingTest {

    private fun node(id: String, label: String, depth: Int, mu: FloatArray? = null): GraphNode =
        GraphNode(id = id, label = label, depth = depth).also { n -> if (mu != null) n.vmfMu = mu }

    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child); child.parents.add(parent); child.treeParentId = parent.id
    }

    private class Graft(val union: GraphNode, val a: GraphNode, val b: GraphNode,
                        val ax: GraphNode, val ay: GraphNode, val bz: GraphNode,
                        val axLeaf: GraphNode, val ayLeaf: GraphNode, val bzLeaf: GraphNode) {
        val leaves get() = listOf(axLeaf, ayLeaf, bzLeaf)
        val parents get() = UnionRouting.treeParents(union)
    }

    private fun graft(): Graft {
        val union = node("union", "A+B", 0)
        val a = node("A:n00000001", "A", 1, floatArrayOf(1f, 0f, 0f))
        val b = node("B:n00000001", "B", 1, floatArrayOf(0f, 1f, 0f))
        val ax = node("A:n00000002", "A/x", 2, floatArrayOf(1f, 0f, 0f))
        val ay = node("A:n00000003", "A/y", 2, floatArrayOf(0.6f, 0.8f, 0f))
        val bz = node("B:n00000002", "B/z", 2, floatArrayOf(0f, 1f, 0f))
        val axLeaf = node("A:n00000004", "A/x/leaf", 3, floatArrayOf(1f, 0f, 0f))
        val ayLeaf = node("A:n00000005", "A/y/leaf", 3, floatArrayOf(0.6f, 0.8f, 0f))
        val bzLeaf = node("B:n00000003", "B/z/leaf", 3, floatArrayOf(0f, 1f, 0f))
        link(union, a); link(union, b)
        link(a, ax); link(a, ay); link(b, bz)
        link(ax, axLeaf); link(ay, ayLeaf); link(bz, bzLeaf)
        UnionGraft.verify(union)
        return Graft(union, a, b, ax, ay, bz, axLeaf, ayLeaf, bzLeaf)
    }

    private val q = Embedding("q", "q", floatArrayOf(0.5f, 0.866f, 0f))

    /** A stand-in for the production descent: the first leaf (by id) beneath the start node, recording the start. */
    private class Descent {
        val starts = mutableListOf<GraphNode>()
        fun from(start: GraphNode): GraphNode? {
            starts.add(start)
            var cur = start
            while (!cur.isLeaf) cur = cur.children.minByOrNull { it.id } ?: return null
            return cur
        }
    }

    @Test
    fun `flatLeaf routes to the nearest leaf over ALL corpora and derives source and domain from it`() {
        val g = graft()
        val d = Descent()
        val r = UnionRouting.route(Rule.FLAT_LEAF, q, g.union, g.leaves, g.parents) { d.from(it) }
        assertSame(g.ayLeaf, r.leaf, "nearest leaf is A/y/leaf (cos 0.99), not B/z/leaf (0.87)")
        assertSame(g.a, r.source, "source = depth-1 ancestor of the leaf")
        assertSame(g.ay, UnionRouting.ancestorAt(r.leaf, 2, g.parents), "domain = depth-2 ancestor of the leaf")
        assertTrue(d.starts.isEmpty(), "flatLeaf never runs the descent")
    }

    @Test
    fun `sourceGate picks the nearest corpus root and descends only inside that corpus`() {
        val g = graft()
        val d = Descent()
        val r = UnionRouting.route(Rule.SOURCE_GATE, q, g.union, g.leaves, g.parents) { d.from(it) }
        assertSame(g.b, r.source, "nearest ROOT is B (cos 0.87 vs 0.50)")
        assertEquals(listOf(g.b), d.starts, "the descent starts at the chosen corpus root, never at the union root")
        assertSame(g.bzLeaf, r.leaf)
        assertSame(g.bz, UnionRouting.ancestorAt(r.leaf, 2, g.parents))
    }

    @Test
    fun `sourceGate keeps its source pick when the in-corpus descent stops above every leaf`() {
        val g = graft()
        val r = UnionRouting.route(Rule.SOURCE_GATE, q, g.union, g.leaves, g.parents) { null }
        assertSame(g.b, r.source)
        assertNull(r.leaf)
    }

    @Test
    fun `descent is the production walk from the union root`() {
        val g = graft()
        val d = Descent()
        val r = UnionRouting.route(Rule.DESCENT, q, g.union, g.leaves, g.parents) { d.from(it) }
        assertEquals(listOf(g.union), d.starts)
        assertSame(g.axLeaf, r.leaf)
        assertSame(g.a, r.source, "source is derived from the routed leaf's depth-1 ancestor")
        val none = UnionRouting.route(Rule.DESCENT, q, g.union, g.leaves, g.parents) { null }
        assertNull(none.leaf); assertNull(none.source)
    }

    @Test
    fun `nearest ignores unfitted nodes, uses the node's own slice width and breaks ties by order`() {
        val fitted = node("x", "x", 3, floatArrayOf(0f, 1f, 0f))
        val unfitted = node("u", "u", 3)
        assertSame(fitted, UnionRouting.nearest(q, listOf(unfitted, fitted)))
        assertNull(UnionRouting.nearest(q, listOf(unfitted)))
        assertNull(UnionRouting.nearest(q, emptyList()))
        // a 2-wide vMF sees the query projected (and renormalised) to its first two coordinates
        val wide = Embedding("w", "w", floatArrayOf(0.5f, 0.866f, 5f))
        val two = node("t", "t", 3, floatArrayOf(0.5f, 0.866f))
        assertEquals(1.0, UnionRouting.cosine(wide, two), 1e-4)   // (0.5, 0.866) has norm 0.99998
        val first = node("f", "f", 3, floatArrayOf(0f, 1f, 0f))
        val second = node("s", "s", 3, floatArrayOf(0f, 1f, 0f))
        assertSame(first, UnionRouting.nearest(q, listOf(first, second)))
    }

    @Test
    fun `tree ancestry follows tree edges from the union root`() {
        val g = graft()
        val p = g.parents
        assertSame(g.union, p[g.a.id]); assertSame(g.ay, p[g.ayLeaf.id])
        assertNull(p[g.union.id])
        assertSame(g.a, UnionRouting.ancestorAt(g.ayLeaf, 1, p))
        assertSame(g.ayLeaf, UnionRouting.ancestorAt(g.ayLeaf, 3, p))
        assertNull(UnionRouting.ancestorAt(g.a, 2, p), "no ancestor BELOW the node")
        assertNull(UnionRouting.ancestorAt(null, 1, p))
        assertEquals(listOf(g.a, g.b), UnionRouting.corpusRoots(g.union))
    }

    @Test
    fun `rule keys parse case-insensitively and unknown keys are refused`() {
        assertEquals(Rule.DESCENT, Rule.parse("descent"))
        assertEquals(Rule.FLAT_LEAF, Rule.parse("flatLeaf"))
        assertEquals(Rule.FLAT_LEAF, Rule.parse(" flatleaf "))
        assertEquals(Rule.SOURCE_GATE, Rule.parse("sourceGate"))
        assertEquals(Rule.DESCENT, Rule.parse(Rule.DEFAULT_KEY))
        assertThrows(IllegalArgumentException::class.java) { Rule.parse("flat") }
        assertThrows(IllegalArgumentException::class.java) { Rule.parse("") }
    }

    @Test
    fun `wilson interval reproduces the stage-1b union readout`() {
        // union_s42: 4,672 of 6,482 -> 72.08% [70.97, 73.16]
        val (lo, hi) = UnionRouting.wilson(4672, 6482)
        assertEquals(0.7097, lo, 5e-4); assertEquals(0.7316, hi, 5e-4)
        assertEquals(0.0 to 0.0, UnionRouting.wilson(0, 0))
        val (l1, h1) = UnionRouting.wilson(10, 10)
        assertTrue(l1 < 1.0 && h1 == 1.0)
    }
}
