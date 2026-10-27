package taxonomy.operations

import org.slf4j.LoggerFactory
import taxonomy.config.TaxonomyConfig
import taxonomy.model.Embedding
import taxonomy.model.EmbeddingSlice
import taxonomy.model.GraphNode
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.MessageDigest

/**
 * PERF-8: exact-content, fail-closed, default-off memo of proposal outcomes that survives
 * `TaxonomyOperations.invalidateCachedJ()`.
 *
 * ## Why a second memo
 *
 * The lossy fingerprint memo in [TaxonomyOperations.tryProposal] is keyed on
 * `(site|proposalKey, population hash, mu hash, n, mass)` and is cleared on every re-route, so
 * it never hits across iterations. Its key is deliberately lossy (raw weight and kappa bits are
 * excluded because they drift at ~1e-13 forever), and that lossiness is what produced the
 * false-hit incident on record (a rejected k=2 memo-skipping k=3, `TaxonomyOperations.kt`
 * k-fallback GUARD comment). This memo takes the opposite stance: the key is a SHA-256 over
 * every input that determines a proposal's outcome, so a hit is only possible when the entire
 * DAG state, the corpus, the run regime and the action identity are bit-identical to a state
 * already decided. It is therefore useless across states that differ in a single ulp — and
 * that is the point: it can never produce the incident class, and the hit counters report
 * honestly whether the loop reaches a bit fixed point (docs/perf_review_2026-09-09.md item 8).
 *
 * ## What the key covers
 *
 * 1. **DAG state digest** — every node reachable from the root via `children` and
 *    `crossLinkChildren`, sorted by id, with every field the proposal path reads AND every
 *    field the persistence layer writes (so "post-evaluation digest == pre-evaluation
 *    digest" means "the snapshot would be byte-identical"): id, label, originalCategory,
 *    description, depth, sliceDim, treeParentId, isBridge, bridgeJsDivergence,
 *    proportionalWeight, phaseCompleted, dasguptaDeltaNorm, dOverN, childCentroidShrinkage,
 *    vmfKappa, vmfLogNormalizer, vmfMu (raw bits), niwKappa0, niwNu0, niwM0, niwLambda (raw
 *    bits), judgePrompt, judgeRubric, judgeGtAgreement, judgeCorpusFingerprint,
 *    judgeModelVersion, children / crossLinkChildren / parents ids IN WALK (ITERATION) ORDER,
 *    deliberately not sorted (the order is load-bearing: `updateChildCentroidShrinkage`
 *    accumulates over `children + crossLinkChildren` in iteration order, the trickler and
 *    every branch walk iterate children in iteration order — so two states whose edge sets
 *    are equal but walk differently are different keys; the sets are ConcurrentHashMap key
 *    sets, and GraphStateBackup re-inserts in the captured order, so a restored evaluation
 *    digests identically), queryWeights sorted by key (key, raw bits), the rawText of every
 *    entry of `queries` SORTED — content-exact but deliberately NOT in list order: the list
 *    order is a scheduling artifact (`reassignQueries` routes chunks concurrently and appends
 *    to `leaf.queries` in arrival order under the per-leaf lock), so hashing it would change
 *    the digest on every re-route and the memo could never hit across iterations. Its only
 *    order-sensitive readers are the `queryWeights.isEmpty()` fallback branches of
 *    `getAllQueriesInBranch` / `getAllQueriesInRegion`, unreachable in the lockstep regime (a
 *    node has `queries` iff it has `queryWeights`), and the LLM labelling sample, which is not
 *    a proposal outcome. Then sorted residualQueries (a set), residualConfidences sorted by
 *    key (key, raw bits).
 *    Excluded, documented: `muResultantCosine` (recomputed from mu and children by
 *    updateChildCentroidShrinkage, read only by an engine log line, not persisted).
 * 2. **Corpus digest** — the `allEmbeddings` list in list order: rawText, groundTruthCategory,
 *    `values` raw bits. Hashed once per list identity (the engine passes the same `uniqueEmbs`
 *    list for a whole run); the per-call part re-hashes the queryId sequence, the list size
 *    and the groundTruthMap size, because `assignQueryIds` rewrites queryIds after every
 *    structural phase.
 * 3. **Run-regime digest** — [EmbeddingSlice.width], the gt-bias regime
 *    (`enableGtWarmStart && currentIteration <= 1`), and a reflective dump of every non-static
 *    field of `FormalismConfig` and `DiagnosticsConfig` sorted by name, so a config key added
 *    later cannot be forgotten.
 *
 * Plus the proposal identity: `(siteId, proposalType, actionId)`.
 *
 * ## Storage and invalidation
 *
 * All entries live under a single `currentStateDigest`. On every lookup or store whose digest
 * differs, every entry is dropped (`invalidations += dropped`, `stateChanges += 1`). That
 * makes "invalidate whenever any input changes" literal — the input is the whole state and
 * entries from a different state cannot exist — and bounds memory to proposals-per-state.
 * Survival across `invalidateCachedJ()` is then automatic.
 *
 * ## Fail-closed
 *
 * - Mode defaults to [MemoMode.OFF]; an unknown mode string is a parse error, never silently on.
 * - An entry is stored only if the evaluation left the state digest unchanged (the action's
 *   side effects were fully restored). An action with unrestored side effects (e.g. a fusion
 *   blends the target's NiW posterior, which `GraphStateBackup` does not restore) is counted in
 *   [notStoredSideEffects] and never memoized.
 * - The invariant "the second execution of an action consumes exactly the same node ids and
 *   labels as the first" is asserted on every miss; a violation self-disables the memo for
 *   the rest of the run ([disabledReason]) and every later proposal is fully evaluated.
 * - Reentrant use disables the memo the same way.
 * - The lossy fingerprint memo stays first in every mode, exactly as on the off path: a lossy
 *   hit burns no ids, so bypassing it would make an ON run drift from the off run. The exact
 *   memo decides only where the lossy one missed, never stores what it answered unevaluated
 *   ([lossyShadowed]), and a hit replays the lossy add the evaluation would have made.
 * - Mode [MemoMode.SHADOW] computes keys and stores entries but skips nothing: on a would-be hit
 *   the full evaluation still runs and its outcome and counter consumption are compared with
 *   the entry ([shadowHits], [shadowMismatches]) — every mismatch class, including a full
 *   evaluation that ACCEPTS where the entry says REJECTED / NO_PROPOSAL (the class an ON run
 *   could never observe, because it would have replayed the entry).
 */
