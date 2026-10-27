package taxonomy.runner

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/** THREAD-CAP (RP07): the printed line's shape on both branches (the fork-level cap is proved by threadCapProbe). */
class ThreadCapTest {
    private val saved = System.getProperty(ThreadCap.PROPERTY)

    @AfterEach
    fun restore() {
        if (saved == null) System.clearProperty(ThreadCap.PROPERTY) else System.setProperty(ThreadCap.PROPERTY, saved)
    }

    private val live get() = Runtime.getRuntime().availableProcessors()

    @Test
    fun absentPropertyReadsNone() {
        System.clearProperty(ThreadCap.PROPERTY)
        assertEquals(
            "[THREAD-CAP] requested=none availableProcessors=$live heapEstimate=n/a budget=6.00GB",
            ThreadCap.line(null, 6_000_000_000L),
        )
    }

    @Test
    fun requestedAndHeapEstimatePrinted() {
        System.setProperty(ThreadCap.PROPERTY, "12")
        assertEquals(
            "[THREAD-CAP] requested=12 availableProcessors=$live heapEstimate=5.00GB budget=5.80GB",
            ThreadCap.line(5_000_000_000L, 5_800_000_000L),
        )
    }
}
