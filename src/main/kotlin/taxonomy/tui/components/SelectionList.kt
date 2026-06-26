package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold

/**
 * Generic string list selector with a visual cursor.
 */
@Composable
fun SelectionList(
    items: List<String>,
    selectedIndex: Int,
    width: Int,
    height: Int,
    scrollOffset: Int,
    selectedPrefix: String = " ▶ ",
    unselectedPrefix: String = "   ",
    selectedColor: Color = Cyan,
    unselectedColor: Color = White
) {
    ScrollablePanelContent(
        pWidth = width,
        pHeight = height,
        itemCount = items.size,
        scrollOffset = scrollOffset,
        hasPadding = false
    ) { visibleHeight, startIdx, contentWidth ->

        val visibleItems = items.drop(startIdx).take(visibleHeight)

        visibleItems.forEachIndexed { idx, item ->
            val absoluteIdx = startIdx + idx
            val isSelected = absoluteIdx == selectedIndex

            Text(
                buildAnnotatedString {
                    val style = if (isSelected) {
                        SpanStyle(color = selectedColor, textStyle = Bold)
                    } else {
                        SpanStyle(color = unselectedColor)
                    }

                    withStyle(style) {
                        append(if (isSelected) selectedPrefix else unselectedPrefix)
                        append(item.take(contentWidth - selectedPrefix.length))
                    }
                }.take(contentWidth),
                modifier = Modifier.height(1)
            )
        }

        val emptyRows = visibleHeight - visibleItems.size
        repeat(emptyRows.coerceAtLeast(0)) {
            Text(" ".repeat(contentWidth), modifier = Modifier.height(1))
        }
    }
}