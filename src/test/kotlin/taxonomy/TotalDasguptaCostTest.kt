package taxonomy

import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.utils.computeTotalDasguptaCost

/**
 * Total Dasgupta cost (Dasgupta 2016). Lower cost ⇔ similar points share a smaller
 * (deeper) subtree. A balanced tree that respects the cluster structure must cost
 * less than a degenerate caterpillar that interleaves the clusters.
 */
class TotalDasguptaCostTest {

    private fun node(label: String, depth: Int) = GraphNode(label = label, depth = depth)
    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child); child.parents.add(parent)
    }
    private fun emb(text: String, vararg vals: Double) =
        Embedding(text, text, FloatArray(vals.size) { vals[it].toFloat() })

    @Test
    fun balanced_tree_with_random_points_is_positive_and_finite() {
        val root = node("root", 0)
        val a = node("a", 1); val b = node("b", 1)
        link(root, a); link(root, b)
        val leaves = listOf("a1" to a, "a2" to a, "b1" to b, "b2" to b).map { (lbl, parent) ->
            node(lbl, 2).also { link(parent, it) }
        }
        val rng = java.util.Random(42)
        val embeddings = mutableListOf<Embedding>()
        leaves.forEach { leaf ->
            repeat(5) { k ->
                val e = emb("${leaf.label}_q$k", rng.nextDouble() + 0.1, rng.nextDouble() + 0.1)
                leaf.queries.add(e); embeddings.add(e)
            }
        }
        val cost = computeTotalDasguptaCost(root, embeddings)
        assertTrue(cost > 0.0, "cost should be positive, was $cost")
        assertTrue(cost.isFinite(), "cost should be finite, was $cost")
    }

    @Test
    fun balanced_tree_costs_less_than_interleaved_caterpillar() {
        // Two orthogonal clusters of 4 points each: cluster 0 = (1,0), cluster 1 = (0,1).
        val c0 = List(4) { "c0_$it" }
        val c1 = List(4) { "c1_$it" }
        fun c0emb(t: String) = emb(t, 1.0, 0.0)
        fun c1emb(t: String) = emb(t, 0.0, 1.0)

        // Balanced tree: root → leafA holds all of cluster 0, leafB holds all of cluster 1.
        val balRoot = node("root", 0)
        val leafA = node("A", 1); val leafB = node("B", 1)
        link(balRoot, leafA); link(balRoot, leafB)
        c0.forEach { leafA.queries.add(c0emb(it)) }
        c1.forEach { leafB.queries.add(c1emb(it)) }
        val balEmb = c0.map { c0emb(it) } + c1.map { c1emb(it) }
        val balanced = computeTotalDasguptaCost(balRoot, balEmb)

        // Caterpillar: a single deepening spine, each leaf holding one point but
        // alternating between the two clusters so similar points sit far apart.
        val interleaved = c0.zip(c1).flatMap { listOf(it.first, it.second) }
        val catRoot = node("root", 0)
        var cur = catRoot
        val catEmb = mutableListOf<Embedding>()
        interleaved.forEachIndexed { i, t ->
            val leaf = node("leaf$i", i + 1)
            link(cur, leaf)
            val e = if (t.startsWith("c0")) c0emb(t) else c1emb(t)
            leaf.queries.add(e); catEmb.add(e)
            if (i < interleaved.size - 1) {
                val spine = node("n$i", i + 1)
                link(cur, spine); cur = spine
            }
        }
        val caterpillar = computeTotalDasguptaCost(catRoot, catEmb)

        assertTrue(
            caterpillar > balanced,
            "interleaved caterpillar ($caterpillar) should cost more than balanced ($balanced)",
        )
    }

    @Test
    fun sampled_estimate_is_close_to_exact_full_cost() {
        // 200 identical unit vectors (cos = 1 ⇒ w = 1) spread over 4 leaves of a balanced
        // tree. Every pair's contribution is its LCA subtree count ∈ {50, 100, 200}, so the
        // sampled mean is a low-variance estimator of the exact total.
        val root = node("root", 0)
        val a = node("a", 1); val b = node("b", 1)
        link(root, a); link(root, b)
        val leaves = listOf(a, a, b, b).mapIndexed { i, parent ->
            node("leaf$i", 2).also { link(parent, it) }
        }
        val embeddings = mutableListOf<Embedding>()
        leaves.forEachIndexed { li, leaf ->
            repeat(50) { k ->
                val e = emb("L${li}_q$k", 1.0, 0.0)
                leaf.queries.add(e); embeddings.add(e)
            }
        }
        val exact = computeTotalDasguptaCost(root, embeddings, maxPairs = Int.MAX_VALUE)
        val sampled = computeTotalDasguptaCost(root, embeddings, maxPairs = 5000, seed = 7)
        val relErr = Math.abs(sampled - exact) / exact
        assertTrue(relErr < 0.10, "sampled $sampled should be within 10% of exact $exact (relErr=$relErr)")
    }
}
