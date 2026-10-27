package taxonomy.dataset

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import taxonomy.dataset.EvalIngestValidator.IngestStatus
import java.io.File
import java.nio.file.Path
import java.sql.DriverManager

/**
 * Stage 1: on a multi-corpus DB the letter-rule checks (PRED_PRESENT, CORRECTNESS_CONSISTENCY)
 * and the gt majority vote apply to the MC_LETTER namespaces only; rows of an `IMPORTED:*`
 * corpus (empty pred, is_correct from the leaderboard metric, run-dependent target) must not
 * exclude a model. Without a `corpus_registry` the validator behaves exactly as before.
 */
class EvalIngestValidatorVerifierAwareTest {

    private data class Row(val qid: Int, val model: String, val text: String, val gt: String, val pred: String?, val correct: Int, val output: String = "trace")

    private fun buildDb(dir: Path, name: String, rows: List<Row>, registry: List<Triple<String, Int, String>>?): String {
        val path = File(dir.toFile(), name).absolutePath
        DriverManager.getConnection("jdbc:sqlite:$path").use { c ->
            c.createStatement().use { s ->
                s.execute(
                    """
                    CREATE TABLE eval_results (question_id INTEGER NOT NULL, model_name TEXT NOT NULL, category TEXT NOT NULL,
                        question_text TEXT NOT NULL, options_json TEXT, gt_answer TEXT, pred TEXT, model_output TEXT NOT NULL,
                        is_correct INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY (question_id, model_name))
                    """.trimIndent()
                )
                if (registry != null) {
                    s.execute("CREATE TABLE corpus_registry (source TEXT PRIMARY KEY, table_name TEXT, id_offset INTEGER, verifier TEXT)")
                    registry.forEach { (src, off, ver) -> s.execute("INSERT INTO corpus_registry VALUES ('$src', 'corpus_questions', $off, '$ver')") }
                }
            }
            c.prepareStatement("INSERT INTO eval_results VALUES (?, ?, 'c', ?, NULL, ?, ?, ?, ?)").use { ps ->
                rows.forEach { r ->
                    ps.setInt(1, r.qid); ps.setString(2, r.model); ps.setString(3, r.text); ps.setString(4, r.gt)
                    ps.setString(5, r.pred); ps.setString(6, r.output); ps.setInt(7, r.correct); ps.addBatch()
                }
                ps.executeBatch()
            }
        }
        return path
    }

    private val models = listOf("m1", "m2", "m3")

    /** 4 MMLU-Pro ids (letters, consistent) + 3 MATH ids (no pred, imported metric) + 2 GPQA ids (run-dependent gt). */
    private fun rows(): List<Row> = buildList {
        for (m in models) {
            for (q in 70..73) add(Row(q, m, "mmlu q$q", "B", if (q % 2 == 0) "B" else "A", if (q % 2 == 0) 1 else 0))
            for (q in 0..2) add(Row(2_000_000 + q, m, "math q$q", "4.5", "", if (m == "m1") 1 else 0, output = "long trace"))
            for (q in 0..1) add(Row(5_000_000 + q, m, "gpqa q$q", "(${'A' + models.indexOf(m)})", "A", 1, output = ""))
        }
    }

    private val registry = listOf(
        Triple("MMLU_PRO", 0, "MC_LETTER"),
        Triple("MATH", 2_000_000, "IMPORTED:exact_match"),
        Triple("GPQA", 5_000_000, "IMPORTED:acc_norm")
    )

    @Test
    fun `imported-metric rows do not fail the roster on a multi-corpus DB`(@TempDir dir: Path) {
        val report = EvalIngestValidator(buildDb(dir, "mc.db", rows(), registry)).validate(models, null)
        assertEquals(models, report.admittedModels, report.renderLines().joinToString("\n"))
        for (v in report.verdicts) {
            assertEquals(IngestStatus.PASS, v.status, v.reasons.joinToString(" | "))
            assertEquals(IngestStatus.PASS, v.check("PRED_PRESENT")!!.status)
            assertEquals(1.0, v.check("PRED_PRESENT")!!.value)
            assertTrue(v.check("PRED_PRESENT")!!.detail.contains("of 4 MC_LETTER rows"), v.check("PRED_PRESENT")!!.detail)
            assertEquals(IngestStatus.PASS, v.check("CORRECTNESS_CONSISTENCY")!!.status)
            assertEquals(IngestStatus.PASS, v.check("GT_ANSWER_AGREEMENT")!!.status)
            assertEquals(IngestStatus.PASS, v.check("QUESTION_IDENTITY")!!.status)
            assertEquals(IngestStatus.PASS, v.check("ROW_COVERAGE")!!.status)
        }
        assertEquals(9, report.consensusQuestions, "identity and coverage still count every corpus")
        assertTrue(report.corpusNotes.any { it.startsWith("verifier-aware: 12 MC_LETTER row(s) and 15 imported-metric row(s)") }, report.corpusNotes.toString())
    }

    @Test
    fun `a model with imported rows only gets SKIP on the letter checks, never FAIL`(@TempDir dir: Path) {
        val onlyImported = rows().filter { it.qid >= 2_000_000 }
        val report = EvalIngestValidator(buildDb(dir, "imp.db", onlyImported, registry)).validate(models, null)
        for (v in report.verdicts) {
            assertEquals(IngestStatus.SKIP, v.check("PRED_PRESENT")!!.status, v.reasons.joinToString(" | "))
            assertEquals(IngestStatus.SKIP, v.check("CORRECTNESS_CONSISTENCY")!!.status)
            assertEquals(IngestStatus.SKIP, v.check("GT_ANSWER_AGREEMENT")!!.status)
            assertEquals(IngestStatus.PASS, v.status, v.reasons.joinToString(" | "))
        }
    }

    @Test
    fun `without a corpus_registry the letter rule still applies to every row`(@TempDir dir: Path) {
        val report = EvalIngestValidator(buildDb(dir, "v2.db", rows(), registry = null)).validate(models, null)
        for (v in report.verdicts) {
            // 3 of 9 rows have an empty pred; 3 MATH rows of m1 and the GPQA rows violate the letter rule.
            assertEquals(IngestStatus.WARN, v.check("PRED_PRESENT")!!.status)
            assertTrue(v.check("PRED_PRESENT")!!.detail.contains("of 9 rows"))
            assertEquals(IngestStatus.FAIL, v.check("CORRECTNESS_CONSISTENCY")!!.status)
        }
        assertTrue(report.corpusNotes.none { it.startsWith("verifier-aware") })
    }
}
