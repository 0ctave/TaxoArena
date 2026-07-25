package taxonomy.operations

import dev.langchain4j.model.chat.request.json.JsonObjectSchema
import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.coroutines.*
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.model.*
import taxonomy.prompts.TaxoPrompts
import taxonomy.utils.StatisticsUtils
import kotlin.math.sqrt

/**
 * Implements Phase 5: Optimize (Structural Refinement).
 * Polishes the DAG by deleting empty nodes, combining highly similar sibling domains,
 * creating polyhierarchical cross-links, and enforcing strict transitive reduction.
 *
 * KEY CHANGE: Cross-link edges are now stored in GraphNode.crossLinkChildren, not in
 * GraphNode.children. This preserves isLeaf = children.isEmpty() for the tree structure,
 * so the trickler correctly distributes queries to all real leaf nodes.
 */
@Service
class TaxonomyMerger(
    private val config: TaxonomyConfig,
    private val llmClient: TaxonomyLlmClient,
    private val datasetFetcher: MMLUDatasetFetcher
) {

    private var cachedAncestorMap: Map<String, Set<String>>? = null
    private var ancestorMapRootId: String? = null

    // Negative-result memo for cross-link proposals. A rejected (host, cand) pair is
    // re-generated and re-J-evaluated (a full re-route each) EVERY iteration even when
    // nothing changed — measured ~10-15 identical rejected proposals per iteration in
    // the converged tail, ~3s/iteration of pure repetition. When the edge topology
    // fingerprint AND the candidate's (captured, poolSize) counts are identical, the
    // J evaluation is deterministic, so skipping the re-evaluation is lossless. Any
    // topology change (accepted proposal, split, prune) changes the fingerprint and
    // clears the memo. Assumption made explicit: with identical topology and identical
    // routing counts, the per-iteration mu refit is at a fixed point (earlyout_rate
    // ~0.96 at convergence), so the cached rejection remains valid.
    private val rejectedCrossLinks = HashSet<String>()
    private var rejectedCrossLinksFingerprint: Int = 0

    private fun edgeTopologyFingerprint(root: GraphNode): Int {
        val edges = mutableListOf<String>()
        for (n in getAllNodes(root)) {
            n.children.forEach { edges.add("${n.id}>${it.id}") }
            n.crossLinkChildren.forEach { edges.add("${n.id}~${it.id}") }
        }
        edges.sort()
        return edges.hashCode()
    }

    private val log = LoggerFactory.getLogger("taxonomy.Merger")

    suspend fun optimizeHierarchy(
        dag: DagRoot,
        allEmbeddings: List<Embedding>,
        groundTruthMap: Map<String, List<String>>,
        currentIteration: Int = 2,
        learningPhase: Boolean = false,
        ops: TaxonomyOperations
    ) {
        val root = dag.node
        if (learningPhase) {
            pruneUnrelevantNodesWithProposals(dag, allEmbeddings, groundTruthMap, currentIteration, ops)
            prunePassthroughNodes(dag, root, allEmbeddings, groundTruthMap, currentIteration, ops)
            pruneUnrelevantNodesWithProposals(dag, allEmbeddings, groundTruthMap, currentIteration, ops)
            removeStaleParentRefs(root)
            invalidateAncestorCache()
        } else {
            pruneUnrelevantNodesWithProposals(dag, allEmbeddings, groundTruthMap, currentIteration, ops)
            mergeSimilarSiblingsWithProposals(dag, root, allEmbeddings, groundTruthMap, currentIteration, ops)

            mergeRedundantNodesWithProposals(dag, allEmbeddings, groundTruthMap, currentIteration, ops)

            do {} while (prunePassthroughNodes(dag, root, allEmbeddings, groundTruthMap, currentIteration, ops))
            pruneUnrelevantNodesWithProposals(dag, allEmbeddings, groundTruthMap, currentIteration, ops)
            removeStaleParentRefs(root)

            if (config.formalism.enableBridging) {
                proposeCrossLinksWithProposals(dag, allEmbeddings, groundTruthMap, currentIteration, ops)
            }

            invalidateAncestorCache()
            val ancestorMapFinal = buildAncestorMap(root)
            if (!config.formalism.enableResidualRouting) {
                transitiveReduction(root, ancestorMapFinal)
            }

            for (node in getAllNodes(root)) {
                // isBridge means BRIDGED — this node has more than one parent. Hosting a
                // cross-link is a different property (hasCrossLinks) and used to be folded in
                // here, which flagged 12 of the 14 depth-1 domains as bridges purely for being
                // hosts and made every "cross-domain node" count meaningless.
                node.isBridge = node.parents.size > 1
            }
        }
    }




    private fun blendVmfAndNiw(target: GraphNode, source: GraphNode) {
        val nA = target.getRecursiveQueryCount().toDouble().coerceAtLeast(1.0)
        val nB = source.getRecursiveQueryCount().toDouble().coerceAtLeast(1.0)
        val d = target.sliceDim

        // vMF Blend
        val mu = FloatArray(d) { i ->
            val valA = if (i < target.vmfMu.size) target.vmfMu[i] else 0.0f
            val valB = if (i < source.vmfMu.size) source.vmfMu[i] else 0.0f
            (nA * valA + nB * valB).toFloat()
        }
        var norm = 0.0
        for (i in 0 until d) norm += mu[i] * mu[i]
        norm = sqrt(norm)
        if (norm > 0.0) {
            for (i in 0 until d) mu[i] = (mu[i] / norm).toFloat()
        } else if (d > 0) {
            mu[0] = 1.0f
        }
        target.vmfMu = mu
        target.vmfKappa = (nA * target.vmfKappa + nB * source.vmfKappa) / (nA + nB)
        target.vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(d, target.vmfKappa)

        // NiW Blend
        target.niwKappa0 = (nA * target.niwKappa0 + nB * source.niwKappa0) / (nA + nB)
        target.niwNu0 = (nA * target.niwNu0 + nB * source.niwNu0) / (nA + nB)
        val mN = FloatArray(d) { i ->
            val valA = if (i < target.niwM0.size) target.niwM0[i] else 0.0f
            val valB = if (i < source.niwM0.size) source.niwM0[i] else 0.0f
            ((nA * valA + nB * valB) / (nA + nB)).toFloat()
        }
        target.niwM0 = mN
        val lambdaN = FloatArray(d) { i ->
            val valA = if (i < target.niwLambda.size) target.niwLambda[i] else 0.0f
            val valB = if (i < source.niwLambda.size) source.niwLambda[i] else 0.0f
            ((nA * valA + nB * valB) / (nA + nB)).toFloat()
        }
        target.niwLambda = lambdaN
    }

    private fun renormalizeQueryWeights(root: GraphNode) {
        val allNodes = mutableListOf<GraphNode>()
        val visited = mutableSetOf<String>()
        fun walk(n: GraphNode) {
            if (!visited.add(n.id)) return
            allNodes.add(n)
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)

        val totalWeights = mutableMapOf<String, Double>()
        for (node in allNodes) {
            for ((q, w) in node.queryWeights) {
                totalWeights[q] = (totalWeights[q] ?: 0.0) + w
            }
        }

        for (node in allNodes) {
            for (q in node.queryWeights.keys.toList()) {
                val tot = totalWeights[q] ?: 1.0
                if (tot > 0.0) {
                    node.queryWeights[q] = node.queryWeights[q]!! / tot
                }
            }
        }
    }

    /** Sufficient statistics of a node's whole branch population at the given dim. */
    private fun branchStats(node: GraphNode, dim: Int): StatisticsUtils.ClusterStats? {
        val branchQueries = node.getAllQueriesInBranch().distinctBy { it.rawText }
        if (branchQueries.isEmpty()) return null
        val sum = DoubleArray(dim)
        for (emb in branchQueries) {
            val v = emb.projectTo(dim)
            for (i in 0 until dim) sum[i] += v[i]
        }
        return StatisticsUtils.ClusterStats(branchQueries.size.toDouble(), sum)
    }

    /** True iff nodeId lies in the subtree rooted at start (tree + cross edges). */
    private fun isInSubtree(start: GraphNode, nodeId: String): Boolean {
        val seen = mutableSetOf<String>()
        fun dfs(n: GraphNode): Boolean {
            if (!seen.add(n.id)) return false
            if (n.id == nodeId) return true
            return n.children.any { dfs(it) } || n.crossLinkChildren.any { dfs(it) }
        }
        return dfs(start)
    }

    /** Diagnostic: total query-weight mass over reachable nodes. */
    private fun reachableMass(root: GraphNode): Double {
        var sum = 0.0
        val seen = mutableSetOf<String>()
        fun walk(n: GraphNode) {
            if (!seen.add(n.id)) return
            sum += n.queryWeights.values.sum()
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)
        return sum
    }

    private fun fuseNodes(target: GraphNode, source: GraphNode) {
        require(target.sliceDim == source.sliceDim) {
            "Cannot fuse nodes at different dims: ${target.label}(${target.sliceDim}) vs ${source.label}(${source.sliceDim})"
        }

        // The target may itself be a parent of the source (earlier fusions redirect
        // edges, so a "sibling" pair can also carry a parent-child edge). Detach that
        // edge FIRST: otherwise the redistribution below routes the source's own mass
        // back onto the source (its mu is trivially the best match for its own
        // queries) and the source-cleanup step wipes it — measured on seed 2048:
        // 229 of 275 weight units lost in a single fusion. The parent-redirect step
        // also skips parent==target, which would leave a ghost target->source edge.
        target.children.remove(source)
        target.crossLinkChildren.remove(source)
        source.parents.remove(target)

        val allQueries = (target.queries + source.queries).distinctBy { it.rawText }
        val allWeights = mutableMapOf<String, Double>()
        for ((q, w) in target.queryWeights) {
            allWeights[q] = (allWeights[q] ?: 0.0) + w
        }
        for ((q, w) in source.queryWeights) {
            allWeights[q] = (allWeights[q] ?: 0.0) + w
        }

        target.queries.clear()
        target.queryWeights.clear()
        
        val newResQueries = (target.residualQueries + source.residualQueries).distinct()
        target.residualQueries.clear()
        target.residualQueries.addAll(newResQueries)

        for ((q, c) in source.residualConfidences) {
            target.residualConfidences.putIfAbsent(q, c)
        }

        // 2. Blend parameters
        blendVmfAndNiw(target, source)

        // 3. Redirect parent edges with defensive copy — preserving edge TYPE. The old
        // code only did parent.children.remove(source) and unconditionally added target
        // as a TREE child: a parent holding source as a cross-link child kept a live
        // forward edge to the destroyed node (the trickler kept routing into the ghost,
        // which re-accumulated queries as an orphan leaf), and cross-link edges were
        // silently converted into tree edges on redirect.
        source.parents.toList().forEach { parent ->
            if (parent != target) {
                val wasTree = parent.children.remove(source)
                val wasCross = parent.crossLinkChildren.remove(source)
                // Cycle safety: the edge parent->target is only legal if parent is
                // NOT inside target's subtree. Un-vetoed redirect chains created
                // real cycles (survived routing via its cycle guard, then blew the
                // structure diff with a StackOverflowError at iteration 35).
                if (isInSubtree(target, parent.id)) {
                    log.info("[FUSE CYCLE-GUARD] dropping redirect '${parent.label}'->'${target.label}' (would create cycle)")
                } else {
                    if (wasTree) parent.children.add(target)
                    if (wasCross && !parent.children.contains(target)) parent.crossLinkChildren.add(target)
                    target.parents.add(parent)
                }
            }
        }

        // Clean up target.parents to remove degenerate ancestor parent edges
        val allParents = target.parents.toList()
        for (p1 in allParents) {
            for (p2 in allParents) {
                if (p1.id != p2.id && isAncestor(p1, p2)) {
                    target.parents.remove(p1)
                    p1.children.remove(target)
                    p1.crossLinkChildren.remove(target)
                }
            }
        }

        // 4. Redirect tree children with defensive copy (cycle-guarded: the edge
        // target->child is only legal if target is not inside child's subtree)
        source.children.toList().forEach { child ->
            if (child != target) {
                child.parents.remove(source)
                if (isInSubtree(child, target.id)) {
                    log.info("[FUSE CYCLE-GUARD] dropping redirect '${target.label}'->'${child.label}' (would create cycle)")
                } else {
                    child.parents.add(target)
                    target.children.add(child)
                }
            }
        }

        // 5. Redirect cross-link children (FIX: also handle crossLinkChildren)
        source.crossLinkChildren.toList().forEach { child ->
            if (child != target) {
                child.parents.remove(source)
                if (isInSubtree(child, target.id)) {
                    log.info("[FUSE CYCLE-GUARD] dropping cross redirect '${target.label}'->'${child.label}' (would create cycle)")
                } else {
                    child.parents.add(target)
                    target.crossLinkChildren.add(child)
                }
            }
        }

        // If target has children, distribute all queries to children to maintain internal composite separation.
        // Iterate the WEIGHT MAP, not the embedding list: queryWeights can hold keys whose
        // embedding is absent from the queries lists (soft multi-assignment / residual
        // bookkeeping). Iterating allQueries silently dropped those entries' mass — an
        // internal sibling fusion at seed 2048 lost 229.0 units this way and tripped
        // tryProposal's mass-conservation assert on the transient pre-reroute state.
        if (target.children.isNotEmpty()) {
            val activeChildren = target.children.filter { it !== source }
            val embByRaw = allQueries.associateBy { it.rawText }
            for ((raw, w) in allWeights) {
                val q = embByRaw[raw] ?: GraphNode.getEmbedding(raw)
                if (q == null) {
                    // No resolvable embedding: keep the mass at the survivor rather than drop it.
                    target.queryWeights[raw] = (target.queryWeights[raw] ?: 0.0) + w
                    continue
                }
                val bestChild = activeChildren.maxByOrNull { child ->
                    if (child.vmfMu.isEmpty()) -Double.MAX_VALUE
                    else StatisticsUtils.dotProduct(q.projectTo(child.sliceDim), child.vmfMu)
                }
                 if (bestChild != null) {
                    if (bestChild.queries.none { it.rawText == raw }) {
                        bestChild.queries.add(q)
                    }
                    bestChild.queryWeights[raw] = (bestChild.queryWeights[raw] ?: 0.0) + w
                } else {
                    if (target.queries.none { it.rawText == raw }) {
                        target.queries.add(q)
                    }
                    target.queryWeights[raw] = (target.queryWeights[raw] ?: 0.0) + w
                }
            }
        } else {
            target.queries.addAll(allQueries)
            target.queryWeights.putAll(allWeights)
        }

        // 6. Clean up source
        source.parents.clear()
        source.children.clear()
        source.crossLinkChildren.clear()
        source.queries.clear()
        source.queryWeights.clear()
        source.residualQueries.clear()
        source.residualConfidences.clear()

        // 7. Renormalize query weights across leaves of the subtree to conserve mass
        var rootNode = target
        val visitedRoot = mutableSetOf<String>()
        while (rootNode.parents.isNotEmpty()) {
            val p = rootNode.parents.first()
            if (!visitedRoot.add(p.id)) break
            rootNode = p
        }
        renormalizeQueryWeights(rootNode)
    }

    private fun pruneSingleNodeTentatively(node: GraphNode, target: GraphNode) {
        node.queries.addAll(target.queries)
        node.children.remove(target)
        node.crossLinkChildren.remove(target)
        target.parents.remove(node)
        target.parents.toList().forEach { p ->
            p.children.remove(target)
            p.crossLinkChildren.remove(target)
        }
        target.crossLinkChildren.toList().forEach { clChild ->
            clChild.parents.remove(target)
            if (clChild.treeParentId == target.id) clChild.treeParentId = null
        }
        target.crossLinkChildren.clear()
        target.children.forEach { c -> c.parents.remove(target) }
        target.children.clear()
    }


    private fun pruneUnrelevantNodes(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
        if (visited.contains(node.id)) return
        visited.add(node.id)

        val currentChildren = (node.children + node.crossLinkChildren).toList()
        for (child in currentChildren) {
            pruneUnrelevantNodes(child, visited)
        }

        // Cache branch-query counts once per child — getAllQueriesInRegion() is O(subtree).
        val allChildren = (node.children + node.crossLinkChildren).toList()
        val branchSizes = allChildren.associateWith { it.getAllQueriesInRegion().size }

        val nodesToPrune = allChildren.filter { child ->
            val totalQueriesInBranch = branchSizes[child] ?: 0
            val isTrulyDead = totalQueriesInBranch == 0

            val liveSiblings = allChildren.filter { (branchSizes[it] ?: 0) > 0 }
            val siblingAvg = if (liveSiblings.size > 1)
                liveSiblings.map { branchSizes[it] ?: 0 }.average()
            else
                allChildren.map { branchSizes[it] ?: 0 }.average()

            val isPhysicalLeaf = child.children.isEmpty() && child.crossLinkChildren.isEmpty()
            // Hard floor tied directly to minClusterSize — the same parameter that already
            // governs the split-time floor (a fresh split is rejected if any resulting cluster
            // would be smaller than this). Symmetric and elegant: no leaf should survive below
            // the size a split was ever allowed to create it at, full stop, no separate relative
            // sibling-average heuristic or extra constant needed.
            val isStarved = isPhysicalLeaf && totalQueriesInBranch < config.formalism.minClusterSize

            // wouldLeaveParentSingleChild veto removed. Traced a specific violating node
            // (Emergent Concept #66 in the 4-domain diagnostic) through the raw structural-change
            // log: each C3 violation it produced was a genuine one-iteration blip (orphaned mass
            // from a pruned sibling folded onto it, then correctly cleared and re-routed by the
            // very next trickle pass) — not a permanent deadlock. The apparent non-convergence
            // came from pruning volume: with the veto gone, far more 2-child-parent cases prune
            // per iteration, so *some* node is always mid-blip, which the GED-based convergence
            // check (needs zero structural change for 5 consecutive iterations) never tolerates
            // within a 35-iteration budget — even though every individual change is legitimate,
            // self-correcting cleanup. See numIterations note on the diagnostic config: this
            // needs a larger iteration budget to let that cleanup fully settle, not a different
            // pruning rule.
            if (child.depth <= 1) false else (isTrulyDead || isStarved)
        }

        if (nodesToPrune.isNotEmpty()) {
            nodesToPrune.forEach { target ->
                if (target.parents.isEmpty() && !node.children.contains(target) && !node.crossLinkChildren.contains(target)) return@forEach  // already pruned this pass
                log.info("[PRUNED] '${target.label}' (starved/empty)")
                node.queries.addAll(target.queries)
                node.children.remove(target)
                node.crossLinkChildren.remove(target)
                target.parents.remove(node)
                // Clean up crossLinkChildren back-refs
                target.parents.toList().forEach { p ->
                    p.children.remove(target)
                    p.crossLinkChildren.remove(target)
                }
                target.crossLinkChildren.toList().forEach { clChild ->
                    clChild.parents.remove(target)
                    if (clChild.treeParentId == target.id) clChild.treeParentId = null
                }
                target.crossLinkChildren.clear()
                target.children.forEach { c -> c.parents.remove(target) }
                target.children.clear()
            }
        }
    }



    private fun selectRepresentativeQueries(cluster: List<Embedding>): List<String> {
        if (cluster.isEmpty()) return emptyList()
        val dims = cluster[0].dimensions
        val centroid = DoubleArray(dims)
        for (emb in cluster) {
            for (d in 0 until dims) centroid[d] += emb.values[d].toDouble()
        }
        for (d in 0 until dims) centroid[d] /= cluster.size.toDouble()

        val sortedByDistance = cluster.map { it to calculateCosineDistance(it.toDoubleArray(), centroid) }
            .sortedBy { it.second }

        val n = sortedByDistance.size
        val sampleRng = kotlin.random.Random(n)
        val innerCore = sortedByDistance.take(n / 10).shuffled(sampleRng).take(7)
        val middleShell = sortedByDistance.subList(n / 10, (9 * n) / 10).shuffled(sampleRng).take(7)
        val outerBoundary = sortedByDistance.takeLast(n / 10).shuffled(sampleRng).take(6)

        return (innerCore + middleShell + outerBoundary).map { it.first.rawText }.distinct()
    }

    private class UnionFind(nodes: List<GraphNode>) {
        private val parentMap = nodes.associateWith { it }.toMutableMap()

        fun find(n: GraphNode): GraphNode {
            var curr = n
            while (parentMap[curr] != curr) {
                parentMap[curr] = parentMap[parentMap[curr]!!]!!
                curr = parentMap[curr]!!
            }
            return curr
        }

        fun union(n1: GraphNode, n2: GraphNode) {
            val root1 = find(n1)
            val root2 = find(n2)
            if (root1.id != root2.id) {
                parentMap[root1] = root2
            }
        }
    }

    private fun getDepth1Ancestor(
        node: GraphNode,
        ancestorMap: Map<String, Set<String>>,
        allNodeById: Map<String, GraphNode>
    ): String? {
        // The node itself if it's at depth 1
        if (node.depth == 1) return node.id
        // Otherwise find the ancestor at depth 1
        return ancestorMap[node.id]
            ?.mapNotNull { allNodeById[it] }
            ?.firstOrNull { it.depth == 1 }
            ?.id
    }

    /**
     * FIX (Bug 12): Cross-links are stored in crossLinkChildren, NOT in children.
     *
     * Before this fix: potentialParent.children.add(node) caused isLeaf = false on
     * any node that received a cross-link, routing all trickled queries to the one
     * node with a genuinely empty children set.
     *
     * After this fix: isLeaf = children.isEmpty() is unaffected by cross-links.
     * All tree leaf nodes remain leaves. The trickler distributes correctly.
     */


    /**
     * FIX: transitiveReduction must consider BOTH children and crossLinkChildren.
     * Tree parent protection (treeParentId) still applies.
     * Redundant parents are removed from BOTH sets.
     */
    internal fun transitiveReduction(root: GraphNode, ancestorMap: Map<String, Set<String>>) {
        val allNodes = getAllNodes(root)
        var keptEdges = 0
        var severedShortcuts = 0
        for (node in allNodes) {
            val redundantParents = node.parents.filter { p1 ->
                if (node.isBridge || p1.isBridge) return@filter false
                if (node.treeParentId == p1.id) {
                    keptEdges++
                    return@filter false
                }
                val p1Ancestors = ancestorMap[p1.id] ?: return@filter false
                node.parents.any { p2 ->
                    !p2.isBridge && p1.id != p2.id && p1.id in (ancestorMap[p2.id] ?: emptySet())
                }
            }
            for (rp in redundantParents) {
                severedShortcuts++
                node.parents.remove(rp)
                rp.children.remove(node)
                rp.crossLinkChildren.remove(node)
            }
        }
        if (severedShortcuts > 0) {
            log.info("[TR] Severed $severedShortcuts shortcuts ($keptEdges edges kept)")
        } else {
            log.debug("[TR] Severed $severedShortcuts shortcuts ($keptEdges edges kept)")
        }
    }

    /**
     * Removes any parent references that point to nodes no longer in the DAG.
     * Must run after pruning/collapsing and before transitiveReduction.
     */
    private fun removeStaleParentRefs(root: GraphNode) {
        val allNodes = getAllNodes(root)
        val allIds = allNodes.map { it.id }.toSet()
        for (node in allNodes) {
            val stale = node.parents.filter { it.id !in allIds }
            for (s in stale) {
                log.debug("[STALE-REF] Removing ghost parent '${s.label}' from '${node.label}'")
                node.parents.remove(s)
            }
        }
    }

    private suspend fun prunePassthroughNodes(
        dag: DagRoot,
        node: GraphNode,
        allEmbeddings: List<Embedding>,
        groundTruthMap: Map<String, List<String>>,
        currentIteration: Int,
        ops: TaxonomyOperations,
        visited: MutableSet<String> = mutableSetOf()
    ): Boolean {
        if (visited.contains(node.id)) return false
        visited.add(node.id)

        var anyPruned = false

        val currentChildren = node.treeChildren.toList()
        for (child in currentChildren) {
            if (prunePassthroughNodes(dag, child, allEmbeddings, groundTruthMap, currentIteration, ops, visited)) anyPruned = true
        }

        while (node.treeChildren.size == 1) {
            val child = node.treeChildren.first()
            if (child.depth <= 1 || child.parents.size > 1) break

            val collapsed = ops.tryProposal(dag = dag, site = node, allEmbeddings = allEmbeddings, groundTruthMap = groundTruthMap, currentIteration = currentIteration, proposalType = ProposalType.SHRINK) {
                log.info("[COLLAPSE] dissolving sole child '${child.label}' into '${node.label}' (${child.treeChildren.size} grandchildren hoisted)")
                
                node.queries = (node.queries + child.queries).distinctBy { it.rawText }.toMutableList()
                for ((q, w) in child.queryWeights) {
                    node.queryWeights[q] = maxOf(node.queryWeights[q] ?: 0.0, w)
                }
                
                val newResQueries = (node.residualQueries + child.residualQueries).distinct()
                node.residualQueries.clear()
                node.residualQueries.addAll(newResQueries)

                for ((q, c) in child.residualConfidences) {
                    node.residualConfidences.putIfAbsent(q, c)
                }

                node.children.remove(child)
                child.treeChildren.toList().forEach { grandchild ->
                    node.children.add(grandchild)
                    grandchild.parents.remove(child)
                    grandchild.parents.add(node)
                    if (grandchild.treeParentId == child.id) {
                        grandchild.treeParentId = node.id
                    }
                    recomputeDepths(grandchild, node.depth + 1)
                }

                child.crossLinkChildren.toList().forEach { clChild ->
                    clChild.parents.remove(child)
                    if (!clChild.parents.contains(node)) {
                        clChild.parents.add(node)
                        node.crossLinkChildren.add(clChild)
                    }
                }

                child.parents.clear()
                child.children.clear()
                child.crossLinkChildren.clear()
                child.queries.clear()
                child.queryWeights.clear()
                child.residualQueries.clear()
                child.residualConfidences.clear()
                true
            }
            if (collapsed == ProposalOutcome.ACCEPTED) {
                anyPruned = true
            } else {
                break
            }
        }

        // Hard queries held by an internal node must carry the residual flag so the
        // C3 invariant stays satisfied until the next trickle re-routes them.
        if (node.treeChildren.isNotEmpty() && node.queries.isNotEmpty()) {
            for (emb in node.queries) {
                val qId = if (emb.queryId != -1) emb.queryId.toString() else emb.rawText
                if (node.residualQueries.add(qId)) {
                    node.residualConfidences.putIfAbsent(qId, 0.0)
                }
            }
        }

        return anyPruned
    }

    /**
     * FIX: getAllNodes must walk BOTH children AND crossLinkChildren so that
     * cross-linked nodes are included in ancestor maps and transitive reduction.
     */
    private fun getAllNodes(node: GraphNode, visited: MutableSet<GraphNode> = mutableSetOf()): Set<GraphNode> {
        if (visited.contains(node)) return visited
        visited.add(node)
        node.children.forEach { getAllNodes(it, visited) }
        node.crossLinkChildren.forEach { getAllNodes(it, visited) }
        return visited
    }

    internal fun buildAncestorMap(root: GraphNode): Map<String, Set<String>> {
        if (root.id == ancestorMapRootId && cachedAncestorMap != null) {
            return cachedAncestorMap!!
        }

        val ancestorMap = mutableMapOf<String, Set<String>>()
        val allNodes = getAllNodes(root)

        for (node in allNodes) {
            val ancestors = mutableSetOf<String>()
            fun collect(n: GraphNode) {
                n.parents.forEach { parent ->
                    if (ancestors.add(parent.id)) {
                        collect(parent)
                    }
                }
            }
            collect(node)
            ancestorMap[node.id] = ancestors
        }

        cachedAncestorMap = ancestorMap
        ancestorMapRootId = root.id

        return ancestorMap
    }

    fun invalidateAncestorCache() { cachedAncestorMap = null }


    private fun calculateCosineDistance(v1: DoubleArray, v2: DoubleArray): Double {
        var dotProduct = 0.0
        var norm1 = 0.0
        var norm2 = 0.0
        for (i in v1.indices) {
            dotProduct += v1[i] * v2[i]
            norm1 += v1[i] * v1[i]
            norm2 += v2[i] * v2[i]
        }
        val similarity = if (norm1 > 0 && norm2 > 0) dotProduct / (sqrt(norm1) * sqrt(norm2)) else 0.0
        return 1.0 - similarity
    }

    private fun recomputeDepths(node: GraphNode, newDepth: Int, visited: MutableSet<String> = mutableSetOf()) {
        if (!visited.add(node.id)) return
        val oldSliceDim = node.sliceDim
        node.depth = newDepth
        node.sliceDim = dimForDepth(newDepth)
        // If the embedding dimension changed, the stored vmfMu is the wrong size.
        // Clear PHASE_VMF_FIT so the fitter recomputes it before the next split/trickle.
        if (node.sliceDim != oldSliceDim) {
            node.phaseCompleted = node.phaseCompleted and PHASE_VMF_FIT.inv()
        }
        node.children.forEach { recomputeDepths(it, newDepth + 1, visited) }
    }

    private fun logBridgeResidual(
        iteration: Int,
        candidateId: String,
        sourceNodes: String,
        size: Int,
        entropy: Double,
        div: Double,
        accepted: Boolean,
        reason: String
    ) {
        val baseDir = taxonomy.model.ExperimentOutputContext.activeBaseDir ?: java.io.File(".")
        val csvFile = java.io.File(baseDir, "bridge_candidates.csv")
        synchronized(this) {
            val exists = csvFile.exists()
            java.io.FileWriter(csvFile, true).use { fw ->
                if (!exists) {
                    fw.write("iteration,candidate_id,source_nodes,size,entropy,div,accepted,reason\n")
                }
                val escNodes = "\"${sourceNodes.replace("\"", "\"\"")}\""
                val escReason = "\"${reason.replace("\"", "\"\"")}\""
                fw.write("$iteration,$candidateId,$escNodes,$size,${"%.4f".format(java.util.Locale.US, entropy)},${"%.4f".format(java.util.Locale.US, div)},$accepted,$escReason\n")
            }
        }
    }

    /**
     * Cross-linking: the polyhierarchy GROWTH edit, generated from residual mass.
     *
     * fuseNodes is a shrink edit — it destroys one node identity and produces multi-parent
     * bridges only as a side effect of redirecting the dead node's parents. A cross-link is
     * the opposite: both identities survive, and a node N gains a SECOND parent P because
     * P's residual queries demonstrably fit N. The Jensen-tight descent gate residualizes
     * queries that sit near a region's centre but match none of its children — under a
     * strict tree a genuinely cross-domain query (biostatistics between Math and Biology)
     * can only pick one branch, fail to specialize there, and residualize. A cross-link
     * gives it a legitimate second path: once N is in P's competition set, exactly the
     * residuals with <mu_N, x> >= r_bar_P * <mu_P, x> start passing P's descent gate.
     *
     * Candidate generation is cheap (no re-routing): for each host P with a residual pool,
     * count the residuals N would capture under the runtime gate formula. A candidate
     * survives iff it captures >= secondaryMassFloor queries AND >= bridgeSupportRelFraction
     * of P's pool. Guards: acyclicity (N must not be an ancestor of P), no
     * ancestor/descendant or existing-parent redundancy (a grandparent link is the old #67
     * degeneracy), and cross-domain-ness (P and N must live under disjoint depth-1 domains
     * — an intra-branch second parent is exactly what transitive reduction exists to kill).
     * Acceptance is the same global-J proposal gate as every other structural edit, with
     * the SPLIT-side positive threshold: a growth edit must strictly improve J
     * (shrink edits only need Delta J > -epsilon).
     */
    internal suspend fun proposeCrossLinksWithProposals(
        dag: DagRoot,
        allEmbeddings: List<Embedding>,
        groundTruthMap: Map<String, List<String>>,
        currentIteration: Int,
        ops: TaxonomyOperations
    ) {
        val root = dag.node
        val allNodes = getAllNodes(root).toList()

        // Rejection memo: valid only while the edge topology is unchanged.
        val fingerprint = edgeTopologyFingerprint(root)
        if (fingerprint != rejectedCrossLinksFingerprint) {
            rejectedCrossLinks.clear()
            rejectedCrossLinksFingerprint = fingerprint
        }

        val embById = HashMap<String, Embedding>(allEmbeddings.size * 2)
        for (emb in allEmbeddings) {
            val key = if (emb.queryId != -1) emb.queryId.toString() else emb.rawText
            embById[key] = emb
        }

        val minMisses = 5
        val hosts = allNodes.filter { p ->
            p.depth >= 1 && p.children.isNotEmpty() && p.vmfMu.isNotEmpty() &&
                p.nearMisses.size >= minMisses
        }

        // ── Phase A: score every (host, candidate) edge against ONE pre-pass state ─────────
        //
        // Scoring and evaluation are separated deliberately. The previous version walked hosts
        // sequentially and evaluated each host's top-3 immediately, so every acceptance changed
        // the state the next proposal was measured against — the same node was accepted at four
        // hosts and rejected at two, with the sign decided by visit order, and it accumulated
        // five parents that way. Ranking the whole field against a single snapshot makes the
        // pass order-independent; the guards are still re-checked at evaluation time, because
        // an acceptance can legitimately invalidate a later edge.
        val prePassAncestors = buildAncestorMap(root)
        val scoredEdges = ArrayList<Triple<GraphNode, GraphNode, Double>>()
        val allF = ArrayList<Double>()

        for (host in hosts) {
            val hostDomains = getDepth1Ancestors(host)
            val hostAnc = prePassAncestors[host.id] ?: emptySet()
            val attached = host.children + host.crossLinkChildren

            for (cand in allNodes) {
                if (cand === host || cand.depth < 2 || cand.vmfMu.isEmpty()) continue
                if (cand.parents.isEmpty()) continue
                if (cand in attached || host in cand.parents) continue
                val candAnc = prePassAncestors[cand.id] ?: emptySet()
                if (host.id in candAnc || cand.id in hostAnc) continue
                if (cand.parents.any { q -> q.id in hostAnc || host.id in (prePassAncestors[q.id] ?: emptySet()) }) continue
                if (getDepth1Ancestors(cand).any { it in hostDomains }) continue
                // A concept under half the corpus's domains is under-specified, not
                // cross-domain. Structural bound, not a tuned one.
                if (cand.parents.size >= config.formalism.maxParentsPerNode) continue

                val f = ambiguityFraction(cand, host) ?: continue
                allF.add(f)
                if (f >= config.formalism.bridgeAmbiguityFloor) {
                    scoredEdges.add(Triple(host, cand, f))
                }
            }
        }

        // Calibration dump over the FULL scored field — before any floor or top-k cut, so
        // bridgeAmbiguityFloor is chosen against the whole distribution rather than the tail
        // that already survived selection.
        if (allF.isNotEmpty()) {
            val hist = IntArray(10)
            for (f in allF) hist[(f * 10).toInt().coerceIn(0, 9)]++
            val sorted = allF.sorted()
            log.info("[F-HIST] scored=${allF.size} deciles=[${hist.joinToString(",")}] " +
                "median=${"%.3f".format(sorted[sorted.size / 2])} p90=${"%.3f".format(sorted[(sorted.size * 9) / 10])} " +
                "passing(f>=${config.formalism.bridgeAmbiguityFloor})=${scoredEdges.size}")
        }

        // ── Phase B: evaluate best-first, one edge per host ────────────────────────────────
        scoredEdges.sortByDescending { it.third }
        val hostsUsed = HashSet<String>()

        for ((host, cand, f) in scoredEdges) {
            // One candidate per host per pass: with f doing the selecting, the second- and
            // third-best are by construction weaker claims of joint membership, and taking
            // three per host is what fixed the bridge count at 3 x |hosts| regardless of merit.
            if (!hostsUsed.add(host.id)) continue

            // Re-check against the LIVE graph: an earlier acceptance in this pass may have
            // changed ancestor sets or filled the candidate's parent budget.
            invalidateAncestorCache()
            val live = buildAncestorMap(root)
            val candAnc = live[cand.id] ?: emptySet()
            val hostAnc = live[host.id] ?: emptySet()
            if (host.id in candAnc || cand.id in hostAnc || host in cand.parents) continue
            if (cand.parents.size >= config.formalism.maxParentsPerNode) continue

            val memoKey = "${host.id}>${cand.id}#${"%.3f".format(f)}"
            if (memoKey in rejectedCrossLinks) {
                log.debug("[CROSS-LINK] memo-skip '${host.label}' -> '${cand.label}' (f=${"%.3f".format(f)})")
                continue
            }

            log.info("[CROSS-LINK] proposing '${host.label}' -> '${cand.label}' " +
                "(f=${"%.3f".format(f)} of ${cand.queries.size} own queries, parents=${cand.parents.size})")
            val refitScope = { _: GraphNode ->
                val toRefit = mutableSetOf(cand)
                toRefit.addAll(cand.parents)
                for (p in cand.parents) {
                    toRefit.addAll(p.children)
                    toRefit.addAll(p.crossLinkChildren)
                }
                for (n in toRefit) {
                    ops.fitSingleNode(n, isFinalIteration = false)
                }
            }
            val accepted = ops.tryProposal(
                dag = dag,
                site = cand,
                allEmbeddings = allEmbeddings,
                groundTruthMap = groundTruthMap,
                currentIteration = currentIteration,
                proposalType = ProposalType.BRIDGE,
                refitScope = refitScope,
                // A cross-link is the pair, not the target: without the host in the
                // memo key every host after the first is skipped unevaluated.
                proposalKey = "bridge:${host.id}"
            ) {
                host.crossLinkChildren.add(cand)
                cand.parents.add(host)
                true
            }
            logBridgeResidual(
                iteration = currentIteration,
                candidateId = "${host.id}->${cand.id}",
                sourceNodes = "${host.label} -> ${cand.label}",
                size = cand.queries.size,
                entropy = f,
                div = 0.0,
                accepted = accepted == ProposalOutcome.ACCEPTED,
                reason = "ambiguity-fraction cross-link"
            )
            if (accepted == ProposalOutcome.ACCEPTED) {
                rejectedCrossLinks.clear()
                rejectedCrossLinksFingerprint = edgeTopologyFingerprint(root)
            } else {
                rejectedCrossLinks.add(memoKey)
            }
        }
        invalidateAncestorCache()
    }

    /**
     * The ambiguity fraction: of the candidate concept's OWN queries, what share does the
     * prospective parent explain at least as well as the concept's current best parent?
     *
     *   f = |{ q in queries(N) : <mu_host, x_q> >= max_p <mu_p, x_q> - gamma }| / |queries(N)|
     *
     * Anchored on N, comparing two parents head to head. The previous formulation anchored on
     * the HOST's near-miss ledger, which is the set of queries that barely belonged at the host
     * — precisely the queries for which <mu_host, x> is low, hence the bar low, hence almost
     * any plausible centroid cleared it. That test asked "does this candidate beat the host's
     * weakest grip on its own leftovers?" and was true by construction: accepted and rejected
     * proposals were distributionally indistinguishable (medians 0.802 vs 0.818, r with dJ =
     * +0.085). This one asks whether the concept's content genuinely belongs to both, which is
     * the claim a polyhierarchy edge actually makes.
     *
     * gamma reuses descentMargin — the same cosine slack the trickler already allows when
     * deciding a query may descend — rather than introducing another knob.
     */
    private fun ambiguityFraction(cand: GraphNode, host: GraphNode): Double? {
        val qs = cand.queries
        if (qs.isEmpty()) return null
        val parents = cand.parents.filter { it.vmfMu.isNotEmpty() }
        if (parents.isEmpty()) return null
        val gamma = config.formalism.descentMargin
        var hits = 0
        for (q in qs) {
            val xHost = q.projectTo(host.vmfMu.size)
            val hostDot = StatisticsUtils.dotProduct(xHost, host.vmfMu)
            var bestParentDot = Double.NEGATIVE_INFINITY
            for (p in parents) {
                val xp = q.projectTo(p.vmfMu.size)
                val d = StatisticsUtils.dotProduct(xp, p.vmfMu)
                if (d > bestParentDot) bestParentDot = d
            }
            if (hostDot >= bestParentDot - gamma) hits++
        }
        return hits.toDouble() / qs.size
    }

    private fun isAncestor(ancestor: GraphNode, descendant: GraphNode): Boolean {
        val visited = mutableSetOf<String>()
        fun check(curr: GraphNode): Boolean {
            if (curr.id == descendant.id) return true
            if (!visited.add(curr.id)) return false
            return curr.children.any { check(it) } || curr.crossLinkChildren.any { check(it) }
        }
        return check(ancestor)
    }

    fun collectAllLeaves(root: GraphNode): List<GraphNode> {
        val leaves = mutableListOf<GraphNode>()
        val visited = mutableSetOf<String>()
        fun walk(node: GraphNode) {
            if (!visited.add(node.id)) return
            if (node.isLeaf) leaves.add(node)
            else {
                node.children.forEach { walk(it) }
                node.crossLinkChildren.forEach { walk(it) }
            }
        }
        walk(root)
        return leaves
    }

    fun getDepth1Ancestors(node: GraphNode, policy: taxonomy.model.TraversalPolicy = taxonomy.model.TraversalPolicy.TREE_ONLY): Set<String> {
        val ancestors = mutableSetOf<String>()
        val visited   = mutableSetOf<String>()
        fun walk(n: GraphNode) {
            if (!visited.add(n.id)) return
            if (n.depth == 1) {
                (n.originalCategory ?: n.label)?.let { ancestors.add(it) }
            } else {
                when (policy) {
                    taxonomy.model.TraversalPolicy.TREE_ONLY -> {
                        val treeParent = n.parents.find { it.id == n.treeParentId } ?: n.parents.firstOrNull()
                        if (treeParent != null) {
                            walk(treeParent)
                        }
                    }
                    taxonomy.model.TraversalPolicy.BRIDGE_ONLY -> {
                        n.parents.filter { it.isBridge }.forEach { walk(it) }
                    }
                    taxonomy.model.TraversalPolicy.DAG_BOTH -> {
                        n.parents.forEach { walk(it) }
                    }
                }
            }
        }
        walk(node)
        return ancestors
    }

    private fun calculateGtEntropy(queries: List<Embedding>): Double {
        val counts = HashMap<String, Int>()
        for (q in queries) {
            val cat = datasetFetcher.getDetailsForQuery(q.rawText)?.category ?: continue
            counts[cat] = (counts[cat] ?: 0) + 1
        }
        val total = counts.values.sum().toDouble()
        if (total == 0.0) return 0.0
        var entropy = 0.0
        for (count in counts.values) {
            val p = count.toDouble() / total
            entropy -= p * kotlin.math.log2(p)
        }
        return entropy
    }

    private fun projectDoubleVector(vec: DoubleArray, targetDim: Int): DoubleArray {
        if (vec.size == targetDim) return vec.copyOf()
        val sliced = vec.copyOf(targetDim)
        var norm2 = 0.0
        for (v in sliced) norm2 += v * v
        val norm = kotlin.math.sqrt(norm2)
        return if (norm > 0.0) DoubleArray(targetDim) { sliced[it] / norm } else sliced
    }

    suspend fun pruneUnrelevantNodesWithProposals(
        dag: DagRoot,
        allEmbeddings: List<Embedding>,
        groundTruthMap: Map<String, List<String>>,
        currentIteration: Int,
        ops: TaxonomyOperations
    ) {
        val root = dag.node
        val visited = mutableSetOf<String>()
        val leaves = mutableListOf<GraphNode>()

        fun walkCollect(node: GraphNode) {
            if (!visited.add(node.id)) return
            if (node.isLeaf && node.depth > 1) {
                val mass = node.getAllQueriesInRegion().size
                if (mass < config.formalism.minClusterSize) {
                    leaves.add(node)
                }
            }
            node.children.forEach { walkCollect(it) }
        }
        walkCollect(root)

        val registry = mutableMapOf<String, GraphNode>()
        fun walkReg(n: GraphNode) {
            if (registry.containsKey(n.id)) return
            registry[n.id] = n
            n.children.forEach { walkReg(it) }
            n.crossLinkChildren.forEach { walkReg(it) }
        }
        walkReg(root)

        for (child in leaves) {
            val parent = child.parents.firstOrNull() ?: continue


            // Keep L as is (Proposal 3 / Base)
            val baseJ = StatisticsUtils.computeDagSeparationJ(root, allEmbeddings)

            // Proposal 1: Prune/Absorb child into parent
            val backupPrune = GraphStateBackup(root)
            pruneSingleNodeTentatively(parent, child)
            root.updateAllShrinkages()
            ops.clearGraphQueries(root)
            ops.reassignQueries(dag, allEmbeddings, groundTruthMap, currentIteration)
            val J_prune = StatisticsUtils.computeDagSeparationJ(root, allEmbeddings)
            backupPrune.restore(registry)

            // Proposal 2: Merge child into nearest sibling
            val siblings = parent.children.filter { it.id != child.id }
            val nearestSibling = siblings.maxByOrNull { sib ->
                if (child.vmfMu.isEmpty() || sib.vmfMu.isEmpty()) -Double.MAX_VALUE
                else StatisticsUtils.dotProduct(child.vmfMu.map { it.toDouble() }.toDoubleArray(), sib.vmfMu)
            }
            var J_merge = Double.NEGATIVE_INFINITY
            var backupMerge: GraphStateBackup? = null
            if (nearestSibling != null) {
                backupMerge = GraphStateBackup(root)
                fuseNodes(nearestSibling, child)
                root.updateAllShrinkages()
                ops.clearGraphQueries(root)
                ops.reassignQueries(dag, allEmbeddings, groundTruthMap, currentIteration)
                val J_merge_val = StatisticsUtils.computeDagSeparationJ(root, allEmbeddings)
                J_merge = J_merge_val
                backupMerge.restore(registry)
            }

            val bestJ = maxOf(baseJ, J_prune, J_merge)
            if (bestJ == baseJ) {
                log.debug("Starved Node: Keeping '${child.label}' (best option)")
            } else if (bestJ == J_prune) {
                pruneSingleNodeTentatively(parent, child)
                log.info("[ACCEPTED STARVED PRUNE] '${child.label}' pruned into '${parent.label}' (Delta J: ${J_prune - baseJ})")
                root.updateAllShrinkages()
                ops.clearGraphQueries(root)
                ops.reassignQueries(dag, allEmbeddings, groundTruthMap, currentIteration)
            } else if (bestJ == J_merge && nearestSibling != null) {
                fuseNodes(nearestSibling, child)
                log.info("[ACCEPTED STARVED MERGE] '${child.label}' merged into '${nearestSibling.label}' (Delta J: ${J_merge - baseJ})")
                root.updateAllShrinkages()
                ops.clearGraphQueries(root)
                ops.reassignQueries(dag, allEmbeddings, groundTruthMap, currentIteration)
            }
        }

        pruneDeadInternalNodes(root)
    }

    private suspend fun mergeSimilarSiblingsWithProposals(
        dag: DagRoot,
        node: GraphNode,
        allEmbeddings: List<Embedding>,
        groundTruthMap: Map<String, List<String>>,
        currentIteration: Int,
        ops: TaxonomyOperations,
        visited: MutableSet<String> = java.util.concurrent.ConcurrentHashMap.newKeySet()
    ) {
        if (visited.contains(node.id)) return
        visited.add(node.id)

        val currentChildren = node.children.toList()
        currentChildren.forEach { child ->
            mergeSimilarSiblingsWithProposals(dag, child, allEmbeddings, groundTruthMap, currentIteration, ops, visited)
        }

        val children = node.children.toList()
        if (children.size < 2) return

        val statsDim = dimForDepth(node.depth + 1)
        val statsByChild = children.associateWith { child ->
            val branchQueries = child.getAllQueriesInBranch().distinctBy { it.rawText }
            if (branchQueries.isEmpty()) null else {
                val sum = DoubleArray(statsDim)
                for (emb in branchQueries) {
                    val v = emb.projectTo(statsDim)
                    for (i in 0 until statsDim) sum[i] += v[i]
                }
                StatisticsUtils.ClusterStats(branchQueries.size.toDouble(), sum)
            }
        }

        val pairsToMerge = mutableListOf<Triple<GraphNode, GraphNode, Double>>()
        for (i in 0 until children.size) {
            for (j in i + 1 until children.size) {
                val nodeA = children[i]
                val nodeB = children[j]
                if (nodeA.depth <= 1 || nodeB.depth <= 1) continue
                val statsA = statsByChild[nodeA] ?: continue
                val statsB = statsByChild[nodeB] ?: continue
                val sep = StatisticsUtils.chanceCorrectedSeparation(listOf(statsA, statsB))
                if (sep < config.formalism.proposalSeparationBar) pairsToMerge.add(Triple(nodeA, nodeB, sep))
            }
        }

        if (pairsToMerge.isEmpty()) return

        val uf = UnionFind(children)
        for ((nodeA, nodeB, _) in pairsToMerge) {
            uf.union(nodeA, nodeB)
        }

        val clusters = children.groupBy { uf.find(it) }.values.filter { it.size > 1 }
        if (clusters.isEmpty()) return

        for (cluster in clusters) {
            val target = cluster[0]
            val sources = cluster.subList(1, cluster.size)
            ops.tryProposal(dag = dag, site = node, allEmbeddings = allEmbeddings, groundTruthMap = groundTruthMap, currentIteration = currentIteration, proposalType = ProposalType.SHRINK) {
                for (source in sources) {
                    fuseNodes(target, source)
                }
                true
            }
        }
    }

    private suspend fun mergeRedundantNodesWithProposals(
        dag: DagRoot,
        allEmbeddings: List<Embedding>,
        groundTruthMap: Map<String, List<String>>,
        currentIteration: Int,
        ops: TaxonomyOperations
    ) {
        val root = dag.node
        val allNodes = getAllNodes(root).toList()
        for (i in 0 until allNodes.size) {
            for (j in i + 1 until allNodes.size) {
                if (i >= allNodes.size || j >= allNodes.size) continue
                val nodeA = allNodes[i]
                val nodeB = allNodes[j]
                if (nodeA.depth <= 1 || nodeB.depth <= 1) continue
                if (nodeA.parents.isEmpty() || nodeB.parents.isEmpty()) continue
                if (isAncestor(nodeA, nodeB) || isAncestor(nodeB, nodeA)) continue

                val commonDim = minOf(nodeA.sliceDim, nodeB.sliceDim)
                if (commonDim == 0 || nodeA.vmfMu.isEmpty() || nodeB.vmfMu.isEmpty()) continue
                val muA = StatisticsUtils.projectVector(nodeA.vmfMu, commonDim)
                val muB = nodeB.vmfMu.copyOf(commonDim)
                val similarity = StatisticsUtils.dotProduct(muA.map { it.toDouble() }.toDoubleArray(), muB)
                if (similarity <= config.formalism.fusionSimilarityThreshold) continue

                // Gate consistency: mu-cosine is only a cheap O(n^2) PREFILTER; the
                // decision uses the same pairwise chance-corrected separation, on the
                // same bar, that the splitter requires to create a pair and that
                // sibling fusion uses to destroy one. Deciding on cosine alone let this
                // pass destroy pairs the splitter had just certified separable (the
                // shared-mean direction inflates cosine — the same geometry that makes
                // uncentered EM collapse), so creation and destruction disagreed and
                // the pair cycled. With one statistic at one bar the two acceptance
                // regions are disjoint: nothing creatable is destroyable.
                val statsA = branchStats(nodeA, commonDim)
                val statsB = branchStats(nodeB, commonDim)
                if (statsA == null || statsB == null) continue
                val pairSep = StatisticsUtils.chanceCorrectedSeparation(listOf(statsA, statsB))
                if (pairSep < config.formalism.proposalSeparationBar) {
                    ops.tryProposal(dag = dag, site = root, allEmbeddings = allEmbeddings, groundTruthMap = groundTruthMap, currentIteration = currentIteration, proposalType = ProposalType.SHRINK) {
                        fuseNodes(nodeA, nodeB)
                        true
                    }
                }
            }
        }
    }

    private fun pruneDeadInternalNodes(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
        if (!visited.add(node.id)) return
        val currentChildren = node.children.toList()
        for (child in currentChildren) {
            pruneDeadInternalNodes(child, visited)
        }
        val targetPrunes = node.children.filter { it.depth > 1 && it.children.isEmpty() && it.crossLinkChildren.isEmpty() && it.getAllQueriesInRegion().isEmpty() }
        targetPrunes.forEach { target ->
            node.children.remove(target)
            target.parents.remove(node)
            log.info("[CLEANUP PRUNED] Empty dead internal node '${target.label}' removed")
        }
    }
}
