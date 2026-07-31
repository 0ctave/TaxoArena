package taxonomy.service

import taxonomy.model.*
import taxonomy.dataset.ModelEvalResult
import java.util.UUID
import kotlin.math.abs
import kotlin.math.ln
import kotlin.math.sqrt

// ─── Common types ──────────────────────────────────────────────────────────

typealias PairKey = Pair<String, String>

fun ordered(a: String, b: String): PairKey = if (a < b) a to b else b to a

enum class LeafState { ACTIVE, RESOLVED, EXHAUSTED }

class PairStats(var sumX: Double = 0.0, var n: Int = 0)

/**
 * One per-leaf arena. predictions is model -> query -> extracted pred.
 */
class LeafArena(
    val leafId: String,
    val modelIds: List<String>,
    val queryIds: List<Int>,
    val predictions: Map<String, Map<Int, String>>,
    val pairBudget: Int,                      // hard cap per pair (B_max)
    /**
     * Fitted Bradley-Terry log-strengths for this leaf, or empty before the first fit.
     * Used to order models when deciding which pairs are rank-adjacent.
     */
    val btScores: Map<String, Double> = emptyMap(),
) {
    val pairs: List<PairKey> = modelIds.flatMapIndexed { i, a ->
        modelIds.drop(i + 1).map { b -> ordered(a, b) }
    }
    val stats = HashMap<PairKey, PairStats>()
    val reserved = HashMap<PairKey, HashSet<Int>>()
    val completed = HashMap<PairKey, HashSet<Int>>()
    val pairExhausted = HashMap<PairKey, Boolean>()   // hit pairBudget unresolved, or no query left
    var state: LeafState = LeafState.ACTIVE

    /**
     * How many times each query has been judged anywhere in this leaf, across ALL pairs.
     *
     * `used(key)` is per-pair and cannot see that a question has already been judged by
     * ten other pairs in the same cell. This counter is what lets pickQuery spread the
     * budget over the question pool instead of re-judging the same few items.
     */
    val queryUseCount = HashMap<Int, Int>()

    fun noteQueryUsed(q: Int) {
        queryUseCount[q] = (queryUseCount[q] ?: 0) + 1
    }

    fun used(key: PairKey): Set<Int> =
        (reserved[key] ?: emptySet()) + (completed[key] ?: emptySet())
}

// ─── Active BT Racing Scheduler ──────────────────────────────────────────────

