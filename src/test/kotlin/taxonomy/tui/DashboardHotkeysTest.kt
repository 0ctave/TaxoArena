package taxonomy.tui

import taxonomy.tui.components.DashboardHotkeys
import taxonomy.tui.components.HotkeyGroup
import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.TuiAppState
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*

class DashboardHotkeysTest {

    private fun keys(groups: List<HotkeyGroup>) = groups.flatMap { it.actions }.map { it.key }

    @Test
    fun hidesAnalysisActionsWhileBuilding() {
        val state = TuiAppState()
        val groups = DashboardHotkeys.groups(
            hasDag = true,
            focused = FocusPanel.ANALYSIS_HUB,
            isRegenerating = true,
            state = state
        )
        val k = keys(groups)
        assertFalse(k.contains("M"), "Metrics must be hidden while building")
        assertFalse(k.contains("A"))
        assertFalse(k.contains("B"))
        // Globals are emitted by GlobalHotkeys and included in groups.
        assertTrue(k.contains("Ctrl-C"), "Globals should be included in groups output")
    }

    @Test
    fun hidesAnalysisActionsWhenNoDag() {
        val state = TuiAppState()
        val groups = DashboardHotkeys.groups(
            hasDag = false,
            focused = FocusPanel.ANALYSIS_HUB,
            isRegenerating = false,
            state = state
        )
        val k = keys(groups)
        assertFalse(k.contains("M"))
        assertTrue(k.contains("X"))
    }

    @Test
    fun groupsContainGlobalsOnce() {
        val state = TuiAppState()
        val groups = DashboardHotkeys.groups(
            hasDag = true,
            focused = FocusPanel.ANALYSIS_HUB,
            isRegenerating = false,
            state = state
        )
        val k = keys(groups)
        assertTrue(k.contains("Tab"))
        assertTrue(k.contains("Ctrl-C"))
        assertTrue(k.contains("?"))
        assertEquals(k.size, k.distinct().size)
    }

    @Test
    fun showsAnalysisActionsWhenDagReady() {
        val state = TuiAppState()
        val groups = DashboardHotkeys.groups(
            hasDag = true,
            focused = FocusPanel.ANALYSIS_HUB,
            isRegenerating = false,
            state = state
        )
        val k = keys(groups)
        assertTrue(k.contains("M"))
        assertTrue(k.contains("A"))
        assertTrue(k.contains("B"))
        assertTrue(k.contains("T"))
        assertFalse(k.contains("N"))
    }

    @Test
    fun showsRenameSnapshotOnlyWhenViewingSnapshot() {
        val state = TuiAppState()
        val viewing = keys(
            DashboardHotkeys.groups(
                hasDag = true,
                focused = FocusPanel.ANALYSIS_HUB,
                isRegenerating = false,
                isViewingSnapshot = true,
                state = state
            )
        )
        assertTrue(viewing.contains("N"))
    }

    @Test
    fun bottomBarIsFixedRegardlessOfFocus() {
        val state = TuiAppState()
        val hub = keys(
            DashboardHotkeys.groups(
                hasDag = true,
                focused = FocusPanel.ANALYSIS_HUB,
                isRegenerating = false,
                state = state
            )
        )
        val topo = keys(
            DashboardHotkeys.groups(
                hasDag = true,
                focused = FocusPanel.TOPOLOGY,
                isRegenerating = false,
                state = state
            )
        )
        assertEquals(hub, topo, "Bottom hotkey bar must be identical across focused panels")
    }
}
