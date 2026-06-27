package taxonomy.utils

import kotlin.math.ln

/**
 * Overlapping Normalized Mutual Information.
 *
 * Lancichinetti, Fortunato & Kertész (2009), "Detecting the overlapping and
 * hierarchical community structure in complex networks", New Journal of Physics
 * 11:033015 — DOI: https://doi.org/10.1088/1367-2630/11/3/033015
 *
 * The standard Shannon NMI assumes disjoint hard partitions and inflates the
 * score when assignments overlap (polyhierarchy / soft routing). This computes
 * the covering-aware variant:
 *
 *   NMI_ovlp(X, Y) = 1 - (H(X|Y)_norm + H(Y|X)_norm) / 2
 *
 * Each query may belong to several clusters in either covering. A membership
 * value > 0 is treated as presence in that cluster's binary indicator; this
 * keeps the metric well-defined for both hard ground truth (1.0 / 0.0) and the
 * soft predicted routing produced by the engine.
 *
 * Inputs are keyed independently per covering — the cluster identifiers of the
 * predicted covering need not match those of the ground-truth covering.
 */
object OverlappingNmi {

    private const val LOG2 = 0.6931471805599453 // ln(2)

    private fun log2(x: Double): Double = ln(x) / LOG2

    /** Bernoulli entropy of a single indicator with P(1) = p, in bits. 0 at p∈{0,1}. */
    private fun hBernoulli(p: Double): Double {
        if (p <= 0.0 || p >= 1.0) return 0.0
        val q = 1.0 - p
        return -p * log2(p) - q * log2(q)
    }

    /**
     * @param predicted   queryId -> (clusterId -> membership in [0,1])
     * @param groundTruth queryId -> (clusterId -> membership in [0,1])
     * @return overlapping NMI in [0, 1]
     */
    fun compute(
        predicted: Map<String, Map<String, Double>>,
        groundTruth: Map<String, Map<String, Double>>,
    ): Double {
        // Universe of items = queries present in either covering.
        val items = (predicted.keys + groundTruth.keys).toList()
        val n = items.size
        if (n == 0) return 0.0

        val x = toClusterSets(predicted, items)  // predicted covering
        val y = toClusterSets(groundTruth, items) // ground-truth covering
        if (x.isEmpty() || y.isEmpty()) return 0.0

        val hxGivenY = normalizedConditionalEntropy(x, y, n)
        val hyGivenX = normalizedConditionalEntropy(y, x, n)
        return (1.0 - 0.5 * (hxGivenY + hyGivenX)).coerceIn(0.0, 1.0)
    }

    /** Convert a fuzzy membership map into binary indicator sets (item indices) per cluster. */
    private fun toClusterSets(
        cover: Map<String, Map<String, Double>>,
        items: List<String>,
    ): List<Set<Int>> {
        val index = items.withIndex().associate { (i, q) -> q to i }
        val clusters = LinkedHashMap<String, MutableSet<Int>>()
        for ((q, memberships) in cover) {
            val itemIdx = index[q] ?: continue
            for ((clusterId, m) in memberships) {
                if (m > 0.0) clusters.getOrPut(clusterId) { mutableSetOf() }.add(itemIdx)
            }
        }
        // Drop empty / universal clusters that carry no information (H = 0).
        return clusters.values.filter { it.isNotEmpty() && it.size < items.size }
    }

    /**
     * H(X|Y)_norm = mean over clusters Xk of  H(Xk|Y) / H(Xk),
     * where H(Xk|Y) = min over Yl of the constrained conditional entropy H(Xk|Yl).
     */
    private fun normalizedConditionalEntropy(
        x: List<Set<Int>>,
        y: List<Set<Int>>,
        n: Int,
    ): Double {
        var sum = 0.0
        var counted = 0
        for (xk in x) {
            val hXk = clusterEntropy(xk.size, n)
            if (hXk <= 0.0) continue
            var best = Double.MAX_VALUE
            for (yl in y) {
                val cond = conditionalEntropy(xk, yl, n, hXk)
                if (cond < best) best = cond
            }
            if (best == Double.MAX_VALUE) best = hXk
            sum += best / hXk
            counted++
        }
        return if (counted > 0) sum / counted else 0.0
    }

    private fun clusterEntropy(size: Int, n: Int): Double =
        hBernoulli(size.toDouble() / n)

    /**
     * Constrained conditional entropy H(Xk|Yl) (LFK 2009).
     * Uses the four-cell contingency of the two indicators; only valid when
     * h(P11)+h(P00) >= h(P10)+h(P01), otherwise Yl is uninformative about Xk
     * and the conditional entropy defaults to H(Xk).
     */
    private fun conditionalEntropy(
        xk: Set<Int>,
        yl: Set<Int>,
        n: Int,
        hXk: Double,
    ): Double {
        val inter = xk.count { it in yl }
        val nX = xk.size
        val nY = yl.size
        val c11 = inter
        val c10 = nX - inter
        val c01 = nY - inter
        val c00 = n - c11 - c10 - c01

        val nd = n.toDouble()
        val h11 = hCell(c11, nd)
        val h10 = hCell(c10, nd)
        val h01 = hCell(c01, nd)
        val h00 = hCell(c00, nd)

        // LFK constraint: the "aligned" cells must dominate the "crossed" cells.
        if (h11 + h00 < h10 + h01) return hXk

        // H(Xk|Yl) = H(Xk,Yl) - H(Yl)
        val hJoint = h11 + h10 + h01 + h00
        val hYl = hBernoulli(nY.toDouble() / n)
        return (hJoint - hYl).coerceAtLeast(0.0)
    }

    /** -count/n * log2(count/n), 0 when count == 0. */
    private fun hCell(count: Int, n: Double): Double {
        if (count <= 0) return 0.0
        val p = count / n
        return -p * log2(p)
    }
}
