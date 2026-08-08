package taxonomy.service

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.arena.*
import taxonomy.dataset.ModelEvalResult
import taxonomy.model.GraphNode
import taxonomy.model.NodePairStats

/**
 * The scheduler must cap each pair at ITS OWN leaf's allowance, not at the run-global
 * `budgetPerPair`.
 *
 * WHAT THIS PINS. `TaxonomyBenchmarkService` seeds `BtStoppingPolicy.pairCustomBudgets`
 * from each leaf's query pool, precisely so the scheduler and the stopping policy agree on
 * when a pair is finished. `ActiveBtRacingScheduler` took only a
 * scalar and applied it to every leaf, so the seeding never reached the component that
 * decides what to sample: pairs were retired at the run-global number, which is computed
 * from the SMALLEST leaf and is therefore below every other leaf's allowance.
 *
 * The settled r8 batch shows the signature exactly — in all eight domains the largest
 * comparison count any (leaf, pair) reached equals that domain's run-global scalar
 * (math 7, physics 3, law 12, engineering 5, psychology 12, philosophy 12, history 10,
 * cs 6), while the seeded per-leaf budgets ran 8-25 under the clamp of the day. In the four
 * domains whose scalar sat
 * below n = 9 — the minimum at which the local binomial test can fire, unanimous and
 * Bonferroni-corrected over the M-1 adjacent pairs — not one pair resolved, which is what
 * the match history records.
 */
class SchedulerPairBudgetTest {

    private val models = listOf("model-A", "model-B")

    private fun leaf(id: String) = GraphNode(id = id, label = id, depth = 1)

    private fun matrix(queryIds: List<Int>): Map<Int, Map<String, ModelEvalResult>> =
        queryIds.associateWith { qId ->
            models.associateWith { m ->
                ModelEvalResult(
                    questionId = qId, modelName = m, category = "Math", questionText = "q$qId",
                    options = listOf("A", "B"), gtAnswer = "A",
                    // Distinct predictions so pickQuery's disagreement filter keeps the pool.
                    pred = if (m == "model-A") "A" else "B",
                    modelOutput = "", isCorrect = m == "model-A", isReserved = true
                )
            }
        }

    /** A pair at `n` comparisons, split so the binomial test cannot resolve it. */
    private fun statsAt(nodeId: String, n: Int) = mapOf(
        nodeId to listOf(
            NodePairStats(
                nodeId = nodeId, modelA = "model-A", modelB = "model-B",
                totalComparisons = n.toDouble(),
                winsA = n / 2.0, winsB = n - n / 2.0, ties = 0.0
            )
        )
    )

    // ── The defect, stated as the behaviour that must not come back ────────────────────

    @Test
    fun `pair past the run-global scalar but inside its leaf's allowance still schedules`() {
        // 40 held-out questions -> the leaf allows 40 comparisons per pair, past the global 3.
        val queryIds = (1..40).toList()
        val nodeToQueries = mapOf("leaf-1" to queryIds)
        val scheduler = ActiveBtRacingScheduler(alpha = 0.05, nMin = 5)

        fun batchWith(pairBudgetFor: ((String, PairKey) -> Int)?) = scheduler.selectNextBatch(
            targetNodes = listOf(leaf("leaf-1")),
            pairStats = statsAt("leaf-1", 3),      // exactly at the run-global cap
            models = models,
            resultsMatrix = matrix(queryIds),
            nodeToQueries = nodeToQueries,
            batchSize = 4,
            completedResults = emptyList(),
            budgetPerPair = 3,                     // the run-global scalar
            pairBudgetFor = pairBudgetFor
        )

        // Old wiring: the scalar is the only cap, the pair is retired at n = 3.
        assertTrue(
            batchWith(null).isEmpty(),
            "with only the run-global scalar the pair is exhausted at n=3 — this is the defect"
        )

        // Fixed wiring: the leaf's own allowance (40) governs, so sampling continues.
        val fixed = batchWith { _, _ -> BtStoppingPolicy(budgetPerPair = 3).leafBudgetPerPair(40) }
        assertFalse(
            fixed.isEmpty(),
            "at n=3 against a leaf budget of 40 the pair must still be schedulable"
        )
        assertTrue(fixed.all { it.nodeId == "leaf-1" })
    }

