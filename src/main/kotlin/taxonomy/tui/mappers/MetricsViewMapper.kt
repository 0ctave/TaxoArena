package taxonomy.tui.mappers

import com.jakewharton.mosaic.text.AnnotatedString
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.Magenta
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import taxonomy.config.TaxonomyConfig
import taxonomy.model.IterationMetrics
import taxonomy.tui.components.header
import java.util.Locale

object MetricsViewMapper {

    fun buildMetricsLines(history: List<IterationMetrics>, config: TaxonomyConfig): List<AnnotatedString> {
        val list = mutableListOf<AnnotatedString>()
        val US = Locale.US

        list += buildAnnotatedString { header(" ◈ METRICS HISTORY & PERFORMANCE REPORT ◈ ") }
        list += buildAnnotatedString { append("") }

        if (history.isEmpty()) {
            list += buildAnnotatedString {
                withStyle(SpanStyle(color = Yellow)) { append(" No iterations completed yet.") }
            }
            return list
        }

        // --- Quality Metrics History ---
        list += buildAnnotatedString { withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append(" [Evolution History]:") } }
        val colWidths = listOf(14, 12, 12, 10, 10, 10, 10, 10, 14, 12)
        val headers = listOf("Iteration", "Nodes", "Graph Edit", "Purity", "ARI", "NMI", "Edge F1", "S. Silh.", "Time (ms)", "GPU Wait")

        list += buildRow(headers, colWidths, Magenta)

        history.forEach { m ->
            val row = listOf(
                m.iteration,
                m.totalNodes.toString(),
                "%.4f".format(US, m.graphEditDistance),
                "%.4f".format(US, m.dendrogramPurity),
                "%.4f".format(US, m.ari),
                "%.4f".format(US, m.nmi),
                "%.4f".format(US, m.edgeF1),
                "%.4f".format(US, m.sphericalSilhouette),
                m.totalTimeMs.toString(),
                m.gpuWaitTimeMs.toString()
            )
            list += buildRow(row, colWidths, White)
        }

        return list
    }

    private fun buildRow(cols: List<String>, widths: List<Int>, color: com.jakewharton.mosaic.ui.Color): AnnotatedString {
        return buildAnnotatedString {
            withStyle(SpanStyle(color = color)) {
                append(" ")
                cols.forEachIndexed { i, col ->
                    append(col.padEnd(widths[i]))
                    if (i < cols.lastIndex) append(" │ ")
                }
            }
        }
    }
}