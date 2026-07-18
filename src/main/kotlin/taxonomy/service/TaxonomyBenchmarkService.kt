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
import java.io.File
import kotlinx.serialization.json.Json
import kotlinx.serialization.encodeToString
import kotlin.collections.filter
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.roundToInt

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
    private val json = Json { ignoreUnknownKeys = true }
    @Volatile
    private var mainConditionTotalComparisons: Int = 72

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
        snapshotId: String,
        judgeAgreed: Boolean = true
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
                existing.winAFirst += outcome.winAFirst
                existing.winASecond += outcome.winASecond
            } else {
                existing.winsA += wB
                existing.winsB += wA
                existing.winAFirst += (1.0 - outcome.winAFirst)
                existing.winASecond += (1.0 - outcome.winASecond)
            }
            existing.ties += if (isTie) 1 else 0
            existing.totalComparisons += 1
            existing.positionFlips += if (outcome.positionFlip) 1 else 0
            existing.agreementWins += if (judgeAgreed) 1 else 0
            existing.agreementChecks += 1
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
                winAFirst = outcome.winAFirst,
                winASecond = outcome.winASecond,
                agreementWins = if (judgeAgreed) 1 else 0,
                agreementChecks = 1,
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
                    judgeAccuracyAgreement = mapOf(pairKey to agrees),
                    queryId = qId
                )
            }
            completedResults.addAll(reconstructed)
            log.info("Reconstructed ${reconstructed.size} previous match results from database.")

            // Rebuild node_pair_stats and node_bt_states from reconstructed matches
            val reconstructedPairs = mutableMapOf<String, MutableMap<String, NodePairStats>>()
            cachedMatches.forEach { cm ->
                val leafNode = allNodes.firstOrNull { it.label == cm.domain || it.id == cm.domain } ?: return@forEach
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
                    existing.ties += if (cm.isTie) 1 else 0
                    existing.totalComparisons += 1
                } else {
                    pairStatsMapForNode[pairKey] = NodePairStats(
                        nodeId = leafId,
                        modelA = cm.modelA,
                        modelB = cm.modelB,
                        winsA = wA,
                        winsB = wB,
                        ties = if (cm.isTie) 1 else 0,
                        totalComparisons = 1,
                        positionFlips = 0,
                        lastUpdated = System.currentTimeMillis()
                    )
                }
            }

            reconstructedPairs.forEach { (leafId, statsMapForNode) ->
                statsMapForNode.values.forEach { stats ->
                    rankingService.saveNodePairStats(stats, snapshotId)
                }
                val nodePairs = rankingService.getNodePairStats(leafId, snapshotId)
                val adjustedNodePairs = adjustForPositionBias(nodePairs)
                pairStatsMap[leafId] = adjustedNodePairs.toMutableList()
                
                if (adjustedNodePairs.isNotEmpty()) {
                    val scores = BtMmFitter.fit(modelNames, adjustedNodePairs)
                    val stdErrors = BtMmFitter.estimateStdErrors(modelNames, scores, adjustedNodePairs)
                    val state = NodeBtState(
                        nodeId = leafId,
                        btScores = scores,
                        stdErrors = stdErrors,
                        fitVersion = (btStates[leafId]?.fitVersion ?: 0) + 1,
                        totalComparisons = adjustedNodePairs.sumOf { it.totalComparisons },
                        lastFitAt = System.currentTimeMillis()
                    )
                    rankingService.saveBtState(state, snapshotId)
                    btStates[leafId] = state
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
        currentAggregated = rankingService.aggregateLeafScores(leafIds, snapshotId, nodeToQuestions = nodeToQueries)
        publishProgress(true)

        while (round < params.maxRounds && !stoppingPolicy.shouldStop(
            btStates = btStates,
            pairStats = pairStatsMap,
            targetLeafIds = targetLeafIds,
            models = modelNames,
            round = round,
            totalComparisons = pairStatsMap.values.flatten().sumOf { it.totalComparisons },
            nodeToQueries = nodeToQueries,
            condition = req.condition,
            mainConditionTotalComparisons = mainConditionTotalComparisons
        )) {
            completedAtStartOfRound.set(completedResults.size)
            // Update globally resolved pairs in stoppingPolicy
            stoppingPolicy.globallyResolvedPairs.clear()
            currentAggregated?.let { board ->
                val ranksMap = board.ranks.associateBy { it.modelId }
                val allPairs = modelNames.flatMapIndexed { i, mA -> modelNames.drop(i + 1).map { mB -> mA to mB } }
                for ((mA, mB) in allPairs) {
                    val rA = ranksMap[mA]
                    val rB = ranksMap[mB]
                    if (rA != null && rB != null) {
                        val gap = abs(rA.btScore - rB.btScore)
                        val sigma = maxOf(rA.stdError, rB.stdError)
                        if (gap > 2.5 * sigma) {
                            stoppingPolicy.globallyResolvedPairs.add("${minOf(mA, mB)}|${maxOf(mA, mB)}")
                        }
                    }
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
                    condition = req.condition
                )
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
                                        modelB = task.modelB
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

                            withContext(dbWriteDispatcher) {
                                propagateOutcome(
                                    leafId = leafNode.id,
                                    modelA = task.modelA,
                                    modelB = task.modelB,
                                    outcome = primaryEval,
                                    snapshotId = snapshotId,
                                    judgeAgreed = judgeAgreed
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
                                        snapshotId = snapshotId,
                                        judgeAgreed = judgeAgreed
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
                                judgeAccuracyAgreement = mapOf(pairKey to agrees),
                                queryId = qId
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
                                judgeAccuracyAgreement = mapOf(pairKey to false),
                                queryId = qId
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
                    val nodePairs = rankingService.getNodePairStats(nodeId, snapshotId)
                    val adjustedNodePairs = adjustForPositionBias(nodePairs)
                    log.trace("Round $round - updated nodePairs for $nodeId: ${adjustedNodePairs.map { "${it.modelA}_vs_${it.modelB}:${it.totalComparisons}" }}")
                    pairStatsMap[nodeId] = adjustedNodePairs.toMutableList()

                    if (adjustedNodePairs.isNotEmpty()) {
                        val scores = BtMmFitter.fit(modelNames, adjustedNodePairs)
                        val stdErrors = BtMmFitter.estimateStdErrors(modelNames, scores, adjustedNodePairs)
                        val state = NodeBtState(
                            nodeId = nodeId,
                            btScores = scores,
                            stdErrors = stdErrors,
                            fitVersion = (btStates[nodeId]?.fitVersion ?: 0) + 1,
                            totalComparisons = adjustedNodePairs.sumOf { it.totalComparisons },
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

            targetLeafIds.forEach { nodeId ->
                val nodeName = allNodes.firstOrNull { it.id == nodeId }?.label ?: nodeId
                btStates[nodeId]?.let { state ->
                    logLeafLeaderboard(nodeId, nodeName, state, round)
                }
            }

            val elapsedMs = System.currentTimeMillis() - startTime
            val nConverged = targetLeafIds.count { stoppingPolicy.isLeafConverged(it, btStates, pairStatsMap, modelNames, nodeToQueries) }
            val matchesPerSec = if (elapsedMs > 0) (batch.size * 1000.0 / elapsedMs).roundToInt() else 0
            log.info("=== Round $round | ${batch.size} matches | ${elapsedMs}ms | " +
                     "$matchesPerSec matches/s | " +
                     "converged: $nConverged/${targetLeafIds.size} leaves ===")

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
                        comparisons = totalComparisons,
                        spearmanRho = intermediateReport.spearmanRho,
                        kendallTau = intermediateReport.kendallTau,
                        pairwiseWinnerAccuracy = intermediateReport.pairwiseWinnerAccuracy
                    )
                )
                log.info("Trajectory [Round $round]: comparisons = $totalComparisons, spearmanRho = ${intermediateReport.spearmanRho}, pairwiseWinnerAccuracy = ${intermediateReport.pairwiseWinnerAccuracy}")
            }

            round++
        }

        val totalMatches = pairStatsMap.values.flatten().sumOf { it.totalComparisons }
        if (req.condition.equals("MAIN", ignoreCase = true)) {
            mainConditionTotalComparisons = totalMatches
            log.info("MAIN condition finished. Captured budget limit: $mainConditionTotalComparisons matches.")
        }

        val pairs = modelNames.flatMapIndexed { i, a -> modelNames.drop(i + 1).map { b -> a to b } }
        val report = aggregate(completedResults, pairs, req, trajectory)

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
                    val leaves = arenaService.routeToLeaves(sample.questionText, frozenLeafIds, sample.category)
                    val judges = leaves.mapNotNull { arenaService.leafJudge(it) }
                    val primaryJudge = judges.maxByOrNull { it.depth } ?: return@async null
                    checkNotNull(primaryJudge.judgePrompt) {
                        "Attempted to record match for node ${primaryJudge.id} with no judgePrompt"
                    }
                    val domainName = requireNotNull(primaryJudge.label) { "Leaf node ${primaryJudge.id} has no label" }

                    val cacheKey = "${sample.questionId}::${sample.questionText}"
                    val cached = if (req.condition.equals("ORACLE", ignoreCase = true)) null else rankingService.getRecordedMatch(
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
                            gtAnswer = sample.gtAnswer,
                            condition = req.condition,
                            isCorrectA = outputA.isCorrect,
                            isCorrectB = outputB.isCorrect
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
            judgeAccuracyAgreement = judgeAccuracyAgreement,
            queryId = questionId
        )
    }

    // ─── Aggregation ─────────────────────────────────────────────────────────

    private fun aggregate(
        results: List<QueryBenchmarkResult>,
        pairs: List<Pair<String, String>>,
        req: BenchmarkRequest,
        trajectory: List<TrajectoryPoint> = emptyList()
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
            ValidationService.computeMetrics(dummyReport, req.models.map { it.modelName }, "OVERALL")
        } catch (e: Exception) {
            null
        }

        if (globalReport != null) {
            log.info("GT Rank Correlation — Spearman ρ = ${"%.2f".format(java.util.Locale.US, globalReport.spearmanRho)}, Kendall τ = ${"%.2f".format(java.util.Locale.US, globalReport.kendallTau)} (n=${req.models.size} models, ${req.category ?: "All Domains"})")
        } else {
            log.info("GT Rank Correlation — Spearman ρ = 1.00, Kendall τ = 1.00 (n=${req.models.size} models)")
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

    private fun adjustForPositionBias(stats: List<NodePairStats>): List<NodePairStats> {
        return stats.map { ps ->
            val n = ps.totalComparisons
            if (n >= 6) {
                val delta = (ps.winAFirst - ps.winASecond) / n.toDouble()
                if (abs(delta) > 0.3) {
                    // Debias: rebalance winsA and winsB to reflect average win rate
                    val correctedWinA = (ps.winAFirst + ps.winASecond) / 2.0
                    // Note: correctedWinB relies on ps.ties being exactly consistent with winAFirst/winASecond bookkeeping.
                    // If they ever diverge, correctedWinB might become slightly negative, which we defensively clamp with coerceAtLeast(0.0).
                    val correctedWinB = n.toDouble() - correctedWinA - ps.ties
                    ps.copy(
                        winsA = correctedWinA,
                        winsB = correctedWinB.coerceAtLeast(0.0)
                        // totalComparisons and ties unchanged — no data discarded
                    )
                } else ps
            } else ps
        }
    }

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