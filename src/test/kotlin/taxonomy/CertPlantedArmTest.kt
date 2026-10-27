package taxonomy

import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import taxonomy.model.Embedding
import taxonomy.model.EmbeddingSlice
import kotlin.math.sqrt

/**
 * CERT-PLANTED: the planted-input members of SeparationNullBySizeTest (cplSiteError, cplReadVectors, cplUnit, cplPlantCheck) and
 * the PL path through the reused members (pcsParseSites -> cplSiteError -> pcsPopulation -> cplReadVectors -> cplPlantCheck ->
 * cpcDeclaredSite with the planted rows) on synthetic fixtures (no DB, no snapshot; runs in `test`). Every assertion is on a VALUE
 * known by construction:
 *  - a well-formed PL site file is accepted (null); each refusal returns its reason (IDENTITY not first / not the root set / 13
 *    categories, no PL site, rows not contiguous, a bad name (a K2_ site, delta 3), an unregistered anchor, a wrong size, one
 *    label only, a third label, halves 3 apart, two deltas of one population with different halves, a population without D0);
 *  - the vector file round-trips big-endian floats in site-file row order and refuses a wrong size;
 *  - the PLANT CHECK accepts delta-0 rows equal to the cache rows, refuses a delta-0 row off by 1e-5, a non-unit row and a file
 *    without delta 0, and reports the max |diff|;
 *  - the PL path: a strongly planted shift (delta 20 x SD along a random axis, fixture strength) certifies (k = 0) against its own
 *    null; the same population at delta 0 (random halves of one cloud) does NOT (k > 14), and its declared statistic is the one
 *    cpcDeclaredSite computes from the planted rows (not the cache rows).
 *
 * MUTANTS (2026-10-04, temporary edits to the new members, bytes restored, this class run each time; table in the commit
 * message).
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CertPlantedArmTest {
    private val harness = SeparationNullBySizeTest()
    private var savedWidth = 0
    private val dim = 256
    private val reps = 40
    private val mcs = 55

    @BeforeAll fun pin() { savedWidth = EmbeddingSlice.width }
    @AfterAll fun restore() { EmbeddingSlice.width = savedWidth; tmpDir.deleteRecursively() }

    private val tmpDir = java.nio.file.Files.createTempDirectory("cpl_arm").toFile().apply { deleteOnExit() }
    private fun splitter() = harness.cpcSplitter(mcs, java.io.File(tmpDir, "corpus-${System.nanoTime()}.db").absolutePath)
    private fun unit(v: DoubleArray): DoubleArray { val n = sqrt(v.sumOf { it * it }); return DoubleArray(v.size) { v[it] / n } }

    private val rootIds = (0 until 280).map { "q%03d".format(it) }.chunked(9).reversed().flatten()
    private val cats14 = (0 until 14).map { "c%02d".format(it) }
    private val identity: Map<String, String> = rootIds.withIndex().associate { (i, id) -> id to cats14[i % 14] }

    private fun file(vararg sites: Pair<String, Map<String, String>>): String =
        "site\tquery_id\tcategory\n" + sites.joinToString("") { (s, m) -> m.entries.joinToString("") { "$s\t${it.key}\t${it.value}\n" } }

    private fun pl(n: Int, half: (Int) -> String = { if (it % 2 == 0) "hi" else "lo" }): Map<String, String> =
        LinkedHashMap<String, String>().apply { rootIds.take(n).forEachIndexed { i, id -> put(id, half(i)) } }

    private fun seq(txt: String) = txt.split("\n").drop(1).filter { it.isNotEmpty() }.map { it.substringBefore("\t") }
    private fun err(txt: String): String? = harness.cplSiteError(harness.pcsParseSites(txt), rootIds.toSet(), seq(txt))

    @Test
    fun `site check - accepted file and every refusal`() {
        assertNull(err(file("IDENTITY" to identity, "PL_math_n120_d1_D0" to pl(120), "PL_math_n120_d1_D2" to pl(120),
            "PL_economics_n11_d5_D0" to pl(11), "PL_economics_n11_d5_D12" to pl(11), "PL_economics_n11_d5_D10" to pl(11))))
        val good = "IDENTITY" to identity
        val cases = listOf(
            file("PL_math_n120_d1_D0" to pl(120), good) to "the site file's first site is 'PL_math_n120_d1_D0', not IDENTITY",
            file("IDENTITY" to identity.filterKeys { it != "q000" }, "PL_math_n120_d1_D0" to pl(120)) to "IDENTITY covers 279 ids; the member root region holds 280 (sets differ)",
            file("IDENTITY" to identity.mapValues { if (it.value == "c13") "c12" else it.value }, "PL_math_n120_d1_D0" to pl(120)) to "IDENTITY holds 13 declared categories, not the registered 14",
            file(good) to "the site file holds no PL site",
            file(good, "PL_math_n120_d1_D0" to pl(120), "PL_math_n10_d1_D0" to pl(10)) + "PL_math_n120_d1_D0\tq999\thi\n" to
                "the site file's rows are not contiguous per site (4 runs for 3 sites)",
            file(good, "K2_math_n120_d1" to pl(120)) to "site 'K2_math_n120_d1' is not PL_<anchor>_n<n>_d<draw>_D<delta> (delta 0 / 2 / 4 / 6 / 8 / 10 / 12)",
            file(good, "PL_math_n120_d1_D3" to pl(120)) to "site 'PL_math_n120_d1_D3' is not PL_<anchor>_n<n>_d<draw>_D<delta> (delta 0 / 2 / 4 / 6 / 8 / 10 / 12)",
            file(good, "PL_math_n120_d1_D0.5" to pl(120)) to "site 'PL_math_n120_d1_D0.5' is not PL_<anchor>_n<n>_d<draw>_D<delta> (delta 0 / 2 / 4 / 6 / 8 / 10 / 12)",
            file(good, "PL_math_n120_d1_D14" to pl(120)) to "site 'PL_math_n120_d1_D14' is not PL_<anchor>_n<n>_d<draw>_D<delta> (delta 0 / 2 / 4 / 6 / 8 / 10 / 12)",
            file(good, "PL_law_n120_d1_D0" to pl(120)) to "site PL_law_n120_d1_D0: anchor 'law' is not one of [economics, math, physics]",
            file(good, "PL_physics_n121_d1_D0" to pl(120)) to "site PL_physics_n121_d1_D0 holds 120 items, not 121",
            file(good, "PL_math_n120_d1_D0" to pl(120) { "hi" }) to "site PL_math_n120_d1_D0 holds the labels [hi], not exactly [hi, lo]",
            file(good, "PL_math_n120_d1_D0" to pl(120) { listOf("hi", "lo", "mid")[it % 3] }) to "site PL_math_n120_d1_D0 holds the labels [hi, lo, mid], not exactly [hi, lo]",
            file(good, "PL_math_n120_d1_D0" to pl(120) { if (it < 62) "hi" else "lo" }) to "site PL_math_n120_d1_D0: halves hi 62 / lo 58 are not a half-split",
            file(good, "PL_math_n120_d1_D0" to pl(120), "PL_math_n120_d1_D4" to pl(120) { if (it < 60) "hi" else "lo" }) to
                "site PL_math_n120_d1_D4: ids or halves differ from the other deltas of PL_math_n120_d1",
            file(good, "PL_math_n120_d1_D2" to pl(120)) to "population(s) without a delta-0 site: [PL_math_n120_d1]")
        for ((txt, want) in cases) assertEquals(want, err(txt))
        // one apart is a half-split (odd n)
        assertNull(err(file(good, "PL_math_n121_d1_D0" to pl(121) { if (it < 61) "hi" else "lo" })))
    }

    private fun bytesOf(rows: List<FloatArray>): ByteArray {
        val buf = java.nio.ByteBuffer.allocate(rows.sumOf { it.size } * 4)
        rows.forEach { r -> r.forEach { buf.putFloat(it) } }
        return buf.array()
    }

    @Test
    fun `vector file - big-endian round trip in site-file order and the size refusal`() {
        val txt = file("IDENTITY" to identity, "PL_math_n3_d1_D0" to pl(3), "PL_math_n3_d1_D6" to pl(3))
        val parsed = harness.pcsParseSites(txt)
        val rows = (0 until 6).map { r -> FloatArray(4) { j -> (r * 10 + j).toFloat() + 0.25f } }
        val b = bytesOf(rows)
        val got = harness.cplReadVectors(b, parsed, 4)
        assertEquals(listOf("PL_math_n3_d1_D0", "PL_math_n3_d1_D6"), got.keys.toList())
        val ids = rootIds.take(3)
        assertArrayEquals(rows[0], got.getValue("PL_math_n3_d1_D0").getValue(ids[0]))
        assertArrayEquals(rows[2], got.getValue("PL_math_n3_d1_D0").getValue(ids[2]))
        assertArrayEquals(rows[3], got.getValue("PL_math_n3_d1_D6").getValue(ids[0]))
        assertArrayEquals(rows[5], got.getValue("PL_math_n3_d1_D6").getValue(ids[2]))
        assertEquals(0x3E, b[0].toInt() and 0xFF, "row 0 float 0 = 0.25f must be written big-endian")
        val e = assertThrows(IllegalArgumentException::class.java) { harness.cplReadVectors(b.copyOf(b.size - 4), parsed, 4) }
        assertEquals("the planted-vector file holds 92 bytes, not 6 rows x 4 floats x 4 = 96", e.message)
        assertThrows(IllegalArgumentException::class.java) { harness.cplReadVectors(b + ByteArray(4), parsed, 4) }
    }

    @Test
    fun `plant check - accepts equal delta-0 rows and refuses each defect`() {
        val r = java.util.Random(5)
        val ids = rootIds.take(4)
        val raw = ids.associateWith { FloatArray(8) { r.nextGaussian().toFloat() } }
        val cache = raw.mapValues { harness.cplUnit(it.value) }
        fun unitF(f: FloatArray): FloatArray { val u = harness.cplUnit(f); return FloatArray(u.size) { u[it].toFloat() } }
        val d0 = ids.associateWith { unitF(raw.getValue(it)) }
        val d2 = ids.associateWith { id -> val v = raw.getValue(id).copyOf(); v[0] += 3f; unitF(v) }
        val ok = harness.cplPlantCheck(linkedMapOf("PL_math_n4_d1_D0" to d0, "PL_math_n4_d1_D2" to d2), cache)
        assertNull(ok.error)
        assertEquals(1, ok.d0Sites)
        assertTrue(ok.d0MaxDiff <= 1e-7, "float rounding only: ${ok.d0MaxDiff}")
        // cplUnit = loadVectorsById's rule
        assertArrayEquals(doubleArrayOf(0.6, 0.8), harness.cplUnit(floatArrayOf(3f, 4f)), 1e-15)
        assertArrayEquals(doubleArrayOf(0.0, 0.0), harness.cplUnit(floatArrayOf(0f, 0f)), 0.0)
        // a delta-0 row off by 1e-5 in one coordinate (renormalised) -> refused
        val bad = d0.toMutableMap()
        bad[ids[2]] = unitF(raw.getValue(ids[2]).copyOf().also { it[3] += 1e-4f * (1 + kotlin.math.abs(it[3])) * 10 })
        val e1 = harness.cplPlantCheck(linkedMapOf("PL_math_n4_d1_D0" to bad), cache)
        assertTrue(e1.error!!.startsWith("site PL_math_n4_d1_D0 id ${ids[2]}: the delta-0 row differs from the cache's slice vector"), e1.error)
        // the D2 rows are NOT compared with the cache (they differ by construction): a D2 site alone has no anchor
        val e2 = harness.cplPlantCheck(linkedMapOf("PL_math_n4_d1_D2" to d2), cache)
        assertEquals("no delta-0 site: the PLANT CHECK has no anchor", e2.error)
        // a non-unit planted row (in any site) -> refused
        val nonUnit = d2.toMutableMap(); nonUnit[ids[1]] = raw.getValue(ids[1])
        val e3 = harness.cplPlantCheck(linkedMapOf("PL_math_n4_d1_D0" to d0, "PL_math_n4_d1_D2" to nonUnit), cache)
        assertTrue(e3.error!!.startsWith("site PL_math_n4_d1_D2 id ${ids[1]}: planted row norm"), e3.error)
        // a delta-0 id without a cache vector -> refused
        val e4 = harness.cplPlantCheck(linkedMapOf("PL_math_n4_d1_D0" to d0), cache - ids[0])
        assertEquals("site PL_math_n4_d1_D0 id ${ids[0]}: no cache vector for the PLANT CHECK", e4.error)
    }

    @Test
    fun `PL path - a strong planted shift certifies, delta 0 does not, the statistic is read from the planted rows`() {
        EmbeddingSlice.width = dim
        val n = 240
        val r = java.util.Random(17)
        val c = unit(DoubleArray(dim) { r.nextGaussian() })
        val ids = rootIds.take(n)
        val base = ids.associateWith { DoubleArray(dim) { j -> c[j] + 0.05 * r.nextGaussian() } }
        fun unitF(v: DoubleArray): FloatArray { val u = unit(v); return FloatArray(dim) { u[it].toFloat() } }
        val x = ids.associateWith { id -> unit(base.getValue(id)) }
        val u = unit(DoubleArray(dim) { r.nextGaussian() })
        // exact half-split: the first n/2 ids of a seeded shuffle are hi
        val hiSet = ids.shuffled(java.util.Random(23)).take(n / 2).toSet()
        val halves = LinkedHashMap<String, String>().apply { ids.forEach { put(it, if (it in hiSet) "hi" else "lo") } }
        val proj = ids.map { id -> x.getValue(id).zip(u).sumOf { (a, b) -> a * b } }
        val mean = proj.average()
        val s = sqrt(proj.sumOf { (it - mean) * (it - mean) } / n)
        fun plant(delta: Double) = ids.associateWith { id ->
            val sign = if (halves.getValue(id) == "hi") 1.0 else -1.0
            unitF(DoubleArray(dim) { j -> x.getValue(id)[j] + sign * delta * s * u[j] })
        }
        val txt = file("IDENTITY" to identity, "PL_math_n240_d1_D0" to halves, "PL_math_n240_d1_D2" to halves)
        val parsed = harness.pcsParseSites(txt)
        assertNull(harness.cplSiteError(parsed, rootIds.toSet(), seq(txt)))
        val p0 = plant(0.0); val p20 = plant(20.0)
        val bytes = bytesOf(ids.map { p0.getValue(it) } + ids.map { p20.getValue(it) })
        val planted = harness.cplReadVectors(bytes, parsed, dim)
        val cache = ids.associateWith { harness.cplUnit(unitF(base.getValue(it))) }
        assertNull(harness.cplPlantCheck(planted, cache).error)
        fun site(name: String): SeparationNullBySizeTest.CpcSite {
            val m = parsed.first { it.first == name }.second
            val (pids, cats, groups) = harness.pcsPopulation(rootIds, m)
            assertEquals(listOf("hi", "lo"), cats)
            assertEquals(listOf(n / 2, n / 2), groups.map { it.size })
            val rows = planted.getValue(name)
            return harness.cpcDeclaredSite(splitter(), harness.cpcNewCapture(), name, 0, pids.map { harness.cplUnit(rows.getValue(it)) },
                pids.map { Embedding(rawText = "$name#$it", distilledText = "$name#$it", values = rows.getValue(it)) }, groups, reps, deflated = false)
        }
        val strong = site("PL_math_n240_d1_D2")
        assertEquals(0, strong.kDeclared, "planted delta 20: declared ${strong.declared} null max ${strong.plain.max()}")
        assertTrue(strong.declared > 0.3, "between share ~ 400 / (256 + 400): ${strong.declared}")
        val zero = site("PL_math_n240_d1_D0")
        assertTrue(zero.kDeclared > 14, "delta 0 (random halves) must not certify: k ${zero.kDeclared} of $reps, declared ${zero.declared}")
        assertTrue(kotlin.math.abs(zero.declared) < 0.01, "random halves: declared ${zero.declared}")
        // the declared statistic is computed from the planted rows: the routine on the planted D2 rows gives it bit for bit
        val m2 = parsed.first { it.first == "PL_math_n240_d1_D2" }.second
        val (pids2, _, g2) = harness.pcsPopulation(rootIds, m2)
        val rows2 = planted.getValue("PL_math_n240_d1_D2")
        val direct = harness.declaredSiteStatistic(g2.map { g -> g.map { Embedding(rawText = "z", distilledText = "z", values = rows2.getValue(pids2[it])) } }, dim)
        assertEquals(direct, strong.declared)
    }
}
