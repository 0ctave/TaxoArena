package taxonomy.tui.controller

import taxonomy.service.AnalysisMode
import taxonomy.tui.components.SettingItem
import taxonomy.tui.state.ConfigSubPanel
import taxonomy.tui.state.TuiAppState

class CommandController(
    private val effects: TuiEffects,
    /** Provides the current setting items so instant toggles/edits resolve by index. */
    private val settingItemsProvider: () -> List<SettingItem> = { emptyList() },
    private val configProvider: () -> taxonomy.config.TaxonomyConfig? = { null }
) {

    private fun selectedSetting(state: TuiAppState): SettingItem? =
        settingItemsProvider().getOrNull(state.config.selectedSettingIdx)

    fun handle(state: TuiAppState, event: TuiEvent, dispatch: (TuiEvent) -> Unit) {
        when (event) {
            TuiEvent.RefreshSnapshots -> {
                effects.refreshSnapshots(dispatch)
            }

            TuiEvent.RefreshDatasetStatus -> {
                effects.refreshDatasetStatus(dispatch)
            }

            // Refreshes the precomputed eval roster (used to gate Arena/Benchmark entry).
            TuiEvent.RefreshArenaModels -> {
                effects.loadArenaModels(dispatch)
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

            is TuiEvent.StartDatasetDownload -> {
                effects.downloadDataset(event.maxQueries, dispatch)
            }

            TuiEvent.CancelGeneration -> {
                effects.cancelActiveJob()
            }

            TuiEvent.StartGeneration -> {
                effects.generateDag(dispatch)
            }

            is TuiEvent.ToggleSelectedDomain -> {
                effects.toggleDomain(event.domainName, dispatch)
            }

            TuiEvent.ActivateSelectedSetting -> {
                if (state.config.activeSubPanel == ConfigSubPanel.SETTINGS) {
                    val item = selectedSetting(state) ?: return
                    val instantValue = item.nextValue()
                    if (item.isInstant && instantValue != null) {
                        // Boolean/Select: toggle/cycle in place, no text entry.
                        effects.applySetting(item.name, instantValue, dispatch)
                    } else {
                        // Number/Text: open the editor pre-filled with the current value.
                        dispatch(TuiEvent.StartEditingSetting(item.getValue()))
                    }
                }
            }

            is TuiEvent.ApplySetting -> {
                effects.applySetting(event.name, event.value, dispatch)
            }

            TuiEvent.ConfirmBatchGeneralityInput -> {
                val generality = state.analysis.batchGeneralityInput.toIntOrNull() ?: 1
                val domains = state.analysis.batchDomainsInput
                    .split(",")
                    .map { it.trim() }
                    .filter { it.isNotBlank() }
                configProvider()?.llm?.judgeDomains = domains
                effects.runBatchJudge(generality, state.analysis.batchReplaceExisting, dispatch)
            }

            // Models-first flow: the run fires on the FINAL input. In precomputed mode that's
            // the question_id; in live mode it's the free-text query.
            TuiEvent.ConfirmArenaQuestionIdInput -> {
                val qId = state.arena.arenaQuestionIdInput.trim().toIntOrNull()
                if (qId != null) {
                    effects.runArenaPrecomputed(
                        questionId = qId,
                        modelA = state.arena.arenaModelAInput,
                        modelB = state.arena.arenaModelBInput
                    )
                }
            }

            TuiEvent.ConfirmArenaQueryInput -> {
                if (state.arena.arenaQueryInput.isNotBlank()) {
                    effects.runArena(
                        query = state.arena.arenaQueryInput,
                        modelA = state.arena.arenaModelAInput,
                        modelB = state.arena.arenaModelBInput
                    )
                }
            }

            TuiEvent.RunBenchmark -> {
                val b = state.benchmark
                val models = b.benchmarkSelectedModels.toList().ifEmpty { b.loadedModels }
                // Single selected domain → restrict to that GT category; multiple/none → all.
                val category = b.benchmarkSelectedDomains.singleOrNull()
                effects.runBenchmarkConfigured(
                    models = models,
                    queryLimit = b.benchmarkQueryLimitInput.trim().toIntOrNull() ?: 0,
                    category = category,
                    confidenceGate = b.benchmarkConfidenceGateInput.trim().toDoubleOrNull() ?: 0.65,
                    parallelism = b.benchmarkParallelismInput.trim().toIntOrNull() ?: 4,
                    updateRankings = b.benchmarkUpdateRankingsInput.trim().toBooleanStrictOrNull() ?: true,
                    reservedOnly = b.benchmarkReservedOnlyInput.trim().toBooleanStrictOrNull() ?: true,
                    dispatch = dispatch
                )
            }

            is TuiEvent.RunBatchTrickleTest -> {
                effects.runBatchTrickle(event.maxQueries, dispatch)
            }

            TuiEvent.DownloadEvalResults -> {
                effects.downloadEvalResults(dispatch)
            }

            TuiEvent.ToggleLeaderboard -> {
                effects.loadLeaderboard(dispatch)
            }

            TuiEvent.ClearLeaderboard -> {
                effects.clearLeaderboard(dispatch)
            }

            TuiEvent.EvalDownloadComplete -> {
                // The cache is now populated; re-scan the catalog so the picker reflects the
                // freshly downloaded files. Ingestion is deferred until the user picks models.
                dispatch(TuiEvent.RefreshEvalCatalog)
            }

            // Open the per-model ingestion picker: scan the cache (no parsing) then show it.
            TuiEvent.OpenEvalCatalogPicker -> {
                effects.refreshEvalCatalog(dispatch)
            }

            TuiEvent.RefreshEvalCatalog -> {
                effects.refreshEvalCatalog(dispatch)
            }

            TuiEvent.ConfirmEvalCatalogSelection -> {
                val selected = state.benchmark.evalCatalog
                    .filter { it.modelName in state.benchmark.evalCatalogSelection }
                effects.loadEvalSelected(selected, dispatch)
            }

            TuiEvent.RunEvalLoad -> {
                val path = state.benchmark.evalLoaderPathInput.trim()
                dispatch(TuiEvent.SetEvalLoaderRunning(true))
                dispatch(TuiEvent.SetEvalLoaderStatus("Loading eval_results…"))
                effects.loadEval(
                    path = path,
                    modelName = state.benchmark.evalLoaderModelInput.trim(),
                    dispatch = dispatch
                )
            }

            TuiEvent.ConfirmTrickleQueryInput -> {
                if (state.trickle.trickleQueryInput.isNotBlank()) {
                    effects.runTrickle(state.trickle.trickleQueryInput, dispatch)
                }
            }

            // Re-probe the on-disk dataset cache whenever the user enters the config screen, so
            // generation doesn't re-prompt for a download that's already present locally.
            TuiEvent.EnterConfigSetup -> {
                effects.refreshDatasetStatus(dispatch)
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
