package taxonomy.service

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.arena.ModelPlacement
import java.util.Random
import kotlin.math.exp

/**
 * Placing a new model in an existing leaderboard must cost what the local crowding demands
 * and nothing more — no floor, no ceiling, no per-pair constant.
 *
 * THE GOVERNING LAW, because the thresholds below only make sense against it. A Bradley-Terry
 * comparison carries at most 0.25 of Fisher information, so resolving a strength to a window
 * of width g costs on the order of 4/g^2 comparisons. Measured mid-board with five anchors:
 * g = 3.0 -> ~12 comparisons, g = 2.0 -> ~27, g = 1.0 -> ~93, g = 0.5 -> beyond 300. Cost is
 * therefore quadratic in crowding, NOT logarithmic in the roster: binary search's O(log k)
 * assumes noiseless comparisons and does not survive contact with a coin flip.
 *
 * Assertions are relative wherever possible; the simulation is seeded, but the point being
 * pinned is the direction of each effect, not a particular count.
 */
class ModelPlacementTest {

    private fun sigmoid(z: Double) = 1.0 / (1.0 + exp(-z))

    /** Runs a placement to completion and returns how many comparisons it took. */
    private fun placeAndCount(
        anchors: List<ModelPlacement.Anchor>,
        trueTheta: Double,
        seed: Long,
        placement: ModelPlacement = ModelPlacement(),
        cap: Int = 300,
        priorMean: Double = 0.0,
        priorSd: Double = 2.0,
        slack: Int = 0,
        adaptive: Boolean = true,
    ): Int {
        val rng = Random(seed)
        val tally = LinkedHashMap<String, ModelPlacement.Outcome>()
        var n = 0
        var cyclic = 0
        while (n < cap) {
            val belief = placement.posterior(anchors, tally.values.toList(), priorMean, priorSd)
            if (placement.isPlaced(belief, anchors, slack)) break
            val opponent =
                if (adaptive) placement.nextOpponent(belief, anchors) ?: break
                else anchors[cyclic++ % anchors.size]
            val win = rng.nextDouble() < sigmoid(trueTheta - opponent.theta)
            val prev = tally[opponent.model] ?: ModelPlacement.Outcome(opponent.model)
            tally[opponent.model] = prev.copy(
                wins = prev.wins + if (win) 1.0 else 0.0,
                losses = prev.losses + if (win) 0.0 else 1.0,
            )
            n++
        }
        return n
    }

    private fun board(vararg thetas: Double): List<ModelPlacement.Anchor> =
        thetas.mapIndexed { i, t -> ModelPlacement.Anchor("m$i", t) }.sortedByDescending { it.theta }

    private fun meanCost(seeds: LongRange = 1L..8L, f: (Long) -> Int) = seeds.map(f).average()

    // ── Cost follows the geometry, not a constant ──────────────────────────────────────

    @Test
    fun `cost rises as the board gets more crowded`() {
        // Same roster size, same relative position, same seeds — only the spacing changes.
        fun costAtGap(gap: Double) = meanCost {
            placeAndCount(board(2 * gap, gap, 0.0, -gap, -2 * gap), trueTheta = gap * 0.5, seed = it)
        }

        val wide = costAtGap(3.0)
        val mid = costAtGap(1.5)
        val tight = costAtGap(0.75)

        assertTrue(wide < mid, "wider gaps must be cheaper (wide=$wide, mid=$mid)")
        assertTrue(mid < tight, "tighter gaps must be dearer (mid=$mid, tight=$tight)")
        // Quadratic, not linear: halving the gap must more than double the cost.
        assertTrue(
            tight > 2.0 * mid,
            "cost should scale like 1/gap^2 (mid=$mid at 1.5, tight=$tight at 0.75)"
        )
    }

    @Test
    fun `a model clearly above the whole board is placed almost immediately`() {
        // The point of having no minimum: an obvious answer should be cheap. The slot above
        // the board is unbounded, so the posterior clears it in a handful of comparisons —
        // where a fixed floor of 8 per pair would have spent 8 against every anchor.
        val anchors = board(2.0, 1.0, 0.0, -1.0, -2.0)
        val cost = meanCost { placeAndCount(anchors, trueTheta = 7.0, seed = it) }
        assertTrue(cost <= 10.0, "a runaway leader should need very few comparisons; took $cost")
    }

    @Test
    fun `allowing one rank of slack is far cheaper than exact placement`() {
        // The knob that replaces the magic constant. On a crowded board, insisting on an exact
        // rank is what turns a placement into a tournament; "position 3 or 4" is both cheaper
        // and usually the honest claim.
        val anchors = board(1.0, 0.5, 0.0, -0.5, -1.0)
        val exact = meanCost { placeAndCount(anchors, 0.25, it, slack = 0) }
        val loose = meanCost { placeAndCount(anchors, 0.25, it, slack = 1) }

        assertTrue(loose < exact, "slack must reduce cost (slack=1 -> $loose, slack=0 -> $exact)")
        assertTrue(loose < 0.5 * exact, "and substantially: $loose vs $exact")
    }

    // ── Adaptive opponent choice earns its keep ────────────────────────────────────────

