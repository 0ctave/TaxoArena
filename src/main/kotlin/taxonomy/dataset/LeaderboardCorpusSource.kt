package taxonomy.dataset

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.sqlite.SQLiteConfig
import java.sql.Connection
import java.sql.DriverManager

/**
 * Stage 1 plugin over the multi-corpus DB written by `tools/ingest/multicorpus_db.py`
 * (docs/multi_corpus_design.md §3.1, §3.4): one instance per leaderboard corpus, reading the
 * `corpus_questions` rows whose `source` is [descriptor].dbSource.
 *
 *  * [fetch] returns `"<NAME>/<domain>" -> queries` in `question_id` order, so a union of
 *    sources merges without key collisions and the split stratifies per (source, domain).
 *    `question_id` in the DB is already namespaced (`id_offset + upstream_id`); every row is
 *    checked against the descriptor's offset, and the DB's own `corpus_registry` row must
 *    agree with the static descriptor (offset and verifier) before anything is read.
 *  * [detailsFor] serves rubric induction and data cards: text, candidate list and target,
 *    from a per-source in-memory table loaded on first use (label-free runs never call it).
 *
 * The DB is opened read-only, per call; this class never writes.
 */
class LeaderboardCorpusSource(
    private val dbPath: String,
    private val descriptor: CorpusRegistry.Descriptor
) : CorpusSource {
    private val log = LoggerFactory.getLogger("taxonomy.LeaderboardCorpus")
    private val json = Json { ignoreUnknownKeys = true; isLenient = true; coerceInputValues = true }

    override val name: String = descriptor.source
    override val tableName: String = descriptor.tableName
    override val verifier: Verifier = descriptor.verifier

    /** `corpus_questions.source` for this corpus (`MMLU_PRO` for MMLU_PRO_LB). */
    val dbSource: String = descriptor.dbSource

    private fun open(): Connection {
        val cfg = SQLiteConfig()
        cfg.setReadOnly(true)
        cfg.setBusyTimeout(15_000)
        val c = DriverManager.getConnection("jdbc:sqlite:$dbPath", cfg.toProperties())
        runCatching { c.createStatement().use { it.execute("PRAGMA query_only = 1") } }
        return c
    }

    private fun hasTable(c: Connection, table: String): Boolean =
        c.prepareStatement("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?").use { ps ->
            ps.setString(1, table)
            ps.executeQuery().use { it.next() }
        }

    /**
     * The DB is the data of record for ids and metrics; the static descriptor is what the JVM
     * assumes about them. Any disagreement is a build-vs-code mismatch and fails here, before a
     * single query is read.
     */
    private fun verifyRegistry(c: Connection) {
        check(hasTable(c, tableName)) { "'$dbPath' has no '$tableName' table — not a multi-corpus DB (corpus '$name')" }
        check(hasTable(c, "corpus_registry")) { "'$dbPath' has no corpus_registry table (corpus '$name')" }
        c.prepareStatement("SELECT table_name, id_offset, verifier FROM corpus_registry WHERE source = ?").use { ps ->
            ps.setString(1, dbSource)
            ps.executeQuery().use { rs ->
                check(rs.next()) { "corpus_registry of '$dbPath' has no row for source '$dbSource' (corpus '$name')" }
                val table = rs.getString(1)
                val offset = rs.getInt(2)
                val verifierName = rs.getString(3)
                check(table == tableName) { "corpus '$name': DB table '$table' != descriptor '$tableName'" }
                check(offset == descriptor.idOffset) { "corpus '$name': DB id_offset $offset != descriptor ${descriptor.idOffset}" }
                check(verifierName == verifier.name) { "corpus '$name': DB verifier '$verifierName' != descriptor '${verifier.name}'" }
            }
        }
    }

    /** Rows of this corpus in the DB (0 when the table or the registry row is absent). */
    fun rowCount(): Int = runCatching {
        open().use { c ->
            if (!hasTable(c, tableName)) return 0
            c.prepareStatement("SELECT COUNT(*) FROM $tableName WHERE source = ?").use { ps ->
                ps.setString(1, dbSource)
                ps.executeQuery().use { if (it.next()) it.getInt(1) else 0 }
            }
        }
    }.getOrElse { 0 }

    override suspend fun fetch(maxQueries: Int, domains: List<String>): Map<String, List<CorpusQuery>> =
        withContext(Dispatchers.IO) {
            val wanted = domains.map { it.trim().lowercase() }.filter { it.isNotEmpty() }.toSet()
            val byDomain = LinkedHashMap<String, MutableList<CorpusQuery>>()
            var taken = 0
            var skippedBlank = 0
            open().use { c ->
                verifyRegistry(c)
                c.prepareStatement(
                    "SELECT question_id, upstream_id, domain, task, text FROM $tableName WHERE source = ? ORDER BY question_id ASC"
                ).use { ps ->
                    ps.setString(1, dbSource)
                    ps.executeQuery().use { rs ->
                        while (rs.next() && taken < maxQueries) {
                            val questionId = rs.getInt(1)
                            val upstreamId = rs.getInt(2)
                            val domain = rs.getString(3)
                            val task = rs.getString(4) ?: domain
                            val text = rs.getString(5) ?: ""
                            check(questionId == descriptor.idOffset + upstreamId) {
                                "corpus '$name': question_id $questionId != id_offset ${descriptor.idOffset} + upstream_id $upstreamId"
                            }
                            val key = CorpusDomains.key(name, domain)
                            if (wanted.isNotEmpty() && key.lowercase() !in wanted && domain.lowercase() !in wanted) continue
                            if (text.isBlank()) { skippedBlank++; continue }
                            byDomain.getOrPut(key) { mutableListOf() }
                                .add(CorpusQuery(source = name, upstreamId = upstreamId, text = text, domain = key, task = task))
                            taken++
                        }
                    }
                }
            }
            check(taken > 0) {
                "corpus '$name' (source '$dbSource') has no rows in '$dbPath'" +
                    (if (wanted.isEmpty()) "" else " for domains $domains") +
                    " — the leaderboard corpora are built by tools/ingest/multicorpus_db.py, never downloaded here"
            }
            log.info("Loaded $taken $name queries across ${byDomain.size} domain(s) from $dbPath" +
                (if (skippedBlank > 0) " ($skippedBlank blank-text rows skipped)" else ""))
            byDomain
        }

    /** text -> item over the whole corpus; loaded once, on first [detailsFor]. */
    private val details: Map<String, CorpusItem> by lazy {
        val out = HashMap<String, CorpusItem>()
        open().use { c ->
            verifyRegistry(c)
            c.prepareStatement(
                "SELECT question_id, domain, text, options_json, target FROM $tableName WHERE source = ? ORDER BY question_id ASC"
            ).use { ps ->
                ps.setString(1, dbSource)
                ps.executeQuery().use { rs ->
                    while (rs.next()) {
                        val text = rs.getString(3) ?: continue
                        val options = rs.getString(4)?.let { raw ->
                            runCatching { json.decodeFromString<List<String>>(raw) }.getOrElse { emptyList() }
                        } ?: emptyList()
                        // First row wins for a duplicated text, as the MMLU-Pro lookup's `WHERE question = ?` does.
                        out.putIfAbsent(
                            text,
                            HFProRowData(
                                id = rs.getInt(1),
                                question = text,
                                category = CorpusDomains.key(name, rs.getString(2)),
                                cot_content = "",
                                options = options,
                                answer = rs.getString(5)
                            )
                        )
                    }
                }
            }
        }
        log.info("Details table for $name loaded: ${out.size} distinct text(s)")
        out
    }

    override fun detailsFor(texts: Collection<String>): Map<String, CorpusItem> {
        if (texts.isEmpty()) return emptyMap()
        val out = LinkedHashMap<String, CorpusItem>()
        for (t in texts) details[t]?.let { out[t] = it }
        return out
    }
}
