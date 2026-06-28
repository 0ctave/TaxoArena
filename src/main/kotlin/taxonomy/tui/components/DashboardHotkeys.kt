package taxonomy.tui.components

import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.TuiAppState

/**
 * Pure builder for the main-dashboard contextual hotkey hints. Extracted from the router so
 * the gating rules (which keys are advertised in which state) are unit-testable.
 *
 * When a snapshot is loaded (or a fresh DAG is generated) the bar looks like:
 *
 * ```
 * DAG : [M] Metrics [C] Config [T] Trickle | Arena : [A] Arena [G] Generate Judges | [B] Benchmark [Tab] Switch Panels [?] Help [X] Load DAG [Ctrl-C] Quit
 * ```
 *
 * On narrow terminals the bar wraps to additional rows automatically.
 */
object DashboardHotkeys {

    /**
     * Returns the full [HotkeyGroup] list to pass to the grouped [HotkeyBar] overload.
     * [globalState] supplies the state needed to build [GlobalHotkeys].
     */
    fun groups(
        hasDag: Boolean,
        focused: FocusPanel,
        isRegenerating: Boolean,
        isViewingSnapshot: Boolean = false,
        state: TuiAppState,
    ): List<HotkeyGroup> {
        // ── DAG is being built ───────────────────────────────────────────────
        if (isRegenerating) {
            return listOf(
                HotkeyGroup("", listOf(
                    HotkeyAction("◌", "Building DAG", TuiTheme.RUNNING),
                    HotkeyAction("Esc", "Cancel", TuiTheme.ERROR),
                )),
                HotkeyGroup("", GlobalHotkeys.forState(state)),
            )
        }

        // ── No DAG loaded ────────────────────────────────────────────────────
        if (!hasDag) {
            return listOf(
                HotkeyGroup("", listOf(
                    HotkeyAction("X", "Load DAG / New DAG", TuiTheme.ACCENT, isPrimary = true),
                )),
                HotkeyGroup("", GlobalHotkeys.forState(state)),
            )
        }

        // ── Topology panel focused ───────────────────────────────────────────
        if (focused == FocusPanel.TOPOLOGY) {
            return listOf(
                HotkeyGroup("DAG", listOf(
                    HotkeyAction("W/S", "Navigate", TuiTheme.ACCENT),
                    HotkeyAction("→/L", "Expand"),
                    HotkeyAction("←/H", "Collapse"),
                    HotkeyAction("Space", "Toggle"),
                    HotkeyAction("Enter", "Inspect"),
                    HotkeyAction("R", "Gen Judge", TuiTheme.OK),
                )),
                HotkeyGroup("", GlobalHotkeys.forState(state)),
            )
        }

        // ── Analysis hub focused — full grouped layout ───────────────────────
        val dagGroup = HotkeyGroup(
            label = "DAG",
            actions = listOf(
                HotkeyAction("M", "Metrics", TuiTheme.ACCENT),
                HotkeyAction("C", "Config"),
                HotkeyAction("T", "Trickle"),
            ),
        )
        val arenaActions = buildList {
            add(HotkeyAction("A", "Arena"))
            add(HotkeyAction("G", "Generate Judges", TuiTheme.OK))
            if (isViewingSnapshot) add(HotkeyAction("N", "Rename Snap"))
        }
        val arenaGroup = HotkeyGroup(label = "Arena", actions = arenaActions)

        val utilActions = buildList<HotkeyAction> {
            add(HotkeyAction("B", "Benchmark"))
        }
        val utilGroup = HotkeyGroup(label = "", actions = utilActions)

        return listOf(
            dagGroup,
            arenaGroup,
            utilGroup,
            HotkeyGroup("", GlobalHotkeys.forState(state)),
        )
    }

    /**
     * Legacy flat-list API kept for callers that already use the contextual/global split
     * [HotkeyBar] overload.  New call-sites should prefer [groups].
     */
    fun forState(
        hasDag: Boolean,
        focused: FocusPanel,
        isRegenerating: Boolean,
        isViewingSnapshot: Boolean = false,
    ): List<HotkeyAction> {
        if (isRegenerating) {
            return listOf(
                HotkeyAction("◌", "Building DAG", TuiTheme.RUNNING),
                HotkeyAction("Esc", "Cancel", TuiTheme.ERROR),
            )
        }
        if (!hasDag) {
            return listOf(
                HotkeyAction("X", "Load DAG / New DAG", TuiTheme.ACCENT, isPrimary = true),
            )
        }
        if (focused == FocusPanel.TOPOLOGY) {
            return listOf(
                HotkeyAction("W/S", "Navigate", TuiTheme.ACCENT),
                HotkeyAction("→/L", "Expand"),
                HotkeyAction("←/H", "Collapse"),
                HotkeyAction("Space", "Toggle"),
                HotkeyAction("Enter", "Inspect"),
                HotkeyAction("R", "Gen Judge", TuiTheme.OK),
            )
        }
        return buildList {
            add(HotkeyAction("M", "Metrics", TuiTheme.ACCENT))
            add(HotkeyAction("C", "Config"))
            add(HotkeyAction("T", "Trickle"))
            add(HotkeyAction("A", "Arena"))
            add(HotkeyAction("G", "Generate Judges", TuiTheme.OK))
            add(HotkeyAction("B", "Benchmark"))
            if (isViewingSnapshot) add(HotkeyAction("N", "Rename Snap"))
        }
    }
}
