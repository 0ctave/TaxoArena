package taxonomy.tui.controller.keys

import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.state.TuiAppState

/**
 * Handles keyboard input on the LOAD_DAG (welcome / snapshot-picker) screen.
 */
internal class WelcomeKeyHandler {

    fun handle(state: TuiAppState, key: String, dispatch: (TuiEvent) -> Unit) {
        val welcomeOptionsCount = 1 + state.snapshot.snapshotList.size

        when (key) {
            "w", "z", "arrowup" -> dispatch(
                TuiEvent.SelectWelcomeIndex(
                    (state.startup.selectedWelcomeIdx - 1 + welcomeOptionsCount) % welcomeOptionsCount
                )
            )

            "s", "arrowdown" -> dispatch(
                TuiEvent.SelectWelcomeIndex(
                    (state.startup.selectedWelcomeIdx + 1) % welcomeOptionsCount
                )
            )

            "d" -> {
                val idx = state.startup.selectedWelcomeIdx - 1
                if (idx in state.snapshot.snapshotList.indices) {
                    dispatch(TuiEvent.RequestDeleteSnapshot(state.snapshot.snapshotList[idx].id))
                }
            }

            "enter" -> {
                if (state.startup.selectedWelcomeIdx == 0) {
                    dispatch(TuiEvent.EnterConfigSetup)
                } else {
                    val snap = state.snapshot.snapshotList
                        .getOrNull(state.startup.selectedWelcomeIdx - 1) ?: return
                    dispatch(TuiEvent.RequestLoadSnapshot(snap.id))
                }
            }

            "escape", "q" -> {
                if (state.snapshot.isViewingSnapshot) {
                    dispatch(TuiEvent.EnterMainDashboard)
                } else {
                    dispatch(TuiEvent.QuitRequested)
                }
            }
        }
    }
}
