package taxonomy.tui

import taxonomy.model.GraphNode
import taxonomy.service.AnalysisMode
import taxonomy.tui.components.StartupState
import taxonomy.tui.controller.TuiController
import taxonomy.tui.controller.TuiEffects
import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.state.AnalysisUiState
import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.ShellState
import taxonomy.tui.state.StartupUiState
import taxonomy.tui.state.TuiAppState
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*

/**
 * Synchronous fake of [TuiEffects]: records the calls relevant to the R-key judge (Fix A) and
 * the dataset-cache re-probe (Fix C). Coroutine-launching effects are replaced with direct,
 * immediate dispatches so the controller's reducer state settles within the test thread.
 */
private class FakeEffects(private val datasetDownloaded: Boolean) : TuiEffects {
    var refreshDatasetStatusCount = 0
    var regenerateJudgeCalled = false
    var generateDagCalled = false
    var inspectedNode: GraphNode? = null

    override fun refreshDatasetStatus(dispatch: (TuiEvent) -> Unit) {
        refreshDatasetStatusCount++
        dispatch(TuiEvent.DatasetStatusLoaded(datasetDownloaded))
    }

    override fun regenerateJudgeForCurrentNode(dispatch: (TuiEvent) -> Unit) {
        regenerateJudgeCalled = true
    }

    override fun generateDag(dispatch: (TuiEvent) -> Unit) {
        generateDagCalled = true
    }

    override fun inspectNode(node: GraphNode?) {
        inspectedNode = node
    }

    // ── Remaining members are inert for these tests ──
    override fun refreshSnapshots(dispatch: (TuiEvent) -> Unit) {}
    override fun loadSnapshot(snapshotId: String, dispatch: (TuiEvent) -> Unit) {}
    override fun saveSnapshot(description: String, dispatch: (TuiEvent) -> Unit) {}
    override fun renameSnapshot(snapshotId: String, newDescription: String, dispatch: (TuiEvent) -> Unit) {}
    override fun deleteSnapshot(snapshotId: String, dispatch: (TuiEvent) -> Unit) {}
    override fun downloadDataset(maxQueries: Int, dispatch: (TuiEvent) -> Unit) {}
    override fun cancelActiveJob() {}
    override fun runBatchJudge(generality: Int, replaceExisting: Boolean, dispatch: (TuiEvent) -> Unit) {}
    override fun runArena(query: String, modelA: String, modelB: String) {}
    override fun runArenaPrecomputed(questionId: Int, modelA: String, modelB: String) {}
    override fun loadArenaModels(dispatch: (TuiEvent) -> Unit) {}
    override fun runTrickle(query: String, dispatch: (TuiEvent) -> Unit) {}
    override fun runBatchTrickle(maxQueries: Int, dispatch: (TuiEvent) -> Unit) {}
    override fun resolveReservedPoolSize(onResolved: (Int) -> Unit) {}
    override fun loadLeaderboard(dispatch: (TuiEvent) -> Unit) {}
    override fun clearLeaderboard(dispatch: (TuiEvent) -> Unit) {}
    override fun downloadEvalResults(dispatch: (TuiEvent) -> Unit) {}
    override fun runBenchmarkConfigured(
        models: List<String>,
        queryLimit: Int,
        category: String?,
        confidenceGate: Double,
        parallelism: Int,
        updateRankings: Boolean,
        reservedOnly: Boolean,
        dispatch: (TuiEvent) -> Unit
    ) {}
    override fun loadEval(path: String, modelName: String, dispatch: (TuiEvent) -> Unit) {}
    override fun refreshEvalCatalog(dispatch: (TuiEvent) -> Unit) {}
    override fun loadEvalSelected(
        entries: List<taxonomy.dataset.EvalCatalogEntry>,
        dispatch: (TuiEvent) -> Unit
    ) {}
    override fun loadBenchmarkModels(dispatch: (TuiEvent) -> Unit) {}
    override fun regenerateLabels(dispatch: (TuiEvent) -> Unit) {}
    override fun setAnalysisMode(mode: AnalysisMode) {}
    override fun loadLeaderboardForNode(node: GraphNode, dispatch: (TuiEvent) -> Unit) {}
    override fun loadLeafRanks(dispatch: (TuiEvent) -> Unit) {}
    override fun toggleDomain(domainName: String, dispatch: (TuiEvent) -> Unit) {}
    override fun applySetting(name: String, value: String, dispatch: (TuiEvent) -> Unit) {}
    override fun resetBenchmarkReport() {}
}

class TuiControllerKeyTest {

    @Test
    fun rKeyInNodeDetailRegeneratesJudge() {
        val fake = FakeEffects(datasetDownloaded = true)
        val controller = TuiController(
            initialState = TuiAppState(
                startup = StartupUiState(state = StartupState.MAINDASHBOARD),
                shell = ShellState(focusedPanel = FocusPanel.ANALYSIS_HUB),
                analysis = AnalysisUiState(mode = AnalysisMode.NODE_DETAIL),
            ),
            effects = fake,
        )

        controller.dispatch(TuiEvent.KeyPressed("r"))

        assertTrue(fake.regenerateJudgeCalled, "R in node-detail must trigger judge regeneration")
        assertTrue(controller.state.value.arena.isGeneratingJudge, "spinner flag must be set")
    }

    @Test
    fun enterConfigReprobesDatasetCacheAndSkipsDownloadPrompt() {
        val fake = FakeEffects(datasetDownloaded = true)
        val controller = TuiController(
            initialState = TuiAppState(startup = StartupUiState(state = StartupState.LOAD_DAG)),
            effects = fake,
        )

        val before = fake.refreshDatasetStatusCount
        controller.dispatch(TuiEvent.EnterConfigSetup)

        assertEquals(before + 1, fake.refreshDatasetStatusCount, "config entry must re-probe the cache")
        assertTrue(controller.state.value.runtime.isDatasetDownloaded, "cache hit should mark dataset present")

        // With the dataset present, R generates straight away instead of opening the download prompt.
        controller.dispatch(TuiEvent.KeyPressed("r"))
        assertTrue(fake.generateDagCalled, "R should generate when the dataset is cached")
        assertFalse(controller.state.value.config.promptingDownloadCount, "download prompt must be bypassed")
    }
}
