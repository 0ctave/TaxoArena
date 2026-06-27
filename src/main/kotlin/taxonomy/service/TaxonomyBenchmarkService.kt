package taxonomy.service

import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.ModelEvalStore
import taxonomy.dataset.ModelEvalResult
import taxonomy.model.BenchmarkReport
import taxonomy.model.BenchmarkRequest
import taxonomy.model.BenchmarkLiveStats
import taxonomy.model.DomainStats
import taxonomy.model.ModelPairStats
import taxonomy.model.QueryBenchmarkResult
import kotlin.collections.filter

@Service
class TaxonomyBenchmarkService(
    private val arenaService: TaxonomyArenaService,
    private val rankingService: TaxonomyRankingService,
    private val datasetFetcher: MMLUDatasetFetcher,
    private val taxonomyService: TaxonomyService,
    private val evalStore: ModelEvalStore
) {
    private val log = LoggerFactory.getLogger("BenchmarkService")

    suspend fun runBenchmark(
        req: BenchmarkRequest,
        onProgress: ((BenchmarkLiveStats) -> Unit)? = null
    ): BenchmarkReport = coroutineScope {
        require(req.models.size >= 2) { "Need at least 2 models" }
        val modelNames = req.models.map { it.modelName }

        // Query the database for the common intersection of MMLU-Pro questions for the selected models
        val matrix = evalStore.getResultsMatrix(
            models = modelNames,
            category = req.category,
            reservedOnly = req.reservedOnly, // defaults to the reserved pool only
            limit = req.queryLimit
        )

        log.info("Benchmark: ${matrix.size} questions, ${modelNames.size} models, " +
                "${modelNames.size * (modelNames.size - 1) / 2} pairs")

        if (matrix.isEmpty()) {
            return@coroutineScope emptyReport()
        }

        // Build all model pairs
        val pairs = modelNames.flatMapIndexed { i, a -> modelNames.drop(i + 1).map { b -> a to b } }

        // Process questions in parallel
        val semaphore = Semaphore(req.parallelism)
        val total = matrix.size
        val completedResults = java.util.Collections.synchronizedList(mutableListOf<QueryBenchmarkResult>())

        val queryResults = matrix.map { (qId, modelResults) ->
            async(Dispatchers.IO) {
                semaphore.withPermit {
                    val res = processPrecomputedQuery(qId, modelResults, pairs, req)
                    if (res != null) {
                        completedResults.add(res)
                        val currentProcessed = completedResults.size
                        if (onProgress != null) {
                            val allAgreements = completedResults.flatMap { it.judgeAccuracyAgreement.values }
                            val runningAgreement = if (allAgreements.isNotEmpty()) allAgreements.count { it }.toDouble() / allAgreements.size else 0.0
                            val runningCoverage = if (completedResults.isNotEmpty()) completedResults.count { it.hadJudge }.toDouble() / completedResults.size else 0.0
                            val perCategoryProgress = completedResults.groupBy { it.gtCategory }.mapValues { it.value.size }

                            val live = BenchmarkLiveStats(
                                processed = currentProcessed,
                                total = total,
                                currentQuestion = res.query,
                                runningAgreement = runningAgreement,
                                runningCoverage = runningCoverage,
                                perCategoryProgress = perCategoryProgress
                            )
                            onProgress.invoke(live)
                        }
                    }
                    res
                }
            }
        }.awaitAll().filterNotNull()

        aggregate(queryResults, pairs, req)
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

        // Model correctness straight from pre-extracted pred
        val modelAnswers = modelResults.mapValues { (_, r) -> r.pred ?: "?" }
        val modelCorrect = modelResults.mapValues { (_, r) -> r.isCorrect }

        // Run all pairs through judges in parallel
        val pairResults = pairs.map { (modelA, modelB) ->
            async {
                val outputA = modelResults[modelA] ?: return@async null
                val outputB = modelResults[modelB] ?: return@async null

                runCatching {
                    // Route the question to leaf judges (no model calls — just routing + judging)
                    val domainEvaluations = arenaService.evaluateWithPrecomputedTraces(
                        query = sample.questionText,
                        options = sample.options,
                        modelA = modelA,
                        traceA = outputA.modelOutput,
                        modelB = modelB,
                        traceB = outputB.modelOutput
                    )

                    val primaryEval = domainEvaluations
                        .filter { it.confidence >= req.confidenceGate }
                        .maxByOrNull { it.confidence }

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

                    if (req.updateRankings && primaryEval != null) {
                        val isTie = judgeWinner == "tie"
                        rankingService.recordMatch(
                            query = sample.questionText,
                            domain = primaryEval.domainLabel,
                            winner = if (isTie) modelA else judgeWinner!!,
                            loser = if (isTie) modelB else if (judgeWinner == modelA) modelB else modelA,
                            isTie = isTie,
                            confidence = primaryEval.confidence
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
                val primaryEval = qr.domainEvaluations
                    .filter { it.confidence >= req.confidenceGate }
                    .maxByOrNull { it.confidence }
                primaryEval?.let { eval ->
                    when (eval.winner) {
                        "Model A" -> judgeWinsA++
                        "Model B" -> judgeWinsB++
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
                avgConfidence = if (confCount > 0) totalConf / confCount else 0.0
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