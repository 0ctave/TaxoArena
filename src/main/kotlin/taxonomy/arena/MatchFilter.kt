package taxonomy.arena

import taxonomy.model.MatchFilterSummary

/**
 * Optional, reference-free restriction on WHICH question a (cell, model pair) match is played on.
 *
 * [NONE] is the default and reproduces the historical scheduler exactly — every code path that
 * reads this enum must be a no-op under it, because the stage-0a replay gate compares artifacts
 * byte for byte.
 *
 * [ANSWER_DISAGREEMENT] restricts a pair's candidate questions to those where the two candidates'
 * OWN extracted final answers differ. Measured on the pool of record over the six top-4 pairs
 * (experiment_results/x12_crossdomain/scheduling_probe.txt, docs/judge_v2_program.md "SCHEDULING
 * (2026-09-13)"): the two answers differ on 16.9% of question-pairs; 79.6% of THOSE are decidable
 * against the key, against 0.04% of the pairs where the answers agree. Scheduling only the
 * disagreements therefore retains 99.8% of every decidable pair while judging 16.9% of the
 * matches — and it deletes exactly the signal-free pairs on which FRONTIER showed the judge
 * inventing length-correlated winners (+34 / -44 between iask_pro and arx_0314).
 *
 * The rule uses NO ANSWER KEY. It compares two predictions and nothing else; see
 * [AnswerDisagreementFilter].
 *
 * CAVEAT, and the reason this is an option rather than the behaviour: it presumes an extractable
 * final answer. On free-form / online arenas where "the same answer" is undefined every question
 * is UNDETERMINED, every question is kept, and the filter degrades to [NONE] on its own.
 */
enum class MatchFilter(val tomlValue: String) {
    NONE("none"),
    ANSWER_DISAGREEMENT("answerDisagreement");

    val enabled: Boolean get() = this != NONE

    companion object {
        fun fromToml(raw: String): MatchFilter {
            val v = raw.trim().trim('"', '\'')
            return entries.firstOrNull { it.tomlValue.equals(v, ignoreCase = true) }
                ?: throw IllegalArgumentException(
                    "matchFilter must be one of " +
                        entries.joinToString(", ") { "\"" + it.tomlValue + "\"" } +
                        ", got \"" + v + "\""
                )
        }
    }
}

/**
 * The predicate itself, deliberately isolated in an object that can see nothing else.
 *
 * ── REFERENCE-FREE BY CONSTRUCTION ────────────────────────────────────────────────────────────
 * The ONLY inputs are the two candidates' own extracted predictions. It must never read
 * `is_correct`, `gt_answer` (ModelEvalResult.isCorrect / .gtAnswer), the reserved pool's key, or
 * anything derived from them: the arena is reference-free, and a scheduler that consulted the key
 * to choose questions would contaminate every verdict downstream of it. `MatchFilterInputsTest`
 * pins both the signature and the source text of this file against that.
 * ──────────────────────────────────────────────────────────────────────────────────────────────
 *
 * Comparison is trimmed and case-insensitive: MMLU-Pro predictions are single letters, and "a"
 * against "A" is agreement rather than evidence.
 */
object AnswerDisagreementFilter {

    enum class Verdict {
        /** Both answers extracted and equal — the pair carries no correctness signal here. */
        AGREE,

        /** Both answers extracted and different — at most one of them can be right. */
        DISAGREE,

        /** At least one answer is missing or blank. Never a reason to drop a question. */
        UNDETERMINED
    }

    fun verdict(predA: String?, predB: String?): Verdict {
        val a = predA?.trim()
        val b = predB?.trim()
        if (a.isNullOrEmpty() || b.isNullOrEmpty()) return Verdict.UNDETERMINED
        return if (a.equals(b, ignoreCase = true)) Verdict.AGREE else Verdict.DISAGREE
    }

    /** Keep the question unless the two extracted answers are known to be the same. */
    fun keep(predA: String?, predB: String?): Boolean = verdict(predA, predB) != Verdict.AGREE
}

/**
 * Per-run bookkeeping for the match filter: what it saw, what it dropped, where it gave up.
 *
 * Shared by [BtMatchScheduler] and the [ActiveBtRacingScheduler] instances it builds per batch, so
 * one object accumulates the whole run. Accesses are synchronised because the racing path is
 * rebuilt each round and nothing guarantees the caller stays on one thread.
 */
class MatchFilterStats(val filter: MatchFilter) {

    private val log = org.slf4j.LoggerFactory.getLogger("taxonomy.arena.MatchFilter")

    private var slotEvaluations = 0L
    private var candidatesBefore = 0L
    private var candidatesAfter = 0L
    private var questionPairsSeen = 0L
    private var questionPairsUndetermined = 0L
    private var matchesScheduled = 0L
    private val fallbackSlots = LinkedHashSet<String>()
    private var inertWarned = false

