package taxonomy.service

import taxonomy.model.NodePairStats
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.sqrt

object BtMmFitter {

    private val log = org.slf4j.LoggerFactory.getLogger("taxonomy.BtMmFitter")

    /**
     * Default phantom-tie strength: half a win in each direction, added to every pair that has
     * at least one REAL comparison.
     *
     * Without it the likelihood is unbounded whenever one model is undefeated in a pair. The MLE
     * then runs to infinity, the MM sweeps never converge, and Fisher information per comparison
     * — n*p*(1-p) — goes to zero exactly where the fit is least determined, so the reported SE
     * shrinks as the estimate gets *worse*. Complete separation is not an edge case here: it is
     * what a working arena produces on any leaf where a frontier model meets Llama-2.
     *
     * Half a win each way is the Beta(0.5, 0.5) / Jeffreys prior on each pairwise probability. It
     * keeps 0 < p < 1 strictly, so the penalised MLE is finite and the information is positive,
     * while contributing one phantom observation against a real budget of dozens — enough to
     * identify the fit, too little to move a determined one.
     */
    const val DEFAULT_PRIOR_STRENGTH = 0.5

    /**
     * Structural verdict on whether a set of comparisons can identify a BT scale at all.
     *
     * This is deliberately assessed on the OBSERVED comparisons only, never on the phantom ties
     * [DEFAULT_PRIOR_STRENGTH] adds. Phantom ties on every pair would make the comparison graph
     * complete and connectivity trivially true, which would hide precisely the defect this type
     * exists to surface — so the prior is applied only to pairs that already have real data.
     */
    data class Identifiability(
        /** Models that appear in at least one real comparison. */
        val participating: Set<String>,
        /** Models in the roster with no comparison at all; their theta is undefined. */
        val isolated: Set<String>,
        /** Connected components of the observed comparison graph, largest first. */
        val components: List<Set<String>>,
        /** Pairs where one side is undefeated, i.e. the separation the prior has to absorb. */
        val separatedPairs: List<Pair<String, String>>,
        val totalComparisons: Double
    ) {
        /**
         * True only when every model in the roster is reachable from every other through real
         * comparisons.
         *
         * Bradley-Terry identifies theta only up to an additive constant PER CONNECTED COMPONENT.
         * Two components therefore carry two independent, unrelated zero points, and their theta
         * values are not on a common scale — a difference between them is not a quantity. Pooling
         * such scores upward mixes incommensurable numbers and produces a leaderboard that looks
         * ordinary and means nothing, which is the failure mode worth refusing over: it exits
         * zero and reports plausible values.
         */
        val identified: Boolean get() = isolated.isEmpty() && components.size <= 1

        fun describe(): String = buildString {
            append("participating=${participating.size} isolated=${isolated.size}")
            append(" components=${components.size}")
            append(" comparisons=${"%.1f".format(java.util.Locale.US, totalComparisons)}")
            if (separatedPairs.isNotEmpty()) append(" separatedPairs=${separatedPairs.size}")
            if (isolated.isNotEmpty()) append(" | no data for: ${isolated.sorted().joinToString(", ")}")
            if (components.size > 1) {
                append(" | components: ")
                append(components.joinToString(" / ") { it.sorted().joinToString("+") })
            }
        }
    }

    /**
     * Assesses whether [pairStats] can identify a common scale over [models]. Pure; no logging.
     */
    fun assessIdentifiability(models: List<String>, pairStats: List<NodePairStats>): Identifiability {
        val roster = models.toSet()
        val adjacency = mutableMapOf<String, MutableSet<String>>()
        val participating = mutableSetOf<String>()
        val separated = mutableListOf<Pair<String, String>>()
        var total = 0.0

        for (ps in pairStats) {
            if (ps.modelA !in roster || ps.modelB !in roster) continue
            val n = ps.winsA + ps.winsB + ps.ties
            if (n <= 0.0 && ps.totalComparisons <= 0.0) continue
            total += ps.totalComparisons
            participating.add(ps.modelA)
            participating.add(ps.modelB)
            adjacency.getOrPut(ps.modelA) { mutableSetOf() }.add(ps.modelB)
            adjacency.getOrPut(ps.modelB) { mutableSetOf() }.add(ps.modelA)
            // Undefeated on one side, ignoring ties: the term the penalty has to hold down.
            if (ps.ties == 0.0 && (ps.winsA == 0.0 || ps.winsB == 0.0)) {
                separated.add(ps.modelA to ps.modelB)
            }
        }

        val seen = mutableSetOf<String>()
        val components = mutableListOf<Set<String>>()
        for (start in participating) {
            if (start in seen) continue
            val comp = mutableSetOf<String>()
            val stack = ArrayDeque(listOf(start))
            while (stack.isNotEmpty()) {
                val cur = stack.removeLast()
                if (!seen.add(cur)) continue
                comp.add(cur)
                adjacency[cur]?.forEach { if (it !in seen) stack.addLast(it) }
            }
            components.add(comp)
        }

        return Identifiability(
            participating = participating,
            isolated = roster - participating,
            components = components.sortedByDescending { it.size },
            separatedPairs = separated,
            totalComparisons = total
        )
    }

