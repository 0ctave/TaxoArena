package taxonomy.operations

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.TraversalPolicy
import taxonomy.model.DagRoot
import taxonomy.diagnostics.DiagnosticsBundle
import kotlin.math.exp

enum class ProposalType { GROW, SHRINK }
enum class ProposalOutcome { ACCEPTED, REJECTED, NO_PROPOSAL }

/**
 * Locale-pinned formatting for diagnostic strings embedded in CSV fields.
 *
 * The JVM runs with `-Duser.country=FR`, so a bare `"%.6f".format(x)` produces `0,024714`. Inside
 * a CSV field that is not merely ugly, it shifts every following column.
 */
internal object DiagFmt {
    fun f(v: Double, decimals: Int = 6): String =
        String.format(java.util.Locale.US, "%.${decimals}f", v)
}

/**
 * The structural acceptance rule, extracted from `tryProposal` so it can be tested without
 * standing up a DAG, a corpus and a full re-route. Pure and behaviour-identical to the
 * expression it replaces.
 *
 * Canonical arm (`zGate == 0`): lexicographic on `(J, -|V|)` against the float tolerance
 * [tau]. A strict J improvement accepts; a J-neutral edit accepts only if it also removes
 * nodes, which is what lets passthrough wrappers dissolve; anything else rejects.
 *
 * z arm (`zGate > 0`): accepts on `deltaJ > max(tau, zGate * SE)`. The [tau] floor — not
 * `zGate * SE` alone — is what makes a termination argument possible: every accepted edit
 * then raises J by at least tau, and J is bounded above by 1, so at most `(1 - J_0)/tau`
 * edits can ever commit. With `zGate * SE` alone a vanishing SE would admit a vanishing
 * improvement and that bound collapses. In practice the floor almost never binds — median
 * SE(dJ) is 5.85e-5, so z=2 gives 1.17e-4, two orders above tau.
 *
 * `SE == 0` identifies a pure structural edit (a passthrough dissolution that moves no
 * query), for which deltaJ is exactly 0 and z is undefined; it falls back to the size test
 * so those edits can still commit.
 *
 * Note the arms are alternatives, not layers: with `zGate > 0` the lexicographic tie-break
 * applies only in the `SE == 0` case, so a J-neutral simplification with SE > 0 cannot
 * commit. The frozen artifact (freeze_mcs55.toml, 2026-07-27) was built with the
 * z-gate arm at acceptanceZ = 2.0; `acceptanceZ = 0` is the legacy lexicographic arm.
 */
internal fun isProposalAccepted(
    deltaJ: Double,
    deltaV: Int,
    tau: Double,
    zGate: Double,
    seDeltaJ: Double?
): Boolean = if (zGate > 0.0 && seDeltaJ != null) {
    if (seDeltaJ > 0.0) deltaJ > maxOf(tau, zGate * seDeltaJ) else deltaV < 0
} else {
    when {
        deltaJ > tau -> true
        kotlin.math.abs(deltaJ) <= tau -> deltaV < 0
        else -> false
    }
}

class ProposalStats {
    val attempted = mutableMapOf<ProposalType, Int>()
    val accepted = mutableMapOf<ProposalType, Int>()
    val rejected = mutableMapOf<ProposalType, Int>()
    val noProposal = mutableMapOf<ProposalType, Int>()
    /** Proposals skipped because an identical (site, population, geometry) was already
     *  decided since the last accepted edit. Reported next to the outcome counts so a
     *  hit rate is always interpretable against how often the path was reached. */
    var memoHits = 0
    var boundarySkips = 0
    
    fun record(type: ProposalType, outcome: ProposalOutcome) {
        attempted[type] = (attempted[type] ?: 0) + 1
        when (outcome) {
            ProposalOutcome.ACCEPTED -> accepted[type] = (accepted[type] ?: 0) + 1
            ProposalOutcome.REJECTED -> rejected[type] = (rejected[type] ?: 0) + 1
            ProposalOutcome.NO_PROPOSAL -> noProposal[type] = (noProposal[type] ?: 0) + 1
        }
    }
    
    fun clear() {
        attempted.clear(); accepted.clear(); rejected.clear(); noProposal.clear()
        memoHits = 0; boundarySkips = 0
    }
    
    fun summary(): String {
        val types = ProposalType.entries
        return types.joinToString(" | ") { t ->
            val att = attempted[t] ?: 0
            if (att == 0) "$t: 0" else
                "$t: $att attempted (${accepted[t] ?: 0} accepted, ${rejected[t] ?: 0} rejected, ${noProposal[t] ?: 0} no-proposal)"
        } + " | [MEMO] hits=$memoHits boundary-exempt=$boundarySkips"
    }
}

/**
 * Orchestrator for DAG operations, delegating to specialized components.
 */
