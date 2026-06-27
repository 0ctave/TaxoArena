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
        assertTrue(k.contains("Ctrl-C"))
    }

    @Test
    fun hidesAnalysisActionsWhenNoDag() {
        val k = keys(DashboardHotkeys.forState(hasDag = false, FocusPanel.ANALYSIS_HUB, isRegenerating = false))
        assertFalse(k.contains("M"))
        assertTrue(k.contains("X"))
    }

    @Test
    fun showsAnalysisActionsWhenDagReadyAndHubFocused() {
        val k = keys(DashboardHotkeys.forState(hasDag = true, FocusPanel.ANALYSIS_HUB, isRegenerating = false))
        assertTrue(k.contains("M"))
        assertTrue(k.contains("A"))
        assertTrue(k.contains("B"))
        assertTrue(k.contains("T"))
        assertTrue(k.contains("N"))
    }

    @Test
    fun topologyFocusShowsTreeControls() {
        val k = keys(DashboardHotkeys.forState(hasDag = true, FocusPanel.TOPOLOGY, isRegenerating = false))
        assertTrue(k.contains("Space"))
        assertTrue(k.contains("Enter"))
        assertFalse(k.contains("M"), "tree-focus bar shouldn't advertise hub actions")
    }
}
