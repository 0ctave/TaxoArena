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
    val pairStats: List<ModelPairStats> = emptyList()
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
    val updateRankings: Boolean = true,
    val reservedOnly: Boolean = true   // benchmark only the reserved test pool by default
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
    val judgeAccuracyAgreement: Map<String, Boolean>  // "A_vs_B" -> true/false
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
    val avgConfidence: Double
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
data class BenchmarkReport(
    val totalQueries: Int,
    val totalModelPairs: Int,
    val coverageRate: Double,           // fraction of queries with ≥1 leaf judge
    val overallJudgeAccuracyAgreement: Double,
    val perPairStats: List<ModelPairStats>,
    val perDomainStats: List<DomainStats>,
    val perCategoryStats: List<DomainStats>,  // grouped by MMLU-Pro GT category
    val queryResults: List<QueryBenchmarkResult>   // full per-query detail
)