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
                        state = StartupState.WELCOME,
                        selectedWelcomeIdx = 0,
                        loadingSnapshotId = null
                    ),
                    shell = state.shell.copy(focusedPanel = FocusPanel.TOPOLOGY)
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
                    if (state.startup.state == StartupState.LOADING) StartupState.WELCOME
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

            is TuiEvent.SnapshotLoaded ->
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
                        isSavingSnapshot = false,
                        snapshotDescInput = "",
                        isRenamingSnapshot = false,
                        renameInput = ""
                    )
                )

            is TuiEvent.SnapshotLoadFailed ->
                state.copy(
                    startup = state.startup.copy(
                        state = StartupState.WELCOME,
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
                    runtime = state.runtime.copy(isRegenerating = false)
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
                        trickleQueryInput = "",
                        isViewingBatchTrickleResults = false,
                        batchTrickleScrollOffset = 0
                    ),
                    shell = state.shell.copy(focusedPanel = FocusPanel.ANALYSIS_HUB)
                )

            is TuiEvent.UpdateTrickleQueryInput ->
                state.copy(
                    trickle = state.trickle.copy(trickleQueryInput = event.value)
                )

            TuiEvent.ConfirmTrickleQueryInput ->
                state.copy(
                    trickle = state.trickle.copy(isEnteringTrickleQuery = false)
                )

            TuiEvent.CancelTrickleInput ->
                state.copy(
                    trickle = state.trickle.copy(
                        isEnteringTrickleQuery = false,
                        trickleQueryInput = ""
                    )
                )

            is TuiEvent.SetViewingBatchTrickleResults ->
                state.copy(
                    trickle = state.trickle.copy(
                        isViewingBatchTrickleResults = event.value
                    )
                )

            is TuiEvent.SetBatchTrickleScrollOffset ->
                state.copy(
                    trickle = state.trickle.copy(
                        batchTrickleScrollOffset = event.offset.coerceAtLeast(0)
                    )
                )

            TuiEvent.StartBenchmarkFlow ->
                state.copy(
                    analysis = state.analysis.copy(mode = AnalysisMode.BENCHMARK),
                    benchmark = state.benchmark.copy(
                        selectedBenchmarkField = 0,
                        isEditingBenchmarkField = false,
                        benchmarkEditingValue = "",
                        benchmarkScrollOffset = 0
                    ),
                    shell = state.shell.copy(focusedPanel = FocusPanel.ANALYSIS_HUB)
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
                        isEditingBenchmarkField = true
                    )
                )

            TuiEvent.ConfirmEditingBenchmarkField ->
                state.copy(
                    benchmark = state.benchmark.copy(
                        isEditingBenchmarkField = false
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

                    AnalysisMode.TRICKLE_TEST ->
                        state.copy(
                            trickle = state.trickle.copy(batchTrickleScrollOffset = safe)
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

                    AnalysisMode.TRICKLE_TEST ->
                        state.copy(
                            trickle = state.trickle.copy(
                                batchTrickleScrollOffset = (state.trickle.batchTrickleScrollOffset + delta).coerceAtLeast(0)
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