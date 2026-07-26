package taxonomy.service

import taxonomy.model.NodePairStats
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.sqrt

object BtMmFitter {

    private val log = org.slf4j.LoggerFactory.getLogger("taxonomy.BtMmFitter")

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
        var itersUsed = maxIter
        var finalDelta = Double.NaN

        for (iter in 0 until maxIter) {
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
            finalDelta = delta
            // Was `return@repeat`, which returns from the lambda for THIS iteration rather
            // than leaving the loop — so the fitter always ran the full 200 sweeps and the
            // convergence check did nothing. Numerically harmless once converged, but it hid
            // whether the fit converged at all, which is what the diagnostic below reports.
            if (delta < tol) { itersUsed = iter + 1; break }
        }

        val totalComparisons = pairStats.sumOf { it.totalComparisons }
        val converged = finalDelta.isFinite() && finalDelta < tol
        if (!converged) {
            log.warn(
                "[ARENA-BT] fit did NOT converge in $maxIter sweeps (final delta=" +
                    "${"%.3e".format(java.util.Locale.US, finalDelta)}, tol=${"%.1e".format(java.util.Locale.US, tol)})" +
                    " models=$K comparisons=$totalComparisons — scores are not a stable MLE"
            )
        } else {
            log.debug(
                "[ARENA-BT] fit converged in $itersUsed sweeps (delta=" +
                    "${"%.3e".format(java.util.Locale.US, finalDelta)}) models=$K comparisons=$totalComparisons"
            )
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
        var floored = 0
        if (inv != null) {
            for (i in 0 until K) {
                // Covariance under sum-to-zero constraint is diag(inv) - 1/K
                val v = inv[i][i] - 1.0 / K
                if (v < 1e-6) floored++
                variances[i] = v.coerceAtLeast(1e-6)
            }
        } else {
            for (i in 0 until K) {
                val diag = F[i][i].coerceAtLeast(1e-6)
                variances[i] = 1.0 / diag
            }
        }

        // ── [ARENA-BT] is this standard error meaningful? ───────────────────────
        // Fisher information per comparison is n*p*(1-p), which VANISHES as the
        // models separate. When one model wins nearly everything, p -> 1, every
        // entry of F -> 0, and Fc = F + 1.0 approaches the rank-one all-ones matrix;
        // whatever the inverse returns there is numerically meaningless, and the
        // 0.01 floor below hides it. That is precisely the regime a well-designed
        // arena drives itself into, so the SE has to be reported with its own
        // diagnostics or it will be quoted as if it were trustworthy.
        run {
            val totalComparisons = pairStats.sumOf { it.totalComparisons }
            val ps = pairStats.mapNotNull { p ->
                val si = scores[p.modelA] ?: return@mapNotNull null
                val sj = scores[p.modelB] ?: return@mapNotNull null
                val d = exp(si) + exp(sj)
                if (d == 0.0) 0.5 else exp(si) / d
            }
            val extreme = ps.count { it > 0.99 || it < 0.01 }
            val minInfo = pairStats.mapNotNull { p ->
                val si = scores[p.modelA] ?: return@mapNotNull null
                val sj = scores[p.modelB] ?: return@mapNotNull null
                val d = exp(si) + exp(sj)
                val pij = if (d == 0.0) 0.5 else exp(si) / d
                p.totalComparisons * pij * (1 - pij)
            }.minOrNull() ?: 0.0
            val msg = "[ARENA-BT] SE diagnostics: models=$K pairs=${pairStats.size}" +
                " comparisons=$totalComparisons inverted=${inv != null}" +
                " variancesFloored=$floored/$K" +
                " minPairInfo=${"%.3e".format(java.util.Locale.US, minInfo)}" +
                " nearSeparatedPairs=$extreme/${ps.size}"
            if (extreme > 0 || floored > 0 || inv == null) {
                log.warn("$msg — SE is unreliable in this regime; do not quote the CI")
            } else {
                log.info(msg)
            }
        }

        return models.mapIndexed { i, m ->
            m to sqrt(variances[i]).coerceAtLeast(0.01)
        }.toMap()
    }
}
