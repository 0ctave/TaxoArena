package taxonomy.tui.features.logs

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Red
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import taxonomy.utils.TuiLogAppender

/**
 * Renders the system-log tail as plain content. The caller (router) owns the bordered
 * [taxonomy.tui.components.Panel] frame, so this draws content only — no inner border.
 * Newest lines sit at the bottom; [scrollOffset] scrolls back into history.
 */
@Composable
fun LogsPanel(
    width: Int,
    height: Int,
    scrollOffset: Int,
    title: String = "",
) {
    val logs = remember(TuiLogAppender.logsVersion.value) { TuiLogAppender.logs.toList() }
    val visible = height.coerceAtLeast(1)
    val end = (logs.size - scrollOffset).coerceIn(0, logs.size)
    val start = (end - visible).coerceAtLeast(0)
    val lines = logs.subList(start, end)

    Column(modifier = Modifier.padding(left = 1)) {
        if (lines.isEmpty()) {
            Text("No logs yet.", color = White)
            return@Column
        }
        lines.forEach { raw ->
            val first = raw.split('\n', '\r').firstOrNull()?.trim() ?: ""
            val (glyph, color) = when {
                first.contains(" ERROR ") || first.startsWith("ERROR") -> "\u2716 " to Red
                first.contains(" WARN ") || first.startsWith("WARN") -> "\u26a0 " to Yellow
                first.contains(" INFO ") || first.startsWith("INFO") -> "\u2139 " to Cyan
                else -> "  " to White
            }
            val body = first.take((width - 4).coerceAtLeast(1))
            Text(
                buildAnnotatedString {
                    withStyle(SpanStyle(color = color, textStyle = Bold)) { append(glyph) }
                    withStyle(SpanStyle(color = color)) { append(body) }
                },
                modifier = Modifier.height(1)
            )
        }
    }
}