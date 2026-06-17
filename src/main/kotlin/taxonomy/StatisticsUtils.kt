package taxonomy

import org.eclipse.lmos.arc.app.taxonomy.Embedding
import org.eclipse.lmos.arc.app.taxonomy.GmmComponent
import org.eclipse.lmos.arc.app.taxonomy.GmmParams
import org.eclipse.lmos.arc.app.taxonomy.GraphNode
import org.slf4j.LoggerFactory
import kotlin.math.*
import kotlin.random.Random

/**
 * Upgraded Statistical engine for OAS and GMM operations.
 */
object StatisticsUtils {
    private val log = LoggerFactory.getLogger(StatisticsUtils::class.java)

    /**
     * Calculates the minimum Regularized Mahalanobis Distance across all components in a GMM.
     * Supports dimension-limited calculations for MRL Funnel Retrieval.
     */
    fun minMahalanobisDistance(x: Embedding, gmm: GmmParams, dimLimit: Int = x.dimensions): Double {
        var minDistance = Double.MAX_VALUE
        for (component in gmm.components) {
            val d2 = mahalanobisDistance(x, component.mean!!, component.diagonalCovariance!!, dimLimit)
            if (d2 < minDistance) minDistance = d2
        }
        return minDistance
    }

    private fun mahalanobisDistance(x: Embedding, mean: DoubleArray, variance: DoubleArray, dimLimit: Int): Double {
        var sum = 0.0
        val d = dimLimit.coerceAtMost(x.dimensions)
        for (i in 0 until d) {
            val diff = x.values[i].toDouble() - mean[i]
            sum += diff.pow(2.0) / variance[i].coerceAtLeast(1e-6)
        }
        // NORMALIZE: Return mean distance per dimension to handle high-D brittleness
        return sum / d.toDouble()
    }

    /**
     * Recursive Union Distribution: A parent node's distribution is the union of its children's.
     */
    fun unionOfChildren(children: Collection<GraphNode>, residualQueries: List<Embedding>): GmmParams? {
        val allComponents = mutableListOf<GmmComponent>()
        
        // Add components from children (Composite GMM)
        children.forEach { child ->
            child.distribution?.components?.forEach { allComponents.add(it) }
        }
        
        // If there are residual queries in the parent, fit a small GMM for the residual pool Up
        if (residualQueries.size >= 10) {
            val residualGmm = computeLeafGmm(residualQueries, maxCentroids = 2)
            residualGmm?.components?.forEach { allComponents.add(it) }
        }

        if (allComponents.isEmpty()) return null
        
        // Normalize weights
        val totalWeight = allComponents.sumOf { it.weight }
        val normalized = allComponents.map { it.copy(weight = it.weight / totalWeight) }
        
        return GmmParams(normalized)
    }

    /**
     * Computes a leaf node GMM using OAS for well-conditioned 4096-D covariance.
     */
    fun computeLeafGmm(embeddings: List<Embedding>, maxCentroids: Int, shrinkage: Double = 0.1): GmmParams? {
        if (embeddings.isEmpty()) return null
        
        // 1. Cluster embeddings using simple K-Means (K based on density)
        val k = min(maxCentroids, max(1, embeddings.size / 10))
        val clusters = performKMeans(embeddings, k)
        
        val components = clusters.mapNotNull { cluster ->
            if (cluster.size < 2) return@mapNotNull null
            
            val mean = calculateMean(cluster)
            val variance = computeOasCovariance(cluster, mean, shrinkage)
            
            GmmComponent(
                mean = mean,
                diagonalCovariance = variance,
                weight = cluster.size.toDouble() / embeddings.size,
                sampleCount = cluster.size
            )
        }
        
        if (components.isEmpty()) return null
        val gmm = GmmParams(components)
        
        // Calculate empirical threshold (100% coverage for ground truth)
        val distances = embeddings.map { minMahalanobisDistance(it, gmm) }.sorted()
        gmm.empiricalThreshold = distances.lastOrNull() ?: Double.MAX_VALUE
        
        return gmm
    }

