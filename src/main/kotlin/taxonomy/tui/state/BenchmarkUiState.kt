package taxonomy.tui.state

import taxonomy.tui.BatchTrickleTestResults

/**
 * Which evaluation the Benchmark hub is showing. [NONE] is the type-selection screen
 * shown whenever the hub is (re)entered.
 */
enum class BenchmarkType {
    NONE,    // Selection screen (entry state)
    ARENA,   // Multi-model pairwise eval over MMLU-Pro
    TRICKLE  // Batch routing accuracy test (moved from the Trickle tab)
}

data class BenchmarkUiState(
    val benchmarkType: BenchmarkType = BenchmarkType.NONE,
    // 0 = ARENA, 1 = TRICKLE (W/S navigation on the selection screen).
    val benchmarkTypeSelectionIndex: Int = 0,

    // Batch routing accuracy test, run under the TRICKLE benchmark type.
    val isRunningBatchTrickleTest: Boolean = false,
    val batchTrickleProgress: String = "",
    val batchTrickleResults: BatchTrickleTestResults? = null,

    val selectedBenchmarkField: Int = 0,
    val isEditingBenchmarkField: Boolean = false,
    val benchmarkEditingValue: String = "",
    val benchmarkScrollOffset: Int = 0,

    val isEnteringBenchmarkConfig: Boolean = false,

    val benchmarkModelsInput: String = "",
    val benchmarkQueryLimitInput: String = "20",
    val benchmarkCategoryInput: String = "",
    val benchmarkConfidenceGateInput: String = "0.65",
    val benchmarkParallelismInput: String = "4",
    val benchmarkUpdateRankingsInput: String = "true",

    // Unused by the panel: BenchmarkPanel gates its display on arenaService's controlState
    // (isRunningBenchmark / benchmarkReport), not this field. Kept to avoid a breaking change.
    val benchmarkSubScreen: BenchmarkSubScreen = BenchmarkSubScreen.CONFIG,

    val evalLoaderFieldIdx: Int = 0,
    val evalLoaderIsEditing: Boolean = false,
    val evalLoaderEditValue: String = "",
    val evalLoaderModelInput: String = "",
    val evalLoaderPathInput: String = "",
    val evalLoaderIsRunning: Boolean = false,
    val evalLoaderStatus: String = "",

    val evalDbTotalRows: Int = 0,
    val evalDbDistinctModels: Int = 0,
    val evalDbPathExists: Boolean = false,

    // Live per-question progress streamed from a running benchmark (null when idle).
    val liveStats: taxonomy.model.BenchmarkLiveStats? = null,

    // Eval-results auto-download progress: file name → fraction complete [0,1].
    val isDownloadingEval: Boolean = false,
    val evalDownloadProgress: Map<String, Float> = emptyMap(),

    // Roster of models currently loaded in the eval_results store.
    val loadedModels: List<String> = emptyList(),

    // ── Per-model eval ingestion picker (the [O] hotkey in Arena/Benchmark) ──
    // The picker lists the eval_results cache and ingests only the selected models, instead of
    // parsing every file in the directory.
    val isPickingEvalCatalog: Boolean = false,
    val evalCatalog: List<taxonomy.dataset.EvalCatalogEntry> = emptyList(),
    val evalCatalogSelection: Set<String> = emptySet(),
    val evalCatalogCursor: Int = 0,

    // Live per-model ingestion progress (modelCount == 0 means "not ingesting").
    val evalLoadingModelIdx: Int = 0,
    val evalLoadingModelCount: Int = 0,
    val evalLoadingCurrentModel: String = "",
    val evalLoadingItem: Int = 0,
    val evalLoadingItemTotal: Int = 0
)

enum class BenchmarkSubScreen {
    CONFIG,
    RESULTS,
    LOADEVAL,
    MODELSELECT,
    CATEGORYSELECT
}