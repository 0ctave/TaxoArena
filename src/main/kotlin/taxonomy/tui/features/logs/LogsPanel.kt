package taxonomy.tui.features.logs

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import com.jakewharton.mosaic.layout.height
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
 *
 * All bare Text() calls in the diagnostics empty-state block clip to (width-1) so that
 * Mosaic never receives a draw call wider than the allocated column space.
 */
@Composable
fun LogsPanel(
    width: Int,
    height: Int,
    scrollOffset: Int,
    title: String = "",
    dispatch: (taxonomy.tui.controller.TuiEvent) -> Unit = {},
) {
    val safeW = width.coerceAtLeast(1)
    val logs = remember(TuiLogAppender.logsVersion.value) {
        synchronized(TuiLogAppender.logs) { ArrayList(TuiLogAppender.logs) }
    }
    val diag = remember(TuiLogAppender.logsVersion.value) { TuiLogAppender.diagnostics() }
    val visible = height.coerceAtLeast(1)

    if (logs.isEmpty()) {
        // Clip every line to (safeW - 1) so no Text overflows its allocated box.
        val lim = (safeW - 1).coerceAtLeast(1)
        Column {
            val appenders = if (diag.attachedAppenderNames.isEmpty()) "none"
                else diag.attachedAppenderNames.joinToString(",")
            val last = diag.lastAppendAt?.toString() ?: "never"
            Text("no logs yet — pipeline diagnostics:".take(lim), color = White)
            Text("  taxonomy INFO active : ${diag.infoActive}".take(lim), color = White)
            Text("  TUI appender attached: ${diag.appenderAttached}  (root appenders: $appenders)".take(lim), color = White)
            Text("  buffer size          : ${diag.bufferSize}".take(lim), color = White)
            Text("  appends seen (life)  : ${diag.appendCount}".take(lim), color = White)
            Text("  last append at       : $last".take(lim), color = White)
            Text("  loggerContext hash   : ${diag.loggerContextIdentityHash}".take(lim), color = White)
        }
        return
    }

    ScrollablePanelContent(
        pWidth = safeW,
        pHeight = visible,
        itemCount = logs.size,
        scrollOffset = scrollOffset,
        hasPadding = false,
        reversed = true,
        onScrollClamp = { dispatch(taxonomy.tui.controller.TuiEvent.ScrollTo(taxonomy.tui.state.ScrollbarTarget.LOGS, it)) }
    ) { visibleHeight, _, contentWidth ->
        val end = (logs.size - scrollOffset).coerceIn(0, logs.size)
        val start = (end - visibleHeight).coerceAtLeast(0)
        val lines = logs.subList(start, end)
        lines.forEach { raw ->
            val first = raw.split('\n', '\r').firstOrNull()?.trim() ?: ""
            val color = when {
                first.contains("ERROR") -> Red
                first.contains("WARN") -> Yellow
                first.contains("INFO") || first.contains("DEBUG") -> Cyan
                else -> White
            }
            val body = first.take((contentWidth - 2).coerceAtLeast(1))
            Text(
                buildAnnotatedString {
                    withStyle(SpanStyle(color = color)) { append(body) }
                },
                modifier = Modifier.height(1)
            )
        }
    }
}
