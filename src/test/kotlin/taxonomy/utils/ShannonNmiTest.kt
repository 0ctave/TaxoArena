package taxonomy.utils

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import kotlin.random.Random

/**
 * Standard Shannon NMI over two flat hard partitions of the same item set.
 */
class ShannonNmiTest {

    @Test
    fun identical_partition_scores_one() {
        val p = (0 until 20).associate { "q$it" to "c${it % 4}" }
        assertEquals(1.0, ShannonNmi.compute(p, p), 1e-9, "NMI(p, p) must be 1")
    }

    @Test
    fun shuffled_labels_score_near_zero() {
        val n = 200
        val rng = Random(42)
        val x = (0 until n).associate { "q$it" to "x${it % 5}" }
        val labels = (0 until n).map { "y${rng.nextInt(5)}" }
        val y = (0 until n).associate { "q$it" to labels[it] }
        val nmi = ShannonNmi.compute(x, y)
        assertTrue(nmi < 0.2, "Independent partitions must give NMI near 0, was $nmi")
    }

    @Test
    fun empty_maps_score_zero() {
        assertEquals(0.0, ShannonNmi.compute(emptyMap(), emptyMap()), 1e-12)
    }

    @Test
    fun single_label_on_either_side_scores_zero() {
        val varied = mapOf("q1" to "a", "q2" to "b", "q3" to "a", "q4" to "b")
        val constant = mapOf("q1" to "z", "q2" to "z", "q3" to "z", "q4" to "z")
        assertEquals(0.0, ShannonNmi.compute(varied, constant), 1e-12)
        assertEquals(0.0, ShannonNmi.compute(constant, varied), 1e-12)
    }

    @Test
    fun disjoint_keys_score_zero() {
        val x = mapOf("a1" to "p", "a2" to "q")
        val y = mapOf("b1" to "p", "b2" to "q")
        assertEquals(0.0, ShannonNmi.compute(x, y), 1e-12)
    }
}
