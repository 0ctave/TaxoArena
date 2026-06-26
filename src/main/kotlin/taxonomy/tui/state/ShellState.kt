package taxonomy.tui.state

data class ShellState(
    val width: Int = 0,
    val height: Int = 0,
    val focusedPanel: FocusPanel = FocusPanel.TOPOLOGY,
    val spinnerTick: Int = 0,
    val draggingScrollbar: ScrollbarTarget? = null
)

enum class FocusPanel {
    TOPOLOGY,
    ANALYSIS_HUB,
    SYSTEM_LOGS,
    CONFIG
}

enum class ConfigSubPanel {
    DOMAINS,
    SETTINGS
}

enum class ScrollbarTarget {
    TOPOLOGY,
    CONFIG_DOMAINS,
    ANALYSIS,
    LOGS
}