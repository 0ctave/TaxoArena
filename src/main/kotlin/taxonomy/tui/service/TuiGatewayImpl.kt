package taxonomy.tui.service

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import taxonomy.service.DagSnapshot
import taxonomy.tui.app.TuiDependencies
import taxonomy.tui.controller.TuiGateway
import taxonomy.utils.TaxonomyMetrics
import taxonomy.utils.TuiLogAppender

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
        deps.config.dataset.selectedDomains = snapshot.settings.selectedDomains
        deps.config.dataset.datasetType = snapshot.settings.datasetType
        deps.config.execution.enableLabeling = snapshot.settings.enableLabeling
        deps.config.execution.enableLiveLabeling = snapshot.settings.enableLiveLabeling
        deps.config.formalism.maxDepth = snapshot.settings.maxDepth
        deps.config.formalism.minClusterSize = snapshot.settings.minClusterSize
        deps.config.formalism.separationEpsilon = snapshot.settings.separationEpsilon
        deps.config.formalism.cosineTau = snapshot.settings.cosineTau
        deps.config.formalism.assignmentGap = snapshot.settings.assignmentGap
        deps.config.formalism.emaAlpha = snapshot.settings.emaAlpha

        val uuid = snapshot.logUuid
        val historicalLogs = if (uuid != null) {
            withContext(Dispatchers.IO) { deps.snapshotManager.loadSnapshotLogs(uuid) }
        } else emptyList()
        TuiLogAppender.loadHistoricalLogs(historicalLogs)

        deps.taxonomyService.clearMetricsHistory()
        val report = TaxonomyMetrics(root).generateReport()
        deps.taxonomyService.addIterationMetrics("Loaded Snapshot", report)

        return true
    }

    override suspend fun saveSnapshot(description: String) {
        val root = deps.taxonomyService.rootNodeFlow.value ?: return
        withContext(Dispatchers.IO) { deps.snapshotManager.saveSnapshot(root, description) }
    }

    override suspend fun renameSnapshot(snapshotId: String, newDescription: String) =
        withContext(Dispatchers.IO) { deps.snapshotManager.renameSnapshot(snapshotId, newDescription) }

    override suspend fun deleteSnapshot(snapshotId: String) =
        withContext(Dispatchers.IO) { deps.snapshotManager.deleteSnapshot(snapshotId) }

    override suspend fun downloadDataset(onProgress: (Float, String) -> Unit) {
        deps.datasetFetcher.onDownloadProgress { current, total, name ->
            val pct = if (total > 0) current.toFloat() / total else 0f
            onProgress(pct, "Downloading $name... $current / $total")
        }
        withContext(Dispatchers.IO) { deps.datasetFetcher.downloadDataset() }
    }

    override suspend fun runBatchJudge(generality: Int, replaceExisting: Boolean) =
        deps.tuiService.batchJudge(generality, replaceExisting)

    override suspend fun runArena(query: String, modelA: String, modelB: String) =
        deps.arenaService.run(query, modelA, modelB)

    override suspend fun runTrickle(query: String) =
        deps.tuiService.runTrickleTest(query)

    override suspend fun runBenchmark() =
        deps.benchmarkService.run()

    override suspend fun regenerateLabels() =
        deps.tuiService.regenerateLabels()

    override suspend fun regenerateJudgeForCurrentNode() =
        deps.tuiService.regenerateJudgeForCurrentNode()

    override suspend fun exportAscii() =
        deps.tuiService.exportAscii()
}