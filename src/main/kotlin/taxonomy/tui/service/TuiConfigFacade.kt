package taxonomy.tui.service

import taxonomy.config.DatasetType
import taxonomy.config.LlmProviderType
import taxonomy.tui.app.TuiDependencies
import taxonomy.tui.components.SettingItem
import taxonomy.tui.components.SettingKind

class TuiConfigFacade(
    private val deps: TuiDependencies
) {
    fun buildSettingItems(): List<SettingItem> = listOf(
        SettingItem(
            name = "Evolution Iterations",
            description = "Number of optimization iterations",
            category = "Execution Settings",
            getValue = { deps.config.execution.numIterations.toString() },
            setValue = { s -> s.toIntOrNull()?.let { deps.config.execution.numIterations = it; true } ?: false },
            kind = SettingKind.NUMBER
        ),
        SettingItem(
            name = "Early Stopping",
            description = "Enable early stopping based on convergence",
            category = "Execution Settings",
            getValue = { deps.config.execution.enableEarlyStopping.toString() },
            setValue = { s -> s.toBooleanStrictOrNull()?.let { deps.config.execution.enableEarlyStopping = it; true } ?: false },
            kind = SettingKind.BOOLEAN
        ),
        SettingItem(
            name = "Labeling",
            description = "Enable LLM labeling of nodes",
            category = "Execution Settings",
            getValue = { deps.config.execution.enableLabeling.toString() },
            setValue = { s -> s.toBooleanStrictOrNull()?.let { deps.config.execution.enableLabeling = it; true } ?: false },
            kind = SettingKind.BOOLEAN
        ),
        SettingItem(
            name = "LLM Parallelism Limit",
            description = "Max parallel LLM requests limit for DAG generation & judge generation",
            category = "Execution Settings",
            getValue = { deps.config.execution.llmParallelism.toString() },
            setValue = { s ->
                s.toIntOrNull()?.let {
                    deps.config.execution.llmParallelism = it
                    deps.arenaService.llmClient.setMaxParallel(it)
                    true
                } ?: false
            },
            kind = SettingKind.NUMBER
        ),

        SettingItem(
            name = "Dataset Type",
            description = "Active dataset to run",
            category = "Dataset Settings",
            getValue = { deps.config.dataset.datasetType.name },
            setValue = { s ->
                try {
                    val newType = DatasetType.valueOf(s.uppercase())
                    if (newType != deps.config.dataset.datasetType) {
                        deps.config.dataset.datasetType = newType
                        deps.config.dataset.selectedDomains = emptyList()
                    }
                    true
                } catch (_: Exception) {
                    false
                }
            },
            kind = SettingKind.SELECT,
            options = DatasetType.entries.map { it.name }
        ),
        SettingItem(
            name = "Selected Domains",
            description = "Click/Enter to select which domains to generate",
            category = "Dataset Settings",
            getValue = {
                val size = deps.config.dataset.selectedDomains.size
                if (size == 0) "All domains selected" else "$size domains selected (${deps.config.dataset.selectedDomains.joinToString(", ")})"
            },
            setValue = { _ -> true },
            kind = SettingKind.TEXT
        ),
        SettingItem(
            name = "Split Dataset",
            description = "Whether to split dataset into train/test",
            category = "Dataset Settings",
            getValue = { deps.config.dataset.splitDataset.toString() },
            setValue = { s -> s.lowercase().toBooleanStrictOrNull()?.let { deps.config.dataset.splitDataset = it; true } ?: false },
            kind = SettingKind.BOOLEAN
        ),
        SettingItem(
            name = "Test Split Ratio",
            description = "Ratio of reserved test queries",
            category = "Dataset Settings",
            getValue = { deps.config.dataset.testSplitRatio.toString() },
            setValue = { s -> s.toDoubleOrNull()?.let { deps.config.dataset.testSplitRatio = it; true } ?: false },
            kind = SettingKind.NUMBER
        ),
        SettingItem(
            name = "LLM Provider",
            description = "Source for LLM model",
            category = "LLM & Embedding Models",
            getValue = { deps.config.llm.provider.name },
            setValue = { s ->
                try {
                    deps.config.llm.provider = LlmProviderType.valueOf(s.uppercase())
                    true
                } catch (_: Exception) {
                    false
                }
            },
            kind = SettingKind.SELECT,
            options = LlmProviderType.entries.map { it.name }
        ),
        SettingItem(
            name = "Labeling Model",
            description = "Node labeling model",
            category = "LLM & Embedding Models",
            getValue = { deps.config.llm.labelingModel },
            setValue = { s -> if (s.isNotBlank()) { deps.config.llm.labelingModel = s; true } else false },
            kind = SettingKind.TEXT
        ),
        SettingItem(
            name = "Expert Judge Model",
            description = "Pairwise judge model",
            category = "LLM & Embedding Models",
            getValue = { deps.config.llm.judgeModel },
            setValue = { s -> if (s.isNotBlank()) { deps.config.llm.judgeModel = s; true } else false },
            kind = SettingKind.TEXT
        ),
        SettingItem(
            name = "Embedding Provider",
            description = "Source for embedding model",
            category = "LLM & Embedding Models",
            getValue = { deps.config.llm.embeddingProvider.name },
            setValue = { s ->
                try {
                    deps.config.llm.embeddingProvider = LlmProviderType.valueOf(s.uppercase())
                    true
                } catch (_: Exception) {
                    false
                }
            },
            kind = SettingKind.SELECT,
            options = LlmProviderType.entries.map { it.name }
        ),
        SettingItem(
            name = "Embedding Model",
            description = "Embedding model name",
            category = "LLM & Embedding Models",
            getValue = { deps.config.llm.embeddingModel },
            setValue = { s -> if (s.isNotBlank()) { deps.config.llm.embeddingModel = s; true } else false },
            kind = SettingKind.TEXT
        ),
        SettingItem(
            name = "Max Hierarchy Depth",
            description = "Maximum DAG depth",
            category = "Taxonomy Geometry",
            getValue = { deps.config.formalism.maxDepth.toString() },
            setValue = { s -> s.toIntOrNull()?.let { deps.config.formalism.maxDepth = it; true } ?: false },
            kind = SettingKind.NUMBER
        ),
        SettingItem(
            name = "Min Cluster Size",
            description = "Minimum split size",
            category = "Taxonomy Geometry",
            getValue = { deps.config.formalism.minClusterSize.toString() },
            setValue = { s -> s.toIntOrNull()?.let { deps.config.formalism.minClusterSize = it; true } ?: false },
            kind = SettingKind.NUMBER
        ),
        SettingItem(
            name = "Max Judge Generality",
            description = "Judge induction scope (0=leaves, 1=+parents, 2=+grandparents)",
            category = "Taxonomy Geometry",
            getValue = { deps.config.llm.maxJudgeGenerality.toString() },
            setValue = { s -> s.toIntOrNull()?.let { deps.config.llm.maxJudgeGenerality = it; true } ?: false },
            kind = SettingKind.SELECT,
            options = listOf("0", "1", "2")
        ),
        SettingItem(
            name = "Separation Epsilon",
            description = "Geometric distinctness threshold",
            category = "Clustering & Routing (VMF)",
            getValue = { deps.config.formalism.separationEpsilon.toString() },
            setValue = { s -> s.toDoubleOrNull()?.let { deps.config.formalism.separationEpsilon = it; true } ?: false },
            kind = SettingKind.NUMBER
        ),
        SettingItem(
            name = "Routing Softmax Tau",
            description = "Routing softmax temperature",
            category = "Clustering & Routing (VMF)",
            getValue = { deps.config.formalism.routingSoftmaxTau.toString() },
            setValue = { s -> s.toDoubleOrNull()?.let { deps.config.formalism.routingSoftmaxTau = it; true } ?: false },
            kind = SettingKind.NUMBER
        )
    )

    fun getAvailableDomains(): List<Pair<String, Int>> = getAvailableDomains(false)

    fun getAvailableDomains(reservedOnly: Boolean = false, forceDataset: Boolean = false): List<Pair<String, Int>> {
        val root = deps.taxonomyService.getGraph()
        if (root != null && !forceDataset) {
            val reservedTexts = if (reservedOnly) {
                val file = java.io.File("reserved_test_queries.json")
                if (file.exists()) {
                    try {
                        val map: Map<String, List<String>> = kotlinx.serialization.json.Json.decodeFromString(file.readText())
                        map.values.flatten().toSet()
                    } catch (e: Exception) {
                        emptySet()
                    }
                } else {
                    emptySet()
                }
            } else {
                emptySet()
            }

            return root.children.map { child ->
                val rawName = child.label ?: child.id
                val prettyName = rawName.split("_", "-").joinToString(" ") { word ->
                    word.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
                }
                val count = if (reservedOnly) {
                    child.getAllQueriesInBranch().count { it.rawText in reservedTexts }
                } else {
                    child.getRecursiveQueryCount()
                }
                prettyName to count
            }.sortedBy { it.first }
        }
        return deps.datasetFetcher.getAvailableDomains()
    }

    fun isDatasetDownloaded(): Boolean =
        deps.datasetFetcher.isDatasetDownloaded()

    suspend fun downloadDataset() {
        deps.datasetFetcher.downloadDataset()
    }

    /** Apply an instant (boolean/select) setting or a confirmed editor value by name. */
    fun applySetting(name: String, value: String): Boolean =
        buildSettingItems().firstOrNull { it.name == name }?.setValue?.invoke(value) ?: false

    fun toggleDomain(domainName: String, availableDomains: List<Pair<String, Int>>) {
        val current = deps.config.dataset.selectedDomains.toMutableList().apply {
            if (contains(domainName)) remove(domainName) else add(domainName)
        }
        deps.config.dataset.selectedDomains = current
    }

    fun selectOnlyDomain(domainName: String) {
        deps.config.dataset.selectedDomains = listOf(domainName)
    }

    fun selectAllDomains() {
        deps.config.dataset.selectedDomains = emptyList()
    }
}
