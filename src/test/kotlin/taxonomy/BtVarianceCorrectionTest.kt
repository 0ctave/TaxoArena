package taxonomy

import taxonomy.arena.*
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Pins the sum-to-zero variance correction in BtMmFitter.
 *
 * The fitter regularises the singular Bradley-Terry Fisher information F (which has 1 in
 * its null space) as Fc = F + J, J the all-ones matrix, then reads variances off the
 * diagonal of Fc^-1. The constrained pseudo-inverse is
 *
 *     F^+ = Fc^-1 - J/K^2
 *
 * so the diagonal correction is 1/K^2. Subtracting 1/K instead over-subtracts (K-1)/K^2
 * from every variance — 0.109 at K=8 — pushing nearly every value into the 1e-6 floor,
 * so reported standard errors become the floor rather than a measurement.
 *
 * This test works on the linear algebra directly rather than through a fitted model,
 * because the identity is what was wrong; a golden-value test would have been written
 * against the incorrect output and locked the bug in.
 */
class BtVarianceCorrectionTest {

    /** Symmetric BT information for K equal-strength models with n comparisons per pair. */
    private fun information(K: Int, n: Double): Array<DoubleArray> {
        val F = Array(K) { DoubleArray(K) }
        for (i in 0 until K) for (j in i + 1 until K) {
            val info = n * 0.25          // p = 0.5 at equal strength
            F[i][i] += info; F[j][j] += info
            F[i][j] -= info; F[j][i] -= info
        }
        return F
    }

    private fun invert(m: Array<DoubleArray>): Array<DoubleArray> {
        val K = m.size
        val a = Array(K) { i -> DoubleArray(2 * K) { j -> if (j < K) m[i][j] else if (j - K == i) 1.0 else 0.0 } }
        for (c in 0 until K) {
            var p = c
            for (r in c until K) if (kotlin.math.abs(a[r][c]) > kotlin.math.abs(a[p][c])) p = r
            val t = a[c]; a[c] = a[p]; a[p] = t
            val pv = a[c][c]
            for (j in 0 until 2 * K) a[c][j] /= pv
            for (r in 0 until K) if (r != c) {
                val f = a[r][c]
                if (f != 0.0) for (j in 0 until 2 * K) a[r][j] -= f * a[c][j]
            }
        }
        return Array(K) { i -> DoubleArray(K) { j -> a[i][j + K] } }
    }

    /**
     * F * 1 = 0, so 1 is an eigenvector of Fc = F + J with eigenvalue K. The 1-direction
     * block of Fc^-1 is therefore J/K^2 exactly — which is the quantity to subtract.
     */
    @Test
    fun `the all-ones block of the regularised inverse is J over K squared`() {
        for (K in intArrayOf(4, 8, 12, 16)) {
            val F = information(K, 40.0)
            // F is singular in the 1 direction.
            for (i in 0 until K) {
                assertEquals(0.0, F[i].sum(), 1e-9, "row $i of F should sum to 0 at K=$K")
            }
            val Fc = Array(K) { i -> DoubleArray(K) { j -> F[i][j] + 1.0 } }
            val inv = invert(Fc)
            // Fc^-1 * 1 = (1/K) * 1  =>  every row of the inverse sums to 1/K.
            for (i in 0 until K) {
                assertEquals(1.0 / K, inv[i].sum(), 1e-9,
                    "row $i of Fc^-1 should sum to 1/K at K=$K")
            }
            // Hence the rank-one component is J/K^2, not J/K.
            val correction = 1.0 / (K.toDouble() * K.toDouble())
            val v = inv[0][0] - correction
            assertTrue(v > 1e-6,
                "corrected variance at K=$K is $v — should be a real value, not the floor")
            val wrong = inv[0][0] - 1.0 / K
            assertTrue(wrong < v,
                "the old 1/K correction should be strictly smaller, confirming over-subtraction")
        }
    }

    /** The magnitude of the old error, so the size of the regression is on record. */
    @Test
    fun `the old correction over-subtracted by K minus one over K squared`() {
        for (K in intArrayOf(8, 12)) {
            val over = 1.0 / K - 1.0 / (K.toDouble() * K.toDouble())
            assertEquals((K - 1.0) / (K.toDouble() * K.toDouble()), over, 1e-12)
        }
        assertEquals(0.109375, 1.0 / 8 - 1.0 / 64, 1e-12)
    }
}
