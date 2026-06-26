package taxonomy.tui.components

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.buildAnnotatedString
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

    Column(modifier = Modifier.padding(left = 1)) {
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

/** Renders the pre-built ASCII tree lines for the DAG topology. */
@Composable
fun AsciiTreeTable(
    pWidth: Int,
    pHeight: Int,
    lines: List<TreeLine>,
    offset: Int,
    selectedIdx: Int,
) {
    val visible = (pHeight - 1).coerceAtLeast(1)
    val start = offset.coerceIn(0, maxOf(0, lines.size - visible))
    val end = (start + visible).coerceAtMost(lines.size)

    Column(modifier = Modifier.padding(left = 1)) {
        if (lines.isEmpty()) {
            Text("No taxonomy graph loaded.", color = White)
            return@Column
        }
        for (i in start until end) {
            val line = lines[i]
            val selected = i == selectedIdx
            Text(
                buildAnnotatedString {
                    append(if (selected) "\u276f " else "  ") // ❯
                    append(line.text)
                }.take((pWidth - 1).coerceAtLeast(1)),
                color = when {
                    selected -> Cyan
                    line.isPoly -> Yellow
                    else -> White
                },
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

    Column(modifier = Modifier.padding(left = 1)) {
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
 * guarding against cycles. A node reachable through more than one parent is
 * flagged [TreeLine.isPoly].
 */
fun buildTreeLines(root: GraphNode?): List<TreeLine> {
    if (root == null) return emptyList()
    val out = mutableListOf<TreeLine>()
    val visited = linkedSetOf<String>()

    fun walk(node: GraphNode, depth: Int) {
        val isPoly = node.parents.size > 1
        val indent = "  ".repeat(depth)
        val label = node.label ?: node.id
        val text = buildAnnotatedString {
            append("$indent$label")
            if (node.queries.isNotEmpty()) append(" (${node.queries.size})")
        }
        out += TreeLine(node = node, text = text, isPoly = isPoly)
        if (!visited.add(node.id)) return
        node.children.sortedByDescending { it.queries.size }.forEach { walk(it, depth + 1) }
    }

    walk(root, 0)
    return out
}
