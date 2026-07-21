package taxonomy.utils

import taxonomy.model.GraphNode
import taxonomy.model.TraversalPolicy

/**
 * DAG-aware hierarchical metrics.
 *
 *  - DAG-compatible Dendrogram Purity — Monath, Zaheer, Dubey, Ahmed & McCallum
 *    (2021), "Scalable Hierarchical Agglomerative Clustering", AISTATS 2021,
 *    PMLR 130. https://proceedings.mlr.press/v130/monath21a/monath21a.pdf
 *  - Hierarchical F₁ — Kosmopoulos, Partalas, Gaussier, Paliouras &
 *    Androutsopoulos (2014), "Evaluation measures for hierarchical
 *    classification", Information Retrieval Journal 18:83–112, arXiv:1306.6473
 *
 * In TaxoArena the taxonomy is a DAG (polyhierarchy), so a pair of nodes can
 * have several Lowest Common Ancestors. Standard tree-based Dendrogram Purity
 * (Heller & Ghahramani 2005) is undefined there. We take the conservative bound
 * recommended by Monath et al.: the *shallowest* LCA (the one furthest from the
 * root, i.e. with the maximum depth), which yields the smallest — most
 * defensible — subtree for the purity test.
 */

/** All common ancestors of [nodeA] and [nodeB] in the DAG (each node counts as its own ancestor). */
fun findAllLCAs(nodeA: GraphNode, nodeB: GraphNode, policy: TraversalPolicy = TraversalPolicy.DAG_BOTH): Set<GraphNode> {
    val ancestorsA = ancestorsInclusive(nodeA, policy)
    val ancestorsB = ancestorsInclusive(nodeB, policy)
    return ancestorsA intersect ancestorsB
}

/**
 * The shallowest Lowest Common Ancestor — the common ancestor with the greatest
 * [GraphNode.depth] (closest to the leaves, furthest from the root). Conservative
 * choice per Monath et al. (2021). Falls back to [nodeA] when the two share no
 * common ancestor (disconnected components).
 */
fun shallowLCA(nodeA: GraphNode, nodeB: GraphNode, policy: TraversalPolicy = TraversalPolicy.DAG_BOTH): GraphNode =
    findAllLCAs(nodeA, nodeB, policy).maxByOrNull { it.depth } ?: nodeA

/** Ancestors reachable by following parents upward, including the node itself. */
private fun ancestorsInclusive(node: GraphNode, policy: TraversalPolicy = TraversalPolicy.DAG_BOTH): Set<GraphNode> {
    val out = mutableSetOf<GraphNode>()
    fun walk(n: GraphNode) {
        if (!out.add(n)) return
        when (policy) {
            TraversalPolicy.TREE_ONLY -> {
                val treeParent = n.parents.find { it.id == n.treeParentId } ?: n.parents.firstOrNull()
                if (treeParent != null) walk(treeParent)
            }
            TraversalPolicy.BRIDGE_ONLY -> {
                n.parents.filter { it.isBridge }.forEach { walk(it) }
            }
            TraversalPolicy.DAG_BOTH -> {
                n.parents.forEach { walk(it) }
            }
        }
    }
    walk(node)
    return out
}

/** Strict ancestors (parents transitively), excluding the node itself. */
fun dagAllAncestors(node: GraphNode, policy: TraversalPolicy = TraversalPolicy.DAG_BOTH): Set<GraphNode> =
    ancestorsInclusive(node, policy) - node

/** All nodes in the tree-subtree rooted at [node] (itself + transitive tree children). */
private fun subtreeNodes(node: GraphNode, policy: TraversalPolicy = TraversalPolicy.DAG_BOTH): Set<GraphNode> {
    val out = mutableSetOf<GraphNode>()
    fun walk(n: GraphNode) {
        if (!out.add(n)) return
        when (policy) {
            TraversalPolicy.TREE_ONLY -> {
                n.children.forEach { walk(it) }
            }
            TraversalPolicy.BRIDGE_ONLY -> {
                n.crossLinkChildren.forEach { walk(it) }
            }
            TraversalPolicy.DAG_BOTH -> {
                (n.children + n.crossLinkChildren).forEach { walk(it) }
            }
        }
    }
    walk(node)
    return out
}

