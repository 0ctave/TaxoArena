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
 * Width safety contract
 * ---------------------
 * The scrollbar is 2 columns wide. Rendering it when innerWidth < 3 would force Mosaic
 * to draw the content column at width ≤ 0, which causes TextSurface.get to throw
 * IllegalStateException ("Check failed"). We therefore suppress the scrollbar entirely
 * when the available width is too narrow, giving all columns to content instead.
 *
 * Regardless, innerWidth and contentW are each floored at 1 so no child composable
 * ever receives a non-positive width.
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
    onScrollClamp: ((Int) -> Unit)? = null,
    contentColumn: @Composable (visibleHeight: Int, startIdx: Int, innerWidth: Int) -> Unit
) {
    val visible = pHeight.coerceAtLeast(1)
    val maxScroll = maxOf(0, itemCount - visible)
    val startIdx = scrollOffset.coerceIn(0, maxScroll)

    if (scrollOffset > maxScroll && maxScroll >= 0 && onScrollClamp != null) {
        androidx.compose.runtime.LaunchedEffect(scrollOffset, maxScroll) {
            onScrollClamp(maxScroll)
        }
    }

    // Step 1: compute the total width available for this component.
    val innerWidth = (if (hasPadding) pWidth - 4 else pWidth).coerceAtLeast(1)

    // Step 2: the scrollbar is a fixed 2-column gutter. Only reserve it when there is
    // actually room (innerWidth >= 3 leaves at least 1 column for content). When the
    // panel is narrower than 3 columns we drop the scrollbar entirely so the content
    // column always receives a positive width.
    val showScrollbar = innerWidth >= 3
    val contentW = if (showScrollbar) (innerWidth - 2).coerceAtLeast(1) else innerWidth

    Row(modifier = Modifier.width(innerWidth).height(visible)) {
        val modifier = if (hasPadding) Modifier.width(contentW).padding(left = 2) else Modifier.width(contentW)
        Column(modifier = modifier) {
            contentColumn(visible, startIdx, contentW)
        }
        if (showScrollbar) {
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
