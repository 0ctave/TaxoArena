package taxonomy.tui.features.analysis

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import taxonomy.model.IterationMetrics
import taxonomy.service.AnalysisMode
import taxonomy.service.AnalysisPanelState
import java.util.Locale

/**
 * Content-only metrics / node-inspector view. The parent [AnalysisPanel] owns the border
 * and the title; this switches on the MVI [mode]. METRICS renders the latest taxonomy
 * metrics report; NODE_DETAIL renders the selected node's stats.
 */
@Composable
fun MetricsOrInspectorPanel(
    width: Int,
    height: Int,
    mode: AnalysisMode,
    controlState: AnalysisPanelState,
    inspectorScroll: Int,
    metricsScroll: Int,
    latestMetrics: IterationMetrics? = null,
) {
    Column(modifier = Modifier.padding(left = 1)) {
        when (mode) {
            AnalysisMode.NODE_DETAIL -> {
                val node = controlState.selectedNode
                if (node == null) {
                    Text("Select a node in the DAG (Enter) to inspect it.", color = White)
                } else {
                    Text(node.label ?: "(unlabeled)", color = Cyan, textStyle = Bold)
                    Spacer()
                    Text("Depth          ${node.depth}", color = White)
                    Text("Direct queries ${node.queries.size}", color = White)
                    Text("Total queries  ${node.getRecursiveQueryCount()}", color = White)
                    Text("Parents        ${node.parents.size}", color = White)
                    Text("Children       ${node.children.size}", color = White)
                    val judged = node.judgePrompt != null
                    Text(
                        "Judge          ${if (judged) "\u2714 specialised" else "\u25cb none"}",
                        color = if (judged) Green else White
                    )
                }
            }

            AnalysisMode.METRICS -> {
                val m = latestMetrics?.metrics
                if (m == null) {
                    Text("No metrics yet \u2014 generate or load a DAG first.", color = Yellow)
                } else {
                    fun pct(d: Double) = String.format(Locale.US, "%.1f%%", d * 100.0)
                    fun num(d: Double) = String.format(Locale.US, "%.3f", d)
                    latestMetrics.iteration.takeIf { it.isNotBlank() }?.let {
                        Text(it, color = Cyan, textStyle = Bold)
                        Spacer()
                    }
                    Text("Total nodes      ${m.totalNodes}", color = White)
                    Text("Leaf nodes       ${m.leafNodes}", color = White)
                    Text("Cross-domain     ${m.crossDomainNodes}", color = White)
                    Text("Max depth        ${m.maxDepth}", color = White)
                    Text("Avg leaf depth   ${num(m.avgLeafDepth)}", color = White)
                    Text("Unique queries   ${m.totalUniqueQueries}", color = White)
                    Text("Residual ratio   ${pct(m.residualRatio)}", color = White)
                    Text("Avg match count  ${num(m.avgMatchCount)}", color = White)
                    Text("Equilibrium      ${pct(m.equilibriumIndex)}", color = White)
                    if (m.ancestorCorrectRate > 0.0) {
                        Text("Ancestor acc.    ${pct(m.ancestorCorrectRate)}", color = White)
                    }
                }
            }

            AnalysisMode.SETTINGS ->
                Text("Open the config screen (X \u2192 Welcome \u2192 Create new) to edit settings.", color = White)

            else -> {
                Text("Analysis Hub", color = Cyan, textStyle = Bold)
                Spacer()
                Text("M Metrics   A Arena   B Benchmark   T Trickle", color = White)
                Text("Enter on a DAG node to inspect it.", color = White)
            }
        }
    }
}
