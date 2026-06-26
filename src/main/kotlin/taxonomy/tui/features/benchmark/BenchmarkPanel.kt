package taxonomy.tui.features.benchmark

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import taxonomy.service.AnalysisPanelState
import taxonomy.tui.components.Panel

@Composable
fun BenchmarkPanel(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
    scrollOffset: Int,
) {
    Panel("BENCHMARK", Cyan, width, height) {
        Column(modifier = Modifier.padding(left = 2, top = 1)) {
            if (controlState.isRunningBenchmark) {
                Text("Running benchmark...", color = White)
                Text(controlState.benchmarkProgress, color = White)
            }
            controlState.benchmarkReport?.let { report ->
                Text("Queries: ${report.totalQueries}", color = White)
                Text("Model Pairs: ${report.totalModelPairs}", color = White)
                Text("Coverage: ${"%.3f".format(report.coverageRate)}", color = White)
                Text("Judge Agreement: ${"%.3f".format(report.overallJudgeAccuracyAgreement)}", color = White)
                Spacer()
                Text("Scroll offset: $scrollOffset", color = White)
            } ?: run {
                if (!controlState.isRunningBenchmark) {
                    Text("No benchmark report yet.", color = White)
                }
            }
        }
    }
}
