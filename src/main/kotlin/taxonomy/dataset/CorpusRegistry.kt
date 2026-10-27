package taxonomy.dataset

import org.springframework.stereotype.Component
import taxonomy.config.DatasetType
import java.util.concurrent.ConcurrentHashMap

/**
 * The set of corpora a run can draw on (docs/multi_corpus_design.md §3.1–3.2).
 *
 * Two layers, deliberately separate:
 *  * [Descriptor]s are static metadata (table name, id namespace, verifier) for every
 *    [DatasetType]; they are available from construction, so the eval store, loader and
 *    validator can resolve table names without depending on the fetcher bean.
 *  * [CorpusSource]s are the fetch adapters; [MMLUDatasetFetcher] registers one per type at
 *    start-up. Looking one up before registration is a programming error and fails loudly.
 *
 * MMLU_PRO keeps id offset 0, so every existing `eval_results.question_id`, pool id and ratings
 * row is unchanged; the leaderboard corpora (stage 1, [LEADERBOARD]) occupy the 1,000,000-wide
 * namespaces 1M..5M exactly as the multi-corpus DB registers them, MMLU_PRO_LB shares offset 0
 * (same TIGER-Lab ids), and the four other built-in types sit above them.
 */
@Component
class CorpusRegistry {

    /**
     * Static metadata of one corpus. [dbSource] is the value of `corpus_questions.source` /
     * `corpus_registry.source` in the multi-corpus DB: it equals [source] except for
     * MMLU_PRO_LB, the leaderboard's own MMLU-Pro samples, which the DB stores as `MMLU_PRO`
     * (same TIGER-Lab ids, hence the shared offset 0).
     */
    data class Descriptor(
        val source: String,
        val tableName: String,
        val idOffset: Int,
        val verifier: Verifier,
        val dbSource: String = source
    )

    private val sources = ConcurrentHashMap<String, CorpusSource>()

    fun register(source: CorpusSource) {
        require(source.name in KNOWN) { "CorpusSource '${source.name}' has no descriptor; add it to CorpusRegistry.BUILTIN or LEADERBOARD" }
        sources[source.name] = source
    }

    fun source(name: String): CorpusSource =
        sources[name] ?: throw IllegalStateException("No CorpusSource registered for '$name' (registered: ${sources.keys})")

    fun descriptor(name: String): Descriptor =
        KNOWN[name] ?: throw IllegalArgumentException("Unknown corpus '$name' (known: ${KNOWN.keys})")

    /** SQLite table holding [name]'s rows — `mmlu_pro` for MMLU_PRO, identical to the former `when`. */
    fun tableFor(name: String): String = descriptor(name).tableName

    fun verifierFor(name: String): Verifier = descriptor(name).verifier

    fun idOffsetFor(name: String): Int = descriptor(name).idOffset

    /** Every corpus name a config may list: the five built-in types plus the leaderboard sources. */
    val names: Set<String> get() = KNOWN.keys

