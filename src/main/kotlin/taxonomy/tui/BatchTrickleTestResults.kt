package taxonomy.tui

/**
 * Aggregate results of running a batch of trickle-routing tests against the
 * active taxonomy DAG. Held in [taxonomy.tui.state.TrickleUiState] and rendered
 * by the trickle feature panel.
 */
data class BatchTrickleTestResults(
    val totalQueries: Int = 0,
    val overallAccuracy: Double = 0.0,
    val overallAncestorAccuracy: Double = 0.0,
    val leafRate: Double = 0.0,
)
