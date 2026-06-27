package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.utils.computeTripletAccuracy

/**
 * Triplet accuracy: fraction of decisive (a,b,c) triplets where embedding
 * similarity and taxonomy LCA depth agree. Perfect taxonomy → 1.0; random → ≈0.5.
 */
class TripletAccuracyTest {

    private fun node(label: String, depth: Int) = GraphNode(label = label, depth = depth)
    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child); child.parents.add(parent)
    }
    private fun emb(text: String, vararg vals: Double) =
        Embedding(text, text, FloatArray(vals.size) { vals[it].toFloat() })

    @Test
    fun perfect_taxonomy_scores_one() {
        // Two orthogonal clusters of 3, identical vectors within a cluster. Same-cluster
        // pairs have cos 1 and cross-cluster cos 0, so every decisive triplet has its
        // closer pair sharing the deeper leaf — fully consistent.
        val root = node("root", 0)
        val a = node("a", 1); val b = node("b", 1)
        link(root, a); link(root, b)
        val embeddings = mutableListOf<Embedding>()
        repeat(3) { i ->
            val e = emb("a$i", 1.0, 0.0); a.queries.add(e); embeddings.add(e)
        }
        repeat(3) { i ->
            val e = emb("b$i", 0.0, 1.0); b.queries.add(e); embeddings.add(e)
        }
        val acc = computeTripletAccuracy(root, embeddings, numTriplets = 2000, seed = 1)
        assertEquals(1.0, acc, 1e-9)
    }

    @Test
    fun random_embeddings_score_near_one_half() {
        // Random points scattered across a tree whose structure is unrelated to the
        // embedding geometry ⇒ taxonomy ranks no better than chance.
        val root = node("root", 0)
        val leaves = (0 until 8).map { node("leaf$it", 1 + it % 3).also { l -> link(root, l) } }
        val rng = java.util.Random(99)
        val embeddings = mutableListOf<Embedding>()
        repeat(80) { i ->
            val e = emb("q$i", rng.nextGaussian(), rng.nextGaussian(), rng.nextGaussian())
            val leaf = leaves[rng.nextInt(leaves.size)]
            leaf.queries.add(e); embeddings.add(e)
        }
        val acc = computeTripletAccuracy(root, embeddings, numTriplets = 3000, seed = 5)
        assertTrue(acc in 0.35..0.65, "random taxonomy should score ≈0.5, was $acc")
    }

    @Test
    fun seeded_runs_are_reproducible() {
        val root = node("root", 0)
        val leaves = (0 until 4).map { node("leaf$it", 1 + it % 2).also { l -> link(root, l) } }
        val rng = java.util.Random(7)
        val embeddings = mutableListOf<Embedding>()
        repeat(40) { i ->
            val e = emb("q$i", rng.nextGaussian(), rng.nextGaussian())
            leaves[rng.nextInt(leaves.size)].queries.add(e); embeddings.add(e)
        }
        val first = computeTripletAccuracy(root, embeddings, numTriplets = 1000, seed = 123)
        val second = computeTripletAccuracy(root, embeddings, numTriplets = 1000, seed = 123)
        assertEquals(first, second, 0.0)
    }
}
