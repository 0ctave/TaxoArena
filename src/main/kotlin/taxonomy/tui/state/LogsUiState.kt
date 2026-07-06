package taxonomy.tui.state

data class LogsUiState(
    val logScrollOffset: Int = 0,
    val processScrollOffset: Int = 0,
    val maxRetainedLines: Int = 2000
)