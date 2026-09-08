package taxonomy.utils

import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.projectTo
import kotlin.math.sqrt

/**
 * Sampling standard error of the global separation objective J.
 *
 * WHY THIS EXISTS. The proposal gate accepts an edit when `deltaJ > tau`, with
 * `tau = 1e-6`. That is a float-neutrality band, not an estimate of anything: J is a
 * statistic computed from a finite construction sample, so it carries a sampling error of
 * its own. If that error is orders of magnitude larger than tau, the gate is accepting
 * edits whose measured improvement is far below the resolution of the measurement — a coin
 * flip on noise — and under greedy hill-climbing one such flip early in construction
 * cascades into a structurally different taxonomy. That is the leading explanation for a
 * leaf count that ranges 63-104 across seeds while held-out accuracy stays at 74.4 +/- 0.4.
 *
 * WHAT IT COMPUTES. A nonparametric bootstrap over the query set. Re-routing is not needed:
 * by the time J is measured the assignments are fixed, so resampling a query with
 * multiplicity m simply scales its contribution to its cells' sufficient statistics
 * `(n_c, sum_c w x)` by m. Cost is O(B * Q * d) with no graph walk.
 *
 * KEEP IN SYNC. The cell construction below mirrors
 * [StatisticsUtils.computeDagSeparationJ] — leaves plus internal nodes carrying a residual
 * pool, residual queries entering at weight 1.0. It is duplicated rather than shared to keep
 * this diagnostic independent of that file. If the objective changes there, change it here.
 */
object JBootstrap {

    data class Result(
        /** J on the full sample; equals StatisticsUtils.computeDagSeparationJ. */
        val j: Double,
        /** Bootstrap standard error of J. */
        val seBoot: Double,
        /** Replicates actually used. */
        val replicates: Int
    )

    /** One query's contribution: its projected vector and the cells it feeds, with weights. */
    private class Contribution(val proj: DoubleArray, val cells: MutableList<Pair<Int, Double>> = mutableListOf())

    /**
     * A frozen view of one structure's cell assignment, keyed by query, for paired comparison.
     * Cells are keyed by STRING id (not index) because the two structures being compared do not
     * share a cell numbering.
     */
    class Capture internal constructor(
        internal val perQuery: LinkedHashMap<String, QueryView>
    ) {
        internal class QueryView(val proj: DoubleArray, val cells: MutableList<Pair<String, Double>> = mutableListOf())
        val queryCount: Int get() = perQuery.size
    }

    /** Cell assignment of the current structure, for later paired bootstrapping. */
    fun capture(root: GraphNode, allEmbeddings: List<Embedding>, d: Int = taxonomy.model.dimForDepth(0)): Capture {
        val embMap = allEmbeddings.associateBy {
            if (it.queryId != -1) it.queryId.toString() else it.rawText
        }
        val rawEmbMap = allEmbeddings.associateBy { it.rawText }

        val perQuery = LinkedHashMap<String, Capture.QueryView>()
        val visited = mutableSetOf<String>()
        fun walk(n: GraphNode) {
            if (!visited.add(n.id)) return
            if (n.isLeaf) {
                for ((text, weight) in n.queryWeights) {
                    val emb = GraphNode.getEmbedding(text) ?: continue
                    perQuery.getOrPut(text) { Capture.QueryView(emb.projectTo(d)) }.cells.add(n.id to weight)
                }
            } else {
                if (n.residualQueries.isNotEmpty()) {
                    val cell = n.id + "_residual"
                    for (key in n.residualQueries) {
                        val emb = GraphNode.getEmbedding(key) ?: embMap[key] ?: rawEmbMap[key] ?: continue
                        perQuery.getOrPut(key) { Capture.QueryView(emb.projectTo(d)) }.cells.add(cell to 1.0)
                    }
                }
                n.children.forEach { walk(it) }
            }
        }
        walk(root)
        return Capture(perQuery)
    }

