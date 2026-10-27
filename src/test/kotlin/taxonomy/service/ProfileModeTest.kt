package taxonomy.service

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.arena.*
import taxonomy.model.GraphNode
import taxonomy.model.NodePairStats
import kotlin.math.exp
import kotlin.random.Random

/**
 * PROFILE mode: stop on SE targets per model x stratum, never on rank decisions.
 *
 * The decision-mode rules (placement, binomial resolution, 2.5-sigma gate) are what
 * starved margin evidence in the x8/x12 runs; these tests pin that profile mode
 * (a) refuses to resolve pairs on order, (b) converges exactly when the stratum's
 * SEs meet the target, and (c) a full simulated tournament terminates with every
 * stratum at target rather than at a rank decision.
 */
class ProfileModeTest {

    private fun targets(seTarget: Double = 0.5) = ProfileTargets(
        seTarget = seTarget,
        leafToStratum = mapOf("leaf-1" to "s1", "leaf-2" to "s1", "leaf-3" to "s2")
    )

    @Test
    fun `stratum is never converged before a fit exists`() {
        val prof = targets()
        assertFalse(prof.converged("s1"))
        assertEquals(Double.MAX_VALUE, prof.worstSe("s1"))
        assertEquals(1.0, prof.deficit("s1", "m1"), 1e-12)
    }

    @Test
    fun `stratum converges exactly when every model meets the target`() {
        val prof = targets(seTarget = 0.5)
        prof.seByStratum = mapOf("s1" to mapOf("a" to 0.4, "b" to 0.51))
        assertFalse(prof.converged("s1"))
        prof.seByStratum = mapOf("s1" to mapOf("a" to 0.4, "b" to 0.5))
        assertTrue(prof.converged("s1"))
        assertEquals(0.0, prof.stratumDeficit("s1"), 1e-12)
    }

    @Test
    fun `poolPairStats merges reversed orientations correctly`() {
        val pooled = ProfileTargets.poolPairStats(listOf(
            NodePairStats("l1", "alpha", "beta", winsA = 3.0, winsB = 1.0, ties = 2.0, totalComparisons = 6.0),
            NodePairStats("l2", "beta", "alpha", winsA = 2.0, winsB = 4.0, ties = 0.0, totalComparisons = 6.0)
        ))
        assertEquals(1, pooled.size)
        val p = pooled[0]
        assertEquals("alpha", p.modelA)
        assertEquals(7.0, p.winsA, 1e-9)   // 3 direct + 4 from the reversed row
        assertEquals(3.0, p.winsB, 1e-9)   // 1 direct + 2 from the reversed row
        assertEquals(12.0, p.totalComparisons, 1e-9)
    }

    @Test
    fun `profile pairStatus never resolves on a lopsided record`() {
        val prof = targets()
        val sched = ActiveBtRacingScheduler(profile = prof)
        val arena = LeafArena("leaf-1", listOf("a", "b"), (1..50).toList(), emptyMap(), 40)
        // 20-0: decision mode would binomial-resolve this instantly.
        arena.stats[ordered("a", "b")] = PairStats(sumX = 20.0, n = 20)
        assertEquals("UNRESOLVED", sched.pairStatus(arena, ordered("a", "b")))
        // Budget spent -> exhausted, and the latch sticks.
        arena.stats[ordered("a", "b")] = PairStats(sumX = 40.0, n = 40)
        assertEquals("PAIR_EXHAUSTED", sched.pairStatus(arena, ordered("a", "b")))
        assertTrue(arena.pairExhausted[ordered("a", "b")] == true)
        // Converged stratum -> RESOLVED regardless of counts.
        val arena2 = LeafArena("leaf-2", listOf("a", "b"), (1..50).toList(), emptyMap(), 40)
        arena2.stats[ordered("a", "b")] = PairStats(sumX = 1.0, n = 2)
        prof.seByStratum = mapOf("s1" to mapOf("a" to 0.1, "b" to 0.1))
        assertEquals("RESOLVED", sched.pairStatus(arena2, ordered("a", "b")))
    }

    @Test
    fun `profile pickPair prefers the pair containing the neediest model`() {
        val prof = targets()
        prof.seByStratum = mapOf("s1" to mapOf("a" to 0.5, "b" to 0.5, "c" to 2.0))
        val sched = ActiveBtRacingScheduler(profile = prof)
        val arena = LeafArena("leaf-1", listOf("a", "b", "c"), (1..60).toList(), emptyMap(), 50)
        // Equal evidence everywhere, balanced records: only the deficit differs.
        for (p in arena.pairs) arena.stats[p] = PairStats(sumX = 3.0, n = 6)
        val pick = sched.pickPair(arena)!!
        assertTrue("c" in listOf(pick.first, pick.second),
            "expected a pair containing the max-deficit model, got $pick")
    }

