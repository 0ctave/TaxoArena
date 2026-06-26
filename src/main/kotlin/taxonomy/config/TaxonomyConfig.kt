package taxonomy.config

import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.context.annotation.Configuration
import taxonomy.model.Embedding
import taxonomy.model.GraphNode

/**
 * Defines the thermodynamic constraints and dynamic parameters of the domain inference space.
 * Updated to align with the Thermodynamic Formalism using vMF-k-means and NiW posteriors.
 */
@Configuration
@ConfigurationProperties(prefix = "taxoadapt")
class TaxonomyConfig {
    var execution: ExecutionConfig = ExecutionConfig()
    var dataset: DatasetConfig = DatasetConfig()
    var llm: LlmConfig = LlmConfig()
    var formalism: FormalismConfig = FormalismConfig()

    // --- Backwards Compatibility Fallback Bindings ---

    var calibrate: Boolean
        get() = execution.calibrate
        set(value) { execution.calibrate = value }

    var startService: Boolean
        get() = execution.startService
        set(value) { execution.startService = value }

    var numIterations: Int
        get() = execution.numIterations
        set(value) { execution.numIterations = value }

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


    var splitDataset: Boolean
        get() = dataset.splitDataset
        set(value) { dataset.splitDataset = value }

    var testSplitRatio: Double
        get() = dataset.testSplitRatio
        set(value) { dataset.testSplitRatio = value }

    var selectedDomains: List<String>
        get() = dataset.selectedDomains
        set(value) { dataset.selectedDomains = value }

    var datasetType: DatasetType
        get() = dataset.datasetType
        set(value) { dataset.datasetType = value }

    var provider: LlmProviderType
        get() = llm.provider
        set(value) { llm.provider = value }

    var embeddingProvider: LlmProviderType
        get() = llm.embeddingProvider
        set(value) { llm.embeddingProvider = value }

    var embeddingModel: String
        get() = llm.embeddingModel
        set(value) { llm.embeddingModel = value }

    var enableEarlyStopping: Boolean
        get() = execution.enableEarlyStopping
        set(value) { execution.enableEarlyStopping = value }

    var enableLabeling: Boolean
        get() = execution.enableLabeling
        set(value) { execution.enableLabeling = value }

    var enableLiveLabeling: Boolean
        get() = execution.enableLiveLabeling
        set(value) { execution.enableLiveLabeling = value }

    class ExecutionConfig {
        var calibrate: Boolean = false
        var startService: Boolean = false
        var numIterations: Int = 15
        var enableEarlyStopping: Boolean = true
        var enableVisualization: Boolean = true
        var enableTui: Boolean = true
        var enableLabeling: Boolean = false
        var enableLiveLabeling: Boolean = false
        val llmParallelism: Int = 8
    }

    class DatasetConfig {
        var datasetType: DatasetType = DatasetType.AG_NEWS
        var splitDataset: Boolean = true
        var testSplitRatio: Double = 0.2
        var selectedDomains: List<String> = emptyList()

        // Directory holding TIGER-AI-Lab MMLU-Pro eval_results files
        // (`model_outputs_<MODEL>_<N>shots.zip` / `.json`) for precomputed-answer mode.
        var evalResultsDir: String = "eval_results"
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


    class FormalismConfig {
        // ── Tree structure ────────────────────────────────────────────────────
        var maxDepth: Int = 12

        // ── Splitting ─────────────────────────────────────────────────────────
        // Minimum queries a node must hold before it is eligible for splitting.
        var minClusterSize: Int = 25

        // Dasgupta separation threshold: a split is accepted when its delta
        // exceeds this value, guaranteeing the two children are geometrically
        // separated in vMF space.
        var separationEpsilon: Double = 0.04

        // ── Routing ───────────────────────────────────────────────────────────
        // Temperature for the softmax over sibling log-likelihoods at each tree
        // node during trickle routing.  Higher = softer (more spread).
        var cosineTau: Double = 2.0

        // Log-likelihood margin for leaf assignment.
        //
        // A query is assigned to every leaf whose vMF log-likelihood is within
        // [assignmentMargin] nats of the best-scoring leaf.  This replaces the
        // old hard cap (maxLeafAssignments) with a geometrically meaningful
        // criterion: only plausible secondary matches are accepted.
        //
        // Intuition: at kappa ≈ 100 a margin of 1.0 nat ≈ Δcosine 0.01,
        // so only leaves whose mean is within ~1° of the best match are included.
        // Increase to allow more cross-domain overlap; decrease for stricter purity.
        var assignmentGap: Double = 0.05

        // ── Merging / convergence ─────────────────────────────────────────────
        var emaAlpha: Double = 0.7
        val gedThreshold: Double = 0.005

        // ── Iteration budget ──────────────────────────────────────────────────
        // (numIterations lives in ExecutionConfig for historical reasons)
    }

    fun formatConfigReport(): String {
        val sb = StringBuilder()
        sb.append("\n┌── TAXONOMY CONFIGURATION PARAMETERS ─────────────────────\n")
        sb.append("│ Execution Settings:\n")
        sb.append("│   - Dataset Type:         ${datasetType.name}\n")
        sb.append("│   - Num Iterations:       $numIterations\n")
        sb.append("│   - Early Stopping:       ${enableEarlyStopping}\n")
        sb.append("│   - Labeling:             $enableLabeling\n")
        sb.append("│   - Live Labeling:        $enableLiveLabeling\n")
        sb.append("│   - Selected Domains:     ${selectedDomains.ifEmpty { listOf("All") }}\n")
        sb.append("│   - Split Dataset:        $splitDataset\n")
        sb.append("│   - Test Split Ratio:     $testSplitRatio\n")
        sb.append("├── LLM & Embedding Models:\n")
        sb.append("│   - LLM Provider:         $provider\n")
        sb.append("│   - Embedding Provider:   $embeddingProvider\n")
        sb.append("│   - Embedding Model:      $embeddingModel\n")
        sb.append("│   - Judge Model:          $judgeModel\n")
        sb.append("│   - Labeling Model:       $labelingModel\n")
        sb.append("│   - Max Judge Generality: $maxJudgeGenerality\n")
        sb.append("├── Advanced Mathematical Formalism Controls:\n")
        sb.append("│   - Max Depth:            ${formalism.maxDepth}\n")
        sb.append("│   - Min Cluster Size:     ${formalism.minClusterSize}\n")
        sb.append("│   - Split Threshold:      ${2 * formalism.minClusterSize} (= 2 × minClusterSize)\n")
        sb.append("│   - Separation Epsilon:   ${formalism.separationEpsilon}\n")
        sb.append("│   - Cosine Tau:           ${formalism.cosineTau}\n")
        sb.append("│   - Assignment Gap:    ${formalism.assignmentGap}\n")
        sb.append("│   - EMA Alpha:            ${formalism.emaAlpha}\n")
        sb.append("└──────────────────────────────────────────────────────────")
        return sb.toString()
    }
}

@kotlinx.serialization.Serializable
enum class LlmProviderType {
    OLLAMA,
    AZURE
}

@kotlinx.serialization.Serializable
enum class DatasetType {
    MMLU_PRO,
    MMLU_ORIGINAL,
    ARC,
    TWENTY_NEWSGROUPS,
    AG_NEWS
}