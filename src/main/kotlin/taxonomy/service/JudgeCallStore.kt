package taxonomy.service

import kotlinx.serialization.Serializable
import java.sql.Connection

/**
 * One judge CALL (one presentation order) under the recipe path, with the provenance FRAMEWORK.md
 * Stage 4 / item 19 require per verdict. Two of these ride on every recipe `DomainEvaluation`
 * (`judgeCalls`); the Mistral path leaves the list empty and, with kotlinx `encodeDefaults` off in
 * the runner's Json, absent from every export.
 */
@Serializable
data class JudgeCallRecord(
    val presentationOrder: Int,          // 1 = (A, B) as given, 2 = (B, A)
    val judgeModel: String,
    val recipe: String,
    val kitHash: String,
    val deploymentFingerprint: String,
    val promptSha256: String,            // sha256(system + NUL + user), UTF-8
    val payloadSha256: String,           // sha256 of the exact bytes posted
    val maxTokens: Int,
    val temperatureLabel: String,        // "omitted" or the Python repr of the literal posted
    val finishReason: String?,
    val completionTokens: Int?,
    val promptTokens: Int?,
    val providerResponseId: String?,
    val providerModel: String?,
    val httpStatus: Int,
    val attempts: Int,
    val latencyMs: Long,
    val rawContent: String,
    val parsedWinner: String,            // the order's OWN vote, uninverted ("Model A"/"Model B"/"TIE"/"INVALID")
    val confidence: Double,
    val anchor: String = "",
    val refLetter: String = "",
    val evalQuestionId: Int? = null,
    val modelA: String = "",
    val modelB: String = "",
    val nodeId: String = ""
)

/**
 * `judge_calls`: the per-call provenance table. Created LAZILY on the first insert and never by the
 * ratings DB's init DDL, so an existing ratings DB keeps its schema until a recipe run actually
 * writes to it. Shared by `TaxonomyRankingService.recordJudgeCalls` (production) and the
 * JudgeWiringHarness's own DB under experiment_results/judge_wiring/.
 */
object JudgeCallStore {
    const val TABLE = "judge_calls"

    private val COLUMNS = listOf(
        "snapshot_id", "eval_question_id", "model_a", "model_b", "node_id", "presentation_order",
        "judge_model", "recipe", "kit_hash", "deployment_fingerprint", "prompt_sha256", "payload_sha256",
        "max_tokens", "temperature_label", "finish_reason", "completion_tokens", "prompt_tokens",
        "provider_response_id", "provider_model", "http_status", "attempts", "latency_ms",
        "raw_content", "parsed_winner", "confidence", "anchor", "ref_letter", "ts"
    )

    fun ensureTable(conn: Connection) {
        conn.createStatement().use { st ->
            st.execute(
                """
                CREATE TABLE IF NOT EXISTS $TABLE (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id TEXT NOT NULL,
                    eval_question_id INTEGER,
                    model_a TEXT NOT NULL,
                    model_b TEXT NOT NULL,
                    node_id TEXT,
                    presentation_order INTEGER NOT NULL,
                    judge_model TEXT NOT NULL,
                    recipe TEXT NOT NULL,
                    kit_hash TEXT NOT NULL,
                    deployment_fingerprint TEXT NOT NULL,
                    prompt_sha256 TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    max_tokens INTEGER NOT NULL,
                    temperature_label TEXT NOT NULL,
                    finish_reason TEXT,
                    completion_tokens INTEGER,
                    prompt_tokens INTEGER,
                    provider_response_id TEXT,
                    provider_model TEXT,
                    http_status INTEGER NOT NULL,
                    attempts INTEGER NOT NULL,
                    latency_ms INTEGER NOT NULL,
                    raw_content TEXT NOT NULL,
                    parsed_winner TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    anchor TEXT,
                    ref_letter TEXT,
                    ts REAL NOT NULL
                )
                """.trimIndent()
            )
            st.execute("CREATE INDEX IF NOT EXISTS idx_${TABLE}_match ON $TABLE (snapshot_id, eval_question_id, model_a, model_b)")
        }
    }

    fun hasTable(conn: Connection): Boolean = conn.prepareStatement(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?"
    ).use { ps -> ps.setString(1, TABLE); ps.executeQuery().use { rs -> rs.next() && rs.getInt(1) > 0 } }

