package taxonomy.dataset

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Stage 0a equivalence: [McLetter] must reproduce the three letter-based sites it replaced
 * byte-for-byte — the ingest correctness rule, the induction rendering, and the leakage-audit
 * spans (docs/multi_corpus_design.md §3.3).
 */
class McLetterTest {

    /** The expression ModelEvalLoader used before the verifier existed. */
    private fun oldIsCorrect(pred: String?, answer: String) = pred != null && pred == answer

    @Test
    fun `isCorrect matches the old letter-equality expression on every pred-answer pair`() {
        val preds = listOf(null, "", "A", "B", "a", "J", " A", "A ", "AB")
        val answers = listOf("", "A", "B", "a", "J", "AB")
        val options = listOf("x", "y")
        var checked = 0
        for (p in preds) for (a in answers) {
            assertEquals(oldIsCorrect(p, a), McLetter.isCorrect(p, a, options), "pred=$p answer=$a")
            assertEquals(oldIsCorrect(p, a), McLetter.isCorrect(p, a, null), "pred=$p answer=$a (no options)")
            checked++
        }
        assertEquals(preds.size * answers.size, checked)
        assertFalse(McLetter.isCorrect(null, "A", options))
        assertTrue(McLetter.isCorrect("", "", null), "empty pred equals empty answer, as before")
        assertTrue(McLetter.isCorrect("C", "C", null))
    }

    @Test
    fun `renderItem reproduces the lettered induction rendering with the answer ticked`() {
        val options = listOf("alpha", "beta", "gamma")
        assertEquals("Q: Which?\nChoices: A) alpha | B) beta ✓ | C) gamma", McLetter.renderItem("Which?", options, "B"))
        // Lower-case letters are upper-cased as before; a missing/blank answer ticks nothing.
        assertEquals("Q: Which?\nChoices: A) alpha ✓ | B) beta | C) gamma", McLetter.renderItem("Which?", options, "a"))
        assertEquals("Q: Which?\nChoices: A) alpha | B) beta | C) gamma", McLetter.renderItem("Which?", options, null))
        assertEquals("Q: Which?\nChoices: A) alpha | B) beta | C) gamma", McLetter.renderItem("Which?", options, ""))
        assertEquals("Q: Which?\nChoices: ", McLetter.renderItem("Which?", emptyList(), "A"))
    }

    @Test
    fun `answerNGrams and distractors split the option list as the leakage audit did`() {
        val options = listOf("alpha", "beta", "gamma")
        assertEquals(setOf("beta"), McLetter.answerNGrams("B", options))
        assertEquals(listOf("alpha", "gamma"), McLetter.distractors("B", options))
        // Out-of-range or absent answers: no correct span, every option a distractor.
        assertEquals(emptySet<String>(), McLetter.answerNGrams("Z", options))
        assertEquals(options, McLetter.distractors("Z", options))
        assertEquals(emptySet<String>(), McLetter.answerNGrams(null, options))
        assertEquals(emptySet<String>(), McLetter.answerNGrams("A", null))
        assertEquals(emptyList<String>(), McLetter.distractors("A", null))
        assertEquals(options, McLetter.candidateSet(options))
        assertEquals("MC_LETTER", McLetter.name)
    }
}
