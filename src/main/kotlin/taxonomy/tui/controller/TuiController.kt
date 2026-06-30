package taxonomy.tui.controller

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import taxonomy.service.AnalysisMode
import taxonomy.tui.app.DashboardLayout
import taxonomy.tui.components.SettingItem
import taxonomy.tui.components.TreeLine
import taxonomy.tui.components.StartupState
import taxonomy.tui.controller.keys.AnalysisKeyHandler
import taxonomy.tui.controller.keys.ConfigKeyHandler
import taxonomy.tui.controller.keys.MainDashboardKeyHandler
import taxonomy.tui.controller.keys.TopologyKeyHandler
import taxonomy.tui.controller.keys.WelcomeKeyHandler
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

    // ── Key handler delegates ───────────────────────────────────────────────────

    private val welcomeHandler = WelcomeKeyHandler()
    private val configHandler = ConfigKeyHandler(
        settingItemsProvider = settingItemsProvider,
        availableDomainsProvider = availableDomainsProvider,
    )
    private val topologyHandler = TopologyKeyHandler(
        treeLinesProvider = treeLinesProvider,
        effects = effects,
    )
    private val analysisHandler = AnalysisKeyHandler(
        effects = effects,
        commandController = commandController,
        metricsHistorySizeProvider = metricsHistorySizeProvider,
    )
    private val dashboardHandler = MainDashboardKeyHandler(
        effects = effects,
        commandController = commandController,
        focusController = focusController,
        configHandler = configHandler,
        topologyHandler = topologyHandler,
        analysisHandler = analysisHandler,
    )

    // ───────────────────────────────────────────────────────────────────

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
            is TuiEvent.KeyPressed    -> handleKeyPressed(event)
            is TuiEvent.MouseWheel    -> handleMouseWheel(event)
            is TuiEvent.MousePressed  -> handleMousePressed(event)
            is TuiEvent.MouseReleased -> dispatch(TuiEvent.StopDraggingScrollbar)
            is TuiEvent.MouseDragged  -> handleMouseDragged(event)
            else -> Unit
        }
    }

    // ── Key routing ───────────────────────────────────────────────────────────

    private fun handleKeyPressed(event: TuiEvent.KeyPressed) {
        val state = _state.value
        val key   = event.key.lowercase()

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
            StartupState.LOAD_DAG         -> welcomeHandler.handle(state, key, ::dispatch)
            StartupState.CONFIGANDDOMAINS -> configHandler.handle(state, key, ::dispatch)
            StartupState.MAINDASHBOARD    -> dashboardHandler.handle(state, key, ::dispatch)
            StartupState.LOADING          -> Unit
        }
    }

    // ── Mouse ──────────────────────────────────────────────────────────────────

    private fun handleMouseWheel(event: TuiEvent.MouseWheel) {
        val scrollEvent = when (event.direction) {
            WheelDirection.Up   -> scrollController.scrollUp(_state.value)
            WheelDirection.Down -> scrollController.scrollDown(_state.value)
        }
        scrollEvent?.let { dispatch(it) }
    }

    private fun handleMousePressed(event: TuiEvent.MousePressed) {
        val state = _state.value
        when (state.startup.state) {
            StartupState.LOAD_DAG         -> handleWelcomeMouse(event)
            StartupState.CONFIGANDDOMAINS -> handleConfigMouse(state, event)
            StartupState.MAINDASHBOARD    -> handleDashboardMouse(state, event)
            StartupState.LOADING          -> Unit
        }
    }

    /**
     * Dashboard mouse: clicking the analysis-hub column focuses it; clicking anywhere in
     * the topology column focuses the topology panel and selects / toggles the clicked row.
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
        val node  = lines.getOrNull(rowIndex)?.node ?: return
        if (rowIndex == state.topology.selectedTreeIdx) {
            // Second click on the same row: toggle expand/collapse or inspect a leaf.
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

    /**
     * Config mouse: click focuses CONFIG, selects the clicked domain or setting row,
     * and a second click on the same row toggles/activates it.
     */
    private fun handleConfigMouse(state: TuiAppState, event: TuiEvent.MousePressed) {
        dispatch(TuiEvent.FocusPanelRequested(FocusPanel.CONFIG))
        if (state.config.isEditingSetting) return

        val layout   = DashboardLayout.config(state.shell.width, state.shell.height)
        val rowIndex = DashboardLayout.configRowIndex(layout, event.y)
        if (rowIndex < 0) return

        if (DashboardLayout.configSide(layout, event.x) == DashboardLayout.ConfigSide.DOMAINS) {
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

    /**
     * Welcome mouse: clicking a menu row immediately selects and activates it
     * (new DAG = row 0, existing snapshot = row n).
     */
    private fun handleWelcomeMouse(event: TuiEvent.MousePressed) {
        val state  = _state.value
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
}
