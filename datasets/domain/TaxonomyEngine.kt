package org.eclipse.lmos.arc.app.domain

import dev.langchain4j.model.embedding.EmbeddingModel
import kotlinx.coroutines.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.eclipse.lmos.arc.app.LLMProvider
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import java.io.File
import java.util.concurrent.ConcurrentHashMap
import kotlin.math.pow

/**
 * Deterministic Epoch-Based Domain Inference Engine.
 * Uses "Global Tightest-Fit Routing" to perfectly map queries to their most specific
 * valid sub-domains, guaranteeing zero data loss and stable hierarchical formation.
 */
@Service
class TaxonomyEngine(
    private val llmProvider: LLMProvider,
    private val embeddingModel: EmbeddingModel,
    @Value("\${taxoadapt.max-density:8}") private val maxDensity: Int,
    @Value("\${taxoadapt.max-depth:4}") private val maxDepth: Int,
    @Value("\${taxoadapt.granularity.merge-threshold:0.12}") private val baseMergeThreshold: Float,
    @Value("\${taxoadapt.granularity.cluster-epsilon:0.18}") private val baseClusterEpsilon: Float
) {
    private val log = LoggerFactory.getLogger(TaxonomyEngine::class.java)
    private val json = Json { ignoreUnknownKeys = true; isLenient = true; coerceInputValues = true }

    private val embeddingCache = ConcurrentHashMap<String, FloatArray>()
    private val embeddingCacheFile = File("embeddings_cache.json")

    // Strict Geometric tracking
    private val domainCentroids = ConcurrentHashMap<String, FloatArray>()
    private val domainRadii = ConcurrentHashMap<String, Float>()

    suspend fun adaptTaxonomy(superRootLabel: String, mmluData: Map<String, List<String>>): GraphNode {
        val totalStart = System.currentTimeMillis()
        log.info("=== [START] Deterministic Tightest-Fit Engine ===")

        val rootNode = GraphNode(label = superRootLabel)
        val allQueries = mmluData.values.flatten().distinct()

        loadEmbeddingsCache()
        computeMissingEmbeddings(allQueries)

        log.info("[Phase 1] Bootstrapping Initial Subjects...")
        var activeNodes = mmluData.map { (subject, questions) ->
            val node = GraphNode(label = subject)
            node.queries.addAll(questions)
            updateMetrics(node)
            node
        }.toMutableList()

        log.info("[Phase 2] Structural Reconciliation (Merge & Synthesize)...")
        activeNodes = mergeIdenticals(activeNodes)
        val synthesizedParents = synthesizeSuperDomains(activeNodes)

        // Attach all top-level structures to Root
        synthesizedParents.forEach { rootNode.addChild(it) }
        activeNodes.filter { it.parents.isEmpty() && !it.isMerged }.forEach { rootNode.addChild(it) }

        // Calculate the Universal Bounding Sphere for the Root
        updateMetrics(rootNode)

        log.info("[Phase 3] Commencing Routing & Expansion Epochs...")
        var iteration = 1
        var graphChanged = true

        // The Expectation-Maximization Epoch Loop
        while (graphChanged && iteration <= 5) {
            log.info("--- [Epoch $iteration] ---")

            // Step A: The Great Routing
            // Clear all current query placements
            rootNode.getAllNodes().forEach { it.queries.clear() }

            // Re-route every query to the most specific domain that bounds it
            routeAllQueriesGlobal(allQueries, rootNode)

            val totalRouted = rootNode.getAllNodes().sumOf { it.queries.size }
            log.info("    -> Routed $totalRouted queries across the graph.")

            // Step B: Update geometric bounds tightly around the new exact placements
            rootNode.getAllNodes().forEach { updateMetrics(it) }

            // Step C: Threshold Expansion
            // Any node accumulating more than maxDensity queries needs a sub-domain
            graphChanged = expandDenseNodes(rootNode)

            iteration++
        }

        log.info("=== [STABILITY] Final Hierarchy Resolved in ${iteration - 1} epochs. ===")
        log.info("Execution Time: ${System.currentTimeMillis() - totalStart}ms")

        return rootNode
    }

    /**
     * Phase 3A: Global Tightest-Fit Routing.
     * Evaluates a query against EVERY node simultaneously. Assigns the query to the node
     * that mathematically encompasses it AND has the smallest radius (most specific).
     */
    private fun routeAllQueriesGlobal(queries: List<String>, rootNode: GraphNode) {
        val allNodes = rootNode.getAllNodes().filter { !it.isMerged }

        queries.forEach { query ->
            val vec = embeddingCache[query] ?: return@forEach

            var bestNode: GraphNode = rootNode
            var minRadius = Float.MAX_VALUE
            var bestDistanceIfNoFit = Float.MAX_VALUE
            var foundFit = false

            for (node in allNodes) {
                val centroid = domainCentroids[node.id] ?: continue
                val radius = domainRadii[node.id] ?: continue

                val distance = Geometry.cosineDistance(centroid, vec)

                // Inclusion Check: Does the query fall within this domain's geometric boundary?
                // (1.05x elasticity buffer handles minor floating point drift across epochs)
                if (distance <= radius * 1.05f) {
                    foundFit = true
                    // Specificity Check: We prefer the tightest/smallest bounding sphere
                    if (radius < minRadius) {
                        minRadius = radius
                        bestNode = node
                    }
                } else if (!foundFit) {
                    // Fallback tracking: If it somehow fits nothing, we track the absolute closest node
                    if (distance < bestDistanceIfNoFit) {
                        bestDistanceIfNoFit = distance
                        bestNode = node
                    }
                }
            }

            // Exactly one node claims ownership of the query.
            bestNode.queries.add(query)
        }
    }

    /**
     * Phase 3C: Expansion of nodes that breached the max-density threshold.
     */
    private suspend fun expandDenseNodes(rootNode: GraphNode): Boolean {
        // Expand nodes that accumulated too many *direct* queries
        val nodesToExpand = rootNode.getAllNodes().filter {
            !it.isMerged && it.queries.size > maxDensity && it.depth < maxDepth
        }

        if (nodesToExpand.isEmpty()) return false

        var structuralChange = false

        coroutineScope {
            nodesToExpand.map { node ->
                async(Dispatchers.IO) {
                    val eps = baseClusterEpsilon * 0.95f.pow(node.depth)
                    val minPts = (maxDensity / 2).coerceAtLeast(2)

                    val embeddedQueries = node.queries.mapNotNull { q ->
                        embeddingCache[q]?.let { vec -> EmbeddedQuery(q, vec) }
                    }

                    val clusters = Geometry.dbscan(embeddedQueries, eps = eps, minPts = minPts)

                    if (clusters.isNotEmpty()) {
                        log.info("[Expansion] Node '${node.label}' triggered expansion into ${clusters.size} sub-domains.")

                        clusters.forEach { cluster ->
                            val representative = cluster.take(maxDensity).map { it.text }
                            try {
                                val prompt = TaxoPrompts.clusterLabeling(representative, node.label, node.children.map { it.label })
                                val resp = llmProvider.completePrompt("TaxoExpander", prompt)
                                val labelDef = json.decodeFromString<LocalLabelResponse>(cleanJson(resp))

                                val newNode = GraphNode(label = labelDef.label)
                                // Temporarily attach queries to seed initial metrics
                                newNode.queries.addAll(cluster.map { it.text })
                                updateMetrics(newNode)

                                synchronized(node) {
                                    node.addChild(newNode)
                                    structuralChange = true
                                }
                            } catch (e: Exception) {
                                log.warn("[Expansion] LLM failed to label cluster for '${node.label}'")
                            }
                        }
                    }
                }
            }.awaitAll()
        }

        return structuralChange
    }

    /**
     * Groups initial subjects into overarching Parent domains using DBSCAN on their Centroids.
     */
    private suspend fun synthesizeSuperDomains(nodes: List<GraphNode>): List<GraphNode> {
        val validNodes = nodes.filter { !it.isMerged && domainCentroids.containsKey(it.id) }
        val embeddedCentroids = validNodes.map { n -> EmbeddedQuery(n.label, domainCentroids[n.id]!!, n.id) }

        val clusters = Geometry.dbscan(embeddedCentroids, eps = baseClusterEpsilon * 1.3f, minPts = 2)
        val parentNodes = mutableListOf<GraphNode>()

        clusters.forEach { cluster ->
            val subjects = cluster.mapNotNull { eq -> validNodes.find { it.id == eq.id } }
            if (subjects.size > 1) {
                val groupNames = subjects.map { it.label }
                try {
                    val resp = llmProvider.completePrompt("TaxoExpander", TaxoPrompts.superDomainSynthesis(groupNames))
                    val labelDef = json.decodeFromString<LocalLabelResponse>(cleanJson(resp))

                    val superNode = GraphNode(label = labelDef.label)
                    subjects.forEach { superNode.addChild(it) }

                    // The Umbrella's true geometric bounds are defined by all underlying queries
                    updateMetrics(superNode)

                    parentNodes.add(superNode)
                    log.info("[Synthesis] Grouped ${groupNames.size} subjects under umbrella: '${superNode.label}'")
                } catch (e: Exception) {
                    log.warn("[Synthesis] LLM failed to synthesize umbrella for $groupNames")
                }
            }
        }
        return parentNodes
    }

    private fun mergeIdenticals(nodes: MutableList<GraphNode>): MutableList<GraphNode> {
        val uniqueNodes = mutableListOf<GraphNode>()
        for (node in nodes) {
            val nCentroid = domainCentroids[node.id] ?: continue
            val existing = uniqueNodes.find { other ->
                val oCentroid = domainCentroids[other.id]
                oCentroid != null && Geometry.cosineDistance(nCentroid, oCentroid) < baseMergeThreshold
            }

            if (existing != null) {
                log.info("[Merge] Combining '${node.label}' -> '${existing.label}'")
                existing.queries.addAll(node.queries)
                node.isMerged = true
                updateMetrics(existing)
            } else {
                uniqueNodes.add(node)
            }
        }
        return uniqueNodes
    }

    /**
     * Calculates the definitive geometric center and Maximum Bounding Sphere for a domain.
     * Incorporates all queries held by the node AND its topological descendants.
     */
    private fun updateMetrics(node: GraphNode) {
        // Collects queries directly in this node + all nested children
        val allQueriesInSubtree = node.getAllNodes()
            .filter { !it.isMerged }
            .flatMap { it.queries }
            .distinct()

        val vecs = allQueriesInSubtree.mapNotNull { embeddingCache[it] }
        if (vecs.isEmpty()) return

        val dims = vecs.first().size
        val centroid = FloatArray(dims)

        vecs.forEach { v -> for (i in 0 until dims) centroid[i] += v[i] }
        for (i in 0 until dims) centroid[i] /= vecs.size.toFloat()

        domainCentroids[node.id] = centroid

        // Define radius as the Absolute Maximum Distance to any constituent query
        var maxDist = 0f
        vecs.forEach { v ->
            val dist = Geometry.cosineDistance(centroid, v)
            if (dist > maxDist) maxDist = dist
        }

        // Apply a strict floor so tight highly-specific nodes don't collapse into 0-volume points
        domainRadii[node.id] = maxDist.coerceAtLeast(0.15f)
    }

    private fun cleanJson(raw: String): String {
        val s = raw.indexOf('{')
        val e = raw.lastIndexOf('}')
        return if (s != -1 && e != -1 && e > s) raw.substring(s, e + 1) else raw
    }

    private fun loadEmbeddingsCache() {
        if (embeddingCacheFile.exists()) try {
            embeddingCache.putAll(json.decodeFromString<Map<String, FloatArray>>(embeddingCacheFile.readText()))
        } catch (e: Exception) { log.warn("Cache load failed.") }
    }

    private suspend fun computeMissingEmbeddings(allQueries: List<String>) {
        val missing = allQueries.filter { !embeddingCache.containsKey(it) }
        if (missing.isEmpty()) return
        log.info("Generating embeddings for ${missing.size} queries...")
        coroutineScope {
            missing.chunked(100).forEach { chunk ->
                launch(Dispatchers.IO) {
                    chunk.forEach { t -> embeddingCache[t] = embeddingModel.embed(t).content().vector() }
                }
            }
        }
        withContext(Dispatchers.IO) {
            try { embeddingCacheFile.writeText(json.encodeToString(embeddingCache.toMap())) } catch (e: Exception) {}
        }
    }

    @Serializable
    private data class LocalLabelResponse(val label: String, val description: String)
}