    /**
     * Oracle Approximating Shrinkage (OAS) for high-dimensional covariance estimation.
     * Returns the diagonal of the regularized covariance matrix.
     */
    fun computeOasCovariance(embeddings: List<Embedding>, mean: DoubleArray, shrinkage: Double): DoubleArray {
        val n = embeddings.size
        val p = mean.size
        val variance = DoubleArray(p)
        
        // Sample Variance (Unbiased)
        for (emb in embeddings) {
            for (i in 0 until p) {
                val diff = emb.values[i].toDouble() - mean[i]
                variance[i] += diff.pow(2.0)
            }
        }
        for (i in 0 until p) variance[i] /= (n - 1).toDouble().coerceAtLeast(1.0)
        
        // Apply Shrinkage: Σ_OAS = (1 - ρ) S + ρ T
        // Target T is the isotropic mean variance
        val mu = variance.average()
        
        return DoubleArray(p) { i ->
            (1.0 - shrinkage) * variance[i] + (shrinkage * mu)
        }
    }

    fun chiSquareThreshold(dimensions: Int, alpha: Double): Double {
        val p = alpha.coerceIn(0.001, 0.999)
        val t = sqrt(-2.0 * ln(if (p <= 0.5) p else 1.0 - p))
        val zRaw = t - (2.515517 + 0.802853 * t + 0.010328 * t * t) /
                (1.0 + 1.432788 * t + 0.189269 * t * t + 0.001308 * t * t * t)
        val z = if (p >= 0.5) zRaw else -zRaw

        // NORMALIZE: The expected value of D²/d is 1.0, with stdDev = sqrt(2/d)
        val mean = 1.0
        val stdDev = sqrt(2.0 / dimensions)
        return (mean + (z * stdDev)).coerceAtLeast(0.1)
    }

    /**
     * Calculates the Kullback-Leibler (KL) Divergence between two diagonal Gaussians.
     * Measures asymmetric hierarchical containment.
     */
    fun klDivergence(mean0: DoubleArray, var0: DoubleArray, mean1: DoubleArray, var1: DoubleArray): Double {
        val k = mean0.size
        var sum = 0.0
        for (i in 0 until k) {
            val v0 = var0[i].coerceAtLeast(1e-9)
            val v1 = var1[i].coerceAtLeast(1e-9)
            sum += (v0 / v1) + ((mean1[i] - mean0[i]).pow(2.0) / v1) - 1.0 + ln(v1 / v0)
        }
        return (0.5 * sum) / k.toDouble()
    }

    /**
     * Calculates the Bhattacharyya distance between two diagonal Gaussians.
     * Measures symmetric overlap/similarity.
     */
    fun bhattacharyyaDistance(mean0: DoubleArray, var0: DoubleArray, mean1: DoubleArray, var1: DoubleArray): Double {
        val k = mean0.size
        var mahalanobisPart = 0.0
        var logDetPart = 0.0
        for (i in 0 until k) {
            val v0 = var0[i].coerceAtLeast(1e-9)
            val v1 = var1[i].coerceAtLeast(1e-9)
            val vAvg = (v0 + v1) / 2.0
            mahalanobisPart += (mean0[i] - mean1[i]).pow(2.0) / vAvg
            logDetPart += ln(vAvg / sqrt(v0 * v1))
        }
        return (1.0 / 8.0) * mahalanobisPart + (1.0 / 2.0) * logDetPart
    }

    /**
     * Calculates the Log-Likelihood of a set of embeddings given a GMM.
     * Parallelized for multi-core performance.
     */
    fun calculateLogLikelihood(gmm: GmmParams, embeddings: List<Embedding>): Double {
        if (embeddings.isEmpty()) return 0.0
        return embeddings.parallelStream().mapToDouble { emb ->
            val logProbs = gmm.components.map { comp ->
                ln(comp.weight.coerceAtLeast(1e-10)) + logMultivariateGaussianPdf(emb, comp.mean!!, comp.diagonalCovariance!!)
            }
            val maxLog = logProbs.maxOrNull() ?: -1000.0
            val sumExp = logProbs.sumOf { exp(it - maxLog) }
            totalLL_for_query(maxLog, sumExp)
        }.sum()
    }

