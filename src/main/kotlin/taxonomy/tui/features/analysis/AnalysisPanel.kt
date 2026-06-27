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
    focused: Boolean = false,
    /** The active hub mode, driven by MVI state (key presses). The panel switches on THIS,
     *  not on the service's controlState.mode (which only changes when a run mutates it). */
    mode: AnalysisMode,
    controlState: AnalysisPanelState,
    inspectorScroll: Int,
    metricsScroll: Int,
    benchmarkScroll: Int,
    batchTrickleScroll: Int,
    trickleState: taxonomy.tui.state.TrickleUiState,
    snapshotState: SnapshotUiState,
    arenaState: ArenaUiState,
    benchmarkState: BenchmarkUiState,
    latestMetrics: taxonomy.model.IterationMetrics? = null,
    metricsHistory: List<taxonomy.model.IterationMetrics> = emptyList(),
    /** Most relevant active process, or null when idle. Pinned at the top so a
     *  running process is always one keystroke away regardless of what the
     *  dashboard is currently showing (selection wins, process resumable). */
    activeProcess: ProcessRow? = null,
) {
    // This panel owns the single bordered frame for the right-hand hub. The title reflects
    // the active mode, and the sub-panels below render content only (no nested borders).
    val title = when (mode) {
        AnalysisMode.ARENA -> "MODEL ARENA"
        AnalysisMode.BENCHMARK -> "BENCHMARK"
        AnalysisMode.TRICKLE_TEST -> "TRICKLE TEST"
        AnalysisMode.JUDGE_PROGRESS -> "JUDGE PROGRESS"
        AnalysisMode.SNAPSHOTS -> "SNAPSHOTS"
        AnalysisMode.NODE_DETAIL -> "NODE INSPECTOR"
        AnalysisMode.METRICS -> "METRICS"
        AnalysisMode.SETTINGS -> "SETTINGS"
        else -> "ANALYSIS HUB"
    }

    Panel(title, TuiTheme.panelAccent(focused), width, height) {
        Column {
            // Pinned resumable-process banner: always visible while work is running.
            val bannerH = if (activeProcess != null) 1 else 0
            if (activeProcess != null) {
                ProcessBanner(width - 2, activeProcess)
            }
            val bodyH = (height - 2 - bannerH).coerceAtLeast(1)
            val bodyW = width - 2

            when (mode) {
                AnalysisMode.ARENA -> ArenaPanel(bodyW, bodyH, controlState, arenaState)
                AnalysisMode.BENCHMARK -> BenchmarkPanel(bodyW, bodyH, controlState, benchmarkScroll, benchmarkState)
                AnalysisMode.TRICKLE_TEST -> TricklePanel(bodyW, bodyH, trickleState, batchTrickleScroll)
                AnalysisMode.JUDGE_PROGRESS -> JudgeProgressPanel(bodyW, bodyH, controlState)
                AnalysisMode.SNAPSHOTS -> SnapshotHubPanel(bodyW, bodyH, snapshotState)
                else -> MetricsOrInspectorPanel(
                    bodyW, bodyH, mode, controlState, inspectorScroll, metricsScroll,
                    latestMetrics, metricsHistory
                )
            }
        }
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
    Column {
        when {
            state.isSavingSnapshot ->
                Text("Save snapshot \u2014 description: ${state.snapshotDescInput}\u2588", color = Cyan)
            state.isRenamingSnapshot ->
                Text("Rename snapshot \u2014 new name: ${state.renameInput}\u2588", color = Cyan)
        }
        if (state.snapshotList.isEmpty()) {
            Text("No snapshots saved yet. Press N to save the active DAG.", color = White)
        } else {
            val visible = (height - 3).coerceAtLeast(1)
            state.snapshotList.take(visible).forEachIndexed { idx, snap ->
                val selected = idx == state.selectedSnapshotIdx
                Text(
                    value = (if (selected) "\u276f " else "  ") + snap.description,
                    color = if (selected) Cyan else White,
                    textStyle = if (selected) Bold else Unspecified
                )
            }
            Spacer()
            Text("L/Enter Load \u00b7 D Delete \u00b7 N Save \u00b7 Esc Back", color = White)
        }
    }
}
