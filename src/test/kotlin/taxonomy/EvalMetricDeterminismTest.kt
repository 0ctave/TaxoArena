package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.utils.TaxonomyMetrics
import taxonomy.utils.computeTotalDasguptaCost
import taxonomy.utils.computeTripletAccuracy
import taxonomy.utils.dagDendrogramPurity
import java.util.Collections
import kotlin.math.sqrt
import kotlin.random.Random

/**
 * EVAL-METRIC-DETERMINISM, criterion C2 (the golden permutation test), registered in
 * docs/judge_v2_program.md ("## Registered 2026-09-25 (before any code or call) —
 * EVAL-METRIC-DETERMINISM: ..."; commit 55a6ce1).
 *
 * GraphNode.queries is filled by parallel routing, so its order is thread-completion
 * order. This test fixes a synthetic tree (3 depths, 6 leaves with non-empty vmfMu,
 * one rawText in two leaves with DIFFERENT vectors, m = 151 distinct texts so that
 * C(m, 2) = 11,325 > 5,000 and computeTotalDasguptaCost takes the SAMPLED branch),
 * applies K = 20 seeded permutations to every leaf.queries list (permutation 0 is
 * the identity) and asserts, per metric, raw-bit identity (doubleToRawLongBits; never
 * a tolerance) of computeTotalDasguptaCost, computeTripletAccuracy,
 * dagDendrogramPurity and TaxonomyMetrics.generateReport().sphericalSilhouette over
 * the 20 permutations, plus a golden literal (raw bits) for each of the four on the
 * unpermuted fixture. The tie rule (equal rawText, different vectors) and the exact
 * branch of the Dasgupta cost (a small fixture, C(40, 2) = 780 <= 5,000) are tested
 * separately.
 *
 * NON-VACUITY (C2 (ii)): this file uses only APIs present before the change, so it
 * compiles against the pre-change metric code, where the sampled Dasgupta cost draws
 * pairs by index over the input order and must FAIL [tdcSampledPermutationInvariant].
 *
 * Synthetic fixture only: no corpus, no DB, no network.
 */
class EvalMetricDeterminismTest {

    private companion object {
        const val K = 20
        const val DIM = 16
        const val FIXTURE_SEED = 20250925L
        const val PERMUTATION_SEED_BASE = 7_000L
        const val SHARED_TEXT = "query shared by two leaves"

        // GOLDEN LITERALS (raw bits of the four metrics on the UNPERMUTED fixture),
        // computed once on the post-change code at the build and written here.
        const val GOLDEN_TDC_BITS = 0x410681e979d904e1L // 184381.18449596225
        const val GOLDEN_TA_BITS = 0x3fe574cae995d32cL  // 0.6705069124423964
        const val GOLDEN_DP_BITS = 0x3fe949ceaa532fd2L  // 0.7902596785220288
        const val GOLDEN_SS_BITS = 0x3fd9d5df3325a4c1L  // 0.40367870325878746
    }

    private class Fixture(
        val root: GraphNode,
        val leaves: List<GraphNode>,
        val base: Map<GraphNode, List<Embedding>>,
        val gt: Map<String, String>,
    )

