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
import org.eclipse.lmos.arc.app.taxonomy.*
import org.eclipse.lmos.arc.app.taxonomy.operations.*

    @Composable
    internal fun TaxonomyTuiService.SnapshotsHub(
        pWidth: Int,
        pHeight: Int,
        selectedIdx: Int,
        isSaving: Boolean,
        descInput: String,
        snapshots: List<DagSnapshot>
    ) {
        Column(modifier = Modifier.padding(1)) {
            Text(buildAnnotatedString {
                withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
                    append("  ◈ DAG SNAPSHOTS ARCHIVE & COMPARATOR ")
                }
            })
            
            if (!isRenamingSnapshot && !isSaving && snapshots.isNotEmpty()) {
                Text("  Controls: [L] Load Selected as Active  ·  [N] Create New  ·  [D] Delete Selected", color = Magenta)
            }
            Spacer(Modifier.height(1))

            if (isRenamingSnapshot) {
                Column {
                    Text("  Rename Current Active Snapshot", color = Yellow, textStyle = Bold)
                    Spacer(Modifier.height(1))
                    Text("  New Description:")
                    Text(buildAnnotatedString {
                        withStyle(SpanStyle(color = Cyan)) {
                            append("  > $renameInput")
                        }
                        withStyle(SpanStyle(color = White, textStyle = Bold)) {
                            append("█")
                        }
                    })
                    Spacer(Modifier.height(1))
                    Text("  [Enter] Save  [Esc/Q] Cancel", color = Cyan)
                }
                return@Column
            }

            if (isSaving) {
                Column {
                    Text("  Create Snapshot of Current Active DAG", color = Yellow, textStyle = Bold)
                    Spacer(Modifier.height(1))
                    Text("  Enter Description:")
                    Text(buildAnnotatedString {
                        withStyle(SpanStyle(color = Cyan)) {
                            append("  > $descInput")
                        }
                        withStyle(SpanStyle(color = White, textStyle = Bold)) {
                            append("█")
                        }
                    })
                    Spacer(Modifier.height(1))
                    Text("  [Enter] Confirm  [Esc] Cancel", color = Cyan)
                }
                return@Column
            }

            if (snapshots.isEmpty()) {
                Column {
                    Text("  ◌ No saved DAG snapshots found in snapshots/ folder.", color = Yellow)
                    Spacer(Modifier.height(1))
                    Text("  Press [N] to save a snapshot of the current active DAG structure,")
                    Text("  including its query assignments, metrics, and generation settings.")
                }
                return@Column
            }

            val listW = (pWidth * 0.45).toInt().coerceAtLeast(35)
            val detailW = (pWidth - listW - 3).coerceAtLeast(30)

            Row(modifier = Modifier.width(pWidth).height(pHeight - 4)) {
                // Left Column: Snapshots List
                Column(modifier = Modifier.width(listW)) {
                    Text("  Saved Version History", color = White, textStyle = Bold)
                    Spacer(Modifier.height(1))
                    snapshots.forEachIndexed { i, snap ->
                        val isSel = i == selectedIdx
                        val prefix = if (isSel) "▶ " else "  "
                        val color = if (isSel) Cyan else White
                        
                        val numNodes = snap.graph.nodes.size
                        val numJudges = snap.graph.nodes.count { !it.judgePrompt.isNullOrEmpty() }
                        val countsStr = " (N:$numNodes/J:$numJudges)"
                        val timeStr = snap.timestamp.take(16)
                        
                        val reservedLength = prefix.length + timeStr.length + 3 + countsStr.length
                        val descLimit = (listW - reservedLength - 2).coerceAtLeast(10)
                        val desc = if (snap.description.length > descLimit) {
                            snap.description.take(descLimit - 3) + "..."
                        } else {
                            snap.description.padEnd(descLimit)
                        }
                        
                        val line = "$prefix$timeStr │ $desc$countsStr"
                        if (isSel) {
                            Text(line.take(listW), color = color, textStyle = Bold)
                        } else {
                            Text(line.take(listW), color = color)
                        }
                    }
                }

                // Vertical Separator
                Column(modifier = Modifier.width(1)) {
                    repeat(pHeight - 4) { Text("│", color = Color.Blue) }
                }

                // Right Column: Details & Comparison
                Column(modifier = Modifier.width(detailW).padding(left = 1)) {
                    val safeIdx = if (snapshots.isEmpty()) 0 else selectedIdx.coerceIn(0, snapshots.size - 1)
                    val snap = snapshots[safeIdx]
                    Text("  Snapshot Details & Comparison".take(detailW - 2), color = Yellow, textStyle = Bold)
                    Spacer(Modifier.height(1))

                    // Settings comparison
                    Text("  [Settings Used]:".take(detailW - 2), color = Magenta, textStyle = Bold)
                    Text("  Domains: ${snap.settings.selectedDomains.joinToString(", ").ifEmpty { "All" }}".take(detailW - 2))
                    Text("  MRL: ${if (snap.settings.enableMrl) "ON (${snap.settings.fixedMrlDimension}D)" else "OFF"}  LiveLabeling: ${snap.settings.enableLiveLabeling}".take(detailW - 2))
                    Text("  Tau: (Fit=${snap.settings.tauFit}, Reparent=${snap.settings.tauReparent}, Merge=${snap.settings.tauMerge})".take(detailW - 2))
                    Spacer(Modifier.height(1))

                    // Metrics Comparison Table
                    Text("  [Metrics Comparison]:".take(detailW - 2), color = Magenta, textStyle = Bold)
                    Text("  Metric                 Snapshot     Current".take(detailW - 2), color = White, textStyle = Bold)
                    
                    val curRoot = taxonomyService.getGraph()
                    val curReport = curRoot?.let { TaxonomyMetrics(it).generateReport() }
                    
                    @Composable
                    fun formatRow(label: String, valSnap: String, valCur: String) {
                        val rowStr = "  ${label.padEnd(22)} ${valSnap.padEnd(12)} $valCur"
                        Text(rowStr.take(detailW - 2))
                    }

                    formatRow("Total Nodes", snap.metrics.totalNodes.toString(), curReport?.totalNodes?.toString() ?: "-")
                    formatRow("Leaf Nodes", snap.metrics.leafNodes.toString(), curReport?.leafNodes?.toString() ?: "-")
                    formatRow("Max Depth", snap.metrics.maxDepth.toString(), curReport?.maxDepth?.toString() ?: "-")
                    formatRow("Unique Queries", snap.metrics.totalUniqueQueries.toString(), curReport?.totalUniqueQueries?.toString() ?: "-")
                    formatRow("Path Redundancy", "%.2f".format(snap.metrics.totalPathRedundancy), curReport?.totalPathRedundancy?.let { "%.2f".format(it) } ?: "-")
                    formatRow("Log Volume", "%.2f".format(snap.metrics.totalLogVolume), curReport?.totalLogVolume?.let { "%.2f".format(it) } ?: "-")
                    formatRow("Relevance Ratio", "%.2f".format(snap.metrics.relevanceComplianceRatio), curReport?.relevanceComplianceRatio?.let { "%.2f".format(it) } ?: "-")
                    
                    // Judges info
                    val nodesWithJudges = snap.graph.nodes.filter { !it.judgePrompt.isNullOrEmpty() }
                    val totalJudges = nodesWithJudges.size
                    val totalNodes = snap.graph.nodes.size
                    val percent = if (totalNodes > 0) (totalJudges * 100.0 / totalNodes) else 0.0
                    Spacer(Modifier.height(1))
                    Text("  [Induced Judges]:".take(detailW - 2), color = Magenta, textStyle = Bold)
                    Text("  Coverage: $totalJudges / $totalNodes nodes (${"%.1f".format(percent)}%)".take(detailW - 2))
                    if (nodesWithJudges.isNotEmpty()) {
                        val names = nodesWithJudges.take(3).joinToString { it.label }
                        val suffix = if (nodesWithJudges.size > 3) ", etc." else ""
                        Text("  On Nodes: $names$suffix".take(detailW - 2))
                    } else {
                        Text("  No judges induced in this snapshot.".take(detailW - 2))
                    }
                }
            }
        }
    }

