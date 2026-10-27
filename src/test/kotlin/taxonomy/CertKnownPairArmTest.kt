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
 * CERT-PC-K2-KNOWN: the merged-pair arm's new member of SeparationNullBySizeTest (kkpSiteError) and the merged-pair path through
 * the reused members (pcsParseSites -> kkpSiteError -> pcsPopulation -> cpcDeclaredSite without the deflated null ->
 * cpcRelabelNull with 2 groups) on synthetic fixtures (no DB, no snapshot; runs in `test`). Every assertion is on a VALUE known by
 * construction:
 *  - a well-formed KK site file (IDENTITY with 14 categories over the root; then STRONG, MID, EDGE blocks of 11 sites: the full
 *    pair site KK_<role>_n<N>_d0, KK_<role>_n486_d1..5, KK_<role>_n441_d1..5) is accepted (null);
 *  - each refusal returns its reason (16 cases: IDENTITY first / root set / 14 categories, the site count, the role order, a bad
 *    name, three labels in a full site, the draw order, a wrong size, a label that is not the id's IDENTITY category, one category
 *    only, an id outside the full site, a full site under 972, a category under 100, two roles on one pair);
 *  - KK-0 (i): declaredSiteStatistic on the fixed fixture of cert_pc_k2_known.fixture_vectors() equals the Python routine's XFIX
 *    (-0.04137677437400078) within 1e-12 (the readout's stage 0 is a Python copy of this routine);
 *  - two categories planted as two clusters certify (k = 0, deflated = false: no deflated arm) with C0 p95 below the null p95, the
 *    groups in sorted category order; the same population with the categories assigned at random does NOT (k > 14).
 *
 * MUTANTS (2026-10-03, temporary edits to kkpSiteError, bytes restored (sha256 checked), this class run each time; table in the
 * commit message): K1 IDENTITY-label check, K2 size check, K3 subset-of-full, K4 eligibility 972, K5 category >= 100, K6 distinct
 * pairs, K7 role order, K8 draw sequence, K9 site count, K10 full-site two categories, K11 subsample labels = the pair's, K12
 * IDENTITY 14 categories, K13 IDENTITY root set (each removed): 13 of 13 killed; control K0 (a comment edit) survived.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CertKnownPairArmTest {
    private val harness = SeparationNullBySizeTest()
    private var savedWidth = 0
    private val dim = 256
    private val reps = 40
    private val mcs = 55

    @BeforeAll fun pin() { savedWidth = EmbeddingSlice.width }
    @AfterAll fun restore() { EmbeddingSlice.width = savedWidth; tmpDir.deleteRecursively() }

    private val tmpDir = java.nio.file.Files.createTempDirectory("kkp_arm").toFile().apply { deleteOnExit() }
    private fun splitter() = harness.cpcSplitter(mcs, java.io.File(tmpDir, "corpus-${System.nanoTime()}.db").absolutePath)
    private fun unit(v: DoubleArray): DoubleArray { val n = sqrt(v.sumOf { it * it }); return DoubleArray(v.size) { v[it] / n } }

    /** Root: c00 1000, c01 500, c02 600, c03 50, c04..c13 10 each (2,250 ids, file order shuffled by blocks). */
    private val sizes = mapOf("c00" to 1000, "c01" to 500, "c02" to 600, "c03" to 50) + (4 until 14).associate { "c%02d".format(it) to 10 }
    private val identity: Map<String, String> = LinkedHashMap<String, String>().apply {
        var i = 0
        for ((c, n) in sizes) repeat(n) { put("q%04d".format(i++), c) }
    }
    private val rootIds = identity.keys.toList().chunked(7).reversed().flatten()
    private fun idsOf(c: String) = identity.filterValues { it == c }.keys.sorted()

    private fun file(sites: List<Pair<String, Map<String, String>>>): String =
        "site\tquery_id\tcategory\n" + sites.joinToString("") { (s, m) -> m.entries.joinToString("") { "$s\t${it.key}\t${it.value}\n" } }

    /** A role block: the full site of (a, b), then n486 d1..5, n441 d1..5 (subsample d = the first n/2 of a rotated by d, the
     *  rest from b). */
    private fun block(role: String, a: String, b: String): List<Pair<String, Map<String, String>>> {
        val full = (idsOf(a) + idsOf(b)).sorted().associateWith { identity.getValue(it) }
        val out = mutableListOf<Pair<String, Map<String, String>>>("KK_${role}_n${full.size}_d0" to full)
        for (n in listOf(486, 441)) for (d in 1..5) {
            val ia = idsOf(a).let { it.drop(d) + it.take(d) }.take(n / 2)
            val ib = idsOf(b).let { it.drop(d) + it.take(d) }.take(n - n / 2)
            out.add("KK_${role}_n${n}_d$d" to (ia + ib).sorted().associateWith { identity.getValue(it) })
        }
        return out
    }
    private fun good() = listOf("IDENTITY" to identity) + block("STRONG", "c00", "c01") + block("MID", "c00", "c02") + block("EDGE", "c01", "c02")
    private fun err(sites: List<Pair<String, Map<String, String>>>): String? = harness.kkpSiteError(harness.pcsParseSites(file(sites)), rootIds.toSet())
    private fun replace(sites: List<Pair<String, Map<String, String>>>, name: String, f: (Pair<String, Map<String, String>>) -> Pair<String, Map<String, String>>) =
        sites.map { if (it.first == name) f(it) else it }

    @Test
    fun `site check - accepted file and every refusal`() {
        assertNull(err(good()))
        val g = good()
        val s1 = "KK_STRONG_n486_d1"
        val cases = listOf(
            (listOf(g[1], g[0]) + g.drop(2)) to "the site file's first site is 'KK_STRONG_n1500_d0', not IDENTITY",
            replace(g, "IDENTITY") { it.first to it.second.filterKeys { k -> k != "q0000" } } to "IDENTITY covers 2249 ids; the member root region holds 2250 (sets differ)",
            replace(g, "IDENTITY") { it.first to it.second.mapValues { e -> if (e.value == "c13") "c12" else e.value } } to "IDENTITY holds 13 declared categories, not the registered 14",
            g.filter { it.first != "KK_EDGE_n441_d5" } to "the site file holds 32 KK sites, not 33 (3 pairs x (1 full + 2 sizes x 5 draws))",
            (listOf(g[0]) + block("MID", "c00", "c02") + block("STRONG", "c00", "c01") + block("EDGE", "c01", "c02")) to
                "site 'KK_MID_n1600_d0' where the STRONG full site KK_STRONG_n<n>_d0 is expected",
            replace(g, "KK_STRONG_n1500_d0") { "PS_n1500_d0" to it.second } to "site 'PS_n1500_d0' is not KK_<role>_n<n>_d<draw>",
            replace(g, "KK_STRONG_n1500_d0") { it.first to it.second + mapOf("q1700" to "c03") } to
                "site KK_STRONG_n1500_d0 holds the labels [c00, c01, c03], not exactly two declared categories",
            g.map { when (it.first) { s1 -> g.first { x -> x.first == "KK_STRONG_n486_d2" }; "KK_STRONG_n486_d2" -> g.first { x -> x.first == s1 }; else -> it } } to
                "site 'KK_STRONG_n486_d2' where 'KK_STRONG_n486_d1' is expected",
            replace(g, "KK_STRONG_n1500_d0") { "KK_STRONG_n1501_d0" to it.second } to "site KK_STRONG_n1501_d0 holds 1500 items, not 1501",
            replace(g, s1) { it.first to it.second.mapValues { e -> if (e.key == it.second.keys.first()) "c01" else e.value } } to
                "site $s1: id ${g.first { it.first == s1 }.second.keys.first()} is labelled 'c01', IDENTITY says 'c00'",
            replace(g, s1) { it.first to idsOf("c00").take(486).associateWith { "c00" } } to "site $s1 holds the labels [c00], not its pair's [c00, c01]",
            replace(g, "KK_STRONG_n1500_d0") { "KK_STRONG_n1499_d0" to it.second.filterKeys { k -> k != idsOf("c00")[1] } } to
                "site $s1 holds ids outside its pair's full site KK_STRONG_n1499_d0")
        for ((sites, want) in cases) assertEquals(want, err(sites))
        // a full site under 972 (c01 + c03 = 550) and a category under 100 (c00 1000 + c03 50 = 1050): EDGE re-pointed
        fun fullOnly(a: String, b: String): List<Pair<String, Map<String, String>>> {
            // subsamples drawn from a only would carry one label: give them both labels with all of b
            val full = (idsOf(a) + idsOf(b)).sorted().associateWith { identity.getValue(it) }
            val out = mutableListOf<Pair<String, Map<String, String>>>("KK_EDGE_n${full.size}_d0" to full)
            for (n in listOf(486, 441)) for (d in 1..5) {
                val ib = idsOf(b).take(minOf(idsOf(b).size, n / 2))
                val ia = idsOf(a).let { it.drop(d) + it.take(d) }.take(n - ib.size)
                out.add("KK_EDGE_n${n}_d$d" to (ia + ib).sorted().associateWith { identity.getValue(it) })
            }
            return out
        }
        assertEquals("full site KK_EDGE_n550_d0 holds 550 items, fewer than 972 (eligibility)",
            err(listOf(g[0]) + block("STRONG", "c00", "c01") + block("MID", "c00", "c02") + fullOnly("c01", "c03")))
        assertEquals("full site KK_EDGE_n1050_d0: c03 50 below 100 items (eligibility)",
            err(listOf(g[0]) + block("STRONG", "c00", "c01") + block("MID", "c00", "c02") + fullOnly("c00", "c03")))
        assertEquals("the three roles do not name three different pairs: [[c00, c01], [c00, c02], [c00, c01]]",
            err(listOf(g[0]) + block("STRONG", "c00", "c01") + block("MID", "c00", "c02") + block("EDGE", "c00", "c01")))
    }

    @Test
    fun `routine - the fixed fixture equals the Python routine (KK-0 i)`() {
        val embs = (0 until 12).map { i ->
            Embedding(rawText = "x$i", distilledText = "x$i", values = FloatArray(600) { j -> (((31 * i + 17 * j) % 101 - 50) / 50.0).toFloat() })
        }
        val x = harness.declaredSiteStatistic(listOf(embs.subList(0, 7), embs.subList(7, 12)), 512)
        assertTrue(kotlin.math.abs(x - (-0.04137677437400078)) <= 1e-12, "Kotlin routine $x vs the Python XFIX -0.04137677437400078")
    }

    @Test
    fun `merged pair path - planted categories certify with C0 comparable, random categories do not`() {
        val r = java.util.Random(17)
        val cs = mapOf("c01" to unit(DoubleArray(dim) { r.nextGaussian() }), "c02" to unit(DoubleArray(dim) { r.nextGaussian() }))
        val pairIds = (idsOf("c01").take(120) + idsOf("c02").take(120)).sorted()
        val emb = pairIds.associateWith { id ->
            val c = cs.getValue(identity.getValue(id))
            Embedding(rawText = id, distilledText = id, values = FloatArray(dim) { j -> (c[j] + 0.05 * r.nextGaussian()).toFloat() })
        }
        fun run(m: Map<String, String>, name: String): Triple<SeparationNullBySizeTest.CpcSite, List<String>, DoubleArray> {
            val (pids, cats, groups) = harness.pcsPopulation(rootIds, m)
            assertEquals(2, groups.size)
            val res = harness.cpcDeclaredSite(splitter(), harness.cpcNewCapture(), name, 0, pids.map { emb.getValue(it).projectTo(dim) },
                pids.map { emb.getValue(it) }, groups, reps, deflated = false)
            assertEquals(null, res.defl)
            assertEquals(-1, res.kDeflDeclared)
            val labels = IntArray(pids.size); groups.forEachIndexed { c, g -> g.forEach { labels[it] = c } }
            val c0 = harness.cpcRelabelNull(pids.map { emb.getValue(it) }, labels, cats.size, reps, harness.pcsC0Seed(name), dim)
            return Triple(res, cats, c0)
        }
        val (planted, cats, c0) = run(pairIds.associateWith { identity.getValue(it) }, "KK_MID_n240_d1")
        assertEquals(listOf("c01", "c02"), cats)
        assertEquals(0, planted.kDeclared, "planted: declared ${planted.declared} null max ${planted.plain.max()}")
        val np95 = planted.plain.sorted()[kotlin.math.ceil(0.95 * reps).toInt() - 1]
        val c0p95 = c0.sorted()[kotlin.math.ceil(0.95 * reps).toInt() - 1]
        assertTrue(c0p95 < np95, "C0 p95 $c0p95 must sit below the null p95 $np95")
        val rr = java.util.Random(5)
        val (rand, _, _) = run(pairIds.associateWith { if (rr.nextBoolean()) "c01" else "c02" }, "KK_MID_n240_d2")
        assertTrue(rand.kDeclared > 14, "random categories must not certify: k ${rand.kDeclared} of $reps, declared ${rand.declared}")
    }
}
