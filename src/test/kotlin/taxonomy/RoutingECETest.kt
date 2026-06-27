package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.utils.computeRoutingECE

/**
 * Expected Calibration Error (Guo et al. 2017): the gap between a router's
 * confidence and its accuracy, averaged over confidence bins.
 */
class RoutingECETest {

    @Test
    fun perfectly_calibrated_router_has_near_zero_ece() {
        // 10 queries, all argmax confidence 0.6; exactly 6 of 10 are correct ⇒ acc == conf.
        val predicted = (0 until 10).associate { i ->
            "q$i" to mapOf("a" to 0.6, "b" to 0.4)
        }
        val groundTruth = (0 until 10).associate { i ->
            "q$i" to if (i < 6) "a" else "b" // 6 correct (argmax "a"), 4 wrong
        }
        val ece = computeRoutingECE(predicted, groundTruth)
        assertEquals(0.0, ece, 1e-9)
    }

    @Test
    fun overconfident_router_has_high_ece() {
        // All queries claim 0.95 confidence but only 2 of 10 are correct ⇒ ECE ≈ 0.75.
        val predicted = (0 until 10).associate { i ->
            "q$i" to mapOf("a" to 0.95, "b" to 0.05)
        }
        val groundTruth = (0 until 10).associate { i ->
            "q$i" to if (i < 2) "a" else "b"
        }
        val ece = computeRoutingECE(predicted, groundTruth)
        assertTrue(ece > 0.5, "overconfident router should have ECE > 0.5, was $ece")
    }

    @Test
    fun empty_ground_truth_returns_zero_without_throwing() {
        val predicted = mapOf("q0" to mapOf("a" to 0.9, "b" to 0.1))
        assertEquals(0.0, computeRoutingECE(predicted, emptyMap()), 1e-9)
    }
}
