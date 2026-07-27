package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.dataset.unwrapTraceEnvelope
import java.io.File
import java.sql.DriverManager

/**
 * Guards the two defects found on 2026-07-27 (see docs/arena-math-findings.md).
 *
 * 1. `arx_3` / `arx_0314` store the trace as a JSON envelope carrying `reason_code`, a
 *    self-reported confidence field that predicts correctness. Handing it to the judge is
 *    an asymmetric side-channel: 2 of the roster's models have one, the rest do not.
 * 2. 28 of the 47 upstream archives put the trace in `generated_text`, which the loader
 *    did not read, so `model_output` was stored empty for 34 of 47 models.
 *
 * These assert the STATE OF THE INGESTED DB, not just the pure function, because the
 * failure mode both times was a mismatch between what the code handled and what the data
 * actually contained. A unit test over a hand-written envelope would have passed
 * throughout the period the bug was live.
 */
class TraceEnvelopeUnwrapTest {

    private val dbPath = "mmlu_pro_dataset_cache_v2.db"

    /** Returns rows as lists of stringified columns, or null when the corpus DB is absent. */
    private fun query(sql: String): List<List<String>>? {
        if (!File(dbPath).exists()) return null
        val out = mutableListOf<List<String>>()
        DriverManager.getConnection("jdbc:sqlite:$dbPath?open_mode=1").use { c ->
            c.createStatement().use { st ->
                st.executeQuery(sql).use { rs ->
                    val n = rs.metaData.columnCount
                    while (rs.next()) out += (1..n).map { rs.getString(it) ?: "" }
                }
            }
        }
        return out
    }

    /** The channel itself: no stored trace may contain the leaking field. */
    @Test
    fun `no ingested trace carries a reason_code field`() {
        val leaking = query(
            """
            SELECT model_name, COUNT(*) FROM eval_results
            WHERE model_output LIKE '%"reason_code"%'
            GROUP BY model_name
            """.trimIndent()
        ) ?: return  // DB absent in a clean checkout; nothing to assert

        assertTrue(
            leaking.isEmpty(),
            "reason_code reached the judge-visible trace for: " +
                leaking.joinToString { "${it[0]} (${it[1]} rows)" } +
                ". unwrapTraceEnvelope must strip the envelope down to `response`."
        )
    }

    /** Envelopes must be unwrapped, not merely stripped of one known key. */
    @Test
    fun `no ingested trace is a raw JSON envelope`() {
        val enveloped = query(
            """
            SELECT model_name, COUNT(*) FROM eval_results
            WHERE TRIM(model_output) LIKE '{%' AND model_output LIKE '%"response"%'
            GROUP BY model_name
            """.trimIndent()
        ) ?: return

        assertTrue(
            enveloped.isEmpty(),
            "raw JSON envelopes remain in model_output for: " +
                enveloped.joinToString { "${it[0]} (${it[1]} rows)" }
        )
    }

    /**
     * These six archives genuinely carry no trace field of any kind — not `model_outputs`,
     * not `cot_content`, not `generated_text`. They cannot be repaired by re-ingest and
     * would need regeneration. Listed explicitly so the assertion below stays sharp: any
     * NEW blank model is a regression, these six are a known data limitation.
     *
     * They must not enter an arena roster: getRobustTrace substitutes a one-line stub,
     * which reproduces the 99.4% format preference documented in arena-math-findings.md.
     */
    private val knownTraceless = setOf(
        "deepseek",
        "flash_0shots_00_35_03",
        "gpt4o(2024-05-13)",
        "opus_2shots_00_37_14",
        "sonnet-3.5_0shots_09_34_29",
        "sonnet_0shots_12_01_18",
    )

    /**
     * The generated_text regression. Before the loader fix, 34 of 47 models had a blank
     * `model_output` for every row while `pred` was populated — invisible unless measured
     * per model, because the aggregate looked healthy. The backfill took that to 6.
     */
    @Test
    fun `no model has a wholly blank trace column`() {
        val blank = query(
            """
            SELECT model_name, COUNT(*) AS n,
                   SUM(CASE WHEN TRIM(COALESCE(model_output,'')) = '' THEN 1 ELSE 0 END) AS empty
            FROM eval_results GROUP BY model_name
            HAVING empty * 1.0 / n > 0.5
            """.trimIndent()
        ) ?: return

        val unexpected = blank.filterNot { it[0] in knownTraceless }
        assertTrue(
            unexpected.isEmpty(),
            "NEW models whose trace is >50% blank (getRobustTrace will substitute a one-line " +
                "stub, reproducing the 99.4% format preference): " +
                unexpected.joinToString { "${it[0]} ${it[2]}/${it[1]}" }
        )
        // And the known set must not silently grow stale either.
        val recovered = knownTraceless - blank.map { it[0] }.toSet()
        assertTrue(
            recovered.isEmpty(),
            "these models now have traces and should be removed from knownTraceless: $recovered"
        )
    }

    /** The pure function, including the fallback path the corpus does not currently exercise. */
    @Test
    fun `unwrap keeps only the response field`() {
        assertEquals(
            "Step 1. The answer is (C)",
            unwrapTraceEnvelope("""{"response": "Step 1. The answer is (C)", "reason_code": "A", "difficulty": 0}""")
        )
        assertFalse(unwrapTraceEnvelope("""{"response": "x", "reason_code": "A"}""").contains("reason_code"))
        // Allow-list: an unknown future metadata key is dropped too, not just reason_code.
        assertEquals("x", unwrapTraceEnvelope("""{"response": "x", "self_rated_confidence": 0.9}"""))
        // Non-envelope prose passes through untouched.
        assertEquals("We refer to Wikipedia articles.", unwrapTraceEnvelope("We refer to Wikipedia articles."))
        // Malformed JSON falls back to the raw string rather than throwing...
        assertEquals("""{"response": broken""", unwrapTraceEnvelope("""{"response": broken"""))
        // ...and an envelope with no usable `response` also falls back, so nothing is lost.
        assertEquals("""{"reason_code": "A"}""", unwrapTraceEnvelope("""{"reason_code": "A"}"""))
    }

    /** The exclusion list must be an enforcement point, not a note. */
    @Test
    fun `banned models are rejected at roster load`() {
        val v = taxonomy.dataset.EvalIngestValidator(dbPath)
        val ex = org.junit.jupiter.api.assertThrows<IllegalStateException> {
            v.enforceNamedExclusions(listOf("gpt-4o-2024-08-06", "Meta-Llama-3-70B-Instruct"))
        }
        assertTrue(ex.message!!.contains("Meta-Llama-3-70B-Instruct"))
        assertTrue(ex.message!!.contains("question-id space"))
        // A clean roster passes.
        v.enforceNamedExclusions(listOf("gpt-4o-2024-08-06", "claude-3-5-haiku-20241022"))
    }
}
