package taxonomy.service

import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.ModelEvalStore
import taxonomy.dataset.ModelEvalResult
import taxonomy.model.*
import kotlin.collections.filter

@Service
class TaxonomyBenchmarkService(
    private val arenaService: TaxonomyArenaService,
    private val rankingService: TaxonomyRankingService,
    private val datasetFetcher: MMLUDatasetFetcher,
    private val taxonomyService: TaxonomyService,
    private val evalStore: ModelEvalStore
) {
    private val log = LoggerFactory.getLogger("taxonomy.BenchmarkService")

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

    private fun propagateOutcome(
        leafId: String,
        ancestors: Set<String>,
        modelA: String,
        modelB: String,
        outcome: DomainEvaluation,
        snapshotId: String
    ) {
        val (wA, wB) = when (outcome.winner.uppercase()) {
            "MODEL A" -> 1.0 to 0.0
            "MODEL B" -> 0.0 to 1.0
            "TIE"     -> 0.5 to 0.5
            else      -> return
        }
        val isTie = outcome.winner.equals("TIE", ignoreCase = true)

        for (nodeId in ancestors) {
            val list = rankingService.getNodePairStats(nodeId, snapshotId)
            val existing = list.firstOrNull { 
                (it.modelA == modelA && it.modelB == modelB) || (it.modelA == modelB && it.modelB == modelA)
            }
            val stats = if (existing != null) {
                if (existing.modelA == modelA) {
                    existing.winsA += wA
                    existing.winsB += wB
                } else {
                    existing.winsA += wB
                    existing.winsB += wA
                }
                existing.ties += if (isTie) 1 else 0
                existing.totalComparisons += 1
                existing.positionFlips += if (outcome.positionFlip) 1 else 0
                existing.lastUpdated = System.currentTimeMillis()
                existing
            } else {
                NodePairStats(
                    nodeId = nodeId,
                    modelA = modelA,
                    modelB = modelB,
                    winsA = wA,
                    winsB = wB,
                    ties = if (isTie) 1 else 0,
                    totalComparisons = 1,
                    positionFlips = if (outcome.positionFlip) 1 else 0,
                    lastUpdated = System.currentTimeMillis()
                )
            }
            rankingService.saveNodePairStats(stats, snapshotId)
        }
    }

    suspend fun runBenchmark(
        req: BenchmarkRequest,
        onProgress: ((BenchmarkLiveStats) -> Unit)? = null
    ): BenchmarkReport = coroutineScope {
        require(req.models.size >= 2) { "Need at least 2 models" }
        val modelNames = req.models.map { it.modelName }

        val matrix = evalStore.getResultsMatrix(
            models = modelNames,
            category = req.category,
            reservedOnly = req.reservedOnly,
            limit = req.queryLimit
        )

        log.info("Benchmark: ${matrix.size} questions, ${modelNames.size} models")

        if (matrix.isEmpty()) {
            return@coroutineScope emptyReport()
        }

        val root = taxonomyService.getGraph() ?: return@coroutineScope emptyReport()
        val allNodes = getAllNodes(root)

        val frozenLeafIds = allNodes.filter { it.children.isEmpty() }.map { it.id }.toSet()

        // Pre-route all questions to target nodes dynamically using the NiW routing engine
        val nodeToQueries = mutableMapOf<String, MutableList<Int>>()
        var outlierCount = 0
        matrix.forEach { (qId, modelResults) ->
            val sample = modelResults.values.firstOrNull() ?: return@forEach
            val leaves = arenaService.routeToLeaves(sample.questionText, frozenLeafIds)
            if (leaves.isEmpty()) {
                outlierCount++
                log.debug("qId=$qId is an outlier — no leaf match, skipping")
                return@forEach
            }
            leaves.forEach { leaf ->
                nodeToQueries.getOrPut(leaf.id) { mutableListOf() }.add(qId)
            }
        }
        log.info("Pre-routing complete: ${matrix.size - outlierCount} questions routed, $outlierCount outliers discarded")

        val numPairs = modelNames.size * (modelNames.size - 1) / 2
        val scheduler = BtMatchScheduler(
            minQueriesForBenchmark = 1,
            queriesPerPair = 20,
            budgetPerPair = 100
        )
        val stoppingPolicy = BtStoppingPolicy(
            minComparisons = maxOf(30, numPairs * 8),
            stabilityRounds = 3,
            separationThreshold = 2.0,
            maxRounds = 20
        )

        val snapshotId = taxonomyService.activeSnapshotId() ?: "unsaved"
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
                    totalComparisons = nodePairs.sumOf { it.totalComparisons },
                    lastFitAt = System.currentTimeMillis()
                )
            }
        }

        val targetNodes = scheduler.selectTargetNodes(allNodes, btStates, nodeToQueries, maxNodes = 100)
        log.info("Selected fixed targetNodes for the entire run: ${targetNodes.map { it.label ?: it.id }}")

        var round = 0
        val maxRounds = 20
        val completedResults = java.util.Collections.synchronizedList(mutableListOf<QueryBenchmarkResult>())

        while (round < maxRounds && !stoppingPolicy.shouldStop(btStates, round, root.id)) {
            if (targetNodes.isEmpty()) break

            val batch = scheduler.selectNextBatch(
                targetNodes = targetNodes,
                btStates = btStates,
                pairStats = pairStatsMap,
                models = modelNames,
                resultsMatrix = matrix,
                nodeToQueries = nodeToQueries,
                batchSize = req.questionsPerRound
            )
            log.debug("Round $round - scheduled batch size: ${batch.size}")
            if (batch.isEmpty()) break

            val roundResults = batch.map { task ->
                async(Dispatchers.IO) {
                    val leafNode = allNodes.firstOrNull { it.id == task.nodeId } ?: return@async emptyList<QueryBenchmarkResult>()

                    task.queryIds.mapNotNull { queryIdStr ->
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

                        val cached = rankingService.getRecordedMatch(
                            snapshotId = snapshotId,
                            domain = domainName,
                            query = sample.questionText,
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
                                frozenLeafIds = frozenLeafIds
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

                        val primaryEval = if (satisfiesGate) {
                            rawPrimaryEval
                        } else {
                            log.warn("evaluation confidence ${rawPrimaryEval.confidence} is below confidenceGate ${req.confidenceGate} for qId $qId. Treating as LOW_CONFIDENCE_TIE.")
                            rawPrimaryEval.copy(winner = "TIE", rationale = "LOW_CONFIDENCE_TIE: Below confidence gate (${rawPrimaryEval.confidence} < ${req.confidenceGate}). Original: ${rawPrimaryEval.rationale}")
                        }

                        if (req.updateRankings && cached == null && primaryEval.winner != "INVALID") {
                            val isTie = primaryEval.winner.equals("TIE", ignoreCase = true)
                            val isModelA = primaryEval.winner.equals("Model A", ignoreCase = true)
                            rankingService.recordMatch(
                                query = sample.questionText,
                                domain = domainName,
                                winner = if (isTie) task.modelA else if (isModelA) task.modelA else task.modelB,
                                loser = if (isTie) task.modelB else if (isModelA) task.modelB else task.modelA,
                                isTie = isTie,
                                confidence = primaryEval.confidence,
                                snapshotId = snapshotId,
                                modelA = task.modelA,
                                modelB = task.modelB
                            )
                        }

                        val ancestors = leafNode.allAncestors()
                        propagateOutcome(
                            leafId = leafNode.id,
                            ancestors = ancestors,
                            modelA = task.modelA,
                            modelB = task.modelB,
                            outcome = primaryEval,
                            snapshotId = snapshotId
                        )

                        val modelAnswers = modelResults.mapValues { (_, r) -> r.pred ?: "?" }
                        val modelCorrect = modelResults.mapValues { (_, r) -> r.isCorrect }
                        val aCorrect = modelCorrect[task.modelA] ?: false
                        val bCorrect = modelCorrect[task.modelB] ?: false
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

                        QueryBenchmarkResult(
                            query = sample.questionText,
                            gtCategory = gtCategory,
                            gtCorrectAnswer = gtAnswer,
                            modelAnswers = modelAnswers,
                            modelCorrect = modelCorrect,
                            matchedLeafLabels = listOf(primaryEval.domain),
                            hadJudge = true,
                            domainEvaluations = listOf(primaryEval),
                            pairEvaluations = mapOf(pairKey to listOf(primaryEval)),
                            judgeAccuracyAgreement = mapOf(pairKey to agrees)
                        )
                    }
                }
            }.awaitAll().flatten()

            completedResults.addAll(roundResults)

            log.info("--- Round $round Results Summary ---")
            roundResults.forEach { qr ->
                val primaryEval = qr.domainEvaluations.firstOrNull()
                val pairKey = qr.pairEvaluations.keys.firstOrNull() ?: "unknown"
                if (primaryEval != null) {
                    log.info("  [$pairKey] Question: \"${qr.query.take(65)}...\" -> Judge Winner: ${primaryEval.winner}${primaryEval.tieSource?.let { "[$it]" } ?: ""} (confidence: ${primaryEval.confidence})")
                }
            }

            val dirtyNodes = roundResults.flatMap { qr ->
                val eval = qr.domainEvaluations.firstOrNull() ?: return@flatMap emptyList<String>()
                val node = allNodes.firstOrNull { it.id == eval.nodeId } ?: allNodes.firstOrNull { it.label == eval.domain } ?: return@flatMap emptyList<String>()
                node.allAncestors()
            }.toSet()
            log.trace("Round $round - dirtyNodes: $dirtyNodes")

            for (nodeId in dirtyNodes) {
                val nodePairs = rankingService.getNodePairStats(nodeId, snapshotId)
                log.trace("Round $round - updated nodePairs for $nodeId: ${nodePairs.map { "${it.modelA}_vs_${it.modelB}:${it.totalComparisons}" }}")
                pairStatsMap[nodeId] = nodePairs.toMutableList()

                if (nodePairs.isNotEmpty()) {
                    val scores = BtMmFitter.fit(modelNames, nodePairs)
                    val stdErrors = BtMmFitter.estimateStdErrors(modelNames, scores, nodePairs)
                    val state = NodeBtState(
                        nodeId = nodeId,
                        btScores = scores,
                        stdErrors = stdErrors,
                        fitVersion = (btStates[nodeId]?.fitVersion ?: 0) + 1,
                        totalComparisons = nodePairs.sumOf { it.totalComparisons },
                        lastFitAt = System.currentTimeMillis()
                    )
                    rankingService.saveBtState(state, snapshotId)
                    btStates[nodeId] = state
                }
            }

            val rootState = btStates[root.id]
            if (rootState != null) {
                log.info("--- Bradley-Terry Ratings (Round $round) ---")
                rootState.btScores.entries.sortedByDescending { it.value }.forEach { (model, score) ->
                    val stdErr = rootState.stdErrors[model] ?: 0.0
                    log.info("  * $model: score = ${String.format("%.4f", score)} (± ${String.format("%.4f", stdErr)})")
                }
            }

            if (onProgress != null && completedResults.isNotEmpty()) {
                val allAgreements = completedResults.flatMap { it.judgeAccuracyAgreement.values }
                val runningAgreement = if (allAgreements.isNotEmpty()) allAgreements.count { it }.toDouble() / allAgreements.size else 0.0
                val runningCoverage = 1.0
                val perCategoryProgress = completedResults.groupBy { it.gtCategory }.mapValues { it.value.size }

                val pairs = modelNames.flatMapIndexed { i, a -> modelNames.drop(i + 1).map { b -> a to b } }
                val livePairStats = pairs.map { (modelA, modelB) ->
                    val pairKey = "${modelA}_vs_${modelB}"
                    val pairResults = completedResults.filter { pairKey in it.judgeAccuracyAgreement }
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

                val lastResult = completedResults.lastOrNull()
                val rootState = btStates[root.id]
                val activeTargetNames = targetNodes.mapNotNull { it.label }
                val live = BenchmarkLiveStats(
                    processed = completedResults.size,
                    total = matrix.size,
                    currentQuestion = lastResult?.query ?: "",
                    runningAgreement = runningAgreement,
                    runningCoverage = runningCoverage,
                    perCategoryProgress = perCategoryProgress,
                    pairStats = livePairStats,
                    currentRound = round + 1,
                    activeTargets = activeTargetNames,
                    btRatings = rootState?.btScores ?: emptyMap(),
                    btErrors = rootState?.stdErrors ?: emptyMap()
                )
                onProgress.invoke(live)
            }

            round++
        }

        val pairs = modelNames.flatMapIndexed { i, a -> modelNames.drop(i + 1).map { b -> a to b } }
        aggregate(completedResults, pairs, req)
    }

    // ─── Core per-query logic ────────────────────────────────────────────────

    private suspend fun processPrecomputedQuery(
        questionId: Int,
        modelResults: Map<String, ModelEvalResult>,
        pairs: List<Pair<String, String>>,
        req: BenchmarkRequest
    ): QueryBenchmarkResult? = coroutineScope {

        val sample = modelResults.values.firstOrNull() ?: return@coroutineScope null
        val gtAnswer = sample.gtAnswer      // e.g. "A"
        val gtCategory = sample.category

        val snapshotId = taxonomyService.activeSnapshotId() ?: "unsaved"
        val root = taxonomyService.getGraph() ?: return@coroutineScope null
        val allNodes = getAllNodes(root)
        val frozenLeafIds = allNodes.filter { it.children.isEmpty() }.map { it.id }.toSet()

        // Model correctness straight from pre-extracted pred
        val modelAnswers = modelResults.mapValues { (_, r) -> r.pred ?: "?" }
        val modelCorrect = modelResults.mapValues { (_, r) -> r.isCorrect }

        // Run all pairs through judges in parallel
        val pairResults = pairs.map { (modelA, modelB) ->
            async {
                val outputA = modelResults[modelA] ?: return@async null
                val outputB = modelResults[modelB] ?: return@async null

                runCatching {
                    val leaves = arenaService.routeToLeaves(sample.questionText, frozenLeafIds)
                    val judges = leaves.mapNotNull { arenaService.leafJudge(it) }
                    val primaryJudge = judges.maxByOrNull { it.depth } ?: return@async null
                    checkNotNull(primaryJudge.judgePrompt) {
                        "Attempted to record match for node ${primaryJudge.id} with no judgePrompt"
                    }
                    val domainName = requireNotNull(primaryJudge.label) { "Leaf node ${primaryJudge.id} has no label" }

                    val cached = rankingService.getRecordedMatch(
                        snapshotId = snapshotId,
                        domain = domainName,
                        query = sample.questionText,
                        modelA = modelA,
                        modelB = modelB
                    )

                    // Route the question to leaf judges (no model calls — just routing + judging)
                    val domainEvaluations = if (cached != null) {
                        val cachedWinner = when {
                            cached.isTie -> "Tie"
                            cached.winner == modelA -> "Model A"
                            cached.winner == modelB -> "Model B"
                            else -> "Tie"
                        }
                        listOf(
                            DomainEvaluation(
                                domain = cached.domain,
                                winner = cachedWinner,
                                rationale = "Cached match result",
                                confidence = 1.0
                            )
                        )
                    } else {
                        arenaService.evaluateWithPrecomputedTraces(
                            query = sample.questionText,
                            options = sample.options,
                            modelA = modelA,
                            traceA = getRobustTrace(outputA),
                            modelB = modelB,
                            traceB = getRobustTrace(outputB),
                            frozenLeafIds = frozenLeafIds
                        )
                    }

                    val primaryEval = domainEvaluations
                        .filter { it.confidence >= req.confidenceGate }
                        .maxByOrNull { eval ->
                            val depth = allNodes.firstOrNull { it.id == eval.nodeId }?.depth ?: 0
                            depth
                        }

                    val judgeWinner: String? = primaryEval?.let {
                        when (it.winner) {
                            "Model A" -> modelA
                            "Model B" -> modelB
                            else -> "tie"
                        }
                    }

                    // GT-based winner
                    val aCorrect = modelCorrect[modelA] ?: false
                    val bCorrect = modelCorrect[modelB] ?: false
                    val gtWinner = when {
                        aCorrect && !bCorrect -> modelA
                        bCorrect && !aCorrect -> modelB
                        else -> "tie"
                    }

                    val agrees = judgeWinner != null && judgeWinner == gtWinner

                    if (req.updateRankings && primaryEval != null && cached == null && primaryEval.winner != "INVALID") {
                        val isTie = judgeWinner == "tie"
                        rankingService.recordMatch(
                            query = sample.questionText,
                            domain = domainName,
                            winner = if (isTie) modelA else judgeWinner!!,
                            loser = if (isTie) modelB else if (judgeWinner == modelA) modelB else modelA,
                            isTie = isTie,
                            confidence = primaryEval.confidence,
                            snapshotId = snapshotId,
                            modelA = modelA,
                            modelB = modelB
                        )
                    }

                    val arenaResult = ArenaResult(
                        query = sample.questionText,
                        modelA = modelA,
                        modelB = modelB,
                        traceA = outputA.modelOutput,
                        traceB = outputB.modelOutput,
                        domainEvaluations = domainEvaluations
                    )

                    PairResult(
                        modelA = modelA, modelB = modelB,
                        arenaResult = arenaResult,
                        modelAnswers = modelAnswers,
                        modelCorrect = modelCorrect,
                        judgeWinner = judgeWinner,
                        gtWinner = gtWinner,
                        agreementKey = "${modelA}_vs_${modelB}" to agrees
                    )
                }.getOrElse { e ->
                    log.warn("Judge failed for $modelA vs $modelB on q$questionId: ${e.message}")
                    null
                }
            }
        }.awaitAll().filterNotNull()

        val leafLabels = pairResults
            .flatMap { pr -> pr.arenaResult.domainEvaluations.map { e -> e.domainLabel } }.distinct()

        val hadJudge = pairResults.any { pr ->
            pr.arenaResult.domainEvaluations.any { it.confidence >= req.confidenceGate }
        }

        val domainEvaluations = pairResults.flatMap { pr -> pr.arenaResult.domainEvaluations }.distinctBy { it.domainLabel }
        val pairEvaluations = pairResults.associate { pr -> pr.agreementKey.first to pr.arenaResult.domainEvaluations }
        val judgeAccuracyAgreement = pairResults.map { it.agreementKey }.toMap()

        QueryBenchmarkResult(
            query = sample.questionText,
            gtCategory = gtCategory,
            gtCorrectAnswer = gtAnswer,
            modelAnswers = modelAnswers,
            modelCorrect = modelCorrect,
            matchedLeafLabels = leafLabels,
            hadJudge = hadJudge,
            domainEvaluations = domainEvaluations,
            pairEvaluations = pairEvaluations,
            judgeAccuracyAgreement = judgeAccuracyAgreement
        )
    }

    // ─── Aggregation ─────────────────────────────────────────────────────────

    private fun aggregate(
        results: List<QueryBenchmarkResult>,
        pairs: List<Pair<String, String>>,
        req: BenchmarkRequest
    ): BenchmarkReport {

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

        return BenchmarkReport(
            totalQueries = totalQueries,
            totalModelPairs = pairs.size,
            coverageRate = coverageRate,
            overallJudgeAccuracyAgreement = overallAgreement,
            perPairStats = perPairStats,
            perDomainStats = perDomainStats,
            perCategoryStats = perCategoryStats,
            queryResults = results
        )
    }

    private fun getRobustTrace(r: ModelEvalResult): String {
        val output = r.modelOutput
        if (!output.isNullOrBlank()) return output
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

    private fun emptyReport() = BenchmarkReport(
        totalQueries = 0, totalModelPairs = 0,
        coverageRate = 0.0, overallJudgeAccuracyAgreement = 0.0,
        perPairStats = emptyList(), perDomainStats = emptyList(),
        perCategoryStats = emptyList(), queryResults = emptyList()
    )
}

private data class PairResult(
    val modelA: String,
    val modelB: String,
    val arenaResult: ArenaResult,
    val modelAnswers: Map<String, String>,
    val modelCorrect: Map<String, Boolean>,
    val judgeWinner: String?,
    val gtWinner: String,
    val agreementKey: Pair<String, Boolean>
)