    private fun node(id: String, label: String, depth: Int) =
        GraphNode(id = id, label = label, depth = depth)

    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child)
        child.parents.add(parent)
    }

    private fun unit(v: DoubleArray): FloatArray {
        val n = sqrt(v.sumOf { it * it })
        return FloatArray(v.size) { (v[it] / n).toFloat() }
    }

    private fun gaussian(rng: Random): Double {
        // Box-Muller; deterministic under the seeded kotlin.random.Random.
        val u1 = rng.nextDouble().coerceAtLeast(1e-12)
        val u2 = rng.nextDouble()
        return sqrt(-2.0 * kotlin.math.ln(u1)) * kotlin.math.cos(2.0 * Math.PI * u2)
    }

    /** The main fixture (sampled branch). Explicit node ids: traversal order never depends on the global id counter. */
    private fun mainFixture(): Fixture {
        val rng = Random(FIXTURE_SEED)
        val root = node("emd-root", "root", 0)
        val a = node("emd-A", "alpha", 1); val b = node("emd-B", "beta", 1)
        val c = node("emd-C", "gamma", 1); val d = node("emd-D", "delta", 1)
        listOf(a, b, c, d).forEach { link(root, it) }
        val a1 = node("emd-A1", "alpha-1", 2); val a2 = node("emd-A2", "alpha-2", 2)
        val b1 = node("emd-B1", "beta-1", 2); val b2 = node("emd-B2", "beta-2", 2)
        link(a, a1); link(a, a2); link(b, b1); link(b, b2)
        val leaves = listOf(a1, a2, b1, b2, c, d)
        val labelOf = mapOf(a1 to "alpha", a2 to "alpha", b1 to "beta", b2 to "beta", c to "gamma", d to "delta")
        val allLabels = listOf("alpha", "beta", "gamma", "delta")

        val centres = leaves.associateWith { DoubleArray(DIM) { gaussian(rng) } }
        leaves.forEach { it.vmfMu = unit(centres.getValue(it)) }

        val base = LinkedHashMap<GraphNode, MutableList<Embedding>>()
        val gt = LinkedHashMap<String, String>()
        var t = 0
        for (leaf in leaves) {
            val list = mutableListOf<Embedding>()
            repeat(25) {
                val text = "query %03d".format(t++)
                val ctr = centres.getValue(leaf)
                val v = unit(DoubleArray(DIM) { ctr[it] + 0.9 * gaussian(rng) })
                list.add(Embedding(text, text, v))
                // ~15% label noise so purity is not trivially 1.0
                gt[text] = if (rng.nextDouble() < 0.15) allLabels[rng.nextInt(allLabels.size)] else labelOf.getValue(leaf)
                leaf.queryWeights[text] = 1.0
            }
            base[leaf] = list
        }
        // One rawText in two leaves, with DIFFERENT vectors (the tie rule's case).
        val sharedInA1 = Embedding(SHARED_TEXT, SHARED_TEXT, unit(DoubleArray(DIM) { centres.getValue(a1)[it] + 0.5 * gaussian(rng) }))
        val sharedInB2 = Embedding(SHARED_TEXT, SHARED_TEXT, unit(DoubleArray(DIM) { centres.getValue(b2)[it] + 0.5 * gaussian(rng) }))
        base.getValue(a1).add(sharedInA1); a1.queryWeights[SHARED_TEXT] = 0.7
        base.getValue(b2).add(sharedInB2); b2.queryWeights[SHARED_TEXT] = 0.3
        gt[SHARED_TEXT] = "alpha"
        return Fixture(root, leaves, base, gt)
    }

    /** Permutation k of every leaf.queries list (k = 0: the identity), installed on the nodes. */
    private fun applyPermutation(f: Fixture, k: Int) {
        for (leaf in f.leaves) {
            val src = f.base.getValue(leaf)
            val perm = if (k == 0) src.toList() else src.shuffled(Random(PERMUTATION_SEED_BASE + 31L * k + leaf.id.hashCode()))
            leaf.queries = Collections.synchronizedList(ArrayList(perm))
        }
    }

    /** The metric input as a caller would assemble it from leaf.queries (leaf order fixed, query order permuted). */
    private fun inputOf(f: Fixture): List<Embedding> = f.leaves.flatMap { it.queries }

    /** queryId -> assigned node, inserted in leaf.queries order (first leaf wins for the shared text). */
    private fun assignmentsOf(f: Fixture): Map<String, GraphNode> {
        val out = LinkedHashMap<String, GraphNode>()
        for (leaf in f.leaves) for (q in leaf.queries) out.putIfAbsent(q.rawText, leaf)
        return out
    }

    private enum class Metric { TDC, TA, DP, SS }

    private fun compute(f: Fixture, metric: Metric): Double = when (metric) {
        Metric.TDC -> computeTotalDasguptaCost(f.root, inputOf(f))
        Metric.TA -> computeTripletAccuracy(f.root, inputOf(f))
        Metric.DP -> dagDendrogramPurity(assignmentsOf(f), f.gt)
        Metric.SS -> TaxonomyMetrics(f.root, f.gt.mapValues { listOf(it.value) }).generateReport().sphericalSilhouette
    }

    private fun assertPermutationInvariant(metric: Metric) {
        val f = mainFixture()
        val values = (0 until K).map { k -> applyPermutation(f, k); compute(f, metric) }
        val bits = values.map { java.lang.Double.doubleToRawLongBits(it) }
        val distinct = bits.distinct()
        println("[EMD-C2] $metric permutations=$K distinct_raw_bits=${distinct.size} " +
            "value[0]=${values[0]} (bits 0x${java.lang.Long.toHexString(bits[0])}) " +
            "min=${values.minOrNull()} max=${values.maxOrNull()}")
        for (k in 1 until K) {
            assertEquals(bits[0], bits[k],
                "$metric: raw bits of permutation $k (${values[k]}) differ from permutation 0 (${values[0]}); " +
                    "${distinct.size} distinct raw-bit values over $K permutations")
        }
    }

    // ── C2 (b): bit identity over K = 20 permutations, one test per metric ──

    @Test
    fun tdcSampledPermutationInvariant() = assertPermutationInvariant(Metric.TDC)

    @Test
    fun tripletAccuracyPermutationInvariant() = assertPermutationInvariant(Metric.TA)

    @Test
    fun dendrogramPurityPermutationInvariant() = assertPermutationInvariant(Metric.DP)

    @Test
    fun sphericalSilhouettePermutationInvariant() = assertPermutationInvariant(Metric.SS)

    // ── C2 (c): golden literals on the unpermuted fixture ──

    @Test
    fun goldenValuesOnUnpermutedFixture() {
        val f = mainFixture()
        applyPermutation(f, 0)
        val golden = mapOf(
            Metric.TDC to GOLDEN_TDC_BITS, Metric.TA to GOLDEN_TA_BITS,
            Metric.DP to GOLDEN_DP_BITS, Metric.SS to GOLDEN_SS_BITS,
        )
        val failures = mutableListOf<String>()
        for ((metric, want) in golden) {
            val v = compute(f, metric)
            val got = java.lang.Double.doubleToRawLongBits(v)
            println("[EMD-GOLDEN] $metric value=$v bits=0x${java.lang.Long.toHexString(got)}L " +
                "golden=0x${java.lang.Long.toHexString(want)}L (${java.lang.Double.longBitsToDouble(want)})")
            if (got != want) failures.add("$metric got $v (0x${java.lang.Long.toHexString(got)}) want ${java.lang.Double.longBitsToDouble(want)}")
        }
        assertTrue(failures.isEmpty(), "golden literal mismatch: $failures")
    }

    // ── C2 (d): the tie rule (equal rawText, different vectors) ──

    @Test
    fun tieRuleKeepsTheSameRepresentativeUnderBothInputOrders() {
        // Small tree on the EXACT branch; the duplicate's representative changes the value.
        val root = node("emd-tie-root", "root", 0)
        val l1 = node("emd-tie-L1", "left", 1); val l2 = node("emd-tie-L2", "right", 1)
        link(root, l1); link(root, l2)
        val others = listOf(
            Embedding("a", "a", floatArrayOf(1f, 0f, 0f)),
            Embedding("b", "b", floatArrayOf(0.9f, 0.1f, 0f)),
            Embedding("c", "c", floatArrayOf(0f, 1f, 0f)),
            Embedding("d", "d", floatArrayOf(0.1f, 0.9f, 0.2f)),
        )
        // Same rawText "dup"; vectors differ at element 0: dupLow < dupHigh under Double.compare.
        val dupLow = Embedding("dup", "dup", floatArrayOf(0.2f, 0.9f, 0.1f))
        val dupHigh = Embedding("dup", "dup", floatArrayOf(0.95f, 0.05f, 0.1f))
        l1.queries = Collections.synchronizedList(ArrayList(listOf(others[0], others[1], dupHigh)))
        l2.queries = Collections.synchronizedList(ArrayList(listOf(others[2], others[3], dupLow)))

        val lowFirst = listOf(dupLow) + others + listOf(dupHigh)
        val highFirst = listOf(dupHigh) + others + listOf(dupLow)
        val vLowFirst = computeTotalDasguptaCost(root, lowFirst)
        val vHighFirst = computeTotalDasguptaCost(root, highFirst)
        val vOnlyLow = computeTotalDasguptaCost(root, others + listOf(dupLow))
        val vOnlyHigh = computeTotalDasguptaCost(root, others + listOf(dupHigh))
        println("[EMD-TIE] lowFirst=$vLowFirst highFirst=$vHighFirst onlyLow=$vOnlyLow onlyHigh=$vOnlyHigh")
        // Non-degenerate: the representative matters.
        assertNotEquals(vOnlyLow, vOnlyHigh, "fixture degenerate: both representatives give the same cost")
        assertEquals(java.lang.Double.doubleToRawLongBits(vLowFirst), java.lang.Double.doubleToRawLongBits(vHighFirst),
            "tie rule: the representative depends on the input order ($vLowFirst vs $vHighFirst)")
        // The declared rule: the representative is the lesser vector under element-wise Double.compare.
        assertEquals(java.lang.Double.doubleToRawLongBits(vOnlyLow), java.lang.Double.doubleToRawLongBits(vHighFirst),
            "tie rule: the representative is not the declared one (element-wise Double.compare minimum)")
    }

    // ── the exact branch of the Dasgupta cost (C(40, 2) = 780 <= 5,000) ──

    @Test
    fun tdcExactBranchPermutationInvariant() {
        val rng = Random(FIXTURE_SEED + 1)
        val root = node("emd-ex-root", "root", 0)
        val l1 = node("emd-ex-L1", "left", 1); val l2 = node("emd-ex-L2", "right", 1)
        link(root, l1); link(root, l2)
        val c1 = DoubleArray(DIM) { gaussian(rng) }; val c2 = DoubleArray(DIM) { gaussian(rng) }
        val base1 = (0 until 20).map { i -> val tx = "ex %02d".format(i); Embedding(tx, tx, unit(DoubleArray(DIM) { c1[it] + gaussian(rng) })) }
        val base2 = (20 until 40).map { i -> val tx = "ex %02d".format(i); Embedding(tx, tx, unit(DoubleArray(DIM) { c2[it] + gaussian(rng) })) }
        val values = (0 until K).map { k ->
            val p1 = if (k == 0) base1 else base1.shuffled(Random(PERMUTATION_SEED_BASE + 101L * k))
            val p2 = if (k == 0) base2 else base2.shuffled(Random(PERMUTATION_SEED_BASE + 103L * k))
            l1.queries = Collections.synchronizedList(ArrayList(p1))
            l2.queries = Collections.synchronizedList(ArrayList(p2))
            computeTotalDasguptaCost(root, p1 + p2)
        }
        val bits = values.map { java.lang.Double.doubleToRawLongBits(it) }
        println("[EMD-EXACT] permutations=$K distinct_raw_bits=${bits.distinct().size} value[0]=${values[0]}")
        for (k in 1 until K) assertEquals(bits[0], bits[k], "exact-branch TDC: permutation $k (${values[k]}) vs 0 (${values[0]})")
    }

    // ── the fixture's non-degeneracy (for the READY's fixture check) ──

    @Test
    fun mainFixtureIsNonDegenerate() {
        val f = mainFixture()
        applyPermutation(f, 0)
        val distinctTexts = inputOf(f).map { it.rawText }.distinct().size
        val pairs = distinctTexts.toLong() * (distinctTexts - 1) / 2
        val depths = f.leaves.map { it.depth }.distinct().size
        val withMu = f.leaves.count { it.vmfMu.isNotEmpty() }
        val sharedLeaves = f.leaves.count { l -> l.queries.any { it.rawText == SHARED_TEXT } }
        val sharedVectors = f.leaves.flatMap { l -> l.queries.filter { it.rawText == SHARED_TEXT } }.map { it.values.toList() }.distinct().size
        println("[EMD-FIXTURE] distinct_texts=$distinctTexts pairs=$pairs leaf_depths=$depths leaves_with_mu=$withMu " +
            "shared_text_leaves=$sharedLeaves shared_text_vectors=$sharedVectors")
        assertTrue(distinctTexts >= 120, "m >= 120")
        assertTrue(pairs > 5000L, "C(m,2) > 5000: the SAMPLED branch")
        assertTrue(depths >= 2, ">= 2 leaf depths")
        assertTrue(withMu >= 4, ">= 4 leaves with non-empty vmfMu")
        assertEquals(2, sharedLeaves, "one rawText present in two leaves")
        assertEquals(2, sharedVectors, "with DIFFERENT vectors")
        val tdc = compute(f, Metric.TDC); val ta = compute(f, Metric.TA)
        val dp = compute(f, Metric.DP); val ss = compute(f, Metric.SS)
        println("[EMD-FIXTURE] TDC=$tdc TA=$ta DP=$dp SS=$ss")
        assertTrue(tdc > 0.0, "TDC > 0")
        assertTrue(ta > 0.0 && ta < 1.0, "TA strictly inside (0,1)")
        assertTrue(dp > 0.0 && dp < 1.0, "DP strictly inside (0,1)")
        assertTrue(ss != 0.0, "SS non-zero")
    }
}
