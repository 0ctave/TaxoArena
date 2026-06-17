package org.eclipse.lmos.arc.app.taxonomy.tui

import androidx.compose.runtime.*
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.*
import com.jakewharton.mosaic.layout.*
import com.jakewharton.mosaic.text.*
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import com.jakewharton.mosaic.ui.Color.Companion.Blue
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.Magenta
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Black
import com.jakewharton.mosaic.ui.Color.Companion.Red
import com.jakewharton.mosaic.animation.animateColorAsState
import kotlinx.coroutines.*
import kotlinx.serialization.json.*
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import org.eclipse.lmos.arc.app.taxonomy.*
import org.eclipse.lmos.arc.app.taxonomy.operations.*
import com.jakewharton.mosaic.LocalTerminalState
import com.jakewharton.mosaic.terminal.Terminal
import com.jakewharton.mosaic.terminal.*
import com.jakewharton.mosaic.animation.*
import org.fusesource.jansi.AnsiConsole

private fun Double.formatPct(): String = "${"%.1f".format(java.util.Locale.US, this * 100.0)}%"
private fun Double.format2d(): String = "%.2f".format(java.util.Locale.US, this)

@Composable
internal fun TaxonomyTuiService.TrickleTestHub(pWidth: Int, pHeight: Int) {
    Column {
        if (isRunningBatchTrickleTest) {
            Text("  ◈ BATCH TRICKLE ROUTING TEST SUITE".take(pWidth - 2), color = Cyan, textStyle = Bold)
            Text("  " + "─".repeat(maxOf(0, pWidth - 4)), color = Cyan)
            Spacer(Modifier.height(2))
            Text("  $batchTrickleProgress".take(pWidth - 2), color = Yellow)
            Spacer(Modifier.height(1))
            Text("  Please wait while we route test queries down the DAG...".take(pWidth - 2), color = White)
            return@Column
        }

        if (isViewingBatchTrickleResults && batchTrickleResults != null) {
            val results = batchTrickleResults!!
            Text("  ◈ BATCH TRICKLE SUITE RESULTS".take(pWidth - 2), color = Cyan, textStyle = Bold)
            Text("  " + "─".repeat(maxOf(0, pWidth - 4)), color = Cyan)
            Spacer(Modifier.height(1))

            if (pWidth < 60) {
                Column {
                    Text("  • Total Queries:      ${results.totalQueries}".take(pWidth - 2), color = White)
                    Text("  • Overall Accuracy:   ${results.overallAccuracy.formatPct()}".take(pWidth - 2), color = White)
                    Text("  • Leaf Assignment:    ${results.leafRate.formatPct()}".take(pWidth - 2), color = White)
                    Text("  • Residual Rate:      ${results.residualRate.formatPct()}".take(pWidth - 2), color = White)
                    Text("  • Avg Path Depth:     ${results.averageDepth.format2d()}".take(pWidth - 2), color = White)
                    Text("  • Avg Match Count:    ${results.averageMatches.format2d()}".take(pWidth - 2), color = White)
                }
            } else {
                Row {
                    Column {
                        Text("  • Total Queries:      ", color = White)
                        Text("  • Overall Accuracy:   ", color = White)
                        Text("  • Leaf Assignment:    ", color = White)
                    }
                    Column {
                        Text("${results.totalQueries} queries", color = Yellow, textStyle = Bold)
                        Text(results.overallAccuracy.formatPct(), color = Green, textStyle = Bold)
                        Text(results.leafRate.formatPct(), color = Cyan, textStyle = Bold)
                    }
                    Spacer(Modifier.width(4))
                    Column {
                        Text("• Residual Rate:   ", color = White)
                        Text("• Avg Path Depth:  ", color = White)
                        Text("• Avg Match Count: ", color = White)
                    }
                    Column {
                        Text(results.residualRate.formatPct(), color = Yellow, textStyle = Bold)
                        Text(results.averageDepth.format2d(), color = Blue, textStyle = Bold)
                        Text(results.averageMatches.format2d(), color = Magenta, textStyle = Bold)
                    }
                }
            }
            Spacer(Modifier.height(1))
            Text("  DOMAIN BREAKDOWN:".take(pWidth - 2), color = Cyan, textStyle = Bold)

            val colDomainWidth = 24
            val colTotalWidth = 7
            val colCorrectWidth = 9
            val colAccWidth = 10
            val colLeafWidth = 11
            val colDepthWidth = 10

            val headerStr = buildString {
                append("  ")
                append("Domain".padEnd(colDomainWidth))
                append("│ ")
                append("Total".padEnd(colTotalWidth))
                append("│ ")
                append("Correct".padEnd(colCorrectWidth))
                append("│ ")
                append("Accuracy".padEnd(colAccWidth))
                append("│ ")
                append("Leaf Rate".padEnd(colLeafWidth))
                append("│ ")
                append("Avg Depth".padEnd(colDepthWidth))
            }
            Text(headerStr.take(pWidth - 2), color = White, textStyle = Bold)

            val separator = buildString {
                append("  ")
                append("─".repeat(colDomainWidth))
                append("┼─")
                append("─".repeat(colTotalWidth))
                append("┼─")
                append("─".repeat(colCorrectWidth))
                append("┼─")
                append("─".repeat(colAccWidth))
                append("┼─")
                append("─".repeat(colLeafWidth))
                append("┼─")
                append("─".repeat(colDepthWidth))
            }
            Text(separator.take(pWidth - 2), color = Cyan)

            val visibleTableHeight = (pHeight - 12).coerceAtLeast(3)
            val scrollOffset = batchTrickleScrollOffset
            val domainMetrics = results.domainMetrics

            domainMetrics.drop(scrollOffset).take(visibleTableHeight).forEach { dm ->
                val domainName = if (dm.domain.length > colDomainWidth - 2) dm.domain.take(colDomainWidth - 5) + "..." else dm.domain
                val rowStr = buildString {
                    append("  ")
                    append(domainName.padEnd(colDomainWidth))
                    append("│ ")
                    append(dm.total.toString().padEnd(colTotalWidth))
                    append("│ ")
                    append(dm.correct.toString().padEnd(colCorrectWidth))
                    append("│ ")
                    append(dm.accuracy.formatPct().padEnd(colAccWidth))
                    append("│ ")
                    append(dm.leafRate.formatPct().padEnd(colLeafWidth))
                    append("│ ")
                    append(dm.averageDepth.format2d().padEnd(colDepthWidth))
                }
                Text(rowStr.take(pWidth - 2))
            }

            if (domainMetrics.size > visibleTableHeight) {
                val remaining = domainMetrics.size - visibleTableHeight - scrollOffset
                val upStr = if (scrollOffset > 0) "▲" else " "
                val downStr = if (remaining > 0) "▼" else " "
                Text("  [Scroll $upStr $downStr | W/Z or Up/Down arrows]".take(pWidth - 2), color = Cyan)
            }
            return@Column
        }

        if (isEnteringTrickleQuery) {
            Text("  ◈ TRICKLE ROUTING TEST".take(pWidth - 2), color = Cyan, textStyle = Bold)
            Text("  " + "─".repeat(maxOf(0, pWidth - 4)), color = Cyan)
            Spacer(Modifier.height(1))
            Text("  Enter text query to test routing path:".take(pWidth - 2))
            val lines = trickleQueryInput.chunked((pWidth - 6).coerceAtLeast(10))
            if (lines.isEmpty()) {
                Text(buildAnnotatedString {
                    withStyle(SpanStyle(color = Cyan)) { append("  > ") }
                    withStyle(SpanStyle(color = White, textStyle = Bold)) { append("█") }
                }.take(pWidth - 2))
            } else {
                lines.forEachIndexed { idx, line ->
                    Text(buildAnnotatedString {
                        if (idx == 0) {
                            withStyle(SpanStyle(color = Cyan)) { append("  > $line") }
                        } else {
                            withStyle(SpanStyle(color = Cyan)) { append("    $line") }
                        }
                        if (idx == lines.lastIndex) {
                            withStyle(SpanStyle(color = White, textStyle = Bold)) { append("█") }
                        }
                    }.take(pWidth - 2))
                }
            }
            Spacer(Modifier.height(1))
            Text("  [Enter] Run Routing  [Esc/Q] Cancel".take(pWidth - 2), color = Cyan)
            return@Column
        }

        Text("  ◈ TRICKLE ROUTING PATHS".take(pWidth - 2), color = Cyan, textStyle = Bold)
        Text("  " + "─".repeat(maxOf(0, pWidth - 4)), color = Cyan)
        Spacer(Modifier.height(1))
        val queryLines = trickleQueryInput.chunked((pWidth - 12).coerceAtLeast(10))
        if (queryLines.isNotEmpty()) {
            queryLines.forEachIndexed { idx, line ->
                Text(buildAnnotatedString {
                    if (idx == 0) {
                        withStyle(SpanStyle(color = Yellow, textStyle = Bold)) { append("  ◉ Query: ") }
                        append(line)
                    } else {
                        append("           $line")
                    }
                }.take(pWidth - 2))
            }
        }
        Spacer(Modifier.height(1))
        if (trickleResultNodes.isEmpty()) {
            Text("  No matching nodes found.".take(pWidth - 2), color = Red)
        } else {
            trickleResultNodes.take(pHeight - 6).forEachIndexed { idx, node ->
                val depthStr = "Depth ${node.depth}".padEnd(9)
                Text(("  ${idx + 1}. $depthStr │ ${node.label} (${node.queries.size} direct, ${node.getRecursiveQueryCount()} recursive queries)").take(pWidth - 2))
            }
        }
    }
}
