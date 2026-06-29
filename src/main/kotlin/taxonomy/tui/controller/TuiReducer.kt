package taxonomy.tui.controller

import taxonomy.service.AnalysisMode
import taxonomy.tui.components.StartupState
import taxonomy.tui.state.ConfigSubPanel
import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.ScrollbarTarget
import taxonomy.tui.state.TuiAppState

object TuiReducer {

    fun reduce(state: TuiAppState, event: TuiEvent): TuiAppState {
        return when (event) {
            is TuiEvent.Resize ->
                state.copy(
                    shell = state.shell.copy(width = event.width, height = event.height)
                )

            TuiEvent.SpinnerTick ->
                state.copy(
                    shell = state.shell.copy(spinnerTick = state.shell.spinnerTick + 1)
                )

            TuiEvent.LogsTick,
            TuiEvent.QuitRequested -> // quit is a pure side-effect, handled in the controller
                state

            is TuiEvent.FocusPanelRequested ->
                state.copy(
                    shell = state.shell.copy(focusedPanel = event.panel)
                )

            TuiEvent.ToggleHelpOverlay ->
                state.copy(
                    shell = state.shell.copy(helpOverlayOpen = !state.shell.helpOverlayOpen)
                )

            TuiEvent.CycleFocusForward ->
                state.copy(
                    shell = state.shell.copy(
                        focusedPanel = when (state.shell.focusedPanel) {
                            FocusPanel.TOPOLOGY -> FocusPanel.ANALYSIS_HUB
                            FocusPanel.ANALYSIS_HUB -> FocusPanel.SYSTEM_LOGS
                            FocusPanel.SYSTEM_LOGS -> FocusPanel.PROCESSES
                            FocusPanel.PROCESSES -> FocusPanel.TOPOLOGY
                            FocusPanel.CONFIG -> FocusPanel.TOPOLOGY
                        }
                    )
                )

            is TuiEvent.SetStartupState ->
                state.copy(
                    startup = state.startup.copy(state = event.state)
                )

            TuiEvent.ReturnToWelcome ->
                state.copy(
                    startup = state.startup.copy(
                        state = StartupState.LOAD_DAG,
                        selectedWelcomeIdx = 0,
                        loadingSnapshotId = null
                    ),
                    shell = state.shell.copy(focusedPanel = FocusPanel.TOPOLOGY),
                    snapshot = state.snapshot.copy(activeSnapshotConfig = null)
                )

            TuiEvent.EnterConfigSetup ->
                state.copy(
                    startup = state.startup.copy(state = StartupState.CONFIGANDDOMAINS),
                    config = state.config.copy(
                        activeSubPanel = ConfigSubPanel.DOMAINS,
                        selectedDomainIdx = 0,
                        selectedSettingIdx = 0
                    ),
                    shell = state.shell.copy(focusedPanel = FocusPanel.CONFIG)
                )

            TuiEvent.EnterMainDashboard ->
                state.copy(
                    startup = state.startup.copy(state = StartupState.MAINDASHBOARD),
                    shell = state.shell.copy(focusedPanel = FocusPanel.TOPOLOGY)
                )

            is TuiEvent.SetAnalysisMode ->
                state.copy(
                    analysis = state.analysis.copy(mode = event.mode),
                    shell = state.shell.copy(focusedPanel = FocusPanel.ANALYSIS_HUB)
                )

            is TuiEvent.SetConfigSubPanel ->
                state.copy(
                    config = state.config.copy(activeSubPanel = event.panel)
                )

            is TuiEvent.StartDraggingScrollbar ->
                state.copy(
                    shell = state.shell.copy(draggingScrollbar = event.target)
                )

            TuiEvent.StopDraggingScrollbar ->
                state.copy(
                    shell = state.shell.copy(draggingScrollbar = null)
                )

            is TuiEvent.ScrollTo ->
                applyScrollTo(state, event.target, event.offset)

            is TuiEvent.ScrollBy ->
                applyScrollBy(state, event.target, event.delta)

            TuiEvent.RefreshSnapshots,
            TuiEvent.RefreshDatasetStatus,
            TuiEvent.RefreshArenaModels ->
                state

            // Side-effect-only config events (handled in CommandController).
            is TuiEvent.ToggleSelectedDomain,
            TuiEvent.ActivateSelectedSetting,
            is TuiEvent.ApplySetting ->
                state

            is TuiEvent.SnapshotsLoaded -> {
                val snapshots = event.snapshots
                val safeSelectedSnapshotIdx =
                    if (snapshots.isEmpty()) 0
                    else state.snapshot.selectedSnapshotIdx.coerceIn(0, snapshots.lastIndex)

                val welcomeOptionsCount = 1 + snapshots.size
                val safeWelcomeIdx =
                    state.startup.selectedWelcomeIdx
                        .coerceIn(0, (welcomeOptionsCount - 1).coerceAtLeast(0))

                // The snapshot list is the data the welcome screen needs; once it has
                // arrived, leave the initial LOADING screen for WELCOME.
                val nextStartupState =
                    if (state.startup.state == StartupState.LOADING) StartupState.LOAD_DAG
                    else state.startup.state

                state.copy(
                    snapshot = state.snapshot.copy(
                        snapshotList = snapshots,
                        selectedSnapshotIdx = safeSelectedSnapshotIdx
                    ),
                    startup = state.startup.copy(
                        selectedWelcomeIdx = safeWelcomeIdx,
                        state = nextStartupState
                    )
                )
            }

            is TuiEvent.SelectWelcomeIndex ->
                state.copy(
                    startup = state.startup.copy(
                        selectedWelcomeIdx = event.index.coerceAtLeast(0)
                    )
                )

            is TuiEvent.SelectSnapshotIndex -> {
                val maxIdx = (state.snapshot.snapshotList.size - 1).coerceAtLeast(0)
                state.copy(
                    snapshot = state.snapshot.copy(
                        selectedSnapshotIdx = event.index.coerceIn(0, maxIdx)
                    )
                )
            }

            TuiEvent.StartSaveSnapshot ->
                state.copy(
                    analysis = state.analysis.copy(mode = AnalysisMode.SNAPSHOTS),
                    shell = state.shell.copy(focusedPanel = FocusPanel.ANALYSIS_HUB),
                    snapshot = state.snapshot.copy(
                        isSavingSnapshot = true,
                        snapshotDescInput = "",
                        isRenamingSnapshot = false,
                        renameInput = ""
                    )
                )

            TuiEvent.ConfirmSaveSnapshot,
            TuiEvent.CancelSaveSnapshot ->
                state.copy(
                    snapshot = state.snapshot.copy(
                        isSavingSnapshot = false,
                        snapshotDescInput = ""
                    )
                )

            is TuiEvent.UpdateSnapshotDescInput ->
                state.copy(
                    snapshot = state.snapshot.copy(snapshotDescInput = event.value)
                )

            TuiEvent.StartRenameSnapshot ->
                state.copy(
                    analysis = state.analysis.copy(mode = AnalysisMode.SNAPSHOTS),
                    shell = state.shell.copy(focusedPanel = FocusPanel.ANALYSIS_HUB),
                    snapshot = state.snapshot.copy(
                        isRenamingSnapshot = true,
                        renameInput = state.snapshot.activeSnapshotDescription.orEmpty(),
                        isSavingSnapshot = false,
                        snapshotDescInput = ""
                    )
                )

            TuiEvent.ConfirmRenameSnapshot,
            TuiEvent.CancelRenameSnapshot ->
                state.copy(
                    snapshot = state.snapshot.copy(
                        isRenamingSnapshot = false,
                        renameInput = ""
                    )
                )

            is TuiEvent.UpdateRenameInput ->
                state.copy(
                    snapshot = state.snapshot.copy(renameInput = event.value)
                )

            is TuiEvent.RequestLoadSnapshot ->
                state.copy(
                    startup = state.startup.copy(
                        state = StartupState.LOADING,
                        loadingSnapshotId = event.snapshotId
                    )
                )

            is TuiEvent.SnapshotLoaded -> {
                // Resolve the embedded EffectiveConfig from the snapshot list so the
                // CONFIG panel can display the generation parameters without an extra
                // service call. Falls back to null for legacy snapshots (pre-config field).
                val loadedConfig = state.snapshot.snapshotList
                    .firstOrNull { it.id == event.snapshotId }
                    ?.config

                state.copy(
                    startup = state.startup.copy(
                        state = StartupState.MAINDASHBOARD,
                        loadingSnapshotId = null
                    ),
                    shell = state.shell.copy(focusedPanel = FocusPanel.TOPOLOGY),
                    snapshot = state.snapshot.copy(
                        isViewingSnapshot = true,
                        activeSnapshotId = event.snapshotId,
                        activeSnapshotDescription = event.description,
                        activeSnapshotConfig = loadedConfig,
                        isSavingSnapshot = false,
                        snapshotDescInput = "",
                        isRenamingSnapshot = false,
                        renameInput = ""
                    )
                )
            }

            is TuiEvent.SnapshotLoadFailed ->
                state.copy(
                    startup = state.startup.copy(
                        state = StartupState.LOAD_DAG,
                        loadingSnapshotId = null
                    )
                )

            is TuiEvent.RequestDeleteSnapshot ->
                state


            TuiEvent.ToggleDomainSelector ->
                state.copy(
                    topology = state.topology.copy(
                        showDomainSelector = !state.topology.showDomainSelector
                    )
                )

            is TuiEvent.SetSelectedListIdx ->
                state.copy(
                    topology = state.topology.copy(
                        selectedListIdx = event.index.coerceAtLeast(0)
                    )
                )

            is TuiEvent.SetSelectedTreeIdx ->
                state.copy(
                    topology = state.topology.copy(
                        selectedTreeIdx = event.index.coerceAtLeast(0)
                    )
                )

            is TuiEvent.SetTopologyAutoScroll ->
                state.copy(
                    topology = state.topology.copy(autoScroll = event.enabled)
                )

            is TuiEvent.ToggleNodeExpanded -> {
                val current = state.topology.expandedNodes[event.nodeId] ?: false
                state.copy(
                    topology = state.topology.copy(
                        expandedNodes = state.topology.expandedNodes + (event.nodeId to !current)
                    )
                )
            }

            is TuiEvent.SetNodeExpanded ->
                state.copy(
                    topology = state.topology.copy(
                        expandedNodes = state.topology.expandedNodes + (event.nodeId to event.expanded)
                    )
                )

            is TuiEvent.SetSelectedDomainIdx ->
                state.copy(
                    config = state.config.copy(
                        selectedDomainIdx = event.index.coerceAtLeast(0)
                    )
                )

            is TuiEvent.SetSelectedSettingIdx ->
                state.copy(
                    config = state.config.copy(
                        selectedSettingIdx = event.index.coerceAtLeast(0)
                    )
                )

            is TuiEvent.StartEditingSetting ->
                state.copy(
                    config = state.config.copy(
                        isEditingSetting = true,
                        editingValue = event.initialValue
                    )
                )

            TuiEvent.ConfirmEditingSetting,
            TuiEvent.CancelEditingSetting ->
                state.copy(
                    config = state.config.copy(
                        isEditingSetting = false,
                        editingValue = ""
                    )
                )

            is TuiEvent.UpdateEditingValue ->
                state.copy(
                    config = state.config.copy(editingValue = event.value)
                )

            TuiEvent.IncrementSettingsVersion ->
                state.copy(
                    config = state.config.copy(
                        settingsVersion = state.config.settingsVersion + 1
                    )
                )

            is TuiEvent.DatasetStatusLoaded ->
                state.copy(runtime = state.runtime.copy(isDatasetDownloaded = event.downloaded))

            TuiEvent.PromptDatasetDownload ->
                state.copy(
                    config = state.config.copy(
                        promptingDownloadCount = true,
                        downloadCountInput = ""
                    )
                )

            is TuiEvent.UpdateDownloadCountInput ->
                state.copy(
                    // Digits only; blank is allowed and means "full dataset".
                    config = state.config.copy(
                        downloadCountInput = event.value.filter { it.isDigit() }.take(7)
                    )
                )

            TuiEvent.CancelDatasetDownload ->
                state.copy(
                    config = state.config.copy(
                        promptingDownloadCount = false,
                        downloadCountInput = ""
                    )
                )

            is TuiEvent.StartDatasetDownload ->
                state.copy(
                    config = state.config.copy(
                        promptingDownloadCount = false,
                        downloadCountInput = "",
                        downloadingDataset = true,
                        datasetDownloadProgress = 0f,
                        datasetDownloadStatusText =
                            if (event.maxQueries <= 0) "Initializing full download..."
                            else "Initializing download of ${event.maxQueries} queries..."
                    )
                )

            is TuiEvent.DatasetDownloadProgress ->
                state.copy(
                    config = state.config.copy(
                        datasetDownloadProgress = event.progress,
                        datasetDownloadStatusText = event.statusText
                    )
                )

            TuiEvent.DatasetDownloadCompleted ->
                state.copy(
                    config = state.config.copy(
                        downloadingDataset = false,
                        datasetDownloadProgress = 1f
                    ),
                    runtime = state.runtime.copy(isDatasetDownloaded = true)
                )

            is TuiEvent.DatasetDownloadFailed ->
                state.copy(
                    config = state.config.copy(
                        downloadingDataset = false,
                        datasetDownloadStatusText = event.message
                    )
                )

            TuiEvent.CancelGeneration ->
                state.copy(
                    config = state.config.copy(
                        downloadingDataset = false,
                        generationStatusText = "Cancelled"
                    ),
                    runtime = state.runtime.copy(isRegenerating = false),
                    benchmark = state.benchmark.copy(
                        isRunningBatchTrickleTest = false,
                        batchTrickleProgress = "Cancelled",
                        isDownloadingEval = false
                    )
                )

            TuiEvent.StartGeneration ->
                state.copy(
                    // Jump to the dashboard so the DAG Explorer streams the live evolution as
                    // the engine builds it (graphVersion bumps drive the rebuild). Progress is
                    // surfaced by the pinned banner + the Processes panel.
                    startup = state.startup.copy(state = StartupState.MAINDASHBOARD),
                    shell = state.shell.copy(focusedPanel = FocusPanel.TOPOLOGY),
                    config = state.config.copy(generationStatusText = "Preparing dataset..."),
                    runtime = state.runtime.copy(isRegenerating = true)
                )

            is TuiEvent.GenerationProgress ->
                state.copy(
                    config = state.config.copy(generationStatusText = event.statusText)
                )

            TuiEvent.GenerationCompleted ->
                state.copy(
                    startup = state.startup.copy(state = StartupState.MAINDASHBOARD),
                    shell = state.shell.copy(focusedPanel = FocusPanel.TOPOLOGY),
                    config = state.config.copy(generationStatusText = ""),
                    runtime = state.runtime.copy(isRegenerating = false, hasActiveGraph = true)
                )

            is TuiEvent.SnapshotAutoSaved ->
                state.copy(
                    snapshot = state.snapshot.copy(
                        lastAutoSaveMessage =
                            if (event.success) "Snapshot saved: ${event.description}"
                            else "Auto-save failed: ${event.description}"
                    )
                )

            is TuiEvent.GenerationFailed ->
                state.copy(
                    config = state.config.copy(
                        generationStatusText = event.message
                    ),
                    runtime = state.runtime.copy(isRegenerating = false)
                )

            is TuiEvent.SetInspectorScroll ->
                state.copy(
                    analysis = state.analysis.copy(
                        inspectorScroll = event.offset.coerceAtLeast(0)
                    )
                )

            is TuiEvent.SetMetricsScroll ->
                state.copy(
                    analysis = state.analysis.copy(
                        metricsScrollOffset = event.offset.coerceAtLeast(0)
                    )
                )

            // -1 selects the Final/last entry; any non-negative value selects that iteration row.
            is TuiEvent.SetMetricsIterationIndex ->
                state.copy(
                    analysis = state.analysis.copy(
                        selectedIterationIndex = event.index.coerceAtLeast(-1),
                        detailScrollOffset = 0
                    )
                )

            is TuiEvent.SetMetricsZoneFocus ->
                state.copy(
                    analysis = state.analysis.copy(metricsZoneFocus = event.focus)
                )

            is TuiEvent.ToggleMetricsPerformance ->
                state.copy(
                    analysis = state.analysis.copy(
                        showPerformanceBlock = !state.analysis.showPerformanceBlock
                    )
                )

            is TuiEvent.SetMetricsDetailScroll ->
                state.copy(
                    analysis = state.analysis.copy(
                        detailScrollOffset = event.offset.coerceAtLeast(0)
                    )
                )

            is TuiEvent.SetLogsScroll ->
                state.copy(
                    logs = state.logs.copy(
                        logScrollOffset = event.offset.coerceAtLeast(0)
                    )
                )

            TuiEvent.StartBatchGeneralityInput ->
                state.copy(
                    analysis = state.analysis.copy(
                        mode = AnalysisMode.JUDGE_PROGRESS,
                        isEnteringBatchGenerality = true,
                        batchGeneralityInput = "1"
                    ),
                    shell = state.shell.copy(focusedPanel = FocusPanel.ANALYSIS_HUB)
                )

            is TuiEvent.UpdateBatchGeneralityInput ->
                state.copy(
                    analysis = state.analysis.copy(batchGeneralityInput = event.value)
                )

            is TuiEvent.SetBatchReplaceExisting ->
                state.copy(
                    analysis = state.analysis.copy(batchReplaceExisting = event.value)
                )

            TuiEvent.CancelBatchGeneralityInput ->
                state.copy(
                    analysis = state.analysis.copy(
                        isEnteringBatchGenerality = false,
                        batchGeneralityInput = "1",
                        batchReplaceExisting = false
                    )
                )

            TuiEvent.ConfirmBatchGeneralityInput ->
                state.copy(
                    analysis = state.analysis.copy(
                        isEnteringBatchGenerality = false
                    )
                )

            TuiEvent.StartArenaFlow -> {
                val roster = state.arena.loadedModels
                val defaultA = state.arena.arenaModelAInput.ifBlank { roster.getOrNull(0).orEmpty() }
                val defaultB = state.arena.arenaModelBInput.ifBlank { roster.getOrNull(1).orEmpty() }
                // Models-first flow: pick Model A -> Model B -> (precomputed) question_id.
                state.copy(
                    analysis = state.analysis.copy(mode = AnalysisMode.ARENA),
                    arena = state.arena.copy(
                        isEnteringArenaModelA = true,
                        isEnteringArenaModelB = false,
                        isEnteringArenaQuestionId = false,
                        arenaQuestionIdInput = "",
                        isEnteringArenaQuery = false,
                        arenaQueryInput = "",
                        arenaModelAInput = defaultA,
                        arenaModelBInput = defaultB
                    ),
                    shell = state.shell.copy(focusedPanel = FocusPanel.ANALYSIS_HUB)
                )
            }

            is TuiEvent.SetGeneratingJudge ->
                state.copy(arena = state.arena.copy(isGeneratingJudge = event.value))

            is TuiEvent.ArenaModelsLoaded ->
                state.copy(arena = state.arena.copy(loadedModels = event.models))

            is TuiEvent.SetArenaUsePrecomputed ->
                state.copy(arena = state.arena.copy(usePrecomputed = event.value))

            is TuiEvent.UpdateArenaQuestionIdInput ->
                state.copy(arena = state.arena.copy(arenaQuestionIdInput = event.value))

            // After the question_id is confirmed the matchup is fully specified; the
            // CommandController fires the actual comparison. Just close the input.
            TuiEvent.ConfirmArenaQuestionIdInput ->
                state.copy(
                    arena = state.arena.copy(
                        isEnteringArenaQuestionId = false
                    )
                )

            is TuiEvent.UpdateArenaQueryInput ->
                state.copy(
                    arena = state.arena.copy(arenaQueryInput = event.value)
                )

            is TuiEvent.UpdateArenaModelAInput ->
                state.copy(
                    arena = state.arena.copy(arenaModelAInput = event.value)
                )

            is TuiEvent.UpdateArenaModelBInput ->
                state.copy(
                    arena = state.arena.copy(arenaModelBInput = event.value)
                )

            // Live mode only: query is the last input before the run fires.
            TuiEvent.ConfirmArenaQueryInput ->
                state.copy(
                    arena = state.arena.copy(
                        isEnteringArenaQuery = false
                    )
                )

            TuiEvent.ConfirmArenaModelAInput ->
                state.copy(
                    arena = state.arena.copy(
                        isEnteringArenaModelA = false,
                        isEnteringArenaModelB = true
                    )
                )

            // Model B confirmed: in precomputed mode collect the question_id next; in live
            // mode collect the free-text query next.
            TuiEvent.ConfirmArenaModelBInput ->
                state.copy(
                    arena = state.arena.copy(
                        isEnteringArenaModelB = false,
                        isEnteringArenaQuestionId = state.arena.usePrecomputed,
                        isEnteringArenaQuery = !state.arena.usePrecomputed
                    )
                )

            TuiEvent.CancelArenaInput ->
                state.copy(
                    arena = state.arena.copy(
                        isEnteringArenaQuestionId = false,
                        isEnteringArenaQuery = false,
                        isEnteringArenaModelA = false,
                        isEnteringArenaModelB = false
                    )
                )

            TuiEvent.StartTrickleFlow ->
                state.copy(
                    analysis = state.analysis.copy(mode = AnalysisMode.TRICKLE_TEST),
                    trickle = state.trickle.copy(
                        isEnteringTrickleQuery = true,
                        trickleQueryInput = ""
                    ),
                    shell = state.shell.copy(focusedPanel = FocusPanel.ANALYSIS_HUB)
                )

            is TuiEvent.UpdateTrickleQueryInput ->
                state.copy(
                    trickle = state.trickle.copy(trickleQueryInput = event.value)
                )

            TuiEvent.ConfirmTrickleQueryInput ->
                state.copy(
                    trickle = state.trickle.copy(
                        isEnteringTrickleQuery = false,
                        isRunningTrickleQuery = true,
                        trickleResultNodes = emptyList()
                    )
                )

            is TuiEvent.TrickleResultReceived ->
                state.copy(
                    trickle = state.trickle.copy(
                        trickleResultNodes = event.nodes,
                        isRunningTrickleQuery = false
                    )
                )

            TuiEvent.RunBatchTrickleTest ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        isRunningBatchTrickleTest = true,
                        batchTrickleProgress = "Starting batch trickle test…",
                        batchTrickleResults = null
                    )
                )