    /**
     * Penalised Bradley-Terry fit by MM updates.
     *
     * Returns scores for every model in [models], mean-centred. Note that centring is only
     * meaningful when the comparison graph is connected — call [assessIdentifiability] and refuse
     * to USE the result when it is not; this function will still return numbers, because several
     * callers legitimately fit pooled statistics where connectivity holds.
     */
    const val DEFAULT_MAX_ITER = 200

    /**
     * Convergence is declared when the MM step falls below this fraction of theta's own standard
     * error, rather than below a fixed absolute number.
     *
     * A fixed tolerance is the wrong shape for this. On the first multi-pair arena run 2264 fits
     * reported non-convergence at a 1e-6 tolerance, with deltas of median 9.0e-6 and max 6.9e-4 —
     * while the per-leaf SEs on the same parameter were 1.1 and, on an earlier run, 3.35 to 6.67.
     * The numerical residual was three to four orders of magnitude BELOW the statistical
     * uncertainty, so those warnings reported precision the data cannot express. (The construction
     * side had the identical defect: tau = 1e-6 against SE(dJ) = 5.85e-5.)
     *
     * Worse, an absolute threshold penalises the best-determined fits. The 15 largest residuals in
     * that run all sat on the RICHEST comparison graphs — 106 to 163 comparisons — because more
     * evidence means stronger separation, larger |theta|, and therefore larger absolute steps at
     * equal relative precision. Ranking by comparisons against delta gave Spearman -0.29 overall
     * but with the entire tail on the dense end.
     *
     * Scaling by SE/100 makes "converged" mean "resolved far beyond what the data can
     * distinguish", so a warning is again evidence of a real problem.
     */
    const val SE_FRACTION_FOR_CONVERGENCE = 0.01

    /**
     * Lower bound on min_i SE(theta_i) at the current estimate, from the Fisher diagonal alone.
     *
     * F_ii = sum_j n_ij p_ij (1 - p_ij), and the constrained covariance satisfies
     * diag(F^-1)_ii >= 1 / F_ii, so 1/sqrt(F_ii) under-estimates the true SE. Using a lower bound
     * makes the derived threshold conservative — stricter than the honest SE would require — and
     * costs one O(K^2) pass with no matrix inversion.
     */
    private fun minSeLowerBound(s: DoubleArray, w: Array<DoubleArray>): Double {
        val K = s.size
        var best = Double.MAX_VALUE
        for (i in 0 until K) {
            var fii = 0.0
            for (j in 0 until K) {
                if (j == i) continue
                val nij = w[i][j] + w[j][i]
                if (nij <= 0.0) continue
                val pij = 1.0 / (1.0 + exp(s[j] - s[i]))
                fii += nij * pij * (1.0 - pij)
            }
            if (fii > 0.0) {
                val se = 1.0 / sqrt(fii)
                if (se < best) best = se
            }
        }
        return if (best == Double.MAX_VALUE) 0.0 else best
    }

    fun fit(
        models: List<String>,
        pairStats: List<NodePairStats>,
        maxIter: Int = DEFAULT_MAX_ITER,
        tol: Double = 1e-6,
        priorStrength: Double = DEFAULT_PRIOR_STRENGTH
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

        // Phantom ties on pairs that carry real data. Applied AFTER the observed counts so the
        // pattern of which pairs exist is untouched — the prior regularises the scale, it must not
        // invent comparisons between models that never met.
        if (priorStrength > 0.0) {
            for (i in 0 until K) {
                for (j in i + 1 until K) {
                    if (w[i][j] + w[j][i] > 0.0) {
                        w[i][j] += priorStrength
                        w[j][i] += priorStrength
                    }
                }
            }
        }

        var s = DoubleArray(K) { 0.0 }
        var itersUsed = maxIter
        var finalDelta = Double.NaN
        var effectiveTol = tol

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
            // Stop against theta's own standard error, not a fixed number: `tol` is only an
            // absolute floor for the degenerate case where the information is ~0. See
            // SE_FRACTION_FOR_CONVERGENCE for why an absolute threshold is the wrong shape and
            // why it penalised the best-determined fits.
            //
            // Was `return@repeat`, which returned from the lambda for THIS iteration rather than
            // leaving the loop — so the fitter always ran every sweep and the convergence check
            // did nothing. Numerically harmless once converged, but it hid whether the fit
            // converged at all.
            val seScale = minSeLowerBound(s, w)
            effectiveTol = maxOf(tol, seScale * SE_FRACTION_FOR_CONVERGENCE)
            if (delta < effectiveTol) { itersUsed = iter + 1; break }
        }

