package taxonomy.tui.service

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.model.BenchmarkLiveStats
import taxonomy.model.BenchmarkRequest
import taxonomy.model.GraphNode
import taxonomy.service.AnalysisMode
import taxonomy.model.ModelSource
import taxonomy.service.DagSnapshot
import taxonomy.service.LeaderboardGroup
import taxonomy.service.SavedBenchmarkMetadata
import taxonomy.service.QueryResponseNode
import taxonomy.service.TaxonomyRankingService.AggregatedLeaderboard
import taxonomy.tui.BatchTrickleTestResults
import taxonomy.tui.app.TuiDependencies
import taxonomy.tui.controller.TuiGateway
import taxonomy.utils.TaxonomyMetrics
import taxonomy.utils.TuiLogAppender
import taxonomy.utils.reportToIterationMetrics
import java.io.File
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse

class TuiGatewayImpl(private val deps: TuiDependencies) : TuiGateway {

    private val dbWriteMutex = Mutex()
    private val prettyJson = kotlinx.serialization.json.Json { prettyPrint = true }

    // ── Snapshot helpers ────────────────────────────────────────────────────────

    /**
     * Appends [trace] to the snapshot log file of the currently active snapshot.
     * No-ops gracefully when no snapshot is active or the trace is empty.
     */
    private suspend fun appendTraceToActiveSnapshot(trace: List<String>) {
        if (trace.isEmpty()) return
        val snapshotId = deps.taxonomyService.activeSnapshotId() ?: return
        withContext(Dispatchers.IO) {
            deps.snapshotManager.appendLogsToSnapshot(snapshotId, trace)
        }
    }

    private suspend fun saveGraphToActiveSnapshot() {
        val snapshotId = deps.taxonomyService.activeSnapshotId() ?: return
        val root = deps.taxonomyService.rootNodeFlow.value ?: return
        dbWriteMutex.withLock {
            withContext(Dispatchers.IO) {
                deps.snapshotManager.updateSnapshot(snapshotId, root)
            }
        }
    }

    // ── Snapshot CRUD ────────────────────────────────────────────────────────────

    override suspend fun listSnapshots(): List<DagSnapshot> =
        withContext(Dispatchers.IO) { deps.snapshotManager.listSnapshots() }

    override suspend fun findSnapshot(snapshotId: String): DagSnapshot? =
        withContext(Dispatchers.IO) {
            deps.snapshotManager.listSnapshots().find { it.id == snapshotId }
        }

    override suspend fun loadSnapshot(snapshotId: String): Boolean {
        val snapshot = findSnapshot(snapshotId) ?: return false
        val root = withContext(Dispatchers.IO) {
            deps.snapshotManager.loadSnapshot(snapshot.id)
        } ?: return false

        deps.taxonomyService.setGraph(root)
        deps.taxonomyService.setActiveSnapshotId(snapshotId)
        deps.config.applyEffectiveConfig(snapshot.config ?: snapshot.settings.toEffectiveConfig())

        val uuid = snapshot.logUuid
        val fileLogs = if (uuid != null) {
            withContext(Dispatchers.IO) { deps.snapshotManager.loadSnapshotLogs(uuid) }
        } else emptyList()
        val replayLogs = (if (fileLogs.isNotEmpty()) fileLogs else snapshot.logTrace)
            .map { if (it.startsWith("[REPLAY]")) it else "[REPLAY] $it" }
        TuiLogAppender.loadHistoricalLogs(replayLogs)

        deps.taxonomyService.clearMetricsHistory()
        val report = TaxonomyMetrics(root).generateReport()
        deps.taxonomyService.addIterationMetrics(reportToIterationMetrics("Loaded Snapshot", report))

        return true
    }

    override suspend fun saveSnapshot(description: String) {
        val root = deps.taxonomyService.rootNodeFlow.value ?: return
        val snapshot = withContext(Dispatchers.IO) {
            deps.snapshotManager.saveSnapshot(root, description)
        }
        deps.taxonomyService.setActiveSnapshotId(snapshot.id)
    }

    override suspend fun renameSnapshot(snapshotId: String, newDescription: String) {
        withContext(Dispatchers.IO) { deps.snapshotManager.renameSnapshot(snapshotId, newDescription) }
    }

    override suspend fun deleteSnapshot(snapshotId: String) {
        withContext(Dispatchers.IO) { deps.snapshotManager.deleteSnapshot(snapshotId) }
        if (deps.taxonomyService.activeSnapshotId() == snapshotId) {
            deps.taxonomyService.setActiveSnapshotId(null)
        }
    }

