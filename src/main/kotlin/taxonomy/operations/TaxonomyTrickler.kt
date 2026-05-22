package org.eclipse.lmos.arc.app.taxonomy.operations

import org.eclipse.lmos.arc.app.taxonomy.Embedding
import org.eclipse.lmos.arc.app.taxonomy.GraphNode
import org.eclipse.lmos.arc.app.taxonomy.TaxonomyConfig
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.StatisticsUtils

/**
 * Implements Phase 3: Trickle (Top-Down Restrictive Routing).
 * Handles pushing queries down the DAG evaluating against bounded probability spaces.
 */
@Service
class TaxonomyTrickler(
    private val config: TaxonomyConfig
) {
    private val log = LoggerFactory.getLogger(TaxonomyTrickler::class.java)

    fun trickleQuery(
        query: Embedding,
        currentNode: GraphNode,
        results: MutableMap<GraphNode, Double>,
        visited: MutableSet<String> = mutableSetOf(),
        previousAssignments: Set<String> = emptySet(),
        originalCategories: Set<String>? = null // NEW: Multi-domain Ground Truth Anchors
    ) {
        if (visited.contains(currentNode.id)) return
        visited.add(currentNode.id)

        // MRL FUNNEL RETRIEVAL: Progressive dimension unrolling based on depth
        val dimLimit = config.formalism.mrlLimits[currentNode.depth] ?: query.dimensions

        // 1. EVALUATE INCLUSION (Guided by Restrictive Funnel)
        currentNode.distribution?.let { gmm ->
            val minD2 = StatisticsUtils.minMahalanobisDistance(query, gmm, dimLimit)
            val scaledD2 = minD2 / config.formalism.inclusionScalingFactor
            val alpha = config.formalism.tauFit * Math.exp(-config.formalism.depthDecayLambda * currentNode.depth)
            
            val statisticalThreshold = StatisticsUtils.chiSquareThreshold(dimLimit, alpha)
            
            val isImmune = originalCategories?.any { it.equals(currentNode.label, ignoreCase = true) } ?: false
            
            // INFERENCE BOOST: Slightly relax the threshold when originalCategories is null (inference mode)
            // to ensure multi-domain queries are not prematurely pruned.
            val thresholdMultiplier = if (originalCategories == null) 1.5 else 1.0
            
            val inclusive = if (isImmune || currentNode.depth == 0) {
                true 
            } else {
                val ok = scaledD2 <= (statisticalThreshold * thresholdMultiplier) || (currentNode.isLeaf && minD2 <= gmm.empiricalThreshold * 5.0)
                if (!ok && originalCategories == null) {
                    log.debug("Rejecting [${currentNode.label}] D2=${"%.4f".format(scaledD2)} > Thr=${"%.4f".format(statisticalThreshold * thresholdMultiplier)}")
                }
                ok
            }

            log.trace("Trickle [${currentNode.label}] depth=${currentNode.depth} dim=$dimLimit: D2=${"%.4f".format(scaledD2)} Thr=${"%.4f".format(statisticalThreshold)} Inc=$inclusive")

            if (!inclusive) { 
                return
            }

            // 2. LEAF ASSIGNMENT
            if (currentNode.isLeaf) {
                log.trace("  -> Matched Leaf: ${currentNode.label}")
                results[currentNode] = scaledD2
                return
            }
        }


        // 3. COMPETITIVE ROUTING (Internal Nodes)
        val initialResultsSize = results.size
        
        val viableChildren = currentNode.children.mapNotNull { child ->
            val childGmm = child.distribution ?: return@mapNotNull null
            val childDimLimit = config.formalism.mrlLimits[child.depth] ?: query.dimensions
            
            val d2 = StatisticsUtils.minMahalanobisDistance(query, childGmm, childDimLimit)
            val scaledD2 = d2 / config.formalism.inclusionScalingFactor
            
            val alpha = config.formalism.tauFit * Math.exp(-config.formalism.depthDecayLambda * child.depth)
            val statisticalThreshold = StatisticsUtils.chiSquareThreshold(childDimLimit, alpha)
            
            val isImmune = originalCategories?.any { it.equals(child.label, ignoreCase = true) } ?: false
            val inclusive = if (isImmune) {
                true 
            } else if (child.isLeaf) {
                d2 <= childGmm.empiricalThreshold * 5.0 || scaledD2 <= statisticalThreshold
            } else {
                scaledD2 <= statisticalThreshold
            }
            
            if (inclusive) {
                val logLikelihood = StatisticsUtils.calculateLogLikelihood(childGmm, listOf(query))
                log.trace("    Child [${child.label}] inclusive with LL=${"%.2f".format(logLikelihood)}")
                child to logLikelihood
            } else null
        }.sortedByDescending { it.second } 

        if (viableChildren.isNotEmpty()) {
            // APPLY BRANCHING LOGIC:
            // If trickleAllViable is true, recurse into everything.
            // Otherwise, take only the top 'maxTrickleBranches' (already sorted by Log-Likelihood).
            val branchesToExplore = if (config.formalism.trickleAllViable) {
                viableChildren
            } else {
                viableChildren.take(config.formalism.maxTrickleBranches)
            }

            for ( (child, _) in branchesToExplore ) {
                trickleQuery(query, child, results, visited, previousAssignments, originalCategories)
            }
        }

        val matchedChild = results.size > initialResultsSize

        // 4. OUTLIER RETENTION (Parent Residuals)
        if (!matchedChild && currentNode.distribution != null) {
            val d2 = StatisticsUtils.minMahalanobisDistance(query, currentNode.distribution!!)
            results[currentNode] = d2
        }
    }
    }