    @Test
    fun `policy isLeafConverged in profile mode follows stratum state and exhaustion`() {
        val prof = targets(seTarget = 0.5)
        val policy = BtStoppingPolicy(budgetPerPair = 10, profile = prof)
        val models = listOf("a", "b")
        val queries = mapOf("leaf-1" to (1..10).toList())
        policy.pairCustomBudgets["leaf-1|a|b"] = 10
        val open = mapOf("leaf-1" to listOf(
            NodePairStats("leaf-1", "a", "b", winsA = 2.0, winsB = 1.0, ties = 0.0, totalComparisons = 3.0)))
        assertFalse(policy.isLeafConverged("leaf-1", emptyMap(), open, models, queries, "MAIN"))
        // Stratum reaches target -> converged.
        prof.seByStratum = mapOf("s1" to mapOf("a" to 0.3, "b" to 0.3))
        assertTrue(policy.isLeafConverged("leaf-1", emptyMap(), open, models, queries, "MAIN"))
        // Pool exhaustion converges the leaf even when the stratum is still open.
        prof.seByStratum = emptyMap()
        val spent = mapOf("leaf-1" to listOf(
            NodePairStats("leaf-1", "a", "b", winsA = 6.0, winsB = 4.0, ties = 0.0, totalComparisons = 10.0)))
        assertTrue(policy.isLeafConverged("leaf-1", emptyMap(), spent, models, queries, "MAIN"))
    }

    @Test
    fun `selectTargetNodes keeps unconverged-stratum leaves that legacy criteria would retire`() {
        // Regression for the 2026-09-06 profile run: selectTargetNodes called
        // isLeafConverged WITHOUT the condition argument, fell into the LEGACY_MAIN
        // branch, judged every leaf converged by decision-mode rules at round 38, and
        // silently ended the run with zero strata at target. In profile mode a leaf
        // with unspent budget and an unconverged stratum must stay a candidate no
        // matter how lopsided its records look to the legacy criterion.
        val prof = targets(seTarget = 0.15)
        val policy = BtStoppingPolicy(budgetPerPair = 30, profile = prof)
        val models = listOf("a", "b")
        val queries = mapOf("leaf-1" to (1..40).toList())
        policy.pairCustomBudgets["leaf-1|a|b"] = 40
        val sched = BtMatchScheduler(
            minQueriesForBenchmark = 1, queriesPerPair = 2,
            budgetPerPair = 3, stoppingPolicy = policy, seed = 1
        )
        val nodes = listOf(GraphNode(id = "leaf-1", label = "leaf-1", depth = 2))
        // 20-0: unanimously resolved to any decision-mode rule, budget far from spent.
        val stats = mapOf("leaf-1" to listOf(
            NodePairStats("leaf-1", "a", "b", winsA = 20.0, winsB = 0.0, ties = 0.0, totalComparisons = 20.0)))

        val underMain = sched.selectTargetNodes(nodes, emptyMap(), queries, stats, models, 100, condition = "MAIN")
        assertEquals(listOf("leaf-1"), underMain.map { it.id },
            "profile-mode MAIN must keep the leaf: stratum unconverged, budget unspent")

        // Stratum reaching target releases the leaf.
        prof.seByStratum = mapOf("s1" to mapOf("a" to 0.1, "b" to 0.1))
        assertTrue(sched.selectTargetNodes(nodes, emptyMap(), queries, stats, models, 100, condition = "MAIN").isEmpty())
    }

    @Test
    fun `pickQuery under maxQueryReuse prefers fresh agreement questions over over-cap disagreement ones`() {
        // Measured on R2: the disagreement filter outranked the least-used spread, so
        // 36,871 matches drew on 2,883 distinct questions (design effect 2.0x median).
        // Under the cap, a fresh agreement question must beat an over-ground
        // disagreement question; with the cap at default the historical rule holds.
        val preds = mapOf(
            "a" to mapOf(1 to "X", 2 to "X", 3 to "Q"),
            "b" to mapOf(1 to "Y", 2 to "X", 3 to "Q")   // query 1 disagrees; 2 and 3 agree
        )
        fun arena() = LeafArena("leaf-1", listOf("a", "b"), listOf(1, 2, 3), preds, 40)

        // Default cap: disagreement wins regardless of reuse (historical behaviour).
        val default = ActiveBtRacingScheduler()
        val a1 = arena()
        repeat(12) { a1.noteQueryUsed(1) }
        assertEquals(1, default.pickQuery(a1, ordered("a", "b")))

        // Cap of 10: query 1 is over-ground, the fresh agreement question wins.
        val capped = ActiveBtRacingScheduler(maxQueryReuse = 10)
        val a2 = arena()
        repeat(12) { a2.noteQueryUsed(1) }
        assertEquals(2, capped.pickQuery(a2, ordered("a", "b")))

        // When everything under-cap is spent for this pair, over-cap stays usable —
        // the cap is soft and no pair starves.
        val a3 = arena()
        repeat(12) { a3.noteQueryUsed(1) }
        a3.completed[ordered("a", "b")] = hashSetOf(2, 3)
        assertEquals(1, capped.pickQuery(a3, ordered("a", "b")))
    }

