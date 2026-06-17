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
    internal fun TaxonomyTuiService.DomainSelectorTable(
        pWidth: Int,
        pHeight: Int,
        domains: List<Pair<String, Int>>,
        offset: Int,
        selectedIdx: Int,
        selectedDomains: List<String>
    ) {
        if (domains.isEmpty()) {
            Column {
                Spacer(Modifier.height(2))
                Text("  ◌ No MMLU Pro cache found in DB".take(pWidth - 1), color = Yellow)
            }
            return
        }

        val visible = (pHeight - 2).coerceAtLeast(1)
        val startIdx = offset.coerceIn(0, maxOf(0, domains.size - visible))
        val items = domains.drop(startIdx).take(visible)
        val maxScroll = maxOf(0, domains.size - visible)

        // Column widths: [checkbox: 8][name: fills space][count: 9]
        val NAME_W = (pWidth - 20).coerceAtLeast(10)

        Row(modifier = Modifier.width(pWidth).height(pHeight)) {
            Column(modifier = Modifier.width(pWidth - 2)) {
                // Header
                Text(buildAnnotatedString {
                    withStyle(SpanStyle(color = White, textStyle = Bold)) {
                        append("    Sel ")
                        append("Domain".padEnd(NAME_W))
                        append("  Queries")
                    }
                }.take(pWidth - 3))

                Spacer(Modifier.height(1))

                items.forEachIndexed { i, (name, count) ->
                    val absIdx = startIdx + i
                    val isSel = absIdx == selectedIdx
                    val isChecked = if (selectedDomains.isEmpty()) true else selectedDomains.contains(name)
                    val box = if (isChecked) "[X]" else "[ ]"
                    
                    val nameStr = if (name.length > NAME_W) name.take(NAME_W - 1) + "…" else name.padEnd(NAME_W)
                    val countStr = count.toString().padStart(6) + " q"

                    val line = buildAnnotatedString {
                        if (isSel) {
                            withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
                                append("  ▶ ")
                                append(box)
                                append(" ")
                                append(nameStr)
                                append(" ")
                                append(countStr)
                            }
                        } else {
                            withStyle(SpanStyle(color = if (isChecked) Green else White)) {
                                append("    ")
                                append(box)
                                append(" ")
                            }
                            withStyle(SpanStyle(color = if (isChecked) White else White)) {
                                append(nameStr)
                            }
                            append(" ")
                            withStyle(SpanStyle(color = Cyan)) {
                                append(countStr)
                            }
                        }
                    }
                    Text(line.take(pWidth - 3), modifier = Modifier.height(1))
                }
                repeat(visible - items.size) { Text(" ".repeat(pWidth - 3)) }
            }

            // Scrollbar column
            Column(modifier = Modifier.width(2)) {
                if (maxScroll > 0) {
                    val thumbPos = ((startIdx.toDouble() / maxScroll) * (visible - 1)).toInt().coerceIn(0, visible - 1)
                    repeat(visible) { i ->
                        Text(if (i == thumbPos) " #" else " |", color = if (i == thumbPos) Cyan else White)
                    }
                } else {
                    repeat(visible) { Text("  ", color = White) }
                }
            }
        }
    }
