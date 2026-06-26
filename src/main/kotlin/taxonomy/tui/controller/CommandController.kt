package taxonomy.tui.controller

import taxonomy.service.AnalysisMode
import taxonomy.tui.state.TuiAppState

class CommandController(
    private val effects: TuiEffects
) {

    fun handle(state: TuiAppState, event: TuiEvent, dispatch: (TuiEvent) -> Unit) {
        when (event) {
            TuiEvent.RefreshSnapshots -> {
                effects.refreshSnapshots(dispatch)
            }

            TuiEvent.ConfirmSaveSnapshot -> {
                effects.saveSnapshot(state.snapshots.snapshotDescInput, dispatch)
            }

            TuiEvent.ConfirmRenameSnapshot -> {
                val id = state.snapshots.activeSnapshotId ?: return
                effects.renameSnapshot(id, state.snapshots.renameInput, dispatch)
            }

            is TuiEvent.RequestLoadSnapshot -> {
                effects.loadSnapshot(event.snapshotId, dispatch)
            }

            is TuiEvent.RequestDeleteSnapshot -> {
                effects.deleteSnapshot(event.snapshotId, dispatch)
            }

            TuiEvent.StartDatasetDownload -> {
                effects.downloadDataset(dispatch)
            }

            TuiEvent.ConfirmBatchGeneralityInput -> {
                val generality = state.analysis.batchGeneralityInput.toIntOrNull() ?: 1
                effects.runBatchJudge(generality, state.analysis.batchReplaceExisting)
            }

            TuiEvent.ConfirmArenaModelBInput -> {
                effects.runArena(
                    query = state.analysis.arenaQueryInput,
                    modelA = state.analysis.arenaModelAInput,
                    modelB = state.analysis.arenaModelBInput
                )
            }

            TuiEvent.ConfirmTrickleQueryInput -> {
                if (state.analysis.trickleQueryInput.isNotBlank()) {
                    effects.runTrickle(state.analysis.trickleQueryInput)
                }
            }

            is TuiEvent.KeyPressed -> {
                when (event.key.lowercase()) {
                    "e" -> effects.exportAscii()
                    "l" -> effects.regenerateLabels()
                    "r" -> effects.regenerateJudgeForCurrentNode()
                    else -> Unit
                }
            }

            else -> Unit
        }
    }

    fun startArena(dispatch: (TuiEvent) -> Unit) {
        dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.ARENA))
        dispatch(TuiEvent.StartArenaFlow)
    }

    fun startTrickle(dispatch: (TuiEvent) -> Unit) {
        dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.TRICKLETEST))
        dispatch(TuiEvent.StartTrickleFlow)
    }

    fun startBenchmark(dispatch: (TuiEvent) -> Unit) {
        dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.BENCHMARK))
    }

    fun startMetrics(dispatch: (TuiEvent) -> Unit) {
        dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.METRICS))
    }

    fun startSnapshots(dispatch: (TuiEvent) -> Unit) {
        dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.SNAPSHOTS))
    }
}