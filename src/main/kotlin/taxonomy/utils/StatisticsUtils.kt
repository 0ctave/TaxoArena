package taxonomy.utils

import org.slf4j.LoggerFactory
import taxonomy.model.GraphNode
import kotlin.math.*

/**
 * Upgraded Statistical engine for vMF and NiW operations.
 */
object StatisticsUtils {
    private val log = LoggerFactory.getLogger("taxonomy.Statistics")

    /**
     * Banerjee closed-form kappa estimation with small-sample shrinkage correction.
     */
    fun correctedKappa(rBar: Double, d: Int, n: Int): Double {
        if (rBar >= 1.0) return 1e4   // Cap at kappa_max (degenerate spike)
        if (rBar <= 0.0) return 1e-3   // Floor at kappa_min (uniform)
        val kappaML   = rBar * (d - rBar * rBar) / (1.0 - rBar * rBar)
        val shrinkage = (n - 1).toDouble() / (n + d - 2).toDouble().coerceAtLeast(1.0)
        return (kappaML * shrinkage).coerceIn(1e-3, 1e4)
    }

    /**
     * κ bias correction for high-dimensional vMF MLE.
     *
     * Hornik & Grün (2014), "movMF: An R Package for Fitting Mixtures of von
     * Mises-Fisher Distributions", Journal of Statistical Software 58(10),
     * Equation (9) — DOI: https://doi.org/10.18637/jss.v058.i10
     *
     * The MLE κ̂ carries an O(d/N) positive bias: at depth ≥ 3 (d=1024, N≈15–30)
     * it over-estimates concentration, making leaf nodes look more coherent than
     * they are and propagating into the NiW posterior and soft routing scores.
     * The correction is only meaningful when d/N is large, so it is applied only
     * for d/N > 5; below that the bias is negligible and the MLE is returned
     * unchanged. When d/N > 10 the estimate is unreliable (the NiW prior should
     * dominate) and a WARN is emitted.
     */
    fun biasCorrectKappa(kappaMle: Double, meanResultantLength: Double, dim: Int, n: Int): Double {
        if (n <= 0) return kappaMle
        val d = dim.toDouble()
        val ratio = d / n
        if (ratio > 10.0) {
            log.warn("[VMF] d/N=${"%.2f".format(ratio)} > 10 — κ estimate unreliable, NiW prior dominates")
        }
        return if (ratio > 5.0) {
            // Hornik & Grün (2014) Eq. (9): apply shrinkage factor ON TOP of the input kappaMle,
            // never recompute from rBar — correctedKappa already ran the Banerjee approximation.
            val shrinkage = (n - 1).toDouble() / (n + dim - 2).toDouble().coerceAtLeast(1.0)
            (kappaMle * shrinkage).coerceIn(1e-3, 1e4)
        } else {
            kappaMle
        }
    }

    fun dotProduct(a: DoubleArray, b: FloatArray): Double {
        var sum = 0.0
        for (i in a.indices) sum += a[i] * b[i]
        return sum
    }

    /**
     * Lanczos log-Gamma approximation for high-precision computation.
     */
    fun logGamma(x: Double): Double {
        if (x < 0.5) return ln(PI / sin(PI * x)) - logGamma(1.0 - x)
        val coeff = doubleArrayOf(
            76.18009172947146,
            -86.50532032941677,
            24.01409824083091,
            -1.231739572450155,
            0.1208650973866179e-2,
            -0.5395239384953e-5
        )
        var y = x
        var tmp = x + 5.5
        tmp -= (x + 0.5) * ln(tmp)
        var ser = 1.000000000190015
        for (j in coeff.indices) {
            y += 1.0
            ser += coeff[j] / y
        }
        return -tmp + ln(2.5066282746310005 * ser / x)
    }

    /**
     * Debye uniform asymptotic approximation of log I_nu(kappa) for high dimensions.
     */
    fun logBesselI(nu: Double, kappa: Double): Double {
        if (kappa <= 1e-4) {
            return nu * ln(kappa / 2.0) - logGamma(nu + 1.0)
        }
        val z = kappa / nu
        val t = sqrt(1.0 + z * z)
        val eta = t + ln(z / (1.0 + t))
        return nu * eta - 0.5 * ln(2.0 * PI * nu) - 0.25 * ln(1.0 + z * z)
    }

