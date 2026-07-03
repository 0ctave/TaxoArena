package taxonomy.tui

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.service.AnalysisMode
import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.controller.TuiReducer
import taxonomy.tui.state.TuiAppState

class BatchSettingsReducerTest {

    @Test
    fun testStartBatchGeneralityInputInitialization() {
        val s0 = TuiAppState()
        val s1 = TuiReducer.reduce(s0, TuiEvent.StartBatchGeneralityInput)

        assertEquals(AnalysisMode.JUDGE_PROGRESS, s1.analysis.mode)
        assertTrue(s1.analysis.isEnteringBatchGenerality)
        assertEquals("0", s1.analysis.batchGeneralityInput)
        assertEquals("", s1.analysis.batchDomainsInput)
        assertEquals(0, s1.analysis.batchSelectedSettingIdx)
        assertFalse(s1.analysis.isEditingBatchSetting)
        assertEquals("", s1.analysis.batchEditingValue)
    }

    @Test
    fun testSettingsNavigationAndEditing() {
        var s = TuiAppState()
        s = TuiReducer.reduce(s, TuiEvent.StartBatchGeneralityInput)

        // Navigate to Target Domains row
        s = TuiReducer.reduce(s, TuiEvent.SetBatchSelectedSettingIdx(1))
        assertEquals(1, s.analysis.batchSelectedSettingIdx)

        // Start editing Target Domains
        s = TuiReducer.reduce(s, TuiEvent.StartEditingBatchSetting("Math, Science"))
        assertTrue(s.analysis.isEditingBatchSetting)
        assertEquals("Math, Science", s.analysis.batchEditingValue)

        // Type/update the value
        s = TuiReducer.reduce(s, TuiEvent.UpdateBatchEditingValue("Math, Science, History"))
        assertEquals("Math, Science, History", s.analysis.batchEditingValue)

        // Confirm edit
        s = TuiReducer.reduce(s, TuiEvent.ConfirmBatchEditingSetting)
        assertFalse(s.analysis.isEditingBatchSetting)
        assertEquals("Math, Science, History", s.analysis.batchDomainsInput)
        assertEquals("", s.analysis.batchEditingValue)

        // Navigate to Max Generality row
        s = TuiReducer.reduce(s, TuiEvent.SetBatchSelectedSettingIdx(0))
        // Start editing Max Generality
        s = TuiReducer.reduce(s, TuiEvent.StartEditingBatchSetting("5"))
        assertTrue(s.analysis.isEditingBatchSetting)

        // Cancel edit
        s = TuiReducer.reduce(s, TuiEvent.CancelBatchEditingSetting)
        assertFalse(s.analysis.isEditingBatchSetting)
        assertEquals("0", s.analysis.batchGeneralityInput) // unchanged
        assertEquals("", s.analysis.batchEditingValue)
    }

    @Test
    fun testSetBatchReplaceExisting() {
        var s = TuiAppState()
        s = TuiReducer.reduce(s, TuiEvent.StartBatchGeneralityInput)

        s = TuiReducer.reduce(s, TuiEvent.SetBatchReplaceExisting(true))
        assertTrue(s.analysis.batchReplaceExisting)

        s = TuiReducer.reduce(s, TuiEvent.SetBatchReplaceExisting(false))
        assertFalse(s.analysis.batchReplaceExisting)
    }

    @Test
    fun testCancelBatchGeneralityInput() {
        var s = TuiAppState()
        s = TuiReducer.reduce(s, TuiEvent.StartBatchGeneralityInput)
        s = TuiReducer.reduce(s, TuiEvent.SetBatchReplaceExisting(true))

        s = TuiReducer.reduce(s, TuiEvent.CancelBatchGeneralityInput)
        assertFalse(s.analysis.isEnteringBatchGenerality)
        assertEquals("0", s.analysis.batchGeneralityInput)
        assertFalse(s.analysis.batchReplaceExisting)
    }
}
