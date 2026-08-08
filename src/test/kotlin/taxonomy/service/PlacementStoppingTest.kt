package taxonomy.service

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.arena.*
import taxonomy.dataset.ModelEvalResult
import taxonomy.model.GraphNode
import taxonomy.model.NodeBtState
import taxonomy.model.NodePairStats

/**
 * Placement stopping wired into the scheduler: a cell stops when its ORDER is decided, not
 * when a comparison count is reached.
 *
 * The property that matters is that cost now follows the board's geometry. A cell whose models
 * are strung out settles quickly; a cell whose models are bunched keeps being funded — with no
 * constant anywhere deciding either. The same rule has to hold in the stopping policy as in the
 * scheduler, or a leaf waits on evidence nothing will schedule.
 */
class PlacementStoppingTest {

    private val models = listOf("m-a", "m-b", "m-c", "m-d")

    private fun leaf(id: String = "leaf-1") = GraphNode(id = id, label = id, depth = 1)

    private fun queries(n: Int) = (1..n).toList()

    private fun matrix(qs: List<Int>) = qs.associateWith { q ->
        models.associateWith { m ->
            ModelEvalResult(
                questionId = q, modelName = m, category = "Math", questionText = "q$q",
                options = listOf("A", "B"), gtAnswer = "A",
                pred = if (m.hashCode() % 2 == 0) "A" else "B",
                modelOutput = "", isCorrect = true, isReserved = true
            )
        }
    }

    /**
     * Every pair at [n] comparisons, with win counts generated FROM the strengths.
     *
     * Must be Bradley-Terry consistent: a flat "the stronger model wins 75%" fixture implies a
     * different strength for the same model against every opponent, so no single position
     * explains the record and the placement posterior is correctly confused by it.
     */
    private fun stats(nodeId: String, thetas: Map<String, Double>, n: Int): Map<String, List<NodePairStats>> {
        val order = thetas.entries.sortedByDescending { it.value }.map { it.key }
        val out = ArrayList<NodePairStats>()
        for (i in order.indices) for (j in i + 1 until order.size) {
            val a = order[i]
            val b = order[j]
            val p = 1.0 / (1.0 + kotlin.math.exp(-(thetas.getValue(a) - thetas.getValue(b))))
            val winsA = Math.round(n * p).toDouble()
            out += NodePairStats(
                nodeId = nodeId, modelA = a, modelB = b,
                totalComparisons = n.toDouble(), winsA = winsA, winsB = n - winsA, ties = 0.0
            )
        }
        return mapOf(nodeId to out)
    }

    private fun btState(nodeId: String, thetas: Map<String, Double>) = mapOf(
        nodeId to NodeBtState(
            nodeId = nodeId, btScores = thetas,
            stdErrors = thetas.mapValues { 0.3 },
            fitVersion = 1, totalComparisons = 100, lastFitAt = 0L
        )
    )

    // Adjacent gap 1.2: at n = 12 each adjacent pair sits at 9 wins of 12, where the exact
    // binomial with Bonferroni over M-1 gives p = 0.44 — nowhere near resolved. Placement still
    // pins every model, because it reads each model's record against ALL its opponents rather
    // than one pair at a time. That difference is the point of the rule.
    private val spread = mapOf("m-a" to 1.8, "m-b" to 0.6, "m-c" to -0.6, "m-d" to -1.8)
    private val bunched = mapOf("m-a" to 0.15, "m-b" to 0.05, "m-c" to -0.05, "m-d" to -0.15)

    // ── The rule fires on the decision, not the count ─────────────────────────────────

    @Test
    fun `a well separated cell stops while its pairs are far under any budget`() {
        val qs = queries(60)
        val policy = BtStoppingPolicy(budgetPerPair = 40, placement = ModelPlacement())
        val scheduler = BtMatchScheduler(
            minQueriesForBenchmark = 1, queriesPerPair = 2, budgetPerPair = 40,
            stoppingPolicy = policy, seed = 42L
        )

        val batch = scheduler.selectNextBatch(
            targetNodes = listOf(leaf()),
            btStates = btState("leaf-1", spread),
            pairStats = stats("leaf-1", spread, n = 12),   // 12 of an allowed 40
            models = models,
            resultsMatrix = matrix(qs),
            nodeToQueries = mapOf("leaf-1" to qs),
            batchSize = 6,
            condition = "MAIN"
        )

        assertTrue(
            batch.isEmpty(),
            "the order is decided at n=12 with a budget of 40 — the count must stop deciding"
        )
    }