    // ── Dataset ─────────────────────────────────────────────────────────────────

    override suspend fun isDatasetDownloaded(): Boolean =
        withContext(Dispatchers.IO) { deps.datasetFetcher.isDatasetDownloaded() }

    override suspend fun downloadDataset(maxQueries: Int, onProgress: (Float, String) -> Unit) {
        deps.datasetFetcher.onDownloadProgress = { current, total, name ->
            if (total > 0) {
                onProgress(
                    current.toFloat() / total,
                    "$name · ${"%,d".format(current)} / ${"%,d".format(total)} rows"
                )
            } else {
                onProgress(0f, "$name · Fetching… ${"%,d".format(current)} rows")
            }
        }
        onProgress(0f, "Connecting to Hugging Face…")
        val cap = if (maxQueries <= 0) MMLUDatasetFetcher.UNBOUNDED_MAX_QUERIES else maxQueries
        withContext(Dispatchers.IO) { deps.datasetFetcher.downloadDataset(maxQueries = cap) }
    }

    // ── DAG generation ───────────────────────────────────────────────────────────

    override suspend fun generateDag(onProgress: (Float, String) -> Unit) {
        withContext(Dispatchers.IO) {
            TuiLogAppender.startRecording()
            try {
                deps.log.info("DAG generation started for dataset '${deps.config.dataset.datasetType.name}'.")
                if (!deps.datasetFetcher.isDatasetDownloaded()) {
                    deps.datasetFetcher.onDownloadProgress = { current, total, name ->
                        val pct = if (total > 0) current.toFloat() / total else 0f
                        onProgress(pct * 0.3f, "Downloading $name... $current / $total")
                    }
                    deps.datasetFetcher.downloadDataset()
                }

                onProgress(0.32f, "Loading dataset \"${deps.config.dataset.datasetType.name}\"...")
                val dataset = deps.datasetFetcher.fetchDataset(
                    selectedDomains = deps.config.dataset.selectedDomains
                )

                val (trainSet, testSet) = deps.datasetFetcher.splitTrainTest(
                    dataset,
                    testRatio = deps.config.dataset.testSplitRatio
                )
                try {
                    deps.evalLoader.syncReservedPool()
                    deps.log.info("Synced reserved pool for the newly generated DAG.")
                } catch (e: Exception) {
                    deps.log.warn("Failed to sync reserved pool after train/test split: ${e.message}")
                }
                onProgress(
                    0.36f,
                    "Train ${trainSet.values.sumOf { it.size }} / test ${testSet.values.sumOf { it.size }}"
                )

                val root = deps.taxonomyEngine.adaptTaxonomy(
                    rootLabel = deps.config.dataset.datasetType.name,
                    dataset = trainSet.mapValues { (_, qs) -> qs.map { it.text } }
                )
                deps.taxonomyService.setGraph(root)
                deps.taxonomyService.setActiveSnapshotId(null)
                deps.log.info("DAG generation complete: ${trainSet.values.sumOf { it.size }} train queries processed.")
            } finally {
                TuiLogAppender.recordGenerationTrace(TuiLogAppender.stopAndGetRecording())
            }
        }
    }

    // ── Judge generation ─────────────────────────────────────────────────────────

    private suspend fun withJudgeRecording(label: String, block: suspend () -> Unit) {
        TuiLogAppender.startRecording()
        try {
            block()
        } catch (t: Throwable) {
            deps.log.error("$label failed: ${t.message}", t)
        } finally {
            appendTraceToActiveSnapshot(TuiLogAppender.stopAndGetRecording())
        }
    }

    // Bug 1 fix: forward generality as parallelismOverride into generateJudgesForDag so the
    // value the user typed in the TUI prompt is actually used.  Previously generality was
    // silently discarded and the service always used config.execution.llmParallelism.
    override suspend fun runBatchJudge(generality: Int, parallelism: Int, replaceExisting: Boolean) {
        val root = deps.taxonomyService.rootNodeFlow.value ?: return
        deps.arenaService.clearJudgeProgress()
        if (parallelism > 0) {
            deps.arenaService.llmClient.setMaxParallel(parallelism)
        }
        try {
            withJudgeRecording("Batch judge generation") {
                deps.judgeService.generateJudgesForDag(
                    root = root,
                    replaceExisting = replaceExisting,
                    maxGenerality = generality,
                    parallelismOverride = parallelism,
                    onNodeComplete = {
                        saveGraphToActiveSnapshot()
                        deps.taxonomyService.notifyGraphUpdated()
                    }
                )
            }
        } finally {
            deps.arenaService.llmClient.setMaxParallel(deps.config.execution.llmParallelism)
        }
    }

