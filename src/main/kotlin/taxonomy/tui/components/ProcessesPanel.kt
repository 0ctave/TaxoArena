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

        // Styled section header with the live count.
        Text(
            value = "  ACTIVE PROCESSES (${rows.size})".take(width - 1),
            color = Cyan,
            textStyle = Bold,
        )

        val barW = (width - 18).coerceIn(8, 48)
        // Each row needs name + (bar) + status; with separators that's ~4 lines. Drop the blank
        // separator when vertical space is tight so rows are never clipped.
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
                // Indeterminate: total unknown (e.g. full-dataset download, eval parse before
                // the record count is known). Render a moving block instead of a fixed bar.
                val pos = spinnerTick % barW
                val track = buildString {
                    for (i in 0 until barW) append(if (i == pos) '\u2588' else '\u2591')
                }
                Text("  $track", color = color)
            }
            val status = row.status.take((width - 3).coerceAtLeast(4))
            if (status.isNotBlank()) Text("  $status", color = TuiTheme.INFO)
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
