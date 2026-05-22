package org.eclipse.lmos.arc.app.domain

import kotlinx.serialization.Serializable
import kotlinx.serialization.Transient
import java.util.Collections
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

/**
 * A general-purpose directed graph node representing a Domain/Capability.
 */
@Serializable
class GraphNode(
    val id: String = UUID.randomUUID().toString(),
    var label: String, // Label or description (e.g., "Programming")
    val children: MutableSet<GraphNode> = Collections.newSetFromMap(ConcurrentHashMap())
) {
    // FIX: Using a Concurrent Set mathematically prevents DAG path duplication!
    @Transient val queries: MutableSet<String> = Collections.newSetFromMap(ConcurrentHashMap())

    // Directed Acyclic Graph (DAG) topology
    @Transient val parents: MutableSet<GraphNode> = Collections.newSetFromMap(ConcurrentHashMap())

    // Tombstone markers for parallel processing (don't save to JSON)
    @Transient @Volatile var isMerged: Boolean = false
    @Transient @Volatile var mergedInto: GraphNode? = null

    // Cycle-safe iterative BFS to find the shortest path to a root node
    val depth: Int
        get() {
            if (parents.isEmpty()) return 0

            var currentDepth = 0
            var currentLevel = setOf(this)
            val visited = mutableSetOf<String>()

            while (currentLevel.isNotEmpty()) {
                if (currentLevel.any { it.parents.isEmpty() }) {
                    return currentDepth
                }

                val nextLevel = mutableSetOf<GraphNode>()
                for (node in currentLevel) {
                    if (visited.add(node.id)) {
                        nextLevel.addAll(node.parents)
                    }
                }
                currentLevel = nextLevel
                currentDepth++
            }
            return currentDepth
        }

    fun addChild(node: GraphNode) {
        children.add(node)
        node.parents.add(this)
    }

    fun removeChild(node: GraphNode) {
        children.remove(node)
        node.parents.remove(this)
    }

    fun getAllNodes(): Set<GraphNode> {
        val visited = mutableSetOf<GraphNode>()
        fun traverse(node: GraphNode) {
            if (visited.add(node)) {
                node.children.forEach { traverse(it) }
            }
        }
        traverse(this)
        return visited
    }

    override fun equals(other: Any?): Boolean = (other as? GraphNode)?.id == this.id
    override fun hashCode(): Int = id.hashCode()
}