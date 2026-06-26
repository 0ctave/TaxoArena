package taxonomy.tui.controller

import taxonomy.service.AnalysisMode
import taxonomy.service.DagSnapshot
import taxonomy.tui.components.StartupState
import taxonomy.tui.state.BenchmarkSubScreen
import taxonomy.tui.state.ConfigSubPanel
import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.ScrollbarTarget

sealed interface TuiEvent {

    data class Resize(val width: Int, val height: Int) : TuiEvent
    data object SpinnerTick : TuiEvent
    data object LogsTick : TuiEvent

    data class KeyPressed(
        val key: String,
        val rawKey: String = key
    ) : TuiEvent

    data class MousePressed(
        val x: Int,
        val y: Int,
        val button: MouseButton = MouseButton.Left
    ) : TuiEvent

    data class MouseReleased(
        val x: Int,
        val y: Int,
        val button: MouseButton = MouseButton.Left
    ) : TuiEvent

    data class MouseDragged(
        val x: Int,
        val y: Int
    ) : TuiEvent

    data class MouseWheel(
        val x: Int,
        val y: Int,
        val direction: WheelDirection
    ) : TuiEvent

    data class FocusPanelRequested(val panel: FocusPanel) : TuiEvent
    data object CycleFocusForward : TuiEvent

    data class SetStartupState(val state: StartupState) : TuiEvent
    data object ReturnToWelcome : TuiEvent
    data object EnterConfigSetup : TuiEvent
    data object EnterMainDashboard : TuiEvent

    data class SetAnalysisMode(val mode: AnalysisMode) : TuiEvent
    data class SetConfigSubPanel(val panel: ConfigSubPanel) : TuiEvent

    data class StartDraggingScrollbar(val target: ScrollbarTarget) : TuiEvent
    data object StopDraggingScrollbar : TuiEvent
    data class ScrollTo(val target: ScrollbarTarget, val offset: Int) : TuiEvent
    data class ScrollBy(val target: ScrollbarTarget, val delta: Int) : TuiEvent

    data object RefreshSnapshots : TuiEvent
    data class SnapshotsLoaded(val snapshots: List<DagSnapshot>) : TuiEvent
    data class SelectWelcomeIndex(val index: Int) : TuiEvent
    data class SelectSnapshotIndex(val index: Int) : TuiEvent
    data class RequestLoadSnapshot(val snapshotId: String) : TuiEvent
    data class SnapshotLoaded(val snapshotId: String, val description: String?) : TuiEvent
    data class SnapshotLoadFailed(val snapshotId: String) : TuiEvent
    data class RequestDeleteSnapshot(val snapshotId: String) : TuiEvent

    data object StartSaveSnapshot : TuiEvent
    data object ConfirmSaveSnapshot : TuiEvent
    data object CancelSaveSnapshot : TuiEvent
    data class UpdateSnapshotDescInput(val value: String) : TuiEvent

    data object StartRenameSnapshot : TuiEvent
    data object ConfirmRenameSnapshot : TuiEvent
    data object CancelRenameSnapshot : TuiEvent
    data class UpdateRenameInput(val value: String) : TuiEvent

    data object ToggleAsciiTree : TuiEvent
    data object ToggleDomainSelector : TuiEvent
    data class SetSelectedListIdx(val index: Int) : TuiEvent
    data class SetSelectedTreeIdx(val index: Int) : TuiEvent
    data class SetTopologyAutoScroll(val enabled: Boolean) : TuiEvent
    data class ToggleNodeExpanded(val nodeId: String) : TuiEvent
    data class SetNodeExpanded(val nodeId: String, val expanded: Boolean) : TuiEvent

    data class SetSelectedDomainIdx(val index: Int) : TuiEvent
    data class SetSelectedSettingIdx(val index: Int) : TuiEvent
    data class StartEditingSetting(val initialValue: String = "") : TuiEvent
    data object ConfirmEditingSetting : TuiEvent
    data object CancelEditingSetting : TuiEvent
    data class UpdateEditingValue(val value: String) : TuiEvent
    data object IncrementSettingsVersion : TuiEvent

    data object StartDatasetDownload : TuiEvent
    data class DatasetDownloadProgress(
        val progress: Float,
        val statusText: String
    ) : TuiEvent
    data object DatasetDownloadCompleted : TuiEvent
    data class DatasetDownloadFailed(val message: String) : TuiEvent

    data class SetInspectorScroll(val offset: Int) : TuiEvent
    data class SetMetricsScroll(val offset: Int) : TuiEvent
    data class SetLogsScroll(val offset: Int) : TuiEvent

    data object StartBatchGeneralityInput : TuiEvent
    data class UpdateBatchGeneralityInput(val value: String) : TuiEvent
    data class SetBatchReplaceExisting(val value: Boolean) : TuiEvent
    data object CancelBatchGeneralityInput : TuiEvent
    data object ConfirmBatchGeneralityInput : TuiEvent

    data object StartArenaFlow : TuiEvent
    data class UpdateArenaQueryInput(val value: String) : TuiEvent
    data class UpdateArenaModelAInput(val value: String) : TuiEvent
    data class UpdateArenaModelBInput(val value: String) : TuiEvent
    data object ConfirmArenaQueryInput : TuiEvent
    data object ConfirmArenaModelAInput : TuiEvent
    data object ConfirmArenaModelBInput : TuiEvent
    data object CancelArenaInput : TuiEvent

    data object StartTrickleFlow : TuiEvent
    data class UpdateTrickleQueryInput(val value: String) : TuiEvent
    data object ConfirmTrickleQueryInput : TuiEvent
    data object CancelTrickleInput : TuiEvent
    data class SetViewingBatchTrickleResults(val value: Boolean) : TuiEvent
    data class SetBatchTrickleScrollOffset(val offset: Int) : TuiEvent

    data class SetSelectedBenchmarkField(val index: Int) : TuiEvent
    data object StartEditingBenchmarkField : TuiEvent
    data object ConfirmEditingBenchmarkField : TuiEvent
    data object CancelEditingBenchmarkField : TuiEvent
    data class UpdateBenchmarkEditingValue(val value: String) : TuiEvent
    data class SetBenchmarkScrollOffset(val offset: Int) : TuiEvent
    data class SetBenchmarkSubScreen(val subScreen: BenchmarkSubScreen) : TuiEvent
    data class SetEvalLoaderFieldIdx(val index: Int) : TuiEvent
    data class SetEvalLoaderEditing(val editing: Boolean) : TuiEvent
    data class UpdateEvalLoaderEditValue(val value: String) : TuiEvent
    data class UpdateEvalLoaderModelInput(val value: String) : TuiEvent
    data class UpdateEvalLoaderPathInput(val value: String) : TuiEvent
    data class SetEvalLoaderRunning(val running: Boolean) : TuiEvent
    data class SetEvalLoaderStatus(val status: String) : TuiEvent
}

enum class MouseButton {
    Left,
    Right,
    Middle
}

enum class WheelDirection {
    Up,
    Down
}