package taxonomy.runner

import kotlinx.coroutines.runBlocking
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.boot.CommandLineRunner
import org.springframework.stereotype.Component
import org.springframework.core.annotation.Order
import taxonomy.config.TaxonomyConfig
import taxonomy.service.TaxonomyBenchmarkService
import taxonomy.service.TaxonomyService
import taxonomy.service.TaxonomySnapshotManager
import taxonomy.dataset.ModelEvalStore
import taxonomy.service.TaxonomyRankingService
import taxonomy.model.BenchmarkRequest
import taxonomy.model.ModelSource
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.ModelEvalLoader
import taxonomy.model.GraphNode
import taxonomy.TaxonomyEngine
import taxonomy.service.TaxonomyJudgeService
import taxonomy.model.ModelRank
import taxonomy.utils.ReportGenerator
import java.io.File
import java.time.Instant

@Serializable
data class HeadlessCliConfig(
    val snapshotId: String = "unsaved",
    val models: List<String>,              // e.g. ["gpt-4o-2024-08-06", "llama-3-8b-instruct"]
    val queryLimit: Int = 0,               // 0 = no limit
    val category: String? = null,          // optional GT category limit
    val confidenceGate: Double = 0.65,
    val parallelism: Int = 6,
    val questionsPerRound: Int = 12,
    val reservedOnly: Boolean = true,
    val conditions: List<String> = listOf("MAIN", "ORACLE", "GENERIC_JUDGE", "RANDOM_SCHEDULER"),
    val outputDir: String = "experiment",
    val testRatio: Double = 0.3,           // 70/30 split
    val seed: Long = 42L,                  // deterministic seed
    val regenerateSplit: Boolean = false,
    val runPipeline: Boolean = false,
    val maxDepth: Int? = null,
    val minClusterSize: Int? = null,
    val separationEpsilon: Double? = null,
    val cosineTau: Double? = null,
    val assignmentGap: Double? = null,
    val emaAlpha: Double? = null,
    val enableLabeling: Boolean? = null,
    val judgeInduction: Boolean = false,
    val datasetType: String? = null,
    val runBenchmark: Boolean = true,
    val runTrickle: Boolean = false,
    val domains: List<String> = emptyList()
)