    @Test
    fun `simulated profile tournament terminates with every stratum at target`() {
        val seTarget = 0.55
        val prof = ProfileTargets(seTarget, mapOf("leaf-1" to "s1", "leaf-2" to "s1", "leaf-3" to "s2"))
        val policy = BtStoppingPolicy(budgetPerPair = 30, profile = prof)
        val sched = ActiveBtRacingScheduler(profile = prof)
        val models = listOf("strong", "middle", "weak")
        val truth = mapOf("strong" to 1.0, "middle" to 0.0, "weak" to -1.0)
        val leaves = listOf("leaf-1", "leaf-2", "leaf-3")
        val nodeToQueries = leaves.associateWith { (1..30).toList() }
        for (l in leaves) for (i in models.indices) for (j in i + 1 until models.size) {
            policy.pairCustomBudgets["$l|${minOf(models[i], models[j])}|${maxOf(models[i], models[j])}"] = 30
        }
        val pairStats = leaves.associateWith { mutableListOf<NodePairStats>() }
        val rng = Random(7)
        val nodes = leaves.map { GraphNode(id = it, label = it, depth = 2) }

        fun refreshSes() {
            val seMap = HashMap<String, Map<String, Double>>()
            for (stratum in prof.allStrata()) {
                val stats = pairStats.filterKeys { prof.stratumOf(it) == stratum }.values.flatten()
                if (stats.isEmpty()) continue
                val pooled = ProfileTargets.poolPairStats(stats)
                if (!BtMmFitter.assessIdentifiability(models, pooled).identified) continue
                val scores = BtMmFitter.fit(models, pooled, context = "profile-test/$stratum")
                seMap[stratum] = BtMmFitter.estimateStdErrors(models, scores, pooled)
            }
            prof.seByStratum = seMap
        }

        var rounds = 0
        while (rounds < 200) {
            refreshSes()
            if (prof.allStrata().all { prof.converged(it) }) break
            val batch = sched.selectNextBatch(
                targetNodes = nodes,
                pairStats = pairStats,
                models = models,
                resultsMatrix = emptyMap(),
                nodeToQueries = nodeToQueries,
                batchSize = 12,
                completedResults = emptyList(),
                budgetPerPair = 30,
                btStates = emptyMap(),
                pairBudgetFor = { leafId, key ->
                    policy.pairCustomBudgets.getOrDefault("$leafId|${key.first}|${key.second}", 30)
                }
            )
            if (batch.isEmpty()) break   // everything exhausted
            for (task in batch) {
                val pWin = 1.0 / (1.0 + exp(-(truth.getValue(task.modelA) - truth.getValue(task.modelB))))
                val aWins = rng.nextDouble() < pWin
                val list = pairStats.getValue(task.nodeId)
                val existing = list.firstOrNull {
                    (it.modelA == task.modelA && it.modelB == task.modelB) ||
                        (it.modelA == task.modelB && it.modelB == task.modelA)
                }
                if (existing == null) {
                    list.add(NodePairStats(task.nodeId, task.modelA, task.modelB,
                        winsA = if (aWins) 1.0 else 0.0, winsB = if (aWins) 0.0 else 1.0,
                        ties = 0.0, totalComparisons = 1.0))
                } else {
                    val direct = existing.modelA == task.modelA
                    if (aWins == direct) existing.winsA += 1.0 else existing.winsB += 1.0
                    existing.totalComparisons += 1.0
                }
            }
            rounds++
        }

        assertTrue(rounds < 200, "profile tournament did not terminate")
        refreshSes()
        for (stratum in prof.allStrata()) {
            assertTrue(prof.converged(stratum),
                "stratum $stratum ended at worst SE ${prof.worstSe(stratum)} > $seTarget")
        }
        // And the policy agrees the run is over.
        assertTrue(policy.shouldStop(
            btStates = emptyMap(), pairStats = pairStats,
            targetLeafIds = leaves.toSet(), models = models,
            round = rounds, totalComparisons = pairStats.values.flatten().sumOf { it.totalComparisons }.toInt(),
            nodeToQueries = nodeToQueries, condition = "MAIN"
        ))
    }
}
