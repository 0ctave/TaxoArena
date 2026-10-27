package taxonomy.service

import taxonomy.dataset.CorpusDomains
import taxonomy.dataset.ReservedPool
import taxonomy.model.GraphNode

/**
 * Federated multi-corpus assembly (docs/multi_corpus_design.md, "Stage 1 certification result …
 * design adjustment", stage 1b): the union taxonomy is not grown; it is GRAFTED from per-corpus
 * snapshots, each built alone with its own loop, split and site null. The union root is a
 * routing layer whose depth-1 children are the per-corpus roots; everything beneath them is the
 * per-corpus tree, byte-for-byte (same ids up to a source prefix, same fits, same soft weights).
 *
 * Three pure operations, each unit-tested on its own:
 *  * [rekey] re-keys one serialized graph so its node ids cannot collide with another
 *    snapshot's (`<SOURCE>:<id>`) and shifts every depth by one level;
 *  * [graft] attaches the loaded per-corpus roots under a fresh union root and verifies the
 *    result (unique ids, tree depths parent + 1);
 *  * [unionReservedPools] merges the per-corpus reserved pools; the union's pool id is the
 *    ordinary content hash ([ReservedPool.computePoolId]) of the merged map, so it is exactly
 *    what a single run over the same held-out questions would have recorded.
 *
 * No LLM calls, no refits of any grafted node: the only fit the runner performs afterwards is
 * the union root's own vMF (the engine's bootstrap fit for a root), which routing needs for
 * its descent gate.
 */
object UnionGraft {
    /** Id of the union root; every grafted id carries a `<SOURCE>:` prefix, so it cannot collide. */
    const val UNION_ROOT_ID = "union"
    const val ID_SEPARATOR = ':'

    fun prefixedId(prefix: String, id: String): String = "$prefix$ID_SEPARATOR$id"

    /**
     * Re-keys every node id of [graph] as `<prefix>:<id>` — the root id, child, cross-link,
     * parent and tree-parent references included — and shifts every depth by [depthShift].
     * Query ids, weights and residual ids are corpus-content keys (q_<hash>, question ids) and
     * stay untouched.
     */
    fun rekey(graph: SerializedGraph, prefix: String, depthShift: Int = 1): SerializedGraph {
        require(prefix.isNotBlank()) { "rekey prefix must not be blank" }
        require(ID_SEPARATOR !in prefix) { "rekey prefix '$prefix' must not contain '$ID_SEPARATOR'" }
        require(depthShift >= 0) { "depthShift must be >= 0, got $depthShift" }
        fun p(id: String) = prefixedId(prefix, id)
        val ids = graph.nodes.map { it.id }
        require(ids.size == ids.toSet().size) { "graph has duplicate node ids before rekeying" }
        require(graph.rootId in ids) { "graph root '${graph.rootId}' is not among its nodes" }
        return graph.copy(
            rootId = p(graph.rootId),
            nodes = graph.nodes.map { n ->
                n.copy(
                    id = p(n.id),
                    depth = n.depth + depthShift,
                    childIds = n.childIds.map(::p),
                    crossLinkChildIds = n.crossLinkChildIds.map(::p),
                    parentIds = n.parentIds.map(::p),
                    treeParentId = n.treeParentId?.let(::p)
                )
            }
        )
    }

    /**
     * Builds the union root labelled [label] and attaches each of [roots] as a depth-1 child.
     * Each root must be parentless and already sit at depth 1 (i.e. loaded from a graph
     * [rekey]ed with `depthShift = 1`). The assembled graph is [verify]ed before it is returned.
     */
    fun graft(label: String, roots: List<GraphNode>): GraphNode {
        require(roots.isNotEmpty()) { "a union needs at least one per-corpus root" }
        // Node sets are keyed by id, so a duplicate root id would be silently deduplicated
        // rather than caught by verify: check the roots explicitly.
        val dup = roots.groupBy { it.id }.filterValues { it.size > 1 }.keys
        check(dup.isEmpty()) { "duplicate node id among the per-corpus roots: $dup (rekey each snapshot with its source prefix)" }
        check(UNION_ROOT_ID !in roots.map { it.id }) { "a per-corpus root uses the union root id '$UNION_ROOT_ID'" }
        val union = GraphNode(id = UNION_ROOT_ID, label = label, depth = 0)
        for (r in roots) {
            require(r.parents.isEmpty()) { "per-corpus root '${r.label}' (${r.id}) already has a parent" }
            require(r.depth == 1) { "per-corpus root '${r.label}' (${r.id}) must arrive at depth 1 (rekey with depthShift = 1), got ${r.depth}" }
            r.parents.add(union)
            r.treeParentId = union.id
            union.children.add(r)
        }
        verify(union)
        return union
    }

