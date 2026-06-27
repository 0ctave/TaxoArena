package taxonomy.tui.features.trickle

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import taxonomy.service.QueryResponseNode
import taxonomy.tui.state.TrickleUiState

private fun flattenTrickle(nodes: List<QueryResponseNode>): List<QueryResponseNode> =
    nodes.flatMap { listOf(it) + flattenTrickle(it.children) }

/** Content-only: parent [taxonomy.tui.features.analysis.AnalysisPanel] owns the border. */
@Composable
fun TricklePanel(
    width: Int,
    height: Int,
    state: TrickleUiState,
    scrollOffset: Int,
) {
    Column {
        when {
            state.isEnteringTrickleQuery -> {
                Text("Route a query through the DAG", color = Cyan)
                Spacer()
                Text("Query \u276f ${state.trickleQueryInput}\u2588", color = Cyan)
                Spacer()
                Text("Enter to run \u00b7 Esc to cancel", color = White)
            }

            state.isRunningBatchTrickleTest -> {
                Text("Running batch trickle test\u2026", color = Yellow)
                if (state.batchTrickleProgress.isNotBlank()) {
                    Spacer()
                    Text(state.batchTrickleProgress, color = White)
                }
            }

            state.batchTrickleResults != null -> {
                val r = state.batchTrickleResults
                Text("Batch trickle results", color = Cyan)
                Spacer()
                Text("Total queries      ${r.totalQueries}", color = White)
                Text("Primary accuracy   ${"%.1f%%".format(r.overallAccuracy * 100)}", color = White)
                Text("Ancestor accuracy  ${"%.1f%%".format(r.overallAncestorAccuracy * 100)}", color = White)
                Text("Leaf rate          ${"%.1f%%".format(r.leafRate * 100)}", color = White)
                Spacer()
                Text("Press B to re-run · T for a single query.", color = White)
            }

            state.trickleResultNodes.isNotEmpty() -> {
                Text("Trickle query results", color = Cyan)
                Spacer()
                val rows = (height - 4).coerceAtLeast(1)
                flattenTrickle(state.trickleResultNodes)
                    .sortedByDescending { it.confidence }
                    .take(rows)
                    .forEach { n ->
                        val pct = "%.0f%%".format(n.confidence * 100)
                        val line = "[$pct] d${n.depth} · ${n.fullPath}"
                        Text(line.take((width - 2).coerceAtLeast(1)), color = White)
                    }
                Spacer()
                Text("Press T for another query · B for a batch test.", color = White)
            }

            else -> {
                Text("Trickle routing test", color = Cyan)
                Spacer()
                Text("Press T to route a single query through the DAG.", color = White)
                Text("Press B to run a batch test over the reserved queries.", color = White)
            }
        }
    }
}