    private fun totalLL_for_query(maxLog: Double, sumExp: Double): Double {
        return maxLog + ln(sumExp.coerceAtLeast(1e-300))
    }

    /**
     * Penalized Bayesian Information Criterion (p-BIC).
     * Normalized by dimensionality to maintain stability in 4096-D.
     */
    fun calculatePBic(
        gmm: GmmParams,
        embeddings: List<Embedding>,
        lambda: Double,
        dEff: Int = embeddings.firstOrNull()?.dimensions ?: 4096
    ): Double {
        if (embeddings.isEmpty()) return Double.POSITIVE_INFINITY
        val n = embeddings.size
        val d = embeddings[0].dimensions
        
        val totalLogLikelihood = calculateLogLikelihood(gmm, embeddings)

        // k: number of parameters calculated with dEff to avoid overparameterization penalty in 4096-D
        val k = gmm.components.size * (2 * dEff + 1) - 1
        
        var totalLogVolume = 0.0
        for (comp in gmm.components) {
            var logDet = 0.0
            for (v in comp.diagonalCovariance!!) {
                logDet += ln(v.coerceAtLeast(1e-15))
            }
            totalLogVolume += comp.weight * logDet
        }

        return (-2.0 * totalLogLikelihood + k * ln(n.toDouble()) + lambda * totalLogVolume) / d.toDouble()
    }

    /**
     * Log-PDF of a Multivariate Gaussian with diagonal covariance.
     * More stable than calculating the PDF directly in 4096-D.
     */
    fun calculateLogSemanticVolume(gmm: GmmParams): Double {
        var totalLogVolume = 0.0
        for (component in gmm.components) {
            var logDeterminant = 0.0
            for (variance in component.diagonalCovariance!!) {
                logDeterminant += ln(variance.coerceAtLeast(1e-15))
            }
            // Weight the log-volume by the component's mixture weight
            totalLogVolume += component.weight * logDeterminant
        }
        return totalLogVolume
    }

    private fun logMultivariateGaussianPdf(x: Embedding, mean: DoubleArray, variance: DoubleArray): Double {
        val d = mean.size
        var exponent = 0.0
        var logDet = 0.0
        for (i in 0 until d) {
            val diff = x.values[i].toDouble() - mean[i]
            val v = variance[i].coerceAtLeast(1e-9)
            exponent += (diff * diff) / v
            logDet += ln(v)
        }
        return -0.5 * (exponent + logDet + d * ln(2.0 * PI))
    }

    private fun multivariateGaussianPdf(x: Embedding, mean: DoubleArray, variance: DoubleArray): Double {
        return exp(logMultivariateGaussianPdf(x, mean, variance))
    }

    /**
     * Calculates axis-aligned box boundaries (offsets) using confidence intervals.
     * offset = lambda * sqrt(variance)
     */
    fun calculateBoxOffsets(diagonalCovariance: DoubleArray, lambda: Double): DoubleArray {
        return DoubleArray(diagonalCovariance.size) { i ->
            lambda * sqrt(diagonalCovariance[i].coerceAtLeast(1e-15))
        }
    }