enum class MemoMode {
    OFF, SHADOW, ON;

    companion object {
        /** Strict: `off` | `shadow` | `on` (case-insensitive). Anything else throws. */
        fun parse(s: String): MemoMode = when (s.trim().lowercase()) {
            "off" -> OFF
            "shadow" -> SHADOW
            "on" -> ON
            else -> throw IllegalArgumentException(
                "proposalMemo must be one of off | shadow | on (got '$s')"
            )
        }
    }
}

/** The exact key: a full-context digest plus the proposal identity. */
data class MemoKey(
    val stateDigest: String,
    val siteId: String,
    val type: ProposalType,
    val actionId: String
) {
    val proposalId: Triple<String, ProposalType, String> get() = Triple(siteId, type, actionId)
}

/** A decided, non-accepting outcome together with the side effects a replay must reproduce. */
data class MemoEntry(
    val outcome: ProposalOutcome,
    /** Node ids consumed by ONE execution of the action (`GraphNode.nextNodeId`). */
    val idsConsumed: Long,
    /** Concept labels consumed by ONE execution of the action (`TaxonomySplitter.conceptCounter`). */
    val labelsConsumed: Int,
    val firstIter: Int,
    val dJ: Double?,
    val dV: Int?,
    val reason: String?
)

class ProposalMemo {
    private val log = LoggerFactory.getLogger("taxonomy.ProposalMemo")

