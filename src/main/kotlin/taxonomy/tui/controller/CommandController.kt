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
                effects.saveSnapshot(state.snapshot.snapshotDescInput, dispatch)
            }

            TuiEvent.ConfirmRenameSnapshot -> {
                val id = state.snapshot.activeSnapshotId ?: return
                effects.renameSnapshot(id, state.snapshot.renameInput, dispatch)
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
                if (state.arena.usePrecomputed) {
                    val qId = state.arena.arenaQuestionIdInput.trim().toIntOrNull()
                    if (qId != null) {
                        effects.runArenaPrecomputed(
                            questionId = qId,
                            modelA = state.arena.arenaModelAInput,
                            modelB = state.arena.arenaModelBInput
                        )
                    }
                } else {
                    effects.runArena(
                        query = state.arena.arenaQueryInput,
                        modelA = state.arena.arenaModelAInput,
                        modelB = state.arena.arenaModelBInput
                    )
                }
            }

            TuiEvent.RunBenchmark -> {
                val models = state.benchmark.benchmarkModelsInput
                    .split(",").map { it.trim() }.filter { it.isNotBlank() }
                    .ifEmpty { state.benchmark.loadedModels }
                effects.runBenchmarkConfigured(
                    models = models,
                    queryLimit = state.benchmark.benchmarkQueryLimitInput.trim().toIntOrNull() ?: 0,
                    category = state.benchmark.benchmarkCategoryInput.trim().ifBlank { null },
                    confidenceGate = state.benchmark.benchmarkConfidenceGateInput.trim().toDoubleOrNull() ?: 0.65,
                    parallelism = state.benchmark.benchmarkParallelismInput.trim().toIntOrNull() ?: 4,
                    updateRankings = state.benchmark.benchmarkUpdateRankingsInput.trim().toBooleanStrictOrNull() ?: true
                )
            }

            TuiEvent.RunEvalLoad -> {
                if (state.benchmark.evalLoaderPathInput.isNotBlank()) {
                    effects.loadEval(
                        path = state.benchmark.evalLoaderPathInput.trim(),
                        modelName = state.benchmark.evalLoaderModelInput.trim(),
                        dispatch = dispatch
                    )
                }
            }

            TuiEvent.ConfirmTrickleQueryInput -> {
                if (state.trickle.trickleQueryInput.isNotBlank()) {
                    effects.runTrickle(state.trickle.trickleQueryInput)
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
        effects.loadArenaModels(dispatch)
        dispatch(TuiEvent.StartArenaFlow)
    }

    fun startTrickle(dispatch: (TuiEvent) -> Unit) {
        dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.TRICKLE_TEST))
        dispatch(TuiEvent.StartTrickleFlow)
    }

    fun startBenchmark(dispatch: (TuiEvent) -> Unit) {
        dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.BENCHMARK))
        dispatch(TuiEvent.StartBenchmarkFlow)
        effects.loadBenchmarkModels(dispatch)
    }

    fun startMetrics(dispatch: (TuiEvent) -> Unit) {
        dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.METRICS))
    }

    fun startSnapshots(dispatch: (TuiEvent) -> Unit) {
        dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.SNAPSHOTS))
    }
}