    companion object {
        /** The corpus every existing artefact was built from. */
        const val DEFAULT_SOURCE = "MMLU_PRO"

        /** The dataset DB every single-corpus MMLU_PRO run has always opened. */
        const val DEFAULT_CORPUS_DB_PATH = "mmlu_pro_dataset_cache_v2.db"

        /** Width of one corpus's id namespace inside `eval_results.question_id`. */
        const val NAMESPACE_WIDTH = 1_000_000

        /** The one table of the multi-corpus DB (`tools/ingest/multicorpus_db.py`) holding every leaderboard corpus. */
        const val MULTI_CORPUS_TABLE = "corpus_questions"

        private val TABLES = mapOf(
            DatasetType.MMLU_PRO to "mmlu_pro",
            DatasetType.MMLU_ORIGINAL to "mmlu_original",
            DatasetType.ARC to "arc",
            DatasetType.TWENTY_NEWSGROUPS to "twenty_newsgroups",
            DatasetType.AG_NEWS to "ag_news",
            // LCB-STAGE0-INTERACTION: appended last, so its offset is (LEADERBOARD_COUNT + 5) x 1M = 10,000,000 and
            // every existing offset (0, 6M..9M) is unchanged.
            DatasetType.LIVECODEBENCH to "livecodebench",
            // INTENT-TRANSFER-S1: appended last, offset (LEADERBOARD_COUNT + 6) x 1M = 11,000,000; every existing offset
            // (0, 6M..10M) is unchanged.
            DatasetType.INTENT to "intent_corpus"
        )

        /**
         * Descriptors for the five built-in types, keyed by [DatasetType.name]. MMLU_PRO is
         * offset 0 (every existing id is unchanged); the four other legacy types — which have
         * never had an `eval_results` row or a pool — sit ABOVE the leaderboard namespaces
         * (6M..9M) so that every namespace in [KNOWN_OFFSETS] is disjoint.
         */
        val BUILTIN: Map<String, Descriptor> = DatasetType.entries.mapIndexed { i, t ->
            val offset = if (t == DatasetType.MMLU_PRO) 0 else (LEADERBOARD_COUNT + i) * NAMESPACE_WIDTH
            t.name to Descriptor(t.name, TABLES.getValue(t), offset, McLetter)
        }.toMap()

        /**
         * Stage 1: the Open LLM Leaderboard corpora, exactly as `tools/ingest/multicorpus_db.py`
         * registers them (`corpus_registry` rows; [LeaderboardCorpusSource] verifies the DB agrees
         * at fetch time). MMLU_PRO_LB is the leaderboard's own MMLU-Pro sample set: TIGER-Lab ids,
         * offset 0, stored under source `MMLU_PRO` in the DB.
         */
        val LEADERBOARD: Map<String, Descriptor> = listOf(
            Descriptor("MMLU_PRO_LB", MULTI_CORPUS_TABLE, 0, McLetter, dbSource = DEFAULT_SOURCE),
            Descriptor("BBH", MULTI_CORPUS_TABLE, 1 * NAMESPACE_WIDTH, Imported("acc_norm")),
            Descriptor("MATH", MULTI_CORPUS_TABLE, 2 * NAMESPACE_WIDTH, Imported("exact_match")),
            Descriptor("MUSR", MULTI_CORPUS_TABLE, 3 * NAMESPACE_WIDTH, Imported("acc_norm")),
            Descriptor("IFEVAL", MULTI_CORPUS_TABLE, 4 * NAMESPACE_WIDTH, Imported("prompt_level_strict_acc")),
            Descriptor("GPQA", MULTI_CORPUS_TABLE, 5 * NAMESPACE_WIDTH, Imported("acc_norm"))
        ).associateBy { it.source }

        private const val LEADERBOARD_COUNT = 5   // BBH..GPQA occupy 1M..5M; MMLU_PRO_LB shares 0

        /** Every known corpus: built-in types first (MMLU_PRO is the first entry), then the leaderboard. */
        val KNOWN: Map<String, Descriptor> = LinkedHashMap<String, Descriptor>().apply { putAll(BUILTIN); putAll(LEADERBOARD) }

        /** source -> id offset over the five built-in types, for [CorpusIds]. */
        val BUILTIN_OFFSETS: Map<String, Int> = BUILTIN.mapValues { it.value.idOffset }

        /**
         * source -> id offset over every known corpus. MMLU_PRO comes first so that
         * `CorpusIds.sourceOf` resolves a TIGER-Lab id to MMLU_PRO, not to its MMLU_PRO_LB alias.
         */
        val KNOWN_OFFSETS: Map<String, Int> = KNOWN.mapValues { it.value.idOffset }

        fun isLeaderboard(name: String): Boolean = name in LEADERBOARD

        /**
         * Lift `corpusDbPath = "…"` out of a headless TOML without the full parser, so the path
         * can be published as the `taxoadapt.eval.db-path` property BEFORE the Spring context
         * opens the SQLite beans (they connect at construction). Returns null when the key is
         * absent, which keeps the property default — the current path — untouched.
         */
        fun corpusDbPathFromToml(text: String): String? =
            Regex("""^\s*corpusDbPath\s*=\s*["']([^"']*)["']""", RegexOption.MULTILINE)
                .find(text)?.groupValues?.get(1)?.takeIf { it.isNotBlank() }
    }
}

