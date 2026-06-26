package taxonomy.tui.features.analysis

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import com.jakewharton.mosaic.ui.TextStyle.Companion.Unspecified
import taxonomy.service.AnalysisMode
import taxonomy.service.AnalysisPanelState
import taxonomy.tui.BatchTrickleTestResults
import taxonomy.tui.components.Panel
import taxonomy.tui.features.arena.ArenaPanel
import taxonomy.tui.features.benchmark.BenchmarkPanel
import taxonomy.tui.features.progress.JudgeProgressPanel
import taxonomy.tui.features.trickle.TricklePanel
import taxonomy.tui.state.ArenaUiState
import taxonomy.tui.state.BenchmarkUiState
import taxonomy.tui.state.SnapshotUiState

@Composable
fun AnalysisPanel(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
    inspectorScroll: Int,
    metricsScroll: Int,
    benchmarkScroll: Int,
    batchTrickleScroll: Int,
    trickleResults: BatchTrickleTestResults?,
    snapshotState: SnapshotUiState,
    arenaState: ArenaUiState,
    benchmarkState: BenchmarkUiState,
) {
    when (controlState.mode) {
        AnalysisMode.ARENA -> ArenaPanel(width, height, controlState, arenaState)
        AnalysisMode.BENCHMARK -> BenchmarkPanel(width, height, controlState, benchmarkScroll, benchmarkState)
        AnalysisMode.TRICKLE_TEST -> TricklePanel(width, height, trickleResults, batchTrickleScroll)
        AnalysisMode.JUDGE_PROGRESS -> JudgeProgressPanel(width, height, controlState)
        AnalysisMode.SNAPSHOTS -> SnapshotHubPanel(width, height, snapshotState)
        else -> MetricsOrInspectorPanel(width, height, controlState, inspectorScroll, metricsScroll)
    }
}

@Composable
private fun SnapshotHubPanel(
    width: Int,
    height: Int,
    state: SnapshotUiState,
) {
    Panel("SNAPSHOTS", Cyan, width, height) {
        Column(modifier = Modifier.padding(left = 2, top = 1)) {
            when {
                state.isSavingSnapshot ->
                    Text("Save snapshot — description: ${state.snapshotDescInput}_", color = Cyan)
                state.isRenamingSnapshot ->
                    Text("Rename snapshot — new name: ${state.renameInput}_", color = Cyan)
            }
            if (state.snapshotList.isEmpty()) {
                Text("No snapshots saved yet. Press N to save the active DAG.", color = White)
            } else {
                val visible = (height - 3).coerceAtLeast(1)
                state.snapshotList.take(visible).forEachIndexed { idx, snap ->
                    val selected = idx == state.selectedSnapshotIdx
                    Text(
                        value = (if (selected) "> " else "  ") + snap.description,
                        color = if (selected) Cyan else White,
                        textStyle = if (selected) Bold else Unspecified
                    )
                }
                Spacer()
                Text("L/Enter load  D delete  N save  Esc back", color = White)
            }
        }
    }
}
