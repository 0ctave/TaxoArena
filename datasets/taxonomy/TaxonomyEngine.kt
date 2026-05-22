package org.eclipse.lmos.arc.app.taxonomy

import org.eclipse.lmos.arc.app.taxonomy.operations.GraphOperations
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import java.io.File
import kotlin.math.pow

@Service
class TaxonomyEngine(
    private val config: TaxonomyConfig,
    private val cache: EmbeddingCache,
    private val ops: GraphOperations
) {
    private val log = LoggerFactory.getLogger(TaxonomyEngine::class.java)

    suspend fun adaptTaxonomy(superRootLabel: String, dataset: Map<String, List<String>>): GraphNode {
        log.info("=== [START] Mathematical Domain Inference Engine ===")
        val universalQueries = dataset.values.flatten().distinct()
        cache.precompute(universalQueries)

        val rootNode = GraphNode(label = superRootLabel)
        dataset.forEach { (subject, questions) ->
            val node = GraphNode(label = subject)
            node.queries.addAll(questions)
            rootNode.addChild(node)
        }
        ops.recalculateMetrics(rootNode.getAllNodes())

        var epoch = 1
        var deltaG = Int.MAX_VALUE

        while (deltaG > 0 && epoch <= 10) {
            log.info("--- [Epoch $epoch] Commencing Lifecycle ---")

            val temp = config.annealingAlpha.pow(-epoch.toFloat())
            val cTauFit = config.tauFit + ((1f - config.tauFit) * (1f - temp))
            val cTauReparent = config.tauReparent + ((1f - config.tauReparent) * (1f - temp))
            val cTauMerge = config.tauMerge + ((1f - config.tauMerge) * (1f - temp))

            // RE-IMPLEMENTED: CONDITIONAL CLEARING LOGIC
            if (epoch == 1 || deltaG > config.perturbFlushThreshold) {
                ops.executeClearing(rootNode)
            } else {
                log.info("[Op 5: Clearing] Skipped. Graph delta ($deltaG) is below perturbation threshold.")
            }

            // Step 2: The Great Routing
            ops.executeFitting(rootNode, universalQueries, cTauFit)
            exportDagToDot(rootNode, "taxonomy_epoch_${epoch}_fitting.dot")

            // Step 3: Metric Recalibration
            ops.recalculateMetrics(rootNode.getAllNodes())

            // Step 4: Consolidation (Merging)
            val merges = ops.executeMerging(rootNode, cTauMerge)

            // Step 5: Topology Optimization (Reparenting)
            val reparents = ops.executeReparenting(rootNode, cTauReparent)

            // Step 6: Expansion (Splitting)
            val splits = ops.executeSplitting(rootNode, temp)

            deltaG = merges + reparents + splits
            log.info("--- [Epoch $epoch] Resolved. ΔG = $deltaG (Merges: $merges, Reparents: $reparents, Splits: $splits) ---")
            epoch++
        }
        exportDagToDot(rootNode, "taxonomy_final_stable.dot")
        return rootNode
    }

    private fun exportDagToDot(root: GraphNode, filename: String) {
        val file = File(filename)
        file.printWriter().use { out ->
            out.println("digraph Taxonomy {\n  rankdir=TB; node [shape=box, style=\"rounded,filled\"];")
            val v = mutableSetOf<String>()
            val e = mutableSetOf<Pair<String, String>>()

            fun tr(n: GraphNode) {
                // FIX: Immediate guard prevents StackOverflowError from highly cross-linked graphs
                if (!v.add(n.id)) return

                val safeLabel = n.label.replace("\"", "\\\"")
                out.println("  \"${n.id}\" [label=\"$safeLabel\\n[${n.queries.size}]\", fillcolor=\"#EFF6FF\"];")

                n.children.forEach { c ->
                    if (e.add(n.id to c.id)) {
                        out.println("  \"${n.id}\" -> \"${c.id}\";")
                    }
                    tr(c)
                }
            }

            tr(root)
            out.println("}")
        }
    }
}