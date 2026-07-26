package taxonomy.dataset

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assertions.fail
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import taxonomy.dataset.EvalIngestValidator.EvalIngestReport
import taxonomy.dataset.EvalIngestValidator.IngestStatus
import taxonomy.dataset.EvalIngestValidator.ModelIngestVerdict
import java.io.File
import java.nio.file.Path
import java.sql.Connection
import java.sql.DriverManager

/**
 * Exercises the pre-flight validator against throwaway SQLite fixtures built here in the test.
 * The production cache (`mmlu_pro_dataset_cache_v2.db`) is never opened.
 *
 * Each fixture mirrors the real corpus in miniature: a handful of clean witness models
 * establishing the majority question text, plus whichever defective model the case is about.
 */
class EvalIngestValidatorTest {

    // ─── Fixture builder ─────────────────────────────────────────────────────────────────

    private data class Row(
        val questionId: Int,
        val model: String,
        val text: String,
        val gt: String = "A",
        val pred: String? = "A",
        val isCorrect: Boolean = pred == gt,
        val reserved: Boolean = false,
        val output: String = "reasoning for q$questionId"
    )

    /** Canonical question text for the shared id space. */
    private fun q(id: Int) = "Question $id: what is the value of x when x = $id?"

    /**
     * Builds a fixture DB with the production `eval_results` schema — including the primary key
     * that causes the silent row loss — and inserts [rows].
     */
    private fun buildDb(dir: Path, name: String, rows: List<Row>): String {
        val path = File(dir.toFile(), name).absolutePath
        DriverManager.getConnection("jdbc:sqlite:$path").use { c: Connection ->
            c.createStatement().use { s ->
                s.execute(
                    """
                    CREATE TABLE eval_results (
                        question_id   INTEGER NOT NULL,
                        model_name    TEXT    NOT NULL,
                        category      TEXT    NOT NULL,
                        question_text TEXT    NOT NULL,
                        options_json  TEXT    NOT NULL,
                        gt_answer     TEXT    NOT NULL,
                        pred          TEXT,
                        model_output  TEXT    NOT NULL,
                        is_correct    INTEGER NOT NULL DEFAULT 0,
                        is_reserved   INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY (question_id, model_name)
                    )
                    """.trimIndent()
                )
            }
            c.prepareStatement(
                """
                INSERT OR IGNORE INTO eval_results
                    (question_id, model_name, category, question_text, options_json,
                     gt_answer, pred, model_output, is_correct, is_reserved)
                VALUES (?, ?, 'math', ?, '["a","b","c","d"]', ?, ?, ?, ?, ?)
                """.trimIndent()
            ).use { ps ->
                rows.forEach { r ->
                    ps.setInt(1, r.questionId)
                    ps.setString(2, r.model)
                    ps.setString(3, r.text)
                    ps.setString(4, r.gt)
                    ps.setString(5, r.pred)
                    ps.setString(6, r.output)
                    ps.setInt(7, if (r.isCorrect) 1 else 0)
                    ps.setInt(8, if (r.reserved) 1 else 0)
                    ps.addBatch()
                }
                ps.executeBatch()
            }
        }
        return path
    }

    /** Clean witness models over ids 1..[n]; ids 1..2 form the reserved pool. */
    private fun cleanWitnesses(n: Int, models: List<String>): List<Row> =
        models.flatMap { m -> (1..n).map { id -> Row(id, m, q(id), reserved = id <= 2) } }

    private fun EvalIngestReport.verdict(model: String): ModelIngestVerdict =
        verdictFor(model) ?: fail("no verdict produced for '$model'")

    private fun ModelIngestVerdict.status(checkName: String): IngestStatus =
        check(checkName)?.status ?: fail("check '$checkName' missing from $modelName")

    private fun ModelIngestVerdict.value(checkName: String): Double =
        check(checkName)?.value ?: fail("check '$checkName' missing from $modelName")

    // ─── Tests ───────────────────────────────────────────────────────────────────────────

    @Test
    fun `a clean model passes every check`(@TempDir dir: Path) {
        val models = listOf("alpha", "beta", "gamma", "delta")
        val db = buildDb(dir, "clean.db", cleanWitnesses(40, models))

        val report = EvalIngestValidator(db).validate(models)

        assertEquals(40, report.consensusQuestions, "all 40 ids are quorum-backed")
        assertEquals(2, report.reservedPoolSize)
        assertEquals(4, report.modelsInCorpus)
        report.verdicts.forEach { v ->
            assertEquals(
                IngestStatus.PASS, v.status,
                "${v.modelName} should pass cleanly, got: ${v.reasons}"
            )
        }
        assertTrue(report.failed.isEmpty())
        assertEquals(models.sorted(), report.admittedModels.sorted())
    }

