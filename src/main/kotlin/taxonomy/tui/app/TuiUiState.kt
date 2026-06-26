package taxonomy.tui.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.Stable
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import taxonomy.config.DatasetType
import taxonomy.config.LlmProviderType
import taxonomy.tui.components.SettingItem
import taxonomy.tui.components.StartupState
import java.time.LocalTime

enum class TuiFocusedPanel {
    TOPOLOGY,
    ANALYSIS_HUB,
    SYSTEM_LOGS
}

enum class TuiConfigPanel {
    DOMAINS,
    SETTINGS
}

@Stable
class TuiUiState(
    val scrollOffset: androidx.compose.runtime.MutableIntState,
    val selectedIdx: androidx.compose.runtime.MutableIntState,
    val autoScroll: androidx.compose.runtime.MutableState<Boolean>,
    val inspectorScroll: androidx.compose.runtime.MutableIntState,
    val logScrollOffset: androidx.compose.runtime.MutableIntState,
    val metricsScrollOffset: androidx.compose.runtime.MutableIntState,
    val selectedSettingIdx: androidx.compose.runtime.MutableIntState,
    val isEditingSetting: androidx.compose.runtime.MutableState<Boolean>,
    val editingValue: androidx.compose.runtime.MutableState<String>,
    val settingsVersion: androidx.compose.runtime.MutableIntState,
    val selectedSnapshotIdx: androidx.compose.runtime.MutableIntState,
    val isSavingSnapshot: androidx.compose.runtime.MutableState<Boolean>,
    val snapshotDescInput: androidx.compose.runtime.MutableState<String>,
    val snapshotVersion: androidx.compose.runtime.MutableIntState,
    val snapshotList: androidx.compose.runtime.MutableState<List<taxonomy.service.DagSnapshot>>,
    val startupState: androidx.compose.runtime.MutableState<StartupState>,
    val downloadingDataset: androidx.compose.runtime.MutableState<Boolean>,
    val datasetDownloadProgress: androidx.compose.runtime.MutableFloatState,
    val datasetDownloadStatusText: androidx.compose.runtime.MutableState<String>,
    val selectedWelcomeIdx: androidx.compose.runtime.MutableIntState,
    val loadingSnapshotId: androidx.compose.runtime.MutableState<String?>,
    val activeConfigPanel: androidx.compose.runtime.MutableState<TuiConfigPanel>,
    val showAsciiTree: androidx.compose.runtime.MutableState<Boolean>,
    val expandedNodes: androidx.compose.runtime.snapshots.SnapshotStateMap<String, Boolean>,
    val selectedTreeIdx: androidx.compose.runtime.MutableIntState,
    val treeScrollOffset: androidx.compose.runtime.MutableIntState,
    val focusedPanel: androidx.compose.runtime.MutableState<TuiFocusedPanel>,
    val currentTime: androidx.compose.runtime.MutableState<LocalTime>,
    val spinnerTick: androidx.compose.runtime.MutableIntState,
    val isRegenerating: androidx.compose.runtime.MutableState<Boolean>,
    val isViewingSnapshot: androidx.compose.runtime.MutableState<Boolean>,
    val activeSnapshotId: androidx.compose.runtime.MutableState<String?>,
    val activeSnapshotDescription: androidx.compose.runtime.MutableState<String?>,
    val isRenamingSnapshot: androidx.compose.runtime.MutableState<Boolean>,
    val renameInput: androidx.compose.runtime.MutableState<String>,
    val selectedDomainIdx: androidx.compose.runtime.MutableIntState,
    val domainScrollOffset: androidx.compose.runtime.MutableIntState,
) {
    var settingItems: List<SettingItem> = emptyList()
}

@Composable
fun rememberTuiState(): TuiUiState {
    return remember {
        TuiUiState(
            scrollOffset = mutableIntStateOf(0),
            selectedIdx = mutableIntStateOf(0),
            autoScroll = mutableStateOf(true),
            inspectorScroll = mutableIntStateOf(0),
            logScrollOffset = mutableIntStateOf(0),
            metricsScrollOffset = mutableIntStateOf(0),
            selectedSettingIdx = mutableIntStateOf(0),
            isEditingSetting = mutableStateOf(false),
            editingValue = mutableStateOf(""),
            settingsVersion = mutableIntStateOf(0),
            selectedSnapshotIdx = mutableIntStateOf(0),
            isSavingSnapshot = mutableStateOf(false),
            snapshotDescInput = mutableStateOf(""),
            snapshotVersion = mutableIntStateOf(0),
            snapshotList = mutableStateOf(emptyList()),
            startupState = mutableStateOf(StartupState.WELCOME),
            downloadingDataset = mutableStateOf(false),
            datasetDownloadProgress = mutableFloatStateOf(0f),
            datasetDownloadStatusText = mutableStateOf(""),
            selectedWelcomeIdx = mutableIntStateOf(0),
            loadingSnapshotId = mutableStateOf(null),
            activeConfigPanel = mutableStateOf(TuiConfigPanel.DOMAINS),
            showAsciiTree = mutableStateOf(true),
            expandedNodes = mutableStateMapOf(),
            selectedTreeIdx = mutableIntStateOf(0),
            treeScrollOffset = mutableIntStateOf(0),
            focusedPanel = mutableStateOf(TuiFocusedPanel.TOPOLOGY),
            currentTime = mutableStateOf(LocalTime.now()),
            spinnerTick = mutableIntStateOf(0),
            isRegenerating = mutableStateOf(false),
            isViewingSnapshot = mutableStateOf(false),
            activeSnapshotId = mutableStateOf(null),
            activeSnapshotDescription = mutableStateOf(null),
            isRenamingSnapshot = mutableStateOf(false),
            renameInput = mutableStateOf(""),
            selectedDomainIdx = mutableIntStateOf(0),
            domainScrollOffset = mutableIntStateOf(0),
        )
    }
}

