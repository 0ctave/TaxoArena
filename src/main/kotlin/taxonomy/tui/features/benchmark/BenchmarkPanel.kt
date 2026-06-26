package taxonomy.tui.features.benchmark

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Text
import taxonomy.arena.TaxonomyArenaState
import taxonomy.tui.components.Panel

@Composable
fun BenchmarkPanel(
    width: Int,
    height: Int,
    controlState: TaxonomyArenaState,
    scrollOffset: Int,
) {
    Panel("BENCHMARK", Cyan, width, height) {
        Column(modifier = Modifier.padding(left = 2, top = 1)) {
            Text("Benchmark mode active.", color = White)
            Text("Scroll offset: $scrollOffset", color = White)
            controlState.benchmarkReport?.let { report ->
                Text("Queries: ${report.totalQueries}", color = White)
                Text("Models: ${report.models.joinToString()}", color = White)
            } ?: Text("No benchmark report yet.", color = White)
        }
    }
}