package taxonomy.tui.features.benchmark

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
import taxonomy.service.AnalysisPanelState
import taxonomy.tui.components.Panel
import taxonomy.tui.state.BenchmarkUiState

@Composable
fun BenchmarkPanel(
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
            Text("Enter run benchmark · o load eval_results", color = Cyan)
        }
}
