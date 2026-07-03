package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import com.jakewharton.mosaic.ui.TextStyle.Companion.Unspecified
import taxonomy.model.GraphNode

/**
 * Renders the dataset domain picker. An empty [selectedDomains] is treated as
 * "all domains selected" to mirror the config facade convention.
 */
@Composable
fun DomainSelectorTable(
    pWidth: Int,
    pHeight: Int,
    domains: List<Pair<String, Int>>,
    offset: Int,
    selectedIdx: Int,
    selectedDomains: List<String>,
) {
    if (domains.isEmpty()) {
        Column {
            Text("No domains available. Download the dataset first.", color = White)
        }
        return
    }
    val allSelected = selectedDomains.isEmpty()

    ScrollablePanelContent(
        pWidth = pWidth,
        pHeight = pHeight,
        itemCount = domains.size,
        scrollOffset = offset,
        hasPadding = false,
    ) { visibleHeight, startIdx, contentWidth ->
        val end = (startIdx + visibleHeight).coerceAtMost(domains.size)
        for (i in startIdx until end) {
            val (name, count) = domains[i]
            val checked = allSelected || selectedDomains.contains(name)
            val selected = i == selectedIdx
            val mark = checkboxMark(checked)
            val caret = if (selected) "\u276f " else "  "      // ❯
            Text(
                value = (caret + "$mark $name ($count)").take((contentWidth).coerceAtLeast(1)),
                color = if (selected) Cyan else if (checked) Green else White,
                textStyle = if (selected) Bold else Unspecified,
                modifier = Modifier.height(1)
            )
        }
        val emptyRows = visibleHeight - (end - startIdx)
        repeat(emptyRows.coerceAtLeast(0)) {
            Text(" ".repeat(contentWidth), modifier = Modifier.height(1))
        }
    }
}

/**
 * Renders the DAG hierarchy: tree on the left (box-drawing connectors, depth colours,
 * fold markers, judge ★, poly ⇄) plus a right-aligned recursive query-count column and
 * a per-node judge column (✔ judged / ○ not). Mirrors the original dashboard table.
 *
 * ### TextSurface bounds contract
 * Mosaic allocates a `TextSurface` whose width equals the `Modifier.width()` set on a
 * `Text` composable (or the string's natural width when no width modifier is set).
 * `TextSurface.get()` throws `IllegalStateException` ("Check failed") when `drawText`
 * tries to write a glyph at a column index ≥ the surface width. This means every `Text`
 * that lives inside a fixed-width container **must** carry a matching `Modifier.width()`
 * so Mosaic never measures a wider natural size than the surface it draws into.
 *
 * All `Text` calls in this function therefore set `Modifier.width(contentWidth)` (passed
 * in by `ScrollablePanelContent`'s lambda) so the surface is always exactly as wide as
 * the column budget, regardless of the Unicode glyph stream produced by the row builder.
 */
@Composable
fun AsciiTreeTable(
    pWidth: Int,
    pHeight: Int,
    lines: List<TreeLine>,
    offset: Int,
    selectedIdx: Int,
    queryCounts: Map<String, Int> = emptyMap(),
) {
    if (lines.isEmpty()) {
        Column {
            Text("\u25cc Awaiting taxonomy construction\u2026".take(pWidth - 1), color = Yellow)
            Text("Generate a DAG (R) or load a snapshot (X).".take(pWidth - 1), color = White)
        }
        return
    }

    // Layout: [caret 2][tree TREE_W][space][queries 6][space][judge 1] (see TreeTableLayout).
    val QCOL = TreeTableLayout.QUERY_COL
    val treeW = TreeTableLayout.treeWidth(pWidth)
    val visible = TreeTableLayout.visibleRows(pHeight)

    Column {
        // Column header — width-constrained so the header Text surface never overflows.
        val headerStr = buildAnnotatedString {
            withStyle(SpanStyle(color = White, textStyle = Bold)) {
                append("  ")
                append("Taxonomy DAG Hierarchy".take(treeW).padEnd(treeW))
                append(" ")
                append("Queries".padStart(QCOL))
                append(" \u2714")
            }
        }
        Text(
            headerStr.take(pWidth - 1),
            modifier = Modifier.height(1).width((pWidth - 1).coerceAtLeast(1))
        )

        ScrollablePanelContent(
            pWidth = pWidth,
            pHeight = visible,
            itemCount = lines.size,
            scrollOffset = offset,
            hasPadding = false,
        ) { visibleHeight, startIdx, contentWidth ->
            val end = (startIdx + visibleHeight).coerceAtMost(lines.size)
            for (i in startIdx until end) {
                val line = lines[i]
                val node = line.node
                val selected = i == selectedIdx
                // Use the memoized count (per graphVersion) to avoid an O(subtree) walk per row.
                val totalQ = queryCounts[node.id] ?: node.getRecursiveQueryCount()
                val hasJudge = node.judgePrompt != null
                val qStr = totalQ.toString().padStart(QCOL)
                val judgeGlyph = if (hasJudge) "\u2714" else "\u25cb" // ✔ / ○

                // The tree text is a colour-annotated string; pad/truncate to a fixed column.
                val treeText = line.text.take(treeW)
                val padCount = (treeW - treeText.length).coerceAtLeast(0)

                val row = buildAnnotatedString {
                    if (selected) {
                        withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append("\u276f ") } // ❯
                    } else {
                        append("  ")
                    }
                    append(treeText)
                    append(" ".repeat(padCount))
                    append(" ")
                    withStyle(SpanStyle(color = Cyan)) { append(qStr) }
                    append(" ")
                    withStyle(
                        SpanStyle(color = if (hasJudge) Green else White, textStyle = Bold)
                    ) { append(judgeGlyph) }
                }
                // Modifier.width(contentWidth) is REQUIRED: it tells Mosaic to allocate a
                // TextSurface of exactly contentWidth columns. Without it, Mosaic measures
                // the AnnotatedString's natural width (which includes styled spans whose
                // character count does not equal their terminal column count for multi-byte
                // Unicode glyphs) and may allocate a surface narrower than what drawText
                // expects, triggering the TextSurface.get() IllegalStateException crash.
                Text(
                    row.take(contentWidth),
                    modifier = Modifier.height(1).width(contentWidth),
                    textStyle = if (selected) Bold else Unspecified
                )
            }
        }
    }
}

