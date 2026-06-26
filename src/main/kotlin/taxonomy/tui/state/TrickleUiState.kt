package taxonomy.tui.state

import taxonomy.model.GraphNode
import taxonomy.tui.BatchTrickleTestResults

data class TrickleUiState(
    val isEnteringTrickleQuery: Boolean = false,
    val trickleQueryInput: String = "",

    val trickleResultNodes: List<GraphNode> = emptyList(),

    val isRunningBatchTrickleTest: Boolean = false,
    val batchTrickleProgress: String = "",
    val batchTrickleResults: BatchTrickleTestResults? = null,
    val isViewingBatchTrickleResults: Boolean = false,
    val batchTrickleScrollOffset: Int = 0
)