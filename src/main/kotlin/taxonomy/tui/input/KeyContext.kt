package taxonomy.tui.input

/**
 * Represents the currently focused semantic area of the application.
 * Controllers use this to decide if they should handle a dispatched action.
 */
enum class KeyContext {
    WELCOME,

    // Config Focus
    CONFIG_DOMAINS,
    CONFIG_SETTINGS,

    // Topology Focus
    TOPOLOGY_TREE,
    TOPOLOGY_LIST,

    // Analysis Hub Focus
    ANALYSIS_IDLE,
    ANALYSIS_SNAPSHOTS,
    ANALYSIS_INSPECTOR,
    ANALYSIS_METRICS,
    ANALYSIS_ARENA,
    ANALYSIS_BENCHMARK,
    ANALYSIS_TRICKLE,

    // Logs Focus
    SYSTEM_LOGS
}