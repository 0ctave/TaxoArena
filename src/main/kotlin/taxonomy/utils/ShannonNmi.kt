package taxonomy.utils

import kotlin.math.ln
import kotlin.math.sqrt

/**
 * Standard Shannon Normalised Mutual Information over two hard partitions of the
 * same item set (Strehl & Ghosh 2002 symmetric normalisation).
 *
 * Each map associates an item key with a single discrete label. Only items
 * present in both maps are scored; cluster labels of the two partitions are
 * independent, so the score is invariant to label renaming.
 */
object ShannonNmi {
    fun compute(x: Map<String, String>, y: Map<String, String>): Double {
        val keys = x.keys intersect y.keys
        val n = keys.size
        if (n < 2) return 0.0

        val joint = HashMap<Pair<String, String>, Int>()
        val marginalX = HashMap<String, Int>()
        val marginalY = HashMap<String, Int>()
        for (k in keys) {
            val xi = x.getValue(k)
            val yi = y.getValue(k)
            joint.merge(xi to yi, 1, Int::plus)
            marginalX.merge(xi, 1, Int::plus)
            marginalY.merge(yi, 1, Int::plus)
        }
        if (marginalX.size < 2 || marginalY.size < 2) return 0.0

        val nd = n.toDouble()
        val hx = entropy(marginalX.values, nd)
        val hy = entropy(marginalY.values, nd)

        var mi = 0.0
        for ((pair, c) in joint) {
            val pxy = c / nd
            val px = marginalX.getValue(pair.first) / nd
            val py = marginalY.getValue(pair.second) / nd
            mi += pxy * ln(pxy / (px * py))
        }

        val denom = sqrt(hx * hy)
        if (denom <= 0.0) return 0.0
        return (mi / denom).coerceIn(0.0, 1.0)
    }

    private fun entropy(counts: Collection<Int>, n: Double): Double {
        var h = 0.0
        for (c in counts) {
            val p = c / n
            if (p > 0.0) h -= p * ln(p)
        }
        return h
    }
}
