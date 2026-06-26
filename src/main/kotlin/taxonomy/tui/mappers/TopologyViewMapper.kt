package taxonomy.tui.mappers

import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.withStyle
import taxonomy.model.GraphNode
import taxonomy.tui.components.TreeLine
import taxonomy.tui.components.TuiTheme
import taxonomy.tui.components.TuiTheme.depthColor
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold

object TopologyViewMapper {

    /** Flatten DAG into a list sorted by query volume. */
    fun collectAllNodes(rootNode: GraphNode?): List<GraphNode> {
        if (rootNode == null) return emptyList()

        val nodes = mutableListOf<GraphNode>()
        fun walk(node: GraphNode, visited: MutableSet<String>) {
            if (!visited.add(node.id)) return
            nodes += node
            node.children.forEach { child -> walk(child, visited) }
        }

        walk(rootNode, mutableSetOf())
        return nodes.sortedByDescending { it.queries.size }
    }

    /** Recursively build formatted TreeLines for the ASCII DAG View. */
    fun buildTreeLines(
        rootNode: GraphNode?,
        expandedNodes: Map<String, Boolean>
    ): List<TreeLine> {
        if (rootNode == null) return emptyList()

        val lines = mutableListOf<TreeLine>()
        val globallyVisited = mutableSetOf<String>()

        fun walk(
            node: GraphNode,
            prefix: String,
            isLast: Boolean,
            isPoly: Boolean
        ) {
            val hasChildren = node.children.isNotEmpty()
            val isExpanded = expandedNodes[node.id] == true

            val branch = if (prefix.isEmpty()) "" else if (isLast) "└─" else "├─"
            val marker = when {
                isPoly -> "◆"
                !hasChildren -> "•"
                isExpanded -> "▼"
                else -> "▶"
            }

            val formattedLine = buildAnnotatedString {
                append(prefix + branch)
                withStyle(SpanStyle(color = depthColor(node.depth), textStyle = Bold)) {
                    append("$marker ")
                    append(node.label ?: node.id)
                }
                append(" ")
                withStyle(SpanStyle(color = Cyan)) {
                    append("[${node.queries.size}]")
                }
                if (node.judge != null) {
                    withStyle(SpanStyle(color = Green)) { append(" ✔") }
                }
            }

            lines += TreeLine(
                node = node,
                text = formattedLine,
                isPoly = isPoly
            )

            if (!globallyVisited.add(node.id)) return
            if (!hasChildren || !isExpanded) return

            val sortedChildren = node.children.sortedWith(
                compareByDescending<GraphNode> { it.queries.size }
                    .thenBy { it.label ?: it.id }
            )

            sortedChildren.forEachIndexed { index, child ->
                val childIsLast = index == sortedChildren.lastIndex
                val nextPrefix = prefix + if (prefix.isEmpty()) "" else if (isLast) "   " else "│  "
                val poly = child.parents.size > 1

                walk(
                    node = child,
                    prefix = nextPrefix,
                    isLast = childIsLast,
                    isPoly = poly
                )
            }
        }

        walk(rootNode, "", isLast = true, isPoly = false)
        return lines
    }
}