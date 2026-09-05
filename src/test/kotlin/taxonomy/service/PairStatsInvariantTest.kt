package taxonomy.service

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.arena.BtMmFitter
import taxonomy.arena.PairStatsLedger
import taxonomy.model.NodePairStats
import kotlin.math.abs
import kotlin.random.Random

/**
 * Conservation-law tests for the verdict -> pair-stats -> BT-fit chain.
 *
 * These assert properties that must hold for ANY input, not worked examples that
 * re-derive the arithmetic (the vacuous-test failure mode removed in the 2026-07-26
 * suite audit). The fixtures encode the verdict-combination rule of
 * TaxonomyArenaService (two presentation orders; an order-inconsistent split is
 * forced to a TIE with winAFirst/winASecond recording the raw per-order votes).
 *
 * The regression test at the bottom pins the 2026-09-05 removal of
 * adjustForPositionBias: order-ledger information is diagnostic and must never
 * change the counts a fit sees. That correction double-counted ties and converted
 * pure position bias into wins for the lexicographically smaller model.
 */
class PairStatsInvariantTest {

    private val node = "leaf-test"

    /** Verdict fixtures, mirroring TaxonomyArenaService.kt's combination rule. */
    private fun consistentAWin() = DomainEvaluation(
        domain = node, winner = "Model A", rationale = "", confidence = 0.9,
        positionFlip = false, winAFirst = 1.0, winASecond = 1.0
    )
    private fun consistentBWin() = DomainEvaluation(
        domain = node, winner = "Model B", rationale = "", confidence = 0.9,
        positionFlip = false, winAFirst = 0.0, winASecond = 0.0
    )
    private fun consistentTie() = DomainEvaluation(
        domain = node, winner = "TIE", rationale = "", confidence = 0.7,
        positionFlip = false, winAFirst = 0.5, winASecond = 0.5
    )
    /** A judge that always prefers the first-presented trace: split verdict, forced TIE. */
    private fun firstSlotFlip() = DomainEvaluation(
        domain = node, winner = "TIE", rationale = "", confidence = 0.5,
        positionFlip = true, winAFirst = 1.0, winASecond = 0.0
    )
    private fun invalid() = DomainEvaluation(
        domain = node, winner = "INVALID", rationale = "", confidence = 0.0
    )

    private fun randomOutcome(rng: Random) = when (rng.nextInt(5)) {
        0 -> consistentAWin()
        1 -> consistentBWin()
        2 -> consistentTie()
        3 -> firstSlotFlip()
        else -> invalid()
    }

    private fun mirror(o: DomainEvaluation) = o.copy(
        winner = when (o.winner) {
            "Model A" -> "Model B"
            "Model B" -> "Model A"
            else -> o.winner
        },
        winAFirst = 1.0 - o.winAFirst,
        winASecond = 1.0 - o.winASecond
    )

    private fun accumulateStream(outcomes: List<DomainEvaluation>): NodePairStats? {
        var row: NodePairStats? = null
        for (o in outcomes) {
            row = PairStatsLedger.accumulate(row, node, "alpha", "beta", o,
                judgeAgreed = true, judgeCheckable = true) ?: row
        }
        return row
    }

    @Test
    fun `accumulation conserves counts for any outcome stream`() {
        val rng = Random(42)
        val outcomes = List(500) { randomOutcome(rng) }
        val row = accumulateStream(outcomes)!!

        // Only decisive verdicts count as wins; every recorded match is a win or a tie.
        assertEquals(row.totalComparisons, row.winsA + row.winsB + row.ties, 1e-9,
            "winsA + winsB + ties must equal totalComparisons")
        // Order ledgers are per-match scores in [0,1], so their sums stay in [0, n].
        assertTrue(row.winAFirst in 0.0..row.totalComparisons)
        assertTrue(row.winASecond in 0.0..row.totalComparisons)
        // A position flip is always recorded as a tie, never as a win.
        assertTrue(row.positionFlips <= row.ties + 1e-9)
        // INVALID outcomes must leave no trace at all.
        val recorded = outcomes.count { it.winner != "INVALID" }
        assertEquals(recorded.toDouble(), row.totalComparisons, 1e-9)
    }

    @Test
    fun `recording the same match from the reversed perspective yields identical stats`() {
        val rng = Random(7)
        val outcomes = List(200) { randomOutcome(rng) }

        val direct = accumulateStream(outcomes)!!

        // Same physical matches, reported with the models' roles swapped: the stored
        // row (keyed alpha/beta by its first match) must come out identical.
        var mirrored: NodePairStats? = null
        for ((i, o) in outcomes.withIndex()) {
            mirrored = if (i == 0 || mirrored == null) {
                PairStatsLedger.accumulate(mirrored, node, "alpha", "beta", o,
                    judgeAgreed = true, judgeCheckable = true) ?: mirrored
            } else {
                PairStatsLedger.accumulate(mirrored, node, "beta", "alpha", mirror(o),
                    judgeAgreed = true, judgeCheckable = true) ?: mirrored
            }
        }

        assertEquals(direct.winsA, mirrored!!.winsA, 1e-9)
        assertEquals(direct.winsB, mirrored.winsB, 1e-9)
        assertEquals(direct.ties, mirrored.ties, 1e-9)
        assertEquals(direct.winAFirst, mirrored.winAFirst, 1e-9)
        assertEquals(direct.winASecond, mirrored.winASecond, 1e-9)
        assertEquals(direct.totalComparisons, mirrored.totalComparisons, 1e-9)
    }

