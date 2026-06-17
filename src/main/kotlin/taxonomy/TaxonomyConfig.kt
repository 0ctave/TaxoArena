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
    var execution: ExecutionConfig = ExecutionConfig()
    var dataset: DatasetConfig = DatasetConfig()
    var llm: LlmConfig = LlmConfig()
    var persistence: PersistenceConfig = PersistenceConfig()
    var formalism: FormalismConfig = FormalismConfig()

    // --- Backwards Compatibility Fallback Bindings ---
    var runBatch: Boolean
        get() = execution.runBatch
        set(value) { execution.runBatch = value }

    var calibrate: Boolean
        get() = execution.calibrate
        set(value) { execution.calibrate = value }

    var startService: Boolean
        get() = execution.startService
        set(value) { execution.startService = value }

    var numIterations: Int
        get() = execution.numIterations
        set(value) { execution.numIterations = value }

    var enableDistillation: Boolean
        get() = execution.enableDistillation
        set(value) { execution.enableDistillation = value }

    var enableVisualization: Boolean
        get() = execution.enableVisualization
        set(value) { execution.enableVisualization = value }

    var enableTui: Boolean
        get() = execution.enableTui
        set(value) { execution.enableTui = value }

    var judgeModel: String
        get() = llm.judgeModel
        set(value) { llm.judgeModel = value }

    var labelingModel: String
        get() = llm.labelingModel
        set(value) { llm.labelingModel = value }

    var maxJudgeGenerality: Int
        get() = llm.maxJudgeGenerality
        set(value) { llm.maxJudgeGenerality = value }

    var sample: Int
        get() = dataset.sample
        set(value) { dataset.sample = value }

    var splitDataset: Boolean
        get() = dataset.splitDataset
        set(value) { dataset.splitDataset = value }

    var testSplitRatio: Double
        get() = dataset.testSplitRatio
        set(value) { dataset.testSplitRatio = value }

    var selectedDomains: List<String>
        get() = dataset.selectedDomains
        set(value) { dataset.selectedDomains = value }

    var provider: LlmProviderType
        get() = llm.provider
        set(value) { llm.provider = value }

    var embeddingProvider: LlmProviderType
        get() = llm.embeddingProvider
        set(value) { llm.embeddingProvider = value }

    var embeddingModel: String
        get() = llm.embeddingModel
        set(value) { llm.embeddingModel = value }

    var enableLiveLabeling: Boolean
        get() = formalism.enableLiveLabeling
        set(value) { formalism.enableLiveLabeling = value }

    class ExecutionConfig {
        var runBatch: Boolean = true
        var calibrate: Boolean = false
        var startService: Boolean = false
        var numIterations: Int = 5
        var enableDistillation: Boolean = true
        var enableVisualization: Boolean = true
        var enableTui: Boolean = true // Default to true for the new experience
    }

    class DatasetConfig {
        var sample: Int = 1000
        var splitDataset: Boolean = true
        var testSplitRatio: Double = 0.2
        var selectedDomains: List<String> = emptyList()
    }

    class LlmConfig {
        var provider: LlmProviderType = LlmProviderType.OLLAMA
        var embeddingProvider: LlmProviderType = LlmProviderType.OLLAMA
        var judgeModel: String = "ministral-3:14b"
        var labelingModel: String = "ministral-3:14b"
        var embeddingModel: String = "qwen3-embedding"
        var maxJudgeGenerality: Int = 1 // 0 = only leaves, 1 = leaves + parents, etc.
        var gemini: GeminiConfig = GeminiConfig()
        var azure: AzureConfig = AzureConfig()
    }

    class GeminiConfig {
        var apiKey: String? = null
        var modelName: String = "gemini-1.5-flash"
    }

    class AzureConfig {
        var endpoint: String = ""
        var apiKey: String = ""
        var deploymentName: String = ""
        var embeddingDeploymentName: String = ""
        var apiVersion: String = "2024-02-15-preview"
    }

    class PersistenceConfig {
        var loadPath: String? = "taxonomy_final.json"
        var savePath: String? = "taxonomy_final.json"
    }

    // --- Phase 2 & 3: HMM & Trickle (Hierarchical Mixture Foundations) ---
    class FormalismConfig {
        var maxDepth: Int = 5

        // Hysteresis Likeness Factors (Probabilities)
        var tauFit: Double = 0.95
        var tauReparent: Double = 0.82
        var tauMerge: Double = 0.92
        
        var inclusionScalingFactor: Double = 1.0

        // Context-Aware Density (Depth Decay)
        var splitBaseThreshold: Int = 50
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

        var enableMrl: Boolean = true
        var fixedMrlDimension: Int = 384
        var enableLiveLabeling: Boolean = true

        // Max branches to explore during trickle. Set to <= 0 (e.g., -1) to explore all viable branches.
        var maxTrickleBranches: Int = 3
        var maxAssignmentsPerQuery: Int = 2

        // Dynamic Dimension Scaling
        var enableDynamicDimension: Boolean = true
        var dynamicDimensionFactor: Double = 2.0
        var dynamicDimensionFloor: Int = 16

        // Split Floor Guard & DBSCAN Limits
        var minRelativeSplitSize: Double = 0.08
        var dbscanEpsFloor: Double = 0.05
        var dbscanEpsCeiling: Double = 0.35
        var collapseMarginalRatio: Double = 0.05

        // Phase 6: Stabilization & Convergence
        var annealingAlpha: Double = 1.05
        var emaAlpha: Double = 0.7
        var persistenceBias: Double = 0.8
        var gedThreshold: Int = 0
        var volumeThreshold: Double = 1e-4
        var enableEarlyStopping: Boolean = true
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

enum class LlmProviderType {
    OLLAMA,
    AZURE
}