    /**
     * Precompute log C_d(kappa) normalizer to prevent underflow.
     */
    fun logVmfNormalizer(d: Int, kappa: Double): Double {
        val nu = d / 2.0 - 1.0
        if (kappa <= 1e-4) {
            return logGamma(d / 2.0) - (d / 2.0) * ln(PI) - ln(2.0)
        }
        return nu * ln(kappa) - (d / 2.0) * ln(2.0 * PI) - logBesselI(nu, kappa)
    }

    /**
     * Debye bessel ratio A_d(kappa) = I_{d/2}(kappa) / I_{d/2-1}(kappa)
     */
    fun besselRatioAd(d: Int, kappa: Double): Double {
        if (kappa <= 0.0) return 0.0
        val nu = d / 2.0
        val logRatio = logBesselI(nu, kappa) - logBesselI(nu - 1.0, kappa)
        return exp(logRatio).coerceIn(0.0, 1.0)
    }

    /**
     * vMF Jensen-Shannon Divergence merge criterion.
     */
    fun vmfJsDivergence(
        muA: FloatArray, kappaA: Double,
        muB: FloatArray, kappaB: Double,
        d: Int
    ): Double {
        val adA = besselRatioAd(d, kappaA)
        val adB = besselRatioAd(d, kappaB)

        var dot = 0.0
        for (i in 0 until d) {
            dot += muA[i].toDouble() * muB[i].toDouble()
        }
        dot = dot.coerceIn(-1.0, 1.0)

        val divA = kappaA * adA * (1.0 - dot)
        val divB = kappaB * adB * (1.0 - dot)
        return 0.5 * (divA + divB)
    }

    /**
     * Dasgupta Cost Delta for split validation in O(N) using vector-sum identities.
     *
     * W(S) proxy = N_S² − ‖sumS‖²
     *
     * For unit-norm vectors, this proxy is always ≥ 0 (since ‖sumS‖ ≤ N_S by
     * Cauchy-Schwarz), is 0 when all vectors are identical, and grows with
     * within-cluster dissimilarity — exactly the property needed to detect a
     * beneficial split. The formula is self-consistent (same expression used for
     * before and after), so the delta ratio is well-defined and monotone.
     *
     * Note: this is NOT the canonical Dasgupta off-diagonal sum Σ_{i≠j} xi·xj;
     * the canonical form equals ‖sumS‖²−N_S (opposite sign, positive for
     * coherent clusters). The proxy N_S²−‖sumS‖² behaves inversely — it is large
     * for *incoherent* clusters — which is what the split oracle wants: high
     * before-cost relative to after-cost. This was the working formula prior to
     * commit c4c0658 and is restored here.
     */
    fun calculateDasguptaDelta(
        left: List<DoubleArray>,
        right: List<DoubleArray>
    ): Double {
        val nL = left.size.toDouble()
        val nR = right.size.toDouble()
        if (nL == 0.0 || nR == 0.0) return 0.0

        val d = left[0].size
        val n = nL + nR

        val sumL = DoubleArray(d)
        for (v in left) for (i in 0 until d) sumL[i] += v[i]

        val sumR = DoubleArray(d)
        for (v in right) for (i in 0 until d) sumR[i] += v[i]

        var normL2 = 0.0
        var normR2 = 0.0
        var normTotal2 = 0.0
        for (i in 0 until d) {
            normL2 += sumL[i] * sumL[i]
            normR2 += sumR[i] * sumR[i]
            val t = sumL[i] + sumR[i]
            normTotal2 += t * t
        }

        // Proxy: N² − ‖sum‖²  (always ≥ 0 for unit-norm vectors; large = incoherent)
        val wL     = nL * nL - normL2
        val wR     = nR * nR - normR2
        val wTotal = n  * n  - normTotal2

        if (wTotal <= 1e-10) return 0.0

        val cAfter  = nR * wL + nL * wR
        val cBefore = n  * wTotal

        return 1.0 - cAfter / cBefore
    }

    /**
     * Dasgupta Cost Delta for k >= 2 clusters (general form).
     *
     * Uses the same W proxy as calculateDasguptaDelta: W(S) = N_S² − ‖sumS‖².
     * C_after  = Σ_c (n − n_c) · W(c)
     * C_before = n · W(all)
     * Delta    = 1 − C_after / C_before   (positive = split helps)
     *
     * Mathematically identical to calculateDasguptaDelta for k=2.
     */
    fun calculateDasguptaDeltaK(clusters: List<List<DoubleArray>>): Double {
        val allPts = clusters.flatten()
        val n = allPts.size.toDouble()
        if (n < 2.0 || clusters.isEmpty()) return 0.0
        val d = allPts[0].size

        val sumTotal = DoubleArray(d)
        for (v in allPts) for (i in 0 until d) sumTotal[i] += v[i]
        var normTotal2 = 0.0
        for (i in 0 until d) normTotal2 += sumTotal[i] * sumTotal[i]
        val wTotal = n * n - normTotal2
        if (wTotal <= 1e-10) return 0.0

        var cAfter = 0.0
        for (cluster in clusters) {
            val nc = cluster.size.toDouble()
            if (nc == 0.0) continue
            val sumC = DoubleArray(d)
            for (v in cluster) for (i in 0 until d) sumC[i] += v[i]
            var normC2 = 0.0
            for (i in 0 until d) normC2 += sumC[i] * sumC[i]
            val wC = nc * nc - normC2
            cAfter += (n - nc) * wC
        }
        return 1.0 - cAfter / (n * wTotal)
    }