    var mode: MemoMode = MemoMode.OFF
        private set

    @Volatile
    var disabledReason: String? = null
        private set

    /** The hot path consults the memo only when this is true. */
    val active: Boolean get() = mode != MemoMode.OFF && disabledReason == null

    // ── counters ───────────────────────────────────────────────────────────────
    var hits: Long = 0; private set
    var misses: Long = 0; private set
    var invalidations: Long = 0; private set
    var stateChanges: Long = 0; private set
    var shadowHits: Long = 0; private set
    var shadowMismatches: Long = 0; private set
    var replayedIds: Long = 0; private set
    var replayedLabels: Long = 0; private set
    var notStoredSideEffects: Long = 0; private set
    /** Proposals the lossy fingerprint memo answered before the exact memo could (all modes). */
    var lossyShadowed: Long = 0; private set
    var digestNanos: Long = 0; private set
    val digestMillis: Long get() = digestNanos / 1_000_000L

    private var currentStateDigest: String? = null
    private val entries = HashMap<Triple<String, ProposalType, String>, MemoEntry>()
    val size: Int get() = entries.size

    // Corpus content digest, cached per list identity (see class doc, item 2).
    private var corpusRef: List<Embedding>? = null
    private var corpusContentDigest: ByteArray? = null

    /** Per-run reset. Called by the engine next to resetConceptCounter/resetIdCounter. */
    fun reset(mode: MemoMode) {
        this.mode = mode
        disabledReason = null
        hits = 0; misses = 0; invalidations = 0; stateChanges = 0
        shadowHits = 0; shadowMismatches = 0; replayedIds = 0; replayedLabels = 0
        notStoredSideEffects = 0; lossyShadowed = 0; digestNanos = 0
        currentStateDigest = null
        entries.clear()
        corpusRef = null
        corpusContentDigest = null
    }

    /** Fail-closed: stop consulting the memo for the rest of the run. Entries are dropped. */
    fun disable(reason: String) {
        if (disabledReason == null) {
            log.error("[MEMO-X] DISABLED for the rest of the run: $reason")
            disabledReason = reason
        }
        entries.clear()
        currentStateDigest = null
    }

    // ── key ────────────────────────────────────────────────────────────────────

    /**
     * The exact key for a proposal in the CURRENT state. Computed at every call (never cached
     * across proposals: the merger mutates state outside tryProposal).
     */
    fun keyFor(
        root: GraphNode,
        allEmbeddings: List<Embedding>,
        groundTruthMap: Map<String, List<String>>,
        config: TaxonomyConfig,
        currentIteration: Int,
        site: GraphNode,
        type: ProposalType,
        actionId: String
    ): MemoKey {
        val digest = stateDigest(root, allEmbeddings, groundTruthMap, config, currentIteration)
        return MemoKey(digest, site.id, type, actionId)
    }

    /** The full-context digest alone (DAG + corpus + regime), as 64 hex chars. Timed. */
    fun stateDigest(
        root: GraphNode,
        allEmbeddings: List<Embedding>,
        groundTruthMap: Map<String, List<String>>,
        config: TaxonomyConfig,
        currentIteration: Int
    ): String {
        val t0 = System.nanoTime()
        try {
            val sink = DigestSink()
            sink.str("dag")
            StateDigest.dag(sink, root)
            sink.str("corpus")
            sink.bytes(corpusContent(allEmbeddings))
            StateDigest.corpusPerCall(sink, allEmbeddings, groundTruthMap)
            sink.str("regime")
            StateDigest.regime(sink, config, currentIteration)
            return hex(sink.digest())
        } finally {
            digestNanos += System.nanoTime() - t0
        }
    }

    private fun corpusContent(allEmbeddings: List<Embedding>): ByteArray {
        val cached = corpusContentDigest
        if (cached != null && corpusRef === allEmbeddings) return cached
        val sink = DigestSink()
        StateDigest.corpusContent(sink, allEmbeddings)
        val d = sink.digest()
        corpusRef = allEmbeddings
        corpusContentDigest = d
        return d
    }

