package taxonomy.tui.controller

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import taxonomy.service.AnalysisMode
import taxonomy.model.GraphNode
import taxonomy.tui.app.DashboardLayout
import taxonomy.tui.components.SettingItem
import taxonomy.tui.components.TreeLine
import taxonomy.tui.components.StartupState
import taxonomy.tui.state.BenchmarkType
import taxonomy.tui.state.ConfigSubPanel
import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.MetricsZoneFocus
import taxonomy.tui.state.TuiAppState

class TuiController(
    initialState: TuiAppState = TuiAppState(),
    private val effects: TuiEffects,
    private val focusController: FocusController = FocusController(),
    private val scrollController: ScrollController = ScrollController(),
    private val commandController: CommandController = CommandController(effects),
    /** Current setting items, used to resolve the selected item for edit/apply. */
    private val settingItemsProvider: () -> List<SettingItem> = { emptyList() },
    /** Available dataset domains (name, count), used to resolve domain toggles. */
    private val availableDomainsProvider: () -> List<Pair<String, Int>> = { emptyList() },
    /** Rebuilds the DAG tree lines from the live graph + expand state, so key handlers can
     *  resolve the selected tree row to a node (expand/collapse, inspect). */
    private val treeLinesProvider: (Map<String, Boolean>) -> List<TreeLine> = { emptyList() },
    /** Size of the live per-iteration metrics history, used to clamp table cursor navigation
     *  in the METRICS view. */
    private val metricsHistorySizeProvider: () -> Int = { 0 },
    /** Invoked when the user asks to quit (Ctrl-C / Ctrl-Q / quit hotkey). Restores the
     *  terminal and stops the process. */
    private val onQuit: () -> Unit = {},
) {

    private val _state = MutableStateFlow(initialState)
    val state: StateFlow<TuiAppState> = _state.asStateFlow()

    init {
        dispatch(TuiEvent.RefreshSnapshots)
        dispatch(TuiEvent.RefreshDatasetStatus)
        dispatch(TuiEvent.RefreshArenaModels)
    }

    fun dispatch(event: TuiEvent) {
        if (event is TuiEvent.QuitRequested) {
            onQuit()
            return
        }
        _state.value = TuiReducer.reduce(_state.value, event)
        commandController.handle(_state.value, event, ::dispatch)

        when (event) {
            is TuiEvent.KeyPressed -> handleKeyPressed(event)
            is TuiEvent.MouseWheel -> handleMouseWheel(event)
            is TuiEvent.MousePressed -> handleMousePressed(event)
            is TuiEvent.MouseReleased -> dispatch(TuiEvent.StopDraggingScrollbar)
            is TuiEvent.MouseDragged -> handleMouseDragged(event)
            else -> Unit
        }
    }

    private fun handleKeyPressed(event: TuiEvent.KeyPressed) {
        val state = _state.value
        val key = event.key.lowercase()

        if (state.startup.state == StartupState.LOADING) return

        when (state.startup.state) {
            StartupState.LOAD_DAG -> handleWelcomeKeys(state, key)
            StartupState.CONFIGANDDOMAINS -> handleConfigKeys(state, key)
            StartupState.MAINDASHBOARD -> handleMainDashboardKeys(state, key)
            StartupState.LOADING -> Unit
        }
    }

    private fun handleWelcomeKeys(state: TuiAppState, key: String) {
        val welcomeOptionsCount = 1 + state.snapshot.snapshotList.size

        when (key) {
            "w", "z", "arrowup" -> {
                dispatch(
                    TuiEvent.SelectWelcomeIndex(
                        (state.startup.selectedWelcomeIdx - 1 + welcomeOptionsCount) % welcomeOptionsCount
                    )
                )
            }

            "s", "arrowdown" -> {
                dispatch(
                    TuiEvent.SelectWelcomeIndex(
                        (state.startup.selectedWelcomeIdx + 1) % welcomeOptionsCount
                    )
                )
            }

            "d" -> {
                val idx = state.startup.selectedWelcomeIdx - 1
                if (idx in state.snapshot.snapshotList.indices) {
                    dispatch(TuiEvent.RequestDeleteSnapshot(state.snapshot.snapshotList[idx].id))
                }
            }

            "enter" -> {
                if (state.startup.selectedWelcomeIdx == 0) {
                    dispatch(TuiEvent.EnterConfigSetup)
                } else {
                    val snap = state.snapshot.snapshotList
                        .getOrNull(state.startup.selectedWelcomeIdx - 1) ?: return
                    dispatch(TuiEvent.RequestLoadSnapshot(snap.id))
                }
            }

            "escape", "q" -> {
                if (state.snapshot.isViewingSnapshot) {
                    dispatch(TuiEvent.EnterMainDashboard)
                } else {
                    // Welcome is the top-level screen; q/Esc here exits the whole app.
                    dispatch(TuiEvent.QuitRequested)
                }
            }
        }
    }

    private fun handleConfigKeys(state: TuiAppState, key: String) {
        // While a dataset download is running, Esc/C cancels it.
        if (state.config.downloadingDataset && (key == "escape" || key == "c")) {
            dispatch(TuiEvent.CancelGeneration)
            return
        }
        if (state.shell.focusedPanel == FocusPanel.SYSTEM_LOGS) {
            when (key) {
                "w", "z", "arrowup" ->
                    dispatch(TuiEvent.SetLogsScroll((state.logs.logScrollOffset - 1).coerceAtLeast(0)))

                "s", "arrowdown" ->
                    dispatch(TuiEvent.SetLogsScroll((state.logs.logScrollOffset + 1).coerceAtLeast(0)))

                "q", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.CONFIG))
            }
            return
        }

        if (state.config.isEditingSetting) {
            handleSettingEditorKeys(state, key)
            return
        }

        // Download-count prompt: type a number (blank = full dataset), Enter to start.
        if (state.config.promptingDownloadCount) {
            when (key) {
                "enter" -> {
                    val n = state.config.downloadCountInput.toIntOrNull() ?: 0
                    dispatch(TuiEvent.StartDatasetDownload(n))
                }
                "escape", "q" -> dispatch(TuiEvent.CancelDatasetDownload)
                "backspace" -> dispatch(
                    TuiEvent.UpdateDownloadCountInput(state.config.downloadCountInput.dropLast(1))
                )
                else -> if (key.length == 1 && key[0].isDigit()) {
                    dispatch(TuiEvent.UpdateDownloadCountInput(state.config.downloadCountInput + key))
                }
            }
            return
        }

        when (key) {
            "tab" -> {
                val next = if (state.config.activeSubPanel == ConfigSubPanel.DOMAINS) {
                    ConfigSubPanel.SETTINGS
                } else {
                    ConfigSubPanel.DOMAINS
                }
                dispatch(TuiEvent.SetConfigSubPanel(next))
            }

            "w", "z", "arrowup" -> {
                if (state.config.activeSubPanel == ConfigSubPanel.DOMAINS) {
                    dispatch(TuiEvent.SetSelectedDomainIdx((state.config.selectedDomainIdx - 1).coerceAtLeast(0)))
                } else {
                    dispatch(TuiEvent.SetSelectedSettingIdx((state.config.selectedSettingIdx - 1).coerceAtLeast(0)))
                }
            }

            "s", "arrowdown" -> {
                if (state.config.activeSubPanel == ConfigSubPanel.DOMAINS) {
                    dispatch(TuiEvent.SetSelectedDomainIdx(state.config.selectedDomainIdx + 1))
                } else {
                    dispatch(TuiEvent.SetSelectedSettingIdx(state.config.selectedSettingIdx + 1))
                }
            }

            "enter", " ", "space" -> {
                if (state.config.activeSubPanel == ConfigSubPanel.DOMAINS) {
                    val domains = availableDomainsProvider()
                    domains.getOrNull(state.config.selectedDomainIdx)?.let { (name, _) ->
                        dispatch(TuiEvent.ToggleSelectedDomain(name))
                    }
                } else {
                    // Settings: instant toggle/cycle for boolean/select, editor for number/text.
                    dispatch(TuiEvent.ActivateSelectedSetting)
                }
            }

            "d" -> dispatch(TuiEvent.PromptDatasetDownload)
            // R generates a new DAG, but only once the dataset is present locally. Domains are
            // read from the downloaded data, so generation is gated on a download first. If the
            // dataset is missing, R opens the download prompt instead.
            "r" -> when {
                state.runtime.isRegenerating -> Unit
                state.runtime.isDatasetDownloaded -> dispatch(TuiEvent.StartGeneration)
                else -> dispatch(TuiEvent.PromptDatasetDownload)
            }
            "arrowdown", "arrowright" -> dispatch(TuiEvent.FocusPanelRequested(FocusPanel.SYSTEM_LOGS))
            "escape", "q" -> dispatch(TuiEvent.ReturnToWelcome)
        }
    }

    private fun handleSettingEditorKeys(state: TuiAppState, key: String) {
        when (key) {
            "enter" -> {
                // Apply the typed value BEFORE the reducer clears editingValue, then close.
                val item = settingItemsProvider().getOrNull(state.config.selectedSettingIdx)
                if (item != null) {
                    dispatch(TuiEvent.ApplySetting(item.name, state.config.editingValue))
                }
                dispatch(TuiEvent.ConfirmEditingSetting)
            }
            // Only Esc cancels: 'q' must remain typable inside text/number value editors.
            "escape" -> dispatch(TuiEvent.CancelEditingSetting)
            "backspace" -> dispatch(TuiEvent.UpdateEditingValue(state.config.editingValue.dropLast(1)))
            else -> {
                if (key.length == 1) {
                    dispatch(TuiEvent.UpdateEditingValue(state.config.editingValue + key))
                }
            }
        }
    }

    private fun handleMainDashboardKeys(state: TuiAppState, key: String) {
        if (isTextInputActive(state)) {
            handleActiveTextInput(state, key)
            return
        }
        // Esc/C cancels any long-running job: DAG generation, batch trickle, or eval download.
        val canCancel = state.runtime.isRegenerating ||
                state.benchmark.isRunningBatchTrickleTest ||
                state.benchmark.isDownloadingEval
        if (canCancel && (key == "escape" || key == "c")) {
            dispatch(TuiEvent.CancelGeneration)
            return
        }

        when (key) {
            "tab" -> dispatch(focusController.cycleForward(state))
            "x" -> dispatch(TuiEvent.ReturnToWelcome)
            "m" -> dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.METRICS))
            // Arena and Benchmark are gated on a loaded precomputed eval roster. Without it
            // there are no model answers to judge, so we surface the metrics view (which shows
            // the "load eval_results" hint) instead of dropping the user into an empty arena.
            "a" -> {
                // Always refresh the model roster so Arena reflects newly downloaded eval results.
                effects.loadArenaModels(::dispatch)
                if (state.arena.loadedModels.isNotEmpty()) {
                    commandController.startArena(::dispatch)
                } else {
                    dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.ARENA))
                }
            }
            // "b" opens the Benchmark hub (always on the type-selection screen). Once the
            // TRICKLE benchmark type is active, "b" instead starts the batch routing test —
            // matching the panel hint. The roster gate now lives inside the ARENA sub-view
            // (Trickle benchmark needs no precomputed models), so entry isn't gated on a roster.
            "b" -> if (state.analysis.mode == AnalysisMode.BENCHMARK &&
                state.benchmark.benchmarkType == BenchmarkType.TRICKLE
            ) {
                if (!state.benchmark.isRunningBatchTrickleTest) {
                    dispatch(TuiEvent.RunBatchTrickleTest)
                }
            } else {
                commandController.startBenchmark(::dispatch)
            }
            "t" -> commandController.startTrickle(::dispatch)

            // Global in their respective modes: "o" downloads MMLU-Pro eval_results while in
            // Benchmark; "l" toggles the leaderboard while in Arena. Outside those modes the
            // keys fall through to the focused panel's handler.
            "o" -> if (state.analysis.mode == AnalysisMode.BENCHMARK) {
                dispatch(TuiEvent.DownloadEvalResults)
            } else {
                routeByFocusedPanel(state, key)
            }
            "l" -> if (state.analysis.mode == AnalysisMode.ARENA) {
                dispatch(TuiEvent.ToggleLeaderboard)
            } else {
                routeByFocusedPanel(state, key)
            }

            "g" -> {
                dispatch(TuiEvent.SetBatchReplaceExisting(false))
                dispatch(TuiEvent.StartBatchGeneralityInput)
            }

            "f" -> {
                dispatch(TuiEvent.SetBatchReplaceExisting(true))
                dispatch(TuiEvent.StartBatchGeneralityInput)
            }

            // Snapshots are auto-saved on generation, so "N" only renames the snapshot
            // currently being viewed (no manual save-new action).
            "n" -> {
                if (state.snapshot.isViewingSnapshot && state.snapshot.activeSnapshotId != null) {
                    dispatch(TuiEvent.StartRenameSnapshot)
                }
            }

            else -> routeByFocusedPanel(state, key)
        }
    }

    private fun routeByFocusedPanel(state: TuiAppState, key: String) {
        when (state.shell.focusedPanel) {
            FocusPanel.TOPOLOGY -> handleTopologyKeys(state, key)
            FocusPanel.ANALYSIS_HUB -> handleAnalysisKeys(state, key)
            FocusPanel.SYSTEM_LOGS -> handleLogsKeys(state, key)
            FocusPanel.PROCESSES -> Unit
            FocusPanel.CONFIG -> handleConfigKeys(state, key)
        }
    }

    private fun handleTopologyKeys(state: TuiAppState, key: String) {
        when (key) {
            "w", "z", "arrowup" -> {
                dispatch(TuiEvent.SetSelectedTreeIdx((state.topology.selectedTreeIdx - 1).coerceAtLeast(0)))
                dispatch(TuiEvent.SetTopologyAutoScroll(false))
            }

            "s", "arrowdown" -> {
                dispatch(TuiEvent.SetSelectedTreeIdx(state.topology.selectedTreeIdx + 1))
                dispatch(TuiEvent.SetTopologyAutoScroll(false))
            }

            // Right / l expands the selected node; left / h collapses it. Space toggles.
            "arrowright", "l", "d" -> selectedTreeNode(state)?.let {
                if (it.children.isNotEmpty()) dispatch(TuiEvent.SetNodeExpanded(it.id, true))
            }
            "arrowleft", "h" -> selectedTreeNode(state)?.let {
                if (it.children.isNotEmpty()) dispatch(TuiEvent.SetNodeExpanded(it.id, false))
            }
            " ", "space" -> selectedTreeNode(state)?.let {
                if (it.children.isNotEmpty()) dispatch(TuiEvent.ToggleNodeExpanded(it.id))
            }

            "enter" -> {
                // Populate the inspector's node (service state) THEN switch the hub to the
                // node-detail view (MVI mode) and focus it.
                effects.inspectNode(selectedTreeNode(state))
                dispatch(TuiEvent.FocusPanelRequested(FocusPanel.ANALYSIS_HUB))
                dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.NODE_DETAIL))
            }

            "q", "escape" -> dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
        }
    }

    /** The DAG node currently highlighted in the tree, if any. */
    private fun selectedTreeNode(state: TuiAppState): GraphNode? {
        val lines = treeLinesProvider(state.topology.expandedNodes)
        return lines.getOrNull(state.topology.selectedTreeIdx)?.node
    }

    private fun handleAnalysisKeys(state: TuiAppState, key: String) {
        when (state.analysis.mode) {
            AnalysisMode.NODE_DETAIL -> when (key) {
                "w", "z", "arrowup" ->
                    dispatch(TuiEvent.SetInspectorScroll((state.analysis.inspectorScroll - 1).coerceAtLeast(0)))

                "s", "arrowdown" ->
                    dispatch(TuiEvent.SetInspectorScroll(state.analysis.inspectorScroll + 1))

                "q", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
            }

            AnalysisMode.METRICS -> handleMetricsKeys(state, key)

            AnalysisMode.ARENA -> when (key) {
                "w", "z", "arrowup" ->
                    dispatch(TuiEvent.SetLeaderboardScrollOffset(
                        (state.arena.leaderboardScrollOffset - 1).coerceAtLeast(0)
                    ))

                "s", "arrowdown" ->
                    dispatch(TuiEvent.SetLeaderboardScrollOffset(
                        state.arena.leaderboardScrollOffset + 1
                    ))

                "q", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
            }

            AnalysisMode.SNAPSHOTS -> handleSnapshotKeys(state, key)

            // Trickle mode is now a single-query routing diagnosis only; the batch test moved
            // to the Benchmark hub's TRICKLE type. Single-query results aren't scrollable.
            AnalysisMode.TRICKLE_TEST -> when (key) {
                "q", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
            }

            AnalysisMode.BENCHMARK -> handleBenchmarkKeys(state, key)

            else -> when (key) {
                "q", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
            }
        }
    }

    /**
     * 3-zone METRICS view key handling. When the TABLE zone is focused, W/S move the
     * iteration cursor (Home/End jump to first/Final); when the DETAIL zone is focused,
     * W/S scroll the per-iteration detail. Tab toggles focus, P toggles the perf block.
     */
    private fun handleMetricsKeys(state: TuiAppState, key: String) {
        val m = state.analysis
        when (m.metricsZoneFocus) {
            MetricsZoneFocus.TABLE -> when (key) {
                "w", "z", "arrowup" ->
                    dispatch(TuiEvent.SetMetricsIterationIndex(m.selectedIterationIndex - 1))

                "s", "arrowdown" -> {
                    val maxIdx = metricsHistorySizeProvider() - 1
                    dispatch(TuiEvent.SetMetricsIterationIndex(
                        (m.selectedIterationIndex + 1).coerceAtMost(maxIdx)
                    ))
                }

                "tab" -> dispatch(TuiEvent.SetMetricsZoneFocus(MetricsZoneFocus.DETAIL))
                "p" -> dispatch(TuiEvent.ToggleMetricsPerformance)
                "home" -> dispatch(TuiEvent.SetMetricsIterationIndex(0))
                "end" -> dispatch(TuiEvent.SetMetricsIterationIndex(-1))

                "q", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
            }

            MetricsZoneFocus.DETAIL -> when (key) {
                "w", "z", "arrowup" ->
                    dispatch(TuiEvent.SetMetricsDetailScroll((m.detailScrollOffset - 1).coerceAtLeast(0)))

                "s", "arrowdown" ->
                    dispatch(TuiEvent.SetMetricsDetailScroll(m.detailScrollOffset + 1))

                "tab", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.SetMetricsZoneFocus(MetricsZoneFocus.TABLE))

                "p" -> dispatch(TuiEvent.ToggleMetricsPerformance)

                "q" -> dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
            }
        }
    }

    /**
     * Benchmark hub key handling, split across its three sub-states: the type-selection
     * screen (NONE), the Arena benchmark (ARENA), and the batch Trickle benchmark (TRICKLE).
     */
    private fun handleBenchmarkKeys(state: TuiAppState, key: String) {
        when (state.benchmark.benchmarkType) {
            BenchmarkType.NONE -> when (key) {
                "w", "z", "arrowup" ->
                    dispatch(TuiEvent.SetBenchmarkTypeSelectionIndex(
                        state.benchmark.benchmarkTypeSelectionIndex - 1
                    ))

                "s", "arrowdown" ->
                    dispatch(TuiEvent.SetBenchmarkTypeSelectionIndex(
                        state.benchmark.benchmarkTypeSelectionIndex + 1
                    ))

                "enter", " ", "space" -> {
                    val selected =
                        if (state.benchmark.benchmarkTypeSelectionIndex == 0) BenchmarkType.ARENA
                        else BenchmarkType.TRICKLE
                    dispatch(TuiEvent.SetBenchmarkType(selected))
                }

                "q", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
            }

            BenchmarkType.ARENA -> when (key) {
                "w", "z", "arrowup" ->
                    dispatch(TuiEvent.SetBenchmarkScrollOffset((state.benchmark.benchmarkScrollOffset - 1).coerceAtLeast(0)))

                "s", "arrowdown" ->
                    dispatch(TuiEvent.SetBenchmarkScrollOffset(state.benchmark.benchmarkScrollOffset + 1))

                "enter" -> dispatch(TuiEvent.RunBenchmark)
                "o" -> dispatch(TuiEvent.DownloadEvalResults)

                "q", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.ResetBenchmarkType)
            }

            // "b" (start batch test) is handled at the dashboard level so it works regardless
            // of which panel holds focus; here we only handle scrolling and going back.
            BenchmarkType.TRICKLE -> when (key) {
                "w", "z", "arrowup" ->
                    dispatch(TuiEvent.SetBenchmarkScrollOffset((state.benchmark.benchmarkScrollOffset - 1).coerceAtLeast(0)))

                "s", "arrowdown" ->
                    dispatch(TuiEvent.SetBenchmarkScrollOffset(state.benchmark.benchmarkScrollOffset + 1))

                "q", "escape", "arrowleft", "backspace" ->
                    if (!state.benchmark.isRunningBatchTrickleTest) {
                        dispatch(TuiEvent.ResetBenchmarkType)
                    }
            }
        }
    }

    private fun handleSnapshotKeys(state: TuiAppState, key: String) {
        if (state.snapshot.isRenamingSnapshot) {
            when (key) {
                "enter" -> dispatch(TuiEvent.ConfirmRenameSnapshot)
                "escape", "q" -> dispatch(TuiEvent.CancelRenameSnapshot)
                "backspace" -> dispatch(TuiEvent.UpdateRenameInput(state.snapshot.renameInput.dropLast(1)))
                else -> {
                    if (key.length == 1) {
                        dispatch(TuiEvent.UpdateRenameInput(state.snapshot.renameInput + key))
                    }
                }
            }
            return
        }

        if (state.snapshot.isSavingSnapshot) {
            when (key) {
                "enter" -> dispatch(TuiEvent.ConfirmSaveSnapshot)
                "escape", "q" -> dispatch(TuiEvent.CancelSaveSnapshot)
                "backspace" -> dispatch(TuiEvent.UpdateSnapshotDescInput(state.snapshot.snapshotDescInput.dropLast(1)))
                else -> {
                    if (key.length == 1) {
                        dispatch(TuiEvent.UpdateSnapshotDescInput(state.snapshot.snapshotDescInput + key))
                    }
                }
            }
            return
        }

        when (key) {
            "w", "z", "arrowup" ->
                dispatch(TuiEvent.SelectSnapshotIndex((state.snapshot.selectedSnapshotIdx - 1).coerceAtLeast(0)))

            "s", "arrowdown" ->
                dispatch(TuiEvent.SelectSnapshotIndex(state.snapshot.selectedSnapshotIdx + 1))

            "l", "enter" -> {
                val snap = state.snapshot.snapshotList.getOrNull(state.snapshot.selectedSnapshotIdx) ?: return
                dispatch(TuiEvent.RequestLoadSnapshot(snap.id))
            }

            "d" -> {
                val snap = state.snapshot.snapshotList.getOrNull(state.snapshot.selectedSnapshotIdx) ?: return
                dispatch(TuiEvent.RequestDeleteSnapshot(snap.id))
            }

            "n" -> dispatch(TuiEvent.StartSaveSnapshot)
            "q", "escape", "arrowleft", "backspace" -> dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
        }
    }

    private fun handleLogsKeys(state: TuiAppState, key: String) {
        when (key) {
            "w", "z", "arrowup" ->
                dispatch(TuiEvent.SetLogsScroll((state.logs.logScrollOffset - 1).coerceAtLeast(0)))

            "s", "arrowdown" ->
                dispatch(TuiEvent.SetLogsScroll((state.logs.logScrollOffset + 1).coerceAtLeast(0)))

            "q", "escape", "arrowleft", "backspace" ->
                dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
        }
    }

    private fun handleActiveTextInput(state: TuiAppState, key: String) {
        when {
            state.snapshot.isRenamingSnapshot -> handleSnapshotKeys(state, key)
            state.snapshot.isSavingSnapshot -> handleSnapshotKeys(state, key)
            state.config.isEditingSetting -> handleSettingEditorKeys(state, key)

            state.analysis.isEnteringBatchGenerality -> {
                when (key) {
                    "enter" -> dispatch(TuiEvent.ConfirmBatchGeneralityInput)
                    "escape", "q" -> dispatch(TuiEvent.CancelBatchGeneralityInput)
                    "backspace" -> dispatch(
                        TuiEvent.UpdateBatchGeneralityInput(
                            state.analysis.batchGeneralityInput.dropLast(1)
                        )
                    )
                    else -> {
                        if (key.all(Char::isDigit)) {
                            dispatch(TuiEvent.UpdateBatchGeneralityInput(state.analysis.batchGeneralityInput + key))
                        }
                    }
                }
            }

            state.arena.isEnteringArenaQuestionId -> {
                when (key) {
                    "enter" -> dispatch(TuiEvent.ConfirmArenaQuestionIdInput)
                    "escape", "q" -> dispatch(TuiEvent.CancelArenaInput)
                    "backspace" -> dispatch(TuiEvent.UpdateArenaQuestionIdInput(state.arena.arenaQuestionIdInput.dropLast(1)))
                    else -> {
                        if (key.all(Char::isDigit) && key.isNotEmpty()) {
                            dispatch(TuiEvent.UpdateArenaQuestionIdInput(state.arena.arenaQuestionIdInput + key))
                        }
                    }
                }
            }

            state.arena.isEnteringArenaQuery -> {
                when (key) {
                    "enter" -> dispatch(TuiEvent.ConfirmArenaQueryInput)
                    "escape", "q" -> dispatch(TuiEvent.CancelArenaInput)
                    "backspace" -> dispatch(TuiEvent.UpdateArenaQueryInput(state.arena.arenaQueryInput.dropLast(1)))
                    else -> {
                        if (key.length == 1) {
                            dispatch(TuiEvent.UpdateArenaQueryInput(state.arena.arenaQueryInput + key))
                        }
                    }
                }
            }

            state.arena.isEnteringArenaModelA -> {
                when (key) {
                    "enter" -> dispatch(TuiEvent.ConfirmArenaModelAInput)
                    "escape", "q" -> dispatch(TuiEvent.CancelArenaInput)
                    "backspace" -> dispatch(TuiEvent.UpdateArenaModelAInput(state.arena.arenaModelAInput.dropLast(1)))
                    else -> {
                        if (key.length == 1) {
                            dispatch(TuiEvent.UpdateArenaModelAInput(state.arena.arenaModelAInput + key))
                        }
                    }
                }
            }

            state.arena.isEnteringArenaModelB -> {
                when (key) {
                    "enter" -> dispatch(TuiEvent.ConfirmArenaModelBInput)
                    "escape", "q" -> dispatch(TuiEvent.CancelArenaInput)
                    "backspace" -> dispatch(TuiEvent.UpdateArenaModelBInput(state.arena.arenaModelBInput.dropLast(1)))
                    else -> {
                        if (key.length == 1) {
                            dispatch(TuiEvent.UpdateArenaModelBInput(state.arena.arenaModelBInput + key))
                        }
                    }
                }
            }

            state.trickle.isEnteringTrickleQuery -> {
                when (key) {
                    "enter" -> dispatch(TuiEvent.ConfirmTrickleQueryInput)
                    "escape", "q" -> dispatch(TuiEvent.CancelTrickleInput)
                    "backspace" -> dispatch(TuiEvent.UpdateTrickleQueryInput(state.trickle.trickleQueryInput.dropLast(1)))
                    else -> {
                        if (key.length == 1) {
                            dispatch(TuiEvent.UpdateTrickleQueryInput(state.trickle.trickleQueryInput + key))
                        }
                    }
                }
            }

            state.benchmark.isEditingBenchmarkField -> {
                when (key) {
                    "enter" -> dispatch(TuiEvent.ConfirmEditingBenchmarkField)
                    "escape", "q" -> dispatch(TuiEvent.CancelEditingBenchmarkField)
                    "backspace" -> dispatch(
                        TuiEvent.UpdateBenchmarkEditingValue(
                            state.benchmark.benchmarkEditingValue.dropLast(1)
                        )
                    )
                    else -> {
                        if (key.length == 1) {
                            dispatch(TuiEvent.UpdateBenchmarkEditingValue(state.benchmark.benchmarkEditingValue + key))
                        }
                    }
                }
            }
        }
    }

    private fun handleMouseWheel(event: TuiEvent.MouseWheel) {
        val state = _state.value
        val scrollEvent = when (event.direction) {
            WheelDirection.Up -> scrollController.scrollUp(state)
            WheelDirection.Down -> scrollController.scrollDown(state)
        }
        if (scrollEvent != null) {
            dispatch(scrollEvent)
        }
    }

    private fun handleMousePressed(event: TuiEvent.MousePressed) {
        val state = _state.value
        when (state.startup.state) {
            StartupState.LOAD_DAG -> handleWelcomeMouse(event)
            StartupState.CONFIGANDDOMAINS -> handleConfigMouse(state, event)
            StartupState.MAINDASHBOARD -> handleDashboardMouse(state, event)
            StartupState.LOADING -> Unit
        }
    }

    /**
     * Mouse in the config screen: choose the DOMAINS or SETTINGS sub-panel by x,
     * select the row under the cursor by y, and toggle/activate it (click = select,
     * a second click on the same row = toggle/cycle/edit).
     */
    private fun handleDashboardMouse(state: TuiAppState, event: TuiEvent.MousePressed) {
        val layout = DashboardLayout.dashboard(state.shell.width, state.shell.height)
        if (DashboardLayout.dashboardRegion(layout, event.x) == DashboardLayout.Region.ANALYSIS_HUB) {
            dispatch(TuiEvent.FocusPanelRequested(FocusPanel.ANALYSIS_HUB))
            return
        }
        dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))

        val rowIndex = DashboardLayout.treeRowIndex(layout, event.y, state.topology.treeScrollOffset)
        if (rowIndex < 0) return

        val lines = treeLinesProvider(state.topology.expandedNodes)
        val node = lines.getOrNull(rowIndex)?.node ?: return
        if (rowIndex == state.topology.selectedTreeIdx) {
            // Second click on the same row toggles expand/collapse (or inspects a leaf).
            if (node.children.isNotEmpty()) {
                dispatch(TuiEvent.ToggleNodeExpanded(node.id))
            } else {
                effects.inspectNode(node)
                dispatch(TuiEvent.FocusPanelRequested(FocusPanel.ANALYSIS_HUB))
                dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.NODE_DETAIL))
            }
        } else {
            dispatch(TuiEvent.SetSelectedTreeIdx(rowIndex))
            dispatch(TuiEvent.SetTopologyAutoScroll(false))
        }
    }

    private fun handleConfigMouse(state: TuiAppState, event: TuiEvent.MousePressed) {
        dispatch(TuiEvent.FocusPanelRequested(FocusPanel.CONFIG))
        if (state.config.isEditingSetting) return

        val layout = DashboardLayout.config(state.shell.width, state.shell.height)
        val rowIndex = DashboardLayout.configRowIndex(layout, event.y)
        if (rowIndex < 0) return

        if (DashboardLayout.configSide(layout, event.x) == DashboardLayout.ConfigSide.DOMAINS) {
            // DOMAINS sub-panel.
            if (state.config.activeSubPanel != ConfigSubPanel.DOMAINS) {
                dispatch(TuiEvent.SetConfigSubPanel(ConfigSubPanel.DOMAINS))
            }
            val domains = availableDomainsProvider()
            domains.getOrNull(rowIndex)?.let { (name, _) ->
                if (rowIndex == state.config.selectedDomainIdx) {
                    dispatch(TuiEvent.ToggleSelectedDomain(name))
                } else {
                    dispatch(TuiEvent.SetSelectedDomainIdx(rowIndex))
                }
            }
        } else {
            // SETTINGS sub-panel.
            if (state.config.activeSubPanel != ConfigSubPanel.SETTINGS) {
                dispatch(TuiEvent.SetConfigSubPanel(ConfigSubPanel.SETTINGS))
            }
            val items = settingItemsProvider()
            if (rowIndex in items.indices) {
                if (rowIndex == state.config.selectedSettingIdx) {
                    dispatch(TuiEvent.ActivateSelectedSetting)
                } else {
                    dispatch(TuiEvent.SetSelectedSettingIdx(rowIndex))
                }
            }
        }
    }

    private fun handleWelcomeMouse(event: TuiEvent.MousePressed) {
        val state = _state.value
        val layout = DashboardLayout.welcome(state.shell.width, state.shell.height)
        val menuIdx = DashboardLayout.welcomeMenuIndex(
            layout, event.y, state.snapshot.snapshotList.size
        )
        when {
            menuIdx < 0 -> Unit
            menuIdx == 0 -> {
                dispatch(TuiEvent.SelectWelcomeIndex(0))
                dispatch(TuiEvent.EnterConfigSetup)
            }
            else -> {
                val snapIndex = menuIdx - 1
                dispatch(TuiEvent.SelectWelcomeIndex(menuIdx))
                dispatch(TuiEvent.RequestLoadSnapshot(state.snapshot.snapshotList[snapIndex].id))
            }
        }
    }

    private fun handleMouseDragged(event: TuiEvent.MouseDragged) {
        val dragging = _state.value.shell.draggingScrollbar ?: return
        dispatch(scrollController.dragTo(dragging, event.y))
    }

    private fun isTextInputActive(state: TuiAppState): Boolean {
        return state.snapshot.isRenamingSnapshot ||
                state.snapshot.isSavingSnapshot ||
                state.config.isEditingSetting ||
                state.analysis.isEnteringBatchGenerality ||
                state.arena.isEnteringArenaQuestionId ||
                state.arena.isEnteringArenaQuery ||
                state.arena.isEnteringArenaModelA ||
                state.arena.isEnteringArenaModelB ||
                state.trickle.isEnteringTrickleQuery ||
                state.benchmark.isEditingBenchmarkField
    }
}