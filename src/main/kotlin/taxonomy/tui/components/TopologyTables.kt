package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.layout.padding
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
    val visible = (pHeight - 1).coerceAtLeast(1)
    val start = offset.coerceIn(0, maxOf(0, domains.size - visible))
    val end = (start + visible).coerceAtMost(domains.size)
    val allSelected = selectedDomains.isEmpty()

    Column {
        if (domains.isEmpty()) {
            Text("No domains available. Download the dataset first.", color = White)
            return@Column
        }
        for (i in start until end) {
            val (name, count) = domains[i]
            val checked = allSelected || selectedDomains.contains(name)
            val selected = i == selectedIdx
            val mark = if (checked) "\u2611" else "\u2610" // ☑ / ☐
            val caret = if (selected) "\u276f " else "  "      // ❯
            Text(
                value = (caret + "$mark $name ($count)").take((pWidth - 1).coerceAtLeast(1)),
                color = if (selected) Cyan else if (checked) Green else White,
                textStyle = if (selected) Bold else Unspecified
            )
        }
    }
}

/**
 * Renders the DAG hierarchy: tree on the left (box-drawing connectors, depth colours,
 * fold markers, judge ★, poly ⇄) plus a right-aligned recursive query-count column and
 * a per-node judge column (✔ judged / ○ not). Mirrors the original dashboard table.
 */
@Composable
fun AsciiTreeTable(
    pWidth: Int,
    pHeight: Int,
    lines: List<TreeLine>,
    offset: Int,
    selectedIdx: Int,
) {
    if (lines.isEmpty()) {
        Column {
            Text("\u25cc Awaiting taxonomy construction\u2026".take(pWidth - 1), color = Yellow)
            Text("Generate a DAG (R) or load a snapshot (X).".take(pWidth - 1), color = White)
        }
        return
    }

    // Layout: [caret 2][tree TREE_W][space][queries 6][space][judge 1]
    val QCOL = 6
    val treeW = (pWidth - 2 - 1 - QCOL - 1 - 1 - 1).coerceAtLeast(10)
    val visible = (pHeight - 2).coerceAtLeast(1)
    val start = offset.coerceIn(0, maxOf(0, lines.size - visible))
    val end = (start + visible).coerceAtMost(lines.size)

    Column {
        // Column header.
        Text(
            buildAnnotatedString {
                withStyle(SpanStyle(color = White, textStyle = Bold)) {
                    append("  ")
                    append("Taxonomy DAG Hierarchy".take(treeW).padEnd(treeW))
                    append(" ")
                    append("Queries".padStart(QCOL))
                    append(" \u2714")
                }
            }.take(pWidth - 1)
        )

        for (i in start until end) {
            val line = lines[i]
            val node = line.node
            val selected = i == selectedIdx
            val totalQ = node.getRecursiveQueryCount()
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
            Text(
                row.take(pWidth - 1),
                modifier = Modifier.height(1),
                textStyle = if (selected) Bold else Unspecified
            )
        }
    }
}

/** Renders the flat node list (sorted by query volume) for the DAG topology. */
@Composable
fun DagTable(
    pWidth: Int,
    pHeight: Int,
    nodes: List<GraphNode>,
    offset: Int,
    selectedIdx: Int,
) {
    val visible = (pHeight - 1).coerceAtLeast(1)
    val start = offset.coerceIn(0, maxOf(0, nodes.size - visible))
    val end = (start + visible).coerceAtMost(nodes.size)

    Column {
        if (nodes.isEmpty()) {
            Text("No taxonomy graph loaded.", color = White)
            return@Column
        }
        for (i in start until end) {
            val node = nodes[i]
            val selected = i == selectedIdx
            val label = node.label ?: node.id
            Text(
                value = (if (selected) "> " else "  ") + "$label  (q:${node.queries.size}, d:${node.depth})",
                color = if (selected) Cyan else White,
                textStyle = if (selected) Bold else Unspecified
            )
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
                        if (ancestorHasMore[j]) "\u251c\u2500\u2500 " else "\u2514\u2500\u2500 " // ├── / └──
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
        val fold = when {
            !hasChildren -> "  "
            isExpanded -> "\u25be " // ▾
            else -> "\u25b8 "        // ▸
        }
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

        out += TreeLine(node = node, text = text, isPoly = isPoly)

        if (alreadyVisited || !isExpanded) return
        val sorted = node.children.sortedByDescending { it.getRecursiveQueryCount() }
        sorted.forEachIndexed { index, child ->
            walk(child, depth + 1, ancestorHasMore + (index < sorted.size - 1))
        }
    }

    walk(root, 0, emptyList())
    return out
}
