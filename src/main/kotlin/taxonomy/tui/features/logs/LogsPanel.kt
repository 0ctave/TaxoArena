package taxonomy.tui.features.logs

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Text
import taxonomy.tui.components.Panel
import taxonomy.utils.TuiLogAppender

@Composable
fun LogsPanel(
    width: Int,
    height: Int,
    scrollOffset: Int,
    title: String = "SYSTEM LOGS",
) {
    val logs = remember(TuiLogAppender.logsVersion.value) { TuiLogAppender.logs.toList() }
    val visible = (height - 2).coerceAtLeast(1)
    val start = (logs.size - visible - scrollOffset).coerceAtLeast(0)
    val end = (start + visible).coerceAtMost(logs.size)
    val lines = if (logs.isEmpty()) listOf("No logs yet.") else logs.subList(start, end)

    Panel(title, White, width, height) {
        Column(modifier = Modifier.padding(left = 1, top = 1)) {
            lines.forEach { line ->
                Text(line.take((width - 3).coerceAtLeast(1)), color = White)
            }
        }
    }
}