    @Test
    fun `a bunched cell keeps being funded at the same comparison count`() {
        // Identical counts, identical budget, identical everything except the spacing of the
        // fitted strengths. This is the whole claim: cost tracks the geometry.
        val qs = queries(60)
        val policy = BtStoppingPolicy(budgetPerPair = 40, placement = ModelPlacement())
        val scheduler = BtMatchScheduler(
            minQueriesForBenchmark = 1, queriesPerPair = 2, budgetPerPair = 40,
            stoppingPolicy = policy, seed = 42L
        )

        val batch = scheduler.selectNextBatch(
            targetNodes = listOf(leaf()),
            btStates = btState("leaf-1", bunched),
            pairStats = stats("leaf-1", bunched, n = 12),
            models = models,
            resultsMatrix = matrix(qs),
            nodeToQueries = mapOf("leaf-1" to qs),
            batchSize = 6,
            condition = "MAIN"
        )

        assertFalse(
            batch.isEmpty(),
            "models within 0.3 logits of each other are not placed at n=12; work must continue"
        )
    }

    @Test
    fun `slack buys the bunched cell its way out`() {
        val qs = queries(60)

        fun batchAtSlack(slack: Int): List<taxonomy.model.BtMatchTask> {
            val policy = BtStoppingPolicy(
                budgetPerPair = 40, placement = ModelPlacement(), placementSlack = slack
            )
            return BtMatchScheduler(
                minQueriesForBenchmark = 1, queriesPerPair = 2, budgetPerPair = 40,
                stoppingPolicy = policy, seed = 42L
            ).selectNextBatch(
                targetNodes = listOf(leaf()),
                btStates = btState("leaf-1", bunched),
                pairStats = stats("leaf-1", bunched, n = 12),
                models = models,
                resultsMatrix = matrix(qs),
                nodeToQueries = mapOf("leaf-1" to qs),
                batchSize = 6,
                condition = "MAIN"
            )
        }

        assertFalse(batchAtSlack(0).isEmpty(), "exact placement is still open")
        assertTrue(
            batchAtSlack(3).isEmpty(),
            "with three ranks of slack even a bunched board is settled — slack is the knob"
        )
    }

    // ── The scheduler and the policy must agree ──────────────────────────────────────

    @Test
    fun `the stopping policy calls the same cell converged that the scheduler abandons`() {
        val qs = queries(60)
        val policy = BtStoppingPolicy(budgetPerPair = 40, placement = ModelPlacement())
        val pairStats = stats("leaf-1", spread, n = 12)
        val btStates = btState("leaf-1", spread)

        val batch = BtMatchScheduler(
            minQueriesForBenchmark = 1, queriesPerPair = 2, budgetPerPair = 40,
            stoppingPolicy = policy, seed = 42L
        ).selectNextBatch(
            targetNodes = listOf(leaf()), btStates = btStates, pairStats = pairStats,
            models = models, resultsMatrix = matrix(qs),
            nodeToQueries = mapOf("leaf-1" to qs), batchSize = 6, condition = "MAIN"
        )

        val converged = policy.isLeafConverged(
            "leaf-1", btStates, pairStats, models, mapOf("leaf-1" to qs), "MAIN"
        )

        assertTrue(batch.isEmpty(), "scheduler has nothing to schedule")
        assertTrue(converged, "policy must agree the leaf is done, or the run waits forever")
    }

    // ── Off by default ───────────────────────────────────────────────────────────────

    @Test
    fun `opting out of placement restores the count-based path`() {
        val qs = queries(60)
        val policy = BtStoppingPolicy(budgetPerPair = 40, placement = null)   // opted out
        val scheduler = BtMatchScheduler(
            minQueriesForBenchmark = 1, queriesPerPair = 2, budgetPerPair = 40,
            stoppingPolicy = policy, seed = 42L
        )

        val batch = scheduler.selectNextBatch(
            targetNodes = listOf(leaf()),
            btStates = btState("leaf-1", spread),
            pairStats = stats("leaf-1", spread, n = 12),
            models = models,
            resultsMatrix = matrix(qs),
            nodeToQueries = mapOf("leaf-1" to qs),
            batchSize = 6,
            condition = "MAIN"
        )

        assertFalse(
            batch.isEmpty(),
            "the count-based path must be untouched: n=12 is under the budget of 40, so it runs"
        )
    }

    @Test
    fun `placedModels needs at least two anchors before it calls anything settled`() {
        val arena = LeafArena("leaf-1", listOf("m-a", "m-b"), queries(10), emptyMap(), 10)
        arena.stats[ordered("m-a", "m-b")] = PairStats(sumX = 8.0, n = 8)
        val placed = placedModels(
            ModelPlacement(), listOf("m-a", "m-b"),
            mapOf("m-a" to 1.0, "m-b" to -1.0), arena.stats
        )
        assertTrue(placed.isEmpty(), "two models define no bounded slot; nothing may be settled")
    }
}
