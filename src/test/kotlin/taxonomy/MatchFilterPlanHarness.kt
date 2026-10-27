package taxonomy

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.arena.*
import taxonomy.dataset.ModelEvalResult
import taxonomy.model.BtMatchTask
import taxonomy.model.GraphNode
import taxonomy.model.NodeBtState
import taxonomy.model.NodePairStats
import taxonomy.model.QueryBenchmarkResult
import taxonomy.service.DomainEvaluation
import java.io.File
import java.sql.DriverManager
import kotlin.math.exp

/**
 * PLAN-ONLY demonstration that `matchFilter = "answerDisagreement"` reduces scheduled matches.
 *
 * ZERO judge calls, zero API calls of any kind, zero writes. The x12 cross-domain schedule is
 * rebuilt from artifacts already on disk — the promoted tree's reserved-pool routing
 * (`reserved_leaf_assignments.csv`), the frozen pool of record, and the 12-model roster of
 * `experiment_configs/x12_crossdomain.toml` — and driven to completion twice, once per arm,
 * with a STUB judge in place of the real one.
 *
 * WHAT IS REAL AND WHAT IS SIMULATED, so the number is read for what it is:
 *  - real: the routing, the question pool, every model's extracted answers, the whole
 *    production scheduling stack (BtMatchScheduler bootstrap + ActiveBtRacingScheduler racing),
 *    BtStoppingPolicy with placement stopping, the per-round Bradley-Terry refit, and the
 *    per-(leaf, pair) budgets the service seeds;
 *  - simulated: the verdicts. A deterministic Bradley-Terry coin, seeded per
 *    (cell, pair, question) and therefore IDENTICAL between the two arms wherever they land on
 *    the same slot, stands in for the judge. Strengths come from the roster's own ordering in
 *    the config, not from the answer key.
 *
 * The answer key is BLANKED OUT in the matrix this harness builds — every `gtAnswer` is "" and
 * every `isCorrect` false. A schedule that changed if the key were present would be reading it.
 *
 * Excluded from `gradlew test` (opens the 2 GB dataset cache, runs two full tournaments).
 * Run it with `gradlew matchFilterPlan`.
 */
class MatchFilterPlanHarness {

    private val evalDb = File("mmlu_pro_dataset_cache_v2.db")
    private val routing = File("reserved_leaf_assignments.csv")
    private val poolId = "p2dca21ab5f4ef3ae"

    /** The x12 cross-domain roster, in the order the config froze it (strongest first). */
    private val roster = listOf(
        "gemini-3.1-pro_5-shots", "arx_0314", "gpt-4o-2024-08-06", "iask_pro",
        "deepseek-chat-v2_5", "Meta-Llama-3_1-70B-Instruct", "Qwen1.5-72B-Chat",
        "c4ai-command-r-v01", "Meta-Llama-3_1-8B", "Yi-6b-Chat", "Llama-2-13b-hf",
        "Llama-2-7b-hf"
    )

    private data class Plan(
        val matches: Int,
        val rounds: Int,
        val distinctQuestions: Int,
        val summary: taxonomy.model.MatchFilterSummary,
        val matchesByPair: Map<PairKey, Int>
    )

    /**
     * The four models whose ordering the campaign could not settle. The pooled 16.9% / 79.6% /
     * 0.04% figures in the SCHEDULING probe are theirs, and they are where the filter is expected
     * to bite hardest: near-equals agree on most questions, so most of their matches carry no
     * signal. The rest of the roster is far apart and disagrees often, which is why the run-wide
     * reduction is much smaller than the frontier one.
     */
    private val top4 = setOf("iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06", "arx_0314")

    // ── inputs ───────────────────────────────────────────────────────────────────────────

    /** question -> its highest-weight leaf in the promoted tree. */
    private fun loadRouting(): Map<Int, String> {
        val out = HashMap<Int, String>()
        val best = HashMap<Int, Double>()
        routing.useLines { lines ->
            for ((i, line) in lines.withIndex()) {
                if (i == 0 || line.isBlank()) continue
                // The weight column was written with a locale decimal comma, so the row has one
                // more field than the header promises. Only columns 0 and 2 are needed.
                val f = line.split(",")
                if (f.size < 3) continue
                val q = f[0].trim().toIntOrNull() ?: continue
                val leaf = f[2].trim().trim('"')
                // Ties on weight break by leaf id, so the assignment is deterministic.
                val w = (f.getOrNull(4)?.trim()?.trim('"')?.replace(" ", "") ?: "").toDoubleOrNull() ?: 0.0
                val prev = best[q]
                if (prev == null || w > prev) { best[q] = w; out[q] = leaf }
            }
        }
        return out
    }

