package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Row
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold

data class HotkeyAction(
    val key: String,
    val label: String,
    val color: Color = White,
    val isPrimary: Boolean = false
)

/**
 * Global contextual hotkey row.
 * Driven entirely by a list of abstract HotkeyActions instead of nested state conditionals.
 */
@Composable
fun HotkeyBar(
    width: Int,
    actions: List<HotkeyAction>
) {
    Row(
        modifier = Modifier
            .width(width)
            .padding(left = 1)
    ) {
        val line = buildAnnotatedString {
            actions.forEachIndexed { index, action ->
                hotkey(
                    key = action.key,
                    label = action.label,
                    color = action.color,
                    primary = action.isPrimary,
                )
            }
        }
        Text(line.take(width - 2))
        Spacer()
    }
}

/**
 * Split hotkey row: feature-specific [contextual] hints on the left, persistent [global]
 * hints (Tab / Help / Quit …) on the right, separated by a "│". Globals always survive; if
 * the row is too narrow, contextual actions are dropped from the right until everything fits.
 */
@Composable
fun HotkeyBar(
    width: Int,
    contextual: List<HotkeyAction>,
    global: List<HotkeyAction>,
) {
    // hotkey() renders "[Key] Label  " = open(1)+key+close(1)+space(1)+label+2 trailing = key+label+5.
    fun actionLen(a: HotkeyAction) = a.key.length + a.label.length + 5
    val separator = "│ " // "│ "

    val budget = (width - 2).coerceAtLeast(0)
    val globalLen = global.sumOf { actionLen(it) }
    val sepLen = if (global.isNotEmpty() && contextual.isNotEmpty()) separator.length else 0
    val ctxBudget = (budget - globalLen - sepLen).coerceAtLeast(0)

    val fitting = buildList {
        var used = 0
        for (a in contextual) {
            val l = actionLen(a)
            if (used + l > ctxBudget) break
            add(a)
            used += l
        }
    }

    Row(
        modifier = Modifier
            .width(width)
            .padding(left = 1)
    ) {
        val line = buildAnnotatedString {
            fitting.forEach { action ->
                hotkey(action.key, action.label, action.color, action.isPrimary)
            }
            if (fitting.isNotEmpty() && global.isNotEmpty()) {
                withStyle(SpanStyle(color = White, textStyle = Bold)) { append(separator) }
            }
            global.forEach { action ->
                hotkey(action.key, action.label, action.color, action.isPrimary)
            }
        }
        Text(line.take(width - 2))
        Spacer()
    }
}