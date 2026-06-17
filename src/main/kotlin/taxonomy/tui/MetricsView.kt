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
    internal fun TaxonomyTuiService.MetricsHub(pWidth: Int, pHeight: Int) {
        val history by taxonomyService.metricsHistoryFlow.collectAsState()
        Column(modifier = Modifier.padding(1)) {
            Text(buildAnnotatedString {
                withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
                    append("  ◈ TAXONOMY EVOLUTION METRICS HISTORY ")
                }
            })
            Spacer(Modifier.height(1))

            if (history.isEmpty()) {
                Text(buildAnnotatedString {
                    withStyle(SpanStyle(color = Yellow)) {
                        append("  No metrics recorded yet.")
                    }
                })
                Text(buildAnnotatedString {
                    append("  Run regeneration (Config [C] -> Regen [R]) to adapt taxonomy.")
                })
            } else {
                // Table headers:
                // ITER     | NODES | LEAF  | CROSS | REDUND | RESID | EQUIL
                val headers = listOf("Iter", "Nodes", "Leaves", "Cross", "Redund", "Resid", "Equil")
                val colWidths = listOf(8, 6, 8, 6, 8, 7, 7)
                
                Text(buildAnnotatedString {
                    withStyle(SpanStyle(color = Yellow, textStyle = Bold)) {
                        for (i in headers.indices) {
                            append(headers[i].padEnd(colWidths[i]))
                        }
                    }
                }.take(pWidth))
                
                Text(buildAnnotatedString {
                    append("-".repeat(colWidths.sum()))
                }.take(pWidth))

                history.forEach { m ->
                    Text(buildAnnotatedString {
                        val rowColor = if (m.iteration.startsWith("Final")) Green else White
                        withStyle(SpanStyle(color = rowColor)) {
                            append(m.iteration.padEnd(colWidths[0]))
                            append(m.totalNodes.toString().padEnd(colWidths[1]))
                            append(m.leafNodes.toString().padEnd(colWidths[2]))
                            append(m.crossDomainNodes.toString().padEnd(colWidths[3]))
                            append("%.2f".format(java.util.Locale.US, m.totalPathRedundancy).padEnd(colWidths[4]))
                            append(m.residualQueries.toString().padEnd(colWidths[5]))
                            append("%.1f%%".format(java.util.Locale.US, m.equilibriumIndex * 100.0).padEnd(colWidths[6]))
                        }
                    }.take(pWidth))
                }
                
                Spacer(Modifier.height(1))
                Text(buildAnnotatedString {
                    append("  * Redund: Avg parents per node")
                }.take(pWidth))
                Text(buildAnnotatedString {
                    append("  * Equil: Tree Balance (1-Gini) based on leaf query counts")
                }.take(pWidth))

                Spacer(Modifier.height(1))
                Text("  [Active DAG Settings]:".take(pWidth - 2), color = Cyan, textStyle = Bold)
                Text("  • Domains: ${if (config.dataset.selectedDomains.isEmpty()) "All" else "${config.dataset.selectedDomains.size} selected"}".take(pWidth - 2))
                Text("  • MRL Enabled: ${config.formalism.enableMrl} (Dim: ${config.formalism.fixedMrlDimension})".take(pWidth - 2))
                Text("  • Tau Fit: ${config.formalism.tauFit} │ Tau Reparent: ${config.formalism.tauReparent} │ Tau Merge: ${config.formalism.tauMerge}".take(pWidth - 2))
            }
        }
    }
