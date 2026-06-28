package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Row
import com.jakewharton.mosaic.ui.Text

/**
 * Generic virtualized rendering helper that handles the right-side scrollbar.
 *
 * @param pWidth Total panel width
 * @param pHeight Total panel height
 * @param itemCount Total number of items in the list
 * @param scrollOffset Current index of the top-most visible item
 * @param hasPadding Whether to add horizontal padding to the content area
 * @param reversed If true, scrollbar thumb starts at the bottom
 * @param contentColumn Builder block for the visible items
 *
 * Width safety: innerWidth and contentW are floored at 1 so that Mosaic never
 * receives a zero-column Box. TextSurface.get asserts col >= 0 && col < width,
 * which throws IllegalStateException when width == 0 regardless of what Text
 * draws. This can happen on narrow terminals or when the app-level panel width
 * calculation subtracts borders down to ≤ 4.
 */
@Composable
fun ScrollablePanelContent(
    pWidth: Int,
    pHeight: Int,
    itemCount: Int,
    scrollOffset: Int,
    hasPadding: Boolean = true,
    reversed: Boolean = false,
    activeColor: Color = Cyan,
    trackColor: Color = White,
    contentColumn: @Composable (visibleHeight: Int, startIdx: Int, innerWidth: Int) -> Unit
) {
    val visible = pHeight.coerceAtLeast(1)
    val maxScroll = maxOf(0, itemCount - visible)
    val startIdx = scrollOffset.coerceIn(0, maxScroll)

    // Guard against narrow terminals: subtracting padding/scrollbar from a small
    // pWidth can produce zero or negative values, causing TextSurface to assert.
    val innerWidth = (if (hasPadding) pWidth - 4 else pWidth).coerceAtLeast(1)
    val contentW = (innerWidth - 2).coerceAtLeast(1) // leave 2 cols for scrollbar gutter

    Row(modifier = Modifier.width(innerWidth).height(visible)) {
        val modifier = if (hasPadding) Modifier.width(contentW).padding(left = 2) else Modifier.width(contentW)
        Column(modifier = modifier) {
            contentColumn(visible, startIdx, contentW)
        }
        TuiScrollbar(
            visibleHeight = visible,
            scrollOffset = startIdx,
            maxScroll = maxScroll,
            reversed = reversed,
            activeColor = activeColor,
            trackColor = trackColor
        )
    }
}

@Composable
private fun TuiScrollbar(
    visibleHeight: Int,
    scrollOffset: Int,
    maxScroll: Int,
    reversed: Boolean,
    activeColor: Color,
    trackColor: Color
) {
    if (maxScroll <= 0) {
        Column(modifier = Modifier.width(2).height(visibleHeight)) {
            repeat(visibleHeight) { Text(" ", modifier = Modifier.height(1)) }
        }
        return
    }

    val fraction = if (maxScroll > 0) scrollOffset.toFloat() / maxScroll else 0f
    val barPos = (fraction * (visibleHeight - 1)).toInt().coerceIn(0, visibleHeight - 1)
    val visualPos = if (reversed) visibleHeight - 1 - barPos else barPos

    Column(modifier = Modifier.width(2).height(visibleHeight)) {
        for (i in 0 until visibleHeight) {
            if (i == visualPos) {
                Text(" █", color = activeColor, modifier = Modifier.height(1))
            } else {
                Text(" │", color = trackColor, modifier = Modifier.height(1))
            }
        }
    }
}
