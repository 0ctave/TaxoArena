package taxonomy.tui.features.benchmark

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import com.jakewharton.mosaic.ui.TextStyle.Companion.Unspecified
import taxonomy.service.AnalysisPanelState
import taxonomy.tui.state.BenchmarkType
import taxonomy.tui.state.BenchmarkUiState

@Composable
fun BenchmarkPanel(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
    scrollOffset: Int,
    benchmarkState: BenchmarkUiState,
) {
    when (benchmarkState.benchmarkType) {
        BenchmarkType.NONE -> BenchmarkTypeSelector(benchmarkState)
        BenchmarkType.ARENA -> ArenaBenchmarkView(width, height, controlState, scrollOffset, benchmarkState)
        BenchmarkType.TRICKLE -> TrickleBenchmarkView(width, height, benchmarkState)
    }
}

/** Entry screen: pick which evaluation to run. */
@Composable
private fun BenchmarkTypeSelector(benchmarkState: BenchmarkUiState) {
    val options = listOf(
        "ARENA" to "Multi-model pairwise eval over MMLU-Pro",
        "TRICKLE" to "Batch routing accuracy test over reserved queries",
    )
    Column {
        Text("BENCHMARK SUITE", color = Cyan, textStyle = Bold)
        Spacer()
        Text("Select a benchmark type:", color = White)
        Spacer()
        options.forEachIndexed { idx, (name, desc) ->
            val selected = idx == benchmarkState.benchmarkTypeSelectionIndex
            Text(
                buildAnnotatedString {
                    withStyle(SpanStyle(color = Yellow, textStyle = Bold)) {
                        append(if (selected) "❯ " else "  ")
                    }
                    withStyle(
                        SpanStyle(
                            color = if (selected) Cyan else White,
                            textStyle = if (selected) Bold else Unspecified
                        )
                    ) { append("[$name] ") }
                    withStyle(SpanStyle(color = White)) { append(desc) }
                }
            )
        }
        Spacer()
        Text("W/S to select · Enter to confirm · Q/Esc to go back", color = Cyan)
    }
}

/** Existing Arena benchmark (MMLU-Pro pairwise eval) view. */
@Composable
private fun ArenaBenchmarkView(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
    scrollOffset: Int,
    benchmarkState: BenchmarkUiState,
) {
    Column {
        if (benchmarkState.loadedModels.isNotEmpty()) {
            Text("Loaded models: ${benchmarkState.loadedModels.joinToString(", ")}", color = Green)
        } else {
            Text("No precomputed models loaded — press o to load eval_results.", color = Yellow)
        }
        Spacer()

        when {
            benchmarkState.isDownloadingEval -> {
                Text("Downloading MMLU-Pro eval_results…", color = Yellow)
                val files = benchmarkState.evalDownloadProgress
                if (files.isEmpty()) {
                    Text("Fetching file listing from GitHub…", color = White)
                } else {
                    val done = files.values.count { it >= 1f }
                    Text("Downloaded $done / ${files.size} files", color = White)
                    files.entries.take((height - 4).coerceAtLeast(1)).forEach { (name, pct) ->
                        Text("  ${name.take((width - 12).coerceAtLeast(1))}  ${"%.0f%%".format(pct * 100)}", color = White)
                    }
                }
            }

            controlState.isRunningBenchmark -> {
                Text("Running benchmark...", color = White)
                Text(controlState.benchmarkProgress, color = White)
                benchmarkState.liveStats?.let { live ->
                    Text(
                        "Live: ${live.processed}/${live.total} · " +
                            "agreement ${"%.2f".format(live.runningAgreement)} · " +
                            "coverage ${"%.2f".format(live.runningCoverage)}",
                        color = White
                    )
                }
            }

            benchmarkState.evalLoaderIsRunning -> {
                Text("Loading eval results...", color = White)
                if (benchmarkState.evalLoaderStatus.isNotBlank()) {
                    Text(benchmarkState.evalLoaderStatus, color = White)
                }
            }

            controlState.benchmarkReport != null -> {
                val report = controlState.benchmarkReport!!
                Text("Queries: ${report.totalQueries}", color = White)
                Text("Model Pairs: ${report.totalModelPairs}", color = White)
                Text("Coverage: ${"%.3f".format(report.coverageRate)}", color = White)
                Text("Judge Agreement: ${"%.3f".format(report.overallJudgeAccuracyAgreement)}", color = White)
                Spacer()
                Text("Scroll offset: $scrollOffset", color = White)
            }

            else -> {
                Text("Models: ${benchmarkState.benchmarkModelsInput.ifBlank { "(all loaded)" }}", color = White)
                Text("Query limit: ${benchmarkState.benchmarkQueryLimitInput.ifBlank { "0 (all)" }}", color = White)
                Text("Category: ${benchmarkState.benchmarkCategoryInput.ifBlank { "—" }}", color = White)
                Text("Confidence gate: ${benchmarkState.benchmarkConfidenceGateInput}", color = White)
                Text("Parallelism: ${benchmarkState.benchmarkParallelismInput}", color = White)
                Text("Update rankings: ${benchmarkState.benchmarkUpdateRankingsInput}", color = White)
            }
        }

        Spacer()
        Text("Enter run benchmark · o load eval_results · Q back", color = Cyan)
    }
}

/** Batch routing accuracy test (formerly the Trickle tab's batch test). */
@Composable
private fun TrickleBenchmarkView(
    width: Int,
    height: Int,
    benchmarkState: BenchmarkUiState,
) {
    Column {
        when {
            benchmarkState.isRunningBatchTrickleTest -> {
                Text("Running batch trickle test…", color = Yellow)
                if (benchmarkState.batchTrickleProgress.isNotBlank()) {
                    Spacer()
                    Text(benchmarkState.batchTrickleProgress, color = White)
                }
            }

            benchmarkState.batchTrickleResults != null -> {
                val r = benchmarkState.batchTrickleResults
                Text("Batch trickle results", color = Cyan, textStyle = Bold)
                Spacer()
                Text("Total queries      ${r.totalQueries}", color = White)
                Text("Primary accuracy   ${"%.1f%%".format(r.overallAccuracy * 100)}", color = White)
                Text("Ancestor accuracy  ${"%.1f%%".format(r.overallAncestorAccuracy * 100)}", color = White)
                Text("Leaf rate          ${"%.1f%%".format(r.leafRate * 100)}", color = White)
                Spacer()
                Text("Press B to re-run · Q to go back.", color = Cyan)
            }

            else -> {
                Text("Trickle benchmark", color = Cyan, textStyle = Bold)
                Spacer()
                Text("Batch routing accuracy test over the reserved test queries.", color = White)
                Spacer()
                Text("Press B to start the batch routing accuracy test.", color = White)
                Text("Q/Esc to go back.", color = Cyan)
            }
        }
    }
}