    @Test
    fun `a mis-keyed model fails the identity check and is refused admission`(@TempDir dir: Path) {
        // 'rogue' answered the same 40 questions, but its source zip numbered them differently:
        // its row for id N carries the text of id N+13 (wrapping). Row count, pred rate,
        // is_correct consistency and reserved coverage are all perfect — only the question
        // identity betrays it. This is the Meta-Llama-3-70B-Instruct signature.
        val witnesses = listOf("alpha", "beta", "gamma")
        val rows = cleanWitnesses(40, witnesses) + (1..40).map { id ->
            Row(id, "rogue", q((id + 12) % 40 + 1), reserved = id <= 2)
        }
        val db = buildDb(dir, "miskeyed.db", rows)

        val report = EvalIngestValidator(db).validate(witnesses + "rogue")
        val rogue = report.verdict("rogue")

        assertEquals(IngestStatus.FAIL, rogue.status)
        assertEquals(IngestStatus.FAIL, rogue.status("QUESTION_IDENTITY"))
        assertEquals(0.0, rogue.value("QUESTION_IDENTITY"), 1e-9)

        // The defect hides from every volume-based check — that is the whole point.
        assertEquals(IngestStatus.PASS, rogue.status("ROW_COVERAGE"))
        assertEquals(IngestStatus.PASS, rogue.status("RESERVED_COVERAGE"))
        assertEquals(IngestStatus.PASS, rogue.status("PRED_PRESENT"))
        assertEquals(IngestStatus.PASS, rogue.status("CORRECTNESS_CONSISTENCY"))

        assertFalse("rogue" in report.admittedModels, "a FAIL model must not be admitted")
        assertEquals(witnesses.sorted(), report.admittedModels.sorted())
        witnesses.forEach { assertEquals(IngestStatus.PASS, report.verdict(it).status) }
        assertTrue(
            rogue.reasons.any { it.contains("QUESTION_IDENTITY") },
            "the reason list must name the decisive check: ${rogue.reasons}"
        )
    }

    @Test
    fun `a truncated model fails row coverage`(@TempDir dir: Path) {
        // 'short' has correctly keyed rows but only 60% of them — the silent-loss signature of
        // INSERT OR IGNORE on PRIMARY KEY (question_id, model_name).
        val witnesses = listOf("alpha", "beta", "gamma")
        val rows = cleanWitnesses(40, witnesses) +
            (1..24).map { id -> Row(id, "short", q(id), reserved = id <= 2) }
        val db = buildDb(dir, "truncated.db", rows)

        val report = EvalIngestValidator(db).validate(witnesses + "short")
        val short = report.verdict("short")

        assertEquals(IngestStatus.FAIL, short.status)
        assertEquals(IngestStatus.FAIL, short.status("ROW_COVERAGE"))
        assertEquals(0.6, short.value("ROW_COVERAGE"), 1e-9)
        // Its rows are genuine, so identity is clean; only the volume is wrong.
        assertEquals(IngestStatus.PASS, short.status("QUESTION_IDENTITY"))
        assertFalse("short" in report.admittedModels)
    }

    @Test
    fun `mild row loss warns instead of failing`(@TempDir dir: Path) {
        // 95% coverage: material enough to report, not enough to reject.
        val witnesses = listOf("alpha", "beta", "gamma")
        val rows = cleanWitnesses(40, witnesses) +
            (1..38).map { id -> Row(id, "nearly", q(id), reserved = id <= 2) }
        val db = buildDb(dir, "mild.db", rows)

        val nearly = EvalIngestValidator(db).validate(witnesses + "nearly").verdict("nearly")
        assertEquals(IngestStatus.WARN, nearly.status)
        assertEquals(IngestStatus.WARN, nearly.status("ROW_COVERAGE"))
    }

    @Test
    fun `whitespace and case differences are not counted as divergences`(@TempDir dir: Path) {
        // The gemini-3.1-pro_5-shots signature: identical questions, different whitespace.
        // Compared raw these would look like 40 divergences and reject a perfectly good model.
        val witnesses = listOf("alpha", "beta", "gamma")
        val rows = cleanWitnesses(40, witnesses) + (1..40).map { id ->
            Row(id, "reformatted", q(id).replace(" ", "").uppercase(), reserved = id <= 2)
        }
        val db = buildDb(dir, "whitespace.db", rows)

        val v = EvalIngestValidator(db).validate(witnesses + "reformatted").verdict("reformatted")
        assertEquals(IngestStatus.PASS, v.status("QUESTION_IDENTITY"))
        assertEquals(1.0, v.value("QUESTION_IDENTITY"), 1e-9)
        assertEquals(IngestStatus.PASS, v.status)
    }