    /** (question, model) -> extracted prediction, for the pool of record. The key is not read. */
    private fun loadPredictions(): Pair<Set<Int>, Map<Int, Map<String, String?>>> {
        val url = "jdbc:sqlite:file:${evalDb.absolutePath.replace('\\', '/')}?mode=ro"
        DriverManager.getConnection(url).use { c ->
            val pool = HashSet<Int>()
            c.prepareStatement("select question_id from reserved_pool where pool_id = ?").use { st ->
                st.setString(1, poolId)
                val rs = st.executeQuery()
                while (rs.next()) pool.add(rs.getInt(1))
            }
            val preds = HashMap<Int, MutableMap<String, String?>>()
            val inList = roster.joinToString(",") { "?" }
            c.prepareStatement("select question_id, model_name, pred from eval_results where model_name in ($inList)").use { st ->
                roster.forEachIndexed { i, m -> st.setString(i + 1, m) }
                val rs = st.executeQuery()
                while (rs.next()) {
                    val q = rs.getInt(1)
                    if (q !in pool) continue
                    preds.getOrPut(q) { HashMap() }[rs.getString(2)] = rs.getString(3)
                }
            }
            return pool to preds
        }
    }

    // ── the stub judge ───────────────────────────────────────────────────────────────────

    /**
     * Deterministic stub judge, keyed by (cell, pair, question) so the two arms see the SAME
     * outcome wherever they land on the same slot: the only thing that can move the match count
     * is WHICH slots get scheduled.
     *
     * It reproduces the one structural fact the whole filter rests on, and nothing else
     * (experiment_results/x12_crossdomain/scheduling_probe.txt):
     *
     *   - on a question where the two candidates DISAGREE, the comparison carries correctness
     *     signal (79.6% of such pairs are key-decidable), so the verdict follows a Bradley-Terry
     *     coin whose strengths come from the roster's own frozen ordering;
     *   - on a question where they AGREE, it carries none (0.04% decidable), so the verdict is a
     *     fair coin. That is the CONSERVATIVE version of the FRONTIER finding: in the real arena
     *     those verdicts are not merely uninformative but skewed toward the longer answer.
     *
     * This is a simulation of the measured decidability structure, not a measurement. It is what
     * lets a match count be reported at all without spending judge budget; the empirical claim in
     * this harness is the candidate-question count, which needs no judge and no assumption.
     */
    private fun stubVerdict(nodeId: String, a: String, b: String, q: Int, decidable: Boolean): Boolean {
        val p = if (!decidable) 0.5 else {
            val ta = (roster.size - roster.indexOf(a)) * 0.35
            val tb = (roster.size - roster.indexOf(b)) * 0.35
            1.0 / (1.0 + exp(-(ta - tb)))
        }
        var h = 1125899906842597L
        for (ch in "$nodeId|$a|$b|$q") h = 31 * h + ch.code
        return java.util.Random(h).nextDouble() < p
    }

    // ── the plan ─────────────────────────────────────────────────────────────────────────

