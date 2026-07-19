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

    suspend fun optimizeHierarchy(root: GraphNode, currentIteration: Int = 2) {
        pruneUnrelevantNodes(root)
        mergeSimilarSiblings(root)

        if (config.formalism.enableBridging) {
            insertBridgingParents(root, currentIteration)
        }

        val ancestorMap = buildAncestorMap(root)  // ← build once
        evaluateCrossLinks(root, ancestorMap)

        do {} while (prunePassthroughNodes(root))
        pruneUnrelevantNodes(root)
        removeStaleParentRefs(root)

        invalidateAncestorCache()
        val ancestorMapFinal = buildAncestorMap(root)  // ← rebuild after structural changes
        transitiveReduction(root, ancestorMapFinal)
    }

    fun prunePassthroughNodesPublic(root: GraphNode) {
        do {} while (prunePassthroughNodes(root))
    }

    private fun blendVmfAndNiw(target: GraphNode, source: GraphNode) {
        val nA = target.getRecursiveQueryCount().toDouble().coerceAtLeast(1.0)
        val nB = source.getRecursiveQueryCount().toDouble().coerceAtLeast(1.0)
        val d = target.sliceDim

        // vMF Blend
        val mu = FloatArray(d) { i ->
            (nA * target.vmfMu[i] + nB * source.vmfMu[i]).toFloat()
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
            ((nA * target.niwM0[i] + nB * source.niwM0[i]) / (nA + nB)).toFloat()
        }
        target.niwM0 = mN
        val lambdaN = FloatArray(d) { i ->
            ((nA * target.niwLambda[i] + nB * source.niwLambda[i]) / (nA + nB)).toFloat()
        }
        target.niwLambda = lambdaN
    }

    private fun fuseNodes(target: GraphNode, source: GraphNode) {
        require(target.sliceDim == source.sliceDim) {
            "Cannot fuse nodes at different dims: ${target.label}(${target.sliceDim}) vs ${source.label}(${source.sliceDim})"
        }

        // 1. Combine queries
        target.queries.addAll(source.queries)

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

        // 6. Clean up source
        source.parents.clear()
        source.children.clear()
        source.crossLinkChildren.clear()
        source.queries.clear()
    }

    private fun pruneUnrelevantNodes(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
        if (visited.contains(node.id)) return
        visited.add(node.id)

        val currentChildren = node.children.toList()
        for (child in currentChildren) {
            pruneUnrelevantNodes(child, visited)
        }

        // Cache branch-query counts once per child — getAllQueriesInBranch() is O(subtree).
        val branchSizes = node.children.associateWith { it.getAllQueriesInBranch().size }

        val nodesToPrune = node.children.filter { child ->
            val totalQueriesInBranch = branchSizes[child] ?: 0
            val isTrulyDead = totalQueriesInBranch == 0

            val liveSiblings = node.children.filter { (branchSizes[it] ?: 0) > 0 }
            val siblingAvg = if (liveSiblings.size > 1)
                liveSiblings.map { branchSizes[it] ?: 0 }.average()
            else
                node.children.map { branchSizes[it] ?: 0 }.average()

            val isStarved = child.isLeaf && totalQueriesInBranch < (siblingAvg * 0.2).coerceAtLeast(5.0)
            val isEmptyParent = !child.isLeaf && child.children.isEmpty()

            val wouldLeaveParentSingleChild = (node.children.size - 1) <= 1

            isTrulyDead || ((isStarved || isEmptyParent) && !wouldLeaveParentSingleChild)
        }

        if (nodesToPrune.isNotEmpty()) {
            nodesToPrune.forEach { target ->
                if (target.parents.isEmpty() && !node.children.contains(target)) return@forEach  // already pruned this pass
                log.info("[PRUNED] '${target.label}' (starved/empty)")
                node.queries.addAll(target.queries)
                node.children.remove(target)
                target.parents.remove(node)
                // Clean up crossLinkChildren back-refs (Problem 10)
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

    private suspend fun mergeSimilarSiblings(
        node: GraphNode,
        visited: MutableSet<String> = java.util.concurrent.ConcurrentHashMap.newKeySet()
    ) {
        if (visited.contains(node.id)) return
        visited.add(node.id)

        val currentChildren = node.children.toList()
        coroutineScope {
            currentChildren.map { child ->
                async(Dispatchers.Default) {
                    mergeSimilarSiblings(child, visited)
                }
            }
        }.awaitAll()

        val children = node.children.toList()
        if (children.size < 2) return

        log.debug("Evaluating sibling merges for parent '${node.label}' with ${children.size} children...")

        // 1. Parallel pairwise vMF JS-divergence calculations
        val siblingMergeThreshold = config.formalism.separationEpsilon
        val pairsToMerge = coroutineScope {
            val jobs = mutableListOf<Deferred<Triple<GraphNode, GraphNode, Double>?>>()
            for (i in 0 until children.size) {
                for (j in i + 1 until children.size) {
                    val nodeA = children[i]
                    val nodeB = children[j]
                    if (nodeA.vmfMu.isEmpty() || nodeB.vmfMu.isEmpty()) continue
                    jobs.add(async(Dispatchers.Default) {
                        val commonDim = minOf(nodeA.vmfMu.size, nodeB.vmfMu.size)
                        val muA = StatisticsUtils.projectVector(nodeA.vmfMu, commonDim)
                        val muB = StatisticsUtils.projectVector(nodeB.vmfMu, commonDim)
                        val div = StatisticsUtils.vmfJsDivergence(
                            muA,
                            nodeA.vmfKappa,
                            muB,
                            nodeB.vmfKappa,
                            commonDim
                        )
                        if (div < siblingMergeThreshold) Triple(nodeA, nodeB, div) else null
                    })
                }
            }
            jobs.awaitAll().filterNotNull()
        }

        if (pairsToMerge.isEmpty()) return

        // 2. Build connected components using Union-Find
        val uf = UnionFind(children)
        for ((nodeA, nodeB, _) in pairsToMerge) {
            uf.union(nodeA, nodeB)
        }

        val clusters = children.groupBy { uf.find(it) }.values.filter { it.size > 1 }
        if (clusters.isEmpty()) return

        log.info("[MERGE] Found ${clusters.size} groups under '${node.label}'")

        for (cluster in clusters) {
            val target = cluster[0]
            val sources = cluster.subList(1, cluster.size)
            val combinedQueries = cluster.flatMap { it.queries }.distinctBy { it.rawText }

            val newLabel = cluster.joinToString(" & ") { it.label ?: "" }

            log.info("[MERGE] Fused ${cluster.map { it.label }} -> '$newLabel'")
            target.label = newLabel

            for (source in sources) {
                fuseNodes(target, source)
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
    private suspend fun evaluateCrossLinks(root: GraphNode, ancestorMap: Map<String, Set<String>>) {
        val allNodes = getAllNodes(root).filter { it.depth > 0 }
        val allNodeById = allNodes.associateBy { it.id }

        coroutineScope {
            allNodes.map { node ->
                async(Dispatchers.Default) {
                    val directQueries = node.queries.toList()
                    if (directQueries.isEmpty() || directQueries.size < config.formalism.minClusterSize) return@async

                    // Fast pre-check: low-kappa nodes won't win majority vote
                    if (node.vmfKappa < 0.5) return@async

                    val potentialParents = allNodes.filter { pp ->
                        node != pp &&
                                !node.parents.contains(pp) &&
                                pp.id !in (ancestorMap[node.id] ?: emptySet()) &&
                                node.id !in (ancestorMap[pp.id] ?: emptySet()) &&
                                pp.depth <= node.depth &&
                                (node.depth - pp.depth) <= 3 &&
                                getDepth1Ancestor(node, ancestorMap, allNodeById) !=
                                getDepth1Ancestor(pp, ancestorMap, allNodeById)
                    }

                    val links = mutableListOf<String>()
                    for (pp in potentialParents) {
                        var votes = 0
                        for (q in directQueries) {
                            val slicedA = q.projectTo(node.sliceDim)
                            val slicedB = q.projectTo(pp.sliceDim)
                            val cosA = StatisticsUtils.dotProduct(slicedA, node.vmfMu)
                            val cosB = StatisticsUtils.dotProduct(slicedB, pp.vmfMu)
                            if (cosB - cosA > 0.05) votes++
                        }
                        if (votes >= directQueries.size / 2) {
                            links.add("'${node.label}' -> '${pp.label}'($votes/${directQueries.size})")
                            synchronized(node) { node.parents.add(pp) }
                            synchronized(pp) { pp.crossLinkChildren.add(node) }
                        }
                    }
                    if (links.isNotEmpty()) log.info("[XL] Crosslinked: ${links.joinToString(", ")}")
                }
            }.awaitAll()
        }
    }

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

    private fun prunePassthroughNodes(node: GraphNode, visited: MutableSet<String> = mutableSetOf()): Boolean {
        if (visited.contains(node.id)) return false
        visited.add(node.id)

        var anyPruned = false

        val currentChildren = node.treeChildren.toList()
        for (child in currentChildren) {
            if (prunePassthroughNodes(child, visited)) anyPruned = true
        }

        val nodesToBypass = node.treeChildren.filter { child ->
            if (child.treeChildren.size != 1 || child.depth <= 1) return@filter false
            val grandchild = child.treeChildren.first()

            val commonDim = minOf(child.sliceDim, grandchild.sliceDim)
            val mu1 = StatisticsUtils.projectVector(child.vmfMu, commonDim)
            val mu2 = StatisticsUtils.projectVector(grandchild.vmfMu, commonDim)
            val div = StatisticsUtils.vmfJsDivergence(mu1, child.vmfKappa, mu2, grandchild.vmfKappa, commonDim)

            div < config.formalism.separationEpsilon && child.queries.size < config.formalism.minClusterSize
        }

        if (nodesToBypass.isNotEmpty()) anyPruned = true

        for (passthrough in nodesToBypass) {
            val grandchild = passthrough.treeChildren.first()
            log.info("[COLLAPSE] '${passthrough.label}' -> '${grandchild.label}'")

            // Move residual queries down
            grandchild.queries.addAll(passthrough.queries)

            // Re-parent grandchild under node (the passthrough's parent)
            node.children.remove(passthrough)
            node.children.add(grandchild)

            grandchild.treeParentId = node.id

            grandchild.parents.remove(passthrough)
            grandchild.parents.add(node)

            recomputeDepths(grandchild, node.depth + 1)

            // Handle passthrough's other tree parents
            passthrough.parents.toList().forEach { p ->
                if (p != node) {
                    p.children.remove(passthrough)
                    p.children.add(grandchild)
                    grandchild.parents.add(p)
                }
            }

            passthrough.crossLinkChildren.toList().forEach { clChild ->
                clChild.parents.remove(passthrough)
                // Only add if grandchild is not already a tree/cross-link parent of clChild
                if (!clChild.parents.contains(grandchild)) {
                    clChild.parents.add(grandchild)
                    grandchild.crossLinkChildren.add(clChild)  // ← cross-link, NOT children
                }
            }

            passthrough.parents.clear()
            passthrough.children.clear()
            passthrough.crossLinkChildren.clear()
            passthrough.queries.clear()
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
        val leaves = collectAllLeaves(root)
        var bridgesCreated = 0
        
        val allNodes = mutableSetOf<GraphNode>()
        fun walkCount(n: GraphNode) {
            if (!allNodes.add(n)) return
            n.children.forEach { walkCount(it) }
            n.crossLinkChildren.forEach { walkCount(it) }
        }
        walkCount(root)
        val currentBridgeCount = allNodes.count { it.isBridge }
        val maxBridgeNodes = config.formalism.maxBridgeNodes
        
        if (currentBridgeCount >= maxBridgeNodes) {
            log.info("Bridge Insertion: budget reached ($currentBridgeCount >= $maxBridgeNodes). Skipping.")
            return
        }

        class BridgeCandidate(val u: GraphNode, val v: GraphNode, val div: Double)

        val leafCandidates = mutableMapOf<GraphNode, MutableList<BridgeCandidate>>()
        for (i in leaves.indices) {
            val u = leaves[i]
            for (j in leaves.indices) {
                if (i == j) continue
                val v = leaves[j]
                
                val uAncestors = getDepth1Ancestors(u)
                val vAncestors = getDepth1Ancestors(v)
                if (uAncestors.isEmpty() || vAncestors.isEmpty() || uAncestors.intersect(vAncestors).isNotEmpty()) {
                    continue
                }
                
                val commonDim = minOf(u.vmfMu.size, v.vmfMu.size)
                if (commonDim == 0) continue
                val projUMu = StatisticsUtils.projectVector(u.vmfMu, commonDim)
                val projVMu = StatisticsUtils.projectVector(v.vmfMu, commonDim)
                val div = StatisticsUtils.vmfJsDivergence(projUMu, u.vmfKappa, projVMu, v.vmfKappa, commonDim)
                
                val lower = config.formalism.separationEpsilon
                val upper = config.formalism.bridgeSeparationCeiling
                if (div in lower..upper) {
                    leafCandidates.getOrPut(u) { mutableListOf() }.add(BridgeCandidate(u, v, div))
                }
            }
        }

        val allCandidates = mutableListOf<BridgeCandidate>()
        val addedPairs = mutableSetOf<String>()
        for ((u, candidates) in leafCandidates) {
            val topK = candidates.sortedBy { it.div }.take(config.formalism.bridgeCandidateTopK ?: 10)
            for (cand in topK) {
                val pairKey = if (cand.u.id < cand.v.id) "${cand.u.id}|${cand.v.id}" else "${cand.v.id}|${cand.u.id}"
                if (addedPairs.add(pairKey)) {
                    allCandidates.add(cand)
                }
            }
        }

        val candidatePairs = allCandidates.sortedBy { it.div }

        log.info("Bridge Insertion: Found ${candidatePairs.size} candidate pairs in adjacency band [${config.formalism.separationEpsilon}, ${config.formalism.bridgeSeparationCeiling}] after Top-K filtering and sorting")

        val bridgedLeaves = mutableMapOf<String, Int>()
        val domainPairCounts = mutableMapOf<String, Int>()

        for (cand in candidatePairs) {
            val u = cand.u
            val v = cand.v
            val div = cand.div
            val candidateId = "cand_${u.id.take(4)}_${v.id.take(4)}"
            if (bridgesCreated + currentBridgeCount >= maxBridgeNodes) break

            // Enforce bridgeParentBudget
            val uCount = bridgedLeaves.getOrDefault(u.id, 0)
            val vCount = bridgedLeaves.getOrDefault(v.id, 0)
            val budget = config.formalism.bridgeParentBudget ?: 1
            if (uCount >= budget || vCount >= budget) {
                log.info("Bridge Insertion: skipping candidate $candidateId; bridgeParentBudget of $budget exceeded for leaf")
                continue
            }

            // Enforce maxBridgesPerDomainPair = 2
            val uAncestors = getDepth1Ancestors(u)
            val vAncestors = getDepth1Ancestors(v)
            val domU = uAncestors.firstOrNull() ?: "unknown"
            val domV = vAncestors.firstOrNull() ?: "unknown"
            val domainPairKey = if (domU < domV) "$domU|$domV" else "$domV|$domU"
            val existingDomainBridges = domainPairCounts.getOrDefault(domainPairKey, 0)
            if (existingDomainBridges >= (config.formalism.maxBridgesPerDomainPair ?: 2)) {
                log.info("Bridge Insertion: skipping candidate between $domU and $domV; limit of ${config.formalism.maxBridgesPerDomainPair ?: 2} bridges for this pair reached.")
                continue
            }

            val sourceNodes = "${u.label ?: u.id} + ${v.label ?: v.id}"
            val combinedQueries = u.queries + v.queries
            val size = combinedQueries.size

            // Enforce minBridgeCoverage = 50
            if (size < config.formalism.minBridgeCoverage) {
                log.info("Bridge Insertion: skipping candidate $candidateId; combined query size $size < minBridgeCoverage ${config.formalism.minBridgeCoverage}")
                continue
            }
            val entropy = calculateGtEntropy(combinedQueries)
            
            val commonDim = minOf(u.vmfMu.size, v.vmfMu.size)
            val projUMu = StatisticsUtils.projectVector(u.vmfMu, commonDim)
            val projVMu = StatisticsUtils.projectVector(v.vmfMu, commonDim)

            val exceedsEntropy = entropy > config.formalism.bridgeEntropyCap
            if (exceedsEntropy) {
                log.info("Diagnostic: entropy ${"%.4f".format(java.util.Locale.US, entropy)} exceeds cap ${config.formalism.bridgeEntropyCap} for candidate $candidateId (diagnostic-only guard, not rejected)")
            }

            val bridgeNode = GraphNode(
                id = "bridge_" + java.util.UUID.randomUUID().toString().take(8),
                label = "Temporary Bridge",
                depth = maxOf(2, minOf(u.depth, v.depth) - 1)
            )
            bridgeNode.isBridge = true
            bridgeNode.bridgeJsDivergence = div
            bridgeNode.sliceDim = commonDim

            val d = commonDim
            val combinedCentroid = DoubleArray(d)
            val projected = combinedQueries.map { it.projectTo(d) }
            for (vec in projected) {
                for (i in 0 until d) combinedCentroid[i] += vec[i]
            }
            var norm = 0.0
            for (i in 0 until d) norm += combinedCentroid[i] * combinedCentroid[i]
            norm = sqrt(norm)
            val mu = FloatArray(d) { i -> if (norm > 0.0) (combinedCentroid[i] / norm).toFloat() else 0.0f }
            if (norm == 0.0 && d > 0) mu[0] = 1.0f
            bridgeNode.vmfMu = mu
            
            var dot = 0.0
            for (vec in projected) for (i in 0 until d) dot += mu[i] * vec[i]
            val rBar = (dot / combinedQueries.size.coerceAtLeast(1)).coerceAtLeast(0.0)
            bridgeNode.vmfKappa = StatisticsUtils.correctedKappa(rBar, d, combinedQueries.size)
            bridgeNode.vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(d, bridgeNode.vmfKappa)

            var finalLabel = "Bridge Concept [${u.label ?: u.id} ↔ ${v.label ?: v.id}]"
            if (config.execution.enableLabeling) {
                try {
                    val representativeSamples = combinedQueries.shuffled().take(30).map { it.rawText }
                    val prompt = taxonomy.prompts.TaxoPrompts.clusterLabeling(
                        querySamples = representativeSamples,
                        parentLabel = "Bridging Parent",
                        siblingLabels = emptyList(),
                        branchHistory = listOf(u.label ?: "", v.label ?: ""),
                        domainAnchors = listOf(u.label ?: "", v.label ?: ""),
                        childLabels = emptyList(),
                        depth = bridgeNode.depth
                    )
                    val generated = llmClient.generateClusterLabel(prompt)
                    if (generated.isNotBlank()) {
                        finalLabel = generated.trim()
                    }
                } catch (e: Exception) {
                    log.warn("LLM labeling failed for bridge, falling back to: $finalLabel")
                }
            }
            bridgeNode.label = finalLabel

            if (isAncestor(u, bridgeNode) || isAncestor(v, bridgeNode) || isAncestor(bridgeNode, u) || isAncestor(bridgeNode, v)) {
                log.warn("Bridge Insertion: cycle detected for candidate $candidateId, skipping.")
                continue
            }

            bridgeNode.crossLinkChildren.add(u)
            bridgeNode.crossLinkChildren.add(v)
            u.parents.add(bridgeNode)
            v.parents.add(bridgeNode)

            val pU = u.parents.find { it.id == u.treeParentId }
            val pV = v.parents.find { it.id == v.treeParentId }
            if (pU != null) {
                bridgeNode.parents.add(pU)
                pU.crossLinkChildren.add(bridgeNode)
            }
            if (pV != null && pV.id != pU?.id) {
                bridgeNode.parents.add(pV)
                pV.crossLinkChildren.add(bridgeNode)
            }

            bridgedLeaves[u.id] = uCount + 1
            bridgedLeaves[v.id] = vCount + 1
            domainPairCounts[domainPairKey] = existingDomainBridges + 1

            bridgesCreated++
            log.info("Bridge Insertion: Created bridge '${bridgeNode.label}' between '${u.label}' and '${v.label}' with entropy ${"%.4f".format(java.util.Locale.US, entropy)}")

            logBridgeResidual(
                iteration = iteration,
                candidateId = candidateId,
                sourceNodes = sourceNodes,
                size = size,
                entropy = entropy,
                div = div,
                accepted = true,
                reason = "Success"
            )
        }
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

    private fun collectAllLeaves(root: GraphNode): List<GraphNode> {
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

    private fun getDepth1Ancestors(node: GraphNode, policy: taxonomy.model.TraversalPolicy = taxonomy.model.TraversalPolicy.TREE_ONLY): Set<String> {
        val ancestors = mutableSetOf<String>()
        val visited   = mutableSetOf<String>()
        fun walk(n: GraphNode) {
            if (!visited.add(n.id)) return
            if (n.depth == 1) {
                (n.originalCategory ?: n.label)?.let { ancestors.add(it) }
            } else {
                when (policy) {
                    taxonomy.model.TraversalPolicy.TREE_ONLY -> {
                        val treeParent = n.parents.find { it.id == n.treeParentId }
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
}