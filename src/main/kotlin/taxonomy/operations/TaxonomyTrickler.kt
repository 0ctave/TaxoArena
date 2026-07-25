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
    fun leaves(enableResidual: Boolean = false): List<Pair<GraphNode, Double>> =
        memberships.filterKeys { it.isLeaf || enableResidual }
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
        // Genuinely negligible, not a selection threshold. At the old value of 1e-4 this was
        // doing real work: TricklerRouterEquivalenceTest showed the topological router reaching
        // nodes the enumerating router never did, because a node's SUMMED posterior cleared
        // 1e-4 while no individual path to it did. Per-path and per-node cutoffs are structurally
        // different rules, so no value makes them agree while the cutoff binds — the two coincide
        // only once it prunes nothing, which is what a truly negligible constant buys. The old
        // value was tuned against an exponential traversal that needed the pruning to terminate;
        // the O(V+E) dynamic program does not, so the guard reverts to its stated purpose of
        // dropping arithmetically irrelevant mass. Routing breadth increases as a result.
        private val LOG_NEGLIGIBLE_PATH = ln(1e-30)
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
        val enableResidual = config.formalism.enableResidualRouting
        return RoutingResult(res.leaves(enableResidual).toMap(), res.residualHits, primary = res.primary)
    }

    /** Children of a node, the beam-admitted subset, and the renormalised log-transitions. */
    internal class ChildTransitions(
        val children: List<GraphNode>,
        val bestIndices: List<Int>,
        val logTransitions: DoubleArray
    )

    /**
     * Per-node scoring, Jensen-tight descent gate and per-level beam — everything about a step
     * except which node we arrived from and with how much mass.
     *
     * Extracted so the production topological router and [trickleByPathEnumeration] provably
     * share it. The differential test between the two only means something if the traversals
     * are the sole difference; a hand-copied reference could drift and silently pass.
     *
     * Returns null when the walk stops here (no children, or the descent gate fired), in which
     * case [onResidual] has been invoked if residual routing is on and the walk is not readOnly.
     */
    internal fun childTransitions(
        node: GraphNode,
        embedding: Embedding,
        opts: TrickleOptions,
        onResidual: (GraphNode, String, Double) -> Unit
    ): ChildTransitions? {
        val children = if (config.formalism.enableBridging) {
            (node.children + node.crossLinkChildren).toList()
        } else {
            node.children.toList()
        }
        if (children.isEmpty()) return null

        val K = children.size
        val vmfScores = DoubleArray(K)

        // 1. Score each child with its own vMF log-density (its own kappa and normalizer —
        // a component with tighter concentration or a better directional match scores higher
        // on its own terms, not relative to a shared/averaged sibling kappa).
        val meanKappa = children.map { it.vmfKappa }.average().coerceAtLeast(1e-9)
        val dots = DoubleArray(K)
        for (i in children.indices) {
            val child = children[i]
            val slicedX = embedding.projectTo(child.sliceDim)
            dots[i] = StatisticsUtils.dotProduct(slicedX, child.vmfMu)
            var f = meanKappa * dots[i]

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
        // this node's own: max_c <mu_c, x> >= \bar{r}_p <mu_p, x>.
        val maxScore = vmfScores.maxOrNull() ?: 0.0
        val maxDot = dots.maxOrNull() ?: 0.0
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
            // descentMargin is slack below the Jensen-tight bar: 0.0 = exact bound,
            // higher admits queries whose best child is slightly worse than the
            // children's weighted-mean alignment (fewer residuals, softer leaves).
            val descentBar = (node.childCentroidShrinkage - config.formalism.descentMargin).coerceAtLeast(0.0)
            if (bestChildDot < descentBar * parentDot) {
                if (config.formalism.enableResidualRouting && node.depth >= 1 && !opts.readOnly) {
                    val sumExpAll = vmfScores.sumOf { exp(it - maxScore) }
                    val bestChildResp = 1.0 / sumExpAll.coerceAtLeast(1.0)
                    val qId = if (embedding.queryId != -1) embedding.queryId.toString() else embedding.rawText
                    onResidual(node, qId, bestChildResp)
                }
                return null
            }
        }

        // 3. Per-level relative beam: a child stays on the beam iff its cosine distance
        // is within routingBeamGamma of the BEST sibling's dot product.
        val bestIndices = children.indices.filter { dots[it] >= maxDot - config.formalism.routingBeamGamma }

        if (!opts.readOnly && config.formalism.enableResidualRouting) {
            val qId = if (embedding.queryId != -1) embedding.queryId.toString() else embedding.rawText
            for (i in children.indices) {
                if (dots[i] < maxDot) {
                    val margin = maxDot - dots[i]
                    val child = children[i]
                    synchronized(child.nearMisses) {
                        if (child.nearMisses.size < 200) {
                            child.nearMisses[qId] = margin
                        } else {
                            val worst = child.nearMisses.maxByOrNull { it.value }
                            if (worst != null && margin < worst.value) {
                                child.nearMisses.remove(worst.key)
                                child.nearMisses[qId] = margin
                            }
                        }
                    }
                }
            }
        }

        // Register the query embedding for MRL-projection lookup
        GraphNode.registerEmbedding(embedding)

        // 4. Renormalize over the admitted set so per-level probabilities sum to 1 (avoids
        // path-depth bias from carrying the excluded tail's mass down the tree).
        val beamSumExp = bestIndices.sumOf { exp(vmfScores[it] - maxScore) }
        val logBeamSumExp = maxScore + ln(beamSumExp.coerceAtLeast(1e-300))

        val logTransitions = DoubleArray(K)
        for (i in bestIndices) logTransitions[i] = vmfScores[i] - logBeamSumExp

        return ChildTransitions(children, bestIndices, logTransitions)
    }

    /**
     * REFERENCE IMPLEMENTATION — the pre-rewrite path-enumerating walk, kept solely so the
     * topological router can be proved equivalent on real graphs. Not used in production: it is
     * exponential in the number of cross-links, which is exactly why [trickle] replaced it.
     *
     * The one deliberate difference is the cutoff. This applies LOG_NEGLIGIBLE_PATH per PATH,
     * as the original did; [trickle] applies it to a node's summed posterior. The two coincide
     * only when the cutoff binds on neither, which is the property the differential test pins
     * down.
     */
    internal fun trickleByPathEnumeration(
        embedding: Embedding,
        root: GraphNode,
        opts: TrickleOptions
    ): Map<String, Double> {
        val logProbMap = mutableMapOf<String, Double>()

        fun logSumExp(a: Double, b: Double): Double {
            val maxVal = maxOf(a, b)
            return maxVal + ln(exp(a - maxVal) + exp(b - maxVal))
        }

        val pathVisited = mutableSetOf<String>()
        fun walk(node: GraphNode, currentLogProb: Double) {
            if (!pathVisited.add(node.id)) return
            val existing = logProbMap[node.id]
            logProbMap[node.id] = if (existing == null) currentLogProb else logSumExp(existing, currentLogProb)

            if (node.isLeaf) {
                pathVisited.remove(node.id)
                return
            }
            val step = childTransitions(node, embedding, opts) { _, _, _ -> }
            if (step == null) {
                pathVisited.remove(node.id)
                return
            }
            for (i in step.bestIndices) {
                val accumulatedWeight = currentLogProb + step.logTransitions[i]
                if (accumulatedWeight >= LOG_NEGLIGIBLE_PATH) {
                    walk(step.children[i], accumulatedWeight)
                }
            }
            pathVisited.remove(node.id)
        }
        walk(root, 0.0)
        return logProbMap
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

        // Topological (reverse-postorder) processing of the reachable subgraph.
        //
        // This was previously a DFS with backtracking — `pathVisited` was removed again on
        // exit — so it enumerated every distinct root-to-node PATH and re-walked a node's
        // entire subtree once per path reaching it. On a tree that is linear (paths = nodes),
        // but every accepted cross-link multiplies the number of paths into the target's whole
        // subtree, so routing cost grew combinatorially in the number of bridges. Measured:
        // per-proposal cost rose 10x (0.30s -> 2.92s) as accepted cross-links went 22 -> 161,
        // which dominated total runtime and got worse the better the polyhierarchy got.
        //
        // The quantity being computed is a logSumExp of path masses over an acyclic graph, so
        // it is a dynamic program: visit each node only after all of its predecessors, and push
        // mass along each EDGE exactly once. The value is unchanged because addition distributes
        // over logSumExp — logSumExp(w1,w2) + t == logSumExp(w1+t, w2+t) — so aggregating at the
        // parent and descending once is identical to descending once per path. O(V+E) instead of
        // O(paths). The per-node scoring work below is untouched; it simply runs once per node.
        val order = ArrayList<GraphNode>()
        run {
            // null = unseen, 0 = on the current stack, 1 = finished. Re-entering a node still on
            // the stack is a back edge; the cross-link guards are supposed to keep the graph
            // acyclic, but ignoring such an edge degrades gracefully instead of overflowing if
            // one ever slips through.
            val state = HashMap<String, Int>()
            fun visit(n: GraphNode) {
                if (state[n.id] != null) return
                state[n.id] = 0
                val kids = if (config.formalism.enableBridging) {
                    n.children + n.crossLinkChildren
                } else {
                    n.children
                }
                for (c in kids) visit(c)
                state[n.id] = 1
                order.add(n)
            }
            visit(root)
        }
        order.reverse()

        // Log-mass accumulated at each node; final by the time topological order reaches it.
        val acc = HashMap<String, Double>()
        acc[root.id] = 0.0

        for (node in order) {
            // No entry means no admitted path reached this node — it is structurally
            // reachable but the descent gate or the beam pruned every route to it.
            val currentLogProb = acc[node.id] ?: continue

            // Negligible-mass cutoff, applied to the node's ACCUMULATED posterior once every
            // incoming edge has been summed — deliberately not per-path. In a tree the two
            // coincide, because a node has exactly one path. In a DAG they do not: several
            // individually-negligible paths into one node can sum to material mass under
            // logSumExp, and multi-parent nodes are precisely the polyhierarchy structure this
            // router exists to measure. Pruning per-edge would therefore discard mass the
            // enumerating router accumulated, with the error concentrated on bridges.
            if (currentLogProb < LOG_NEGLIGIBLE_PATH) continue

            nodeMap[node.id] = node
            logProbMap[node.id] = currentLogProb

            if (node.isLeaf) continue

            val step = childTransitions(node, embedding, opts) { n, qId, resp ->
                residualHits.add(ResidualHit(n, qId, resp))
            } ?: continue

            for (i in step.bestIndices) {
                val child = step.children[i]
                val accumulatedWeight = currentLogProb + step.logTransitions[i]
                // Push unconditionally; the cutoff is applied to the child's summed posterior
                // when the child is processed, not to this single contribution.
                val prev = acc[child.id]
                acc[child.id] = if (prev == null) accumulatedWeight else logSumExp(prev, accumulatedWeight)
            }
        }

        // 1. Gather all candidates (both leaf candidates and fallback internal nodes)
        val candidates = mutableMapOf<GraphNode, Double>()

        // Find leaf candidates
        val leafCandidates = logProbMap
            .filterKeys { id -> nodeMap[id]?.isLeaf == true }
            .map { (id, logProb) -> nodeMap.getValue(id) to logProb }
            .toMap()
        candidates.putAll(leafCandidates)

        // Internal nodes fallback if no active children reached
        val enableResidual = config.formalism.enableResidualRouting
        if (enableResidual || leafCandidates.isEmpty()) {
            for ((nodeId, logProb) in logProbMap) {
                val node = nodeMap[nodeId] ?: continue
                // No isBridge exclusion here: isBridge marks legitimate cross-link hosts
                // (e.g. a domain node with a bridged child) whose residual pool must
                // remain a valid destination, or its unrouted queries fall back to root.
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
