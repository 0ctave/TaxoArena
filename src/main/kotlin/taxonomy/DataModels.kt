package org.eclipse.lmos.arc.app.taxonomy

import kotlinx.serialization.Serializable

/**
 * Represents a high-dimensional vector x ∈ ℝᵈ along with its source text.
 * Stores both the original raw query and its distilled semantic signature.
 */
@Serializable
data class Embedding(
    val rawText: String,
    val distilledText: String,
    val values: FloatArray
) {
    @kotlinx.serialization.Transient
    var queryId: Int = -1

    val dimensions: Int get() = values.size

    // Convert to DoubleArray for high-precision statistical calculations (Mahalanobis/KL)
    fun toDoubleArray(): DoubleArray = DoubleArray(values.size) { values[it].toDouble() }

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Embedding) return false
        if (rawText != other.rawText) return false
        return values.contentEquals(other.values)
    }

    override fun hashCode(): Int {
        var result = rawText.hashCode()
        result = 31 * result + values.contentHashCode()
        return result
    }
}

/**
 * Parameters for a single component in a Gaussian Mixture Model.
 * High-dimensional vectors are stored in SQL and referenced by vectorId.
 */
@Serializable
data class GmmComponent(
    val mean: DoubleArray? = null,
    val diagonalCovariance: DoubleArray? = null,
    val weight: Double,
    val sampleCount: Int,
    val vectorId: String? = null
)

/**
 * Represents a Gaussian Mixture Model (GMM) distribution for a node.
 */
@Serializable
data class GmmParams(
    val components: List<GmmComponent>,
    var empiricalThreshold: Double = Double.MAX_VALUE
) {
    val totalSamples: Int get() = components.sumOf { it.sampleCount }
}

/**
 * Stores snapshot metrics of the DAG at a specific iteration or final state.
 */
@Serializable
data class IterationMetrics(
    val iteration: String,
    val totalNodes: Int,
    val leafNodes: Int,
    val crossDomainNodes: Int,
    val maxDepth: Int,
    val avgLeafDepth: Double,
    val totalUniqueQueries: Int,
    val residualQueries: Int,
    val totalPathRedundancy: Double,
    val totalLogVolume: Double,
    val residualRatio: Double,
    val maxLeafConcentration: Double,
    val contaminationRatio: Double,
    val equilibriumIndex: Double,
    val relevanceComplianceRatio: Double
)