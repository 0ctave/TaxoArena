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
import kotlin.math.exp

enum class ProposalType { GROW, SHRINK, BRIDGE }
enum class ProposalOutcome { ACCEPTED, REJECTED, NO_PROPOSAL }

class ProposalStats {
    val attempted = mutableMapOf<ProposalType, Int>()
    val accepted = mutableMapOf<ProposalType, Int>()
    val rejected = mutableMapOf<ProposalType, Int>()
    val noProposal = mutableMapOf<ProposalType, Int>()
    
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
    }
    
    fun summary(): String {
        val types = ProposalType.entries
        return types.joinToString(" | ") { t ->
            val att = attempted[t] ?: 0
            if (att == 0) "$t: 0" else
                "$t: $att attempted (${accepted[t] ?: 0} accepted, ${rejected[t] ?: 0} rejected, ${noProposal[t] ?: 0} no-proposal)"
        }
    }
}

/**
 * Orchestrator for DAG operations, delegating to specialized components.
 */
@Service
class TaxonomyOperations(
    private val fitter: TaxonomyFitter,
    private val trickler: TaxonomyTrickler,
    private val splitter: TaxonomySplitter,
    private val merger: TaxonomyMerger,
    private val config: TaxonomyConfig
) {
    private val log = LoggerFactory.getLogger("taxonomy.Operations")
    
    private var cachedBaseJ: Double? = null
    private val rejectedProposalsCache = java.util.concurrent.ConcurrentHashMap.newKeySet<ProposalFingerprint>()
    val proposalStats = ProposalStats()
    
    fun invalidateCachedJ() {
        cachedBaseJ = null
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
                val outcome = tryProposal(dag, node, allEmbeddings, groundTruthMap, currentIteration, ProposalType.GROW) {
                    // splitSingleNode requires splitter to be called
                    splitter.splitSingleNode(node)
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
                        // legal exactly when they are residual-flagged). The previous version
                        // recorded only the naked ID — the query lost its weight (mass leaked
                        // every iteration) and its embedding never entered the region, so the
                        // residual-split mechanism could never recover it.
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
                        // Residual routing disabled entirely: preserve the old hard-assignment-to-root
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
        val populationHash = site.queryWeights.entries.map { it.key.hashCode() xor it.value.hashCode() }.sum()
        val fingerprint = ProposalFingerprint(
            nodeId = if (proposalKey != null) "${site.id}|$proposalKey" else site.id,
            populationHash = populationHash,
            muHash = site.vmfMu.contentHashCode(),
            kappaHash = site.vmfKappa
        )
        if (rejectedProposalsCache.contains(fingerprint)) {
            log.debug("[MEMOIZED REJECTION] Skip tryProposal for site '${site.label ?: site.id}'")
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

            // Re-execute action
            action()
            
            if (refitScope == null) {
                cachedBaseJ = jVal
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
        // Lexicographic objective: (J, B, -|V|)
        val deltaV = postRegistry.size - registry.size
        val deltaB = postRegistry.values.sumOf { it.crossLinkChildren.size } - registry.values.sumOf { it.crossLinkChildren.size }
        val tau = config.formalism.tau
        
        // Delta J SELECTS growth and shrink edits, but only VETOES bridges.
        //
        // The old rule accepted any J-neutral edit that added a cross-link (deltaB > 0). That
        // terminates — bridges are monotone — but it gives no account of whether a bridge is
        // worth having, and the evidence says J cannot supply one: accepted bridges spanned
        // 1e-6 to 8e-4 with the sign flipping on evaluation order, the same node being accepted
        // at four hosts and rejected at two. Selection now lives in the ambiguity fraction,
        // which is a statement about joint membership; J keeps the one job it can do here,
        // which is blocking an edge that actively degrades the partition.
        val accepted = when {
            proposalType == ProposalType.BRIDGE -> deltaJ >= -tau
            deltaJ > tau -> true
            kotlin.math.abs(deltaJ) <= tau -> deltaV < 0
            else -> false
        }

        if (accepted) {
            log.info("[$proposalType ACCEPTED] '${site.label ?: site.id}' Delta J = ${"%.6f".format(deltaJ)}, Delta V = $deltaV")
            rejectedProposalsCache.clear()
            cachedBaseJ = newJ
            proposalStats.record(proposalType, ProposalOutcome.ACCEPTED)
            return ProposalOutcome.ACCEPTED
        } else {
            if (kotlin.math.abs(deltaJ) > 1e-9) {
                log.info("[$proposalType REJECTED] '${site.label ?: site.id}' Delta J = ${"%.6f".format(deltaJ)}, Delta V = $deltaV. Reverting.")
            } else {
                log.debug("[$proposalType REJECTED] '${site.label ?: site.id}' Delta J = ${"%.6f".format(deltaJ)}, Delta V = $deltaV. Reverting.")
            }
            rejectedProposalsCache.add(fingerprint)
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
        node.nearMisses.clear()
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
     * docs/dag-chain-formation-handoff.md. Here we're only deciding what to print.
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
    val kappaHash: Double
)
