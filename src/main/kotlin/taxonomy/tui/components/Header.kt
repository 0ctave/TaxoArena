package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
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
    activeSnapshotName: String?
) {
    Row(modifier = Modifier.width(width)) {
        Text(
            buildAnnotatedString {
                withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
                    append(" ◈ TAXONOMY DAG EVOLUTION ENGINE ◈ ")
                }
                withStyle(SpanStyle(color = White)) {
                    append(" v2.0 ")
                }
            }
        )

        Spacer()

        Text(
            buildAnnotatedString {
                if (activeSnapshotName != null) {
                    withStyle(SpanStyle(color = Yellow, textStyle = Bold)) {
                        append(" [ARCHIVE: $activeSnapshotName] ")
                    }
                }
                withStyle(SpanStyle(color = White)) {
                    append(" Nodes: ")
                }
                withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
                    append("$totalNodes")
                }
                withStyle(SpanStyle(color = White)) {
                    append(" │ Dataset: $activeDatasetName │ $time ")
                }
            }
        )
    }
}