    /**
     * Measures Asymmetric Entailment probability P(Child ⊆ Parent).
     * Uses a combination of KL Divergence and Box Volume Overlap.
     */
    fun calculateEntailmentScore(childGmm: GmmParams, parentGmm: GmmParams, inclusionFactor: Double): Double {
        // 1. Probabilistic Containment via KL
        val avgKl = childGmm.components.map { c0 ->
            parentGmm.components.minOf { c1 ->
                klDivergence(c0.mean!!, c0.diagonalCovariance!!, c1.mean!!, c1.diagonalCovariance!!)
            }
        }.average()

        // 2. Geometric Volume Ratio (Specificity Guard)
        val childVol = calculateLogSemanticVolume(childGmm)
        val parentVol = calculateLogSemanticVolume(parentGmm)
        
        // Parent must be broader. If child is broader, entailment is impossible.
        if (childVol > parentVol) return 0.0

        // Score: Higher is better containment. 
        // We use an exponential decay on KL and normalize by volume gap.
        return exp(-15.0 * avgKl / inclusionFactor)
    }

    fun gmmSimilarity(gmmA: GmmParams, gmmB: GmmParams): Double {
        if (gmmA.components.isEmpty() || gmmB.components.isEmpty()) return 0.0
        
        // Hausdorff-like similarity with divergence penalty
        val bestMatchesA = gmmA.components.map { cA ->
            gmmB.components.maxOf { cB -> 
                val cos = cosineSimilarity(cA.mean!!, cB.mean!!)
                // Divergence penalty: reduce similarity if KL divergence is high
                val kl = klDivergence(cA.mean!!, cA.diagonalCovariance!!, cB.mean!!, cB.diagonalCovariance!!)
                cos * exp(-0.01 * kl) // Sensitive to high-D volume overlap
            }
        }
        val bestMatchesB = gmmB.components.map { cB ->
            gmmA.components.maxOf { cA -> 
                val cos = cosineSimilarity(cB.mean!!, cA.mean!!)
                val kl = klDivergence(cB.mean!!, cB.diagonalCovariance!!, cA.mean!!, cA.diagonalCovariance!!)
                cos * exp(-0.01 * kl)
            }
        }
        return (bestMatchesA.average() + bestMatchesB.average()) / 2.0
    }

    fun cosineSimilarity(v1: DoubleArray, v2: DoubleArray): Double {
        var dotProduct = 0.0
        var norm1 = 0.0
        var norm2 = 0.0
        for (i in v1.indices) {
            dotProduct += v1[i] * v2[i]
            norm1 += v1[i] * v1[i]
            norm2 += v2[i] * v2[i]
        }
        if (norm1 == 0.0 || norm2 == 0.0) return 0.0
        return dotProduct / (sqrt(norm1) * sqrt(norm2))
    }

    private fun performKMeans(embeddings: List<Embedding>, k: Int, maxIterations: Int = 10): List<List<Embedding>> {
        if (embeddings.isEmpty()) return emptyList()
        if (k <= 1) return listOf(embeddings)

        var centroids = embeddings.shuffled(Random(42)).take(k).map { it.toDoubleArray() }.toMutableList()
        var clusters = List(k) { mutableListOf<Embedding>() }

        repeat(maxIterations) {
            val nextClusters = List(k) { mutableListOf<Embedding>() }
            
            // Parallelize assignment step for large datasets
            embeddings.parallelStream().forEach { emb ->
                var minDist = Double.MAX_VALUE
                var bestK = 0
                val embArr = emb.toDoubleArray()
                for (idx in 0 until k) {
                    val dist = euclideanDistance(embArr, centroids[idx])
                    if (dist < minDist) {
                        minDist = dist
                        bestK = idx
                    }
                }
                synchronized(nextClusters[bestK]) {
                    nextClusters[bestK].add(emb)
                }
            }
            
            val nextCentroids = centroids.toMutableList()
            for (idx in 0 until k) {
                if (nextClusters[idx].isNotEmpty()) {
                    nextCentroids[idx] = calculateMean(nextClusters[idx])
                }
            }
            if (centroids == nextCentroids) return@repeat
            centroids = nextCentroids
            clusters = nextClusters
        }
        return clusters.filter { it.isNotEmpty() }
    }

