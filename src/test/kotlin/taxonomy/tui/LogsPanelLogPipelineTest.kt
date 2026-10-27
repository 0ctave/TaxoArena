package taxonomy.tui

import ch.qos.logback.classic.Level
import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.LoggerContext
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.slf4j.LoggerFactory
import taxonomy.utils.TuiLogAppender

/**
 * Regression guard for the log pipeline: INFO events emitted on a `taxonomy.*` logger must land
 * in [TuiLogAppender.logs] synchronously on the logging thread. Before PR #51 the appender only
 * enqueued to a side queue that a Compose `LaunchedEffect` drained, so logs never surfaced in a
 * non-UI context (and stalled in the TUI whenever generation saturated the main dispatcher).
 */
class LogsPanelLogPipelineTest {

    @Test
    fun infoLogsLandInTuiAppenderBuffer() {
        val ctx = LoggerFactory.getILoggerFactory() as LoggerContext
        val root = ctx.getLogger(Logger.ROOT_LOGGER_NAME)

        // Attach a fresh TUI appender exactly like LogbackConfigurator does in TUI mode.
        val appender = TuiLogAppender()
        appender.context = ctx
        appender.name = "TUI"
        appender.start()
        root.addAppender(appender)
        root.level = Level.INFO

        val before = TuiLogAppender.logs.size
        try {
            val log = LoggerFactory.getLogger("taxonomy.test")
            repeat(10) { i -> log.info("pipeline probe $i") }

            val delta = TuiLogAppender.logs.size - before
            assertTrue(delta >= 10, "expected >= 10 new lines in TuiLogAppender.logs, saw $delta")
            assertTrue(
                TuiLogAppender.diagnostics().appenderAttached,
                "diagnostics() should report the TUI appender attached",
            )
        } finally {
            root.detachAppender("TUI")
        }
    }
}
