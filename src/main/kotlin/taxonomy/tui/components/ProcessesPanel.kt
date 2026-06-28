package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.Magenta
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold

/**
 * A single running/finished process row, rendered uniformly regardless of the
 * underlying source (dataset download, embedding, generation, labeling, judge).
 */
data class ProcessRow(
    val name: String,
    /** 0..100 (or null when indeterminate). */
    val percent: Double?,
    val status: String,
    val done: Boolean = false,
    val error: Boolean = false,
)

/**
 * Live "running processes" panel: one colored row per active (or just-finished)
 * process with a progress bar and status text. Always renderable so unfinished
 * work is never hidden. UI-agnostic — caller derives [rows] from app state.
 *
 * Width-safety contract
 * ---------------------
 * Mosaic 0.18.0's TextSurface.get throws IllegalStateException("Check failed") when a
 * Text composable draws past the end of its allocated row. Two distinct failure modes
 * exist here:
 *
 * 1. Embedded newlines in row.status: the judge process sets its status to a raw LLM
 *    response (multi-line JSON). String.take(n) counts *characters*, not lines, so a
 *    300-char take still leaves \n chars inside the string. Mosaic then tries to draw
 *    the newline continuation into a surface row that doesn't exist -> crash.
 *    Fix: take only the first non-blank line of status before width-clipping.
 *
 * 2. Indeterminate progress track: Text("  $track") had no width guard, so on narrow
 *    panels "  " + barW chars could exceed the available column.
 *    Fix: take(width - 1) on the assembled track string.
 */
@Composable
fun ProcessesPanel(
    width: Int,
    height: Int,
    rows: List<ProcessRow>,
    spinnerTick: Int,
) {
    Column(modifier = Modifier.padding(left = 1, top = 0)) {
        if (rows.isEmpty()) {
            val s = TuiTheme.SPINNER[spinnerTick % TuiTheme.SPINNER.size]
            Text("Idle $s  no active processes", color = TuiTheme.INFO)
            return@Column
        }

        Text(
            value = "  ACTIVE PROCESSES (${rows.size})".take(width - 1),
            color = Cyan,
            textStyle = Bold,
        )

        val barW = (width - 18).coerceIn(8, 48)
        val budget = (height - 2).coerceAtLeast(1)
        val withSeparators = budget >= rows.size * 4
        rows.take((budget / if (withSeparators) 4 else 3).coerceAtLeast(1)).forEachIndexed { idx, row ->
            val color = TuiTheme.statusColor(done = row.done, error = row.error)
            val marker = when {
                row.error -> "x"
                row.done  -> "\u2713"
                else      -> TuiTheme.SPINNER[spinnerTick % TuiTheme.SPINNER.size]
            }
            Text(
                value = "$marker ${row.name}".take(width - 1),
                color = nameColor(row.name, color),
                textStyle = Bold,
            )
            if (row.percent != null) {
                ProgressBar(
                    percent = row.percent,
                    width = barW,
                    label = "  ",
                    barColor = color,
                    textColor = color,
                )
            } else if (!row.done && !row.error) {
                val pos = spinnerTick % barW
                val track = buildString {
                    for (i in 0 until barW) append(if (i == pos) '\u2588' else '\u2591')
                }
                // Guard: "  " prefix + track must not exceed available width.
                Text("  $track".take(width - 1), color = color)
            }
            // Extract the first non-blank line of status so that multi-line LLM responses
            // (judge prompts, JSON blobs) never embed \n into a single-line Text draw call.
            val statusLine = row.status
                .lineSequence()
                .firstOrNull { it.isNotBlank() }
                ?.trim()
                ?.take((width - 3).coerceAtLeast(4))
                ?: ""
            if (statusLine.isNotBlank()) Text("  $statusLine", color = TuiTheme.INFO)
            if (withSeparators && idx < rows.lastIndex) Text("", color = TuiTheme.INFO)
        }
    }
}

/** Tint the process name by its kind so the panel reads at a glance. */
private fun nameColor(name: String, fallback: Color): Color = when {
    name.contains("Dataset download", ignoreCase = true) -> Cyan
    name.contains("Embeddings", ignoreCase = true) -> Yellow
    name.contains("DAG generation", ignoreCase = true) -> Green
    name.contains("Labeling", ignoreCase = true) -> Magenta
    name.contains("Eval", ignoreCase = true) -> White
    name.contains("Judge", ignoreCase = true) -> Magenta
    else -> fallback
}
