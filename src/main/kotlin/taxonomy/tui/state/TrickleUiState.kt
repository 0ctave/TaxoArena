package taxonomy.tui.state

import taxonomy.service.QueryResponseNode
import taxonomy.tui.BatchTrickleTestResults

data class TrickleUiState(
    val isEnteringTrickleQuery: Boolean = false,
    val trickleQueryInput: String = "",

    val trickleResultNodes: List<QueryResponseNode> = emptyList(),
    val isRunningTrickleQuery: Boolean = false,

    val isRunningBatchTrickleTest: Boolean = false,
    val batchTrickleProgress: String = "",
    val batchTrickleResults: BatchTrickleTestResults? = null,
    val isViewingBatchTrickleResults: Boolean = false,
    val batchTrickleScrollOffset: Int = 0
)