    // ── lookup / store ─────────────────────────────────────────────────────────

    private fun adopt(stateDigest: String) {
        if (currentStateDigest != stateDigest) {
            if (currentStateDigest != null) {
                invalidations += entries.size
                stateChanges += 1
            }
            entries.clear()
            currentStateDigest = stateDigest
        }
    }

    /**
     * Null on a miss. Drops every entry of a different state first. Counts nothing: the hot
     * path calls [recordMiss] only once it knows the lossy fingerprint memo did NOT answer the
     * proposal (a lossy-answered absent entry is [lossyShadowed], not a miss, so the three
     * classes miss / hit / lossyShadowed partition the calls that reach the memo); [hits] is
     * counted by [recordHit] when a replay actually happens (shadow mode skips nothing, so its
     * would-be hits are [shadowHits] and [hits] stays 0).
     */
    fun lookup(key: MemoKey): MemoEntry? {
        adopt(key.stateDigest)
        return entries[key.proposalId]
    }

    /** A proposal with no entry that the lossy memo did not answer, i.e. a full evaluation. */
    fun recordMiss() { misses += 1 }

    /** Stores a non-accepting outcome under the key's state. ACCEPTED is never stored. */
    fun store(key: MemoKey, entry: MemoEntry) {
        require(entry.outcome != ProposalOutcome.ACCEPTED) { "ACCEPTED outcomes are never memoized" }
        adopt(key.stateDigest)
        entries[key.proposalId] = entry
    }

    fun recordHit(ids: Long, labels: Long) {
        hits += 1
        replayedIds += ids
        replayedLabels += labels
    }

    fun recordShadowHit(mismatch: String?) {
        shadowHits += 1
        if (mismatch != null) {
            shadowMismatches += 1
            log.error("[MEMO-X SHADOW MISMATCH] $mismatch")
        }
    }

    fun recordNotStored() { notStoredSideEffects += 1 }

    fun recordLossyShadowed() { lossyShadowed += 1 }

    // ── reporting ──────────────────────────────────────────────────────────────

    data class Snapshot(
        val mode: String,
        val hits: Long,
        val misses: Long,
        val invalidations: Long,
        val stateChanges: Long,
        val shadowHits: Long,
        val shadowMismatches: Long,
        val replayedIds: Long,
        val replayedLabels: Long,
        val notStoredSideEffects: Long,
        val lossyShadowed: Long,
        val digestMs: Long,
        val disabledReason: String?
    )

    fun snapshot(): Snapshot = Snapshot(
        mode = mode.name.lowercase(),
        hits = hits, misses = misses, invalidations = invalidations, stateChanges = stateChanges,
        shadowHits = shadowHits, shadowMismatches = shadowMismatches,
        replayedIds = replayedIds, replayedLabels = replayedLabels,
        notStoredSideEffects = notStoredSideEffects, lossyShadowed = lossyShadowed,
        digestMs = digestMillis, disabledReason = disabledReason
    )

    fun summary(): String {
        val s = snapshot()
        return "[MEMO-X] mode=${s.mode} hits=${s.hits} misses=${s.misses} inval=${s.invalidations}" +
            " states=${s.stateChanges} shadowHits=${s.shadowHits} shadowMismatch=${s.shadowMismatches}" +
            " replayedIds=${s.replayedIds} replayedLabels=${s.replayedLabels}" +
            " notStored=${s.notStoredSideEffects} lossyShadowed=${s.lossyShadowed} digestMs=${s.digestMs}" +
            (s.disabledReason?.let { " DISABLED($it)" } ?: "")
    }

    companion object {
        fun hex(b: ByteArray): String {
            val sb = StringBuilder(b.size * 2)
            for (x in b) sb.append(String.format(java.util.Locale.US, "%02x", x.toInt() and 0xff))
            return sb.toString()
        }
    }
}

