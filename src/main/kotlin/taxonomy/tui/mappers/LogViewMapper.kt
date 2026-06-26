package taxonomy.tui.mappers

import com.jakewharton.mosaic.text.AnnotatedString
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color.Companion.Blue
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.Magenta
import com.jakewharton.mosaic.ui.Color.Companion.Red
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import taxonomy.tui.components.safeChunked

object LogViewMapper {

    /**
     * Converts raw text logs into color-coded AnnotatedStrings.
     * Highlights log levels ([INFO], [WARN], [ERROR], [DEBUG]).
     */
    fun formatLogLine(line: String, maxWidth: Int): List<AnnotatedString> {
        val colored = buildAnnotatedString {
            when {
                line.contains("[INFO]") -> {
                    val parts = line.split("[INFO]", limit = 2)
                    withStyle(SpanStyle(color = Green)) { append(parts[0] + "[INFO]") }
                    withStyle(SpanStyle(color = White)) { append(parts.getOrNull(1) ?: "") }
                }
                line.contains("[WARN]") -> {
                    val parts = line.split("[WARN]", limit = 2)
                    withStyle(SpanStyle(color = Yellow, textStyle = Bold)) { append(parts[0] + "[WARN]") }
                    withStyle(SpanStyle(color = Yellow)) { append(parts.getOrNull(1) ?: "") }
                }
                line.contains("[ERROR]") -> {
                    val parts = line.split("[ERROR]", limit = 2)
                    withStyle(SpanStyle(color = Red, textStyle = Bold)) { append(parts[0] + "[ERROR]") }
                    withStyle(SpanStyle(color = Red)) { append(parts.getOrNull(1) ?: "") }
                }
                line.contains("[DEBUG]") -> {
                    val parts = line.split("[DEBUG]", limit = 2)
                    withStyle(SpanStyle(color = Blue)) { append(parts[0] + "[DEBUG]") }
                    withStyle(SpanStyle(color = Magenta)) { append(parts.getOrNull(1) ?: "") }
                }
                else -> {
                    withStyle(SpanStyle(color = White)) { append(line) }
                }
            }
        }

        return colored.safeChunked(maxWidth)
    }
}