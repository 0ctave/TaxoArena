package taxonomy.tui.state

import taxonomy.service.QueryResponseNode

data class TrickleUiState(
    val isEnteringTrickleQuery: Boolean = false,
    val trickleQueryInput: String = "",

    val trickleResultNodes: List<QueryResponseNode> = emptyList(),
    val isRunningTrickleQuery: Boolean = false
)