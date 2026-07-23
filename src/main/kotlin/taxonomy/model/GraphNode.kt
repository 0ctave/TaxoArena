package taxonomy.model

import java.util.*

/**
 * The core topological unit: Directed Acyclic Graph (DAG) Node.
 * Updated to use a unified query list for both Leaf Data and Parent Residuals.
 * Uses vMF for self-modeling and NiW for Bayesian posterior regularization.
 *
 * FIX (Bug 12): Separate tree children from cross-link children so that
 * isLeaf only reflects the tree structure. Cross-link children added by
 * evaluateCrossLinks() must NOT cause a node to lose its leaf status.
 */
data class GraphNode(
    val id: String = UUID.randomUUID().toString(),
    var label: String?,
    var originalCategory: String? = null,
    var depth: Int,

    // --- Topology (DAG) ---
    // Tree children: nodes created by the splitter under this node.
    // This is the ONLY set that governs isLeaf.
    val children: MutableSet<GraphNode> = java.util.concurrent.ConcurrentHashMap.newKeySet(),

    // Cross-link children: nodes added by evaluateCrossLinks() because their
    // query distribution also fits this node's vMF. These do NOT affect isLeaf.
    val crossLinkChildren: MutableSet<GraphNode> = java.util.concurrent.ConcurrentHashMap.newKeySet(),

    val parents: MutableSet<GraphNode> = java.util.concurrent.ConcurrentHashMap.newKeySet(),

    // Soft routing query weights map (rawText -> weight)
    val queryWeights: MutableMap<String, Double> = java.util.concurrent.ConcurrentHashMap(),

    // Unified Data Space (retained for backward compatibility and list access)
    var queries: MutableList<Embedding> = Collections.synchronizedList(ArrayList()),

    // Immutable sliceDim based on depth
    var sliceDim: Int = dimForDepth(depth),

    // vMF self-model (single component, fitted at this node's sliceDim)
    var vmfMu: FloatArray = FloatArray(0),      // Unit-norm mean direction, shape [sliceDim]
    var vmfKappa: Double = 1.0,                 // Concentration, bias-corrected
    var vmfLogNormalizer: Double = 0.0,          // log C_d(kappa), precomputed

    // NiW posterior (for soft membership scoring at inference)
    var niwM0: FloatArray = FloatArray(0),      // Posterior mean, shape [sliceDim]
    var niwKappa0: Double = 0.0,                // Posterior pseudocount
    var niwNu0: Double = 0.0,                   // Posterior degrees of freedom
    var niwLambda: FloatArray = FloatArray(0),  // Diagonal of posterior scale matrix

    // Dasgupta audit
    var dasguptaDeltaNorm: Double = 0.0,        // Delta/C_before at time of split; 0.0 if root or unsplit

    // Phase tracking
    var phaseCompleted: Int = 0,                 // Bitmask: EMBEDDED=1, VMF_FIT=2, SPLIT_EVAL=4, NIW_FIT=8, OPTIMIZED=16

    // Agent Judge Profiles
    var judgePrompt: String? = null,
    var judgeRubric: String? = null,
    var judgeGtAgreement: Double? = null,
    var isBridge: Boolean = false,
    var bridgeJsDivergence: Double = 0.0,
    val residualQueries: MutableSet<String> = java.util.concurrent.ConcurrentHashMap.newKeySet(),
    val residualConfidences: MutableMap<String, Double> = java.util.concurrent.ConcurrentHashMap(),
    var dOverN: Double = 0.0,
    var description: String? = null
) {
    companion object {
        val EmbeddingRegistry = java.util.concurrent.ConcurrentHashMap<String, Embedding>()
        fun registerEmbedding(emb: Embedding) {
            EmbeddingRegistry[emb.rawText] = emb
        }
        fun getEmbedding(rawText: String): Embedding? = EmbeddingRegistry[rawText]
    }
    // isLeaf is true iff this node has NO tree children and is not a bridge/multi-parent node.
    val isLeaf: Boolean get() = children.isEmpty() && !isBridge && parents.size <= 1

    val treeChildren: MutableSet<GraphNode> get() = children

    /**
     * Cross-link / Bridge children: non-tree directed polyhierarchy edges.
     * "Bridge" and "Cross-link" refer to the exact same polyhierarchy concept.
     */
    val bridgeChildren: MutableSet<GraphNode> get() = crossLinkChildren

    /**
     * Boolean alias confirming whether this node is a cross-link bridge target / polyhierarchy node.
     */
    val isCrossLink: Boolean get() = isBridge

    // Proportional weight of this node as a component in its parent's vMF/NiW
    var proportionalWeight: Double = 1.0

    // Fingerprints for judge caching and validation
    var judgeCorpusFingerprint: String? = null
    var judgeModelVersion: String? = null

    // treeParentId: set once by the splitter, never cleared by merger or transitive reduction
    var treeParentId: String? = null

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is GraphNode) return false
        return id == other.id
    }

    override fun hashCode(): Int = id.hashCode()

    /**
     * Aggregates all queries in the branch (this node + all descendants).
     * Walks BOTH tree children AND cross-link children for completeness.
     * Handles DAG polyhierarchy by ensuring each node is visited only once.
     */
    fun getAllQueriesInBranch(): List<Embedding> {
        val seenIds = mutableSetOf<Int>()
        val seenTexts = mutableSetOf<String>()
        val allQueries = mutableListOf<Embedding>()
        val visitedNodes = mutableSetOf<String>()

        fun walk(node: GraphNode) {
            if (!visitedNodes.add(node.id)) return
            if (node.queryWeights.isNotEmpty()) {
                for (text in node.queryWeights.keys) {
                    val q = getEmbedding(text) ?: continue
                    val isNew = if (q.queryId >= 0) seenIds.add(q.queryId) else seenTexts.add(q.rawText)
                    if (isNew) allQueries.add(q)
                }
            } else {
                synchronized(node.queries) {
                    for (q in node.queries) {
                        val isNew = if (q.queryId >= 0) seenIds.add(q.queryId) else seenTexts.add(q.rawText)
                        if (isNew) allQueries.add(q)
                    }
                }
            }
            node.treeChildren.forEach { walk(it) }
        }
        walk(this)
        return allQueries
    }

    /**
     * Like getAllQueriesInBranch() but also follows crossLinkChildren.
     * Used by the fitter to estimate the full query population this node
     * geometrically "covers", including cross-linked sub-regions.
     * NOT for structural metrics — those use getAllQueriesInBranch().
     */
    fun getAllQueriesInRegion(): List<Embedding> {
        val seenIds = mutableSetOf<Int>()
        val seenTexts = mutableSetOf<String>()
        val allQueries = mutableListOf<Embedding>()
        val visitedNodes = mutableSetOf<String>()

        fun walk(node: GraphNode) {
            if (!visitedNodes.add(node.id)) return
            if (node.queryWeights.isNotEmpty()) {
                for (text in node.queryWeights.keys) {
                    val q = getEmbedding(text) ?: continue
                    val isNew = if (q.queryId >= 0) seenIds.add(q.queryId) else seenTexts.add(q.rawText)
                    if (isNew) allQueries.add(q)
                }
            } else {
                synchronized(node.queries) {
                    for (q in node.queries) {
                        val isNew = if (q.queryId >= 0) seenIds.add(q.queryId) else seenTexts.add(q.rawText)
                        if (isNew) allQueries.add(q)
                    }
                }
            }
            node.treeChildren.forEach { walk(it) }
            node.crossLinkChildren.forEach { walk(it) }  // ← the only difference
        }
        walk(this)
        return allQueries
    }

    /**
     * Fast count of all unique queries in the branch.
     */
    fun getRecursiveQueryCount(): Int {
        val visited = mutableSetOf<String>()
        val bitSet = BitSet()
        val fallbackSet = mutableSetOf<String>()

        fun walk(node: GraphNode) {
            if (!visited.add(node.id)) return
            if (node.queryWeights.isNotEmpty()) {
                node.queryWeights.keys.forEach { text ->
                    val q = getEmbedding(text)
                    if (q != null && q.queryId >= 0) bitSet.set(q.queryId) else fallbackSet.add(text)
                }
            } else {
                synchronized(node.queries) {
                    node.queries.forEach { q ->
                        if (q.queryId >= 0) bitSet.set(q.queryId) else fallbackSet.add(q.rawText)
                    }
                }
            }
            node.children.forEach { walk(it) }
        }
        walk(this)
        return bitSet.cardinality() + fallbackSet.size
    }

    fun getRecursiveSoftMass(): Double {
        val visited = mutableSetOf<String>()
        var sum = 0.0
        fun walk(node: GraphNode) {
            if (!visited.add(node.id)) return
            sum += node.queryWeights.values.sum()
            node.treeChildren.forEach { walk(it) }
            node.crossLinkChildren.forEach { walk(it) }
        }
        walk(this)
        return sum
    }
}

