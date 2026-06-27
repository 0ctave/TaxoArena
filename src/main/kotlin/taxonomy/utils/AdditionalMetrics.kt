package taxonomy.utils

import org.slf4j.LoggerFactory
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import kotlin.math.abs
import kotlin.math.sqrt
import kotlin.random.Random

/**
 * Publication-grade taxonomy metrics that complement the structural/clustering
 * suite in [TaxonomyMetrics] and [HierarchicalMetrics].
 *
 *  - Total Dasgupta cost — Dasgupta (2016), "A cost function for similarity-based
 *    hierarchical clustering", STOC 2016. https://doi.org/10.1145/2897518.2897527
 *  - Expected Calibration Error — Guo, Pleiss, Sun & Weinberger (2017),
 *    "On Calibration of Modern Neural Networks", ICML 2017. arXiv:1706.04599
 *  - Triplet accuracy — intrinsic, gold-free ranking consistency between
 *    embedding similarity and taxonomy LCA depth.
 *  - Normalised Sackin index — Sackin (1972); see the survey by Fischer, Herbst,
 *    Kersting, Kühn & Wicke (2021), "Tree balance indices: a comprehensive
 *    survey", arXiv:2109.12281.
 *
 * The DAG LCA convention matches PR #46's [shallowLCA]: the common ancestor with
 * the greatest depth (the smallest, most defensible subtree under polyhierarchy).
 */

private val additionalMetricsLog = LoggerFactory.getLogger("AdditionalMetrics")

// ─────────────────────────────────────────────────────────────────────────────
//  Shared helpers
// ─────────────────────────────────────────────────────────────────────────────

/** Cosine similarity of two embedding vectors; 0 when either is degenerate. */
private fun cosine(a: FloatArray, b: FloatArray): Double {
    val n = minOf(a.size, b.size)
    if (n == 0) return 0.0
    var dot = 0.0; var na = 0.0; var nb = 0.0
    for (i in 0 until n) {
        val x = a[i].toDouble(); val y = b[i].toDouble()
        dot += x * y; na += x * x; nb += y * y
    }
    val denom = sqrt(na) * sqrt(nb)
    return if (denom > 0.0) dot / denom else 0.0
}

/** Tree descendants (inclusive) of [node], following tree children only, deduped for DAGs. */
private fun treeDescendantsInclusive(node: GraphNode): Set<GraphNode> {
    val out = mutableSetOf<GraphNode>()
    fun walk(n: GraphNode) { if (out.add(n)) n.children.forEach { walk(it) } }
    walk(node)
    return out
}

/**
 * Map each query (by raw text) to the single taxonomy node it is assigned to.
 * A query present in several leaves (polyhierarchy / soft routing) is attributed
 * to its deepest containing node, mirroring the conservative shallowest-LCA rule.
 */
private fun assignedNodeByText(dag: GraphNode): Map<String, GraphNode> {
    val best = HashMap<String, GraphNode>()
    val visited = mutableSetOf<String>()
    fun walk(n: GraphNode) {
        if (!visited.add(n.id)) return
        for (q in n.queries) {
            val cur = best[q.rawText]
            if (cur == null || n.depth > cur.depth) best[q.rawText] = n
        }
        n.children.forEach { walk(it) }
    }
    walk(dag)
    return best
}

// ─────────────────────────────────────────────────────────────────────────────
//  1. Total Dasgupta cost
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Total Dasgupta cost of the final tree (Dasgupta 2016):
 *
 *   cost(T) = Σ_{i≠j} w_ij · |T_ij|
 *
 * with w_ij = cos(x_i, x_j) clipped to [0,1] and |T_ij| the number of data-point
 * queries contained in the subtree rooted at the (shallowest) LCA of the nodes
 * to which queries i and j are assigned. Lower is better.
 *
 * Complexity is O(M²) in the number of data points. To bound the blow-up on
 * large query sets, when the number of unordered pairs exceeds [maxPairs] this
 * samples [maxPairs] pairs uniformly at random (seeded by [seed]) and rescales
 * the mean contribution by the exact total pair count, yielding an unbiased
 * estimate of the full cost.
 *
 * @param dag             root of the taxonomy
 * @param queryEmbeddings the data-point queries (must carry vectors); only those
 *                        actually assigned to a node in [dag] participate
 * @param maxPairs        cap on the number of pairs evaluated (default 5000)
 * @param seed            RNG seed for the sampling path
 */
