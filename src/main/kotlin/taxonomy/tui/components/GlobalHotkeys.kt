package taxonomy.tui.components

import taxonomy.tui.state.TuiAppState

/**
 * Persistent, state-independent hotkeys shown on the right side of every [HotkeyBar]. These
 * are always available regardless of which panel or mode holds focus, so feature-specific
 * builders no longer advertise them (see [DashboardHotkeys]).
 */
object GlobalHotkeys {
    fun forState(state: TuiAppState): List<HotkeyAction> = buildList {
        add(HotkeyAction("Tab", "Switch Panels"))
        add(HotkeyAction("?", "Help", TuiTheme.ACCENT))
        // X reloads / loads a DAG; only meaningful once a graph is active (otherwise the
        // contextual bar surfaces X as the primary "get started" action).
        if (state.runtime.hasActiveGraph) add(HotkeyAction("X", "Load DAG"))
        add(HotkeyAction("Ctrl-C", "Quit", TuiTheme.ERROR))
    }
}
