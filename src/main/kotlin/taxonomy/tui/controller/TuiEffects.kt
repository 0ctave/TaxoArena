package taxonomy.tui.controller

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import taxonomy.model.GraphNode
import taxonomy.service.AnalysisMode
import taxonomy.service.DagSnapshot
import taxonomy.service.TaxonomyRankingService.AggregatedLeaderboard

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

    fun runBatchJudge(generality: Int, replaceExisting: Boolean, dispatch: (TuiEvent) -> Unit)
    fun runArena(query: String, modelA: String, modelB: String)
    fun runArenaPrecomputed(questionId: Int, modelA: String, modelB: String)
    fun loadArenaModels(dispatch: (TuiEvent) -> Unit)
    fun runTrickle(query: String, dispatch: (TuiEvent) -> Unit)
    /** @param maxQueries 0 = use full reserved pool, >0 = cap at that many queries. */
    fun runBatchTrickle(maxQueries: Int, dispatch: (TuiEvent) -> Unit)
    /** Resolve the size of the reserved test-query pool (reads reserved_test_queries.json). */
    fun resolveReservedPoolSize(onResolved: (Int) -> Unit)
    fun loadLeaderboard(dispatch: (TuiEvent) -> Unit)
    fun clearLeaderboard(dispatch: (TuiEvent) -> Unit)
    fun downloadEvalResults(dispatch: (TuiEvent) -> Unit)
    fun runBenchmarkConfigured(
        models: List<String>,
        queryLimit: Int,
        category: String?,
        confidenceGate: Double,
        parallelism: Int,
        updateRankings: Boolean,
        reservedOnly: Boolean,
        dispatch: (TuiEvent) -> Unit
    )
    fun loadEval(path: String, modelName: String, dispatch: (TuiEvent) -> Unit)
    /** Scan the eval_results cache (no parsing) and dispatch [TuiEvent.EvalCatalogLoaded]. */
    fun refreshEvalCatalog(dispatch: (TuiEvent) -> Unit)
    /** Ingest only the selected catalog entries, streaming per-model progress. */
    fun loadEvalSelected(entries: List<taxonomy.dataset.EvalCatalogEntry>, dispatch: (TuiEvent) -> Unit)
    fun loadBenchmarkModels(dispatch: (TuiEvent) -> Unit)
    fun regenerateLabels(dispatch: (TuiEvent) -> Unit)
    fun regenerateJudgeForCurrentNode(dispatch: (TuiEvent) -> Unit)
    fun inspectNode(node: GraphNode?)
    fun loadLeaderboardForNode(node: GraphNode, dispatch: (TuiEvent) -> Unit)
    fun loadLeafRanks(dispatch: (TuiEvent) -> Unit)
    fun setAnalysisMode(mode: AnalysisMode)

    /** Toggle a dataset domain on/off, then refresh the settings view. */
    fun toggleDomain(domainName: String, dispatch: (TuiEvent) -> Unit)
    /** Apply a setting value by item name (instant toggle or confirmed editor), then refresh. */
    fun applySetting(name: String, value: String, dispatch: (TuiEvent) -> Unit)
    fun resetBenchmarkReport()
}