    /**
     * Record one (cell, pair) slot evaluation and say which candidate set to schedule from.
     *
     * [candidates] is the unfiltered set the scheduler would have used. Returned UNCHANGED — the
     * same list instance, not a copy — under [MatchFilter.NONE], so the caller's downstream code
     * is literally the historical code path.
     *
     * GRACEFUL DEGRADATION. When filtering leaves fewer than [minNeeded] candidates for this slot,
     * the unfiltered set is returned and the slot is counted as a fallback, logged once per slot
     * naming the cell and the pair. A question whose verdict is UNDETERMINED is always kept, so
     * missing predictions can only ever widen the set, never narrow it.
     */
    fun apply(
        leafId: String,
        key: PairKey,
        candidates: List<Int>,
        minNeeded: Int,
        predA: (Int) -> String?,
        predB: (Int) -> String?
    ): List<Int> {
        if (!filter.enabled) return candidates
        val kept = ArrayList<Int>(candidates.size)
        var undetermined = 0
        for (q in candidates) {
            // NO ANSWER KEY IS READ HERE, and none may ever be: the only values that reach the
            // predicate are the two candidates' own extracted predictions (eval_results.pred).
            // Reading is_correct / gt_answer here would contaminate a reference-free arena.
            val v = AnswerDisagreementFilter.verdict(predA(q), predB(q))
            if (v == AnswerDisagreementFilter.Verdict.UNDETERMINED) undetermined++
            if (v != AnswerDisagreementFilter.Verdict.AGREE) kept.add(q)
        }
        synchronized(this) {
            slotEvaluations++
            candidatesBefore += candidates.size
            questionPairsSeen += candidates.size
            questionPairsUndetermined += undetermined
            if (candidates.isNotEmpty() && undetermined == candidates.size && !inertWarned) {
                inertWarned = true
                log.warn(
                    "[MATCH-FILTER] matchFilter=" + filter.tomlValue + " is INERT on this corpus: no question " +
                        "in cell " + leafId + " has an extracted answer for BOTH " + key.first + " and " +
                        key.second + ", so every question is UNDETERMINED and kept. Scheduling proceeds " +
                        "exactly as matchFilter=\"none\". Expected on free-form/generative corpora, where " +
                        "\"the same answer\" is undefined."
                )
            }
            if (kept.size < minNeeded && candidates.size >= minNeeded) {
                candidatesAfter += candidates.size
                if (fallbackSlots.add(leafId + "|" + key.first + "|" + key.second)) {
                    log.info(
                        "[MATCH-FILTER] fallback: cell " + leafId + ", pair " + key.first + " vs " + key.second +
                            " — answer-disagreement filtering left " + kept.size + " candidate question(s), " +
                            "below the " + minNeeded + " the scheduler needs; using the unfiltered " +
                            candidates.size + " for this slot."
                    )
                }
                return candidates
            }
            candidatesAfter += kept.size
        }
        return kept
    }

    fun noteMatchesScheduled(n: Int) {
        if (n <= 0) return
        synchronized(this) { matchesScheduled += n }
    }

    fun summary(): MatchFilterSummary = synchronized(this) {
        MatchFilterSummary(
            filter = filter.tomlValue,
            slotEvaluations = slotEvaluations,
            candidateQuestionsBefore = candidatesBefore,
            candidateQuestionsAfter = candidatesAfter,
            fallbackSlots = fallbackSlots.size,
            matchesScheduled = matchesScheduled,
            questionPairsSeen = questionPairsSeen,
            questionPairsUndetermined = questionPairsUndetermined,
            inert = filter.enabled && questionPairsSeen > 0L && questionPairsSeen == questionPairsUndetermined
        )
    }

    /** True when the filter ran but never saw a question with both answers extracted. */
    fun isInert(): Boolean = summary().inert

    fun logSummary() {
        val s = summary()
        if (!filter.enabled) {
            log.info(
                "[MATCH-FILTER] matchFilter=\"none\": " + s.matchesScheduled +
                    " match(es) scheduled, no filtering applied."
            )
            return
        }
        val retained =
            if (s.candidateQuestionsBefore > 0) 100.0 * s.candidateQuestionsAfter / s.candidateQuestionsBefore
            else 0.0
        log.info(
            "[MATCH-FILTER] matchFilter=\"" + filter.tomlValue + "\": " + s.slotEvaluations +
                " (cell, pair) slot evaluation(s); candidate questions " + s.candidateQuestionsBefore +
                " before -> " + s.candidateQuestionsAfter + " after (" + "%.1f".format(retained) +
                "% retained); " + s.fallbackSlots + " slot(s) fell back to the unfiltered set; " +
                s.questionPairsUndetermined + " of " + s.questionPairsSeen + " question-pairs UNDETERMINED " +
                "(missing prediction, kept); " + s.matchesScheduled + " match(es) scheduled." +
                (if (s.inert) " FILTER WAS INERT for the whole run — behaviour identical to \"none\"." else "")
        )
    }
}
