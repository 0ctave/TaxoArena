package taxonomy.tui

import taxonomy.tui.app.DashboardLayout
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*

/**
 * Golden geometry tests. These guard the layout math that, if wrong, pushes the header off
 * screen or misaligns mouse clicks — the failure surface we can't see without a live terminal.
 */
class DashboardLayoutTest {

    private val sizes = listOf(80 to 24, 100 to 30, 120 to 40, 140 to 50, 100 to 20)

    @Test
    fun dashboardRegionsFitWithinTerminal() {
        for ((w, h) in sizes) {
            val l = DashboardLayout.dashboard(w, h)
            // Left + gap(1) + right must not exceed terminal width.
            assertTrue(l.dagW + 1 + l.arenaW <= w, "row width overflow at ${w}x$h")
            // Vertical body must fit in the content region (height - shell rows - footer).
            assertTrue(l.topH + l.bottomH <= l.bodyH + 1, "body height overflow at ${w}x$h")
            assertTrue(l.bodyH <= h, "bodyH exceeds height at ${w}x$h")
        }
    }

    @Test
    fun treeFirstRowIsBelowHeaderAndPanelChrome() {
        val l = DashboardLayout.dashboard(100, 30)
        // Header(1) + rule(1) + panel border(1) + inset(1) + column header(1) = first data row 5.
        assertEquals(5, l.treeFirstRowY)
    }

    @Test
    fun treeRowIndexAccountsForScroll() {
        val l = DashboardLayout.dashboard(100, 30)
        // A click on the very first data row with no scroll -> index 0.
        assertEquals(0, DashboardLayout.treeRowIndex(l, l.treeFirstRowY, 0))
        // Clicking above the first row -> -1 (no hit).
        assertEquals(-1, DashboardLayout.treeRowIndex(l, l.treeFirstRowY - 1, 0))
        // Scroll offset shifts the mapping.
        assertEquals(3, DashboardLayout.treeRowIndex(l, l.treeFirstRowY, 3))
    }

    @Test
    fun dashboardRegionSplitsAtDagWidth() {
        val l = DashboardLayout.dashboard(100, 30)
        assertEquals(DashboardLayout.Region.TOPOLOGY, DashboardLayout.dashboardRegion(l, 0))
        assertEquals(DashboardLayout.Region.TOPOLOGY, DashboardLayout.dashboardRegion(l, l.dagW - 1))
        assertEquals(DashboardLayout.Region.ANALYSIS_HUB, DashboardLayout.dashboardRegion(l, l.dagW))
    }

    @Test
    fun configSideSplitsAtLeftWidth() {
        val l = DashboardLayout.config(100, 30)
        assertEquals(DashboardLayout.ConfigSide.DOMAINS, DashboardLayout.configSide(l, 0))
        assertEquals(DashboardLayout.ConfigSide.SETTINGS, DashboardLayout.configSide(l, l.leftW))
    }

    @Test
    fun welcomeMenuIndexMapsCreateThenSnapshots() {
        val l = DashboardLayout.welcome(100, 30)
        assertEquals(-1, DashboardLayout.welcomeMenuIndex(l, l.firstMenuRowY - 1, 3))
        assertEquals(0, DashboardLayout.welcomeMenuIndex(l, l.firstMenuRowY, 3)) // Create new
        assertEquals(1, DashboardLayout.welcomeMenuIndex(l, l.firstMenuRowY + 1, 3)) // snapshot 0
        assertEquals(-1, DashboardLayout.welcomeMenuIndex(l, l.firstMenuRowY + 4, 3)) // past end
    }
}
