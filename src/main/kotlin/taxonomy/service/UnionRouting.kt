package taxonomy.service

import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.projectTo
import taxonomy.utils.StatisticsUtils

/**
 * Root routing rules for a GRAFTED union (docs/multi_corpus_design.md, stage 1c). The union root
 * is a routing layer over per-corpus trees; under the production descent the six-way root step
 * hands a fifth of MMLU-Pro's held-out questions to the adjacent corpus roots (stage 1b: union
 * Top-1 72.1% vs 75.8% for the MMLU-Pro tree alone, flat nearest-centroid sweep over the same
 * leaves 81.6%). These rules replace ONLY the union root step in the union validation readout;
 * nothing here is reachable from single-corpus construction or routing.
 *
 *  * [Rule.DESCENT]     — today's behaviour: the production trickle from the union root.
 *  * [Rule.FLAT_LEAF]   — nearest leaf centroid over ALL grafted leaves (cosine against each
 *                         leaf's fitted vMF direction, the readout sweep); source and domain are
 *                         the leaf's depth-1 and depth-2 tree ancestors.
 *  * [Rule.SOURCE_GATE] — pick the corpus by the nearest per-corpus ROOT direction (the
 *                         per-corpus tree's own root vMF, grafted unchanged), then run the
 *                         production descent INSIDE that corpus tree.
 *
 * Pure functions over [GraphNode]s: the descent itself is injected as a lambda so the object
 * stays free of Spring and the engine's routing code stays untouched.
 */
object UnionRouting {
    enum class Rule(val key: String) {
        DESCENT("descent"), FLAT_LEAF("flatLeaf"), SOURCE_GATE("sourceGate");

        companion object {
            const val DEFAULT_KEY = "descent"
            fun parse(raw: String): Rule {
                val s = raw.trim()
                return entries.firstOrNull { it.key.equals(s, ignoreCase = true) }
                    ?: throw IllegalArgumentException("unionRootRouting = \"$raw\" is not one of ${entries.joinToString { "\"${it.key}\"" }}")
            }
        }
    }

    /** The routed leaf (null = unrouted) and the depth-1 corpus root the rule committed to (null = none). */
    data class Routed(val leaf: GraphNode?, val source: GraphNode?)

    /**
     * cos(x, mu_v) with x projected to the node's own slice width — the same alignment the
     * trickler's descent gate reads; -inf for an unfitted node so it can never win an argmax.
     */
    fun cosine(emb: Embedding, node: GraphNode): Double {
        if (node.vmfMu.isEmpty()) return Double.NEGATIVE_INFINITY
        return StatisticsUtils.dotProduct(emb.projectTo(node.vmfMu.size), node.vmfMu)
    }

    /** Argmax of [cosine] over [candidates]; the first candidate wins a tie (caller fixes the order). */
    fun nearest(emb: Embedding, candidates: List<GraphNode>): GraphNode? {
        var best: GraphNode? = null
        var bestScore = Double.NEGATIVE_INFINITY
        for (c in candidates) {
            val s = cosine(emb, c)
            if (s > bestScore) { bestScore = s; best = c }
        }
        return best
    }

    /** Per-corpus roots of a grafted union in a fixed order (by id). */
    fun corpusRoots(unionRoot: GraphNode): List<GraphNode> = unionRoot.children.sortedBy { it.id }

    /**
     * Tree parent of every node reachable from [root] over tree edges: first discovery in BFS
     * order, children by id — the ancestry exportUnionRouting has used since stage 1b.
     */
    fun treeParents(root: GraphNode): Map<String, GraphNode> {
        val parent = HashMap<String, GraphNode>()
        val seen = HashSet<String>().apply { add(root.id) }
        val queue = ArrayDeque<GraphNode>().apply { add(root) }
        while (queue.isNotEmpty()) {
            val n = queue.removeFirst()
            for (c in n.children.sortedBy { it.id }) if (seen.add(c.id)) { parent[c.id] = n; queue.add(c) }
        }
        return parent
    }

    /** The tree ancestor of [n] at exactly [depth] (n itself if it sits there), or null. */
    fun ancestorAt(n: GraphNode?, depth: Int, parents: Map<String, GraphNode>): GraphNode? {
        var cur = n
        while (cur != null && cur.depth > depth) cur = parents[cur.id]
        return cur?.takeIf { it.depth == depth }
    }

    /**
     * Routes one held-out embedding under [rule]. [descend] is the production descent started
     * at the given node, returning its top leaf (null = the walk stopped above every leaf);
     * [leaves] is the union's leaf set in a fixed order; [parents] from [treeParents].
     */
    fun route(
        rule: Rule,
        emb: Embedding,
        unionRoot: GraphNode,
        leaves: List<GraphNode>,
        parents: Map<String, GraphNode>,
        descend: (GraphNode) -> GraphNode?
    ): Routed = when (rule) {
        Rule.DESCENT -> {
            val leaf = descend(unionRoot)
            Routed(leaf, ancestorAt(leaf, 1, parents))
        }
        Rule.FLAT_LEAF -> {
            val leaf = nearest(emb, leaves)
            Routed(leaf, ancestorAt(leaf, 1, parents))
        }
        Rule.SOURCE_GATE -> {
            val src = nearest(emb, corpusRoots(unionRoot))
            Routed(src?.let(descend), src)
        }
    }

    /** 95% Wilson score interval for k successes in n trials (the trickle's own formula). */
    fun wilson(k: Int, n: Int, z: Double = 1.96): Pair<Double, Double> {
        if (n <= 0) return 0.0 to 0.0
        val p = k.toDouble() / n
        val centre = p + z * z / (2.0 * n)
        val half = z * kotlin.math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n.toDouble() * n))
        val denom = 1.0 + z * z / n
        return ((centre - half) / denom).coerceIn(0.0, 1.0) to ((centre + half) / denom).coerceIn(0.0, 1.0)
    }
}
