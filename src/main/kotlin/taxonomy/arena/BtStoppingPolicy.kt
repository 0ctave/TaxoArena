package taxonomy.arena

import taxonomy.model.NodeBtState
import taxonomy.model.NodePairStats
import kotlin.math.abs

class BtStoppingPolicy(
    val maxRounds: Int = 20,
    val minComparisonsPerLeaf: Int = 8,
    val targetLeafConvergenceFraction: Double = 0.65,
    val stabilityRounds: Int = 2,
    val separationThreshold: Double = 1.0,
    val minTotalComparisons: Int = 20,
    val budgetPerPair: Int,
    /**
     * Placement stopping, when enabled. MUST match what the scheduler was given: the scheduler
     * stops sampling a pair whose models are both placed, so if this policy does not also count
     * that pair terminal the leaf waits forever on evidence nothing will fund. That is exactly
     * the disagreement the per-leaf budget defect produced in the other direction.
     */
    val placement: ModelPlacement? = ModelPlacement(),
    /**
     * Rank slots a placement claim may span. 2, because the measured boards cluster: the three
     * frontier models sit within 0.06 logits of each other in the settled batch, so "top tier,
     * order undetermined" is both the honest claim and the only affordable one. At 0 the rule
     * fired in one cell of 51 and saved nothing.
     */
    val placementSlack: Int = 2
) {
    private val leafRankHistory = mutableMapOf<String, ArrayDeque<List<String>>>()

    /**
     * Pairs the confidence gate has settled, keyed `"nodeId|modelA|modelB"` — PER CELL.
     *
     * WHAT THIS REPLACED, AND WHY (2026-07-31). The set used to be keyed on the pair alone and
     * populated from the AGGREGATE leaderboard: if the pooled gap between two models exceeded
     * 2.5 sigma, the pair was suppressed in every cell at once. That inverts the experiment.
     * Whether a pair's ordering is the same in every cell is the question the per-cell arena
     * exists to ask, and a cell where the ordering reverses can only reveal it by comparing
     * those two models IN THAT CELL. Retiring the pair everywhere on the strength of the pooled
     * result assumes the null and then reports it cannot be rejected.
     *
     * Measured on the 2026-07-31 history run: 45 of 66 pairs suppressed after round 1, 57 of 66
     * by round 4, and NOT ONE of the 44 adjacent pairs across the four cells met the local
     * resolution test. Three cells were nonetheless declared converged, because
     * [isLeafConverged] counted a globally suppressed pair as terminal. The run stopped for want
     * of schedulable work and recorded it as convergence.
     *
     * The gate is now evaluated against each cell's own theta and standard errors, so a pair
     * settled in one cell keeps being sampled in another until that cell settles it too. It is
     * still a real local criterion, so it may legitimately mark a pair terminal in its own cell.
     */
    val resolvedPairs = mutableSetOf<String>()

    fun isPairResolved(nodeId: String, mA: String, mB: String): Boolean =
        resolvedPairs.contains("$nodeId|${minOf(mA, mB)}|${maxOf(mA, mB)}")
    val pairCustomBudgets = mutableMapOf<String, Int>()

    /**
     * Comparisons a single pair may accumulate inside one leaf: the leaf's own question pool,
     * which is the only real bound — a pair cannot be judged on more distinct questions than
     * exist.
     *
     * WHY THIS IS NO LONGER A FORMULA (2026-08-08). It used to be `(pool / 4).coerceIn(8, 25)`,
     * and every part of that was a guess doing a job the stopping rule should do. The ceiling
     * of 25 was meant to stop a large leaf buying evidence it did not need; the floor of 8 was
     * meant to keep the binomial test reachable, and did not even manage that — resolution
     * needs n >= 9 at eight models, so the floor sat below the threshold it existed to clear.
     * Worse, both numbers decided how much evidence a cell got WITHOUT looking at whether the
     * cell's ordering was in doubt, which is the only thing that should decide it.
     *
     * Placement stopping now answers that question directly: a cell is finished when every
     * model's rank slot is pinned, which costs what the local crowding demands and nothing
     * more. A well-separated cell stops far below this cap; a bunched one keeps going until it
     * earns its position or runs out of questions. See [placement] and `placedModels`.
     *
     * What remains here is a backstop, not a policy. [budgetPerPair] still applies when the
     * leaf's pool is unknown.
     */
    fun leafBudgetPerPair(leafQueryCount: Int): Int =
        if (leafQueryCount <= 0) budgetPerPair else leafQueryCount

    // PUBLIC — called by both shouldStop() and BtMatchScheduler
    fun isLeafConverged(
        nodeId: String,
        btStates: Map<String, NodeBtState>,
        pairStats: Map<String, List<NodePairStats>>,
        models: List<String>,
        nodeToQueries: Map<String, List<Int>> = emptyMap(),
        condition: String = "LEGACY_MAIN"
    ): Boolean {
        val numPairs = models.size * (models.size - 1) / 2
        val available = nodeToQueries[nodeId]?.size ?: 0
        val maxPossible = if (available > 0) available * numPairs else 0

        if (condition.equals("ROUND_ROBIN", ignoreCase = true) || condition.equals("RANDOM_SCHEDULER", ignoreCase = true)) {
            val liveTotalComparisons = (pairStats[nodeId] ?: emptyList()).sumOf { it.totalComparisons }
            return liveTotalComparisons >= maxPossible
        }

        if (condition.equals("MAIN", ignoreCase = true)) {
            val queryIds = nodeToQueries[nodeId] ?: emptyList()
            val leafBudget = leafBudgetPerPair(queryIds.size)
            val leafArena = LeafArena(nodeId, models, queryIds, emptyMap(), leafBudget)

            val nodePairs = pairStats[nodeId] ?: emptyList()
            for (ps in nodePairs) {
                val key = ordered(ps.modelA, ps.modelB)
                val stats = leafArena.stats.getOrPut(key) { PairStats() }
                val isModelA = key.first == ps.modelA
                val winsFirst = if (isModelA) ps.winsA else ps.winsB
                stats.sumX = winsFirst + 0.5 * ps.ties
                stats.n = ps.totalComparisons.toInt()
            }

            // Exact two-sided binomial tail against p = 0.5, Bonferroni-corrected over
            // the (k-1) ADJACENT pairs this test is actually applied to — only adjacent
            // pairs are tested below, so a union bound over all k(k-1)/2 pairs would
            // over-correct by ~6x. The exact tail is used because it is far tighter than
            // a Hoeffding bound in the lopsided regime that matters here: a unanimous
            // pair resolves at 9 comparisons where Hoeffding cannot fire before ~23,
            // which typical per-pair budgets never reach. Adjacent pairs are the CLOSEST
            // pairs by construction, so most still terminate by exhaustion rather than
            // resolution — the test is honest and occasionally useful; it does not make
            // convergence easy.
            fun logChoose(n: Int, k: Int): Double {
                var s = 0.0
                for (i in 1..k) s += Math.log((n - k + i).toDouble()) - Math.log(i.toDouble())
                return s
            }
            fun binomTwoSidedP(n: Int, successes: Int): Double {
                if (n <= 0) return 1.0
                val kk = Math.min(successes, n - successes)
                var tail = 0.0
                for (i in 0..kk) tail += Math.exp(logChoose(n, i) + n * Math.log(0.5))
                return Math.min(1.0, 2.0 * tail)
            }
            val adjacentTests = Math.max(1, models.size - 1)

            // Rank on the fitted Bradley-Terry strengths, falling back to Copeland only
            // before a fit exists. This MUST match ActiveBtRacingScheduler.ranking(): the
            // scheduler samples rank-adjacent pairs and this decides whether those pairs
            // are terminal, so if the two order models differently they are testing
            // different pairs and the leaf can never satisfy a criterion the scheduler is
            // not working toward. Copeland gives a pair with one comparison the same
            // weight as a pair with thirty, which made the order -- and therefore the
            // adjacency set -- churn between rounds; see the note on that function.
            val leafBt = btStates[nodeId]?.btScores ?: emptyMap()
            val ranked = if (leafBt.isNotEmpty() && models.any { (leafBt[it] ?: 0.0) != 0.0 }) {
                models.sortedByDescending { leafBt[it] ?: 0.0 }
            } else {
                val score = models.associateWith { 0.0 }.toMutableMap()
                for ((key, s) in leafArena.stats) {
                    val (x, y) = key
                    if (s.n == 0) continue
                    val phat = s.sumX / s.n
                    score[x] = score.getValue(x) + phat
                    score[y] = score.getValue(y) + (1.0 - phat)
                }
                score.toList().sortedByDescending { it.second }.map { it.first }
            }

            if (ranked.size < 2) return true

            if (leafArena.pairs.any { (leafArena.stats[it]?.n ?: 0) == 0 }) {
                return false
            }

            // Placement stopping: the cell is finished when every model's position in its order
            // is pinned to the required precision. Read the same way the scheduler reads it, so
            // both agree on which pairs are still worth funding.
            val placed = placement?.let {
                placedModels(it, models, leafBt, leafArena.stats, placementSlack)
            } ?: emptySet()
            if (placement != null && placed.isNotEmpty() && placed.containsAll(models)) return true

            var allTerminal = true
            for (k in 0 until ranked.size - 1) {
                val key = ordered(ranked[k], ranked[k + 1])
                val s = leafArena.stats[key] ?: PairStats()
                // sumX carries half-weighted ties, so round to the nearest whole win count
                // for the exact tail; ties push it toward n/2 and away from significance,
                // which is the conservative direction.
                val wins = Math.round(s.sumX).toInt().coerceIn(0, s.n)
                val p = binomTwoSidedP(s.n, wins) * adjacentTests
                val resolved = (s.n >= 5) && (p < 0.05)
                // Read the SAME per-(leaf, pair) budget the scheduler enforces, defaulting
                // to this leaf's budget. Comparing against the run-global `budgetPerPair`
                // would deadlock every pair the scheduler has retired: marking a pair
                // STABLE or IRRESOLVABLE sets its custom budget down to its current
                // comparison count and stops sampling it, so `n` freezes below the global
                // budget, `exhausted` never fires, and the leaf can never converge.
                val pairBudget = pairCustomBudgets.getOrDefault(
                    "$nodeId|${key.first}|${key.second}", leafBudget
                )
                // A pair the gate has settled IN THIS CELL stops being sampled here, so it
                // must count as terminal here too; leaving it UNRESOLVED deadlocks the leaf
                // on a pair nothing will fund. The gate key carries the cell id (see
                // [resolvedPairs]) — keyed on the pair alone, this line would let a cell
                // converge on evidence gathered somewhere else.
                val gateDone = isPairResolved(nodeId, key.first, key.second)
                val bothPlaced = key.first in placed && key.second in placed
                val exhausted = gateDone || bothPlaced || s.n >= pairBudget
                if (!resolved && !exhausted) {
                    allTerminal = false
                    break
                }
            }
            return allTerminal
        }

        val state = btStates[nodeId] ?: return false

        val targetLimit = if (maxPossible > 0) {
            maxOf(1, minOf(kotlin.math.ceil(budgetPerPair.toDouble() * numPairs / 2.0).toInt(), (maxPossible * 0.9).toInt()))
        } else {
            maxOf(1, kotlin.math.ceil(budgetPerPair.toDouble() * numPairs / 2.0).toInt())
        }

        val liveTotalComparisons = (pairStats[nodeId] ?: emptyList()).sumOf { it.totalComparisons }
        val dataExhausted = liveTotalComparisons >= targetLimit
        if (dataExhausted) return true

        if (liveTotalComparisons < minComparisonsPerLeaf) return false

        val allPairs = models.flatMapIndexed { i, mA -> models.drop(i + 1).map { mB -> mA to mB } }
        val informativePairs = allPairs.filter { (mA, mB) ->
            val pairKey = "${minOf(mA, mB)}|${maxOf(mA, mB)}"
            if (isPairResolved(nodeId, mA, mB)) return@filter false

            val ps = (pairStats[nodeId] ?: emptyList()).firstOrNull {
                (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
            }
            val nij = ps?.totalComparisons?.toInt() ?: 0
            if (nij < 2) return@filter true  // bootstrap not done -> still informative

            // NEW: if this pair has exhausted its budget, it's resolved regardless of gap
            val budget = pairCustomBudgets.getOrDefault("${nodeId}|$pairKey", budgetPerPair).coerceAtLeast(1)
            if (nij >= budget) return@filter false  // budget-exhausted → accepted as resolved

            val si = state.btScores[mA] ?: 0.0
            val sj = state.btScores[mB] ?: 0.0
            val seA = state.stdErrors[mA] ?: 10.0
            val seB = state.stdErrors[mB] ?: 10.0
            abs(si - sj) < 3.0 * (seA + seB)
        }

        // All remaining informative pairs resolved -> leaf is done
        if (informativePairs.isEmpty()) return true

        // Coverage check only on informative pairs
        val minPerPair = (minComparisonsPerLeaf / models.size).coerceAtLeast(1)
        val informativePairsCovered = informativePairs.all { (mA, mB) ->
            val ps = (pairStats[nodeId] ?: emptyList()).firstOrNull {
                (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
            }
            (ps?.totalComparisons?.toInt() ?: 0) >= minPerPair
        }
        if (!informativePairsCovered) return false

        // Top-2 separation
        val ranked = state.btScores.entries.sortedByDescending { it.value }
        if (ranked.size < 2) return true
        val gap = ranked[0].value - ranked[1].value
        val combinedSE = (state.stdErrors[ranked[0].key] ?: 10.0) +
                         (state.stdErrors[ranked[1].key] ?: 10.0)
        return gap > separationThreshold * combinedSE
    }

    fun shouldStop(
        btStates: Map<String, NodeBtState>,
        pairStats: Map<String, List<NodePairStats>>,
        targetLeafIds: Set<String>,
        models: List<String>,
        round: Int,
        totalComparisons: Int,
        nodeToQueries: Map<String, List<Int>> = emptyMap(),
        condition: String = "LEGACY_MAIN",
        mainConditionTotalComparisons: Int = 72,
        /**
         * Distinct judge calls this arm has spent, as opposed to [totalComparisons], which is
         * leaf-credited and counts one verdict once per cell that admits its question.
         *
         * The two diverge under multi-membership, and they diverge ASYMMETRICALLY between
         * the arms: MAIN spreads its questions over many cells, so a shared question is
         * credited several times, while C5 has a single cell and cannot inflate. Matching
         * the arms on the leaf-credited number would therefore hand C5 more real judge
         * calls than MAIN — extra evidence for the arm the contrast is measured against,
         * biasing Delta rho against MAIN by construction.
         *
         * Budget parity is a claim about judging cost, so it is enforced on verdicts.
         */
        verdictsThisArm: Int = 0
    ): Boolean {
        // ── Arm matching ──────────────────────────────────────────────────────────
        // C5 stops at MAIN's verdict count instead of running its own convergence rule
        // to a different total. Delta rho compares the two arms' rank correlation
        // against ground truth; an arm with less evidence has a noisier Bradley-Terry
        // fit and therefore a depressed rho, so any difference in arm size biases the
        // contrast toward whichever arm got more data. Matching the totals removes the
        // threat by construction. MAIN must run first; TaxonomyBenchmarkService captures
        // its total when it finishes and passes it here. RANDOM_SCHEDULER is matched the
        // same way.
        if (condition.equals("RANDOM_SCHEDULER", ignoreCase = true) ||
            condition.equals("C5", ignoreCase = true) ||
            condition.equals("GENERIC_PAIRV2", ignoreCase = true)
        ) {
            // Verdicts, not leaf-credited comparisons — see `verdictsThisArm`.
            return verdictsThisArm >= mainConditionTotalComparisons
        }
        if (round >= maxRounds) return true
        if (condition.equals("ROUND_ROBIN", ignoreCase = true)) return false
        if (totalComparisons < minTotalComparisons) return false
        if (targetLeafIds.isEmpty()) return false

        if (round >= maxRounds - 3) {
            // Last 3 rounds: stop if at least 50% are structurally converged
            // (even without rank stability) — prevents infinite runs
            val structConv = targetLeafIds.count { leafId ->
                isLeafConverged(leafId, btStates, pairStats, models, nodeToQueries, condition)
            }
            if (structConv.toDouble() / targetLeafIds.size >= 0.50) return true
        }

        val totalWeight = targetLeafIds.sumOf { leafId ->
            (nodeToQueries[leafId]?.size ?: 1).toDouble()
        }
        var weightedConverged = 0.0
        for (leafId in targetLeafIds) {
            val state = btStates[leafId] ?: continue

            // Rank stability check
            val currentRank = state.btScores.entries.sortedByDescending { it.value }.map { it.key }
            val history = leafRankHistory.getOrPut(leafId) { ArrayDeque() }
            history.addLast(currentRank)
            if (history.size > stabilityRounds) history.removeFirst()

            val rankStable = history.size >= stabilityRounds && history.all { it == currentRank }
            val structurallyConverged = isLeafConverged(leafId, btStates, pairStats, models, nodeToQueries, condition)

            val allPairs = models.flatMapIndexed { i, mA -> models.drop(i + 1).map { mB -> mA to mB } }
            // NEW: irresolvable-only leaf — rank noise from tie pairs should not block
            val allPairsResolved = allPairs.all { (mA, mB) ->
                val pk = "${minOf(mA, mB)}|${maxOf(mA, mB)}"
                isPairResolved(leafId, mA, mB) ||
                (pairStats[leafId] ?: emptyList()).firstOrNull {
                    (it.modelA == mA && it.modelB == mB) || (it.modelA == mB && it.modelB == mA)
                }?.let { ps ->
                    ps.totalComparisons.toInt() >= pairCustomBudgets.getOrDefault("$leafId|$pk", budgetPerPair)
                } ?: false
            }

            val leafWeight = (nodeToQueries[leafId]?.size ?: 1).toDouble()
            if ((rankStable || allPairsResolved) && structurallyConverged) {
                weightedConverged += leafWeight
            }
        }

        return if (totalWeight > 0.0) weightedConverged / totalWeight >= targetLeafConvergenceFraction else false
    }
}
