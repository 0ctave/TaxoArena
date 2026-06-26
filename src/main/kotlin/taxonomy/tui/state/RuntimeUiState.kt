package taxonomy.tui.state

data class RuntimeUiState(
    val hasActiveGraph: Boolean = false,
    val graphVersion: Long = 0L,
    val logsVersion: Long = 0L,
    val metricsHistorySize: Int = 0,
    val availableDomainsVersion: Int = 0,
    val isDatasetDownloaded: Boolean = false,
    val isRegenerating: Boolean = false,
    val currentTimeText: String = ""
)