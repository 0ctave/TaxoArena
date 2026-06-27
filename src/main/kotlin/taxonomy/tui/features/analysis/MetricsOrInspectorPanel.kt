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
    Column {
        when (mode) {
            AnalysisMode.NODE_DETAIL -> {
                val node = controlState.selectedNode
                if (node == null) {
                    Text("Select a node in the DAG (Enter) to inspect it.", color = White)
                } else {
                    Text(node.label ?: "(unlabeled)", color = Cyan, textStyle = Bold)
                    Spacer()
                    Text("Type           ${if (node.isLeaf) "leaf" else "internal"}", color = White)
                    Text("Depth          ${node.depth}", color = White)
                    Text("Direct queries ${node.queries.size}", color = White)
                    Text("Total queries  ${node.getRecursiveQueryCount()}", color = White)
                    Text("Parents        ${node.parents.size}", color = White)
                    Text("Children       ${node.children.size}", color = White)
                    if (node.crossLinkChildren.isNotEmpty())
                        Text("Cross-links    ${node.crossLinkChildren.size}", color = Yellow)
                    val judged = node.judgePrompt != null
                    Text(
                        "Judge          ${if (judged) "\u2714 specialised" else "\u25cb none"}",
                        color = if (judged) Green else White
                    )
                    if (node.parents.size > 1) {
                        Spacer()
                        Text("Parents:", color = Cyan)
                        node.parents.take(3).forEach {
                            Text("  \u00b7 ${it.label ?: it.id}", color = White)
                        }
                    }
                    val samples = node.queries.take(3)
                    if (samples.isNotEmpty()) {
                        Spacer()
                        Text("Sample queries:", color = Cyan)
                        samples.forEach {
                            Text("  \u00b7 ${it.rawText.take((width - 6).coerceAtLeast(8))}", color = White)
                        }
                    }
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
                    if (m.ancestorCorrectRate > 0.0)
                        Text("Ancestor acc.    ${pct(m.ancestorCorrectRate)}", color = White)
                    // Clustering-quality metrics (only when computed / non-zero).
                    if (m.sphericalSilhouette != 0.0)
                        Text("Silhouette       ${num(m.sphericalSilhouette)}", color = White)
                    if (m.nmi > 0.0) Text("NMI              ${num(m.nmi)}", color = White)
                    if (m.ari > 0.0) Text("ARI              ${num(m.ari)}", color = White)
                    if (m.weightedLeafPurity > 0.0)
                        Text("Leaf purity      ${pct(m.weightedLeafPurity)}", color = White)
                    if (m.residualQueries > 0)
                        Text("Residual queries ${m.residualQueries}", color = White)
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
