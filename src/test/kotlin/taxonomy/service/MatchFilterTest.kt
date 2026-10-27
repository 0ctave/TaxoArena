package taxonomy.service

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.arena.*
import java.io.File

/**
 * The optional answer-disagreement match filter.
 *
 * Three things are pinned here, in order of how much damage getting them wrong would do:
 *
 *  1. THE FILTER READS NO ANSWER KEY. `no key inputs` walks the predicate's signature and the
 *     source of every site that calls it. The arena is reference-free; a scheduler that chose
 *     questions by consulting `is_correct` / `gt_answer` would contaminate every verdict
 *     downstream of it, and it would do so silently.
 *  2. "none" IS THE HISTORICAL SCHEDULER. Not approximately — `apply` hands back the caller's
 *     own list instance, so the downstream code is the same code. The stage-0a replay gate
 *     compares artifacts byte for byte.
 *  3. IT NEVER STARVES A SLOT. Missing predictions keep a question; a (cell, pair) whose
 *     filtered pool cannot fund its next match falls back to the unfiltered pool and says so.
 */
class MatchFilterTest {

    // ── 1. the predicate ─────────────────────────────────────────────────────────────────

    @Test
    fun `agreeing answers are dropped, disagreeing ones kept`() {
        assertFalse(AnswerDisagreementFilter.keep("A", "A"))
        assertEquals(AnswerDisagreementFilter.Verdict.AGREE, AnswerDisagreementFilter.verdict("A", "A"))
        assertTrue(AnswerDisagreementFilter.keep("A", "B"))
        assertEquals(AnswerDisagreementFilter.Verdict.DISAGREE, AnswerDisagreementFilter.verdict("A", "B"))
    }

    @Test
    fun `a blank or missing prediction on either side keeps the question`() {
        val cases: List<Pair<String?, String?>> = listOf(
            null to "A", "A" to null, null to null,
            "" to "A", "A" to "", "   " to "A", "A" to "   ",
            "" to "", null to ""
        )
        for (pair in cases) {
            val (a, b) = pair
            assertEquals(
                AnswerDisagreementFilter.Verdict.UNDETERMINED,
                AnswerDisagreementFilter.verdict(a, b),
                "verdict($a, $b)"
            )
            assertTrue(AnswerDisagreementFilter.keep(a, b), "keep($a, $b)")
        }
    }

    @Test
    fun `comparison is trimmed and case-insensitive`() {
        assertFalse(AnswerDisagreementFilter.keep(" A ", "a"))
        assertTrue(AnswerDisagreementFilter.keep("A", "AB"))
    }

    @Test
    fun `matchFilter parses its two values and rejects anything else`() {
        assertEquals(MatchFilter.NONE, MatchFilter.fromToml("none"))
        assertEquals(MatchFilter.NONE, MatchFilter.fromToml("\"none\""))
        assertEquals(MatchFilter.ANSWER_DISAGREEMENT, MatchFilter.fromToml("\"answerDisagreement\""))
        assertEquals(MatchFilter.ANSWER_DISAGREEMENT, MatchFilter.fromToml(" answerdisagreement "))
        assertFalse(MatchFilter.NONE.enabled)
        assertTrue(MatchFilter.ANSWER_DISAGREEMENT.enabled)
        val e = assertThrows(IllegalArgumentException::class.java) { MatchFilter.fromToml("\"disagree\"") }
        assertTrue(e.message!!.contains("answerDisagreement"), e.message)
    }

    // ── 2. no key inputs ─────────────────────────────────────────────────────────────────

    /** Source with KDoc, block and line comments removed — the code the compiler actually sees. */
    private fun codeOf(path: String): String {
        val src = File(path)
        assertTrue(src.isFile, "$path not found; run from the repo root")
        return src.readText()
            .replace(Regex("/\\*.*?\\*/", RegexOption.DOT_MATCHES_ALL), " ")
            .lines().joinToString("\n") { it.substringBefore("//") }
    }

