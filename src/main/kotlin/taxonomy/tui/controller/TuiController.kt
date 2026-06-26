package taxonomy.tui.controller

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import taxonomy.service.AnalysisMode
import taxonomy.tui.components.StartupState
import taxonomy.tui.state.ConfigSubPanel
import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.TuiAppState

class TuiController(
    initialState: TuiAppState = TuiAppState(),
    private val effects: TuiEffects,
    private val focusController: FocusController = FocusController(),
    private val scrollController: ScrollController = ScrollController(),
    private val commandController: CommandController = CommandController(effects)
) {

    private val _state = MutableStateFlow(initialState)
    val state: StateFlow<TuiAppState> = _state.asStateFlow()

    init {
        dispatch(TuiEvent.RefreshSnapshots)
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

            "enter", " " -> {
                if (state.config.activeSubPanel == ConfigSubPanel.SETTINGS) {
                    dispatch(TuiEvent.StartEditingSetting())
                }
            }

            "d" -> dispatch(TuiEvent.StartDatasetDownload)
            "r" -> dispatch(TuiEvent.EnterMainDashboard)
            "arrowdown" -> dispatch(TuiEvent.FocusPanelRequested(FocusPanel.SYSTEM_LOGS))
            "escape", "q" -> dispatch(TuiEvent.ReturnToWelcome)
        }
    }

    private fun handleSettingEditorKeys(state: TuiAppState, key: String) {
        when (key) {
            "enter" -> dispatch(TuiEvent.ConfirmEditingSetting)
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
            "a" -> commandController.startArena(::dispatch)
            "b" -> commandController.startBenchmark(::dispatch)
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
                dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.NODEDETAIL))
            }

            "q", "escape" -> dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
        }
    }

    private fun handleAnalysisKeys(state: TuiAppState, key: String) {
        when (state.analysis.mode) {
            AnalysisMode.NODEDETAIL -> when (key) {
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

            AnalysisMode.TRICKLETEST -> when (key) {
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
            StartupState.CONFIGANDDOMAINS -> dispatch(TuiEvent.FocusPanelRequested(FocusPanel.CONFIG))
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
                state.arena.isEnteringArenaQuery ||
                state.arena.isEnteringArenaModelA ||
                state.arena.isEnteringArenaModelB ||
                state.trickle.isEnteringTrickleQuery ||
                state.benchmark.isEditingBenchmarkField
    }
}