        val ident = assessIdentifiability(models, pairStats)
        val converged = finalDelta.isFinite() && finalDelta < effectiveTol
        // Identification cost. The budget question for the fidelity-vs-granularity curve is
        // how many calls a cell needs to reach a CONNECTED comparison graph, and that has
        // never been measured: the Math run spent exactly 56 comparisons on every cell
        // regardless of size (33..111 queries), which is a scheduler allocation, not a cost.
        // The bracket for 87 cells is 1,200 (spanning tree, 7 pairs) to 9,744 (full 28-pair
        // floor at minMatches=2) — wide enough to decide whether leaf-level judging is
        // affordable at all. Emitted on every identified fit; take the MINIMUM per node
        // across rounds to get the cost, and pair it with the cell's query count to see
        // whether cost climbs as cells shrink.
        if (ident.identified) {
            val livePairs = pairStats.count { it.totalComparisons > 0 }
            val calls = pairStats.sumOf { it.totalComparisons }
            log.info(
                "[ARENA-IDENT] identified: models=${models.size} pairs_with_data=$livePairs" +
                    " of ${models.size * (models.size - 1) / 2} comparisons=$calls"
            )
        }
        if (!ident.identified) {
            // Structural, and not fixable by more sweeps: say so plainly rather than letting a
            // convergence warning imply the budget is the problem.
            log.warn(
                "[ARENA-BT] fit is NOT identified — ${ident.describe()}." +
                    " Bradley-Terry fixes theta only up to a constant per connected component," +
                    " so these scores are not on one scale and must not be pooled."
            )
        } else if (!converged) {
            // Distinguish "needs more sweeps" from "not converging". MM descends monotonically,
            // so a delta within a couple of orders of the tolerance is a stopped-early fit whose
            // scores are fine to two more decimal places than anything downstream uses; treating
            // that as a failure buried the cases that matter under thousands of benign warnings.
            log.warn(
                "[ARENA-BT] fit stopped at $maxIter sweeps still short of SE/100 (final delta=" +
                    "${"%.3e".format(java.util.Locale.US, finalDelta)}, threshold=" +
                    "${"%.3e".format(java.util.Locale.US, effectiveTol)})" +
                    " models=$K comparisons=${"%.1f".format(java.util.Locale.US, ident.totalComparisons)}" +
                    " — the residual is now large relative to theta's own uncertainty, so this is a" +
                    " real failure rather than a tolerance artifact"
            )
        } else {
            log.debug(
                "[ARENA-BT] fit converged in $itersUsed sweeps (delta=" +
                    "${"%.3e".format(java.util.Locale.US, finalDelta)}) models=$K" +
                    " comparisons=${"%.1f".format(java.util.Locale.US, ident.totalComparisons)}" +
                    (if (ident.separatedPairs.isNotEmpty())
                        " separatedPairs=${ident.separatedPairs.size} (absorbed by the Jeffreys prior)" else "")
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
        pairStats: List<NodePairStats>,
        priorStrength: Double = DEFAULT_PRIOR_STRENGTH
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
            // Count the phantom observations too: they are part of the penalised likelihood the
            // scores were fitted under, so excluding them here would report the information of a
            // model that was not the one estimated.
            val nij = ps.totalComparisons.toDouble() + (if (ps.totalComparisons > 0.0) 2.0 * priorStrength else 0.0)
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
                // Constrained covariance is diag(Fc^-1) - 1/K^2, NOT - 1/K.
                //
                // F is singular with 1 in its null space (F*1 = 0), so it is regularised here as
                // Fc = F + J, J the all-ones matrix. Since J = K*P with P = 1*1^T/K, we get
                // Fc*1 = K*1: the 1-direction is an eigenvector of Fc with eigenvalue K, and on
                // its orthogonal complement Fc acts as F. Hence
                //
                //     Fc^-1 = F^+ + (1/K)*(1*1^T/K) = F^+ + J/K^2
                //     =>  F^+ = Fc^-1 - J/K^2,  so the diagonal correction is 1/K^2.
                //
                // The previous 1/K over-subtracted by (1/K - 1/K^2) = (K-1)/K^2 from EVERY
                // variance — 0.109 at K=8, 0.083 at K=12 — which drove most values straight into
                // the 1e-6 floor and made every reported standard error the floor rather than a
                // measurement. 12_Appendix_Numerics.tex:137-139 documents the same wrong constant.
                val v = inv[i][i] - 1.0 / (K.toDouble() * K.toDouble())
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
        // The Jeffreys prior in fit() keeps p away from 0 and 1, so information no longer
        // collapses to zero outright, but it can still be small on a near-separated pair with a
        // thin budget. These diagnostics stay because the floor is a bound, not a guarantee: the
        // 0.01 floor at the bottom of this function would otherwise present a number with no
        // information behind it as if it were precise.
        run {
            val ident = assessIdentifiability(models, pairStats)
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
                val nij = p.totalComparisons + (if (p.totalComparisons > 0.0) 2.0 * priorStrength else 0.0)
                nij * pij * (1 - pij)
            }.minOrNull() ?: 0.0
            val msg = "[ARENA-BT] SE diagnostics: models=$K pairs=${pairStats.size}" +
                " comparisons=${"%.1f".format(java.util.Locale.US, ident.totalComparisons)}" +
                " inverted=${inv != null} identified=${ident.identified}" +
                " variancesFloored=$floored/$K" +
                " minPairInfo=${"%.3e".format(java.util.Locale.US, minInfo)}" +
                " nearSeparatedPairs=$extreme/${ps.size}"
            if (!ident.identified || extreme > 0 || floored > 0 || inv == null) {
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
