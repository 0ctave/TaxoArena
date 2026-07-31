package taxonomy.dataset

import java.security.MessageDigest
import java.sql.Connection

/**
 * Durable, content-addressed storage for held-out ("reserved") query pools.
 *
 * ## Why this exists
 *
 * Neither of the two other places the pool appears is durable on its own: the boolean
 * `eval_results.is_reserved` column holds exactly one pool (`markReserved` opens with
 * `UPDATE eval_results SET is_reserved = 0`, so writing a pool destroys the previous one —
 * a smoke run or a unit test can silently replace the baseline pool), and the mutable
 * `reserved_test_queries.json` at the repo root is rewritten by every run. Neither records
 * provenance, so "which pool was this result produced against?" needs a durable answer
 * somewhere else. This table is that answer.
 *
 * ## Design
 *
 * [TABLE_POOL] is the source of truth and holds *every* pool, so pools coexist and a smoke run
 * cannot destroy a baseline. `eval_results.is_reserved` is kept as a denormalised mirror of
 * whichever pool is currently ACTIVE ([TABLE_ACTIVE]), which is what every existing
 * `reservedOnly` read still uses — so this is additive rather than a rewrite of the read paths.
 *
 * A pool's id is a hash of its own contents (see [computePoolId]), not of the parameters that
 * produced it. Content addressing means the same split always resolves to the same id no matter
 * which code path recorded it, so the fetcher writing a pool at split time and the loader
 * activating it from the JSON converge without having to agree on anything but the ids
 * themselves. It also makes re-activating a previous pool exact rather than a restore-from-file.
 */
object ReservedPool {

    /** Stratum recorded when a caller supplies a flat id set with no domain information. */
    const val UNKNOWN_DOMAIN = "<unstratified>"

    const val TABLE_POOL = "reserved_pool"
    const val TABLE_META = "reserved_pool_meta"
    const val TABLE_ACTIVE = "active_reserved_pool"

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
            // Reverse lookup: "which pools contain this question?", and the join direction used
            // when mirroring a pool onto eval_results.
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

            // Single-row table; the CHECK makes "there is at most one active pool" a schema
            // guarantee rather than a convention callers have to remember.
            s.execute(
                """
                CREATE TABLE IF NOT EXISTS $TABLE_ACTIVE (
                    only_row  INTEGER PRIMARY KEY CHECK (only_row = 1),
                    pool_id   TEXT NOT NULL,
                    active_at INTEGER NOT NULL
                )
                """.trimIndent()
            )
        }
    }

    /**
     * Content address of a pool: `p<16 hex>` over the sorted `domain:id` pairs.
     *
     * Sorting is what makes this stable — the split shuffles, and two runs that select the same
     * questions must agree on the id regardless of emission order. The domain is included
     * because the split is domain-stratified, so the same id set under a different stratification
     * is genuinely a different pool.
     */
    fun computePoolId(idsByDomain: Map<String, List<Int>>): String {
        val canonical = idsByDomain.entries
            .flatMap { (domain, ids) -> ids.map { "$domain:$it" } }
            .sorted()
            .joinToString("\n")
        val digest = MessageDigest.getInstance("SHA-256").digest(canonical.toByteArray())
        return "p" + digest.take(8).joinToString("") { "%02x".format(it) }
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
        val createdAt: Long,
        val isActive: Boolean
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

    /**
     * Makes [poolId] the active pool and rebuilds the `eval_results.is_reserved` mirror from it.
     *
     * The clear step is `WHERE is_reserved = 1`, not an unconditional update: that uses
     * `idx_eval_reserved` and touches only the rows actually set (160k of 560k on the current
     * corpus) instead of rewriting the entire table to express a set change.
     *
     * Returns the number of `eval_results` rows now flagged.
     */
    fun activate(c: Connection, poolId: String, nowMillis: Long): Int {
        ensureSchema(c)
        val known = c.prepareStatement("SELECT COUNT(*) FROM $TABLE_POOL WHERE pool_id = ?").use { ps ->
            ps.setString(1, poolId)
            ps.executeQuery().let { it.next(); it.getInt(1) }
        }
        require(known > 0) { "Unknown reserved pool '$poolId' — save() it before activating." }

        val prevAutoCommit = c.autoCommit
        c.autoCommit = false
        try {
            c.createStatement().use { s ->
                s.executeUpdate("UPDATE eval_results SET is_reserved = 0 WHERE is_reserved = 1")
            }
            val flagged = c.prepareStatement(
                """
                UPDATE eval_results SET is_reserved = 1
                WHERE question_id IN (SELECT question_id FROM $TABLE_POOL WHERE pool_id = ?)
                """.trimIndent()
            ).use { ps ->
                ps.setString(1, poolId)
                ps.executeUpdate()
            }
            c.prepareStatement(
                "INSERT OR REPLACE INTO $TABLE_ACTIVE (only_row, pool_id, active_at) VALUES (1, ?, ?)"
            ).use { ps ->
                ps.setString(1, poolId)
                ps.setLong(2, nowMillis)
                ps.executeUpdate()
            }
            c.commit()
            return flagged
        } catch (e: Exception) {
            c.rollback()
            throw e
        } finally {
            c.autoCommit = prevAutoCommit
        }
    }

    /** The active pool id, or null if none has been activated. */
    fun activeId(c: Connection): String? {
        ensureSchema(c)
        c.createStatement().use { s ->
            s.executeQuery("SELECT pool_id FROM $TABLE_ACTIVE WHERE only_row = 1").use { rs ->
                return if (rs.next()) rs.getString(1) else null
            }
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
        val active = activeId(c)
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
                            createdAt = rs.getLong("created_at"),
                            isActive = id == active
                        )
                    )
                }
            }
        }
        return out
    }
}
