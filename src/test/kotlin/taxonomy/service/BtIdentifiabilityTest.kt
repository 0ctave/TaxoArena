package taxonomy.service

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.model.NodePairStats
import kotlin.math.abs

/**
 * Guards the two ways a Bradley-Terry fit can be meaningless while still returning numbers.
 *
 * **Separation.** If one model is undefeated in a pair the likelihood is unbounded: the MLE runs
 * to infinity, MM sweeps never converge, and Fisher information n*p*(1-p) goes to zero exactly
 * where the estimate is least determined — so the SE gets *smaller* as the fit gets worse. This
 * is the normal case in an arena spanning frontier models to Llama-2.
 *
 * **Disconnection.** Theta is identified only up to an additive constant PER CONNECTED COMPONENT.
 * Scores from two components sit on two unrelated zero points, so pooling them upward mixes
 * incommensurable quantities and yields a leaderboard that looks ordinary and means nothing.
 */
class BtIdentifiabilityTest {

    private fun pair(a: String, b: String, winsA: Double, winsB: Double, ties: Double = 0.0) =
        NodePairStats(
            nodeId = "leaf", modelA = a, modelB = b,
            winsA = winsA, winsB = winsB, ties = ties,
            totalComparisons = winsA + winsB + ties
        )

    // ── connectivity ─────────────────────────────────────────────────────────────────

    @Test
    fun `a connected round robin is identified`() {
        val models = listOf("A", "B", "C")
        val stats = listOf(pair("A", "B", 6.0, 4.0), pair("B", "C", 7.0, 3.0))
        val id = BtMmFitter.assessIdentifiability(models, stats)
        assertTrue(id.identified, id.describe())
        assertEquals(1, id.components.size)
        assertTrue(id.isolated.isEmpty())
    }

    @Test
    fun `two disjoint pairs are two components and are refused`() {
        val models = listOf("A", "B", "C", "D")
        val stats = listOf(pair("A", "B", 5.0, 5.0), pair("C", "D", 5.0, 5.0))
        val id = BtMmFitter.assessIdentifiability(models, stats)
        assertFalse(id.identified, "A+B and C+D have independent zero points")
        assertEquals(2, id.components.size)
        assertTrue(id.describe().contains("components"))
    }

    @Test
    fun `a model that never played leaves the fit unidentified`() {
        // The smoke-run shape: 3 models in the roster, one real pair.
        val models = listOf("A", "B", "C")
        val id = BtMmFitter.assessIdentifiability(models, listOf(pair("A", "B", 2.0, 1.0)))
        assertFalse(id.identified, "theta_C is undefined — it has no comparisons at all")
        assertEquals(setOf("C"), id.isolated)
    }

    @Test
    fun `a chain is connected even without every pair present`() {
        // Connectivity, not completeness, is the requirement.
        val models = listOf("A", "B", "C", "D")
        val stats = listOf(pair("A", "B", 3.0, 2.0), pair("B", "C", 3.0, 2.0), pair("C", "D", 3.0, 2.0))
        assertTrue(BtMmFitter.assessIdentifiability(models, stats).identified)
    }

    @Test
    fun `pairs recorded with no comparisons do not create connectivity`() {
        val models = listOf("A", "B", "C")
        val stats = listOf(pair("A", "B", 3.0, 2.0), pair("B", "C", 0.0, 0.0))
        val id = BtMmFitter.assessIdentifiability(models, stats)
        assertFalse(id.identified, "an empty pair record is not evidence that the two models met")
        assertEquals(setOf("C"), id.isolated)
    }

    // ── the prior must not fabricate connectivity ────────────────────────────────────

    @Test
    fun `the phantom-tie prior does not make a disconnected graph look connected`() {
        // The whole point of applying the prior only to pairs with real data. Phantom ties on
        // every pair would complete the graph and make this assertion pass for the wrong reason,
        // hiding the defect the connectivity check exists to catch.
        val models = listOf("A", "B", "C", "D")
        val stats = listOf(pair("A", "B", 5.0, 0.0), pair("C", "D", 5.0, 0.0))
        BtMmFitter.fit(models, stats)   // applies the prior internally
        val id = BtMmFitter.assessIdentifiability(models, stats)
        assertEquals(2, id.components.size, "identifiability is assessed on observed data only")
        assertFalse(id.identified)
    }

    // ── separation ───────────────────────────────────────────────────────────────────

    @Test
    fun `separation is detected`() {
        val models = listOf("A", "B")
        val id = BtMmFitter.assessIdentifiability(models, listOf(pair("A", "B", 8.0, 0.0)))
        assertEquals(1, id.separatedPairs.size, "A is undefeated, so the unpenalised MLE is infinite")
    }

    @Test
    fun `a completely separated fit stays finite and converges`() {
        // Without the prior this diverges: theta_A -> +inf. With it the penalised MLE is finite,
        // which is what makes the score and its information reportable at all.
        val models = listOf("A", "B", "C")
        val stats = listOf(pair("A", "B", 10.0, 0.0), pair("B", "C", 10.0, 0.0))
        val scores = BtMmFitter.fit(models, stats)
        scores.forEach { (m, v) ->
            assertTrue(v.isFinite(), "theta for $m must be finite under separation, was $v")
            assertTrue(abs(v) < 25.0, "theta for $m ran away: $v")
        }
        assertTrue(scores["A"]!! > scores["B"]!!, "the ordering must still be recovered")
        assertTrue(scores["B"]!! > scores["C"]!!)
    }

    @Test
    fun `separation leaves positive Fisher information so the SE is not spuriously tiny`() {
        val models = listOf("A", "B")
        val stats = listOf(pair("A", "B", 10.0, 0.0))
        val scores = BtMmFitter.fit(models, stats)
        val ses = BtMmFitter.estimateStdErrors(models, scores, stats)
        // An undefeated pair is the regime where the unpenalised information collapses to 0 and
        // the SE therefore collapses with it. Penalised, the SE must remain substantial: a
        // 10-0 record on 10 comparisons is a weak constraint on theta, not a precise one.
        ses.forEach { (m, se) ->
            assertTrue(se.isFinite() && se > 0.05, "SE for $m should not be spuriously precise: $se")
        }
    }

    @Test
    fun `the prior does not move a well-determined fit much`() {
        // It has to be weak enough not to distort a real result: one phanton observation against
        // a budget of 200.
        val models = listOf("A", "B")
        val stats = listOf(pair("A", "B", 150.0, 50.0))
        val withPrior = BtMmFitter.fit(models, stats)
        val without = BtMmFitter.fit(models, stats, priorStrength = 0.0)
        val shift = abs((withPrior["A"]!! - withPrior["B"]!!) - (without["A"]!! - without["B"]!!))
        assertTrue(shift < 0.02, "prior shifted a determined fit by $shift")
    }

    @Test
    fun `ties alone do not count as separation`() {
        val models = listOf("A", "B")
        val id = BtMmFitter.assessIdentifiability(models, listOf(pair("A", "B", 0.0, 0.0, ties = 6.0)))
        assertTrue(id.separatedPairs.isEmpty(), "an all-tie pair is uninformative, not separated")
        assertTrue(id.identified)
    }
}
