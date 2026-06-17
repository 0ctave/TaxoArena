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
    internal fun TaxonomyTuiService.JudgeInductionProgress(pWidth: Int, pHeight: Int, state: AnalysisPanelState) {
        Column {
            if (isEnteringBatchGenerality) {
                Text("  ◈ BATCH AGENT JUDGE GENERATION".take(pWidth - 2), color = Yellow, textStyle = Bold)
                Text("  " + "─".repeat(maxOf(0, pWidth - 4)), color = Yellow)
                Spacer(Modifier.height(1))
                Text("  Specify height limit from leaf nodes (n):".take(pWidth - 2))
                Text("  (0 = only leaves, 1 = leaves + parents, etc.)".take(pWidth - 2))
                Text(buildAnnotatedString {
                    withStyle(SpanStyle(color = Cyan)) {
                        append("  > $batchGeneralityInput")
                    }
                    withStyle(SpanStyle(color = White, textStyle = Bold)) {
                        append("█")
                    }
                }.take(pWidth - 2))
                Spacer(Modifier.height(1))
                Text("  [Enter] Start Generation  [Esc/Q] Cancel".take(pWidth - 2), color = Cyan)
                return@Column
            }

            Text(buildAnnotatedString {
                withStyle(SpanStyle(color = Yellow, textStyle = Bold)) { append("  ◈ JUDGE INDUCTION IN PROGRESS") }
            }.take(pWidth - 1))
            Text("  " + "─".repeat(maxOf(0, pWidth - 4)), color = Yellow)
            Spacer(Modifier.height(1))

            state.currentInductions.values.take(pHeight - 4).forEach { prog ->
                key(prog.nodeLabel) {
                    val percent  = if (prog.total > 0) prog.processed.toDouble() / prog.total else 0.0
                    val percentAnimState = animateFloatAsState(percent.toFloat())
                    val percentAnim = percentAnimState.value
                    
                    val labelW   = 14
                    val barW     = (pWidth - labelW - 14).coerceAtLeast(6)
                    val filled   = (percentAnim * barW).toInt()
                    val empty    = maxOf(0, barW - filled)

                    val annot = buildAnnotatedString {
                        append("  ")
                        withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
                            append(prog.nodeLabel.take(labelW).padEnd(labelW))
                        }
                        append(" [")
                        withStyle(SpanStyle(color = Green)) { append("█".repeat(filled)) }
                        withStyle(SpanStyle(color = White))  { append("░".repeat(empty)) }
                        append("] ")
                        withStyle(SpanStyle(color = Cyan))  { append("${(percentAnim * 100).toInt()}%".padStart(4)) }
                        append("  ")
                        withStyle(SpanStyle(color = if (prog.status == "READY") Green else Yellow, textStyle = Bold)) {
                            append(prog.status.take(8))
                        }
                    }
                    Text(annot.take(pWidth - 1))
                }
            }
        }
    }
