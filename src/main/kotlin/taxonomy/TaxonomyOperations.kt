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

    suspend fun generateLabelsPostPass(root: GraphNode) = splitter.generateLabelsPostPass(root)

    fun resetConceptCounter() = splitter.resetConceptCounter()

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
        val numCores = Runtime.getRuntime().availableProcessors()
        val chunkSize = maxOf(5, (embeddings.size + (numCores * 4) - 1) / (numCores * 4)).coerceAtMost(25)

        embeddings.chunked(chunkSize).map { chunk ->
            async(Dispatchers.Default) {
                chunk.map { emb ->
                    val matches = mutableMapOf<GraphNode, Double>()
                    val previousIds = prevMap[emb.rawText] ?: emptySet()
                    val originals = groundTruthMap[emb.rawText]
                    
                    trickler.trickleQuery(
                        query = emb,
                        currentNode = root,
                        results = matches,
                        visited = mutableSetOf(),
                        previousAssignments = previousIds,
                        originalCategories = originals
                    )
                    
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
            val candidateEntries = biasedMatches.entries.filter { it.key.depth > 0 }
            val originals = groundTruthMap[emb.rawText]
            
            val originalMatches = candidateEntries.filter { entry ->
                originals?.any { it.equals(entry.key.label, ignoreCase = true) } ?: false
            }.sortedBy { it.value }
            
            val otherMatches = candidateEntries.filter { entry ->
                !(originals?.any { it.equals(entry.key.label, ignoreCase = true) } ?: false)
            }.sortedBy { it.value }
            
            val maxAllowed = config.formalism.maxAssignmentsPerQuery
            val selectedNodes = mutableListOf<GraphNode>()
            
            // First, take matching original ground-truth nodes
            selectedNodes.addAll(originalMatches.take(maxAllowed).map { it.key })
            
            // Fill remaining slots with other matches
            if (selectedNodes.size < maxAllowed) {
                val remainingCount = maxAllowed - selectedNodes.size
                selectedNodes.addAll(otherMatches.take(remainingCount).map { it.key })
            }
            
            val sortedMatches = selectedNodes.ifEmpty { listOf(root) }

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

    fun printHierarchy(root: GraphNode) {
        val sb = java.lang.StringBuilder()
        sb.append("\n+----------------------------------------------------------\n")
        sb.append("|              TAXONOMY DAG HIERARCHY\n")
        sb.append("+----------------------------------------------------------\n")
        buildTreeString(root, "| ", true, sb, mutableSetOf())
        sb.append("+----------------------------------------------------------")
        log.info(sb.toString())
    }

    private fun buildTreeString(
        node: GraphNode,
        prefix: String,
        isTail: Boolean,
        sb: java.lang.StringBuilder,
        visited: MutableSet<String>
    ) {
        val cross = if (visited.contains(node.id)) " [CROSS-LINK]" else ""
        val type = if (node.isLeaf) "Leaf" else "Parent/Residual"

        val gmmStats = node.distribution?.let { gmm ->
            val avgVar = gmm.components.flatMap { it.diagonalCovariance!!.toList() }.average()
            " (GMM ${gmm.components.size} centroids, σ² avg: ${"%.6f".format(java.util.Locale.US, avgVar)})"
        } ?: ""

        val nodeLabel = "${node.label} [${node.queries.size} q - $type]$gmmStats$cross"
        sb.append(prefix).append(if (node.depth == 0) "" else if (isTail) "+-- " else "+-- ").append(nodeLabel).append("\n")

        if (visited.contains(node.id)) return
        visited.add(node.id)

        val children = node.children.toList()
        for (i in 0 until children.size) {
            val childIsTail = i == children.size - 1
            val nextPrefix = prefix + if (node.depth == 0) "" else if (isTail) "    " else "|   "
            buildTreeString(children[i], nextPrefix, childIsTail, sb, visited)
        }
    }

    fun collapseMarginalNodes(root: GraphNode) {
        val allNodes = mutableListOf<GraphNode>()
        fun walk(n: GraphNode, visited: MutableSet<String>) {
            if (!visited.add(n.id)) return
            allNodes.add(n)
            n.children.forEach { walk(it, visited) }
        }
        walk(root, mutableSetOf())
        
        // Sort bottom-up (excluding root node, which has depth == 0)
        val sortedNodes = allNodes.filter { it.depth > 0 }.sortedByDescending { it.depth }
        
        for (C in sortedNodes) {
            val parentsCopy = C.parents.toList()
            for (P in parentsCopy) {
                val siblings = P.children.filter { it != C }
                if (siblings.isNotEmpty()) {
                    val childCount = C.getRecursiveQueryCount()
                    val avgSiblingCount = siblings.map { it.getRecursiveQueryCount() }.average()
                    if (childCount < avgSiblingCount * config.formalism.collapseMarginalRatio) {
                        log.info("Collapsing marginal node [${C.label}] (queries: $childCount) into parent [${P.label}] (sibling avg: ${"%.1f".format(java.util.Locale.US, avgSiblingCount)})")
                        
                        // Move queries to parent. If C has other parents left, we keep C's queries
                        val isOrphaned = C.parents.size <= 1
                        P.queries.addAll(C.queries)
                        if (isOrphaned) {
                            C.queries.clear()
                        }
                        
                        // Reparent children of C to P
                        val childrenCopy = C.children.toList()
                        for (K in childrenCopy) {
                            P.children.add(K)
                            K.parents.add(P)
                        }
                        
                        // Disconnect P and C
                        P.children.remove(C)
                        C.parents.remove(P)
                        
                        // If C is fully orphaned now, clean up its children links too
                        if (C.parents.isEmpty()) {
                            for (K in childrenCopy) {
                                K.parents.remove(C)
                            }
                            C.children.clear()
                        }
                    }
                }
            }
        }
    }
}