    @Test
    fun `choosing the informative opponent beats cycling through the board`() {
        // Uniform allocation spends comparisons on anchors far from the newcomer, where the
        // outcome is nearly certain and the information near zero.
        val anchors = board(6.0, 4.0, 2.0, 0.0, -2.0, -4.0, -6.0)
        val adaptive = meanCost { placeAndCount(anchors, trueTheta = 0.8, seed = it, adaptive = true) }
        val uniform = meanCost { placeAndCount(anchors, trueTheta = 0.8, seed = it, adaptive = false) }

        assertTrue(
            adaptive < uniform,
            "adaptive opponent choice must beat round-robin (adaptive=$adaptive, uniform=$uniform)"
        )
    }

    @Test
    fun `the chosen opponent is the one nearest the current belief`() {
        val anchors = board(4.0, 2.0, 0.0, -2.0, -4.0)
        val placement = ModelPlacement()
        val belief = placement.posterior(anchors, emptyList(), priorMean = 2.0, priorSd = 0.5)

        val chosen = placement.nextOpponent(belief, anchors)!!
        val nearest = anchors.minBy { kotlin.math.abs(it.theta - belief.mean) }
        assertEquals(
            nearest.model, chosen.model,
            "Fisher information peaks at the nearest anchor (belief mean ${belief.mean})"
        )
    }

    // ── Per-cell placement: the pooled fit as the prior ────────────────────────────────

    @Test
    fun `a pooled prior only pays when it carries its precision`() {
        // The saving that keeps closely-related cells from exploding — but only if the cell
        // inherits the pooled SE as well as the pooled mean. Re-centring a prior that stays
        // two logits wide buys nothing, which is worth pinning: it is the mistake that makes
        // "just use the parent's answer" look useless when it is merely under-specified.
        val anchors = board(2.0, 1.0, 0.0, -1.0, -2.0)
        val truth = 0.5

        val cold = meanCost { placeAndCount(anchors, truth, it, priorMean = 0.0, priorSd = 2.0) }
        val centredOnly = meanCost { placeAndCount(anchors, truth, it, priorMean = truth, priorSd = 2.0) }
        val pooled = meanCost { placeAndCount(anchors, truth, it, priorMean = truth, priorSd = 0.4) }

        assertTrue(
            pooled < 0.8 * cold,
            "a tight pooled prior must cut the cost materially (pooled=$pooled, cold=$cold)"
        )
        assertTrue(
            kotlin.math.abs(centredOnly - cold) < 0.4 * cold,
            "merely re-centring a wide prior should change little (centred=$centredOnly, cold=$cold)"
        )
    }

    // ── Structure ──────────────────────────────────────────────────────────────────────

    @Test
    fun `an undefeated newcomer does not blow up the posterior`() {
        // Complete separation: the case a Newton fit diverges on, and the reason the belief is
        // carried on a grid.
        val anchors = board(1.0, 0.0, -1.0)
        val belief = ModelPlacement().posterior(
            anchors,
            anchors.map { ModelPlacement.Outcome(it.model, wins = 5.0) },
        )
        assertTrue(belief.mean.isFinite() && belief.sd.isFinite())
        assertTrue(belief.mean > 1.0, "an undefeated model should sit above the board")
        assertTrue(belief.sd < 10.0, "the prior must keep the posterior proper; sd=${belief.sd}")
    }

    @Test
    fun `rank probabilities are a distribution over the slots`() {
        val anchors = board(2.0, 0.0, -2.0)
        val placement = ModelPlacement()
        val belief = placement.posterior(anchors, listOf(ModelPlacement.Outcome("m1", wins = 3.0)))
        val post = placement.rankPosterior(belief, anchors)

        assertEquals(anchors.size + 1, post.size, "one slot above, one below, one per gap")
        assertEquals(1.0, post.sum(), 1e-9)
        assertTrue(post.all { it >= 0.0 })
    }

    @Test
    fun `a wider window never holds less mass than a narrower one`() {
        val anchors = board(2.0, 1.0, 0.0, -1.0, -2.0)
        val placement = ModelPlacement()
        val belief = placement.posterior(anchors, listOf(ModelPlacement.Outcome("m2", wins = 2.0, losses = 1.0)))

        val exact = placement.bestWindow(belief, anchors, slack = 0).second
        val loose = placement.bestWindow(belief, anchors, slack = 1).second
        val looser = placement.bestWindow(belief, anchors, slack = 2).second
        assertTrue(exact <= loose && loose <= looser, "$exact / $loose / $looser")
        assertTrue(looser <= 1.0 + 1e-9)
    }

    @Test
    fun `tightestGap reports how crowded the board is`() {
        assertEquals(1.0, ModelPlacement.tightestGap(board(3.0, 2.0, 0.0)), 1e-12)
        assertEquals(0.25, ModelPlacement.tightestGap(board(1.0, 0.75, 0.0)), 1e-12)
        assertTrue(ModelPlacement.tightestGap(board(1.0)).isInfinite())
    }

    @Test
    fun `unidentified models are not used as anchors`() {
        // A model with no comparisons in a cell carries a placeholder strength of 0.0; used as
        // an anchor it would sit in the middle of the board and drag placements toward it.
        val anchors = ModelPlacement.anchorsFrom(
            btScores = mapOf("seen-a" to 1.5, "seen-b" to -1.5, "unseen" to 0.0),
            stdErrors = mapOf("seen-a" to 0.3, "seen-b" to 0.3, "unseen" to 10.0),
            identified = setOf("seen-a", "seen-b"),
        )
        assertEquals(listOf("seen-a", "seen-b"), anchors.map { it.model })
    }
}
