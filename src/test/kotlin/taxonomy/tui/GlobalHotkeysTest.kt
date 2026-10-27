package taxonomy.tui

import taxonomy.tui.components.GlobalHotkeys
import taxonomy.tui.state.TuiAppState
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*

class GlobalHotkeysTest {

    private fun keys(state: TuiAppState) = GlobalHotkeys.forState(state).map { it.key }

    @Test
    fun alwaysPresentRegardlessOfGraph() {
        val noGraph = keys(TuiAppState())
        assertTrue(noGraph.contains("Tab"))
        assertTrue(noGraph.contains("?"))
        assertTrue(noGraph.contains("Ctrl-C"))
    }

    @Test
    fun loadDagOnlyWhenGraphActive() {
        val noGraph = TuiAppState()
        assertFalse(keys(noGraph).contains("X"), "X must be hidden when no graph is active")

        val withGraph = noGraph.copy(runtime = noGraph.runtime.copy(hasActiveGraph = true))
        assertTrue(keys(withGraph).contains("X"), "X must appear once a graph is active")
    }
}
