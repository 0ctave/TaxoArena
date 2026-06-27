package taxonomy.tui

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.dataset.EvalCatalogEntry
import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.controller.TuiReducer
import taxonomy.tui.state.BenchmarkUiState
import taxonomy.tui.state.TuiAppState

class EvalCatalogPickerReducerTest {

    private val entries = listOf(
        EvalCatalogEntry("FOO", "/x/FOO.zip", 10, alreadyIngested = false),
        EvalCatalogEntry("BAR", "/x/BAR.zip", 20, alreadyIngested = true),
        EvalCatalogEntry("BAZ", "/x/BAZ.zip", 30, alreadyIngested = false),
    )

    private fun loaded(): TuiAppState {
        var s = TuiAppState()
        s = TuiReducer.reduce(s, TuiEvent.OpenEvalCatalogPicker)
        return TuiReducer.reduce(s, TuiEvent.EvalCatalogLoaded(entries))
    }

    @Test
    fun openSetsPickerFlagAndCatalogLoadDefaultSelectsNonIngested() {
        val s = loaded()
        assertTrue(s.benchmark.isPickingEvalCatalog)
        assertEquals(3, s.benchmark.evalCatalog.size)
        assertEquals(setOf("FOO", "BAZ"), s.benchmark.evalCatalogSelection)
    }

    @Test
    fun cursorMoveIsClampedToCatalogBounds() {
        var s = loaded()
        s = TuiReducer.reduce(s, TuiEvent.MoveEvalCatalogCursor(-1))
        assertEquals(0, s.benchmark.evalCatalogCursor)
        s = TuiReducer.reduce(s, TuiEvent.MoveEvalCatalogCursor(5))
        assertEquals(2, s.benchmark.evalCatalogCursor)
    }

    @Test
    fun toggleFlipsSelectionForEntryUnderCursor() {
        var s = loaded() // cursor at 0 → FOO, currently selected
        s = TuiReducer.reduce(s, TuiEvent.ToggleEvalCatalogSelection)
        assertFalse("FOO" in s.benchmark.evalCatalogSelection)
        s = TuiReducer.reduce(s, TuiEvent.ToggleEvalCatalogSelection)
        assertTrue("FOO" in s.benchmark.evalCatalogSelection)
    }

    @Test
    fun selectAllNonIngestedIgnoresIngestedEntries() {
        var s = loaded()
        // Clear selection first by toggling both default-selected entries off.
        s = TuiReducer.reduce(s, TuiEvent.ToggleEvalCatalogSelection) // FOO off
        s = TuiReducer.reduce(s, TuiEvent.SelectAllNonIngestedEntries)
        assertEquals(setOf("FOO", "BAZ"), s.benchmark.evalCatalogSelection)
    }

    @Test
    fun ingestionProgressClosesPickerAndComplete() {
        var s = loaded()
        s = TuiReducer.reduce(s, TuiEvent.EvalIngestionProgress(0, 2, "FOO", 5, 10))
        assertFalse(s.benchmark.isPickingEvalCatalog)
        assertTrue(s.benchmark.evalLoaderIsRunning)
        assertEquals(2, s.benchmark.evalLoadingModelCount)
        assertEquals("FOO", s.benchmark.evalLoadingCurrentModel)

        s = TuiReducer.reduce(s, TuiEvent.EvalIngestionComplete)
        assertFalse(s.benchmark.evalLoaderIsRunning)
        assertEquals(0, s.benchmark.evalLoadingModelCount)
    }

    @Test
    fun closePickerClearsFlag() {
        var s = loaded()
        s = TuiReducer.reduce(s, TuiEvent.CloseEvalCatalogPicker)
        assertFalse(s.benchmark.isPickingEvalCatalog)
    }
}
