package taxonomy.model

import taxonomy.dataset.SplitSide

/**
 * TRAIN-only tree state (FRAMEWORK.md guard 3, item 18 TRAIN-ONLY-TREE): EVAL items never
 * enter a member set. This guard measures the invariant BY CONTENT, not by id: an id-list split
 * is not closed under text equality (sentinel-id duplicates of MMLU-Pro rows, GPQA sub-task
 * copies, ...), so a tree built on the "train" ids of record can still hold the text of an arena
 * question. Every member text is keyed by [SplitSide.stemKey] and counted against the EVAL keys.
 *
 * Wiring: FATAL after construction and after the union graft (HeadlessBenchmarkRunner), FATAL in
 * saveSnapshot with an expected pool, REPORT in loadSnapshot (an audit must stay able to load the
 * incident's frozen tree), FATAL before judging unless the exact count is acknowledged and
 * disclosed.
 */
object TrainOnlyGuard {

    /**
     * [count] is member slots (one per node holding an EVAL text); [distinctKeys] is the number
     * of distinct EVAL texts that are members, the figure a snapshot is acknowledged at.
     */
    data class Report(
        val count: Int,
        val distinctKeys: Int,
        val nodesHit: Int,
        val first: List<Pair<String, String>>
    ) {
        val clean: Boolean get() = count == 0
        override fun toString(): String =
            "$count EVAL item(s) in $nodesHit node(s), $distinctKeys distinct" +
                if (first.isEmpty()) "" else " (first: ${first.joinToString("; ") { "${it.first}:${it.second}" }})"
    }

    /**
     * RP12 ARCH-V2-E-T, "TrainOnlyGuard generalised to every generation artefact": the GLOBAL reserved
     * key set of a v2 build (every non-TRAIN item of the draw over all corpora, sentinels included;
     * [taxonomy.dataset.V2EnginePool.globalReservedKeys]), installed once by the runner before
     * construction. Every guard site unions it into its own EVAL keys ([withGlobal]) and judge induction
     * withholds any text it keys ([isGloballyReserved]). NOT installed (every non-v2 run) = the empty
     * set, and every site computes exactly what it computed before; [consultations] counts the reads so
     * a test can show the new code ran on the absent path too (the vacuity rule).
     */
    object GlobalReserved {
        @Volatile private var keys: Set<String> = emptySet()
        @Volatile var origin: String? = null
            private set
        private val reads = java.util.concurrent.atomic.AtomicLong()

        fun install(keys: Set<String>, origin: String) {
            require(keys.isNotEmpty()) { "[TRAIN-ONLY] refusing to install an empty global reserved key set ($origin)" }
            this.keys = keys
            this.origin = origin
        }

        fun clear() { keys = emptySet(); origin = null }
        fun installed(): Boolean = keys.isNotEmpty()
        fun keys(): Set<String> { reads.incrementAndGet(); return keys }
        fun consultations(): Long = reads.get()
    }

    /** [evalKeys] plus the installed global reserved keys (the same set when none is installed). */
    fun withGlobal(evalKeys: Set<String>): Set<String> {
        val g = GlobalReserved.keys()
        return if (g.isEmpty()) evalKeys else evalKeys + g
    }

    /** True iff a global key set is installed and [text]'s stem key is in it. */
    fun isGloballyReserved(text: String): Boolean {
        val g = GlobalReserved.keys()
        return g.isNotEmpty() && SplitSide.stemKey(text) in g
    }

    /** Stem keys of [texts]. */
    fun keysOf(texts: Collection<String>, keyFn: (String) -> String = SplitSide::stemKey): Set<String> =
        texts.mapTo(HashSet(texts.size)) { keyFn(it) }

    /**
     * Walks children and crossLinkChildren once and counts every member slot whose text keys
     * into [evalKeys]: node.queries (raw text), node.queryWeights keys (raw text after hydration)
     * and node.residualQueries (query-id strings resolved through the embedding registry, else
     * taken as raw text). A text held in several slots of one node is counted once per node.
     * [keyFn] is the content key (default [SplitSide.stemKey]); the audit harness also passes the
     * identity to reproduce an exact-text reading.
     */
    fun evalMembers(root: GraphNode, evalKeys: Set<String>, keyFn: (String) -> String = SplitSide::stemKey): Report {
        if (evalKeys.isEmpty()) return Report(0, 0, 0, emptyList())
        val idToText = HashMap<String, String>()
        for (e in GraphNode.EmbeddingRegistry.values) if (e.queryId >= 0) idToText[e.queryId.toString()] = e.rawText
        val visited = HashSet<String>()
        var count = 0
        var nodesHit = 0
        val distinct = HashSet<String>()
        val first = ArrayList<Pair<String, String>>()
        fun walk(node: GraphNode) {
            if (!visited.add(node.id)) return
            val texts = HashSet<String>()
            synchronized(node.queries) { for (q in node.queries) texts.add(q.rawText) }
            texts.addAll(node.queryWeights.keys)
            for (r in node.residualQueries) texts.add(idToText[r] ?: r)
            var hitHere = 0
            for (t in texts) {
                val k = keyFn(t)
                if (k in evalKeys) {
                    hitHere++
                    distinct.add(k)
                    if (first.size < 10) first.add(node.id to k.take(12))
                }
            }
            if (hitHere > 0) { nodesHit++; count += hitHere }
            node.children.forEach { walk(it) }
            node.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)
        return Report(count, distinct.size, nodesHit, first)
    }

    /** FATAL unless [report] is clean. */
    fun assertNone(report: Report, where: String) {
        check(report.clean) {
            "[TRAIN-ONLY] $where: ${report.count} EVAL items are members of ${report.nodesHit} nodes" +
                " (${report.distinctKeys} distinct; first: ${report.first.joinToString("; ") { "${it.first}:${it.second}" }})"
        }
    }

    /**
     * Parses `acknowledgedEvalMembers = ["<snapshotId>:<count>"]` entries; a snapshot is
     * acknowledged only at its exact count.
     */
    fun acknowledged(entries: List<String>, snapshotId: String?, count: Int): Boolean {
        if (snapshotId == null) return false
        return entries.any { e ->
            val i = e.lastIndexOf(':')
            i > 0 && e.substring(0, i) == snapshotId && e.substring(i + 1).trim().toIntOrNull() == count
        }
    }
}
