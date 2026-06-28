package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.AnnotatedString
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Column
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
 * A named group of [HotkeyAction]s shown with a bold section label in the bar.
 *
 * Example: `HotkeyGroup("DAG", listOf(HotkeyAction("M", "Metrics"), ...))`
 * renders as `DAG : [M] Metrics  [C] Config  …`
 */
data class HotkeyGroup(
    val label: String,
    val actions: List<HotkeyAction>,
)

// ──────────────────────────────────────────────────────────────────────────────
//  Internal helpers
// ──────────────────────────────────────────────────────────────────────────────

/** Character width of a single [HotkeyAction] as rendered by [hotkey]. */
private fun actionLen(a: HotkeyAction): Int = a.key.length + a.label.length + 5

/** Character width of `"LABEL : "` prefix for a group. */
private fun groupPrefixLen(g: HotkeyGroup): Int = g.label.length + 3   // " : "

/** Character width of `"| "` separator between groups. */
private const val SEP_LEN = 2

/**
 * Render one [HotkeyAction] into an [AnnotatedString.Builder].  Matches [TuiTheme.hotkey]
 * exactly so styling is consistent everywhere.
 */
private fun AnnotatedString.Builder.appendAction(action: HotkeyAction) {
    hotkey(
        key    = action.key,
        label  = action.label,
        color  = action.color,
        primary = action.isPrimary,
    )
}

/**
 * Render a group label prefix: `"LABEL : "`.
 */
private fun AnnotatedString.Builder.appendGroupLabel(label: String) {
    withStyle(SpanStyle(color = White, textStyle = Bold)) { append(label) }
    withStyle(SpanStyle(color = White)) { append(" : ") }
}

/**
 * Render the `"| "` inter-group separator.
 */
private fun AnnotatedString.Builder.appendSeparator() {
    withStyle(SpanStyle(color = White, textStyle = Bold)) { append("| ") }
}

// ──────────────────────────────────────────────────────────────────────────────
//  Word-wrap core
// ──────────────────────────────────────────────────────────────────────────────

/**
 * Represents a logical token in the hotkey bar: either a [GroupLabel], an [Action], or a
 * [Separator] between groups.  All tokens know their visual column width.
 */
private sealed interface Token {
    val width: Int

    data class GroupLabel(val text: String) : Token {
        override val width: Int get() = text.length + 3  // "LABEL : "
    }

    data class Action(val action: HotkeyAction) : Token {
        override val width: Int get() = actionLen(action)
    }

    data object Separator : Token {
        override val width: Int = SEP_LEN
    }
}

/**
 * Tokenize a flat list of [HotkeyAction]s (no groups) into [Token]s.
 */
private fun tokenize(actions: List<HotkeyAction>): List<Token> =
    actions.map { Token.Action(it) }

/**
 * Tokenize a list of [HotkeyGroup]s into [Token]s, inserting separators between groups.
 */
private fun tokenize(groups: List<HotkeyGroup>): List<Token> = buildList {
    groups.forEachIndexed { idx, group ->
        if (idx > 0) add(Token.Separator)
        if (group.label.isNotEmpty()) add(Token.GroupLabel(group.label))
        group.actions.forEach { add(Token.Action(it)) }
    }
}

/**
 * Split [tokens] into rows of at most [rowWidth] columns each.
 *
 * Rules:
 * - A [Token.GroupLabel] always starts on the same row as the first action in its group
 *   (i.e. if the label + first action don't fit, wrap before the label, not between label
 *   and action).
 * - A [Token.Separator] is dropped if it would be the first token on a new line.
 * - Any single token that is wider than [rowWidth] is placed on its own row (no infinite
 *   loop; it is still safe).
 */
private fun wrapTokens(tokens: List<Token>, rowWidth: Int): List<List<Token>> {
    if (rowWidth <= 0) return if (tokens.isEmpty()) emptyList() else listOf(tokens)

    val rows   = mutableListOf<MutableList<Token>>()
    var current = mutableListOf<Token>()
    var used    = 0

    fun flush() {
        if (current.isNotEmpty()) {
            rows.add(current)
            current = mutableListOf()
            used    = 0
        }
    }

    var i = 0
    while (i < tokens.size) {
        val tok = tokens[i]

        // Separators at the start of a new row are silently dropped.
        if (tok is Token.Separator && used == 0) { i++; continue }

        // For a GroupLabel, peek ahead to the first Action of this group so we can keep
        // them together on the same line.
        val lookaheadWidth: Int = if (tok is Token.GroupLabel && i + 1 < tokens.size) {
            val next = tokens[i + 1]
            if (next is Token.Action) tok.width + next.width else tok.width
        } else {
            tok.width
        }

        if (used + lookaheadWidth > rowWidth && used > 0) {
            // Doesn't fit — start a new row.
            flush()
            // Skip a leading separator on the new row.
            if (tok is Token.Separator) { i++; continue }
        }

        current.add(tok)
        used += tok.width
        i++
    }
    flush()
    return rows
}

