package taxonomy.service

import taxonomy.arena.*
import kotlinx.coroutines.*
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.utils.TaxonomyPerformanceTracker
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EvalIngestValidator
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.ModelEvalStore
import taxonomy.dataset.ModelEvalResult
import taxonomy.dataset.unwrapTraceEnvelope
import taxonomy.model.*
import java.io.File
import kotlinx.serialization.json.Json
import kotlinx.serialization.encodeToString
import kotlin.collections.filter
import kotlin.math.abs
import kotlin.math.roundToInt

@OptIn(ExperimentalCoroutinesApi::class)
@Service
class TaxonomyBenchmarkService(
    private val arenaService: TaxonomyArenaService,
    private val rankingService: TaxonomyRankingService,
    private val datasetFetcher: MMLUDatasetFetcher,
    private val taxonomyService: TaxonomyService,
    private val evalStore: ModelEvalStore,
    private val config: TaxonomyConfig,
    private val perfTracker: TaxonomyPerformanceTracker,
    private val ingestValidator: EvalIngestValidator
) {
    private val log = LoggerFactory.getLogger("taxonomy.BenchmarkService")
    private val dbWriteDispatcher = Dispatchers.IO.limitedParallelism(1)
    private val json = Json { ignoreUnknownKeys = true }
    @Volatile
    private var mainConditionTotalComparisons: Int = 72

    /**
     * Verdicts served from the match cache instead of the judge, over the whole run.
     *
     * A non-zero value means the scheduler drew a (leaf, pair, question) triple it had already
     * judged. That costs nothing and is harmless in itself, but it used to be propagated into
     * the pair statistics a second time, which is how the leaf-credited comparison total came
     * to exceed the number of verdicts actually produced. Reported at the end of the run so the
     * two counts can be reconciled without going to the database.
     */
    private val replayedVerdicts = java.util.concurrent.atomic.AtomicInteger(0)

    private fun getAllNodes(root: GraphNode): List<GraphNode> {
        val visited = mutableSetOf<String>()
        val list = mutableListOf<GraphNode>()
        fun walk(node: GraphNode) {
            if (!visited.add(node.id)) return
            list.add(node)
            node.children.forEach { walk(it) }
            node.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)
        return list
    }

    private fun anchorsOf(
        node: GraphNode,
        cache: MutableMap<String, Set<String>> = HashMap()
    ): Set<String> {
        cache[node.id]?.let { return it }
        val result = LinkedHashSet<String>()
        val seen = HashSet<String>()
        val stack = ArrayDeque<GraphNode>()
        stack.addLast(node)
        while (stack.isNotEmpty()) {
            val cur = stack.removeLast()
            if (!seen.add(cur.id)) continue
            if (cur.depth == 1) {
                (cur.originalCategory ?: cur.label)?.let { result.add(it) }
                // depth-1 is an anchor; do not walk above it
                continue
            }
            for (p in cur.parents) stack.addLast(p)
        }
        cache[node.id] = result
        return result
    }

    private fun propagateOutcome(
        leafId: String,
        modelA: String,
        modelB: String,
        outcome: DomainEvaluation,
        snapshotId: String,
        judgeAgreed: Boolean = true,
        /**
         * Whether the answer key has an opinion about this match at all.
         *
         * The key discriminates only when exactly one of the two models is correct. When both
         * are right or both are wrong it says "TIE", which is not a judgement about response
         * quality — it is the key declining to rank. Counting those as agreement checks scores
         * the judge against a reference that mostly abstains: the judge names a winner ~78% of
         * the time, the key says TIE far more often, and the exact-match rate lands near 0.45
         * no matter how good the judge is. That is a property of the comparison, not of the
         * judge. Only decidable matches are counted, so `agreementWins / agreementChecks` is
         * the rate at which the judge picks the model that actually answered correctly.
         */
        judgeCheckable: Boolean = true
    ) {
        val list = rankingService.getNodePairStats(leafId, snapshotId)
        val existing = list.firstOrNull {
            (it.modelA == modelA && it.modelB == modelB) || (it.modelA == modelB && it.modelB == modelA)
        }
        val stats = PairStatsLedger.accumulate(
            existing = existing,
            nodeId = leafId,
            modelA = modelA,
            modelB = modelB,
            outcome = outcome,
            judgeAgreed = judgeAgreed,
            judgeCheckable = judgeCheckable
        ) ?: return
        rankingService.saveNodePairStats(stats, snapshotId)
    }

    suspend fun runBenchmark(
        req: BenchmarkRequest,
        onProgress: ((BenchmarkLiveStats) -> Unit)? = null
    ): BenchmarkReport = coroutineScope {
        require(req.models.size >= 2) { "Need at least 2 models" }
        val requestedModels = req.models.map { it.modelName }

        // ── [ARENA-INGEST] pre-flight ingest validation ─────────────────────────
        // Runs BEFORE getResultsMatrix, because the matrix joins on question_id alone and
        // therefore cannot tell a model that answered question 70 from a model whose zip
        // numbered a different question 70. Once a mis-keyed model is in the matrix its rows
        // are indistinguishable from good ones, and the resulting leaderboard is silently
        // wrong — no downstream export records question provenance.
        //
        // FAIL models are excluded rather than tolerated; if that leaves fewer than two
        // participants the run is aborted, because a "benchmark" of one model is not one.
        val modelNames = run {
            val ingest = ingestValidator.validate(requestedModels)
            ingest.renderLines().forEach { log.info("[ARENA-INGEST] $it") }
            val rejected = ingest.failed
            if (rejected.isEmpty()) {
                requestedModels
            } else {
                rejected.forEach { v ->
                    log.error(
                        "[ARENA-INGEST] EXCLUDED ${v.modelName} — ingest validation FAILED: " +
                            v.reasons.joinToString(" | ")
                    )
                }
                val kept = requestedModels.filterNot { m -> rejected.any { it.modelName == m } }
                check(kept.size >= 2) {
                    "[ARENA-INGEST] Cannot run benchmark: ${rejected.size} of ${requestedModels.size} " +
                        "requested model(s) failed ingest validation (${rejected.joinToString(", ") { it.modelName }}), " +
                        "leaving only ${kept.size} usable. Re-ingest the failing model(s) before benchmarking."
                }
                log.warn(
                    "[ARENA-INGEST] proceeding with ${kept.size} of ${requestedModels.size} requested models"
                )
                kept
            }
        }

        val health = evalStore.verifyIngestion(modelNames)
        health.forEach { h ->
            log.info("  ${h.modelName}: total=${h.totalRows} reserved=${h.reservedRows} math=${h.mathRows} reserved_math=${h.reservedMathRows}")
        }
        if (req.reservedOnly) {
            val empty = health.filter { it.reservedRows == 0 }
            require(empty.isEmpty()) {
                "Cannot run benchmark: ${empty.map { it.modelName }} have 0 reserved rows. " +
                "Load a snapshot first or run syncReservedPool."
            }
        }

        // queryLimit is applied AFTER domain scoping, not here, whenever a construction domain
        // is set. Applying it here bounded the whole reserved pool BEFORE the scope filter
        // below dropped everything outside the target domain, so the bound did not mean what
        // it says: on a Math run, `queryLimit = 24` drew 24 questions from all 14 domains and
        // only the ~11.4% that route into Math survived — ONE judged question. A smoke test
        // sized by this bound therefore measured nothing and could not cost a real run.
        val deferLimit = !req.category.isNullOrBlank()
        val matrix = evalStore.getResultsMatrix(
            models = modelNames,
            category = null,
            reservedOnly = req.reservedOnly,
            limit = if (deferLimit) 0 else req.queryLimit,
            minModelCount = 2
        )

        log.info("Benchmark: ${matrix.size} questions, ${modelNames.size} models")

        // ── [ARENA-POOL] what the arena is actually about to judge ──────────────
        // The leaderboard reports models, never the provenance of the questions behind
        // them, so a pool drawn from the wrong population is invisible in every export.
        //
        // The pool is scoped by reservedOnly, which restricts it to THIS run's held-out
        // split, so the category argument below is intentionally null: adding a second
        // filter on eval_results.category would drop legitimate held-out questions
        // whenever the two stores disagree about a question's category — and they do.
        //
        // Measured on a Math-only run: the dataset fetcher reserved 405 questions under
        // "Math", and eval_results labels 48 of those same ids "economics". Inspection
        // confirms the eval_results label is the accurate one (e.g. question 7506 is a
        // marginal-product problem), so MMLU-Pro's math category genuinely contains
        // economics-flavoured items. That is a cross-store labelling disagreement, NOT
        // pool contamination: every judged question belongs to this run's own split.
        run {
            val byCategory = matrix.values
                .mapNotNull { it.values.firstOrNull()?.category }
                .groupingBy { it }.eachCount()
                .entries.sortedByDescending { it.value }
            log.info(
                "[ARENA-POOL] questions=${matrix.size} models=${modelNames.size}" +
                    " reservedOnly=${req.reservedOnly} constructionDomain=${req.category ?: "<all>"}" +
                    " | eval_results category composition: " +
                    byCategory.joinToString(", ") { "${it.key}=${it.value}" }
            )
            if (!req.reservedOnly) {
                log.warn(
                    "[ARENA-POOL] reservedOnly=false — the pool is NOT restricted to this run's" +
                        " held-out split, so the arena may judge questions the taxonomy was built on."
                )
            }
            val requested = req.category
            if (!requested.isNullOrBlank()) {
                val disagreeing = byCategory.filter { !it.key.equals(requested, ignoreCase = true) }.sumOf { it.value }
                if (disagreeing > 0) {
                    log.info(
                        "[ARENA-POOL] $disagreeing of ${matrix.size} reserved question(s)" +
                            " (${"%.0f".format(java.util.Locale.US, 100.0 * disagreeing / matrix.size)}%)" +
                            " carry an eval_results category other than '$requested'." +
                            " These are still this run's own held-out questions — the dataset" +
                            " fetcher's domain and eval_results.category disagree for them."
                    )
                }
            }
        }

        // Validate answer matrix completeness and export a missingness table
        val missingnessReport = mutableListOf<String>()
        var missingCount = 0
        matrix.forEach { (qId, modelResults) ->
            val presentModels = modelResults.keys
            val missingModels = modelNames.filter { it !in presentModels }
            if (missingModels.isNotEmpty()) {
                missingCount++
                val sample = modelResults.values.firstOrNull()
                val qText = sample?.questionText?.replace("\n", " ")?.replace("\r", "")?.replace("\"", "\"\"")?.take(60) ?: "unknown"
                missingnessReport.add("$qId,\"$qText\",${missingModels.joinToString("|")}")
            }
        }

        if (missingnessReport.isNotEmpty()) {
            log.warn("Answer matrix completeness check: $missingCount / ${matrix.size} queries have missing model answers!")
            val missingnessFile = File("answer_matrix_missingness.csv")
            try {
                missingnessFile.bufferedWriter().use { writer ->
                    writer.write("query_id,query_text,missing_models\n")
                    missingnessReport.forEach { line ->
                        writer.write("$line\n")
                    }
                }
                log.info("Successfully exported missingness table to ${missingnessFile.absolutePath}")
            } catch (e: Exception) {
                log.error("Failed to export missingness table: ${e.message}", e)
            }
        } else {
            log.info("Answer matrix completeness check: 100% complete! No missing model answers across all ${matrix.size} queries.")
        }

        if (matrix.isEmpty()) {
            return@coroutineScope emptyReport()
        }

        val root = taxonomyService.getGraph() ?: return@coroutineScope emptyReport()
        val allNodes = getAllNodes(root)

        val frozenLeafIds = allNodes.filter { it.children.isEmpty() }.map { it.id }.toSet()

        // Pre-route all questions to target nodes dynamically using the NiW routing engine
        val nodeToQueries = mutableMapOf<String, MutableList<Int>>()
        val queryToLeaves = mutableMapOf<Int, MutableList<String>>()
        val queryToSoftRouting = java.util.Collections.synchronizedMap(mutableMapOf<Int, TaxonomyArenaService.SoftRoutingResult>())
        val targetCategory = req.category
        val anchorCache = HashMap<String, Set<String>>()
        var outlierCount = 0
        var scopedOutCount = 0

        val routeStart = System.currentTimeMillis()
        matrix.forEach { (qId, modelResults) ->
            val sample = modelResults.values.firstOrNull() ?: return@forEach
            val softResult = arenaService.routeToLeavesSoft(sample.questionText, frozenLeafIds, sample.category)
            if (softResult == null) {
                outlierCount++
                log.debug("qId=$qId is an outlier — no leaf match, skipping")
                return@forEach
            }
            
            // Scope check: Keep only if primaryLeaf is under targetCategory (if targetCategory is set)
            if (targetCategory != null && targetCategory.isNotBlank()) {
                val leafAnchors = anchorsOf(softResult.primaryLeaf, anchorCache)
                if (targetCategory.lowercase() !in leafAnchors.map { it.lowercase() }) {
                    scopedOutCount++
                    return@forEach
                }
            }

            queryToSoftRouting[qId] = softResult
            // One query, one cell: only the primary (argmax) leaf is filed, even though
            // `routeToLeavesSoft` also returns `secondaryMemberships` above the admission
            // floor. Filing secondaries as well was tried and withdrawn, because crediting
            // one verdict to several cells makes the leaf-credited total exceed the number
            // of judge calls, and it biases the paired contrast: MAIN spreads questions
            // over many cells while C5 has a single cell, so leaf-credited arm matching
            // would fund C5 with more real judge calls than MAIN. With one query in one
            // cell, verdict counts and leaf-credited counts coincide by construction.
            // The sibling propagation downstream tolerates multi-leaf membership; it simply
            // never fires while every query maps to one leaf.
            val leaf = softResult.primaryLeaf
            nodeToQueries.getOrPut(leaf.id) { mutableListOf() }.add(qId)
            queryToLeaves.getOrPut(qId) { mutableListOf() }.add(leaf.id)
        }
        // Now that scoping has run, `queryLimit` can mean "N questions IN THIS DOMAIN".
        // Deterministic: qIds are sorted, so the same limit always selects the same questions.
        if (deferLimit && req.queryLimit > 0 && queryToSoftRouting.size > req.queryLimit) {
            val keep = queryToSoftRouting.keys.sorted().take(req.queryLimit).toSet()
            val dropped = queryToSoftRouting.size - keep.size
            queryToSoftRouting.keys.retainAll(keep)
            queryToLeaves.keys.retainAll(keep)
            nodeToQueries.values.forEach { it.retainAll(keep) }
            nodeToQueries.entries.removeIf { it.value.isEmpty() }
            log.info("[ARENA-POOL] queryLimit=${req.queryLimit} applied AFTER domain scoping: " +
                "kept ${keep.size} in-domain questions across ${nodeToQueries.size} leaves, dropped $dropped")
        }
        val routeEnd = System.currentTimeMillis()
        if (config.diagnostics.enableProfiling) {
            perfTracker.recordTime("arena.routing.pre_route", routeEnd - routeStart, matrix.size.toLong())
        }
        log.info("Pre-routing complete: ${matrix.size - outlierCount - scopedOutCount} questions routed, $outlierCount outliers discarded, $scopedOutCount out-of-scope domain queries filtered")

        val params = buildSchedulingParams(
            numModels = modelNames.size,
            numLeaves = nodeToQueries.size,
            totalQuestions = matrix.size - outlierCount,
            minQuestionsPerLeaf = nodeToQueries.values.map { it.size }.minOrNull() ?: 10,
            req = req
        )
        log.info("Scheduling params: $params")

        val stoppingPolicy = BtStoppingPolicy(
            maxRounds = params.maxRounds,
            minComparisonsPerLeaf = params.minComparisonsPerLeaf,
            targetLeafConvergenceFraction = params.targetConvergenceFraction,
            separationThreshold = params.separationThreshold,
            minTotalComparisons = params.minTotalComparisons,
            budgetPerPair = params.budgetPerPair
        )
        // Seed the per-(leaf, pair) budget map from each leaf's own query pool, so the
        // scheduler and the stopping policy enforce the SAME number.
        //
        // Both sides read `pairCustomBudgets.getOrDefault(key, <default>)`, but their
        // fallbacks differ: the scheduler falls back to the run-global
        // `params.budgetPerPair` while the stopping policy sizes budgets per leaf.
        // Left unseeded, a leaf allowed 25 comparisons per pair would stall at the global
        // 7 — the scheduler stops issuing matches long before the stopping policy
        // considers the pair exhausted. Seeding the per-leaf value up front makes the two
        // agree by construction; the scheduler's own mutations still work, since it caps
        // a retired pair to its current count and extends budgets by addition.
        run {
            var seeded = 0
            for ((nodeId, qs) in nodeToQueries) {
                val b = stoppingPolicy.leafBudgetPerPair(qs.size)
                for (i in modelNames.indices) for (j in i + 1 until modelNames.size) {
                    val a = modelNames[i]; val c = modelNames[j]
                    stoppingPolicy.pairCustomBudgets["$nodeId|${minOf(a, c)}|${maxOf(a, c)}"] = b
                    seeded++
                }
            }
            val sizes = nodeToQueries.values.map { stoppingPolicy.leafBudgetPerPair(it.size) }
            log.info("[ARENA-BUDGET] seeded $seeded per-(leaf,pair) budgets from leaf size:" +
                " range [${sizes.minOrNull() ?: 0}, ${sizes.maxOrNull() ?: 0}]," +
                " run-global fallback was ${params.budgetPerPair}")
        }
        val scheduler = BtMatchScheduler(
            minQueriesForBenchmark = 1,
            queriesPerPair = params.queriesPerPair,
            budgetPerPair = params.budgetPerPair,
            stoppingPolicy = stoppingPolicy,
            seed = req.seed
        )

        val snapshotId = taxonomyService.activeSnapshotId() ?: "unsaved"
        val isReplayCondition = req.condition.equals("C3", ignoreCase = true) || req.condition.equals("C5", ignoreCase = true) || req.condition.equals("GENERIC_JUDGE", ignoreCase = true)
        val baseSnapshotId = snapshotId.substringBefore("_MAIN").substringBefore("_ORACLE").substringBefore("_C3").substringBefore("_C5").substringBefore("_GENERIC_JUDGE").substringBefore("_RANDOM_SCHEDULER").substringBefore("_KMEANS_BASELINE").substringBefore("_WARD_BASELINE").substringBefore("_RANDOMNULL_BASELINE")
        
        val replayTriples: List<FrozenMatchTriple>? = if (isReplayCondition) {
            val triplesFile = File("frozen_triples_${baseSnapshotId}_MAIN.json")
            if (triplesFile.exists()) {
                try {
                    log.info("Loading frozen triples from ${triplesFile.absolutePath} for replay...")
                    json.decodeFromString<List<FrozenMatchTriple>>(triplesFile.readText())
                } catch (e: Exception) {
                    throw IllegalStateException("Failed to parse frozen triples: ${e.message}", e)
                }
            } else {
                throw IllegalStateException("Required frozen triples file for replay not found: ${triplesFile.absolutePath}")
            }
        } else {
            null
        }
        val evaluatedTriples = mutableListOf<FrozenMatchTriple>()
        val trajectory = mutableListOf<TrajectoryPoint>()
        if (req.updateRankings) {
            val savedOffsets = rankingService.getPairQueryOffsets(snapshotId)
            if (savedOffsets.isNotEmpty()) {
                scheduler.loadOffsets(savedOffsets)
                log.info("Loaded ${savedOffsets.size} saved pair query offsets for snapshot '$snapshotId' to resume benchmark.")
            }
        }
        val btStates = mutableMapOf<String, NodeBtState>()
        val pairStatsMap = mutableMapOf<String, MutableList<NodePairStats>>()

        val allPairStatsFromDb = rankingService.getAllNodePairStats(snapshotId)
        val allBtStatesFromDb = rankingService.getAllBtStates(snapshotId)

        allNodes.forEach { node ->
            val nodePairs = allPairStatsFromDb[node.id]?.toMutableList() ?: mutableListOf()
            pairStatsMap[node.id] = nodePairs

            val btState = allBtStatesFromDb[node.id]
            if (btState != null) {
                btStates[node.id] = btState
            } else {
                btStates[node.id] = NodeBtState(
                    nodeId = node.id,
                    btScores = modelNames.associateWith { 0.0 },
                    stdErrors = modelNames.associateWith { 10.0 },
                    fitVersion = 0,
                    totalComparisons = nodePairs.sumOf { it.totalComparisons }.toInt(),
                    lastFitAt = System.currentTimeMillis()
                )
            }
        }

        // targetLeafIds is fixed — used by shouldStop to track full convergence across all eligible leaves
        val targetLeafIds = allNodes
            .filter { it.children.isEmpty() && (nodeToQueries[it.id]?.size ?: 0) >= scheduler.minQueriesForBenchmark }
            .map { it.id }.toSet()
        log.info("Benchmark scope: ${targetLeafIds.size} eligible leaf nodes")

        var targetNodes = scheduler.selectTargetNodes(
            allNodes, btStates, nodeToQueries,
            pairStats = pairStatsMap, models = modelNames, maxNodes = 100
        )

        var round = btStates.values.map { it.fitVersion }.maxOrNull() ?: 0
        val completedResults = java.util.Collections.synchronizedList(mutableListOf<QueryBenchmarkResult>())
        
        val cachedMatches = if (req.updateRankings) {
            rankingService.getAllRecordedMatches(snapshotId)
        } else {
            emptyList()
        }
        if (cachedMatches.isNotEmpty()) {
            val reconstructed = cachedMatches.mapNotNull { cm ->
                val parts = cm.queryKey.split("::", limit = 2)
                val qId = parts.firstOrNull()?.toIntOrNull() ?: return@mapNotNull null
                val modelResults = matrix[qId] ?: return@mapNotNull null
                val sample = modelResults.values.firstOrNull() ?: return@mapNotNull null

                val modelAnswers = modelResults.mapValues { (_, r) -> r.pred ?: "?" }
                val modelCorrect = modelResults.mapValues { (_, r) -> r.isCorrect }
                val aCorrect = modelCorrect[cm.modelA] ?: false
                val bCorrect = modelCorrect[cm.modelB] ?: false
                val gtWinner = when {
                    aCorrect && !bCorrect -> cm.modelA
                    bCorrect && !aCorrect -> cm.modelB
                    else -> "tie"
                }
                val judgeWinner = when {
                    cm.isTie -> "tie"
                    cm.winner == cm.modelA -> cm.modelA
                    else -> cm.modelB
                }
                val agrees = judgeWinner == gtWinner
                val pairKey = "${cm.modelA}_vs_${cm.modelB}"

                val primaryEval = DomainEvaluation(
                    domain = cm.domain,
                    winner = if (cm.isTie) "TIE" else if (cm.winner == cm.modelA) "Model A" else "Model B",
                    rationale = "Reconstructed from database",
                    confidence = 1.0,
                    positionFlip = false,
                    // node_id straight from the row when present; label lookup only for
                    // legacy rows written before the node_id column existed.
                    nodeId = cm.nodeId ?: allNodes.firstOrNull { it.label == cm.domain }?.id ?: "unknown"
                )

                QueryBenchmarkResult(
                    query = sample.questionText,
                    gtCategory = sample.category,
                    gtCorrectAnswer = sample.gtAnswer,
                    modelAnswers = modelAnswers,
                    modelCorrect = modelCorrect,
                    matchedLeafLabels = listOf(cm.domain),
                    hadJudge = true,
                    domainEvaluations = listOf(primaryEval),
                    pairEvaluations = mapOf(pairKey to listOf(primaryEval)),
                    // Agreement is recorded only where the key ranks the two responses; on
                    // undecidable comparisons the entry is omitted, so every consumer
                    // computes a decidable-only rate.
                    judgeAccuracyAgreement = if (gtWinner != "tie") mapOf(pairKey to agrees) else emptyMap(),
                    queryId = qId
                )
            }
            completedResults.addAll(reconstructed)
            log.info("Reconstructed ${reconstructed.size} previous match results from database.")

            // Rebuild node_pair_stats and node_bt_states from reconstructed matches
            val reconstructedPairs = mutableMapOf<String, MutableMap<String, NodePairStats>>()
            cachedMatches.forEach { cm ->
                // Key the leaf by node_id (unique by construction); the label match survives
                // only for legacy rows without node_id. A label collision here would silently
                // misattribute matches and make resume re-judge already-paid slots.
                val leafNode = allNodes.firstOrNull { it.id == cm.nodeId }
                    ?: allNodes.firstOrNull { it.label == cm.domain || it.id == cm.domain }
                    ?: return@forEach
                val leafId = leafNode.id
                val pairKey = "${cm.modelA}_vs_${cm.modelB}"
                val pairStatsMapForNode = reconstructedPairs.getOrPut(leafId) { mutableMapOf() }
                
                val (wA, wB) = if (cm.isTie) {
                    0.0 to 0.0
                } else if (cm.winner == cm.modelA) {
                    1.0 to 0.0
                } else {
                    0.0 to 1.0
                }
                
                val existing = pairStatsMapForNode[pairKey]
                if (existing != null) {
                    existing.winsA += wA
                    existing.winsB += wB
                    existing.ties += if (cm.isTie) 1.0 else 0.0
                    existing.totalComparisons += 1.0
                } else {
                    pairStatsMapForNode[pairKey] = NodePairStats(
                        nodeId = leafId,
                        modelA = cm.modelA,
                        modelB = cm.modelB,
                        winsA = wA,
                        winsB = wB,
                        ties = if (cm.isTie) 1.0 else 0.0,
                        totalComparisons = 1.0,
                        positionFlips = 0,
                        lastUpdated = System.currentTimeMillis()
                    )
                }
            }

            reconstructedPairs.forEach { (leafId, statsMapForNode) ->
                statsMapForNode.values.forEach { stats ->
                    rankingService.saveNodePairStats(stats, snapshotId)
                }
                val nodePairs = PairStatsLedger.auditOrderBias(rankingService.getNodePairStats(leafId, snapshotId))
                pairStatsMap[leafId] = nodePairs.toMutableList()
                
                if (nodePairs.isNotEmpty()) {
                    // Refuse to persist a fit whose comparison graph cannot identify one scale.
                    // Bradley-Terry pins theta only up to a constant per connected component, so a
                    // leaf split into components (or with models that never played) yields scores
                    // on several unrelated zero points. aggregateLeafScores pools per-leaf theta
                    // upward, and pooling across components mixes incommensurable quantities —
                    // which fails silently, with ordinary-looking numbers and exit code 0. Not
                    // persisting is what keeps such a leaf out of the aggregate entirely.
                    val ident = BtMmFitter.assessIdentifiability(modelNames, nodePairs)
                    if (!ident.identified) {
                        log.warn(
                            "[ARENA-BT] leaf '$leafId': refusing the fit — ${ident.describe()}." +
                                " Not persisted, so it is excluded from upward aggregation."
                        )
                    } else {
                        val fitStart = System.currentTimeMillis()
                        val scores = BtMmFitter.fit(modelNames, nodePairs, context = "leaf/$leafId")
                        val stdErrors = BtMmFitter.estimateStdErrors(modelNames, scores, nodePairs)
                        val fitEnd = System.currentTimeMillis()
                        if (config.diagnostics.enableProfiling) {
                            perfTracker.recordTime("arena.bt_fit.mm_update", fitEnd - fitStart, 1L)
                        }
                        val state = NodeBtState(
                            nodeId = leafId,
                            btScores = scores,
                            stdErrors = stdErrors,
                            fitVersion = (btStates[leafId]?.fitVersion ?: 0) + 1,
                            totalComparisons = nodePairs.sumOf { it.totalComparisons }.toInt(),
                            lastFitAt = System.currentTimeMillis()
                        )
                        rankingService.saveBtState(state, snapshotId)
                        btStates[leafId] = state
                    }
                }
            }
        }

        val completedAtStartOfRound = java.util.concurrent.atomic.AtomicInteger(completedResults.size)

        var currentAggregated: TaxonomyRankingService.AggregatedLeaderboard? = null
        var lastUpdateAt = 0L

        val publishProgress: (Boolean) -> Unit = { force ->
            val now = System.currentTimeMillis()
            if (force || now - lastUpdateAt >= 150L) {
                lastUpdateAt = now
                val resultsSnapshot = synchronized(completedResults) { completedResults.toList() }
                if (onProgress != null) {
                    val allAgreements = resultsSnapshot.flatMap { it.judgeAccuracyAgreement.values }
                    val runningAgreement = if (allAgreements.isNotEmpty()) allAgreements.count { it }.toDouble() / allAgreements.size else 0.0
                    val runningCoverage = 1.0
                    val perCategoryProgress = resultsSnapshot.groupBy { it.gtCategory }.mapValues { it.value.size }

                    val pairs = modelNames.flatMapIndexed { i, a -> modelNames.drop(i + 1).map { b -> a to b } }
                    val livePairStats = pairs.map { (modelA, modelB) ->
                        val pairKey = "${modelA}_vs_${modelB}"
                        val pairResults = resultsSnapshot.filter { pairKey in it.judgeAccuracyAgreement }
                        var judgeWinsA = 0; var judgeWinsB = 0; var judgeTies = 0
                        var accWinsA = 0; var accWinsB = 0; var accTies = 0
                        var totalConf = 0.0; var confCount = 0

                        pairResults.forEach { qr ->
                            val aCorrect = qr.modelCorrect[modelA] ?: false
                            val bCorrect = qr.modelCorrect[modelB] ?: false
                            when {
                                aCorrect && !bCorrect -> accWinsA++
                                bCorrect && !aCorrect -> accWinsB++
                                else -> accTies++
                            }
                            val evals = qr.pairEvaluations[pairKey] ?: qr.domainEvaluations
                            val primaryEval = evals
                                .filter { it.confidence >= req.confidenceGate }
                                .maxByOrNull { it.confidence }
                            primaryEval?.let { eval ->
                                when (eval.winner.uppercase()) {
                                    "MODEL A" -> judgeWinsA++
                                    "MODEL B" -> judgeWinsB++
                                    else -> judgeTies++
                                }
                                totalConf += eval.confidence
                                confCount++
                            }
                        }

                        ModelPairStats(
                            modelA = modelA,
                            modelB = modelB,
                            totalMatches = pairResults.size,
                            judgeWinsA = judgeWinsA,
                            judgeWinsB = judgeWinsB,
                            judgeTies = judgeTies,
                            accuracyWinsA = accWinsA,
                            accuracyWinsB = accWinsB,
                            accuracyTies = accTies,
                            judgeAccuracyAgreementRate = pairResults.mapNotNull { it.judgeAccuracyAgreement[pairKey] }.let { l -> if (l.isEmpty()) 0.0 else l.count { it }.toDouble() / l.size },
                            avgConfidence = if (confCount > 0) totalConf / confCount else 0.0,
                            isExhausted = false
                        )
                    }

                    val lastResult = resultsSnapshot.lastOrNull()
                    val activeTargetNames = targetNodes.mapNotNull { it.label }
                    
                    val remainingQueries = targetLeafIds.sumOf { leafId ->
                        val isConverged = stoppingPolicy.isLeafConverged(leafId, btStates, pairStatsMap, modelNames, nodeToQueries)
                        if (isConverged) {
                            0
                        } else {
                            val state = btStates[leafId]
                            val numPairs = modelNames.size * (modelNames.size - 1) / 2
                            val available = nodeToQueries[leafId]?.size ?: 0
                            val maxPossible = if (available > 0) available * numPairs else 0
                            val mCap = if (maxPossible > 0) {
                                maxOf(1, minOf(kotlin.math.ceil(params.budgetPerPair.toDouble() * numPairs / 2.0).toInt(), (maxPossible * 0.9).toInt()))
                            } else {
                                maxOf(1, kotlin.math.ceil(params.budgetPerPair.toDouble() * numPairs / 2.0).toInt())
                            }
                            
                            val minPerPair = (stoppingPolicy.minComparisonsPerLeaf / modelNames.size).coerceAtLeast(1)
                            val mCoverage = numPairs * minPerPair
                            val deltaSeparation = (0.75 * numPairs).toInt()
                            val mLeaf = minOf(mCap, mCoverage + deltaSeparation)
                            
                            val comps = state?.totalComparisons ?: 0
                            maxOf(0, mLeaf - comps)
                        }
                    }
                    val completedInCurrentRound = resultsSnapshot.size - completedAtStartOfRound.get()
                    val activeRemaining = maxOf(0, remainingQueries - completedInCurrentRound)
                    
                    val maxTotalMatches = targetLeafIds.sumOf { leafId ->
                        val numPairs = modelNames.size * (modelNames.size - 1) / 2
                        val available = nodeToQueries[leafId]?.size ?: 0
                        val maxPossible = if (available > 0) available * numPairs else 0
                        val mCap = if (maxPossible > 0) {
                            maxOf(1, minOf(kotlin.math.ceil(params.budgetPerPair.toDouble() * numPairs / 2.0).toInt(), (maxPossible * 0.9).toInt()))
                        } else {
                            maxOf(1, kotlin.math.ceil(params.budgetPerPair.toDouble() * numPairs / 2.0).toInt())
                        }
                        
                        val minPerPair = (stoppingPolicy.minComparisonsPerLeaf / modelNames.size).coerceAtLeast(1)
                        val mCoverage = numPairs * minPerPair
                        val deltaSeparation = (0.75 * numPairs).toInt()
                        minOf(mCap, mCoverage + deltaSeparation)
                    }
                    val estimatedTotal = minOf(maxTotalMatches, resultsSnapshot.size + activeRemaining).coerceAtLeast(resultsSnapshot.size)

                    val live = BenchmarkLiveStats(
                        processed = resultsSnapshot.size,
                        total = estimatedTotal,
                        currentQuestion = lastResult?.query ?: "",
                        runningAgreement = runningAgreement,
                        runningCoverage = runningCoverage,
                        perCategoryProgress = perCategoryProgress,
                        pairStats = livePairStats,
                        currentRound = round + 1,
                        activeTargets = activeTargetNames,
                        btRatings = currentAggregated?.ranks?.takeIf { it.isNotEmpty() }?.associate { it.modelId to it.btScore }
                            ?: modelNames.associateWith { 0.0 },
                        btErrors = currentAggregated?.ranks?.takeIf { it.isNotEmpty() }?.associate { it.modelId to it.stdError }
                            ?: modelNames.associateWith { 10.0 }
                    )
                    onProgress?.invoke(live)
                }
            }
        }

        val leafIds = mutableListOf<String>()
        val visited = mutableSetOf<String>()
        fun walk(n: GraphNode) {
            if (!visited.add(n.id)) return
            if (n.children.isEmpty()) leafIds.add(n.id)
            else n.children.forEach { walk(it) }
        }
        walk(root)
        val aggStart = System.currentTimeMillis()
        currentAggregated = rankingService.aggregateLeafScores(leafIds, snapshotId, nodeToQuestions = nodeToQueries)
        val aggEnd = System.currentTimeMillis()
        if (config.diagnostics.enableProfiling) {
            perfTracker.recordTime("arena.ranking.propagate", aggEnd - aggStart, 1L)
        }
        publishProgress(true)

        fun checkStoppingPolicy(): Boolean {
            val start = System.currentTimeMillis()
            val res = stoppingPolicy.shouldStop(
                btStates = btStates,
                pairStats = pairStatsMap,
                targetLeafIds = targetLeafIds,
                models = modelNames,
                round = round,
                totalComparisons = pairStatsMap.values.flatten().sumOf { it.totalComparisons }.toInt(),
                nodeToQueries = nodeToQueries,
                condition = req.condition,
                mainConditionTotalComparisons = mainConditionTotalComparisons,
                verdictsThisArm = completedResults.size
            )
            val end = System.currentTimeMillis()
            if (config.diagnostics.enableProfiling) {
                perfTracker.recordTime("arena.stopping_policy.check", end - start, 1L)
            }
            return res
        }

        while (round < params.maxRounds && !checkStoppingPolicy()) {
            completedAtStartOfRound.set(completedResults.size)
            // ── Confidence gate, evaluated PER CELL ──────────────────────────────────
            // Each cell's pairs are tested against that cell's own theta and standard
            // errors, never against the aggregate board: gating on the pooled fit would
            // retire exactly the comparisons that could show a cell ordering differing
            // from the pooled one — the question the per-cell arena exists to answer.
            // See BtStoppingPolicy.resolvedPairs.
            stoppingPolicy.resolvedPairs.clear()
            run {
                val allPairs = modelNames.flatMapIndexed { i, mA -> modelNames.drop(i + 1).map { mB -> mA to mB } }
                for ((leafId, st) in btStates) {
                    for ((mA, mB) in allPairs) {
                        val sA = st.btScores[mA] ?: continue
                        val sB = st.btScores[mB] ?: continue
                        val eA = st.stdErrors[mA] ?: continue
                        val eB = st.stdErrors[mB] ?: continue
                        val sigma = maxOf(eA, eB)
                        if (sigma > 0.0 && abs(sA - sB) > 2.5 * sigma) {
                            stoppingPolicy.resolvedPairs.add("$leafId|${minOf(mA, mB)}|${maxOf(mA, mB)}")
                        }
                    }
                }
            }
            // Per-round ranking snapshot, aggregate and per leaf. node_bt_states is
            // INSERT OR REPLACE keyed on (snapshot_id, node_id), so each round overwrites the
            // last and a stopping rule that fires on rank stability could never be audited
            // afterwards — only watched live, which this project has repeatedly shown is where
            // misreadings happen. Append-only, so "why did it stop" stays answerable.
            run {
                currentAggregated?.let { board ->
                    val ordered = board.ranks.sortedByDescending { it.btScore }.map { it.modelId }
                    taxonomy.diagnostics.DiagnosticsBundle.recordRanking(
                        round = round, scope = "AGGREGATE", scopeLabel = req.condition,
                        comparisons = board.totalComparisons.toDouble(),
                        ranking = ordered,
                        scores = board.ranks.associate { it.modelId to it.btScore }
                    )
                }
                for ((leafId, st) in btStates) {
                    val ordered = st.btScores.entries.sortedByDescending { it.value }.map { it.key }
                    taxonomy.diagnostics.DiagnosticsBundle.recordRanking(
                        round = round, scope = leafId,
                        scopeLabel = getAllNodes(root).firstOrNull { it.id == leafId }?.label,
                        comparisons = st.totalComparisons.toDouble(),
                        ranking = ordered, scores = st.btScores
                    )
                }
            }

            // ── [ARENA-SCHED] global resolution is a cross-leaf suppression ──────────
            // The key here omits nodeId, unlike every per-leaf budget key, so a pair marked
            // resolved stops being sampled in EVERY leaf (checked at BtMatchScheduler:156, :189,
            // :360 and BtStoppingPolicy:107, :196). That is a confound for any comparison between
            // groupings with different leaf counts: a 104-leaf adapted taxonomy loses sampling
            // across far more cells than a 14-domain baseline, so the two receive systematically
            // different evidence per cell for reasons that have nothing to do with the grouping.
            //
            // It is recomputed from scratch each round rather than accumulated, so a pair can
            // leave the set. The gate width is 2.5*sigma, so it is only as trustworthy as the
            // SE it reads — an understated sigma fires the gate on far too little evidence
            // (see [ARENA-SE]). The set is in-memory only, so it is logged every round below;
            // "how many pairs, at what round" must be answerable after a run.
            run {
                val totalPairs = modelNames.size * (modelNames.size - 1) / 2
                // Per-cell breakdown of WHY each pair is or is not still being sampled.
                // `n>=5` is the precondition for the local binomial test to be eligible at
                // all; if it stays near zero while the gate count climbs, the local
                // criterion is unreachable at this budget and convergence is being carried
                // entirely by the gate.
                val parts = btStates.keys.sorted().map { leafId ->
                    val gate = stoppingPolicy.resolvedPairs.count { it.startsWith("$leafId|") }
                    val eligible = (pairStatsMap[leafId] ?: emptyList()).count { it.totalComparisons >= 5 }
                    "$leafId gate=$gate/$totalPairs n>=5:$eligible"
                }
                if (parts.isNotEmpty()) {
                    log.info(
                        "[ARENA-SCHED] round $round: per-cell confidence gate (gap > 2.5*sigma on that" +
                            " cell's own theta/SE) — ${parts.joinToString(" | ")}"
                    )
                }
            }

            // Re-select each round: converged leaves are excluded, uncertain ones are promoted
            targetNodes = scheduler.selectTargetNodes(
                allNodes, btStates, nodeToQueries,
                pairStats = pairStatsMap, models = modelNames, maxNodes = 100
            )
            if (targetNodes.isEmpty() && replayTriples == null) break
            log.debug("Round $round — active leaves: ${targetNodes.size} / ${targetLeafIds.size} " +
                      "(converged: ${targetLeafIds.size - targetNodes.size})")

            val batch = if (replayTriples != null) {
                val startIdx = round * params.questionsPerRound
                if (startIdx >= replayTriples.size) {
                    break
                }
                val chunk = replayTriples.drop(startIdx).take(params.questionsPerRound)
                chunk.mapIndexed { idx, triple ->
                    BtMatchTask(
                        nodeId = triple.nodeId,
                        modelA = triple.modelA,
                        modelB = triple.modelB,
                        queryIds = listOf(triple.questionId.toString()),
                        priority = 1.0,
                        batchId = "replay_${round}_$idx"
                    )
                }
            } else {
                scheduler.selectNextBatch(
                    targetNodes = targetNodes,
                    btStates = btStates,
                    pairStats = pairStatsMap,
                    models = modelNames,
                    resultsMatrix = matrix,
                    nodeToQueries = nodeToQueries,
                    batchSize = params.questionsPerRound,
                    maxConcurrentPerModel = params.maxConcurrentPerModel,
                    globalLeaderboard = currentAggregated,
                    condition = req.condition,
                    completedResults = completedResults.toList()
                )
            }
            // ── Empty batch means the scheduler has nothing left to do ──────────────
            // `shouldStop` only sees btStates and pairStats and cannot know the scheduler
            // has run dry, so the loop must break here: once every pair is resolved,
            // exhausted or retired domain-wide, selectNextBatch returns an empty list and
            // further rounds would idle to maxRounds, making "ran to maxRounds" ambiguous
            // between a spent budget and an early finish. A replay condition is exempt:
            // `replayTriples` breaks out on its own when the chunk index passes the end.
            if (batch.isEmpty()) {
                log.info("[ARENA-SCHED] round $round: scheduler returned no work — every pair is " +
                    "resolved, budget-exhausted or globally retired. Ending the ${req.condition} " +
                    "arm at $round round(s) of ${params.maxRounds} rather than idling to the cap.")
                break
            }

            val startTime = System.currentTimeMillis()

            val roundResults = batch.mapIndexed { i, task ->
                async(Dispatchers.IO) {
                    delay(i * 10L)
                    val leafNode = allNodes.firstOrNull { it.id == task.nodeId } ?: return@async emptyList<QueryBenchmarkResult>()

                    try {
                        val taskResults = task.queryIds.mapNotNull { queryIdStr ->
                            val qId = queryIdStr.toIntOrNull() ?: run {
                                log.warn("queryIdStr is not Int: $queryIdStr")
                                return@mapNotNull null
                            }
                            val modelResults = matrix[qId] ?: run {
                                log.warn("matrix[qId] is null for qId $qId")
                                return@mapNotNull null
                            }

                            val sample = modelResults.values.firstOrNull() ?: run {
                                log.warn("modelResults has no values for qId $qId")
                                return@mapNotNull null
                            }
                            val gtAnswer = sample.gtAnswer
                            val gtCategory = sample.category

                            val outputA = modelResults[task.modelA] ?: run {
                                log.warn("modelResults has no entry for modelA ${task.modelA} for qId $qId. Available models in results: ${modelResults.keys}")
                                return@mapNotNull null
                            }
                            val outputB = modelResults[task.modelB] ?: run {
                                log.warn("modelResults has no entry for modelB ${task.modelB} for qId $qId. Available models in results: ${modelResults.keys}")
                                return@mapNotNull null
                            }

                            checkNotNull(leafNode.judgePrompt) {
                                "Attempted to record match for node ${leafNode.id} with no judgePrompt"
                            }
                            val domainName = requireNotNull(leafNode.label) { "Leaf node ${leafNode.id} has no label" }

                            val cacheKey = "${qId}::${sample.questionText}"
                            val cached = if (req.condition.equals("ORACLE", ignoreCase = true)) null else rankingService.getRecordedMatch(
                                snapshotId = snapshotId,
                                domain = domainName,
                                query = cacheKey,
                                modelA = task.modelA,
                                modelB = task.modelB
                            )

                            val domainEvaluations = if (cached != null) {
                                val cachedWinner = when {
                                    cached.isTie -> "TIE"
                                    cached.winner == task.modelA -> "Model A"
                                    cached.winner == task.modelB -> "Model B"
                                    else -> "TIE"
                                }
                                listOf(
                                    DomainEvaluation(
                                        domain = cached.domain,
                                        winner = cachedWinner,
                                        rationale = "Cached match result",
                                        confidence = 1.0,
                                        positionFlip = false,
                                        nodeId = leafNode.id
                                    )
                                )
                            } else {
                                val evals = arenaService.evaluateWithPrecomputedTraces(
                                    query = sample.questionText,
                                    options = sample.options,
                                    modelA = task.modelA,
                                    traceA = getRobustTrace(outputA),
                                    modelB = task.modelB,
                                    traceB = getRobustTrace(outputB),
                                    expectedNodeId = task.nodeId,
                                    frozenLeafIds = frozenLeafIds,
                                    gtAnswer = sample.gtAnswer,
                                    assignedLeafIds = queryToLeaves[qId],
                                    condition = req.condition,
                                    isCorrectA = outputA.isCorrect,
                                    isCorrectB = outputB.isCorrect
                                )
                                evals
                            }

                            if (domainEvaluations.isEmpty()) {
                                log.trace("domainEvaluations is empty for qId $qId")
                                return@mapNotNull null
                            }

                            log.debug("multi-judge qId=$qId: ${domainEvaluations.joinToString { "${it.domain.take(15)}->${it.winner}" }}")

                            val rawPrimaryEval = domainEvaluations.firstOrNull { it.nodeId == task.nodeId }
                                ?: domainEvaluations.maxByOrNull { it.confidence }
                                ?: return@mapNotNull null
                            val satisfiesGate = rawPrimaryEval.confidence >= req.confidenceGate
                                || rawPrimaryEval.tieSource == "POSITION_FLIP"

                            val primaryEval = if (satisfiesGate) {
                                rawPrimaryEval
                            } else {
                                log.warn("evaluation confidence ${rawPrimaryEval.confidence} is below confidenceGate ${req.confidenceGate} for qId $qId. Treating as LOW_CONFIDENCE_TIE.")
                                rawPrimaryEval.copy(winner = "TIE", rationale = "LOW_CONFIDENCE_TIE: Below confidence gate (${rawPrimaryEval.confidence} < ${req.confidenceGate}). Original: ${rawPrimaryEval.rationale}")
                            }

                            if (req.updateRankings && cached == null && primaryEval.winner != "INVALID") {
                                val isTie = primaryEval.winner.equals("TIE", ignoreCase = true)
                                val isModelA = primaryEval.winner.equals("Model A", ignoreCase = true)
                                withContext(dbWriteDispatcher) {
                                    rankingService.recordMatch(
                                        query = cacheKey,
                                        domain = domainName,
                                        winner = if (isTie) task.modelA else if (isModelA) task.modelA else task.modelB,
                                        loser = if (isTie) task.modelB else if (isModelA) task.modelB else task.modelA,
                                        isTie = isTie,
                                        confidence = primaryEval.confidence,
                                        snapshotId = snapshotId,
                                        modelA = task.modelA,
                                        modelB = task.modelB,
                                        nodeId = task.nodeId,
                                        evalQuestionId = qId.toString(),
                                        condition = req.condition
                                    )
                                }
                            }

                            val modelCorrect = modelResults.mapValues { (_, r) -> r.isCorrect }
                            val aCorrectVal = modelCorrect[task.modelA] ?: false
                            val bCorrectVal = modelCorrect[task.modelB] ?: false
                            val accWinner = when {
                                aCorrectVal && !bCorrectVal -> "MODEL A"
                                bCorrectVal && !aCorrectVal -> "MODEL B"
                                else -> "TIE"
                            }
                            val judgeWinnerVal = primaryEval.winner.uppercase()
                            val judgeAgreed = (judgeWinnerVal == accWinner)
                            // Only matches the key can actually rank count as agreement checks;
                            // see `judgeCheckable` on propagateOutcome.
                            val judgeCheckable = (accWinner != "TIE")

                            // A cache hit is a verdict this DB already holds, and it was already
                            // propagated into the pair statistics when it was first judged.
                            // Propagating it again would count one judgement as several: win
                            // counts, `totalComparisons` and the Fisher information all grow
                            // while no new evidence exists, so the standard errors shrink toward
                            // a precision the arena never bought. The verdict is still returned
                            // to the caller, so validation metrics and the trajectory see the
                            // match; only the fit's counters are left alone.
                            if (cached == null) {
                                withContext(dbWriteDispatcher) {
                                    propagateOutcome(
                                        leafId = leafNode.id,
                                        modelA = task.modelA,
                                        modelB = task.modelB,
                                        outcome = primaryEval,
                                        snapshotId = snapshotId,
                                        judgeAgreed = judgeAgreed,
                                        judgeCheckable = judgeCheckable
                                    )
                                }
                            } else {
                                replayedVerdicts.incrementAndGet()
                            }

                            val otherLeaves = if (cached != null) emptyList()
                                else queryToLeaves[qId]?.filter { it != task.nodeId } ?: emptyList()
                            for (siblingLeafId in otherLeaves) {
                                val siblingNode = allNodes.firstOrNull { it.id == siblingLeafId } ?: continue
                                if (siblingNode.judgePrompt == null) continue
                                withContext(dbWriteDispatcher) {
                                    propagateOutcome(
                                        leafId = siblingLeafId,
                                        modelA = task.modelA,
                                        modelB = task.modelB,
                                        outcome = primaryEval,
                                        snapshotId = snapshotId,
                                        judgeAgreed = judgeAgreed,
                                        judgeCheckable = judgeCheckable
                                    )
                                    if (req.updateRankings && cached == null && primaryEval.winner != "INVALID") {
                                        val siblingDomain = siblingNode.label ?: siblingNode.id
                                        val isTie = primaryEval.winner.equals("TIE", ignoreCase = true)
                                        val isModelA = primaryEval.winner.equals("Model A", ignoreCase = true)
                                        rankingService.recordMatch(
                                            query = cacheKey,
                                            domain = siblingDomain,
                                            winner = if (isTie) task.modelA else if (isModelA) task.modelA else task.modelB,
                                            loser = if (isTie) task.modelB else if (isModelA) task.modelB else task.modelA,
                                            isTie = isTie,
                                            confidence = primaryEval.confidence,
                                            snapshotId = snapshotId,
                                            modelA = task.modelA,
                                            modelB = task.modelB,
                                            nodeId = task.nodeId,
                                            evalQuestionId = qId.toString(),
                                            condition = req.condition
                                        )
                                    }
                                }
                            }

                            val modelAnswers = modelResults.mapValues { (_, r) -> r.pred ?: "?" }
                            val aCorrect = aCorrectVal
                            val bCorrect = bCorrectVal
                            val gtWinner = when {
                                aCorrect && !bCorrect -> task.modelA
                                bCorrect && !aCorrect -> task.modelB
                                else -> "tie"
                            }
                            val judgeWinner = when (primaryEval.winner) {
                                "Model A" -> task.modelA
                                "Model B" -> task.modelB
                                else -> "tie"
                            }
                            val agrees = judgeWinner == gtWinner
                            val pairKey = "${task.modelA}_vs_${task.modelB}"

                            val triple = FrozenMatchTriple(
                                questionId = qId,
                                modelA = task.modelA,
                                modelB = task.modelB,
                                nodeId = task.nodeId
                            )
                            synchronized(evaluatedTriples) {
                                evaluatedTriples.add(triple)
                            }

                            val softResult = queryToSoftRouting[qId]
                            val secondaryMemberships = softResult?.secondaryMemberships ?: emptyMap()

                            QueryBenchmarkResult(
                                query = sample.questionText,
                                gtCategory = gtCategory,
                                gtCorrectAnswer = gtAnswer,
                                modelAnswers = modelAnswers,
                                modelCorrect = modelCorrect,
                                matchedLeafLabels = listOf(primaryEval.domain),
                                hadJudge = (cached == null && !req.condition.equals("ORACLE", ignoreCase = true)),
                                domainEvaluations = listOf(primaryEval),
                                pairEvaluations = mapOf(pairKey to listOf(primaryEval)),
                                // Decidable comparisons only -- see the note at the
                                // reconstruction path above.
                                judgeAccuracyAgreement = if (gtWinner != "tie") mapOf(pairKey to agrees) else emptyMap(),
                                queryId = qId,
                                secondaryMemberships = secondaryMemberships
                            )
                        }

                        if (taskResults.isNotEmpty()) {
                            synchronized(completedResults) {
                                completedResults.addAll(taskResults)
                            }
                            publishProgress(false)
                        }
                        taskResults
                    } catch (e: Exception) {
                        log.error("Hard error occurred during judging of task ${task.modelA} vs ${task.modelB} on node ${task.nodeId}: ${e.message}", e)
                        val fallbackResults = task.queryIds.mapNotNull { queryIdStr ->
                            val qId = queryIdStr.toIntOrNull() ?: return@mapNotNull null
                            val modelResults = matrix[qId] ?: return@mapNotNull null
                            val sample = modelResults.values.firstOrNull() ?: return@mapNotNull null
                            
                            val pairKey = "${task.modelA}_vs_${task.modelB}"
                            val primaryEval = DomainEvaluation(
                                domain = leafNode.label ?: leafNode.id,
                                winner = "INVALID",
                                rationale = "CRITICAL HARD ERROR: ${e.message}",
                                confidence = 0.0,
                                positionFlip = false,
                                nodeId = leafNode.id
                            )
                            val modelCorrect = modelResults.mapValues { (_, r) -> r.isCorrect }
                            val modelAnswers = modelResults.mapValues { (_, r) -> r.pred ?: "?" }
                            
                            val softResult = queryToSoftRouting[qId]
                            val secondaryMemberships = softResult?.secondaryMemberships ?: emptyMap()
                            
                            QueryBenchmarkResult(
                                query = sample.questionText,
                                gtCategory = sample.category,
                                gtCorrectAnswer = sample.gtAnswer,
                                modelAnswers = modelAnswers,
                                modelCorrect = modelCorrect,
                                matchedLeafLabels = listOf(primaryEval.domain),
                                hadJudge = true,
                                domainEvaluations = listOf(primaryEval),
                                pairEvaluations = mapOf(pairKey to listOf(primaryEval)),
                                // An INVALID verdict is a judge failure, not a key
                                // abstention, so it stays countable -- but only where the
                                // key had an opinion to disagree with. `gtWinner` from the
                                // judging path is out of scope in this catch block, so
                                // decidability is recomputed from modelCorrect.
                                judgeAccuracyAgreement = if (modelCorrect[task.modelA] != modelCorrect[task.modelB])
                                    mapOf(pairKey to false) else emptyMap(),
                                queryId = qId,
                                secondaryMemberships = secondaryMemberships
                            )
                        }
                        if (fallbackResults.isNotEmpty()) {
                            synchronized(completedResults) {
                                completedResults.addAll(fallbackResults)
                            }
                            publishProgress(false)
                        }
                        fallbackResults
                    }
                }
            }.awaitAll().flatten()

            val pairSummaries = roundResults.flatMap { qr ->
                qr.pairEvaluations.entries.map { (pairKey, evals) ->
                    pairKey to evals
                }
            }.groupBy { it.first }
             .map { (pairKey, pairsList) ->
                 val evals = pairsList.flatMap { it.second }
                 val wins = evals.count { it.winner == "Model A" }
                 val losses = evals.count { it.winner == "Model B" }
                 val ties = evals.count { it.winner == "TIE" }
                 val flips = evals.count { it.positionFlip }
                 val avgConf = if (evals.isEmpty()) 0.0 else evals.map { it.confidence }.average()
                 PairRoundSummary(
                     pair = pairKey,
                     wins = wins,
                     losses = losses,
                     ties = ties,
                     posFlips = flips,
                     avgConf = avgConf
                 )
             }
            logRoundSummary(round, pairSummaries)

            val dirtyNodes = roundResults.mapNotNull { qr ->
                qr.domainEvaluations.firstOrNull()?.nodeId
            }.toSet()
            log.trace("Round $round - dirtyNodes: $dirtyNodes")

            withContext(dbWriteDispatcher) {
                for (nodeId in dirtyNodes) {
                    val nodePairs = PairStatsLedger.auditOrderBias(rankingService.getNodePairStats(nodeId, snapshotId))
                    log.trace("Round $round - updated nodePairs for $nodeId: ${nodePairs.map { "${it.modelA}_vs_${it.modelB}:${it.totalComparisons}" }}")
                    pairStatsMap[nodeId] = nodePairs.toMutableList()

                    if (nodePairs.isNotEmpty()) {
                        // Same connectivity refusal as the pre-round fit above: an unidentified
                        // leaf must not reach aggregateLeafScores, because theta is only defined
                        // up to a constant per component and pooling components is meaningless.
                        // Early rounds legitimately hit this while the scheduler is still filling
                        // pairs in, so it is logged at debug until the round is the last word.
                        val ident = BtMmFitter.assessIdentifiability(modelNames, nodePairs)
                        if (!ident.identified) {
                            log.debug(
                                "[ARENA-BT] round $round, node '$nodeId': fit not identified" +
                                    " (${ident.describe()}) — not persisted this round."
                            )
                        } else {
                            val fitStart = System.currentTimeMillis()
                            val scores = BtMmFitter.fit(modelNames, nodePairs, context = "leaf/$nodeId@r$round")
                            val stdErrors = BtMmFitter.estimateStdErrors(modelNames, scores, nodePairs)
                            val fitEnd = System.currentTimeMillis()
                            if (config.diagnostics.enableProfiling) {
                                perfTracker.recordTime("arena.bt_fit.mm_update", fitEnd - fitStart, 1L)
                            }
                            val state = NodeBtState(
                                nodeId = nodeId,
                                btScores = scores,
                                stdErrors = stdErrors,
                                fitVersion = (btStates[nodeId]?.fitVersion ?: 0) + 1,
                                totalComparisons = nodePairs.sumOf { it.totalComparisons }.toInt(),
                                lastFitAt = System.currentTimeMillis()
                            )
                            rankingService.saveBtState(state, snapshotId)
                            btStates[nodeId] = state
                        }
                    }
                }
                if (req.updateRankings) {
                    rankingService.savePairQueryOffsets(scheduler.getOffsets(), snapshotId)
                    log.debug("Round $round - saved ${scheduler.getOffsets().size} pair query offsets for snapshot '$snapshotId'")
                }
            }

            targetLeafIds.forEach { nodeId ->
                val nodeName = allNodes.firstOrNull { it.id == nodeId }?.label ?: nodeId
                btStates[nodeId]?.let { state ->
                    logLeafLeaderboard(nodeId, nodeName, state, round)
                }
            }

            val elapsedMs = System.currentTimeMillis() - startTime
            val convergedIds = targetLeafIds.filter {
                stoppingPolicy.isLeafConverged(it, btStates, pairStatsMap, modelNames, nodeToQueries, req.condition)
            }
            val nConverged = convergedIds.size
            // The stop decision uses a SIZE-WEIGHTED fraction, not this count. Logging only
            // the count made the rule unverifiable from the logs: the law run stopped at
            // "3/6 leaves", which reads as 50% against a 70% bar and is only correct if
            // those three leaves held 70% of the questions. Nobody could check that.
            // Both numbers are printed now, and the weighted one is the one that decides.
            val totalWeight = targetLeafIds.sumOf { (nodeToQueries[it]?.size ?: 1).toDouble() }
            val convWeight = convergedIds.sumOf { (nodeToQueries[it]?.size ?: 1).toDouble() }
            val weightedFrac = if (totalWeight > 0) convWeight / totalWeight else 0.0
            val matchesPerSec = if (elapsedMs > 0) (batch.size * 1000.0 / elapsedMs).roundToInt() else 0
            log.info("=== Round $round | ${batch.size} matches | ${elapsedMs}ms | " +
                     "$matchesPerSec matches/s | " +
                     "converged: $nConverged/${targetLeafIds.size} leaves, " +
                     "weighted ${"%.2f".format(java.util.Locale.US, weightedFrac)} " +
                     "(bar ${"%.2f".format(java.util.Locale.US, params.targetConvergenceFraction)}) ===")

            val leafIds = mutableListOf<String>()
            val visited = mutableSetOf<String>()
            fun walk(n: GraphNode) {
                if (!visited.add(n.id)) return
                if (n.children.isEmpty()) leafIds.add(n.id)
                else n.children.forEach { walk(it) }
            }
            walk(root)
            val aggStart = System.currentTimeMillis()
            val aggregated = rankingService.aggregateLeafScores(leafIds, snapshotId, nodeToQuestions = nodeToQueries)
            val aggEnd = System.currentTimeMillis()
            if (config.diagnostics.enableProfiling) {
                perfTracker.recordTime("arena.ranking.propagate", aggEnd - aggStart, 1L)
            }
            if (aggregated.ranks.isNotEmpty()) {
                // An all-zero board with unit errors is what aggregateLeafScores returns when it
                // had nothing to fit. It prints like an ordinary leaderboard, so say plainly that
                // it is empty rather than letting twelve zeros pass for a result.
                val degenerate = aggregated.ranks.all { it.btScore == 0.0 }
                if (degenerate) {
                    log.error(
                        "[ARENA-AGG] round $round: aggregate leaderboard is degenerate — every score is" +
                            " exactly 0 over ${aggregated.ranks.size} models (${aggregated.leafsEligible} of" +
                            " ${aggregated.leafsTotal} leaves eligible). Nothing was pooled; this board" +
                            " carries no information and must not be read as a ranking."
                    )
                } else {
                    log.info("--- Bradley-Terry Ratings (Round $round) [aggregated root] ---")
                    aggregated.ranks.forEach { mr ->
                        log.info("  * ${mr.modelId}: score = ${String.format("%.4f", mr.btScore)} (± ${String.format("%.4f", mr.stdError)})")
                    }
                }
            }

            currentAggregated = aggregated
            publishProgress(true)

            val totalComparisons = pairStatsMap.values.flatten().sumOf { it.totalComparisons }
            val dummyReport = BenchmarkReport(
                totalQueries = completedResults.size,
                totalModelPairs = modelNames.size * (modelNames.size - 1) / 2,
                coverageRate = 1.0,
                overallJudgeAccuracyAgreement = 1.0,
                perPairStats = emptyList(),
                perDomainStats = emptyList(),
                perCategoryStats = emptyList(),
                queryResults = completedResults.toList()
            )
            val intermediateReport = try {
                ValidationService.computeMetrics(dummyReport, modelNames, "OVERALL", bootstrapResamples = 1)
            } catch (e: Exception) {
                null
            }
            if (intermediateReport != null) {
                trajectory.add(
                    TrajectoryPoint(
                        round = round,
                        comparisons = totalComparisons.toInt(),
                        spearmanRho = intermediateReport.spearmanRho,
                        kendallTau = intermediateReport.kendallTau,
                        pairwiseWinnerAccuracy = intermediateReport.pairwiseWinnerAccuracy
                    )
                )
                // `comparisons` is LEAF-CREDITED, not the number of judge calls: a question that
                // belongs to several leaves contributes one verdict to each of them, which is
                // what the per-leaf fits consume. `verdicts` is the distinct judgements behind
                // it, and is the number to read as budget spent. They are equal only when no
                // question has multiple memberships.
                log.info(
                    "Trajectory [Round $round]: leafCreditedComparisons = $totalComparisons," +
                        " verdicts = ${completedResults.size}, replayed = ${replayedVerdicts.get()}," +
                        " spearmanRho = ${intermediateReport.spearmanRho}," +
                        " pairwiseWinnerAccuracy = ${intermediateReport.pairwiseWinnerAccuracy}"
                )
            }

            round++
        }

        val totalMatches = pairStatsMap.values.flatten().sumOf { it.totalComparisons }
        if (req.condition.equals("MAIN", ignoreCase = true)) {
            // Verdicts, not leaf-credited comparisons. Under multi-membership the two differ by
            // the average number of cells a question belongs to, and only MAIN can inflate —
            // C5 has a single cell. Capturing the leaf-credited figure here would fund C5 with
            // that much more real judging. See BtStoppingPolicy.verdictsThisArm.
            mainConditionTotalComparisons = completedResults.size
            if (config.llm.judgeOptionMode.equals("RESOLVED", ignoreCase = true)) {
                val inj = resolvedInjected.get(); val un = resolvedUnavailable.get()
                val tot = (inj + un).coerceAtLeast(1)
                log.info(
                    "[ARENA-OPTMODE] RESOLVED: selected option attached to $inj/${inj + un} traces" +
                        " (${"%.1f".format(java.util.Locale.US, 100.0 * inj / tot)}%);" +
                        " $un left verbatim because `pred` was missing or unresolvable"
                )
            }
            // Agreement is reported over the decidable subset only, so the denominator
            // has to be visible somewhere: from the export alone a reader cannot tell
            // the rate is conditional.
            val decidable = completedResults.count { it.judgeAccuracyAgreement.isNotEmpty() }
            val allCmp = completedResults.size.coerceAtLeast(1)
            log.info(
                "[ARENA-AGREE] decidable comparisons: $decidable of ${completedResults.size}" +
                    " (${"%.1f".format(java.util.Locale.US, 100.0 * decidable / allCmp)}%);" +
                    " agreement is reported over the decidable subset only"
            )
            log.info(
                "MAIN condition finished. Captured budget limit: $mainConditionTotalComparisons" +
                    " verdicts (leaf-credited was ${totalMatches.toInt()}; the arms are matched on" +
                    " verdicts because only the partitioned arm can inflate the leaf-credited count)."
            )
        }

        val pairs = modelNames.flatMapIndexed { i, a -> modelNames.drop(i + 1).map { b -> a to b } }
        val report = aggregate(completedResults, pairs, req, trajectory, admittedModels = modelNames)

        // Export evaluated triples if this is the C1/MAIN condition
        val isExportCondition = req.condition.equals("MAIN", ignoreCase = true)
        if (isExportCondition && evaluatedTriples.isNotEmpty()) {
            val baseSnapshotId = snapshotId.substringBefore("_MAIN").substringBefore("_ORACLE").substringBefore("_C3").substringBefore("_C5").substringBefore("_GENERIC_JUDGE").substringBefore("_RANDOM_SCHEDULER").substringBefore("_KMEANS_BASELINE").substringBefore("_WARD_BASELINE").substringBefore("_RANDOMNULL_BASELINE")
            val triplesFile = File("frozen_triples_${baseSnapshotId}_MAIN.json")
            try {
                triplesFile.writeText(json.encodeToString<List<FrozenMatchTriple>>(evaluatedTriples))
                log.info("Successfully exported ${evaluatedTriples.size} frozen triples to ${triplesFile.absolutePath}")
            } catch (e: Exception) {
                log.error("Failed to export frozen triples: ${e.message}", e)
            }
        }

        return@coroutineScope report
    }

    // ─── Core per-query logic ────────────────────────────────────────────────


    // ─── Aggregation ─────────────────────────────────────────────────────────

    private fun aggregate(
        results: List<QueryBenchmarkResult>,
        pairs: List<Pair<String, String>>,
        req: BenchmarkRequest,
        trajectory: List<TrajectoryPoint> = emptyList(),
        // Models that actually competed. Not req.models: a model rejected by [ARENA-INGEST]
        // has no comparisons, so ranking it against ground truth would inject a meaningless
        // rank into the correlation metrics.
        admittedModels: List<String> = req.models.map { it.modelName }
    ): BenchmarkReport {

        // ─── Compute judge-GT agreement per leaf ───
        val leafAgreement = results.groupBy { it.domainEvaluations.firstOrNull()?.nodeId }
            .mapValues { (nodeId, resList) ->
                if (nodeId == null) return@mapValues 0.0
                val total = resList.size
                val agreeing = resList.count { r ->
                    val pairKey = r.judgeAccuracyAgreement.keys.firstOrNull() ?: ""
                    r.judgeAccuracyAgreement[pairKey] == true
                }
                if (total > 0) agreeing.toDouble() / total else 0.0
            }

        val root = taxonomyService.getGraph()
        if (root != null) {
            val allNodes = mutableListOf<GraphNode>()
            val visited = mutableSetOf<String>()
            fun walk(n: GraphNode) {
                if (!visited.add(n.id)) return
                allNodes.add(n)
                n.children.forEach { walk(it) }
            }
            walk(root)
            leafAgreement.forEach { (nodeId, agreement) ->
                allNodes.firstOrNull { it.id == nodeId }?.let { node ->
                    node.judgeGtAgreement = agreement
                }
            }
        }

        val totalQueries = results.size
        val coverageRate = if (totalQueries > 0) results.count { it.hadJudge }.toDouble() / totalQueries else 0.0

        // Overall agreement across all pairs and queries
        val allAgreements = results.flatMap { it.judgeAccuracyAgreement.values }
        val overallAgreement = if (allAgreements.isEmpty()) 0.0
        else allAgreements.count { it }.toDouble() / allAgreements.size

        // Per-pair stats
        val perPairStats = pairs.map { (modelA, modelB) ->
            val pairKey = "${modelA}_vs_${modelB}"
            val pairResults = results.filter { pairKey in it.judgeAccuracyAgreement }

            var judgeWinsA = 0; var judgeWinsB = 0; var judgeTies = 0
            var accWinsA = 0; var accWinsB = 0; var accTies = 0
            var totalConf = 0.0; var confCount = 0

            pairResults.forEach { qr ->
                // GT accuracy winner
                val aCorrect = qr.modelCorrect[modelA] ?: false
                val bCorrect = qr.modelCorrect[modelB] ?: false
                when {
                    aCorrect && !bCorrect -> accWinsA++
                    bCorrect && !aCorrect -> accWinsB++
                    else -> accTies++
                }
                // Judge winner (from primary domain evaluation)
                val evals = qr.pairEvaluations[pairKey] ?: qr.domainEvaluations
                val primaryEval = evals
                    .filter { it.confidence >= req.confidenceGate }
                    .maxByOrNull { it.confidence }
                primaryEval?.let { eval ->
                    when (eval.winner.uppercase()) {
                        "MODEL A" -> judgeWinsA++
                        "MODEL B" -> judgeWinsB++
                        else -> judgeTies++
                    }
                    totalConf += eval.confidence
                    confCount++
                }
            }

            val agreementRate = pairResults
                .mapNotNull { it.judgeAccuracyAgreement[pairKey] }
                .let { list -> if (list.isEmpty()) 0.0 else list.count { it }.toDouble() / list.size }

            ModelPairStats(
                modelA = modelA,
                modelB = modelB,
                totalMatches = pairResults.size,
                judgeWinsA = judgeWinsA,
                judgeWinsB = judgeWinsB,
                judgeTies = judgeTies,
                accuracyWinsA = accWinsA,
                accuracyWinsB = accWinsB,
                accuracyTies = accTies,
                judgeAccuracyAgreementRate = agreementRate,
                avgConfidence = if (confCount > 0) totalConf / confCount else 0.0,
                isExhausted = pairResults.size < 20
            )
        }

        // Per-leaf-domain stats
        val perDomainStats = results
            .flatMap { qr ->
                qr.domainEvaluations
                    .filter { it.confidence >= req.confidenceGate }
                    .map { eval -> eval.domainLabel to qr }
            }
            .groupBy { it.first }
            .map { (domain, pairs) ->
                val qrs = pairs.map { it.second }
                val agreementRates = qrs.flatMap { qr -> qr.judgeAccuracyAgreement.values }
                val avgConf = qrs
                    .flatMap { qr -> qr.domainEvaluations.filter { it.domainLabel == domain } }
                    .map { it.confidence }.average()
                DomainStats(
                    domain = domain,
                    totalQueries = qrs.size,
                    judgeAccuracyAgreementRate = if (agreementRates.isEmpty()) 0.0
                    else agreementRates.count { it }.toDouble() / agreementRates.size,
                    avgConfidence = avgConf,
                    coverageRate = 1.0  // all included had a judge for this domain
                )
            }.sortedByDescending { it.totalQueries }

        // Per-GT-category stats (coarser, MMLU-Pro level)
        val perCategoryStats = results
            .groupBy { it.gtCategory }
            .map { (cat, qrs) ->
                val agreementRates = qrs.flatMap { it.judgeAccuracyAgreement.values }
                val covRate = if (qrs.isNotEmpty()) qrs.count { it.hadJudge }.toDouble() / qrs.size else 0.0
                val avgConf = qrs.flatMap { qr ->
                    qr.domainEvaluations.filter { it.confidence >= req.confidenceGate }
                        .map { it.confidence }
                }.let { cs -> if (cs.isEmpty()) 0.0 else cs.average() }
                DomainStats(
                    domain = cat,
                    totalQueries = qrs.size,
                    judgeAccuracyAgreementRate = if (agreementRates.isEmpty()) 0.0
                    else agreementRates.count { it }.toDouble() / agreementRates.size,
                    avgConfidence = avgConf,
                    coverageRate = covRate
                )
            }.sortedByDescending { it.totalQueries }

        val dummyReport = BenchmarkReport(
            totalQueries = totalQueries,
            totalModelPairs = pairs.size,
            coverageRate = coverageRate,
            overallJudgeAccuracyAgreement = overallAgreement,
            perPairStats = perPairStats,
            perDomainStats = perDomainStats,
            perCategoryStats = perCategoryStats,
            queryResults = results
        )
        val globalReport = try {
            ValidationService.computeMetrics(dummyReport, admittedModels, "OVERALL")
        } catch (e: Exception) {
            null
        }

        // ── [ARENA-VERDICT] judge behaviour, not just judge output ──────────────
        // Every comparison is judged twice with the positions swapped; positionFlip
        // records that the two orders DISAGREED, which is then forced to a TIE. The
        // flip rate is therefore the direct measure of positional inconsistency, and
        // it is the number that justifies the bias-control design in Chapter 3. None
        // of it appears anywhere in the exported CSVs.
        run {
            val evals = results.flatMap { it.domainEvaluations }
            if (evals.isNotEmpty()) {
                val flips = evals.count { it.positionFlip }
                val winners = evals.groupingBy { it.winner }.eachCount()
                val tieSources = evals.filter { it.winner == "TIE" }
                    .groupingBy { it.tieSource ?: "<none>" }.eachCount()
                val confs = evals.map { it.confidence }.sorted()
                fun pct(p: Double) = confs[(confs.size * p).toInt().coerceAtMost(confs.size - 1)]

                // DomainEvaluation.winner is a POSITION label ("Model A"/"Model B"), not a
                // model name, so the raw tally reads "Model B=38" and says nothing about which
                // model won until you join it against the pairing table by hand. Resolve it
                // through pairEvaluations, whose key is "<modelA>_vs_<modelB>". Both tallies
                // are kept: the positional one is the position-bias signal (a judge that
                // always answers "B" shows up there and nowhere else), the resolved one is
                // what a reader actually wants.
                val winsByModel = mutableMapOf<String, Int>()
                results.forEach { r ->
                    r.pairEvaluations.forEach { (pairKey, evs) ->
                        // Model names contain '_' (Meta-Llama-3_1-70B-Instruct) but not '_vs_'.
                        val sides = pairKey.split("_vs_", limit = 2)
                        if (sides.size == 2) {
                            evs.forEach { e ->
                                when (e.winner) {
                                    "Model A" -> winsByModel.merge(sides[0], 1, Int::plus)
                                    "Model B" -> winsByModel.merge(sides[1], 1, Int::plus)
                                }
                            }
                        }
                    }
                }
                log.info(
                    "[ARENA-VERDICT] evaluations=${evals.size} overQueries=${results.count { it.hadJudge }}" +
                        " positionFlips=$flips (${"%.1f".format(java.util.Locale.US, 100.0 * flips / evals.size)}%" +
                        " order-inconsistent, forced to TIE)" +
                        " | wins by model: " + (if (winsByModel.isEmpty()) "<unresolved>"
                            else winsByModel.entries.sortedByDescending { it.value }
                                .joinToString(", ") { "${it.key}=${it.value}" }) +
                        " | by position slot: " + winners.entries.joinToString(", ") { "${it.key}=${it.value}" } +
                        " | tie sources: " + (if (tieSources.isEmpty()) "none" else tieSources.entries.joinToString(", ") { "${it.key}=${it.value}" }) +
                        " | confidence p10=${"%.3f".format(java.util.Locale.US, pct(0.10))}" +
                        " median=${"%.3f".format(java.util.Locale.US, pct(0.50))}" +
                        " p90=${"%.3f".format(java.util.Locale.US, pct(0.90))}"
                )
                // The judge's confidence is effectively TWO-VALUED, not graded: measured on the
                // first end-to-end run, p10 = 0.500, median = 0.950, p90 = 0.950. So
                // confidenceGate is a binary filter that partitions a bimodal distribution at the
                // obvious point between the modes — it is not a tunable threshold on a continuum,
                // and describing it as one would misrepresent what it does. Report the modes and
                // the share the gate actually removes, so the claim can be checked rather than
                // assumed.
                run {
                    val distinct = confs.distinct().sorted()
                    val gate = req.confidenceGate
                    val below = confs.count { it < gate }
                    val modes = confs.groupingBy { it }.eachCount()
                        .entries.sortedByDescending { it.value }.take(4)
                    log.info(
                        "[ARENA-VERDICT] confidence is ${if (distinct.size <= 3) "effectively discrete" else "continuous"}" +
                            " with ${distinct.size} distinct value(s): " +
                            modes.joinToString(", ") {
                                "${"%.3f".format(java.util.Locale.US, it.key)}x${it.value}"
                            } +
                            " | gate=${"%.2f".format(java.util.Locale.US, gate)} removes $below/${confs.size}" +
                            " (${"%.1f".format(java.util.Locale.US, 100.0 * below / confs.size)}%)" +
                            (if (distinct.size <= 3)
                                " — a binary partition of a bimodal distribution, not a graded threshold"
                            else "")
                    )
                }

                val perNode = evals.groupingBy { it.nodeId ?: it.domain }.eachCount()
                    .entries.sortedByDescending { it.value }
                log.info(
                    "[ARENA-VERDICT] evaluations per node (top 10): " +
                        perNode.take(10).joinToString(", ") { "${it.key}=${it.value}" } +
                        (if (perNode.size > 10) " ... ${perNode.size} nodes total" else "")
                )
            } else {
                log.warn("[ARENA-VERDICT] no judged comparisons — every result came from cache or was skipped")
            }
        }

        if (globalReport != null) {
            log.info("GT Rank Correlation — Spearman ρ = ${"%.2f".format(java.util.Locale.US, globalReport.spearmanRho)}, Kendall τ = ${"%.2f".format(java.util.Locale.US, globalReport.kendallTau)} (n=${admittedModels.size} models, ${req.category ?: "All Domains"})")
        } else {
            log.info("GT Rank Correlation — Spearman ρ = 1.00, Kendall τ = 1.00 (n=${admittedModels.size} models)")
        }

        return BenchmarkReport(
            totalQueries = totalQueries,
            totalModelPairs = pairs.size,
            coverageRate = coverageRate,
            overallJudgeAccuracyAgreement = overallAgreement,
            perPairStats = perPairStats,
            perDomainStats = perDomainStats,
            perCategoryStats = perCategoryStats,
            queryResults = results,
            trajectory = trajectory
        )
    }

    /** Counts how often RESOLVED could and could not attach the selected option. */
    private val resolvedInjected = java.util.concurrent.atomic.AtomicInteger(0)
    private val resolvedUnavailable = java.util.concurrent.atomic.AtomicInteger(0)

    // Strips the arx JSON envelope (and its correctness-predicting `reason_code`) down to
    // the prose response. See taxonomy.dataset.unwrapTraceEnvelope.
    private fun getRobustTrace(r: ModelEvalResult): String {
        val output = r.modelOutput?.let { unwrapTraceEnvelope(it) }
        if (!output.isNullOrBlank()) return maybeResolveSelection(r, output)
        val pred = r.pred?.trim()?.uppercase() ?: return "The model did not provide a prediction."
        val predChar = pred.firstOrNull() ?: return "The model did not provide a prediction."
        if (predChar in 'A'..'J') {
            val idx = predChar - 'A'
            if (idx in r.options.indices) {
                return "The model selected option $predChar: \"${r.options[idx]}\"."
            }
        }
        return "The model predicted: \"$pred\"."
    }

    /**
     * Under `judgeOptionMode = RESOLVED`, append this model's OWN selected option, resolved
     * from its `pred` letter to the option text, so a bare "the answer is (C)" carries a
     * referent once the candidate set is withheld.
     *
     * WHY. Measured over 2,000 reserved traces: 72% end in "the answer is (X)" and only 23%
     * carry the option text anywhere nearby. Withholding the options without this leaves
     * roughly half the traces' conclusions unreadable — "(C)" against "(F)" — so a fall in
     * judge agreement cannot be separated into "assessed the reasoning instead" and "could
     * not tell what was claimed". Resolving the selection holds the second fixed and varies
     * only the first, which is the question RQ1 asks.
     *
     * The injection is ADDITIVE and marked, never a rewrite of the model's prose: the trace
     * stays verbatim and gains one bracketed line. It is a transformation applied before
     * judging and must be reported as such.
     *
     * ANSWER-KEY BLINDNESS. This appends the model's OWN selection, which is wrong on a
     * large fraction of comparisons. `gt_answer` is never consulted here or anywhere on the
     * judging path.
     */
    private fun maybeResolveSelection(r: ModelEvalResult, trace: String): String {
        if (!config.llm.judgeOptionMode.equals("RESOLVED", ignoreCase = true)) return trace
        val predChar = r.pred?.trim()?.uppercase()?.firstOrNull()
        if (predChar == null || predChar !in 'A'..'J') {
            resolvedUnavailable.incrementAndGet(); return trace
        }
        val idx = predChar - 'A'
        if (idx !in r.options.indices) { resolvedUnavailable.incrementAndGet(); return trace }
        val text = r.options[idx].toString().trim()
        if (text.isEmpty()) { resolvedUnavailable.incrementAndGet(); return trace }
        resolvedInjected.incrementAndGet()
        return "$trace\n\n[This model's selected answer: ($predChar) $text]"
    }

    private fun logLeafLeaderboard(nodeId: String, nodeName: String, state: NodeBtState, round: Int) {
        val sorted = state.btScores.entries.sortedByDescending { it.value }
        val lines = StringBuilder()
        lines.appendLine("  ┌── [$nodeName] (round $round, n=${state.totalComparisons}) ──")
        sorted.forEachIndexed { rank, (model, score) ->
            val se    = state.stdErrors[model]?.let { "±%.3f".format(it) } ?: "  n/a "
            val short = model.replace("Meta-Llama-3_1-", "L3.1-")
                            .replace("Llama-2-", "L2-")
                            .replace("-Instruct", "-I")
                            .replace("gemini-3.1-pro_5-shots", "gemini")
                            .replace("claude-3-5-sonnet-20241022", "claude")
                            .take(18).padEnd(18)
            lines.appendLine("  │ %2d. %s %+.3f %s".format(rank+1, short, score, se))
        }
        lines.append("  └─────────────────────────────────")
        log.info(lines.toString())
    }

    // adjustForPositionBias was removed 2026-09-05: it double-counted ties (the order
    // ledgers half-credit them and BtMmFitter adds 0.5*ties again) and only ever in
    // favour of modelA, the lexicographically smaller model on every pair. Detection
    // lives on as PairStatsLedger.auditOrderBias; debiasing happens at the verdict
    // level, where an order-inconsistent split is forced to a TIE.

    private fun logRoundSummary(round: Int, summaries: List<PairRoundSummary>) {
        log.info("--- Round $round Pair Summary (${summaries.size} pairs) ---")
        summaries
            .sortedByDescending { abs(it.wins - it.losses) }  // most decisive first
            .forEach { s ->
                log.info("  ${s.pair.padEnd(55)} W:${s.wins} L:${s.losses} T:${s.ties}" +
                         " flips:${s.posFlips} conf:${"%.2f".format(s.avgConf)}")
            }
    }

    private fun emptyReport() = BenchmarkReport(
        totalQueries = 0, totalModelPairs = 0,
        coverageRate = 0.0, overallJudgeAccuracyAgreement = 0.0,
        perPairStats = emptyList(), perDomainStats = emptyList(),
        perCategoryStats = emptyList(), queryResults = emptyList()
    )
}