/**
 * Canonical byte stream into SHA-256. Every string is UTF-8 with a 4-byte length prefix (-1
 * for null), every double via raw long bits, every float via raw int bits, every list with a
 * length prefix, so that `0.0` and `-0.0`, or one ulp, are different keys.
 */
internal class DigestSink {
    private val md: MessageDigest = MessageDigest.getInstance("SHA-256")
    private val buf: ByteBuffer = ByteBuffer.allocate(1 shl 16).order(ByteOrder.BIG_ENDIAN)

    private fun ensure(n: Int) { if (buf.remaining() < n) flush() }
    private fun flush() { buf.flip(); md.update(buf); buf.clear() }

    fun int(v: Int) { ensure(4); buf.putInt(v) }
    fun long(v: Long) { ensure(8); buf.putLong(v) }
    fun double(v: Double) = long(java.lang.Double.doubleToRawLongBits(v))
    fun float(v: Float) = int(java.lang.Float.floatToRawIntBits(v))
    fun bool(v: Boolean) { ensure(1); buf.put(if (v) 1 else 0) }
    fun str(s: String?) {
        if (s == null) { int(-1); return }
        val b = s.toByteArray(Charsets.UTF_8)
        int(b.size)
        bytes(b)
    }
    fun bytes(b: ByteArray) {
        var off = 0
        while (off < b.size) {
            if (!buf.hasRemaining()) flush()
            val n = minOf(buf.remaining(), b.size - off)
            buf.put(b, off, n)
            off += n
        }
    }
    fun floats(a: FloatArray) { int(a.size); for (f in a) float(f) }
    fun strs(l: List<String>) { int(l.size); for (s in l) str(s) }
    fun digest(): ByteArray { flush(); return md.digest() }
}

/** The three digest builders. Pure functions of their inputs. */
internal object StateDigest {

    fun reachable(root: GraphNode): List<GraphNode> {
        val seen = HashMap<String, GraphNode>()
        val queue = ArrayDeque<GraphNode>().apply { add(root) }
        while (queue.isNotEmpty()) {
            val n = queue.removeFirst()
            if (seen.put(n.id, n) != null) continue
            queue.addAll(n.children)
            queue.addAll(n.crossLinkChildren)
        }
        return seen.values.sortedBy { it.id }
    }

    fun dag(sink: DigestSink, root: GraphNode) {
        val nodes = reachable(root)
        sink.int(nodes.size)
        for (n in nodes) node(sink, n)
    }

    fun node(sink: DigestSink, n: GraphNode) {
        sink.str(n.id)
        sink.str(n.label)
        sink.str(n.originalCategory)
        sink.str(n.description)
        sink.int(n.depth)
        sink.int(n.sliceDim)
        sink.str(n.treeParentId)
        sink.bool(n.isBridge)
        sink.double(n.bridgeJsDivergence)
        sink.double(n.proportionalWeight)
        sink.int(n.phaseCompleted)
        sink.double(n.dasguptaDeltaNorm)
        sink.double(n.dOverN)
        sink.double(n.childCentroidShrinkage)
        sink.double(n.vmfKappa)
        sink.double(n.vmfLogNormalizer)
        sink.floats(n.vmfMu)
        sink.double(n.niwKappa0)
        sink.double(n.niwNu0)
        sink.floats(n.niwM0)
        sink.floats(n.niwLambda)
        sink.str(n.judgePrompt)
        sink.str(n.judgeRubric)
        sink.double(n.judgeGtAgreement ?: Double.NaN)
        sink.bool(n.judgeGtAgreement == null)
        sink.str(n.judgeCorpusFingerprint)
        sink.str(n.judgeModelVersion)
        // Edge collections in WALK (iteration) order, deliberately unsorted: class doc, item 1.
        sink.strs(n.children.map { it.id })
        sink.strs(n.crossLinkChildren.map { it.id })
        sink.strs(n.parents.map { it.id })
        val weights = n.queryWeights.entries.sortedBy { it.key }
        sink.int(weights.size)
        for ((k, w) in weights) { sink.str(k); sink.double(w) }
        // The routed query list as a SORTED multiset (not list order: class doc, item 1).
        sink.strs(synchronized(n.queries) { n.queries.map { it.rawText } }.sorted())
        sink.strs(n.residualQueries.sorted())
        val conf = n.residualConfidences.entries.sortedBy { it.key }
        sink.int(conf.size)
        for ((k, c) in conf) { sink.str(k); sink.double(c) }
    }

