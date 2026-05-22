package org.eclipse.lmos.arc.app.taxonomy.operations

import kotlinx.coroutines.*
import org.eclipse.lmos.arc.app.taxonomy.Embedding
import org.eclipse.lmos.arc.app.taxonomy.GraphNode
import org.eclipse.lmos.arc.app.taxonomy.TaxonomyConfig
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.StatisticsUtils

/**
 * Implements Phase 2: Fit (Context-Aware Distribution Modeling).
 */
@Service
class TaxonomyFitter(
    private val config: TaxonomyConfig
) {
    private val log = LoggerFactory.getLogger(TaxonomyFitter::class.java)

    /**
     * Recursively traverses the DAG bottom-up to fit statistical models.
     */
    suspend fun fitNodeRecursive(node: GraphNode, visited: MutableSet<String> = mutableSetOf()): Unit = coroutineScope {
        if (visited.contains(node.id)) return@coroutineScope
        visited.add(node.id)

        // 1. Traverse to deepest children first (Bottom-up)
        // Parallelize children fitting
        node.children.map { child ->
            async {
                fitNodeRecursive(child, visited)
            }
        }.awaitAll()

        // 2. Fit Terminal Leaf Nodes (Multi-Centroid OAS-GMM)
        if (node.isLeaf) {
            if (node.queries.isNotEmpty()) {
                val newGmm = StatisticsUtils.computeLeafGmm(node.queries, config.formalism.maxCentroidsPerNode, config.formalism.oasShrinkage)
                
                // STABILIZATION: Apply EMA blending
                node.distribution = StatisticsUtils.stabilizeGmm(node.previousDistribution, newGmm, 0.7) // Fixed EMA for internal stability
                node.previousDistribution = node.distribution
            }
        }
        // 3. Fit Internal Parent Nodes (Recursive Union Distribution)
        else {
            // Parent distribution is strictly the UNION of its children's distributions.
            // Parent residual queries (Up) are tracked but not used to define the parent macro-boundary
            // until they are "discovered" as a new child.
            val unionGmm = StatisticsUtils.unionOfChildren(node.children, emptyList()) // Strict child union

            // SIMPLIFICATION: Merge extremely overlapping centroids to prevent linear explosion
            node.distribution = unionGmm?.let { StatisticsUtils.simplifyGmm(it, config.formalism.tauMerge) }
        }
    }
}