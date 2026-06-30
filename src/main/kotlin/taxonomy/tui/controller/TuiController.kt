package taxonomy.tui.controller

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import taxonomy.tui.app.DashboardLayout
import taxonomy.tui.components.SettingItem
import taxonomy.tui.components.TreeLine
import taxonomy.tui.components.StartupState
import taxonomy.tui.controller.keys.AnalysisKeyHandler
import taxonomy.tui.controller.keys.ConfigKeyHandler
import taxonomy.tui.controller.keys.MainDashboardKeyHandler
import taxonomy.tui.controller.keys.TopologyKeyHandler
import taxonomy.tui.controller.keys.WelcomeKeyHandler
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
            is TuiEvent.MouseReleased -> dispatch(TuiEvent.StopDraggingScrollbar)
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
}