fun computeTotalDasguptaCost(
    dag: GraphNode,
    queryEmbeddings: List<Embedding>,
    maxPairs: Int = 5000,
    seed: Long = 0,
): Double {
    val nodeByText = assignedNodeByText(dag)
    // Deduplicate by raw text and keep only queries that landed somewhere in the tree.
    val points = queryEmbeddings
        .distinctBy { it.rawText }
        .mapNotNull { emb -> nodeByText[emb.rawText]?.let { emb to it } }
    val m = points.size
    if (m < 2) return 0.0

    // Subtree data-point counts, memoized per LCA node.
    val directCount = HashMap<GraphNode, Int>()
    for ((_, node) in points) directCount[node] = (directCount[node] ?: 0) + 1
    val subtreeCountCache = HashMap<GraphNode, Int>()
    fun subtreeCount(node: GraphNode): Int = subtreeCountCache.getOrPut(node) {
        treeDescendantsInclusive(node).sumOf { directCount[it] ?: 0 }
    }

    fun contribution(i: Int, j: Int): Double {
        val (embI, nodeI) = points[i]
        val (embJ, nodeJ) = points[j]
        val w = cosine(embI.values, embJ.values).coerceIn(0.0, 1.0)
        if (w == 0.0) return 0.0
        return w * subtreeCount(shallowLCA(nodeI, nodeJ)).toDouble()
    }

    val totalPairs = m.toLong() * (m - 1L) / 2L
    if (totalPairs <= maxPairs.toLong()) {
        var sum = 0.0
        for (i in 0 until m) for (j in i + 1 until m) sum += contribution(i, j)
        return sum
    }

    // Sampled estimate: mean contribution over sampled pairs × exact total pairs.
    val rng = Random(seed)
    var sum = 0.0
    var sampled = 0
    while (sampled < maxPairs) {
        val i = rng.nextInt(m)
        var j = rng.nextInt(m)
        if (i == j) { j = (j + 1) % m }
        sum += contribution(minOf(i, j), maxOf(i, j))
        sampled++
    }
    return (sum / sampled) * totalPairs.toDouble()
}

