package taxonomy.service

import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.jsonObject
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.dataset.ModelEvalResult

/**
 * `TracePreparation.robustTrace` (moved verbatim out of TaxonomyBenchmarkService) equals the Python
 * port `rejudge_grok.robust_trace` / `maybe_resolve` on every fixture case: envelope unwrap, RESOLVED
 * injection, OPTIONS / BLIND (no injection), blank output with a pred letter in / out of range, no
 * pred, malformed envelopes. The counters increment as the service's fields did.
 */
class TracePreparationTest {

    private fun row(output: String?, pred: String?, options: List<String>) = ModelEvalResult(
        questionId = 1, modelName = "m", category = "c", questionText = "q", options = options, gtAnswer = "A",
        pred = pred, modelOutput = output ?: "", isCorrect = false
    )

    @Test
    fun `every fixture case matches the Python port`() {
        val cases = JudgeWiringFixtures.read("trace_prep_cases.json") as JsonArray
        assertTrue(cases.size >= 10)
        for (c in cases) {
            val o = c.jsonObject
            val stats = TracePreparation.Stats()
            val out = TracePreparation.robustTrace(
                row(JudgeWiringFixtures.strOrNull(o, "model_output"), JudgeWiringFixtures.strOrNull(o, "pred"), JudgeWiringFixtures.strings(o, "options")),
                JudgeWiringFixtures.str(o, "mode"), stats
            )
            assertEquals(JudgeWiringFixtures.str(o, "expected"), out, "case: ${JudgeWiringFixtures.str(o, "label")}")
        }
    }

    @Test
    fun `counters track injected and unavailable resolutions`() {
        val stats = TracePreparation.Stats()
        val opts = listOf("x", "y", "")
        TracePreparation.robustTrace(row("trace", "A", opts), "RESOLVED", stats)     // injected
        TracePreparation.robustTrace(row("trace", "C", opts), "RESOLVED", stats)     // empty option text -> unavailable
        TracePreparation.robustTrace(row("trace", "Z", opts), "RESOLVED", stats)     // out of range -> unavailable
        TracePreparation.robustTrace(row("trace", null, opts), "RESOLVED", stats)    // no pred -> unavailable
        TracePreparation.robustTrace(row("trace", "A", opts), "OPTIONS", stats)      // not RESOLVED: untouched, uncounted
        TracePreparation.robustTrace(row("", "A", opts), "RESOLVED", stats)          // blank output: fallback, uncounted
        assertEquals(1, stats.resolvedInjected.get())
        assertEquals(3, stats.resolvedUnavailable.get())
    }
}
