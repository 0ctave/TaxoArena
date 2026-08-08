package taxonomy.arena

import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.sqrt

/**
 * Places ONE new model in an already-fitted leaderboard, in as few comparisons as the local
 * crowding demands.
 *
 * WHY THIS IS NOT A TOURNAMENT. Ranking k models from nothing costs O(k^2) pairs. Inserting
 * one model into an order that already exists is a SEARCH: bracket it against the models
 * around it and stop when its position is no longer in doubt. The existing strengths are
 * treated as fixed anchors, so exactly one parameter is being estimated rather than k, and
 * the comparisons that pin it are the ones against nearby anchors.
 *
 * WHICH OPPONENT. A Bradley-Terry comparison against anchor j carries Fisher information
 * p(1-p) with p = sigma(theta - theta_j), maximised at p = 0.5 — the anchor whose strength
 * matches the newcomer's current estimate. A comparison against a far-away anchor is nearly
 * deterministic and tells you almost nothing. [nextOpponent] picks the argmax of expected
 * information under the current belief, not under a point estimate, so it stays honest while
 * the belief is still wide.
 *
 * WHEN TO STOP. Not at a match count. [isPlaced] asks whether the posterior puts at least
 * 1 - alpha of its mass in a single rank slot — the interval between two consecutive anchor
 * strengths. A newcomer that lands in a sparse stretch of the board is placed in two or three
 * comparisons because the slot is wide; one landing in a dense cluster needs more, because the
 * slots there are narrow. No floor and no ceiling: the number of matches is read off the
 * leaderboard's local geometry, which is the only thing that should decide it.
 *
 * The posterior is carried on a grid rather than as a Gaussian. It costs a few hundred
 * multiplications per update, it cannot diverge the way a Newton step can under complete
 * separation (an undefeated newcomer, which is the common case early), and rank probabilities
 * are then a matter of summing mass between two anchors rather than trusting a normal tail.
 */
