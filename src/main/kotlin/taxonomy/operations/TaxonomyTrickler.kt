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
import kotlin.math.pow

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
data class TrickleOptions(
    val margin: Double,
    val maxAssignments: Int,
    val readOnly: Boolean = true,
    val kappaAdaptive: Boolean = true,
    val enableGtBias: Boolean = false,
    val originalCategories: List<String>? = null
)

data class TrickleResult(
    val allNodes: Map<GraphNode, Double>,
    val primary: GraphNode,
    val memberships: Map<GraphNode, Double>,
    val residualHits: List<ResidualHit> = emptyList()
) {
    fun leaves(): List<Pair<GraphNode, Double>> =
        memberships.filterKeys { it.isLeaf }
            .toList()
            .sortedByDescending { it.second }
}

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
        val margin = if (isInference) config.formalism.arenaMargin else config.formalism.constructionMargin
        val opts = TrickleOptions(
            margin = margin,
            maxAssignments = config.formalism.maxLeafAssignments,
            readOnly = isInference,
            kappaAdaptive = false,
            enableGtBias = (config.formalism.enableGtWarmStart && currentIteration <= 1),
            originalCategories = originalCategories
        )
        val res = trickle(query, root, opts)
        return RoutingResult(res.leaves().toMap(), res.residualHits)
    }

    fun trickle(
        embedding: Embedding,
        root: GraphNode,
        opts: TrickleOptions
    ): TrickleResult {
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

            val K = children.size
            val vmfScores = DoubleArray(K)

            // 1. Score each child i using its own kappa and Normalizer (Issue A)
            val siblingKappas = mutableListOf<Double>()
            for (i in children.indices) {
                val child = children[i]
                val slicedX = embedding.projectTo(child.sliceDim)
                val logNorm = StatisticsUtils.logVmfNormalizer(child.sliceDim, child.vmfKappa)
                var f = logNorm + child.vmfKappa * StatisticsUtils.dotProduct(slicedX, child.vmfMu)

                // Ground Truth bias (iter == 1 only, governed by opts)
                val isOriginal = opts.originalCategories?.any { it.equals(child.label, ignoreCase = true) } ?: false
                if (opts.enableGtBias && isOriginal) {
                    f += ln(1.0 / 0.7)
                }

                vmfScores[i] = f
                siblingKappas.add(child.vmfKappa)
            }

            val siblingKappa = siblingKappas.average().coerceIn(1.0, 100.0)

            // Temperature-scaled softmax with dynamic inverse-variance scaling (tau)
            val gamma = config.formalism.tauKappaScalingFactor.coerceIn(0.0, 1.0)
            val dynamicTau = config.formalism.routingSoftmaxTau.coerceAtLeast(0.01) * siblingKappa.pow(gamma)
            val tempScores = DoubleArray(K) { vmfScores[it] / dynamicTau }
            val maxTemp = tempScores.maxOrNull() ?: 0.0
            val sumExp = tempScores.sumOf { exp(it - maxTemp) }
            val logSumExpVal = maxTemp + ln(sumExp.coerceAtLeast(1e-300))

            val responsibilities = DoubleArray(K) { exp(tempScores[it] - logSumExpVal) }

            // 2. Residual routing check: stop walk if best child responsibility is below adaptive threshold (Issue D)
            if (config.formalism.enableResidualRouting && node.depth >= 2) {
                val bestChildResp = responsibilities.maxOrNull() ?: 0.0
                val residualC = 1.6
                val adaptiveThreshold = (residualC / K).coerceAtMost(0.80)
                if (bestChildResp < adaptiveThreshold) {
                    if (!opts.readOnly) {
                        val qId = if (embedding.queryId != -1) embedding.queryId.toString() else taxonomy.model.TextNormalizer.cleanText(embedding.rawText)
                        residualHits.add(ResidualHit(node, qId, bestChildResp))
                    }
                    return
                }
            }

            // Register the query embedding for MRL-projection lookup
            GraphNode.registerEmbedding(embedding)

            // 3. Beam: retain B = { i : (maxTemp - tempScores[i]) <= delta * siblingKappa } (mathematically equivalent to max_j log r_j - log r_i) (Issue B)
            val effectiveMargin = opts.margin * (if (opts.kappaAdaptive) siblingKappa else 1.0)
            val bestIndices = children.indices
                .filter { (maxTemp - tempScores[it]) <= effectiveMargin }

            // 4. Renormalize over the beam to eliminate path-depth bias (Issue C)
            val beamSumExp = bestIndices.sumOf { exp(tempScores[it] - maxTemp) }
            val logBeamSumExp = maxTemp + ln(beamSumExp.coerceAtLeast(1e-300))

            for (i in bestIndices) {
                val child = children[i]
                val logTransitionProb = tempScores[i] - logBeamSumExp
                val accumulatedWeight = currentLogProb + logTransitionProb
                walk(child, accumulatedWeight)
            }
        }

        walk(root, 0.0)

        // 1. Gather all candidates (both leaf candidates and fallback internal nodes)
        val candidates = mutableMapOf<GraphNode, Double>()

        // Find leaf candidates
        val leafCandidates = logProbMap
            .filterKeys { id -> nodeMap[id]?.isLeaf == true }
            .map { (id, logProb) -> nodeMap.getValue(id) to logProb }
            .toMap()
        candidates.putAll(leafCandidates)

        // Internal nodes fallback if no active children reached
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
                    candidates[node] = logProb
                }
            }
        }

        if (candidates.isEmpty()) {
            candidates[root] = 0.0
        }

        // 2. Sort candidates by joint path logProb and cap to maxAssignments
        val topCandidates = candidates.entries
            .sortedByDescending { it.value }
            .take(opts.maxAssignments)
            .map { it.key }

        // 3. For top candidates, retain their properly normalized path log-probabilities
        val results = mutableMapOf<GraphNode, Double>()
        topCandidates.forEach { node ->
            results[node] = logProbMap.getValue(node.id)
        }

        // Normalize allNodes and memberships maps to sum to 1.0 in probability space
        fun normalizeLogProbs(raw: Map<GraphNode, Double>): Map<GraphNode, Double> {
            if (raw.isEmpty()) return emptyMap()
            val maxL = raw.values.maxOrNull() ?: 0.0
            val sumE = raw.values.sumOf { exp(it - maxL) }
            val logSumExpFinal = maxL + ln(sumE.coerceAtLeast(1e-300))
            return raw.mapValues { (_, logProb) -> logProb - logSumExpFinal }
        }

        val normalizedMemberships = normalizeLogProbs(results)
        val normalizedAllNodes = normalizeLogProbs(logProbMap.mapKeys { nodeMap.getValue(it.key) })

        val primaryNode = normalizedMemberships.maxByOrNull { it.value }?.key ?: root

        return TrickleResult(
            allNodes = normalizedAllNodes,
            primary = primaryNode,
            memberships = normalizedMemberships,
            residualHits = residualHits
        )
    }
}