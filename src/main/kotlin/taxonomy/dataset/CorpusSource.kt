package taxonomy.dataset

import taxonomy.config.DatasetType

/**
 * One question of one corpus, with its identity qualified by [source] (docs/multi_corpus_design.md
 * §3.1). [upstreamId] is the corpus's own id (for MMLU-Pro the TIGER-AI-Lab `question_id`);
 * [domain] is the corpus's category string; [task] defaults to the domain and is the
 * task-family label a router acts on.
 */
data class CorpusQuery(
    val source: String,
    val upstreamId: Int,
    val text: String,
    val domain: String,
    val task: String = domain
)

/** Per-item details as consumed by rubric induction and data cards. */
typealias CorpusItem = HFProRowData

/**
 * A corpus is a plugin: one implementation per dataset, looked up by name in [CorpusRegistry].
 */
interface CorpusSource {
    /** Registry key, e.g. `MMLU_PRO`. */
    val name: String
    /** SQLite table in the dataset DB that holds this corpus's rows. */
    val tableName: String
    val verifier: Verifier

    /** domain -> queries. [domains] empty = every domain. */
    suspend fun fetch(maxQueries: Int, domains: List<String>): Map<String, List<CorpusQuery>>

    /** Item details by question text, for induction / cards. */
    fun detailsFor(texts: Collection<String>): Map<String, CorpusItem>
}

/**
 * Stage 0a adapter: one instance per [DatasetType], each wrapping the [MMLUDatasetFetcher]
 * method that already fetched that type. The fetcher's behaviour is untouched; this class only
 * gives the existing `when (datasetType)` dispatch a registry shape.
 */
class MmluProCorpusSource(
    private val fetcher: MMLUDatasetFetcher,
    val type: DatasetType,
    override val tableName: String,
    override val verifier: Verifier = McLetter
) : CorpusSource {
    override val name: String = type.name

    override suspend fun fetch(maxQueries: Int, domains: List<String>): Map<String, List<CorpusQuery>> {
        val byDomain = when (type) {
            DatasetType.MMLU_PRO -> fetcher.fetchMmluPro(maxQueries, domains)
            DatasetType.MMLU_ORIGINAL -> fetcher.fetchMmluOriginal(maxQueries, domains)
            DatasetType.ARC -> fetcher.fetchArc(maxQueries, domains)
            DatasetType.TWENTY_NEWSGROUPS -> fetcher.fetchTwentyNewsgroups(maxQueries, domains)
            DatasetType.AG_NEWS -> fetcher.fetchAgNews(maxQueries, domains)
            DatasetType.LIVECODEBENCH -> fetcher.fetchLiveCodeBench(maxQueries, domains)
            DatasetType.INTENT -> fetcher.fetchIntent(maxQueries, domains)
        }
        // Map order and per-query fields are carried through unchanged (the fetcher converts back
        // to MMLUQuery), so the construction input stays byte-identical.
        return byDomain.mapValues { (_, queries) ->
            queries.map { q -> CorpusQuery(source = name, upstreamId = q.id, text = q.text, domain = q.category) }
        }
    }

    override fun detailsFor(texts: Collection<String>): Map<String, CorpusItem> =
        fetcher.getDetailsForQueries(texts.toList())
}
