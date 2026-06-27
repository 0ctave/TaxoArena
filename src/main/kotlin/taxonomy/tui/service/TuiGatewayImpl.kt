package taxonomy.tui.service

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import taxonomy.model.BenchmarkRequest
import taxonomy.model.GraphNode
import taxonomy.service.AnalysisMode
import taxonomy.model.ModelSource
import taxonomy.service.DagSnapshot
import taxonomy.tui.app.TuiDependencies
import taxonomy.tui.controller.TuiGateway
import taxonomy.utils.TaxonomyMetrics
import taxonomy.utils.TuiLogAppender
import taxonomy.utils.reportToIterationMetrics

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
        val historicalLogs = if (uuid != null) {
            withContext(Dispatchers.IO) { deps.snapshotManager.loadSnapshotLogs(uuid) }
        } else emptyList()
        TuiLogAppender.loadHistoricalLogs(historicalLogs)

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
            val pct = if (total > 0) current.toFloat() / total else 0f
            onProgress(
                pct,
                "$name \u00b7 ${"%,d".format(current)} / ${"%,d".format(total)} rows"
            )
        }
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

    override suspend fun runTrickle(query: String) {
        // Route the query through the live DAG; queryTaxonomy logs the matched lineage,
        // which surfaces in the System Logs panel.
        withContext(Dispatchers.IO) {
            try {
                deps.taxonomyService.queryTaxonomy(query)
            } catch (t: Throwable) {
                deps.log.warn("Trickle routing failed: {}", t.message)
            }
        }
    }

    override suspend fun runBenchmarkConfigured(
        models: List<String>,
        queryLimit: Int,
        category: String?,
        confidenceGate: Double,
        parallelism: Int,
        updateRankings: Boolean
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
        deps.arenaService.startBenchmark("Starting benchmark over ${models.size} models…")
        try {
            val report = deps.benchmarkService.runBenchmark(request) { live ->
                deps.arenaService.updateBenchmarkProgress(
                    "Processed ${live.processed}/${live.total} · " +
                        "agreement ${"%.2f".format(live.runningAgreement)} · " +
                        "coverage ${"%.2f".format(live.runningCoverage)}"
                )
            }
            deps.arenaService.completeBenchmark(report)
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
        deps.log.info("Label regeneration requested.")
    }

    override suspend fun regenerateJudgeForCurrentNode() {
        deps.log.info("Judge regeneration for current node requested.")
    }

    override fun inspectNode(node: GraphNode?) {
        // Push the selected node into the arena/analysis service state so the Node Inspector
        // panel (which reads controlState.selectedNode) renders it.
        deps.arenaService.inspectNode(node)
    }

    override fun setAnalysisMode(mode: AnalysisMode) {
        deps.arenaService.setMode(mode)
    }

    override suspend fun exportAscii() {
        deps.log.info("ASCII export requested.")
    }

    private val configFacade by lazy { TuiConfigFacade(deps) }

    override fun toggleDomain(domainName: String) {
        configFacade.toggleDomain(domainName, configFacade.getAvailableDomains())
    }

    override fun applySetting(name: String, value: String): Boolean =
        configFacade.applySetting(name, value)

    override suspend fun generateDag(onProgress: (Float, String) -> Unit) {
        withContext(Dispatchers.IO) {
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

            // 3. Run the adaptation engine. It streams GenerationProgress into
            //    taxonomyService (surfaced by the Processes panel), then we publish the graph.
            val root = deps.taxonomyEngine.adaptTaxonomy(
                rootLabel = deps.config.dataset.datasetType.name,
                dataset = dataset
            )
            deps.taxonomyService.setGraph(root)
        }
    }
}
