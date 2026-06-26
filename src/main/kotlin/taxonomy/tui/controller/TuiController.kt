package taxonomy.tui.controller

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import taxonomy.service.AnalysisMode
import taxonomy.tui.components.SettingItem
import taxonomy.tui.components.StartupState
import taxonomy.tui.state.ConfigSubPanel
import taxonomy.tui.state.FocusPanel
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
) {

    private val _state = MutableStateFlow(initialState)
    val state: StateFlow<TuiAppState> = _state.asStateFlow()

    init {
        dispatch(TuiEvent.RefreshSnapshots)
        dispatch(TuiEvent.RefreshDatasetStatus)
        dispatch(TuiEvent.RefreshArenaModels)
    }

    fun dispatch(event: TuiEvent) {
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
            StartupState.WELCOME -> handleWelcomeKeys(state, key)
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
                }
            }
        }
    }

    private fun handleConfigKeys(state: TuiAppState, key: String) {
        if (state.shell.focusedPanel == FocusPanel.SYSTEM_LOGS) {
            when (key) {
                "w", "z", "arrowup" ->
                    dispatch(TuiEvent.SetLogsScroll((state.logs.logScrollOffset + 1).coerceAtLeast(0)))

                "s", "arrowdown" ->
                    dispatch(TuiEvent.SetLogsScroll((state.logs.logScrollOffset - 1).coerceAtLeast(0)))

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
            "arrowdown" -> dispatch(TuiEvent.FocusPanelRequested(FocusPanel.SYSTEM_LOGS))
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
            "escape", "q" -> dispatch(TuiEvent.CancelEditingSetting)
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

        when (key) {
            "tab" -> dispatch(focusController.cycleForward(state))
            "x" -> dispatch(TuiEvent.ReturnToWelcome)
            "m" -> dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.METRICS))
            // Arena and Benchmark are gated on a loaded precomputed eval roster. Without it
            // there are no model answers to judge, so we surface the metrics view (which shows
            // the "load eval_results" hint) instead of dropping the user into an empty arena.
            "a" -> if (state.arena.loadedModels.isNotEmpty()) {
                commandController.startArena(::dispatch)
            } else {
                dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.ARENA))
            }
            "b" -> if (state.arena.loadedModels.isNotEmpty()) {
                commandController.startBenchmark(::dispatch)
            } else {
                dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.BENCHMARK))
            }
            "t" -> commandController.startTrickle(::dispatch)

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
                } else {
                    dispatch(TuiEvent.StartSaveSnapshot)
                }
            }

            "v" -> dispatch(TuiEvent.ToggleAsciiTree)
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
                if (state.topology.showAsciiTree) {
                    dispatch(TuiEvent.SetSelectedTreeIdx((state.topology.selectedTreeIdx - 1).coerceAtLeast(0)))
                } else {
                    dispatch(TuiEvent.SetSelectedListIdx((state.topology.selectedListIdx - 1).coerceAtLeast(0)))
                }
                dispatch(TuiEvent.SetTopologyAutoScroll(false))
            }

            "s", "arrowdown" -> {
                if (state.topology.showAsciiTree) {
                    dispatch(TuiEvent.SetSelectedTreeIdx(state.topology.selectedTreeIdx + 1))
                } else {
                    dispatch(TuiEvent.SetSelectedListIdx(state.topology.selectedListIdx + 1))
                }
                dispatch(TuiEvent.SetTopologyAutoScroll(false))
            }

            "enter", " " -> {
                dispatch(TuiEvent.FocusPanelRequested(FocusPanel.ANALYSIS_HUB))
                dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.NODE_DETAIL))
            }

            "q", "escape" -> dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
        }
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

            AnalysisMode.METRICS -> when (key) {
                "w", "z", "arrowup" ->
                    dispatch(TuiEvent.SetMetricsScroll((state.analysis.metricsScrollOffset - 1).coerceAtLeast(0)))

                "s", "arrowdown" ->
                    dispatch(TuiEvent.SetMetricsScroll(state.analysis.metricsScrollOffset + 1))

                "q", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
            }

            AnalysisMode.SNAPSHOTS -> handleSnapshotKeys(state, key)

            AnalysisMode.TRICKLE_TEST -> when (key) {
                "w", "z", "arrowup" ->
                    dispatch(TuiEvent.SetBatchTrickleScrollOffset((state.trickle.batchTrickleScrollOffset - 1).coerceAtLeast(0)))

                "s", "arrowdown" ->
                    dispatch(TuiEvent.SetBatchTrickleScrollOffset(state.trickle.batchTrickleScrollOffset + 1))

                "q", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
            }

            AnalysisMode.BENCHMARK -> when (key) {
                "w", "z", "arrowup" ->
                    dispatch(TuiEvent.SetBenchmarkScrollOffset((state.benchmark.benchmarkScrollOffset - 1).coerceAtLeast(0)))

                "s", "arrowdown" ->
                    dispatch(TuiEvent.SetBenchmarkScrollOffset(state.benchmark.benchmarkScrollOffset + 1))

                "enter" -> dispatch(TuiEvent.RunBenchmark)
                "o" -> dispatch(TuiEvent.RunEvalLoad)

                "q", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
            }

            else -> when (key) {
                "q", "escape", "arrowleft", "backspace" ->
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
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
                dispatch(TuiEvent.SetLogsScroll((state.logs.logScrollOffset + 1).coerceAtLeast(0)))

            "s", "arrowdown" ->
                dispatch(TuiEvent.SetLogsScroll((state.logs.logScrollOffset - 1).coerceAtLeast(0)))

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
            StartupState.WELCOME -> handleWelcomeMouse(event)
            StartupState.CONFIGANDDOMAINS -> handleConfigMouse(state, event)
            StartupState.MAINDASHBOARD -> {
                if (event.x < 60) {
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY))
                } else {
                    dispatch(TuiEvent.FocusPanelRequested(FocusPanel.ANALYSIS_HUB))
                }
            }
            StartupState.LOADING -> Unit
        }
    }

    /**
     * Mouse in the config screen: choose the DOMAINS or SETTINGS sub-panel by x,
     * select the row under the cursor by y, and toggle/activate it (click = select,
     * a second click on the same row = toggle/cycle/edit).
     */
    private fun handleConfigMouse(state: TuiAppState, event: TuiEvent.MousePressed) {
        dispatch(TuiEvent.FocusPanelRequested(FocusPanel.CONFIG))
        if (state.config.isEditingSetting) return

        // Header (2) + HRule (1) + panel title (1) + spacer (1) ≈ first content row at y=5.
        val firstRowY = 5
        val rowIndex = (event.y - firstRowY).coerceAtLeast(-1)
        if (rowIndex < 0) return

        val leftWidth = (state.shell.width * 0.35).toInt().coerceAtLeast(20)
        if (event.x < leftWidth) {
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

        if (event.y <= 8) {
            dispatch(TuiEvent.SelectWelcomeIndex(0))
            dispatch(TuiEvent.EnterConfigSetup)
            return
        }

        val snapIndex = event.y - 12
        if (snapIndex in state.snapshot.snapshotList.indices) {
            dispatch(TuiEvent.SelectWelcomeIndex(snapIndex + 1))
            dispatch(TuiEvent.RequestLoadSnapshot(state.snapshot.snapshotList[snapIndex].id))
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