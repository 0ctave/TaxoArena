package org.eclipse.lmos.arc.app.taxonomy

import java.lang.Math.pow
import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.max
import kotlin.math.sqrt
import kotlin.math.pow
import kotlin.math.abs
import kotlin.math.pow

/**
 * Pure mathematical functions implementing the Formalization Document.
 * Operates on highly optimized primitive FloatArrays to prevent GC overhead.
 */
object GeometryMath {

    /**
     * Computes Centroid μ_D: The mean vector of all queries in the domain.
     */
    fun calculateCentroid(vectors: List<FloatArray>, dimensions: Int): FloatArray {
        val mu = FloatArray(dimensions)
        if (vectors.isEmpty()) return mu
        val n = vectors.size.toFloat()
        for (v in vectors) {
            for (j in 0 until dimensions) {
                mu[j] += v[j] / n
            }
        }
        return mu
    }

    /**
     * Computes Radii Vector σ²_D: The variance vector representing spatial spread.
     */
    fun calculateVariance(vectors: List<FloatArray>, mu: FloatArray, minFloor: Float): FloatArray {
        val dimensions = mu.size
        val variance = FloatArray(dimensions)
        if (vectors.isEmpty()) {
            for (j in 0 until dimensions) variance[j] = minFloor
            return variance
        }
        val n = vectors.size.toFloat()
        for (v in vectors) {
            for (j in 0 until dimensions) {
                val diff = v[j] - mu[j]
                variance[j] += (diff * diff) / n
            }
        }
        // Apply singularity floor
        for (j in 0 until dimensions) {
            variance[j] = max(minFloor, variance[j])
        }
        return variance
    }

    /**
     * Calculates the Likeness Factor P(q ∈ D) using the CDF of the Chi-Squared distribution
     * evaluating the squared Mahalanobis distance.
     */
    fun inclusionProbability(q: FloatArray, mu: FloatArray, variance: FloatArray, scalingFactor: Float = 1.0f): Float {
        val d = q.size
        var d2 = 0f
        for (j in 0 until d) {
            val diff = q[j] - mu[j]
            d2 += (diff * diff) / variance[j]
        }

        // P(x ∈ N_k) = 1 - CDF_{χ²_d}(D²_M(x, μ_k))
        // Apply scaling factor to distance to maintain dynamic strictness control
        val adjustedD2 = d2 / scalingFactor
        return chiSquaredSurvival(adjustedD2, d)
    }

    /**
     * Calculates the probability of inclusion evaluating against a Gaussian Mixture Model (GMM).
     * Returns the sum of weighted probabilities across all sub-components.
     */
    fun gmmInclusionProbability(q: FloatArray, components: List<GaussianComponent>, scalingFactor: Float = 1.0f): Float {
        if (components.isEmpty()) return 0f
        var totalProb = 0f
        for (comp in components) {
            val prob = inclusionProbability(q, comp.centroid, comp.variance, scalingFactor)
            totalProb += comp.weight * prob
        }
        return totalProb
    }

    /**
     * Approximates the Survival Function (1 - CDF) of the Chi-Squared distribution
     * using the Wilson-Hilferty transformation (highly accurate for d >= 3).
     */
    private fun chiSquaredSurvival(x: Float, k: Int): Float {
        if (x <= 0f) return 1f
        val kFloat = k.toFloat()
        val ratio = x / kFloat
        val p1 = ratio.toDouble().pow(1.0 / 3.0).toFloat()
        val p2 = 1f - 2f / (9f * kFloat)
        val p3 = sqrt(2.0 / (9.0 * kFloat)).toFloat()

        // Transform to Z-score
        val z = (p1 - p2) / p3

        // Return 1 - Normal CDF
        return 1f - normalCdf(z)
    }

    /**
     * High-precision approximation of the Standard Normal CDF.
     */
    private fun normalCdf(z: Float): Float {
        val b1 =  0.319381530f
        val b2 = -0.356563782f
        val b3 =  1.781477937f
        val b4 = -1.821255978f
        val b5 =  1.330274429f
        val p  =  0.2316419f
        val c  =  0.39894228f

        val absZ = abs(z)
        val t = 1f / (1f + p * absZ)
        val expPart = c * exp(-z * z / 2f)
        val poly = t * (b1 + t * (b2 + t * (b3 + t * (b4 + t * b5))))
        val prob = 1f - expPart * poly

        return if (z > 0) prob else 1f - prob
    }

    /**
     * Converts Bhattacharyya Distance into a normalized 0 to 1 percentage (Bhattacharyya Coefficient).
     */
    fun bhattacharyyaCoefficient(muA: FloatArray, varA: FloatArray, muB: FloatArray, varB: FloatArray): Float {
        val distB = bhattacharyyaDistance(muA, varA, muB, varB)
        return exp(-distB)
    }

    /**
     * Calculates the Bhattacharyya Distance D_B(A, B) between two statistical domains.
     */
    private fun bhattacharyyaDistance(muA: FloatArray, varA: FloatArray, muB: FloatArray, varB: FloatArray): Float {
        val d = muA.size
        var distPart1 = 0f
        var distPart2 = 0f

        for (j in 0 until d) {
            val vA = varA[j]
            val vB = varB[j]
            val meanVar = vA + vB

            // First term: Separation of means relative to pooled variance
            val diff = muA[j] - muB[j]
            distPart1 += (diff * diff) / meanVar

            // Second term: Difference in the shape/spread of the variance
            val shapeRatio = meanVar / (2f * sqrt(vA * vB))
            distPart2 += ln(shapeRatio.toDouble()).toFloat()
        }
        return (0.25f * distPart1) + (0.5f * distPart2)
    }

    /**
     * Sum of the diagonal of the variance matrix.
     */
    fun varianceTrace(variance: FloatArray): Float {
        var trace = 0f
        for (v in variance) trace += v
        return trace
    }
}