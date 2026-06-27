package taxonomy.tui.controller

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import taxonomy.model.GraphNode
import taxonomy.service.AnalysisMode
import taxonomy.service.DagSnapshot

interface TuiEffects {
    fun refreshSnapshots(dispatch: (TuiEvent) -> Unit)
    fun loadSnapshot(snapshotId: String, dispatch: (TuiEvent) -> Unit)
    fun saveSnapshot(description: String, dispatch: (TuiEvent) -> Unit)
    fun renameSnapshot(snapshotId: String, newDescription: String, dispatch: (TuiEvent) -> Unit)
    fun deleteSnapshot(snapshotId: String, dispatch: (TuiEvent) -> Unit)
    fun refreshDatasetStatus(dispatch: (TuiEvent) -> Unit)
    fun downloadDataset(maxQueries: Int, dispatch: (TuiEvent) -> Unit)
    fun generateDag(dispatch: (TuiEvent) -> Unit)
    fun cancelActiveJob()

    fun runBatchJudge(generality: Int, replaceExisting: Boolean)
    fun runArena(query: String, modelA: String, modelB: String)
    fun runArenaPrecomputed(questionId: Int, modelA: String, modelB: String)
    fun loadArenaModels(dispatch: (TuiEvent) -> Unit)
    fun runTrickle(query: String, dispatch: (TuiEvent) -> Unit)
    fun runBatchTrickle(dispatch: (TuiEvent) -> Unit)
    fun loadLeaderboard(dispatch: (TuiEvent) -> Unit)
    fun downloadEvalResults(dispatch: (TuiEvent) -> Unit)
    fun runBenchmarkConfigured(
        models: List<String>,
        queryLimit: Int,
        category: String?,
        confidenceGate: Double,
        parallelism: Int,
        updateRankings: Boolean,
        dispatch: (TuiEvent) -> Unit
    )
    fun loadEval(path: String, modelName: String, dispatch: (TuiEvent) -> Unit)
    fun loadBenchmarkModels(dispatch: (TuiEvent) -> Unit)
    fun regenerateLabels()
    fun regenerateJudgeForCurrentNode(dispatch: (TuiEvent) -> Unit)
    fun inspectNode(node: GraphNode?)
    fun setAnalysisMode(mode: AnalysisMode)

    /** Toggle a dataset domain on/off, then refresh the settings view. */
    fun toggleDomain(domainName: String, dispatch: (TuiEvent) -> Unit)
    /** Apply a setting value by item name (instant toggle or confirmed editor), then refresh. */
    fun applySetting(name: String, value: String, dispatch: (TuiEvent) -> Unit)
}

