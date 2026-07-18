package taxonomy.utils

import org.slf4j.LoggerFactory
import taxonomy.model.BenchmarkReport
import taxonomy.model.GraphNode
import taxonomy.service.ValidationService
import java.io.File
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

object ReportGenerator {
    private val log = LoggerFactory.getLogger(ReportGenerator::class.java)
    private val json = Json { prettyPrint = true; ignoreUnknownKeys = true }

    @Serializable
    data class CompleteThesisReport(
        val condition: String,
        val totalQueries: Int,
        val totalModelPairs: Int,
        val coverageRate: Double,
        val overallJudgeAccuracyAgreement: Double,
        // Structural metrics
        val totalNodes: Int,
        val leafNodes: Int,
        val maxDepth: Int,
        val avgLeafDepth: Double,
        val nmi: Double,
        val ari: Double,
        val dendrogramPurity: Double,
        val weightedLeafPurity: Double,
        val sphericalSilhouette: Double,
        val totalDasguptaCost: Double,
        val routingECE: Double,
        val normalisedSackin: Double,
        // Validation metrics
        val overallSpearmanRho: Double,
        val overallSpearmanCiLow: Double,
        val overallSpearmanCiHigh: Double,
        val overallKendallTau: Double,
        val overallKendallCiLow: Double,
        val overallKendallCiHigh: Double,
        val overallPairwiseWinnerAccuracy: Double,
        val overallTopKJaccard: Double,
        val domainReports: List<ValidationService.ValidationMetricsReport>
    )