/**
 * Namespaced question ids: `eval_results.question_id = idOffset(source) + upstreamId`, so the
 * integer primary key, `INSERT OR IGNORE`, the ratings' `eval_question_id` and every existing row
 * stay untouched (MMLU_PRO is offset 0, hence `namespaced("MMLU_PRO", id) == id`).
 */
object CorpusIds {
    fun namespaced(source: String, upstreamId: Int, offsets: Map<String, Int> = CorpusRegistry.KNOWN_OFFSETS): Int {
        val offset = offsets[source] ?: throw IllegalArgumentException("Unknown corpus '$source'")
        require(upstreamId in 0 until CorpusRegistry.NAMESPACE_WIDTH) {
            "upstream id $upstreamId of '$source' is outside its ${CorpusRegistry.NAMESPACE_WIDTH}-wide namespace"
        }
        return offset + upstreamId
    }

    /**
     * [namespaced], except that a negative id — the fetcher's `UNLINKED_QUERY_ID_BASE` sentinel
     * for rows with no eval row — passes through untouched: it belongs to no corpus and must
     * keep matching nothing. For MMLU_PRO (offset 0) this is the identity on every input.
     */
    fun namespacedOrSentinel(source: String, upstreamId: Int, offsets: Map<String, Int> = CorpusRegistry.KNOWN_OFFSETS): Int =
        if (upstreamId < 0) upstreamId else namespaced(source, upstreamId, offsets)

    fun upstreamId(questionId: Int, offsets: Map<String, Int> = CorpusRegistry.KNOWN_OFFSETS): Int =
        questionId - offsets.getValue(sourceOf(questionId, offsets))

    fun sourceOf(questionId: Int, offsets: Map<String, Int> = CorpusRegistry.KNOWN_OFFSETS): String {
        require(questionId >= 0) { "question id $questionId is negative (sentinel ids belong to no corpus)" }
        return offsets.entries.firstOrNull { (_, off) -> questionId in off until off + CorpusRegistry.NAMESPACE_WIDTH }?.key
            ?: throw IllegalArgumentException("question id $questionId falls in no registered corpus namespace")
    }
}

/**
 * Domain keys of multi-corpus runs (docs/multi_corpus_design.md §3.5): a leaderboard corpus's
 * domains enter the construction map as `<SOURCE>/<domain>` (`BBH/boolean_expressions`,
 * `MATH/Algebra`), so the keys of a union cannot collide and the stratified split is per
 * (source, domain) automatically. The legacy MMLU_PRO plugin keeps its bare, title-cased
 * category keys (`Philosophy`), which never carry a source prefix.
 */
object CorpusDomains {
    const val SEPARATOR = '/'

    fun key(source: String, domain: String): String = "$source$SEPARATOR$domain"

    /** The source a key is prefixed with, or `null` for a bare (single-corpus MMLU_PRO) key. */
    fun sourceOfKey(key: String): String? {
        val cut = key.indexOf(SEPARATOR)
        if (cut <= 0) return null
        val prefix = key.substring(0, cut)
        return prefix.takeIf { it in CorpusRegistry.KNOWN }
    }

    /** The corpus's own domain string, i.e. [key] without a recognised source prefix. */
    fun domainOfKey(key: String): String =
        if (sourceOfKey(key) == null) key else key.substring(key.indexOf(SEPARATOR) + 1)
}
