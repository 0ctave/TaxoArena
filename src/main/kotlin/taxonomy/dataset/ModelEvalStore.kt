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
    val isCorrect: Boolean,         // pred == gtAnswer
    val isReserved: Boolean         // true = belongs to the reserved test pool
)

@Serializable
data class EvalLoadStats(
    val modelName: String,
    val inserted: Int,
    val skipped: Int,               // already existed
    val linkedToDataset: Int,       // had a matching row in mmlu_pro
    val linkedToEmbedding: Int,     // had a cached embedding
    val reservedCount: Int,
    val errors: Int
)

@Service
class ModelEvalStore(
    // Injectable so integration tests can point at a throwaway DB file. Defaults to the
    // shared dataset cache so joins with mmlu_pro work without ATTACH in production.
    @Value("\${taxoadapt.eval.db-path:mmlu_pro_dataset_cache_v2.db}")
    private val dbPath: String = "mmlu_pro_dataset_cache_v2.db"
) {
    private val log = LoggerFactory.getLogger("ModelEvalStore")
    private val json = Json { ignoreUnknownKeys = true; isLenient = true; coerceInputValues = true }

    private val dbUrl = "jdbc:sqlite:$dbPath?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000"

    private fun conn(): Connection = DriverManager.getConnection(dbUrl).also { it.autoCommit = true }

    init { initSchema() }

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
                        is_reserved   INTEGER  NOT NULL DEFAULT 0,
                        PRIMARY KEY (question_id, model_name)
                    )
                """.trimIndent())

                // Index for fast lookup by model
                s.execute("CREATE INDEX IF NOT EXISTS idx_eval_model ON eval_results(model_name)")
                // Index for reserved pool queries
                s.execute("CREATE INDEX IF NOT EXISTS idx_eval_reserved ON eval_results(is_reserved, model_name)")
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
        }
        log.info("ModelEvalStore schema ready.")
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
                         gt_answer, pred, model_output, is_correct, is_reserved)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        ps.setInt(10, if (r.isReserved) 1 else 0)
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
     * Mark all rows for a given set of question_ids as reserved.
     * Called after the reserved pool is determined.
     */
    fun markReserved(questionIds: Set<Int>) {
        if (questionIds.isEmpty()) return
        conn().use { c ->
            c.autoCommit = false
            try {
                questionIds.chunked(900).forEach { chunk ->
                    val placeholders = chunk.joinToString(",") { "?" }
                    c.prepareStatement(
                        "UPDATE eval_results SET is_reserved = 1 WHERE question_id IN ($placeholders)"
                    ).use { ps ->
                        chunk.forEachIndexed { i, id -> ps.setInt(i + 1, id) }
                        ps.executeUpdate()
                    }
                }
                c.commit()
            } catch (e: Exception) { c.rollback(); throw e }
        }
        log.info("Marked ${questionIds.size} questions as reserved in eval_results.")
    }

    // ─── Read ─────────────────────────────────────────────────────────────────

    /**
     * Returns all eval results for a given model, optionally filtered to the reserved pool.
     */
    fun getResultsForModel(modelName: String, reservedOnly: Boolean = false): List<ModelEvalResult> {
        val sql = if (reservedOnly)
            "SELECT * FROM eval_results WHERE model_name = ? AND is_reserved = 1"
        else
            "SELECT * FROM eval_results WHERE model_name = ?"
        return conn().use { c ->
            c.prepareStatement(sql).use { ps ->
                ps.setString(1, modelName)
                ps.executeQuery().toEvalResults()
            }
        }
    }

    /**
     * Returns a map of questionId → map of modelName → ModelEvalResult,
     * for a given set of models and optional category filter.
     * This is the primary query for BenchmarkService.
     */
    fun getResultsMatrix(
        models: List<String>,
        category: String? = null,
        reservedOnly: Boolean = true,
        limit: Int = 0
    ): Map<Int, Map<String, ModelEvalResult>> {
        val modelPlaceholders = models.joinToString(",") { "?" }
        val sb = StringBuilder("SELECT * FROM eval_results WHERE model_name IN ($modelPlaceholders)")
        if (category != null) sb.append(" AND category = ?")
        if (reservedOnly) sb.append(" AND is_reserved = 1")
        if (limit > 0) sb.append(" LIMIT $limit")

        val matrix = mutableMapOf<Int, MutableMap<String, ModelEvalResult>>()
        conn().use { c ->
            c.prepareStatement(sb.toString()).use { ps ->
                var idx = 1
                models.forEach { ps.setString(idx++, it) }
                if (category != null) ps.setString(idx++, category)
                val rs = ps.executeQuery()
                while (rs.next()) {
                    val r = rs.toSingleEvalResult()
                    matrix.getOrPut(r.questionId) { mutableMapOf() }[r.modelName] = r
                }
            }
        }
        // Only return rows where ALL requested models have an answer
        return matrix.filter { (_, byModel) -> models.all { it in byModel } }
    }

    /**
     * Returns question_ids from the reserved pool that have embeddings cached.
     * These are the "fully linked" questions ready for benchmark.
     */
    fun getLinkedReservedQuestionIds(models: List<String>): Set<Int> {
        val modelPlaceholders = models.joinToString(",") { "?" }
        val sql = """
            SELECT DISTINCT l.question_id
            FROM eval_question_link l
            WHERE l.has_embedding = 1
              AND l.mmlu_pro_row_id IS NOT NULL
              AND l.question_id IN (
                  SELECT question_id FROM eval_results
                  WHERE is_reserved = 1 AND model_name IN ($modelPlaceholders)
                  GROUP BY question_id
                  HAVING COUNT(DISTINCT model_name) = ${models.size}
              )
        """.trimIndent()
        val ids = mutableSetOf<Int>()
        conn().use { c ->
            c.prepareStatement(sql).use { ps ->
                models.forEachIndexed { i, m -> ps.setString(i + 1, m) }
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
    fun getSharedQuestionIds(models: List<String>, limit: Int = 0): List<Int> {
        if (models.isEmpty()) return emptyList()
        val placeholders = models.joinToString(",") { "?" }
        val sql = buildString {
            append("SELECT question_id FROM eval_results WHERE model_name IN ($placeholders) ")
            append("GROUP BY question_id HAVING COUNT(DISTINCT model_name) = ${models.size} ")
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
                val reserved = s.executeQuery("SELECT COUNT(*) FROM eval_results WHERE is_reserved = 1").also { it.next() }.getInt(1)
                val linked = s.executeQuery("SELECT COUNT(*) FROM eval_question_link WHERE has_embedding = 1 AND mmlu_pro_row_id IS NOT NULL").also { it.next() }.getInt(1)
                mapOf("totalRows" to total, "reservedRows" to reserved, "fullyLinked" to linked)
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
        isCorrect = getInt("is_correct") == 1,
        isReserved = getInt("is_reserved") == 1
    )

    fun getLoadedCategories(): List<String> = conn().use { c ->
        c.createStatement().use { s ->
            val rs = s.executeQuery(
                "SELECT DISTINCT category FROM eval_results ORDER BY category"
            )
            buildList { while (rs.next()) add(rs.getString(1)) }
        }
    }
}

data class EvalQuestionLink(
    val questionId: Int,
    val mmlProRowId: Int?,
    val questionText: String,
    val hasEmbedding: Boolean
)