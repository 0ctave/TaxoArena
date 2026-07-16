package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Test
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.utils.OverlappingNmi
import taxonomy.utils.ShannonNmi
import taxonomy.utils.computeHierarchicalF1
import taxonomy.utils.computeNormalisedSackin
import taxonomy.utils.computeRoutingECE
import taxonomy.utils.computeTotalDasguptaCost
import taxonomy.utils.computeTripletAccuracy
import taxonomy.utils.dagDendrogramPurity
import taxonomy.utils.findAllLCAs
import taxonomy.utils.shallowLCA
import kotlin.random.Random

/**
 * Consolidated test suite for all Taxonomy mathematical, structural, and clustering metrics.
 */
class TaxonomyMetricsConsolidatedTest {

    private fun node(label: String, depth: Int) = GraphNode(label = label, depth = depth)
    
    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child)
        child.parents.add(parent)
    }

    private fun emb(text: String, vararg vals: Double) =
        Embedding(text, text, FloatArray(vals.size) { vals[it].toFloat() })

    // ─────────────────────────────────────────────────────────────────────────
    //  Dendrogram Purity Tests
    // ─────────────────────────────────────────────────────────────────────────
    @Test
    fun perfect_tree_is_fully_pure() {
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
        val root = node("root", 0)
        val a = node("A", 1); val b = node("B", 1)
        val a1 = node("a1", 2); val a2 = node("a2", 2); val b1 = node("b1", 2)
        link(root, a); link(root, b)
        link(a, a1); link(a, a2); link(b, b1)
        link(a, b1)

        val assignments = mapOf("q1" to a1, "q2" to a2, "q3" to b1)
        val gt = mapOf("q1" to "A", "q2" to "A", "q3" to "B")

        val purity = dagDendrogramPurity(assignments, gt)
        assertTrue(purity < 1.0, "Cross-link must lower purity below the tree value, was $purity")
        assertEquals(0.0, purity, 1e-9)
    }

    @Test
    fun shallowest_lca_is_selected() {
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

    // ─────────────────────────────────────────────────────────────────────────
    //  Hierarchical F1 Tests
    // ─────────────────────────────────────────────────────────────────────────
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
        val a = node("A", 1); val a1 = node("a1", 2)
        link(a, a1)

        val predicted = mapOf("q1" to a)
        val groundTruth = mapOf("q1" to a1)

        val (hP, hR, hF1) = computeHierarchicalF1(predicted, groundTruth)
        assertEquals(1.0, hP, 1e-9, "Predicted ancestors ⊆ true ancestors → precision 1")
        assertTrue(hR < 1.0, "Missing the leaf must drop recall below 1, was $hR")
        assertEquals(0.5, hR, 1e-9)
    }

    // ─────────────────────────────────────────────────────────────────────────
    //  Normalised Sackin Tests
    // ─────────────────────────────────────────────────────────────────────────
    @Test
    fun balanced_tree_returns_known_mean_depth() {
        val root = node("root", 0)
        val a = node("a", 1); val b = node("b", 1)
        link(root, a); link(root, b)
        listOf("a1", "a2").forEach { link(a, node(it, 2)) }
        listOf("b1", "b2").forEach { link(b, node(it, 2)) }

        assertEquals(2.0, computeNormalisedSackin(root), 1e-9)
    }

    @Test
    fun single_leaf_tree_returns_zero() {
        val root = node("root", 0)
        assertEquals(0.0, computeNormalisedSackin(root), 1e-9)
    }

    // ─────────────────────────────────────────────────────────────────────────
    //  Overlapping NMI Tests
    // ─────────────────────────────────────────────────────────────────────────
    @Test
    fun disjoint_perfect_assignment_scores_one() {
        val predicted = mapOf(
            "q1" to mapOf("c1" to 1.0),
            "q2" to mapOf("c1" to 1.0),
            "q3" to mapOf("c2" to 1.0),
            "q4" to mapOf("c2" to 1.0),
        )
        val groundTruth = mapOf(
            "q1" to mapOf("g1" to 1.0),
            "q2" to mapOf("g1" to 1.0),
            "q3" to mapOf("g2" to 1.0),
            "q4" to mapOf("g2" to 1.0),
        )
        val nmi = OverlappingNmi.compute(predicted, groundTruth)
        assertEquals(1.0, nmi, 1e-9, "Identical disjoint coverings must give NMI = 1")
    }

    @Test
    fun independent_random_assignment_scores_near_zero() {
        val n = 100
        val predicted = HashMap<String, Map<String, Double>>()
        val groundTruth = HashMap<String, Map<String, Double>>()
        for (i in 0 until n) {
            val q = "q$i"
            predicted[q] = mapOf((if (i % 2 == 0) "p0" else "p1") to 1.0)
            groundTruth[q] = mapOf((if (i < n / 2) "g0" else "g1") to 1.0)
        }
        val nmi = OverlappingNmi.compute(predicted, groundTruth)
        assertTrue(nmi < 0.25, "Independent partitions must give NMI near 0, was $nmi")
    }

    @Test
    fun overlapping_membership_differs_from_disjoint() {
        val groundTruth = mapOf(
            "q1" to mapOf("g1" to 1.0),
            "q2" to mapOf("g1" to 1.0),
            "q3" to mapOf("g2" to 1.0),
            "q4" to mapOf("g2" to 1.0),
        )
        val disjoint = mapOf(
            "q1" to mapOf("c1" to 1.0),
            "q2" to mapOf("c1" to 1.0),
            "q3" to mapOf("c2" to 1.0),
            "q4" to mapOf("c2" to 1.0),
        )
        val overlapping = mapOf(
            "q1" to mapOf("c1" to 1.0),
            "q2" to mapOf("c1" to 1.0, "c2" to 1.0),
            "q3" to mapOf("c2" to 1.0),
            "q4" to mapOf("c2" to 1.0),
        )
        val disjointNmi = OverlappingNmi.compute(disjoint, groundTruth)
        val overlappingNmi = OverlappingNmi.compute(overlapping, groundTruth)
        assertTrue(
            kotlin.math.abs(disjointNmi - overlappingNmi) > 1e-3,
            "Overlap must change the score measurably (disjoint=$disjointNmi overlap=$overlappingNmi)",
        )
    }

    // ─────────────────────────────────────────────────────────────────────────
    //  Routing ECE Tests
    // ─────────────────────────────────────────────────────────────────────────
    @Test
    fun perfectly_calibrated_router_has_near_zero_ece() {
        val predicted = (0 until 10).associate { i ->
            "q$i" to mapOf("a" to 0.6, "b" to 0.4)
        }
        val groundTruth = (0 until 10).associate { i ->
            "q$i" to if (i < 6) "a" else "b"
        }
        val ece = computeRoutingECE(predicted, groundTruth)
        assertEquals(0.0, ece, 1e-9)
    }

    @Test
    fun overconfident_router_has_high_ece() {
        val predicted = (0 until 10).associate { i ->
            "q$i" to mapOf("a" to 0.95, "b" to 0.05)
        }
        val groundTruth = (0 until 10).associate { i ->
            "q$i" to if (i < 2) "a" else "b"
        }
        val ece = computeRoutingECE(predicted, groundTruth)
        assertTrue(ece > 0.5, "overconfident router should have ECE > 0.5, was $ece")
    }

    @Test
    fun empty_ground_truth_returns_zero_without_throwing() {
        val predicted = mapOf("q0" to mapOf("a" to 0.9, "b" to 0.1))
        assertEquals(0.0, computeRoutingECE(predicted, emptyMap()), 1e-9)
    }

    // ─────────────────────────────────────────────────────────────────────────
    //  Total Dasgupta Cost Tests
    // ─────────────────────────────────────────────────────────────────────────
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
        val c0 = List(4) { "c0_$it" }
        val c1 = List(4) { "c1_$it" }
        fun c0emb(t: String) = emb(t, 1.0, 0.0)
        fun c1emb(t: String) = emb(t, 0.0, 1.0)

        val balRoot = node("root", 0)
        val leafA = node("A", 1); val leafB = node("B", 1)
        link(balRoot, leafA); link(balRoot, leafB)
        c0.forEach { leafA.queries.add(c0emb(it)) }
        c1.forEach { leafB.queries.add(c1emb(it)) }
        val balEmb = c0.map { c0emb(it) } + c1.map { c1emb(it) }
        val balanced = computeTotalDasguptaCost(balRoot, balEmb)

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

    // ─────────────────────────────────────────────────────────────────────────
    //  Triplet Accuracy Tests
    // ─────────────────────────────────────────────────────────────────────────
    @Test
    fun perfect_taxonomy_scores_one() {
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

    // ─────────────────────────────────────────────────────────────────────────
    //  Shannon NMI Tests
    // ─────────────────────────────────────────────────────────────────────────
    @Test
    fun shannon_identical_partition_scores_one() {
        val p = (0 until 20).associate { "q$it" to "c${it % 4}" }
        assertEquals(1.0, ShannonNmi.compute(p, p), 1e-9, "NMI(p, p) must be 1")
    }

    @Test
    fun shannon_shuffled_labels_score_near_zero() {
        val n = 200
        val rng = java.util.Random(42)
        val x = (0 until n).associate { "q$it" to "x${it % 5}" }
        val labels = (0 until n).map { "y${rng.nextInt(5)}" }
        val y = (0 until n).associate { "q$it" to labels[it] }
        val nmi = ShannonNmi.compute(x, y)
        assertTrue(nmi < 0.25, "Independent partitions must give NMI near 0, was $nmi")
    }

    @Test
    fun shannon_empty_maps_score_zero() {
        assertEquals(0.0, ShannonNmi.compute(emptyMap(), emptyMap()), 1e-12)
    }

    @Test
    fun shannon_single_label_on_either_side_scores_zero() {
        val varied = mapOf("q1" to "a", "q2" to "b", "q3" to "a", "q4" to "b")
        val constant = mapOf("q1" to "z", "q2" to "z", "q3" to "z", "q4" to "z")
        assertEquals(0.0, ShannonNmi.compute(varied, constant), 1e-12)
        assertEquals(0.0, ShannonNmi.compute(constant, varied), 1e-12)
    }

    @Test
    fun shannon_disjoint_keys_score_zero() {
        val x = mapOf("a1" to "p", "a2" to "q")
        val y = mapOf("b1" to "p", "b2" to "q")
        assertEquals(0.0, ShannonNmi.compute(x, y), 1e-12)
    }
}