    /**
     * EM implementation for Bisecting vMF-k-Means (k=2, kept for compatibility).
     */
    data class VmfParameters(val mu: FloatArray, val kappa: Double, val logNormalizer: Double)
    data class VmfMixture(val pi: DoubleArray, val components: List<VmfParameters>, val responsibilities: List<DoubleArray>)

    fun performVmfBisection(
        embeddings: List<DoubleArray>,
        d: Int
    ): VmfMixture? = runVmfEm(embeddings, d, k = 2, minClusterFrac = 0.05)

    /**
     * k-ary vMF mixture selection.
     *
     * Tries k = 2, 3, ..., maxK using vMF-EM with k-means++ initialization.
     * Selects the highest k whose Dasgupta delta improves by at least marginalEps
     * over the previous k. All clusters must have >= minClusterFrac * n members.
     *
     * Returns the winning VmfMixture (responsibilities has k columns).
     * Returns null if even k=2 collapses.
     *
     * @param embeddings     L2-normalized unit vectors in R^d (PCA-projected)
     * @param d              Dimension
     * @param maxK           Maximum number of clusters to try (default 4)
     * @param minClusterFrac Minimum fraction of n per cluster (default 0.05)
     * @param marginalEps    Min absolute Dasgupta improvement to accept k+1 (default 0.02)
     */
    fun performVmfKMeans(
        embeddings: List<DoubleArray>,
        d: Int,
        maxK: Int = 4,
        minClusterFrac: Double = 0.05,
        marginalEps: Double = 0.02
    ): VmfMixture? {
        val n = embeddings.size
        if (n < 2) return null

        var bestMixture: VmfMixture? = null
        var bestDasgupta = -Double.MAX_VALUE

        for (k in 2..maxK) {
            val mixture = runVmfEm(embeddings, d, k, minClusterFrac) ?: break

            // Hard-assign for Dasgupta evaluation
            val clusters = Array(k) { mutableListOf<DoubleArray>() }
            for (i in 0 until n) {
                val resp = mixture.responsibilities[i]
                val best = resp.indices.maxByOrNull { resp[it] } ?: 0
                clusters[best].add(embeddings[i])
            }

            // Reject if any cluster is below minimum size
            val minSize = (n * minClusterFrac).toInt().coerceAtLeast(1)
            if (clusters.any { it.size < minSize }) {
                log.debug("k-Means: k=$k rejected — cluster below minSize=$minSize")
                break
            }

            val delta = calculateDasguptaDeltaK(clusters.map { it.toList() })
            val improvement = delta - bestDasgupta

            if (bestMixture == null) {
                // k=2: always accept (caller will apply its own Dasgupta epsilon check)
                bestMixture = mixture
                bestDasgupta = delta
                log.debug("k-Means: k=2 selected, Dasgupta=${"%.4f".format(delta)}")
            } else if (improvement >= marginalEps) {
                bestMixture = mixture
                bestDasgupta = delta
                log.debug("k-Means: k=$k selected (improvement=${"%.4f".format(improvement)}), Dasgupta=${"%.4f".format(delta)}")
            } else {
                log.debug("k-Means: k=$k rejected (improvement=${"%.4f".format(improvement)} < eps=${"%.4f".format(marginalEps)})")
                break
            }
        }

        return bestMixture
    }

