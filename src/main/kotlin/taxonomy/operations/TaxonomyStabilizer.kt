package org.eclipse.lmos.arc.app.taxonomy.operations

import org.eclipse.lmos.arc.app.taxonomy.GraphNode
import org.eclipse.lmos.arc.app.taxonomy.TaxonomyConfig
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.StatisticsUtils
import kotlin.math.abs

/**
 * Implements Phase 6: Stabilize (Convergence of the Mixture).
 * Measures structural Graph Edit Distance (GED) and Log-Semantic Volume changes to determine taxonomy stability.
 */
@Service
class TaxonomyStabilizer(
    private val config: TaxonomyConfig
) {
    private val log = LoggerFactory.getLogger(TaxonomyStabilizer::class.java)

    private var prevNodes: Set<String>? = null
    private var prevRelations: Set<Pair<String, String>>? = null
    private var prevVolume: Double? = null

    data class StabilizationResult(
        val ged: Int,
        val currentVolume: Double,
        val volumeDelta: Double,
        val volumeRelativeDelta: Double,
        val isConverged: Boolean
    )

    /**
     * Resets the stabilizer's tracking state for a new adaptation run.
     */
    fun reset() {
        prevNodes = null
        prevRelations = null
        prevVolume = null
    }

    /**
     * Analyzes structural and statistical changes to evaluate convergence.
     */
    fun evaluateConvergence(root: GraphNode, iteration: Int): StabilizationResult {
        // 1. Gather all current nodes and active parent-child relationships
        val currentNodes = mutableSetOf<String>()
        val currentRelations = mutableSetOf<Pair<String, String>>()
        
        fun collect(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
            if (visited.contains(node.id)) return
            visited.add(node.id)
            currentNodes.add(node.label)
            for (child in node.children) {
                currentRelations.add(node.label to child.label)
                collect(child, visited)
            }
        }
        collect(root)

        // 2. Measure Graph Edit Distance (GED) relative to the previous iteration
        val ged = if (prevNodes == null || prevRelations == null) {
            0
        } else {
            val addedNodes = currentNodes - prevNodes!!
            val removedNodes = prevNodes!! - currentNodes
            val addedRelations = currentRelations - prevRelations!!
            val removedRelations = prevRelations!! - currentRelations
            
            val d = addedNodes.size + removedNodes.size + addedRelations.size + removedRelations.size
            log.info("GED Analysis (Iter $iteration): +${addedNodes.size}/-${removedNodes.size} nodes, +${addedRelations.size}/-${removedRelations.size} relations.")
            d
        }

        // 3. Compute leaf Log-Semantic Volume Minimization
        val leafNodes = getAllNodes(root).filter { it.isLeaf && it.distribution != null }
        val currentVolume = leafNodes.sumOf { StatisticsUtils.calculateLogSemanticVolume(it.distribution!!) }
        
        val volumeDelta = if (prevVolume == null) 0.0 else abs(currentVolume - prevVolume!!)
        val volumeRelativeDelta = if (prevVolume == null || prevVolume == 0.0) 0.0 else volumeDelta / abs(prevVolume!!)

        // 4. Decide convergence
        val isFirstIteration = prevVolume == null
        val isConverged = if (isFirstIteration || !config.formalism.enableEarlyStopping) {
            false
        } else {
            ged <= config.formalism.gedThreshold && volumeDelta <= config.formalism.volumeThreshold
        }

        log.info(
            "Stabilization Monitor (Iter $iteration): Leaf Log-Volume = ${"%.4f".format(java.util.Locale.US, currentVolume)} " +
            "(Delta: ${"%.4f".format(java.util.Locale.US, volumeDelta)} / ${"%.4f%%".format(java.util.Locale.US, volumeRelativeDelta * 100.0)}), " +
            "GED = $ged (Threshold <= ${config.formalism.gedThreshold})"
        )

        if (isConverged) {
            log.info("Convergence Met: Taxonomy mixture has stabilized structurally and statistically.")
        }

        // 5. Store current state for the next check
        prevNodes = currentNodes
        prevRelations = currentRelations
        prevVolume = currentVolume

        return StabilizationResult(ged, currentVolume, volumeDelta, volumeRelativeDelta, isConverged)
    }

    private fun getAllNodes(node: GraphNode, visited: MutableSet<GraphNode> = mutableSetOf()): Set<GraphNode> {
        if (visited.contains(node)) return visited
        visited.add(node)
        node.children.forEach { getAllNodes(it, visited) }
        return visited
    }
}