    @Test
    fun `auditOrderBias returns stats unchanged even when it flags`() {
        val flagged = NodePairStats(node, "alpha", "beta",
            winsA = 2.0, winsB = 1.0, ties = 9.0, totalComparisons = 12.0,
            winAFirst = 11.0, winASecond = 1.0)      // delta 0.83 — well over the flag bar
        val quiet = NodePairStats(node, "gamma", "delta",
            winsA = 5.0, winsB = 4.0, ties = 3.0, totalComparisons = 12.0,
            winAFirst = 7.0, winASecond = 6.0)
        val input = listOf(flagged, quiet)
        val before = input.map { it.copy() }

        val out = PairStatsLedger.auditOrderBias(input)

        assertSame(input, out, "auditOrderBias must be the identity on its input list")
        assertEquals(before, out.map { it.copy() }, "auditOrderBias must not mutate any field")
    }

    @Test
    fun `pure position bias produces a flat fit — regression for the removed correction`() {
        // A judge with maximal position bias and zero real preference: every match is an
        // order-inconsistent split, forced to a TIE, with the ledgers at 1.0 / 0.0.
        val row = accumulateStream(List(12) { firstSlotFlip() })!!

        assertEquals(0.0, row.winsA, 1e-9)
        assertEquals(0.0, row.winsB, 1e-9)
        assertEquals(12.0, row.ties, 1e-9)
        val delta = PairStatsLedger.orderDelta(row)!!
        assertEquals(1.0, delta, 1e-9, "the diagnostic must detect the bias at full strength")

        // Through the production pre-fit path. The pre-2026-09-05 correction turned this
        // exact input into winsA=6, winsB=0 — order noise converted into a decisive gap
        // for the model that pair ordering happens to call "A".
        val fitInput = PairStatsLedger.auditOrderBias(listOf(row))
        val theta = BtMmFitter.fit(listOf("alpha", "beta"), fitInput, context = "invariant-test")
        assertEquals(theta["alpha"]!!, theta["beta"]!!, 1e-9,
            "a pair with no decisive verdicts must fit dead level, whatever the ledgers say")
    }

    @Test
    fun `order ledgers never influence the fit`() {
        fun stats(waf: Double, was: Double) = listOf(
            NodePairStats(node, "alpha", "beta",
                winsA = 7.0, winsB = 3.0, ties = 2.0, totalComparisons = 12.0,
                winAFirst = waf, winASecond = was))

        val neutral  = BtMmFitter.fit(listOf("alpha", "beta"),
            PairStatsLedger.auditOrderBias(stats(5.0, 5.0)), context = "invariant-test")
        val skewed   = BtMmFitter.fit(listOf("alpha", "beta"),
            PairStatsLedger.auditOrderBias(stats(12.0, 0.0)), context = "invariant-test")

        assertEquals(neutral["alpha"]!!, skewed["alpha"]!!, 1e-12)
        assertEquals(neutral["beta"]!!, skewed["beta"]!!, 1e-12)
    }

    @Test
    fun `consistent ties keep models level`() {
        val row = accumulateStream(List(10) { consistentTie() })!!
        val theta = BtMmFitter.fit(listOf("alpha", "beta"),
            PairStatsLedger.auditOrderBias(listOf(row)), context = "invariant-test")
        assertEquals(theta["alpha"]!!, theta["beta"]!!, 1e-9)
    }

    @Test
    fun `fit is invariant to the order models are listed in`() {
        val rng = Random(99)
        val models = listOf("m1", "m2", "m3", "m4")
        val pairs = mutableListOf<NodePairStats>()
        for (i in models.indices) for (j in i + 1 until models.size) {
            val wa = rng.nextInt(0, 8).toDouble()
            val wb = rng.nextInt(0, 8).toDouble()
            val t = rng.nextInt(0, 4).toDouble()
            pairs += NodePairStats(node, models[i], models[j],
                winsA = wa, winsB = wb, ties = t, totalComparisons = wa + wb + t)
        }
        val a = BtMmFitter.fit(models, pairs, context = "invariant-test")
        val b = BtMmFitter.fit(models.reversed(), pairs, context = "invariant-test")
        for (m in models) {
            assertEquals(a[m]!!, b[m]!!, 1e-6, "theta for $m must not depend on list order")
        }
    }
}
