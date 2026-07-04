package taxonomy.tui

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.model.GraphNode
import taxonomy.service.AnalysisMode
import taxonomy.service.DagSnapshot
import taxonomy.service.TaxonomyRankingService.AggregatedLeaderboard
import taxonomy.tui.controller.DefaultTuiEffects
import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.controller.TuiGateway

/**
 * A gateway that records snapshot saves and otherwise no-ops. Suspend functions never actually
 * suspend, so launching effects on [Dispatchers.Unconfined] runs them to completion inline.
 */
private class RecordingGateway(private val failSave: Boolean = false) : TuiGateway {
    val savedDescriptions = mutableListOf<String>()

    override suspend fun saveSnapshot(description: String) {
        if (failSave) throw RuntimeException("disk full")
        savedDescriptions += description
    }

    override suspend fun generateDag(onProgress: (Float, String) -> Unit) { /* completes immediately */ }

    // ── Everything else is inert ──
    override suspend fun listSnapshots(): List<DagSnapshot> = emptyList()
    override suspend fun findSnapshot(snapshotId: String): DagSnapshot? = null
    override suspend fun loadSnapshot(snapshotId: String): Boolean = false
    override suspend fun renameSnapshot(snapshotId: String, newDescription: String) {}
    override suspend fun deleteSnapshot(snapshotId: String) {}
    override suspend fun isDatasetDownloaded(): Boolean = false
    override suspend fun downloadDataset(maxQueries: Int, onProgress: (Float, String) -> Unit) {}
    override suspend fun runBatchJudge(generality: Int, parallelism: Int, replaceExisting: Boolean) {}
    override suspend fun runArena(query: String, modelA: String, modelB: String) {}
    override suspend fun runArenaPrecomputed(questionId: Int, modelA: String, modelB: String) {}
    override suspend fun loadedModels(): List<String> = emptyList()
    override suspend fun runTrickle(query: String): List<taxonomy.service.QueryResponseNode> = emptyList()
    override suspend fun runBatchTrickle(
        maxQueries: Int,
        onProgress: (String) -> Unit,
        onComplete: (BatchTrickleTestResults) -> Unit
    ) {}
    override suspend fun reservedPoolSize(): Int = 0
    override suspend fun loadLeaderboard(): List<taxonomy.service.LeaderboardGroup> = emptyList()
    override suspend fun downloadEvalResults(onProgress: (String, Long, Long) -> Unit) {}
    override suspend fun runBenchmarkConfigured(
        models: List<String>,
        queryLimit: Int,
        category: String?,
        confidenceGate: Double,
        parallelism: Int,
        updateRankings: Boolean,
        reservedOnly: Boolean,
        onLive: (taxonomy.model.BenchmarkLiveStats) -> Unit
    ) {}
    override suspend fun loadEval(path: String, modelName: String, onProgress: (Int, Int) -> Unit): String = ""
    override suspend fun scanEvalCatalog(): List<taxonomy.dataset.EvalCatalogEntry> = emptyList()
    override suspend fun loadEvalSelected(
        entries: List<taxonomy.dataset.EvalCatalogEntry>,
        onProgress: (modelIdx: Int, modelCount: Int, modelName: String, item: Int, itemTotal: Int) -> Unit
    ) {}
    override suspend fun regenerateLabels() {}
    override suspend fun regenerateJudgeForCurrentNode() {}
    override fun inspectNode(node: GraphNode?) {}
    override fun setAnalysisMode(mode: AnalysisMode) {}
    override fun toggleDomain(domainName: String) {}
    override fun selectAllDomains() {}
    override fun clearAllDomains() {}
    override fun applySetting(name: String, value: String): Boolean = false
    override fun resetBenchmarkReport() {}
    override fun clearLeaderboard() {}
    override suspend fun loadLeaderboardForNode(node: GraphNode): AggregatedLeaderboard =
        AggregatedLeaderboard(emptyList(), 0, 1, 0, false)
    override suspend fun loadLeafRanks(): Map<String, Pair<String, String>> = emptyMap()
}

class AutoSaveSnapshotEffectTest {

    @Test
    fun `generateDag auto-saves a snapshot on completion`() {
        val gateway = RecordingGateway()
        val effects = DefaultTuiEffects(CoroutineScope(Dispatchers.Unconfined), gateway)
        val events = mutableListOf<TuiEvent>()

        effects.generateDag { events += it }

        assertEquals(1, gateway.savedDescriptions.size, "exactly one auto-save after generation")
        assertTrue(gateway.savedDescriptions.single().startsWith("Auto-saved after generation @"))
        assertTrue(events.contains(TuiEvent.GenerationCompleted))
        val autoSaved = events.filterIsInstance<TuiEvent.SnapshotAutoSaved>().single()
        assertTrue(autoSaved.success)
    }

    @Test
    fun `generateDag survives a snapshot save failure`() {
        val gateway = RecordingGateway(failSave = true)
        val effects = DefaultTuiEffects(CoroutineScope(Dispatchers.Unconfined), gateway)
        val events = mutableListOf<TuiEvent>()

        effects.generateDag { events += it }

        // Generation still completes; the failure is reported, not thrown.
        assertTrue(events.contains(TuiEvent.GenerationCompleted))
        val autoSaved = events.filterIsInstance<TuiEvent.SnapshotAutoSaved>().single()
        assertFalse(autoSaved.success)
        assertTrue(events.contains(TuiEvent.IncrementSettingsVersion))
    }
}
