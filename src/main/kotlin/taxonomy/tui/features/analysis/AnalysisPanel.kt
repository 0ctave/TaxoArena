package taxonomy.tui.features.analysis

import androidx.compose.runtime.Composable
import taxonomy.arena.AnalysisMode
import taxonomy.arena.TaxonomyArenaState
import taxonomy.tui.features.arena.ArenaPanel
import taxonomy.tui.features.benchmark.BenchmarkPanel
import taxonomy.tui.features.progress.JudgeProgressPanel
import taxonomy.tui.features.snapshots.SnapshotPanel
import taxonomy.tui.features.trickle.TricklePanel

@Composable
fun AnalysisPanel(
    width: Int,
    height: Int,
    controlState: TaxonomyArenaState,
    inspectorScroll: Int,
    metricsScroll: Int,
    benchmarkScroll: Int,
    batchTrickleScroll: Int,
    snapshotSelectedIdx: Int,
    snapshotCount: Int,
    isSavingSnapshot: Boolean,
    snapshotDescInput: String,
    isRenamingSnapshot: Boolean,
    renameInput: String,
) {
    when (controlState.mode) {
        AnalysisMode.ARENA -> ArenaPanel(width, height, controlState)
        AnalysisMode.BENCHMARK -> BenchmarkPanel(width, height, controlState, benchmarkScroll)
        AnalysisMode.TRICKLE_TEST -> TricklePanel(width, height, controlState, batchTrickleScroll)
        AnalysisMode.JUDGE_PROGRESS -> JudgeProgressPanel(width, height, controlState)
        AnalysisMode.SNAPSHOTS -> SnapshotPanel(
            width = width,
            height = height,
            selectedSnapshotIdx = snapshotSelectedIdx,
            snapshotCount = snapshotCount,
            isSavingSnapshot = isSavingSnapshot,
            snapshotDescInput = snapshotDescInput,
            isRenamingSnapshot = isRenamingSnapshot,
            renameInput = renameInput
        )
        else -> MetricsOrInspectorPanel(width, height, controlState, inspectorScroll, metricsScroll)
    }
}