package taxonomy.service

import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.serialization.Serializable
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.*
import taxonomy.dataset.*
import taxonomy.model.*
import taxonomy.operations.*
import taxonomy.utils.*
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
    private val llmClient: TaxonomyLlmClient,
    private val perfTracker: TaxonomyPerformanceTracker
) {
    private val log = LoggerFactory.getLogger("taxonomy.Service")

    fun getPerformanceReport(): Map<String, PerformanceStats> = perfTracker.getReport()
    fun getPerformanceReportString(): String = perfTracker.printReport()
    fun clearPerformanceTracker() = perfTracker.clear()

    // REACTIVE STATE: For TUI observation
    private val _rootNode = MutableStateFlow<GraphNode?>(null)
    val rootNodeFlow: StateFlow<GraphNode?> = _rootNode.asStateFlow()

    private val _graphVersion = MutableStateFlow(0)
    val graphVersionFlow: StateFlow<Int> = _graphVersion.asStateFlow()

    fun notifyGraphUpdated(structuralChange: Boolean = false) {
        if (structuralChange) {
            _rootNode.value?.let { assignQueryIds(it, config.formalism.enableStableQuestionIds) }
        }
        _graphVersion.value += 1
    }

    private val _metricsHistory = MutableStateFlow<List<IterationMetrics>>(emptyList())
    val metricsHistoryFlow: StateFlow<List<IterationMetrics>> = _metricsHistory.asStateFlow()

    private val _generationProgress = MutableStateFlow<GenerationProgress?>(null)
    val generationProgressFlow: StateFlow<GenerationProgress?> = _generationProgress.asStateFlow()

    private val _labelingProgress = MutableStateFlow<Pair<Int, Int>?>(null)
    val labelingProgressFlow: StateFlow<Pair<Int, Int>?> = _labelingProgress.asStateFlow()

    private val _embeddingProgress = MutableStateFlow<Pair<Int, Int>?>(null)
    val embeddingProgressFlow: StateFlow<Pair<Int, Int>?> = _embeddingProgress.asStateFlow()

    /**
     * ID of the snapshot that is currently "active" — i.e. the one that was most recently saved
     * or loaded. Gateway operations that append logs to the snapshot (judge generation, benchmark)
     * read this so they know which row/file to extend without having to plumb the ID through every
     * call site. Null when no snapshot is active (freshly started DAG not yet saved).
     */
    @Volatile private var _activeSnapshotId: String? = null

    fun activeSnapshotId(): String? = _activeSnapshotId
    fun setActiveSnapshotId(id: String?) { _activeSnapshotId = id }

    fun updateGenerationProgress(progress: GenerationProgress) {
        _generationProgress.value = progress
    }

    fun updateLabelingProgress(current: Int, total: Int) {
        _labelingProgress.value = Pair(current, total)
    }

    fun updateEmbeddingProgress(current: Int, total: Int) {
        _embeddingProgress.value = Pair(current, total)
    }

    fun clearEmbeddingProgress() {
        _embeddingProgress.value = null
    }

    fun clearGenerationProgress() {
        _generationProgress.value = null
        _labelingProgress.value = null
        _embeddingProgress.value = null
    }

    fun clearMetricsHistory() {
        _metricsHistory.value = emptyList()
    }

    fun addIterationMetrics(iterationMetrics: IterationMetrics) {
        _metricsHistory.value += iterationMetrics
    }

    fun getMetricsHistory(): List<IterationMetrics> = _metricsHistory.value

    fun setGraph(node: GraphNode?) {
        _rootNode.value = node
        notifyGraphUpdated()
    }

    fun getGraph(): GraphNode? = _rootNode.value

    suspend fun queryTaxonomy(text: String): List<QueryResponseNode> = coroutineScope {
        log.info("Incoming query: '${if (text.length > 50) text.take(50) + "..." else text}'")
        val currentRoot = getGraph() ?: throw IllegalStateException("Taxonomy not loaded")

        val vector = embeddingCache.getOrCreate(text)
        val emb = Embedding(text, text, vector)

        val results = ops.routeQuery(emb, currentRoot, isInference = true)

        log.info("Query matched ${results.size} nodes: ${results.keys.joinToString { it.label ?: it.id }}")

        return@coroutineScope buildHierarchicalResponse(currentRoot, results.keys, results)
    }

    /**
     * Route a query directly to its matched LEAF nodes, bypassing the hierarchical-wrapper
     * shaping that [queryTaxonomy] applies. Returns (leaf, confidence) pairs sorted by descending
     * confidence, where confidence is exp(logProb) clamped to [0,1]. Used by the batch-trickle
     * benchmark, which needs the concrete leaves (and their query distributions) rather than a
     * presentation tree. Empty if the taxonomy is not loaded or nothing matched.
     */
    internal suspend fun routeQueryToLeaves(text: String): List<Pair<GraphNode, Double>> = coroutineScope {
        val currentRoot = getGraph() ?: return@coroutineScope emptyList<Pair<GraphNode, Double>>()
        val vector = embeddingCache.getOrCreate(text)
        val emb = Embedding(text, text, vector)
        ops.routeQuery(emb, currentRoot, isInference = true).entries
            .filter { it.key.isLeaf }
            .map { it.key to exp(it.value).coerceIn(0.0, 1.0) }
            .sortedByDescending { it.second }
    }

    private fun buildHierarchicalResponse(
        node: GraphNode,
        matchedNodes: Set<GraphNode>,
        scores: Map<GraphNode, Double>,
        parentPath: String = ""
    ): List<QueryResponseNode> {
        val label = node.label ?: node.id
        val currentPath = if (parentPath.isEmpty()) label else "$parentPath > $label"
        val childrenResponse =
            node.treeChildren.flatMap { buildHierarchicalResponse(it, matchedNodes, scores, currentPath) }

        val isMatched = matchedNodes.contains(node)
        if (isMatched || childrenResponse.isNotEmpty()) {
            val confidence = if (isMatched) {
                val score = scores[node] ?: 0.0
                exp(score).coerceIn(0.0, 1.0)
            } else 1.0

            return listOf(QueryResponseNode(
                label = label,
                fullPath = currentPath,
                depth = node.depth,
                confidence = confidence,
                children = childrenResponse.sortedByDescending { it.confidence }
            ))
        }
        return emptyList()
    }
}
