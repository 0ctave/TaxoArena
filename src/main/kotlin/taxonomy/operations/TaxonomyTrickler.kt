package taxonomy.operations

import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.projectTo
import taxonomy.utils.StatisticsUtils
import kotlin.math.exp
import kotlin.math.ln

/**
 * Implements Phase 3: Trickle (Top-Down Restrictive Routing).
 * Routes queries down the DAG using log-space temperature-scaled softmax,
 * then prunes results to within [assignmentMargin] nats of the best leaf.
 */
data class RoutingResult(
    val leaves: Map<GraphNode, Double>,
    val residualHits: List<ResidualHit>,
    val trace: List<String> = emptyList()
)

data class ResidualHit(
    val node: GraphNode,
    val questionId: String,
    val bestChildScore: Double
)

@Service
class TaxonomyTrickler(
    private val config: TaxonomyConfig
) {
    private val log = LoggerFactory.getLogger("taxonomy.Trickler")

    fun routeQuery(
        query: Embedding,
        root: GraphNode,
        currentIteration: Int,
        originalCategories: List<String>? = null,
        isInference: Boolean = false
        ): RoutingResult {
        val logProbMap = mutableMapOf<String, Double>()
        val nodeMap = mutableMapOf<String, GraphNode>()
        val residualHits = mutableListOf<ResidualHit>()

        fun logSumExp(a: Double, b: Double): Double {
            val maxVal = maxOf(a, b)
            return maxVal + ln(exp(a - maxVal) + exp(b - maxVal))
        }

        fun walk(node: GraphNode, currentLogProb: Double) {
            nodeMap[node.id] = node
            val existing = logProbMap[node.id]
            logProbMap[node.id] = if (existing == null) currentLogProb else logSumExp(existing, currentLogProb)

            if (node.isLeaf) return

            val children = if (config.formalism.enableBridging) {
                (node.children + node.crossLinkChildren).toList()
            } else {
                node.children.toList()
            }
            if (children.isEmpty()) return

            val scores = DoubleArray(children.size)
            val gtBiasActive = currentIteration <= 1

            var kappaSum = 0.0
            for (c in children) kappaSum += c.vmfKappa
            val siblingKappa = (kappaSum / children.size.coerceAtLeast(1)).coerceIn(1.0, 100.0)

            val sharedLogNorm = StatisticsUtils.logVmfNormalizer(children[0].sliceDim, siblingKappa)

            for (i in children.indices) {
                val child = children[i]
                val slicedX = query.projectTo(child.sliceDim)
                var f = sharedLogNorm + siblingKappa * StatisticsUtils.dotProduct(slicedX, child.vmfMu)

                // Ground Truth bias (iter == 1 only)
                val isOriginal = originalCategories?.any { it.equals(child.label, ignoreCase = true) } ?: false
                if (gtBiasActive && isOriginal) {
                    f += ln(1.0 / 0.7)
                }

                scores[i] = f
            }

            // Temperature-scaled softmax
            val tau = config.formalism.routingSoftmaxTau.coerceAtLeast(0.01)
            val tempScores = DoubleArray(scores.size) { scores[it] / tau }
            val maxTemp = tempScores.maxOrNull() ?: 0.0
            val sumExp = tempScores.sumOf { exp(it - maxTemp) }
            val logSumExpVal = maxTemp + ln(sumExp.coerceAtLeast(1e-300))

            val logSoftmax = DoubleArray(scores.size) { tempScores[it] - logSumExpVal }

            val K = children.size
            val laplaceEps = 0.05 / K
            val rawProbs = DoubleArray(K) { exp(logSoftmax[it]) }

            // pre-smoothing best-child responsibility
            val bestChildResp = rawProbs.maxOrNull() ?: 0.0
            val baseTauAtDepth = when (node.depth) {
                0, 1 -> 0.999
                2 -> 0.80
                else -> config.formalism.tauFunnelFloor.coerceAtMost(0.80)
            }
            val adaptiveTau = (baseTauAtDepth * (2.0 / K)).coerceAtMost(baseTauAtDepth)
            if (config.formalism.enableResidualRouting && node.depth >= 2 && bestChildResp < adaptiveTau) {
                val qId = if (query.queryId != -1) query.queryId.toString() else taxonomy.model.TextNormalizer.cleanText(query.rawText)
                residualHits.add(ResidualHit(node, qId, bestChildResp))
            }

            val smoothedProbs = DoubleArray(K) { (rawProbs[it] + laplaceEps) / (1.0 + K * laplaceEps) }
            val logSmoothed = DoubleArray(K) { ln(smoothedProbs[it].coerceAtLeast(1e-300)) }

            // Register the query embedding for MRL-projection lookup
            GraphNode.registerEmbedding(query)

            val maxLogSoftmax = logSoftmax.maxOrNull() ?: 0.0
            val bestIndices = children.indices
                .filter { (maxLogSoftmax - logSoftmax[it]) <= config.formalism.deltaAssign }

            for (i in bestIndices) {
                val child = children[i]
                val transitionProb = smoothedProbs[i]
                val accumulatedWeight = currentLogProb + ln(transitionProb.coerceAtLeast(1e-300))
                walk(child, accumulatedWeight)
            }
        }

        walk(root, 0.0)


        // --- assignmentMargin filter ---
        val leafCandidates = logProbMap
            .filterKeys { id -> nodeMap[id]?.isLeaf == true }
            .map { (id, logProb) -> nodeMap.getValue(id) to logProb }
            .toMap()

        val bestLeafLogProb = leafCandidates.values.maxOrNull() ?: Double.NEGATIVE_INFINITY

        val results = mutableMapOf<GraphNode, Double>()
        val qualifiedLeaves = leafCandidates.entries
            .filter { (leaf, logProb) ->
                val parent = leaf.parents.find { it.id == leaf.treeParentId } ?: leaf.parents.firstOrNull()
                val siblingKappaEffective = parent?.let { p ->
                    val activeChildren = p.children
                    if (activeChildren.isNotEmpty()) activeChildren.map { it.vmfKappa }.average() else null
                }?.coerceIn(1.0, 100.0) ?: leaf.vmfKappa.coerceIn(1.0, 100.0)

                val tauEffective = config.formalism.leafAcceptanceScale.coerceAtLeast(0.01)
                val marginNats = config.formalism.assignmentCosineGap * (siblingKappaEffective / tauEffective)
                (bestLeafLogProb - logProb) <= marginNats
            }
            .sortedByDescending { it.value }
            .take(config.formalism.maxLeafAssignments)

        qualifiedLeaves.forEach { (leaf, logProb) ->
            results[leaf] = logProb
        }

        for ((nodeId, logProb) in logProbMap) {
            val node = nodeMap[nodeId] ?: continue
            if (node.isBridge) continue
            if (!node.isLeaf) {
                val activeChildren = if (config.formalism.enableBridging) {
                    node.children + node.crossLinkChildren
                } else {
                    node.children
                }
                if (!activeChildren.any { logProbMap.containsKey(it.id) }) {
                    results[node] = logProb
                }
            }
        }

        if (results.isEmpty()) {
            results[root] = 0.0
        }

        // Normalize to log-probabilities that sum to 1
        val maxLog = results.values.maxOrNull() ?: 0.0
        val sumExpVal = results.values.sumOf { exp(it - maxLog) }
        val logSumExpFinal = maxLog + ln(sumExpVal.coerceAtLeast(1e-300))

        val leavesMap = results.mapValues { (_, logProb) ->
            logProb - logSumExpFinal
        }

        return RoutingResult(leavesMap, residualHits)
    }
}