/**
 * DAG-compatible Dendrogram Purity.
 *
 * For every pair of queries sharing a ground-truth label, take the shallowest
 * LCA of their assigned nodes. The pair is "pure" iff every query assigned to
 * any node in that LCA's subtree shares the same ground-truth label. Purity is
 * the fraction of pure same-label pairs.
 *
 * @param queryAssignments queryId -> assigned node
 * @param groundTruth      queryId -> ground-truth label
 */
fun dagDendrogramPurity(
    queryAssignments: Map<String, GraphNode>,
    groundTruth: Map<String, String>,
    policy: TraversalPolicy = TraversalPolicy.DAG_BOTH
): Double {
    // queries with both an assignment and a known label, grouped by label
    val labelled = queryAssignments.keys
        .filter { groundTruth[it] != null }
        .groupBy { groundTruth.getValue(it) }
        .filter { it.value.size >= 2 }
    if (labelled.isEmpty()) return 0.0

    // node -> labels of queries assigned to it (for the purity test over a subtree)
    val nodeToLabels = HashMap<GraphNode, MutableList<String>>()
    for ((q, node) in queryAssignments) {
        val gt = groundTruth[q] ?: continue
        nodeToLabels.getOrPut(node) { mutableListOf() }.add(gt)
    }

    val subtreeCache = HashMap<GraphNode, Set<GraphNode>>()
    fun subtreeOf(n: GraphNode) = subtreeCache.getOrPut(n) { subtreeNodes(n, policy) }

    var pureSum = 0.0
    var total = 0
    for ((label, queries) in labelled) {
        for (i in queries.indices) for (j in i + 1 until queries.size) {
            val a = queryAssignments.getValue(queries[i])
            val b = queryAssignments.getValue(queries[j])
            val lca = shallowLCA(a, b, policy)
            val subtree = subtreeOf(lca)
            var match = 0
            var seen = 0
            for (node in subtree) {
                val labels = nodeToLabels[node] ?: continue
                for (l in labels) {
                    seen++
                    if (l == label) match++
                }
            }
            if (seen == 0) continue
            total++
            pureSum += match.toDouble() / seen
        }
    }
    return if (total > 0) pureSum / total else 0.0
}

/**
 * Hierarchical Precision / Recall / F₁ (Kosmopoulos et al. 2014).
 *
 * Each prediction and ground truth is augmented with the ancestors of its leaf
 * (the full root-to-leaf path). Micro-averaged over all queries:
 *
 *   H-P = |∩ ancestors| / |pred ancestors|
 *   H-R = |∩ ancestors| / |true ancestors|
 *   H-F₁ = 2·H-P·H-R / (H-P + H-R)
 *
 * @param predicted   queryId -> predicted leaf node
 * @param groundTruth queryId -> true leaf node
 * @return Triple(H-P, H-R, H-F₁)
 */
fun computeHierarchicalF1(
    predicted: Map<String, GraphNode>,
    groundTruth: Map<String, GraphNode>,
    policy: TraversalPolicy = TraversalPolicy.DAG_BOTH
): Triple<Double, Double, Double> {
    var numerator = 0.0
    var predDenom = 0.0
    var trueDenom = 0.0

    for ((queryId, predLeaf) in predicted) {
        val trueLeaf = groundTruth[queryId] ?: continue
        val predAncestors = dagAllAncestors(predLeaf, policy) + predLeaf
        val trueAncestors = dagAllAncestors(trueLeaf, policy) + trueLeaf

        numerator += (predAncestors intersect trueAncestors).size.toDouble()
        predDenom += predAncestors.size.toDouble()
        trueDenom += trueAncestors.size.toDouble()
    }

    val hP = if (predDenom > 0) numerator / predDenom else 0.0
    val hR = if (trueDenom > 0) numerator / trueDenom else 0.0
    val hF1 = if (hP + hR > 0) 2 * hP * hR / (hP + hR) else 0.0
    return Triple(hP, hR, hF1)
}
