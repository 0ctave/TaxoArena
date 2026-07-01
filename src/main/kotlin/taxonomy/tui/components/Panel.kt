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
        // Top border with the title inlaid: ╭─ TITLE ───╮
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

        // Body rows: left edge │, content box, right edge │.
        val bodyRows = (h - 2 - hintRows).coerceAtLeast(0)
        Box(modifier = Modifier.width(w).height(bodyRows)) {
            // Vertical edges drawn as a full-height frame behind the content.
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
            // Content sits inside the frame with a 2-col left inset and a 1-row top inset.
            Box(
                modifier = Modifier
                    .padding(left = 2, top = 1)
                    .width((innerW - 2).coerceAtLeast(1))
                    .height((bodyRows - 1).coerceAtLeast(1))
            ) {
                content()
            }
        }

        // Context hints row — single AnnotatedString, same pattern as body border rows.
        // A Row+Spacer approach fails: the hint Text with explicit width consumes all
        // remaining space and the right │ never renders inline.
        if (hintRows > 0) {
            Text(
                buildAnnotatedString {
                    // Left border + 1-space indent (matches body content indent)
                    withStyle(SpanStyle(color = accentColor)) { append("│") }
                    withStyle(SpanStyle(color = White)) { append(" ") }
                    // Build hint tokens
                    val hints = buildAnnotatedString {
                        contextHints.forEachIndexed { i, action ->
                            if (i > 0) withStyle(SpanStyle(color = TuiTheme.INFO)) { append("  ") }
                            hotkey(
                                key = action.key,
                                label = action.label,
                                color = action.color,
                                primary = action.isPrimary,
                            )
                        }
                    }
                    // Clip to fit: innerW - 1 (leading space) - 1 (right border)
                    val maxHintW = (innerW - 2).coerceAtLeast(0)
                    val clipped = if (hints.length <= maxHintW) hints
                                  else hints.subSequence(0, maxHintW)
                    append(clipped)
                    // Pad with spaces so the right border sits flush at column w-1
                    val pad = (innerW - 1 - clipped.length - 1).coerceAtLeast(0)
                    withStyle(SpanStyle(color = White)) { append(" ".repeat(pad)) }
                    // Right border
                    withStyle(SpanStyle(color = accentColor)) { append("│") }
                }.take(w),
                modifier = Modifier.height(1)
            )
        }

        // Bottom border: ╰─────────╯
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