    override suspend fun regenerateLabels() {
        val root = deps.taxonomyService.rootNodeFlow.value ?: run {
            deps.log.warn("Regenerate labels: no active DAG.")
            return
        }
        deps.log.info("Regenerating all judges (replace=true)…")
        withJudgeRecording("Label regeneration") {
            deps.judgeService.generateJudgesForDag(root, replaceExisting = true)
        }
        deps.log.info("Label regeneration complete.")
    }

    override suspend fun regenerateJudgeForCurrentNode() {
        val node = deps.arenaService.state.value.selectedNode ?: run {
            deps.log.warn("Regenerate judge: no node currently inspected.")
            return
        }
        deps.log.info("Regenerating judge for node '${node.label}' (id=${node.id})…")
        withJudgeRecording("Node judge generation") {
            deps.judgeService.generateJudgeForNode(node) {
                saveGraphToActiveSnapshot()
                deps.taxonomyService.notifyGraphUpdated()
            }
        }
        deps.log.info("Node judge generation complete.")
    }

    // ── Benchmark ────────────────────────────────────────────────────────────────

    override suspend fun runBenchmarkConfigured(
        models: List<String>,
        queryLimit: Int,
        category: String?,
        confidenceGate: Double,
        parallelism: Int,
        updateRankings: Boolean,
        reservedOnly: Boolean,
        resume: Boolean,
        onLive: (BenchmarkLiveStats) -> Unit
    ) {
        if (deps.arenaService.state.value.isRunningBenchmark) {
            deps.log.warn("Benchmark is already running. Ignoring run request.")
            return
        }
        var finalModels = models
        var finalQueryLimit = queryLimit
        var finalCategory = category
        var finalConfidenceGate = confidenceGate
        var finalParallelism = parallelism
        var finalUpdateRankings = updateRankings
        var finalReservedOnly = reservedOnly

        if (resume) {
            val savedSnapshotId = findLatestSavedBenchmarkSnapshotId()
            if (savedSnapshotId != null) {
                if (savedSnapshotId != deps.taxonomyService.activeSnapshotId() && savedSnapshotId != "global") {
                    deps.log.info("Resuming benchmark: Automatically loading saved benchmark snapshot '$savedSnapshotId'")
                    loadSnapshot(savedSnapshotId)
                }
                val metadata = deps.arenaService.rankingService.getBenchmarkMetadata(savedSnapshotId)
                if (metadata != null) {
                    finalModels = metadata.models
                    finalQueryLimit = metadata.queryLimit
                    finalCategory = metadata.category
                    finalConfidenceGate = metadata.confidenceGate
                    finalParallelism = metadata.parallelism
                    finalUpdateRankings = metadata.updateRankings
                    finalReservedOnly = metadata.reservedOnly

                    val savedOffsets = deps.arenaService.rankingService.getPairQueryOffsets(savedSnapshotId)
                    val matchCount = deps.arenaService.rankingService.getAllRecordedMatches(savedSnapshotId).size
                    val totalOffset = savedOffsets.values.sum()
                    deps.log.info(
                        "Resuming benchmark: Restored snapshot '$savedSnapshotId' (settings: ${finalModels.size} models, " +
                        "$matchCount matches recorded, offset sum = $totalOffset, limit = $finalQueryLimit, category = ${finalCategory ?: "all"})"
                    )
                }
            }
        } else {
            val snapshotId = deps.taxonomyService.activeSnapshotId() ?: "global"
            deps.arenaService.rankingService.clearRatings(snapshotId)
            deps.log.info("Fresh run requested: Cleared existing ratings and offsets for snapshot '$snapshotId'.")
        }

        if (finalModels.size < 2) {
            deps.log.warn("Benchmark needs ≥2 models; got ${finalModels.size}")
            return
        }

        deps.arenaService.llmClient.setMaxParallel(finalParallelism)
        val request = BenchmarkRequest(
            models = finalModels.map { ModelSource(it) },
            queryLimit = finalQueryLimit,
            category = finalCategory?.takeIf { it.isNotBlank() },
            confidenceGate = finalConfidenceGate,
            parallelism = finalParallelism.coerceAtLeast(1),
            updateRankings = finalUpdateRankings,
            reservedOnly = finalReservedOnly
        )
        deps.log.info(
            "Starting benchmark: ${finalModels.size} models [${finalModels.joinToString()}] · " +
                "queryLimit=$finalQueryLimit · category=${finalCategory ?: "all"} · " +
                "confidenceGate=$finalConfidenceGate · parallelism=$finalParallelism · updateRankings=$finalUpdateRankings"
        )
        if (deps.taxonomyService.activeSnapshotId() == null) {
            val root = deps.taxonomyService.getGraph()
            if (root != null) {
                val snap = deps.snapshotManager.saveSnapshot(root, "auto_pre_benchmark")
                deps.taxonomyService.setActiveSnapshotId(snap.id)
                deps.log.info("Auto-saved snapshot '${snap.id}' before benchmark")
            }
        }

        val snapId = deps.taxonomyService.activeSnapshotId() ?: "global"
        deps.arenaService.rankingService.saveBenchmarkMetadata(
            SavedBenchmarkMetadata(
                snapshotId = snapId,
                models = finalModels,
                queryLimit = finalQueryLimit,
                category = finalCategory,
                confidenceGate = finalConfidenceGate,
                parallelism = finalParallelism,
                updateRankings = finalUpdateRankings,
                reservedOnly = finalReservedOnly
            )
        )

        try {
            deps.evalLoader.syncReservedPool()
            deps.log.info("Synced reserved pool before starting benchmark.")
        } catch (e: Exception) {
            deps.log.warn("Failed to sync reserved pool before benchmark: ${e.message}")
        }

        deps.arenaService.startBenchmark("Starting benchmark over ${models.size} models…")
        TuiLogAppender.startRecording()
        try {
            val report = deps.benchmarkService.runBenchmark(request) { live ->
                deps.arenaService.updateBenchmarkProgress(
                    "Processed ${live.processed}/${live.total} · " +
                        "agreement ${"%,.2f".format(live.runningAgreement)} · " +
                        "coverage ${"%,.2f".format(live.runningCoverage)}"
                )
                deps.arenaService.updateBenchmarkLiveStats(live)
                onLive(live)
            }
            deps.arenaService.completeBenchmark(report)
            
            val backupDir = java.io.File("benchmark_backups")
            if (!backupDir.exists()) {
                backupDir.mkdirs()
            }
            val timestamp = java.text.SimpleDateFormat("yyyyMMdd_HHmmss").format(java.util.Date())
            val backupFile = java.io.File(backupDir, "benchmark_${snapId}_$timestamp.json")
            try {
                val jsonString = prettyJson.encodeToString(
                    taxonomy.model.BenchmarkReport.serializer(),
                    report
                )
                backupFile.writeText(jsonString)
                deps.log.info("Saved benchmark report backup to ${backupFile.absolutePath}")
            } catch (e: Exception) {
                deps.log.error("Failed to backup benchmark report: ${e.message}", e)
            }
            deps.log.info(
                "Benchmark complete: ${report.totalQueries} queries · ${report.totalModelPairs} pairs · " +
                    "coverage ${"%,.3f".format(report.coverageRate)} · " +
                    "judge-agreement ${"%,.3f".format(report.overallJudgeAccuracyAgreement)}"
            )
            report.perPairStats.forEach { pair ->
                deps.log.info(
                    "  ${pair.modelA} vs ${pair.modelB}: " +
                        "judgeA=${pair.judgeWinsA} judgeB=${pair.judgeWinsB} ties=${pair.judgeTies} " +
                        "agreement=${"%,.3f".format(pair.judgeAccuracyAgreementRate)} " +
                        "avgConf=${"%,.3f".format(pair.avgConfidence)}"
                )
            }
        } catch (t: Throwable) {
            deps.log.error("Benchmark failed: ${t.message}", t)
            deps.arenaService.updateBenchmarkProgress("Benchmark failed: ${t.message}")
        } finally {
            deps.arenaService.llmClient.setMaxParallel(deps.config.execution.llmParallelism)
            appendTraceToActiveSnapshot(TuiLogAppender.stopAndGetRecording())
        }
    }

