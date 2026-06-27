package taxonomy.tui.state

data class BenchmarkUiState(
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
    val loadedModels: List<String> = emptyList()
)

enum class BenchmarkSubScreen {
    CONFIG,
    RESULTS,
    LOADEVAL,
    MODELSELECT,
    CATEGORYSELECT
}