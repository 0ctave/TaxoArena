package taxonomy

import kotlinx.coroutines.coroutineScope
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.model.*
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomyOperations
import taxonomy.operations.TaxonomyStabilizer
import taxonomy.operations.TaxonomyVisualizer
import taxonomy.service.TaxonomyService
import taxonomy.utils.TaxonomyMetrics
import taxonomy.utils.TaxonomyPerformanceTracker
import taxonomy.utils.reportToIterationMetrics
import java.io.File
import kotlin.system.measureTimeMillis

/**
 * High-level orchestrator for the Taxonomy adaptation workflow.
 * Executing Phase 1 (Extract), Phase 2 (Fit), and Phase 3 (Trickle).
 */
@Service
class TaxonomyEngine(
    private val config: TaxonomyConfig,
    private val embeddingCache: EmbeddingCache,
    internal val ops: TaxonomyOperations,
    private val llmClient: TaxonomyLlmClient,
    private val visualizer: TaxonomyVisualizer,
    private val stabilizer: TaxonomyStabilizer,
    private val taxonomyService: TaxonomyService,
    private val perfTracker: TaxonomyPerformanceTracker
) {
    private val log = LoggerFactory.getLogger("Engine")

    suspend fun adaptTaxonomy(rootLabel: String, dataset: Map<String, List<String>>): GraphNode = coroutineScope {
        log.info("Starting Taxonomy Adaptation: $rootLabel")
        log.info(config.formatConfigReport())
        perfTracker.clear()
        ops.resetConceptCounter()
        taxonomyService.clearMetricsHistory()

        val totalIters = config.execution.numIterations
        try {
            // 1. EMBEDDING PRECOMPUTATION: Precompute query embeddings using cache
            log.info("Phase 1: Precomputing Embeddings...")
            taxonomyService.updateGenerationProgress(
                GenerationProgress(
                    currentIteration = 0,
                    totalIterations = totalIters,
                    currentStep = "Phase 1: Precomputing Embeddings",
                    stepIndex = 1,
                    totalSteps = 2,
                    percentComplete = 5.0,
                    statusText = "Precomputing and loading query embeddings..."
                )
            )

            val distilledData: List<Triple<String, String, String>>
            val phase1Time = measureTimeMillis {
                distilledData = dataset.flatMap { (category, queries) ->
                    queries.map { rawText ->
                        Triple(category, rawText, rawText)
                    }
                }

                val allTexts = distilledData.map { it.third }.distinct()
                embeddingCache.precompute(allTexts) { current, total ->
                    taxonomyService.updateEmbeddingProgress(current, total)
                }
                taxonomyService.clearEmbeddingProgress()
            }
            perfTracker.recordTime("Phase 1: Precomputing Embeddings", phase1Time)

            val root = GraphNode(label = rootLabel, depth = 0)

            // 2. Initial Structural Setup & Bootstrap Fitting
            taxonomyService.updateGenerationProgress(
                GenerationProgress(
                    currentIteration = 0,
                    totalIterations = totalIters,
                    currentStep = "Bootstrap Fitting",
                    stepIndex = 2,
                    totalSteps = 2,
                    percentComplete = 10.0,
                    statusText = "Seeding GMM bounds with ground-truth anchors..."
                )
            )

            val bootstrapTime = measureTimeMillis {
                val categoryGroups = distilledData.groupBy { it.first }
                categoryGroups.forEach { (name, items) ->
                    val node = GraphNode(label = name, depth = 1)
                    val embs = items.mapNotNull { (_, raw, keywords) ->
                        embeddingCache.get(keywords)?.let { vec -> Embedding(raw, keywords, vec) }
                    }
                    if (embs.isNotEmpty()) {
                        node.queries.addAll(embs)
                        node.parents.add(root)
                        root.children.add(node)
                    }
                }

                taxonomyService.setGraph(root)
                taxonomyService.notifyGraphUpdated()

                log.info("Bootstrap: Seeding GMMs with 100% ground-truth data...")
                ops.fitNodeRecursive(root)
                taxonomyService.notifyGraphUpdated()
            }
            perfTracker.recordTime("Bootstrap Fitting", bootstrapTime)

            // Ground truth map
            val groundTruthMap = distilledData.groupBy({ it.second }, { it.first })
                .mapValues { it.value.toList() }

            // --- NEW: Print Initial State ---
            log.info("Initial DAG Structure (Before Statistical Fitting)")
            ops.printHierarchy(root)
            saveDot(root, "taxonomy_initial")

            val uniqueEmbs = root.children.flatMap { gatherAllEmbeddingsInBranch(it) }.distinctBy { it.rawText }

            stabilizer.reset()

            var previousDagState: Map<String, NodeState>? = null
            for (i in 1..totalIters) {
                log.info("STARTING EVOLUTION ITERATION $i")

                clearFitPhases(root)

                val iterationTime = measureTimeMillis {
                    if (uniqueEmbs.isNotEmpty()) {
                        // Phase 3: Trickle (Top-Down Restrictive Funnel Routing)
                        log.debug("Phase 3: Trickling (Reassigning Queries)...")
                        val tricklePercent = 10.0 + ((i - 1).toDouble() / totalIters) * 80.0 + (1.0 / 5.0) * (80.0 / totalIters)
                        taxonomyService.updateGenerationProgress(
                            GenerationProgress(
                                currentIteration = i,
                                totalIterations = totalIters,
                                currentStep = "Phase 3: Trickle Routing",
                                stepIndex = 1,
                                totalSteps = 5,
                                percentComplete = tricklePercent,
                                statusText = "Routing queries down parent-child nodes..."
                            )
                        )

                        val trickleTime = measureTimeMillis {
                            ops.clearGraphQueries(root)
                            ops.reassignQueries(root, uniqueEmbs, groundTruthMap, i)
                        }
                        perfTracker.recordTime("Phase 3: Trickle Routing", trickleTime)
                        taxonomyService.notifyGraphUpdated()

                        // Phase 3c: Pre-split passthrough collapse
                        log.debug("Phase 3c: Pre-split passthrough collapse...")
                        val prunePercent = 10.0 + ((i - 1).toDouble() / totalIters) * 80.0 + (2.0 / 5.0) * (80.0 / totalIters)
                        taxonomyService.updateGenerationProgress(
                            GenerationProgress(
                                currentIteration = i,
                                totalIterations = totalIters,
                                currentStep = "Phase 3c: Passthrough Collapse",
                                stepIndex = 2,
                                totalSteps = 5,
                                percentComplete = prunePercent,
                                statusText = "Bypassing intermediate single-child chains..."
                            )
                        )

                        val pruneTime = measureTimeMillis {
                            ops.prunePassthroughNodesPublic(root)
                        }
                        perfTracker.recordTime("Phase 3c: Passthrough Collapse", pruneTime)
                        taxonomyService.notifyGraphUpdated(true)

                        // Phase 4: Discover (Adaptive Splitting)
                        log.debug("Phase 4: Discovering emergent concepts (Splitting)...")
                        val splitPercent = 10.0 + ((i - 1).toDouble() / totalIters) * 80.0 + (3.0 / 5.0) * (80.0 / totalIters)
                        taxonomyService.updateGenerationProgress(
                            GenerationProgress(
                                currentIteration = i,
                                totalIterations = totalIters,
                                currentStep = "Phase 4: Adaptive Splitting",
                                stepIndex = 3,
                                totalSteps = 5,
                                percentComplete = splitPercent,
                                statusText = "Clustering density anomalies and splitting concepts..."
                            )
                        )

                        val splitTime = measureTimeMillis {
                            ops.splitNodesRecursive(root)
                        }
                        perfTracker.recordTime("Phase 4: Adaptive Splitting", splitTime)
                        taxonomyService.notifyGraphUpdated(true)

                        // Phase 5: Optimize (Structural Refinement)
                        log.debug("Phase 5: Optimizing hierarchy (Merging & Cross-linking)...")
                        val optimizePercent = 10.0 + ((i - 1).toDouble() / totalIters) * 80.0 + (4.0 / 5.0) * (80.0 / totalIters)
                        taxonomyService.updateGenerationProgress(
                            GenerationProgress(
                                currentIteration = i,
                                totalIterations = totalIters,
                                currentStep = "Phase 5: Hierarchy Optimization",
                                stepIndex = 4,
                                totalSteps = 5,
                                percentComplete = optimizePercent,
                                statusText = "Merging sibling domains and establishing cross-links..."
                            )
                        )

                        val optimizeTime = measureTimeMillis {
                            ops.optimizeHierarchy(root)
                        }
                        perfTracker.recordTime("Phase 5: Hierarchy Optimization", optimizeTime)
                        taxonomyService.notifyGraphUpdated(true)
                        
                        // Final Refit after optimization
                        log.debug("Phase 2 Refit: Refitting bounds after optimization...")
                        val refitPercent = 10.0 + ((i - 1).toDouble() / totalIters) * 80.0 + (5.0 / 5.0) * (80.0 / totalIters)
                        taxonomyService.updateGenerationProgress(
                            GenerationProgress(
                                currentIteration = i,
                                totalIterations = totalIters,
                                currentStep = "Refit after Optimization",
                                stepIndex = 5,
                                totalSteps = 5,
                                percentComplete = refitPercent,
                                statusText = "Refitting vMF/NiW bounds after topology edits..."
                            )
                        )

                        val refitTime = measureTimeMillis {
                            ops.fitNodeRecursive(root)
                        }
                        perfTracker.recordTime("Refit after Optimization", refitTime)
                        taxonomyService.notifyGraphUpdated()
                    }
                }

                log.info("Iteration $i completed in ${iterationTime}ms.")

                // Calculate and store iteration metrics
                val iterMetrics = TaxonomyMetrics(root, groundTruthMap).generateReport()
                taxonomyService.addIterationMetrics(reportToIterationMetrics("Iter $i", iterMetrics))

                // Print intermediate DAG structure / changes to save log size
                val currentDagState = captureDagState(root)
                if (previousDagState == null) {
                    log.info("=== DAG after iteration $i ===")
                    ops.printHierarchyCompact(root)
                } else {
                    log.info("=== DAG Changes in iteration $i ===")
                    log.info(diffDagState(previousDagState!!, currentDagState, root))
                }
                previousDagState = currentDagState

                // Phase 6: Stabilize Convergence Check
                val stabilizationResult = stabilizer.evaluateConvergence(root, i)
                if (stabilizationResult.isConverged) {
                    log.info("Early stopping triggered in iteration $i due to convergence.")
                    break
                }
            }

            if (!config.execution.enableLiveLabeling && config.execution.enableLabeling) {
                log.info("Post-Pass: Live Labeling was disabled. Performing post-pass labeling on all nodes.")
                taxonomyService.updateGenerationProgress(
                    GenerationProgress(
                        currentIteration = totalIters,
                        totalIterations = totalIters,
                        currentStep = "Post-Pass Labeling",
                        stepIndex = 1,
                        totalSteps = 1,
                        percentComplete = 95.0,
                        statusText = "Synthesizing descriptive labels using LLM..."
                    )
                )

                val postLabelTime = measureTimeMillis {
                    ops.generateLabelsPostPass(root) { current, total ->
                        taxonomyService.updateLabelingProgress(current, total)
                    }
                }
                perfTracker.recordTime("Post-Pass Labeling", postLabelTime)
                taxonomyService.notifyGraphUpdated()
            }

            assignQueryIds(root)
            log.info("--- ${config.execution.numIterations}-Iteration Evolution Completed ---")
            ops.printHierarchy(root)
            
            // Final Exports
            if (config.execution.enableVisualization) {
                visualizer.exportForVisualization(root, groundTruthMap, "taxonomy_visualization.json")
                saveDot(root, "taxonomy_final")
            }

            // Log final performance report
            val perfReport = perfTracker.printReport()
            log.info(perfReport)

            taxonomyService.updateGenerationProgress(
                GenerationProgress(
                    currentIteration = totalIters,
                    totalIterations = totalIters,
                    currentStep = "Complete",
                    stepIndex = 1,
                    totalSteps = 1,
                    percentComplete = 100.0,
                    statusText = "Taxonomy DAG generation completed successfully!"
                )
            )

            // GENERATE ARCHITECTURAL REPORT
            val finalReport = TaxonomyMetrics(root, groundTruthMap)
            finalReport.printReport(config)
            taxonomyService.addIterationMetrics(reportToIterationMetrics("Final", finalReport.generateReport()))
            
            return@coroutineScope root
        } finally {
            taxonomyService.clearGenerationProgress()
        }
    }

    private fun saveDot(root: GraphNode, filename: String) {
        try {
            val dot = ops.exportToDot(root)
            File("$filename.dot").writeText(dot)
            log.info("Graph exported to $filename.dot")
        } catch (e: Exception) {
            log.error("Failed to export DOT graph: ${e.message}")
        }
    }

    private fun gatherAllEmbeddingsInBranch(node: GraphNode, visited: MutableSet<String> = mutableSetOf()): List<Embedding> {
        if (visited.contains(node.id)) return emptyList()
        visited.add(node.id)

        val result = mutableListOf<Embedding>()
        result.addAll(node.queries) // Add local data (leaf data or parent residuals)
        node.treeChildren.forEach { result.addAll(gatherAllEmbeddingsInBranch(it, visited)) }
        return result
    }

    fun clearFitPhases(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
        log.debug("Clearing fit phases for ${node.label} (phase was ${node.phaseCompleted})")
        if (!visited.add(node.id)) return
        // Keep only SPLIT_EVAL and EMBEDDED, clear VMF_FIT(2), NIW_FIT(8), OPTIMIZED(16)
        node.phaseCompleted = node.phaseCompleted and (PHASE_SPLIT_EVAL or PHASE_EMBEDDED)
        node.treeChildren.forEach { clearFitPhases(it, visited) }
        node.crossLinkChildren.forEach { clearFitPhases(it, visited) }
    }

    private fun captureDagState(root: GraphNode): Map<String, NodeState> {
        val stateMap = mutableMapOf<String, NodeState>()
        fun walk(n: GraphNode, visited: MutableSet<String>) {
            if (!visited.add(n.id)) return
            stateMap[n.id] = NodeState(
                id = n.id,
                label = n.label,
                depth = n.depth,
                isLeaf = n.isLeaf,
                parents = n.parents.map { it.id }.toSet(),
                children = n.children.map { it.id }.toSet(),
                kappa = n.vmfKappa,
                directQueries = n.queries.size,
                totalQueries = n.getRecursiveQueryCount()
            )
            n.children.forEach { walk(it, visited) }
            n.crossLinkChildren.forEach { walk(it, visited) }
        }
        walk(root, mutableSetOf())
        return stateMap
    }

    private fun diffDagState(prev: Map<String, NodeState>, curr: Map<String, NodeState>, root: GraphNode): String {
        val sb = StringBuilder()
        sb.append("┌── TAXONOMY CHANGES (WITH CONTEXT) ───────────────────────\n")

        val addedIds = curr.keys - prev.keys
        val removedIds = prev.keys - curr.keys
        val commonIds = prev.keys intersect curr.keys

        // Compute diff for each node
        val diffs = mutableMapOf<String, NodeDiff>()
        addedIds.forEach { id ->
            val state = curr[id]!!
            diffs[id] = NodeDiff(id, state.label, isAdded = true, isRemoved = false, isMutated = false, emptyList(), state)
        }
        removedIds.forEach { id ->
            val state = prev[id]!!
            diffs[id] = NodeDiff(id, state.label, isAdded = false, isRemoved = true, isMutated = false, emptyList(), null)
        }
        commonIds.forEach { id ->
            val p = prev[id]!!
            val c = curr[id]!!
            val details = mutableListOf<String>()
            if (p.isLeaf != c.isLeaf) {
                details.add("type changed: ${if (p.isLeaf) "Leaf" else "Parent"} -> ${if (c.isLeaf) "Leaf" else "Parent"}")
            }
            if (p.label != c.label) {
                details.add("label updated: \"${p.label}\" -> \"${c.label}\"")
            }
            if (p.parents != c.parents) {
                val addedParents = c.parents - p.parents
                val removedParents = p.parents - c.parents
                val parentChanges = mutableListOf<String>()
                if (addedParents.isNotEmpty()) {
                    parentChanges.add("added parents: " + addedParents.map { curr[it]?.label ?: it }.joinToString(", "))
                }
                if (removedParents.isNotEmpty()) {
                    parentChanges.add("removed parents: " + removedParents.map { prev[it]?.label ?: it }.joinToString(", "))
                }
                details.add("relationships updated (" + parentChanges.joinToString("; ") + ")")
            }

            diffs[id] = NodeDiff(id, c.label, isAdded = false, isRemoved = false, isMutated = details.isNotEmpty(), details, c)
        }

        // Find closest surviving ancestor in curr for each removed node
        val removedChildren = mutableMapOf<String, MutableList<NodeDiff>>()
        removedIds.forEach { rId ->
            val rDiff = diffs[rId]!!
            val parentId = findClosestSurvivingAncestor(rId, prev, curr) ?: root.id
            removedChildren.getOrPut(parentId) { mutableListOf() }.add(rDiff)
        }

        // Check recursively if a node has changes in its subtree
        val memoHasChanges = mutableMapOf<String, Boolean>()
        fun hasChangesInSubtree(nodeId: String): Boolean {
            memoHasChanges[nodeId]?.let { return it }
            val diff = diffs[nodeId]
            val selfChanged = diff != null && (diff.isAdded || diff.isMutated)
            val hasRemoved = removedChildren.containsKey(nodeId)
            var childrenChanged = false
            val nodeState = curr[nodeId]
            if (nodeState != null) {
                for (childId in nodeState.children) {
                    if (hasChangesInSubtree(childId)) {
                        childrenChanged = true
                    }
                }
            }
            val result = selfChanged || hasRemoved || childrenChanged
            memoHasChanges[nodeId] = result
            return result
        }

        // If root has no changes in its subtree, return no changes
        if (!hasChangesInSubtree(root.id)) {
            sb.append("│   (No structural changes in this iteration)\n")
            sb.append("└──────────────────────────────────────────────────────────")
            return sb.toString()
        }

        // Build tree recursively
        fun buildTree(
            nodeId: String,
            prefix: String,
            isTail: Boolean,
            visited: MutableSet<String>
        ) {
            val diff = diffs[nodeId]
            val state = curr[nodeId] ?: return
            val cross = if (visited.contains(nodeId)) " [CROSS-LINK]" else ""
            
            val type = if (state.isLeaf) "Leaf" else "Parent"
            val nodeLabel = when {
                diff?.isAdded == true -> "[ADDED] \"${state.label}\" ($type, kappa: ${"%.1f".format(java.util.Locale.US, state.kappa)}, q=${state.directQueries}/${state.totalQueries})"
                diff?.isMutated == true -> "[MUTATED] \"${state.label}\" ($type, kappa: ${"%.1f".format(java.util.Locale.US, state.kappa)}, q=${state.directQueries}/${state.totalQueries}) -> ${diff.mutationDetails.joinToString(", ")}"
                else -> "\"${state.label}\" ($type, q=${state.directQueries}/${state.totalQueries})"
            }

            val connector = if (state.depth == 0) "" else if (isTail) "└── " else "├── "
            sb.append(prefix).append(connector).append(nodeLabel).append(cross).append("\n")

            if (!visited.add(nodeId)) return

            // Gather children to print
            val childrenToPrint = mutableListOf<PrintItem>()
            state.children.forEach { childId ->
                if (hasChangesInSubtree(childId)) {
                    val childState = curr[childId]!!
                    childrenToPrint.add(PrintItem.Surviving(childState))
                }
            }
            removedChildren[nodeId]?.forEach { rDiff ->
                childrenToPrint.add(PrintItem.Removed(rDiff))
            }

            for (i in 0 until childrenToPrint.size) {
                val item = childrenToPrint[i]
                val childIsTail = i == childrenToPrint.size - 1
                val nextPrefix = prefix + if (state.depth == 0) "" else if (isTail) "    " else "│   "
                
                when (item) {
                    is PrintItem.Surviving -> {
                        buildTree(item.state.id, nextPrefix, childIsTail, visited)
                    }
                    is PrintItem.Removed -> {
                        val rConnector = if (childIsTail) "└── " else "├── "
                        sb.append(nextPrefix).append(rConnector).append("[REMOVED] \"${item.diff.label ?: item.diff.id}\"\n")
                    }
                }
            }
        }

        buildTree(root.id, "│ ", true, mutableSetOf())

        sb.append("└──────────────────────────────────────────────────────────")
        return sb.toString()
    }

    private fun findClosestSurvivingAncestor(rId: String, prev: Map<String, NodeState>, curr: Map<String, NodeState>): String? {
        val visited = mutableSetOf<String>()
        val queue = java.util.ArrayDeque<String>()
        queue.add(rId)
        visited.add(rId)
        
        while (queue.isNotEmpty()) {
            val currentId = queue.removeFirst()
            val state = prev[currentId] ?: continue
            for (parentId in state.parents) {
                if (parentId in curr) {
                    return parentId
                }
                if (visited.add(parentId)) {
                    queue.addLast(parentId)
                }
            }
        }
        return null
    }
}

private data class NodeState(
    val id: String,
    val label: String?,
    val depth: Int,
    val isLeaf: Boolean,
    val parents: Set<String>,
    val children: Set<String>,
    val kappa: Double,
    val directQueries: Int,
    val totalQueries: Int
)

private data class NodeDiff(
    val id: String,
    val label: String?,
    val isAdded: Boolean,
    val isRemoved: Boolean,
    val isMutated: Boolean,
    val mutationDetails: List<String>,
    val state: NodeState?
)

private sealed class PrintItem {
    data class Surviving(val state: NodeState) : PrintItem()
    data class Removed(val diff: NodeDiff) : PrintItem()
}