package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.Magenta
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Row
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold

/**
 * Top-level application banner.
 * Decoupled from services; relies entirely on pure data inputs.
 */
@Composable
fun Header(
    width: Int,
    time: String,
    totalNodes: Int,
    activeDatasetName: String,
    activeSnapshotName: String?,
    maxDepth: Int = 0,
    leafCount: Int = 0,
) {
    Row(modifier = Modifier.width(width)) {
        Text(
            buildAnnotatedString {
                withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
                    append(" ◈ TAXOARENA ")
                }
                withStyle(SpanStyle(color = White)) {
                    append(" v2.0 ")
                }
            }
        )

        Spacer()

        Text(
            buildAnnotatedString {
                // Stat chips, each in its own color so the eye can pick them apart at a glance.
                withStyle(SpanStyle(color = White)) { append(" Nodes: ") }
                withStyle(SpanStyle(color = Green, textStyle = Bold)) { append("$totalNodes") }
                withStyle(SpanStyle(color = White)) { append("  Depth: ") }
                withStyle(SpanStyle(color = Yellow, textStyle = Bold)) { append("$maxDepth") }
                withStyle(SpanStyle(color = White)) { append("  Leaves: ") }
                withStyle(SpanStyle(color = Magenta, textStyle = Bold)) { append("$leafCount") }
                withStyle(SpanStyle(color = White)) { append("  Dataset: ") }
                withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append(activeDatasetName) }
                if (activeSnapshotName != null) {
                    withStyle(SpanStyle(color = Yellow, textStyle = Bold)) {
                        append("   [ARCHIVE: $activeSnapshotName]")
                    }
                }
                withStyle(SpanStyle(color = White)) { append("   $time ") }
            }
        )
    }
}