    fun generateAndExport(
        dir: File,
        condition: String,
        report: BenchmarkReport,
        root: GraphNode,
        models: List<String>
    ) {
        dir.mkdirs()

        // 1. Build groundTruthMap from BenchmarkReport
        val groundTruthMap = report.queryResults.associate { it.query to listOf(it.gtCategory) }

        // 2. Compute Structural metrics
        val structReport = try {
            TaxonomyMetrics(root, groundTruthMap).generateReport()
        } catch (e: Exception) {
            log.error("Failed to generate TaxonomyMetrics report: ${e.message}", e)
            null
        }

        // 3. Compute Validation metrics (per domain and overall)
        val domains = report.queryResults.flatMap { it.matchedLeafLabels }.distinct()
        val domainReports = domains.map { domain ->
            ValidationService.computeMetrics(report, models, domain)
        }
        val globalReport = ValidationService.computeMetrics(report, models, "OVERALL")

        // 4. Construct Complete Report
        val completeReport = CompleteThesisReport(
            condition = condition,
            totalQueries = report.totalQueries,
            totalModelPairs = report.totalModelPairs,
            coverageRate = report.coverageRate,
            overallJudgeAccuracyAgreement = report.overallJudgeAccuracyAgreement,
            totalNodes = structReport?.totalNodes ?: 0,
            leafNodes = structReport?.leafNodes ?: 0,
            maxDepth = structReport?.maxDepth ?: 0,
            avgLeafDepth = structReport?.avgLeafDepth ?: 0.0,
            nmi = structReport?.nmi ?: 0.0,
            ari = structReport?.ari ?: 0.0,
            dendrogramPurity = structReport?.dendrogramPurity ?: 0.0,
            weightedLeafPurity = structReport?.weightedLeafPurity ?: 0.0,
            sphericalSilhouette = structReport?.sphericalSilhouette ?: 0.0,
            totalDasguptaCost = structReport?.totalDasguptaCost ?: 0.0,
            routingECE = structReport?.routingECE ?: 0.0,
            normalisedSackin = structReport?.normalisedSackin ?: 0.0,
            overallSpearmanRho = globalReport.spearmanRho,
            overallSpearmanCiLow = globalReport.spearmanCiLow,
            overallSpearmanCiHigh = globalReport.spearmanCiHigh,
            overallKendallTau = globalReport.kendallTau,
            overallKendallCiLow = globalReport.kendallCiLow,
            overallKendallCiHigh = globalReport.kendallCiHigh,
            overallPairwiseWinnerAccuracy = globalReport.pairwiseWinnerAccuracy,
            overallTopKJaccard = globalReport.topKJaccard,
            domainReports = domainReports
        )

        // 5. Export JSON
        val jsonFile = File(dir, "${condition}_thesis_metrics.json")
        try {
            jsonFile.writeText(json.encodeToString(completeReport))
            log.info("Successfully exported JSON report to ${jsonFile.absolutePath}")
        } catch (e: Exception) {
            log.error("Failed to write thesis metrics JSON: ${e.message}", e)
        }

        // 6. Export CSV
        val csvFile = File(dir, "${condition}_thesis_metrics.csv")
        try {
            csvFile.bufferedWriter().use { writer ->
                writer.write("Condition,MetricName,Value\n")
                
                // Write overall benchmark and structural stats
                writer.write("$condition,totalQueries,${completeReport.totalQueries}\n")
                writer.write("$condition,totalModelPairs,${completeReport.totalModelPairs}\n")
                writer.write("$condition,coverageRate,${completeReport.coverageRate}\n")
                writer.write("$condition,overallJudgeAccuracyAgreement,${completeReport.overallJudgeAccuracyAgreement}\n")
                writer.write("$condition,totalNodes,${completeReport.totalNodes}\n")
                writer.write("$condition,leafNodes,${completeReport.leafNodes}\n")
                writer.write("$condition,maxDepth,${completeReport.maxDepth}\n")
                writer.write("$condition,avgLeafDepth,${completeReport.avgLeafDepth}\n")
                writer.write("$condition,nmi,${completeReport.nmi}\n")
                writer.write("$condition,ari,${completeReport.ari}\n")
                writer.write("$condition,dendrogramPurity,${completeReport.dendrogramPurity}\n")
                writer.write("$condition,weightedLeafPurity,${completeReport.weightedLeafPurity}\n")
                writer.write("$condition,sphericalSilhouette,${completeReport.sphericalSilhouette}\n")
                writer.write("$condition,totalDasguptaCost,${completeReport.totalDasguptaCost}\n")
                writer.write("$condition,routingECE,${completeReport.routingECE}\n")
                writer.write("$condition,normalisedSackin,${completeReport.normalisedSackin}\n")
                
                // Write overall validation stats
                writer.write("$condition,overallSpearmanRho,${completeReport.overallSpearmanRho}\n")
                writer.write("$condition,overallSpearmanCiLow,${completeReport.overallSpearmanCiLow}\n")
                writer.write("$condition,overallSpearmanCiHigh,${completeReport.overallSpearmanCiHigh}\n")
                writer.write("$condition,overallKendallTau,${completeReport.overallKendallTau}\n")
                writer.write("$condition,overallKendallCiLow,${completeReport.overallKendallCiLow}\n")
                writer.write("$condition,overallKendallCiHigh,${completeReport.overallKendallCiHigh}\n")
                writer.write("$condition,overallPairwiseWinnerAccuracy,${completeReport.overallPairwiseWinnerAccuracy}\n")
                writer.write("$condition,overallTopKJaccard,${completeReport.overallTopKJaccard}\n")
            }
            log.info("Successfully exported CSV report to ${csvFile.absolutePath}")
        } catch (e: Exception) {
            log.error("Failed to write thesis metrics CSV: ${e.message}", e)
        }

        // 7. Export domain validation report in CSV
        val domainCsvFile = File(dir, "${condition}_domain_validation_details.csv")
        try {
            domainCsvFile.bufferedWriter().use { writer ->
                writer.write("Condition,Domain,SpearmanRho,SpearmanCiLow,SpearmanCiHigh,KendallTau,KendallCiLow,KendallCiHigh,PairwiseWinnerAccuracy,TopKJaccard\n")
                completeReport.domainReports.forEach { d ->
                    writer.write(
                        "$condition," +
                        "${escapeCsv(d.domain)}," +
                        "${d.spearmanRho}," +
                        "${d.spearmanCiLow}," +
                        "${d.spearmanCiHigh}," +
                        "${d.kendallTau}," +
                        "${d.kendallCiLow}," +
                        "${d.kendallCiHigh}," +
                        "${d.pairwiseWinnerAccuracy}," +
                        "${d.topKJaccard}\n"
                    )
                }
            }
            log.info("Successfully exported domain validation CSV to ${domainCsvFile.absolutePath}")
        } catch (e: Exception) {
            log.error("Failed to write domain validation CSV: ${e.message}", e)
        }
    }

    private fun escapeCsv(str: String): String {
        if (str.contains(",") || str.contains("\"") || str.contains("\n")) {
            return "\"" + str.replace("\"", "\"\"") + "\""
        }
        return str
    }
}
