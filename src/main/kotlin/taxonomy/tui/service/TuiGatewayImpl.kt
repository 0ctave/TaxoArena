package taxonomy.tui.service

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
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
        // The full effective config travels with the snapshot; legacy snapshots fall back to
        // the partial SnapshotSettings (mapped via toEffectiveConfig). Adding a new config field
        // flows through automatically with no extra wiring here.
        deps.config.applyEffectiveConfig(snapshot.config ?: snapshot.settings.toEffectiveConfig())

        val uuid = snapshot.logUuid
        val fileLogs = if (uuid != null) {
            withContext(Dispatchers.IO) { deps.snapshotManager.loadSnapshotLogs(uuid) }
        } else emptyList()
        // Prefer the external .log file; fall back to the trace carried inside the snapshot
        // object (populated for JSON-migrated snapshots). Replayed lines are tagged so they're
        // visibly distinct from live generation logs in the LogsPanel.
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
        withContext(Dispatchers.IO) { deps.snapshotManager.saveSnapshot(root, description) }
    }

    override suspend fun renameSnapshot(snapshotId: String, newDescription: String) {
        withContext(Dispatchers.IO) { deps.snapshotManager.renameSnapshot(snapshotId, newDescription) }
    }

    override suspend fun deleteSnapshot(snapshotId: String) {
        withContext(Dispatchers.IO) { deps.snapshotManager.deleteSnapshot(snapshotId) }
    }

    override suspend fun isDatasetDownloaded(): Boolean =
        withContext(Dispatchers.IO) { deps.datasetFetcher.isDatasetDownloaded() }

    override suspend fun downloadDataset(maxQueries: Int, onProgress: (Float, String) -> Unit) {
        deps.datasetFetcher.onDownloadProgress = { current, total, name ->
            if (total > 0) {
                onProgress(
                    current.toFloat() / total,
                    "$name \u00b7 ${"%,d".format(current)} / ${"%,d".format(total)} rows"
                )
            } else {
                // Total unknown (full-dataset pull): keep the bar indeterminate (pct 0f) but
                // tick the row count so the status text proves work is happening.
                onProgress(0f, "$name \u00b7 Fetching\u2026 ${"%,d".format(current)} rows")
            }
        }
        // Surface a live status immediately so the panel never sits on a blank indeterminate
        // bar while the first HTTP round-trip to Hugging Face is in flight.
        onProgress(0f, "Connecting to Hugging Face\u2026")
        // maxQueries <= 0 means "full dataset"; the fetcher treats a very large cap as all.
        val cap = if (maxQueries <= 0) Int.MAX_VALUE else maxQueries
        withContext(Dispatchers.IO) { deps.datasetFetcher.downloadDataset(maxQueries = cap) }
    }

    override suspend fun runBatchJudge(generality: Int, replaceExisting: Boolean) {
        val root = deps.taxonomyService.rootNodeFlow.value ?: return
        deps.judgeService.generateJudgesForDag(root, replaceExisting)
    }

    override suspend fun runArena(query: String, modelA: String, modelB: String) {
        deps.arenaService.compareModels(query, modelA, modelB)
    }

    override suspend fun runArenaPrecomputed(questionId: Int, modelA: String, modelB: String) {
        deps.arenaService.compareModelsPrecomputed(questionId, modelA, modelB)
    }

    override suspend fun loadedModels(): List<String> =
        withContext(Dispatchers.IO) { deps.evalStore.getLoadedModels() }

    override suspend fun runTrickle(query: String): List<QueryResponseNode> {
        // Route the query through the live DAG; queryTaxonomy logs the matched lineage,
        // which surfaces in the System Logs panel. The matched nodes are returned so the
        // Trickle panel can render them.
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

    override suspend fun runBatchTrickle(
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

            // 1. Tag every leaf with the dominant domain of its TRAINING queries. The full dataset
            //    comes from the local SQLite cache (no network); subtracting the reserved test texts
            //    yields the train set, from which we build a rawText -> domain index.
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

            // 2. Sample the reserved queries (capped for interactivity) and score routing.
            val sampleCap = 200
            val testQueries = reservedByDomain
                .flatMap { (domain, queries) -> queries.map { domain to it } }
                .shuffled()
                .take(sampleCap)
            if (testQueries.isEmpty()) {
                onProgress("Reserved test set is empty.")
                onComplete(BatchTrickleTestResults())
                return@withContext
            }

            deps.log.info("Batch trickle: routing ${testQueries.size} reserved queries…")
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
                        onProgress("Routing test queries: $processed / $total · running top1 acc=${"%.1f%%".format(runningTop1 * 100)}")
                    }
                },
            )
            deps.log.info(
                "Batch trickle complete: ${out.totalQueries} queries · " +
                    "top1 ${"%.2f".format(out.top1Accuracy)} · any ${"%.2f".format(out.anyMatchAccuracy)} · " +
                    "macroF1 ${"%.2f".format(out.macroF1)} · no-match ${"%.2f".format(out.noMatchRate)}"
            )
            onComplete(out)
        }
    }

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
            // Skip the network round-trip entirely if the cache is already populated.
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

    override suspend fun runBenchmarkConfigured(
        models: List<String>,
        queryLimit: Int,
        category: String?,
        confidenceGate: Double,
        parallelism: Int,
        updateRankings: Boolean,
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
            updateRankings = updateRankings
        )
        deps.log.info(
            "Starting benchmark: ${models.size} models [${models.joinToString()}] · " +
                "queryLimit=$queryLimit · category=${category ?: "all"} · " +
                "confidenceGate=$confidenceGate · parallelism=$parallelism · updateRankings=$updateRankings"
        )
        deps.arenaService.startBenchmark("Starting benchmark over ${models.size} models…")
        try {
            val report = deps.benchmarkService.runBenchmark(request) { live ->
                deps.arenaService.updateBenchmarkProgress(
                    "Processed ${live.processed}/${live.total} · " +
                        "agreement ${"%.2f".format(live.runningAgreement)} · " +
                        "coverage ${"%.2f".format(live.runningCoverage)}"
                )
                onLive(live)
            }
            deps.arenaService.completeBenchmark(report)
            deps.log.info(
                "Benchmark complete: ${report.totalQueries} queries · ${report.totalModelPairs} pairs · " +
                    "coverage ${"%.3f".format(report.coverageRate)} · " +
                    "judge-agreement ${"%.3f".format(report.overallJudgeAccuracyAgreement)}"
            )
        } catch (t: Throwable) {
            deps.log.error("Benchmark failed", t)
            deps.arenaService.updateBenchmarkProgress("Benchmark failed: ${t.message}")
        }
    }

    override suspend fun loadEval(
        path: String,
        modelName: String,
        onProgress: (Int, Int) -> Unit,
    ): String =
        withContext(Dispatchers.IO) {
            // Blank path → the configured eval_results directory (default "eval_results").
            val resolvedPath = path.ifBlank { deps.config.dataset.evalResultsDir }
            val stats = deps.evalLoader.loadFromPath(resolvedPath, modelName.ifBlank { null }) { cur, total ->
                onProgress(cur, total)
            }
            "Loaded '${stats.modelName}': ${"%,d".format(stats.inserted)} new, " +
                "${"%,d".format(stats.skipped)} existing, ${"%,d".format(stats.linkedToDataset)} linked, " +
                "${stats.errors} errors"
        }

    override suspend fun regenerateLabels() {
        val root = deps.taxonomyService.rootNodeFlow.value ?: run {
            deps.log.warn("Regenerate labels: no active DAG.")
            return
        }
        deps.log.info("Regenerating judges for all unlabelled nodes…")
        // judgeService has no label-only entry point; generateJudgesForDag with
        // replaceExisting = false induces judges only for nodes that lack one, which is the
        // closest available "fill in the gaps" operation.
        deps.judgeService.generateJudgesForDag(root, replaceExisting = false)
        deps.log.info("Label regeneration complete.")
    }

    override suspend fun regenerateJudgeForCurrentNode() {
        // The currently inspected node is tracked in the arena service's panel state.
        val node = deps.arenaService.state.value.selectedNode ?: run {
            deps.log.warn("Regenerate judge: no node currently inspected.")
            return
        }
        deps.log.info("Regenerating judge for node '${node.label}'…")
        deps.judgeService.generateJudgeForNode(node)
        deps.log.info("Judge regenerated for '${node.label}'.")
    }

    override fun inspectNode(node: GraphNode?) {
        // Push the selected node into the arena/analysis service state so the Node Inspector
        // panel (which reads controlState.selectedNode) renders it.
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

    override suspend fun generateDag(onProgress: (Float, String) -> Unit) {
        withContext(Dispatchers.IO) {
            // Bracket the whole generation so every framework log line it emits is captured into a
            // per-session trace; saveSnapshot() then persists exactly this slice with the snapshot.
            TuiLogAppender.startRecording()
            try {
            deps.log.info("DAG generation started for dataset '${deps.config.dataset.datasetType.name}'.")
            // 1. Ensure the dataset is present locally (auto-download if missing).
            if (!deps.datasetFetcher.isDatasetDownloaded()) {
                deps.datasetFetcher.onDownloadProgress = { current, total, name ->
                    val pct = if (total > 0) current.toFloat() / total else 0f
                    onProgress(pct * 0.3f, "Downloading $name... $current / $total")
                }
                deps.datasetFetcher.downloadDataset()
            }

            // 2. Fetch the configured dataset / selected domains.
            onProgress(0.32f, "Loading dataset \"${deps.config.dataset.datasetType.name}\"...")
            val dataset = deps.datasetFetcher.fetchDataset(
                selectedDomains = deps.config.dataset.selectedDomains
            )

            // 2b. Domain-stratified RANDOM train/test split. The DAG is built ONLY from the
            //     train set; the held-out test set is written to reserved_test_queries.json so
            //     it is never seen during generation and travels with the snapshot on save.
            onProgress(0.34f, "Reserving a balanced random test set...")
            val (trainSet, testSet) = deps.datasetFetcher.splitTrainTest(dataset, testRatio = 0.2)
            onProgress(
                0.36f,
                "Train ${trainSet.values.sumOf { it.size }} / test ${testSet.values.sumOf { it.size }}"
            )

            // 3. Run the adaptation engine on the TRAIN set only. It streams GenerationProgress
            //    into taxonomyService (surfaced by the Processes panel); then publish the graph.
            val root = deps.taxonomyEngine.adaptTaxonomy(
                rootLabel = deps.config.dataset.datasetType.name,
                dataset = trainSet
            )
            deps.taxonomyService.setGraph(root)
            deps.log.info("DAG generation complete: ${trainSet.values.sumOf { it.size }} train queries processed.")
            } finally {
                TuiLogAppender.recordGenerationTrace(TuiLogAppender.stopAndGetRecording())
            }
        }
    }
}
