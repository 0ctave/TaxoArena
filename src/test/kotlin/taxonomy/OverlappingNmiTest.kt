package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.utils.OverlappingNmi

/**
 * Lancichinetti, Fortunato & Kertész (2009) overlapping NMI.
 *
 * Coverings are expressed as queryId -> (clusterId -> membership). Cluster ids
 * of the two coverings are independent — only the shared item universe matters.
 */
class OverlappingNmiTest {

    @Test
    fun disjoint_perfect_assignment_scores_one() {
        // Predicted and ground-truth describe the same disjoint partition,
        // even though the cluster labels differ between the two coverings.
        val predicted = mapOf(
            "q1" to mapOf("c1" to 1.0),
            "q2" to mapOf("c1" to 1.0),
            "q3" to mapOf("c2" to 1.0),
            "q4" to mapOf("c2" to 1.0),
        )
        val groundTruth = mapOf(
            "q1" to mapOf("g1" to 1.0),
            "q2" to mapOf("g1" to 1.0),
            "q3" to mapOf("g2" to 1.0),
            "q4" to mapOf("g2" to 1.0),
        )
        val nmi = OverlappingNmi.compute(predicted, groundTruth)
        assertEquals(1.0, nmi, 1e-9, "Identical disjoint coverings must give NMI = 1")
    }

    @Test
    fun independent_random_assignment_scores_near_zero() {
        // Predicted splits by parity; ground truth splits by half. The two
        // partitions are statistically independent, so NMI ≈ 0.
        val n = 100
        val predicted = HashMap<String, Map<String, Double>>()
        val groundTruth = HashMap<String, Map<String, Double>>()
        for (i in 0 until n) {
            val q = "q$i"
            predicted[q] = mapOf((if (i % 2 == 0) "p0" else "p1") to 1.0)
            groundTruth[q] = mapOf((if (i < n / 2) "g0" else "g1") to 1.0)
        }
        val nmi = OverlappingNmi.compute(predicted, groundTruth)
        assertTrue(nmi < 0.15, "Independent partitions must give NMI near 0, was $nmi")
    }

    @Test
    fun overlapping_membership_differs_from_disjoint() {
        // Ground truth: two clusters. Predicted: same two clusters, but one
        // query (q2) is routed to BOTH predicted clusters (soft / polyhierarchy).
        val groundTruth = mapOf(
            "q1" to mapOf("g1" to 1.0),
            "q2" to mapOf("g1" to 1.0),
            "q3" to mapOf("g2" to 1.0),
            "q4" to mapOf("g2" to 1.0),
        )
        val disjoint = mapOf(
            "q1" to mapOf("c1" to 1.0),
            "q2" to mapOf("c1" to 1.0),
            "q3" to mapOf("c2" to 1.0),
            "q4" to mapOf("c2" to 1.0),
        )
        val overlapping = mapOf(
            "q1" to mapOf("c1" to 1.0),
            "q2" to mapOf("c1" to 1.0, "c2" to 1.0), // q2 in two clusters
            "q3" to mapOf("c2" to 1.0),
            "q4" to mapOf("c2" to 1.0),
        )
        val disjointNmi = OverlappingNmi.compute(disjoint, groundTruth)
        val overlappingNmi = OverlappingNmi.compute(overlapping, groundTruth)
        assertTrue(
            kotlin.math.abs(disjointNmi - overlappingNmi) > 1e-3,
            "Overlap must change the score measurably (disjoint=$disjointNmi overlap=$overlappingNmi)",
        )
    }
}
