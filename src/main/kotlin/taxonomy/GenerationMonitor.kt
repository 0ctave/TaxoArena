package org.eclipse.lmos.arc.app.taxonomy

import androidx.compose.runtime.mutableStateMapOf
import org.springframework.stereotype.Component
import java.util.concurrent.atomic.AtomicInteger

/**
 * Manages real-time display of parallel LLM generations using Compose state.
 */
@Component
class GenerationMonitor {

    data class SlotData(
        val modelName: String,
        var text: String = "",
        var tokenCount: Int = 0,
        var isComplete: Boolean = false
    )

    // Reactive State: Automatically triggers UI recomposition in Mosaic
    private val _activeSlots = mutableStateMapOf<Int, SlotData>()
    val activeSlots: Map<Int, SlotData> get() = _activeSlots

    private val nextSlot = AtomicInteger(1)

    fun acquireSlot(modelName: String): Int {
        val slot = nextSlot.getAndIncrement()
        _activeSlots[slot] = SlotData(modelName)
        return slot
    }

    fun releaseSlot(slot: Int) {
        _activeSlots[slot]?.let {
            _activeSlots[slot] = it.copy(isComplete = true)
        }
        // Keep it briefly for the UI to show [DONE], then we'll clean up in the TUI service
    }

    fun updateSlot(slot: Int, delta: String) {
        _activeSlots[slot]?.let {
            _activeSlots[slot] = it.copy(
                text = (it.text + delta).takeLast(100),
                tokenCount = it.tokenCount + 1
            )
        }
    }

    fun removeSlot(slot: Int) {
        _activeSlots.remove(slot)
        if (_activeSlots.isEmpty()) nextSlot.set(1)
    }
}