/**
 * Builds the same settings list the old dashboard constructed inline from config.
 */
fun buildSettingItems(deps: TuiDependencies): List<SettingItem> = listOf(
    SettingItem(
        name = "Evolution Iterations",
        description = "Number of optimization iterations",
        category = "Execution Settings",
        getValue = { deps.config.execution.numIterations.toString() },
        setValue = { s -> s.toIntOrNull()?.let { deps.config.execution.numIterations = it; true } ?: false }
    ),
    SettingItem(
        name = "Early Stopping",
        description = "Enable early stopping based on convergence",
        category = "Execution Settings",
        getValue = { deps.config.execution.enableEarlyStopping.toString() },
        setValue = { s -> s.toBooleanStrictOrNull()?.let { deps.config.execution.enableEarlyStopping = it; true } ?: false }
    ),
    SettingItem(
        name = "Labeling",
        description = "Enable LLM labeling of nodes",
        category = "Execution Settings",
        getValue = { deps.config.execution.enableLabeling.toString() },
        setValue = { s -> s.toBooleanStrictOrNull()?.let { deps.config.execution.enableLabeling = it; true } ?: false }
    ),
    SettingItem(
        name = "Live Labeling",
        description = "Enable live LLM labeling during execution",
        category = "Execution Settings",
        getValue = { deps.config.execution.enableLiveLabeling.toString() },
        setValue = { s -> s.toBooleanStrictOrNull()?.let { deps.config.execution.enableLiveLabeling = it; true } ?: false }
    ),
    SettingItem(
        name = "Dataset Type",
        description = "Active dataset",
        category = "Dataset Settings",
        getValue = { deps.config.dataset.datasetType.name },
        setValue = { s ->
            try {
                deps.config.dataset.datasetType = DatasetType.valueOf(s.uppercase())
                deps.config.dataset.selectedDomains = emptyList()
                true
            } catch (_: Exception) {
                false
            }
        }
    ),
    SettingItem(
        name = "Selected Domains",
        description = "Comma-separated domains",
        category = "Dataset Settings",
        getValue = { deps.config.dataset.selectedDomains.joinToString(", ") },
        setValue = { s ->
            deps.config.dataset.selectedDomains =
                s.split(",").map { it.trim() }.filter { it.isNotBlank() }
            true
        }
    ),
    SettingItem(
        name = "LLM Provider",
        description = "LLM provider",
        category = "LLM Model Settings",
        getValue = { deps.config.llm.provider.name },
        setValue = { s ->
            try {
                deps.config.llm.provider = LlmProviderType.valueOf(s.uppercase())
                true
            } catch (_: Exception) {
                false
            }
        }
    ),
    SettingItem(
        name = "Embedding Model",
        description = "Embedding model",
        category = "LLM Model Settings",
        getValue = { deps.config.llm.embeddingModel },
        setValue = { s ->
            if (s.isNotBlank()) {
                deps.config.llm.embeddingModel = s
                true
            } else false
        }
    ),
    SettingItem(
        name = "Labeling Model",
        description = "Labeling model",
        category = "LLM Model Settings",
        getValue = { deps.config.llm.labelingModel },
        setValue = { s ->
            if (s.isNotBlank()) {
                deps.config.llm.labelingModel = s
                true
            } else false
        }
    ),
    SettingItem(
        name = "Expert Judge Model",
        description = "Judge model",
        category = "LLM Model Settings",
        getValue = { deps.config.llm.judgeModel },
        setValue = { s ->
            if (s.isNotBlank()) {
                deps.config.llm.judgeModel = s
                true
            } else false
        }
    ),
    SettingItem(
        name = "Max Hierarchy Depth",
        description = "Maximum DAG depth",
        category = "Mathematical Formalism",
        getValue = { deps.config.formalism.maxDepth.toString() },
        setValue = { s -> s.toIntOrNull()?.let { deps.config.formalism.maxDepth = it; true } ?: false }
    ),
    SettingItem(
        name = "Min Cluster Size",
        description = "Minimum split cluster size",
        category = "Mathematical Formalism",
        getValue = { deps.config.formalism.minClusterSize.toString() },
        setValue = { s -> s.toIntOrNull()?.let { deps.config.formalism.minClusterSize = it; true } ?: false }
    ),
    SettingItem(
        name = "Separation Epsilon",
        description = "Geometric distinctness threshold",
        category = "Mathematical Formalism",
        getValue = { deps.config.formalism.separationEpsilon.toString() },
        setValue = { s -> s.toDoubleOrNull()?.let { deps.config.formalism.separationEpsilon = it; true } ?: false }
    ),
    SettingItem(
        name = "Cosine Tau",
        description = "Routing temperature",
        category = "Mathematical Formalism",
        getValue = { deps.config.formalism.cosineTau.toString() },
        setValue = { s -> s.toDoubleOrNull()?.let { deps.config.formalism.cosineTau = it; true } ?: false }
    ),
    SettingItem(
        name = "Assignment Gap",
        description = "Maximum leaf assignments",
        category = "Mathematical Formalism",
        getValue = { deps.config.formalism.assignmentGap.toString() },
        setValue = { s -> s.toDoubleOrNull()?.let { deps.config.formalism.assignmentGap = it; true } ?: false }
    ),
    SettingItem(
        name = "EMA Alpha",
        description = "EMA factor",
        category = "Mathematical Formalism",
        getValue = { deps.config.formalism.emaAlpha.toString() },
        setValue = { s -> s.toDoubleOrNull()?.let { deps.config.formalism.emaAlpha = it; true } ?: false }
    ),
)