    @Test
    fun `no key inputs - the predicate takes exactly two predictions and nothing else`() {
        // Signature: two nullable Strings in, a verdict out. There is no third channel through
        // which a ground-truth answer could reach the decision.
        val fns = AnswerDisagreementFilter::class.java.declaredMethods
            .filter { it.name == "verdict" || it.name == "keep" }
        assertEquals(2, fns.size, "expected exactly verdict() and keep()")
        for (f in fns) {
            assertEquals(2, f.parameterCount, "${f.name} must take exactly the two predictions")
            assertTrue(f.parameterTypes.all { it == String::class.java },
                "${f.name} parameters must both be String?, were ${f.parameterTypes.map { p -> p.name }}")
        }
        // The object holds no state at all, so nothing can be smuggled in through a field.
        val fields = AnswerDisagreementFilter::class.java.declaredFields
            .filter { !it.isSynthetic && it.name != "INSTANCE" && !it.name.startsWith("$") }
        assertTrue(fields.isEmpty(), "the predicate must be stateless, found ${fields.map { it.name }}")
    }

    @Test
    fun `no key inputs - neither the filter nor its call sites mention the answer key`() {
        val forbidden = listOf("isCorrect", "gtAnswer", "is_correct", "gt_answer", "correctAnswer")
        val files = listOf(
            "src/main/kotlin/taxonomy/arena/MatchFilter.kt",
            "src/main/kotlin/taxonomy/arena/ActiveBtRacingScheduler.kt",
            "src/main/kotlin/taxonomy/arena/BtMatchScheduler.kt"
        )
        for (path in files) {
            val code = codeOf(path)
            for (bad in forbidden) {
                assertFalse(code.contains(bad), "$path reads the answer key ('$bad') in executable code")
            }
        }
        // Every value handed to the filter at a call site comes from `pred`, the model's own
        // extracted answer. If a new call site appears, it has to satisfy this too.
        val accessor = Regex("pred[AB] = \\{([^}]*)\\}")
        val bodies = files.flatMap { p ->
            accessor.findAll(codeOf(p)).map { it.groupValues[1].substringAfter("->").trim() }.toList()
        }
        assertEquals(6, bodies.size, "expected two accessors at each of the three call sites, got $bodies")
        for (body in bodies) {
            // Either the eval row's own `pred` column, or the LeafArena prediction maps built
            // from it. Nothing else may be read to decide which question a pair is judged on.
            assertTrue(
                body.endsWith("?.pred") || Regex("^pred[XY]\\[q]$").matches(body),
                "a match-filter accessor reads something other than a prediction: `$body`"
            )
        }
    }

    // ── 3. behaviour in the scheduler ────────────────────────────────────────────────────

    private fun arena(preds: Map<String, Map<Int, String>>, queries: List<Int> = (1..5).toList()) =
        LeafArena("leaf-1", listOf("a", "b"), queries, preds, pairBudget = 40)

    @Test
    fun `filter off is the historical path and touches nothing`() {
        val a = arena(mapOf(
            "a" to mapOf(1 to "A", 2 to "A", 3 to "A", 4 to "A", 5 to "A"),
            "b" to mapOf(1 to "A", 2 to "A", 3 to "B", 4 to "A", 5 to "A")
        ))
        val off = MatchFilterStats(MatchFilter.NONE)
        val sched = ActiveBtRacingScheduler(matchFilterStats = off, minCandidatesPerSlot = 1)
        val plain = ActiveBtRacingScheduler()
        assertEquals(plain.pickQuery(a, ordered("a", "b")), sched.pickQuery(a, ordered("a", "b")))
        val s = off.summary()
        assertEquals(0L, s.slotEvaluations)
        assertEquals(0L, s.candidateQuestionsBefore)
        // Identity, not a copy: the historical code path is literally unchanged.
        val candidates = listOf(1, 2, 3)
        assertSame(candidates, off.apply("leaf-1", ordered("a", "b"), candidates, 1, { "A" }, { "A" }))
    }