    @Test
    fun `two leaves with different pools get different caps in the same batch`() {
        // 40 questions -> budget 40 (a pair at n=40 is spent); 100 -> budget 100 (n=40 is not).
        val small = (1..40).toList()
        val large = (101..200).toList()
        val policy = BtStoppingPolicy(budgetPerPair = 3)
        assertEquals(40, policy.leafBudgetPerPair(small.size))
        assertEquals(100, policy.leafBudgetPerPair(large.size))

        val batch = ActiveBtRacingScheduler(alpha = 0.05, nMin = 5).selectNextBatch(
            targetNodes = listOf(leaf("small"), leaf("large")),
            pairStats = statsAt("small", 40) + statsAt("large", 40),
            models = models,
            resultsMatrix = matrix(small + large),
            nodeToQueries = mapOf("small" to small, "large" to large),
            batchSize = 8,
            completedResults = emptyList(),
            budgetPerPair = 3,
            pairBudgetFor = { leafId, _ ->
                policy.leafBudgetPerPair(if (leafId == "small") small.size else large.size)
            }
        )

        assertTrue(batch.isNotEmpty(), "the large leaf still has allowance at n=40")
        assertTrue(
            batch.none { it.nodeId == "small" },
            "the small leaf's pair is past its own budget of 40 and must be retired"
        )
        assertTrue(batch.all { it.nodeId == "large" })
    }

    // ── The wiring itself: what BtMatchScheduler hands the racing scheduler ────────────

    @Test
    fun `BtMatchScheduler honours the seeded per-leaf budget, not the global fallback`() {
        val queryIds = (1..40).toList()          // the leaf allows 40 per pair
        val nodeToQueries = mapOf("leaf-1" to queryIds)
        val policy = BtStoppingPolicy(budgetPerPair = 3)
        // Seed exactly as TaxonomyBenchmarkService does before a run.
        policy.pairCustomBudgets["leaf-1|model-A|model-B"] = policy.leafBudgetPerPair(queryIds.size)

        val scheduler = BtMatchScheduler(
            minQueriesForBenchmark = 1,
            queriesPerPair = 2,
            budgetPerPair = 3,                   // the run-global scalar that used to win
            stoppingPolicy = policy,
            seed = 42L
        )

        val batch = scheduler.selectNextBatch(
            targetNodes = listOf(leaf("leaf-1")),
            btStates = emptyMap(),
            pairStats = statsAt("leaf-1", 5),    // past the global 3, inside the leaf's 40
            models = models,
            resultsMatrix = matrix(queryIds),
            nodeToQueries = nodeToQueries,
            batchSize = 4,
            condition = "MAIN"
        )

        assertFalse(
            batch.isEmpty(),
            "MAIN must keep sampling a pair at n=5 when its leaf allows 10; an empty batch " +
                "means the run-global scalar reached the arena again"
        )
    }

    @Test
    fun `an unseeded caller keeps the run-global cap, which may exceed the leaf formula`() {
        // 9 questions -> the leaf allows 9 per pair, BELOW the run-global 12 here. Deriving a
        // fallback from the pool would silently cap this leaf at 9, which is how
        // BenchmarkE2EIntegrationTest caught the first attempt at this fix. Nothing is seeded,
        // so the global number must still govern.
        val queryIds = (1..9).toList()
        val policy = BtStoppingPolicy(budgetPerPair = 12)
        assertEquals(9, policy.leafBudgetPerPair(queryIds.size), "the cap is the pool itself")

        val scheduler = BtMatchScheduler(
            minQueriesForBenchmark = 1, queriesPerPair = 2, budgetPerPair = 12,
            stoppingPolicy = policy, seed = 42L
        )

        val batch = scheduler.selectNextBatch(
            targetNodes = listOf(leaf("leaf-1")),
            btStates = emptyMap(),
            pairStats = statsAt("leaf-1", 9),    // at the leaf's own cap, under the global 12
            models = models,
            resultsMatrix = matrix(queryIds),
            nodeToQueries = mapOf("leaf-1" to queryIds),
            batchSize = 2,
            condition = "MAIN"
        )

        assertFalse(
            batch.isEmpty(),
            "an unseeded caller must keep the run-global cap of 12, not drop to the formula's 8"
        )
    }

    @Test
    fun `a pair genuinely at its leaf's budget is still retired`() {
        val queryIds = (1..40).toList()          // budget 40
        val policy = BtStoppingPolicy(budgetPerPair = 3)
        policy.pairCustomBudgets["leaf-1|model-A|model-B"] = policy.leafBudgetPerPair(queryIds.size)

        val scheduler = BtMatchScheduler(
            minQueriesForBenchmark = 1, queriesPerPair = 2, budgetPerPair = 3,
            stoppingPolicy = policy, seed = 42L
        )

        val batch = scheduler.selectNextBatch(
            targetNodes = listOf(leaf("leaf-1")),
            btStates = emptyMap(),
            pairStats = statsAt("leaf-1", 40),   // exactly at the leaf's own budget
            models = models,
            resultsMatrix = matrix(queryIds),
            nodeToQueries = mapOf("leaf-1" to queryIds),
            batchSize = 4,
            condition = "MAIN"
        )

        assertTrue(
            batch.isEmpty(),
            "the fix must raise the cap to the leaf's allowance, not remove the cap"
        )
    }
}
