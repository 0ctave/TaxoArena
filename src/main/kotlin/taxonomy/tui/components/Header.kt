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
 *
 * Width-safety note
 * -----------------
 * Mosaic 0.18.0's TextSurface.get throws IllegalStateException("Check failed") when a Text
 * composable draws past its allocated column space. A Row(width=N) with Spacer() between two
 * Text composables does NOT constrain the second Text's draw width — it only adjusts layout
 * position. The second Text still draws as many columns as its string is long, which overflows
 * when dynamic fields (activeSnapshotName, activeDatasetName) push the total past `width`.
 *
 * Fix: assemble the entire right-side stats string first, measure the left badge width (fixed at
 * 13 chars: " ◈ TAXOARENA  v2.0 "), then take() the stats string to at most (width - 13) cols
 * so the combined Row content never exceeds the terminal width.
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
    judgesCount: Int = 0,
) {
    // Left badge is fixed: " ◈ TAXOARENA  v2.0 " = 19 visible chars.
    val leftWidth = 19
    val rightMax = (width - leftWidth).coerceAtLeast(0)

    // Build the right-side stats as a plain string first so we can measure and clip it.
    val statsRaw = buildString {
        append(" Nodes: $totalNodes")
        append("  Depth: $maxDepth")
        append("  Leaves: $leafCount")
        append("  Judges: $judgesCount")
        append("  Dataset: $activeDatasetName")
        if (activeSnapshotName != null) append("   [ARCHIVE: $activeSnapshotName]")
        append("   $time ")
    }
    // Clip to available columns so the AnnotatedString never causes an overflow draw.
    val statsClipped = statsRaw.take(rightMax)

    // Re-build as AnnotatedString with color spans, now guaranteed to fit.
    val statsAnnotated = buildAnnotatedString {
        // We replay the same segments but only up to statsClipped.length chars total.
        var remaining = statsClipped.length
        fun seg(plain: String, block: () -> Unit) {
            if (remaining <= 0) return
            val chunk = plain.take(remaining)
            remaining -= chunk.length
            block()
        }
        val nodesStr = " Nodes: $totalNodes"
        val depthStr = "  Depth: $maxDepth"
        val leavesStr = "  Leaves: $leafCount"
        val judgesStr = "  Judges: $judgesCount"
        val datasetStr = "  Dataset: $activeDatasetName"
        val archiveStr = if (activeSnapshotName != null) "   [ARCHIVE: $activeSnapshotName]" else null
        val timeStr = "   $time "

        // Nodes
        val nodesLabel = " Nodes: ".take(remaining); remaining -= nodesLabel.length
        withStyle(SpanStyle(color = White)) { append(nodesLabel) }
        val nodesVal = "$totalNodes".take(remaining); remaining -= nodesVal.length
        withStyle(SpanStyle(color = Green, textStyle = Bold)) { append(nodesVal) }
        // Depth
        val depthLabel = "  Depth: ".take(remaining); remaining -= depthLabel.length
        withStyle(SpanStyle(color = White)) { append(depthLabel) }
        val depthVal = "$maxDepth".take(remaining); remaining -= depthVal.length
        withStyle(SpanStyle(color = Yellow, textStyle = Bold)) { append(depthVal) }
        // Leaves
        val leavesLabel = "  Leaves: ".take(remaining); remaining -= leavesLabel.length
        withStyle(SpanStyle(color = White)) { append(leavesLabel) }
        val leavesVal = "$leafCount".take(remaining); remaining -= leavesVal.length
        withStyle(SpanStyle(color = Magenta, textStyle = Bold)) { append(leavesVal) }
        // Judges
        val judgesLabel = "  Judges: ".take(remaining); remaining -= judgesLabel.length
        withStyle(SpanStyle(color = White)) { append(judgesLabel) }
        val judgesVal = "$judgesCount".take(remaining); remaining -= judgesVal.length
        withStyle(SpanStyle(color = Green, textStyle = Bold)) { append(judgesVal) }
        // Dataset
        val datasetLabel = "  Dataset: ".take(remaining); remaining -= datasetLabel.length
        withStyle(SpanStyle(color = White)) { append(datasetLabel) }
        val datasetVal = activeDatasetName.take(remaining); remaining -= datasetVal.length
        withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append(datasetVal) }
        // Archive
        if (activeSnapshotName != null && remaining > 0) {
            val archiveVal = "   [ARCHIVE: $activeSnapshotName]".take(remaining); remaining -= archiveVal.length
            withStyle(SpanStyle(color = Yellow, textStyle = Bold)) { append(archiveVal) }
        }
        // Time
        if (remaining > 0) {
            val timeVal = "   $time ".take(remaining)
            withStyle(SpanStyle(color = White)) { append(timeVal) }
        }
    }

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
        Text(statsAnnotated)
    }
}
