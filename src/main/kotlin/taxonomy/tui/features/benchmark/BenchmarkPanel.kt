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
                controlState.isRunningBenchmark -> {
                    Text("Running benchmark...", color = White)
                    Text(controlState.benchmarkProgress, color = White)
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
