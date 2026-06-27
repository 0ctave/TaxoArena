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
import taxonomy.tui.components.ScrollablePanelContent
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
    // Reading logsVersion subscribes this composable to recomposition when the pump drains
    // new lines. The snapshot copy MUST happen inside synchronized(logs): loadHistoricalLogs()
    // clears and refills the same synchronized list from an IO coroutine, so an unguarded
    // toList() can race it — throwing ConcurrentModificationException (which wedges the panel)
    // or observing the list mid-clear as empty.
    val logs = remember(TuiLogAppender.logsVersion.value) {
        synchronized(TuiLogAppender.logs) { ArrayList(TuiLogAppender.logs) }
    }
    // Re-queried whenever the buffer version changes (keyed on logsVersion) so the empty-state
    // overlay reflects *live* pipeline health — appends seen, last-append time, attached appenders
    // and the active LoggerContext — rather than a stale one-time snapshot. This is what lets a
    // blank panel explain precisely why it is blank (root-level filtering, detached appender,
    // split LoggerContext, or simply nothing logged yet).
    val diag = remember(TuiLogAppender.logsVersion.value) { TuiLogAppender.diagnostics() }
    val visible = height.coerceAtLeast(1)

    if (logs.isEmpty()) {
        Column {
            val appenders = if (diag.attachedAppenderNames.isEmpty()) "none"
                else diag.attachedAppenderNames.joinToString(",")
            val last = diag.lastAppendAt?.toString() ?: "never"
            Text("no logs yet — pipeline diagnostics:", color = White)
            Text("  taxonomy INFO active : ${diag.infoActive}", color = White)
            Text("  TUI appender attached: ${diag.appenderAttached}  (root appenders: $appenders)", color = White)
            Text("  buffer size          : ${diag.bufferSize}", color = White)
            Text("  appends seen (life)  : ${diag.appendCount}", color = White)
            Text("  last append at       : $last", color = White)
            Text("  loggerContext hash   : ${diag.loggerContextIdentityHash}", color = White)
        }
        return
    }

    ScrollablePanelContent(
        pWidth = width,
        pHeight = visible,
        itemCount = logs.size,
        scrollOffset = scrollOffset,
        hasPadding = false,
        reversed = true,
    ) { visibleHeight, _, contentWidth ->
        val end = (logs.size - scrollOffset).coerceIn(0, logs.size)
        val start = (end - visibleHeight).coerceAtLeast(0)
        val lines = logs.subList(start, end)
        lines.forEach { raw ->
            val first = raw.split('\n', '\r').firstOrNull()?.trim() ?: ""
            val (glyph, color) = when {
                first.contains("ERROR") -> "\u2716 " to Red
                first.contains("WARN") -> "\u26a0 " to Yellow
                first.contains("INFO") || first.contains("DEBUG") -> "\u2139 " to Cyan
                else -> "  " to White
            }
            val body = first.take((contentWidth - 2).coerceAtLeast(1))
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