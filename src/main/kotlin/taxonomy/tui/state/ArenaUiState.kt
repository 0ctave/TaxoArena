package taxonomy.tui.state

data class ArenaUiState(
    val isEnteringArenaQuery: Boolean = false,
    val arenaQueryInput: String = "",

    val isEnteringArenaModelA: Boolean = false,
    val arenaModelAInput: String = "qwen3.5:2b",

    val isEnteringArenaModelB: Boolean = false,
    val arenaModelBInput: String = "ministral:3b-14b"
)