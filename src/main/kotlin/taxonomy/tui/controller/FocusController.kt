package taxonomy.tui.controller

import taxonomy.service.AnalysisMode
import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.TuiAppState

class FocusController {

    fun cycleForward(state: TuiAppState): TuiEvent {
        return TuiEvent.CycleFocusForward
    }

    fun focusTopology(): TuiEvent = TuiEvent.FocusPanelRequested(FocusPanel.TOPOLOGY)

    fun focusAnalysis(mode: AnalysisMode? = null): List<TuiEvent> {
        return buildList {
            add(TuiEvent.FocusPanelRequested(FocusPanel.ANALYSIS_HUB))
            if (mode != null) add(TuiEvent.SetAnalysisMode(mode))
        }
    }

    fun focusLogs(): TuiEvent = TuiEvent.FocusPanelRequested(FocusPanel.SYSTEM_LOGS)

    fun focusConfig(): TuiEvent = TuiEvent.FocusPanelRequested(FocusPanel.CONFIG)
}