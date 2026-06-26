package taxonomy.tui.state

data class ArenaUiState(
    // Precomputed-answers mode (no live generation): models + question_id come from
    // the loaded MMLU-Pro eval_results roster rather than hardcoded model names.
    val usePrecomputed: Boolean = true,
    val loadedModels: List<String> = emptyList(),

    val isEnteringArenaQuestionId: Boolean = false,
    val arenaQuestionIdInput: String = "",

    val isEnteringArenaQuery: Boolean = false,
    val arenaQueryInput: String = "",

    val isEnteringArenaModelA: Boolean = false,
    val arenaModelAInput: String = "",

    val isEnteringArenaModelB: Boolean = false,
    val arenaModelBInput: String = ""
)