// ─────────────────────────────────────────────────────────────────────────────
//  2. Expected Calibration Error (ECE) for soft routing
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Expected Calibration Error of the soft routing distribution (Guo et al. 2017).
 *
 * Each query's confidence is the maximum membership in its predicted routing
 * distribution; its prediction is the argmax node. Confidences are binned into
 * [numBins] equal-width bins on [0,1] and
 *
 *   ECE = Σ_b (|B_b| / N) · |acc(B_b) − conf(B_b)|.
 *
 * Requires per-query ground-truth leaves (PR #48 plumbing). When [groundTruth]
 * is empty the metric is undefined, so this logs a WARN and returns 0.0 rather
 * than throwing.
 *
 * @param predicted   queryId → (nodeId → membership/probability)
 * @param groundTruth queryId → true leaf nodeId
 * @param numBins     number of equal-width confidence bins (default 10)
 */
fun computeRoutingECE(
    predicted: Map<String, Map<String, Double>>,
    groundTruth: Map<String, String>,
    numBins: Int = 10,
): Double {
    if (groundTruth.isEmpty()) {
        additionalMetricsLog.warn("computeRoutingECE: empty ground truth — returning 0.0 (GT plumbing absent)")
        return 0.0
    }
    val bins = numBins.coerceAtLeast(1)
    val binConfSum = DoubleArray(bins)
    val binAccSum = DoubleArray(bins)
    val binCount = IntArray(bins)
    var n = 0

    for ((queryId, dist) in predicted) {
        val trueLeaf = groundTruth[queryId] ?: continue
        val argmax = dist.maxByOrNull { it.value } ?: continue
        val conf = argmax.value.coerceIn(0.0, 1.0)
        val correct = if (argmax.key == trueLeaf) 1.0 else 0.0
        // Equal-width bins; conf == 1.0 lands in the final bin.
        val b = (conf * bins).toInt().coerceIn(0, bins - 1)
        binConfSum[b] += conf
        binAccSum[b] += correct
        binCount[b]++
        n++
    }
    if (n == 0) return 0.0

    var ece = 0.0
    for (b in 0 until bins) {
        val c = binCount[b]
        if (c == 0) continue
        val acc = binAccSum[b] / c
        val conf = binConfSum[b] / c
        ece += (c.toDouble() / n) * abs(acc - conf)
    }
    return ece
}

// ─────────────────────────────────────────────────────────────────────────────
//  3. Triplet accuracy (intrinsic, gold-free)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Triplet ranking accuracy: for random triplets (a, b, c) it checks that, when
 * the embeddings say a is closer to b than to c (cos(a,b) > cos(a,c)), the
 * taxonomy agrees by placing a & b in a deeper (smaller) LCA subtree than a & c
 * — i.e. depth(LCA(a,b)) > depth(LCA(a,c)). Returns the fraction of decisive
 * triplets that are consistent. Ties (equal cosine or equal LCA depth) are
 * skipped. A perfect taxonomy → 1.0; a random one → ≈ 0.5.
 *
 * @param dag             root of the taxonomy
 * @param queryEmbeddings data-point queries assigned within [dag]
 * @param numTriplets     number of random triplets to sample (default 1000)
 * @param seed            RNG seed for reproducibility (default 0)
 */
fun computeTripletAccuracy(
    dag: GraphNode,
    queryEmbeddings: List<Embedding>,
    numTriplets: Int = 1000,
    seed: Long = 0,
): Double {
    val nodeByText = assignedNodeByText(dag)
    val points = queryEmbeddings
        .distinctBy { it.rawText }
        .mapNotNull { emb -> nodeByText[emb.rawText]?.let { emb to it } }
    val m = points.size
    if (m < 3) return 0.0

    val rng = Random(seed)
    var consistent = 0
    var decisive = 0
    repeat(numTriplets) {
        val a = rng.nextInt(m)
        var b = rng.nextInt(m); if (b == a) b = (b + 1) % m
        var c = rng.nextInt(m)
        while (c == a || c == b) c = (c + 1) % m

        val (embA, nodeA) = points[a]
        val (embB, nodeB) = points[b]
        val (embC, nodeC) = points[c]

        val simAB = cosine(embA.values, embB.values)
        val simAC = cosine(embA.values, embC.values)
        if (simAB == simAC) return@repeat // similarity tie: not decisive

        val depthAB = shallowLCA(nodeA, nodeB).depth
        val depthAC = shallowLCA(nodeA, nodeC).depth
        if (depthAB == depthAC) return@repeat // taxonomy can't rank: not decisive

        decisive++
        val embeddingPrefersB = simAB > simAC
        val taxonomyPrefersB = depthAB > depthAC
        if (embeddingPrefersB == taxonomyPrefersB) consistent++
    }
    return if (decisive > 0) consistent.toDouble() / decisive else 0.0
}

// ─────────────────────────────────────────────────────────────────────────────
//  4. Normalised Sackin index
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Normalised Sackin index — the mean root-to-leaf depth (Sackin 1972; Fischer
 * et al. 2021):
 *
 *   S̄ = (1 / N_leaves) · Σ_{ℓ ∈ leaves} depth(ℓ).
 *
 * This is the formal definition behind the report's "Avg Leaf Depth" figure. A
 * single-leaf tree (root only) has depth 0 → S̄ = 0.
 */
fun computeNormalisedSackin(dag: GraphNode): Double {
    val leafDepths = mutableListOf<Int>()
    val visited = mutableSetOf<String>()
    fun walk(n: GraphNode) {
        if (!visited.add(n.id)) return
        if (n.isLeaf) leafDepths.add(n.depth) else n.children.forEach { walk(it) }
    }
    walk(dag)
    return if (leafDepths.isEmpty()) 0.0 else leafDepths.average()
}
