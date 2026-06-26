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
 * ╰────────────────────────────╯
 * ```
 *
 * The border colour reflects focus (passed in as [accentColor]); the body stays
 * neutral. Fully domain-agnostic layout container.
 */
@Composable
fun Panel(
    title: String,
    accentColor: Color,
    width: Int,
    height: Int,
    content: @Composable () -> Unit
) {
    val w = width.coerceAtLeast(4)
    val h = height.coerceAtLeast(3)
    val innerW = w - 2

    Column(modifier = Modifier.width(w).height(h)) {
        // Top border with the title inlaid: ╭─ TITLE ──────╮
        Text(
            buildAnnotatedString {
                withStyle(SpanStyle(color = accentColor, textStyle = Bold)) {
                    append("╭─")
                }
                if (title.isNotEmpty()) {
                    withStyle(SpanStyle(color = accentColor, textStyle = Bold)) {
                        append(" ${title.uppercase()} ")
                    }
                }
                val used = 2 + (if (title.isNotEmpty()) title.length + 2 else 0)
                val fill = (w - used - 1).coerceAtLeast(0)
                withStyle(SpanStyle(color = accentColor, textStyle = Bold)) {
                    append("─".repeat(fill))
                    append("╮")
                }
            }.take(w),
            modifier = Modifier.height(1)
        )

        // Body rows: a left edge, the content box, and a right edge.
        Box(modifier = Modifier.width(w).height(h - 2)) {
            // Vertical edges drawn as a full-height frame behind the content.
            Column(modifier = Modifier.width(w).height(h - 2)) {
                repeat(h - 2) {
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
            // Content sits inside the frame with a 1-col left inset.
            Box(modifier = Modifier.padding(left = 1).width(innerW).height(h - 2)) {
                content()
            }
        }

        // Bottom border: ╰────────────╯
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
