package taxonomy

import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import taxonomy.model.Embedding
import taxonomy.model.EmbeddingSlice
import taxonomy.model.projectTo
import kotlin.math.sqrt

/**
 * CERT-PC-K2: the declared two-family arm's new member of SeparationNullBySizeTest (pk2SiteError) and the K2 path through the
 * reused members (pcsParseSites -> pk2SiteError -> pcsPopulation -> cpcDeclaredSite -> cpcRelabelNull with 2 groups) on
 * synthetic fixtures (no DB, no snapshot; runs in `test`). Every assertion is on a VALUE known by construction:
 *  - a well-formed K2 site file (IDENTITY with 14 categories over the root, then K2_<anchor>_n<n>_d<draw> sites holding exactly
 *    the families 'added' / 'ori_mmlu') is accepted (null);
 *  - each refusal returns its reason: IDENTITY not first, IDENTITY not the root set, IDENTITY with 13 categories, no K2 site,
 *    a bad name (a PS_ site of CERT-PC-SIZE), an unregistered anchor, a wrong size, one family only, a third label;
 *  - a K2 site whose two families are two planted clusters certifies (k = 0) with C0 p95 below the null p95 and groups ordered
 *    'added' then 'ori_mmlu'; the same population with the families assigned at random does NOT (k > 14).
 *
 * MUTANTS (2026-10-03, temporary edits to pk2SiteError, bytes restored, this class run each time; table in the commit message):
 * K1 families check removed, K2 size check removed, K3 anchor check removed, K4 14-category IDENTITY check removed, K5 name regex
 * accepts PS_, K6 root-set check removed, K7 empty-K2 check removed, K8 a subset of the families accepted: 8 of 8 killed; control
 * K0 survived.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CertPcK2ArmTest {
    private val harness = SeparationNullBySizeTest()
    private var savedWidth = 0
    private val dim = 256
    private val reps = 40
    private val mcs = 55

    @BeforeAll fun pin() { savedWidth = EmbeddingSlice.width }
    @AfterAll fun restore() { EmbeddingSlice.width = savedWidth; tmpDir.deleteRecursively() }

    private val tmpDir = java.nio.file.Files.createTempDirectory("pk2_arm").toFile().apply { deleteOnExit() }
    private fun splitter() = harness.cpcSplitter(mcs, java.io.File(tmpDir, "corpus-${System.nanoTime()}.db").absolutePath)
    private fun unit(v: DoubleArray): DoubleArray { val n = sqrt(v.sumOf { it * it }); return DoubleArray(v.size) { v[it] / n } }

    /** 280 root ids; the 14 declared categories cycle; a K2 site = the first 160 ids, families by index parity of block. */
    private val rootIds = (0 until 280).map { "q%03d".format(it) }.chunked(9).reversed().flatten()
    private val cats14 = (0 until 14).map { "c%02d".format(it) }
    private val identity: Map<String, String> = rootIds.withIndex().associate { (i, id) -> id to cats14[i % 14] }

    private fun file(vararg sites: Pair<String, Map<String, String>>): String =
        "site\tquery_id\tcategory\n" + sites.joinToString("") { (s, m) -> m.entries.joinToString("") { "$s\t${it.key}\t${it.value}\n" } }

    private fun k2(n: Int, fam: (Int) -> String = { if (it % 2 == 0) "ori_mmlu" else "added" }): Map<String, String> =
        LinkedHashMap<String, String>().apply { rootIds.take(n).forEachIndexed { i, id -> put(id, fam(i)) } }

    private fun err(txt: String): String? = harness.pk2SiteError(harness.pcsParseSites(txt), rootIds.toSet())

    @Test
    fun `site check - accepted file and every refusal`() {
        assertNull(err(file("IDENTITY" to identity, "K2_math_n120_d1" to k2(120), "K2_economics_n10_d5" to k2(10))))
        val cases = listOf(
            file("K2_math_n120_d1" to k2(120), "IDENTITY" to identity) to "the site file's first site is 'K2_math_n120_d1', not IDENTITY",
            file("IDENTITY" to identity.filterKeys { it != "q000" }, "K2_math_n120_d1" to k2(120)) to "IDENTITY covers 279 ids; the member root region holds 280 (sets differ)",
            file("IDENTITY" to identity.mapValues { if (it.value == "c13") "c12" else it.value }, "K2_math_n120_d1" to k2(120)) to "IDENTITY holds 13 declared categories, not the registered 14",
            file("IDENTITY" to identity) to "the site file holds no K2 site",
            file("IDENTITY" to identity, "PS_n120_d1" to k2(120)) to "site 'PS_n120_d1' is not K2_<anchor>_n<n>_d<draw>",
            file("IDENTITY" to identity, "K2_law_n120_d1" to k2(120)) to "site K2_law_n120_d1: anchor 'law' is not one of [economics, math, physics]",
            file("IDENTITY" to identity, "K2_physics_n121_d1" to k2(120)) to "site K2_physics_n121_d1 holds 120 items, not 121",
            file("IDENTITY" to identity, "K2_math_n120_d1" to k2(120) { "added" }) to "site K2_math_n120_d1 holds the labels [added], not exactly [added, ori_mmlu]",
            file("IDENTITY" to identity, "K2_math_n120_d1" to k2(120) { listOf("added", "ori_mmlu", "stemez")[it % 3] }) to
                "site K2_math_n120_d1 holds the labels [added, ori_mmlu, stemez], not exactly [added, ori_mmlu]")
        for ((txt, want) in cases) assertEquals(want, err(txt))
    }

    @Test
    fun `K2 path - planted two families certify with C0 comparable, random families do not`() {
        val n = 240
        val r = java.util.Random(11)
        val cs = List(2) { unit(DoubleArray(dim) { r.nextGaussian() }) }
        val ids = rootIds.take(n)
        // planted: family = cluster; cluster by position in the K2 list
        val emb = ids.withIndex().associate { (i, id) ->
            val c = cs[i % 2]
            id to Embedding(rawText = id, distilledText = id, values = FloatArray(dim) { j -> (c[j] + 0.05 * r.nextGaussian()).toFloat() })
        }
        fun run(m: Map<String, String>, name: String): Triple<SeparationNullBySizeTest.CpcSite, List<String>, DoubleArray> {
            val parsed = harness.pcsParseSites(file("IDENTITY" to identity, name to m))
            assertNull(harness.pk2SiteError(parsed, rootIds.toSet()))
            val (pids, cats, groups) = harness.pcsPopulation(rootIds, parsed[1].second)
            assertEquals(2, groups.size)
            val res = harness.cpcDeclaredSite(splitter(), harness.cpcNewCapture(), name, 0, pids.map { emb.getValue(it).projectTo(dim) },
                pids.map { emb.getValue(it) }, groups, reps, deflated = true)
            val labels = IntArray(pids.size); groups.forEachIndexed { c, g -> g.forEach { labels[it] = c } }
            val c0 = harness.cpcRelabelNull(pids.map { emb.getValue(it) }, labels, cats.size, reps, harness.pcsC0Seed(name), dim)
            return Triple(res, cats, c0)
        }
        val (planted, cats, c0) = run(k2(n), "K2_math_n240_d1")
        assertEquals(listOf("added", "ori_mmlu"), cats)
        assertEquals(0, planted.kDeclared, "planted: declared ${planted.declared} null max ${planted.plain.max()}")
        val np95 = planted.plain.sorted()[kotlin.math.ceil(0.95 * reps).toInt() - 1]
        val c0p95 = c0.sorted()[kotlin.math.ceil(0.95 * reps).toInt() - 1]
        assertTrue(c0p95 < np95, "C0 p95 $c0p95 must sit below the null p95 $np95")
        val rr = java.util.Random(3)
        val randomFam = k2(n) { if (rr.nextBoolean()) "ori_mmlu" else "added" }
        val (rand, _, _) = run(randomFam, "K2_math_n240_d2")
        assertTrue(rand.kDeclared > 14, "random families must not certify: k ${rand.kDeclared} of $reps, declared ${rand.declared}")
    }
}
