package taxonomy.tui.state

data class ProgressUiState(
    val isRegenerating: Boolean = false,

    val generationCurrentIteration: Int = 0,
    val generationTotalIterations: Int = 0,
    val generationPercentComplete: Double = 0.0,
    val generationStep: String = "",
    val generationStatusText: String = "",

    val labelingCurrent: Int = 0,
    val labelingTotal: Int = 0,

    val embeddingCurrent: Int = 0,
    val embeddingTotal: Int = 0
)