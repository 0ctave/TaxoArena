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
import taxonomy.model.GraphNode
import taxonomy.tui.components.ScrollBarDragManager
import taxonomy.tui.input.HitTesting
import taxonomy.tui.input.PanelRegion
import taxonomy.tui.state.ScrollbarTarget
import taxonomy.tui.state.MetricsZoneFocus
import taxonomy.utils.TuiLogAppender

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
    private val selectedNodeProvider: () -> GraphNode? = { null },
    private val metricsHistoryProvider: () -> List<taxonomy.model.IterationMetrics> = { emptyList() },
    private val performanceReportProvider: () -> Map<String, taxonomy.utils.PerformanceStats> = { emptyMap() },
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
        availableDomainsProvider = availableDomainsProvider,
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
        effects.loadLeafRanks(::dispatch)
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
        val scrollbarBounds = detectScrollbarClickAndTarget(state, event.x, event.y)
        if (scrollbarBounds != null) {
            dispatch(TuiEvent.StartDraggingScrollbar(scrollbarBounds.target))
            val newOffset = ScrollBarDragManager.calculateScrollTarget(
                clickY = event.y,
                trackStartY = scrollbarBounds.trackStartY,
                visibleItems = scrollbarBounds.visibleItems,
                totalItems = scrollbarBounds.totalItems,
                reversed = scrollbarBounds.reversed
            )
            dispatch(TuiEvent.ScrollTo(scrollbarBounds.target, newOffset))
            return
        }

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
        val state = _state.value
        val dragging = state.shell.draggingScrollbar ?: return
        val bounds = getScrollbarBounds(state, dragging) ?: return
        val newOffset = ScrollBarDragManager.calculateScrollTarget(
            clickY = event.y,
            trackStartY = bounds.trackStartY,
            visibleItems = bounds.visibleItems,
            totalItems = bounds.totalItems,
            reversed = bounds.reversed
        )
        dispatch(TuiEvent.ScrollTo(dragging, newOffset))
    }

    private data class ScrollbarTargetBounds(
        val target: ScrollbarTarget,
        val trackStartY: Int,
        val visibleItems: Int,
        val totalItems: Int,
        val reversed: Boolean = false
    )

    private fun detectScrollbarClickAndTarget(state: TuiAppState, x: Int, y: Int): ScrollbarTargetBounds? {
        val layout = HitTesting.LayoutMetrics(
            width = state.shell.width,
            height = state.shell.height,
            isConfigMode = state.startup.state == StartupState.CONFIGANDDOMAINS
        )
        val region = HitTesting.getRegionForCoordinate(x, y, layout)
        if (region == PanelRegion.OUT_OF_BOUNDS) return null

        val endX = when (region) {
            PanelRegion.TOPOLOGY -> layout.dagWidth
            PanelRegion.ANALYSIS_HUB -> layout.width
            PanelRegion.CONFIG_LEFT -> layout.configLeftWidth
            PanelRegion.CONFIG_RIGHT -> layout.width
            PanelRegion.SYSTEM_LOGS -> layout.logsWidth
            PanelRegion.GPU_TRACES -> layout.width
            else -> return null
        }
        if (x !in (endX - 3)..<endX) return null

        val target = when (region) {
            PanelRegion.TOPOLOGY -> ScrollbarTarget.TOPOLOGY
            PanelRegion.CONFIG_LEFT -> ScrollbarTarget.CONFIG_DOMAINS
            PanelRegion.SYSTEM_LOGS -> ScrollbarTarget.LOGS
            PanelRegion.ANALYSIS_HUB -> ScrollbarTarget.ANALYSIS
            else -> return null
        }

        if (target == ScrollbarTarget.ANALYSIS && state.analysis.mode == AnalysisMode.METRICS) {
            val bodyH = (layout.topHeight - 2).coerceAtLeast(1)
            val zone1H = (bodyH * 0.4).toInt().coerceIn(4, (bodyH - 4).coerceAtLeast(4))
            val tableEndY = layout.topRowStartY + zone1H - 1
            val focus = if (y <= tableEndY) MetricsZoneFocus.TABLE else MetricsZoneFocus.DETAIL
            dispatch(TuiEvent.SetMetricsZoneFocus(focus))
        }

        return getScrollbarBounds(_state.value, target)
    }

    private fun getScrollbarBounds(state: TuiAppState, target: ScrollbarTarget): ScrollbarTargetBounds? {
        val layout = HitTesting.LayoutMetrics(
            width = state.shell.width,
            height = state.shell.height,
            isConfigMode = state.startup.state == StartupState.CONFIGANDDOMAINS
        )
        return when (target) {
            ScrollbarTarget.TOPOLOGY -> {
                val visible = (layout.topHeight - 2).coerceAtLeast(1)
                if (state.topology.showDomainSelector) {
                    val domains = availableDomainsProvider()
                    ScrollbarTargetBounds(
                        target = target,
                        trackStartY = layout.topRowStartY + 1,
                        visibleItems = visible,
                        totalItems = domains.size
                    )
                } else {
                    val lines = treeLinesProvider(state.topology.expandedNodes)
                    ScrollbarTargetBounds(
                        target = target,
                        trackStartY = layout.topRowStartY + 2,
                        visibleItems = (visible - 1).coerceAtLeast(1),
                        totalItems = lines.size
                    )
                }
            }
            ScrollbarTarget.CONFIG_DOMAINS -> {
                val domains = availableDomainsProvider()
                val visible = (layout.topHeight - 2).coerceAtLeast(1)
                ScrollbarTargetBounds(
                    target = target,
                    trackStartY = layout.topRowStartY + 1,
                    visibleItems = visible,
                    totalItems = domains.size
                )
            }
            ScrollbarTarget.LOGS -> {
                val total = synchronized(TuiLogAppender.logs) { TuiLogAppender.logs.size }
                ScrollbarTargetBounds(
                    target = target,
                    trackStartY = layout.bottomRowStartY + 1,
                    visibleItems = (layout.bottomHeight - 2).coerceAtLeast(1),
                    totalItems = total,
                    reversed = true
                )
            }
            ScrollbarTarget.ANALYSIS -> {
                val bodyH = (layout.topHeight - 2).coerceAtLeast(1)
                when (state.analysis.mode) {
                    AnalysisMode.NODE_DETAIL -> {
                        val node = selectedNodeProvider() ?: return null
                        val isGeneratingJudge = state.arena.isGeneratingJudge
                        val items = taxonomy.tui.features.analysis.buildNodeDetailLines(node, layout.arenaWidth - 4, isGeneratingJudge)
                        ScrollbarTargetBounds(
                            target = target,
                            trackStartY = layout.topRowStartY + 1,
                            visibleItems = bodyH,
                            totalItems = items.size
                        )
                    }
                    AnalysisMode.CONFIG -> {
                        val config = state.snapshot.activeSnapshotConfig
                        if (config == null) null else {
                            ScrollbarTargetBounds(
                                target = target,
                                trackStartY = layout.topRowStartY + 1,
                                visibleItems = bodyH,
                                totalItems = 28
                            )
                        }
                    }
                    AnalysisMode.LEADERBOARD -> {
                        val items = state.arena.leaderboard.flatMap { g -> g.agents.map { g.rank to it } }
                        val rows = (bodyH - 4).coerceAtLeast(1)
                        ScrollbarTargetBounds(
                            target = target,
                            trackStartY = layout.topRowStartY + 4,
                            visibleItems = rows,
                            totalItems = items.size
                        )
                    }
                    AnalysisMode.SNAPSHOTS -> {
                        val bannerH = if (state.snapshot.isSavingSnapshot || state.snapshot.isRenamingSnapshot) 1 else 0
                        val visible = (bodyH - 2 - bannerH).coerceAtLeast(1)
                        ScrollbarTargetBounds(
                            target = target,
                            trackStartY = layout.topRowStartY + bannerH + 1,
                            visibleItems = visible,
                            totalItems = state.snapshot.snapshotList.size
                        )
                    }
                    AnalysisMode.BENCHMARK -> {
                        val domains = availableDomainsProvider()
                        ScrollbarTargetBounds(
                            target = target,
                            trackStartY = layout.topRowStartY + 1,
                            visibleItems = bodyH,
                            totalItems = domains.size
                        )
                    }
                    AnalysisMode.METRICS -> {
                        val history = metricsHistoryProvider()
                        if (history.isEmpty()) return null
                        val lastIdx = history.lastIndex
                        val zone1H = (bodyH * 0.4).toInt().coerceIn(4, (bodyH - 4).coerceAtLeast(4))

                        if (state.analysis.metricsZoneFocus == MetricsZoneFocus.TABLE) {
                            val visible = (zone1H - 4).coerceAtLeast(1)
                            ScrollbarTargetBounds(
                                target = target,
                                trackStartY = layout.topRowStartY + 2,
                                visibleItems = visible,
                                totalItems = lastIdx
                            )
                        } else {
                            val selResolved = if (state.analysis.selectedIterationIndex in 0..lastIdx) state.analysis.selectedIterationIndex else lastIdx
                            val entry = history[selResolved]
                            val lines = taxonomy.tui.features.analysis.buildMetricLines(entry.metrics).toMutableList()
                            if (state.analysis.showPerformanceBlock) {
                                lines += taxonomy.tui.features.analysis.performanceLines(performanceReportProvider())
                            }
                            val bottomH = (bodyH - zone1H).coerceAtLeast(4)
                            val body = (bottomH - 1).coerceAtLeast(1)
                            ScrollbarTargetBounds(
                                target = target,
                                trackStartY = layout.topRowStartY + zone1H + 1,
                                visibleItems = body,
                                totalItems = lines.size
                            )
                        }
                    }
                    else -> null
                }
            }
        }
    }
}
