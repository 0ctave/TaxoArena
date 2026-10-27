package taxonomy

import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotSame
import org.junit.jupiter.api.Test
import taxonomy.utils.StatisticsUtils
import kotlin.math.sqrt

/**
 * Bit-equality guard for the performance edits to [StatisticsUtils.pcaProject]
 * (docs/perf_review_2026-09-09.md items #2 and #4): the in-place deflation and the
 * single-slot memo must return exactly what the historical implementation returned.
 * [referencePcaProject] is that historical implementation, copied verbatim.
 */
class PcaProjectEquivalenceTest {

    private fun referencePcaProject(vectors: List<DoubleArray>, k: Int, dropTop: Int = 0, whiten: Boolean = false): List<DoubleArray> {
        val n = vectors.size
        if (n == 0) return emptyList()
        val d = vectors[0].size
        if (d == 0) return vectors
        val skip = dropTop.coerceIn(0, d - 1)
        val keep = k.coerceAtMost(d - skip)
        val mean = DoubleArray(d)
        for (v in vectors) {
            for (i in 0 until d) {
                mean[i] += v[i] / n
            }
        }
        val centered = vectors.map { v -> DoubleArray(d) { i -> v[i] - mean[i] } }
        val components = mutableListOf<DoubleArray>()
        var residual = centered.map { it.copyOf() }
        repeat(skip + keep) { comp ->
            val rng = java.util.Random(0x5EEDL + comp * 7919L + d * 104729L + n * 31L)
            var vec = DoubleArray(d) { rng.nextDouble() - 0.5 }
            repeat(30) {
                val proj = DoubleArray(d)
                for (row in residual) {
                    var dot = 0.0
                    for (i in 0 until d) {
                        dot += row[i] * vec[i]
                    }
                    for (i in 0 until d) {
                        proj[i] += dot * row[i]
                    }
                }
                for (c in components) {
                    var dot = 0.0
                    for (i in 0 until d) {
                        dot += proj[i] * c[i]
                    }
                    for (i in 0 until d) {
                        proj[i] -= dot * c[i]
                    }
                }
                var normSq = 0.0
                for (i in 0 until d) {
                    normSq += proj[i] * proj[i]
                }
                val norm = sqrt(normSq)
                vec = if (norm > 1e-10) DoubleArray(d) { proj[it] / norm } else proj
            }
            components.add(vec)
            residual = residual.map { row ->
                var dot = 0.0
                for (i in 0 until d) {
                    dot += row[i] * vec[i]
                }
                DoubleArray(d) { i -> row[i] - dot * vec[i] }
            }
        }
        val kept = components.subList(skip, skip + keep)
        val raw = centered.map { row ->
            DoubleArray(keep) { j ->
                val c = kept[j]
                var dot = 0.0
                for (i in 0 until d) {
                    dot += row[i] * c[i]
                }
                dot
            }
        }
        val scale = DoubleArray(keep) { 1.0 }
        if (whiten) {
            for (j in 0 until keep) {
                var ss = 0.0
                for (row in raw) ss += row[j] * row[j]
                val sd = sqrt(ss / n)
                if (sd > 1e-10) scale[j] = 1.0 / sd
            }
        }
        return raw.map { proj ->
            for (j in 0 until keep) proj[j] *= scale[j]
            var normSq = 0.0
            for (i in 0 until keep) {
                normSq += proj[i] * proj[i]
            }
            val norm = sqrt(normSq)
            if (norm > 1e-10) DoubleArray(keep) { proj[it] / norm } else proj
        }
    }

    private fun cloud(n: Int, d: Int, seed: Long): List<DoubleArray> {
        val rng = java.util.Random(seed)
        // anisotropic: a few strong directions plus noise, unit-normalised like MRL slices
        val axes = List(4) { DoubleArray(d) { rng.nextGaussian() } }
        return List(n) {
            val v = DoubleArray(d) { rng.nextGaussian() * 0.05 }
            for (a in axes) { val w = rng.nextGaussian(); for (i in 0 until d) v[i] += w * a[i] }
            val norm = sqrt(v.sumOf { it * it }); DoubleArray(d) { v[it] / norm }
        }
    }

    private fun assertSame(expected: List<DoubleArray>, actual: List<DoubleArray>) {
        assertEquals(expected.size, actual.size)
        for (i in expected.indices) assertArrayEquals(expected[i], actual[i], 0.0)
    }

    @Test
    fun `in-place deflation is bit-identical to the historical implementation`() {
        for ((n, d, k, drop, whiten) in listOf(
            listOf(120, 64, 32, 0, false), listOf(300, 128, 64, 0, false), listOf(300, 128, 64, 2, false),
            listOf(150, 96, 32, 1, true), listOf(40, 16, 8, 0, false))) {
            val x = cloud(n as Int, d as Int, seed = 1000L + n)
            val input = x.map { it.copyOf() }
            assertSame(referencePcaProject(x, k as Int, drop as Int, whiten as Boolean),
                       StatisticsUtils.pcaProject(x, k, drop, whiten))
            assertSame(input, x) // the caller's vectors are never touched
        }
    }

    @Test
    fun `memo hits only on exact content and returns fresh copies`() {
        val x = cloud(200, 64, seed = 7)
        val a = StatisticsUtils.pcaProjectMemo(x, 32)
        val b = StatisticsUtils.pcaProjectMemo(x.map { it.copyOf() }, 32)   // same content, other objects
        assertSame(a, b)
        assertNotSame(a[0], b[0])
        b[0][0] = 42.0                                                      // mutate a returned row
        assertSame(a, StatisticsUtils.pcaProjectMemo(x, 32))                // memo unaffected
        assertSame(referencePcaProject(x, 32, 1, false), StatisticsUtils.pcaProjectMemo(x, 32, 1, false)) // different params -> recompute
        val y = x.map { it.copyOf() }; y[17][3] += 1e-12                    // one element differs
        assertSame(referencePcaProject(y, 32), StatisticsUtils.pcaProjectMemo(y, 32))
        val z = x.map { it.copyOf() }; z[17][3] += 1e-12                    // equals y -> hit, same result
        assertSame(referencePcaProject(y, 32), StatisticsUtils.pcaProjectMemo(z, 32))
    }
}
