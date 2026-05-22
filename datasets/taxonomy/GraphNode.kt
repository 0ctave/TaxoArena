package org.eclipse.lmos.arc.app.taxonomy

import kotlinx.serialization.Serializable
import kotlinx.serialization.Transient
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import java.util.Collections

@Serializable
class GraphNode(
    var label: String,
    var description: String = ""
) {
    val id: String = UUID.randomUUID().toString()

    // --- Graph Topology (Thread-Safe) ---
    @Transient val parents: MutableSet<GraphNode> = Collections.newSetFromMap(ConcurrentHashMap())
    @Transient val children: MutableSet<GraphNode> = Collections.newSetFromMap(ConcurrentHashMap())

    // --- Empirical State ---
    // The actual subset of Q_univ resting in this domain
    @Transient val queries: MutableSet<String> = Collections.newSetFromMap(ConcurrentHashMap())

    // --- Statistical Geometry ---
    @Transient var centroid: FloatArray? = null    // μ_D
    @Transient var variance: FloatArray? = null    // σ²_D

    // --- Concurrency Markers ---
    @Transient @Volatile var isMerged: Boolean = false
    @Transient @Volatile var observationCount: Int = 0 // Required for Welford's O(1) Updates

    fun addChild(node: GraphNode) {
        children.add(node)
        node.parents.add(this)
    }

    fun removeChild(node: GraphNode) {
        children.remove(node)
        node.parents.remove(this)
    }

    val depth: Int
        get() {
            if (parents.isEmpty()) return 0
            val visited = mutableSetOf<String>()
            var currentLevel = setOf(this)
            var d = 0
            while (currentLevel.isNotEmpty() && !currentLevel.any { it.parents.isEmpty() }) {
                currentLevel = currentLevel.flatMap { it.parents }.filter { visited.add(it.id) }.toSet()
                d++
            }
            return d
        }

    fun getAllNodes(): Set<GraphNode> {
        val visited = Collections.newSetFromMap(ConcurrentHashMap<GraphNode, Boolean>())
        fun traverse(n: GraphNode) {
            if (visited.add(n)) n.children.forEach { traverse(it) }
        }
        traverse(this)
        return visited
    }

    override fun equals(other: Any?): Boolean = (other as? GraphNode)?.id == this.id
    override fun hashCode(): Int = id.hashCode()
}