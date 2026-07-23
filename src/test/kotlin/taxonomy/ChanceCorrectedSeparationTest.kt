package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.utils.StatisticsUtils
import kotlin.math.abs

/**
 * Verifies the chance-corrected separation score that gates split acceptance,
 * sibling merging, and sibling distinctness:
 *
 *   score = 1 − Σ_c W(S_c) / E[Σ_c W(S_c) | random partition of same sizes]
 *
 * with W(S) = |S|² − ‖Σx‖² and E = W(total) · Σ_c n_c(n_c−1) / (n(n−1)).
 * Required properties: 1 for a perfect partition, ≈ 0 for a random partition,
 * exactly 0 for the degenerate k=1 case (a wrapper separates nothing).
 */
class ChanceCorrectedSeparationTest {

    private fun basisVector(d: Int, axis: Int): DoubleArray =
        DoubleArray(d) { if (it == axis) 1.0 else 0.0 }

    @Test
    fun perfect_partition_scores_one() {
        val d = 8
        val clusterA = List(50) { basisVector(d, 0) }
        val clusterB = List(50) { basisVector(d, 1) }
        val score = StatisticsUtils.chanceCorrectedSeparation(listOf(clusterA, clusterB))
        assertEquals(1.0, score, 1e-9, "internally identical, mutually orthogonal clusters must score 1")
    }

    @Test
    fun random_partition_scores_near_zero() {
        // One mixed population (half e0, half e1) split into two equally mixed halves:
        // within-cluster scatter matches the random-partition expectation up to the
        // finite-size correction, so the score must sit at ~0, not at the ~0.5 the
        // uncorrected within/total ratio would report.
        val d = 8
        val half = List(25) { basisVector(d, 0) } + List(25) { basisVector(d, 1) }
        val score = StatisticsUtils.chanceCorrectedSeparation(listOf(half, half))
        assertTrue(abs(score) < 0.05, "evenly mixed halves should score ≈ 0, got $score")
    }

    @Test
    fun single_cluster_wrapper_scores_exactly_zero() {
        val d = 8
        val mixed = List(30) { basisVector(d, 0) } + List(30) { basisVector(d, 1) }
        val score = StatisticsUtils.chanceCorrectedSeparation(listOf(mixed))
        assertEquals(0.0, score, 1e-12, "a k=1 non-partition must score exactly 0")
    }

    @Test
    fun stats_overload_matches_pointwise_computation() {
        val d = 4
        val clusterA = List(10) { basisVector(d, 0) } + List(5) { basisVector(d, 2) }
        val clusterB = List(12) { basisVector(d, 1) }
        val fromPoints = StatisticsUtils.chanceCorrectedSeparation(listOf(clusterA, clusterB))

        fun stats(cluster: List<DoubleArray>): StatisticsUtils.ClusterStats {
            val sum = DoubleArray(d)
            for (v in cluster) for (i in 0 until d) sum[i] += v[i]
            return StatisticsUtils.ClusterStats(cluster.size.toDouble(), sum)
        }
        val fromStats = StatisticsUtils.chanceCorrectedSeparation(listOf(stats(clusterA), stats(clusterB)))
        assertEquals(fromPoints, fromStats, 1e-12, "stats-based overload must agree with pointwise form")
    }
}