@Service
class TaxonomyOperations(
    val fitter: TaxonomyFitter,
    private val trickler: TaxonomyTrickler,
    private val splitter: TaxonomySplitter,
    private val merger: TaxonomyMerger,
    private val config: TaxonomyConfig
) {
    private val log = LoggerFactory.getLogger("taxonomy.Operations")
    
    private var cachedBaseJ: Double? = null
    // Cell assignment matching cachedBaseJ, kept so the paired dJ bootstrap can use the same
    // pre-edit state the cached baseJ came from instead of forcing a restore.
    private var cachedBaseCapture: taxonomy.utils.JBootstrap.Capture? = null
    private val rejectedProposalsCache = java.util.concurrent.ConcurrentHashMap.newKeySet<ProposalFingerprint>()
    val proposalStats = ProposalStats()

    fun invalidateCachedJ() {
        cachedBaseJ = null
        cachedBaseCapture = null
        rejectedProposalsCache.clear()
    }

    fun routeQuery(
        query: Embedding,
        root: GraphNode,
        currentIteration: Int = 2,
        originalCategories: List<String>? = null,
        isInference: Boolean = false
    ): Map<GraphNode, Double> =
        trickler.routeQuery(query, root, currentIteration, originalCategories, isInference).leaves

    suspend fun fitNodeRecursive(node: GraphNode, currentIteration: Int = 0, isFinalIteration: Boolean = false) = fitter.fitNodeRecursive(node, currentIteration, isFinalIteration)
    fun fitSingleNode(node: GraphNode, isFinalIteration: Boolean = false) = fitter.fitSingleNode(node, isFinalIteration)

    suspend fun splitNodesRecursive(
        dag: DagRoot,
        allEmbeddings: List<Embedding>,
        groundTruthMap: Map<String, List<String>>,
        currentIteration: Int
    ) {
        val root = dag.node
        val byDepth = mutableMapOf<Int, MutableList<GraphNode>>()
        val visited = mutableSetOf<String>()
        val queue = ArrayDeque<GraphNode>().apply { add(root) }

        while (queue.isNotEmpty()) {
            val n = queue.removeFirst()
            if (!visited.add(n.id)) continue
            byDepth.getOrPut(n.depth) { mutableListOf() }.add(n)
            queue.addAll(n.children)
        }

        byDepth.keys.sortedDescending().forEach { depth ->
            val nodesAtDepth = byDepth[depth]!!
            for (node in nodesAtDepth) {
                // Split threshold is 0 (veto, not toll): split QUALITY is already gated
                // locally by the splitter itself — chance-corrected separation >= epsilon
                // on the ROUTED partition, routing-sustainability, sibling distinctness.
                // The global J check only needs to reject splits that degrade the DAG.
                // A positive epsilon*pi_S bar double-charges the same question through a
                // diluted lens: global J measures cells against the whole-corpus
                // expectation, so refining an already-tight region gains far less
                // globally than its local separation indicates (measured: Business,
                // 620 q, local sep 0.058 = 5.8x epsilon, Delta J +0.00148, rejected
                // every iteration at bar 0.00208 = epsilon*0.21 — domains stayed
                // childless leaves and depth stalled at 3).
                // ── k-fallback ────────────────────────────────────────────────
                // Previously: EM picked one k, and if that single candidate failed any
                // downstream gate the node stayed an unsplit leaf with no recourse.
                // That made maxK a structural determinant rather than a cost cap —
                // measured: raising it 4 -> 6 collapsed the tree to 36 leaves and J
                // 0.181, because wider proposals died outright instead of falling back.
                //
                // Now every k in 2..maxK is offered in ASCENDING order and the first
                // one the objective accepts is taken.
                //
                // Selection is lowest-k-first, NOT argmax dJ. Taking a maximum over
                // several noisy dJ estimates is the same optimisation bias that makes
                // argmax-separation invalid for choosing k: with 3 candidates the max
                // is biased upward even when all three are equivalent, and the winner
                // is disproportionately the one whose bootstrap SE happened to land
                // low. Every candidate here has already cleared the SAME statistical
                // gate independently, so the ordering only has to break ties among
                // edits that are each individually supported. Parsimony is the
                // conservative tie-break and is deterministic, which argmax is not.
                //
                // GUARD (memo): proposalKey carries k. The memo fingerprint is keyed on
                // the site, so without a discriminator a rejected k=2 would memo-skip
                // k=3 and record it REJECTED unevaluated — the false-hit class the
                // MEMOIZED row caught on internal nodes.
                //
                // GUARD (determinism): ascending k, first acceptance wins. No tie-break
                // on a float comparison, so the bit-identical-at-fixed-split property
                // is preserved.
                //
                // Coarsening can map different k onto the same routed partition (k=4
                // and k=3 both collapsing to 3). Those are not deduplicated here: a
                // duplicate simply fails the memo on a different proposalKey and costs
                // one extra evaluation. Dedup would need the routed assignment, which
                // is only known inside splitSingleNode after it has already mutated
                // the node.
                var outcome = ProposalOutcome.NO_PROPOSAL
                for (k in 2..config.formalism.maxK) {
                    outcome = tryProposal(
                        dag, node, allEmbeddings, groundTruthMap, currentIteration,
                        ProposalType.GROW, proposalKey = "k$k"
                    ) {
                        splitter.splitSingleNode(node, forcedK = k, currentIteration = currentIteration)
                    }
                    if (outcome == ProposalOutcome.ACCEPTED) break
                }
            }
        }
    }

    suspend fun generateLabelsPostPass(root: GraphNode, onProgress: (Int, Int) -> Unit = { _, _ -> }) =
        splitter.generateLabelsPostPass(root, onProgress)

    fun resetConceptCounter() = splitter.resetConceptCounter()

    suspend fun optimizeHierarchy(
        dag: DagRoot,
        allEmbeddings: List<Embedding>,
        groundTruthMap: Map<String, List<String>>,
        currentIteration: Int = 2,
        learningPhase: Boolean = false
    ) = merger.optimizeHierarchy(dag, allEmbeddings, groundTruthMap, currentIteration, learningPhase, this)



    /**
     * Phase 3: Reassign all embeddings to their destination leaves using a
     * log-likelihood margin criterion.
     *
     * For each query, the trickler produces a normalized log-probability over
     * every reachable leaf.  We assign the query to every leaf whose score is
     * within [config.formalism.assignmentMargin] nats of the best-scoring leaf.
     *
     * This replaces the old hard cap (maxLeafAssignments).  The number of
     * assignments per query is now determined purely by the geometry of the
     * embedding space: tightly-separated leaves produce single assignments;
     * genuinely overlapping concepts produce multiple assignments in proportion
     * to their overlap.
     *
     * At bootstrap (4 leaves, coarsely separated domains) a query that is
     * clearly a Biology query will score >>1 nat above History/Law/Physics,
     * so it gets assigned to exactly one leaf.  At equilibrium with hundreds of
     * fine-grained leaves, semantically ambiguous queries naturally land in 2–3
     * closely-scoring leaves.
     */
    suspend fun reassignQueries(
        dag: DagRoot,
        embeddings: List<Embedding>,
        groundTruthMap: Map<String, List<String>> = emptyMap(),
        currentIteration: Int = 1
    ) = coroutineScope {
        val root = dag.node
        root.updateAllShrinkages()

        val numCores = Runtime.getRuntime().availableProcessors()
        val chunkSize = maxOf(5, (embeddings.size + (numCores * 4) - 1) / (numCores * 4)).coerceAtMost(25)
        embeddings.chunked(chunkSize).map { chunk ->
            async(Dispatchers.Default) {
                for (emb in chunk) {
                    val originals = groundTruthMap[emb.rawText]
                    val routeResult = trickler.routeQuery(emb, root, currentIteration, originals)
                    GraphNode.registerEmbedding(emb)
                    if (routeResult.leaves.isNotEmpty()) {
                        routeResult.leaves.forEach { (leaf, logWeight) ->
                            val weight = kotlin.math.exp(logWeight)
                            synchronized(leaf.queryWeights) {
                                // `queries` and `queryWeights` move in lockstep: clearGraphQueries
                                // empties both, GraphStateBackup restores both, and every caller of
                                // reassignQueries clears immediately beforehand. So "emb is already
                                // in queries" is exactly "rawText is already a queryWeights key
                                // before this merge" — an O(1) lookup in place of an O(|queries|)
                                // scan held under the per-leaf lock. That scan made a full reassign
                                // quadratic in leaf population and serialised the parallel routing.
                                val alreadyPresent = leaf.queryWeights.containsKey(emb.rawText)
                                leaf.queryWeights.merge(emb.rawText, weight, Double::plus)
                                if (!alreadyPresent) {
                                    leaf.queries.add(emb)
                                }
                            }
                        }
                    } else if (config.formalism.enableResidualRouting) {
                        // No leaf reached at all: the query must still be RETAINED, not just
                        // flagged. Attribute it to the node the walk converged to (guaranteed
                        // non-leaf) with full weight AND the residual flag: the weight keeps
                        // total mass conserved, the embedding in `.queries` makes the query
                        // visible to getAllQueriesInRegion so the residual-split gate can carve
                        // a new child out of coherent residual mass, and the residualQueries
                        // entry keeps the C3 invariant satisfied (internal hard queries are
                        // legal exactly when they are residual-flagged). Recording only the
                        // naked ID would lose the weight (mass leaks every iteration) and
                        // keep the embedding out of the region, so the residual-split
                        // mechanism could never recover it.
                        log.debug("Query '${emb.rawText.take(40)}' reached no leaf — retained as residual at ${routeResult.primary.label ?: routeResult.primary.id}")
                        val qId = if (emb.queryId != -1) emb.queryId.toString() else emb.rawText
                        synchronized(routeResult.primary.residualQueries) {
                            routeResult.primary.residualQueries.add(qId)
                            routeResult.primary.residualConfidences[qId] = 0.0
                        }
                        synchronized(routeResult.primary.queryWeights) {
                            // O(1) presence test — see the lockstep note in the leaf branch above.
                            val alreadyPresent = routeResult.primary.queryWeights.containsKey(emb.rawText)
                            routeResult.primary.queryWeights.merge(emb.rawText, 1.0, Double::plus)
                            if (!alreadyPresent) {
                                routeResult.primary.queries.add(emb)
                            }
                        }
                    } else {
                        // Residual routing disabled entirely: hard-assign to root as the
                        // fallback so mass still lands somewhere.
                        log.debug("Query '${emb.rawText.take(40)}' fell back to root — out-of-distribution?")
                        synchronized(root.queryWeights) {
                            // O(1) presence test — see the lockstep note in the leaf branch above.
                            val alreadyPresent = root.queryWeights.containsKey(emb.rawText)
                            root.queryWeights.merge(emb.rawText, 1.0, Double::plus)
                            if (!alreadyPresent) {
                                root.queries.add(emb)
                            }
                        }
                    }

                    if (config.formalism.enableResidualRouting) {
                        for (hit in routeResult.residualHits) {
                            synchronized(hit.node.residualQueries) {
                                hit.node.residualQueries.add(hit.questionId)
                                hit.node.residualConfidences[hit.questionId] = hit.bestChildScore
                            }
                        }
                    }
                }
            }
        }.awaitAll()

        // ── Completeness diagnostic: every embedding must have deposited weight
        // somewhere REACHABLE. A reroute that silently drops queries corrupts the
        // state every later proposal is judged (and asserted) against.
        run {
            val reachableKeys = HashSet<String>()
            val seen = HashSet<String>()
            fun walkKeys(n: GraphNode) {
                if (!seen.add(n.id)) return
                reachableKeys.addAll(n.queryWeights.keys)
                n.children.forEach { walkKeys(it) }
                n.crossLinkChildren.forEach { walkKeys(it) }
            }
            walkKeys(root)
            val dropped = embeddings.filter { it.rawText !in reachableKeys }
            if (dropped.isNotEmpty()) {
                log.warn("[REROUTE DIAG] ${dropped.size}/${embeddings.size} queries deposited no weight on any reachable node")
                for (emb in dropped.take(3)) {
                    val rr = trickler.routeQuery(emb, root, currentIteration, groundTruthMap[emb.rawText])
                    val leafInfo = rr.leaves.toList().take(4).joinToString(", ") { (n, lw) ->
                        "'${n.label}'(logW=${"%.2f".format(java.util.Locale.US, lw)}, reachable=${seen.contains(n.id)})"
                    }
                    log.warn("[REROUTE DIAG] '${emb.rawText.take(50)}' -> leaves=${rr.leaves.size} [$leafInfo] primary='${rr.primary.label}' primaryReachable=${seen.contains(rr.primary.id)}")
                }
            }
        }
    }

    private fun computePairwiseDenom(root: GraphNode): Double {
        val leaves = mutableListOf<GraphNode>()
        val residualParents = mutableListOf<GraphNode>()
        val visited = mutableSetOf<String>()
        fun walk(n: GraphNode) {
            if (!visited.add(n.id)) return
            if (n.isLeaf) {
                leaves.add(n)
            } else {
                if (n.residualQueries.isNotEmpty()) {
                    residualParents.add(n)
                }
                n.children.forEach { walk(it) }
            }
        }
        walk(root)

        var pairFrac = 0.0
        for (leaf in leaves) {
            val cN = leaf.queryWeights.values.sum()
            pairFrac += cN * (cN - 1.0)
        }
        for (parent in residualParents) {
            val cN = parent.residualQueries.size.toDouble()
            pairFrac += cN * (cN - 1.0)
        }
        return pairFrac
    }

    suspend fun tryProposal(
        dag: DagRoot,
        site: GraphNode,
        allEmbeddings: List<Embedding>,
        groundTruthMap: Map<String, List<String>>,
        currentIteration: Int,
        proposalType: ProposalType,
        refitScope: ((GraphNode) -> Unit)? = null,
        proposalKey: String? = null,
        action: suspend () -> Boolean
    ): ProposalOutcome {
        // Memoization check: identify if this exact proposal has been rejected in this iteration.
        // `site` alone does NOT identify a proposal when several distinct edits target the same
        // node: a cross-link is the pair (host -> target) and `site` is only the target, so
        // rejecting 'Law -> N' would memo-skip 'Philosophy -> N', a genuinely different edit with
        // a different J outcome, and record it as REJECTED without ever evaluating it. Callers
        // whose proposal is not identified by its site pass a discriminating `proposalKey`.
        // Fingerprint components are chosen from MEASURED stability, not from what
        // looks like it identifies the state. Instrumenting a full canonical run over
        // iterations 5..10 — after growth stops, when nothing should move — gave:
        //
        //   key-set hash   139/139 sites constant      mu.contentHashCode  139/139
        //   node size n    139/139 constant            mu quantized        139/139
        //   weight bits     51/139 constant            kappa bits            1/139
        //   weights @1e-6   52/139 constant            kappa @1e-6           1/139
        //
        // Raw Double bits of the membership weights and of kappa must NOT be folded in:
        // both are re-derived by routing every iteration and never reach bit-identity —
        // kappa converges asymptotically, drifting at ~1e-13 forever — so a fingerprint
        // that includes them changes on almost every site every iteration and the memo
        // can never hit.
        //
        // Excluding them is sound rather than a tolerance fudge. kappa is FITTED from
        // this node's population and direction, so conditioning on (keys, mu, n)
        // already pins it up to fit noise; and its only consumer in the split path is
        // the `vmfKappa < 0.5` diffuse test, against observed values around 130-200.
        // The weights likewise enter only through the mass/ess feasibility thresholds.
        // Both are guarded below rather than trusted.
        // Mixed rather than a plain sum of hashCodes. A plain sum collides whenever a
        // site loses query X and gains query Y with hash(X) == hash(Y) at unchanged n —
        // and the failure mode is a STALE MEMO silently recorded as REJECTED. The
        // multiplier costs nothing and destroys that coincidence.
        //
        // It matters more than it looks: site.vmfMu is STALE during phase 4 (the refit
        // runs at end-of-iteration, so mu reflects the previous iteration's population),
        // so muHash discriminates ACROSS iterations but not WITHIN one. The real
        // within-iteration discriminators are this hash, n and massQ.
        //
        // Walked over the SUBTREE, not just site.queryWeights. Internal nodes hold no
        // direct queries, so a site-local hash degenerates to (nodeId, muHash) for
        // every SHRINK proposal — and muHash is stale within an iteration, so the
        // fingerprint would be effectively constant across iterations for exactly the
        // proposals whose outcome depends on their children's drifting populations.
        // Latent while the cache never hit; live the moment it did.
        var populationHash = 0L
        var siteMass = 0.0
        var siteSumSq = 0.0
        var siteN = 0
        run {
            val seen = HashSet<String>()
            val stack = ArrayDeque<GraphNode>().apply { add(site) }
            while (stack.isNotEmpty()) {
                val cur = stack.removeLast()
                if (!seen.add(cur.id)) continue
                for ((k, w) in cur.queryWeights) {
                    populationHash += k.hashCode() * -0x61c8864680b583ebL + cur.id.hashCode()
                    siteMass += w; siteSumSq += w * w; siteN++
                }
                cur.children.forEach { stack.add(it) }
            }
        }
        val siteEss = if (siteMass > 0.0) (siteMass * siteMass / siteSumSq) else 0.0
        val fingerprint = ProposalFingerprint(
            nodeId = if (proposalKey != null) "${site.id}|$proposalKey" else site.id,
            populationHash = populationHash.toInt(),
            muHash = site.vmfMu.contentHashCode(),
            n = siteN,
            massQ = Math.round(siteMass * 1e3)
        )

        // Boundary guard. The quantities deliberately left out of the fingerprint
        // reach the split decision only through threshold comparisons, so a node
        // sitting on one of those thresholds is never memoized — there, the low-bit
        // drift the fingerprint ignores could genuinely flip the outcome. Away from
        // them, identical (keys, mu, n, mass) provably gives an identical decision.
        val feasibility = 2.0 * config.formalism.minClusterSize
        val diffuseMass = 10.0 * config.formalism.minClusterSize
        val onABoundary =
            kotlin.math.abs(siteMass - feasibility) < 0.05 ||
                kotlin.math.abs(siteEss - feasibility) < 0.05 ||
                kotlin.math.abs(siteMass - diffuseMass) < 0.05 ||
                site.vmfKappa < 1.0 ||
                site.depth >= config.formalism.maxDepth - 1
        if (onABoundary) proposalStats.boundarySkips++
        if (!onABoundary && rejectedProposalsCache.contains(fingerprint)) {
            proposalStats.memoHits++
            log.debug("[MEMOIZED REJECTION] Skip tryProposal for site '${site.label ?: site.id}'")
            // Record the ROW, not just the counter. Without this the memo erases its own
            // audit trail: the repeated (site, dJ) rows are exactly what made "44
            // redundant REJECTED, 255 redundant NO_PROPOSAL" computable in the first
            // place, and folding them into an aggregate would make the hit rate
            // checkable per run but never per site.
            //
            // COMPATIBILITY: like the k= change, this is a break. proposals.csv written
            // before this commit contains the repeats as full REJECTED rows; after it,
            // the repeat appears once as decision=MEMOIZED with the fingerprint that
            // matched. Anything counting redundancy across the boundary must treat
            // MEMOIZED rows as the repeats.
            DiagnosticsBundle.recordProposal(
                iter = currentIteration, type = proposalType.name,
                siteId = site.id, siteLabel = site.label,
                dJ = null, seDJ = null, z = null, dV = null,
                decision = "MEMOIZED",
                reason = "identical_since_last_accept(pop=${fingerprint.populationHash}" +
                    ",n=${fingerprint.n},massQ=${fingerprint.massQ})",
                nSite = siteN
            )
            proposalStats.record(proposalType, ProposalOutcome.REJECTED)
            return ProposalOutcome.REJECTED
        }

        val root = dag.node
        val registry = mutableMapOf<String, GraphNode>()
        fun walkReg(n: GraphNode) {
            if (registry.containsKey(n.id)) return
            registry[n.id] = n
            n.children.forEach { walkReg(it) }
            n.crossLinkChildren.forEach { walkReg(it) }
        }
        walkReg(root)

        // 1. Capture structural state before action
        val beforeNodes = registry.values.map { node ->
            StructuralState(
                id = node.id,
                childrenIds = node.children.map { it.id }.toSet(),
                crossLinkChildrenIds = node.crossLinkChildren.map { it.id }.toSet(),
                parentsIds = node.parents.map { it.id }.toSet()
            )
        }.toSet()

        val backup = taxonomy.model.GraphStateBackup(root)

        val didAnything = action()
        if (!didAnything) {
            // Memoized like a rejection: the site proposed nothing, and with the same
            // population and geometry it will propose nothing again. Cleared on every
            // accepted edit, exactly as rejections are.
            if (!onABoundary) rejectedProposalsCache.add(fingerprint)
            proposalStats.record(proposalType, ProposalOutcome.NO_PROPOSAL)
            return ProposalOutcome.NO_PROPOSAL
        }

        // 2. Capture structural state after action
        val postRegistry = mutableMapOf<String, GraphNode>()
        fun walkRegPost(n: GraphNode) {
            if (postRegistry.containsKey(n.id)) return
            postRegistry[n.id] = n
            n.children.forEach { walkRegPost(it) }
            n.crossLinkChildren.forEach { walkRegPost(it) }
        }
        walkRegPost(root)

        val afterNodes = postRegistry.values.map { node ->
            StructuralState(
                id = node.id,
                childrenIds = node.children.map { it.id }.toSet(),
                crossLinkChildrenIds = node.crossLinkChildren.map { it.id }.toSet(),
                parentsIds = node.parents.map { it.id }.toSet()
            )
        }.toSet()

        if (beforeNodes == afterNodes) {
            // No structural change occurred at all (complete early exit, no log clutter)
            backup.restore(registry)
            if (!onABoundary) rejectedProposalsCache.add(fingerprint)
            proposalStats.record(proposalType, ProposalOutcome.NO_PROPOSAL)
            return ProposalOutcome.NO_PROPOSAL
        }

        // Diagnose reachability loss: nodes present before the action but absent
        // from the post-action walk are either intentionally destroyed (fusion
        // sources) or ORPHANED subtrees whose mass silently leaves the graph.
        val lostIds = registry.keys - postRegistry.keys
        if (lostIds.isNotEmpty()) {
            val details = lostIds.take(8).joinToString(" | ") { id ->
                val n = registry[id]!!
                "'${n.label}' w=${"%.1f".format(java.util.Locale.US, n.queryWeights.values.sum())} res=${n.residualQueries.size} ch=${n.children.size} par=${n.parents.size}"
            }
            log.info("[PROPOSAL DIAG] ${lostIds.size} node(s) unreachable after action: $details")
        }

        // The z-gate needs SE(dJ) to decide, so it forces the bootstrap on regardless of the
        // diagnostics flag.
        val zGate = config.formalism.acceptanceZ
        val bootstrapOn = config.diagnostics.enableProfiling || zGate > 0.0
        var baseCapture: taxonomy.utils.JBootstrap.Capture? =
            if (bootstrapOn && refitScope == null) cachedBaseCapture else null

        val baseJ = if (cachedBaseJ != null && refitScope == null) {
            cachedBaseJ!!
        } else {
            // Restore backup to get back to base state, compute baseJ, then re-execute action
            backup.restore(registry)
            if (refitScope != null) {
                refitScope(root)
            }
            root.updateAllShrinkages()
            clearGraphQueries(root)
            reassignQueries(dag, allEmbeddings, groundTruthMap, currentIteration)
            // Base side of the proposal: this is a settled post-reroute state, so the same
            // invariant applies. Checking here too means a conservation failure is attributed
            // to the state that carried it in, rather than surfacing on the next proposal's
            // post-action check and looking like that edit's fault.
            assertMassConservation(root, allEmbeddings)
            val jVal = taxonomy.utils.StatisticsUtils.computeDagSeparationJ(root, allEmbeddings)

            // Capture the pre-edit cell assignment while the graph is genuinely in the base
            // state — this is the only point in the flow where it is.
            if (bootstrapOn) {
                baseCapture = taxonomy.utils.JBootstrap.capture(root, allEmbeddings)
            }

            // Re-execute action
            action()

            if (refitScope == null) {
                cachedBaseJ = jVal
                if (bootstrapOn) cachedBaseCapture = baseCapture
            }
            jVal
        }

        if (refitScope != null) {
            refitScope(root)
        }
        root.updateAllShrinkages()
        clearGraphQueries(root)
        reassignQueries(dag, allEmbeddings, groundTruthMap, currentIteration)

        // Runs on EVERY proposal, deliberately. It is cheap next to the full re-route it
        // follows, and it is the invariant that caught the corpus-swallowing fusion, the
        // maxOf weight destruction and the mass > q_dir excesses — all of which lived in
        // iterations 2..N, so restricting it to iteration 1 would blind exactly the window
        // where structural edits actually go wrong.
        assertMassConservation(root, allEmbeddings)
        val newJ = taxonomy.utils.StatisticsUtils.computeDagSeparationJ(root, allEmbeddings)
        val deltaJ = newJ - baseJ

        // Lexicographic objective: (J, -|V|)
        val deltaV = postRegistry.size - registry.size

        // Diagnostic only — nothing below reads this. Reports whether dJ is distinguishable
        // from zero given that both sides share a corpus draw, which is the question the gate
        // is really asking and the one tau (1e-6, a float tolerance) cannot answer.
        var afterCapture: taxonomy.utils.JBootstrap.Capture? = null
        var seDeltaJ: Double? = null
        if (bootstrapOn && baseCapture != null) {
            try {
                afterCapture = taxonomy.utils.JBootstrap.capture(root, allEmbeddings)
                val seDelta = taxonomy.utils.JBootstrap.pairedDeltaSe(baseCapture!!, afterCapture!!)
                seDeltaJ = seDelta
                // Rendered as text, not NaN: a NaN in this field breaks comparison ordering in
                // any downstream sort or percentile over the log.
                val zText = if (seDelta > 0.0) "%.2f".format(java.util.Locale.US, deltaJ / seDelta) else "n/a"

                // SE(dJ) == 0 means no query changed cells between the two structures. Then dJ
                // must be exactly 0 as well: identical cell contents cannot produce a different
                // J. If it does, the capture points are not the states they claim to be, and
                // every z below is being computed against the wrong baseline. Exact zero is the
                // right test — with continuous Dirichlet weights a genuine partition change
                // cannot land on 0.
                if (seDelta == 0.0 && deltaJ != 0.0) {
                    log.error(
                        "[DJ-SE INVARIANT] SE(dJ)=0 but dJ=${"%.3e".format(java.util.Locale.US, deltaJ)}" +
                            " for $proposalType '${site.label ?: site.id}' — identical cells cannot" +
                            " change J. The before/after capture points are inconsistent."
                    )
                }
                log.info(
                    "[DJ-SE] $proposalType '${site.label ?: site.id}'" +
                        " dJ=${"%.3e".format(java.util.Locale.US, deltaJ)}" +
                        " SE_dJ=${"%.3e".format(java.util.Locale.US, seDelta)}" +
                        " z=$zText" +
                        " dV=$deltaV"
                )
            } catch (e: Exception) {
                afterCapture = null
                log.debug("[DJ-SE] bootstrap failed for '${site.label ?: site.id}': ${e.message}")
            }
        }
        val tau = config.formalism.tau
        
        // Two acceptance rules, selected by acceptanceZ.
        //
        // z-gate (acceptanceZ > 0): an edit is taken if its measured improvement is large
        // relative to the paired bootstrap error of that same measurement, or if it changes no
        // query's cell at all and strictly simplifies the structure. The second clause is not a
        // loophole — SE(dJ) == 0 identifies a pure structural edit (a passthrough dissolution
        // that moves no query), for which dJ is exactly 0 and z is undefined. Without it those
        // edits could never commit and wrapper nodes would accumulate through construction.
        //
        // Legacy (acceptanceZ == 0): lexicographic on (J, -|V|) against the float tolerance
        // tau. Retained as the baseline arm so the gate change can be attributed.
        val accepted = isProposalAccepted(deltaJ, deltaV, tau, zGate, seDeltaJ)

        // Second sink for the same values the log lines below carry, in a form that can be
        // grouped. The rejection tallies this project needs (unique nodes blocked, and by which
        // gate) are a GROUP BY on this file rather than a re-read of 200k log lines.
        taxonomy.diagnostics.DiagnosticsBundle.recordProposal(
            iter = currentIteration,
            type = proposalType.name,
            siteId = site.id,
            siteLabel = site.label,
            dJ = deltaJ,
            seDJ = seDeltaJ,
            z = seDeltaJ?.takeIf { it > 0.0 }?.let { deltaJ / it },
            dV = deltaV,
            decision = if (accepted) "ACCEPTED" else "REJECTED",
            reason = if (accepted) null else {
                // Which arm refused it, with the threshold that bound — the category alone is
                // not enough to reconstruct why afterwards.
                if (zGate > 0.0 && seDeltaJ != null && seDeltaJ > 0.0)
                    "z_gate(need>${DiagFmt.f(maxOf(tau, zGate * seDeltaJ), 9)})"
                else if (kotlin.math.abs(deltaJ) <= tau) "j_neutral_and_dV>=0(dV=$deltaV)"
                else "j_regression"
            },
            nSite = site.queryWeights.size
        )

        if (accepted) {
            log.info("[$proposalType ACCEPTED] '${site.label ?: site.id}' Delta J = ${"%.6f".format(java.util.Locale.US, deltaJ)}, Delta V = $deltaV")
            rejectedProposalsCache.clear()
            cachedBaseJ = newJ
            // The accepted post-edit state becomes the next proposal's base. If it was not
            // captured, drop the stale one rather than pair the next dJ against the wrong base.
            cachedBaseCapture = afterCapture
            proposalStats.record(proposalType, ProposalOutcome.ACCEPTED)
            return ProposalOutcome.ACCEPTED
        } else {
            if (kotlin.math.abs(deltaJ) > 1e-9) {
                log.info("[$proposalType REJECTED] '${site.label ?: site.id}' Delta J = ${"%.6f".format(java.util.Locale.US, deltaJ)}, Delta V = $deltaV. Reverting.")
            } else {
                log.debug("[$proposalType REJECTED] '${site.label ?: site.id}' Delta J = ${"%.6f".format(java.util.Locale.US, deltaJ)}, Delta V = $deltaV. Reverting.")
            }
            if (!onABoundary) rejectedProposalsCache.add(fingerprint)
            backup.restore(registry)
            proposalStats.record(proposalType, ProposalOutcome.REJECTED)
            return ProposalOutcome.REJECTED
        }
    }

    fun assertMassConservation(root: GraphNode, allEmbeddings: List<Embedding>) {
        val allNodes = mutableListOf<GraphNode>()
        val visited = mutableSetOf<String>()
        fun collect(n: GraphNode) {
            if (!visited.add(n.id)) return
            allNodes.add(n)
            n.children.forEach { collect(it) }
            n.crossLinkChildren.forEach { collect(it) }
        }
        collect(root)

        val queryWeights = mutableMapOf<String, Double>()
        for (node in allNodes) {
            for ((q, w) in node.queryWeights) {
                queryWeights[q] = (queryWeights[q] ?: 0.0) + w
            }
        }

        val totalAssignedMass = queryWeights.values.sum()
        if (totalAssignedMass == 0.0) return

        val recursiveSum = root.getRecursiveSoftMass()
        if (Math.abs(totalAssignedMass - recursiveSum) > 1e-6) {
            throw AssertionError("Mass definitions mismatched: deduped by query=$totalAssignedMass vs recursive sum=$recursiveSum")
        }

        // 1. Check for weight excess (> 1.01) on any query
        val queryWithExcessWeight = queryWeights.filter { it.value > 1.01 }
        if (queryWithExcessWeight.isNotEmpty()) {
            val example = queryWithExcessWeight.entries.first()
            throw AssertionError("Query weight excess detected: query '${example.key}' has weight ${example.value} > 1.01!")
        }

        // 2. Check total mass conservation
        if (config.formalism.enableResidualRouting) {
            val N = allEmbeddings.size.toDouble()
            if (Math.abs(totalAssignedMass - N) > 1.5) {
                // Diagnose WHERE the mass went before throwing: which corpus queries
                // hold no weight anywhere reachable, and whether they are at least
                // residual-flagged somewhere (naked-ID retention leak) or fully gone.
                val weightedKeys = queryWeights.keys
                val residualIds = mutableSetOf<String>()
                for (node in allNodes) residualIds.addAll(node.residualQueries)
                val missing = allEmbeddings.filter { it.rawText !in weightedKeys }
                val missingFlagged = missing.count { emb ->
                    val qId = if (emb.queryId != -1) emb.queryId.toString()
                              else emb.rawText
                    qId in residualIds || emb.rawText in residualIds
                }
                val samples = missing.take(3).joinToString(" | ") { it.rawText.take(60) }
                throw AssertionError(
                    "Mass conservation violated: Total assigned mass is $totalAssignedMass but total corpus size N is $N. " +
                    "Difference: ${Math.abs(totalAssignedMass - N)}. " +
                    "Queries with no weight anywhere: ${missing.size} (of which residual-flagged: $missingFlagged). " +
                    "Reachable nodes: ${allNodes.size}. Samples: [$samples]"
                )
            }
        }
    }


    fun clearGraphQueries(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
        if (!visited.add(node.id)) return
        node.queries.clear()
        node.queryWeights.clear()
        node.residualQueries.clear()
        node.residualConfidences.clear()
        node.children.forEach { clearGraphQueries(it, visited) }
        node.crossLinkChildren.forEach { clearGraphQueries(it, visited) }
    }

    fun countNodes(root: GraphNode): Int {
        val visited = mutableSetOf<String>()
        fun walk(node: GraphNode) {
            if (visited.contains(node.id)) return
            visited.add(node.id)
            node.children.forEach { walk(it) }
        }
        walk(root)
        return visited.size
    }

    fun exportToDot(root: GraphNode, policy: TraversalPolicy = TraversalPolicy.DAG_BOTH): String {
        val sb = StringBuilder()
        sb.append("digraph Taxonomy {\n")
        sb.append("  rankdir=LR;\n")
        sb.append("  node [shape=box, style=filled, fillcolor=white];\n")

        val visitedNodes = mutableSetOf<String>()
        val edges = mutableSetOf<String>()

        fun walk(node: GraphNode) {
            if (visitedNodes.contains(node.id)) return
            visitedNodes.add(node.id)

            val color = if (node.isBridge) "lightpink" else if (node.isLeaf) "lightblue" else "lightgrey"
            val shape = if (node.isBridge) "doublecircle" else "box"
            sb.append("  \"${node.id}\" [label=\"${node.label}\\n(${node.queries.size} q)\", fillcolor=$color, shape=$shape];\n")

            if (policy == TraversalPolicy.TREE_ONLY || policy == TraversalPolicy.DAG_BOTH) {
                node.children.forEach { child ->
                    val edge = "\"${node.id}\" -> \"${child.id}\""
                    if (!edges.contains(edge)) {
                        edges.add(edge)
                        sb.append("  $edge;\n")
                    }
                    walk(child)
                }
            }

            if (policy == TraversalPolicy.BRIDGE_ONLY || policy == TraversalPolicy.DAG_BOTH) {
                node.crossLinkChildren.forEach { child ->
                    val edge = "\"${node.id}\" -> \"${child.id}\" [style=dashed, color=red]"
                    val key = "\"${node.id}\" -> \"${child.id}\""
                    if (!edges.contains(key)) {
                        edges.add(key)
                        sb.append("  $edge;\n")
                    }
                    walk(child)
                }
            }
        }

        walk(root)
        sb.append("}\n")
        return sb.toString()
    }

    fun printHierarchy(root: GraphNode, policy: TraversalPolicy = TraversalPolicy.DAG_BOTH) {
        val sb = java.lang.StringBuilder()
        sb.append("\n┌── TAXONOMY DAG HIERARCHY ───────────────────────────────\n")
        buildTreeString(root, "│ ", true, sb, mutableSetOf(), false, policy)
        sb.append("└─────────────────────────────────────────────────────────")
        log.info(sb.toString())
    }

    fun printHierarchyCompact(root: GraphNode, policy: TraversalPolicy = TraversalPolicy.DAG_BOTH) {
        val sb = java.lang.StringBuilder()
        sb.append("\n┌── TAXONOMY HIERARCHY ───────────────────────────────────\n")
        buildTreeStringCompact(root, "│ ", true, sb, mutableSetOf(), false, policy)
        sb.append("└─────────────────────────────────────────────────────────")
        log.info(sb.toString())
    }

    /**
     * True iff [node] is a pure single-child pass-through wrapper for display purposes:
     * exactly one tree child, no cross-links, no queries of its own (hard or residual),
     * deep enough not to be a protected anchor. This is a printing-only concept -- it
     * never touches the live tree, construction, or routing, and is independent of
     * (deliberately looser than) TaxonomyMerger's own passthrough-collapse gate, which
     * has to stay conservative for convergence reasons documented in
     * archive/docs/dag-chain-formation-handoff.md. Here we're only deciding what to print.
     */
    private fun isDisplayWrapper(node: GraphNode): Boolean =
        node.treeChildren.size == 1 && node.crossLinkChildren.isEmpty() &&
        node.queries.isEmpty() && node.residualQueries.isEmpty() && node.depth > 1

    /**
     * Walk forward from [start] through consecutive display-wrapper levels, returning
     * the first node actually worth rendering and how many levels were skipped to reach
     * it.
     */
    private fun collapseWrapperChain(start: GraphNode): Pair<GraphNode, Int> {
        var current = start
        var hops = 0
        while (isDisplayWrapper(current)) {
            current = current.treeChildren.first()
            hops++
        }
        return current to hops
    }

    private fun buildTreeStringCompact(
        node: GraphNode,
        prefix: String,
        isTail: Boolean,
        sb: java.lang.StringBuilder,
        visited: MutableSet<String>,
        isCrossEdge: Boolean = false,
        policy: TraversalPolicy = TraversalPolicy.DAG_BOTH,
        chainSkipped: Int = 0
    ) {
        val cross = if (visited.contains(node.id)) " [CROSS-LINK]" else ""
        val edgeType = if (isCrossEdge) " [BRIDGE-EDGE]" else ""
        val type = if (node.isBridged) "Bridge" else if (node.isLeaf) "Leaf" else "Parent"
        val qCount = node.getRecursiveQueryCount()
        val directQ = node.queries.size
        val softMass = node.getRecursiveSoftMass()

        val parentNames = node.parents.mapNotNull { it.label }.filter { it.isNotBlank() }.distinct()
        val parentsInfo = if (parentNames.size > 1) " [Bridge Parents: ${parentNames.joinToString(" & ")}]" else ""

        val vmfStats = if (node.vmfMu.isNotEmpty()) {
            " (kappa: ${"%.1f".format(java.util.Locale.US, node.vmfKappa)})"
        } else ""
        val chainNote = if (chainSkipped > 0) " [⋯ $chainSkipped wrapper level${if (chainSkipped > 1) "s" else ""} collapsed]" else ""

        val metrics = "q_dir=$directQ, q_rec=$qCount, mass=${"%.1f".format(java.util.Locale.US, softMass)}"
        val nodeLabel = "${node.label} [$metrics, $type]$vmfStats$parentsInfo$chainNote$cross$edgeType"
        val connector = if (node.depth == 0) "" else if (isTail) "└── " else "├── "
        sb.append(prefix).append(connector).append(nodeLabel).append("\n")

        if (visited.contains(node.id)) return
        visited.add(node.id)

        val children = if (policy == TraversalPolicy.TREE_ONLY || policy == TraversalPolicy.DAG_BOTH) node.children.toList() else emptyList()
        val crossLinks = if (policy == TraversalPolicy.BRIDGE_ONLY || policy == TraversalPolicy.DAG_BOTH) node.crossLinkChildren.toList() else emptyList()
        val allChildren = children + crossLinks
        for (i in allChildren.indices) {
            val rawChild = allChildren[i]
            val childIsTail = i == allChildren.size - 1
            val nextPrefix = prefix + if (node.depth == 0) "" else if (isTail) "    " else "│   "
            val childIsCross = i >= children.size
            val (displayChild, skipped) = if (childIsCross) rawChild to 0 else collapseWrapperChain(rawChild)
            buildTreeStringCompact(displayChild, nextPrefix, childIsTail, sb, visited, childIsCross, policy, skipped)
        }
    }

    private fun buildTreeString(
        node: GraphNode,
        prefix: String,
        isTail: Boolean,
        sb: java.lang.StringBuilder,
        visited: MutableSet<String>,
        isCrossEdge: Boolean = false,
        policy: TraversalPolicy = TraversalPolicy.DAG_BOTH,
        chainSkipped: Int = 0
    ) {
        val cross = if (visited.contains(node.id)) " [CROSS-LINK]" else ""
        val edgeType = if (isCrossEdge) " [BRIDGE-EDGE]" else ""
        val type = if (node.isBridged) "Bridge" else if (node.isLeaf) "Leaf" else "Parent/Residual"

        val directQ = node.queries.size
        val qCount = node.getRecursiveQueryCount()
        val softMass = node.getRecursiveSoftMass()

        val parentNames = node.parents.mapNotNull { it.label }.filter { it.isNotBlank() }.distinct()
        val parentsInfo = if (parentNames.size > 1) " [Bridge Parents: ${parentNames.joinToString(" & ")}]" else ""

        val vmfStats = if (node.vmfMu.isNotEmpty()) {
            " (vMF kappa: ${"%.3f".format(java.util.Locale.US, node.vmfKappa)})"
        } else ""
        val chainNote = if (chainSkipped > 0) " [⋯ $chainSkipped wrapper level${if (chainSkipped > 1) "s" else ""} collapsed]" else ""

        val metrics = "q_dir=$directQ, q_rec=$qCount, mass=${"%.1f".format(java.util.Locale.US, softMass)}"
        val nodeLabel = "${node.label} [$metrics - $type]$vmfStats$parentsInfo$chainNote$cross$edgeType"
        val connector = if (node.depth == 0) "" else if (isTail) "└── " else "├── "
        sb.append(prefix).append(connector).append(nodeLabel).append("\n")

        if (visited.contains(node.id)) return
        visited.add(node.id)

        val children = if (policy == TraversalPolicy.TREE_ONLY || policy == TraversalPolicy.DAG_BOTH) node.children.toList() else emptyList()
        val crossLinks = if (policy == TraversalPolicy.BRIDGE_ONLY || policy == TraversalPolicy.DAG_BOTH) node.crossLinkChildren.toList() else emptyList()
        val allChildren = children + crossLinks
        for (i in allChildren.indices) {
            val rawChild = allChildren[i]
            val childIsTail = i == allChildren.size - 1
            val nextPrefix = prefix + if (node.depth == 0) "" else if (isTail) "    " else "│   "
            val childIsCross = i >= children.size
            val (displayChild, skipped) = if (childIsCross) rawChild to 0 else collapseWrapperChain(rawChild)
            buildTreeString(displayChild, nextPrefix, childIsTail, sb, visited, childIsCross, policy, skipped)
        }
    }

}

private data class StructuralState(
    val id: String,
    val childrenIds: Set<String>,
    val crossLinkChildrenIds: Set<String>,
    val parentsIds: Set<String>
)

private data class ProposalFingerprint(
    val nodeId: String,
    val populationHash: Int,
    val muHash: Int,
    val n: Int,
    val massQ: Long
)
