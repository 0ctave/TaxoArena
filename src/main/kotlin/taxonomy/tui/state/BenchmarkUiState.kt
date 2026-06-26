package taxonomy.tui.state

data class BenchmarkUiState(
    val selectedBenchmarkField: Int = 0,
    val isEditingBenchmarkField: Boolean = false,
    val benchmarkEditingValue: String = "",
    val benchmarkScrollOffset: Int = 0,

    val isEnteringBenchmarkConfig: Boolean = false,

    val benchmarkModelsInput: String = "qwen3.5:2b, ministral:3b-14b",
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
    val evalDbPathExists: Boolean = false
)

enum class BenchmarkSubScreen {
    CONFIG,
    RESULTS,
    LOADEVAL,
    MODELSELECT,
    CATEGORYSELECT
}