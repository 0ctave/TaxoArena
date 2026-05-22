package org.eclipse.lmos.arc.app.taxonomy

import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.stereotype.Component

/**
 * Defines the thermodynamic constraints and dynamic parameters of the domain inference space.
 * Follows the principle of Hysteresis: (tauFit < tauReparent < tauMerge).
 */
@Component
@ConfigurationProperties(prefix = "taxoadapt.formalism")
class TaxonomyConfig {
    // Hysteresis Likeness Factors
    var tauFit: Float = 0.70f       // Probability to trickle down into a domain
    var tauReparent: Float = 0.85f  // Avg probability required to topological subsume
    var tauMerge: Float = 0.95f     // Bhattacharyya similarity required to fuse domains
    var inclusionScalingFactor: Float = 5.0f // Scales the Mahalanobis distance curve (lower = stricter)

    // Context-Aware Density (Depth Decay)
    var splitBaseThreshold: Int = 50
    var splitMinThreshold: Int = 5
    var depthDecayLambda: Float = 0.6f

    // Splitting Compression
    var varianceCompressionRho: Float = 0.60f // Children must be 40% tighter than parent
    var minVarianceFloor: Float = 0.01f       // Prevents singularity when |Q| = 1

    // Thermodynamic Stabilization (Simulated Annealing)
    var annealingAlpha: Float = 1.15f         // Cooling rate per epoch

    // Graph Limits
    var maxDepth: Int = 4
    var maxWidth: Int = 8
    var perturbFlushThreshold: Int = 3        // ΔG threshold to trigger Op 5 (Clearing)
}