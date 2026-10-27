package taxonomy.service

import taxonomy.dataset.ModelEvalResult
import taxonomy.dataset.unwrapTraceEnvelope
import java.util.concurrent.atomic.AtomicInteger

/**
 * Trace preparation before judging: envelope unwrap, blank-output fallbacks and the RESOLVED
 * selected-answer injection. Moved VERBATIM out of `TaxonomyBenchmarkService`
 * (`getRobustTrace` / `maybeResolveSelection`, 2026-09-16, JUDGE-WIRING) so the runner and the
 * payload harness share one implementation; the only change is that the two RESOLVED counters
 * travel in a [Stats] parameter instead of the service's fields. `rejudge_grok.robust_trace` /
 * `maybe_resolve` are the Python port of the same functions and TracePreparationTest pins the
 * two against shared fixtures. `MistralJudgePathUnchangedTest` guards the move.
 */
object TracePreparation {

    /** Counts how often RESOLVED could and could not attach the selected option. */
    class Stats {
        val resolvedInjected = AtomicInteger(0)
        val resolvedUnavailable = AtomicInteger(0)
    }

    // Strips the arx JSON envelope (and its correctness-predicting `reason_code`) down to
    // the prose response. See taxonomy.dataset.unwrapTraceEnvelope.
    fun robustTrace(r: ModelEvalResult, judgeOptionMode: String, stats: Stats): String {
        val output = r.modelOutput?.let { unwrapTraceEnvelope(it) }
        if (!output.isNullOrBlank()) return maybeResolveSelection(r, output, judgeOptionMode, stats)
        val pred = r.pred?.trim()?.uppercase() ?: return "The model did not provide a prediction."
        val predChar = pred.firstOrNull() ?: return "The model did not provide a prediction."
        if (predChar in 'A'..'J') {
            val idx = predChar - 'A'
            if (idx in r.options.indices) {
                return "The model selected option $predChar: \"${r.options[idx]}\"."
            }
        }
        return "The model predicted: \"$pred\"."
    }

    /**
     * Under `judgeOptionMode = RESOLVED`, append this model's OWN selected option, resolved
     * from its `pred` letter to the option text, so a bare "the answer is (C)" carries a
     * referent once the candidate set is withheld.
     *
     * WHY. Measured over 2,000 reserved traces: 72% end in "the answer is (X)" and only 23%
     * carry the option text anywhere nearby. Withholding the options without this leaves
     * roughly half the traces' conclusions unreadable — "(C)" against "(F)" — so a fall in
     * judge agreement cannot be separated into "assessed the reasoning instead" and "could
     * not tell what was claimed". Resolving the selection holds the second fixed and varies
     * only the first, which is the question RQ1 asks.
     *
     * The injection is ADDITIVE and marked, never a rewrite of the model's prose: the trace
     * stays verbatim and gains one bracketed line. It is a transformation applied before
     * judging and must be reported as such.
     *
     * ANSWER-KEY BLINDNESS. This appends the model's OWN selection, which is wrong on a
     * large fraction of comparisons. `gt_answer` is never consulted here or anywhere on the
     * judging path.
     */
    fun maybeResolveSelection(r: ModelEvalResult, trace: String, judgeOptionMode: String, stats: Stats): String {
        if (!judgeOptionMode.equals("RESOLVED", ignoreCase = true)) return trace
        val predChar = r.pred?.trim()?.uppercase()?.firstOrNull()
        if (predChar == null || predChar !in 'A'..'J') {
            stats.resolvedUnavailable.incrementAndGet(); return trace
        }
        val idx = predChar - 'A'
        if (idx !in r.options.indices) { stats.resolvedUnavailable.incrementAndGet(); return trace }
        val text = r.options[idx].toString().trim()
        if (text.isEmpty()) { stats.resolvedUnavailable.incrementAndGet(); return trace }
        stats.resolvedInjected.incrementAndGet()
        return "$trace\n\n[This model's selected answer: ($predChar) $text]"
    }
}
