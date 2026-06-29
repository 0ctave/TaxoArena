package taxonomy.tui.service

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
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
import taxonomy.service.QueryResponseNode
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

                onProgress(0.34f, "Reserving a balanced random test set...")
                val (trainSet, testSet) = deps.datasetFetcher.splitTrainTest(dataset, testRatio = 0.2)
                onProgress(
                    0.36f,
                    "Train ${trainSet.values.sumOf { it.size }} / test ${testSet.values.sumOf { it.size }}"
                )

                val root = deps.taxonomyEngine.adaptTaxonomy(
                    rootLabel = deps.config.dataset.datasetType.name,
                    dataset = trainSet
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
    override suspend fun runBatchJudge(generality: Int, replaceExisting: Boolean) {
        val root = deps.taxonomyService.rootNodeFlow.value ?: return
        withJudgeRecording("Batch judge generation") {
            deps.judgeService.generateJudgesForDag(root, replaceExisting, parallelismOverride = generality)
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
        deps.log.info("Regenerating judge for node '${node.label}'…")
        withJudgeRecording("Single-node judge regeneration for '${node.label}'") {
            deps.judgeService.generateJudgeForNode(node)
        }
        deps.log.info("Judge regenerated for '${node.label}'.")
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
        onLive: (BenchmarkLiveStats) -> Unit
    ) {
        if (models.size < 2) {
            deps.log.warn("Benchmark needs ≥2 models; got ${models.size}")
            return
        }
        val request = BenchmarkRequest(
            models = models.map { ModelSource(it) },
            queryLimit = queryLimit,
            category = category?.takeIf { it.isNotBlank() },
            confidenceGate = confidenceGate,
            parallelism = parallelism.coerceAtLeast(1),
            updateRankings = updateRankings,
            reservedOnly = reservedOnly
        )
        deps.log.info(
            "Starting benchmark: ${models.size} models [${models.joinToString()}] · " +
                "queryLimit=$queryLimit · category=${category ?: "all"} · " +
                "confidenceGate=$confidenceGate · parallelism=$parallelism · updateRankings=$updateRankings"
        )
        deps.arenaService.startBenchmark("Starting benchmark over ${models.size} models…")
        TuiLogAppender.startRecording()
        try {
            val report = deps.benchmarkService.runBenchmark(request) { live ->
                deps.arenaService.updateBenchmarkProgress(
                    "Processed ${live.processed}/${live.total} · " +
                        "agreement ${"%,.2f".format(live.runningAgreement)} · " +
                        "coverage ${"%,.2f".format(live.runningCoverage)}"
                )
                onLive(live)
            }
            deps.arenaService.completeBenchmark(report)
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
            val reservedByDomain: Map<String, List<String>> = try {
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
            val reservedTexts: Set<String> = reservedByDomain.values.flatten().toSet()
            val textToDomain = HashMap<String, String>()
            for ((domain, queries) in fullByDomain) {
                for (q in queries) if (q !in reservedTexts) textToDomain[q] = domain
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
            val poolAll = reservedByDomain
                .flatMap { (domain, queries) -> queries.map { domain to it } }
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
                },
            )
            deps.log.info(
                "Batch trickle complete: ${out.totalQueries} queries · " +
                    "top1 ${"%,.2f".format(out.top1Accuracy)} · any ${"%,.2f".format(out.anyMatchAccuracy)} · " +
                    "macroF1 ${"%,.2f".format(out.macroF1)} · no-match ${"%,.2f".format(out.noMatchRate)}"
            )
            onComplete(out)
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

    override suspend fun downloadEvalResults(onProgress: (String, Long, Long) -> Unit) {
        withContext(Dispatchers.IO) {
            val targetDir = File(deps.config.dataset.evalResultsDir)
            val existing = targetDir.listFiles { f -> f.isFile && f.length() > 0 }
            if (targetDir.isDirectory && existing != null && existing.isNotEmpty()) {
                deps.log.info("Eval results already cached in '${targetDir.path}' (${existing.size} files); skipping download.")
                return@withContext
            }
            targetDir.mkdirs()

            val client = HttpClient.newBuilder().build()
            val listingUrl =
                "https://api.github.com/repos/TIGER-AI-Lab/MMLU-Pro/contents/eval_results"
            deps.log.info("Downloading MMLU-Pro eval_results from GitHub…")

            val listingReq = HttpRequest.newBuilder()
                .uri(URI.create(listingUrl))
                .header("User-Agent", "TaxoArena-TUI")
                .header("Accept", "application/vnd.github.v3+json")
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
        configFacade.toggleDomain(domainName, configFacade.getAvailableDomains())
    }

    override fun applySetting(name: String, value: String): Boolean =
        configFacade.applySetting(name, value)
}
