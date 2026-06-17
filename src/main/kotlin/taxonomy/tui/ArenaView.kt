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

    @Composable
    internal fun TaxonomyTuiService.DetailedArena(pWidth: Int, pHeight: Int, state: AnalysisPanelState) {
        Column {
            if (isEnteringArenaQuery) {
                Text("  ◈ ARENA MATCH CONFIGURATION".take(pWidth - 2), color = Cyan, textStyle = Bold)
                Text("  " + "─".repeat(maxOf(0, pWidth - 4)), color = Cyan)
                Spacer(Modifier.height(1))
                Text("  Enter Evaluation Query:".take(pWidth - 2))
                val lines = arenaQueryInput.chunked((pWidth - 6).coerceAtLeast(10))
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
                Text("  [Enter] Next (Model A)  [Esc/Q] Cancel".take(pWidth - 2), color = Cyan)
                return@Column
            }
            if (isEnteringArenaModelA) {
                Text("  ◈ ARENA MATCH CONFIGURATION".take(pWidth - 2), color = Cyan, textStyle = Bold)
                Text("  " + "─".repeat(maxOf(0, pWidth - 4)), color = Cyan)
                Spacer(Modifier.height(1))
                Text("  Enter Model A Name (Ollama / API):".take(pWidth - 2))
                Text(buildAnnotatedString {
                    withStyle(SpanStyle(color = Cyan)) { append("  > $arenaModelAInput") }
                    withStyle(SpanStyle(color = White, textStyle = Bold)) { append("█") }
                }.take(pWidth - 2))
                Spacer(Modifier.height(1))
                Text("  [Enter] Next (Model B)  [Esc/Q] Cancel".take(pWidth - 2), color = Cyan)
                return@Column
            }
            if (isEnteringArenaModelB) {
                Text("  ◈ ARENA MATCH CONFIGURATION".take(pWidth - 2), color = Cyan, textStyle = Bold)
                Text("  " + "─".repeat(maxOf(0, pWidth - 4)), color = Cyan)
                Spacer(Modifier.height(1))
                Text("  Enter Model B Name (Ollama / API):".take(pWidth - 2))
                Text(buildAnnotatedString {
                    withStyle(SpanStyle(color = Cyan)) { append("  > $arenaModelBInput") }
                    withStyle(SpanStyle(color = White, textStyle = Bold)) { append("█") }
                }.take(pWidth - 2))
                Spacer(Modifier.height(1))
                Text("  [Enter] Run Match  [Esc/Q] Cancel".take(pWidth - 2), color = Cyan)
                return@Column
            }

            Text(buildAnnotatedString {
                withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append("  ⚔  ARENA: ") }
                append("${state.modelA}  vs  ${state.modelB}")
            }.take(pWidth - 1))
            val q = state.query ?: ""
            val queryLines = q.chunked((pWidth - 12).coerceAtLeast(10))
            if (queryLines.isNotEmpty()) {
                queryLines.forEachIndexed { idx, line ->
                    Text(buildAnnotatedString {
                        if (idx == 0) {
                            withStyle(SpanStyle(color = Yellow, textStyle = Bold)) { append("  ◉ QUERY: ") }
                            append(line)
                        } else {
                            append("           $line")
                        }
                    })
                }
            }
            Text("  " + "─".repeat(maxOf(0, pWidth - 4)), color = White)

            val domains   = state.domainStatus.entries.toList()
            val rowsPerCol = (pHeight - 5).coerceAtLeast(1)
            val colW       = pWidth / 2
            Row(modifier = Modifier.width(pWidth)) {
                Column(modifier = Modifier.width(colW)) {
                    domains.take(rowsPerCol).forEach { (label, status) ->
                        val color = when {
                            status.contains("Model") -> Green
                            status == "JUDGING"      -> Yellow
                            else                     -> White
                        }
                        val icon = when { status.contains("Model") -> "✔"; status == "JUDGING" -> "◌"; else -> "·" }
                        Text(("  $icon ${label.take(colW - 14).padEnd(colW - 14)} ${status.take(8)}").take(colW - 1), color = color)
                    }
                }
                Column(modifier = Modifier.width(colW)) {
                    domains.drop(rowsPerCol).take(rowsPerCol).forEach { (label, status) ->
                        val color = when {
                            status.contains("Model") -> Green
                            status == "JUDGING"      -> Yellow
                            else                     -> White
                        }
                        val icon = when { status.contains("Model") -> "✔"; status == "JUDGING" -> "◌"; else -> "·" }
                        Text(("  $icon ${label.take(colW - 14).padEnd(colW - 14)} ${status.take(8)}").take(colW - 1), color = color)
                    }
                }
            }
        }
    }