    @Test
    fun `filter on schedules only the question the two answers differ on`() {
        val a = arena(mapOf(
            "a" to mapOf(1 to "A", 2 to "A", 3 to "A", 4 to "A", 5 to "A"),
            "b" to mapOf(1 to "A", 2 to "A", 3 to "B", 4 to "A", 5 to "A")
        ))
        val stats = MatchFilterStats(MatchFilter.ANSWER_DISAGREEMENT)
        val sched = ActiveBtRacingScheduler(matchFilterStats = stats, minCandidatesPerSlot = 1)
        // Unfiltered, least-used-then-lowest-id would take question 1.
        assertEquals(3, sched.pickQuery(a, ordered("a", "b")))
        val s = stats.summary()
        assertEquals(1L, s.slotEvaluations)
        assertEquals(5L, s.candidateQuestionsBefore)
        assertEquals(1L, s.candidateQuestionsAfter)
        assertEquals(0, s.fallbackSlots)
        assertFalse(s.inert)
    }

    @Test
    fun `a slot the filter would starve falls back to the unfiltered pool`() {
        // Every answer agrees: filtering leaves nothing, so the pair must still get a question.
        val a = arena(mapOf(
            "a" to mapOf(1 to "A", 2 to "B", 3 to "C", 4 to "D", 5 to "E"),
            "b" to mapOf(1 to "A", 2 to "B", 3 to "C", 4 to "D", 5 to "E")
        ))
        val stats = MatchFilterStats(MatchFilter.ANSWER_DISAGREEMENT)
        val sched = ActiveBtRacingScheduler(matchFilterStats = stats, minCandidatesPerSlot = 1)
        assertEquals(1, sched.pickQuery(a, ordered("a", "b")))
        val s = stats.summary()
        assertEquals(1, s.fallbackSlots)
        // The fallback slot is charged its full unfiltered pool, so the CSV's before/after
        // ratio reports what was actually scheduled from rather than a hypothetical.
        assertEquals(5L, s.candidateQuestionsBefore)
        assertEquals(5L, s.candidateQuestionsAfter)
        assertFalse(s.inert)
    }

    @Test
    fun `a corpus with no extractable answers leaves the filter inert`() {
        val a = arena(mapOf(
            "a" to mapOf(1 to "", 2 to "", 3 to "", 4 to "", 5 to ""),
            "b" to mapOf(1 to "", 2 to "", 3 to "", 4 to "", 5 to "")
        ))
        val stats = MatchFilterStats(MatchFilter.ANSWER_DISAGREEMENT)
        val sched = ActiveBtRacingScheduler(matchFilterStats = stats, minCandidatesPerSlot = 1)
        assertEquals(1, sched.pickQuery(a, ordered("a", "b")))
        val s = stats.summary()
        assertTrue(s.inert, "a corpus with no extractable answers must report the filter inert")
        assertEquals(0, s.fallbackSlots, "nothing was dropped, so nothing fell back")
        assertEquals(s.questionPairsSeen, s.questionPairsUndetermined)
        assertEquals(s.candidateQuestionsBefore, s.candidateQuestionsAfter)
    }

    @Test
    fun `already-used questions are not offered to the filter twice`() {
        val a = arena(mapOf(
            "a" to mapOf(1 to "A", 2 to "A", 3 to "A"),
            "b" to mapOf(1 to "B", 2 to "B", 3 to "A")
        ), queries = listOf(1, 2, 3))
        val stats = MatchFilterStats(MatchFilter.ANSWER_DISAGREEMENT)
        val sched = ActiveBtRacingScheduler(matchFilterStats = stats, minCandidatesPerSlot = 1)
        val key = ordered("a", "b")
        assertEquals(1, sched.pickQuery(a, key))
        a.completed.getOrPut(key) { hashSetOf() }.add(1)
        assertEquals(2, sched.pickQuery(a, key))
        a.completed.getValue(key).add(2)
        // Only question 3 is left and the two models agree on it: fall back rather than starve.
        assertEquals(3, sched.pickQuery(a, key))
        assertEquals(1, stats.summary().fallbackSlots)
    }
}
