package taxonomy.tui.state

import taxonomy.service.AnalysisMode

/** Which zone of the redesigned 3-zone METRICS view currently has keyboard focus. */
enum class MetricsZoneFocus { TABLE, DETAIL }

data class AnalysisUiState(
    val mode: AnalysisMode = AnalysisMode.IDLE,
    val inspectorScroll: Int = 0,
    val metricsScrollOffset: Int = 0,
    val lastActiveProcessMode: AnalysisMode? = null,

    // 3-zone METRICS view state.
    /** Selected iteration row in the evolution table. -1 means the Final/last entry. */
    val selectedIterationIndex: Int = -1,
    val metricsZoneFocus: MetricsZoneFocus = MetricsZoneFocus.TABLE,
    val showPerformanceBlock: Boolean = false,
    val detailScrollOffset: Int = 0,

    val isEnteringBatchGenerality: Boolean = false,
    val batchGeneralityInput: String = "1",
    val batchReplaceExisting: Boolean = false
)