    fun insert(conn: Connection, snapshotId: String, rows: List<JudgeCallRecord>) {
        if (rows.isEmpty()) return
        ensureTable(conn)
        val sql = "INSERT INTO $TABLE (${COLUMNS.joinToString(", ")}) VALUES (${COLUMNS.joinToString(", ") { "?" }})"
        val now = System.currentTimeMillis() / 1000.0
        conn.prepareStatement(sql).use { ps ->
            for (r in rows) {
                var i = 1
                ps.setString(i++, snapshotId)
                if (r.evalQuestionId == null) ps.setNull(i++, java.sql.Types.INTEGER) else ps.setInt(i++, r.evalQuestionId)
                ps.setString(i++, r.modelA)
                ps.setString(i++, r.modelB)
                ps.setString(i++, r.nodeId)
                ps.setInt(i++, r.presentationOrder)
                ps.setString(i++, r.judgeModel)
                ps.setString(i++, r.recipe)
                ps.setString(i++, r.kitHash)
                ps.setString(i++, r.deploymentFingerprint)
                ps.setString(i++, r.promptSha256)
                ps.setString(i++, r.payloadSha256)
                ps.setInt(i++, r.maxTokens)
                ps.setString(i++, r.temperatureLabel)
                ps.setString(i++, r.finishReason)
                if (r.completionTokens == null) ps.setNull(i++, java.sql.Types.INTEGER) else ps.setInt(i++, r.completionTokens)
                if (r.promptTokens == null) ps.setNull(i++, java.sql.Types.INTEGER) else ps.setInt(i++, r.promptTokens)
                ps.setString(i++, r.providerResponseId)
                ps.setString(i++, r.providerModel)
                ps.setInt(i++, r.httpStatus)
                ps.setInt(i++, r.attempts)
                ps.setLong(i++, r.latencyMs)
                ps.setString(i++, r.rawContent)
                ps.setString(i++, r.parsedWinner)
                ps.setDouble(i++, r.confidence)
                ps.setString(i++, r.anchor)
                ps.setString(i++, r.refLetter)
                ps.setDouble(i, now)
                ps.addBatch()
            }
            ps.executeBatch()
        }
    }

    fun readAll(conn: Connection, snapshotId: String): List<JudgeCallRecord> {
        if (!hasTable(conn)) return emptyList()
        val out = mutableListOf<JudgeCallRecord>()
        conn.prepareStatement("SELECT * FROM $TABLE WHERE snapshot_id = ? ORDER BY id").use { ps ->
            ps.setString(1, snapshotId)
            ps.executeQuery().use { rs ->
                while (rs.next()) {
                    out += JudgeCallRecord(
                        presentationOrder = rs.getInt("presentation_order"),
                        judgeModel = rs.getString("judge_model"),
                        recipe = rs.getString("recipe"),
                        kitHash = rs.getString("kit_hash"),
                        deploymentFingerprint = rs.getString("deployment_fingerprint"),
                        promptSha256 = rs.getString("prompt_sha256"),
                        payloadSha256 = rs.getString("payload_sha256"),
                        maxTokens = rs.getInt("max_tokens"),
                        temperatureLabel = rs.getString("temperature_label"),
                        finishReason = rs.getString("finish_reason"),
                        completionTokens = rs.getInt("completion_tokens").let { if (rs.wasNull()) null else it },
                        promptTokens = rs.getInt("prompt_tokens").let { if (rs.wasNull()) null else it },
                        providerResponseId = rs.getString("provider_response_id"),
                        providerModel = rs.getString("provider_model"),
                        httpStatus = rs.getInt("http_status"),
                        attempts = rs.getInt("attempts"),
                        latencyMs = rs.getLong("latency_ms"),
                        rawContent = rs.getString("raw_content"),
                        parsedWinner = rs.getString("parsed_winner"),
                        confidence = rs.getDouble("confidence"),
                        anchor = rs.getString("anchor") ?: "",
                        refLetter = rs.getString("ref_letter") ?: "",
                        evalQuestionId = rs.getInt("eval_question_id").let { if (rs.wasNull()) null else it },
                        modelA = rs.getString("model_a"),
                        modelB = rs.getString("model_b"),
                        nodeId = rs.getString("node_id") ?: ""
                    )
                }
            }
        }
        return out
    }
}
