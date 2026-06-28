package taxonomy.tui.components

import taxonomy.tui.state.TuiAppState

/**
 * Persistent, state-independent hotkeys shown in the global section of every [HotkeyBar].
 * These are always available regardless of which panel or mode holds focus.
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

    /** Version that doesn't need app-state; used by screens with no active graph context. */
    val always: List<HotkeyAction> = listOf(
        HotkeyAction("Tab", "Switch Panels"),
        HotkeyAction("?", "Help", TuiTheme.ACCENT),
        HotkeyAction("Ctrl-C", "Quit", TuiTheme.ERROR),
    )
}
