package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.model.GraphNode
import taxonomy.utils.computeHierarchicalF1

/**
 * Kosmopoulos et al. (2014) hierarchical Precision / Recall / F₁.
 *
 * The test DAGs intentionally have no shared root (each top-level domain is a
 * parentless depth-1 node), so two leaves in different branches share no
 * ancestors — matching the convention that the artificial root is excluded.
 */
class HierarchicalF1Test {

    private fun node(label: String, depth: Int) = GraphNode(label = label, depth = depth)
    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child)
        child.parents.add(parent)
    }

    @Test
    fun perfect_routing_scores_one() {
        val a = node("A", 1)
        val a1 = node("a1", 2); val a2 = node("a2", 2)
        link(a, a1); link(a, a2)

        val predicted = mapOf("q1" to a1, "q2" to a2)
        val groundTruth = mapOf("q1" to a1, "q2" to a2)

        val (hP, hR, hF1) = computeHierarchicalF1(predicted, groundTruth)
        assertEquals(1.0, hP, 1e-9)
        assertEquals(1.0, hR, 1e-9)
        assertEquals(1.0, hF1, 1e-9)
    }

    @Test
    fun completely_wrong_branch_scores_near_zero() {
        // Two disjoint branches with no common ancestor.
        val a = node("A", 1); val a1 = node("a1", 2)
        val b = node("B", 1); val b1 = node("b1", 2)
        link(a, a1); link(b, b1)

        val predicted = mapOf("q1" to a1)
        val groundTruth = mapOf("q1" to b1)

        val (hP, hR, hF1) = computeHierarchicalF1(predicted, groundTruth)
        assertEquals(0.0, hP, 1e-9)
        assertEquals(0.0, hR, 1e-9)
        assertEquals(0.0, hF1, 1e-9, "Disjoint branches must give H-F₁ ≈ 0")
    }

    @Test
    fun predicting_parent_gives_full_precision_partial_recall() {
        // True leaf is a1 (path A → a1). Prediction stops at the parent A
        // (correct ancestor, missing child).
        val a = node("A", 1); val a1 = node("a1", 2)
        link(a, a1)

        val predicted = mapOf("q1" to a)    // {A}
        val groundTruth = mapOf("q1" to a1) // {a1, A}

        val (hP, hR, hF1) = computeHierarchicalF1(predicted, groundTruth)
        assertEquals(1.0, hP, 1e-9, "Predicted ancestors ⊆ true ancestors → precision 1")
        assertTrue(hR < 1.0, "Missing the leaf must drop recall below 1, was $hR")
        assertEquals(0.5, hR, 1e-9)
    }
}
