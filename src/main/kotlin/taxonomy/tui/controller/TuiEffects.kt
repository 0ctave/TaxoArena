package taxonomy.tui.controller

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch
import taxonomy.service.DagSnapshot

interface TuiEffects {
    fun refreshSnapshots(dispatch: (TuiEvent) -> Unit)
    fun loadSnapshot(snapshotId: String, dispatch: (TuiEvent) -> Unit)
    fun saveSnapshot(description: String, dispatch: (TuiEvent) -> Unit)
    fun renameSnapshot(snapshotId: String, newDescription: String, dispatch: (TuiEvent) -> Unit)
    fun deleteSnapshot(snapshotId: String, dispatch: (TuiEvent) -> Unit)
    fun downloadDataset(dispatch: (TuiEvent) -> Unit)

    fun runBatchJudge(generality: Int, replaceExisting: Boolean)
    fun runArena(query: String, modelA: String, modelB: String)
    fun runTrickle(query: String)
    fun runBenchmark()
    fun regenerateLabels()
    fun regenerateJudgeForCurrentNode()
    fun exportAscii()
}

class DefaultTuiEffects(
    private val scope: CoroutineScope,
    private val gateway: TuiGateway
) : TuiEffects {

    override fun refreshSnapshots(dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            val snapshots = gateway.listSnapshots()
            dispatch(TuiEvent.SnapshotsLoaded(snapshots))
        }
    }

    override fun loadSnapshot(snapshotId: String, dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            val snapshot = gateway.findSnapshot(snapshotId)
            val ok = gateway.loadSnapshot(snapshotId)
            if (ok) {
                dispatch(TuiEvent.SnapshotLoaded(snapshotId, snapshot?.description))
                dispatch(TuiEvent.RefreshSnapshots)
            } else {
                dispatch(TuiEvent.SnapshotLoadFailed(snapshotId))
            }
        }
    }

    override fun saveSnapshot(description: String, dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            gateway.saveSnapshot(description.ifBlank { "Snapshot" })
            dispatch(TuiEvent.CancelSaveSnapshot)
            dispatch(TuiEvent.RefreshSnapshots)
        }
    }

    override fun renameSnapshot(snapshotId: String, newDescription: String, dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            gateway.renameSnapshot(snapshotId, newDescription.ifBlank { "Snapshot" })
            dispatch(TuiEvent.CancelRenameSnapshot)
            dispatch(TuiEvent.RefreshSnapshots)
        }
    }

    override fun deleteSnapshot(snapshotId: String, dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            gateway.deleteSnapshot(snapshotId)
            dispatch(TuiEvent.RefreshSnapshots)
        }
    }

    override fun downloadDataset(dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            try {
                gateway.downloadDataset { progress, text ->
                    dispatch(TuiEvent.DatasetDownloadProgress(progress, text))
                }
                dispatch(TuiEvent.DatasetDownloadCompleted)
                dispatch(TuiEvent.IncrementSettingsVersion)
            } catch (t: Throwable) {
                dispatch(TuiEvent.DatasetDownloadFailed(t.message ?: "Dataset download failed"))
            }
        }
    }

    override fun runBatchJudge(generality: Int, replaceExisting: Boolean) {
        scope.launch { gateway.runBatchJudge(generality, replaceExisting) }
    }

    override fun runArena(query: String, modelA: String, modelB: String) {
        scope.launch { gateway.runArena(query, modelA, modelB) }
    }

    override fun runTrickle(query: String) {
        scope.launch { gateway.runTrickle(query) }
    }

    override fun runBenchmark() {
        scope.launch { gateway.runBenchmark() }
    }

    override fun regenerateLabels() {
        scope.launch { gateway.regenerateLabels() }
    }

    override fun regenerateJudgeForCurrentNode() {
        scope.launch { gateway.regenerateJudgeForCurrentNode() }
    }

    override fun exportAscii() {
        scope.launch { gateway.exportAscii() }
    }
}

interface TuiGateway {
    suspend fun listSnapshots(): List<DagSnapshot>
    suspend fun findSnapshot(snapshotId: String): DagSnapshot?
    suspend fun loadSnapshot(snapshotId: String): Boolean
    suspend fun saveSnapshot(description: String)
    suspend fun renameSnapshot(snapshotId: String, newDescription: String)
    suspend fun deleteSnapshot(snapshotId: String)

    suspend fun downloadDataset(onProgress: (Float, String) -> Unit)

    suspend fun runBatchJudge(generality: Int, replaceExisting: Boolean)
    suspend fun runArena(query: String, modelA: String, modelB: String)
    suspend fun runTrickle(query: String)
    suspend fun runBenchmark()
    suspend fun regenerateLabels()
    suspend fun regenerateJudgeForCurrentNode()
    suspend fun exportAscii()
}