class ActiveBtRacingScheduler(
    private val alpha: Double = 0.05,        // confidence level
    private val nMin: Int = 5,                // per-pair warm-start guard
    /**
     * Pairs already retired domain-wide by the aggregate `gap > 2.5*sigma` gate.
     *
     * The scheduler stops sampling these, so anything that asks "is this pair done?"
     * must agree, or it waits on evidence that will never arrive. Passing the set in
     * rather than reaching for a global keeps this class testable in isolation.
     */
    private val externallyResolved: (String, PairKey) -> Boolean = { _, _ -> false },
) {

    /** Hoeffding radius with union bound over P pairs and Bmax peeks. */
    fun epsilon(n: Int, k: Int, bMax: Int): Double {
        if (n <= 0) return Double.POSITIVE_INFINITY
        val p = k * (k - 1) / 2
        return sqrt(ln(2.0 * p * bMax / alpha) / (2.0 * n))
    }

    // ── Exact binomial resolution ─────────────────────────────────────────────
    //
    // The RESOLUTION test is the exact two-sided binomial tail, not `epsilon`:
    // Hoeffding needs |phat - 0.5| > eps, and eps < 0.5 requires n > ~20 whatever the
    // data says, which realistic per-pair budgets never reach — every pair would run
    // to exhaustion. The exact tail is far tighter where it matters (a pair one model
    // wins outright resolves at n = 9 with Bonferroni over the adjacent pairs, against
    // ~23 for Hoeffding), and the correction is over the k-1 ADJACENT pairs actually
    // tested rather than all k(k-1)/2. `epsilon` is retained because `debt` uses it as
    // a continuous priority signal, where its looseness is harmless -- it orders
    // leaves, it does not decide anything.
    private fun logChoose(n: Int, k: Int): Double {
        var s = 0.0
        for (i in 1..k) s += ln((n - k + i).toDouble()) - ln(i.toDouble())
        return s
    }

    fun binomTwoSidedP(n: Int, successes: Int): Double {
        if (n <= 0) return 1.0
        val kk = minOf(successes, n - successes)
        var tail = 0.0
        for (i in 0..kk) tail += Math.exp(logChoose(n, i) + n * ln(0.5))
        return minOf(1.0, 2.0 * tail)
    }

    /**
     * Comparisons a pair has, counting those RESERVED earlier in this same batch.
     *
     * `stats` is refreshed between rounds, not within one. Without this the scheduler
     * re-reads a stale count on every iteration of the batch loop, concludes the same
     * pair is still the neediest, and schedules it again -- a leaf can pour its entire
     * share of a batch into a single pair before seeing any outcome. Counting
     * reservations makes the budget bind inside the batch and lets the next-neediest
     * pair be chosen, which is what the racing design intends.
     */
    fun effectiveN(a: LeafArena, key: PairKey): Int =
        (a.stats[key]?.n ?: 0) + (a.reserved[key]?.size ?: 0)

    /**
     * Model order used to decide which pairs are rank-adjacent.
     *
     * Prefers the fitted Bradley-Terry strengths; falls back to Copeland (summed win
     * rates) only before the first fit exists.
     *
     * WHY. Copeland weights every pair equally regardless of how much evidence it
     * carries: a pair with ONE comparison contributes exactly 0 or 1 to a model's
     * score, the same as a pair with thirty. Early in a run most pairs have one
     * comparison, so the order is dominated by coin flips and shuffles between rounds --
     * and since only rank-ADJACENT pairs are ever sampled, the set of pairs under test
     * churns with it. A leaf that satisfied the convergence criterion stops satisfying
     * it because different pairs became adjacent, not because anything got worse.
     *
     * A Bradley-Terry fit weights each pair by its comparison count, so a single
     * comparison moves a model slightly instead of several places, and the adjacency set
     * stabilises as evidence accumulates.
     */
    fun ranking(a: LeafArena): List<String> {
        if (a.btScores.isNotEmpty() && a.modelIds.any { (a.btScores[it] ?: 0.0) != 0.0 }) {
            return a.modelIds.sortedByDescending { a.btScores[it] ?: 0.0 }
        }
        val score = a.modelIds.associateWith { 0.0 }.toMutableMap()
        for ((key, s) in a.stats) {
            val (x, y) = key
            if (s.n == 0) continue
            val phat = s.sumX / s.n
            score[x] = score.getValue(x) + phat
            score[y] = score.getValue(y) + (1.0 - phat)
        }
        return score.toList().sortedByDescending { it.second }.map { it.first }
    }

    fun pairStatus(a: LeafArena, key: PairKey): String {
        if (a.pairExhausted[key] == true) return "PAIR_EXHAUSTED"
        // Settled by the confidence gate IN THIS LEAF: the scheduler already refuses to
        // sample it, so it must count as terminal here too — treated as UNRESOLVED, the
        // leaf would wait forever on a pair nothing will ever fund. The gate is keyed
        // per leaf; a domain-wide key would let one leaf's evidence retire the pair in
        // every other leaf.
        if (externallyResolved(a.leafId, key)) return "RESOLVED"
        val s = a.stats.getOrPut(key) { PairStats() }
        val n = effectiveN(a, key)
        // Exact binomial, Bonferroni over the (k-1) adjacent pairs actually tested.
        val wins = Math.round(s.sumX).toInt().coerceIn(0, s.n)
        val adjTests = maxOf(1, a.modelIds.size - 1)
        val resolved = (s.n >= nMin) && (binomTwoSidedP(s.n, wins) * adjTests < alpha)
        if (resolved) return "RESOLVED"
        if (n >= a.pairBudget) {
            // Only latch exhaustion on SETTLED counts. Reservations can be dropped if a
            // task fails, so latching on them would retire a pair that never ran.
            if (s.n >= a.pairBudget) a.pairExhausted[key] = true
            return "PAIR_EXHAUSTED"
        }
        return "UNRESOLVED"
    }

    /**
     * Warm start: until every pair has >=1 comparison, pick globally least-sampled.
     * After: rank-adjacent largest-overlap pair.
     */
    fun pickPair(a: LeafArena): PairKey? {
        if (a.state != LeafState.ACTIVE) return null
        if (a.modelIds.size < 2) { 
            a.state = LeafState.RESOLVED
            return null 
        }

        // Warm start tournament pass
        val unseeded = a.pairs.filter { effectiveN(a, it) == 0 && a.pairExhausted[it] != true }
        if (unseeded.isNotEmpty()) return unseeded.first()
        if (a.pairs.any { effectiveN(a, it) == 0 }) {
            a.state = LeafState.EXHAUSTED
            return null
        }

        val ranked = ranking(a)
        var best: PairKey? = null
        var bestOverlap = Double.NEGATIVE_INFINITY
        var allResolved = true

        for (k in 0 until ranked.size - 1) {
            val key = ordered(ranked[k], ranked[k + 1])
            when (pairStatus(a, key)) {
                "RESOLVED" -> { /* keep */ }
                "PAIR_EXHAUSTED" -> { allResolved = false }
                else -> {
                    allResolved = false
                    val s = a.stats.getValue(key)
                    val n = effectiveN(a, key)
                    val eps = epsilon(n, a.modelIds.size, a.pairBudget)
                    val phat = if (s.n > 0) s.sumX / s.n else 0.5
                    // effectiveN, so a pair already reserved to nMin this batch stops
                    // returning +infinity and the batch moves on to the next-neediest.
                    val overlap = if (n < nMin) Double.POSITIVE_INFINITY else eps - abs(phat - 0.5)
                    if (overlap > bestOverlap) { 
                        bestOverlap = overlap
                        best = key 
                    }
                }
            }
        }
        if (best == null) {
            a.state = if (allResolved) LeafState.RESOLVED else LeafState.EXHAUSTED
        }
        return best
    }

    /**
     * Query to judge next for this pair: disagreement first, then LEAST-USED across the
     * whole leaf. Answer-key-blind.
     *
     * Least-used must be counted across the LEAF, not per pair: `used` is per-pair, so a
     * per-pair minimum (e.g. lowest unused id) lets every pair in a leaf converge on the
     * same handful of low-numbered questions — the budget buys repetition rather than
     * breadth. That matters because rho is measured against ground-truth accuracy
     * computed on the questions the run actually judged; a small distinct-question count
     * makes that reference noise-dominated relative to the 2-4 point gaps between
     * adjacent models.
     *
     * Least-used-first spreads the budget over the pool while keeping the two properties
     * that matter: disagreement pairs are still preferred (a comparison where both models
     * gave the same answer carries little signal), and selection stays deterministic —
     * ties on use-count break by query id, so a re-run with the same seed reproduces.
     */
    fun pickQuery(a: LeafArena, key: PairKey): Int? {
        val used = a.used(key)
        val (x, y) = key
        val predX = a.predictions[x] ?: emptyMap()
        val predY = a.predictions[y] ?: emptyMap()
        val disagree = a.queryIds.filter { q -> q !in used && predX[q] != predY[q] && !predX[q].isNullOrBlank() && !predY[q].isNullOrBlank() }
        val pool = disagree.ifEmpty { a.queryIds.filter { it !in used } }
        // Least-used across the leaf, then lowest id. Not `minOrNull()`.
        return pool.minWithOrNull(
            compareBy({ a.queryUseCount[it] ?: 0 }, { it })
        )
    }

    fun debt(a: LeafArena): Double {
        if (a.state != LeafState.ACTIVE) return 0.0
        if (a.pairs.any { effectiveN(a, it) == 0 }) return Double.POSITIVE_INFINITY
        val ranked = ranking(a)
        var d = 0.0
        for (k in 0 until ranked.size - 1) {
            val key = ordered(ranked[k], ranked[k + 1])
            if (pairStatus(a, key) != "UNRESOLVED") continue
            val s = a.stats.getValue(key)
            val eps = epsilon(effectiveN(a, key), a.modelIds.size, a.pairBudget)
            val phat = if (s.n > 0) s.sumX / s.n else 0.5
            d += (eps - abs(phat - 0.5)).coerceAtLeast(0.0)
        }
        return d
    }

    fun selectNextBatch(
        targetNodes: List<GraphNode>,
        pairStats: Map<String, List<NodePairStats>>,
        models: List<String>,
        resultsMatrix: Map<Int, Map<String, ModelEvalResult>>,
        nodeToQueries: Map<String, List<Int>>,
        batchSize: Int,
        completedResults: List<QueryBenchmarkResult>,
        budgetPerPair: Int,
        btStates: Map<String, NodeBtState> = emptyMap()
    ): List<BtMatchTask> {
        // Build LeafArenas
        val arenas = targetNodes.map { node ->
            val leafId = node.id
            val queryIds = nodeToQueries[node.id] ?: emptyList()
            val predictions = models.associateWith { model ->
                queryIds.associateWith { qId ->
                    resultsMatrix[qId]?.get(model)?.pred ?: ""
                }
            }
            val leafArena = LeafArena(
                leafId, models, queryIds, predictions, budgetPerPair,
                btScores = btStates[node.id]?.btScores ?: emptyMap()
            )

            // Populate completed
            for (qr in completedResults) {
                val qId = qr.queryId
                for ((pairKeyStr, evals) in qr.pairEvaluations) {
                    val pairModels = pairKeyStr.split("_vs_")
                    if (pairModels.size != 2) continue
                    val key = ordered(pairModels[0], pairModels[1])
                    if (evals.any { it.nodeId == leafId }) {
                        if (leafArena.completed.getOrPut(key) { hashSetOf() }.add(qId)) {
                            leafArena.noteQueryUsed(qId)
                        }
                    }
                }
            }

            // Populate stats
            val nodePairs = pairStats[node.id] ?: emptyList()
            for (ps in nodePairs) {
                val key = ordered(ps.modelA, ps.modelB)
                val stats = leafArena.stats.getOrPut(key) { PairStats() }
                val isModelA = key.first == ps.modelA
                val winsFirst = if (isModelA) ps.winsA else ps.winsB
                stats.sumX = winsFirst + 0.5 * ps.ties
                stats.n = ps.totalComparisons.toInt()
            }

            leafArena
        }

        // ── Allocate the batch in proportion to each leaf's query pool ───────────────
        //
        // An equal share per ACTIVE leaf would be defensible for a PER-CELL fit, where
        // the cost of pinning every pair does not scale with cell size — but it is wrong
        // for the DOMAIN estimate, which pools sufficient statistics: cell weight there
        // follows comparison count, so equal shares let a small cell contribute far more
        // evidence per question than a large one.
        //
        // Quotas are proportional to pool size with a floor of 1, so no cell is starved
        // out of a batch entirely. If quotas are filled and the batch is not, a second
        // pass ignores them, so a domain whose large cells run dry still spends its full
        // budget rather than idling.
        val totalPool = arenas.sumOf { it.queryIds.size }.coerceAtLeast(1)
        val quota = HashMap<String, Int>()
        for (a in arenas) {
            quota[a.leafId] = maxOf(
                1,
                Math.round(batchSize.toDouble() * a.queryIds.size / totalPool).toInt()
            )
        }
        val taken = HashMap<String, Int>()

        val tasks = ArrayList<BtMatchTask>()
        while (tasks.size < batchSize) {
            val active = arenas.filter {
                it.state == LeafState.ACTIVE &&
                    (taken[it.leafId] ?: 0) < (quota[it.leafId] ?: 0)
            }.sortedByDescending { debt(it) }
            if (active.isEmpty()) {
                // QUOTAS HOLD. An earlier version dropped them here and let any still-active
                // leaf absorb the remainder, which undid most of the point: on history the
                // small cell still took 24.6% of comparisons against a 15.0% pool share
                // (ratio 1.64, down only from 1.82 under equal allocation).
                //
                // Large cells go inactive FIRST, which is what triggered the fallback. A
                // cell's capacity is 66 pairs x budget, and budget = clamp(pool/4, 8, 25)
                // flattens it -- a 38-question cell gets 9, a 20-question cell gets 8, so
                // capacity is 594 against 528. Proportional quotas then feed the large cell
                // 38 tasks a round against 20, so it fills its near-identical capacity in
                // roughly 15 rounds where the small one needs 26. Allocation scales with
                // pool size; capacity does not.
                //
                // Letting the batch come back short is the correct response: a domain whose
                // large cells are done has genuinely run out of proportionate work, and
                // topping the batch up from a small cell buys comparisons that over-weight
                // that cell in the pooled domain fit. Short batches shrink the round and the
                // run ends sooner, which is the honest signal.
                break
            }
            var progressed = false
            for (leaf in active) {
                if (tasks.size >= batchSize) break
                val key = pickPair(leaf) ?: continue
                val q = pickQuery(leaf, key)
                if (q == null) {
                    leaf.pairExhausted[key] = true
                    progressed = true
                    continue
                }
                if (leaf.reserved.getOrPut(key) { hashSetOf() }.add(q)) {
                    leaf.noteQueryUsed(q)
                }
                taken[leaf.leafId] = (taken[leaf.leafId] ?: 0) + 1
                tasks.add(
                    BtMatchTask(
                        nodeId = leaf.leafId,
                        modelA = key.first,
                        modelB = key.second,
                        queryIds = listOf(q.toString()),
                        priority = debt(leaf),
                        batchId = UUID.randomUUID().toString()
                    )
                )
                progressed = true
            }
            if (!progressed) break
        }
        return tasks
    }
}
