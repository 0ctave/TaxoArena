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
            // Collapse is bound to \u2190/H only ('a' is consumed by the Arena shortcut at the
            // dashboard level), so advertise H/L to match what actually works.
            return listOf(
                HotkeyAction("W/S", "Navigate", TuiTheme.ACCENT),
                HotkeyAction("\u2192/L", "Expand"),
                HotkeyAction("\u2190/H", "Collapse"),
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
            HotkeyAction("G", "Generate Judges", TuiTheme.OK),
            HotkeyAction("F", "Force-Regen Judges", TuiTheme.RUNNING),
            HotkeyAction("E", "Export ASCII"),
            HotkeyAction("N", "Save Snapshot"),
            HotkeyAction("X", "Welcome", TuiTheme.ACCENT),
            HotkeyAction("Ctrl-C", "Quit", TuiTheme.ERROR),
        )
    }
}
