package taxonomy.arena

import org.slf4j.LoggerFactory
import taxonomy.model.NodePairStats
import taxonomy.service.DomainEvaluation
import kotlin.math.abs

/**
 * Pure accumulation of match outcomes into per-leaf pair statistics, plus the
 * presentation-order diagnostic. Extracted from TaxonomyBenchmarkService so the
 * arithmetic is testable without a Spring context (same pattern as AcceptanceRuleTest).
 *
 * Invariants this object maintains, asserted by PairStatsInvariantTest:
 *   - winsA + winsB + ties == totalComparisons (only decisive verdicts count as wins)
 *   - winAFirst and winASecond each lie in [0, totalComparisons]
 *   - the ledger fields (winAFirst/winASecond) are DIAGNOSTIC ONLY and never feed a fit
 *
 * On that last point: position debiasing happens once, at the verdict level — each match
 * is judged in both presentation orders and an order-inconsistent split is forced to a
 * TIE (TaxonomyArenaService). A second, post-hoc "correction" of the pair counts from
 * the order ledgers was removed on 2026-09-05: it double-counted ties (the ledgers
 * half-credit them, and the fitter adds 0.5*ties again) and always in favour of
 * modelA, which pair ordering makes the lexicographically smaller model on every
 * comparison. auditOrderBias() keeps the detection and drops the mutation.
 */
object PairStatsLedger {

    private val log = LoggerFactory.getLogger(javaClass)

    /** Minimum comparisons before an order-share estimate is worth flagging. */
    const val ORDER_BIAS_MIN_N = 6.0

    /** |winAFirst - winASecond| / n above which a pair is flagged as order-sensitive. */
    const val ORDER_BIAS_DELTA = 0.3

    /**
     * Fold one combined verdict into the pair's statistics. Handles both storage
     * orientations: when [existing] is stored as (modelB, modelA) the outcome and its
     * order ledgers are mirrored before accumulation. Mutates and returns [existing]
     * when present, builds a fresh row otherwise. Returns null for an unrecordable
     * winner string (e.g. INVALID), in which case nothing must be persisted.
     */
    fun accumulate(
        existing: NodePairStats?,
        nodeId: String,
        modelA: String,
        modelB: String,
        outcome: DomainEvaluation,
        judgeAgreed: Boolean,
        judgeCheckable: Boolean,
        now: Long = System.currentTimeMillis()
    ): NodePairStats? {
        val (wA, wB) = when (outcome.winner.uppercase()) {
            "MODEL A" -> 1.0 to 0.0
            "MODEL B" -> 0.0 to 1.0
            "TIE"     -> 0.0 to 0.0
            else      -> return null
        }
        val isTie = outcome.winner.equals("TIE", ignoreCase = true)

        if (existing == null) {
            return NodePairStats(
                nodeId = nodeId,
                modelA = modelA,
                modelB = modelB,
                winsA = wA,
                winsB = wB,
                ties = if (isTie) 1.0 else 0.0,
                totalComparisons = 1.0,
                positionFlips = if (outcome.positionFlip) 1 else 0,
                winAFirst = outcome.winAFirst,
                winASecond = outcome.winASecond,
                agreementWins = if (judgeCheckable && judgeAgreed) 1 else 0,
                agreementChecks = if (judgeCheckable) 1 else 0,
                lastUpdated = now
            )
        }

        if (existing.modelA == modelA) {
            existing.winsA += wA
            existing.winsB += wB
            existing.winAFirst += outcome.winAFirst
            existing.winASecond += outcome.winASecond
        } else {
            existing.winsA += wB
            existing.winsB += wA
            existing.winAFirst += (1.0 - outcome.winAFirst)
            existing.winASecond += (1.0 - outcome.winASecond)
        }
        existing.ties += if (isTie) 1 else 0
        existing.totalComparisons += 1
        existing.positionFlips += if (outcome.positionFlip) 1 else 0
        if (judgeCheckable) {
            existing.agreementWins += if (judgeAgreed) 1 else 0
            existing.agreementChecks += 1
        }
        existing.lastUpdated = now
        return existing
    }

    /**
     * Signed order-preference of the pair, (winAFirst - winASecond) / n, or null while
     * n < [ORDER_BIAS_MIN_N]. Positive means modelA does better when presented first.
     */
    fun orderDelta(ps: NodePairStats): Double? {
        if (ps.totalComparisons < ORDER_BIAS_MIN_N) return null
        return (ps.winAFirst - ps.winASecond) / ps.totalComparisons
    }

    /**
     * Log any pair whose order-preference exceeds [ORDER_BIAS_DELTA] and return the
     * stats UNCHANGED. This is the only step between the stored pair statistics and
     * BtMmFitter.fit, and its contract is identity: order bias is detected here and
     * debiased at the verdict level, never by rewriting counts. Any future pre-fit
     * transformation added here must keep PairStatsInvariantTest green.
     */
    fun auditOrderBias(pairStats: List<NodePairStats>): List<NodePairStats> {
        for (ps in pairStats) {
            val delta = orderDelta(ps) ?: continue
            if (abs(delta) > ORDER_BIAS_DELTA) {
                log.warn(
                    String.format(
                        java.util.Locale.ROOT,
                        "[ORDER-BIAS] node '%s' %s vs %s: order delta %.2f over n=%.0f " +
                            "(ledgers %.1f/%.1f). Diagnostic only — counts are not modified; " +
                            "flips were already forced to ties per verdict.",
                        ps.nodeId, ps.modelA, ps.modelB,
                        delta, ps.totalComparisons, ps.winAFirst, ps.winASecond
                    )
                )
            }
        }
        return pairStats
    }
}