class DefaultTuiEffects(
    private val scope: CoroutineScope,
    private val gateway: TuiGateway
) : TuiEffects {

    /** The long-running generation/download job, so it can be cancelled mid-flight. */
    private var activeJob: Job? = null

    override fun cancelActiveJob() {
        activeJob?.cancel()
        activeJob = null
    }

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

    override fun refreshDatasetStatus(dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            dispatch(TuiEvent.DatasetStatusLoaded(gateway.isDatasetDownloaded()))
        }
    }

    override fun downloadDataset(maxQueries: Int, dispatch: (TuiEvent) -> Unit) {
        activeJob = scope.launch {
            try {
                gateway.downloadDataset(maxQueries) { progress, text ->
                    dispatch(TuiEvent.DatasetDownloadProgress(progress, text))
                }
                dispatch(TuiEvent.DatasetDownloadCompleted)
                dispatch(TuiEvent.IncrementSettingsVersion)
            } catch (c: CancellationException) {
                dispatch(TuiEvent.DatasetDownloadFailed("Download cancelled"))
                throw c
            } catch (t: Throwable) {
                dispatch(TuiEvent.DatasetDownloadFailed(t.message ?: "Dataset download failed"))
            }
        }
    }

    override fun generateDag(dispatch: (TuiEvent) -> Unit) {
        activeJob = scope.launch {
            try {
                gateway.generateDag { progress, text ->
                    dispatch(TuiEvent.GenerationProgress(progress, text))
                }
                dispatch(TuiEvent.GenerationCompleted)
                dispatch(TuiEvent.IncrementSettingsVersion)
            } catch (c: CancellationException) {
                dispatch(TuiEvent.GenerationFailed("Generation cancelled"))
                throw c
            } catch (t: Throwable) {
                dispatch(TuiEvent.GenerationFailed(t.message ?: "DAG generation failed"))
            }
        }
    }

    override fun runBatchJudge(generality: Int, replaceExisting: Boolean) {
        scope.launch { gateway.runBatchJudge(generality, replaceExisting) }
    }

    override fun runArena(query: String, modelA: String, modelB: String) {
        scope.launch { gateway.runArena(query, modelA, modelB) }
    }

    override fun runArenaPrecomputed(questionId: Int, modelA: String, modelB: String) {
        scope.launch { gateway.runArenaPrecomputed(questionId, modelA, modelB) }
    }

    override fun loadArenaModels(dispatch: (TuiEvent) -> Unit) {
        scope.launch { dispatch(TuiEvent.ArenaModelsLoaded(gateway.loadedModels())) }
    }

    override fun runTrickle(query: String, dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            val nodes = gateway.runTrickle(query)
            dispatch(TuiEvent.TrickleResultReceived(nodes))
        }
    }

    override fun runBatchTrickle(dispatch: (TuiEvent) -> Unit) {
        activeJob = scope.launch {
            try {
                gateway.runBatchTrickle(
                    onProgress = { text -> dispatch(TuiEvent.BatchTrickleProgress(text)) },
                    onComplete = { results -> dispatch(TuiEvent.BatchTrickleCompleted(results)) }
                )
            } catch (c: CancellationException) {
                throw c
            } catch (t: Throwable) {
                dispatch(TuiEvent.BatchTrickleProgress("Batch trickle failed: ${t.message}"))
                dispatch(TuiEvent.BatchTrickleCompleted(taxonomy.tui.BatchTrickleTestResults()))
            }
        }
    }

    override fun loadLeaderboard(dispatch: (TuiEvent) -> Unit) {
        scope.launch { dispatch(TuiEvent.LeaderboardLoaded(gateway.loadLeaderboard())) }
    }

    override fun downloadEvalResults(dispatch: (TuiEvent) -> Unit) {
        activeJob = scope.launch {
            try {
                gateway.downloadEvalResults { fileName, downloaded, total ->
                    dispatch(TuiEvent.EvalDownloadProgress(fileName, downloaded, total))
                }
            } catch (c: CancellationException) {
                throw c
            } catch (_: Throwable) {
                // Best-effort; surfaced via logs.
            }
            dispatch(TuiEvent.EvalDownloadComplete)
        }
    }

    override fun runBenchmarkConfigured(
        models: List<String>,
        queryLimit: Int,
        category: String?,
        confidenceGate: Double,
        parallelism: Int,
        updateRankings: Boolean,
        dispatch: (TuiEvent) -> Unit
    ) {
        scope.launch {
            gateway.runBenchmarkConfigured(
                models, queryLimit, category, confidenceGate, parallelism, updateRankings
            ) { stats -> dispatch(TuiEvent.BenchmarkLiveUpdate(stats)) }
        }
    }

    override fun loadEval(path: String, modelName: String, dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            val status = try {
                gateway.loadEval(path, modelName) { cur, total ->
                    dispatch(
                        TuiEvent.SetEvalLoaderStatus(
                            "Parsing ${"%,d".format(cur)} / ${"%,d".format(total)} records\u2026"
                        )
                    )
                }
            } catch (t: Throwable) {
                "Load failed: ${t.message}"
            }
            dispatch(TuiEvent.SetEvalLoaderStatus(status))
            dispatch(TuiEvent.SetEvalLoaderRunning(false))
            dispatch(TuiEvent.BenchmarkModelsLoaded(gateway.loadedModels()))
        }
    }

    override fun loadBenchmarkModels(dispatch: (TuiEvent) -> Unit) {
        scope.launch { dispatch(TuiEvent.BenchmarkModelsLoaded(gateway.loadedModels())) }
    }

    override fun regenerateLabels() {
        scope.launch { gateway.regenerateLabels() }
    }

    override fun regenerateJudgeForCurrentNode(dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            try {
                gateway.regenerateJudgeForCurrentNode()
            } finally {
                dispatch(TuiEvent.SetGeneratingJudge(false))
            }
        }
    }

    override fun inspectNode(node: GraphNode?) {
        gateway.inspectNode(node)
    }

    override fun setAnalysisMode(mode: AnalysisMode) {
        gateway.setAnalysisMode(mode)
    }

    override fun toggleDomain(domainName: String, dispatch: (TuiEvent) -> Unit) {
        gateway.toggleDomain(domainName)
        dispatch(TuiEvent.IncrementSettingsVersion)
    }

    override fun applySetting(name: String, value: String, dispatch: (TuiEvent) -> Unit) {
        gateway.applySetting(name, value)
        dispatch(TuiEvent.IncrementSettingsVersion)
    }
}

interface TuiGateway {
    suspend fun listSnapshots(): List<DagSnapshot>
    suspend fun findSnapshot(snapshotId: String): DagSnapshot?
    suspend fun loadSnapshot(snapshotId: String): Boolean
    suspend fun saveSnapshot(description: String)
    suspend fun renameSnapshot(snapshotId: String, newDescription: String)
    suspend fun deleteSnapshot(snapshotId: String)

    suspend fun isDatasetDownloaded(): Boolean
    suspend fun downloadDataset(maxQueries: Int, onProgress: (Float, String) -> Unit)
    suspend fun generateDag(onProgress: (Float, String) -> Unit)

    suspend fun runBatchJudge(generality: Int, replaceExisting: Boolean)
    suspend fun runArena(query: String, modelA: String, modelB: String)
    suspend fun runArenaPrecomputed(questionId: Int, modelA: String, modelB: String)
    suspend fun loadedModels(): List<String>
    suspend fun runTrickle(query: String): List<taxonomy.service.QueryResponseNode>
    suspend fun runBatchTrickle(
        onProgress: (String) -> Unit,
        onComplete: (taxonomy.tui.BatchTrickleTestResults) -> Unit
    )
    suspend fun loadLeaderboard(): List<taxonomy.service.LeaderboardGroup>
    suspend fun downloadEvalResults(onProgress: (String, Long, Long) -> Unit)
    suspend fun runBenchmarkConfigured(
        models: List<String>,
        queryLimit: Int,
        category: String?,
        confidenceGate: Double,
        parallelism: Int,
        updateRankings: Boolean,
        onLive: (taxonomy.model.BenchmarkLiveStats) -> Unit
    )
    suspend fun loadEval(path: String, modelName: String, onProgress: (Int, Int) -> Unit): String
    suspend fun regenerateLabels()
    suspend fun regenerateJudgeForCurrentNode()
    fun inspectNode(node: GraphNode?)
    fun setAnalysisMode(mode: AnalysisMode)

    fun toggleDomain(domainName: String)
    fun applySetting(name: String, value: String): Boolean
}