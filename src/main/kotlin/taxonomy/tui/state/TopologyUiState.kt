package taxonomy.tui.state

data class TopologyUiState(
    val showDomainSelector: Boolean = false,

    val selectedListIdx: Int = 0,
    val selectedTreeIdx: Int = 0,

    val scrollOffset: Int = 0,
    val treeScrollOffset: Int = 0,

    val expandedNodes: Map<String, Boolean> = emptyMap(),
    val autoScroll: Boolean = true,
    val leafRanks: Map<String, Pair<String, String>> = emptyMap()
)