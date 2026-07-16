package taxonomy.utils

import androidx.compose.runtime.snapshotFlow
import ch.qos.logback.classic.Level
import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.LoggerContext
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeoutOrNull
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.slf4j.LoggerFactory
import kotlin.concurrent.thread

/**
 * Consolidated test suite for [TuiLogAppender].
 * 
 * Verifies foreign-thread appends, diagnostic reports, and log partitioning/historical logs loading.
 */
class TuiLogAppenderTest {

    private fun freshAppender(ctx: LoggerContext): TuiLogAppender =
        TuiLogAppender().apply {
            context = ctx
            name = "TUI"
            start()
        }

    /** Drive a line through the real append() path (recording + buffer + version bump). */
    private fun emit(appender: TuiLogAppender, message: String) = 
        appender.doAppend(fakeEvent(message))

    private fun fakeEvent(message: String): ch.qos.logback.classic.spi.ILoggingEvent {
        val event = ch.qos.logback.classic.spi.LoggingEvent()
        event.level = Level.INFO
        event.message = message
        return event
    }

    @Test
    fun foreignThreadAppendIsObservedBySnapshotFlow() = runBlocking {
        val ctx = LoggerFactory.getILoggerFactory() as LoggerContext
        val root = ctx.getLogger(Logger.ROOT_LOGGER_NAME)
        val appender = TuiLogAppender().apply {
            context = ctx
            name = "TUI"
            start()
        }
        root.addAppender(appender)
        root.level = Level.INFO
        try {
            val start = TuiLogAppender.logsVersion.value
            val observedBump = CompletableDeferred<Int>()

            val collector = launch(Dispatchers.Default) {
                snapshotFlow { TuiLogAppender.logsVersion.value }
                    .collect { value ->
                        if (value > start && !observedBump.isCompleted) observedBump.complete(value)
                    }
            }

            // Emit from a non-Compose, non-collector thread to mimic Logback's logging thread.
            thread(name = "fake-logback") {
                LoggerFactory.getLogger("taxonomy.foreign.test").info("from foreign thread")
            }

            val seen = withTimeoutOrNull(5_000) { observedBump.await() }
            collector.cancel()

            assertNotNull(
                seen,
                "snapshotFlow collector should observe logsVersion advance after a foreign-thread append",
            )
            assertTrue(seen!! > start, "observed version must be greater than the starting version")
        } finally {
            root.detachAppender("TUI")
        }
    }

    @Test
    fun diagnosticsReportAttachedAppenderAndAppendActivity() {
        val ctx = LoggerFactory.getILoggerFactory() as LoggerContext
        val root = ctx.getLogger(Logger.ROOT_LOGGER_NAME)
        val appender = freshAppender(ctx)
        root.addAppender(appender)
        root.level = Level.INFO
        try {
            val before = TuiLogAppender.diagnostics().appendCount

            LoggerFactory.getLogger("taxonomy.diag.test").info("diagnostic probe")

            val diag = TuiLogAppender.diagnostics()
            assertTrue(diag.appenderAttached, "TUI appender must report as attached")
            assertTrue(diag.attachedAppenderNames.contains("TUI"), "root appender list must include TUI")
            assertTrue(diag.infoActive, "taxonomy logger should be INFO-active under an INFO root")
            assertTrue(diag.appendCount > before, "append counter must advance after an INFO log")
            assertTrue(diag.bufferSize > 0, "buffer must hold the appended line")
            assertNotNull(diag.lastAppendAt, "lastAppendAt must be set once an event lands")
            assertNotEquals(0, diag.loggerContextIdentityHash, "context hash must be populated")
        } finally {
            root.detachAppender("TUI")
        }
    }

    @Test
    fun nonTaxonomyLoggerIsDroppedUnderWarnRoot() {
        val ctx = LoggerFactory.getILoggerFactory() as LoggerContext
        val root = ctx.getLogger(Logger.ROOT_LOGGER_NAME)
        val appender = freshAppender(ctx)
        root.addAppender(appender)
        root.level = Level.WARN
        ctx.getLogger("taxonomy").level = Level.INFO
        try {
            val before = TuiLogAppender.logs.size

            LoggerFactory.getLogger("Engine").info("this must be dropped")
            assertEquals(before, TuiLogAppender.logs.size, "non-taxonomy INFO must be filtered out")

            LoggerFactory.getLogger("taxonomy.Engine").info("this must land")
            assertTrue(TuiLogAppender.logs.size > before, "taxonomy.* INFO must reach the appender")
        } finally {
            root.detachAppender("TUI")
            ctx.getLogger("taxonomy").level = null
            root.level = Level.INFO
        }
    }

    @Test
    fun recordingCapturesOnlyTheLinesEmittedWhileActive() {
        val ctx = LoggerFactory.getILoggerFactory() as LoggerContext
        val appender = freshAppender(ctx)
        TuiLogAppender.startRecording()
        repeat(5) { i -> emit(appender, "recorded line $i") }
        val recorded = TuiLogAppender.stopAndGetRecording()

        emit(appender, "post-stop line")

        assertEquals(5, recorded.size, "exactly the 5 lines emitted during recording must be returned")
        assertTrue(recorded.all { it.contains("recorded line") }, "recording must not leak unrelated lines")
        assertTrue(recorded.none { it.contains("post-stop") }, "post-stop lines must be excluded")
    }

    @Test
    fun loadHistoricalLogsReplacesBufferAndBumpsVersion() {
        val ctx = LoggerFactory.getILoggerFactory() as LoggerContext
        val appender = freshAppender(ctx)
        emit(appender, "stale live line")
        val versionBefore = TuiLogAppender.logsVersion.value

        TuiLogAppender.loadHistoricalLogs(listOf("a", "b", "c"))

        val snapshot = synchronized(TuiLogAppender.logs) { ArrayList(TuiLogAppender.logs) }
        assertEquals(listOf("a", "b", "c"), snapshot, "buffer must be replaced by the historical lines")
        assertTrue(
            TuiLogAppender.logsVersion.value > versionBefore,
            "loadHistoricalLogs must bump logsVersion so the panel recomposes",
        )
    }
}
