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

    /** User asked to quit the whole TUI (Ctrl-C, Ctrl-Q, or the quit hotkey). */
    data object QuitRequested : TuiEvent

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

    /** Show/hide the global keyboard-reference overlay (the "?" hotkey). */
    data object ToggleHelpOverlay : TuiEvent

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

    data object ToggleDomainSelector : TuiEvent
    data class SetSelectedListIdx(val index: Int) : TuiEvent
    data class SetSelectedTreeIdx(val index: Int) : TuiEvent
    data class SetTopologyAutoScroll(val enabled: Boolean) : TuiEvent
    data class ToggleNodeExpanded(val nodeId: String) : TuiEvent
    data class SetNodeExpanded(val nodeId: String, val expanded: Boolean) : TuiEvent

    data class SetSelectedDomainIdx(val index: Int) : TuiEvent
    data class SetSelectedSettingIdx(val index: Int) : TuiEvent
    /** Toggle a dataset domain on/off (Space/Enter in the DOMAINS panel). */
    data class ToggleSelectedDomain(val domainName: String) : TuiEvent
    /** Space/Enter on a setting: instant toggle/cycle, or open the editor pre-filled. */
    data object ActivateSelectedSetting : TuiEvent
    data class StartEditingSetting(val initialValue: String = "") : TuiEvent
    /** Apply a confirmed editor value to the named setting. */
    data class ApplySetting(val name: String, val value: String) : TuiEvent
    data object ConfirmEditingSetting : TuiEvent
    data object CancelEditingSetting : TuiEvent
    data class UpdateEditingValue(val value: String) : TuiEvent
    data object IncrementSettingsVersion : TuiEvent

    // Download is a two-step flow: prompt for a query count (blank = full dataset),
    // then start the actual download with that count.
    // Seeds runtime.isDatasetDownloaded from the on-disk dataset cache at startup.
    data object RefreshDatasetStatus : TuiEvent
    data object RefreshArenaModels : TuiEvent
    data class DatasetStatusLoaded(val downloaded: Boolean) : TuiEvent
    data object PromptDatasetDownload : TuiEvent
    data class UpdateDownloadCountInput(val value: String) : TuiEvent
    data object CancelDatasetDownload : TuiEvent
    data class StartDatasetDownload(val maxQueries: Int) : TuiEvent
    data class DatasetDownloadProgress(
        val progress: Float,
        val statusText: String
    ) : TuiEvent
    data object DatasetDownloadCompleted : TuiEvent
    data class DatasetDownloadFailed(val message: String) : TuiEvent

    /** Generate a brand-new taxonomy DAG from the configured dataset/domains. */
    data object StartGeneration : TuiEvent
    /** Cancel an in-flight generation or download. */
    data object CancelGeneration : TuiEvent
    data class GenerationProgress(
        val progress: Float,
        val statusText: String
    ) : TuiEvent
    data object GenerationCompleted : TuiEvent
    data class GenerationFailed(val message: String) : TuiEvent

    data class SetInspectorScroll(val offset: Int) : TuiEvent
    data class SetMetricsScroll(val offset: Int) : TuiEvent
    data class SetLogsScroll(val offset: Int) : TuiEvent

    // 3-zone METRICS view navigation.
    data class SetMetricsIterationIndex(val index: Int) : TuiEvent
    data class SetMetricsZoneFocus(val focus: taxonomy.tui.state.MetricsZoneFocus) : TuiEvent
    data object ToggleMetricsPerformance : TuiEvent
    data class SetMetricsDetailScroll(val offset: Int) : TuiEvent

    data object StartBatchGeneralityInput : TuiEvent
    data class UpdateBatchGeneralityInput(val value: String) : TuiEvent
    data class SetBatchReplaceExisting(val value: Boolean) : TuiEvent
    data object CancelBatchGeneralityInput : TuiEvent
    data object ConfirmBatchGeneralityInput : TuiEvent

    /** Track in-flight single-node judge generation (R in NODE_DETAIL). */
    data class SetGeneratingJudge(val value: Boolean) : TuiEvent

    data object StartArenaFlow : TuiEvent
    data class ArenaModelsLoaded(val models: List<String>) : TuiEvent
    data class SetArenaUsePrecomputed(val value: Boolean) : TuiEvent
    data class UpdateArenaQuestionIdInput(val value: String) : TuiEvent
    data object ConfirmArenaQuestionIdInput : TuiEvent
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
    /** Run a single trickle query against the live taxonomy; results land via [TrickleResultReceived]. */
    data class TrickleResultReceived(val nodes: List<taxonomy.service.QueryResponseNode>) : TuiEvent
    /** Run the full batch trickle test (the "B" hotkey under the TRICKLE benchmark type). */
    data object RunBatchTrickleTest : TuiEvent
    data class BatchTrickleProgress(val text: String) : TuiEvent
    data class BatchTrickleCompleted(val results: taxonomy.tui.BatchTrickleTestResults) : TuiEvent

    data object StartBenchmarkFlow : TuiEvent
    /** Pick an evaluation type on the Benchmark hub selection screen. */
    data class SetBenchmarkType(val type: taxonomy.tui.state.BenchmarkType) : TuiEvent
    /** Move the W/S cursor on the Benchmark hub selection screen. */
    data class SetBenchmarkTypeSelectionIndex(val index: Int) : TuiEvent
    /** Return to the Benchmark hub selection screen (ESC from a chosen type). */
    data object ResetBenchmarkType : TuiEvent
    data object RunBenchmark : TuiEvent
    data object RunEvalLoad : TuiEvent
    /** Live per-question progress streamed from a running benchmark. */
    data class BenchmarkLiveUpdate(val stats: taxonomy.model.BenchmarkLiveStats) : TuiEvent
    /** Auto-download the MMLU-Pro eval_results cache from GitHub (the "d" key inside the picker). */
    data object DownloadEvalResults : TuiEvent

    // ── Per-model eval ingestion picker (the "o" hotkey in Arena/Benchmark) ──
    /** Re-scan the eval_results cache directory (no parsing); result lands via [EvalCatalogLoaded]. */
    data object RefreshEvalCatalog : TuiEvent
    /** Open the picker overlay and trigger a fresh scan. */
    data object OpenEvalCatalogPicker : TuiEvent
    data object CloseEvalCatalogPicker : TuiEvent
    data class EvalCatalogLoaded(val entries: List<taxonomy.dataset.EvalCatalogEntry>) : TuiEvent
    data class MoveEvalCatalogCursor(val delta: Int) : TuiEvent
    data object ToggleEvalCatalogSelection : TuiEvent
    data object SelectAllNonIngestedEntries : TuiEvent
    /** Confirm the picked models; the CommandController fires the ingestion side-effect. */
    data object ConfirmEvalCatalogSelection : TuiEvent
    data class EvalIngestionProgress(
        val modelIdx: Int,
        val modelCount: Int,
        val modelName: String,
        val item: Int,
        val itemTotal: Int
    ) : TuiEvent
    data object EvalIngestionComplete : TuiEvent
    data class EvalDownloadProgress(
        val fileName: String,
        val bytesDownloaded: Long,
        val totalBytes: Long
    ) : TuiEvent
    data object EvalDownloadComplete : TuiEvent
    /** Toggle the Arena leaderboard sub-view (the "l" hotkey while in Arena mode). */
    data object ToggleLeaderboard : TuiEvent
    data class SetLeaderboardScrollOffset(val offset: Int) : TuiEvent
    data class LeaderboardLoaded(val groups: List<taxonomy.service.LeaderboardGroup>) : TuiEvent
    data class BenchmarkModelsLoaded(val models: List<String>) : TuiEvent
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