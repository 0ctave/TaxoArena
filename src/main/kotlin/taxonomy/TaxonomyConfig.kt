package org.eclipse.lmos.arc.app.taxonomy

import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.context.annotation.Configuration

/**
 * Defines the thermodynamic constraints and dynamic parameters of the domain inference space.
 * Follows the principle of Hysteresis: (tauFit < tauReparent < tauMerge).
 * Updated to align with the Thermodynamic Formalism while retaining GMM multi-centroid control.
 */
@Configuration
@ConfigurationProperties(prefix = "taxoadapt")
class TaxonomyConfig {
    var runBatch: Boolean = true
    var startService: Boolean = false
    var numIterations: Int = 5
    var enableDistillation: Boolean = true
    var enableVisualization: Boolean = true
    var enableTui: Boolean = true // Default to true for the new experience
    var judgeModel: String = "ministral-3:14b"
    var maxJudgeGenerality: Int = 1 // 0 = only leaves, 1 = leaves + parents, etc.

    var sample: Int = 1000

    var gemini: GeminiConfig = GeminiConfig()

    class GeminiConfig {
        var apiKey: String? = null
        var modelName: String = "gemini-1.5-flash"
    }

    var persistence: PersistenceConfig = PersistenceConfig()

    class PersistenceConfig {
        var loadPath: String? = "taxonomy_final.json"
        var savePath: String? = "taxonomy_final.json"
    }

    // --- Phase 2 & 3: HMM & Trickle (Hierarchical Mixture Foundations) ---
    var formalism: FormalismConfig = FormalismConfig()

    class FormalismConfig {
        var maxDepth: Int = 5

        // Hysteresis Likeness Factors (Probabilities)
        var tauFit: Double = 0.95
        var tauReparent: Double = 0.82
        var tauMerge: Double = 0.92
        
        var inclusionScalingFactor: Double = 1.0

        // Context-Aware Density (Depth Decay)
        var splitBaseThreshold: Int = 50
        var splitMinThreshold: Int = 25
        var depthDecayLambda: Double = 0.1

        // p-BIC Regularization
        var pBicLambda: Double = 0.1 

        // GMM / HMM Multi-Centroid Parameters
        var maxCentroidsPerNode: Int = 3
        var relativeMaxSize: Double = 0.7
        var oasShrinkage: Double = 0.1

        // MRL Funnel Limits
        var mrlLimits: Map<Int, Int> = mapOf(
            0 to 256,
            1 to 512,
            2 to 1024
        )

        var maxTrickleBranches: Int = 3
        var trickleAllViable: Boolean = false
        var maxAssignmentsPerQuery: Int = 2
    }
}

/**
 * Result of a Matching Operation (MAP Inference via BVH Pruning).
 */
data class InferenceMatch(
    val query: Embedding,
    val path: List<GraphNode>,
    val matchedNode: GraphNode,
    val isKdeMatch: Boolean
)
