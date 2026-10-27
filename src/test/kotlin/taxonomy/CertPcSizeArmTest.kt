package taxonomy

import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import taxonomy.model.Embedding
import taxonomy.model.EmbeddingSlice
import taxonomy.model.projectTo
import kotlin.math.sqrt

/**
 * CERT-PC-SIZE: the subsampled declared-site arm's new members of SeparationNullBySizeTest (pcsParseSites, pcsPopulation,
 * pcsC0Seed) on synthetic fixtures (no DB, no snapshot; runs in `test`). Every assertion is on a VALUE known by construction:
 *  - the site file parser keeps the sites in order of first appearance and refuses a wrong header, a malformed row, a
 *    duplicate (site, id) and an empty file;
 *  - a site's population is taken in the ROOT REGION's order whatever the file's order, and its groups are exactly the
 *    certPositiveControl arm's PC1 construction (re-stated here verbatim from the arm); an id outside the root refuses;
 *  - IDENTITY by construction: for the full root region, the declared statistic and the plain null through the new path
 *    (deflated = false, seeded by the root id) equal PC1's call (deflated = true) bit for bit, element for element;
 *  - a subsample listed in shuffled file order gives the same statistic and null as the same subsample in root order;
 *  - the C0 seed is siteNull's formula on base 20261002 and differs across the 15 registered subsample names.
 *
 * MUTANTS (2026-10-03, temporary edits to the pcs* members, bytes restored; this class run each time): see the commit
 * message's table (P1 population in file order, P2 categories unsorted, P3 duplicate check removed, P4 outside-root check
 * removed, P5 C0 seed base, P6 C0 seed without the site name, P7 sites sorted by name: 7 of 7 killed, control P0 survived).
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CertPcSizeArmTest {
    private val harness = SeparationNullBySizeTest()
    private var savedWidth = 0
    private val dim = 256
    private val reps = 12
    private val mcs = 55

    @BeforeAll fun pin() { savedWidth = EmbeddingSlice.width }
    @AfterAll fun restore() { EmbeddingSlice.width = savedWidth; tmpDir.deleteRecursively() }

    private val tmpDir = java.nio.file.Files.createTempDirectory("pcs_arm").toFile().apply { deleteOnExit() }
    private fun splitter() = harness.cpcSplitter(mcs, java.io.File(tmpDir, "corpus-${System.nanoTime()}.db").absolutePath)
    private fun unit(v: DoubleArray): DoubleArray { val n = sqrt(v.sumOf { it * it }); return DoubleArray(v.size) { v[it] / n } }

    /** 240 items in three planted clusters (80 each), ids "q000".."q239"; category = cluster name. */
    private val ids = (0 until 240).map { "q%03d".format(it) }
    private val catOf: Map<String, String> = ids.withIndex().associate { (i, id) -> id to listOf("law", "biology", "math")[i / 80] }
    private val embOf: Map<String, Embedding> by lazy {
        val r = java.util.Random(5)
        val cs = List(3) { unit(DoubleArray(dim) { r.nextGaussian() }) }
        ids.withIndex().associate { (i, id) ->
            val c = cs[i / 80]
            id to Embedding(rawText = id, distilledText = id, values = FloatArray(dim) { j -> (c[j] + 0.05 * r.nextGaussian()).toFloat() })
        }
    }
    /** A root region order that is NOT sorted (the arm's rootIds come from a DFS): ids reversed in blocks. */
    private val rootIds = ids.chunked(7).reversed().flatten()

    @Test
    fun `site file parser - order of first appearance and refusals`() {
        val txt = "site\tquery_id\tcategory\nIDENTITY\tq1\tlaw\r\nPS_n2_d2\tq2\tmath\nIDENTITY\tq2\tmath\nPS_n2_d2\tq1\tlaw\nPS_n1_d1\tq1\tlaw\n"
        val p = harness.pcsParseSites(txt)
        assertEquals(listOf("IDENTITY", "PS_n2_d2", "PS_n1_d1"), p.map { it.first })
        assertEquals(mapOf("q1" to "law", "q2" to "math"), p[0].second)
        assertEquals(listOf("q2", "q1"), p[1].second.keys.toList())
        for ((bad, needle) in listOf(
            "query_id\tcategory\tsrc\nq1\tlaw\tx\n" to "header",
            "site\tquery_id\tcategory\nIDENTITY\tq1\n" to "malformed",
            "site\tquery_id\tcategory\nIDENTITY\tq1\t\n" to "malformed",
            "site\tquery_id\tcategory\nIDENTITY\tq1\tlaw\nIDENTITY\tq1\tmath\n" to "duplicate",
            "site\tquery_id\tcategory\n" to "no rows")) {
            val e = assertThrows(IllegalArgumentException::class.java) { harness.pcsParseSites(bad) }
            assertTrue(e.message!!.contains(needle), "${e.message} !~ $needle")
        }
    }

    @Test
    fun `population - root order, PC1's groups, outside-root refusal`() {
        // the file lists a subsample in REVERSED id order; the population must follow rootIds
        val sub = ids.filter { it.last() in "02468" }.reversed()
        val m = LinkedHashMap<String, String>().apply { sub.forEach { put(it, catOf.getValue(it)) } }
        val (pids, cats, groups) = harness.pcsPopulation(rootIds, m)
        assertEquals(rootIds.filter { it in m }, pids)
        assertNotEquals(sub, pids)
        assertEquals(listOf("biology", "law", "math"), cats)
        // PC1's construction in the certPositiveControl arm, verbatim on the same population
        val catIdx = cats.withIndex().associate { it.value to it.index }
        val labels = IntArray(pids.size) { catIdx.getValue(m.getValue(pids[it])) }
        val pc1 = List(cats.size) { c -> labels.indices.filter { labels[it] == c } }
        assertEquals(pc1, groups)
        assertEquals(pids.size, groups.sumOf { it.size })
        assertTrue(groups[0].all { m.getValue(pids[it]) == "biology" })
        val e = assertThrows(IllegalArgumentException::class.java) { harness.pcsPopulation(rootIds, m + ("zz" to "law")) }
        assertTrue(e.message!!.contains("1 site ids are not in the member root region"), e.message)
    }

    @Test
    fun `identity by construction - the full root through the new path is PC1's call bit for bit`() {
        val sp = splitter(); val cap = harness.cpcNewCapture()
        // PC1's call (the certPositiveControl arm's root): population rootIds, groups by sorted category, deflated = true
        val cats = catOf.values.toSortedSet().toList()
        val catIdx = cats.withIndex().associate { it.value to it.index }
        val labels = IntArray(rootIds.size) { catIdx.getValue(catOf.getValue(rootIds[it])) }
        val pc1Groups = List(cats.size) { c -> labels.indices.filter { labels[it] == c } }
        val pc1 = harness.cpcDeclaredSite(sp, cap, "n00000001", 0, rootIds.map { embOf.getValue(it).projectTo(dim) },
            rootIds.map { embOf.getValue(it) }, pc1Groups, reps, deflated = true)
        // the new path: the file in sorted-id order, population re-ordered to rootIds, deflated = false, same seed id
        val m = LinkedHashMap<String, String>().apply { ids.forEach { put(it, catOf.getValue(it)) } }
        val (pids, _, groups) = harness.pcsPopulation(rootIds, m)
        val res = harness.cpcDeclaredSite(sp, cap, "n00000001", 0, pids.map { embOf.getValue(it).projectTo(dim) },
            pids.map { embOf.getValue(it) }, groups, reps, deflated = false)
        assertEquals(pc1.declared.toRawBits(), res.declared.toRawBits(), "declared ${pc1.declared} vs ${res.declared}")
        assertTrue(pc1.plain.contentEquals(res.plain), "plain nulls differ")
        assertEquals(pc1.kDeclared, res.kDeclared)
        assertEquals(0, res.kDeclared, "three planted clusters are certifiable: declared ${res.declared} max ${res.plain.max()}")
        assertEquals(null, res.defl)
    }

    @Test
    fun `a subsample in shuffled file order equals the same subsample in root order`() {
        val sp = splitter(); val cap = harness.cpcNewCapture()
        val sub = rootIds.filterIndexed { i, _ -> i % 2 == 0 }
        val shuffled = sub.shuffled(java.util.Random(9))
        fun run(order: List<String>): SeparationNullBySizeTest.CpcSite {
            val m = LinkedHashMap<String, String>().apply { order.forEach { put(it, catOf.getValue(it)) } }
            val (pids, _, groups) = harness.pcsPopulation(rootIds, m)
            return harness.cpcDeclaredSite(sp, cap, "PS_n120_d1", 0, pids.map { embOf.getValue(it).projectTo(dim) },
                pids.map { embOf.getValue(it) }, groups, reps, deflated = true)
        }
        val a = run(sub); val b = run(shuffled)
        assertEquals(a.declared.toRawBits(), b.declared.toRawBits())
        assertTrue(a.plain.contentEquals(b.plain) && a.defl!!.contentEquals(b.defl!!))
    }

    @Test
    fun `C0 seed - siteNull's formula on base 20261002, distinct across the 15 subsamples`() {
        assertEquals(20261002L + "PS_n486_d1".hashCode().toLong() * 2654435761L, harness.pcsC0Seed("PS_n486_d1"))
        assertEquals(harness.cpcSeed(20261002L, "PS_n441_d3", 0), harness.pcsC0Seed("PS_n441_d3"))
        val names = listOf(486, 441, 264).flatMap { n -> (1..5).map { d -> "PS_n${n}_d$d" } }
        assertEquals(15, names.map { harness.pcsC0Seed(it) }.toSet().size)
    }
}
