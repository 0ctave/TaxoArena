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
import kotlin.math.exp

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

    fun routeQuery(
        query: Embedding,
        root: GraphNode,
        currentIteration: Int = 2,
        originalCategories: List<String>? = null,
        isInference: Boolean = false
    ): Map<GraphNode, Double> =
        trickler.routeQuery(query, root, currentIteration, originalCategories, isInference).leaves

    suspend fun fitNodeRecursive(node: GraphNode, currentIteration: Int = 0, isFinalIteration: Boolean = false) = fitter.fitNodeRecursive(node, currentIteration, isFinalIteration)

    suspend fun splitNodesRecursive(node: GraphNode) = splitter.splitNodesRecursive(node)

    suspend fun generateLabelsPostPass(root: GraphNode, onProgress: (Int, Int) -> Unit = { _, _ -> }) =
        splitter.generateLabelsPostPass(root, onProgress)

    fun resetConceptCounter() = splitter.resetConceptCounter()

    suspend fun optimizeHierarchy(root: GraphNode, currentIteration: Int = 2, learningPhase: Boolean = false) = merger.optimizeHierarchy(root, currentIteration, learningPhase)

    suspend fun prunePassthroughNodesPublic(root: GraphNode) = merger.prunePassthroughNodesPublic(root)

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
        root: GraphNode,
        embeddings: List<Embedding>,
        groundTruthMap: Map<String, List<String>> = emptyMap(),
        currentIteration: Int = 1
    ) = coroutineScope {

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
                                leaf.queryWeights.merge(emb.rawText, weight, Double::plus)
                                if (!leaf.queries.contains(emb)) {
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
                        val qId = if (emb.queryId != -1) emb.queryId.toString() else taxonomy.model.TextNormalizer.cleanText(emb.rawText)
                        synchronized(routeResult.primary.residualQueries) {
                            routeResult.primary.residualQueries.add(qId)
                            routeResult.primary.residualConfidences[qId] = 0.0
                        }
                        synchronized(routeResult.primary.queryWeights) {
                            routeResult.primary.queryWeights.merge(emb.rawText, 1.0, Double::plus)
                            if (!routeResult.primary.queries.contains(emb)) {
                                routeResult.primary.queries.add(emb)
                            }
                        }
                    } else {
                        // Residual routing disabled entirely: preserve the old hard-assignment-to-root
                        // fallback so mass still lands somewhere.
                        log.debug("Query '${emb.rawText.take(40)}' fell back to root — out-of-distribution?")
                        synchronized(root.queryWeights) {
                            root.queryWeights.merge(emb.rawText, 1.0, Double::plus)
                            if (!root.queries.contains(emb)) {
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
        val type = if (node.isBridge) "Bridge" else if (node.isLeaf) "Leaf" else "Parent"
        val qCount = node.getRecursiveQueryCount()
        val directQ = node.queries.size

        val parentNames = node.parents.mapNotNull { it.label }.filter { it.isNotBlank() }.distinct()
        val parentsInfo = if (parentNames.size > 1) " [Bridge Parents: ${parentNames.joinToString(" & ")}]" else ""

        val vmfStats = if (node.vmfMu.isNotEmpty()) {
            " (kappa: ${"%.1f".format(java.util.Locale.US, node.vmfKappa)})"
        } else ""
        val chainNote = if (chainSkipped > 0) " [⋯ $chainSkipped wrapper level${if (chainSkipped > 1) "s" else ""} collapsed]" else ""

        val nodeLabel = "${node.label} [q=$directQ/$qCount, $type]$vmfStats$parentsInfo$chainNote$cross$edgeType"
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
        val type = if (node.isBridge) "Bridge" else if (node.isLeaf) "Leaf" else "Parent/Residual"

        val parentNames = node.parents.mapNotNull { it.label }.filter { it.isNotBlank() }.distinct()
        val parentsInfo = if (parentNames.size > 1) " [Bridge Parents: ${parentNames.joinToString(" & ")}]" else ""

        val vmfStats = if (node.vmfMu.isNotEmpty()) {
            " (vMF kappa: ${"%.3f".format(java.util.Locale.US, node.vmfKappa)})"
        } else ""
        val chainNote = if (chainSkipped > 0) " [⋯ $chainSkipped wrapper level${if (chainSkipped > 1) "s" else ""} collapsed]" else ""

        val nodeLabel = "${node.label} [${node.queries.size} q - $type]$vmfStats$parentsInfo$chainNote$cross$edgeType"
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