package taxonomy.utils

import org.slf4j.LoggerFactory
import taxonomy.model.GraphNode
import taxonomy.model.Embedding
import taxonomy.model.projectTo
import kotlin.math.*
import kotlinx.coroutines.*

/**
 * Upgraded Statistical engine for vMF and NiW operations.
 */
object StatisticsUtils {
    private val log = LoggerFactory.getLogger("taxonomy.Statistics")
    private val unreliableKappaCount = java.util.concurrent.atomic.AtomicInteger(0)

    /**
     * vMF kappa MLE: Banerjee closed-form estimate refined to the exact MLE via
     * Newton-Raphson on A_d(kappa) = rBar (Sra 2012), then Hornik-Grün small-sample
     * shrinkage correction. The closed-form estimate is only an approximation to the
     * true MLE; refining it makes kappaML consistent with what the Hornik-Grün
     * correction below is actually derived to correct.
     */
    fun correctedKappa(rBar: Double, d: Int, n: Int): Double {
        if (rBar >= 1.0) return 1e4   // Cap at kappa_max (degenerate spike)
        if (rBar <= 0.0) return 1e-3   // Floor at kappa_min (uniform)

        var kappa = rBar * (d - rBar * rBar) / (1.0 - rBar * rBar)

        // Newton-Raphson refinement: A_d'(kappa) = 1 - A_d(kappa)^2 - ((d-1)/kappa)*A_d(kappa).
        // The closed-form value above is already a good seed, so this converges in 1-2
        // iterations; capped at 5 as a safety bound against pathological inputs.
        for (i in 0 until 5) {
            val ad = besselRatioAd(d, kappa)
            val derivative = 1.0 - ad * ad - ((d - 1).toDouble() / kappa) * ad
            if (abs(derivative) < 1e-9) break
            val next = kappa - (ad - rBar) / derivative
            if (!next.isFinite() || next <= 0.0) break
            val converged = abs(next - kappa) < 1e-6 * kappa
            kappa = next.coerceIn(1e-3, 1e6)
            if (converged) break
        }

        val kappaML   = kappa.coerceIn(1e-3, 1e4)
        val shrinkage = (n - 1).toDouble() / (n + d - 2).toDouble().coerceAtLeast(1.0)
        if (n > 0 && d.toDouble() / n > 10.0) {
            val count = unreliableKappaCount.incrementAndGet()
            if (count == 1 || count % 100 == 0) {
                log.warn("[VMF] d/N=${"%.2f".format(d.toDouble() / n)} > 10 — κ estimate unreliable, NiW prior dominates (occurrence count: $count)")
            }
        }
        return (kappaML * shrinkage).coerceIn(1e-3, 1e4)
    }

    fun resetUnreliableKappaCount() {
        unreliableKappaCount.set(0)
    }

