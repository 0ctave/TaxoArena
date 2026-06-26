package taxonomy.tui.service

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import taxonomy.model.GraphNode
import taxonomy.tui.app.TuiDependencies
import taxonomy.utils.TaxonomyMetrics
import taxonomy.utils.TuiLogAppender
import taxonomy.utils.reportToIterationMetrics

class TuiLifecycleFacade(
    private val deps: TuiDependencies
) {
    suspend fun regenerateTaxonomy(
        selectedDomains: List<String>,
        splitDataset: Boolean,
        testSplitRatio: Double,
        onSnapshotAutoSaved: ((snapshotId: String, description: String) -> Unit)? = null,
        onGraphReady: ((GraphNode) -> Unit)? = null
    ): GraphNode = withContext(Dispatchers.Default) {
        deps.log.info("Starting TUI-triggered taxonomy regeneration")

        deps.taxonomyService.setGraph(null)
        TuiLogAppender.loadHistoricalLogs(emptyList())
        TuiLogAppender.startRecording()

        val rawDataset = deps.datasetFetcher.fetchDataset(selectedDomains = selectedDomains)
        val dataset = if (splitDataset) {
            val (train, _) = deps.datasetFetcher.splitTrainTest(rawDataset, testSplitRatio)
            train
        } else {
            rawDataset
        }

        val root = deps.taxonomyEngine.adaptTaxonomy("MMLU Universal Knowledge", dataset)
        deps.taxonomyService.setGraph(root)
        onGraphReady?.invoke(root)

        try {
            val report = TaxonomyMetrics(root).generateReport()
            deps.taxonomyService.addIterationMetrics(
                "Final",
                reportToIterationMetrics("Final", report)
            )
        } catch (e: Exception) {
            deps.log.warn("Metrics generation after regen failed: ${e.message}")
        }

        try {
            val activeDomains = selectedDomains
            val domainDesc = if (activeDomains.isEmpty()) "All" else "${activeDomains.size} domains"
            val desc = "Generated ($domainDesc)"
            val recordedLogs = TuiLogAppender.stopAndGetRecording()
            val autoSaved = deps.snapshotManager.saveSnapshot(root, desc, recordedLogs)
            deps.log.info("Auto-saved snapshot ${autoSaved.description}")
            onSnapshotAutoSaved?.invoke(autoSaved.id, autoSaved.description)
        } catch (e: Exception) {
            deps.log.error("Failed to auto-save snapshot after regeneration", e)
        }

        root
    }

    suspend fun loadSnapshot(
        snapshotId: String,
        onLoaded: ((root: GraphNode, description: String) -> Unit)? = null
    ): GraphNode? = withContext(Dispatchers.IO) {
        val snap = deps.snapshotManager.listSnapshots().find { it.id == snapshotId } ?: return@withContext null
        val root = deps.snapshotManager.loadSnapshot(snapshotId) ?: return@withContext null

        deps.taxonomyService.setGraph(root)

        try {
            val logUuid = snap.logUuid
            if (logUuid != null) {
                val histLogs = deps.snapshotManager.loadSnapshotLogs(logUuid)
                TuiLogAppender.loadHistoricalLogs(histLogs)
            } else {
                TuiLogAppender.loadHistoricalLogs(emptyList())
            }
        } catch (e: Exception) {
            deps.log.warn("Failed to restore snapshot logs: ${e.message}")
            TuiLogAppender.loadHistoricalLogs(emptyList())
        }

        try {
            deps.taxonomyService.clearMetricsHistory()
            val report = TaxonomyMetrics(root).generateReport()
            deps.taxonomyService.addIterationMetrics(
                "Loaded Snapshot",
                reportToIterationMetrics("Loaded Snapshot", report)
            )
        } catch (e: Exception) {
            deps.log.warn("Failed to generate snapshot metrics after load: ${e.message}")
        }

        onLoaded?.invoke(root, snap.description)
        root
    }

    suspend fun <T> runWithLogRecording(
        activeSnapshotId: String?,
        isViewingSnapshot: Boolean,
        block: suspend () -> T
    ): T {
        TuiLogAppender.startRecording()
        try {
            return block()
        } finally {
            val recorded = TuiLogAppender.stopAndGetRecording()
            if (isViewingSnapshot && activeSnapshotId != null && recorded.isNotEmpty()) {
                deps.snapshotManager.appendLogsToSnapshot(activeSnapshotId, recorded)
            }
        }
    }

    fun autoSaveActiveGraph(
        activeSnapshotId: String?,
        isViewingSnapshot: Boolean,
        root: GraphNode
    ) {
        if (isViewingSnapshot && activeSnapshotId != null) {
            deps.snapshotManager.updateSnapshot(activeSnapshotId, root)
        }
    }
}