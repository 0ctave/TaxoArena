package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import taxonomy.model.GraphNode
import taxonomy.utils.computeNormalisedSackin

/**
 * Normalised Sackin index = mean root-to-leaf depth (Sackin 1972; Fischer et al. 2021).
 */
class NormalisedSackinTest {

    private fun node(label: String, depth: Int) = GraphNode(label = label, depth = depth)
    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child); child.parents.add(parent)
    }

    @Test
    fun balanced_tree_returns_known_mean_depth() {
        // root(0) → a,b(1); each → two leaves(2). Four leaves, all at depth 2 → mean = 2.0.
        val root = node("root", 0)
        val a = node("a", 1); val b = node("b", 1)
        link(root, a); link(root, b)
        listOf("a1", "a2").forEach { link(a, node(it, 2)) }
        listOf("b1", "b2").forEach { link(b, node(it, 2)) }

        assertEquals(2.0, computeNormalisedSackin(root), 1e-9)
    }

    @Test
    fun single_leaf_tree_returns_zero() {
        // Root only: it is itself a leaf at depth 0 → mean depth 0.
        val root = node("root", 0)
        assertEquals(0.0, computeNormalisedSackin(root), 1e-9)
    }
}
