package taxonomy.dataset

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import java.sql.Connection
import java.sql.DriverManager

/**
 * One row in eval_results: a single model's answer to a single MMLU-Pro question.
 * question_id is the canonical TIGER-AI-Lab upstream ID (from the zip JSON).
 * question_text is denormalized for easy joins without cross-DB lookups.
 */
@Serializable
data class ModelEvalResult(
    val questionId: Int,            // upstream MMLU-Pro question_id
    val modelName: String,          // e.g. "GPT-4o", "claude-3-5-sonnet"
    val category: String,           // e.g. "math"
    val questionText: String,       // denormalized — matches mmlu_pro.question
    val options: List<String>,      // A-J choices
    val gtAnswer: String,           // ground-truth letter e.g. "A"
    val pred: String?,              // model's extracted answer letter (null = failed extraction)
    val modelOutput: String,        // full CoT reasoning trace
    val isCorrect: Boolean          // pred == gtAnswer
    // No per-row side flag: which questions are EVAL is a property of a POOL (reserved_pool by
    // pool id, ReservedPoolRegistry), never of a row. FRAMEWORK item 18.
)

@Serializable
data class EvalLoadStats(
    val modelName: String,
    val inserted: Int,
    val skipped: Int,               // already existed
    val linkedToDataset: Int,       // had a matching row in mmlu_pro
    val linkedToEmbedding: Int,     // had a cached embedding
    val errors: Int
)

