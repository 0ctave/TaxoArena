package taxonomy.operations

import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.model.GraphNode
import taxonomy.utils.StatisticsUtils
import kotlin.math.abs

/**
 * Implements Phase 6: Stabilize (Convergence of the Mixture).
 * Measures structural Graph Edit Distance (GED) and Log-Semantic Volume changes to determine taxonomy stability.
 */
@Service
class TaxonomyStabilizer(
    private val config: TaxonomyConfig
) {
    private val log = LoggerFactory.getLogger("taxonomy.Stabilizer")

    private var prevNodes: Set<String>? = null
    private var prevRelations: Set<Pair<String, String>>? = null
    private var prevVolume: Double? = null

    private var consecutiveConvergedCount = 0
    private val requiredConsecutive = 5

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
        consecutiveConvergedCount = 0
    }

    private fun minIterations(root: GraphNode): Int {
        val domainCount = root.children.size  // depth-1 nodes = domain count
        return (domainCount * 0.8).toInt().coerceAtLeast(5)
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
            currentNodes.add(node.id)
            for (child in node.children) {
                currentRelations.add(node.id to child.id)
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
        val leafNodes = getAllNodes(root).filter { it.isLeaf }
        val currentVolume = leafNodes.sumOf { StatisticsUtils.calculateLogSemanticVolume(it) }
        
        val volumeDelta = if (prevVolume == null) 0.0 else abs(currentVolume - prevVolume!!)
        val volumeRelativeDelta = if (prevVolume == null || prevVolume == 0.0) 0.0 else volumeDelta / abs(prevVolume!!)

        // 4. Decide convergence
        val isFirstIteration = prevVolume == null

        val singleIterConverged = !isFirstIteration && (ged == 0)

        if (iteration < minIterations(root)) {
            consecutiveConvergedCount = 0
            prevNodes = currentNodes
            prevRelations = currentRelations
            prevVolume = currentVolume
            return StabilizationResult(ged, currentVolume, volumeDelta, volumeRelativeDelta, false)
        }

        if (singleIterConverged) {
            consecutiveConvergedCount++
            log.info("Convergence streak: $consecutiveConvergedCount/$requiredConsecutive")
        } else {
            consecutiveConvergedCount = 0
        }

        val isConverged = config.execution.enableEarlyStopping &&
                consecutiveConvergedCount >= requiredConsecutive

        if (isConverged) log.info("Convergence Met: Taxonomy mixture has stabilized for $requiredConsecutive consecutive iterations.")

        // Update tracking state for next iteration
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

    fun countEdges(root: GraphNode): Int {
        val visited = mutableSetOf<String>()
        var edges = 0
        fun walk(node: GraphNode) {
            if (!visited.add(node.id)) return
            edges += node.children.size
            node.children.forEach { walk(it) }
        }
        walk(root)
        return edges
    }
}
