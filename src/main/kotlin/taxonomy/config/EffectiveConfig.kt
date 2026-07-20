package taxonomy.config

import kotlinx.serialization.Serializable

/**
 * Immutable, serializable snapshot of the effective tunable configuration.
 *
 * This is the persistence/transport representation of [TaxonomyConfig]: it carries
 * the algorithmic, dataset and model tunables that should travel with a DAG snapshot
 * and be restored when that snapshot is loaded.
 *
 * Deliberately excluded:
 *  - secrets (Azure/Gemini endpoints & API keys) — those stay externalized via env/.env;
 *  - launch-mode flags (enableTui, startService, calibrate, enableVisualization) — those are
 *    environment concerns, not snapshot tunables, and must not be silently flipped on restore.
 */
@Serializable
data class EffectiveConfig(
    val execution: Execution = Execution(),
    val dataset: Dataset = Dataset(),
    val llm: Llm = Llm(),
    val formalism: Formalism = Formalism()
) {
    @Serializable
    data class Execution(
        val numIterations: Int = 15,
        val enableEarlyStopping: Boolean = true,
        val enableLabeling: Boolean = false
    )

    @Serializable
    data class Dataset(
        val datasetType: DatasetType = DatasetType.AG_NEWS,
        val splitDataset: Boolean = true,
        val testSplitRatio: Double = 0.2,
        val selectedDomains: List<String> = emptyList()
    )

    @Serializable
    data class Llm(
        val provider: LlmProviderType = LlmProviderType.OLLAMA,
        val embeddingProvider: LlmProviderType = LlmProviderType.OLLAMA,
        val judgeModel: String = "ministral-3:14b",
        val labelingModel: String = "ministral-3:14b",
        val embeddingModel: String = "qwen3-embedding",
        val maxJudgeGenerality: Int = 1,
        val judgeDomains: List<String> = emptyList()
    )

    @Serializable
    data class Formalism(
        val maxDepth: Int = 12,
        val minClusterSize: Int = 25,
        val separationEpsilon: Double = 0.04,
        val cosineTau: Double = 2.0,
        val routingSoftmaxTau: Double = 1.0,
        val leafAcceptanceScale: Double = 1.0,
        val assignmentGap: Double = 0.05,
        val assignmentCosineGap: Double = 0.03,
        val deltaAssign: Double = 0.20,
        val maxLeafAssignments: Int = 5,
        val emaAlpha: Double = 0.7,
        val enableStableQuestionIds: Boolean = false,
        val enableResidualRouting: Boolean = false,
        val enableResidualSplitGate: Boolean = false,
        val enableBridging: Boolean = false,
        val refitMuPerIteration: Boolean = false,
        val hdlssThreshold: Double = 8.0,
        val fusionSimilarityThreshold: Double = 0.92,
        val effectiveSupportFloor: Double = 2.0,
        val secondaryMassFloor: Double = 5.0,
        val bridgeSupportFloor: Double = 50.0,
        val tauFunnelFloor: Double = 0.90,
        val defaultKappaPrior: Double = 10.0,
        val dPrefix: Int = 64
    )
}
