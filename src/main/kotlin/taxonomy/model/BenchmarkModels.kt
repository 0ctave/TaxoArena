package taxonomy.model

import kotlinx.serialization.Serializable
import taxonomy.service.DomainEvaluation

@Serializable
data class BenchmarkLiveStats(
    val processed: Int,
    val total: Int,
    val currentQuestion: String,
    val runningAgreement: Double,   // rolling judge-GT agreement
    val runningCoverage: Double,    // fraction with ≥1 leaf judge so far
    val perCategoryProgress: Map<String, Int>,  // category → matched so far
    val pairStats: List<ModelPairStats> = emptyList(),
    val currentRound: Int = 0,
    val activeTargets: List<String> = emptyList(),
    val btRatings: Map<String, Double> = emptyMap(),
    val btErrors: Map<String, Double> = emptyMap()
)

@Serializable
data class ModelSource(
    val modelName: String,      // ...path to extracted directory
)

@Serializable
data class BenchmarkRequest(
    val models: List<ModelSource>,  // ≥ 2 models with their output files
    val queryLimit: Int = 0,        // 0 = all available questions
    val category: String? = null,   // optional: restrict to one GT category
    val confidenceGate: Double = 0.65,
    val parallelism: Int = 6,
    val questionsPerRound: Int = 12, // total queries per round (= numPairs * BATCH_STEP_SIZE)
    val updateRankings: Boolean = true,
    // The reserved pool to judge, by content id (ReservedPool.computePoolId); the matrix is the
    // semijoin of eval_results with that pool. null = unrestricted arena, kept loud by the
    // service ([ARENA-POOL] WARN) and never used for a run of record. FRAMEWORK item 18.
    val poolId: String? = null,
    val condition: String = "MAIN",
    val seed: Long = 42L,
    // PROFILE mode (both must be supplied): stop on SE targets per model x stratum
    // instead of on rank decisions. See taxonomy.arena.ProfileTargets.
    val profileSeTarget: Double? = null,
    val profileStrata: Map<String, String> = emptyMap(),   // leafId -> stratumId
    // Soft cap on per-question reuse within a leaf across all pairs; Int.MAX_VALUE
    // keeps historical behaviour. See ActiveBtRacingScheduler.maxQueryReuse.
    val maxQueryReuse: Int = Int.MAX_VALUE,
    // Optional reference-free restriction on which QUESTION a (cell, pair) match is played
    // on. "none" (the default) is byte-identical to the historical scheduler; see
    // taxonomy.arena.MatchFilter. Carried as the TOML string so BenchmarkRequest stays free
    // of an arena-package dependency.
    val matchFilter: String = "none"
)

@Serializable
data class QueryBenchmarkResult(
    val query: String,
    val gtCategory: String,
    val gtCorrectAnswer: String,        // e.g. "A"
    val modelAnswers: Map<String, String>,   // modelId -> extracted answer letter
    val modelCorrect: Map<String, Boolean>,  // modelId -> whether answer == GT
    val matchedLeafLabels: List<String>,     // leaves the query routed to (for coverage)
    val hadJudge: Boolean,
    val domainEvaluations: List<DomainEvaluation>,
    val pairEvaluations: Map<String, List<DomainEvaluation>> = emptyMap(),
    // per-model-pair: judgeWinner agrees with accuracy-based winner?
    val judgeAccuracyAgreement: Map<String, Boolean>,  // "A_vs_B" -> true/false
    val queryId: Int = 0,
    val secondaryMemberships: Map<String, Double> = emptyMap()
)

@Serializable
data class ModelPairStats(
    val modelA: String,
    val modelB: String,
    val totalMatches: Int,
    val judgeWinsA: Int,
    val judgeWinsB: Int,
    val judgeTies: Int,
    val accuracyWinsA: Int,             // GT-based: A correct, B wrong
    val accuracyWinsB: Int,
    val accuracyTies: Int,
    val judgeAccuracyAgreementRate: Double,   // core validation metric
    val avgConfidence: Double,
    val isExhausted: Boolean = false
)

@Serializable
data class DomainStats(
    val domain: String,
    val totalQueries: Int,
    val judgeAccuracyAgreementRate: Double,
    val avgConfidence: Double,
    val coverageRate: Double            // fraction of queries that got a leaf judge
)