/**
 * Flatten a DAG into rendered tree lines via DFS over [GraphNode.children],
 * honouring per-node expand/collapse state in [expandedNodes].
 *
 * Each line carries box-drawing connectors (├──, └──, │), a depth-tinted label,
 * a fold marker (▸ collapsed / ▾ expanded) for nodes with children, a judge star
 * (★), and a poly marker (⇄) for nodes reachable through more than one parent.
 * Children are ordered by descending query volume so the heaviest branches sit on top.
 */
fun buildTreeLines(
    root: GraphNode?,
    expandedNodes: Map<String, Boolean> = emptyMap(),
    leafRanks: Map<String, Pair<String, String>> = emptyMap(),
): List<TreeLine> {
    if (root == null) return emptyList()
    val out = mutableListOf<TreeLine>()
    val visited = mutableSetOf<String>()

    fun walk(node: GraphNode, depth: Int, ancestorHasMore: List<Boolean>) {
        val alreadyVisited = !visited.add(node.id)
        val isPoly = node.parents.size > 1

        // Box-drawing connector prefix for the current depth.
        val prefix = buildString {
            for (j in 0 until depth) {
                append(
                    if (j == depth - 1) {
                        if (ancestorHasMore[j]) "\u251c\u2500\u2500" else "\u2514\u2500\u2500" // ├── / └──
                    } else {
                        if (ancestorHasMore[j]) "\u2502   " else "    " // │
                    }
                )
            }
        }

        val hasChildren = node.children.isNotEmpty() && !alreadyVisited
        // Default view (no explicit expand state yet): auto-expand the root and the first
        // level so the domains are visible immediately; deeper levels stay collapsed.
        val isExpanded = expandedNodes[node.id] ?: (depth < 1)
        val fold = " "
        val nodeCol = depthColor(node.depth)
        val label = node.label ?: node.id

        val text = buildAnnotatedString {
            withStyle(SpanStyle(color = White)) { append(prefix) }
            withStyle(SpanStyle(color = nodeCol)) { append(fold) }
            if (node.judgePrompt != null) {
                withStyle(SpanStyle(color = Green, textStyle = Bold)) { append("\u2605 ") } // ★
            }
            if (alreadyVisited) {
                withStyle(SpanStyle(color = nodeCol, textStyle = Bold)) { append(label) }
                withStyle(SpanStyle(color = Yellow, textStyle = Bold)) { append(" \u21c4") } // ⇄
            } else {
                withStyle(SpanStyle(color = nodeCol)) { append(label) }
            }
        }

        out += TreeLine(node = node, text = text, isPoly = isPoly, topTwoRanks = leafRanks[node.id])

        if (alreadyVisited || !isExpanded) return
        val sorted = node.children.sortedByDescending { it.getRecursiveQueryCount() }
        sorted.forEachIndexed { index, child ->
            walk(child, depth + 1, ancestorHasMore + (index < sorted.size - 1))
        }
    }

    walk(root, 0, emptyList())
    return out
}

fun shortModelName(name: String): String {
    val clean = name.lowercase()
    return when {
        clean.contains("claude") -> "claude"
        clean.contains("70b") -> "70B"
        clean.contains("8b") -> "8B"
        clean.contains("13b") -> "13B"
        clean.contains("7b") -> "7B"
        clean.contains("gpt-4") -> "gpt4"
        else -> name.take(8)
    }
}
