package taxonomy.dataset

import java.security.MessageDigest
import java.sql.Connection

/**
 * Durable, content-addressed storage for held-out ("reserved") query pools.
 *
 * ## Why this exists
 *
 * The mutable `reserved_test_queries.json` at the repo root is rewritten by every run and
 * records no provenance, so "which pool was this result produced against?" needs a durable
 * answer somewhere else. This table is that answer: [TABLE_POOL] holds *every* pool, so pools
 * coexist and a smoke run cannot destroy a baseline.
 *
 * ## No active pool
 *
 * Until FRAMEWORK item 18 (SPLIT-FUNCTION-IMPL) there was also an `active_reserved_pool`
 * pointer and a denormalised legacy `eval_results.is_reserved` mirror of it, rebuilt by every
 * construction run. That made "the pool" a global mutable: a sweep build in another JVM switched
 * it under a judged run (incident 2026-09-09, 71% of arena questions on the tree's train side).
 * Both are gone from the code: every reader takes the pool id and semijoins this table
 * ([questionIds]; `ModelEvalStore` reads by pool id). The legacy column and pointer table may
 * still exist physically in older databases; nothing reads or writes them any more.
 *
 * A pool's id is a hash of its own contents (see [computePoolId]), not of the parameters that
 * produced it. Content addressing means the same split always resolves to the same id no matter
 * which code path recorded it, and the pinned pools of record reproduce from their id files
 * ([ReservedPoolRegistry]).
 */
object ReservedPool {

    /** Stratum recorded when a caller supplies a flat id set with no domain information. */
    const val UNKNOWN_DOMAIN = "<unstratified>"

    const val TABLE_POOL = "reserved_pool"
    const val TABLE_META = "reserved_pool_meta"

    /**
     * Creates the tables if absent. Safe to call from any component holding a connection to the
     * dataset cache; both [ModelEvalStore] and [MMLUDatasetFetcher] do, and whichever runs first
     * wins.
     */
    fun ensureSchema(c: Connection) {
        c.createStatement().use { s ->
            // WITHOUT ROWID: the primary key IS the whole row, so this avoids a redundant
            // rowid and its index on a table that is only ever queried by that key.
            s.execute(
                """
                CREATE TABLE IF NOT EXISTS $TABLE_POOL (
                    pool_id     TEXT    NOT NULL,
                    question_id INTEGER NOT NULL,
                    domain      TEXT    NOT NULL,
                    PRIMARY KEY (pool_id, question_id)
                ) WITHOUT ROWID
                """.trimIndent()
            )
            // Reverse lookup: "which pools contain this question?".
            s.execute("CREATE INDEX IF NOT EXISTS idx_reserved_pool_q ON $TABLE_POOL(question_id)")

            s.execute(
                """
                CREATE TABLE IF NOT EXISTS $TABLE_META (
                    pool_id        TEXT PRIMARY KEY,
                    dataset        TEXT,
                    corpus_size    INTEGER,
                    seed           INTEGER,
                    test_ratio     REAL,
                    domains        TEXT,
                    question_count INTEGER NOT NULL,
                    domain_count   INTEGER NOT NULL,
                    created_at     INTEGER NOT NULL
                )
                """.trimIndent()
            )
        }
    }

    /**
     * Content address of a pool: `p<16 hex>` over the sorted [canonicalLine]s.
     *
     * Sorting is what makes this stable — the split shuffles, and two runs that select the same
     * questions must agree on the id regardless of emission order. The domain is included
     * because the split is domain-stratified, so the same id set under a different stratification
     * is genuinely a different pool.
     */
    fun computePoolId(idsByDomain: Map<String, List<Int>>): String {
        val canonical = idsByDomain.entries
            .flatMap { (domain, ids) -> ids.map { canonicalLine(domain, it) } }
            .sorted()
            .joinToString("\n")
        val digest = MessageDigest.getInstance("SHA-256").digest(canonical.toByteArray())
        return "p" + digest.take(8).joinToString("") { "%02x".format(it) }
    }

    /**
     * One hashed line (docs/multi_corpus_design.md §3.5): `domain:id` for MMLU_PRO rows — the
     * bare category keys of every existing pool, so p2dca21ab5f4ef3ae and every other recorded
     * id are reproduced — and `source|domain:id` for a leaderboard corpus, whose split key is
     * `<SOURCE>/<domain>` ([CorpusDomains]). The `|` form is also what
     * `tools/analysis/pool_guard.py` would have to mirror for a non-MMLU_PRO pool.
     */
    fun canonicalLine(domainKey: String, id: Int): String {
        val source = CorpusDomains.sourceOfKey(domainKey)
        return if (source == null || source == CorpusRegistry.DEFAULT_SOURCE) "$domainKey:$id"
        else "$source|${CorpusDomains.domainOfKey(domainKey)}:$id"
    }

