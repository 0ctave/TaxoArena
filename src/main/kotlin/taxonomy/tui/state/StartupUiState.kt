package taxonomy.tui.state

import taxonomy.tui.components.StartupState

data class StartupUiState(
    // Start on the LOADING screen; flips to WELCOME once the snapshot list arrives.
    val state: StartupState = StartupState.LOADING,
    val selectedWelcomeIdx: Int = 0,
    val loadingSnapshotId: String? = null
)