/**
 * Render a list of [Token]s into a single [AnnotatedString].
 */
private fun renderRow(tokens: List<Token>): AnnotatedString = buildAnnotatedString {
    tokens.forEach { tok ->
        when (tok) {
            is Token.GroupLabel -> appendGroupLabel(tok.text)
            is Token.Action     -> appendAction(tok.action)
            is Token.Separator  -> appendSeparator()
        }
    }
}

// ──────────────────────────────────────────────────────────────────────────────
//  Public composables
// ──────────────────────────────────────────────────────────────────────────────

/**
 * Simple single-section hotkey bar driven by a flat [actions] list.
 * Wraps onto additional rows automatically if the content overflows [width].
 */
@Composable
fun HotkeyBar(
    width: Int,
    actions: List<HotkeyAction>
) {
    val rowWidth = (width - 2).coerceAtLeast(1)
    val tokens   = tokenize(actions)
    val rows     = wrapTokens(tokens, rowWidth)

    Column(modifier = Modifier.width(width).padding(left = 1)) {
        if (rows.isEmpty()) {
            // Always emit at least one Text node so the layout sees exactly the right height.
            Row(modifier = Modifier.width(rowWidth)) { Spacer() }
        } else {
            rows.forEach { rowTokens ->
                val line = renderRow(rowTokens)
                Row(modifier = Modifier.width(rowWidth)) {
                    Text(line.safeClip(rowWidth))
                    Spacer()
                }
            }
        }
    }
}

/**
 * Split hotkey bar: feature-specific [contextual] hints on the left, persistent [global]
 * hints on the right, separated by a `│`.  Both sides are word-wrapped if content overflows.
 *
 * When a DAG is loaded, the preferred layout is:
 * ```
 * DAG : [M] Metrics [C] Config [T] Trickle | Arena : [A] Arena [G] Generate Judges | [B] Benchmark [Tab] Switch Panels [?] Help [X] Load DAG [Ctrl-C] Quit
 * ```
 * If the terminal is narrower than the full line the bar wraps gracefully.
 */
@Composable
fun HotkeyBar(
    width: Int,
    contextual: List<HotkeyAction>,
    global: List<HotkeyAction>,
) {
    val rowWidth = (width - 2).coerceAtLeast(1)

    // Merge contextual + separator + global into one token stream so word-wrap can break
    // anywhere — including between contextual and global sections.
    val tokens: List<Token> = buildList {
        addAll(tokenize(contextual))
        if (contextual.isNotEmpty() && global.isNotEmpty()) add(Token.Separator)
        addAll(tokenize(global))
    }
    val rows = wrapTokens(tokens, rowWidth)

    Column(modifier = Modifier.width(width).padding(left = 1)) {
        if (rows.isEmpty()) {
            Row(modifier = Modifier.width(rowWidth)) { Spacer() }
        } else {
            rows.forEach { rowTokens ->
                val line = renderRow(rowTokens)
                Row(modifier = Modifier.width(rowWidth)) {
                    Text(line.safeClip(rowWidth))
                    Spacer()
                }
            }
        }
    }
}

/**
 * Grouped hotkey bar.  [groups] are rendered with bold section labels separated by `|` pipes.
 * Wraps onto additional rows when [width] is insufficient.
 *
 * Example:
 * ```kotlin
 * HotkeyBar(
 *     width = terminalWidth,
 *     groups = listOf(
 *         HotkeyGroup("DAG",   listOf(HotkeyAction("M", "Metrics"), HotkeyAction("C", "Config"))),
 *         HotkeyGroup("Arena", listOf(HotkeyAction("A", "Arena"))),
 *         HotkeyGroup("",      GlobalHotkeys.forState(state)),  // no label for global section
 *     )
 * )
 * ```
 */
@Composable
fun HotkeyBar(
    width: Int,
    groups: List<HotkeyGroup>,
) {
    val rowWidth = (width - 2).coerceAtLeast(1)
    val tokens   = tokenize(groups)
    val rows     = wrapTokens(tokens, rowWidth)

    Column(modifier = Modifier.width(width).padding(left = 1)) {
        if (rows.isEmpty()) {
            Row(modifier = Modifier.width(rowWidth)) { Spacer() }
        } else {
            rows.forEach { rowTokens ->
                val line = renderRow(rowTokens)
                Row(modifier = Modifier.width(rowWidth)) {
                    Text(line.safeClip(rowWidth))
                    Spacer()
                }
            }
        }
    }
}

// ──────────────────────────────────────────────────────────────────────────────
//  Private utility
// ──────────────────────────────────────────────────────────────────────────────

/**
 * Safely clips an [AnnotatedString] to [n] characters without crashing when n ≥ length.
 * Unlike the extension in TuiTheme (which operates on code units and is alias for this),
 * this is scoped privately here so the bar is self-contained.
 */
private fun AnnotatedString.safeClip(n: Int): AnnotatedString =
    if (this.length <= n) this else this.subSequence(0, n)
