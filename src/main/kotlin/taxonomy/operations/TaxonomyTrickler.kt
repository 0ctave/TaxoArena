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
 *
 * Routes queries down the DAG using each child's own vMF posterior responsibility
 * (softmax of its log-density at temperature=1 — the true Bayesian mixture posterior,
 * no artificial softening). A child is a genuine membership destination iff its
 * responsibility clears [TaxonomyConfig.FormalismConfig.membershipFloor]; the same floor
 * bounds cumulative path probability (stop descending once a path's product of
 * per-level responsibilities decays below it) and triggers residual routing (no child
 * clears the floor -> this position is residual). One probability-scale parameter
 * governs all three, and it means the same thing everywhere in the tree regardless of
 * local vMF concentration — unlike the previous nats-margin-times-kappa scheme.
 */
data class RoutingResult(
    val leaves: Map<GraphNode, Double>,
    val residualHits: List<ResidualHit>,
    val trace: List<String> = emptyList(),
    // Best node the trickle actually converged to, leaf or not. When `leaves` is empty this is
    // guaranteed non-leaf — callers should attribute the query to this node's residualQueries
    // rather than hard-assigning it to root, or the C3 invariant (internal node with hard
    // queries but no residualQueries) gets violated by construction.
    val primary: GraphNode
)

data class ResidualHit(
    val node: GraphNode,
    val questionId: String,
    val bestChildScore: Double
)

@Service
data class TrickleOptions(
    val membershipFloor: Double,
    val maxAssignments: Int,
    val readOnly: Boolean = true,
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
        // Construction and arena share the same posterior-probability floor: both should mean
        // "genuine membership" the same way. maxLeafAssignments (arena-only, a judge-call-cost
        // bound) is enforced downstream in TaxonomyArenaService, not here.
        val opts = TrickleOptions(
            membershipFloor = config.formalism.membershipFloor,
            maxAssignments = config.formalism.maxLeafAssignments,
            readOnly = isInference,
            enableGtBias = (config.formalism.enableGtWarmStart && currentIteration <= 1),
            originalCategories = originalCategories
        )
        val res = trickle(query, root, opts)
        return RoutingResult(res.leaves().toMap(), res.residualHits, primary = res.primary)
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

            // 1. Score each child with its own vMF log-density (its own kappa and normalizer —
            // a component with tighter concentration or a better directional match scores higher
            // on its own terms, not relative to a shared/averaged sibling kappa).
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
            }

            // 2. True Bayesian posterior responsibility — softmax of the raw vMF log-densities,
            // temperature=1, no artificial softening. The fitted kappa of each child already
            // determines how sharp or soft its boundary should be; no separate calibration knob
            // (routingSoftmaxTau / tauKappaScalingFactor) is needed on top of that.
            val maxScore = vmfScores.maxOrNull() ?: 0.0
            val sumExp = vmfScores.sumOf { exp(it - maxScore) }
            val logSumExpVal = maxScore + ln(sumExp.coerceAtLeast(1e-300))
            val responsibilities = DoubleArray(K) { exp(vmfScores[it] - logSumExpVal) }

            // 3. Membership: a child is a genuine destination iff its responsibility clears
            // membershipFloor — a probability, so this means the same thing everywhere in the
            // tree regardless of local kappa. If nothing clears it, this position is residual by
            // construction (no separate residual threshold needed).
            val bestIndices = children.indices.filter { responsibilities[it] >= opts.membershipFloor }

            if (bestIndices.isEmpty()) {
                if (config.formalism.enableResidualRouting && node.depth >= 2 && !opts.readOnly) {
                    val bestChildResp = responsibilities.maxOrNull() ?: 0.0
                    val qId = if (embedding.queryId != -1) embedding.queryId.toString() else taxonomy.model.TextNormalizer.cleanText(embedding.rawText)
                    residualHits.add(ResidualHit(node, qId, bestChildResp))
                }
                return
            }

            // Register the query embedding for MRL-projection lookup
            GraphNode.registerEmbedding(embedding)

            // 4. Renormalize over the admitted set so per-level probabilities sum to 1 (avoids
            // path-depth bias from carrying the excluded tail's mass down the tree).
            val beamSumExp = bestIndices.sumOf { exp(vmfScores[it] - maxScore) }
            val logBeamSumExp = maxScore + ln(beamSumExp.coerceAtLeast(1e-300))

            val logFloor = ln(opts.membershipFloor.coerceAtLeast(1e-300))
            for (i in bestIndices) {
                val child = children[i]
                val logTransitionProb = vmfScores[i] - logBeamSumExp
                val accumulatedWeight = currentLogProb + logTransitionProb
                // Cumulative-path pruning: stop descending once this path's own probability from
                // the root (not just this level's) has decayed below the floor. A numerical
                // safety valve against fan-out at deep trees, not a semantic cap — it discards
                // only what's already provably negligible.
                if (accumulatedWeight >= logFloor) {
                    walk(child, accumulatedWeight)
                }
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