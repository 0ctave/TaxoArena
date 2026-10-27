package taxonomy.utils

import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.snapshots.Snapshot
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

    private val lock = Any()

    // Reactive State: Automatically triggers UI recomposition in Mosaic
    private val _activeSlots = mutableStateMapOf<Int, SlotData>()
    val activeSlots: Map<Int, SlotData> get() = _activeSlots

    private val nextSlot = AtomicInteger(1)

    fun acquireSlot(modelName: String): Int {
        val slot = nextSlot.getAndIncrement()
        synchronized(lock) {
            Snapshot.withMutableSnapshot {
                _activeSlots[slot] = SlotData(modelName)
            }
        }
        return slot
    }

    fun releaseSlot(slot: Int) {
        synchronized(lock) {
            Snapshot.withMutableSnapshot {
                _activeSlots[slot]?.let {
                    _activeSlots[slot] = it.copy(isComplete = true)
                }
            }
        }
    }

    fun updateSlot(slot: Int, delta: String) {
        synchronized(lock) {
            Snapshot.withMutableSnapshot {
                _activeSlots[slot]?.let {
                    _activeSlots[slot] = it.copy(
                        text = (it.text + delta).takeLast(100),
                        tokenCount = it.tokenCount + 1
                    )
                }
            }
        }
    }

    fun removeSlot(slot: Int) {
        synchronized(lock) {
            Snapshot.withMutableSnapshot {
                _activeSlots.remove(slot)
                if (_activeSlots.isEmpty()) nextSlot.set(1)
            }
        }
    }
}
