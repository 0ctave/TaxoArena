package taxonomy.utils

import ch.qos.logback.classic.LoggerContext
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.slf4j.LoggerFactory

/**
 * Exercises the per-session log partitioning on [TuiLogAppender]: a recording window captures only
 * the lines emitted while it is active, and [TuiLogAppender.loadHistoricalLogs] swaps the live
 * buffer wholesale (the snapshot-replay path) while bumping the Compose version.
 */
class SnapshotLogTracePartitioningTest {

    private val appender: TuiLogAppender =
        TuiLogAppender().apply {
            context = LoggerFactory.getILoggerFactory() as LoggerContext
            name = "TUI-test"
            start()
        }

    /** Drive a line through the real append() path (recording + buffer + version bump). */
    private fun emit(message: String) = appender.doAppend(fakeEvent(message))

    @Test
    fun recordingCapturesOnlyTheLinesEmittedWhileActive() {
        TuiLogAppender.startRecording()
        repeat(5) { i -> emit("recorded line $i") }
        val recorded = TuiLogAppender.stopAndGetRecording()

        // Lines emitted after stop must NOT be captured by the finished recording.
        emit("post-stop line")

        assertEquals(5, recorded.size, "exactly the 5 lines emitted during recording must be returned")
        assertTrue(recorded.all { it.contains("recorded line") }, "recording must not leak unrelated lines")
        assertTrue(recorded.none { it.contains("post-stop") }, "post-stop lines must be excluded")
    }

    @Test
    fun loadHistoricalLogsReplacesBufferAndBumpsVersion() {
        // Seed some live content first so we prove a *replacement*, not an append.
        emit("stale live line")
        val versionBefore = TuiLogAppender.logsVersion.value

        TuiLogAppender.loadHistoricalLogs(listOf("a", "b", "c"))

        val snapshot = synchronized(TuiLogAppender.logs) { ArrayList(TuiLogAppender.logs) }
        assertEquals(listOf("a", "b", "c"), snapshot, "buffer must be replaced by the historical lines")
        assertTrue(
            TuiLogAppender.logsVersion.value > versionBefore,
            "loadHistoricalLogs must bump logsVersion so the panel recomposes",
        )
    }

    /** Minimal ILoggingEvent stub: append() only reads level + formattedMessage. */
    private fun fakeEvent(message: String): ch.qos.logback.classic.spi.ILoggingEvent {
        val event = ch.qos.logback.classic.spi.LoggingEvent()
        event.level = ch.qos.logback.classic.Level.INFO
        event.message = message
        return event
    }
}