    @Test
    fun `foreign question ids are reported as orphans not as agreements`(@TempDir dir: Path) {
        // 'alien' uses ids nobody else has. A naive majority vote would make it its own
        // majority and hand it a perfect identity score; the quorum rule prevents that.
        val witnesses = listOf("alpha", "beta", "gamma")
        val rows = cleanWitnesses(40, witnesses) +
            (901..940).map { id -> Row(id, "alien", "alien question $id") }
        val db = buildDb(dir, "orphans.db", rows)

        val v = EvalIngestValidator(db).validate(witnesses + "alien").verdict("alien")
        assertEquals(IngestStatus.FAIL, v.status("ID_SPACE_ORPHANS"))
        assertEquals(1.0, v.value("ID_SPACE_ORPHANS"), 1e-9)
        // No quorum-backed row at all, so identity cannot be established either.
        assertEquals(IngestStatus.FAIL, v.status("QUESTION_IDENTITY"))
        assertEquals(IngestStatus.FAIL, v.status)
    }

    @Test
    fun `zero reserved rows fail while the pool is non-empty`(@TempDir dir: Path) {
        val witnesses = listOf("alpha", "beta", "gamma")
        val rows = cleanWitnesses(40, witnesses) +
            (1..40).map { id -> Row(id, "unreserved", q(id), reserved = false) }
        val db = buildDb(dir, "reserved.db", rows)

        val v = EvalIngestValidator(db).validate(witnesses + "unreserved").verdict("unreserved")
        assertEquals(IngestStatus.FAIL, v.status("RESERVED_COVERAGE"))
        assertEquals(IngestStatus.FAIL, v.status)
    }

    @Test
    fun `an empty reserved pool is skipped rather than failed`(@TempDir dir: Path) {
        val models = listOf("alpha", "beta", "gamma")
        val rows = models.flatMap { m -> (1..40).map { id -> Row(id, m, q(id)) } }
        val db = buildDb(dir, "nopool.db", rows)

        val report = EvalIngestValidator(db).validate(models)
        assertEquals(0, report.reservedPoolSize)
        report.verdicts.forEach { v ->
            assertEquals(IngestStatus.SKIP, v.status("RESERVED_COVERAGE"))
            assertEquals(IngestStatus.PASS, v.status)
        }
        assertTrue(
            report.corpusNotes.any { it.contains("is_reserved") },
            "an empty reserved pool must be surfaced as a corpus note: ${report.corpusNotes}"
        )
    }

    @Test
    fun `answer sanity fails a model whose answers were mostly not extracted`(@TempDir dir: Path) {
        val witnesses = listOf("alpha", "beta", "gamma")
        // 30 of 40 rows have no extracted answer → 25% present, below the 50% floor.
        val rows = cleanWitnesses(40, witnesses) + (1..40).map { id ->
            if (id <= 30) Row(id, "sloppy", q(id), pred = null, isCorrect = false, reserved = id <= 2)
            else Row(id, "sloppy", q(id))
        }
        val db = buildDb(dir, "sanity.db", rows)

        val v = EvalIngestValidator(db).validate(witnesses + "sloppy").verdict("sloppy")
        assertEquals(IngestStatus.FAIL, v.status("PRED_PRESENT"))
        assertEquals(0.25, v.value("PRED_PRESENT"), 1e-9)
        assertEquals(IngestStatus.FAIL, v.status)
    }

    @Test
    fun `a single is_correct inconsistency warns without rejecting the model`(@TempDir dir: Path) {
        val witnesses = listOf("alpha", "beta", "gamma")
        // One row out of 200 claims correctness while pred != gt_answer.
        val rows = cleanWitnesses(200, witnesses) + (1..200).map { id ->
            if (id == 31) Row(id, "odd", q(id), gt = "A", pred = "B", isCorrect = true)
            else Row(id, "odd", q(id), reserved = id <= 2)
        }
        val db = buildDb(dir, "consistency.db", rows)

        val v = EvalIngestValidator(db).validate(witnesses + "odd").verdict("odd")
        assertEquals(IngestStatus.WARN, v.status("CORRECTNESS_CONSISTENCY"))
        assertEquals(0.995, v.value("CORRECTNESS_CONSISTENCY"), 1e-9)
        assertEquals(IngestStatus.WARN, v.status)
        assertTrue("odd" in EvalIngestValidator(db).validate(witnesses + "odd").admittedModels)
    }