private data class SchedulingParams(
    val minComparisonsPerLeaf: Int,
    val targetConvergenceFraction: Double,
    val separationThreshold: Double,
    val queriesPerPair: Int,
    val budgetPerPair: Int,
    val maxRounds: Int,
    val minTotalComparisons: Int,
    val maxConcurrentPerModel: Int,
    val questionsPerRound: Int
)

private fun buildSchedulingParams(
    numModels: Int,
    numLeaves: Int,
    totalQuestions: Int,
    minQuestionsPerLeaf: Int,
    req: BenchmarkRequest
): SchedulingParams {
    val K = numModels
    val numPairs = K * (K - 1) / 2

    // Minimum comparisons per leaf: enough for each pair to appear at least twice
    // and for the BT fitter to have a non-degenerate solution
    // Formula: max(K, 2*K) = 2K, floored at 6, capped at 30
    val minCompsPerLeaf = (2 * K).coerceIn(6, 30)

    // Queries per pair: enough to detect a medium effect (BT gap ~0.5 SE)
    // with ~80% power at alpha=0.05 requires ~8-12 comparisons per pair
    // Scale up slightly if we have many questions available
    val avgQuestionsPerLeaf = if (numLeaves > 0) totalQuestions / numLeaves else 10
    val baseQueriesPerPair = when {
        minQuestionsPerLeaf >= 40 -> 8
        minQuestionsPerLeaf >= 20 -> 6
        minQuestionsPerLeaf >= 12 -> 4
        else -> 2
    }
    var queriesPerPair = minOf(baseQueriesPerPair, minQuestionsPerLeaf).coerceAtLeast(1)
    if (totalQuestions <= 20) {
        queriesPerPair = totalQuestions.coerceAtLeast(1)
    }

    // Budget = enough for 2 full task-slot rotations per pair, floored at BATCH_STEP_SIZE*2
    val budgetPerPair = (queriesPerPair * 2)
        .coerceAtLeast(BtMatchScheduler.BATCH_STEP_SIZE * 2)
        .coerceAtMost(maxOf(queriesPerPair, minQuestionsPerLeaf / 2))   // never exceed half the leaf pool unless it drops below queriesPerPair

    // Convergence fraction: deliberately CONSTANT across granularities. The central
    // comparison in this thesis is across granularities (14 domains vs 87 leaves vs 152),
    // so a leaf-count-dependent stopping rule would let the finer partition stop on less
    // evidence than the baseline it is measured against — a confound sitting directly
    // under the link-3 comparison. 0.70 matches the value used by the 6-20 leaf runs
    // that make up most of the series rather than being tuned for a new result.
    val convergenceFraction = 0.70

    // Separation threshold: stricter with more questions (can afford higher confidence)
    val separationThreshold = when {
        avgQuestionsPerLeaf >= 15 -> 1.5
        else                      -> 1.0   // relax if data is scarce
    }

    // Max rounds: enough for every leaf to reach minCompsPerLeaf at BATCH_STEP_SIZE per round
    // Each round schedules batchSize / numLeaves queries per leaf approximately
    val roundsNeeded = (minCompsPerLeaf * numPairs * numLeaves) /
                       (req.questionsPerRound.coerceAtLeast(1)) + 5
    val maxRounds = roundsNeeded.coerceIn(10, 40)

    // Global minimum before any stopping: all models must have appeared at least once
    val minTotalComparisons = numPairs * 2

    // Max concurrent per model: allow more parallelism with more models
    val maxConcurrent = (K - 1).coerceIn(2, 4)

    // Must fit at least one task slot per pair per round.
    // Use parallelism * 4 as cap (not *3), and floor at numPairs * BATCH_STEP_SIZE if parallelism allows.
    val idealQPerRound = numPairs * BtMatchScheduler.BATCH_STEP_SIZE
    val questionsPerRound = idealQPerRound
        .coerceAtMost(req.parallelism * 4)         // was *3 → *4
        .coerceAtLeast(numPairs * 2)               // at minimum 2 questions per pair per round
        .coerceAtLeast(req.questionsPerRound)

    return SchedulingParams(
        minComparisonsPerLeaf = minCompsPerLeaf,
        targetConvergenceFraction = convergenceFraction,
        separationThreshold = separationThreshold,
        queriesPerPair = queriesPerPair,
        budgetPerPair = budgetPerPair,
        maxRounds = maxRounds,
        minTotalComparisons = minTotalComparisons,
        maxConcurrentPerModel = maxConcurrent,
        questionsPerRound = questionsPerRound
    )
}

data class PairRoundSummary(
    val pair: String,
    val wins: Int,
    val losses: Int,
    val ties: Int,
    val posFlips: Int,
    val avgConf: Double
)
