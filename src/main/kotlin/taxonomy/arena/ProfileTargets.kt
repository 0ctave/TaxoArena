package taxonomy.arena

import taxonomy.model.NodePairStats

/**
 * Shared state for PROFILE mode: sample until SE(theta_{model, stratum}) <= [seTarget]
 * for every model in every stratum, instead of stopping on rank decisions.
 *
 * WHY THIS MODE EXISTS (2026-09-06). Decision-mode stopping (placement + binomial)
 * retires a pair the moment its ORDER is pinned, which systematically starves the
 * per-cell margins where the model x domain interaction lives — measured twice: the
 * registered per-pair test of the x8 runs died of it, and the x12 top-cluster deltas
 * collapsed where tie-heavy rank-adjacent sampling compressed them (independently
 * corroborated by the grok second-judge pass). Profile mode asks the estimation
 * question directly: fund comparisons until every model's strength IN EVERY STRATUM
 * is measured to [seTarget] logits, or the stratum's question pool is exhausted.
 *
 * Strata are groups of leaves (frozen in experiment_configs/strata_profile_v1.json,
 * derived from the leaves' vMF embedding geometry). SEs are computed by the service
 * once per round from a pooled per-stratum Bradley-Terry fit and published here; the
 * scheduler and the stopping policy both read this object, so they cannot disagree
 * about what "finished" means — same discipline as [placedModels].
 *
 * In profile mode the decision-mode machinery is deliberately OFF: no placement, no
 * binomial early-resolution, no 2.5-sigma gate. Pairs retire only when their stratum
 * meets the target or their per-(leaf, pair) budget (= the leaf's pool) is spent.
 */
class ProfileTargets(
    val seTarget: Double,
    val leafToStratum: Map<String, String>,
) {
    /** stratum -> model -> SE from the latest pooled fit; empty until the first fit. */
    @Volatile
    var seByStratum: Map<String, Map<String, Double>> = emptyMap()

    fun stratumOf(leafId: String): String? = leafToStratum[leafId]

    fun allStrata(): Set<String> = leafToStratum.values.toSet()

    /** Worst model SE in the stratum; MAX_VALUE before any fit (never converged early). */
    fun worstSe(stratum: String): Double =
        seByStratum[stratum]?.values?.maxOrNull() ?: Double.MAX_VALUE

    fun converged(stratum: String): Boolean =
        seByStratum[stratum]?.let { ses -> ses.isNotEmpty() && ses.values.all { it <= seTarget } } ?: false

    /** How far a model is above target in this stratum; 1.0 for every model pre-fit. */
    fun deficit(stratum: String, model: String): Double {
        val ses = seByStratum[stratum] ?: return 1.0
        val se = ses[model] ?: return 1.0
        return (se - seTarget).coerceAtLeast(0.0)
    }

    /** Stratum-level priority: worst deficit, 0 once converged, 1.0 pre-fit. */
    fun stratumDeficit(stratum: String): Double {
        val ses = seByStratum[stratum] ?: return 1.0
        if (ses.isEmpty()) return 1.0
        return (ses.values.max() - seTarget).coerceAtLeast(0.0)
    }

    companion object {
        /**
         * Pool per-leaf pair stats into per-stratum sufficient statistics, orientation-
         * normalised the way aggregateLeafScores pools leaves into the domain fit.
         */
        fun poolPairStats(stats: List<NodePairStats>): List<NodePairStats> {
            val pooled = HashMap<String, NodePairStats>()
            for (ps in stats) {
                val a = minOf(ps.modelA, ps.modelB)
                val b = maxOf(ps.modelA, ps.modelB)
                val flipped = ps.modelA != a
                val wA = if (flipped) ps.winsB else ps.winsA
                val wB = if (flipped) ps.winsA else ps.winsB
                val key = "$a|$b"
                val cur = pooled[key]
                if (cur == null) {
                    pooled[key] = NodePairStats(
                        nodeId = "stratum", modelA = a, modelB = b,
                        winsA = wA, winsB = wB, ties = ps.ties,
                        totalComparisons = ps.totalComparisons
                    )
                } else {
                    cur.winsA += wA
                    cur.winsB += wB
                    cur.ties += ps.ties
                    cur.totalComparisons += ps.totalComparisons
                }
            }
            return pooled.values.toList()
        }
    }
}
