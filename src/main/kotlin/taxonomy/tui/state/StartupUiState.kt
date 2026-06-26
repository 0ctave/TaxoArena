package taxonomy.tui.state

import taxonomy.tui.components.StartupState

data class StartupUiState(
    val state: StartupState = StartupState.WELCOME,
    val selectedWelcomeIdx: Int = 0,
    val loadingSnapshotId: String? = null
)