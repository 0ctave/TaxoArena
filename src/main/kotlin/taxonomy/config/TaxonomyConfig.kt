package taxonomy.config

import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.context.annotation.Configuration
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import java.io.Serializable
import kotlinx.serialization.Serializable as KotlinxSerializable

@KotlinxSerializable
enum class DagMode { TREE_BASELINE, DAG_MAX }

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

    class ExecutionConfig {
        var calibrate: Boolean = false
        var startService: Boolean = false
        var numIterations: Int = 15
        var enableEarlyStopping: Boolean = true
        var enableVisualization: Boolean = true
        var enableTui: Boolean = true
        var enableLabeling: Boolean = false

        /**
         * Kill-switch for the pre-flight TTY probe done before the TUI enters the alt-screen.
         * The probe reflectively calls Mosaic's internal `Tty.tryBind()` to fail fast (and loudly)
         * when there is no controlling terminal. Set true to skip it entirely if the probe itself
         * ever misbehaves (e.g. the internal API changes); the TUI then starts optimistically.
         */
        var skipTtyPrecheck: Boolean = false
        var llmParallelism: Int = 8
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
        var judgeDomains: List<String> = emptyList()
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
        var routingSoftmaxTau: Double = 1.0
        var assignmentCosineGap: Double = 0.03
        var deltaAssign: Double = 0.20
        var maxLeafAssignments: Int = 5

        // ── Merging / convergence ─────────────────────────────────────────────
        var emaAlpha: Double = 0.7
        val gedThreshold: Double = 0.005

        // ── Mode Switch ──────────────────────────────────────────────────────
        var dagMode: DagMode = DagMode.DAG_MAX
            set(value) {
                field = value
                val isDag = (value == DagMode.DAG_MAX)
                enableStableQuestionIds = isDag
                enableResidualRouting = isDag
                enableResidualSplitGate = isDag
                enableBridging = isDag
                refitMuPerIteration = isDag
            }

        // ── Internal boolean flags (mapped by dagMode, overrideable for regression)
        var enableStableQuestionIds: Boolean = true
        var enableResidualRouting: Boolean = true
        var enableResidualSplitGate: Boolean = true
        var enableBridging: Boolean = true
        var refitMuPerIteration: Boolean = true

        var fusionSimilarityThreshold: Double = 0.92
        var effectiveSupportFloor: Double = 2.0
        var tauKappaScalingFactor: Double = 0.0
        var defaultKappaPrior: Double = 10.0
    }

    var diagnostics: DiagnosticsConfig = DiagnosticsConfig()

    class DiagnosticsConfig {
        var secondaryMassFloor: Double = 5.0
        var bridgeSupportFloor: Double = 50.0
        var bridgeSupportRelFraction: Double = 0.10
    }

    fun formatConfigReport(): String {
        val sb = StringBuilder()
        sb.append("\n┌── TAXONOMY CONFIGURATION PARAMETERS ─────────────────────\n")
        sb.append("│ Execution Settings:\n")
        sb.append("│   - Dataset Type:         ${dataset.datasetType.name}\n")
        sb.append("│   - Num Iterations:       ${execution.numIterations}\n")
        sb.append("│   - Early Stopping:       ${execution.enableEarlyStopping}\n")
        sb.append("│   - Labeling:             ${execution.enableLabeling}\n")
        sb.append("│   - Selected Domains:     ${dataset.selectedDomains.ifEmpty { listOf("All") }}\n")
        sb.append("│   - Split Dataset:        ${dataset.splitDataset}\n")
        sb.append("│   - Test Split Ratio:     ${dataset.testSplitRatio}\n")
        sb.append("├── LLM & Embedding Models:\n")
        sb.append("│   - LLM Provider:         ${llm.provider}\n")
        sb.append("│   - Embedding Provider:   ${llm.embeddingProvider}\n")
        sb.append("│   - Embedding Model:      ${llm.embeddingModel}\n")
        sb.append("│   - Judge Model:          ${llm.judgeModel}\n")
        sb.append("│   - Labeling Model:       ${llm.labelingModel}\n")
        sb.append("│   - Max Judge Generality: ${llm.maxJudgeGenerality}\n")
        sb.append("├── Advanced Mathematical Formalism Controls:\n")
        sb.append("│   - DAG Mode:             ${formalism.dagMode}\n")
        sb.append("│   - Max Depth:            ${formalism.maxDepth}\n")
        sb.append("│   - Min Cluster Size:     ${formalism.minClusterSize}\n")
        sb.append("│   - Separation Epsilon:   ${formalism.separationEpsilon}\n")
        sb.append("│   - Routing Softmax Tau:  ${formalism.routingSoftmaxTau}\n")
        sb.append("│   - Assignment Cosine Gap:${formalism.assignmentCosineGap}\n")
        sb.append("│   - Delta Assign:         ${formalism.deltaAssign}\n")
        sb.append("│   - EMA Alpha:            ${formalism.emaAlpha}\n")
        sb.append("│   - Fusion Sim Threshold: ${formalism.fusionSimilarityThreshold}\n")
        sb.append("│   - Eff Support Floor:    ${formalism.effectiveSupportFloor}\n")
        sb.append("│   - Default Kappa Prior:  ${formalism.defaultKappaPrior}\n")
        sb.append("└──────────────────────────────────────────────────────────")
        return sb.toString()
    }

    /** Capture the current tunables as an immutable, serializable snapshot (secrets excluded). */
    fun toEffectiveConfig(): EffectiveConfig = EffectiveConfig(
        execution = EffectiveConfig.Execution(
            numIterations = execution.numIterations,
            enableEarlyStopping = execution.enableEarlyStopping,
            enableLabeling = execution.enableLabeling
        ),
        dataset = EffectiveConfig.Dataset(
            datasetType = dataset.datasetType,
            splitDataset = dataset.splitDataset,
            testSplitRatio = dataset.testSplitRatio,
            selectedDomains = dataset.selectedDomains
        ),
        llm = EffectiveConfig.Llm(
            provider = llm.provider,
            embeddingProvider = llm.embeddingProvider,
            judgeModel = llm.judgeModel,
            labelingModel = llm.labelingModel,
            embeddingModel = llm.embeddingModel,
            maxJudgeGenerality = llm.maxJudgeGenerality,
            judgeDomains = llm.judgeDomains
        ),
        formalism = EffectiveConfig.Formalism(
            dagMode = formalism.dagMode,
            maxDepth = formalism.maxDepth,
            minClusterSize = formalism.minClusterSize,
            separationEpsilon = formalism.separationEpsilon,
            routingSoftmaxTau = formalism.routingSoftmaxTau,
            assignmentCosineGap = formalism.assignmentCosineGap,
            deltaAssign = formalism.deltaAssign,
            maxLeafAssignments = formalism.maxLeafAssignments,
            emaAlpha = formalism.emaAlpha,
            enableStableQuestionIds = formalism.enableStableQuestionIds,
            enableResidualRouting = formalism.enableResidualRouting,
            enableResidualSplitGate = formalism.enableResidualSplitGate,
            enableBridging = formalism.enableBridging,
            refitMuPerIteration = formalism.refitMuPerIteration,
            fusionSimilarityThreshold = formalism.fusionSimilarityThreshold,
            effectiveSupportFloor = formalism.effectiveSupportFloor,
            tauKappaScalingFactor = formalism.tauKappaScalingFactor,
            defaultKappaPrior = formalism.defaultKappaPrior
        ),
        diagnostics = EffectiveConfig.Diagnostics(
            secondaryMassFloor = diagnostics.secondaryMassFloor,
            bridgeSupportFloor = diagnostics.bridgeSupportFloor,
            bridgeSupportRelFraction = diagnostics.bridgeSupportRelFraction
        )
    )

    /** Apply a restored snapshot's tunables onto the live config. Secrets are left untouched. */
    fun applyEffectiveConfig(c: EffectiveConfig) {
        execution.numIterations = c.execution.numIterations
        execution.enableEarlyStopping = c.execution.enableEarlyStopping
        execution.enableLabeling = c.execution.enableLabeling

        dataset.datasetType = c.dataset.datasetType
        dataset.splitDataset = c.dataset.splitDataset
        dataset.testSplitRatio = c.dataset.testSplitRatio
        dataset.selectedDomains = c.dataset.selectedDomains

        llm.provider = c.llm.provider
        llm.embeddingProvider = c.llm.embeddingProvider
        llm.judgeModel = c.llm.judgeModel
        llm.labelingModel = c.llm.labelingModel
        llm.embeddingModel = c.llm.embeddingModel
        llm.maxJudgeGenerality = c.llm.maxJudgeGenerality
        llm.judgeDomains = c.llm.judgeDomains

        formalism.dagMode = c.formalism.dagMode
        formalism.maxDepth = c.formalism.maxDepth
        formalism.minClusterSize = c.formalism.minClusterSize
        formalism.separationEpsilon = c.formalism.separationEpsilon
        formalism.routingSoftmaxTau = c.formalism.routingSoftmaxTau
        formalism.assignmentCosineGap = c.formalism.assignmentCosineGap
        formalism.deltaAssign = c.formalism.deltaAssign
        formalism.maxLeafAssignments = c.formalism.maxLeafAssignments
        formalism.emaAlpha = c.formalism.emaAlpha
        formalism.enableStableQuestionIds = c.formalism.enableStableQuestionIds
        formalism.enableResidualRouting = c.formalism.enableResidualRouting
        formalism.enableResidualSplitGate = c.formalism.enableResidualSplitGate
        formalism.enableBridging = c.formalism.enableBridging
        formalism.refitMuPerIteration = c.formalism.refitMuPerIteration
        formalism.fusionSimilarityThreshold = c.formalism.fusionSimilarityThreshold
        formalism.effectiveSupportFloor = c.formalism.effectiveSupportFloor
        formalism.tauKappaScalingFactor = c.formalism.tauKappaScalingFactor
        formalism.defaultKappaPrior = c.formalism.defaultKappaPrior

        diagnostics.secondaryMassFloor = c.diagnostics.secondaryMassFloor
        diagnostics.bridgeSupportFloor = c.diagnostics.bridgeSupportFloor
        diagnostics.bridgeSupportRelFraction = c.diagnostics.bridgeSupportRelFraction
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