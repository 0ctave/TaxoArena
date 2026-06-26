package taxonomy.tui.features.trickle

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Text
import taxonomy.tui.BatchTrickleTestResults
import taxonomy.tui.components.Panel

@Composable
fun TricklePanel(
    width: Int,
    height: Int,
    results: BatchTrickleTestResults?,
    scrollOffset: Int,
) {
        Column(modifier = Modifier.padding(left = 2, top = 1)) {
            if (results == null) {
                Text("No trickle results available.", color = White)
                Text("Use T for single-query or B for batch trickle.", color = White)
            } else {
                Text("Total Queries: ${results.totalQueries}", color = White)
                Text("Primary Accuracy: ${"%.3f".format(results.overallAccuracy)}", color = White)
                Text("Ancestor Accuracy: ${"%.3f".format(results.overallAncestorAccuracy)}", color = White)
                Text("Leaf Rate: ${"%.3f".format(results.leafRate)}", color = White)
                Text("Scroll: $scrollOffset", color = White)
            }
        }
}