    /** Every node reachable from [root] over tree and cross-link edges, each exactly once, BFS order. */
    fun nodes(root: GraphNode): List<GraphNode> {
        val seen = LinkedHashMap<String, GraphNode>()
        val queue = ArrayDeque<GraphNode>().apply { add(root) }
        while (queue.isNotEmpty()) {
            val n = queue.removeFirst()
            if (seen.putIfAbsent(n.id, n) != null) continue
            queue.addAll(n.children.sortedBy { it.id })
            queue.addAll(n.crossLinkChildren.sortedBy { it.id })
        }
        return seen.values.toList()
    }

    /**
     * Structural invariants of a grafted graph: node ids are unique (two distinct node objects
     * never share an id) and every tree child sits exactly one level below its parent. Cross-link
     * edges are not depth-constrained, as in the engine.
     */
    fun verify(root: GraphNode) {
        check(root.depth == 0 && root.parents.isEmpty()) { "union root must be parentless at depth 0" }
        val byId = HashMap<String, GraphNode>()
        val queue = ArrayDeque<GraphNode>().apply { add(root) }
        // GraphNode.equals is id-based, which is the very thing under test: track object identity.
        val objects = java.util.Collections.newSetFromMap(java.util.IdentityHashMap<GraphNode, Boolean>())
        while (queue.isNotEmpty()) {
            val n = queue.removeFirst()
            if (!objects.add(n)) continue
            val prev = byId.put(n.id, n)
            check(prev == null || prev === n) { "duplicate node id '${n.id}' in the union ('${prev?.label}' vs '${n.label}')" }
            for (c in n.children) {
                check(c.depth == n.depth + 1) { "tree child '${c.label}' (${c.id}) at depth ${c.depth} under '${n.label}' (${n.id}) at depth ${n.depth}" }
                queue.add(c)
            }
            queue.addAll(n.crossLinkChildren)
        }
    }

    /**
     * Union of per-corpus reserved pools, `source -> (domain key -> ids)`. Domain keys are
     * `<SOURCE>/<domain>` and must belong to their source and be disjoint across sources, so
     * the union is a plain concatenation; ids are kept verbatim (sentinels included, as in every
     * reserved_test_queries.json) — [poolId] applies the standard `> 0` filter when hashing.
     */
    fun unionReservedPools(pools: Map<String, Map<String, List<Int>>>): Map<String, List<Int>> {
        require(pools.isNotEmpty()) { "no reserved pools to merge" }
        val out = LinkedHashMap<String, List<Int>>()
        for ((source, pool) in pools) {
            require(pool.isNotEmpty()) { "reserved pool of '$source' is empty" }
            for ((key, ids) in pool) {
                val keySource = CorpusDomains.sourceOfKey(key)
                require(keySource == source) { "reserved domain key '$key' does not belong to source '$source' (parsed as '$keySource')" }
                require(key !in out) { "reserved domain key '$key' appears in more than one per-corpus pool" }
                out[key] = ids.toList()
            }
        }
        return out
    }

    /** Content id of a (union) pool: [ReservedPool.computePoolId] over the judgeable (id > 0) entries. */
    fun poolId(pool: Map<String, List<Int>>): String =
        ReservedPool.computePoolId(pool.mapValues { (_, ids) -> ids.filter { it > 0 } }.filterValues { it.isNotEmpty() })
}
