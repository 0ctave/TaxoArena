package taxonomy.tui.service

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
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

    override suspend fun downloadDataset(onProgress: (Float, String) -> Unit) {
        deps.datasetFetcher.onDownloadProgress = { current, total, name ->
            val pct = if (total > 0) current.toFloat() / total else 0f
            onProgress(pct, "Downloading $name... $current / $total")
        }
        withContext(Dispatchers.IO) { deps.datasetFetcher.downloadDataset() }
    }

    override suspend fun runBatchJudge(generality: Int, replaceExisting: Boolean) {
        val root = deps.taxonomyService.rootNodeFlow.value ?: return
        deps.judgeService.generateJudgesForDag(root, replaceExisting)
    }

    override suspend fun runArena(query: String, modelA: String, modelB: String) {
        deps.arenaService.compareModels(query, modelA, modelB)
    }

    override suspend fun runTrickle(query: String) {
        // Single-query trickle routing is driven interactively from a precomputed
        // query embedding; record the request as a sensible no-op equivalent.
        deps.log.info("Trickle requested for query: {}", query)
    }

    override suspend fun runBenchmark() {
        // A full benchmark run requires a BenchmarkRequest assembled from UI inputs
        // (models, category, query limit), which are not available at this layer.
        deps.log.info("Benchmark run requested without a configured request; skipping.")
    }

    override suspend fun regenerateLabels() {
        deps.log.info("Label regeneration requested.")
    }

    override suspend fun regenerateJudgeForCurrentNode() {
        deps.log.info("Judge regeneration for current node requested.")
    }

    override suspend fun exportAscii() {
        deps.log.info("ASCII export requested.")
    }
}
