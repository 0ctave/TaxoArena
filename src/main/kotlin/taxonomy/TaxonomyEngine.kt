package org.eclipse.lmos.arc.app.taxonomy

import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service

import kotlinx.coroutines.*
import taxonomy.StatisticsUtils
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
    private val ops: TaxonomyOperations,
    private val llmClient: org.eclipse.lmos.arc.app.taxonomy.operations.TaxonomyLlmClient,
    private val distillationCache: org.eclipse.lmos.arc.app.taxonomy.operations.DistillationCache,
    private val visualizer: org.eclipse.lmos.arc.app.taxonomy.operations.TaxonomyVisualizer,
    private val stabilizer: org.eclipse.lmos.arc.app.taxonomy.operations.TaxonomyStabilizer,
    private val taxonomyService: TaxonomyService
) {
    private val log = LoggerFactory.getLogger(TaxonomyEngine::class.java)

    suspend fun adaptTaxonomy(rootLabel: String, dataset: Map<String, List<String>>): GraphNode = coroutineScope {
        log.info("Starting Taxonomy Adaptation: $rootLabel")
        ops.resetConceptCounter()
        taxonomyService.clearMetricsHistory()

        // 1. SEMANTIC DISTILLATION: Convert raw queries to taxonomic signatures using cache
        log.info("Phase 1: Semantic Distillation (Extracting Taxonomic Signatures)...")
        val distilledData = dataset.flatMap { (category, queries) ->
            queries.map { rawText ->
                async(Dispatchers.IO) {
                    val keywords = if (config.execution.enableDistillation) {
                        distillationCache.get(rawText, category) ?: run {
                            val prompt = taxonomy.TaxoPrompts.getDistillationPrompt(rawText, category)
                            val distilled = llmClient.distillQuery(prompt)
                            val result = if (distilled.isNotBlank()) distilled else rawText
                            distillationCache.put(rawText, category, result)
                            result
                        }
                    } else {
                        rawText
                    }
                    Triple(category, rawText, keywords)
                }
            }
        }.awaitAll()

        val allDistilledTexts = distilledData.map { it.third }.distinct()
        embeddingCache.precompute(allDistilledTexts)

        val root = GraphNode(label = rootLabel, depth = 0)

        // 2. Initial Structural Setup
        val categoryGroups = distilledData.groupBy { it.first }
        // NEW: Build a multi-value ground truth map
        val groundTruthMap = distilledData.groupBy({ it.second }, { it.first })
            .mapValues { it.value.toSet() }

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

        // --- NEW: Print Initial State ---
        log.info("Initial DAG Structure (Before Statistical Fitting)")
        ops.printHierarchy(root)
        saveDot(root, "taxonomy_initial")

        // BOOTSTRAP: Seed GMMs with 100% ground-truth data
        log.info("Bootstrap: Seeding GMMs with 100% ground-truth data...")
        ops.fitNodeRecursive(root)
        taxonomyService.notifyGraphUpdated()

        val uniqueEmbs = root.children.flatMap { gatherAllEmbeddingsInBranch(it) }.distinctBy { it.rawText }

        val originalTauFit = config.formalism.tauFit
        val originalTauReparent = config.formalism.tauReparent
        val originalTauMerge = config.formalism.tauMerge
        stabilizer.reset()

        try {
            for (i in 1..config.execution.numIterations) {
                log.info("STARTING EVOLUTION ITERATION $i")
                
                // Thermodynamic Annealing: Cool parameters dynamically
                val coolingFactor = Math.pow(config.formalism.annealingAlpha, (i - 1).toDouble())
                config.formalism.tauFit = originalTauFit / coolingFactor
                // For reparenting and merging, higher threshold is stricter. They should increase towards 1.0.
                config.formalism.tauReparent = (1.0 - (1.0 - originalTauReparent) / coolingFactor).coerceAtMost(0.999)
                config.formalism.tauMerge = (1.0 - (1.0 - originalTauMerge) / coolingFactor).coerceAtMost(0.999)

                log.info(
                    "Thermodynamic Annealing (Iter $i): " +
                    "tauFit=${"%.4f".format(java.util.Locale.US, config.formalism.tauFit)}, " +
                    "tauReparent=${"%.4f".format(java.util.Locale.US, config.formalism.tauReparent)}, " +
                    "tauMerge=${"%.4f".format(java.util.Locale.US, config.formalism.tauMerge)}"
                )
                
                // STABLE INCLUSION: Avoid "Domain Eating" by using conservative factors
                // Starting at 1.5 and tapering to 1.00 (strict freeze) for maximal boundary stability
                val taperingFactor = if (config.execution.numIterations > 1) (i - 1).toDouble() / (config.execution.numIterations - 1) else 1.0
                config.formalism.inclusionScalingFactor = 1.5 - (0.50 * taperingFactor)
                
                log.info("Inclusion Phase (Iter $i): inclusionScalingFactor set to ${"%.4f".format(java.util.Locale.US, config.formalism.inclusionScalingFactor)}")

                val iterationTime = measureTimeMillis {
                    if (uniqueEmbs.isNotEmpty()) {
                        // Phase 3: Trickle (Top-Down Restrictive Funnel Routing)
                        log.info("Phase 3: Trickling (Reassigning Queries)...")
                        ops.clearGraphQueries(root)
                        ops.reassignQueries(root, uniqueEmbs, groundTruthMap)
                        log.info("Phase 3b: Collapsing marginal nodes compared to siblings...")
                        ops.collapseMarginalNodes(root)
                        taxonomyService.notifyGraphUpdated()

                        // Phase 4: Discover (Adaptive Splitting)
                        log.info("Phase 4: Discovering emergent concepts (Splitting)...")
                        ops.splitNodesRecursive(root)
                        taxonomyService.notifyGraphUpdated()

                        // Phase 2: Refit (Recursive Union)
                        log.info("Phase 2: Refitting statistical bounds...")
                        ops.fitNodeRecursive(root)
                        taxonomyService.notifyGraphUpdated()

                        // Phase 5: Optimize (Structural Refinement)
                        log.info("Phase 5: Optimizing hierarchy (Merging & Cross-linking)...")
                        ops.optimizeHierarchy(root)
                        taxonomyService.notifyGraphUpdated()
                        
                        // Final Refit after optimization
                        ops.fitNodeRecursive(root)
                        taxonomyService.notifyGraphUpdated()
                    }
                }

                log.info("Iteration $i completed in ${iterationTime}ms.")

                // Calculate and store iteration metrics
                val iterMetrics = TaxonomyMetrics(root, groundTruthMap).generateReport()
                taxonomyService.addIterationMetrics("Iter $i", iterMetrics)

                // Phase 6: Stabilize Convergence Check
                val stabilizationResult = stabilizer.evaluateConvergence(root, i)
                if (stabilizationResult.isConverged) {
                    log.info("Early stopping triggered in iteration $i due to convergence.")
                    break
                }
            }
        } finally {
            // Restore original config values to prevent side effects
            config.formalism.tauFit = originalTauFit
            config.formalism.tauReparent = originalTauReparent
            config.formalism.tauMerge = originalTauMerge
        }

        if (!config.formalism.enableLiveLabeling) {
            log.info("Post-Pass: Live Labeling was disabled. Performing post-pass labeling on all nodes.")
            ops.generateLabelsPostPass(root)
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

        // GENERATE ARCHITECTURAL REPORT
        val finalReport = TaxonomyMetrics(root, groundTruthMap)
        finalReport.printReport()
        taxonomyService.addIterationMetrics("Final", finalReport.generateReport())
        
        return@coroutineScope root
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
        node.children.forEach { result.addAll(gatherAllEmbeddingsInBranch(it, visited)) }
        return result
    }
    }