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
import taxonomy.tui.state.BenchmarkSection
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

        if (state.shell.helpOverlayOpen) {
            if (key == "?" || key == "escape") dispatch(TuiEvent.ToggleHelpOverlay)
            return
        }
        if (key == "?") {
            dispatch(TuiEvent.ToggleHelpOverlay)
            return
        }

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
                    dispatch(TuiEvent.QuitRequested)
                }
            }
        }
    }

    private fun handleConfigKeys(state: TuiAppState, key: String) {
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
                    dispatch(TuiEvent.ActivateSelectedSetting)
                }
            }

            "d" -> dispatch(TuiEvent.PromptDatasetDownload)
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
                val item = settingItemsProvider().getOrNull(state.config.selectedSettingIdx)
                if (item != null) {
                    dispatch(TuiEvent.ApplySetting(item.name, state.config.editingValue))
                }
                dispatch(TuiEvent.ConfirmEditingSetting)
            }
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
        if (state.benchmark.isPickingEvalCatalog) {
            handleEvalCatalogPickerKeys(state, key)
            return
        }
        if (state.benchmark.benchmarkIsPickingModels || state.benchmark.benchmarkIsPickingDomains) {
            handleBenchmarkPickerKeys(state, key)
            return
        }
        if (isTextInputActive(state)) {
            handleActiveTextInput(state, key)
            return
        }
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
            "a" -> {
                effects.loadArenaModels(::dispatch)
                if (state.arena.loadedModels.isNotEmpty()) {
                    commandController.startArena(::dispatch)
                } else {
                    dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.ARENA))
                }
            }
            // "b" on the TRICKLE type: if already entered the input screen, confirm and run.
            // If not yet on the input screen, open it (resolving the pool size first).
            "b" -> if (state.analysis.mode == AnalysisMode.BENCHMARK &&
                state.benchmark.benchmarkType == BenchmarkType.TRICKLE
            ) {
                when {
                    state.benchmark.isRunningBatchTrickleTest -> Unit
                    state.benchmark.isEnteringTrickleQueryLimit -> {
                        // Confirm with current input value.
                        val maxQ = state.benchmark.trickleQueryLimitInput.toIntOrNull() ?: 0
                        dispatch(TuiEvent.RunBatchTrickleTest(maxQ))
                    }
                    else -> {
                        // Open the input panel pre-filled with the pool size.
                        effects.resolveReservedPoolSize { poolSize ->
                            dispatch(TuiEvent.StartTrickleBenchmarkInput(poolSize))
                        }
                    }
                }
            } else {
                commandController.startBenchmark(::dispatch)
            }
            "t" -> commandController.startTrickle(::dispatch)

            "o" -> if (state.analysis.mode == AnalysisMode.BENCHMARK ||
                state.analysis.mode == AnalysisMode.ARENA
            ) {
                dispatch(TuiEvent.OpenEvalCatalogPicker)
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
                effects.inspectNode(selectedTreeNode(state))
                dispatch(TuiEvent.FocusPanelRequested(FocusPanel.ANALYSIS_HUB))
                dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.NODE_DETAIL))
            }

            "r" -> selectedTreeNode(state)?.let { node ->
                effects.inspectNode(node)
                dispatch(TuiEvent.FocusPanelRequested(FocusPanel.ANALYSIS_HUB))
                dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.NODE_DETAIL))
                dispatch(TuiEvent.SetGeneratingJudge(true))
                effects.regenerateJudgeForCurrentNode(::dispatch)
            }

            "q", "escape" -> dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
        }
    }

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

                "r" -> {
                    dispatch(TuiEvent.SetGeneratingJudge(true))
                    effects.regenerateJ