    private fun plan(
        filter: MatchFilter,
        nodeToQueries: Map<String, List<Int>>,
        matrix: Map<Int, Map<String, ModelEvalResult>>
    ): Plan {
        val nodes = nodeToQueries.keys.sorted().map { GraphNode(id = it, label = it, depth = 2) }
        // Same numbers TaxonomyBenchmarkService derives for this run shape: 12 models, 250
        // questions per round, per-(leaf, pair) budgets seeded from each leaf's own pool.
        // The round cap is lifted far above reach ON PURPOSE. x12 itself ran out of rounds
        // (40 x 250 = 10,000 against 9,144 verdicts), and under a cap both arms simply spend the
        // cap — the question here is how many matches each arm needs to FINISH, so the run has
        // to end on resolution/exhaustion instead.
        val policy = BtStoppingPolicy(
            maxRounds = 600,
            minComparisonsPerLeaf = 24,
            targetLeafConvergenceFraction = 0.70,
            separationThreshold = 1.5,
            minTotalComparisons = 66 * 2,
            budgetPerPair = 8
        )
        for ((nodeId, qs) in nodeToQueries) {
            val b = policy.leafBudgetPerPair(qs.size)
            for (i in roster.indices) for (j in i + 1 until roster.size) {
                policy.pairCustomBudgets["$nodeId|${minOf(roster[i], roster[j])}|${maxOf(roster[i], roster[j])}"] = b
            }
        }
        val scheduler = BtMatchScheduler(
            minQueriesForBenchmark = 1,
            queriesPerPair = 8,
            budgetPerPair = 8,
            stoppingPolicy = policy,
            seed = 44L,
            matchFilter = filter
        )

        val pairStatsMap = HashMap<String, MutableList<NodePairStats>>()
        val btStates = HashMap<String, NodeBtState>()
        val completed = ArrayList<QueryBenchmarkResult>()
        val questionsUsed = HashSet<Int>()
        var matches = 0
        var round = 0
        val matchesByPair = HashMap<PairKey, Int>()
        val targetLeafIds = nodeToQueries.keys.toSet()

        while (round < policy.maxRounds) {
            val stop = policy.shouldStop(
                btStates = btStates,
                pairStats = pairStatsMap,
                targetLeafIds = targetLeafIds,
                models = roster,
                round = round,
                totalComparisons = pairStatsMap.values.flatten().sumOf { it.totalComparisons }.toInt(),
                nodeToQueries = nodeToQueries,
                condition = "MAIN",
                verdictsThisArm = completed.size
            )
            if (stop) break
            val batch: List<BtMatchTask> = scheduler.selectNextBatch(
                targetNodes = nodes,
                btStates = btStates,
                pairStats = pairStatsMap,
                models = roster,
                resultsMatrix = matrix,
                nodeToQueries = nodeToQueries,
                batchSize = 250,
                maxConcurrentPerModel = 4,
                condition = "MAIN",
                completedResults = completed.toList()
            )
            if (batch.isEmpty()) break

            for (task in batch) {
                for (qs in task.queryIds) {
                    val q = qs.toIntOrNull() ?: continue
                    matches++
                    questionsUsed.add(q)
                    val key = ordered(task.modelA, task.modelB)
                    matchesByPair[key] = (matchesByPair[key] ?: 0) + 1
                    // Only the two candidates' own extracted answers decide whether this
                    // comparison carries signal — the same reference-free rule the filter uses.
                    val decidable = AnswerDisagreementFilter.verdict(
                        matrix[q]?.get(key.first)?.pred, matrix[q]?.get(key.second)?.pred
                    ) == AnswerDisagreementFilter.Verdict.DISAGREE
                    val aWins = stubVerdict(task.nodeId, key.first, key.second, q, decidable)
                    val list = pairStatsMap.getOrPut(task.nodeId) { ArrayList() }
                    val ps = list.firstOrNull { ordered(it.modelA, it.modelB) == key }
                        ?: NodePairStats(
                            nodeId = task.nodeId, modelA = key.first, modelB = key.second,
                            winsA = 0.0, winsB = 0.0, ties = 0.0, totalComparisons = 0.0
                        ).also { list.add(it) }
                    ps.totalComparisons += 1.0
                    if (aWins) ps.winsA += 1.0 else ps.winsB += 1.0
                    completed.add(
                        QueryBenchmarkResult(
                            query = "q$q", gtCategory = "", gtCorrectAnswer = "",
                            modelAnswers = emptyMap(), modelCorrect = emptyMap(),
                            matchedLeafLabels = listOf(task.nodeId), hadJudge = true,
                            domainEvaluations = emptyList(),
                            pairEvaluations = mapOf(
                                "${key.first}_vs_${key.second}" to listOf(
                                    DomainEvaluation(
                                        domain = task.nodeId,
                                        winner = if (aWins) "Model A" else "Model B",
                                        rationale = "stub", confidence = 0.9, nodeId = task.nodeId
                                    )
                                )
                            ),
                            judgeAccuracyAgreement = emptyMap(), queryId = q
                        )
                    )
                }
            }

            for ((nodeId, list) in pairStatsMap) {
                if (list.sumOf { it.totalComparisons } <= 0.0) continue
                val scores = BtMmFitter.fit(roster, list, context = "plan/$nodeId")
                btStates[nodeId] = NodeBtState(
                    nodeId = nodeId, btScores = scores,
                    stdErrors = BtMmFitter.estimateStdErrors(roster, scores, list),
                    fitVersion = (btStates[nodeId]?.fitVersion ?: 0) + 1,
                    totalComparisons = list.sumOf { it.totalComparisons }.toInt(),
                    lastFitAt = 0L
                )
            }
            round++
        }
        return Plan(matches, round, questionsUsed.size, scheduler.matchFilterStats.summary(), matchesByPair)
    }