    /**
     * Standard error of the PAIRED difference dJ = J(after) - J(before).
     *
     * This is the quantity the proposal gate actually tests, and it is far smaller than
     * SE(J): both sides are computed on the same corpus draw and differ by a single edit, so
     * Var(dJ) = Var(J') + Var(J) - 2Cov(J', J) and the shared variance very nearly cancels.
     * Testing dJ against SE(J) instead would be the textbook paired/unpaired error — measured
     * at SE(J) = 2.65e-3, it would have rejected 11 of the 14 depth-1 domain splits.
     *
     * Only queries whose cell assignment CHANGED are resampled; the rest are held at weight
     * 1.0 in both structures, where they contribute identically and cancel from the
     * difference. That is what makes this O(B * (n_affected + C) * d) instead of O(B * N * d),
     * cheap enough to run on every proposal.
     *
     * Weights are Bayesian-bootstrap (Dirichlet) rather than multinomial: smoother when the
     * affected set is small, and it cannot produce a degenerate replicate in which a small
     * cell draws zero queries.
     *
     * @return SE of dJ, or NaN if the comparison is degenerate.
     */
    fun pairedDeltaSe(
        before: Capture,
        after: Capture,
        replicates: Int = 200,
        seed: Long = 987654321L,
        d: Int = taxonomy.model.dimForDepth(0)
    ): Double {
        fun sig(v: Capture.QueryView?): List<Pair<String, Double>> =
            v?.cells?.sortedBy { it.first } ?: emptyList()

        val keys = LinkedHashSet<String>().apply { addAll(before.perQuery.keys); addAll(after.perQuery.keys) }
        val affected = keys.filter { sig(before.perQuery[it]) != sig(after.perQuery[it]) }
        if (affected.isEmpty()) return 0.0

        val affectedSet = affected.toHashSet()

        // Fixed part: every unaffected query, accumulated once per structure.
        class Fixed(val n: HashMap<String, Double> = HashMap(), val s: HashMap<String, DoubleArray> = HashMap())
        fun fixedOf(cap: Capture): Fixed {
            val f = Fixed()
            for ((k, v) in cap.perQuery) {
                if (k in affectedSet) continue
                for ((cell, w) in v.cells) {
                    f.n[cell] = (f.n[cell] ?: 0.0) + w
                    val row = f.s.getOrPut(cell) { DoubleArray(d) }
                    for (j in 0 until d) row[j] += w * v.proj[j]
                }
            }
            return f
        }
        val fb = fixedOf(before)
        val fa = fixedOf(after)

        fun jOf(cap: Capture, fixed: Fixed, w: DoubleArray, idx: Map<String, Int>): Double {
            val cellN = HashMap<String, Double>(fixed.n)
            val cellS = HashMap<String, DoubleArray>()
            for ((c, row) in fixed.s) cellS[c] = row.copyOf()
            for (k in affected) {
                val v = cap.perQuery[k] ?: continue
                val wi = w[idx[k]!!]
                for ((cell, weight) in v.cells) {
                    val ww = weight * wi
                    cellN[cell] = (cellN[cell] ?: 0.0) + ww
                    val row = cellS.getOrPut(cell) { DoubleArray(d) }
                    for (j in 0 until d) row[j] += ww * v.proj[j]
                }
            }
            var n = 0.0
            val sTot = DoubleArray(d)
            var wWithin = 0.0
            var pairFrac = 0.0
            for ((cell, cN) in cellN) {
                if (cN <= 0.0) continue
                n += cN
                val row = cellS[cell] ?: continue
                var norm2 = 0.0
                for (j in 0 until d) { sTot[j] += row[j]; norm2 += row[j] * row[j] }
                wWithin += cN * cN - norm2
                pairFrac += cN * (cN - 1.0)
            }
            if (n < 2.0) return Double.NaN
            var normTot2 = 0.0
            for (j in 0 until d) normTot2 += sTot[j] * sTot[j]
            val wTotal = n * n - normTot2
            val expected = wTotal * pairFrac / (n * (n - 1.0))
            if (expected <= 1e-10) return Double.NaN
            return 1.0 - wWithin / expected
        }

        val idx = affected.withIndex().associate { it.value to it.index }
        val rng = kotlin.random.Random(seed)
        val deltas = ArrayList<Double>(replicates)
        val w = DoubleArray(affected.size)
        repeat(replicates) {
            // Dirichlet(1,...,1) via normalised Exp(1), scaled so the affected mass is preserved.
            var sum = 0.0
            for (i in w.indices) {
                val e = -kotlin.math.ln(1.0 - rng.nextDouble())
                w[i] = e; sum += e
            }
            val scale = affected.size / sum
            for (i in w.indices) w[i] *= scale

            val jb = jOf(before, fb, w, idx)
            val ja = jOf(after, fa, w, idx)
            if (jb.isFinite() && ja.isFinite()) deltas.add(ja - jb)
        }
        if (deltas.size < 2) return Double.NaN
        val mean = deltas.average()
        return sqrt(deltas.sumOf { (it - mean) * (it - mean) } / (deltas.size - 1))
    }

