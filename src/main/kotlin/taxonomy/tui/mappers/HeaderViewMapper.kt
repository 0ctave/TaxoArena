package taxonomy.tui.mappers

import taxonomy.model.GraphNode
import java.time.LocalTime
import java.time.format.DateTimeFormatter

/**
 * Clean data model for the top banner.
 */
data class HeaderViewModel(
    val time: String,
    val totalNodes: Int,
    val activeDatasetName: String,
    val activeSnapshotName: String?
)

object HeaderViewMapper {
    private val timeFormatter = DateTimeFormatter.ofPattern("HH:mm:ss")

    fun map(
        rootNode: GraphNode?,
        datasetName: String,
        activeSnapshotName: String?
    ): HeaderViewModel {
        return HeaderViewModel(
            time = LocalTime.now().format(timeFormatter),
            totalNodes = countNodes(rootNode),
            activeDatasetName = datasetName,
            activeSnapshotName = activeSnapshotName
        )
    }

    private fun countNodes(root: GraphNode?): Int {
        if (root == null) return 0
        val visited = mutableSetOf<String>()
        fun walk(node: GraphNode) {
            if (!visited.add(node.id)) return
            node.children.forEach { walk(it) }
        }
        walk(root)
        return visited.size
    }
}