class ModelPlacement(
    /** Mass a single rank slot must hold before the newcomer counts as placed. */
    val alpha: Double = 0.05,
    /** Prior width on the newcomer's strength, in logits, when nothing is known about it. */
    val priorSd: Double = 2.0,
    /**
     * Strength difference below which two models are reported as equivalent rather than
     * ordered, in logits. See [isSettled]; 0.2 is a 5 percentage point win-rate difference at
     * even odds. Set to 0.0 to disable the equivalence stop.
     */
    val equivalenceMargin: Double = 0.2,
    val gridPoints: Int = 801,
) {

    /** A model already on the board: its fitted strength, and the error on that fit. */
    data class Anchor(val model: String, val theta: Double, val se: Double = 0.0)

    /** What the newcomer did against one anchor. Ties split, matching `PairStats.sumX`. */
    data class Outcome(
        val opponent: String,
        val wins: Double = 0.0,
        val losses: Double = 0.0,
        val ties: Double = 0.0,
    ) {
        val n: Double get() = wins + losses + ties
    }

    /** Posterior over the newcomer's strength, as mass on a grid. */
    class Belief(val grid: DoubleArray, val weight: DoubleArray) {
        val mean: Double = grid.indices.sumOf { grid[it] * weight[it] }
        val sd: Double = sqrt(grid.indices.sumOf { weight[it] * (grid[it] - mean) * (grid[it] - mean) })

        /** Posterior mass on the open interval (lo, hi). */
        fun mass(lo: Double, hi: Double): Double =
            grid.indices.sumOf { if (grid[it] > lo && grid[it] <= hi) weight[it] else 0.0 }
    }

    private fun sigmoid(z: Double): Double = 1.0 / (1.0 + exp(-z))

    /**
     * Posterior over the newcomer's strength given the anchors it has played.
     *
     * [priorMean] is where a pooled or parent-level fit already places this model, when one
     * exists — that is what makes per-cell placement cheap: the cell starts from the board's
     * answer and only has to fund the part where the cell disagrees.
     */
    fun posterior(
        anchors: List<Anchor>,
        outcomes: List<Outcome>,
        priorMean: Double = 0.0,
        priorSd: Double = this.priorSd,
    ): Belief {
        require(anchors.isNotEmpty()) { "placement needs at least one anchor" }
        val theta = anchors.associate { it.model to it.theta }

        // Cover the anchors plus room to land outside them entirely: a newcomer stronger than
        // everything on the board must be representable, or its posterior piles up at the edge
        // and `isPlaced` reports a confidence the data does not support.
        val lo = minOf(anchors.minOf { it.theta }, priorMean) - 4.0 * priorSd
        val hi = maxOf(anchors.maxOf { it.theta }, priorMean) + 4.0 * priorSd
        val step = (hi - lo) / (gridPoints - 1)
        val grid = DoubleArray(gridPoints) { lo + it * step }

        val logW = DoubleArray(gridPoints) { i ->
            val z = (grid[i] - priorMean) / priorSd
            -0.5 * z * z
        }
        for (o in outcomes) {
            val tj = theta[o.opponent] ?: continue
            val w = o.wins + 0.5 * o.ties
            val l = o.losses + 0.5 * o.ties
            if (w == 0.0 && l == 0.0) continue
            for (i in 0 until gridPoints) {
                val p = sigmoid(grid[i] - tj).coerceIn(1e-12, 1 - 1e-12)
                logW[i] += w * ln(p) + l * ln(1.0 - p)
            }
        }

        val max = logW.max()
        var sum = 0.0
        val weight = DoubleArray(gridPoints) { exp(logW[it] - max).also { v -> sum += v } }
        for (i in weight.indices) weight[i] /= sum
        return Belief(grid, weight)
    }

    /**
     * Posterior probability of each rank slot, index 0 = above every anchor, index k = below
     * every anchor. Slot r is the gap between the r-th and (r+1)-th strongest anchors.
     */
    fun rankPosterior(belief: Belief, anchors: List<Anchor>): DoubleArray {
        val sorted = anchors.map { it.theta }.sortedDescending()
        val out = DoubleArray(sorted.size + 1)
        for (r in out.indices) {
            val upper = if (r == 0) Double.POSITIVE_INFINITY else sorted[r - 1]
            val lower = if (r == sorted.size) Double.NEGATIVE_INFINITY else sorted[r]
            out[r] = belief.mass(lower, upper)
        }
        return out
    }

    /**
     * True once some run of [slack] + 1 consecutive slots holds at least 1 - alpha of the mass.
     *
     * WHY SLACK IS THE KNOB THAT MATTERS. Each comparison carries at most 0.25 of Fisher
     * information (at p = 0.5), so pinning the strength to a window of width g costs on the
     * order of 4/g^2 comparisons. Measured on this implementation, mid-board with five
     * anchors: g = 3.0 costs ~12, g = 2.0 ~27, g = 1.0 ~93, and g = 0.5 does not finish inside
     * 300. That is not an inefficiency to tune away, it is what the information in a binary
     * outcome allows.
     *
     * So exact rank certainty is the wrong target on a crowded board, and demanding it is how
     * a placement turns into a tournament. `slack = 1` — "this model is in position 4 or 5" —
     * costs a small fraction of `slack = 0` and is usually the honest claim anyway. Callers
     * that want a strength rather than a rank should read [Belief.sd] and stop at a target
     * precision instead.
     */
    fun isPlaced(belief: Belief, anchors: List<Anchor>, slack: Int = 0): Boolean =
        bestWindow(belief, anchors, slack).second >= 1.0 - alpha

    /** The most likely run of [slack] + 1 slots, as (first slot, mass). */
    fun bestWindow(belief: Belief, anchors: List<Anchor>, slack: Int = 0): Pair<Int, Double> {
        val post = rankPosterior(belief, anchors)
        val width = (slack + 1).coerceAtMost(post.size)
        var bestAt = 0
        var bestMass = -1.0
        for (start in 0..post.size - width) {
            var m = 0.0
            for (i in start until start + width) m += post[i]
            if (m > bestMass) { bestMass = m; bestAt = start }
        }
        return bestAt to bestMass
    }

    /** The slot the newcomer most likely occupies, and how sure that is. */
    fun placement(belief: Belief, anchors: List<Anchor>): Pair<Int, Double> =
        bestWindow(belief, anchors, slack = 0)

    /** Grid quantile of the posterior. */
    private fun quantile(belief: Belief, q: Double): Double {
        var acc = 0.0
        for (i in belief.grid.indices) {
            acc += belief.weight[i]
            if (acc >= q) return belief.grid[i]
        }
        return belief.grid.last()
    }

    /** Central credible interval at 1 - alpha. */
    fun credibleInterval(belief: Belief): Pair<Double, Double> =
        quantile(belief, alpha / 2.0) to quantile(belief, 1.0 - alpha / 2.0)

    /**
     * Settled: either the position is pinned, or the only models it cannot be ordered against
     * are equivalent to each other anyway.
     *
     * THE EQUIVALENCE STOP, AND WHY IT IS NEEDED. [isPlaced] can only ever say "not yet
     * separated". It has no way to say "these are the same", so a model sitting inside a tied
     * cluster stays open forever and spends its whole budget on a distinction that does not
     * exist. Measured on the settled r8 batch, that is the normal case rather than the corner
     * case: the three frontier models are routinely within 0.06 logits of one another, which no
     * budget can order.
     *
     * The rule: take the models the credible interval cannot separate this one from. If they
     * span less than [equivalenceMargin] between themselves, the remaining ambiguity is a tie
     * among equals and more comparisons cannot resolve it. Stop, and report the tie.
     *
     * The margin is a strength difference, not a rank count, and that distinction is what makes
     * this scale. A rank-based tolerance tightens automatically as the roster grows — k models
     * over a fixed range have slots of width ~range/k, so demanding a fixed number of slots
     * demands ever finer resolution and the cost per model climbs with k. A margin in logits
     * asks the same question at every roster size. Its default of 0.2 is the smallest difference
     * worth reporting rather than an arbitrary constant: at even odds, 0.2 logits is a 5
     * percentage point difference in win rate (sigma(0.1) - sigma(-0.1) = 0.0499). Raise it if
     * smaller differences do not interest you; the cost falls quadratically as you do.
     */
    fun isSettled(
        belief: Belief,
        anchors: List<Anchor>,
        slack: Int = 0,
        margin: Double = equivalenceMargin,
    ): Boolean {
        if (isPlaced(belief, anchors, slack)) return true
        if (margin <= 0.0) return false
        val (lo, hi) = credibleInterval(belief)
        // Known to within the margin: nothing left worth buying, whatever the ranks do.
        if (hi - lo <= margin) return true
        // Otherwise: which anchors does the interval fail to separate this model from?
        val confusable = anchors.map { it.theta }.filter { it > lo && it < hi }
        if (confusable.isEmpty()) return true          // interval lies inside one slot
        return (confusable.max() - confusable.min()) <= margin
    }

    /**
     * The anchor worth playing next: the one maximising expected Fisher information
     * E_theta[p(1-p)] under the current belief.
     *
     * Averaged over the belief rather than evaluated at its mean. With a wide posterior the
     * mean can sit in a gap where no anchor looks informative, and a point estimate would then
     * pick almost arbitrarily; the expectation keeps choosing the anchor that discriminates
     * across the range the newcomer might actually occupy.
     *
     * [available] filters anchors that still have unjudged questions; an anchor with nothing
     * left to play on cannot be chosen however informative it would be.
     */
    fun nextOpponent(
        belief: Belief,
        anchors: List<Anchor>,
        available: (String) -> Boolean = { true },
    ): Anchor? = anchors
        .filter { available(it.model) }
        .maxByOrNull { a ->
            belief.grid.indices.sumOf { i ->
                val p = sigmoid(belief.grid[i] - a.theta)
                belief.weight[i] * p * (1.0 - p)
            }
        }

    /**
     * Comparisons this placement would still need, as a planning figure: how many more
     * observations at the current information rate before one slot clears 1 - alpha.
     *
     * A projection, not a promise — the rate changes as the belief moves. It exists so a
     * caller can budget a round without committing to a fixed per-pair number.
     */
    fun projectedRemaining(belief: Belief, anchors: List<Anchor>, cap: Int = 64, slack: Int = 0): Int {
        if (isPlaced(belief, anchors, slack)) return 0
        val opponent = nextOpponent(belief, anchors) ?: return cap
        var b = belief
        var n = 0
        // Advance on the EXPECTED outcome: split each further comparison between win and loss
        // in the proportion the belief currently predicts, so the projection neither assumes
        // a lucky streak nor a stalemate.
        val outcomes = mutableListOf<Outcome>()
        while (n < cap && !isPlaced(b, anchors, slack)) {
            n++
            val p = sigmoid(b.mean - opponent.theta)
            outcomes += Outcome(opponent.model, wins = p, losses = 1.0 - p)
            b = posterior(anchors, outcomes, priorMean = belief.mean, priorSd = belief.sd)
        }
        return n
    }

    companion object {
        /**
         * Anchors from a fitted cell, dropping models whose strength is not identified.
         *
         * A model with no comparisons in a cell has a placeholder strength of 0.0, which would
         * otherwise act as a real anchor in the middle of the board and drag placements toward
         * it.
         */
        fun anchorsFrom(
            btScores: Map<String, Double>,
            stdErrors: Map<String, Double>,
            identified: Set<String> = btScores.keys,
        ): List<Anchor> = btScores
            .filter { it.key in identified }
            .map { (m, t) -> Anchor(m, t, stdErrors[m] ?: 0.0) }
            .sortedByDescending { it.theta }

        /** Smallest gap between neighbouring anchors — how crowded this board is. */
        fun tightestGap(anchors: List<Anchor>): Double {
            val s = anchors.map { it.theta }.sortedDescending()
            if (s.size < 2) return Double.POSITIVE_INFINITY
            return (1 until s.size).minOf { abs(s[it - 1] - s[it]) }
        }
    }
}
