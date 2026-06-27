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
    badge: String? = null,
    content: @Composable () -> Unit
) {
    val w = width.coerceAtLeast(4)
    val h = height.coerceAtLeast(3)
    val innerW = w - 2
    // A badge is appended to the inlaid title: ╭─ PROCESSES · 3 RUNNING ─╮
    val titleText = if (!badge.isNullOrEmpty()) "$title · $badge" else title

    Column(modifier = Modifier.width(w).height(h)) {
        // Top border with the title inlaid: ╭─ TITLE ──────╮
        Text(
            buildAnnotatedString {
                withStyle(SpanStyle(color = accentColor, textStyle = Bold)) {
                    append("╭─")
                }
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
            // Content sits inside the frame with a 2-col left inset and a 1-row top inset so
            // text never hugs the border (panels share this breathing room).
            Box(modifier = Modifier.padding(left = 2, top = 1).width((innerW - 2).coerceAtLeast(1)).height((h - 3).coerceAtLeast(1))) {
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
