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
import taxonomy.tui.components.ProcessRow
import taxonomy.tui.components.TuiTheme
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
    /** Most relevant active process, or null when idle. Pinned at the top so a
     *  running process is always one keystroke away regardless of what the
     *  dashboard is currently showing (selection wins, process resumable). */
    activeProcess: ProcessRow? = null,
) {
    // Pinned resumable-process banner: always visible while work is running.
    val bannerH = if (activeProcess != null) 1 else 0
    if (activeProcess != null) {
        ProcessBanner(width, activeProcess)
    }
    val bodyH = (height - bannerH).coerceAtLeast(1)

    when (controlState.mode) {
        AnalysisMode.ARENA -> ArenaPanel(width, bodyH, controlState, arenaState)
        AnalysisMode.BENCHMARK -> BenchmarkPanel(width, bodyH, controlState, benchmarkScroll, benchmarkState)
        AnalysisMode.TRICKLE_TEST -> TricklePanel(width, bodyH, trickleResults, batchTrickleScroll)
        AnalysisMode.JUDGE_PROGRESS -> JudgeProgressPanel(width, bodyH, controlState)
        AnalysisMode.SNAPSHOTS -> SnapshotHubPanel(width, bodyH, snapshotState)
        else -> MetricsOrInspectorPanel(width, bodyH, controlState, inspectorScroll, metricsScroll)
    }
}

/** One-line pinned banner summarising the active process with a resume hint. */
@Composable
private fun ProcessBanner(width: Int, p: ProcessRow) {
    val color = TuiTheme.statusColor(done = p.done, error = p.error)
    val pct = p.percent?.let { " ${"%.0f".format(java.util.Locale.US, it)}%%" } ?: ""
    val text = "▶ ${p.name}$pct — ${p.status}  [P] resume".take(width - 1)
    Text(text, color = color, textStyle = Bold)
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
