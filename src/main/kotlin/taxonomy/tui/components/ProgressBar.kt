package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import java.util.Locale

/**
 * A single-line progress bar: "label: xx.x% [████████░░░░]".
 */
@Composable
fun ProgressBar(
    percent: Double,
    width: Int,
    label: String,
    newline: Boolean = false,
    barColor: Color = Cyan,
    textColor: Color = Green
) {
    val barWidth = (width - label.length - 10).coerceAtLeast(5)
    val filled = (percent / 100.0 * barWidth).toInt().coerceIn(0, barWidth)
    val empty = barWidth - filled
    val progressBar = "█".repeat(filled) + "░".repeat(empty)

    Text(buildAnnotatedString {
        withStyle(SpanStyle(color = textColor, textStyle = Bold)) {
            append(label)
            append(": ")
            append(String.format(Locale.US, "%5.1f%%", percent))
            append(" [")
        }
        withStyle(SpanStyle(color = barColor)) {
            append(progressBar)
        }
        withStyle(SpanStyle(color = textColor, textStyle = Bold)) {
            append("]")
        }
        if (newline) {
            append("\n")
        }
    })
}