    // ── Arena ────────────────────────────────────────────────────────────────────

    override suspend fun runArena(query: String, modelA: String, modelB: String) {
        deps.arenaService.compareModels(query, modelA, modelB)
    }

    override suspend fun runArenaPrecomputed(questionId: Int, modelA: String, modelB: String) {
        deps.arenaService.compareModelsPrecomputed(questionId, modelA, modelB)
    }

    override suspend fun loadedModels(): List<String> =
        withContext(Dispatchers.IO) { deps.evalStore.getLoadedModels() }

    // ── Trickle ──────────────────────────────────────────────────────────────────

    override suspend fun runTrickle(query: String): List<QueryResponseNode> {
        return withContext(Dispatchers.IO) {
            try {
                deps.log.info("Trickle query: '$query'")
                val nodes = deps.taxonomyService.queryTaxonomy(query)
                deps.log.info("Trickle matched ${nodes.size} top-level result(s).")
                nodes
            } catch (t: Throwable) {
                deps.log.warn("Trickle routing failed: {}", t.message)
                emptyList()
            }
        }
    }

    private val batchJson = Json { ignoreUnknownKeys = true; isLenient = true }

    /** Returns the total number of reserved test queries across all domains. */
    override suspend fun reservedPoolSize(): Int = withContext(Dispatchers.IO) {
        val file = File("reserved_test_queries.json")
        if (!file.exists()) return@withContext 0
        try {
            val map: Map<String, List<String>> = batchJson.decodeFromString(file.readText())
            map.values.sumOf { it.size }
        } catch (_: Throwable) { 0 }
    }

