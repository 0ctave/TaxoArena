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
    internal fun TaxonomyTuiService.SettingsHub(
        pWidth: Int,
        pHeight: Int,
        selectedIdx: Int,
        isEditing: Boolean,
        editingVal: String,
        items: List<SettingItem>,
        isRegenerating: Boolean,
        regeneratingColor: Color
    ) {
        Column {
            Text(buildAnnotatedString {
                withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
                    append("  ◈ SYSTEM CONFIGURATION & HYPERPARAMETERS ")
                }
                if (isRegenerating) {
                    withStyle(SpanStyle(color = regeneratingColor, textStyle = Bold)) {
                        append(" [REGENERATING...]")
                    }
                }
            }.take(pWidth - 1))
            Spacer(Modifier.height(1))

            items.forEachIndexed { idx, item ->
                val isSel = idx == selectedIdx
                val nameStr = item.name.padEnd(22).take(22)
                val valStr = item.getValue()
                
                val line = buildAnnotatedString {
                    append("  ")
                    if (isSel) {
                        if (isEditing) {
                            withStyle(SpanStyle(color = Yellow, textStyle = Bold)) {
                                append("  ▶  ")
                                append(nameStr)
                            }
                            append("  ")
                            withStyle(SpanStyle(color = Black, background = Yellow, textStyle = Bold)) {
                                append(" EDIT: ")
                                append(editingVal.padEnd(18).take(18))
                            }
                        } else {
                            withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
                                append("  ▶  ")
                                append(nameStr)
                                append("  ")
                                append(valStr.padEnd(18).take(18))
                            }
                        }
                    } else {
                        withStyle(SpanStyle(color = White)) {
                            append("  ○   ")
                        }
                        withStyle(SpanStyle(color = White, textStyle = Bold)) {
                            append(nameStr)
                        }
                        append("  ")
                        withStyle(SpanStyle(color = Cyan)) {
                            append(valStr.padEnd(18).take(18))
                        }
                    }
                    append(" ")
                    withStyle(SpanStyle(color = White)) {
                        val descMaxLen = pWidth - 52
                        if (descMaxLen > 0) {
                            append("·  ${item.description.take(descMaxLen)}")
                        }
                    }
                }
                Text(line.take(pWidth - 1))
            }
            
            if (isEditing) {
                Spacer(Modifier.height(1))
                Text(buildAnnotatedString {
                    withStyle(SpanStyle(color = Yellow)) {
                        append("  Type new value, then press [ Enter ] to save or [ Esc ] to cancel.")
                    }
                }.take(pWidth - 1))
            } else {
                Spacer(Modifier.height(1))
                Text(buildAnnotatedString {
                    withStyle(SpanStyle(color = Green, textStyle = Bold)) {
                        append("  Press [ R ] to regenerate the DAG with these parameters.")
                    }
                }.take(pWidth - 1))
            }
        }
    }
