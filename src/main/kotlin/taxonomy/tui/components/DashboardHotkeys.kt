package taxonomy.tui.components

import taxonomy.tui.state.FocusPanel

/**
 * Pure builder for the main-dashboard contextual hotkey hints. Extracted from the router so the
 * gating rules (which keys are advertised in which state) are unit-testable.
 */
object DashboardHotkeys {
    fun forState(
        hasDag: Boolean,
        focused: FocusPanel,
        isRegenerating: Boolean,
    ): List<HotkeyAction> {
        // While the DAG is still building, the analysis actions are not usable yet.
        if (isRegenerating) {
            return listOf(
                HotkeyAction("\u25cc", "Building DAG", TuiTheme.RUNNING),
                HotkeyAction("Esc", "Cancel", TuiTheme.ERROR),
                HotkeyAction("Ctrl-C", "Quit", TuiTheme.ERROR),
            )
        }
        if (!hasDag) {
            return listOf(
                HotkeyAction("X", "Welcome / New DAG", TuiTheme.ACCENT, isPrimary = true),
                HotkeyAction("Tab", "Switch Panels"),
                HotkeyAction("Ctrl-C", "Quit", TuiTheme.ERROR),
            )
        }
        if (focused == FocusPanel.TOPOLOGY) {
            return listOf(
                HotkeyAction("W/S", "Navigate", TuiTheme.ACCENT),
                HotkeyAction("\u2192/\u2190", "Expand/Collapse"),
                HotkeyAction("Space", "Toggle"),
                HotkeyAction("Enter", "Inspect"),
                HotkeyAction("Tab", "Switch Panels"),
                HotkeyAction("Ctrl-C", "Quit", TuiTheme.ERROR),
            )
        }
        return listOf(
            HotkeyAction("Tab", "Switch Panels", TuiTheme.ACCENT),
            HotkeyAction("M", "Metrics"),
            HotkeyAction("A", "Arena"),
            HotkeyAction("B", "Benchmark"),
            HotkeyAction("T", "Trickle"),
            HotkeyAction("N", "Save Snapshot"),
            HotkeyAction("X", "Welcome", TuiTheme.ACCENT),
            HotkeyAction("Ctrl-C", "Quit", TuiTheme.ERROR),
        )
    }
}
