package taxonomy.tui.components

import com.jakewharton.mosaic.text.AnnotatedString
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.Magenta
import com.jakewharton.mosaic.ui.Color.Companion.Red
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold

/** Central place for all TUI theme constants. */
object TuiTheme {
    val DEPTH_COLORS: List<Color> = listOf(White, Cyan, Green, Yellow, Magenta, Red, Cyan)
    val SPINNER: List<String>     = listOf("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")

    // ── Semantic palette (single source of truth for state colors) ──
    /** Primary accent: focus, selection, primary actions. */
    val ACCENT: Color  = Cyan
    /** Secondary accent for distinct identities. */
    val ACCENT2: Color = Magenta
    /** Completed / success / healthy. */
    val OK: Color      = Green
    /** In-progress / running / warning. */
    val RUNNING: Color = Yellow
    /** Error / failure. */
    val ERROR: Color   = Red
    /** Default foreground / informational. */
    val INFO: Color    = White

    fun depthColor(depth: Int): Color = DEPTH_COLORS[depth.coerceIn(0, DEPTH_COLORS.lastIndex)]

    /** Border/title color for a panel given whether it currently holds focus. */
    fun panelAccent(focused: Boolean): Color = if (focused) ACCENT else INFO

    /** Color for a progress/status indicator given its lifecycle state. */
    fun statusColor(done: Boolean, error: Boolean = false): Color = when {
        error -> ERROR
        done  -> OK
        else  -> RUNNING
    }
}

fun depthColor(depth: Int): Color = TuiTheme.depthColor(depth)

/** Styled section header for AnnotatedString builders. */
fun AnnotatedString.Builder.header(text: String) {
    withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
        append(text)
    }
}

/** In-line hotkey styler for AnnotatedString builders. */
fun AnnotatedString.Builder.hotkey(key: String, label: String, color: Color = White) {
    withStyle(SpanStyle(color = color, textStyle = Bold)) {
        append("[")
        append(key)
        append("]")
    }
    append(" ")
    withStyle(SpanStyle(color = White)) {
        append(label)
    }
    append("  ")
}

// ─────────────────────────────────────────────
//  AnnotatedString & String utilities
// ─────────────────────────────────────────────

/** Safe truncation for [AnnotatedString] (no crash when n ≥ length). */
fun AnnotatedString.take(n: Int): AnnotatedString =
    if (this.length <= n) this else this.subSequence(0, n)

/** Chunk an [AnnotatedString] into lines of at most [width] chars. */
fun AnnotatedString.safeChunked(width: Int): List<AnnotatedString> {
    if (this.length <= width || width <= 0) return listOf(this)
    val result = mutableListOf<AnnotatedString>()
    var start = 0
    while (start < this.length) {
        val end = minOf(start + width, this.length)
        result.add(this.subSequence(start, end))
        start = end
    }
    return result
}

/** Centre a string within [width] columns (pads left and right). */
fun String.center(width: Int): String {
    val target = width - 1
    if (this.length >= target) return this.take(target)
    val padding = (target - this.length) / 2
    return " ".repeat(padding) + this + " ".repeat(target - this.length - padding)
}