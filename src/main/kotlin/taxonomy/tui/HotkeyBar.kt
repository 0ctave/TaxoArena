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
    internal fun TaxonomyTuiService.HotkeyBar(
        width: Int,
        mode: AnalysisMode,
        showDomainSelector: Boolean,
        isSavingSnapshot: Boolean,
        showAsciiTree: Boolean,
        isViewingSnapshot: Boolean
    ) {
        Text(buildAnnotatedString {
            if (showDomainSelector) {
                header("Domain Filter: ")
                hotkey("↑↓", "Navigate")
                hotkey("Space/Enter", "Toggle Selection")
                hotkey("R", "Regen DAG")
                hotkey("D/Esc", "Confirm/Done")
            } else {
                when (mode) {
                    AnalysisMode.SETTINGS -> {
                        header("Configuration: ")
                        hotkey("↑↓", "Navigate")
                        hotkey("Enter", "Edit/Save")
                        hotkey("R", "Adapt Taxonomy")
                        hotkey("M", "Metrics")
                        hotkey("Q/Esc", "Back")
                    }
                    AnalysisMode.METRICS -> {
                        header("Metrics View: ")
                        hotkey("Q/Esc", "Back to DAG")
                    }
                    AnalysisMode.SNAPSHOTS -> {
                        if (isRenamingSnapshot) {
                            header("Rename Snapshot: ")
                            hotkey("Enter", "Save")
                            hotkey("Esc/Q", "Cancel")
                        } else if (isSavingSnapshot) {
                            header("Save Snapshot: ")
                            hotkey("Enter", "Confirm Description")
                            hotkey("Esc", "Cancel")
                        } else {
                            header("Snapshots History: ")
                            hotkey("↑↓", "Select")
                            hotkey("L", "Load Active")
                            hotkey("N", "Save New")
                            hotkey("D", "Delete")
                            hotkey("Esc/Q", "Back")
                        }
                    }
                    AnalysisMode.LOGS_SCROLL -> {
                        header("System Logs: ")
                        hotkey("↑↓", "Scroll Logs")
                        hotkey("Q/Esc", "Exit Scroll")
                    }
                    AnalysisMode.ARENA -> {
                        if (isEnteringArenaQuery) {
                            header("Arena Query: ")
                            hotkey("Enter", "Next")
                            hotkey("Esc/Q", "Cancel")
                        } else if (isEnteringArenaModelA) {
                            header("Arena Model A: ")
                            hotkey("Enter", "Next")
                            hotkey("Esc/Q", "Back")
                        } else if (isEnteringArenaModelB) {
                            header("Arena Model B: ")
                            hotkey("Enter", "Run Match")
                            hotkey("Esc/Q", "Back")
                        } else {
                            header("Arena View: ")
                            hotkey("Q/Esc/←", "Back to DAG")
                        }
                    }
                    AnalysisMode.TRICKLE_TEST -> {
                        if (isEnteringTrickleQuery) {
                            header("Trickle Query: ")
                            hotkey("Enter", "Run Trickle")
                            hotkey("Esc/Q", "Cancel")
                        } else {
                            header("Trickle Routing: ")
                            hotkey("T", "Single Query")
                            hotkey("B", "Batch Test")
                            if (isViewingBatchTrickleResults) {
                                hotkey("↑↓", "Scroll Results")
                            }
                            hotkey("Q/Esc/←", "Back to DAG")
                        }
                    }
                    AnalysisMode.JUDGE_PROGRESS -> {
                        if (isEnteringBatchGenerality) {
                            header("Batch Generality: ")
                            hotkey("Enter", "Start")
                            hotkey("Esc/Q", "Cancel")
                        } else {
                            header("Judge Progress: ")
                            hotkey("Q/Esc/←", "Back to DAG")
                        }
                    }
                    else -> {
                        header("System: ")
                        hotkey("↑↓", "Navigate")
                        hotkey("Enter", "Inspect")
                        hotkey("M", "Metrics")
                        if (isViewingSnapshot && activeSnapshotId != null) {
                            hotkey("N", "Rename Snap")
                        }
                        hotkey("A", "Arena")
                        hotkey("T", "Trickle")
                        hotkey("L", "Logs")
                        hotkey("X", "Setup Hub")
                        hotkey("E", "Export ASCII")
                        hotkey("V", if (showAsciiTree) "Flat List" else "Tree View")
                        
                        withStyle(SpanStyle(color = Color.Blue)) { append(" │ ") }
                        
                        header("Judges: ")
                        hotkey("R", "Gen Node")
                        hotkey("G", "Batch")
                        hotkey("F", "Force Batch")
                    }
                }
            }
        }.take(width - 1), modifier = Modifier.height(1))
    }