@Service
class ModelEvalStore(
    // Injectable so integration tests can point at a throwaway DB file. Defaults to the
    // shared dataset cache so joins with mmlu_pro work without ATTACH in production.
    @Value("\${taxoadapt.eval.db-path:mmlu_pro_dataset_cache_v2.db}")
    val dbPath: String = "mmlu_pro_dataset_cache_v2.db",
    private val corpusRegistry: CorpusRegistry = CorpusRegistry()
) {
    private val log = LoggerFactory.getLogger("taxonomy.ModelEvalStore")
    private val json = Json { ignoreUnknownKeys = true; isLenient = true; coerceInputValues = true }

    private val dbUrl = "jdbc:sqlite:$dbPath?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000"

    private val isTest = System.getProperty("org.gradle.test.worker") != null ||
            System.getProperty("java.class.path")?.contains("junit") == true

    private val dbLock = Any()
    private val sharedConnection: Connection by lazy {
        DriverManager.getConnection(dbUrl).also { it.autoCommit = true }
    }

    private fun conn(): Connection {
        if (isTest) {
            return DriverManager.getConnection(dbUrl).also { it.autoCommit = true }
        }
        return java.lang.reflect.Proxy.newProxyInstance(
            Connection::class.java.classLoader,
            arrayOf(Connection::class.java)
        ) { _, method, args ->
            if (method.name == "close") {
                null
            } else {
                synchronized(dbLock) {
                    var attempts = 0
                    val maxRetries = 100
                    val delayMs = 100L
                    var completed = false
                    var result: Any? = null
                    while (!completed) {
                        try {
                            result = method.invoke(sharedConnection, *(args ?: emptyArray()))
                            completed = true
                        } catch (e: java.lang.reflect.InvocationTargetException) {
                            val cause = e.cause
                            if (cause is java.sql.SQLException) {
                                attempts++
                                val msg = cause.message ?: ""
                                val isBusy = cause.errorCode == 5 ||
                                             msg.contains("busy", ignoreCase = true) ||
                                             msg.contains("locked", ignoreCase = true)
                                if (isBusy && attempts < maxRetries) {
                                    log.warn("Database busy/locked (attempt $attempts/$maxRetries). Retrying in ${delayMs}ms...")
                                    Thread.sleep(delayMs)
                                } else {
                                    throw cause
                                }
                            } else {
                                throw cause ?: e
                            }
                        }
                    }
                    result
                }
            }
        } as Connection
    }

    init {
        initSchema()
        if (!isTest) {
            try {
                Runtime.getRuntime().addShutdownHook(Thread {
                    runCatching {
                        synchronized(dbLock) {
                            if (!sharedConnection.isClosed) {
                                sharedConnection.close()
                                log.info("SQLite evaluation store database connection closed cleanly via shutdown hook.")
                            }
                        }
                    }
                })
            } catch (_: Exception) {}
        }
    }

    // ─── Schema ──────────────────────────────────────────────────────────────

    private fun initSchema() {
        conn().use { c ->
            c.createStatement().use { s ->

                // Core eval results — one row per (question_id, model_name)
                s.execute("""
                    CREATE TABLE IF NOT EXISTS eval_results (
                        question_id   INTEGER  NOT NULL,
                        model_name    TEXT     NOT NULL,
                        category      TEXT     NOT NULL,
                        question_text TEXT     NOT NULL,
                        options_json  TEXT     NOT NULL,
                        gt_answer     TEXT     NOT NULL,
                        pred          TEXT,
                        model_output  TEXT     NOT NULL,
                        is_correct    INTEGER  NOT NULL DEFAULT 0,
                        PRIMARY KEY (question_id, model_name)
                    )
                """.trimIndent())
                // A fresh DB has no `is_reserved` column and no index on it (FRAMEWORK item 18). Older
                // databases keep the legacy column physically, at its DEFAULT 0 for new rows; nothing
                // reads or writes it. Which questions are EVAL is answered by `reserved_pool` by pool id.

                // Index for fast lookup by model
                s.execute("CREATE INDEX IF NOT EXISTS idx_eval_model ON eval_results(model_name)")
                // Index for category-level filtering
                s.execute("CREATE INDEX IF NOT EXISTS idx_eval_category ON eval_results(category, model_name)")

                // Lookup table: upstream question_id → local mmlu_pro.id
                // Populated on first load, used for joins.
                s.execute("""
                    CREATE TABLE IF NOT EXISTS eval_question_link (
                        question_id      INTEGER PRIMARY KEY,
                        mmlu_pro_row_id  INTEGER,   -- mmlu_pro.id (AUTOINCREMENT), null if not matched
                        question_text    TEXT NOT NULL,
                        has_embedding    INTEGER NOT NULL DEFAULT 0
                    )
                """.trimIndent())

                s.execute("CREATE INDEX IF NOT EXISTS idx_link_mmlu ON eval_question_link(mmlu_pro_row_id)")
            }
            // Durable, content-addressed reserved pools; every reserved read below semijoins them
            // by an explicit pool id. See ReservedPool for why there is no active pool.
            ReservedPool.ensureSchema(c)
            // Stage 0a (docs/multi_corpus_design.md §3.2): which corpora this DB holds, with the
            // id namespace each one occupies in eval_results.question_id. Additive only — the
            // single MMLU_PRO row at offset 0 describes every existing row without touching it.
            c.createStatement().use { s ->
                s.execute(
                    """
                    CREATE TABLE IF NOT EXISTS corpus_registry (
                        source     TEXT PRIMARY KEY,
                        table_name TEXT,
                        id_offset  INTEGER,
                        verifier   TEXT
                    )
                    """.trimIndent()
                )
            }
            val mmluPro = corpusRegistry.descriptor(CorpusRegistry.DEFAULT_SOURCE)
            c.prepareStatement(
                "INSERT OR IGNORE INTO corpus_registry (source, table_name, id_offset, verifier) VALUES (?, ?, ?, ?)"
            ).use { ps ->
                ps.setString(1, mmluPro.source)
                ps.setString(2, mmluPro.tableName)
                ps.setInt(3, mmluPro.idOffset)
                ps.setString(4, mmluPro.verifier.name)
                ps.executeUpdate()
            }
        }
        log.info("ModelEvalStore schema ready.")
    }

    /** The `corpus_registry` rows of this DB: source -> (table_name, id_offset, verifier). */
    fun corpusRegistryRows(): Map<String, CorpusRegistry.Descriptor> {
        val rows = linkedMapOf<String, CorpusRegistry.Descriptor>()
        conn().use { c ->
            c.createStatement().use { s ->
                s.executeQuery("SELECT source, table_name, id_offset, verifier FROM corpus_registry ORDER BY id_offset").use { rs ->
                    while (rs.next()) {
                        val verifier = try {
                            Verifier.parse(rs.getString(4) ?: "")
                        } catch (e: IllegalArgumentException) {
                            throw IllegalStateException("corpus_registry: ${e.message} for '${rs.getString(1)}'")
                        }
                        rows[rs.getString(1)] = CorpusRegistry.Descriptor(rs.getString(1), rs.getString(2), rs.getInt(3), verifier)
                    }
                }
            }
        }
        return rows
    }

    // ─── Write ────────────────────────────────────────────────────────────────

    /**
     * Bulk insert a batch of results for one model.
     * Uses INSERT OR IGNORE so re-running is idempotent.
     * Returns (inserted, skipped) counts.
     */
    fun saveBatch(results: List<ModelEvalResult>): Pair<Int, Int> {
        if (results.isEmpty()) return 0 to 0
        var inserted = 0
        var skipped = 0
        conn().use { c ->
            c.autoCommit = false
            try {
                c.prepareStatement("""
                    INSERT OR IGNORE INTO eval_results
                        (question_id, model_name, category, question_text, options_json,
                         gt_answer, pred, model_output, is_correct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """.trimIndent()).use { ps ->
                    for (r in results) {
                        ps.setInt(1, r.questionId)
                        ps.setString(2, r.modelName)
                        ps.setString(3, r.category)
                        ps.setString(4, r.questionText)
                        ps.setString(5, json.encodeToString(r.options))
                        ps.setString(6, r.gtAnswer)
                        ps.setString(7, r.pred)
                        ps.setString(8, r.modelOutput)
                        ps.setInt(9, if (r.isCorrect) 1 else 0)
                        ps.addBatch()
                    }
                    val counts = ps.executeBatch()
                    inserted = counts.count { it > 0 }
                    skipped = counts.size - inserted
                }
                c.commit()
            } catch (e: Exception) {
                c.rollback()
                throw e
            }
        }
        return inserted to skipped
    }

    /**
     * Upsert link records. Called after saveBatch to record the cross-DB join.
     */
    fun saveLinks(links: List<EvalQuestionLink>) {
        if (links.isEmpty()) return
        conn().use { c ->
            c.autoCommit = false
            try {
                c.prepareStatement("""
                    INSERT OR REPLACE INTO eval_question_link
                        (question_id, mmlu_pro_row_id, question_text, has_embedding)
                    VALUES (?, ?, ?, ?)
                """.trimIndent()).use { ps ->
                    for (l in links) {
                        ps.setInt(1, l.questionId)
                        ps.setObject(2, l.mmlProRowId)  // nullable Int
                        ps.setString(3, l.questionText)
                        ps.setInt(4, if (l.hasEmbedding) 1 else 0)
                        ps.addBatch()
                    }
                    ps.executeBatch()
                }
                c.commit()
            } catch (e: Exception) { c.rollback(); throw e }
        }
    }

    /**
     * Records [idsByDomain] as a pool and returns its content-addressed id. Recording is all a
     * writer can do: there is no activation and no per-row flag (FRAMEWORK item 18). Idempotent,
     * because the id is a hash of the contents.
     */
    fun recordReservedPool(
        idsByDomain: Map<String, List<Int>>,
        dataset: String? = null,
        corpusSize: Int? = null,
        seed: Long? = null,
        testRatio: Double? = null
    ): String {
        val now = System.currentTimeMillis()
        val poolId = conn().use { c -> ReservedPool.save(c, idsByDomain, dataset, corpusSize, seed, testRatio, now) }
        log.info(
            "Reserved pool '$poolId' recorded: ${idsByDomain.values.sumOf { it.size }} question(s) across" +
                " ${idsByDomain.size} domain(s); nothing activated."
        )
        return poolId
    }

    /** Whether [poolId] is recorded in this DB. */
    fun isReservedPoolRecorded(poolId: String): Boolean = conn().use { c -> ReservedPool.isRecorded(c, poolId) }

    /** Every recorded pool, newest first. */
    fun listReservedPools(): List<ReservedPool.Info> = conn().use { c -> ReservedPool.list(c) }

    /** Question ids in a recorded pool. */
    fun reservedPoolQuestionIds(poolId: String): Set<Int> =
        conn().use { c -> ReservedPool.questionIds(c, poolId) }

    // ─── Read ─────────────────────────────────────────────────────────────────

    /** `question_id IN (pool)` semijoin: the one predicate every reserved read uses. */
    private fun inPool(alias: String = "") =
        "${if (alias.isEmpty()) "" else "$alias."}question_id IN (SELECT question_id FROM ${ReservedPool.TABLE_POOL} WHERE pool_id = ?)"

    /**
     * Returns all eval results for a given model, restricted to [poolId] when given.
     */
    fun getResultsForModel(modelName: String, poolId: String? = null): List<ModelEvalResult> {
        val sql = if (poolId != null)
            "SELECT * FROM eval_results WHERE model_name = ? AND ${inPool()}"
        else
            "SELECT * FROM eval_results WHERE model_name = ?"
        return conn().use { c ->
            c.prepareStatement(sql).use { ps ->
                ps.setString(1, modelName)
                if (poolId != null) ps.setString(2, poolId)
                ps.executeQuery().toEvalResults()
            }
        }
    }

    /**
     * Returns a map of questionId → map of modelName → ModelEvalResult,
     * for a given set of models and optional category filter.
     * This is the primary query for BenchmarkService. [poolId] restricts the matrix to that
     * pool's questions; null is the unrestricted arena, which the caller keeps loud.
     */
    fun getResultsMatrix(
        models: List<String>,
        category: String? = null,
        poolId: String?,
        limit: Int = 0,
        minModelCount: Int = 2
    ): Map<Int, Map<String, ModelEvalResult>> {
        val effectiveMin = minModelCount.coerceIn(2, models.size.coerceAtLeast(2))
        val modelPlaceholders = models.joinToString(",") { "?" }
        val catLower = category?.lowercase()
        val matrix = mutableMapOf<Int, MutableMap<String, ModelEvalResult>>()

        if (limit > 0) {
            val subQuery = buildString {
                append("SELECT question_id FROM eval_results WHERE model_name IN ($modelPlaceholders)")
                if (catLower != null) append(" AND category = ?")
                if (poolId != null) append(" AND ${inPool()}")
                append(" GROUP BY question_id HAVING COUNT(DISTINCT model_name) >= $effectiveMin")
                // Ordered so a limited draw is a function of the DB contents, not of scan order.
                append(" ORDER BY question_id LIMIT $limit")
            }

            val questionIds = mutableListOf<Int>()
            conn().use { c ->
                c.prepareStatement(subQuery).use { ps ->
                    var idx = 1
                    models.forEach { ps.setString(idx++, it) }
                    if (catLower != null) ps.setString(idx++, catLower)
                    if (poolId != null) ps.setString(idx++, poolId)
                    val rs = ps.executeQuery()
                    while (rs.next()) {
                        questionIds.add(rs.getInt(1))
                    }
                }
            }

            if (questionIds.isNotEmpty()) {
                val qPlaceholders = questionIds.joinToString(",") { "?" }
                val query = "SELECT * FROM eval_results WHERE question_id IN ($qPlaceholders) AND model_name IN ($modelPlaceholders)"
                conn().use { c ->
                    c.prepareStatement(query).use { ps ->
                        var idx = 1
                        questionIds.forEach { ps.setInt(idx++, it) }
                        models.forEach { ps.setString(idx++, it) }
                        val rs = ps.executeQuery()
                        while (rs.next()) {
                            val r = rs.toSingleEvalResult()
                            matrix.getOrPut(r.questionId) { mutableMapOf() }[r.modelName] = r
                        }
                    }
                }
            }
        } else {
            val query = buildString {
                append("SELECT * FROM eval_results WHERE model_name IN ($modelPlaceholders)")
                if (catLower != null) append(" AND category = ?")
                if (poolId != null) append(" AND ${inPool()}")
            }
            conn().use { c ->
                c.prepareStatement(query).use { ps ->
                    var idx = 1
                    models.forEach { ps.setString(idx++, it) }
                    if (catLower != null) ps.setString(idx++, catLower)
                    if (poolId != null) ps.setString(idx++, poolId)
                    val rs = ps.executeQuery()
                    while (rs.next()) {
                        val r = rs.toSingleEvalResult()
                        matrix.getOrPut(r.questionId) { mutableMapOf() }[r.modelName] = r
                    }
                }
            }
        }

        // Only return rows where at least minModelCount models have an answer
        return matrix.filter { (_, byModel) ->
            byModel.size >= effectiveMin &&
            models.count { it in byModel } >= effectiveMin
        }
    }

    /**
     * Returns question_ids of [poolId] that have embeddings cached.
     * These are the "fully linked" questions ready for benchmark.
     */
    fun getLinkedReservedQuestionIds(models: List<String>, poolId: String, minModelCount: Int = 2): Set<Int> {
        val effectiveMin = minModelCount.coerceIn(2, models.size.coerceAtLeast(2))
        val modelPlaceholders = models.joinToString(",") { "?" }
        val sql = """
            SELECT DISTINCT l.question_id
            FROM eval_question_link l
            WHERE l.has_embedding = 1
              AND l.mmlu_pro_row_id IS NOT NULL
              AND l.question_id IN (
                  SELECT question_id FROM eval_results
                  WHERE ${inPool()} AND model_name IN ($modelPlaceholders)
                  GROUP BY question_id
                  HAVING COUNT(DISTINCT model_name) >= $effectiveMin
              )
        """.trimIndent()
        val ids = mutableSetOf<Int>()
        conn().use { c ->
            c.prepareStatement(sql).use { ps ->
                ps.setString(1, poolId)
                models.forEachIndexed { i, m -> ps.setString(i + 2, m) }
                val rs = ps.executeQuery()
                while (rs.next()) ids.add(rs.getInt(1))
            }
        }
        return ids
    }

    /**
     * Fetch a single model's precomputed result for one question, or null if absent.
     * Used by the precomputed Arena pairwise path (no live generation).
     */
    fun getResult(modelName: String, questionId: Int): ModelEvalResult? = conn().use { c ->
        c.prepareStatement(
            "SELECT * FROM eval_results WHERE model_name = ? AND question_id = ? LIMIT 1"
        ).use { ps ->
            ps.setString(1, modelName)
            ps.setInt(2, questionId)
            ps.executeQuery().toEvalResults().firstOrNull()
        }
    }

    /** Question ids shared by ALL given models (intersection), capped by limit (0 = all). */
    fun getSharedQuestionIds(models: List<String>, limit: Int = 0, minModelCount: Int = 2): List<Int> {
        if (models.isEmpty()) return emptyList()
        val effectiveMin = minModelCount.coerceIn(2, models.size.coerceAtLeast(2))
        val placeholders = models.joinToString(",") { "?" }
        val sql = buildString {
            append("SELECT question_id FROM eval_results WHERE model_name IN ($placeholders) ")
            append("GROUP BY question_id HAVING COUNT(DISTINCT model_name) >= $effectiveMin ")
            append("ORDER BY question_id")
            if (limit > 0) append(" LIMIT $limit")
        }
        return conn().use { c ->
            c.prepareStatement(sql).use { ps ->
                models.forEachIndexed { i, m -> ps.setString(i + 1, m) }
                val rs = ps.executeQuery()
                buildList { while (rs.next()) add(rs.getInt(1)) }
            }
        }
    }

    fun getLoadedModels(): List<String> = conn().use { c ->
        c.createStatement().use { s ->
            val rs = s.executeQuery("SELECT DISTINCT model_name FROM eval_results ORDER BY model_name")
            buildList { while (rs.next()) add(rs.getString(1)) }
        }
    }

    fun getStats(): Map<String, Any> {
        return conn().use { c ->
            c.createStatement().use { s ->
                val total = s.executeQuery("SELECT COUNT(*) FROM eval_results").also { it.next() }.getInt(1)
                val pools = s.executeQuery("SELECT COUNT(*) FROM ${ReservedPool.TABLE_META}").also { it.next() }.getInt(1)
                val linked = s.executeQuery("SELECT COUNT(*) FROM eval_question_link WHERE has_embedding = 1 AND mmlu_pro_row_id IS NOT NULL").also { it.next() }.getInt(1)
                mapOf("totalRows" to total, "recordedPools" to pools, "fullyLinked" to linked)
            }
        }
    }

    // ─── ResultSet helpers ────────────────────────────────────────────────────

    private fun java.sql.ResultSet.toEvalResults(): List<ModelEvalResult> =
        buildList { while (next()) add(toSingleEvalResult()) }

    private fun java.sql.ResultSet.toSingleEvalResult() = ModelEvalResult(
        questionId = getInt("question_id"),
        modelName = getString("model_name"),
        category = getString("category"),
        questionText = getString("question_text"),
        options = json.decodeFromString(getString("options_json")),
        gtAnswer = getString("gt_answer"),
        pred = getString("pred"),
        modelOutput = getString("model_output"),
        isCorrect = getInt("is_correct") == 1
    )

    fun getLoadedCategories(): List<String> = conn().use { c ->
        c.createStatement().use { s ->
            val rs = s.executeQuery(
                "SELECT DISTINCT category FROM eval_results ORDER BY category"
            )
            buildList { while (rs.next()) add(rs.getString(1)) }
        }
    }

    fun getModelAccuracies(
        models: List<String>,
        category: String? = null,
        poolId: String? = null
    ): Map<String, Double> = conn().use { c ->
        val catLower = category?.lowercase()
        models.associateWith { model ->
            val sql = buildString {
                append("SELECT COUNT(*), SUM(is_correct) FROM eval_results WHERE model_name = ?")
                if (catLower != null) append(" AND category = ?")
                if (poolId != null) append(" AND ${inPool()}")
            }
            c.prepareStatement(sql).use { ps ->
                var idx = 1
                ps.setString(idx++, model)
                if (catLower != null) ps.setString(idx++, catLower)
                if (poolId != null) ps.setString(idx++, poolId)
                val rs = ps.executeQuery()
                if (rs.next()) {
                    val total = rs.getInt(1)
                    val correct = rs.getInt(2)
                    if (total > 0) correct.toDouble() / total else 0.0
                } else {
                    0.0
                }
            }
        }
    }

    /** Per-model row counts; the reserved counts are over [poolId] (0 when null). */
    fun verifyIngestion(models: List<String>, poolId: String?): List<IngestionHealth> = conn().use { c ->
        models.map { model ->
            var total = 0
            var reserved = 0
            var math = 0
            var reservedMath = 0

            c.prepareStatement("SELECT COUNT(*) FROM eval_results WHERE model_name=?").use { ps ->
                ps.setString(1, model)
                val rs = ps.executeQuery()
                if (rs.next()) total = rs.getInt(1)
            }
            c.prepareStatement("SELECT COUNT(*) FROM eval_results WHERE model_name=? AND category='math'").use { ps ->
                ps.setString(1, model)
                val rs = ps.executeQuery()
                if (rs.next()) math = rs.getInt(1)
            }
            if (poolId != null) {
                c.prepareStatement("SELECT COUNT(*) FROM eval_results WHERE model_name=? AND ${inPool()}").use { ps ->
                    ps.setString(1, model)
                    ps.setString(2, poolId)
                    val rs = ps.executeQuery()
                    if (rs.next()) reserved = rs.getInt(1)
                }
                c.prepareStatement("SELECT COUNT(*) FROM eval_results WHERE model_name=? AND category='math' AND ${inPool()}").use { ps ->
                    ps.setString(1, model)
                    ps.setString(2, poolId)
                    val rs = ps.executeQuery()
                    if (rs.next()) reservedMath = rs.getInt(1)
                }
            }

            IngestionHealth(model, total, reserved, math, reservedMath)
        }
    }

    /**
     * The authoritative text of every question in [poolId], for withholding from rubric
     * induction. Resolves each reserved question to its ONE text via the link table (not every
     * question_text any model filed under that id: Meta-Llama-3-70B-Instruct is mis-keyed and
     * would over-count by 45%), and through corpus_questions for the leaderboard corpora.
     *
     * Fails closed: a pool that resolves to 0 texts throws, so induction can never proceed
     * withholding nothing. There is no flag fallback any more.
     */
    fun getReservedQuestionTexts(poolId: String): Set<String> {
        require(poolId.isNotBlank()) { "[JUDGE-LEAK] a pool id is mandatory" }
        val result = mutableSetOf<String>()
        conn().use { conn ->
            conn.prepareStatement(
                """
                SELECT DISTINCT m.question
                FROM ${ReservedPool.TABLE_POOL} p
                JOIN eval_question_link l ON l.question_id = p.question_id
                JOIN ${corpusRegistry.tableFor(CorpusRegistry.DEFAULT_SOURCE)} m ON m.id = l.mmlu_pro_row_id
                WHERE p.pool_id = ?
                """.trimIndent()
            ).use { ps ->
                ps.setString(1, poolId)
                ps.executeQuery().use { rs ->
                    while (rs.next()) rs.getString(1)?.let { result.add(it) }
                }
            }
            // Stage 1: the leaderboard corpora keep their texts in corpus_questions (namespaced
            // ids, so the pool joins directly). Union over that table too, when the DB has it,
            // so the induction leak filter protects every corpus of a multi-corpus pool.
            val hasCorpusQuestions = conn.prepareStatement(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?"
            ).use { ps -> ps.setString(1, CorpusRegistry.MULTI_CORPUS_TABLE); ps.executeQuery().use { it.next() } }
            if (hasCorpusQuestions) {
                conn.prepareStatement(
                    """
                    SELECT DISTINCT q.text
                    FROM ${ReservedPool.TABLE_POOL} p
                    JOIN ${CorpusRegistry.MULTI_CORPUS_TABLE} q ON q.question_id = p.question_id
                    WHERE p.pool_id = ?
                    """.trimIndent()
                ).use { ps ->
                    ps.setString(1, poolId)
                    ps.executeQuery().use { rs ->
                        while (rs.next()) rs.getString(1)?.let { result.add(it) }
                    }
                }
            }
        }
        check(result.isNotEmpty()) {
            "[JUDGE-LEAK] pool $poolId resolves to 0 texts in $dbPath (not recorded, or no link rows): refusing to" +
                " withhold nothing"
        }
        return result
    }
}

data class IngestionHealth(
    val modelName: String,
    val totalRows: Int,
    val reservedRows: Int,
    val mathRows: Int,
    val reservedMathRows: Int
)

data class EvalQuestionLink(
    val questionId: Int,
    val mmlProRowId: Int?,
    val questionText: String,
    val hasEmbedding: Boolean
)