class DefaultTuiEffects(
    private val scope: CoroutineScope,
    private val gateway: TuiGateway
) : TuiEffects {

    /** The long-running generation/download/judge job, so it can be cancelled mid-flight. */
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
                loadLeafRanks(dispatch)
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
                val desc = "Auto-saved after generation @ ${java.time.LocalDateTime.now()
                    .truncatedTo(java.time.temporal.ChronoUnit.SECONDS)}"
                try {
                    gateway.saveSnapshot(desc)
                    dispatch(TuiEvent.SnapshotAutoSaved(true, desc))
                    dispatch(TuiEvent.RefreshSnapshots)
                } catch (c: CancellationException) {
                    throw c
                } catch (t: Throwable) {
                    dispatch(TuiEvent.SnapshotAutoSaved(false, t.message ?: "unknown error"))
                }
                dispatch(TuiEvent.IncrementSettingsVersion)
            } catch (c: CancellationException) {
                dispatch(TuiEvent.GenerationFailed("Generation cancelled"))
                throw c
            } catch (t: Throwable) {
                dispatch(TuiEvent.GenerationFailed(t.message ?: "DAG generation failed"))
            }
        }
    }

    // Bug 4 fix: assign the launched coroutine to activeJob so that cancelActiveJob() (Esc/C
    // from the TUI) can interrupt a running batch-judge pass.  Previously this launched on scope
    // without tracking the Job, making cancellation silently ineffective.
    override fun runBatchJudge(generality: Int, replaceExisting: Boolean, dispatch: (TuiEvent) -> Unit) {
        dispatch(TuiEvent.SetJudgeGenerationRunning(true))
        activeJob = scope.launch {
            try {
                gateway.runBatchJudge(generality, replaceExisting)
            } catch (c: CancellationException) {
                throw c
            } catch (t: Throwable) {
                // withJudgeRecording in the gateway already logs the error.
            } finally {
                dispatch(TuiEvent.SetJudgeGenerationRunning(false))
            }
        }
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

    override fun runBatchTrickle(maxQueries: Int, dispatch: (TuiEvent) -> Unit) {
        activeJob = scope.launch {
            try {
                gateway.runBatchTrickle(
                    maxQueries = maxQueries,
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

    override fun resolveReservedPoolSize(onResolved: (Int) -> Unit) {
        scope.launch {
            onResolved(gateway.reservedPoolSize())
        }
    }

    override fun loadLeaderboard(dispatch: (TuiEvent) -> Unit) {
        scope.launch { dispatch(TuiEvent.LeaderboardLoaded(gateway.loadLeaderboard())) }
    }

    override fun clearLeaderboard(dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            gateway.clearLeaderboard()
            dispatch(TuiEvent.LeaderboardLoaded(gateway.loadLeaderboard()))
            loadLeafRanks(dispatch)
        }
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
        reservedOnly: Boolean,
        dispatch: (TuiEvent) -> Unit
    ) {
        scope.launch {
            gateway.runBenchmarkConfigured(
                models, queryLimit, category, confidenceGate, parallelism, updateRankings, reservedOnly
            ) { stats -> dispatch(TuiEvent.BenchmarkLiveUpdate(stats)) }
            loadLeafRanks(dispatch)
        }
    }

    override fun loadEval(path: String, modelName: String, dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            val status = try {
                gateway.loadEval(path, modelName) { cur, total ->
                    dispatch(
                        TuiEvent.SetEvalLoaderStatus(
                            "Parsing ${"%,d".format(cur)} / ${"%,d".format(total)} records…"
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

    override fun refreshEvalCatalog(dispatch: (TuiEvent) -> Unit) {
        scope.launch { dispatch(TuiEvent.EvalCatalogLoaded(gateway.scanEvalCatalog())) }
    }

    override fun loadEvalSelected(
        entries: List<taxonomy.dataset.EvalCatalogEntry>,
        dispatch: (TuiEvent) -> Unit
    ) {
        if (entries.isEmpty()) {
            dispatch(TuiEvent.CloseEvalCatalogPicker)
            return
        }
        activeJob = scope.launch {
            try {
                gateway.loadEvalSelected(entries) { modelIdx, modelCount, modelName, item, itemTotal ->
                    dispatch(
                        TuiEvent.EvalIngestionProgress(modelIdx, modelCount, modelName, item, itemTotal)
                    )
                }
            } catch (c: CancellationException) {
                throw c
            } catch (t: Throwable) {
                dispatch(TuiEvent.SetEvalLoaderStatus("Ingestion failed: ${t.message}"))
            } finally {
                dispatch(TuiEvent.EvalIngestionComplete)
                dispatch(TuiEvent.BenchmarkModelsLoaded(gateway.loadedModels()))
                dispatch(TuiEvent.ArenaModelsLoaded(gateway.loadedModels()))
            }
        }
    }

    override fun loadBenchmarkModels(dispatch: (TuiEvent) -> Unit) {
        scope.launch { dispatch(TuiEvent.BenchmarkModelsLoaded(gateway.loadedModels())) }
    }

    override fun regenerateLabels(dispatch: (TuiEvent) -> Unit) {
        dispatch(TuiEvent.SetJudgeGenerationRunning(true))
        scope.launch {
            try {
                gateway.regenerateLabels()
            } catch (c: CancellationException) {
                throw c
            } catch (t: Throwable) {
                // withJudgeRecording in the gateway already logs the error;
                // catching here prevents a silent coroutine scope crash.
            } finally {
                dispatch(TuiEvent.SetJudgeGenerationRunning(false))
            }
        }
    }

    override fun regenerateJudgeForCurrentNode(dispatch: (TuiEvent) -> Unit) {
        dispatch(TuiEvent.SetJudgeGenerationRunning(true))
        scope.launch {
            try {
                gateway.regenerateJudgeForCurrentNode()
            } catch (c: CancellationException) {
                throw c
            } catch (_: Throwable) {
                // withJudgeRecording in the gateway already logs the error.
            } finally {
                dispatch(TuiEvent.SetGeneratingJudge(false))
                dispatch(TuiEvent.SetJudgeGenerationRunning(false))
            }
        }
    }

    override fun inspectNode(node: GraphNode?) {
        gateway.inspectNode(node)
    }

    override fun loadLeaderboardForNode(node: GraphNode, dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            dispatch(TuiEvent.NodeLeaderboardLoading)
            val leaderboard = gateway.loadLeaderboardForNode(node)
            dispatch(TuiEvent.NodeLeaderboardLoaded(leaderboard))
        }
    }

    override fun loadLeafRanks(dispatch: (TuiEvent) -> Unit) {
        scope.launch {
            val ranks = gateway.loadLeafRanks()
            dispatch(TuiEvent.LeafRanksLoaded(ranks))
        }
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

    override fun resetBenchmarkReport() {
        gateway.resetBenchmarkReport()
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
        maxQueries: Int,
        onProgress: (String) -> Unit,
        onComplete: (taxonomy.tui.BatchTrickleTestResults) -> Unit
    )
    /** Returns the total number of entries in the reserved test-query pool (0 if file absent). */
    suspend fun reservedPoolSize(): Int
    suspend fun loadLeaderboard(): List<taxonomy.service.LeaderboardGroup>
    suspend fun downloadEvalResults(onProgress: (String, Long, Long) -> Unit)
    suspend fun runBenchmarkConfigured(
        models: List<String>,
        queryLimit: Int,
        category: String?,
        confidenceGate: Double,
        parallelism: Int,
        updateRankings: Boolean,
        reservedOnly: Boolean,
        onLive: (taxonomy.model.BenchmarkLiveStats) -> Unit
    )
    suspend fun loadEval(path: String, modelName: String, onProgress: (Int, Int) -> Unit): String
    suspend fun scanEvalCatalog(): List<taxonomy.dataset.EvalCatalogEntry>
    suspend fun loadEvalSelected(
        entries: List<taxonomy.dataset.EvalCatalogEntry>,
        onProgress: (modelIdx: Int, modelCount: Int, modelName: String, item: Int, itemTotal: Int) -> Unit
    )
    suspend fun regenerateLabels()
    suspend fun regenerateJudgeForCurrentNode()
    fun inspectNode(node: GraphNode?)
    fun setAnalysisMode(mode: AnalysisMode)

    fun toggleDomain(domainName: String)
    fun applySetting(name: String, value: String): Boolean
    fun resetBenchmarkReport()
    fun clearLeaderboard()
    suspend fun loadLeaderboardForNode(node: GraphNode): AggregatedLeaderboard
    suspend fun loadLeafRanks(): Map<String, Pair<String, String>>
}