            is TuiEvent.BatchTrickleProgress ->
                state.copy(
                    benchmark = state.benchmark.copy(batchTrickleProgress = event.text)
                )

            is TuiEvent.BatchTrickleCompleted ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        isRunningBatchTrickleTest = false,
                        batchTrickleResults = event.results
                    )
                )

            TuiEvent.CancelTrickleInput ->
                state.copy(
                    trickle = state.trickle.copy(
                        isEnteringTrickleQuery = false,
                        isRunningTrickleQuery = false,
                        trickleQueryInput = ""
                    )
                )

            TuiEvent.StartBenchmarkFlow ->
                state.copy(
                    analysis = state.analysis.copy(mode = AnalysisMode.BENCHMARK),
                    benchmark = state.benchmark.copy(
                        // Always (re)enter on the type-selection screen.
                        benchmarkType = taxonomy.tui.state.BenchmarkType.NONE,
                        benchmarkTypeSelectionIndex = 0,
                        selectedBenchmarkField = 0,
                        isEditingBenchmarkField = false,
                        benchmarkEditingValue = "",
                        benchmarkScrollOffset = 0,
                        benchmarkActiveSection = taxonomy.tui.state.BenchmarkSection.MODELS,
                        benchmarkIsPickingModels = false,
                        benchmarkIsPickingDomains = false,
                        benchmarkPickerCursor = 0,
                        benchmarkLiveView = taxonomy.tui.state.BenchmarkLiveView.SUMMARY
                    ),
                    shell = state.shell.copy(focusedPanel = FocusPanel.ANALYSIS_HUB)
                )

            is TuiEvent.SetBenchmarkType ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        benchmarkType = event.type,
                        benchmarkScrollOffset = 0
                    )
                )

            is TuiEvent.SetBenchmarkTypeSelectionIndex ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        benchmarkTypeSelectionIndex = event.index.coerceIn(0, 1)
                    )
                )

            TuiEvent.ResetBenchmarkType ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        benchmarkType = taxonomy.tui.state.BenchmarkType.NONE,
                        benchmarkTypeSelectionIndex = 0,
                        benchmarkScrollOffset = 0
                    )
                )

            is TuiEvent.BenchmarkModelsLoaded ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        loadedModels = event.models,
                        evalDbDistinctModels = event.models.size,
                        benchmarkModelsInput = state.benchmark.benchmarkModelsInput
                            .ifBlank { event.models.take(2).joinToString(", ") }
                    )
                )

            is TuiEvent.BenchmarkLiveUpdate ->
                state.copy(
                    benchmark = state.benchmark.copy(liveStats = event.stats)
                )

            TuiEvent.DownloadEvalResults ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        isDownloadingEval = true,
                        evalDownloadProgress = emptyMap()
                    )
                )

            is TuiEvent.EvalDownloadProgress ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        evalDownloadProgress = state.benchmark.evalDownloadProgress + (
                            event.fileName to if (event.totalBytes > 0)
                                (event.bytesDownloaded.toFloat() / event.totalBytes).coerceIn(0f, 1f)
                            else 1f
                            )
                    )
                )

            TuiEvent.EvalDownloadComplete ->
                state.copy(
                    benchmark = state.benchmark.copy(isDownloadingEval = false)
                )

            // ── Per-model eval ingestion picker ──
            // Side-effect-only triggers (scan/ingest run in the CommandController).
            TuiEvent.RefreshEvalCatalog,
            TuiEvent.ConfirmEvalCatalogSelection ->
                state

            TuiEvent.OpenEvalCatalogPicker ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        isPickingEvalCatalog = true,
                        evalCatalogCursor = 0
                    )
                )

            TuiEvent.CloseEvalCatalogPicker ->
                state.copy(
                    benchmark = state.benchmark.copy(isPickingEvalCatalog = false)
                )

            is TuiEvent.EvalCatalogLoaded ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        evalCatalog = event.entries,
                        // Default-select every model not yet ingested.
                        evalCatalogSelection = event.entries
                            .filterNot { it.alreadyIngested }
                            .map { it.modelName }
                            .toSet(),
                        evalCatalogCursor = state.benchmark.evalCatalogCursor
                            .coerceIn(0, (event.entries.size - 1).coerceAtLeast(0))
                    )
                )

            is TuiEvent.MoveEvalCatalogCursor -> {
                val maxIdx = (state.benchmark.evalCatalog.size - 1).coerceAtLeast(0)
                state.copy(
                    benchmark = state.benchmark.copy(
                        evalCatalogCursor =
                            (state.benchmark.evalCatalogCursor + event.delta).coerceIn(0, maxIdx)
                    )
                )
            }

            TuiEvent.ToggleEvalCatalogSelection -> {
                val entry = state.benchmark.evalCatalog.getOrNull(state.benchmark.evalCatalogCursor)
                    ?: return state
                val sel = state.benchmark.evalCatalogSelection
                val next = if (entry.modelName in sel) sel - entry.modelName else sel + entry.modelName
                state.copy(benchmark = state.benchmark.copy(evalCatalogSelection = next))
            }

            TuiEvent.SelectAllNonIngestedEntries ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        evalCatalogSelection = state.benchmark.evalCatalog
                            .filterNot { it.alreadyIngested }
                            .map { it.modelName }
                            .toSet()
                    )
                )

            is TuiEvent.EvalIngestionProgress ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        // Confirming the picker closes it; progress then shows in the Arena view.
                        isPickingEvalCatalog = false,
                        evalLoaderIsRunning = true,
                        evalLoadingModelIdx = event.modelIdx,
                        evalLoadingModelCount = event.modelCount,
                        evalLoadingCurrentModel = event.modelName,
                        evalLoadingItem = event.item,
                        evalLoadingItemTotal = event.itemTotal
                    )
                )

            TuiEvent.EvalIngestionComplete ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        evalLoaderIsRunning = false,
                        evalLoadingModelCount = 0,
                        evalLoadingCurrentModel = ""
                    )
                )

            TuiEvent.ToggleLeaderboard -> {
                val nowOpen = !state.arena.isViewingLeaderboard
                state.copy(
                    arena = state.arena.copy(
                        isViewingLeaderboard = nowOpen,
                        // Reset scroll to the top whenever the leaderboard is closed.
                        leaderboardScrollOffset =
                            if (nowOpen) state.arena.leaderboardScrollOffset else 0
                    )
                )
            }

            is TuiEvent.SetLeaderboardScrollOffset ->
                state.copy(
                    arena = state.arena.copy(
                        leaderboardScrollOffset = event.offset.coerceAtLeast(0)
                    )
                )

            is TuiEvent.LeaderboardLoaded ->
                state.copy(
                    arena = state.arena.copy(leaderboard = event.groups)
                )

            TuiEvent.RunBenchmark ->
                state.copy(
                    benchmark = state.benchmark.copy(benchmarkSubScreen = taxonomy.tui.state.BenchmarkSubScreen.RESULTS)
                )

            TuiEvent.RunEvalLoad ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        evalLoaderIsRunning = true,
                        evalLoaderStatus = "Loading…"
                    )
                )

            is TuiEvent.SetSelectedBenchmarkField ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        selectedBenchmarkField = event.index.coerceAtLeast(0)
                    )
                )

            TuiEvent.StartEditingBenchmarkField ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        isEditingBenchmarkField = true,
                        // The only text-editable option is the query limit; prefill it.
                        benchmarkEditingValue = state.benchmark.benchmarkQueryLimitInput
                    )
                )

            TuiEvent.ConfirmEditingBenchmarkField ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        isEditingBenchmarkField = false,
                        benchmarkQueryLimitInput =
                            state.benchmark.benchmarkEditingValue.trim().ifBlank { "0" }
                    )
                )

            TuiEvent.CancelEditingBenchmarkField ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        isEditingBenchmarkField = false,
                        benchmarkEditingValue = ""
                    )
                )

            is TuiEvent.UpdateBenchmarkEditingValue ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        benchmarkEditingValue = event.value
                    )
                )

            is TuiEvent.SetBenchmarkScrollOffset ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        benchmarkScrollOffset = event.offset.coerceAtLeast(0)
                    )
                )

            is TuiEvent.SetBenchmarkSection ->
                state.copy(
                    benchmark = state.benchmark.copy(benchmarkActiveSection = event.section)
                )

            is TuiEvent.OpenBenchmarkPicker ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        benchmarkIsPickingModels = !event.domains,
                        benchmarkIsPickingDomains = event.domains,
                        benchmarkPickerCursor = 0,
                        benchmarkDomainOptions =
                            if (event.domains) event.domainOptions else state.benchmark.benchmarkDomainOptions
                    )
                )

            TuiEvent.CloseBenchmarkPicker ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        benchmarkIsPickingModels = false,
                        benchmarkIsPickingDomains = false
                    )
                )

            is TuiEvent.MoveBenchmarkPickerCursor -> {
                val size = if (state.benchmark.benchmarkIsPickingDomains)
                    state.benchmark.benchmarkDomainOptions.size
                else state.benchmark.loadedModels.size
                val maxIdx = (size - 1).coerceAtLeast(0)
                state.copy(
                    benchmark = state.benchmark.copy(
                        benchmarkPickerCursor =
                            (state.benchmark.benchmarkPickerCursor + event.delta).coerceIn(0, maxIdx)
                    )
                )
            }

            TuiEvent.ToggleBenchmarkPickerItem -> {
                if (state.benchmark.benchmarkIsPickingDomains) {
                    val name = state.benchmark.benchmarkDomainOptions
                        .getOrNull(state.benchmark.benchmarkPickerCursor) ?: return state
                    val sel = state.benchmark.benchmarkSelectedDomains
                    val next = if (name in sel) sel - name else sel + name
                    state.copy(benchmark = state.benchmark.copy(benchmarkSelectedDomains = next))
                } else {
                    val name = state.benchmark.loadedModels
                        .getOrNull(state.benchmark.benchmarkPickerCursor) ?: return state
                    val sel = state.benchmark.benchmarkSelectedModels
                    val next = if (name in sel) sel - name else sel + name
                    state.copy(benchmark = state.benchmark.copy(benchmarkSelectedModels = next))
                }
            }

            TuiEvent.ToggleBenchmarkReservedOnly -> {
                val now = state.benchmark.benchmarkReservedOnlyInput.toBooleanStrictOrNull() ?: true
                state.copy(
                    benchmark = state.benchmark.copy(benchmarkReservedOnlyInput = (!now).toString())
                )
            }

            TuiEvent.ToggleBenchmarkUpdateRankings -> {
                val now = state.benchmark.benchmarkUpdateRankingsInput.toBooleanStrictOrNull() ?: true
                state.copy(
                    benchmark = state.benchmark.copy(benchmarkUpdateRankingsInput = (!now).toString())
                )
            }

            TuiEvent.ToggleBenchmarkLiveView ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        benchmarkLiveView =
                            if (state.benchmark.benchmarkLiveView == taxonomy.tui.state.BenchmarkLiveView.SUMMARY)
                                taxonomy.tui.state.BenchmarkLiveView.STREAM
                            else taxonomy.tui.state.BenchmarkLiveView.SUMMARY
                    )
                )

            is TuiEvent.SetBenchmarkSubScreen ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        benchmarkSubScreen = event.subScreen
                    )
                )

            is TuiEvent.SetEvalLoaderFieldIdx ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        evalLoaderFieldIdx = event.index.coerceAtLeast(0)
                    )
                )

            is TuiEvent.SetEvalLoaderEditing ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        evalLoaderIsEditing = event.editing
                    )
                )

            is TuiEvent.UpdateEvalLoaderEditValue ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        evalLoaderEditValue = event.value
                    )
                )

            is TuiEvent.UpdateEvalLoaderModelInput ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        evalLoaderModelInput = event.value
                    )
                )

            is TuiEvent.UpdateEvalLoaderPathInput ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        evalLoaderPathInput = event.value
                    )
                )

            is TuiEvent.SetEvalLoaderRunning ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        evalLoaderIsRunning = event.running
                    )
                )

            is TuiEvent.SetEvalLoaderStatus ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        evalLoaderStatus = event.status
                    )
                )

            is TuiEvent.KeyPressed,
            is TuiEvent.MousePressed,
            is TuiEvent.MouseReleased,
            is TuiEvent.MouseDragged,
            is TuiEvent.MouseWheel ->
                state
        }
    }

    private fun applyScrollTo(
        state: TuiAppState,
        target: ScrollbarTarget,
        offset: Int
    ): TuiAppState {
        val safe = offset.coerceAtLeast(0)

        return when (target) {
            ScrollbarTarget.TOPOLOGY -> {
                if (state.topology.showDomainSelector) {
                    state.copy(
                        config = state.config.copy(domainScrollOffset = safe)
                    )
                } else {
                    state.copy(
                        topology = state.topology.copy(
                            treeScrollOffset = safe,
                            autoScroll = false
                        )
                    )
                }
            }

            ScrollbarTarget.CONFIG_DOMAINS ->
                state.copy(
                    config = state.config.copy(domainScrollOffset = safe)
                )

            ScrollbarTarget.ANALYSIS ->
                when (state.analysis.mode) {
                    AnalysisMode.NODE_DETAIL ->
                        state.copy(
                            analysis = state.analysis.copy(inspectorScroll = safe)
                        )

                    AnalysisMode.METRICS ->
                        state.copy(
                            analysis = state.analysis.copy(metricsScrollOffset = safe)
                        )

                    AnalysisMode.BENCHMARK ->
                        state.copy(
                            benchmark = state.benchmark.copy(benchmarkScrollOffset = safe)
                        )

                    AnalysisMode.SNAPSHOTS ->
                        state.copy(
                            snapshot = state.snapshot.copy(
                                selectedSnapshotIdx = safe.coerceIn(
                                    0,
                                    (state.snapshot.snapshotList.size - 1).coerceAtLeast(0)
                                )
                            )
                        )

                    else -> state
                }

            ScrollbarTarget.LOGS ->
                state.copy(
                    logs = state.logs.copy(logScrollOffset = safe)
                )
        }
    }

    private fun applyScrollBy(
        state: TuiAppState,
        target: ScrollbarTarget,
        delta: Int
    ): TuiAppState {
        return when (target) {
            ScrollbarTarget.TOPOLOGY -> {
                if (state.topology.showDomainSelector) {
                    state.copy(
                        config = state.config.copy(
                            domainScrollOffset = (state.config.domainScrollOffset + delta).coerceAtLeast(0)
                        )
                    )
                } else {
                    state.copy(
                        topology = state.topology.copy(
                            treeScrollOffset = (state.topology.treeScrollOffset + delta).coerceAtLeast(0),
                            autoScroll = false
                        )
                    )
                }
            }

            ScrollbarTarget.CONFIG_DOMAINS ->
                state.copy(
                    config = state.config.copy(
                        domainScrollOffset = (state.config.domainScrollOffset + delta).coerceAtLeast(0)
                    )
                )

            ScrollbarTarget.ANALYSIS ->
                when (state.analysis.mode) {
                    AnalysisMode.NODE_DETAIL ->
                        state.copy(
                            analysis = state.analysis.copy(
                                inspectorScroll = (state.analysis.inspectorScroll + delta).coerceAtLeast(0)
                            )
                        )

                    AnalysisMode.METRICS ->
                        state.copy(
                            analysis = state.analysis.copy(
                                metricsScrollOffset = (state.analysis.metricsScrollOffset + delta).coerceAtLeast(0)
                            )
                        )

                    AnalysisMode.BENCHMARK ->
                        state.copy(
                            benchmark = state.benchmark.copy(
                                benchmarkScrollOffset = (state.benchmark.benchmarkScrollOffset + delta).coerceAtLeast(0)
                            )
                        )

                    AnalysisMode.SNAPSHOTS -> {
                        val maxIdx = (state.snapshot.snapshotList.size - 1).coerceAtLeast(0)
                        state.copy(
                            snapshot = state.snapshot.copy(
                                selectedSnapshotIdx = (state.snapshot.selectedSnapshotIdx + delta).coerceIn(0, maxIdx)
                            )
                        )
                    }

                    else -> state
                }

            ScrollbarTarget.LOGS ->
                state.copy(
                    logs = state.logs.copy(
                        logScrollOffset = (state.logs.logScrollOffset + delta).coerceAtLeast(0)
                    )
                )
        }
    }
}
