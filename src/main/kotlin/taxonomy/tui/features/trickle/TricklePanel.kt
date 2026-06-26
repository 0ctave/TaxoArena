package taxonomy.tui.features.trickle

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Text
import taxonomy.arena.TaxonomyArenaState
import taxonomy.tui.components.Panel
import taxonomy.tui.BatchTrickleTestResults

@Composable
fun TricklePanel(
    width: Int,
    height: Int,
    controlState: TaxonomyArenaState,
    scrollOffset: Int,
) {
    Panel("TRICKLE TEST", Cyan, width, height) {
        Column(modifier = Modifier.padding(left = 2, top = 1)) {
            val result = controlState.batchTrickleResults as? BatchTrickleTestResults
            if (result == null) {
                Text("No trickle results available.", color = White)
                Text("Use T for single-query or B for batch trickle.", color = White)
            } else {
                Text("Total Queries: ${result.totalQueries}", color = White)
                Text("Primary Accuracy: ${"%.3f".format(result.overallAccuracy)}", color = White)
                Text("Ancestor Accuracy: ${"%.3f".format(result.overallAncestorAccuracy)}", color = White)
                Text("Leaf Rate: ${"%.3f".format(result.leafRate)}", color = White)
                Text("Scroll: $scrollOffset", color = White)
            }
        }
    }
}