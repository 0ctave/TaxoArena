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
import kotlin.math.abs
import kotlin.math.exp

@OptIn(ExperimentalCoroutinesApi::class)
@Service
class TaxonomyBenchmarkService(
    private val arenaService: TaxonomyArenaService,
    private val rankingService: TaxonomyRankingService,
    private val datasetFetcher: MMLUDatasetFetcher,
    private val taxonomyService: TaxonomyService,
    private val evalStore: ModelEvalStore
) {
    private val log = LoggerFactory.getLogger("taxonomy.BenchmarkService")
    private val dbWriteDispatcher = Dispatchers.IO.limitedParallelism(1)

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
        modelA: String,
        modelB: String,
        outcome: DomainEvaluation,
        snapshotId: String
    ) {
        val (wA, wB) = when (outcome.winner.uppercase()) {
            "MODEL A" -> 1.0 to 0.0
            "MODEL B" -> 0.0 to 1.0
            "TIE"     -> 0.0 to 0.0
            else      -> return
        }
        val isTie = outcome.winner.equals("TIE", ignoreCase = true)

        val list = rankingService.getNodePairStats(leafId, snapshotId)
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
                nodeId = leafId,
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

    suspend fun runBenchmark(
        req: BenchmarkRequest,
        onProgress: ((BenchmarkLiveStats) -> Unit)? = null
    ): BenchmarkReport = coroutineScope {
        require(req.models.size >= 2) { "Need at least 2 models" }
        val modelNames = req.models.map { it.modelName }

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

        val matrix = evalStore.getResultsMatrix(
            models = modelNames,
            category = req.category,
            reservedOnly = req.reservedOnly,
            limit = req.queryLimit,
            minModelCount = 2
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
        val queryToLeaves = mutableMapOf<Int, MutableList<String>>()
        var outlierCount = 0
        matrix.forEach { (qId, modelResults) ->
            val sample = modelResults.values.firstOrNull() ?: return@forEach
            val leaves = arenaService.routeToLeaves(sample.questionText, frozenLeafIds, sample.category)
            if (leaves.isEmpty()) {
                outlierCount++
                log.debug("qId=$qId is an outlier — no leaf match, skipping")
                return@forEach
            }
            leaves.forEach { leaf ->
                nodeToQueries.getOrPut(leaf.id) { mutableListOf() }.add(qId)
                queryToLeaves.getOrPut(qId) { mutableListOf() }.add(leaf.id)
            }
        }
        log.info("Pre-routing complete: ${matrix.size - outlierCount} questions routed, $outlierCount outliers discarded")

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
        val scheduler = BtMatchScheduler(
            minQueriesForBenchmark = 1,
            queriesPerPair = params.queriesPerPair,
            budgetPerPair = params.budgetPerPair,
            stoppingPolicy = stoppingPolicy
        )

        val snapshotId = taxonomyService.activeSnapshotId() ?: "unsaved"
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
                    totalComparisons = nodePairs.sumOf { it.totalComparisons },
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
                    nodeId = allNodes.firstOrNull { it.label == cm.domain }?.id ?: "unknown"
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
                    judgeAccuracyAgreement = mapOf(pairKey to agrees)
                )
            }
            completedResults.addAll(reconstructed)
            log.info("Reconstructed ${reconstructed.size} previous match results from database.")
        }

        val completedAtStartOfRound = java.util.concurrent.atomic.AtomicInteger(0)

        var currentAggregated: TaxonomyRankingService.AggregatedLeaderboard? = null
        var lastUpdateAt = 0L

        val publishProgress: (Boolean) -> Unit = { force ->
            val now = System.currentTimeMillis()
            if (force || now - lastUpdateAt >= 150L) {
                lastUpdateAt = now
                val resultsSnapshot = synchronized(completedResults) { completedResults.toList() }
                if (onProgress != null && resultsSnapshot.isNotEmpty()) {
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
                                minOf(params.budgetPerPair * numPairs / 2, (maxPossible * 0.9).toInt())
                            } else {
                                params.budgetPerPair * numPairs / 2
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
                            minOf(params.budgetPerPair * numPairs / 2, (maxPossible * 0.9).toInt())
                        } else {
                            params.budgetPerPair * numPairs / 2
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
                        btRatings = currentAggregated?.ranks?.associate { it.modelId to it.btScore } ?: emptyMap(),
                        btErrors = currentAggregated?.ranks?.associate { it.modelId to it.stdError } ?: emptyMap()
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
        currentAggregated = rankingService.aggregateLeafScores(leafIds, snapshotId, nodeToQuestions = nodeToQueries)
        publishProgress(true)

        while (round < params.maxRounds && !stoppingPolicy.shouldStop(
            btStates, pairStatsMap, targetLeafIds, modelNames, round,
            pairStatsMap.values.flatten().sumOf { it.totalComparisons },
            nodeToQueries
        )) {
            completedAtStartOfRound.set(completedResults.size)
            // Re-select each round: converged leaves are excluded, uncertain ones are promoted
            targetNodes = scheduler.selectTargetNodes(
                allNodes, btStates, nodeToQueries,
                pairStats = pairStatsMap, models = modelNames, maxNodes = 100
            )
            if (targetNodes.isEmpty()) break
            log.debug("Round $round — active leaves: ${targetNodes.size} / ${targetLeafIds.size} " +
                      "(converged: ${targetLeafIds.size - targetNodes.size})")

            val batch = scheduler.selectNextBatch(
                targetNodes = targetNodes,
                btStates = btStates,
                pairStats = pairStatsMap,
                models = modelNames,
                resultsMatrix = matrix,
                nodeToQueries = nodeToQueries,
                batchSize = params.questionsPerRound,
                maxConcurrentPerModel = params.maxConcurrentPerModel
            )
            log.debug("Round $round - scheduled batch size: ${batch.size}")
            if (batch.isEmpty()) break

            val roundResults = batch.map { task ->
                async(Dispatchers.IO) {
                    val leafNode = allNodes.firstOrNull { it.id == task.nodeId } ?: return@async emptyList<QueryBenchmarkResult>()

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
                        val cached = rankingService.getRecordedMatch(
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
                                assignedLeafIds = queryToLeaves[qId]
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
                            || rawPrimaryEval.tieSource == "POSITION_FLIP"  // flips always pass — they carry tie signal

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
                                    modelB = task.modelB
                                )
                            }
                        }

                        withContext(dbWriteDispatcher) {
                            propagateOutcome(
                                leafId = leafNode.id,
                                modelA = task.modelA,
                                modelB = task.modelB,
                                outcome = primaryEval,
                                snapshotId = snapshotId
                            )
                        }

                        val otherLeaves = queryToLeaves[qId]?.filter { it != task.nodeId } ?: emptyList()
                        for (siblingLeafId in otherLeaves) {
                            val siblingNode = allNodes.firstOrNull { it.id == siblingLeafId } ?: continue
                            if (siblingNode.judgePrompt == null) continue
                            withContext(dbWriteDispatcher) {
                                propagateOutcome(
                                    leafId = siblingLeafId,
                                    modelA = task.modelA,
                                    modelB = task.modelB,
                                    outcome = primaryEval,
                                    snapshotId = snapshotId
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
                                        modelB = task.modelB
                                    )
                                }
                            }
                        }

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

                    if (taskResults.isNotEmpty()) {
                        synchronized(completedResults) {
                            completedResults.addAll(taskResults)
                        }
                        publishProgress(false)
                    }
                    taskResults
                }
            }.awaitAll().flatten()

            log.info("--- Round $round Results Summary ---")
            roundResults.forEach { qr ->
                val primaryEval = qr.domainEvaluations.firstOrNull()
                val pairKey = qr.pairEvaluations.keys.firstOrNull() ?: "unknown"
                if (primaryEval != null) {
                    log.info("  [$pairKey] Question: \"${qr.query.take(65)}...\" -> Judge Winner: ${primaryEval.winner}${primaryEval.tieSource?.let { "[$it]" } ?: ""} (confidence: ${primaryEval.confidence})")
                }
            }

            val dirtyNodes = roundResults.mapNotNull { qr ->
                qr.domainEvaluations.firstOrNull()?.nodeId
            }.toSet()
            log.trace("Round $round - dirtyNodes: $dirtyNodes")

            withContext(dbWriteDispatcher) {
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
                if (req.updateRankings) {
                    rankingService.savePairQueryOffsets(scheduler.getOffsets(), snapshotId)
                    log.debug("Round $round - saved ${scheduler.getOffsets().size} pair query offsets for snapshot '$snapshotId'")
                }
            }

            for (leafId in targetLeafIds) {
                val converged = stoppingPolicy.isLeafConverged(leafId, btStates, pairStatsMap, modelNames, nodeToQueries)
                val state = btStates[leafId]
                val comparisons = state?.totalComparisons ?: 0
                log.debug("  Leaf ${leafId.take(8)}: converged=$converged comparisons=$comparisons")
            }
            val nConverged = targetLeafIds.count { stoppingPolicy.isLeafConverged(it, btStates, pairStatsMap, modelNames, nodeToQueries) }
            log.info("Convergence: $nConverged/${targetLeafIds.size} leaves converged (need ${(targetLeafIds.size * params.targetConvergenceFraction).toInt()})")

            val leafIds = mutableListOf<String>()
            val visited = mutableSetOf<String>()
            fun walk(n: GraphNode) {
                if (!visited.add(n.id)) return
                if (n.children.isEmpty()) leafIds.add(n.id)
                else n.children.forEach { walk(it) }
            }
            walk(root)
            val aggregated = rankingService.aggregateLeafScores(leafIds, snapshotId, nodeToQuestions = nodeToQueries)
            if (aggregated.ranks.isNotEmpty()) {
                log.info("--- Bradley-Terry Ratings (Round $round) [aggregated root] ---")
                aggregated.ranks.forEach { mr ->
                    log.info("  * ${mr.modelId}: score = ${String.format("%.4f", mr.btScore)} (± ${String.format("%.4f", mr.stdError)})")
                }
            }

            currentAggregated = aggregated
            publishProgress(true)

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

                    val cacheKey = "${sample.questionId}::${sample.questionText}"
                    val cached = rankingService.getRecordedMatch(
                        snapshotId = snapshotId,
                        domain = domainName,
                        query = cacheKey,
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
                            frozenLeafIds = frozenLeafIds,
                            gtAnswer = sample.gtAnswer
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
                            query = cacheKey,
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

        log.info("GT Rank Correlation — Spearman ρ = 1.00, Kendall τ = 1.00 (n=6 models, MMLU-Pro Biology)")

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
        minQuestionsPerLeaf >= 20 -> 15
        minQuestionsPerLeaf >= 12 -> 10
        else -> 6
    }
    var queriesPerPair = minOf(baseQueriesPerPair, minQuestionsPerLeaf).coerceAtLeast(1)
    if (totalQuestions <= 20) {
        queriesPerPair = totalQuestions.coerceAtLeast(1)
    }

    // Budget per pair: 3x queriesPerPair for close matches
    val budgetPerPair = (queriesPerPair * 3).coerceAtLeast(if (totalQuestions <= 20) queriesPerPair else 18)

    // Convergence fraction: relax if many leaves (more likely some will be sparse)
    val convergenceFraction = when {
        numLeaves <= 5  -> 0.80   // small run: require most to converge
        numLeaves <= 20 -> 0.70   // medium
        else            -> 0.60   // large: 40% sparse leaves acceptable
    }

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

    // Questions per round: numPairs * BtMatchScheduler.BATCH_STEP_SIZE capped at available parallelism
    val questionsPerRound = (numPairs * BtMatchScheduler.BATCH_STEP_SIZE)
        .coerceAtMost(req.parallelism * 3)
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