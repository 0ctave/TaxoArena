package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.model.GraphNode
import taxonomy.utils.dagDendrogramPurity
import taxonomy.utils.findAllLCAs
import taxonomy.utils.shallowLCA

/**
 * Monath et al. (2021) DAG-compatible Dendrogram Purity using the shallowest LCA.
 */
class DagDendrogramPurityTest {

    private fun node(label: String, depth: Int) = GraphNode(label = label, depth = depth)
    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child)
        child.parents.add(parent)
    }

    @Test
    fun perfect_tree_is_fully_pure() {
        // root → A → {a1, a2}, root → B → {b1}
        val root = node("root", 0)
        val a = node("A", 1); val b = node("B", 1)
        val a1 = node("a1", 2); val a2 = node("a2", 2); val b1 = node("b1", 2)
        link(root, a); link(root, b)
        link(a, a1); link(a, a2); link(b, b1)

        val assignments = mapOf("q1" to a1, "q2" to a2, "q3" to b1)
        val gt = mapOf("q1" to "A", "q2" to "A", "q3" to "B")

        val purity = dagDendrogramPurity(assignments, gt)
        assertEquals(1.0, purity, 1e-9, "A clean tree must be perfectly pure")
    }

    @Test
    fun cross_link_reduces_purity_below_tree() {
        // Same tree, but b1 also becomes a (tree) child of A — a polyhierarchy
        // edge. Now A's subtree contains a B-labelled query, so the same-label
        // pair (q1,q2) is no longer pure.
        val root = node("root", 0)
        val a = node("A", 1); val b = node("B", 1)
        val a1 = node("a1", 2); val a2 = node("a2", 2); val b1 = node("b1", 2)
        link(root, a); link(root, b)
        link(a, a1); link(a, a2); link(b, b1)
        link(a, b1) // cross-link: b1 now has parents {B, A}

        val assignments = mapOf("q1" to a1, "q2" to a2, "q3" to b1)
        val gt = mapOf("q1" to "A", "q2" to "A", "q3" to "B")

        val purity = dagDendrogramPurity(assignments, gt)
        assertTrue(purity < 1.0, "Cross-link must lower purity below the tree value, was $purity")
        assertEquals(0.0, purity, 1e-9)
    }

    @Test
    fun shallowest_lca_is_selected() {
        // Diamond: T(1) → U(2) → {leafA(3), leafB(3)}, plus direct edges
        // T → leafA and T → leafB. Common ancestors of the leaves are {U, T};
        // the shallowest LCA is U (greater depth), not T.
        val t = node("T", 1)
        val u = node("U", 2)
        val leafA = node("leafA", 3); val leafB = node("leafB", 3)
        link(t, u)
        link(u, leafA); link(u, leafB)
        link(t, leafA); link(t, leafB)

        val all = findAllLCAs(leafA, leafB)
        assertTrue(u in all && t in all, "Both U and T are common ancestors")

        val lca = shallowLCA(leafA, leafB)
        assertEquals(u, lca, "Shallowest LCA must be the deepest common ancestor (U), not the root-ward T")
        assertEquals(2, lca.depth)
    }
}
