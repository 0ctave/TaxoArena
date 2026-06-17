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

enum class StartupState { WELCOME, CONFIG_AND_DOMAINS, MAIN_DASHBOARD }

class TreeLine(
    val node: GraphNode,
    val text: AnnotatedString,
    val isPoly: Boolean
)

class SettingItem(
        val name: String,
        val description: String,
        val getValue: () -> String,
        val setValue: (String) -> Boolean
    )

    @Composable
    fun Panel(title: String, accentColor: Color, panelWidth: Int, panelHeight: Int, content: @Composable () -> Unit) {
        Column(modifier = Modifier.width(panelWidth).height(panelHeight)) {
            // Elegant, minimalist colored header tag
            Text(buildAnnotatedString {
                withStyle(SpanStyle(color = accentColor, textStyle = Bold)) {
                    append("  $title  ")
                }
            }.take(panelWidth - 1), modifier = Modifier.height(1))
 
            // Spacer below title
            Spacer(Modifier.height(1))
 
            // Content area
            Box(modifier = Modifier.width(panelWidth).height(maxOf(1, panelHeight - 2))) {
                content()
            }
        }
    }

    @Composable
    fun HRule(width: Int, c1: Color, c2: Color, c3: Color) {
        Text("─".repeat(maxOf(0, width - 1)), color = c1, modifier = Modifier.height(1))
    }

    @Composable
    fun VDivider(panelHeight: Int, c1: Color, c2: Color) {
        Column(modifier = Modifier.width(1).height(panelHeight)) {
            repeat(panelHeight) {
                Text("│", color = c1)
            }
        }
    }

internal val DEPTH_COLORS = listOf(White, Cyan, Green, Yellow, Magenta, Red, Cyan)

fun depthColor(depth: Int): Color = DEPTH_COLORS[depth.coerceIn(0, DEPTH_COLORS.lastIndex)]

internal val SPINNER = listOf("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