    override suspend fun runBatchTrickle(
        maxQueries: Int,
        onProgress: (String) -> Unit,
        onComplete: (BatchTrickleTestResults) -> Unit
    ) {
        TuiLogAppender.startRecording()
        try {
            withContext(Dispatchers.IO) {
                val root = deps.taxonomyService.getGraph()
                if (root == null) {
                    onProgress("No active DAG — generate or load one first.")
                    onComplete(BatchTrickleTestResults())
                    return@withContext
                }

                val reservedFile = File("reserved_test_queries.json")
                if (!reservedFile.exists()) {
                    deps.log.warn("Batch trickle: reserved_test_queries.json not found.")
                    onProgress("No reserved test set found (reserved_test_queries.json).")
                    onComplete(BatchTrickleTestResults())
                    return@withContext
                }
                val reservedByDomain: Map<String, List<Int>> = try {
                    batchJson.decodeFromString(reservedFile.readText())
                } catch (t: Throwable) {
                    deps.log.error("Batch trickle: failed to parse reserved set", t)
                    onProgress("Failed to parse reserved test set.")
                    onComplete(BatchTrickleTestResults())
                    return@withContext
                }

                onProgress("Loading training distribution from cache…")
                val fullByDomain = deps.datasetFetcher.fetchDataset(
                    selectedDomains = deps.config.dataset.selectedDomains
                )
                val reservedIds: Set<Int> = reservedByDomain.values.flatten().toSet()
                val textToDomain = HashMap<String, String>()
                for ((domain, queries) in fullByDomain) {
                    for (q in queries) if (q.id !in reservedIds) textToDomain[q.text] = domain
                }

                val leaves = BatchTrickleEvaluator.collectLeaves(root)
                val profiles = BatchTrickleEvaluator.buildLeafProfiles(leaves, textToDomain)
                onProgress("Indexing leaves: ${profiles.size} / ${leaves.size} leaves tagged with a domain.")
                deps.log.info("Batch trickle: ${profiles.size}/${leaves.size} leaves tagged from ${textToDomain.size} train queries.")
                if (profiles.isEmpty()) {
                    onProgress("No leaves could be tagged — DAG has no labeled training queries.")
                    onComplete(BatchTrickleTestResults())
                    return@withContext
                }

                // Apply the user-supplied cap; 0 means "use all". Always >= 1.
                val idToText = fullByDomain.values.flatten().associate { it.id to it.text }
                val poolAll = reservedByDomain
                    .flatMap { (domain, ids) ->
                        ids.mapNotNull { id ->
                            idToText[id]?.let { text -> domain to text }
                        }
                    }
                    .shuffled()
                val sampleCap = if (maxQueries > 0) maxQueries else poolAll.size
                val testQueries = poolAll.take(sampleCap)
                if (testQueries.isEmpty()) {
                    onProgress("Reserved test set is empty.")
                    onComplete(BatchTrickleTestResults())
                    return@withContext
                }

                deps.log.info("Batch trickle: routing ${testQueries.size} reserved queries (cap=$sampleCap)…")
                val out = BatchTrickleEvaluator.computeBatchTrickleMetrics(
                    perLeafDomains = profiles,
                    testQueries = testQueries,
                    routeFn = { text ->
                        try {
                            runBlocking {
                                deps.taxonomyService.routeQueryToLeaves(text).map { it.first.id to it.second }
                            }
                        } catch (t: Throwable) {
                            deps.log.warn("Batch trickle query failed: {}", t.message)
                            emptyList()
                        }
                    },
                    onProgress = { processed, total, runningTop1 ->
                        if (processed % 10 == 0 || processed == total) {
                            onProgress("Routing test queries: $processed / $total · running top1 acc=${"%,.1f%%".format(runningTop1 * 100)}")
                        }
                    }
                )
                val summary = StringBuilder().apply {
                    appendLine()
                    appendLine("=== Batch Trickle Routing Benchmark Results ===")
                    appendLine("Total Queries: ${out.totalQueries}")
                    appendLine("Top-1 Accuracy: ${"%,.2f%%".format(out.top1Accuracy * 100)}")
                    appendLine("Any-Match Accuracy: ${"%,.2f%%".format(out.anyMatchAccuracy * 100)}")
                    appendLine("Mean Leaf Purity: ${"%,.2f%%".format(out.meanLeafPurity * 100)}")
                    appendLine("Mean Routing Depth: ${"%,.2f".format(out.meanRoutingDepth)}")
                    appendLine("Macro F1: ${"%,.2f%%".format(out.macroF1 * 100)}")
                    appendLine("No-Match Rate: ${"%,.2f%%".format(out.noMatchRate * 100)}")
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
                deps.log.info(summary)
                onComplete(out)
            }
        } finally {
            appendTraceToActiveSnapshot(TuiLogAppender.stopAndGetRecording())
        }
    }

    // ── Leaderboard / Eval ───────────────────────────────────────────────────────

    override suspend fun loadLeaderboard(): List<LeaderboardGroup> =
        withContext(Dispatchers.IO) {
            try {
                deps.arenaService.getLeaderboard("global")
            } catch (t: Throwable) {
                deps.log.warn("Leaderboard load failed: {}", t.message)
                emptyList()
            }
        }

    override fun clearLeaderboard() {
        deps.arenaService.clearLeaderboard()
    }

    override suspend fun loadLeaderboardForNode(node: GraphNode): AggregatedLeaderboard =
        withContext(Dispatchers.IO) {
            val root = deps.taxonomyService.getGraph()
            val allNodes = mutableListOf<GraphNode>()
            if (root != null) {
                val visited = mutableSetOf<String>()
                fun walk(n: GraphNode) {
                    if (!visited.add(n.id)) return
                    allNodes.add(n)
                    n.children.forEach { walk(it) }
                }
                walk(root)
            }
            val leaderboard = deps.arenaService.getLeaderboardForNode(
                node, allNodes, deps.taxonomyService.activeSnapshotId() ?: "global"
            )
            deps.arenaService.setNodeLeaderboard(leaderboard)
            leaderboard
        }

    override suspend fun loadLeafRanks(): Map<String, Pair<String, String>> =
        withContext(Dispatchers.IO) {
            val snapshotId = deps.taxonomyService.activeSnapshotId() ?: "global"
            val root = deps.taxonomyService.getGraph()
            if (root == null) return@withContext emptyMap()
            val leaves = mutableListOf<GraphNode>()
            val visited = mutableSetOf<String>()
            fun walk(n: GraphNode) {
                if (!visited.add(n.id)) return
                if (n.children.isEmpty()) leaves.add(n)
                else n.children.forEach { walk(it) }
            }
            walk(root)
            leaves.associate { leaf ->
                val ranks = deps.arenaService.rankingService.getNodeLeaderboard(leaf.id, snapshotId) ?: emptyList()
                val top2 = if (ranks.size >= 2) {
                    Pair(ranks[0].modelId, ranks[1].modelId)
                } else if (ranks.size == 1) {
                    Pair(ranks[0].modelId, "")
                } else {
                    null
                }
                leaf.id to top2
            }.filterValues { it != null }.mapValues { it.value!! }
        }

    override suspend fun findLatestSavedBenchmarkSnapshotId(): String? {
        val active = deps.taxonomyService.activeSnapshotId()
        if (active != null) {
            val hasOffsets = deps.arenaService.rankingService.getPairQueryOffsets(active).isNotEmpty()
            if (hasOffsets) return active
            return null
        }

        // If no snapshot is active (e.g. freshly generated DAG or startup)
        val currentRoot = deps.taxonomyService.getGraph()

        // Scan all snapshots sorted by timestamp descending
        val snaps = deps.snapshotManager.listSnapshots().sortedByDescending { it.timestamp }
        for (snap in snaps) {
            if (currentRoot != null && snap.graph.rootId != currentRoot.id) continue

            val hasOffsets = deps.arenaService.rankingService.getPairQueryOffsets(snap.id).isNotEmpty()
            if (hasOffsets) {
                return snap.id
            }
        }

        return null
    }

    override suspend fun hasSavedBenchmark(): Boolean =
        withContext(Dispatchers.IO) {
            findLatestSavedBenchmarkSnapshotId() != null
        }

    override suspend fun getSavedBenchmarkMetadata(): SavedBenchmarkMetadata? =
        withContext(Dispatchers.IO) {
            val targetId = findLatestSavedBenchmarkSnapshotId() ?: return@withContext null
            deps.arenaService.rankingService.getBenchmarkMetadata(targetId)
        }

    override suspend fun getModelAccuracies(
        models: List<String>,
        category: String?,
        reservedOnly: Boolean
    ): Map<String, Double> = withContext(Dispatchers.IO) {
        deps.evalStore.getModelAccuracies(models, category, reservedOnly)
    }

    override suspend fun loadSavedBenchmarkLiveStats(): taxonomy.model.BenchmarkLiveStats? =
        withContext(Dispatchers.IO) {
            val snapId = deps.taxonomyService.activeSnapshotId() ?: return@withContext null
            val metadata = deps.arenaService.rankingService.getBenchmarkMetadata(snapId) ?: return@withContext null
            val modelNames = metadata.models
            
            val allRecordedMatches = deps.arenaService.rankingService.getAllRecordedMatches(snapId)
            if (allRecordedMatches.isEmpty()) return@withContext null
            
            val runningAgreement = 1.0
            val runningCoverage = 1.0
            
            val pairs = modelNames.flatMapIndexed { i: Int, a: String ->
                modelNames.drop(i + 1).map { b: String -> Pair(a, b) }
            }
            val livePairStats = pairs.map { p ->
                val modelA = p.first
                val modelB = p.second
                val pairKey = "${modelA}_vs_${modelB}"
                val matches = allRecordedMatches.filter { (it.modelA == modelA && it.modelB == modelB) || (it.modelA == modelB && it.modelB == modelA) }
                var winsA = 0.0; var winsB = 0.0; var ties = 0
                matches.forEach { cm ->
                    if (cm.isTie) {
                        ties++
                    } else if (cm.winner == modelA) {
                        winsA++
                    } else {
                        winsB++
                    }
                }
                taxonomy.model.ModelPairStats(
                    modelA = modelA,
                    modelB = modelB,
                    totalMatches = matches.size,
                    judgeWinsA = winsA.toInt(),
                    judgeWinsB = winsB.toInt(),
                    judgeTies = ties,
                    accuracyWinsA = 0,
                    accuracyWinsB = 0,
                    accuracyTies = 0,
                    judgeAccuracyAgreementRate = 1.0,
                    avgConfidence = 1.0,
                    isExhausted = false
                )
            }
            
            val root = deps.taxonomyService.getGraph()
            val leafIds = mutableListOf<String>()
            if (root != null) {
                val visited = mutableSetOf<String>()
                fun walk(n: GraphNode) {
                    if (!visited.add(n.id)) return
                    if (n.children.isEmpty()) leafIds.add(n.id)
                    else n.children.forEach { walk(it) }
                }
                walk(root)
            }
            
            val currentAggregated = deps.arenaService.rankingService.aggregateLeafScores(leafIds, snapId)
            
            val offsets = deps.arenaService.rankingService.getPairQueryOffsets(snapId)
            val processed = allRecordedMatches.size
            val total = offsets.values.sum().coerceAtLeast(processed)
            
            taxonomy.model.BenchmarkLiveStats(
                processed = processed,
                total = total,
                currentQuestion = "",
                runningAgreement = runningAgreement,
                runningCoverage = runningCoverage,
                perCategoryProgress = emptyMap(),
                pairStats = livePairStats,
                currentRound = deps.arenaService.rankingService.getAllBtStates(snapId).values.map { it.fitVersion }.maxOrNull() ?: 1,
                activeTargets = emptyList(),
                btRatings = currentAggregated.ranks.associate { it.modelId to it.btScore },
                btErrors = currentAggregated.ranks.associate { it.modelId to it.stdError }
            )
        }

    override suspend fun downloadEvalResults(onProgress: (String, Long, Long) -> Unit) {
        withContext(Dispatchers.IO) {
            val targetDir = File(deps.config.dataset.evalResultsDir)
            val existing = targetDir.listFiles { f -> f.isFile && f.length() > 0 }
            if (targetDir.isDirectory && existing != null && existing.isNotEmpty()) {
                deps.log.info("Eval results already cached in '${targetDir.path}' (${existing.size} files); skipping download.")
                return@withContext
            }
            targetDir.mkdirs()

            val client = HttpClient.newBuilder()
                .connectTimeout(java.time.Duration.ofSeconds(10))
                .build()
            val listingUrl =
                "https://api.github.com/repos/TIGER-AI-Lab/MMLU-Pro/contents/eval_results"
            deps.log.info("Downloading MMLU-Pro eval_results from GitHub…")

            val listingReq = HttpRequest.newBuilder()
                .uri(URI.create(listingUrl))
                .header("User-Agent", "TaxoArena-TUI")
                .header("Accept", "application/vnd.github.v3+json")
                .timeout(java.time.Duration.ofSeconds(15))
                .GET()
                .build()
            val listingResp = client.send(listingReq, HttpResponse.BodyHandlers.ofString())
            if (listingResp.statusCode() != 200) {
                deps.log.error("GitHub listing failed (HTTP ${listingResp.statusCode()}).")
                return@withContext
            }

            val entries = batchJson.parseToJsonElement(listingResp.body()).jsonArray
            val files = entries.mapNotNull { el ->
                val obj = el.jsonObject
                val type = obj["type"]?.jsonPrimitive?.content
                val name = obj["name"]?.jsonPrimitive?.content
                val url = obj["download_url"]?.jsonPrimitive?.content
                val size = obj["size"]?.jsonPrimitive?.content?.toLongOrNull() ?: 0L
                if (type == "file" && name != null && url != null) Triple(name, url, size) else null
            }
            deps.log.info("Found ${files.size} eval files to download.")

            for ((name, url, size) in files) {
                try {
                    val fileReq = HttpRequest.newBuilder()
                        .uri(URI.create(url))
                        .header("User-Agent", "TaxoArena-TUI")
                        .timeout(java.time.Duration.ofSeconds(20))
                        .GET()
                        .build()
                    val bytes = client.send(fileReq, HttpResponse.BodyHandlers.ofByteArray()).body()
                    File(targetDir, name).writeBytes(bytes)
                    onProgress(name, bytes.size.toLong(), if (size > 0) size else bytes.size.toLong())
                    deps.log.info("Downloaded eval file '$name' (${bytes.size} bytes).")
                } catch (t: Throwable) {
                    deps.log.warn("Failed to download eval file '$name': {}", t.message)
                }
            }
            deps.log.info("Eval results download complete.")
        }
    }

    override suspend fun loadEval(
        path: String,
        modelName: String,
        onProgress: (Int, Int) -> Unit,
    ): String =
        withContext(Dispatchers.IO) {
            val resolvedPath = path.ifBlank { deps.config.dataset.evalResultsDir }
            val stats = deps.evalLoader.loadFromPath(resolvedPath, modelName.ifBlank { null }) { cur, total ->
                onProgress(cur, total)
            }
            "Loaded '${stats.modelName}': ${"%,d".format(stats.inserted)} new, " +
                "${"%,d".format(stats.skipped)} existing, ${"%,d".format(stats.linkedToDataset)} linked, " +
                "${stats.errors} errors"
        }

    private val evalCatalog by lazy { taxonomy.dataset.EvalCatalog(deps.evalStore) }

    override suspend fun scanEvalCatalog(): List<taxonomy.dataset.EvalCatalogEntry> =
        withContext(Dispatchers.IO) {
            evalCatalog.scan(deps.config.dataset.evalResultsDir)
        }

    override suspend fun loadEvalSelected(
        entries: List<taxonomy.dataset.EvalCatalogEntry>,
        onProgress: (modelIdx: Int, modelCount: Int, modelName: String, item: Int, itemTotal: Int) -> Unit
    ) {
        withContext(Dispatchers.IO) {
            deps.log.info("Ingesting ${entries.size} selected eval model(s): ${entries.joinToString { it.modelName }}")
            deps.evalLoader.loadEntries(
                entries,
                onModelStart = { idx, count, model -> onProgress(idx, count, model, 0, 0) },
                onItemProgress = { idx, count, model, cur, total -> onProgress(idx, count, model, cur, total) }
            )
        }
    }

    // ── Settings ─────────────────────────────────────────────────────────────────

    override fun inspectNode(node: GraphNode?) {
        deps.arenaService.inspectNode(node)
    }

    override fun setAnalysisMode(mode: AnalysisMode) {
        deps.arenaService.setMode(mode)
    }

    private val configFacade by lazy { TuiConfigFacade(deps) }

    override fun toggleDomain(domainName: String) {
        configFacade.toggleDomain(domainName, configFacade.getAvailableDomains(forceDataset = true))
    }

    override fun selectAllDomains() {
        deps.config.dataset.selectedDomains =
            configFacade.getAvailableDomains(forceDataset = true).map { it.first }
    }

    override fun clearAllDomains() {
        deps.config.dataset.selectedDomains = emptyList()
    }

    override fun applySetting(name: String, value: String): Boolean =
        configFacade.applySetting(name, value)

    override fun resetBenchmarkReport() {
        deps.arenaService.setBenchmarkReport(null)
    }
}