    @Test
    fun `a wrong answer key is caught by ground-truth agreement`(@TempDir dir: Path) {
        // Correct questions, but the model carries a different answer key throughout — the
        // second, independent symptom of a mis-keyed source zip.
        val witnesses = listOf("alpha", "beta", "gamma")
        val rows = cleanWitnesses(40, witnesses) +
            (1..40).map { id -> Row(id, "wrongkey", q(id), gt = "C", pred = "C", reserved = id <= 2) }
        val db = buildDb(dir, "gt.db", rows)

        val v = EvalIngestValidator(db).validate(witnesses + "wrongkey").verdict("wrongkey")
        assertEquals(IngestStatus.PASS, v.status("QUESTION_IDENTITY"))
        assertEquals(IngestStatus.FAIL, v.status("GT_ANSWER_AGREEMENT"))
        assertEquals(IngestStatus.FAIL, v.status)
    }

    @Test
    fun `a blank chain-of-thought is advisory and never blocks admission`(@TempDir dir: Path) {
        // 32 of the 47 real cached models store no CoT; getRobustTrace synthesises one from
        // pred, so this must be reported without rejecting the model.
        val witnesses = listOf("alpha", "beta", "gamma")
        val rows = cleanWitnesses(40, witnesses) +
            (1..40).map { id -> Row(id, "notrace", q(id), reserved = id <= 2, output = "") }
        val db = buildDb(dir, "notrace.db", rows)

        val report = EvalIngestValidator(db).validate(witnesses + "notrace")
        val v = report.verdict("notrace")

        assertEquals(IngestStatus.WARN, v.status("TRACE_PRESENCE"))
        assertTrue(v.check("TRACE_PRESENCE")!!.advisory)
        assertEquals(IngestStatus.PASS, v.status, "advisory checks must not change the rollup")
        assertTrue("notrace" in report.admittedModels)
    }

    @Test
    fun `a model that was never ingested fails instead of throwing`(@TempDir dir: Path) {
        val models = listOf("alpha", "beta", "gamma")
        val db = buildDb(dir, "missing.db", cleanWitnesses(40, models))

        val v = EvalIngestValidator(db).validate(models + "ghost").verdict("ghost")
        assertEquals(IngestStatus.FAIL, v.status)
        assertEquals(0, v.totalRows)
        assertEquals(IngestStatus.FAIL, v.status("ROWS_PRESENT"))
    }

    @Test
    fun `a missing eval_results table fails every model`(@TempDir dir: Path) {
        val path = File(dir.toFile(), "empty.db").absolutePath
        DriverManager.getConnection("jdbc:sqlite:$path").use { c ->
            c.createStatement().use { it.execute("CREATE TABLE unrelated (x INTEGER)") }
        }
        val report = EvalIngestValidator(path).validate(listOf("alpha", "beta"))
        assertEquals(2, report.failed.size)
        assertTrue(report.admittedModels.isEmpty())
    }

    @Test
    fun `the validator does not write to the database`(@TempDir dir: Path) {
        val models = listOf("alpha", "beta", "gamma")
        val db = buildDb(dir, "readonly.db", cleanWitnesses(40, models))
        val file = File(db)
        val before = file.readBytes()

        EvalIngestValidator(db).validate(models)

        assertTrue(before.contentEquals(file.readBytes()), "validate() must not mutate the DB file")
    }

    @Test
    fun `the SQL and Kotlin question normalisers agree`(@TempDir dir: Path) {
        // NORMALISED_QUESTION_SQL drives the grouping; normaliseQuestion is its documented
        // twin. If the two drift the check silently changes meaning, so pin them together.
        val samples = listOf(
            "For r(t) = [ln(t^3 + 1)]",
            "Forr(t)\t=\n[ln(t^3 + 1)]",
            "MIXED CaseTexthere",
            "non breaking spaces"
        )
        val db = buildDb(dir, "norm.db", samples.mapIndexed { i, s -> Row(i + 1, "alpha", s) })

        DriverManager.getConnection("jdbc:sqlite:$db").use { c ->
            c.prepareStatement(
                "SELECT question_text, ${EvalIngestValidator.NORMALISED_QUESTION_SQL} FROM eval_results"
            ).use { ps ->
                ps.executeQuery().use { rs ->
                    var seen = 0
                    while (rs.next()) {
                        seen++
                        assertEquals(
                            EvalIngestValidator.normaliseQuestion(rs.getString(1)),
                            rs.getString(2),
                            "normalisers disagree on '${rs.getString(1)}'"
                        )
                    }
                    assertEquals(samples.size, seen)
                }
            }
        }
    }
}
