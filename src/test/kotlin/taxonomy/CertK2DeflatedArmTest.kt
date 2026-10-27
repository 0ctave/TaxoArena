package taxonomy

import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
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
 * CERT-K2-DEFLATED: the new members of SeparationNullBySizeTest (dflSiteError, dflSeedBase, dflDeflatedSite) on synthetic
 * fixtures (no DB, no snapshot; runs in `test`). Every assertion is on a VALUE known by construction:
 *  - a well-formed 87-site file (IDENTITY; 33 KK sites; 33 K2 sites economics / math / physics, each full d0 + n486 d1..5 + n441
 *    d1..5; 20 NC sites NC_STRONG_n486_s1..10 / NC_math_n486_s1..10) is accepted (null);
 *  - each refusal returns its exact reason (15 cases: IDENTITY first, the site count, a KK-block error through kkpSiteError, a
 *    K2-block error through pk2SiteError, the anchor order, a full site under 486, the draw order, an id of another category, a
 *    subsample outside its full site, an NC name, NC ids not the source's, NC labels, NC not size-matched, NC = the source
 *    partition, NC = its complement);
 *  - (amended 26605924) dflEcError: the 87 sites followed by the 10 elongation-cut controls EC_STRONG / EC_MID_n486_d1..5 are
 *    accepted; 9 refusals with exact messages (count 86 / 95, an error of the first 87, name, ids, labels, pc_lo under half, the
 *    declared partition, its complement);
 *  - the fresh seed: dflSeedBase() = 20261004; dflDeflatedSite's replicates EQUAL cpcSiteArm(tag SNDF, 20261004, the site name) on the
 *    deflated rows and DIFFER from cpcDeclaredSite's deflated arm (siteNull's 88820260908, whose replicates are on disk), and it
 *    deflates exactly 1 dim for 2 groups;
 *  - ties count: identical rows give declared 0.0 and all-zero replicates, so k = reps (">=", the registration's);
 *  - two planted clusters certify under the deflated null (k = 0) while a random relabelling of the same population does not
 *    (k > 14).
 *
 * MUTANTS (2026-10-04, temporary edits to the new members, bytes restored (sha256 checked), this class run each time; the table is
 * in the commit message).
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CertK2DeflatedArmTest {
    private val harness = SeparationNullBySizeTest()
    private var savedWidth = 0
    private val dim = 256
    private val reps = 40
    private val mcs = 55

    @BeforeAll fun pin() { savedWidth = EmbeddingSlice.width }
    @AfterAll fun restore() { EmbeddingSlice.width = savedWidth; tmpDir.deleteRecursively() }

    private val tmpDir = java.nio.file.Files.createTempDirectory("dfl_arm").toFile().apply { deleteOnExit() }
    private fun splitter() = harness.cpcSplitter(mcs, java.io.File(tmpDir, "corpus-${System.nanoTime()}.db").absolutePath)
    private fun unit(v: DoubleArray): DoubleArray { val n = sqrt(v.sumOf { it * it }); return DoubleArray(v.size) { v[it] / n } }

    private val sizes = linkedMapOf("chemistry" to 500, "economics" to 520, "law" to 500, "math" to 800, "physics" to 600) +
        (5 until 14).associate { "c%02d".format(it) to 10 }
    private val identity: Map<String, String> = LinkedHashMap<String, String>().apply {
        var i = 0
        for ((c, n) in sizes) repeat(n) { put("q%04d".format(i++), c) }
    }
    private val rootIds = identity.keys.toList().chunked(7).reversed().flatten()
    private fun idsOf(c: String) = identity.filterValues { it == c }.keys.sorted()
    private fun rot(xs: List<String>, d: Int) = xs.drop(d) + xs.take(d)

    private fun file(sites: List<Pair<String, Map<String, String>>>): String =
        "site\tquery_id\tcategory\n" + sites.joinToString("") { (s, m) -> m.entries.joinToString("") { "$s\t${it.key}\t${it.value}\n" } }

    private fun kkBlock(role: String, a: String, b: String): List<Pair<String, Map<String, String>>> {
        val full = (idsOf(a) + idsOf(b)).sorted().associateWith { identity.getValue(it) }
        val out = mutableListOf<Pair<String, Map<String, String>>>("KK_${role}_n${full.size}_d0" to full)
        for (n in listOf(486, 441)) for (d in 1..5) {
            val ia = rot(idsOf(a), d).take(n / 2)
            val ib = rot(idsOf(b), d).take(n - n / 2)
            out.add("KK_${role}_n${n}_d$d" to (ia + ib).sorted().associateWith { identity.getValue(it) })
        }
        return out
    }

    /** family of an anchor id: even index in the sorted anchor list -> added, odd -> ori_mmlu */
    private fun fam(a: String): Map<String, String> = idsOf(a).withIndex().associate { it.value to if (it.index % 2 == 0) "added" else "ori_mmlu" }

    private fun k2Block(a: String, fullIds: List<String> = idsOf(a)): List<Pair<String, Map<String, String>>> {
        val f = fam(a)
        val out = mutableListOf<Pair<String, Map<String, String>>>("K2_${a}_n${fullIds.size}_d0" to fullIds.sorted().associateWith { f.getValue(it) })
        for (n in listOf(486, 441)) for (d in 1..5) out.add("K2_${a}_n${n}_d$d" to rot(fullIds, d).take(n).sorted().associateWith { f.getValue(it) })
        return out
    }

    private fun relabel(src: Map<String, String>, seed: Int): Map<String, String> {
        val ids = src.keys.sorted()
        val first = src.values.toSortedSet().first()
        val lab = ids.map { src.getValue(it) }.toMutableList()
        java.util.Collections.shuffle(lab, java.util.Random(seed.toLong()))
        return ids.withIndex().associate { it.value to if (lab[it.index] == first) "rel_a" else "rel_b" }
    }

    private fun good(): List<Pair<String, Map<String, String>>> {
        val kk = kkBlock("STRONG", "chemistry", "law") + kkBlock("MID", "law", "math") + kkBlock("EDGE", "economics", "physics")
        val k2 = k2Block("economics") + k2Block("math") + k2Block("physics")
        val sS = kk.first { it.first == "KK_STRONG_n486_d1" }.second
        val sM = k2.first { it.first == "K2_math_n486_d1" }.second
        val nc = (1..10).map { "NC_STRONG_n486_s$it" to relabel(sS, it) } + (1..10).map { "NC_math_n486_s$it" to relabel(sM, it) }
        return listOf("IDENTITY" to identity) + kk + k2 + nc
    }

    private fun err(sites: List<Pair<String, Map<String, String>>>): String? = harness.dflSiteError(harness.pcsParseSites(file(sites)), rootIds.toSet())
    private fun replace(sites: List<Pair<String, Map<String, String>>>, name: String, f: (Pair<String, Map<String, String>>) -> Pair<String, Map<String, String>>) =
        sites.map { if (it.first == name) f(it) else it }
    private fun swap(sites: List<Pair<String, Map<String, String>>>, x: String, y: String) =
        sites.map { when (it.first) { x -> sites.first { s -> s.first == y }; y -> sites.first { s -> s.first == x }; else -> it } }

    @Test
    fun `site check - accepted file and every refusal`() {
        val g = good()
        assertEquals(87, g.size)
        assertNull(err(g))
        val sS = g.first { it.first == "KK_STRONG_n486_d1" }.second
        val chemIds = sS.filterValues { it == "chemistry" }.keys
        val m1 = "K2_math_n486_d1"
        val mathIds = g.first { it.first == m1 }.second.keys.sorted()
        val reorder = g.subList(0, 34) + k2Block("economics") + k2Block("physics") + k2Block("math") + g.subList(67, 87)
        val econShort = idsOf("economics").take(480)
        val cases = listOf(
            (listOf(g[1], g[0]) + g.drop(2)) to "the site file's first site is 'KK_STRONG_n1000_d0', not IDENTITY",
            g.filter { it.first != "NC_math_n486_s10" } to "the site file holds 85 sites after IDENTITY, not 86 (33 KK + 33 K2 + 20 NC)",
            replace(g, "KK_MID_n1300_d0") { "KK_MID_n1301_d0" to it.second } to "KK block: site KK_MID_n1301_d0 holds 1300 items, not 1301",
            replace(g, m1) { it.first to it.second.mapValues { "added" } } to "K2 block: site $m1 holds the labels [added], not exactly [added, ori_mmlu]",
            reorder to "site 'K2_physics_n600_d0' where the math full site K2_math_n<N>_d0 is expected",
            replace(g, "K2_economics_n520_d0") { "K2_economics_n480_d0" to it.second.filterKeys { k -> k in econShort } } to
                "full site K2_economics_n480_d0 holds 480 items, fewer than 486",
            swap(g, m1, "K2_math_n486_d2") to "site 'K2_math_n486_d2' where '$m1' is expected",
            replace(g, m1) { it.first to (it.second - mathIds[0]) + mapOf(idsOf("law")[0] to "added") } to
                "site $m1: id ${idsOf("law")[0]} is IDENTITY category 'law', not the anchor 'math'",
            replace(g, "K2_math_n800_d0") { "K2_math_n799_d0" to (it.second - mathIds[0]) } to "site $m1 holds ids outside its anchor's full site K2_math_n799_d0",
            replace(g, "NC_STRONG_n486_s3") { "NC_STRONG_n486_s11" to it.second } to "site 'NC_STRONG_n486_s11' where 'NC_STRONG_n486_s3' is expected",
            replace(g, "NC_math_n486_s2") { it.first to relabel(g.first { s -> s.first == "K2_math_n486_d2" }.second, 2) } to
                "site NC_math_n486_s2 does not hold exactly the ids of its source K2_math_n486_d1",
            replace(g, "NC_math_n486_s2") { it.first to it.second.mapValues { e -> if (e.key == mathIds[0]) "rel_c" else e.value } } to
                "site NC_math_n486_s2 holds the labels [rel_a, rel_b, rel_c], not exactly [rel_a, rel_b]",
            replace(g, "NC_STRONG_n486_s1") { it.first to sS.keys.associateWith { "rel_b" }.mapValues { e -> if (e.key in chemIds.drop(1)) "rel_a" else e.value } } to
                "site NC_STRONG_n486_s1: rel_a holds ${chemIds.size - 1} ids, its source's 'chemistry' ${chemIds.size} (not size-matched)",
            replace(g, "NC_STRONG_n486_s1") { it.first to sS.mapValues { e -> if (e.value == "chemistry") "rel_a" else "rel_b" } } to
                "site NC_STRONG_n486_s1 reproduces its source's declared partition")
        for ((sites, want) in cases) assertEquals(want, err(sites))
        // the complement (rel_a = the law ids) is size-matched here because the fixture's STRONG d1 holds 243 / 243
        assertEquals(chemIds.size, sS.size - chemIds.size)
        assertEquals("site NC_STRONG_n486_s1 reproduces its source's declared partition",
            err(replace(g, "NC_STRONG_n486_s1") { it.first to sS.mapValues { e -> if (e.value == "law") "rel_a" else "rel_b" } }))
    }

    /** EC control fixture: the KK_<role>_n486_d<d> ids, pc_lo on even positions of the sorted ids (243 of 486), pc_hi otherwise. */
    private fun ecSites(g: List<Pair<String, Map<String, String>>>): List<Pair<String, Map<String, String>>> =
        listOf("STRONG", "MID").flatMap { role ->
            (1..5).map { d ->
                val ids = g.first { it.first == "KK_${role}_n486_d$d" }.second.keys.sorted()
                "EC_${role}_n486_d$d" to ids.withIndex().associate { it.value to if (it.index % 2 == 0) "pc_lo" else "pc_hi" }
            }
        }

    private fun errEc(sites: List<Pair<String, Map<String, String>>>): String? = harness.dflEcError(harness.pcsParseSites(file(sites)), rootIds.toSet())

    @Test
    fun `amended site check - 10 elongation-cut controls after the 87 sites, and every refusal`() {
        val g = good()
        val ec = ecSites(g)
        val g97 = g + ec
        assertEquals(97, g97.size)
        assertNull(errEc(g97))
        val e1 = "EC_STRONG_n486_d1"
        val src = g.first { it.first == "KK_STRONG_n486_d1" }.second
        val chem = src.filterValues { it == "chemistry" }.keys
        val cases = listOf(
            g to "the site file holds 86 sites after IDENTITY, not 96 (33 KK + 33 K2 + 20 NC + 10 EC)",
            g97.filter { it.first != "EC_MID_n486_d5" } to "the site file holds 95 sites after IDENTITY, not 96 (33 KK + 33 K2 + 20 NC + 10 EC)",
            replace(g97, "NC_STRONG_n486_s3") { "NC_STRONG_n486_s11" to it.second } to "site 'NC_STRONG_n486_s11' where 'NC_STRONG_n486_s3' is expected",
            replace(g97, e1) { "EC_STRONG_n486_d9" to it.second } to "site 'EC_STRONG_n486_d9' where '$e1' is expected",
            replace(g97, e1) { it.first to ec.first { x -> x.first == "EC_STRONG_n486_d2" }.second } to "site $e1 does not hold exactly the ids of KK_STRONG_n486_d1",
            replace(g97, e1) { it.first to it.second.mapValues { e -> if (e.value == "pc_hi") "pc_x" else e.value } } to "site $e1 holds the labels [pc_lo, pc_x], not exactly [pc_hi, pc_lo]",
            replace(g97, e1) { it.first to it.second.keys.sorted().withIndex().associate { x -> x.value to if (x.index < 242) "pc_lo" else "pc_hi" } } to
                "site $e1: pc_lo holds 242 of 486 ids, fewer than half (ties go to the lower half)",
            replace(g97, e1) { it.first to src.keys.associateWith { k -> if (k in chem) "pc_lo" else "pc_hi" } } to "site $e1 reproduces the declared partition of KK_STRONG_n486_d1",
            replace(g97, e1) { it.first to src.keys.associateWith { k -> if (k in chem) "pc_hi" else "pc_lo" } } to "site $e1 reproduces the declared partition of KK_STRONG_n486_d1")
        for ((sites, want) in cases) assertEquals(want, errEc(sites))
    }

    @Test
    fun `fresh seed - the deflated arm draws seed base 20261004 and not siteNull's 88820260908`() {
        assertEquals(20261004L, harness.dflSeedBase())
        val r = java.util.Random(23)
        val cA = unit(DoubleArray(dim) { r.nextGaussian() })
        val cB = unit(DoubleArray(dim) { r.nextGaussian() })
        val embs = (0 until 240).map { i ->
            val c = if (i < 120) cA else cB
            Embedding(rawText = "f$i", distilledText = "f$i", values = FloatArray(dim) { j -> (c[j] + 0.30 * r.nextGaussian()).toFloat() })
        }
        val vectors = embs.map { it.projectTo(dim) }
        val groups = listOf((0 until 120).toList(), (120 until 240).toList())
        val name = "KK_STRONG_n240_d1"
        val res = harness.dflDeflatedSite(splitter(), harness.cpcNewCapture(), name, 0, vectors, embs, groups, reps)
        assertEquals(1, res.deflDims)
        assertTrue(res.defl.count { it > 0.0 } >= reps / 2, "the deflated replicates must reach the gate: ${res.defl.toList()}")
        val (mu, centered) = harness.cpcMoments(vectors)
        val (dc, _) = harness.cpcDeflate(vectors, centered, groups)
        val direct = harness.cpcSiteArm(splitter(), harness.cpcNewCapture(), "SNDF", 20261004L, name, mu, dc, vectors.size, reps)
        assertArrayEquals(direct, res.defl, 0.0)
        val old = harness.cpcDeclaredSite(splitter(), harness.cpcNewCapture(), name, 0, vectors, embs, groups, reps, deflated = true,
            plainIn = DoubleArray(reps))
        assertEquals(1, old.deflDims)
        assertEquals(old.declared, res.declared, 0.0)
        assertFalse(old.defl!!.contentEquals(res.defl), "the fresh-seed replicates must differ from siteNull's seed base")
        assertEquals(res.defl.count { it >= res.declared }, res.kDefl)
    }

    @Test
    fun `k counts replicates at or above the declared statistic - ties count`() {
        // identical rows: declared = 0.0 exactly (no within/total spread) and every replicate of the zero-texture null scores 0.0,
        // so ">=" counts all reps and ">" none
        val v = unit(DoubleArray(dim) { if (it == 0) 1.0 else 0.0 })
        val embs = (0 until 240).map { i -> Embedding(rawText = "t$i", distilledText = "t$i", values = FloatArray(dim) { j -> v[j].toFloat() }) }
        val res = harness.dflDeflatedSite(splitter(), harness.cpcNewCapture(), "NC_math_n240_s1", 0, embs.map { it.projectTo(dim) }, embs,
            listOf((0 until 120).toList(), (120 until 240).toList()), reps)
        assertEquals(0.0, res.declared, 0.0)
        assertTrue(res.defl.all { it == 0.0 }, "zero-texture replicates: ${res.defl.toList()}")
        assertEquals(reps, res.kDefl)
    }

    @Test
    fun `deflated path - planted clusters certify, a random relabelling of the same population does not`() {
        val r = java.util.Random(17)
        val cA = unit(DoubleArray(dim) { r.nextGaussian() })
        val cB = unit(DoubleArray(dim) { r.nextGaussian() })
        val ids = (0 until 240).map { "p%03d".format(it) }
        val emb = ids.withIndex().associate { (i, id) ->
            val c = if (i < 120) cA else cB
            id to Embedding(rawText = id, distilledText = id, values = FloatArray(dim) { j -> (c[j] + 0.05 * r.nextGaussian()).toFloat() })
        }
        val rootOf = ids
        fun run(m: Map<String, String>, name: String): SeparationNullBySizeTest.DflSite {
            val (pids, _, groups) = harness.pcsPopulation(rootOf, m)
            assertEquals(2, groups.size)
            return harness.dflDeflatedSite(splitter(), harness.cpcNewCapture(), name, 0, pids.map { emb.getValue(it).projectTo(dim) },
                pids.map { emb.getValue(it) }, groups, reps)
        }
        val planted = run(ids.withIndex().associate { (i, id) -> id to if (i < 120) "a" else "b" }, "KK_MID_n240_d1")
        assertEquals(0, planted.kDefl, "planted: declared ${planted.declared} deflated max ${planted.defl.max()}")
        val rr = java.util.Random(5)
        val rand = run(ids.associateWith { if (rr.nextBoolean()) "rel_a" else "rel_b" }, "NC_STRONG_n240_s1")
        assertTrue(rand.kDefl > 14, "a random relabelling must not deflated-null certify: k ${rand.kDefl} of $reps, declared ${rand.declared}")
    }
}