    @Test
    fun `answerDisagreement schedules fewer matches than none on the promoted tree`() {
        assumeArtifacts()
        val routed = loadRouting()
        val (pool, preds) = loadPredictions()
        // Only questions every contestant answered can be judged pairwise across the roster.
        val usable = routed.keys.filter { q -> q in pool && preds[q]?.keys?.containsAll(roster) == true }.sorted()
        assertTrue(usable.size > 2000, "expected the frozen pool to route; got ${usable.size} questions")

        val matrix: Map<Int, Map<String, ModelEvalResult>> = usable.associateWith { q ->
            roster.associateWith { m ->
                ModelEvalResult(
                    questionId = q, modelName = m, category = "", questionText = "",
                    options = emptyList(),
                    // THE ANSWER KEY IS BLANKED. Nothing in the scheduling path may depend on it.
                    gtAnswer = "", pred = preds.getValue(q)[m], modelOutput = "",
                    isCorrect = false
                )
            }
        }
        val nodeToQueries = usable.groupBy { routed.getValue(it) }.toSortedMap().toMap()

        // DIRECT measurement first — no simulation, no judge, no key: over the six top-4 pairs,
        // what share of the pool would the filter even offer? This is the probe's 16.9%,
        // recomputed here from the same predictions the scheduler reads.
        var fDiffer = 0L
        var fTotal = 0L
        val t4 = roster.filter { it in top4 }
        for (i in t4.indices) for (j in i + 1 until t4.size) {
            for (q in usable) {
                fTotal++
                if (AnswerDisagreementFilter.verdict(preds.getValue(q)[t4[i]], preds.getValue(q)[t4[j]])
                    == AnswerDisagreementFilter.Verdict.DISAGREE) fDiffer++
            }
        }

        val off = plan(MatchFilter.NONE, nodeToQueries, matrix)
        val on = plan(MatchFilter.ANSWER_DISAGREEMENT, nodeToQueries, matrix)

        println("== MATCH FILTER PLAN (zero judge calls) ==")
        println("  tree            : 20260727_042523_Headless_Run_Auto_ge, ${nodeToQueries.size} cells")
        println("  pool            : $poolId, ${usable.size} questions answered by all ${roster.size} models")
        println("  %-22s %10s %8s %10s".format("arm", "matches", "rounds", "questions"))
        println("  %-22s %10d %8d %10d".format("none", off.matches, off.rounds, off.distinctQuestions))
        println("  %-22s %10d %8d %10d".format("answerDisagreement", on.matches, on.rounds, on.distinctQuestions))
        println("  reduction       : %.1f%% of the unfiltered match count".format(
            java.util.Locale.US, 100.0 * on.matches / off.matches))
        println("  candidate questions before -> after : ${on.summary.candidateQuestionsBefore} -> " +
            "${on.summary.candidateQuestionsAfter} over ${on.summary.slotEvaluations} slot evaluations")
        println("  (cell, pair) slots that fell back   : ${on.summary.fallbackSlots}")
        println("  question-pairs UNDETERMINED (kept)  : ${on.summary.questionPairsUndetermined} of " +
            "${on.summary.questionPairsSeen}")

        println("  frontier candidate pool (direct, no simulation): $fDiffer of $fTotal question-pairs " +
            "differ = %.1f%% offered to the judge".format(java.util.Locale.US, 100.0 * fDiffer / fTotal))
        val frontierOff = off.matchesByPair.entries.filter { it.key.first in top4 && it.key.second in top4 }.sumOf { it.value }
        val frontierOn = on.matchesByPair.entries.filter { it.key.first in top4 && it.key.second in top4 }.sumOf { it.value }
        println("  frontier (the six top-4 pairs, where the probe measured 16.9%/79.6%/0.04%):")
        println("    matches none -> answerDisagreement : $frontierOff -> $frontierOn (%.1f%%)".format(
            java.util.Locale.US, 100.0 * frontierOn / frontierOff))

        assertEquals("none", off.summary.filter)
        assertEquals(0L, off.summary.slotEvaluations, "the filter must not run at all when off")
        assertTrue(on.matches < off.matches,
            "the filter must reduce scheduled matches (${on.matches} vs ${off.matches})")
        assertFalse(on.summary.inert, "the pool has extracted answers; the filter must not be inert")
    }

    private fun assumeArtifacts() {
        assertTrue(evalDb.isFile, "${evalDb.path} not found; run from the repo root")
        assertTrue(routing.isFile, "${routing.path} not found; run `gradlew routeReserved` first")
    }
}
