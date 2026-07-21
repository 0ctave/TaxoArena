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
import taxonomy.service.TaxonomyArenaService
import taxonomy.dataset.ModelEvalStore
import taxonomy.service.TaxonomyRankingService
import taxonomy.service.ValidationService
import taxonomy.model.BenchmarkRequest
import taxonomy.model.ModelSource
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.ModelEvalLoader
import taxonomy.model.GraphNode
import taxonomy.TaxonomyEngine
import taxonomy.service.TaxonomyJudgeService
import taxonomy.model.ModelRank
import taxonomy.model.Embedding
import taxonomy.utils.ReportGenerator
import taxonomy.dataset.EmbeddingCache
import java.io.File
import java.time.Instant
import taxonomy.model.projectTo
import taxonomy.utils.StatisticsUtils
import taxonomy.tui.service.LeafDomainProfile
import taxonomy.model.BenchmarkReport
import kotlin.math.sqrt

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
    val seeds: List<Long> = emptyList(),   // multi-seed support
    val regenerateSplit: Boolean = false,
    val runPipeline: Boolean = false,
    val maxDepth: Int? = null,
    val minClusterSize: Int? = null,
    val separationEpsilon: Double? = null,
    val routingSoftmaxTau: Double? = null,
    val assignmentCosineGap: Double? = null,
    val defaultKappaPrior: Double? = null,
    val emaAlpha: Double? = null,
    val enableLabeling: Boolean? = null,
    val judgeInduction: Boolean = false,
    val datasetType: String? = null,
    val runBenchmark: Boolean = true,
    val runTrickle: Boolean = false,
    val domains: List<String> = emptyList(),
    val enableStableQuestionIds: Boolean? = null,
    val enableResidualRouting: Boolean? = null,
    val enableResidualSplitGate: Boolean? = null,
    val enableBridging: Boolean? = null,
    val fusionSimilarityThreshold: Double? = null,
    val effectiveSupportFloor: Double? = null,
    val numIterations: Int? = null,
    val runBaselines: Boolean = true,
    val secondaryMassFloor: Double? = null,
    val bridgeSupportFloor: Double? = null,
    val bridgeSupportRelFraction: Double? = null,
    val deltaAssign: Double? = null,
    val maxLeafAssignments: Int? = null,
    val refitMuPerIteration: Boolean? = null,
    val tauKappaScalingFactor: Double? = null,
    val dagMode: String? = null
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
    private val judgeService: TaxonomyJudgeService,
    private val embeddingCache: EmbeddingCache,
    private val arenaService: TaxonomyArenaService
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
        cliConfig.routingSoftmaxTau?.let { config.formalism.routingSoftmaxTau = it }
        cliConfig.assignmentCosineGap?.let { config.formalism.assignmentCosineGap = it }
        cliConfig.defaultKappaPrior?.let { config.formalism.defaultKappaPrior = it }
        cliConfig.emaAlpha?.let { config.formalism.emaAlpha = it }
        cliConfig.enableLabeling?.let { config.execution.enableLabeling = it }
        cliConfig.datasetType?.let {
            config.dataset.datasetType = taxonomy.config.DatasetType.valueOf(it.uppercase())
        }

        cliConfig.enableStableQuestionIds?.let { config.formalism.enableStableQuestionIds = it }
        cliConfig.enableResidualRouting?.let { config.formalism.enableResidualRouting = it }
        cliConfig.enableResidualSplitGate?.let { config.formalism.enableResidualSplitGate = it }
        cliConfig.enableBridging?.let { config.formalism.enableBridging = it }
        cliConfig.fusionSimilarityThreshold?.let { config.formalism.fusionSimilarityThreshold = it }
        cliConfig.effectiveSupportFloor?.let { config.formalism.effectiveSupportFloor = it }
        cliConfig.secondaryMassFloor?.let { config.diagnostics.secondaryMassFloor = it }
        cliConfig.bridgeSupportFloor?.let { config.diagnostics.bridgeSupportFloor = it }
        cliConfig.bridgeSupportRelFraction?.let { config.diagnostics.bridgeSupportRelFraction = it }
        cliConfig.tauKappaScalingFactor?.let { config.formalism.tauKappaScalingFactor = it }
        cliConfig.deltaAssign?.let { config.formalism.deltaAssign = it }
        cliConfig.maxLeafAssignments?.let { config.formalism.maxLeafAssignments = it }
        cliConfig.refitMuPerIteration?.let { config.formalism.refitMuPerIteration = it }
        cliConfig.dagMode?.let {
            config.formalism.dagMode = taxonomy.config.DagMode.valueOf(it.uppercase())
        }
        cliConfig.numIterations?.let { config.execution.numIterations = it }

        val targetDomains = if (cliConfig.domains.isNotEmpty()) cliConfig.domains else (cliConfig.category?.let { listOf(it) } ?: emptyList())
        if (targetDomains.isNotEmpty()) {
            config.dataset.selectedDomains = targetDomains
        }

        val seeds = if (cliConfig.seeds.isNotEmpty()) cliConfig.seeds else listOf(cliConfig.seed)
        for (currentSeed in seeds) {
            val baseDir = File(cliConfig.outputDir + "/seed_$currentSeed")
            baseDir.mkdirs()
            taxonomy.model.ExperimentOutputContext.activeBaseDir = baseDir
            val seedLogFile = File(baseDir, "headless_run.log")
            val seedAppender = try {
                startFileLogging(seedLogFile.absolutePath)
            } catch (e: Exception) {
                log.error("Failed to initialize seed file logging: ${e.message}")
                null
            }

            try {
                log.info("==================================================")
                log.info("STARTING PIPELINE AND EVALUATION WITH SEED: $currentSeed")
                log.info("==================================================")

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
                log.info("Splitting dataset into train/test (ratio=${cliConfig.testRatio}, seed=$currentSeed)...")
                val (trainSet, testSet) = datasetFetcher.splitTrainTest(
                    dataset,
                    testRatio = cliConfig.testRatio,
                    seed = currentSeed
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
                log.info("Regenerating deterministic 70/30 split (ratio=${cliConfig.testRatio}, seed=$currentSeed)")
                if (!datasetFetcher.isDatasetDownloaded()) {
                    log.info("Downloading dataset...")
                    datasetFetcher.downloadDataset()
                }
                val dataset = datasetFetcher.fetchDataset(
                    selectedDomains = targetDomains
                )
                datasetFetcher.splitTrainTest(dataset, testRatio = cliConfig.testRatio, seed = currentSeed)
                log.info("Syncing database reserved pool...")
                evalLoader.syncReservedPool()
            }

            // 3. Create export directories per seed
            val baseDir = File(cliConfig.outputDir + "/seed_$currentSeed")
            val validationDir = File(baseDir, "validation")
            val judgingDir = File(baseDir, "judging")
            validationDir.mkdirs()
            judgingDir.mkdirs()
            taxonomy.model.ExperimentOutputContext.activeBaseDir = baseDir

            // Export bridge details for diagnostics
            exportBridgeNodes(validationDir, root)
            exportBridgeResiduals(validationDir, root)

            // 4. Run trickle validation if enabled
            val reportsByCondition = mutableMapOf<String, BenchmarkReport>()
            val completedConditions = mutableListOf<String>()
            val logicalComparisonsMap = mutableMapOf<String, Int>()
            val judgeApiCallsMap = mutableMapOf<String, Int>()

            // 4. Run each condition back-to-back if enabled
            if (cliConfig.runBenchmark) {
                cliConfig.conditions.forEach { condition ->
                    log.info("========================================")
                    log.info("RUNNING BENCHMARK CONDITION: $condition")
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
                        seed = currentSeed
                    )

                    val report = benchmarkService.runBenchmark(request)
                    reportsByCondition[condition] = report
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

                // Write Experiment Manifest
                val manifestFile = File(baseDir, "manifest.json")
                val manifest = ExperimentManifest(
                    runId = "run_" + Instant.now().toString().replace(":", "-"),
                    snapshotId = snapshotId,
                    models = cliConfig.models,
                    seed = currentSeed,
                    testRatio = cliConfig.testRatio,
                    conditionsRun = completedConditions,
                    runTimestamp = Instant.now().toString(),
                    logicalComparisons = logicalComparisonsMap,
                    llmJudgeApiCalls = judgeApiCallsMap
                )
                manifestFile.writeText(json.encodeToString(manifest))
                log.info("Experiment manifest written to ${manifestFile.absolutePath}")
            }

            // 5. Run trickle validation if enabled
            if (cliConfig.runTrickle) {
                val baseSnapshotId = snapshotId.substringBefore("_MAIN").substringBefore("_ORACLE").substringBefore("_C3").substringBefore("_C5").substringBefore("_GENERIC_JUDGE").substringBefore("_RANDOM_SCHEDULER").substringBefore("_KMEANS_BASELINE").substringBefore("_WARD_BASELINE").substringBefore("_RANDOMNULL_BASELINE")

                log.info("========================================")
                log.info("RUNNING TRICKLE VALIDATION: MAIN")
                log.info("========================================")
                taxonomyService.setGraph(root)
                val mainCorrect = runHeadlessTrickle(root, "MAIN", cliConfig, baseDir, currentSeed, reportsByCondition["MAIN"])

                if (cliConfig.runBaselines) {
                    var kmeansCorrect: Map<String, Boolean>? = null
                    val kmeansSnapshot = "${baseSnapshotId}_baseline_kmeans"
                    snapshotManager.loadSnapshot(kmeansSnapshot)?.let { kmeansRoot ->
                        log.info("========================================")
                        log.info("RUNNING TRICKLE VALIDATION: KMEANS_BASELINE")
                        log.info("========================================")
                        taxonomyService.setGraph(kmeansRoot)
                        kmeansCorrect = runHeadlessTrickle(kmeansRoot, "KMEANS_BASELINE", cliConfig, baseDir, currentSeed, reportsByCondition["KMEANS_BASELINE"])
                    }

                    var wardCorrect: Map<String, Boolean>? = null
                    val wardSnapshot = "${baseSnapshotId}_baseline_ward"
                    snapshotManager.loadSnapshot(wardSnapshot)?.let { wardRoot ->
                        log.info("========================================")
                        log.info("RUNNING TRICKLE VALIDATION: WARD_BASELINE")
                        log.info("========================================")
                        taxonomyService.setGraph(wardRoot)
                        wardCorrect = runHeadlessTrickle(wardRoot, "WARD_BASELINE", cliConfig, baseDir, currentSeed, reportsByCondition["WARD_BASELINE"])
                    }

                    var randomNullCorrect: Map<String, Boolean>? = null
                    val randomNullSnapshot = "${baseSnapshotId}_baseline_randomnull"
                    snapshotManager.loadSnapshot(randomNullSnapshot)?.let { randomNullRoot ->
                        log.info("========================================")
                        log.info("RUNNING TRICKLE VALIDATION: RANDOMNULL_BASELINE")
                        log.info("========================================")
                        taxonomyService.setGraph(randomNullRoot)
                        randomNullCorrect = runHeadlessTrickle(randomNullRoot, "RANDOMNULL_BASELINE", cliConfig, baseDir, currentSeed, reportsByCondition["RANDOMNULL_BASELINE"])
                    }

                    // McNemar significance comparisons between MAIN and the baselines
                    try {
                        val mcnemarFile = File(validationDir, "mcnemar_significance_results.csv")
                        mcnemarFile.bufferedWriter().use { writer ->
                            writer.write("Baseline,BothCorrect,MainCorrectBaselineIncorrect,BaselineCorrectMainIncorrect,BothIncorrect,ChiSquared,PValue\n")
                            
                            fun checkMcNemar(baselineName: String, baselineCorrect: Map<String, Boolean>?) {
                                if (baselineCorrect == null) return
                                var bothCorrect = 0
                                var mainCorrectBaselineIncorrect = 0
                                var baselineCorrectMainIncorrect = 0
                                var bothIncorrect = 0
                                
                                for ((q, correctMain) in mainCorrect) {
                                    val correctBase = baselineCorrect[q] ?: false
                                    if (correctMain && correctBase) bothCorrect++
                                    else if (correctMain && !correctBase) mainCorrectBaselineIncorrect++
                                    else if (!correctMain && correctBase) baselineCorrectMainIncorrect++
                                    else bothIncorrect++
                                }
                                val discordant = mainCorrectBaselineIncorrect + baselineCorrectMainIncorrect
                                val chiSquared = if (discordant > 0) {
                                    val diff = kotlin.math.abs(mainCorrectBaselineIncorrect - baselineCorrectMainIncorrect).toDouble()
                                    val correctedDiff = (diff - 1.0).coerceAtLeast(0.0)
                                    (correctedDiff * correctedDiff) / discordant.toDouble()
                                } else 0.0
                                val pVal = ValidationService.chiSquaredToPValue(chiSquared)
                                writer.write("$baselineName,$bothCorrect,$mainCorrectBaselineIncorrect,$baselineCorrectMainIncorrect,$bothIncorrect,$chiSquared,$pVal\n")
                                
                                log.info("McNemar Significance (MAIN vs $baselineName):")
                                log.info("  - Chi-Squared: ${"%,.4f".format(chiSquared)}")
                                log.info("  - p-value: ${"%.4e".format(pVal)}")
                            }
                            
                            checkMcNemar("KMEANS_BASELINE", kmeansCorrect)
                            checkMcNemar("WARD_BASELINE", wardCorrect)
                            checkMcNemar("RANDOMNULL_BASELINE", randomNullCorrect)
                        }
                        log.info("McNemar significance results written to ${mcnemarFile.absolutePath}")
                    } catch (e: Exception) {
                        log.error("Failed to run McNemar significance tests: ${e.message}", e)
                    }
                }

                // Restore active root graph for downstream benchmark
                taxonomyService.setGraph(root)
            }
            } finally {
                try {
                    stopFileLogging(seedAppender)
                } catch (e: Exception) {
                    log.error("Failed to stop seed file logging: ${e.message}")
                }
            }
        }
    }


    private fun runHeadlessTrickle(
        root: GraphNode, 
        condition: String, 
        cliConfig: HeadlessCliConfig, 
        baseDir: File,
        currentSeed: Long,
        benchmarkReport: BenchmarkReport? = null
    ): Map<String, Boolean> = runBlocking {
        log.info("Starting Headless Batch Trickle Validation for $condition...")

        val validationDir = File(baseDir, "validation")
        validationDir.mkdirs()
        try {
            exportGraphValidity(validationDir, root, condition)
            exportTaxonomyQuality(validationDir, root, condition)
            exportBridgeQuality(validationDir, root, condition)
        } catch (e: Exception) {
            log.error("Failed to export structural/quality metrics for $condition: ${e.message}", e)
        }

        val reservedFile = File("reserved_test_queries.json")
        if (!reservedFile.exists()) {
            log.warn("reserved_test_queries.json not found — cannot run trickle validation."); return@runBlocking emptyMap()
        }
        val reservedByDomain: Map<String, List<Int>> = try {
            json.decodeFromString(reservedFile.readText())
        } catch (t: Throwable) {
            log.error("Failed to parse reserved set for trickle validation", t); return@runBlocking emptyMap()
        }

        fun cleanText(s: String): String = s.replace("\r\n", "\n").replace("\r", "\n").trim()

        val leaves = taxonomy.tui.service.BatchTrickleEvaluator.collectLeaves(root)
        val textToDomain = HashMap<String, String>()

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

        val profiles = taxonomy.tui.service.BatchTrickleEvaluator.buildLeafProfiles(leaves, textToDomain)
        log.info("Indexed leaves: ${profiles.size} / ${leaves.size} leaves tagged with a domain.")
        if (profiles.isEmpty()) {
            log.warn("No leaves could be tagged — DAG has no labeled training queries. Skipping trickle."); return@runBlocking emptyMap()
        }

        val idToText = fullByDomain.values.flatten().associate { it.id to it.text }
        val poolAll = reservedByDomain
            .flatMap { (domain, ids) ->
                ids.mapNotNull { id ->
                    idToText[id]?.let { text -> domain to text }
                }
            }
            .shuffled(java.util.Random(currentSeed))
        
        val testQueries = poolAll
        if (testQueries.isEmpty()) {
            log.warn("Reserved test set is empty. Skipping trickle."); return@runBlocking emptyMap()
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
        log.info("  - Top-1 Accuracy: ${"%,.2f%%".format(out.top1Accuracy * 100)} (95% Wilson CI: [${"%,.2f%%".format(out.top1WilsonLow * 100)}, ${"%,.2f%%".format(out.top1WilsonHigh * 100)}])")
        log.info("  - Any-Match Accuracy: ${"%,.2f%%".format(out.anyMatchAccuracy * 100)}")
        log.info("  - Mean Leaf Purity: ${"%,.2f%%".format(out.meanLeafPurity * 100)}")
        log.info("  - Expected Calibration Error (ECE): ${"%,.4f".format(out.ece)}")
        log.info("  - Macro F1: ${"%,.2f%%".format(out.macroF1 * 100)}")
        log.info("  - Avg Match Count (Eval): ${"%,.2f".format(out.avgMatchCountEval)} leaves/query")
        log.info("  - Median Nodes/Query (Eval): ${"%,.2f".format(out.medianNodesPerQueryEval)}")

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

        val trickleDir = File(baseDir, "validation")
        trickleDir.mkdirs()
        val file = File(trickleDir, "${condition}_trickle_validation_results.csv")
        file.bufferedWriter().use { writer ->
            writer.write("Metric,Value\n")
            writer.write("TotalQueries,${out.totalQueries}\n")
            writer.write("Top1Accuracy,${out.top1Accuracy}\n")
            writer.write("Top1WilsonLow,${out.top1WilsonLow}\n")
            writer.write("Top1WilsonHigh,${out.top1WilsonHigh}\n")
            writer.write("AnyMatchAccuracy,${out.anyMatchAccuracy}\n")
            writer.write("MeanLeafPurity,${out.meanLeafPurity}\n")
            writer.write("MeanRoutingDepth,${out.meanRoutingDepth}\n")
            writer.write("MacroF1,${out.macroF1}\n")
            writer.write("NoMatchRate,${out.noMatchRate}\n")
            writer.write("ECE,${out.ece}\n")
            writer.write("AvgMatchCountEval,${out.avgMatchCountEval}\n")
            writer.write("MedianNodesPerQueryEval,${out.medianNodesPerQueryEval}\n")
        }
        log.info("Trickle validation results written to ${file.absolutePath}")

        // 1. Run Nearest Centroid flat sweep baseline
        try {
            runCentroidRoutingTest(leaves, profiles, testQueries, condition, baseDir)
        } catch (e: Exception) {
            log.error("Failed to run centroid routing test: ${e.message}", e)
        }

        // 2. Compute and export migration flow matrix
        try {
            val domainsList = profiles.values.map { it.dominantDomain }.distinct().sorted()
            val matrix = LinkedHashMap<String, LinkedHashMap<String, Int>>()
            for (trueDomain in testQueries.map { it.first }.distinct().sorted()) {
                val row = LinkedHashMap<String, Int>()
                domainsList.forEach { row[it] = 0 }
                row["Other"] = 0
                matrix[trueDomain] = row
            }

            for ((trueDomain, text) in testQueries) {
                val matched = try {
                    runBlocking {
                        taxonomyService.routeQueryToLeaves(text).mapNotNull { (leaf, conf) ->
                            profiles[leaf.id]?.let { it to conf }
                        }
                    }
                } catch (t: Throwable) {
                    emptyList()
                }
                val row = matrix[trueDomain] ?: continue
                if (matched.isEmpty()) {
                    row["Other"] = (row["Other"] ?: 0) + 1
                } else {
                    val top = matched.maxByOrNull { it.second }!!.first
                    val predicted = top.dominantDomain
                    row[predicted] = (row[predicted] ?: 0) + 1
                }
            }

            val matrixFile = File(trickleDir, "${condition}_migration_flow_matrix.csv")
            matrixFile.bufferedWriter().use { writer ->
                writer.write("TrueDomain," + domainsList.joinToString(",") + ",Other\n")
                for ((trueDomain, row) in matrix) {
                    writer.write(trueDomain + "," + domainsList.map { row[it] ?: 0 }.joinToString(",") + "," + (row["Other"] ?: 0) + "\n")
                }
            }
            log.info("Migration flow matrix written to ${matrixFile.absolutePath}")
        } catch (e: Exception) {
            log.error("Failed to generate migration flow matrix: ${e.message}", e)
        }

        // 3. Compute and export WARD/MAIN diagnostics
        val correctnessMap = HashMap<String, Boolean>()
        var diagWriter: java.io.BufferedWriter? = null
        try {
            if (condition.equals("WARD_BASELINE", ignoreCase = true) || condition.equals("MAIN", ignoreCase = true)) {
                val diagFile = File(trickleDir, "${condition}_routing_diagnostics.txt")
                diagWriter = diagFile.bufferedWriter()
                diagWriter.write("=== Per-Query Routing Diagnostics ($condition) ===\n\n")
            }

            for ((trueDomain, text) in testQueries) {
                val matched = try {
                    runBlocking {
                        taxonomyService.routeQueryToLeaves(text).mapNotNull { (leaf, conf) ->
                            profiles[leaf.id]?.let { it to conf }
                        }.sortedByDescending { it.second }
                    }
                } catch (t: Throwable) {
                    emptyList()
                }

                val isCorrect = if (matched.isEmpty()) {
                    false
                } else {
                    matched.first().first.dominantDomain == trueDomain
                }
                correctnessMap[text] = isCorrect

                diagWriter?.let { writer ->
                    writer.write("Query: \"$text\"\n")
                    writer.write("True Domain: $trueDomain\n")
                    writer.write("Candidate Count: ${matched.size}\n")
                    if (matched.isNotEmpty()) {
                        writer.write("Top-1 Leaf: ${matched.first().first.label} (ID: ${matched.first().first.leafId}) | Dominant: ${matched.first().first.dominantDomain} | Conf: ${"%.4f".format(matched.first().second)}\n")
                        
                        val firstCorrectIdx = matched.indexOfFirst { it.first.dominantDomain == trueDomain }
                        val firstCorrectRank = if (firstCorrectIdx != -1) (firstCorrectIdx + 1).toString() else "N/A"
                        writer.write("Rank of First Correct Domain Candidate: $firstCorrectRank\n")
                        
                        writer.write("All Match Candidates:\n")
                        matched.forEachIndexed { idx, (profile, conf) ->
                            writer.write("  [${idx + 1}] Leaf: ${profile.label} | Dominant: ${profile.dominantDomain} | Conf: ${"%.4f".format(conf)}\n")
                        }
                    } else {
                        writer.write("No candidates matched.\n")
                    }
                    writer.write("--------------------------------------------------\n")
                }
            }
        } catch (e: Exception) {
            log.error("Failed to write routing diagnostics: ${e.message}", e)
        } finally {
            diagWriter?.close()
        }

        try {
            val predictedMap = HashMap<String, Map<String, Double>>()
            val gtMap = HashMap<String, String>()
            val matchCounts = mutableListOf<Int>()
            for ((trueDomain, text) in testQueries) {
                gtMap[text] = trueDomain
                val matched = try {
                    runBlocking {
                        taxonomyService.routeQueryToLeaves(text).mapNotNull { (leaf, conf) ->
                            profiles[leaf.id]?.let { it to conf }
                        }
                    }
                } catch (t: Throwable) {
                    emptyList()
                }
                matchCounts.add(matched.size)
                if (matched.isNotEmpty()) {
                    val domainConf = matched.groupBy { it.first.dominantDomain }
                        .mapValues { (_, list) -> list.maxOf { it.second } }
                    predictedMap[text] = domainConf
                }
            }

            val brierVal = computeBrierScore(predictedMap, gtMap, profiles.values)
            val maxLeafAssignments = config.formalism.maxLeafAssignments
            val maxAssignmentCapRate = if (testQueries.isNotEmpty()) {
                matchCounts.count { it >= maxLeafAssignments }.toDouble() / testQueries.size.toDouble()
            } else 0.0

            val calibrationFile = File(trickleDir, "${condition}_routing_calibration.csv")
            calibrationFile.bufferedWriter().use { writer ->
                writer.write("Metric,Value\n")
                writer.write("RoutingECE,${out.ece}\n")
                writer.write("BrierScore,$brierVal\n")
                writer.write("AvgMatchCount,${out.avgMatchCountEval}\n")
                writer.write("NoMatchRate,${out.noMatchRate}\n")
                writer.write("MaxAssignmentCapRate,$maxAssignmentCapRate\n")
            }
            log.info("Routing calibration CSV written to ${calibrationFile.absolutePath}")

            appendToTuningLedger(
                cliConfig.outputDir,
                currentSeed,
                condition,
                root,
                out,
                brierVal,
                maxAssignmentCapRate,
                testQueries,
                profiles,
                benchmarkReport,
                cliConfig
            )
        } catch (e: Exception) {
            log.error("Failed to compute and export calibration/ledger metrics for $condition: ${e.message}", e)
        }

        return@runBlocking correctnessMap
    }

    private fun runCentroidRoutingTest(
        leaves: List<GraphNode>,
        profiles: Map<String, taxonomy.tui.service.LeafDomainProfile>,
        testQueries: List<Pair<String, String>>,
        condition: String,
        baseDir: File
    ) {
        val testTexts = testQueries.map { it.second }.toSet()
        val embeddings = embeddingCache.getBatch(testTexts)

        var top1Correct = 0
        var top3Correct = 0
        var top5Correct = 0
        var top10Correct = 0
        var total = 0

        for ((trueDomain, text) in testQueries) {
            val emb = embeddings[text] ?: continue
            val doubleEmb = DoubleArray(emb.size) { emb[it].toDouble() }
            val normEmb = l2Normalize(doubleEmb)

            val scoredLeaves = leaves.mapNotNull { leaf ->
                val profile = profiles[leaf.id] ?: return@mapNotNull null
                val centroid = leaf.vmfMu
                if (centroid.isEmpty()) return@mapNotNull null
                val doubleCentroid = DoubleArray(centroid.size) { centroid[it].toDouble() }
                val normCentroid = l2Normalize(doubleCentroid)
                val dot = dotProduct(normEmb, normCentroid)
                profile to dot
            }.sortedByDescending { it.second }

            if (scoredLeaves.isEmpty()) continue
            total++

            if (scoredLeaves.first().first.dominantDomain == trueDomain) {
                top1Correct++
            }
            if (scoredLeaves.take(3).any { it.first.dominantDomain == trueDomain }) {
                top3Correct++
            }
            if (scoredLeaves.take(5).any { it.first.dominantDomain == trueDomain }) {
                top5Correct++
            }
            if (scoredLeaves.take(10).any { it.first.dominantDomain == trueDomain }) {
                top10Correct++
            }
        }

        val t1 = if (total > 0) top1Correct.toDouble() / total else 0.0
        val t3 = if (total > 0) top3Correct.toDouble() / total else 0.0
        val t5 = if (total > 0) top5Correct.toDouble() / total else 0.0
        val t10 = if (total > 0) top10Correct.toDouble() / total else 0.0

        log.info("Nearest-Centroid Routing Results ($condition):")
        log.info("  - Total Evaluated: $total")
        log.info("  - Top-1 Accuracy: ${"%,.2f%%".format(t1 * 100)}")
        log.info("  - Top-3 Accuracy: ${"%,.2f%%".format(t3 * 100)}")
        log.info("  - Top-5 Accuracy: ${"%,.2f%%".format(t5 * 100)}")
        log.info("  - Top-10 Accuracy: ${"%,.2f%%".format(t10 * 100)}")

        val trickleDir = File(baseDir, "validation")
        val file = File(trickleDir, "${condition}_centroid_routing_results.csv")
        file.bufferedWriter().use { writer ->
            writer.write("Metric,Value\n")
            writer.write("TotalQueries,$total\n")
            writer.write("Top1Accuracy,$t1\n")
            writer.write("Top3Accuracy,$t3\n")
            writer.write("Top5Accuracy,$t5\n")
            writer.write("Top10Accuracy,$t10\n")
        }
        log.info("Centroid routing results written to ${file.absolutePath}")
    }

    private fun l2Normalize(vec: DoubleArray): DoubleArray {
        var sum = 0.0
        for (x in vec) sum += x * x
        val mag = kotlin.math.sqrt(sum)
        if (mag == 0.0) return vec
        return DoubleArray(vec.size) { vec[it] / mag }
    }

    private fun dotProduct(a: DoubleArray, b: DoubleArray): Double {
        var sum = 0.0
        val limit = minOf(a.size, b.size)
        for (i in 0 until limit) {
            sum += a[i] * b[i]
        }
        return sum
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

    private fun exportBridgeNodes(dir: File, root: GraphNode) {
        val file = File(dir, "bridge_nodes.csv")
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (!allNodes.add(n)) return
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)

        fun collectSubtreeQueries(node: GraphNode): List<Embedding> {
            val queries = mutableListOf<Embedding>()
            val visited = mutableSetOf<String>()
            fun walk(n: GraphNode) {
                if (!visited.add(n.id)) return
                if (n.isLeaf) {
                    queries.addAll(n.queries)
                } else {
                    n.children.forEach { walk(it) }
                    n.crossLinkChildren.forEach { walk(it) }
                }
            }
            walk(node)
            return queries
        }

        val bridges = allNodes.filter { it.isBridge || it.parents.size > 1 || it.crossLinkChildren.isNotEmpty() }
        file.bufferedWriter().use { writer ->
            writer.write("BridgeId,Label,MemberDomains,ChildLeafIds,Coverage,Entropy,JsDivergence,Depth\n")
            bridges.forEach { b ->
                val memberDomains = b.crossLinkChildren.mapNotNull { it.originalCategory ?: it.label }.distinct().joinToString(";")
                val childLeafIds = b.crossLinkChildren.map { it.id }.joinToString(";")
                val combinedQueries = b.crossLinkChildren.flatMap { collectSubtreeQueries(it) }.distinctBy { it.rawText }
                val coverage = combinedQueries.size
                val entropyVal = calculateGtEntropyForQueries(combinedQueries)
                val jsDiv = b.bridgeJsDivergence
                writer.write("${escapeCsv(b.id)},${escapeCsv(b.label ?: "")},${escapeCsv(memberDomains)},${escapeCsv(childLeafIds)},$coverage,${"%.4f".format(java.util.Locale.US, entropyVal)},${"%.4f".format(java.util.Locale.US, jsDiv)},${b.depth}\n")
            }
        }
        log.info("Bridge Nodes CSV written to ${file.absolutePath}")
    }

    private fun calculateGtEntropyForQueries(queries: List<Embedding>): Double {
        val counts = HashMap<String, Int>()
        for (q in queries) {
            val cat = q.groundTruthCategory
            if (!cat.isNullOrBlank()) {
                counts[cat] = (counts[cat] ?: 0) + 1
            }
        }
        val total = counts.values.sum().toDouble()
        if (total == 0.0) return 0.0
        var entropy = 0.0
        for (count in counts.values) {
            val p = count.toDouble() / total
            entropy -= p * (kotlin.math.log(p, 2.0))
        }
        return entropy
    }

    private fun exportBridgeResiduals(dir: File, root: GraphNode) {
        val file = File(dir, "bridge_residuals.csv")
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (!allNodes.add(n)) return
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)

        val queryIdToCategory = mutableMapOf<String, String>()
        allNodes.forEach { node ->
            node.queries.forEach { q ->
                val qIdStr = if (q.queryId != -1) q.queryId.toString() else q.rawText
                queryIdToCategory[qIdStr] = q.groundTruthCategory
            }
        }

        val nodesWithResiduals = allNodes.filter { it.residualQueries.isNotEmpty() }
        file.bufferedWriter().use { writer ->
            writer.write("NodeId,Label,ResidualCount,ResidualDomains,ConfDistribution\n")
            nodesWithResiduals.forEach { n ->
                val confs = n.residualConfidences.values
                val confSummary = if (confs.isEmpty()) {
                    "N/A"
                } else {
                    val avg = confs.average()
                    val min = confs.minOrNull() ?: 0.0
                    val max = confs.maxOrNull() ?: 0.0
                    "avg=${"%.4f".format(java.util.Locale.US, avg)};min=${"%.4f".format(java.util.Locale.US, min)};max=${"%.4f".format(java.util.Locale.US, max)}"
                }
                
                val domains = n.residualQueries.mapNotNull { qId ->
                    queryIdToCategory[qId]
                }.distinct().joinToString(";")

                writer.write("${escapeCsv(n.id)},${escapeCsv(n.label ?: "")},${n.residualQueries.size},${escapeCsv(domains)},${escapeCsv(confSummary)}\n")
            }
        }
        log.info("Bridge Residuals CSV written to ${file.absolutePath}")
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
        var seeds = listOf<Long>()
        var regenerateSplit = false
        var runPipeline = false
        var maxDepth: Int? = null
        var minClusterSize: Int? = null
        var separationEpsilon: Double? = null
        var cosineTau: Double? = null
        var routingSoftmaxTau: Double? = null
        var leafAcceptanceScale: Double? = null
        var assignmentGap: Double? = null
        var emaAlpha: Double? = null
        var enableLabeling: Boolean? = null
        var judgeInduction = false
        var datasetType: String? = null
        var runBenchmark = true
        var runTrickle = false
        var domains = listOf<String>()
        var enableStableQuestionIds: Boolean? = null
        var enableResidualRouting: Boolean? = null
        var enableResidualSplitGate: Boolean? = null
        var enableBridging: Boolean? = null
        var fusionSimilarityThreshold: Double? = null
        var effectiveSupportFloor: Double? = null
        var secondaryMassFloor: Double? = null
        var bridgeSupportFloor: Double? = null
        var bridgeSupportRelFraction: Double? = null
        var deltaAssign: Double? = null
        var maxLeafAssignments: Int? = null
        var tauKappaScalingFactor: Double? = null
        var refitMuPerIteration: Boolean? = null
        var dagMode: String? = null
        var numIterations: Int? = null
        var assignmentCosineGap: Double? = null
        var defaultKappaPrior: Double? = null
        var runBaselines = true

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
                "routingSoftmaxTau" -> routingSoftmaxTau = rawVal.toDouble()
                "emaAlpha" -> emaAlpha = rawVal.toDouble()
                "enableLabeling" -> enableLabeling = rawVal.toBoolean()
                "judgeInduction" -> judgeInduction = rawVal.toBoolean()
                "datasetType" -> datasetType = rawVal.trim('"', '\'')
                "runBenchmark" -> runBenchmark = rawVal.toBoolean()
                "runTrickle" -> runTrickle = rawVal.toBoolean()
                "domains" -> domains = parseStringList(rawVal)
                "seeds" -> seeds = parseStringList(rawVal).map { it.toLong() }
                "enableStableQuestionIds" -> enableStableQuestionIds = rawVal.toBoolean()
                "enableResidualRouting" -> enableResidualRouting = rawVal.toBoolean()
                "enableResidualSplitGate" -> enableResidualSplitGate = rawVal.toBoolean()
                "enableBridging" -> enableBridging = rawVal.toBoolean()
                "enableBridgeAnalysis" -> config.diagnostics.enableBridgeAnalysis = rawVal.toBoolean()
                "fusionSimilarityThreshold" -> fusionSimilarityThreshold = rawVal.toDouble()
                "effectiveSupportFloor" -> effectiveSupportFloor = rawVal.toDouble()
                "secondaryMassFloor" -> secondaryMassFloor = rawVal.toDouble()
                "bridgeSupportFloor" -> bridgeSupportFloor = rawVal.toDouble()
                "bridgeSupportRelFraction" -> bridgeSupportRelFraction = rawVal.toDouble()
                "deltaAssign" -> deltaAssign = rawVal.toDouble()
                "maxLeafAssignments" -> maxLeafAssignments = rawVal.toInt()
                "tauKappaScalingFactor" -> tauKappaScalingFactor = rawVal.toDouble()
                "refitMuPerIteration" -> refitMuPerIteration = rawVal.toBoolean()
                "dagMode" -> dagMode = rawVal.trim().trim('"').trim('\'')
                "numIterations" -> numIterations = rawVal.toInt()
                "assignmentCosineGap" -> assignmentCosineGap = rawVal.toDouble()
                "defaultKappaPrior" -> defaultKappaPrior = rawVal.toDouble()
                "runBaselines" -> runBaselines = rawVal.toBoolean()
                else -> log.warn("[CONFIG WARN] Unknown or deprecated configuration key in TOML file: '$key' = '$rawVal'")
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
            seeds = seeds,
            regenerateSplit = regenerateSplit,
            runPipeline = runPipeline,
            maxDepth = maxDepth,
            minClusterSize = minClusterSize,
            separationEpsilon = separationEpsilon,
            routingSoftmaxTau = routingSoftmaxTau,
            assignmentCosineGap = assignmentCosineGap,
            defaultKappaPrior = defaultKappaPrior,
            emaAlpha = emaAlpha,
            enableLabeling = enableLabeling,
            judgeInduction = judgeInduction,
            datasetType = datasetType,
            runBenchmark = runBenchmark,
            runTrickle = runTrickle,
            domains = domains,
            enableStableQuestionIds = enableStableQuestionIds,
            enableResidualRouting = enableResidualRouting,
            enableResidualSplitGate = enableResidualSplitGate,
            enableBridging = enableBridging,
            fusionSimilarityThreshold = fusionSimilarityThreshold,
            effectiveSupportFloor = effectiveSupportFloor,
            secondaryMassFloor = secondaryMassFloor,
            bridgeSupportFloor = bridgeSupportFloor,
            bridgeSupportRelFraction = bridgeSupportRelFraction,
            deltaAssign = deltaAssign,
            maxLeafAssignments = maxLeafAssignments,
            tauKappaScalingFactor = tauKappaScalingFactor,
            refitMuPerIteration = refitMuPerIteration,
            dagMode = dagMode,
            numIterations = numIterations,
            runBaselines = runBaselines
        )
    }

    private fun checkAcyclic(root: GraphNode): Boolean {
        val visited = mutableMapOf<String, Int>() // 0=unvisited, 1=visiting, 2=visited
        fun dfs(n: GraphNode): Boolean {
            val state = visited[n.id] ?: 0
            if (state == 1) return false
            if (state == 2) return true
            visited[n.id] = 1
            for (c in n.children + n.crossLinkChildren) {
                if (!dfs(c)) return false
            }
            visited[n.id] = 2
            return true
        }
        return dfs(root)
    }

    private fun getGitCommitSha(): String {
        return try {
            val process = Runtime.getRuntime().exec("git rev-parse HEAD")
            process.inputStream.bufferedReader().readText().trim()
        } catch (e: Exception) {
            "unknown"
        }
    }

    private fun computeConfigHash(): String {
        val raw = listOf(
            config.formalism.maxDepth,
            config.formalism.minClusterSize,
            config.formalism.separationEpsilon,
            config.formalism.routingSoftmaxTau,
            config.formalism.assignmentCosineGap,
            config.formalism.deltaAssign,
            config.formalism.maxLeafAssignments,
            config.formalism.tauKappaScalingFactor,
            config.formalism.dagMode,
            config.formalism.emaAlpha,
            config.formalism.refitMuPerIteration,
            config.formalism.fusionSimilarityThreshold,
            config.formalism.effectiveSupportFloor,
            config.diagnostics.secondaryMassFloor,
            config.diagnostics.bridgeSupportFloor,
            config.diagnostics.bridgeSupportRelFraction
        ).joinToString(",")
        return String.format(java.util.Locale.US, "%08x", raw.hashCode())
    }

    private fun exportGraphValidity(dir: File, root: GraphNode, condition: String) {
        val file = File(dir, "${condition}_graph_validity.csv")
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (!allNodes.add(n)) return
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)

        val acyclic = checkAcyclic(root)
        val rootReachable = true
        val leafCount = allNodes.count { it.isLeaf }
        val bridgeCount = allNodes.count { it.isBridge }
        val orphanCount = allNodes.count { it.id != root.id && it.parents.isEmpty() }
        
        val bridges = allNodes.filter { it.isBridge }
        val bridgeGroups = bridges.groupBy { it.crossLinkChildren.map { c -> c.id }.toSet() }
        val duplicateBridgeCount = bridgeGroups.values.filter { it.size > 1 }.sumOf { it.size - 1 }

        val depthDist = allNodes.groupBy { it.depth }
            .entries.sortedBy { it.key }
            .joinToString(";") { "${it.key}:${it.value.size}" }

        val residualCount = allNodes.sumOf { it.residualQueries.size }

        file.bufferedWriter().use { writer ->
            writer.write("Metric,Value\n")
            writer.write("Acyclic,$acyclic\n")
            writer.write("RootReachable,$rootReachable\n")
            writer.write("OrphanCount,$orphanCount\n")
            writer.write("DuplicateBridgeCount,$duplicateBridgeCount\n")
            writer.write("DepthDistribution,$depthDist\n")
            writer.write("LeafCount,$leafCount\n")
            writer.write("BridgeCount,$bridgeCount\n")
            writer.write("ResidualCount,$residualCount\n")
        }
        log.info("Graph validity CSV for $condition written to ${file.absolutePath}")
    }

    private fun exportTaxonomyQuality(dir: File, root: GraphNode, condition: String) {
        val file = File(dir, "${condition}_taxonomy_quality.csv")
        
        val groundTruthMap = mutableMapOf<String, List<String>>()
        fun walkGt(n: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
            if (!visited.add(n.id)) return
            n.queries.forEach { emb ->
                val gt = emb.groundTruthCategory
                if (gt.isNotBlank()) {
                    groundTruthMap[emb.rawText] = listOf(gt)
                }
            }
            n.children.forEach { walkGt(it, visited) }
            n.crossLinkChildren.forEach { walkGt(it, visited) }
        }
        walkGt(root)

        val reportObj = taxonomy.utils.TaxonomyMetrics(root, groundTruthMap).generateReport()

        file.bufferedWriter().use { writer ->
            writer.write("Metric,Value\n")
            writer.write("WeightedLeafPurity,${reportObj.weightedLeafPurity}\n")
            writer.write("DendrogramPurity,${reportObj.dendrogramPurity}\n")
            writer.write("SphericalSilhouette,${reportObj.sphericalSilhouette}\n")
            writer.write("TotalDasguptaCost,${reportObj.totalDasguptaCost}\n")
            writer.write("NormalisedSackinIndex,${reportObj.normalisedSackin}\n")
        }
        log.info("Taxonomy quality CSV for $condition written to ${file.absolutePath}")
    }

    private fun exportBridgeQuality(dir: File, root: GraphNode, condition: String) {
        val file = File(dir, "${condition}_bridge_quality.csv")
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (!allNodes.add(n)) return
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)

        val bridges = allNodes.filter { it.isBridge || it.parents.size > 1 || it.crossLinkChildren.isNotEmpty() }
        val sourceA = bridges.filter { it.parents.size > 1 && !it.id.startsWith("bridge_sourceB_") }
        val sourceB = bridges.filter { it.crossLinkChildren.isNotEmpty() || it.id.startsWith("bridge_sourceB_") }

        fun collectSubtreeQueries(node: GraphNode): List<Embedding> {
            val queries = mutableListOf<Embedding>()
            val visited = mutableSetOf<String>()
            fun walkSub(n: GraphNode) {
                if (!visited.add(n.id)) return
                if (n.isLeaf) {
                    queries.addAll(n.queries)
                } else {
                    n.children.forEach { walkSub(it) }
                    n.crossLinkChildren.forEach { walkSub(it) }
                }
            }
            walkSub(node)
            return queries
        }

        file.bufferedWriter().use { writer ->
            writer.write("Metric/BridgeId,BridgeType/Value,Depth,Coverage,CrossDomainLabelMix,TopRepresentativeQueries\n")
            writer.write("SourceA_Count,${sourceA.size},N/A,N/A,N/A,N/A\n")
            writer.write("SourceB_Count,${sourceB.size},N/A,N/A,N/A,N/A\n")
            bridges.forEach { b ->
                val bType = if (b.id.startsWith("bridge_sourceB_")) "SourceB" else "SourceA"
                val memberDomains = b.crossLinkChildren.mapNotNull { it.originalCategory ?: it.label }.distinct().joinToString(";")
                val combinedQueries = b.crossLinkChildren.flatMap { collectSubtreeQueries(it) }.distinctBy { it.rawText }
                val coverage = combinedQueries.size
                val topQueries = b.queries.take(10).map { it.rawText.replace(",", " ").replace("\n", " ").trim() }.joinToString(";")
                writer.write("${escapeCsv(b.id)},$bType,${b.depth},$coverage,${escapeCsv(memberDomains)},${escapeCsv(topQueries)}\n")
            }
        }
        log.info("Bridge quality CSV for $condition written to ${file.absolutePath}")
    }

    private fun computeBrierScore(
        predictedMap: Map<String, Map<String, Double>>,
        gtMap: Map<String, String>,
        perLeafDomains: Collection<taxonomy.tui.service.LeafDomainProfile>
    ): Double {
        if (gtMap.isEmpty()) return 0.0
        val allDomains = (perLeafDomains.map { it.dominantDomain } + gtMap.values).distinct().toSet()
        var brierSum = 0.0
        for ((text, trueDomain) in gtMap) {
            val domainConf = predictedMap[text] ?: emptyMap()
            var queryBrier = 0.0
            for (d in allDomains) {
                val f = domainConf[d] ?: 0.0
                val y = if (d == trueDomain) 1.0 else 0.0
                queryBrier += (f - y) * (f - y)
            }
            brierSum += queryBrier
        }
        return brierSum / gtMap.size
    }

    private fun appendToTuningLedger(
        outputDir: String,
        currentSeed: Long,
        condition: String,
        root: GraphNode,
        out: taxonomy.tui.BatchTrickleTestResults,
        brierVal: Double,
        maxAssignmentCapRate: Double,
        testQueries: List<Pair<String, String>>,
        profiles: Map<String, LeafDomainProfile>,
        benchmarkReport: BenchmarkReport?,
        cliConfig: HeadlessCliConfig
    ) {
        val ledgerFile = File(outputDir, "tuning_ledger.csv")
        val isNew = !ledgerFile.exists()

        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (!allNodes.add(n)) return
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)

        val acyclic = checkAcyclic(root)
        val rootReachable = true
        val leafCount = allNodes.count { it.isLeaf }
        val bridges = allNodes.filter { it.isBridge || it.parents.size > 1 || it.crossLinkChildren.isNotEmpty() }
        val bridgeCount = bridges.size
        val orphanCount = allNodes.count { it.id != root.id && it.parents.isEmpty() }
        
        val bridgeGroups = bridges.groupBy { (it.children.map { c -> c.id } + it.crossLinkChildren.map { c -> c.id }).toSet() }
        val duplicateBridgeCount = bridgeGroups.values.filter { it.size > 1 }.sumOf { it.size - 1 }
        val residualCount = allNodes.sumOf { it.residualQueries.size }

        val sourceA = bridges.filter { it.parents.size > 1 && !it.id.startsWith("bridge_sourceB_") }
        val sourceB = bridges.filter { it.crossLinkChildren.isNotEmpty() || it.id.startsWith("bridge_sourceB_") }

        val groundTruthMap = mutableMapOf<String, List<String>>()
        fun walkGt(n: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
            if (!visited.add(n.id)) return
            n.queries.forEach { emb ->
                val gt = emb.groundTruthCategory
                if (gt.isNotBlank()) {
                    groundTruthMap[emb.rawText] = listOf(gt)
                }
            }
            n.children.forEach { walkGt(it, visited) }
            n.crossLinkChildren.forEach { walkGt(it, visited) }
        }
        walkGt(root)

        val reportObj = taxonomy.utils.TaxonomyMetrics(root, groundTruthMap).generateReport()

        val configHash = computeConfigHash()
        val commitSha = getGitCommitSha()

        // ─── Extended metrics calculations ───
        val valReport = benchmarkReport?.let { report ->
            try {
                ValidationService.computeMetrics(report, cliConfig.models, "OVERALL")
            } catch (e: Exception) {
                null
            }
        }

        // Soft routing / borderline
        var borderlineCount = 0
        var softDegreeSum = 0
        var entropyGuardCount = 0
        var essSum = 0.0

        val queryToPrimaryLeaf = testQueries.associate { (_, text) ->
            val matched = try {
                runBlocking { taxonomyService.routeQueryToLeaves(text) }
            } catch (t: Throwable) {
                emptyList()
            }
            text to matched.firstOrNull()?.first
        }

        for ((_, text) in testQueries) {
            val matched = try {
                runBlocking { taxonomyService.routeQueryToLeaves(text) }
            } catch (t: Throwable) {
                emptyList()
            }
            
            val isBorderline = matched.size > 1
            if (isBorderline) {
                borderlineCount++
                softDegreeSum += matched.size
            }
            
            val softResult = try {
                runBlocking { arenaService.routeToLeavesSoft(text, null, null) }
            } catch (t: Throwable) {
                null
            }
            
            if (softResult != null) {
                val wSecondary = softResult.secondaryMemberships.values
                val wPrimary = (1.0 - wSecondary.sum()).coerceIn(0.0, 1.0)
                val sumW2 = wPrimary * wPrimary + wSecondary.sumOf { it * it }
                val ess = if (sumW2 > 0.0) 1.0 / sumW2 else 1.0
                essSum += ess
                
                if (isBorderline && wSecondary.isEmpty()) {
                    entropyGuardCount++
                }
            } else {
                essSum += 1.0
            }
        }

        val borderlineRate = if (testQueries.isNotEmpty()) borderlineCount.toDouble() / testQueries.size else 0.0
        val softDegreeMean = if (borderlineCount > 0) softDegreeSum.toDouble() / borderlineCount else 0.0
        val entropyGuardRate = if (borderlineCount > 0) entropyGuardCount.toDouble() / borderlineCount else 0.0
        val softEffSampleSize = essSum

        // Migration / non-vacuity
        var migrationCount = 0
        for ((trueDomain, text) in testQueries) {
            val primaryLeaf = queryToPrimaryLeaf[text]
            val primaryLeafId = primaryLeaf?.id
            val adaptedAnchor = if (primaryLeafId != null) profiles[primaryLeafId]?.dominantDomain else null
            if (adaptedAnchor != null && adaptedAnchor != trueDomain) {
                migrationCount++
            }
        }
        val crossAnchorMigrationRate = if (testQueries.isNotEmpty()) migrationCount.toDouble() / testQueries.size else 0.0

        val jaccards = mutableListOf<Double>()
        for ((leafId, profile) in profiles) {
            val canonicalQueries = testQueries.filter { it.first == profile.dominantDomain }.map { it.second }.toSet()
            val adaptedQueries = testQueries.filter { queryToPrimaryLeaf[it.second]?.id == leafId }.map { it.second }.toSet()
            
            val intersection = canonicalQueries.intersect(adaptedQueries).size
            val union = canonicalQueries.union(adaptedQueries).size
            if (union > 0) {
                jaccards.add(intersection.toDouble() / union.toDouble())
            }
        }
        val canonicalAdaptedJaccard = if (jaccards.isNotEmpty()) {
            val sorted = jaccards.sorted()
            if (sorted.size % 2 == 0) {
                (sorted[sorted.size / 2] + sorted[sorted.size / 2 - 1]) / 2.0
            } else {
                sorted[sorted.size / 2]
            }
        } else 0.0
        val canonicalAdaptedSymDiffMass = 1.0 - canonicalAdaptedJaccard

        // vMF kappa / dOverN summaries
        val leaves = allNodes.filter { it.isLeaf }
        val smallLeaves = leaves.filter { it.dOverN > 10.0 }
        val smallLeafFraction = if (leaves.isNotEmpty()) smallLeaves.size.toDouble() / leaves.size else 0.0
        
        val shrinkageVals = smallLeaves.mapNotNull { leaf ->
            val branchQueries = leaf.getAllQueriesInRegion()
            val n = branchQueries.size
            val d = leaf.sliceDim
            if (n > 0 && d > 0) {
                val projected = branchQueries.map { it.projectTo(d) }
                val sumVec = DoubleArray(d)
                for (vec in projected) for (i in 0 until d) sumVec[i] += vec[i]
                var normVec = 0.0
                for (i in 0 until d) normVec += sumVec[i] * sumVec[i]
                normVec = sqrt(normVec)
                val rBar = normVec / n
                val rawKappa = StatisticsUtils.correctedKappa(rBar, d, n)
                val kappaNew = leaf.vmfKappa
                if (rawKappa > 0.0) {
                    kotlin.math.abs(kappaNew - rawKappa) / rawKappa
                } else null
            } else null
        }
        val kappaShrinkageMean = if (shrinkageVals.isNotEmpty()) shrinkageVals.sum() / shrinkageVals.size else 0.0

        // Delta Rho decomposition
        val rhoCanonicalHard = valReport?.rhoHardCanonical ?: 0.0
        val rhoAdaptedHard = valReport?.rhoHardAdapted ?: 0.0
        val rhoAdaptedSoft = valReport?.rhoSoftAdapted ?: 0.0
        val deltaRhoGeom = valReport?.deltaRhoGeom ?: 0.0
        val deltaRhoSoft = valReport?.deltaRhoSoft ?: 0.0
        val deltaRhoTotal = valReport?.deltaRhoTotal ?: 0.0

        // Judge-readiness
        val leafCounts = leaves.map { it.getAllQueriesInRegion().size }
        val sortedCounts = leafCounts.sorted()
        val selectedNodeP10QueryCount = if (sortedCounts.isNotEmpty()) {
            val idx = (sortedCounts.size * 0.10).toInt().coerceAtMost(sortedCounts.size - 1)
            sortedCounts[idx].toDouble()
        } else 0.0
        
        val starvedThreshold = 10
        val starvedCount = leafCounts.count { it < starvedThreshold }
        val selectedNodeStarvedLeafFraction = if (leafCounts.isNotEmpty()) starvedCount.toDouble() / leafCounts.size else 0.0
        
        val totalQueriesInLeaves = leafCounts.sum().toDouble()
        val selectedNodeLeafBalanceEntropy = if (totalQueriesInLeaves > 0.0) {
            -leafCounts.sumOf { count ->
                val p = count.toDouble() / totalQueriesInLeaves
                if (p > 0.0) p * kotlin.math.log(p, kotlin.math.E) else 0.0
            }
        } else 0.0

        // Bridges
        val sourceBDepth2Count = sourceB.count { it.depth >= 2 }
        val sourceBCountPerDomain = mutableMapOf<String, Int>()
        for (b in sourceB) {
            val targetedDomains = b.crossLinkChildren.mapNotNull { target ->
                profiles[target.id]?.dominantDomain
            }.distinct()
            for (domain in targetedDomains) {
                sourceBCountPerDomain[domain] = (sourceBCountPerDomain[domain] ?: 0) + 1
            }
        }
        val allDomains = profiles.values.map { it.dominantDomain }.distinct()
        val sourceBPerAnchorMean = if (allDomains.isNotEmpty()) {
            allDomains.sumOf { domain -> sourceBCountPerDomain[domain] ?: 0 }.toDouble() / allDomains.size
        } else 0.0
        val bridgeStabilityScore = "NA"

        ledgerFile.parentFile?.mkdirs()
        val fw = java.io.FileWriter(ledgerFile, true)
        fw.buffered().use { writer ->
            if (isNew) {
                writer.write("ConfigHash,CommitSHA,Seed,Condition,Acyclic,RootReachable,OrphanCount,DuplicateBridgeCount,LeafCount,BridgeCount,ResidualCount,WeightedLeafPurity,DendrogramPurity,SphericalSilhouette,TotalDasguptaCost,NormalisedSackinIndex,SourceA_Count,SourceB_Count,RoutingECE,BrierScore,AvgMatchCount,NoMatchRate,MaxAssignmentCapRate,Top1Accuracy,AnyMatchAccuracy,MacroF1,BorderlineRate,SoftDegreeMean,EntropyGuardRate,SoftEffSampleSize,CrossAnchorMigrationRate,CanonicalAdaptedJaccard,CanonicalAdaptedSymDiffMass,RhoCanonicalHard,RhoAdaptedHard,RhoAdaptedSoft,DeltaRhoGeom,DeltaRhoSoft,DeltaRhoTotal,SmallLeafFraction,KappaShrinkageMean,SelectedNodeP10QueryCount,SelectedNodeStarvedLeafFraction,SelectedNodeLeafBalanceEntropy,SourceBBridgeCount,SourceBDepth2Count,SourceBPerAnchorMean,BridgeStabilityScore\n")
            }
            writer.write("$configHash,$commitSha,$currentSeed,$condition,$acyclic,$rootReachable,$orphanCount,$duplicateBridgeCount,$leafCount,$bridgeCount,$residualCount,${reportObj.weightedLeafPurity},${reportObj.dendrogramPurity},${reportObj.sphericalSilhouette},${reportObj.totalDasguptaCost},${reportObj.normalisedSackin},${sourceA.size},${sourceB.size},${out.ece},$brierVal,${out.avgMatchCountEval},${out.noMatchRate},$maxAssignmentCapRate,${out.top1Accuracy},${out.anyMatchAccuracy},${out.macroF1},$borderlineRate,$softDegreeMean,$entropyGuardRate,$softEffSampleSize,$crossAnchorMigrationRate,$canonicalAdaptedJaccard,$canonicalAdaptedSymDiffMass,$rhoCanonicalHard,$rhoAdaptedHard,$rhoAdaptedSoft,$deltaRhoGeom,$deltaRhoSoft,$deltaRhoTotal,$smallLeafFraction,$kappaShrinkageMean,$selectedNodeP10QueryCount,$selectedNodeStarvedLeafFraction,$selectedNodeLeafBalanceEntropy,${sourceB.size},$sourceBDepth2Count,$sourceBPerAnchorMean,$bridgeStabilityScore\n")
        }
        log.info("Appended condition $condition results to ledger at ${ledgerFile.absolutePath}")
    }

    private fun startFileLogging(filePath: String): ch.qos.logback.core.Appender<ch.qos.logback.classic.spi.ILoggingEvent>? {
        val context = org.slf4j.LoggerFactory.getILoggerFactory() as? ch.qos.logback.classic.LoggerContext ?: return null
        val rootLogger = context.getLogger(ch.qos.logback.classic.Logger.ROOT_LOGGER_NAME) as? ch.qos.logback.classic.Logger ?: return null

        val fileAppender = ch.qos.logback.core.FileAppender<ch.qos.logback.classic.spi.ILoggingEvent>()
        fileAppender.context = context
        fileAppender.name = "SEED_FILE_APPENDER"
        fileAppender.file = filePath
        fileAppender.isAppend = true

        val encoder = ch.qos.logback.classic.encoder.PatternLayoutEncoder()
        encoder.context = context
        encoder.charset = java.nio.charset.StandardCharsets.UTF_8
        encoder.pattern = "%d{HH:mm:ss.SSS} [%-5level] %logger{0} - %msg%n"
        encoder.start()

        fileAppender.encoder = encoder
        fileAppender.start()

        rootLogger.addAppender(fileAppender)
        return fileAppender
    }

    private fun stopFileLogging(appender: ch.qos.logback.core.Appender<ch.qos.logback.classic.spi.ILoggingEvent>?) {
        if (appender == null) return
        val context = org.slf4j.LoggerFactory.getILoggerFactory() as? ch.qos.logback.classic.LoggerContext ?: return
        val rootLogger = context.getLogger(ch.qos.logback.classic.Logger.ROOT_LOGGER_NAME) as? ch.qos.logback.classic.Logger ?: return
        rootLogger.detachAppender(appender)
        appender.stop()
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
