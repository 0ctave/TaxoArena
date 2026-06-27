package taxonomy.tui.features.topology

import androidx.compose.runtime.Composable
import taxonomy.model.GraphNode
import taxonomy.tui.components.TreeLine
import taxonomy.tui.state.TopologyUiState
import taxonomy.tui.components.AsciiTreeTable
import taxonomy.tui.components.DomainSelectorTable

/**
 * Feature panel orchestrator for Topology.
 * Renders purely based on State passed down from the Controller.
 */
@Composable
internal fun TopologyPanel(
    width: Int,
    height: Int,
    state: TopologyUiState,
    availableDomains: List<Pair<String, Int>>,
    selectedDomains: List<String>,
    allNodes: List<GraphNode>,
    treeLines: List<TreeLine>,
    queryCounts: Map<String, Int> = emptyMap(),
) {
    when {
        state.showDomainSelector -> {
            DomainSelectorTable(
                pWidth = width,
                pHeight = height,
                domains = availableDomains,
                offset = state.scrollOffset,
                selectedIdx = state.selectedListIdx,
                selectedDomains = selectedDomains
            )
        }
        else -> {
            // Single canonical DAG view: collapsible tree with the recursive query column.
            AsciiTreeTable(
                pWidth = width,
                pHeight = height,
                lines = treeLines,
                offset = state.treeScrollOffset,
                selectedIdx = state.selectedTreeIdx,
                queryCounts = queryCounts,
            )
        }
    }
}