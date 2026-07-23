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
 * Implements Phase 3: Trickle (Top-Down Routing).
 *
 * Routes queries down the DAG with three independent, correctly-scoped criteria:
 *
 * 1. Descent-vs-residual (parameter-free): at each internal node, descend only if some
 *    child's vMF log-density beats the node's OWN component density — a parent-vs-children
 *    Bayes factor at threshold 1. If not, the sub-structure fails to explain the query and
 *    it is recorded as residual at that node. The parent's fitted concentration is the
 *    baseline, so the criterion adapts to its environment by construction.
 * 2. Per-level beam ([TaxonomyConfig.FormalismConfig.routingBeamGamma]): siblings within
 *    gamma of the best sibling's responsibility stay on the beam. Relative-to-best keeps
 *    genuine sharing (0.50/0.50) and drops negligible tails (0.90/0.05) — an absolute
 *    floor cannot distinguish the two.
 * 3. Final membership share ([TaxonomyConfig.FormalismConfig.membershipFloor]): memberships
 *    are normalized over the leaves the query actually reached; a leaf counts iff it holds
 *    at least that fraction of the query's own membership. Self-normalized, hence invariant
 *    to depth and fan-out — the previous flat product-vs-floor test made balanced structure
 *    unreachable below depth 2 and forced dominant-child wrapper churn.
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

    companion object {
        // Purely numerical fan-out guard: abandon walk paths whose absolute posterior has
        // become negligible (< 0.01%). Carries no membership semantics — those live in the
        // relative beam, the parent-gate, and the final per-query share floor.
        private val LOG_NEGLIGIBLE_PATH = ln(1e-4)
    }

    fun routeQuery(
        query: Embedding,
        root: GraphNode,
        currentIteration: Int,
        originalCategories: List<String>? = null,
        isInference: Boolean = false
    ): RoutingResult {
        // Construction and arena share the same posterior-probability floor: both should mean
        // "genuine membership" the same way. maxLeafAssignments is an arena-only judge-call-cost
        // bound: construction-time membership is unbounded, exactly as documented on the config —
        // the membershipFloor and the cumulative-path floor already bound it naturally (a leaf
        // needs >= floor path probability, so at most ~1/floor leaves per query). Applying the
        // cap during construction ranked leaves by JOINT path probability, which mechanically
        // penalises depth (a child's path prob is its parent's x a transition <= 1), so the
        // moment a leaf split, its children fell out of most queries' top-k and starved —
        // soft-membership siblings with genuine query concentration died to rank eviction.
        val opts = TrickleOptions(
            membershipFloor = config.formalism.membershipFloor,
            maxAssignments = if (isInference) config.formalism.maxLeafAssignments else Int.MAX_VALUE,
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

            // 2. Descent-vs-residual gate: parent-vs-children Bayes factor at threshold 1,
            // evaluated in the shared-concentration limit — i.e. on DIRECTIONS only.
            // Descend iff some child's mean direction matches the query at least as well as
            // this node's own: max_c <mu_c, x> >= <mu_p, x>. Comparing full densities here
            // is systematically biased toward the parent: the Hornik-Grün shrinkage factor
            // (n-1)/(n+d-2) scales with n, so a parent fitted on 4x the queries carries a
            // structurally larger kappa than its children, and the bias (~tens of nats)
            // dwarfs any honest evidence difference — observed as 56% of the corpus
            // residualizing at the anchors. Under a locally-shared kappa the density
            // comparison reduces exactly to the direction comparison, which is immune to
            // that estimation artifact, still parameter-free, and keeps the honest residual
            // semantics: queries at the parent's own center that no child specializes in
            // stay at the parent.
            val maxScore = vmfScores.maxOrNull() ?: 0.0
            if (node.vmfMu.isNotEmpty()) {
                val parentX = embedding.projectTo(node.vmfMu.size)
                val parentDot = StatisticsUtils.dotProduct(parentX, node.vmfMu)
                var bestChildDot = Double.NEGATIVE_INFINITY
                for (child in children) {
                    if (child.vmfMu.isEmpty()) continue
                    val childX = embedding.projectTo(child.vmfMu.size)
                    val dot = StatisticsUtils.dotProduct(childX, child.vmfMu)
                    if (dot > bestChildDot) bestChildDot = dot
                }
                if (bestChildDot < parentDot - config.formalism.descentMargin) {
                    if (config.formalism.enableResidualRouting && node.depth >= 1 && !opts.readOnly) {
                        val sumExpAll = vmfScores.sumOf { exp(it - maxScore) }
                        val bestChildResp = 1.0 / sumExpAll.coerceAtLeast(1.0)
                        val qId = if (embedding.queryId != -1) embedding.queryId.toString() else taxonomy.model.TextNormalizer.cleanText(embedding.rawText)
                        residualHits.add(ResidualHit(node, qId, bestChildResp))
                    }
                    return
                }
            }

            // 3. Per-level relative beam: a child stays on the beam iff its responsibility is
            // within gamma of the BEST sibling's (equivalently, its log-density is within
            // -ln(gamma) nats of the best). Relative-to-best is scale-free and adapts to the
            // realized competition: genuine 0.50/0.50 sharing keeps both children, 0.90/0.05
            // drops the tail. The argmax child always passes, so the beam is never empty.
            val lnGamma = ln(config.formalism.routingBeamGamma.coerceIn(1e-6, 1.0))
            val bestIndices = children.indices.filter { vmfScores[it] >= maxScore + lnGamma }

            // Register the query embedding for MRL-projection lookup
            GraphNode.registerEmbedding(embedding)

            // 4. Renormalize over the admitted set so per-level probabilities sum to 1 (avoids
            // path-depth bias from carrying the excluded tail's mass down the tree).
            val beamSumExp = bestIndices.sumOf { exp(vmfScores[it] - maxScore) }
            val logBeamSumExp = maxScore + ln(beamSumExp.coerceAtLeast(1e-300))

            for (i in bestIndices) {
                val child = children[i]
                val logTransitionProb = vmfScores[i] - logBeamSumExp
                val accumulatedWeight = currentLogProb + logTransitionProb
                // Purely numerical guard against combinatorial fan-out: abandon paths whose
                // absolute posterior is negligible. Membership semantics live in the final
                // per-query share floor (below), NOT here — the old flat product-vs-floor
                // test made balanced structure unreachable below depth 2 and forced the
                // dominant-child wrapper churn.
                if (accumulatedWeight >= LOG_NEGLIGIBLE_PATH) {
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

        // Normalize allNodes and memberships maps to sum to 1.0 in probability space
        fun normalizeLogProbs(raw: Map<GraphNode, Double>): Map<GraphNode, Double> {
            if (raw.isEmpty()) return emptyMap()
            val maxL = raw.values.maxOrNull() ?: 0.0
            val sumE = raw.values.sumOf { exp(it - maxL) }
            val logSumExpFinal = maxL + ln(sumE.coerceAtLeast(1e-300))
            return raw.mapValues { (_, logProb) -> logProb - logSumExpFinal }
        }

        // 2. Final membership: normalize over the candidates this query actually reached,
        // then keep destinations holding at least membershipFloor of THIS query's own
        // membership. Self-normalized, so the floor's meaning ("at least this share of the
        // query") is invariant to tree depth and fan-out. If nothing clears the share floor
        // (membership genuinely diffuse over many leaves), the single best destination is
        // kept — trimming negligible tails is this floor's job, declaring residuals is the
        // parent-gate's. maxAssignments then caps arena-time judge cost (construction is
        // unbounded).
        val normalizedCandidates = normalizeLogProbs(candidates)
        val logShareFloor = ln(opts.membershipFloor.coerceAtLeast(1e-300))
        val admitted = normalizedCandidates.filterValues { it >= logShareFloor }
            .ifEmpty {
                normalizedCandidates.maxByOrNull { it.value }
                    ?.let { mapOf(it.key to it.value) } ?: emptyMap()
            }

        // 3. Cap to maxAssignments by share, then renormalize the survivors
        val results = admitted.entries
            .sortedByDescending { it.value }
            .take(opts.maxAssignments)
            .associate { it.key to it.value }

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