package taxonomy.tui.features.analysis

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Text
import taxonomy.service.AnalysisMode
import taxonomy.service.AnalysisPanelState

/** Content-only: the parent [AnalysisPanel] owns the border and title. */
@Composable
fun MetricsOrInspectorPanel(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
    inspectorScroll: Int,
    metricsScroll: Int,
) {
    Column(modifier = Modifier.padding(left = 1)) {
            when (controlState.mode) {
                AnalysisMode.NODE_DETAIL -> {
                    val node = controlState.selectedNode
                    if (node == null) {
                        Text("No node selected.", color = White)
                    } else {
                        Text("Label: ${node.label ?: "unlabeled"}", color = White)
                        Text("Depth: ${node.depth}", color = White)
                        Text("Queries: ${node.queries.size}", color = White)
                        Text("Parents: ${node.parents.size}", color = White)
                        Text("Children: ${node.children.size}", color = White)
                        Text("Inspector scroll: $inspectorScroll", color = White)
                    }
                }
                AnalysisMode.METRICS -> {
                    Text("Metrics view active.", color = White)
                    Text("Scroll offset: $metricsScroll", color = White)
                }
                AnalysisMode.SETTINGS -> {
                    Text("Settings view active.", color = White)
                }
                else -> {
                    Text("Select a mode from topology shortcuts.", color = White)
                }
            }
    }
}
