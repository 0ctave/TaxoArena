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
    // Deterministic, monotonic ids. Node sets (children/parents/crossLinkChildren) are
    // hash sets keyed by id, so id values determine every traversal order — and with
    // them EM input assembly, proposal enumeration order, and which of two comparable
    // edits lands first. Random UUIDs made all of that differ run-to-run at a fixed
    // seed. Counter ids are reproducible as long as node CREATION order is (it is:
    // bootstrap and per-depth proposal loops are sequential). Reset per pipeline run.
    val id: String = nextNodeId(),
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
    val nearMisses: MutableMap<String, Double> = java.util.concurrent.ConcurrentHashMap(),
    var dOverN: Double = 0.0,
    var description: String? = null
) {
    companion object {
        val EmbeddingRegistry = java.util.concurrent.ConcurrentHashMap<String, Embedding>()
        fun registerEmbedding(emb: Embedding) {
            EmbeddingRegistry[emb.rawText] = emb
        }
        fun getEmbedding(rawText: String): Embedding? = EmbeddingRegistry[rawText]

        private val idCounter = java.util.concurrent.atomic.AtomicLong(0L)
        fun nextNodeId(): String = "n" + "%08d".format(idCounter.incrementAndGet())
        fun resetIdCounter() = idCounter.set(0L)
    }
    // isLeaf is true iff this node has NO outgoing edges of either kind. Parent count is
    // deliberately irrelevant: a leaf that gains a second parent through a cross-link
    // proposal is still a leaf — it must remain a routing destination and a J-cell,
    // now reachable from both branches. (The old `!isBridge && parents.size <= 1` clause
    // silently orphaned every cross-link target: the moment a leaf was bridged it left
    // the leaf set and could receive no membership at all.)
    val isLeaf: Boolean get() = children.isEmpty() && crossLinkChildren.isEmpty()

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

    /** This node is BRIDGED: it has more than one parent, i.e. it is a polyhierarchy target. */
    val isBridged: Boolean get() = parents.size > 1

    /**
     * This node HOSTS cross-links. Distinct from [isBridged] — a domain that hosts a bridge is
     * not itself cross-domain, and conflating the two counted 12 of 14 domains as bridges.
     */
    val hasCrossLinks: Boolean get() = crossLinkChildren.isNotEmpty()

    // Proportional weight of this node as a component in its parent's vMF/NiW
    var proportionalWeight: Double = 1.0

    // Fingerprints for judge caching and validation
    var judgeCorpusFingerprint: String? = null
    var judgeModelVersion: String? = null

    // treeParentId: set once by the splitter, never cleared by merger or transitive reduction
    var treeParentId: String? = null

    // Jensen-tight shrinkage factor r_bar_p for descent gate
    var childCentroidShrinkage: Double = 1.0

    /**
     * cos(mu_v, sum_c w_c mu_c) — 1.0 iff this node's fitted direction coincides with its
     * children's mass-weighted resultant, which is what the descent-gate derivation assumes.
     * Anything below 1.0 is the gap descentMargin is paying for. NaN when undefined (no
     * children, or an unfitted node).
     */
    var muResultantCosine: Double = Double.NaN

    fun updateChildCentroidShrinkage() {
        val childrenList = buildList {
            addAll(children)
            addAll(crossLinkChildren)
        }
        if (childrenList.isEmpty()) {
            childCentroidShrinkage = 1.0
            return
        }
        val k = childrenList.size
        val weights = DoubleArray(k)
        var sumW = 0.0
        for (i in 0 until k) {
            val child = childrenList[i]
            val mass = child.queryWeights.values.sum()
            weights[i] = mass
            sumW += mass
        }
        if (sumW > 0.0) {
            for (i in 0 until k) {
                weights[i] /= sumW
            }
        } else {
            for (i in 0 until k) {
                weights[i] = 1.0 / k
            }
        }
        val dim = childrenList[0].vmfMu.size
        if (dim == 0) {
            childCentroidShrinkage = 1.0
            return
        }
        val sumVector = DoubleArray(dim)
        for (i in 0 until k) {
            val child = childrenList[i]
            if (child.vmfMu.size == dim) {
                val w = weights[i]
                for (j in 0 until dim) {
                    sumVector[j] += w * child.vmfMu[j]
                }
            }
        }
        var sumSq = 0.0
        for (j in 0 until dim) {
            sumSq += sumVector[j] * sumVector[j]
        }
        childCentroidShrinkage = Math.sqrt(sumSq).coerceIn(0.0, 1.0)

        // Angle between this node's own fitted direction and the mass-weighted resultant of its
        // children's directions.
        //
        // The descent gate's derivation assumes these are the same vector. If they were, the
        // gate would be a tautology: r_v <mu_v, x> = sum_c w_c <mu_c, x> <= max_c <mu_c, x> by
        // Jensen, so it would always descend and no query could ever residualise. It fires only
        // because mu_v is fitted independently on the node's own queries while the resultant
        // re-normalises each child (each child's contribution carries a 1/r_c inflation, so
        // diffuse children are up-weighted relative to their share of the parent's own fit).
        // descentMargin absorbs that gap, so measuring it directly turns delta from a
        // calibrated constant into a quantified correction.
        val ownDim = minOf(dim, vmfMu.size)
        if (ownDim > 0 && childCentroidShrinkage > 1e-12) {
            var dot = 0.0
            var ownNorm = 0.0
            for (j in 0 until ownDim) {
                dot += vmfMu[j] * sumVector[j]
                ownNorm += vmfMu[j].toDouble() * vmfMu[j].toDouble()
            }
            ownNorm = Math.sqrt(ownNorm)
            muResultantCosine = if (ownNorm > 1e-12)
                (dot / (ownNorm * childCentroidShrinkage)).coerceIn(-1.0, 1.0)
            else Double.NaN
        } else {
            muResultantCosine = Double.NaN
        }
    }

    fun updateAllShrinkages() {
        val visited = mutableSetOf<String>()
        fun walk(node: GraphNode) {
            if (!visited.add(node.id)) return
            node.updateChildCentroidShrinkage()
            node.children.forEach { walk(it) }
            node.crossLinkChildren.forEach { walk(it) }
        }
        walk(this)
    }


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

/**
 * MRL slice width for a given depth. Flat 256 at every depth — the argument is
 * deliberately unused.
 *
 * This was a real design axis: a per-depth Matryoshka ladder (128 at the root,
 * widening with depth) so coarse levels compared on a cheap prefix and fine levels
 * used the full vector. It was flattened to a constant after the ladder proved to
 * cost accuracy at the coarse end without buying speed at the fine end, since every
 * gate that matters — routing, the separation statistic, the vMF posterior — runs at
 * the child dimension anyway.
 *
 * Kept as a function rather than inlined because it is the SINGLE SOURCE OF TRUTH for
 * that width across 11 call sites (TaxonomyFitter, TaxonomyMerger, TaxonomySplitter,
 * EmbeddingCache, TaxonomyPersistence, the engine's dimension fast-fail). Inlining
 * would scatter the literal 256 across all of them and make reintroducing a ladder —
 * or changing the width for a different embedding model — an edit in 11 places
 * instead of one. The unused parameter is the price of keeping the seam.
 */
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
                    q.queryId = QuestionIdRegistry.lookup(q.rawText)
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
                    if (q.queryId != -1) {
                        textToId[q.rawText] = q.queryId
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
                    q.queryId = textToId[q.rawText] ?: q.queryId
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

class GraphStateBackup(root: GraphNode) {
    private val nodeStates = mutableMapOf<String, NodeState>()
    private val rootRef = root

    class NodeState(
        val children: List<String>,
        val crossLinkChildren: List<String>,
        val parents: List<String>,
        val queryWeights: Map<String, Double>,
        val queries: List<Embedding>,
        val residualQueries: Set<String>,
        val residualConfidences: Map<String, Double>,
        val isBridge: Boolean,
        val vmfMu: FloatArray,
        val vmfKappa: Double,
        val vmfLogNormalizer: Double,
        val depth: Int,
        val label: String?,
        val originalCategory: String?,
        val treeParentId: String?,
        val childCentroidShrinkage: Double
    )

    init {
        val visited = mutableSetOf<String>()
        fun walk(n: GraphNode) {
            if (!visited.add(n.id)) return
            nodeStates[n.id] = NodeState(
                children = n.children.map { it.id },
                crossLinkChildren = n.crossLinkChildren.map { it.id },
                parents = n.parents.map { it.id },
                queryWeights = n.queryWeights.toMap(),
                queries = n.queries.toList(),
                residualQueries = n.residualQueries.toSet(),
                residualConfidences = n.residualConfidences.toMap(),
                isBridge = n.isBridge,
                vmfMu = n.vmfMu.copyOf(),
                vmfKappa = n.vmfKappa,
                vmfLogNormalizer = n.vmfLogNormalizer,
                depth = n.depth,
                label = n.label,
                originalCategory = n.originalCategory,
                treeParentId = n.treeParentId,
                childCentroidShrinkage = n.childCentroidShrinkage
            )
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(rootRef)
    }

    fun restore(registry: Map<String, GraphNode>) {
        for ((id, state) in nodeStates) {
            val node = registry[id] ?: continue
            node.children.clear()
            node.crossLinkChildren.clear()
            node.parents.clear()
            node.queryWeights.clear()
            node.queryWeights.putAll(state.queryWeights)
            node.queries.clear()
            node.queries.addAll(state.queries)
            node.residualQueries.clear()
            node.residualQueries.addAll(state.residualQueries)
            node.residualConfidences.clear()
            node.residualConfidences.putAll(state.residualConfidences)
            node.isBridge = state.isBridge
            node.vmfMu = state.vmfMu.copyOf()
            node.vmfKappa = state.vmfKappa
            node.vmfLogNormalizer = state.vmfLogNormalizer
            node.depth = state.depth
            node.label = state.label
            node.originalCategory = state.originalCategory
            node.treeParentId = state.treeParentId
            node.childCentroidShrinkage = state.childCentroidShrinkage
        }
        for ((id, state) in nodeStates) {
            val node = registry[id] ?: continue
            state.children.forEach { cid ->
                registry[cid]?.let { node.children.add(it) }
            }
            state.crossLinkChildren.forEach { cid ->
                registry[cid]?.let { node.crossLinkChildren.add(it) }
            }
            state.parents.forEach { pid ->
                registry[pid]?.let { node.parents.add(it) }
            }
        }
    }
}

@JvmInline
value class DagRoot(val node: GraphNode) {
    init {
        require(node.parents.isEmpty() && node.depth == 0) {
            "DagRoot must be the true root of the taxonomy (no parents, depth 0), got node '${node.label}' with depth ${node.depth} and ${node.parents.size} parents"
        }
    }
}
