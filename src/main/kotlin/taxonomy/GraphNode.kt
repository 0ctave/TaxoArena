package org.eclipse.lmos.arc.app.taxonomy

import java.util.UUID

/**
 * The core topological unit: Directed Acyclic Graph (DAG) Node.
 * Updated to use a unified query list for both Leaf Data and Parent Residuals.
 */
data class GraphNode(
    val id: String = UUID.randomUUID().toString(),
    var label: String,
    val depth: Int,

    // Topology (DAG)
    val children: MutableSet<GraphNode> = java.util.concurrent.ConcurrentHashMap.newKeySet(),
    val parents: MutableSet<GraphNode> = java.util.concurrent.ConcurrentHashMap.newKeySet(),

    // Unified Data Space:
    // If isLeaf == true: Holds the explicit data for this domain.
    // If isLeaf == false: Holds the residual "unmapped/outlier" queries that failed to trickle to children.
    val queries: MutableList<Embedding> = java.util.concurrent.CopyOnWriteArrayList(),

    // Statistical Modeling - Hierarchical Mixture Model (HMM)
    var distribution: GmmParams? = null,
    var previousDistribution: GmmParams? = null,

    // Agent Judge Profiles
    var judgePrompt: String? = null,
    var judgeRubric: String? = null
) {
    val isLeaf: Boolean get() = children.isEmpty()

    // Proportional weight of this node as a component in its parent's GMM
    var proportionalWeight: Double = 1.0

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is GraphNode) return false
        return id == other.id
    }

    override fun hashCode(): Int = id.hashCode()

    /**
     * Aggregates all queries in the branch (this node + all descendants).
     * Handles DAG polyhierarchy by ensuring each node is visited only once.
     */
    fun getAllQueriesInBranch(): List<Embedding> {
        val allQueries = mutableListOf<Embedding>()
        val visited = mutableSetOf<String>()
        
        fun walk(node: GraphNode) {
            if (!visited.add(node.id)) return
            allQueries.addAll(node.queries)
            node.children.forEach { walk(it) }
        }
        
        walk(this)
        return allQueries
    }

    /**
     * Fast count of all unique queries in the branch.
     * Uses a bit register (java.util.BitSet) via attributed query IDs for efficient binary deduplication.
     */
    fun getRecursiveQueryCount(): Int {
        val visited = mutableSetOf<String>()
        val bitSet = java.util.BitSet()
        val fallbackSet = mutableSetOf<String>()
        
        fun walk(node: GraphNode) {
            if (!visited.add(node.id)) return
            node.queries.forEach { q ->
                if (q.queryId >= 0) {
                    bitSet.set(q.queryId)
                } else {
                    fallbackSet.add(q.rawText)
                }
            }
            node.children.forEach { walk(it) }
        }
        
        walk(this)
        return bitSet.cardinality() + fallbackSet.size
    }
}

/**
 * Traverses the entire DAG, collects all unique queries, attributes sequential integer IDs to them,
 * and ensures all occurrences of identical queries share the same ID.
 */
fun assignQueryIds(root: GraphNode) {
    val visited = mutableSetOf<String>()
    val uniqueQueries = mutableListOf<Embedding>()
    val seenTexts = mutableSetOf<String>()
    
    fun walk(node: GraphNode) {
        if (!visited.add(node.id)) return
        node.queries.forEach { q ->
            if (seenTexts.add(q.rawText)) {
                uniqueQueries.add(q)
            }
        }
        node.children.forEach { walk(it) }
    }
    walk(root)
    
    uniqueQueries.forEachIndexed { index, emb ->
        emb.queryId = index
    }
    
    val textToId = uniqueQueries.associate { it.rawText to it.queryId }
    
    val visitedAssign = mutableSetOf<String>()
    fun walkAssign(node: GraphNode) {
        if (!visitedAssign.add(node.id)) return
        node.queries.forEach { q ->
            q.queryId = textToId[q.rawText] ?: -1
        }
        node.children.forEach { walkAssign(it) }
    }
    walkAssign(root)
}