package taxonomy

import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import taxonomy.model.Embedding
import taxonomy.model.EmbeddingSlice
import taxonomy.model.projectTo
import kotlin.math.sqrt

/**
 * CERT-POSITIVE-CONTROL: the declared-site arm of SeparationNullBySizeTest on synthetic fixtures (no DB, no snapshot, no
 * network; runs in `test`). Every assertion is on a VALUE whose correct answer is known by construction:
 *  - routine identity: the declared-site routine applied to the children the production splitter routed returns the
 *    splitter's own dasguptaDeltaNorm BIT FOR BIT (I-1's live leg on a planted fixture);
 *  - the registration's selftest: a planted two-cluster population, declared by its true clusters, is matched by NO null
 *    replicate (k = 0, the CERTIFIED side), C0's relabelling p95 stays far below the null's p95 (comparable); a single
 *    anisotropic Gaussian declared by random balanced labels is exceeded by EVERY replicate (k = reps), and declared by
 *    the median cut along its top axis is still exceeded by more than 5% of them (never certified);
 *  - the ">=" of the exceedance count (a tie counts), siteNull's seed formula and seed bases, the deflation (it changes
 *    the null), the src pooling rule (a src with exactly minClusterSize items stays its own child; no-src items pooled).
 *
 * MUTANTS (run 2026-10-02 by a harness, one temporary edit at a time in SeparationNullBySizeTest's cpc* members, bytes
 * restored and compared after each; this class run each time): K0 control (no edit) SURVIVED | K1 k ">=" -> ">" KILLED (tie) |
 * K2 C0 shuffle removed KILLED (planted C0) | K3 pooling ">=" -> ">" KILLED (pooling) | K4 deflation not applied KILLED
 * (planted: deflated != undeflated at the deflated seed) | K5 plain seed base = the deflated's KILLED (planted: plain ==
 * siteNull's SN arm) | K6 cpcSeed formula KILLED (seed) | K7 routine at another width KILLED (identity) | K8 no-src dropped
 * KILLED (pooling) | K9 sepBinding instead of sepKway KILLED (isotropic: 4-decimal values) | K12 deflation basis from one
 * group KILLED (planted) | K10 live leg recomputed := persisted SURVIVED, NOT equivalent [CORRECTED 2026-10-02 by
 * READY_cert_positive_control D-5]: it would make the ARM's I-1 live gate vacuous (a broken routine would pass); it survives
 * because this test applies the routine itself to the returned routed children (r.groups), which guards the routine, not the
 * arm's gate; an UNKILLED survivor of the arm path, disclosed (fix offered: recompute in the arm loop from r.groups) | K11 live
 * children in hash-set order SURVIVED, EQUIVALENT at k = 2 (two-term sums commute) and fail-closed otherwise (a last-bit
 * mismatch makes the arm refuse, never certify): 10 of 11 non-equivalent killed, K10 survives.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CertPositiveControlArmTest {
    private val harness = SeparationNullBySizeTest()
    private var savedWidth = 0
    private val dim = 256
    private val reps = 40
    private val mcs = 55

    @BeforeAll fun pin() { savedWidth = EmbeddingSlice.width }
    @AfterAll fun restore() { EmbeddingSlice.width = savedWidth; tmpDir.deleteRecursively() }

    private fun unit(v: DoubleArray): DoubleArray { val n = sqrt(v.sumOf { it * it }); return DoubleArray(v.size) { v[it] / n } }
    private fun emb(i: Int, v: DoubleArray) = Embedding(rawText = "fx#$i", distilledText = "fx#$i", values = FloatArray(v.size) { v[it].toFloat() })

    /** Two clusters of 150 around two random directions, noise sd 0.03 per coordinate. */
    private fun planted(): List<Embedding> {
        val r = java.util.Random(7)
        val c1 = unit(DoubleArray(dim) { r.nextGaussian() }); val c2 = unit(DoubleArray(dim) { r.nextGaussian() })
        return (0 until 300).map { i -> val c = if (i < 150) c1 else c2; emb(i, unit(DoubleArray(dim) { c[it] + 0.03 * r.nextGaussian() })) }
    }

    /** One anisotropic Gaussian (coordinate scales 0.20 / (1 + j/8)) around a random direction, projected to the sphere. */
    private fun gaussian(): List<Embedding> {
        val r = java.util.Random(11)
        val mu = unit(DoubleArray(dim) { r.nextGaussian() })
        return (0 until 300).map { i -> emb(i, unit(DoubleArray(dim) { mu[it] + 0.20 / (1.0 + it / 8.0) * r.nextGaussian() })) }
    }

    private val tmpDir = java.nio.file.Files.createTempDirectory("cpc_arm").toFile().apply { deleteOnExit() }
    private fun splitter() = harness.cpcSplitter(mcs, java.io.File(tmpDir, "corpus-${System.nanoTime()}.db").absolutePath)
    private fun p95(xs: DoubleArray): Double { val s = xs.sorted(); return s[kotlin.math.ceil(0.95 * s.size).toInt() - 1] }

    @Test
    fun `routine identity - the declared-site routine reproduces the splitter's own dasguptaDeltaNorm bit for bit`() {
        val sp = splitter()
        val r = harness.cpcLiveIdentity(sp, "CPC_T_LIVE", planted(), 1)
        assertTrue(r.accepted, "the planted population must be split")
        assertEquals(2, r.k)
        assertEquals(r.persisted.toRawBits(), r.recomputed.toRawBits(), "persisted ${r.persisted} recomputed ${r.recomputed}")
        // the routine applied HERE to the routed children reproduces the splitter's value (independent of cpcLiveIdentity's own
        // recomputation), and the routed children are the planted clusters
        assertEquals(r.persisted.toRawBits(), harness.declaredSiteStatistic(r.groups, dim).toRawBits())
        assertEquals(listOf(150, 150), r.groups.map { it.size }.sorted())
        assertTrue(r.groups.all { g -> g.map { it.queryId < 150 }.distinct().size == 1 }, "a routed child mixes the planted clusters")
        assertTrue(r.persisted > 0.5, "planted separation ${r.persisted}")
    }

    @Test
    fun `planted two clusters - k_d = 0 (certifiable) and C0 far below the null`() {
        val sp = splitter(); val cap = harness.cpcNewCapture()
        val embs = planted()
        val vectors = embs.map { it.projectTo(dim) }
        val groups = listOf((0 until 150).toList(), (150 until 300).toList())
        val res = harness.cpcDeclaredSite(sp, cap, "fx_planted", 1, vectors, embs, groups, reps, deflated = true)
        assertEquals(0, res.kDeclared, "declared ${res.declared} max null ${res.plain.max()}")
        assertEquals(reps, res.plain.size)
        assertEquals(1, res.deflDims, "two groups give a one-dimensional between-centroid subspace")
        val defl = res.defl!!
        assertTrue(!defl.contentEquals(res.plain), "deflation must change the null")
        // ... by the projection, not only by the seed base: the undeflated rows at the deflated seed base give another null
        val (mu0, centered0) = harness.cpcMoments(vectors)
        assertTrue(!defl.contentEquals(harness.cpcSiteArm(sp, cap, "SND", 88820260908L, "fx_planted", mu0, centered0, vectors.size, reps)))
        // the plain null is siteNull's arm at seed base 20260908 (I-2 parity), the deflated at 88820260908
        val (mu, centered) = harness.cpcMoments(vectors)
        assertTrue(harness.cpcSiteArm(sp, cap, "SN", 20260908L, "fx_planted", mu, centered, vectors.size, reps).contentEquals(res.plain))
        val labels = IntArray(300) { if (it < 150) 0 else 1 }
        val c0 = harness.cpcRelabelNull(embs, labels, 2, reps, 20261002L, dim)
        assertTrue(p95(c0) < 0.02 && p95(c0) < p95(res.plain), "C0 p95 ${p95(c0)} null p95 ${p95(res.plain)}")
        assertTrue(c0.contentEquals(harness.cpcRelabelNull(embs, labels, 2, reps, 20261002L, dim)), "C0 is seeded")
    }

    @Test
    fun `single Gaussian - random labels give k_d = reps, a top-axis median cut is still not certified`() {
        val sp = splitter(); val cap = harness.cpcNewCapture()
        val embs = gaussian()
        val vectors = embs.map { it.projectTo(dim) }
        val r = java.util.Random(5)
        val perm = (0 until 300).shuffled(r)
        val random = listOf(perm.take(150).sorted(), perm.drop(150).sorted())
        val res = harness.cpcDeclaredSite(sp, cap, "fx_gauss", 1, vectors, embs, random, reps, deflated = false)
        assertEquals(reps, res.kDeclared, "declared ${res.declared}, min null ${res.plain.min()}")
        assertEquals(null, res.defl)
        // the median cut along the first coordinate's deviation (the population's top axis by construction)
        val (mu, _) = harness.cpcMoments(vectors)
        val order = (0 until 300).sortedBy { vectors[it][0] - mu[0] }
        val cut = listOf(order.take(150).sorted(), order.drop(150).sorted())
        val res2 = harness.cpcDeclaredSite(sp, cap, "fx_gauss", 1, vectors, embs, cut, reps, deflated = false, plainIn = res.plain)
        assertTrue((res2.kDeclared + 1).toDouble() / (reps + 1) > 0.05, "k ${res2.kDeclared} declared ${res2.declared}")
    }

    @Test
    fun `the null statistic is the uncensored sepKway, never the 4-decimal logged min-pair value`() {
        // an ISOTROPIC cloud (no structure): min-pair rejects most replicates at the bar; with the arm's capture attached to the
        // splitter's logger (as the arm does) the binding value would be the logged sep rounded to 4 decimals
        val sp = splitter(); val cap = harness.cpcNewCapture()
        val splitLog = org.slf4j.LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        val oldLevel = splitLog.level; val oldAdd = splitLog.isAdditive
        cap.context = splitLog.loggerContext; cap.start(); splitLog.level = ch.qos.logback.classic.Level.DEBUG
        splitLog.isAdditive = false; splitLog.addAppender(cap)
        try {
            val r = java.util.Random(13)
            val mu = unit(DoubleArray(dim) { r.nextGaussian() })
            val embs = (0 until 300).map { i -> emb(i, unit(DoubleArray(dim) { mu[it] + 0.05 * r.nextGaussian() })) }
            val vectors = embs.map { it.projectTo(dim) }
            val (m, c) = harness.cpcMoments(vectors)
            val xs = harness.cpcSiteArm(sp, cap, "SN", 20260908L, "fx_iso", m, c, vectors.size, reps)
            val reached = xs.filter { it > 0.0 }
            assertTrue(reached.isNotEmpty(), "no replicate reached the gate")
            assertTrue(reached.any { kotlin.math.abs(it * 1e4 - kotlin.math.round(it * 1e4)) > 1e-6 }, "every value is 4-decimal: ${reached.take(5)}")
        } finally {
            splitLog.detachAppender(cap); cap.stop(); splitLog.level = oldLevel; splitLog.isAdditive = oldAdd
        }
    }

    @Test
    fun `exceedance count is greater-or-equal - a tie counts`() {
        val sp = splitter(); val cap = harness.cpcNewCapture()
        val embs = planted(); val vectors = embs.map { it.projectTo(dim) }
        val groups = listOf((0 until 150).toList(), (150 until 300).toList())
        val d = harness.declaredSiteStatistic(groups.map { g -> g.map { embs[it] } }, dim)
        val crafted = doubleArrayOf(0.0, d, d - 1e-12, d + 1e-12, 1.0)
        val res = harness.cpcDeclaredSite(sp, cap, "fx_tie", 1, vectors, embs, groups, 5, deflated = false, plainIn = crafted)
        assertEquals(d, res.declared)
        assertEquals(3, res.kDeclared)
    }

    @Test
    fun `seed formula is siteNull's runArm verbatim`() {
        assertEquals(20260908L + "n00000006".hashCode().toLong() * 2654435761L + 7 * 104729L, harness.cpcSeed(20260908L, "n00000006", 7))
        assertNotEquals(harness.cpcSeed(20260908L, "a", 1), harness.cpcSeed(20260908L, "a", 2))
    }

    @Test
    fun `src pooling - exactly minClusterSize stays, smaller and no-src are pooled into one last child`() {
        val ids = (0 until 200).map { "q$it" }
        val src = HashMap<String, String>()
        ids.forEachIndexed { i, id -> src[id] = when { i < 60 -> "b_src"; i < 115 -> "a_src"; i < 169 -> "c_src"; i < 179 -> "d_src"; else -> "" } }
        val (kids, pooled) = harness.cpcSrcGroups(ids, src, 55)
        assertEquals(listOf(55, 60, 85), kids.map { it.size })          // a_src (55, kept), b_src (60), pooled c+d+none (54+10+21)
        assertEquals(85, pooled)
        assertEquals((0 until 200).toList(), kids.flatten().sorted())
        assertEquals((60 until 115).toList(), kids[0])
        val (one, p1) = harness.cpcSrcGroups(ids.take(50), src, 55)    // every src < 55: one pooled child -> not scored (< 2)
        assertEquals(1, one.size); assertEquals(50, p1)
    }
}
