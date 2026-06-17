package org.eclipse.lmos.arc.app.taxonomy

import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.serialization.Serializable
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.TaxoPrompts
import kotlin.math.exp

@Serializable
data class QueryResponseNode(
    val label: String,
    val fullPath: String,
    val depth: Int,
    val confidence: Double,
    val children: List<QueryResponseNode> = emptyList()
)

@Service
class TaxonomyService(
    private val config: TaxonomyConfig,
    private val ops: TaxonomyOperations,
    private val embeddingCache: EmbeddingCache,
    private val persistence: TaxonomyPersistence,
    private val llmClient: org.eclipse.lmos.arc.app.taxonomy.operations.TaxonomyLlmClient,
    private val distillationCache: org.eclipse.lmos.arc.app.taxonomy.operations.DistillationCache
) {
    private val log = LoggerFactory.getLogger(TaxonomyService::class.java)
    
    // REACTIVE STATE: For TUI observation
    private val _rootNode = MutableStateFlow<GraphNode?>(null)
    val rootNodeFlow: StateFlow<GraphNode?> = _rootNode.asStateFlow()

    private val _graphVersion = MutableStateFlow(0)
    val graphVersionFlow: StateFlow<Int> = _graphVersion.asStateFlow()

    fun notifyGraphUpdated() {
        _rootNode.value?.let { assignQueryIds(it) }
        _graphVersion.value = _graphVersion.value + 1
    }

    private val _metricsHistory = MutableStateFlow<List<IterationMetrics>>(emptyList())
    val metricsHistoryFlow: StateFlow<List<IterationMetrics>> = _metricsHistory.asStateFlow()

    fun clearMetricsHistory() {
        _metricsHistory.value = emptyList()
    }

    fun addIterationMetrics(iteration: String, report: TaxonomyMetrics.Report) {
        val metrics = IterationMetrics(
            iteration = iteration,
            totalNodes = report.totalNodes,
            leafNodes = report.leafNodes,
            crossDomainNodes = report.crossDomainNodes,
            maxDepth = report.maxDepth,
            avgLeafDepth = report.avgLeafDepth,
            totalUniqueQueries = report.totalUniqueQueries,
            residualQueries = report.residualQueries,
            totalPathRedundancy = report.totalPathRedundancy,
            totalLogVolume = report.totalLogVolume,
            residualRatio = report.residualRatio,
            maxLeafConcentration = report.maxLeafConcentration,
            contaminationRatio = report.contaminationRatio,
            equilibriumIndex = report.equilibriumIndex,
            relevanceComplianceRatio = report.relevanceComplianceRatio
        )
        _metricsHistory.value = _metricsHistory.value + metrics
    }

    fun getMetricsHistory(): List<IterationMetrics> = _metricsHistory.value


    fun setGraph(node: GraphNode) {
        _rootNode.value = node
        notifyGraphUpdated()
    }

    fun getGraph(): GraphNode? = _rootNode.value

    suspend fun queryTaxonomy(text: String): List<QueryResponseNode> = coroutineScope {
        log.info("Incoming query: '${if (text.length > 50) text.take(50) + "..." else text}'")
        val currentRoot = getGraph() ?: throw IllegalStateException("Taxonomy not loaded")
        
        val distilled = if (config.execution.enableDistillation) {
             distillationCache.get(text, "query") ?: run {
                val prompt = TaxoPrompts.getDistillationPrompt(text, "General")
                val result = llmClient.distillQuery(prompt)
                if (result.isNotBlank()) {
                    distillationCache.put(text, "query", result)
                    result
                } else text
            }
        } else text

        val vector = embeddingCache.getOrCreate(distilled)
        val emb = Embedding(text, distilled, vector)

        val results = mutableMapOf<GraphNode, Double>()
        ops.trickleQuery(emb, currentRoot, results)
        
        log.info("Query matched ${results.size} nodes: ${results.keys.joinToString { it.label }}")

        return@coroutineScope buildHierarchicalResponse(currentRoot, results.keys, results)
    }

    private fun buildHierarchicalResponse(
        node: GraphNode, 
        matchedNodes: Set<GraphNode>, 
        scores: Map<GraphNode, Double>,
        parentPath: String = ""
    ): List<QueryResponseNode> {
        val currentPath = if (parentPath.isEmpty()) node.label else "$parentPath > ${node.label}"
        val childrenResponse = node.children
            .map { buildHierarchicalResponse(it, matchedNodes, scores, currentPath) }
            .flatten()

        val isMatched = matchedNodes.contains(node)
        if (isMatched || childrenResponse.isNotEmpty()) {
            val confidence = if (isMatched) {
                val score = scores[node] ?: 0.0
                exp(-0.1 * score).coerceIn(0.0, 1.0)
            } else 1.0

            return listOf(QueryResponseNode(
                label = node.label,
                fullPath = currentPath,
                depth = node.depth,
                confidence = confidence,
                children = childrenResponse.sortedByDescending { it.confidence }
            ))
        }
        return emptyList()
    }

    fun saveGraph(path: String) {
        getGraph()?.let { persistence.save(it, path) }
    }

    fun loadGraph(path: String) {
        persistence.load(path)?.let {
            setGraph(it)
            clearMetricsHistory()
            val report = TaxonomyMetrics(it).generateReport()
            addIterationMetrics("Loaded", report)
        }
    }
}
