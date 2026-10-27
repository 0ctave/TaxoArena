package taxonomy.operations

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * H9-REM: the construction-order shuffle helper.
 *
 * The absent path is the production path for every run ever built, so it has to be the
 * identity with no copy and no RNG (test 1). The present path is a registered arm, so its
 * permutation has to be pinned (test 3) and independent of what ran before it (test 2).
 */
class ConstructionOrderTest {

    private val items = (0 until 16).map { "n%08d".format(it + 1) }

    @Test
    fun `absent seed returns the same list instance`() {
        val order = ConstructionOrder(null)
        assertFalse(order.active)
        for ((iteration, pass) in listOf(1 to "split@d1", 3 to "split@d2", 7 to "starved", 2 to "siblings@n00000004", 9 to "redundant")) {
            assertSame(items, order.arrange(items, iteration, pass), "inert path must return the caller's list, not a copy")
        }
        val empty = emptyList<String>()
        assertSame(empty, order.arrange(empty, 1, "split@d1"))
    }

    @Test
    fun `permutation is a pure function of seed, iteration and pass`() {
        val a = ConstructionOrder(42L)
        val b = ConstructionOrder(42L)
        assertTrue(a.active)
        // b runs other shuffles first: the count of prior shuffles must not matter.
        b.arrange(items, 1, "split@d1"); b.arrange(items, 5, "redundant"); b.arrange(items, 2, "starved")
        assertEquals(a.arrange(items, 3, "split@d2"), b.arrange(items, 3, "split@d2"))
        assertEquals(a.arrange(items, 3, "split@d2"), a.arrange(items, 3, "split@d2"), "repeat call, same result")
    }

    @Test
    fun `permutation equals Collections shuffle under Random of derive`() {
        // Pins the algorithm: a refactor that changed it would silently change the permutation
        // of a registered arm.
        val seed = 7L
        val expected = ArrayList(items).also {
            java.util.Collections.shuffle(it, java.util.Random(ConstructionOrder.derive(seed, 4, "split@d3")))
        }
        assertEquals(expected, ConstructionOrder(seed).arrange(items, 4, "split@d3"))
        assertEquals(
            seed xor (4L * -0x61c8864680b583ebL) xor "split@d3".hashCode().toLong(),
            ConstructionOrder.derive(seed, 4, "split@d3")
        )
    }

    @Test
    fun `different iteration or pass tag changes the permutation`() {
        val order = ConstructionOrder(1L)
        val base = order.arrange(items, 1, "split@d1")
        assertNotEquals(items, base, "seed 1 must not be the identity on 16 elements")
        assertNotEquals(base, order.arrange(items, 2, "split@d1"), "iteration is part of the key")
        assertNotEquals(base, order.arrange(items, 1, "split@d2"), "pass tag is part of the key")
        assertNotEquals(base, ConstructionOrder(2L).arrange(items, 1, "split@d1"), "seed is part of the key")
    }

    @Test
    fun `output is a permutation`() {
        for (seed in listOf(1L, 2L, 3L, 137L)) {
            val out = ConstructionOrder(seed).arrange(items, 1, "split@d1")
            assertEquals(items.size, out.size)
            assertEquals(items.sorted(), out.sorted(), "same multiset")
            assertNotSame(items, out)
        }
    }

    private fun assertNotSame(a: Any, b: Any) = assertFalse(a === b, "shuffled path must not mutate the caller's list")
}
