package taxonomy.tui.features.config

import taxonomy.config.DatasetType
import taxonomy.config.LlmProviderType
import taxonomy.config.TaxonomyConfig
import taxonomy.tui.components.SettingItem

/**
 * Extracted from DashboardRoot.kt
 * Pure definition of configurable items mapping directly to the TaxonomyConfig.
 */
object SettingDefinitions {

    fun buildSettingItems(config: TaxonomyConfig): List<SettingItem> {
        return listOf(
            SettingItem(
                name = "Evolution Iterations",
                description = "Number of optimization iterations",
                category = "Execution Settings",
                getValue = { config.numIterations.toString() },
                setValue = { s -> s.toIntOrNull()?.let { config.numIterations = it; true } ?: false }
            ),
            SettingItem(
                name = "Early Stopping",
                description = "Enable early stopping based on GED and volume convergence",
                category = "Execution Settings",
                getValue = { config.enableEarlyStopping.toString() },
                setValue = { s -> s.toBooleanStrictOrNull()?.let { config.enableEarlyStopping = it; true } ?: false }
            ),
            SettingItem(
                name = "Labeling",
                description = "Enable LLM labeling of nodes",
                category = "Execution Settings",
                getValue = { config.enableLabeling.toString() },
                setValue = { s -> s.toBooleanStrictOrNull()?.let { config.enableLabeling = it; true } ?: false }
            ),
            SettingItem(
                name = "Live Labeling",
                description = "Enable live LLM labeling of nodes during execution",
                category = "Execution Settings",
                getValue = { config.enableLiveLabeling.toString() },
                setValue = { s -> s.toBooleanStrictOrNull()?.let { config.enableLiveLabeling = it; true } ?: false }
            ),
            SettingItem(
                name = "Split Dataset",
                description = "Whether to split the dataset 80% train / 20% test",
                category = "Dataset Settings",
                getValue = { config.dataset.splitDataset.toString() },
                setValue = { s -> s.lowercase().toBooleanStrictOrNull()?.let { config.dataset.splitDataset = it; true } ?: false }
            ),
            SettingItem(
                name = "Test Split Ratio",
                description = "Ratio of reserved test set queries (e.g. 0.2)",
                category = "Dataset Settings",
                getValue = { config.dataset.testSplitRatio.toString() },
                setValue = { s -> s.toDoubleOrNull()?.let { config.dataset.testSplitRatio = it; true } ?: false }
            ),
            SettingItem(
                name = "Selected Domains",
                description = "Comma-separated domains to filter",
                category = "Dataset Settings",
                getValue = { config.dataset.selectedDomains.joinToString(", ") },
                setValue = { s ->
                    config.dataset.selectedDomains =
                        s.split(",").map { it.trim() }.filter { it.isNotEmpty() }
                    true
                }
            ),
            SettingItem(
                name = "Dataset Type",
                description = "Active dataset to run",
                category = "Dataset Settings",
                getValue = { config.dataset.datasetType.name },
                setValue = { s ->
                    try {
                        val newType = DatasetType.valueOf(s.uppercase())
                        if (newType != config.dataset.datasetType) {
                            config.dataset.datasetType = newType
                            config.dataset.selectedDomains = emptyList()
                        }
                        true
                    } catch (_: Exception) {
                        false
                    }
                }
            ),
            SettingItem(
                name = "LLM Provider",
                description = "Source for LLM model",
                category = "LLM & Model Settings",
                getValue = { config.llm.provider.name },
                setValue = { s ->
                    try {
                        config.llm.provider = LlmProviderType.valueOf(s.uppercase())
                        true
                    } catch (_: Exception) {
                        false
                    }
                }
            )
        )
    }
}