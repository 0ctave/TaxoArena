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

            if (config.formalism.enableBridging) {
                insertBridgingParents(root, currentIteration)
            }

            mergeRedundantNodesWithProposals(dag, allEmbeddings, groundTruthMap, currentIteration, ops)

            do {} while (prunePassthroughNodes(dag, root, allEmbeddings, groundTruthMap, currentIteration, ops))
            pruneUnrelevantNodesWithProposals(dag, allEmbeddings, groundTruthMap, currentIteration, ops)
            removeStaleParentRefs(root)

            invalidateAncestorCache()
            val ancestorMapFinal = buildAncestorMap(root)
            transitiveReduction(root, ancestorMapFinal)

            for (node in getAllNodes(root)) {
                if (node.parents.size > 1 || node.crossLinkChildren.isNotEmpty()) {
                    node.isBridge = true
                }
            }
        }
    }

    fun prunePassthroughNodesPublic(root: GraphNode) {
        // Ignored or left as no-op/dummy, or we can use empty args
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

    private fun fuseNodes(target: GraphNode, source: GraphNode) {
        require(target.sliceDim == source.sliceDim) {
            "Cannot fuse nodes at different dims: ${target.label}(${target.sliceDim}) vs ${source.label}(${source.sliceDim})"
        }

        val allQueries = (target.queries + source.queries).distinctBy { it.rawText }
        val allWeights = mutableMapOf<String, Double>()
        for ((q, w) in target.queryWeights) {
            allWeights[q] = maxOf(allWeights[q] ?: 0.0, w)
        }
        for ((q, w) in source.queryWeights) {
            allWeights[q] = maxOf(allWeights[q] ?: 0.0, w)
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

        // 3. Redirect tree parents with defensive copy
        source.parents.toList().forEach { parent ->
            if (parent != target) {
                parent.children.remove(source)
                parent.children.add(target)
                target.parents.add(parent)
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

        // 4. Redirect tree children with defensive copy
        source.children.toList().forEach { child ->
            if (child != target) {
                child.parents.remove(source)
                child.parents.add(target)
                target.children.add(child)
            }
        }

        // 5. Redirect cross-link children (FIX: also handle crossLinkChildren)
        source.crossLinkChildren.toList().forEach { child ->
            if (child != target) {
                child.parents.remove(source)
                child.parents.add(target)
                target.crossLinkChildren.add(child)
            }
        }

        // If target has children, distribute all queries to children to maintain internal composite separation
        if (target.children.isNotEmpty()) {
            val activeChildren = target.children.toList()
            for (q in allQueries) {
                val w = allWeights[q.rawText] ?: 1.0
                val bestChild = activeChildren.maxByOrNull { child ->
                    if (child.vmfMu.isEmpty()) -Double.MAX_VALUE
                    else StatisticsUtils.dotProduct(q.projectTo(child.sliceDim), child.vmfMu)
                }
                 if (bestChild != null) {
                    if (!bestChild.queries.contains(q)) {
                        bestChild.queries.add(q)
                    }
                    bestChild.queryWeights[q.rawText] = maxOf(bestChild.queryWeights[q.rawText] ?: 0.0, w)
                } else {
                    if (!target.queries.contains(q)) {
                        target.queries.add(q)
                    }
                    target.queryWeights[q.rawText] = maxOf(target.queryWeights[q.rawText] ?: 0.0, w)
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
        val innerCore = sortedByDistance.take(n / 10).shuffled().take(7)
        val middleShell = sortedByDistance.subList(n / 10, (9 * n) / 10).shuffled().take(7)
        val outerBoundary = sortedByDistance.takeLast(n / 10).shuffled().take(6)

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

            val collapsed = ops.tryProposal(dag = dag, site = node, allEmbeddings = allEmbeddings, groundTruthMap = groundTruthMap, currentIteration = currentIteration, deltaThreshold = -config.formalism.separationEpsilon) {
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
            }
            if (collapsed) {
                anyPruned = true
            } else {
                break
            }
        }

        // Hard queries held by an internal node must carry the residual flag so the
        // C3 invariant stays satisfied until the next trickle re-routes them.
        if (node.treeChildren.isNotEmpty() && node.queries.isNotEmpty()) {
            for (emb in node.queries) {
                val qId = if (emb.queryId != -1) emb.queryId.toString() else TextNormalizer.cleanText(emb.rawText)
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

    internal suspend fun insertBridgingParents(root: GraphNode, iteration: Int) {
        // No-op: mergeRedundantNodes deleted
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
            val deltaThreshold = -config.formalism.separationEpsilon

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
            } else if (bestJ == J_prune && J_prune > baseJ + deltaThreshold) {
                pruneSingleNodeTentatively(parent, child)
                log.info("[ACCEPTED STARVED PRUNE] '${child.label}' pruned into '${parent.label}' (Delta J: ${J_prune - baseJ})")
                root.updateAllShrinkages()
                ops.clearGraphQueries(root)
                ops.reassignQueries(dag, allEmbeddings, groundTruthMap, currentIteration)
            } else if (bestJ == J_merge && J_merge > baseJ + deltaThreshold && nearestSibling != null) {
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

        val siblingMergeThreshold = config.formalism.separationEpsilon
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
                if (sep < siblingMergeThreshold) pairsToMerge.add(Triple(nodeA, nodeB, sep))
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
            ops.tryProposal(dag = dag, site = node, allEmbeddings = allEmbeddings, groundTruthMap = groundTruthMap, currentIteration = currentIteration, deltaThreshold = -config.formalism.separationEpsilon) {
                for (source in sources) {
                    fuseNodes(target, source)
                }
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

                if (similarity > config.formalism.fusionSimilarityThreshold) {
                    ops.tryProposal(dag = dag, site = root, allEmbeddings = allEmbeddings, groundTruthMap = groundTruthMap, currentIteration = currentIteration, deltaThreshold = -config.formalism.separationEpsilon) {
                        fuseNodes(nodeA, nodeB)
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