    /**
     * Internal: run vMF EM with exactly k components.
     * Initialization: k-means++ adapted to cosine distance on the sphere.
     *   mu_1 = normalized centroid of all points
     *   mu_j = point with maximum minimum cosine-distance to all existing centers (maximin)
     *
     * Returns null if any component collapses (soft count < minClusterFrac * n).
     */
    private fun runVmfEm(
        embeddings: List<DoubleArray>,
        d: Int,
        k: Int,
        minClusterFrac: Double
    ): VmfMixture? {
        val n = embeddings.size
        if (n < k) return null

        // ── k-means++ initialization ──────────────────────────────────────────
        val mus = mutableListOf<DoubleArray>()

        // mu_1 = normalized centroid
        val centroid = DoubleArray(d)
        for (v in embeddings) for (i in 0 until d) centroid[i] += v[i]
        var cNorm = 0.0
        for (i in 0 until d) cNorm += centroid[i] * centroid[i]
        cNorm = sqrt(cNorm)
        mus.add(DoubleArray(d) { if (cNorm > 0.0) centroid[it] / cNorm else 0.0 })

        // mu_2..k = maximin cosine distance from all existing centers
        repeat(k - 1) {
            var bestScore = -Double.MAX_VALUE
            var bestIdx = 0
            for (idx in embeddings.indices) {
                val x = embeddings[idx]
                // Minimum cosine distance to any existing center
                var minDist = Double.MAX_VALUE
                for (mu in mus) {
                    var dot = 0.0
                    for (i in 0 until d) dot += mu[i] * x[i]
                    val dist = 1.0 - dot.coerceIn(-1.0, 1.0)   // cosine distance ∈ [0, 2]
                    if (dist < minDist) minDist = dist
                }
                if (minDist > bestScore) {
                    bestScore = minDist
                    bestIdx = idx
                }
            }
            mus.add(embeddings[bestIdx].copyOf())
        }

        // ── EM ───────────────────────────────────────────────────────────────
        val kappas   = MutableList(k) { 10.0 }
        val logNorms = MutableList(k) { logVmfNormalizer(d, 10.0) }
        val pis      = MutableList(k) { 1.0 / k }

        // responsibilities[i][c]
        val R = Array(n) { DoubleArray(k) }
        var lastLikelihood = -Double.MAX_VALUE
        val minSoftCount = minClusterFrac * n

        val logPs = DoubleArray(k)
        val exps  = DoubleArray(k)
        for (iter in 0 until 200) {
            // ── E-step ───────────────────────────────────────────────────────
            var totalLikelihood = 0.0
            for (i in 0 until n) {
                val x = embeddings[i]
                for (c in 0 until k) {
                    var dot = 0.0
                    for (j in 0 until d) dot += mus[c][j] * x[j]
                    logPs[c] = ln(pis[c].coerceAtLeast(1e-10)) + logNorms[c] + kappas[c] * dot
                }
                var maxLP = logPs[0]
                for (c in 1 until k) {
                    if (logPs[c] > maxLP) maxLP = logPs[c]
                }
                var sumExp = 0.0
                for (c in 0 until k) {
                    exps[c] = exp(logPs[c] - maxLP)
                    sumExp += exps[c]
                }
                for (c in 0 until k) {
                    R[i][c] = exps[c] / sumExp
                }
                totalLikelihood += maxLP + ln(sumExp)
            }

            if (abs(totalLikelihood - lastLikelihood) < 1e-5) break
            lastLikelihood = totalLikelihood

            // ── M-step ───────────────────────────────────────────────────────
            val sumR    = DoubleArray(k)
            val nextMus = Array(k) { DoubleArray(d) }
            for (i in 0 until n) {
                val x = embeddings[i]
                for (c in 0 until k) {
                    sumR[c] += R[i][c]
                    for (j in 0 until d) nextMus[c][j] += R[i][c] * x[j]
                }
            }

            // Collapse check
            if (sumR.any { it < minSoftCount }) return null

            for (c in 0 until k) {
                pis[c] = sumR[c] / n
                var norm = 0.0
                for (j in 0 until d) norm += nextMus[c][j] * nextMus[c][j]
                norm = sqrt(norm)
                mus[c] = if (norm > 0.0) DoubleArray(d) { nextMus[c][it] / norm } else DoubleArray(d)
                val rBar = norm / sumR[c].coerceAtLeast(1e-9)
                kappas[c] = correctedKappa(rBar, d, sumR[c].roundToInt().coerceAtLeast(2))
                logNorms[c] = logVmfNormalizer(d, kappas[c])
            }
        }

        val components = (0 until k).map { c ->
            VmfParameters(FloatArray(d) { mus[c][it].toFloat() }, kappas[c], logNorms[c])
        }
        val responsibilities = (0 until n).map { i -> R[i].copyOf() }

        return VmfMixture(pis.toDoubleArray(), components, responsibilities)
    }

