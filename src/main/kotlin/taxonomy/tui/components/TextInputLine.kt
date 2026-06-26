package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold

/**
 * Common text input line rendering for forms (Arena, Trickle, Snapshots, Settings).
 * Automatically truncates to fit width and renders a blinking cursor block.
 */
@Composable
fun TextInputLine(
    prompt: String,
    input: String,
    width: Int,
    promptColor: Color = Yellow,
    inputColor: Color = White,
    cursorColor: Color = Cyan,
    showCursor: Boolean = true
) {
    Text(
        buildAnnotatedString {
            withStyle(SpanStyle(color = promptColor, textStyle = Bold)) {
                append(prompt)
                append(" ")
            }

            val remainingWidth = (width - prompt.length - 2).coerceAtLeast(1)
            val displayText = if (input.length > remainingWidth - 1) {
                "..." + input.takeLast(remainingWidth - 4)
            } else {
                input
            }

            withStyle(SpanStyle(color = inputColor)) {
                append(displayText)
            }

            if (showCursor) {
                withStyle(SpanStyle(color = cursorColor)) {
                    append("█")
                }
            }
        }.take(width)
    )
}