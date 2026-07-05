package taxonomy.tui.controller.keys

import taxonomy.service.AnalysisMode
import taxonomy.tui.controller.CommandController
import taxonomy.tui.controller.FocusController
import taxonomy.tui.controller.TuiEffects
import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.state.BenchmarkType
import taxonomy.tui.state.BenchmarkSubScreen
import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.TuiAppState

/**
 * Handles top-level keyboard input while the MAINDASHBOARD screen is active.
 *
 * Global hotkeys (M, A, B, T, G, F, N, X, Tab) are handled here; all others
 * are routed to the focused-panel sub-handler.
 */
internal class MainDashboardKeyHandler(
    private val effects: TuiEffects,
    private val commandController: CommandController,
    private val focusController: FocusController,
    private val configHandler: ConfigKeyHandler,
    private val topologyHandler: TopologyKeyHandler,
    private val analysisHandler: AnalysisKeyHandler,
) {

    fun handle(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        if ((state.benchmark.benchmarkIsPickingModels || state.benchmark.benchmarkIsPickingDomains) &&
            state.shell.focusedPanel == FocusPanel.TOPOLOGY) {
            analysisHandler.handleBenchmarkPickerKeys(state, key, dispatch)
            return
        }

        // Modal overlays take priority.
        if (state.benchmark.isPickingEvalCatalog) {
            analysisHandler.handleEvalCatalogPickerKeys(state, key, dispatch)
            return
        }

        if (analysisHandler.isTextInputActive(state)) {
            analysisHandler.handleActiveTextInput(state, key, dispatch)
            return
        }

        // Cancellable operations.
        val canCancel = state.runtime.isRegenerating ||
            state.benchmark.isRunningBatchTrickleTest ||
            state.benchmark.isDownloadingEval
        if (canCancel && (key == "escape" || key == "c")) {
            dispatch(TuiEvent.CancelGeneration)
            return
        }

        when (key) {
            "tab" -> dispatch(focusController.cycleForward(state))

            "x"   -> dispatch(TuiEvent.ReturnToWelcome)

            "m"   -> dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.METRICS))

            "c"   -> {
                val nextMode = if (state.analysis.mode == AnalysisMode.CONFIG) AnalysisMode.IDLE else AnalysisMode.CONFIG
                dispatch(TuiEvent.SetAnalysisMode(nextMode))
            }

            "a"   -> {
                effects.loadArenaModels(dispatch)
                if (state.arena.loadedModels.isNotEmpty()) {
                    commandController.startArena(dispatch)
                } else {
                    dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.ARENA))
                }
            }

            "b"   -> commandController.startBenchmark(dispatch)

            "t"   -> commandController.startTrickle(dispatch)

            "g", "G" -> {
                dispatch(TuiEvent.SetBatchReplaceExisting(false))
                dispatch(TuiEvent.StartBatchGeneralityInput)
            }

            "f", "F" -> {
                dispatch(TuiEvent.SetBatchReplaceExisting(true))
                dispatch(TuiEvent.StartBatchGeneralityInput)
            }

            "p", "P" -> {
                val targetMode = when {
                    state.analysis.isJudgeGenerationRunning -> AnalysisMode.JUDGE_PROGRESS
                    state.benchmark.benchmarkType != BenchmarkType.NONE || state.benchmark.evalLoaderIsRunning -> AnalysisMode.BENCHMARK
                    state.benchmark.isRunningBatchTrickleTest -> AnalysisMode.TRICKLE_TEST
                    else -> null
                }
                if (targetMode != null) {
                    dispatch(TuiEvent.SetAnalysisMode(targetMode))
                }
            }

            "n"   -> {
                if (state.snapshot.isViewingSnapshot && state.snapshot.activeSnapshotId != null) {
                    dispatch(TuiEvent.StartRenameSnapshot)
                }
            }

            "o"   -> if (
                state.analysis.mode == AnalysisMode.BENCHMARK ||
                state.analysis.mode == AnalysisMode.ARENA
            ) {
                dispatch(TuiEvent.OpenEvalCatalogPicker)
            } else {
                routeByPanel(state, key, dispatch)
            }

            "l", "L"   -> {
                if (state.analysis.mode == AnalysisMode.BENCHMARK &&
                    state.benchmark.benchmarkType == BenchmarkType.ARENA &&
                    state.benchmark.benchmarkSubScreen == BenchmarkSubScreen.CONFIG
                ) {
                    routeByPanel(state, key, dispatch)
                } else {
                    if (state.analysis.mode == AnalysisMode.LEADERBOARD) {
                        dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
                    } else {
                        dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.LEADERBOARD))
                        effects.loadLeaderboard(dispatch)
                    }
                }
            }

            else  -> routeByPanel(state, key, dispatch)
        }
    }

    private fun routeByPanel(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (state.shell.focusedPanel) {
            FocusPanel.TOPOLOGY      -> topologyHandler.handle(state, key, dispatch)
            FocusPanel.ANALYSIS_HUB  -> analysisHandler.handle(state, key, dispatch)
            FocusPanel.SYSTEM_LOGS   -> analysisHandler.handleLogsKeys(state, key, dispatch)
            FocusPanel.PROCESSES     -> Unit
            FocusPanel.CONFIG        -> configHandler.handle(state, key, dispatch)
        }
    }
}
