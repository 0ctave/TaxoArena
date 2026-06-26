package taxonomy.tui.service

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import taxonomy.config.TaxonomyConfig
import taxonomy.model.GraphNode
import taxonomy.service.DagSnapshot
import taxonomy.service.TaxonomyService
import taxonomy.service.TaxonomySnapshotManager
import taxonomy.utils.TaxonomyMetrics
import taxonomy.utils.TuiLogAppender

class TuiSnapshotFacade(
    private val snapshotManager: TaxonomySnapshotManager,
    private val taxonomyService: TaxonomyService,
    private val config: TaxonomyConfig
) {
    suspend fun listSnapshots(): List<DagSnapshot> =
        withContext(Dispatchers.IO) {
            snapshotManager.listSnapshots()
        }

    suspend fun loadSnapshot(snapshotId: String): LoadedSnapshotResult? =
        withContext(Dispatchers.IO) {
            val snapshot = snapshotManager.listSnapshots().firstOrNull { it.id == snapshotId } ?: return@withContext null
            val root = snapshotManager.loadSnapshot(snapshot.id) ?: return@withContext null
            val logs = snapshot.logUuid?.let { snapshotManager.loadSnapshotLogs(it) }.orEmpty()
            LoadedSnapshotResult(
                snapshot = snapshot,
                root = root,
                logs = logs
            )
        }

    suspend fun saveCurrentGraphSnapshot(
        root: GraphNode,
        description: String,
        recordedLogs: List<String> = emptyList()
    ): DagSnapshot = withContext(Dispatchers.IO) {
        snapshotManager.saveSnapshot(root, description, recordedLogs)
    }

    suspend fun deleteSnapshot(snapshotId: String) {
        withContext(Dispatchers.IO) {
            snapshotManager.deleteSnapshot(snapshotId)
        }
    }

    suspend fun renameSnapshot(snapshotId: String, newDescription: String): DagSnapshot? =
        withContext(Dispatchers.IO) {
            val snapshot = snapshotManager.listSnapshots().firstOrNull { it.id == snapshotId } ?: return@withContext null
            val root = snapshotManager.loadSnapshot(snapshot.id) ?: return@withContext null
            val existingLogs = snapshot.logUuid?.let { snapshotManager.loadSnapshotLogs(it) }.orEmpty()
            snapshotManager.deleteSnapshot(snapshotId)
            snapshotManager.saveSnapshot(root, newDescription, existingLogs)
        }

    suspend fun appendLogsToActiveSnapshot(
        activeSnapshotId: String?,
        isViewingSnapshot: Boolean,
        logsToAppend: List<String>
    ) {
        if (!isViewingSnapshot || activeSnapshotId == null || logsToAppend.isEmpty()) return
        withContext(Dispatchers.IO) {
            snapshotManager.appendLogsToSnapshot(activeSnapshotId, logsToAppend)
        }
    }

    suspend fun autoSaveActiveGraph(
        activeSnapshotId: String?,
        isViewingSnapshot: Boolean,
        root: GraphNode
    ) {
        if (!isViewingSnapshot || activeSnapshotId == null) return
        withContext(Dispatchers.IO) {
            snapshotManager.updateSnapshot(activeSnapshotId, root)
        }
    }

    suspend fun applySnapshotToRuntime(loaded: LoadedSnapshotResult) {
        taxonomyService.setGraph(loaded.root)
        config.dataset.selectedDomains = loaded.snapshot.settings.selectedDomains
        config.dataset.datasetType = loaded.snapshot.settings.datasetType
        config.execution.enableLabeling = loaded.snapshot.settings.enableLabeling
        config.execution.enableLiveLabeling = loaded.snapshot.settings.enableLiveLabeling
        config.formalism.maxDepth = loaded.snapshot.settings.maxDepth
        config.formalism.minClusterSize = loaded.snapshot.settings.minClusterSize
        config.formalism.separationEpsilon = loaded.snapshot.settings.separationEpsilon
        config.formalism.cosineTau = loaded.snapshot.settings.cosineTau
        config.formalism.assignmentGap = loaded.snapshot.settings.assignmentGap
        config.formalism.emaAlpha = loaded.snapshot.settings.emaAlpha
        TuiLogAppender.loadHistoricalLogs(loaded.logs)
    }

    suspend fun refreshMetricsForLoadedSnapshot(root: GraphNode) {
        withContext(Dispatchers.Default) {
            taxonomyService.clearMetricsHistory()
            val report = TaxonomyMetrics(root).generateReport()
            taxonomyService.addIterationMetrics(
                "Loaded Snapshot",
                reportToIterationMetrics("Loaded Snapshot", report)
            )
        }
    }

    private fun reportToIterationMetrics(
        label: String,
        r: TaxonomyMetrics.Report
    ) = taxonomy.model.IterationMetrics(
        iteration = label,
        totalNodes = r.totalNodes,
        leafNodes = r.leafNodes,
        crossDomainNodes = r.crossDomainNodes,
        maxDepth = r.maxDepth,
        avgLeafDepth = r.avgLeafDepth,
        medianLeafAssignments = r.medianLeafAssignments,
        totalUniqueQueries = r.totalUniqueQueries,
        residualQueries = r.residualQueries,
        residualRatio = r.residualRatio,
        maxLeafConcentration = r.maxLeafConcentration,
        contaminationRatio = r.contaminationRatio,
        equilibriumIndex = r.equilibriumIndex,
        nmi = r.nmi,
        ari = r.ari,
        dendrogramPurity = r.dendrogramPurity,
        weightedLeafPurity = r.weightedLeafPurity,
        edgeF1 = r.edgeF1,
        sphericalSilhouette = r.sphericalSilhouette,
        ancestorCorrectRate = r.ancestorCorrectRate,
        avgMatchCount = r.avgMatchCount,
        leafDistribEntropy = r.leafDistribEntropy
    )

    data class LoadedSnapshotResult(
        val snapshot: DagSnapshot,
        val root: GraphNode,
        val logs: List<String>
    )
}