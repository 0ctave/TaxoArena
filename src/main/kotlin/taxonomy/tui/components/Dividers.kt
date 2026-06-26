package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold

/** Horizontal rule across the screen. */
@Composable
fun HRule(width: Int, leftColor: Color, midColor: Color, rightColor: Color) {
    val seg = width / 3
    Text(
        buildAnnotatedString {
            withStyle(SpanStyle(color = leftColor, textStyle = Bold)) { append("─".repeat(seg)) }
            withStyle(SpanStyle(color = midColor, textStyle = Bold)) { append("─".repeat(seg)) }
            withStyle(SpanStyle(color = rightColor, textStyle = Bold)) { append("─".repeat(width - seg * 2)) }
        }.take(width)
    )
}

/** Vertical divider for splitting columns. */
@Composable
fun VDivider(height: Int, topColor: Color, bottomColor: Color) {
    val half = height / 2
    Column(modifier = Modifier.width(1).height(height)) {
        repeat(half) {
            Text("│", color = topColor, modifier = Modifier.height(1))
        }
        repeat(height - half) {
            Text("│", color = bottomColor, modifier = Modifier.height(1))
        }
    }
}