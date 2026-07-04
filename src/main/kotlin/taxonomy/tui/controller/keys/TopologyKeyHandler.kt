package taxonomy.tui.controller.keys

import taxonomy.model.GraphNode
import taxonomy.service.AnalysisMode
import taxonomy.tui.components.TreeLine
import taxonomy.tui.controller.TuiEffects
import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.TuiAppState

/**
 * Handles keyboard input when the TOPOLOGY (DAG Explorer) panel has focus.
 */
internal class TopologyKeyHandler(
    private val treeLinesProvider: (Map<String, Boolean>) -> List<TreeLine>,
    private val effects: TuiEffects,
) {

    fun handle(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        when (key) {
            "w", "z", "arrowup" -> {
                dispatch(TuiEvent.SetSelectedTreeIdx((state.topology.selectedTreeIdx - 1).coerceAtLeast(0)))
                dispatch(TuiEvent.SetTopologyAutoScroll(false))
            }

            "s", "arrowdown" -> {
                val lines = treeLinesProvider(state.topology.expandedNodes)
                val maxIdx = (lines.size - 1).coerceAtLeast(0)
                dispatch(TuiEvent.SetSelectedTreeIdx((state.topology.selectedTreeIdx + 1).coerceAtMost(maxIdx)))
                dispatch(TuiEvent.SetTopologyAutoScroll(false))
            }

            "arrowright", "l", "d" -> selectedTreeNode(state)?.let {
                if (it.children.isNotEmpty()) dispatch(TuiEvent.SetNodeExpanded(it.id, true))
            }

            "arrowleft", "h" -> selectedTreeNode(state)?.let {
                if (it.children.isNotEmpty()) dispatch(TuiEvent.SetNodeExpanded(it.id, false))
            }

            " ", "space" -> selectedTreeNode(state)?.let {
                if (it.children.isNotEmpty()) dispatch(TuiEvent.ToggleNodeExpanded(it.id))
            }

            "enter" -> {
                val node = selectedTreeNode(state)
                effects.inspectNode(node)
                dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.NODE_DETAIL, requestFocus = false))
                if (node != null) effects.loadLeaderboardForNode(node, dispatch)
            }

            "r" -> selectedTreeNode(state)?.let { node ->
                val d = dispatch
                effects.inspectNode(node)
                d(TuiEvent.FocusPanelRequested(FocusPanel.ANALYSIS_HUB))
                d(TuiEvent.SetAnalysisMode(AnalysisMode.NODE_DETAIL))
                d(TuiEvent.SetGeneratingJudge(true))
                effects.regenerateJudgeForCurrentNode(d)
            }

            "q", "escape" -> dispatch(TuiEvent.SetAnalysisMode(AnalysisMode.IDLE))
        }
    }

    fun selectedTreeNode(state: TuiAppState): GraphNode? {
        val lines = treeLinesProvider(state.topology.expandedNodes)
        return lines.getOrNull(state.topology.selectedTreeIdx)?.node
    }
}
