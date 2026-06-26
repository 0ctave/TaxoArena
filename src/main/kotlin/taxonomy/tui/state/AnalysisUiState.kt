package taxonomy.tui.state

import taxonomy.service.AnalysisMode

data class AnalysisUiState(
    val mode: AnalysisMode = AnalysisMode.IDLE,
    val inspectorScroll: Int = 0,
    val metricsScrollOffset: Int = 0,
    val lastActiveProcessMode: AnalysisMode? = null,

    val isEnteringBatchGenerality: Boolean = false,
    val batchGeneralityInput: String = "1",
    val batchReplaceExisting: Boolean = false
)