fun dimForDepth(depth: Int): Int = 256

// Phase completion flags
const val PHASE_EMBEDDED = 1
const val PHASE_VMF_FIT = 2
const val PHASE_SPLIT_EVAL = 4
const val PHASE_NIW_FIT = 8
const val PHASE_OPTIMIZED = 16

/**
 * Traverses the entire DAG, collects all unique queries, attributes sequential integer IDs to them,
 * and ensures all occurrences of identical queries share the same ID.
 * Walks BOTH tree children AND cross-link children.
 */
fun assignQueryIds(root: GraphNode, enableStableQuestionIds: Boolean = false) {
    val visited = mutableSetOf<String>()
    val uniqueQueries = mutableListOf<Embedding>()
    val seenTexts = mutableSetOf<String>()

    fun walk(node: GraphNode) {
        if (!visited.add(node.id)) return
        synchronized(node.queries) {
            node.queries.forEach { q ->
                if (enableStableQuestionIds) {
                    val clean = TextNormalizer.cleanText(q.rawText)
                    val qId = QuestionIdRegistry.lookup(q.rawText) 
                        ?: QuestionIdRegistry.lookup(clean)
                        ?: (clean.hashCode() and 0x7FFFFFFF)
                    q.queryId = qId
                } else {
                    if (seenTexts.add(q.rawText)) {
                        uniqueQueries.add(q)
                    }
                }
            }
        }
        node.children.forEach { walk(it) }
        node.crossLinkChildren.forEach { walk(it) }
    }
    walk(root)

    if (!enableStableQuestionIds) {
        uniqueQueries.forEachIndexed { index, emb ->
            emb.queryId = index
        }
        val textToId = uniqueQueries.associate { it.rawText to it.queryId }

        val visitedAssign = mutableSetOf<String>()
        fun walkAssign(node: GraphNode) {
            if (!visitedAssign.add(node.id)) return
            synchronized(node.queries) {
                node.queries.forEach { q ->
                    q.queryId = textToId[q.rawText] ?: -1
                }
            }
            node.children.forEach { walkAssign(it) }
            node.crossLinkChildren.forEach { walkAssign(it) }
        }
        walkAssign(root)
    } else {
        val textToId = mutableMapOf<String, Int>()
        val visitedCollect = mutableSetOf<String>()
        fun walkCollect(node: GraphNode) {
            if (!visitedCollect.add(node.id)) return
            synchronized(node.queries) {
                node.queries.forEach { q ->
                    val clean = TextNormalizer.cleanText(q.rawText)
                    if (q.queryId != -1) {
                        textToId[clean] = q.queryId
                    }
                }
            }
            node.children.forEach { walkCollect(it) }
            node.crossLinkChildren.forEach { walkCollect(it) }
        }
        walkCollect(root)

        val visitedAssign = mutableSetOf<String>()
        fun walkAssign(node: GraphNode) {
            if (!visitedAssign.add(node.id)) return
            synchronized(node.queries) {
                node.queries.forEach { q ->
                    val clean = TextNormalizer.cleanText(q.rawText)
                    q.queryId = textToId[clean] ?: q.queryId
                }
            }
            node.children.forEach { walkAssign(it) }
            node.crossLinkChildren.forEach { walkAssign(it) }
        }
        walkAssign(root)
    }
}

fun GraphNode.allAncestors(): Set<String> {
    val ancestors = mutableSetOf(this.id)
    fun traverse(node: GraphNode) {
        for (parent in node.parents) {
            if (ancestors.add(parent.id)) {
                traverse(parent)
            }
        }
    }
    traverse(this)
    return ancestors
}