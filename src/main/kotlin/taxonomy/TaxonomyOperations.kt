package org.eclipse.lmos.arc.app.taxonomy

import kotlinx.coroutines.*
import org.eclipse.lmos.arc.app.taxonomy.operations.*
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.StatisticsUtils

/**
 * Orchestrator for DAG operations, delegating to specialized components.
 */
@Service
class TaxonomyOperations(
    private val fitter: TaxonomyFitter,
    private val trickler: TaxonomyTrickler,
    private val splitter: TaxonomySplitter,
    private val merger: TaxonomyMerger,
    private val config: TaxonomyConfig
) {
    private val log = LoggerFactory.getLogger(TaxonomyOperations::class.java)

    fun trickleQuery(query: Embedding, currentNode: GraphNode, results: MutableMap<GraphNode, Double>, previousAssignments: Set<String> = emptySet()) =
        trickler.trickleQuery(query, currentNode, results, mutableSetOf(), previousAssignments)

    suspend fun fitNodeRecursive(node: GraphNode) = fitter.fitNodeRecursive(node)

    suspend fun splitNodesRecursive(node: GraphNode) = splitter.splitNodesRecursive(node)

    suspend fun optimizeHierarchy(root: GraphNode) = merger.optimizeHierarchy(root)

    suspend fun reassignQueries(
        root: GraphNode, 
        embeddings: List<Embedding>,
        groundTruthMap: Map<String, Set<String>> = emptyMap() // NEW: Multi-domain support
    ) = coroutineScope {
        // Build a lookup map for previous assignments (Persistence Bias)
        val prevMap = mutableMapOf<String, MutableSet<String>>()
        fun buildMap(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
            if (visited.contains(node.id)) return
            visited.add(node.id)
            node.queries.forEach { emb ->
                prevMap.getOrPut(emb.rawText) { mutableSetOf() }.add(node.id)
            }
            node.children.forEach { buildMap(it, visited) }
        }
        buildMap(root)

        // Process queries in parallel chunks
        embeddings.chunked(100).map { chunk ->
            async(Dispatchers.Default) {
                chunk.map { emb ->
                    val matches = mutableMapOf<GraphNode, Double>()
                    val previousIds = prevMap[emb.rawText] ?: emptySet()
                    val originals = groundTruthMap[emb.rawText]
                    
                    trickler.trickleQuery(emb, root, matches, previousIds.toMutableSet(), originalCategories = originals)
                    
                    // STABILITY & GROUND TRUTH BIAS
                    val biasedMatches = matches.mapValues { (node, distance) ->
                        var score = distance
                        // Persistence Bias: 20% advantage to current home
                        if (previousIds.contains(node.id)) score *= 0.8 
                        // Ground Truth Anchor: 30% advantage to original domains
                        val isOriginal = originals?.any { it.equals(node.label, ignoreCase = true) } ?: false
                        if (isOriginal) score *= 0.7
                        score
                    }
                    
                    emb to biasedMatches
                }
            }
        }.awaitAll().flatten().forEach { (emb, biasedMatches) ->

            // COMPETITIVE ASSIGNMENT
            val sortedMatches = biasedMatches.entries
                .filter { it.key.depth > 0 }
                .sortedBy { it.value }
                .take(config.formalism.maxAssignmentsPerQuery)
                .map { it.key }
                .ifEmpty { listOf(root) }

            // Assign to the best mathematically viable destinations
            sortedMatches.forEach { node ->
                synchronized(node.queries) {
                    node.queries.add(emb)
                }
            }
        }
    }

    fun clearGraphQueries(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
        if (visited.contains(node.id)) return
        visited.add(node.id)
        node.queries.clear()
        node.children.forEach { clearGraphQueries(it, visited) }
    }

    fun countNodes(root: GraphNode): Int {
        val visited = mutableSetOf<String>()
        fun walk(node: GraphNode) {
            if (visited.contains(node.id)) return
            visited.add(node.id)
            node.children.forEach { walk(it) }
        }
        walk(root)
        return visited.size
    }

    fun exportToDot(root: GraphNode): String {
        val sb = StringBuilder()
        sb.append("digraph Taxonomy {\n")
        sb.append("  rankdir=LR;\n")
        sb.append("  node [shape=box, style=filled, fillcolor=white];\n")

        val visitedNodes = mutableSetOf<String>()
        val edges = mutableSetOf<String>()

        fun walk(node: GraphNode) {
            if (visitedNodes.contains(node.id)) return
            visitedNodes.add(node.id)

            val color = if (node.isLeaf) "lightblue" else "lightgrey"
            sb.append("  \"${node.id}\" [label=\"${node.label}\\n(${node.queries.size} q)\", fillcolor=$color];\n")

            node.children.forEach { child ->
                val edge = "\"${node.id}\" -> \"${child.id}\""
                if (!edges.contains(edge)) {
                    edges.add(edge)
                    sb.append("  $edge;\n")
                }
                walk(child)
            }
        }

        walk(root)
        sb.append("}\n")
        return sb.toString()
    }

    fun printHierarchy(node: GraphNode, indent: String = "", visited: MutableSet<String> = mutableSetOf()) {
        val cross = if (visited.contains(node.id)) " [CROSS-LINK]" else ""
        val type = if (node.isLeaf) "Leaf" else "Parent/Residual"

        val gmmStats = node.distribution?.let { gmm ->
            val avgVar = gmm.components.flatMap { it.diagonalCovariance!!.toList() }.average()
            " (GMM ${gmm.components.size} centroids, σ² avg: ${"%.6f".format(avgVar)})"
        } ?: ""

        log.info("$indent- ${node.label} [${node.queries.size} q - $type]$gmmStats$cross")

        if (visited.contains(node.id)) return
        visited.add(node.id)
        node.children.forEach { printHierarchy(it, "$indent  ", visited) }
    }
}