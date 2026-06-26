package taxonomy.tui.app

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.Composable
import taxonomy.service.DagSnapshot
import taxonomy.tui.components.StartupState

class TuiRuntimeState {
    var startupState by mutableStateOf(StartupState.WELCOME)

    var selectedIdx by mutableIntStateOf(0)
    var scrollOffset by mutableIntStateOf(0)
    var inspectorScroll by mutableIntStateOf(0)
    var logScrollOffset by mutableIntStateOf(0)
    var metricsScrollOffset by mutableIntStateOf(0)

    var selectedSettingIdx by mutableIntStateOf(0)
    var isEditingSetting by mutableStateOf(false)
    var editingValue by mutableStateOf("")
    var settingsVersion by mutableIntStateOf(0)

    var selectedSnapshotIdx by mutableIntStateOf(0)
    var isSavingSnapshot by mutableStateOf(false)
    var snapshotDescInput by mutableStateOf("")
    var snapshotList by mutableStateOf<List<DagSnapshot>>(emptyList())
    var snapshotVersion by mutableIntStateOf(0)

    var isViewingSnapshot by mutableStateOf(false)
    var activeSnapshotId by mutableStateOf<String?>(null)
    var activeSnapshotDescription by mutableStateOf<String?>(null)
    var isRenamingSnapshot by mutableStateOf(false)
    var renameInput by mutableStateOf("")
}

@Composable
fun rememberTuiRuntimeState(): TuiRuntimeState = remember { TuiRuntimeState() }