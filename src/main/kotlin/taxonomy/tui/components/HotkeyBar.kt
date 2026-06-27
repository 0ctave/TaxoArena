package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Row
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text

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