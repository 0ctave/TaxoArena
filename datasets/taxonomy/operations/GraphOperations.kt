package org.eclipse.lmos.arc.app.taxonomy.operations

import kotlinx.coroutines.*
import kotlinx.serialization.json.Json
import org.eclipse.lmos.arc.app.LLMProvider
import org.eclipse.lmos.arc.app.taxonomy.*
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import kotlin.math.exp
import kotlin.math.max

@Service
class GraphOperations(
    private val llmProvider: LLMProvider,
    private val config: TaxonomyConfig,
    private val cache: EmbeddingCache
) {
    private val log = LoggerFactory.getLogger(GraphOperations::class.java)
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }
    private val safeMinFloor = kotlin.math.min(config.minVarianceFloor, 0.0001f)

    fun recalculateMetrics(graph: Set<GraphNode>) {
        val d = cache.dimensionality
        graph.filter { !it.isMerged }.forEach { node ->
            val vectors = node.queries.mapNotNull { cache.get(it) }
            if (vectors.isNotEmpty()) {
                node.centroid = GeometryMath.calculateCentroid(vectors, d)
                node.variance = GeometryMath.calculateVariance(vectors, node.centroid!!, safeMinFloor)
            }
        }
    }

    suspend fun executeFitting(root: GraphNode, allQueries: List<String>, tempTauFit: Float) {
        log.info("[Op 1: Fitting] Trickling ${allQueries.size} queries down the DAG (tauFit=$tempTauFit)")

        coroutineScope {
            allQueries.map { qId ->
                async(Dispatchers.Default) {
                    val vec = cache.get(qId) ?: return@async
                    val queue = ArrayDeque<GraphNode>()
                    queue.add(root)

                    var settledInLeaf = false
                    val visited = mutableSetOf<String>()

                    while (queue.isNotEmpty()) {
                        val current = queue.removeFirst()
                        if (current.isMerged || !visited.add(current.id)) continue

                        val evaluatedChildren = current.children
                            .filter { !it.isMerged && it.centroid != null && it.variance != null }
                            .map { it to GeometryMath.inclusionProbability(vec, it.centroid!!, it.variance!!, config.inclusionScalingFactor) }

                        val passingChildren = evaluatedChildren.filter { it.second >= tempTauFit }

                        if (passingChildren.isNotEmpty()) {
                            val bestProb = passingChildren.maxOf { it.second }
                            val winners = passingChildren.filter { it.second >= bestProb * 0.99f }.map { it.first }

                            winners.forEach { queue.add(it) }
                            settledInLeaf = true
                        } else {
                            current.queries.add(qId)
                        }
                    }

                    if (!settledInLeaf && !root.queries.contains(qId)) {
                        root.queries.add(qId)
                    }
                }
            }.awaitAll()
        }

        // PRUNING: Remove any leaf nodes that have zero queries after trickling down
        var pruned = 0
        val allNodes = root.getAllNodes().filter { !it.isMerged && it != root }
        for (node in allNodes) {
            if (node.children.isEmpty() && node.queries.isEmpty()) {
                log.info("[Op 1.5: Pruning] Removing empty leaf node '${node.label}'")
                node.isMerged = true
                node.parents.toList().forEach { it.removeChild(node) }
                pruned++
            }
        }
        if (pruned > 0) {
            log.info("[Op 1.5: Pruning] Swept $pruned empty leaf domains from the graph.")
        }
    }

    suspend fun executeSplitting(root: GraphNode, currentTemp: Float): Int {
        val allNodes = root.getAllNodes().filter { !it.isMerged }
        var splitsOccurred = 0

        coroutineScope {
            allNodes.map { node ->
                async(Dispatchers.IO) {
                    val dynamicDensityReq = max(
                        config.splitMinThreshold.toFloat(),
                        config.splitBaseThreshold * exp(-config.depthDecayLambda * node.depth)
                    ).toInt()

                    if (node.queries.size > dynamicDensityReq && node.depth < config.maxDepth && node.children.size < config.maxWidth) {
                        val points = node.queries.mapNotNull { q -> cache.get(q)?.let { v -> EmbeddedQuery(q, v) } }
                        val clusters = Geometry.dbscan(points, eps = 0.15f, minPts = config.splitMinThreshold)

                        if (clusters.isNotEmpty()) {
                            val parentVarTrace = GeometryMath.varianceTrace(node.variance!!)

                            clusters.forEach { cluster ->
                                val vecs = cluster.map { it.embedding }
                                val mu = GeometryMath.calculateCentroid(vecs, cache.dimensionality)
                                val variance = GeometryMath.calculateVariance(vecs, mu, safeMinFloor)
                                val childVarTrace = GeometryMath.varianceTrace(variance)

                                if (childVarTrace < config.varianceCompressionRho * currentTemp * parentVarTrace) {
                                    val samples = cluster.take(10).map { it.text }
                                    try {
                                        val prompt = TaxonomyPrompts.clusterLabeling(samples, node.label, node.children.map { it.label })
                                        val resp = json.decodeFromString<LocalLabelResponse>(cleanJson(llmProvider.completePrompt("Expander", prompt)))
                                        val newNode = GraphNode(resp.label, resp.description)
                                        synchronized(node) { node.addChild(newNode) }
                                        splitsOccurred++
                                    } catch (e: Exception) { /* skip */ }
                                }
                            }
                        }
                    }
                }
            }.awaitAll()
        }
        return splitsOccurred
    }

    private data class ReparentProposal(val nodeA: GraphNode, val nodeB: GraphNode, val avgProb: Float)

    suspend fun executeReparenting(root: GraphNode, tempTauReparent: Float): Int {
        var reparents = 0
        val allNodes = root.getAllNodes().filter { !it.isMerged && it != root }
        val proposals = java.util.concurrent.ConcurrentLinkedQueue<ReparentProposal>()

        // PHASE 1: Massively parallel mathematical evaluation of Subsumption ($O(N^2)$)
        coroutineScope {
            allNodes.map { nodeA ->
                async(Dispatchers.Default) {
                    if (nodeA.queries.isEmpty()) return@async
                    val vectorsA = nodeA.queries.mapNotNull { cache.get(it) }
                    if (vectorsA.isEmpty()) return@async

                    for (nodeB in allNodes) {
                        if (nodeA == nodeB || isAncestor(nodeA, nodeB)) continue

                        if (nodeB.centroid != null && nodeB.variance != null) {
                            var probSum = 0f
                            vectorsA.forEach { v ->
                                probSum += GeometryMath.inclusionProbability(v, nodeB.centroid!!, nodeB.variance!!, config.inclusionScalingFactor)
                            }
                            val avgProb = probSum / vectorsA.size

                            if (avgProb >= tempTauReparent && !nodeA.parents.contains(nodeB)) {
                                proposals.add(ReparentProposal(nodeA, nodeB, avgProb))
                            }
                        }
                    }
                }
            }.awaitAll()
        }

        // PHASE 2: Apply topological changes sequentially to strictly prevent concurrent DAG cycles
        val validProposals = proposals.sortedByDescending { it.avgProb }
        val relabelTasks = mutableListOf<suspend () -> Unit>()

        for (proposal in validProposals) {
            val nodeA = proposal.nodeA
            val nodeB = proposal.nodeB

            // Must re-check cycle/parent conditions because the graph mutates during this loop
            if (nodeA.parents.contains(nodeB) || isAncestor(nodeA, nodeB)) continue

            log.info("[Op 3: Reparenting] Subsumption Edge Created: '${nodeB.label}' -> '${nodeA.label}' (P_avg = ${proposal.avgProb})")

            val sharedParents = nodeA.parents.intersect(nodeB.parents.toSet()).toList()
            nodeB.addChild(nodeA)

            sharedParents.forEach { sharedParent ->
                sharedParent.removeChild(nodeA)
                log.info("  -> Severed redundant shared edge: '${sharedParent.label}' -> '${nodeA.label}'")
            }

            reparents++

            // Queue up the LLM task
            relabelTasks.add {
                val samples = nodeA.queries.take(10).toList()
                try {
                    val prompt = TaxonomyPrompts.domainRelabeling(nodeA.label, nodeB.label, samples)
                    val resp = json.decodeFromString<LocalLabelResponse>(cleanJson(llmProvider.completePrompt("Expander", prompt)))
                    if (resp.label != nodeA.label) {
                        log.info("  -> Relabeled '${nodeA.label}' to '${resp.label}' to fit under '${nodeB.label}'")
                        nodeA.label = resp.label
                        nodeA.description = resp.description
                    }
                } catch (e: Exception) {
                    log.debug("  -> Failed to relabel '${nodeA.label}'", e)
                }
            }
        }

        // PHASE 3: Execute all LLM Relabeling network calls in parallel
        if (relabelTasks.isNotEmpty()) {
            coroutineScope {
                relabelTasks.map { task -> async(Dispatchers.IO) { task() } }.awaitAll()
            }
        }

        return reparents
    }

    fun executeMerging(root: GraphNode, tempTauMerge: Float): Int {
        var merges = 0
        val allNodes = root.getAllNodes().filter { !it.isMerged && it != root }.toMutableList()

        for (i in allNodes.indices) {
            val nodeA = allNodes[i]
            // FIX: Guard against null geometry if nodeA hasn't settled or is an empty parent
            if (nodeA.centroid == null || nodeA.variance == null) continue

            for (j in i + 1 until allNodes.size) {
                val nodeB = allNodes[j]
                // FIX: Ensure nodeB still exists and has valid geometry metrics
                if (nodeB.isMerged || nodeB.centroid == null || nodeB.variance == null) continue

                val distB = GeometryMath.bhattacharyyaDistance(nodeA.centroid!!, nodeA.variance!!, nodeB.centroid!!, nodeB.variance!!)
                if (distB < (1f - tempTauMerge)) {
                    log.info("[Op 4: Merging] Fusing '${nodeB.label}' into '${nodeA.label}'")
                    nodeB.isMerged = true
                    nodeA.children.addAll(nodeB.children)
                    nodeB.children.forEach { it.parents.add(nodeA); it.parents.remove(nodeB) }
                    merges++
                }
            }
        }
        return merges
    }

    fun executeClearing(root: GraphNode) {
        log.info("[Op 5: Clearing] Flushing empirical state to prepare for fresh trickling.")
        root.getAllNodes().forEach { it.queries.clear() }
    }

    private fun isAncestor(potentialAncestor: GraphNode, targetNode: GraphNode): Boolean {
        val visited = mutableSetOf<String>()
        val queue = ArrayDeque<GraphNode>()
        queue.addAll(targetNode.parents)
        while (queue.isNotEmpty()) {
            val curr = queue.removeFirst()
            if (curr.id == potentialAncestor.id) return true
            if (visited.add(curr.id)) queue.addAll(curr.parents)
        }
        return false
    }

    private fun cleanJson(raw: String): String {
        val start = raw.indexOf('{'); val end = raw.lastIndexOf('}')
        return if (start != -1 && end != -1 && end > start) raw.substring(start, end + 1) else raw
    }
}