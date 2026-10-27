package taxonomy.tui.components

import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.TuiAppState

/**
 * Pure builder for the main-dashboard hotkey bar.
 *
 * The bottom bar is **fixed** once a DAG is loaded:
 *
 * ```
 * DAG : [M] Metrics [C] Config [T] Trickle | Arena : [A] Arena [G] Generate Judges | [B] Benchmark [Tab] Switch Panels [?] Help [X] Load DAG [Ctrl-C] Quit
 * ```
 *
 * Context-sensitive hints for individual panels (e.g. node navigation, metrics
 * scroll) are displayed **inside** the relevant panel via [Panel.contextHints],
 * not in the global bar.
 */
object DashboardHotkeys {

    /**
     * Returns the full [HotkeyGroup] list to pass to [HotkeyBarGrouped].
     * Always shows the fixed grouped layout when a DAG is loaded.
     */
    fun groups(
        hasDag: Boolean,
        focused: FocusPanel,
        isRegenerating: Boolean,
        isViewingSnapshot: Boolean = false,
        state: TuiAppState,
    ): List<HotkeyGroup> {

        // DAG is being built
        if (isRegenerating) {
            return listOf(
                HotkeyGroup("", listOf(
                    HotkeyAction("◌", "Building DAG", TuiTheme.RUNNING),
                    HotkeyAction("Esc", "Cancel", TuiTheme.ERROR),
                )),
                HotkeyGroup("", GlobalHotkeys.forState(state)),
            )
        }

        // No DAG loaded
        if (!hasDag) {
            return listOf(
                HotkeyGroup("", listOf(
                    HotkeyAction("X", "Load DAG / New DAG", TuiTheme.ACCENT, isPrimary = true),
                )),
                HotkeyGroup("", GlobalHotkeys.forState(state)),
            )
        }

        // Fixed layout — always the same regardless of which panel is focused
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
            if (isViewingSnapshot) {
                add(HotkeyAction("N", "Rename Snap"))
                add(HotkeyAction("Y", "Copy ID"))
            }
        }
        val arenaGroup = HotkeyGroup(label = "Arena", actions = arenaActions)

        val benchmarkGroup = HotkeyGroup(
            label = "",
            actions = listOf(HotkeyAction("B", "Benchmark")),
        )

        return listOf(
            dagGroup,
            arenaGroup,
            benchmarkGroup,
            HotkeyGroup("", GlobalHotkeys.forState(state)),
        )
    }
}