    fun dotProduct(a: DoubleArray, b: FloatArray): Double {
        var sum = 0.0
        val len = minOf(a.size, b.size)
        for (i in 0 until len) sum += a[i] * b[i]
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
        val safeNu = if (nu <= 0.0) 1e-5 else nu
        val z = kappa / safeNu
        val t = sqrt(1.0 + z * z)
        val eta = t + ln(z / (1.0 + t))
        return safeNu * eta - 0.5 * ln(2.0 * PI * safeNu) - 0.25 * ln(1.0 + z * z)
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
     * Sufficient statistics of one cluster for separation scoring: member count and
     * un-normalized vector sum. W(S) = n² − ‖sum‖² is recoverable from these alone.
     */
    data class ClusterStats(val n: Double, val sum: DoubleArray)

    /**
     * Chance-corrected separation score of a candidate partition of unit vectors.
     *
     * W(S) = |S|² − ‖Σx‖² = Σ_{i≠j∈S} (1 − xᵢ·xⱼ) is the total pairwise cosine
     * dissimilarity of S. For a partition {S_c}, the observed within-cluster scatter
     * is Σ_c W(S_c); under a uniformly random partition into the same sizes its
     * exact expectation is E = W(S) · Σ_c n_c(n_c−1) / (n(n−1)), because each
     * unordered pair lands inside cluster c with probability n_c(n_c−1)/(n(n−1)).
     *
     *   score = 1 − Σ_c W(S_c) / E
     *
     * = 1 for a perfect partition (each cluster internally identical), ≈ 0 for a
     * random partition, negative for an anti-clustered one, and exactly 0 for the
     * degenerate k=1 "partition" — so a non-separating (wrapper) candidate can never
     * clear a positive threshold. The chance correction removes the mechanical
     * dependence the raw within/total ratio has on k and on the cluster-size
     * profile, so one separationEpsilon means the same thing for split acceptance,
     * sibling merging, and sibling distinctness everywhere in the tree.
     *
     * Replaces two structurally broken gates: the former "Dasgupta delta"
     * 1 − Σ_c(n−n_c)W_c/(nW), which measured the *remaining*-cost fraction
     * (≈0.8 for every real split, leaving any epsilon below that inert), and the
     * κ-scaled vMF divergence, whose magnitude grew with κ and became
     * unsatisfiable exactly where merge/collapse decisions mattered most.
     */
    fun chanceCorrectedSeparation(clusters: List<List<DoubleArray>>): Double {
        val stats = clusters.filter { it.isNotEmpty() }.map { cluster ->
            val d = cluster[0].size
            val sum = DoubleArray(d)
            for (v in cluster) for (i in 0 until d) sum[i] += v[i]
            ClusterStats(cluster.size.toDouble(), sum)
        }
        return chanceCorrectedSeparation(stats)
    }

    /**
     * Same score computed from precomputed per-cluster sufficient statistics —
     * O(k·d), so pairwise sibling comparisons don't re-scan query vectors.
     */
    @JvmName("chanceCorrectedSeparationFromStats")
    fun chanceCorrectedSeparation(clusters: List<ClusterStats>): Double {
        val nonEmpty = clusters.filter { it.n > 0.0 }
        if (nonEmpty.isEmpty()) return 0.0
        val d = nonEmpty[0].sum.size
        val n = nonEmpty.sumOf { it.n }
        if (n < 2.0) return 0.0

        val sumTotal = DoubleArray(d)
        var wWithin = 0.0
        var pairFrac = 0.0
        for (c in nonEmpty) {
            var normC2 = 0.0
            for (i in 0 until d) {
                sumTotal[i] += c.sum[i]
                normC2 += c.sum[i] * c.sum[i]
            }
            wWithin += c.n * c.n - normC2
            pairFrac += c.n * (c.n - 1.0)
        }
        var normTotal2 = 0.0
        for (i in 0 until d) normTotal2 += sumTotal[i] * sumTotal[i]
        val wTotal = n * n - normTotal2

        val expectedWithin = wTotal * pairFrac / (n * (n - 1.0))
        if (expectedWithin <= 1e-10) return 0.0
        return 1.0 - wWithin / expectedWithin
    }

    fun computeDagSeparationJ(root: GraphNode, allEmbeddings: List<Embedding>): Double {
        val embMap = allEmbeddings.associateBy {
            if (it.queryId != -1) it.queryId.toString() else taxonomy.model.TextNormalizer.cleanText(it.rawText)
        }
        val rawEmbMap = allEmbeddings.associateBy { it.rawText }

        val leaves = mutableListOf<GraphNode>()
        val residualParents = mutableListOf<GraphNode>()
        
        fun walk(n: GraphNode) {
            if (n.isLeaf) {
                leaves.add(n)
            } else {
                if (n.residualQueries.isNotEmpty()) {
                    residualParents.add(n)
                }
                n.children.forEach { walk(it) }
            }
        }
        walk(root)

        val leafIds = leaves.map { it.id }.toSet()
        val resIds = residualParents.map { it.id }.toSet()
        
        val cellCount = leafIds.size + resIds.size
        if (cellCount < 2) return 0.0
        
        val d = 256
        
        val cellN = DoubleArray(cellCount)
        val cellSum = Array(cellCount) { DoubleArray(d) }
        
        val cells = mutableListOf<String>()
        leaves.forEach { cells.add(it.id) }
        residualParents.forEach { cells.add(it.id + "_residual") }
        val cellToIndex = cells.withIndex().associate { it.value to it.index }
        
        for (leaf in leaves) {
            val cellIdx = cellToIndex[leaf.id] ?: continue
            for ((text, weight) in leaf.queryWeights) {
                val emb = GraphNode.getEmbedding(text) ?: continue
                val proj = emb.projectTo(d)
                cellN[cellIdx] += weight
                for (j in 0 until d) {
                    cellSum[cellIdx][j] += weight * proj[j]
                }
            }
        }
        for (parent in residualParents) {
            val cellIdx = cellToIndex[parent.id + "_residual"] ?: continue
            for (qIdOrText in parent.residualQueries) {
                val emb = GraphNode.getEmbedding(qIdOrText) 
                    ?: embMap[qIdOrText]
                    ?: rawEmbMap[qIdOrText]
                    ?: continue
                val proj = emb.projectTo(d)
                cellN[cellIdx] += 1.0
                for (j in 0 until d) {
                    cellSum[cellIdx][j] += proj[j]
                }
            }
        }

        val nonEmptyIndices = cellToIndex.values.filter { cellN[it] > 0.0 }
        if (nonEmptyIndices.isEmpty()) return 0.0
        val n = cellN.sum()
        if (n < 2.0) return 0.0

        val sumTotal = DoubleArray(d)
        var wWithin = 0.0
        var pairFrac = 0.0
        for (c in nonEmptyIndices) {
            var normC2 = 0.0
            val cN = cellN[c]
            for (i in 0 until d) {
                sumTotal[i] += cellSum[c][i]
                normC2 += cellSum[c][i] * cellSum[c][i]
            }
            wWithin += cN * cN - normC2
            pairFrac += cN * (cN - 1.0)
        }
        var normTotal2 = 0.0
        for (i in 0 until d) normTotal2 += sumTotal[i] * sumTotal[i]
        val wTotal = n * n - normTotal2

        val expectedWithin = wTotal * pairFrac / (n * (n - 1.0))
        if (expectedWithin <= 1e-10) return 0.0
        return 1.0 - wWithin / expectedWithin
    }


    /**
     * EM implementation for Bisecting vMF-k-Means (k=2, kept for compatibility).
     */
    data class VmfParameters(val mu: FloatArray, val kappa: Double, val logNormalizer: Double)
    data class VmfMixture(val pi: DoubleArray, val components: List<VmfParameters>, val responsibilities: List<DoubleArray>, val converged: Boolean = true)

    fun performVmfBisection(
        embeddings: List<DoubleArray>,
        d: Int
    ): VmfMixture? = runVmfEm(embeddings, d, k = 2, minClusterFrac = 0.05)

    /**
     * k-ary vMF mixture selection.
     *
     * Tries k = 2, 3, ..., maxK using vMF-EM with k-means++ initialization.
     * Selects the highest k whose chance-corrected separation improves by at least
     * marginalEps over the previous k. All clusters must have >= minClusterFrac * n
     * members.
     *
     * Returns the winning VmfMixture (responsibilities has k columns).
     * Returns null if even k=2 collapses.
     *
     * @param embeddings     L2-normalized unit vectors in R^d (PCA-projected)
     * @param d              Dimension
     * @param maxK           Maximum number of clusters to try (default 4)
     * @param minClusterFrac Minimum fraction of n per cluster (default 0.05)
     * @param marginalEps    Min absolute separation improvement to accept k+1 (default 0.02)
     */
    suspend fun performVmfKMeans(
        embeddings: List<DoubleArray>,
        d: Int,
        maxK: Int = 4,
        minClusterFrac: Double = 0.05,
        marginalEps: Double = 0.02
    ): VmfMixture? = coroutineScope {
        val n = embeddings.size
        if (n < 2) return@coroutineScope null

        val minSize = (n * minClusterFrac).toInt().coerceAtLeast(1)
        val actualMaxK = minOf(maxK, n / minSize)
        if (actualMaxK < 2) return@coroutineScope null

        // Concurrent candidate EM runs
        val deferredMixtures = (2..actualMaxK).map { k ->
            async(Dispatchers.Default) {
                k to runVmfEm(embeddings, d, k, minClusterFrac)
            }
        }
        val mixtures = deferredMixtures.map { it.await() }.toMap()

        var bestMixture: VmfMixture? = null
        var bestDasgupta = -Double.MAX_VALUE

        for (k in 2..actualMaxK) {
            val mixture = mixtures[k] ?: break

            // Hard-assign for Dasgupta evaluation
            val clusters = Array(k) { mutableListOf<DoubleArray>() }
            for (i in 0 until n) {
                val resp = mixture.responsibilities[i]
                val best = resp.indices.maxByOrNull { resp[it] } ?: 0
                clusters[best].add(embeddings[i])
            }

            // Reject if any cluster is below minimum size
            if (clusters.any { it.size < minSize }) {
                log.debug("k-Means: k=$k rejected — cluster below minSize=$minSize")
                break
            }

            val delta = chanceCorrectedSeparation(clusters.map { it.toList() })
            val improvement = delta - bestDasgupta

            if (bestMixture == null) {
                // k=2: always accept (caller will apply its own separation epsilon check)
                bestMixture = mixture
                bestDasgupta = delta
                log.debug("k-Means: k=2 selected, separation=${"%.4f".format(delta)}")
            } else if (improvement >= marginalEps) {
                bestMixture = mixture
                bestDasgupta = delta
                log.debug("k-Means: k=$k selected (improvement=${"%.4f".format(improvement)}), separation=${"%.4f".format(delta)}")
            } else {
                log.debug("k-Means: k=$k rejected (improvement=${"%.4f".format(improvement)} < eps=${"%.4f".format(marginalEps)})")
                break
            }
        }

        bestMixture
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
        val mus = Array(k) { DoubleArray(d) }

        // mu_1 = normalized centroid
        val centroid = DoubleArray(d)
        for (v in embeddings) for (i in 0 until d) centroid[i] += v[i]
        var cNorm = 0.0
        for (i in 0 until d) cNorm += centroid[i] * centroid[i]
        cNorm = sqrt(cNorm)
        mus[0] = DoubleArray(d) { if (cNorm > 0.0) centroid[it] / cNorm else 0.0 }

        // mu_2..k = maximin cosine distance from all existing centers
        for (c in 1 until k) {
            var bestScore = -Double.MAX_VALUE
            var bestIdx = 0
            for (idx in embeddings.indices) {
                val x = embeddings[idx]
                // Minimum cosine distance to any existing center
                var minDist = Double.MAX_VALUE
                for (prev in 0 until c) {
                    val mu = mus[prev]
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
            mus[c] = embeddings[bestIdx].copyOf()
        }

        // ── EM ───────────────────────────────────────────────────────────────
        val kappas   = DoubleArray(k) { 10.0 }
        val logNorms = DoubleArray(k) { logVmfNormalizer(d, 10.0) }
        val pis      = DoubleArray(k) { 1.0 / k }

        // responsibilities[i][c]
        val R = Array(n) { DoubleArray(k) }
        var lastLikelihood = -Double.MAX_VALUE
        val minSoftCount = minClusterFrac * n

        val logPs = DoubleArray(k)
        val exps  = DoubleArray(k)
        var converged = false
        var finalIters = 0
        var bestLikelihood = -Double.MAX_VALUE
        var patienceCount = 0
        val maxPatience = 10
        val maxIters = 150

        for (iter in 0 until maxIters) {
            finalIters = iter + 1
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

            val delta = abs(totalLikelihood - lastLikelihood)
            if (delta / n < 1e-5) {
                converged = true
                break
            }

            // Plateau / oscillation guard
            if (totalLikelihood > bestLikelihood + 1e-6) {
                bestLikelihood = totalLikelihood
                patienceCount = 0
            } else {
                patienceCount++
                if (patienceCount >= maxPatience) {
                    log.debug("[VMF EM] Early exit due to plateau/oscillation at iteration $finalIters (no likelihood improvement for $maxPatience iterations)")
                    break
                }
            }

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
        if (converged) {
            log.debug("[VMF EM] K=$k, N=$n converged (tolerance met) in $finalIters iterations")
        } else if (patienceCount >= maxPatience) {
            converged = true
            log.debug("[VMF EM] K=$k, N=$n converged (plateau reached) in $finalIters iterations")
        } else {
            log.debug("[VMF EM] K=$k, N=$n hit iteration cap at $finalIters iterations")
        }

        val components = (0 until k).map { c ->
            VmfParameters(FloatArray(d) { mus[c][it].toFloat() }, kappas[c], logNorms[c])
        }
        val responsibilities = (0 until n).map { i -> R[i].copyOf() }

        return VmfMixture(pis, components, responsibilities, converged)
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