package org.eclipse.lmos.arc.app.taxonomy

import kotlinx.serialization.Serializable

/**
 * Data Transfer Object (DTO) for parsing JSON responses from the LLM.
 * Used during Cluster Labeling (Splitting) and Super-Domain Synthesis (Reparenting).
 */
@Serializable
data class LocalLabelResponse(
    val label: String,
    val description: String
)

/**
 * Represents a single Gaussian Component within a Gaussian Mixture Model (GMM).
 * Used for highly-resolved geometric domain representation.
 */
class GaussianComponent(
    var weight: Float,
    var centroid: FloatArray,
    var variance: FloatArray
)