    /** The expensive part: list order, rawText, groundTruthCategory and raw value bits. */
    fun corpusContent(sink: DigestSink, allEmbeddings: List<Embedding>) {
        sink.int(allEmbeddings.size)
        for (e in allEmbeddings) {
            sink.str(e.rawText)
            sink.str(e.groundTruthCategory)
            sink.floats(e.values)
        }
    }

    /** The cheap part that can change between calls on the same list. */
    fun corpusPerCall(sink: DigestSink, allEmbeddings: List<Embedding>, groundTruthMap: Map<String, List<String>>) {
        sink.int(allEmbeddings.size)
        for (e in allEmbeddings) sink.int(e.queryId)
        sink.int(groundTruthMap.size)
    }

    fun regime(sink: DigestSink, config: TaxonomyConfig, currentIteration: Int) {
        sink.int(EmbeddingSlice.width)
        sink.bool(config.formalism.enableGtWarmStart && currentIteration <= 1)
        sink.str("formalism")
        reflect(sink, config.formalism)
        sink.str("diagnostics")
        reflect(sink, config.diagnostics)
    }

    /**
     * Every non-static declared field of [obj], sorted by name, with a typed canonical
     * encoding. Reflection rather than a hand-written list so a config key added later cannot
     * be forgotten (the omission class the incident belongs to).
     */
    fun reflect(sink: DigestSink, obj: Any) {
        val fields = obj.javaClass.declaredFields
            .filter { !java.lang.reflect.Modifier.isStatic(it.modifiers) && !it.isSynthetic }
            .sortedBy { it.name }
        sink.int(fields.size)
        for (f in fields) {
            f.isAccessible = true
            sink.str(f.name)
            value(sink, f.get(obj))
        }
    }

    private fun value(sink: DigestSink, v: Any?) {
        when (v) {
            null -> sink.str(null)
            is Double -> { sink.str("D"); sink.double(v) }
            is Float -> { sink.str("F"); sink.float(v) }
            is Int -> { sink.str("I"); sink.int(v) }
            is Long -> { sink.str("L"); sink.long(v) }
            is Short -> { sink.str("S"); sink.int(v.toInt()) }
            is Byte -> { sink.str("B"); sink.int(v.toInt()) }
            is Boolean -> { sink.str("Z"); sink.bool(v) }
            is String -> { sink.str("s"); sink.str(v) }
            is Enum<*> -> { sink.str("E"); sink.str(v.name) }
            is Map<*, *> -> {
                sink.str("M")
                val es = v.entries.sortedBy { it.key.toString() }
                sink.int(es.size)
                for ((k, x) in es) { sink.str(k.toString()); value(sink, x) }
            }
            is Set<*> -> {
                sink.str("T")
                val xs = v.map { it.toString() }.sorted()
                sink.strs(xs)
            }
            is Collection<*> -> {
                sink.str("C")
                sink.int(v.size)
                for (x in v) value(sink, x)
            }
            is DoubleArray -> { sink.str("[D"); sink.int(v.size); for (x in v) sink.double(x) }
            is FloatArray -> { sink.str("[F"); sink.floats(v) }
            is IntArray -> { sink.str("[I"); sink.int(v.size); for (x in v) sink.int(x) }
            else -> { sink.str("O"); sink.str(v.toString()) }
        }
    }
}
