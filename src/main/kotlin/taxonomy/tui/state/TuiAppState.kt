package taxonomy.tui.state

import taxonomy.service.AnalysisMode

data class TuiAppState(
    val shell: ShellState = ShellState(),
    val startup: StartupUiState = StartupUiState(),
    val topology: TopologyUiState = TopologyUiState(),
    val config: ConfigUiState = ConfigUiState(),
    val analysis: AnalysisUiState = AnalysisUiState(),
    val snapshot: SnapshotUiState = SnapshotUiState(),
    val logs: LogsUiState = LogsUiState(),
    val benchmark: BenchmarkUiState = BenchmarkUiState(),
    val arena: ArenaUiState = ArenaUiState(),
    val trickle: TrickleUiState = TrickleUiState(),
    val progress: ProgressUiState = ProgressUiState(),
    val runtime: RuntimeUiState = RuntimeUiState()
)

private fun TuiAppState.withAnalysisMode(mode: AnalysisMode): TuiAppState =
    copy(
        analysis = analysis.copy(mode = mode),
        shell = shell.copy(focusedPanel = FocusPanel.ANALYSIS_HUB)
    )