    /** Summary of a stored pool, for listing and diagnostics. */
    data class Info(
        val poolId: String,
        val questionCount: Int,
        val domainCount: Int,
        val dataset: String?,
        val corpusSize: Int?,
        val seed: Long?,
        val testRatio: Double?,
        val createdAt: Long
    )

    /**
     * Records a pool and its provenance. Idempotent: re-recording the same split is a no-op
     * beyond refreshing the metadata, because the id is derived from the contents.
     *
     * Returns the pool id.
     */
    fun save(
        c: Connection,
        idsByDomain: Map<String, List<Int>>,
        dataset: String? = null,
        corpusSize: Int? = null,
        seed: Long? = null,
        testRatio: Double? = null,
        nowMillis: Long
    ): String {
        ensureSchema(c)
        val poolId = computePoolId(idsByDomain)
        val prevAutoCommit = c.autoCommit
        c.autoCommit = false
        try {
            c.prepareStatement(
                "INSERT OR IGNORE INTO $TABLE_POOL (pool_id, question_id, domain) VALUES (?, ?, ?)"
            ).use { ps ->
                for ((domain, ids) in idsByDomain) {
                    for (id in ids) {
                        ps.setString(1, poolId)
                        ps.setInt(2, id)
                        ps.setString(3, domain)
                        ps.addBatch()
                    }
                }
                ps.executeBatch()
            }
            c.prepareStatement(
                """
                INSERT OR REPLACE INTO $TABLE_META
                    (pool_id, dataset, corpus_size, seed, test_ratio, domains,
                     question_count, domain_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """.trimIndent()
            ).use { ps ->
                ps.setString(1, poolId)
                ps.setString(2, dataset)
                if (corpusSize != null) ps.setInt(3, corpusSize) else ps.setNull(3, java.sql.Types.INTEGER)
                if (seed != null) ps.setLong(4, seed) else ps.setNull(4, java.sql.Types.INTEGER)
                if (testRatio != null) ps.setDouble(5, testRatio) else ps.setNull(5, java.sql.Types.REAL)
                ps.setString(6, idsByDomain.keys.sorted().joinToString(","))
                ps.setInt(7, idsByDomain.values.sumOf { it.size })
                ps.setInt(8, idsByDomain.size)
                ps.setLong(9, nowMillis)
                ps.executeUpdate()
            }
            c.commit()
        } catch (e: Exception) {
            c.rollback()
            throw e
        } finally {
            c.autoCommit = prevAutoCommit
        }
        return poolId
    }

    /** Whether [poolId] has rows in [TABLE_POOL]. */
    fun isRecorded(c: Connection, poolId: String): Boolean {
        ensureSchema(c)
        c.prepareStatement("SELECT 1 FROM $TABLE_POOL WHERE pool_id = ? LIMIT 1").use { ps ->
            ps.setString(1, poolId)
            ps.executeQuery().use { rs -> return rs.next() }
        }
    }

    /** Question ids belonging to [poolId]. */
    fun questionIds(c: Connection, poolId: String): Set<Int> {
        ensureSchema(c)
        val out = LinkedHashSet<Int>()
        c.prepareStatement("SELECT question_id FROM $TABLE_POOL WHERE pool_id = ?").use { ps ->
            ps.setString(1, poolId)
            ps.executeQuery().use { rs -> while (rs.next()) out.add(rs.getInt(1)) }
        }
        return out
    }

    /** All stored pools, newest first. */
    fun list(c: Connection): List<Info> {
        ensureSchema(c)
        val out = mutableListOf<Info>()
        c.createStatement().use { s ->
            s.executeQuery(
                """
                SELECT pool_id, question_count, domain_count, dataset, corpus_size,
                       seed, test_ratio, created_at
                FROM $TABLE_META ORDER BY created_at DESC
                """.trimIndent()
            ).use { rs ->
                while (rs.next()) {
                    val seed = rs.getLong("seed").let { if (rs.wasNull()) null else it }
                    val ratio = rs.getDouble("test_ratio").let { if (rs.wasNull()) null else it }
                    val corpus = rs.getInt("corpus_size").let { if (rs.wasNull()) null else it }
                    val id = rs.getString("pool_id")
                    out.add(
                        Info(
                            poolId = id,
                            questionCount = rs.getInt("question_count"),
                            domainCount = rs.getInt("domain_count"),
                            dataset = rs.getString("dataset"),
                            corpusSize = corpus,
                            seed = seed,
                            testRatio = ratio,
                            createdAt = rs.getLong("created_at")
                        )
                    )
                }
            }
        }
        return out
    }
}
