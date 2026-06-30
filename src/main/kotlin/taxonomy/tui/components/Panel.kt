package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Box
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Row
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold

/**
 * Titled panel drawn with a rounded Unicode box-drawing frame:
 *
 * ```
 * ╭─ TITLE ───────────────────╮
 * │  content                   │
 * │  [Key] Hint  [Key] Hint    │  ← contextHints row (only when hints supplied)
 * ╰────────────────────────────╯
 * ```
 *
 * The border colour reflects focus (passed in as [accentColor]); the body stays
 * neutral. Fully domain-agnostic layout container.
 *
 * @param contextHints When non-empty, a compact hint line is rendered just above
 *   the bottom border and the body height is reduced by 1 row to accommodate it.
 */
@Composable
fun Panel(
    title: String,
    accentColor: Color,
    width: Int,
    height: Int,
    badge: String? = null,
    contextHints: List<HotkeyAction> = emptyList(),
    content: @Composable () -> Unit
) {
    val w = width.coerceAtLeast(4)
    val h = height.coerceAtLeast(3)
    val innerW = w - 2
    val titleText = if (!badge.isNullOrEmpty()) "$title · $badge" else title

    // When hints are supplied we steal 1 row from the body for the hint line.
    val hintRows = if (contextHints.isNotEmpty()) 1 else 0

    Column(modifier = Modifier.width(w).height(h)) {
        // Top border with the title inlaid
        Text(
            buildAnnotatedString {
                withStyle(SpanStyle(color = accentColor, textStyle = Bold)) { append("╭─") }
                if (titleText.isNotEmpty()) {
                    withStyle(SpanStyle(color = accentColor, textStyle = Bold)) {
                        append(" ${titleText.uppercase()} ")
                    }
                }
                val used = 2 + (if (titleText.isNotEmpty()) titleText.length + 2 else 0)
                val fill = (w - used - 1).coerceAtLeast(0)
                withStyle(SpanStyle(color = accentColor, textStyle = Bold)) {
                    append("─".repeat(fill))
                    append("╮")
                }
            }.take(w),
            modifier = Modifier.height(1)
        )

        // Body rows
        val bodyRows = (h - 2 - hintRows).coerceAtLeast(0)
        Box(modifier = Modifier.width(w).height(bodyRows)) {
            Column(modifier = Modifier.width(w).height(bodyRows)) {
                repeat(bodyRows) {
                    Text(
                        buildAnnotatedString {
                            withStyle(SpanStyle(color = accentColor)) { append("│") }
                            withStyle(SpanStyle(color = White)) { append(" ".repeat(innerW)) }
                            withStyle(SpanStyle(color = accentColor)) { append("│") }
                        },
                        modifier = Modifier.height(1)
                    )
                }
            }
            Box(modifier = Modifier.padding(left = 2, top = 1)
                .width((innerW - 2).coerceAtLeast(1))
                .height((bodyRows - 1).coerceAtLeast(1))) {
                content()
            }
        }

        // Context hints row (optional)
        if (hintRows > 0) {
            Row(modifier = Modifier.width(w).height(1)) {
                // Left border
                Text(
                    buildAnnotatedString {
                        withStyle(SpanStyle(color = accentColor)) { append("│") }
                    },
                    modifier = Modifier.width(1)
                )
                // Hint tokens inline, clipped to available width
                val hintStr = buildAnnotatedString {
                    contextHints.forEachIndexed { i, action ->
                        if (i > 0) withStyle(SpanStyle(color = TuiTheme.MUTED)) { append("  ") }
                        hotkey(
                            key = action.key,
                            label = action.label,
                            color = action.color,
                            primary = action.isPrimary,
                        )
                    }
                }
                val available = (innerW - 1).coerceAtLeast(0)
                Text(
                    hintStr.let { if (it.length <= available) it else it.subSequence(0, available) },
                    modifier = Modifier.width(available)
                )
                Spacer()
                // Right border
                Text(
                    buildAnnotatedString {
                        withStyle(SpanStyle(color = accentColor)) { append("│") }
                    },
                    modifier = Modifier.width(1)
                )
            }
        }

        // Bottom border
        Text(
            buildAnnotatedString {
                withStyle(SpanStyle(color = accentColor, textStyle = Bold)) {
                    append("╰")
                    append("─".repeat((w - 2).coerceAtLeast(0)))
                    append("╯")
                }
            }.take(w),
            modifier = Modifier.height(1)
        )
    }
}