@Serializable
data class TrajectoryPoint(
    val round: Int,
    val comparisons: Int,
    val spearmanRho: Double,
    val kendallTau: Double,
    val pairwiseWinnerAccuracy: Double
)

/**
 * What the optional match filter did over a whole run. See taxonomy.arena.MatchFilter.
 *
 * Defaulted throughout so an older serialized report still parses, and so a run with the filter
 * off carries the "none" row rather than a null the exporter has to special-case.
 */
@Serializable
data class MatchFilterSummary(
    val filter: String = "none",
    /** (cell, pair) slot evaluations the filter was consulted on. */
    val slotEvaluations: Long = 0L,
    /** Candidate questions offered to the filter, summed over slot evaluations. */
    val candidateQuestionsBefore: Long = 0L,
    /** Candidate questions surviving it, summed the same way (equal to `before` when off). */
    val candidateQuestionsAfter: Long = 0L,
    /** Distinct (cell, pair) slots that had to fall back to the unfiltered candidate set. */
    val fallbackSlots: Int = 0,
    /** Matches the scheduler actually emitted over the run. */
    val matchesScheduled: Long = 0L,
    val questionPairsSeen: Long = 0L,
    /** Of those, how many had a missing/blank prediction on either side and were kept. */
    val questionPairsUndetermined: Long = 0L,
    /** True when the filter was on but no question anywhere had both answers extracted. */
    val inert: Boolean = false
)

@Serializable
data class BenchmarkReport(
    val totalQueries: Int,
    val totalModelPairs: Int,
    val coverageRate: Double,           // fraction of queries with ≥1 leaf judge
    val overallJudgeAccuracyAgreement: Double,
    val perPairStats: List<ModelPairStats>,
    val perDomainStats: List<DomainStats>,
    val perCategoryStats: List<DomainStats>,  // grouped by MMLU-Pro GT category
    val queryResults: List<QueryBenchmarkResult>,   // full per-query detail
    val trajectory: List<TrajectoryPoint> = emptyList(),
    val matchFilter: MatchFilterSummary = MatchFilterSummary()
)

@Serializable
data class NodePairStats(
    val nodeId: String,
    val modelA: String,
    val modelB: String,
    var winsA: Double = 0.0,      // Double to support 0.5 for BT ties
    var winsB: Double = 0.0,
    var ties: Double = 0.0,             // raw tie count (position flips)
    var totalComparisons: Double = 0.0,
    var positionFlips: Int = 0,
    var lastUpdated: Long = 0L,
    var winAFirst: Double = 0.0,
    var winASecond: Double = 0.0,
    var agreementWins: Int = 0,
    var agreementChecks: Int = 0
) {
    constructor(
        nodeId: String,
        modelA: String,
        modelB: String,
        winsA: Double = 0.0,
        winsB: Double = 0.0,
        ties: Int = 0,
        totalComparisons: Int = 0,
        positionFlips: Int = 0,
        lastUpdated: Long = 0L,
        winAFirst: Double = 0.0,
        winASecond: Double = 0.0,
        agreementWins: Int = 0,
        agreementChecks: Int = 0
    ) : this(
        nodeId, modelA, modelB, winsA, winsB,
        ties.toDouble(), totalComparisons.toDouble(),
        positionFlips, lastUpdated, winAFirst, winASecond,
        agreementWins, agreementChecks
    )
}

@Serializable
data class NodeBtState(
    val nodeId: String,
    val btScores: Map<String, Double>,        // modelId -> strength
    val stdErrors: Map<String, Double>,       // modelId -> std error
    val fitVersion: Int,
    val totalComparisons: Int,
    val lastFitAt: Long
)

@Serializable
data class BtMatchTask(
    val nodeId: String,
    val modelA: String,
    val modelB: String,
    val queryIds: List<String>,               // reserved queries routed to this node
    val priority: Double,                     // computed utility score
    val batchId: String
)

@Serializable
data class ModelRank(
    val modelId: String,
    val btScore: Double,
    val stdError: Double,
    val rank: Int,
    val confidenceIntervalLow: Double,   // btScore - 2*stdError
    val confidenceIntervalHigh: Double,  // btScore + 2*stdError
    val winsTotal: Double,
    val comparisonsTotal: Int
)

@Serializable
data class FrozenMatchTriple(
    val questionId: Int,
    val modelA: String,
    val modelB: String,
    val nodeId: String
)