    /**
     * Centroid-approximated Spherical Silhouette score in O(NK).
     */
    fun calculateSphericalSilhouette(
        embeddings: List<DoubleArray>,
        clusterCentroids: List<FloatArray>
    ): Double {
        if (embeddings.isEmpty() || clusterCentroids.size < 2) return 0.0
        var silhouetteSum = 0.0
        for (x in embeddings) {
            var closestIdx = -1
            var maxSim = -Double.MAX_VALUE
            for (k in clusterCentroids.indices) {
                val mu = clusterCentroids[k]
                var dot = 0.0
                for (i in x.indices) {
                    dot += x[i] * mu[i].toDouble()
                }
                if (dot > maxSim) {
                    maxSim = dot
                    closestIdx = k
                }
            }

            val a = acos(maxSim.coerceIn(-1.0, 1.0))

            var minOtherDist = Double.MAX_VALUE
            for (k in clusterCentroids.indices) {
                if (k == closestIdx) continue
                val mu = clusterCentroids[k]
                var dot = 0.0
                for (i in x.indices) {
                    dot += x[i] * mu[i].toDouble()
                }
                val dist = acos(dot.coerceIn(-1.0, 1.0))
                if (dist < minOtherDist) {
                    minOtherDist = dist
                }
            }

            val s = if (max(a, minOtherDist) > 0.0) {
                (minOtherDist - a) / max(a, minOtherDist)
            } else {
                0.0
            }
            silhouetteSum += s
        }
        return silhouetteSum / embeddings.size
    }

    fun projectVector(vec: FloatArray, targetDim: Int): FloatArray {
        if (vec.size == targetDim) return vec.copyOf()
        val sliced = vec.copyOf(targetDim)
        var norm2 = 0.0f
        for (v in sliced) norm2 += v * v
        val norm = sqrt(norm2)
        return if (norm > 0f) FloatArray(targetDim) { sliced[it] / norm } else sliced
    }

    /**
     * Compute log-semantic volume from diagonal NiW scale matrix Lambda_N.
     */
    fun calculateLogSemanticVolume(node: GraphNode): Double {
        if (node.niwLambda.isEmpty()) return 0.0
        return node.niwLambda.sumOf { ln(it.toDouble().coerceAtLeast(1e-9)) }
    }

    fun pcaProject(vectors: List<DoubleArray>, k: Int): List<DoubleArray> {
        val n = vectors.size
        if (n == 0) return emptyList()
        val d = vectors[0].size
        if (d == 0) return vectors

        // 1. Center
        val mean = DoubleArray(d)
        for (v in vectors) {
            for (i in 0 until d) {
                mean[i] += v[i] / n
            }
        }
        val centered = vectors.map { v -> DoubleArray(d) { i -> v[i] - mean[i] } }

        // 2. Power iteration for top-k eigenvectors (cheap, no LAPACK needed)
        val components = mutableListOf<DoubleArray>()
        var residual = centered.map { it.copyOf() }

        repeat(k) {
            var vec = DoubleArray(d) { java.util.concurrent.ThreadLocalRandom.current().nextDouble() - 0.5 }
            repeat(30) {
                val proj = DoubleArray(d)
                for (row in residual) {
                    var dot = 0.0
                    for (i in 0 until d) {
                        dot += row[i] * vec[i]
                    }
                    for (i in 0 until d) {
                        proj[i] += dot * row[i]
                    }
                }
                for (comp in components) {
                    var dot = 0.0
                    for (i in 0 until d) {
                        dot += proj[i] * comp[i]
                    }
                    for (i in 0 until d) {
                        proj[i] -= dot * comp[i]
                    }
                }
                var normSq = 0.0
                for (i in 0 until d) {
                    normSq += proj[i] * proj[i]
                }
                val norm = sqrt(normSq)
                vec = if (norm > 1e-10) DoubleArray(d) { proj[it] / norm } else proj
            }
            components.add(vec)
            residual = residual.map { row ->
                var dot = 0.0
                for (i in 0 until d) {
                    dot += row[i] * vec[i]
                }
                DoubleArray(d) { i -> row[i] - dot * vec[i] }
            }
        }

        // 3. Project
        return centered.map { row ->
            val proj = DoubleArray(k) { j ->
                val comp = components[j]
                var dot = 0.0
                for (i in 0 until d) {
                    dot += row[i] * comp[i]
                }
                dot
            }
            var normSq = 0.0
            for (i in 0 until k) {
                normSq += proj[i] * proj[i]
            }
            val norm = sqrt(normSq)
            if (norm > 1e-10) DoubleArray(k) { proj[it] / norm } else proj
        }
    }
}