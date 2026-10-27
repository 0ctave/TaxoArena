package taxonomy.tui.features.trickle

import androidx.compose.runtime.Composable
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
) {
    Column {
        // Mosaic's TextSurface throws Check failed when a Text overflows its row. Truncate every
        // user-input echo to the panel column to avoid the same crash class seen in ArenaPanel.
        val w = (width - 1).coerceAtLeast(1)
        when {
            state.isEnteringTrickleQuery -> {
                Text("Route a query through the DAG".take(w), color = Cyan)
                Spacer()
                Text("Query ❯ ${state.trickleQueryInput}█".take(w), color = Cyan)
                Spacer()
                Text("Enter to run · Esc to cancel".take(w), color = White)
            }

            state.isRunningTrickleQuery -> {
                Text("Routing query through DAG…".take(w), color = Yellow)
                Spacer()
                Text("Query: ${state.trickleQueryInput}".take(w), color = White)
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
                Text("Press T to route another query.", color = White)
            }

            else -> {
                Text("Trickle routing test", color = Cyan)
                Spacer()
                Text("Press T to route a single query through the DAG.", color = White)
            }
        }
    }
}
