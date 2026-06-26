package taxonomy.tui.controller

import taxonomy.service.AnalysisMode
import taxonomy.tui.state.ConfigSubPanel
import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.ScrollbarTarget
import taxonomy.tui.state.TuiAppState

class ScrollController {

    fun scrollUp(state: TuiAppState): TuiEvent? = resolveScroll(state, -1)

    fun scrollDown(state: TuiAppState): TuiEvent? = resolveScroll(state, +1)

    fun dragTo(target: ScrollbarTarget, offset: Int): TuiEvent =
        TuiEvent.ScrollTo(target, offset)

    private fun resolveScroll(state: TuiAppState, delta: Int): TuiEvent? {
        return when (state.shell.focusedPanel) {
            FocusPanel.TOPOLOGY -> TuiEvent.ScrollBy(ScrollbarTarget.TOPOLOGY, delta)
            FocusPanel.SYSTEM_LOGS -> TuiEvent.ScrollBy(ScrollbarTarget.LOGS, delta)
            FocusPanel.PROCESSES -> null
            FocusPanel.CONFIG -> {
                when (state.config.activeSubPanel) {
                    ConfigSubPanel.DOMAINS -> TuiEvent.ScrollBy(ScrollbarTarget.CONFIG_DOMAINS, delta)
                    ConfigSubPanel.SETTINGS -> null
                }
            }
            FocusPanel.ANALYSIS_HUB -> {
                when (state.analysis.mode) {
                    AnalysisMode.NODE_DETAIL,
                    AnalysisMode.METRICS,
                    AnalysisMode.TRICKLE_TEST,
                    AnalysisMode.BENCHMARK -> TuiEvent.ScrollBy(ScrollbarTarget.ANALYSIS, delta)
                    AnalysisMode.SNAPSHOTS -> null
                    else -> null
                }
            }
        }
    }
}