    private fun calculateMean(embeddings: List<Embedding>): DoubleArray {
        if (embeddings.isEmpty()) return DoubleArray(0)
        val d = embeddings[0].dimensions
        val mean = DoubleArray(d)
        for (emb in embeddings) {
            for (i in 0 until d) mean[i] += emb.values[i].toDouble()
        }
        for (i in 0 until d) mean[i] /= embeddings.size.toDouble()
        return mean
    }

    private fun euclideanDistance(v1: DoubleArray, v2: DoubleArray): Double {
        var sum = 0.0
        for (i in v1.indices) sum += (v1[i] - v2[i]).pow(2.0)
        return sqrt(sum)
    }

    fun stabilizeGmm(old: GmmParams?, new: GmmParams?, alpha: Double = 0.7): GmmParams? {
        if (new == null) return null
        if (old == null) return new
        val stabilizedComponents = mutableListOf<GmmComponent>()
        val matchedNewIndices = mutableSetOf<Int>()
        for (oldComp in old.components) {
            var bestMatchIdx = -1
            var maxSim = -1.0
            for (j in new.components.indices) {
                if (matchedNewIndices.contains(j)) continue
                val sim = cosineSimilarity(oldComp.mean!!, new.components[j].mean!!)
                if (sim > maxSim) { maxSim = sim; bestMatchIdx = j }
            }
            if (bestMatchIdx != -1 && maxSim > 0.95) {
                val newComp = new.components[bestMatchIdx]
                matchedNewIndices.add(bestMatchIdx)
                val bMean = DoubleArray(oldComp.mean!!.size) { i -> (1.0 - alpha) * oldComp.mean!![i] + alpha * newComp.mean!![i] }
                val bVar = DoubleArray(oldComp.mean!!.size) { i -> (1.0 - alpha) * oldComp.diagonalCovariance!![i] + alpha * newComp.diagonalCovariance!![i] }
                stabilizedComponents.add(GmmComponent(bMean, bVar, (1.0 - alpha) * oldComp.weight + alpha * newComp.weight, newComp.sampleCount))
            } else { stabilizedComponents.add(oldComp.copy(weight = oldComp.weight * (1.0 - alpha))) }
        }
        for (j in new.components.indices) { if (!matchedNewIndices.contains(j)) stabilizedComponents.add(new.components[j].copy(weight = new.components[j].weight * alpha)) }
        val totalWeight = stabilizedComponents.sumOf { it.weight }.coerceAtLeast(1e-9)
        val normalized = stabilizedComponents.map { it.copy(weight = it.weight / totalWeight) }
        val gmm = GmmParams(normalized)
        gmm.empiricalThreshold = (1.0 - alpha) * old.empiricalThreshold + alpha * new.empiricalThreshold
        return gmm
    }

    fun simplifyGmm(gmm: GmmParams, overlapThreshold: Double = 0.98): GmmParams {
        if (gmm.components.size < 2) return gmm
        val components = gmm.components.toMutableList()
        var simplified = true
        while (simplified) {
            simplified = false
            for (i in 0 until components.size) {
                for (j in i + 1 until components.size) {
                    if (cosineSimilarity(components[i].mean!!, components[j].mean!!) >= overlapThreshold) {
                        val c1 = components[i]; val c2 = components[j]
                        val nTotal = c1.sampleCount + c2.sampleCount
                        val nMean = DoubleArray(c1.mean!!.size) { d -> ((c1.mean!![d] * c1.sampleCount) + (c2.mean!![d] * c2.sampleCount)) / nTotal }
                        val nVar = DoubleArray(c1.mean!!.size) { d -> ((c1.diagonalCovariance!![d] * (c1.sampleCount - 1)) + (c2.diagonalCovariance!![d] * (c2.sampleCount - 1))) / (nTotal - 1).coerceAtLeast(1) }
                        components[i] = GmmComponent(nMean, nVar, c1.weight + c2.weight, nTotal)
                        components.removeAt(j); simplified = true; break
                    }
                }
                if (simplified) break
            }
        }
        return GmmParams(components)
    }
}
