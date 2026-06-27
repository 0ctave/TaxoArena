package taxonomy.tui

import taxonomy.tui.components.DashboardHotkeys
import taxonomy.tui.state.FocusPanel
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*

class DashboardHotkeysTest {

    private fun keys(actions: List<taxonomy.tui.components.HotkeyAction>) = actions.map { it.key }

    @Test
    fun hidesAnalysisActionsWhileBuilding() {
        val k = keys(DashboardHotkeys.forState(hasDag = true, FocusPanel.ANALYSIS_HUB, isRegenerating = true))
        assertFalse(k.contains("M"), "Metrics must be hidden while building")
        assertFalse(k.contains("A"))
        assertFalse(k.contains("B"))
        // Globals are emitted by GlobalHotkeys now, not by the contextual builder.
        assertFalse(k.contains("Ctrl-C"))
    }

    @Test
    fun hidesAnalysisActionsWhenNoDag() {
        val k = keys(DashboardHotkeys.forState(hasDag = false, FocusPanel.ANALYSIS_HUB, isRegenerating = false))
        assertFalse(k.contains("M"))
        // When there's no active graph yet, X is surfaced contextually as the primary action.
        assertTrue(k.contains("X"))
    }

    @Test
    fun contextualBuilderNeverEmitsGlobals() {
        // The hub and topology bars (with a DAG present) must not duplicate the global keys.
        val hub = keys(DashboardHotkeys.forState(hasDag = true, FocusPanel.ANALYSIS_HUB, isRegenerating = false))
        val topo = keys(DashboardHotkeys.forState(hasDag = true, FocusPanel.TOPOLOGY, isRegenerating = false))
        for (k in listOf(hub, topo)) {
            assertFalse(k.contains("Tab"), "Tab is global")
            assertFalse(k.contains("Ctrl-C"), "Ctrl-C is global")
            assertFalse(k.contains("X"), "X is global when a DAG is active")
            assertFalse(k.contains("?"), "? is global")
        }
    }

    @Test
    fun showsAnalysisActionsWhenDagReadyAndHubFocused() {
        val k = keys(DashboardHotkeys.forState(hasDag = true, FocusPanel.ANALYSIS_HUB, isRegenerating = false))
        assertTrue(k.contains("M"))
        assertTrue(k.contains("A"))
        assertTrue(k.contains("B"))
        assertTrue(k.contains("T"))
        // Export ASCII and manual Save-Snapshot were removed; N (rename) only shows when viewing.
        assertFalse(k.contains("E"))
        assertFalse(k.contains("N"))
    }

    @Test
    fun showsRenameSnapshotOnlyWhenViewingSnapshot() {
        val viewing = keys(
            DashboardHotkeys.forState(
                hasDag = true, FocusPanel.ANALYSIS_HUB, isRegenerating = false, isViewingSnapshot = true
            )
        )
        assertTrue(viewing.contains("N"))
    }

    @Test
    fun topologyFocusShowsTreeControls() {
        val k = keys(DashboardHotkeys.forState(hasDag = true, FocusPanel.TOPOLOGY, isRegenerating = false))
        assertTrue(k.contains("Space"))
        assertTrue(k.contains("Enter"))
        assertFalse(k.contains("M"), "tree-focus bar shouldn't advertise hub actions")
    }
}
