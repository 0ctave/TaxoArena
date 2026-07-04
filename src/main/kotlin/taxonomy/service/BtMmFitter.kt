package taxonomy.service

import taxonomy.model.NodePairStats
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.sqrt

object BtMmFitter {

    fun fit(
        models: List<String>,
        pairStats: List<NodePairStats>,
        maxIter: Int = 200,
        tol: Double = 1e-6
    ): Map<String, Double> {
        if (models.size < 2) return models.associateWith { 0.0 }

        val idx = models.withIndex().associate { (i, m) -> m to i }
        val K = models.size
        val w = Array(K) { DoubleArray(K) }   // w[i][j] = wins of i when playing j

        for (ps in pairStats) {
            val i = idx[ps.modelA] ?: continue
            val j = idx[ps.modelB] ?: continue
            w[i][j] += ps.winsA + 0.5 * ps.ties
            w[j][i] += ps.winsB + 0.5 * ps.ties
        }

        var s = DoubleArray(K) { 0.0 }

        repeat(maxIter) {
            val sNew = DoubleArray(K)
            for (i in 0 until K) {
                val Wi = (0 until K).sumOf { j -> w[i][j] }
                if (Wi == 0.0) { 
                    sNew[i] = s[i]
                    continue
                }
                val denom = (0 until K).filter { j -> j != i }
                    .sumOf { j ->
                        val nij = w[i][j] + w[j][i]
                        if (nij == 0.0) 0.0
                        else nij / (exp(s[i]) + exp(s[j]))
                    }
                sNew[i] = if (denom == 0.0) s[i] else ln(Wi / denom)
            }
            // normalize
            val mean = sNew.average()
            for (i in 0 until K) sNew[i] -= mean

            val delta = sNew.zip(s.toList()).maxOf { (a, b) -> abs(a - b) }
            s = sNew
            if (delta < tol) return@repeat
        }

        return models.zip(s.toList()).toMap()
    }

    private fun invertMatrix(A: Array<DoubleArray>): Array<DoubleArray>? {
        val n = A.size
        val I = Array(n) { DoubleArray(n) { i -> if (i == it) 1.0 else 0.0 } }
        val temp = Array(n) { i -> A[i].clone() }
        for (i in 0 until n) {
            var maxRow = i
            for (j in i + 1 until n) {
                if (abs(temp[j][i]) > abs(temp[maxRow][i])) {
                    maxRow = j
                }
            }
            if (abs(temp[maxRow][i]) < 1e-12) return null
            val tRow = temp[i]; temp[i] = temp[maxRow]; temp[maxRow] = tRow
            val iRow = I[i]; I[i] = I[maxRow]; I[maxRow] = iRow
            val pivot = temp[i][i]
            for (j in 0 until n) {
                temp[i][j] /= pivot
                I[i][j] /= pivot
            }
            for (j in 0 until n) {
                if (j != i) {
                    val factor = temp[j][i]
                    for (k in 0 until n) {
                        temp[j][k] -= factor * temp[i][k]
                        I[j][k] -= factor * I[i][k]
                    }
                }
            }
        }
        return I
    }

    fun estimateStdErrors(
        models: List<String>,
        scores: Map<String, Double>,
        pairStats: List<NodePairStats>
    ): Map<String, Double> {
        val idx = models.withIndex().associate { (i, m) -> m to i }
        val K = models.size
        if (K == 0) return emptyMap()

        val F = Array(K) { DoubleArray(K) }
        for (ps in pairStats) {
            val i = idx[ps.modelA] ?: continue
            val j = idx[ps.modelB] ?: continue
            val si = scores[ps.modelA] ?: 0.0
            val sj = scores[ps.modelB] ?: 0.0
            val denom = exp(si) + exp(sj)
            val pij = if (denom == 0.0) 0.5 else exp(si) / denom
            val nij = ps.totalComparisons.toDouble()
            val info = nij * pij * (1.0 - pij)
            F[i][i] += info
            F[j][j] += info
            F[i][j] -= info
            F[j][i] -= info
        }

        // Add 1.0 to all elements to enforce mean-zero constraint ranking projection
        val Fc = Array(K) { i -> DoubleArray(K) { j -> F[i][j] + 1.0 } }
        val inv = invertMatrix(Fc)

        val variances = DoubleArray(K)
        if (inv != null) {
            for (i in 0 until K) {
                // Covariance under sum-to-zero constraint is diag(inv) - 1/K
                val v = inv[i][i] - 1.0 / K
                variances[i] = v.coerceAtLeast(1e-6)
            }
        } else {
            for (i in 0 until K) {
                val diag = F[i][i].coerceAtLeast(1e-6)
                variances[i] = 1.0 / diag
            }
        }

        return models.mapIndexed { i, m ->
            m to sqrt(variances[i]).coerceAtLeast(0.01)
        }.toMap()
    }
}
