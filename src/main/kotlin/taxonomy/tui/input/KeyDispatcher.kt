package taxonomy.tui.input

/**
 * Dispatch contract for feature-specific keyboard controllers.
 *
 * A controller should return true when it handled the action for the current context.
 */
interface KeyController {
    fun handleKeyAction(context: KeyContext, action: KeyAction): Boolean
}

/**
 * Global keyboard dispatcher that:
 * 1. Maps raw terminal keys to semantic KeyAction values via Keymap.
 * 2. Resolves the current semantic KeyContext from app/UI state.
 * 3. Broadcasts the action to registered controllers until one handles it.
 *
 * This keeps raw key parsing out of feature controllers and gives you one place
 * to define routing semantics that match the dashboard structure.
 */
class KeyDispatcher(
    private val controllers: List<KeyController>
) {

    /**
     * Minimal app state needed to resolve where a key should be routed.
     *
     * Keep this intentionally semantic rather than leaking every UI flag.
     */
    data class State(
        val startupState: StartupStateLike,
        val focusedRegion: PanelRegion = PanelRegion.TOPOLOGY,

        val activeConfigPanel: ConfigPanelLike = ConfigPanelLike.DOMAINS,

        val topologyView: TopologyViewLike = TopologyViewLike.TREE,

        val analysisMode: AnalysisModeLike = AnalysisModeLike.IDLE,

        val isEditingSetting: Boolean = false,
        val isSavingSnapshot: Boolean = false,
        val isRenamingSnapshot: Boolean = false,

        val isEnteringArenaQuery: Boolean = false,
        val isEnteringArenaModelA: Boolean = false,
        val isEnteringArenaModelB: Boolean = false,

        val isEnteringTrickleQuery: Boolean = false,

        val isEditingBenchmarkField: Boolean = false,
        val isEnteringBatchGenerality: Boolean = false
    ) {
        val isTextInputActive: Boolean
            get() = isEditingSetting ||
                    isSavingSnapshot ||
                    isRenamingSnapshot ||
                    isEnteringArenaQuery ||
                    isEnteringArenaModelA ||
                    isEnteringArenaModelB ||
                    isEnteringTrickleQuery ||
                    isEditingBenchmarkField ||
                    isEnteringBatchGenerality
    }

    /**
     * Entry point for raw terminal keys.
     */
    fun dispatchRawKey(rawKey: String, state: State): Boolean {
        val action = Keymap.map(rawKey = rawKey, isTextInputActive = state.isTextInputActive)
            ?: return false

        val context = resolveContext(state)
        return dispatch(context, action)
    }

    /**
     * Entry point if something upstream has already mapped the raw key.
     */
    fun dispatch(action: KeyAction, state: State): Boolean {
        val context = resolveContext(state)
        return dispatch(context, action)
    }

    /**
     * Direct dispatch with an already resolved context.
     */
    fun dispatch(context: KeyContext, action: KeyAction): Boolean {
        for (controller in controllers) {
            if (controller.handleKeyAction(context, action)) return true
        }
        return false
    }

    /**
     * Central semantic routing table.
     */
    fun resolveContext(state: State): KeyContext {
        return when (state.startupState) {
            StartupStateLike.WELCOME -> KeyContext.WELCOME

            StartupStateLike.LOADING -> {
                // Loading usually swallows input upstream, but if anything reaches
                // the dispatcher route it to welcome-style/global handling.
                KeyContext.WELCOME
            }

            StartupStateLike.CONFIG_AND_DOMAINS -> {
                when (state.focusedRegion) {
                    PanelRegion.CONFIG_LEFT -> KeyContext.CONFIG_DOMAINS
                    PanelRegion.CONFIG_RIGHT -> KeyContext.CONFIG_SETTINGS
                    PanelRegion.SYSTEM_LOGS -> KeyContext.SYSTEM_LOGS
                    else -> {
                        if (state.activeConfigPanel == ConfigPanelLike.DOMAINS) {
                            KeyContext.CONFIG_DOMAINS
                        } else {
                            KeyContext.CONFIG_SETTINGS
                        }
                    }
                }
            }

            StartupStateLike.MAIN_DASHBOARD -> {
                when (state.focusedRegion) {
                    PanelRegion.TOPOLOGY -> {
                        when (state.topologyView) {
                            TopologyViewLike.TREE -> KeyContext.TOPOLOGY_TREE
                            TopologyViewLike.LIST -> KeyContext.TOPOLOGY_LIST
                        }
                    }

                    PanelRegion.ANALYSIS_HUB -> {
                        when {
                            state.isSavingSnapshot || state.isRenamingSnapshot ->
                                KeyContext.ANALYSIS_SNAPSHOTS

                            state.isEditingSetting ->
                                KeyContext.ANALYSIS_IDLE

                            state.isEnteringArenaQuery ||
                                    state.isEnteringArenaModelA ||
                                    state.isEnteringArenaModelB ->
                                KeyContext.ANALYSIS_ARENA

                            state.isEnteringTrickleQuery ->
                                KeyContext.ANALYSIS_TRICKLE

                            state.isEditingBenchmarkField ->
                                KeyContext.ANALYSIS_BENCHMARK

                            state.isEnteringBatchGenerality ->
                                KeyContext.ANALYSIS_IDLE

                            else -> when (state.analysisMode) {
                                AnalysisModeLike.IDLE,
                                AnalysisModeLike.NODE_DETAIL,
                                AnalysisModeLike.SETTINGS,
                                AnalysisModeLike.CONFIG_PANEL,
                                AnalysisModeLike.LOGS_SCROLL,
                                AnalysisModeLike.JUDGE_PROGRESS -> KeyContext.ANALYSIS_IDLE

                                AnalysisModeLike.SNAPSHOTS -> KeyContext.ANALYSIS_SNAPSHOTS
                                AnalysisModeLike.METRICS -> KeyContext.ANALYSIS_METRICS
                                AnalysisModeLike.ARENA -> KeyContext.ANALYSIS_ARENA
                                AnalysisModeLike.BENCHMARK -> KeyContext.ANALYSIS_BENCHMARK
                                AnalysisModeLike.TRICKLE -> KeyContext.ANALYSIS_TRICKLE
                            }
                        }
                    }

                    PanelRegion.SYSTEM_LOGS,
                    PanelRegion.GPU_TRACES -> KeyContext.SYSTEM_LOGS

                    else -> {
                        // Sensible fallback based on currently active mode.
                        when (state.analysisMode) {
                            AnalysisModeLike.SNAPSHOTS -> KeyContext.ANALYSIS_SNAPSHOTS
                            AnalysisModeLike.METRICS -> KeyContext.ANALYSIS_METRICS
                            AnalysisModeLike.ARENA -> KeyContext.ANALYSIS_ARENA
                            AnalysisModeLike.BENCHMARK -> KeyContext.ANALYSIS_BENCHMARK
                            AnalysisModeLike.TRICKLE -> KeyContext.ANALYSIS_TRICKLE
                            else -> KeyContext.TOPOLOGY_TREE
                        }
                    }
                }
            }
        }
    }
}

/**
 * Small semantic enums so KeyDispatcher stays decoupled from the exact UI package
 * types used by the dashboard. You can either:
 * - use these directly in your state adapter, or
 * - add conversion helpers from your real enums/classes.
 */
enum class StartupStateLike {
    WELCOME,
    LOADING,
    CONFIG_AND_DOMAINS,
    MAIN_DASHBOARD
}

enum class ConfigPanelLike {
    DOMAINS,
    SETTINGS
}

enum class TopologyViewLike {
    TREE,
    LIST
}

enum class AnalysisModeLike {
    IDLE,
    NODE_DETAIL,
    SETTINGS,
    CONFIG_PANEL,
    LOGS_SCROLL,
    SNAPSHOTS,
    METRICS,
    ARENA,
    BENCHMARK,
    TRICKLE,
    JUDGE_PROGRESS
}
