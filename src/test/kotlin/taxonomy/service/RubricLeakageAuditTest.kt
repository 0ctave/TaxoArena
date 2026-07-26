package taxonomy.service

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.ModelEvalStore
import taxonomy.operations.TaxonomyLlmClient

/**
 * Guards the rubric leakage audit.
 *
 * The induction prompt tells the model not to restate question text or correct options, but an
 * instruction is not a check. A rubric that reproduces a correct option verbatim has memorised
 * an answer rather than abstracted a reasoning property, and that transfers to the held-out split
 * even though the held-out QUESTIONS were withheld. This makes the constraint measurable, so it
 * can be reported as a property rather than asserted as an intention.
 */
class RubricLeakageAuditTest {

    private fun service() = TaxonomyJudgeService(
        // maxSharedNgram is pure string work; no collaborator is reached.
        mock(MMLUDatasetFetcher::class.java),
        mock(TaxonomyLlmClient::class.java),
        mock(TaxonomyConfig::class.java),
        mock(TaxonomyArenaService::class.java),
        mock(ModelEvalStore::class.java)
    )

    @Test
    fun `verbatim reuse of a correct option is detected`() {
        val s = service()
        val options = listOf("the marginal product of the third worker equals ten units")
        val rubric = "Rules: must verify that the marginal product of the third worker equals ten units."
        val (n, gram) = s.maxSharedNgram(rubric, options)
        assertTrue(n >= 5, "expected a long shared span, got $n ($gram)")
    }

    @Test
    fun `an abstract rule shares no long span`() {
        val s = service()
        val options = listOf("the marginal product of the third worker equals ten units")
        val rubric = "Must check that dimensional consistency holds before comparing quantities."
        val (n, _) = s.maxSharedNgram(rubric, options)
        assertTrue(n < 5, "an abstract rule should not share a 5-gram, got $n")
    }

    @Test
    fun `short technical phrases do not trip the threshold`() {
        // "standard deviation" is expected vocabulary overlap, not leakage. The threshold is 5
        // tokens precisely so ordinary domain language does not produce false positives.
        val s = service()
        val options = listOf("a standard deviation of 4.5 across the sample")
        val rubric = "Must compute the standard deviation correctly from the sample variance."
        val (n, _) = s.maxSharedNgram(rubric, options)
        assertTrue(n in 1..4, "expected a short overlap below threshold, got $n")
    }

    @Test
    fun `matching is case and punctuation insensitive`() {
        val s = service()
        val options = listOf("Apply Bayes' theorem to the conditional chain.")
        val rubric = "apply bayes theorem to the conditional chain"
        val (n, _) = s.maxSharedNgram(rubric, options)
        assertTrue(n >= 5, "casing and punctuation must not hide verbatim reuse, got $n")
    }

    @Test
    fun `empty inputs are handled`() {
        val s = service()
        assertEquals(0, s.maxSharedNgram("", listOf("something")).first)
        assertEquals(0, s.maxSharedNgram("something", emptyList()).first)
    }

    @Test
    fun `the longest shared span is reported, not the first`() {
        val s = service()
        val options = listOf("alpha beta gamma delta epsilon zeta")
        val rubric = "prefix alpha beta gamma delta epsilon zeta suffix"
        val (n, gram) = s.maxSharedNgram(rubric, options)
        assertEquals(6, n, "should report the maximal span, got $n ($gram)")
    }
}