    fun estimate(
        root: GraphNode,
        allEmbeddings: List<Embedding>,
        replicates: Int = 200,
        seed: Long = 987654321L,
        d: Int = taxonomy.model.dimForDepth(0)
    ): Result {
        val embMap = allEmbeddings.associateBy {
            if (it.queryId != -1) it.queryId.toString() else it.rawText
        }
        val rawEmbMap = allEmbeddings.associateBy { it.rawText }

        val leaves = mutableListOf<GraphNode>()
        val residualParents = mutableListOf<GraphNode>()
        val visited = mutableSetOf<String>()
        fun walk(n: GraphNode) {
            if (!visited.add(n.id)) return
            if (n.isLeaf) {
                leaves.add(n)
            } else {
                if (n.residualQueries.isNotEmpty()) residualParents.add(n)
                n.children.forEach { walk(it) }
            }
        }
        walk(root)

        val cellCount = leaves.size + residualParents.size
        if (cellCount < 2) return Result(0.0, 0.0, 0)

        val cellIndex = HashMap<String, Int>(cellCount * 2)
        leaves.forEachIndexed { i, n -> cellIndex[n.id] = i }
        residualParents.forEachIndexed { i, n -> cellIndex[n.id + "_residual"] = leaves.size + i }

        // Group contributions by query so a bootstrap draw scales the whole query at once.
        val byQuery = LinkedHashMap<String, Contribution>()
        for (leaf in leaves) {
            val ci = cellIndex[leaf.id] ?: continue
            for ((text, weight) in leaf.queryWeights) {
                val emb = GraphNode.getEmbedding(text) ?: continue
                byQuery.getOrPut(text) { Contribution(emb.projectTo(d)) }.cells.add(ci to weight)
            }
        }
        for (parent in residualParents) {
            val ci = cellIndex[parent.id + "_residual"] ?: continue
            for (key in parent.residualQueries) {
                val emb = GraphNode.getEmbedding(key) ?: embMap[key] ?: rawEmbMap[key] ?: continue
                byQuery.getOrPut(key) { Contribution(emb.projectTo(d)) }.cells.add(ci to 1.0)
            }
        }
        val contributions = byQuery.values.toList()
        if (contributions.size < 2) return Result(0.0, 0.0, 0)

        val pointJ = jFrom(contributions, IntArray(contributions.size) { 1 }, cellCount, d)

        val rng = kotlin.random.Random(seed)
        val js = ArrayList<Double>(replicates)
        val q = contributions.size
        for (b in 0 until replicates) {
            val mult = IntArray(q)
            repeat(q) { mult[rng.nextInt(q)]++ }
            val jb = jFrom(contributions, mult, cellCount, d)
            if (jb.isFinite()) js.add(jb)
        }
        if (js.size < 2) return Result(pointJ, 0.0, js.size)

        val mean = js.average()
        val se = sqrt(js.sumOf { (it - mean) * (it - mean) } / (js.size - 1))
        return Result(pointJ, se, js.size)
    }

    /** J under per-query multiplicities; `mult[i] == 1` for every i reproduces the point estimate. */
    private fun jFrom(contributions: List<Contribution>, mult: IntArray, cellCount: Int, d: Int): Double {
        val cellN = DoubleArray(cellCount)
        val cellSum = Array(cellCount) { DoubleArray(d) }

        for (i in contributions.indices) {
            val m = mult[i]
            if (m == 0) continue
            val c = contributions[i]
            for ((cellIdx, weight) in c.cells) {
                val w = weight * m
                cellN[cellIdx] += w
                val row = cellSum[cellIdx]
                for (j in 0 until d) row[j] += w * c.proj[j]
            }
        }

        val n = cellN.sum()
        if (n < 2.0) return Double.NaN

        val sumTotal = DoubleArray(d)
        var wWithin = 0.0
        var pairFrac = 0.0
        for (ci in 0 until cellCount) {
            val cN = cellN[ci]
            if (cN <= 0.0) continue
            var normC2 = 0.0
            val row = cellSum[ci]
            for (j in 0 until d) {
                sumTotal[j] += row[j]
                normC2 += row[j] * row[j]
            }
            wWithin += cN * cN - normC2
            pairFrac += cN * (cN - 1.0)
        }
        var normTotal2 = 0.0
        for (j in 0 until d) normTotal2 += sumTotal[j] * sumTotal[j]
        val wTotal = n * n - normTotal2

        val expectedWithin = wTotal * pairFrac / (n * (n - 1.0))
        if (expectedWithin <= 1e-10) return Double.NaN
        return 1.0 - wWithin / expectedWithin
    }
}