@Component
@Order(2)
class HeadlessBenchmarkRunner(
    private val config: TaxonomyConfig,
    private val benchmarkService: TaxonomyBenchmarkService,
    private val snapshotManager: TaxonomySnapshotManager,
    private val taxonomyService: TaxonomyService,
    private val evalStore: ModelEvalStore,
    private val rankingService: TaxonomyRankingService,
    private val datasetFetcher: MMLUDatasetFetcher,
    private val evalLoader: ModelEvalLoader,
    private val taxonomyEngine: TaxonomyEngine,
    private val judgeService: TaxonomyJudgeService
) : CommandLineRunner {

    private val log = LoggerFactory.getLogger("taxonomy.HeadlessRunner")
    private val json = Json { prettyPrint = true; ignoreUnknownKeys = true }

    override fun run(vararg args: String?) {
        val configArg = args.indexOf("--config")
        if (configArg == -1) {
            // Only run if --config command line argument is passed
            return
        }

        val configPath = if (configArg + 1 < args.size) args[configArg + 1] else null
        if (configPath == null) {
            log.error("Missing path after --config parameter!")
            kotlin.system.exitProcess(1)
        }

        log.info("Starting Headless Benchmark Mode with config: $configPath")
        try {
            runHeadlessBenchmark(configPath)
            log.info("Headless Benchmark finished successfully.")
            kotlin.system.exitProcess(0)
        } catch (t: Throwable) {
            log.error("Headless Benchmark failed with error", t)
            kotlin.system.exitProcess(1)
        }
    }

    private fun runHeadlessBenchmark(configPath: String) = runBlocking {
        val configFile = File(configPath)
        if (!configFile.exists()) {
            throw IllegalArgumentException("Config file does not exist: ${configFile.absolutePath}")
        }

        val cliConfig = if (configPath.endsWith(".toml", ignoreCase = true)) {
            parseToml(configFile.readText())
        } else {
            json.decodeFromString<HeadlessCliConfig>(configFile.readText())
        }

        log.info("Loaded CLI Configuration: $cliConfig")

        // Apply any pipeline configuration overrides from TOML config
        cliConfig.maxDepth?.let { config.formalism.maxDepth = it }
        cliConfig.minClusterSize?.let { config.formalism.minClusterSize = it }
        cliConfig.separationEpsilon?.let { config.formalism.separationEpsilon = it }
        cliConfig.cosineTau?.let { config.formalism.cosineTau = it }
        cliConfig.assignmentGap?.let { config.formalism.assignmentGap = it }
        cliConfig.emaAlpha?.let { config.formalism.emaAlpha = it }
        cliConfig.enableLabeling?.let { config.execution.enableLabeling = it }
        cliConfig.datasetType?.let {
            config.dataset.datasetType = taxonomy.config.DatasetType.valueOf(it.uppercase())
        }

        val targetDomains = if (cliConfig.domains.isNotEmpty()) cliConfig.domains else (cliConfig.category?.let { listOf(it) } ?: emptyList())
        if (targetDomains.isNotEmpty()) {
            config.dataset.selectedDomains = targetDomains
        }

        var snapshotId = cliConfig.snapshotId
        var root: GraphNode

        if (cliConfig.runPipeline) {
            log.info("Headless pipeline execution enabled. Starting DAG generation pipeline...")
            if (!datasetFetcher.isDatasetDownloaded()) {
                log.info("Downloading dataset...")
                datasetFetcher.downloadDataset()
            }
            log.info("Loading dataset for domains: $targetDomains")
            val dataset = datasetFetcher.fetchDataset(
                selectedDomains = targetDomains
            )
            log.info("Splitting dataset into train/test (ratio=${cliConfig.testRatio}, seed=${cliConfig.seed})...")
            val (trainSet, testSet) = datasetFetcher.splitTrainTest(
                dataset,
                testRatio = cliConfig.testRatio,
                seed = cliConfig.seed
            )
            log.info("Syncing database reserved pool...")
            evalLoader.syncReservedPool()

            log.info("Running GMM splitting and trickle routing pipeline...")
            root = taxonomyEngine.adaptTaxonomy(
                rootLabel = config.dataset.datasetType.name,
                dataset = trainSet.mapValues { (_, qs) -> qs.map { it.text } }
            )

            if (cliConfig.judgeInduction) {
                log.info("Starting headless LLM judge prompt induction...")
                judgeService.generateJudgesForDag(root, replaceExisting = true)
            }

            log.info("Saving generated DAG snapshot to database...")
            val snapshotDesc = "Headless Run Auto-generated DAG"
            val snapshot = snapshotManager.saveSnapshot(root, snapshotDesc)
                ?: throw IllegalStateException("Failed to save snapshot for the newly generated DAG")
            snapshotId = snapshot.id
            log.info("Successfully generated and saved snapshot. Snapshot ID: $snapshotId")

            // Generate baseline snapshots via Python subprocess
            try {
                log.info("Generating baseline snapshots via Python subprocess...")
                val pb = ProcessBuilder("python", "scripts/generate_baselines.py")
                pb.directory(File("."))
                pb.redirectOutput(ProcessBuilder.Redirect.INHERIT)
                pb.redirectError(ProcessBuilder.Redirect.INHERIT)
                val process = pb.start()
                val exitCode = process.waitFor()
                if (exitCode == 0) {
                    log.info("Baseline snapshots successfully generated.")
                } else {
                    log.error("Baseline generation failed with exit code $exitCode")
                }
            } catch (e: Exception) {
                log.error("Failed to run baseline generator: ${e.message}", e)
            }
        } else {
            log.info("Loading pre-existing snapshot: $snapshotId")
            root = snapshotManager.loadSnapshot(snapshotId)
                ?: throw IllegalStateException("Could not load snapshot: $snapshotId")
        }

        // Apply fallback judge prompts to all nodes in the loaded/generated tree to prevent runtime IllegalStateException
        fun ensureJudgePrompts(n: GraphNode, condition: String) {
            val isMain = condition.equals("MAIN", ignoreCase = true)
            if (n.children.isEmpty()) { // leaf node
                if (isMain && cliConfig.runBenchmark && (n.judgePrompt.isNullOrBlank() || n.judgeRubric.isNullOrBlank())) {
                    throw IllegalStateException("Missing custom induced judge prompt/rubric for leaf node '${n.label}' (id=${n.id}) under MAIN condition!")
                }
            }
            if (n.judgePrompt.isNullOrBlank()) {
                n.judgePrompt = "You are a domain-expert judge evaluating answers in ${n.label}."
            }
            if (n.judgeRubric.isNullOrBlank()) {
                n.judgeRubric = "Evaluate correctness based on accuracy and reasoning clarity."
            }
            n.children.forEach { ensureJudgePrompts(it, condition) }
        }
        ensureJudgePrompts(root, "MAIN")

        taxonomyService.setGraph(root)
        log.info("Active graph node set: ${root.id}")

        // Deterministic train/test split if requested for pre-existing snapshot
        if (cliConfig.regenerateSplit && !cliConfig.runPipeline) {
            log.info("Regenerating deterministic 70/30 split (ratio=${cliConfig.testRatio}, seed=${cliConfig.seed})")
            if (!datasetFetcher.isDatasetDownloaded()) {
                log.info("Downloading dataset...")
                datasetFetcher.downloadDataset()
            }
            val dataset = datasetFetcher.fetchDataset(
                selectedDomains = targetDomains
            )
            datasetFetcher.splitTrainTest(dataset, testRatio = cliConfig.testRatio, seed = cliConfig.seed)
            log.info("Syncing database reserved pool...")
            evalLoader.syncReservedPool()
        }

        // 3. Create export directories
        val baseDir = File(cliConfig.outputDir)
        val validationDir = File(baseDir, "validation")
        val judgingDir = File(baseDir, "judging")
        validationDir.mkdirs()
        judgingDir.mkdirs()

        // 4. Run trickle validation if enabled
        if (cliConfig.runTrickle) {
            val baseSnapshotId = snapshotId.substringBefore("_MAIN").substringBefore("_ORACLE").substringBefore("_C3").substringBefore("_C5").substringBefore("_GENERIC_JUDGE").substringBefore("_RANDOM_SCHEDULER").substringBefore("_KMEANS_BASELINE").substringBefore("_WARD_BASELINE").substringBefore("_RANDOMNULL_BASELINE")

            log.info("========================================")
            log.info("RUNNING TRICKLE VALIDATION: MAIN")
            log.info("========================================")
            taxonomyService.setGraph(root)
            runHeadlessTrickle(root, "MAIN", cliConfig, baseDir)

            val kmeansSnapshot = "${baseSnapshotId}_baseline_kmeans"
            snapshotManager.loadSnapshot(kmeansSnapshot)?.let { kmeansRoot ->
                log.info("========================================")
                log.info("RUNNING TRICKLE VALIDATION: KMEANS_BASELINE")
                log.info("========================================")
                taxonomyService.setGraph(kmeansRoot)
                runHeadlessTrickle(kmeansRoot, "KMEANS_BASELINE", cliConfig, baseDir)
            }

            val wardSnapshot = "${baseSnapshotId}_baseline_ward"
            snapshotManager.loadSnapshot(wardSnapshot)?.let { wardRoot ->
                log.info("========================================")
                log.info("RUNNING TRICKLE VALIDATION: WARD_BASELINE")
                log.info("========================================")
                taxonomyService.setGraph(wardRoot)
                runHeadlessTrickle(wardRoot, "WARD_BASELINE", cliConfig, baseDir)
            }

            val randomNullSnapshot = "${baseSnapshotId}_baseline_randomnull"
            snapshotManager.loadSnapshot(randomNullSnapshot)?.let { randomNullRoot ->
                log.info("========================================")
                log.info("RUNNING TRICKLE VALIDATION: RANDOMNULL_BASELINE")
                log.info("========================================")
                taxonomyService.setGraph(randomNullRoot)
                runHeadlessTrickle(randomNullRoot, "RANDOMNULL_BASELINE", cliConfig, baseDir)
            }

            // Restore active root graph for downstream benchmark
            taxonomyService.setGraph(root)
        }

        // 5. Run each condition back-to-back if enabled
        if (cliConfig.runBenchmark) {
            val completedConditions = mutableListOf<String>()
            val logicalComparisonsMap = mutableMapOf<String, Int>()
            val judgeApiCallsMap = mutableMapOf<String, Int>()

            cliConfig.conditions.forEach { condition ->
                log.info("========================================")
                log.info("RUNNING CONDITION: $condition")
                log.info("========================================")

                val isKmeans = condition.equals("KMEANS_BASELINE", ignoreCase = true)
                val isWard = condition.equals("WARD_BASELINE", ignoreCase = true)
                val isRandomNull = condition.equals("RANDOMNULL_BASELINE", ignoreCase = true)

                val baseSnapshotId = snapshotId.substringBefore("_MAIN").substringBefore("_ORACLE").substringBefore("_C3").substringBefore("_C5").substringBefore("_GENERIC_JUDGE").substringBefore("_RANDOM_SCHEDULER").substringBefore("_KMEANS_BASELINE").substringBefore("_WARD_BASELINE").substringBefore("_RANDOMNULL_BASELINE")

                val activeRoot = when {
                    isKmeans -> {
                        log.info("Loading Flat k-means baseline snapshot...")
                        snapshotManager.loadSnapshot("${baseSnapshotId}_baseline_kmeans")
                            ?: throw IllegalStateException("Required KMEANS_BASELINE snapshot not found: ${baseSnapshotId}_baseline_kmeans")
                    }
                    isWard -> {
                        log.info("Loading HAC Ward baseline snapshot...")
                        snapshotManager.loadSnapshot("${baseSnapshotId}_baseline_ward")
                            ?: throw IllegalStateException("Required WARD_BASELINE snapshot not found: ${baseSnapshotId}_baseline_ward")
                    }
                    isRandomNull -> {
                        log.info("Loading Random null baseline snapshot...")
                        snapshotManager.loadSnapshot("${baseSnapshotId}_baseline_randomnull")
                            ?: throw IllegalStateException("Required RANDOMNULL_BASELINE snapshot not found: ${baseSnapshotId}_baseline_randomnull")
                    }
                    else -> root
                }

                val isBaseline = isKmeans || isWard || isRandomNull
                if (cliConfig.judgeInduction && isBaseline) {
                    log.info("Running judge prompt induction for baseline condition $condition to isolate topology effect...")
                    judgeService.generateJudgesForDag(activeRoot, replaceExisting = true)
                }

                ensureJudgePrompts(activeRoot, condition)
                taxonomyService.setGraph(activeRoot)

                // Suffix active snapshotId to isolate condition stats in SQLite
                val suffixedSnapshotId = "${snapshotId}_$condition"
                taxonomyService.setActiveSnapshotId(suffixedSnapshotId)
                
                // Clear existing snapshot data to ensure clean, reproducible experimental runs from scratch
                rankingService.clearRatings(suffixedSnapshotId)

                val modelSources = cliConfig.models.map { ModelSource(it) }
                val request = BenchmarkRequest(
                    models = modelSources,
                    queryLimit = cliConfig.queryLimit,
                    category = cliConfig.category,
                    confidenceGate = cliConfig.confidenceGate,
                    parallelism = cliConfig.parallelism,
                    questionsPerRound = cliConfig.questionsPerRound,
                    updateRankings = true,
                    reservedOnly = cliConfig.reservedOnly,
                    condition = condition,
                    seed = cliConfig.seed
                )

                val report = benchmarkService.runBenchmark(request)
                val logicalComparisons = report.queryResults.size
                val judgeApiCalls = report.queryResults.count { it.hadJudge } * 2
                logicalComparisonsMap[condition] = logicalComparisons
                judgeApiCallsMap[condition] = judgeApiCalls

                log.info("Condition $condition completed. Overall Agreement Rate: ${report.overallJudgeAccuracyAgreement}")
                log.info("  - Logical Comparisons: $logicalComparisons")
                log.info("  - LLM Judge API Calls: $judgeApiCalls")

                // Export results
                exportValidationMetrics(validationDir, condition, report)
                exportLeafLeaderboard(validationDir, condition, suffixedSnapshotId, activeRoot, cliConfig.models)
                exportDomainStats(validationDir, condition, report)
                exportVerdicts(judgingDir, condition, report)
                ReportGenerator.generateAndExport(validationDir, condition, report, activeRoot, cliConfig.models)

                // Compute and export LaTeX table for the global leaderboard
                val leafIds = mutableListOf<String>()
                val visited = mutableSetOf<String>()
                fun walk(n: GraphNode) {
                    if (!visited.add(n.id)) return
                    if (n.children.isEmpty()) leafIds.add(n.id)
                    else n.children.forEach { walk(it) }
                }
                walk(activeRoot)
                val globalLeaderboard = rankingService.aggregateLeafScores(leafIds, suffixedSnapshotId)
                exportLatexTable(validationDir, condition, globalLeaderboard.ranks)

                // Save backup of the full JSON benchmark report
                val backupDir = File("benchmark_backups")
                if (!backupDir.exists()) {
                    backupDir.mkdirs()
                }
                val timestamp = java.text.SimpleDateFormat("yyyyMMdd_HHmmss").format(java.util.Date())
                val backupFile = File(backupDir, "benchmark_${suffixedSnapshotId}_$timestamp.json")
                try {
                    val jsonString = json.encodeToString(report)
                    backupFile.writeText(jsonString)
                    log.info("Saved benchmark report backup to ${backupFile.absolutePath}")
                } catch (e: Exception) {
                    log.error("Failed to backup benchmark report: ${e.message}", e)
                }

                completedConditions.add(condition)
            }

            // 6. Write Experiment Manifest
            val manifestFile = File(baseDir, "manifest.json")
            val manifest = ExperimentManifest(
                runId = "run_" + Instant.now().toString().replace(":", "-"),
                snapshotId = snapshotId,
                models = cliConfig.models,
                seed = cliConfig.seed,
                testRatio = cliConfig.testRatio,
                conditionsRun = completedConditions,
                runTimestamp = Instant.now().toString(),
                logicalComparisons = logicalComparisonsMap,
                llmJudgeApiCalls = judgeApiCallsMap
            )
            manifestFile.writeText(json.encodeToString(manifest))
            log.info("Experiment manifest written to ${manifestFile.absolutePath}")
        }
    }

    private fun runHeadlessTrickle(root: GraphNode, condition: String, cliConfig: HeadlessCliConfig, baseDir: File) = runBlocking {
        log.info("Starting Headless Batch Trickle Validation for $condition...")

        val reservedFile = File("reserved_test_queries.json")
        if (!reservedFile.exists()) {
            log.warn("reserved_test_queries.json not found — cannot run trickle validation."); return@runBlocking
        }
        val reservedByDomain: Map<String, List<Int>> = try {
            json.decodeFromString(reservedFile.readText())
        } catch (t: Throwable) {
            log.error("Failed to parse reserved set for trickle validation", t); return@runBlocking
        }

        fun cleanText(s: String): String = s.replace("\r\n", "\n").replace("\r", "\n").trim()

        val leaves = taxonomy.tui.service.BatchTrickleEvaluator.collectLeaves(root)
        val textToDomain = HashMap<String, String>()

        // 1. First try to extract categories directly from GraphNode queries
        var embeddedCount = 0
        for (leaf in leaves) {
            for (emb in leaf.queries) {
                if (!emb.groundTruthCategory.isNullOrBlank()) {
                    textToDomain[emb.rawText] = emb.groundTruthCategory
                    textToDomain[cleanText(emb.rawText)] = emb.groundTruthCategory
                    embeddedCount++
                }
            }
        }
        log.info("Loaded $embeddedCount ground-truth categories directly from DAG queries.")

        // 2. Fetch train set to backfill or profile
        val targetDomains = if (cliConfig.domains.isNotEmpty()) cliConfig.domains else (cliConfig.category?.let { listOf(it) } ?: emptyList())
        val fullByDomain = datasetFetcher.fetchDataset(selectedDomains = targetDomains)
        val reservedIds: Set<Int> = reservedByDomain.values.flatten().toSet()
        var databaseCount = 0
        for ((domain, queries) in fullByDomain) {
            for (q in queries) if (q.id !in reservedIds) {
                if (!textToDomain.containsKey(q.text)) {
                    textToDomain[q.text] = domain
                    databaseCount++
                }
                val cleaned = cleanText(q.text)
                if (!textToDomain.containsKey(cleaned)) {
                    textToDomain[cleaned] = domain
                }
            }
        }
        log.info("Backfilled $databaseCount categories from local cache. Total mapping keys: ${textToDomain.size}")

        // Diagnostic logs
        if (textToDomain.isNotEmpty()) {
            log.info("Sample mapping keys: ${textToDomain.keys.take(3).map { it.take(50) }}")
        }
        val allLeafQueries = leaves.flatMap { it.queries }
        if (allLeafQueries.isNotEmpty()) {
            log.info("Sample leaf query rawTexts: ${allLeafQueries.take(3).map { it.rawText.take(50) }}")
            val matches = allLeafQueries.count { textToDomain.containsKey(it.rawText) || textToDomain.containsKey(cleanText(it.rawText)) }
            log.info("Diagnostic matching rate: $matches out of ${allLeafQueries.size} leaf queries match textToDomain keys.")
        }

        val profiles = taxonomy.tui.service.BatchTrickleEvaluator.buildLeafProfiles(leaves, textToDomain)
        log.info("Indexed leaves: ${profiles.size} / ${leaves.size} leaves tagged with a domain.")
        if (profiles.isEmpty()) {
            log.warn("No leaves could be tagged — DAG has no labeled training queries. Skipping trickle."); return@runBlocking
        }

        val idToText = fullByDomain.values.flatten().associate { it.id to it.text }
        val poolAll = reservedByDomain
            .flatMap { (domain, ids) ->
                ids.mapNotNull { id ->
                    idToText[id]?.let { text -> domain to text }
                }
            }
            .shuffled(java.util.Random(cliConfig.seed))
        
        val testQueries = poolAll
        if (testQueries.isEmpty()) {
            log.warn("Reserved test set is empty. Skipping trickle."); return@runBlocking
        }

        log.info("Routing ${testQueries.size} test queries...")
        val out = taxonomy.tui.service.BatchTrickleEvaluator.computeBatchTrickleMetrics(
            perLeafDomains = profiles,
            testQueries = testQueries,
            routeFn = { text ->
                try {
                    runBlocking {
                        taxonomyService.routeQueryToLeaves(text).map { it.first.id to it.second }
                    }
                } catch (t: Throwable) {
                    log.warn("Routing query failed: {}", t.message)
                    emptyList()
                }
            }
        )

        log.info("Batch Trickle Results ($condition):")
        log.info("  - Total Queries: ${out.totalQueries}")
        log.info("  - Top-1 Accuracy: ${"%,.2f%%".format(out.top1Accuracy * 100)}")
        log.info("  - Any-Match Accuracy: ${"%,.2f%%".format(out.anyMatchAccuracy * 100)}")
        log.info("  - Mean Leaf Purity: ${"%,.2f%%".format(out.meanLeafPurity * 100)}")
        log.info("  - Expected Calibration Error (ECE): ${"%,.4f".format(out.ece)}")
        log.info("  - Macro F1: ${"%,.2f%%".format(out.macroF1 * 100)}")

        val tableStr = StringBuilder().apply {
            appendLine("Per-Domain Trickle Results ($condition):")
            appendLine("----------------------------------------------------------------------")
            appendLine("%-25s | %7s | %9s | %8s | %8s".format("Domain", "Support", "Precision", "Recall", "F1"))
            appendLine("----------------------------------------------------------------------")
            out.perDomainF1.entries.sortedByDescending { it.value.support }.forEach { (domain, f1) ->
                appendLine("%-25s | %7d | %8.1f%% | %7.1f%% | %7.1f%%".format(
                    domain.take(25), f1.support, f1.precision * 100, f1.recall * 100, f1.f1 * 100
                ))
            }
            appendLine("======================================================================")
        }.toString()
        log.info("\n$tableStr")

        // Export results
        val trickleDir = File(baseDir, "validation")
        trickleDir.mkdirs()
        val file = File(trickleDir, "${condition}_trickle_validation_results.csv")
        file.bufferedWriter().use { writer ->
            writer.write("Metric,Value\n")
            writer.write("TotalQueries,${out.totalQueries}\n")
            writer.write("Top1Accuracy,${out.top1Accuracy}\n")
            writer.write("AnyMatchAccuracy,${out.anyMatchAccuracy}\n")
            writer.write("MeanLeafPurity,${out.meanLeafPurity}\n")
            writer.write("MeanRoutingDepth,${out.meanRoutingDepth}\n")
            writer.write("MacroF1,${out.macroF1}\n")
            writer.write("NoMatchRate,${out.noMatchRate}\n")
            writer.write("ECE,${out.ece}\n")
        }
        log.info("Trickle validation results written to ${file.absolutePath}")
    }

    private fun exportValidationMetrics(dir: File, condition: String, report: taxonomy.model.BenchmarkReport) {
        val file = File(dir, "${condition}_metrics.csv")
        file.bufferedWriter().use { writer ->
            writer.write("Condition,TotalQueries,TotalModelPairs,CoverageRate,OverallJudgeAccuracyAgreement\n")
            writer.write("${escapeCsv(condition)},${report.totalQueries},${report.totalModelPairs},${report.coverageRate},${report.overallJudgeAccuracyAgreement}\n")
        }
        log.info("Metrics CSV written to ${file.absolutePath}")
    }

    private fun exportLeafLeaderboard(dir: File, condition: String, snapshotId: String, root: GraphNode, models: List<String>) {
        val file = File(dir, "${condition}_leaf_leaderboard.csv")
        val btStates = rankingService.getAllBtStates(snapshotId)
        file.bufferedWriter().use { writer ->
            writer.write("Condition,LeafId,ModelId,BtScore,StdError,TotalComparisons\n")
            btStates.forEach { (leafId, state) ->
                models.forEach { model ->
                    val score = state.btScores[model] ?: 0.0
                    val err = state.stdErrors[model] ?: 10.0
                    writer.write("${escapeCsv(condition)},${escapeCsv(leafId)},${escapeCsv(model)},$score,$err,${state.totalComparisons}\n")
                }
            }
        }
        log.info("Leaderboard CSV written to ${file.absolutePath}")
    }

    private fun exportDomainStats(dir: File, condition: String, report: taxonomy.model.BenchmarkReport) {
        val file = File(dir, "${condition}_domain_stats.csv")
        file.bufferedWriter().use { writer ->
            writer.write("Condition,Domain,TotalQueries,AgreementRate,AvgConfidence,CoverageRate\n")
            report.perDomainStats.forEach { stat ->
                writer.write("${escapeCsv(condition)},${escapeCsv(stat.domain)},${stat.totalQueries},${stat.judgeAccuracyAgreementRate},${stat.avgConfidence},${stat.coverageRate}\n")
            }
        }
        log.info("Domain Stats CSV written to ${file.absolutePath}")
    }

    private fun exportVerdicts(dir: File, condition: String, report: taxonomy.model.BenchmarkReport) {
        val file = File(dir, "${condition}_verdicts.csv")
        file.bufferedWriter().use { writer ->
        writer.write("Condition,QueryId,QueryText,Category,ModelA,ModelB,AnswerA,AnswerB,CorrectA,CorrectB,GroundTruth,Winner,Confidence,PositionFlip,Rationale\n")
        report.queryResults.forEach { qr ->
            qr.pairEvaluations.forEach { (pairKey, evals) ->
                val models = pairKey.split("_vs_")
                val mA = models.getOrNull(0) ?: "Model A"
                val mB = models.getOrNull(1) ?: "Model B"
                val ansA = qr.modelAnswers[mA] ?: "?"
                val ansB = qr.modelAnswers[mB] ?: "?"
                val corrA = qr.modelCorrect[mA] ?: false
                val corrB = qr.modelCorrect[mB] ?: false

                evals.forEach { ev ->
                    writer.write(
                        "${escapeCsv(condition)}," +
                        "${qr.queryId}," +
                        "${escapeCsv(qr.query)}," +
                        "${escapeCsv(qr.gtCategory)}," +
                        "${escapeCsv(mA)}," +
                        "${escapeCsv(mB)}," +
                        "${escapeCsv(ansA)}," +
                        "${escapeCsv(ansB)}," +
                        "$corrA," +
                        "$corrB," +
                        "${escapeCsv(qr.gtCorrectAnswer)}," +
                        "${escapeCsv(ev.winner)}," +
                        "${ev.confidence}," +
                        "${ev.positionFlip}," +
                        "${escapeCsv(ev.rationale)}\n"
                    )
                }
            }
        }
        }
        log.info("Verdicts CSV written to ${file.absolutePath}")
    }

    private fun exportLatexTable(dir: File, condition: String, ranks: List<ModelRank>) {
        val file = File(dir, "${condition}_leaderboard.tex")
        file.bufferedWriter().use { writer ->
            writer.write("\\begin{table}[ht]\n")
            writer.write("\\centering\n")
            writer.write("\\caption{Global Bradley-Terry Leaderboard for Condition \\textsc{${condition.uppercase()}}}\n")
            writer.write("\\label{tab:leaderboard_${condition.lowercase()}}\n")
            writer.write("\\begin{tabular}{cccccc}\n")
            writer.write("\\hline\n")
            writer.write("\\textbf{Rank} & \\textbf{Model ID} & \\textbf{BT Score} & \\textbf{Std Error} & \\textbf{95\\% CI} & \\textbf{Total Matches} \\\\\n")
            writer.write("\\hline\n")
            ranks.forEach { r ->
                val ciLow = String.format(java.util.Locale.US, "%.4f", r.confidenceIntervalLow)
                val ciHigh = String.format(java.util.Locale.US, "%.4f", r.confidenceIntervalHigh)
                val scoreStr = String.format(java.util.Locale.US, "%+.4f", r.btScore)
                val seStr = String.format(java.util.Locale.US, "%.4f", r.stdError)
                writer.write("${r.rank} & ${r.modelId.replace("_", "\\_")} & $scoreStr & $seStr & $[$ciLow, $ciHigh]$ & ${r.comparisonsTotal} \\\\\n")
            }
            writer.write("\\hline\n")
            writer.write("\\end{tabular}\n")
            writer.write("\\end{table}\n")
        }
        log.info("LaTeX Leaderboard Table written to ${file.absolutePath}")
    }

    private fun escapeCsv(value: Any?): String {
        val s = value?.toString() ?: ""
        if (s.contains(",") || s.contains("\"") || s.contains("\n") || s.contains("\r")) {
            return "\"" + s.replace("\"", "\"\"") + "\""
        }
        return s
    }

    private fun parseToml(text: String): HeadlessCliConfig {
        var snapshotId = "unsaved"
        var models = listOf<String>()
        var queryLimit = 0
        var category: String? = null
        var confidenceGate = 0.65
        var parallelism = 6
        var questionsPerRound = 12
        var reservedOnly = true
        var conditions = listOf("MAIN", "ORACLE", "GENERIC_JUDGE", "RANDOM_SCHEDULER")
        var outputDir = "experiment"
        var testRatio = 0.3
        var seed = 42L
        var regenerateSplit = false
        var runPipeline = false
        var maxDepth: Int? = null
        var minClusterSize: Int? = null
        var separationEpsilon: Double? = null
        var cosineTau: Double? = null
        var assignmentGap: Double? = null
        var emaAlpha: Double? = null
        var enableLabeling: Boolean? = null
        var judgeInduction = false
        var datasetType: String? = null
        var runBenchmark = true
        var runTrickle = false
        var domains = listOf<String>()

        val lines = mutableListOf<String>()
        var inArray = false
        var arrayBuffer = StringBuilder()

        text.lines().forEach { rawLine ->
            val trimmed = rawLine.substringBefore("#").trim()
            if (trimmed.isEmpty()) return@forEach

            if (inArray) {
                arrayBuffer.append(" ").append(trimmed)
                if (trimmed.contains("]")) {
                    lines.add(arrayBuffer.toString())
                    inArray = false
                }
            } else {
                if (trimmed.contains("=") && trimmed.substringAfter("=").trim().startsWith("[") && !trimmed.contains("]")) {
                    inArray = true
                    arrayBuffer = StringBuilder(trimmed)
                } else {
                    lines.add(trimmed)
                }
            }
        }

        lines.forEach { line ->
            val key = line.substringBefore("=").trim()
            val rawVal = line.substringAfter("=").trim()

            fun parseStringList(s: String): List<String> {
                return s.trim('[', ']').split(",").map { it.trim(' ', '"', '\'') }.filter { it.isNotEmpty() }
            }

            when (key) {
                "snapshotId" -> snapshotId = rawVal.trim('"', '\'')
                "models" -> models = parseStringList(rawVal)
                "queryLimit" -> queryLimit = rawVal.toInt()
                "category" -> category = rawVal.trim('"', '\'').takeIf { it != "null" && it.isNotEmpty() }
                "confidenceGate" -> confidenceGate = rawVal.toDouble()
                "parallelism" -> parallelism = rawVal.toInt()
                "questionsPerRound" -> questionsPerRound = rawVal.toInt()
                "reservedOnly" -> reservedOnly = rawVal.toBoolean()
                "conditions" -> conditions = parseStringList(rawVal)
                "outputDir" -> outputDir = rawVal.trim('"', '\'')
                "testRatio" -> testRatio = rawVal.toDouble()
                "seed" -> seed = rawVal.toLong()
                "regenerateSplit" -> regenerateSplit = rawVal.toBoolean()
                "runPipeline" -> runPipeline = rawVal.toBoolean()
                "maxDepth" -> maxDepth = rawVal.toInt()
                "minClusterSize" -> minClusterSize = rawVal.toInt()
                "separationEpsilon" -> separationEpsilon = rawVal.toDouble()
                "cosineTau" -> cosineTau = rawVal.toDouble()
                "assignmentGap" -> assignmentGap = rawVal.toDouble()
                "emaAlpha" -> emaAlpha = rawVal.toDouble()
                "enableLabeling" -> enableLabeling = rawVal.toBoolean()
                "judgeInduction" -> judgeInduction = rawVal.toBoolean()
                "datasetType" -> datasetType = rawVal.trim('"', '\'')
                "runBenchmark" -> runBenchmark = rawVal.toBoolean()
                "runTrickle" -> runTrickle = rawVal.toBoolean()
                "domains" -> domains = parseStringList(rawVal)
            }
        }
        return HeadlessCliConfig(
            snapshotId = snapshotId,
            models = models,
            queryLimit = queryLimit,
            category = category,
            confidenceGate = confidenceGate,
            parallelism = parallelism,
            questionsPerRound = questionsPerRound,
            reservedOnly = reservedOnly,
            conditions = conditions,
            outputDir = outputDir,
            testRatio = testRatio,
            seed = seed,
            regenerateSplit = regenerateSplit,
            runPipeline = runPipeline,
            maxDepth = maxDepth,
            minClusterSize = minClusterSize,
            separationEpsilon = separationEpsilon,
            cosineTau = cosineTau,
            assignmentGap = assignmentGap,
            emaAlpha = emaAlpha,
            enableLabeling = enableLabeling,
            judgeInduction = judgeInduction,
            datasetType = datasetType,
            runBenchmark = runBenchmark,
            runTrickle = runTrickle,
            domains = domains
        )
    }
}

@Serializable
data class ExperimentManifest(
    val runId: String,
    val snapshotId: String,
    val models: List<String>,
    val seed: Long,
    val testRatio: Double,
    val conditionsRun: List<String>,
    val runTimestamp: String,
    val logicalComparisons: Map<String, Int> = emptyMap(),
    val llmJudgeApiCalls: Map<String, Int> = emptyMap()
)
