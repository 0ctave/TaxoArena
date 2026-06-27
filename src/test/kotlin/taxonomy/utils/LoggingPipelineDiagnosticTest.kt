package taxonomy.utils

import ch.qos.logback.classic.Level
import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.LoggerContext
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.slf4j.LoggerFactory

/**
 * Guards the extended [TuiLogAppender.diagnostics] surface used by the empty-state overlay.
 *
 * The original "no logs yet" message only reported INFO-active + appender-attached, which could
 * not distinguish "events are filtered at the root level" from "nothing has been logged". The
 * extended diagnostics expose the lifetime append counter, buffer size, attached appender names
 * and the LoggerContext identity so the panel can pinpoint the failure.
 */
class LoggingPipelineDiagnosticTest {

    private fun freshAppender(ctx: LoggerContext): TuiLogAppender =
        TuiLogAppender().apply {
            context = ctx
            name = "TUI"
            start()
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
        // Reproduces the real bug: a logger OUTSIDE the taxonomy.* namespace inherits the WARN
        // root level, so its INFO events never reach the appender. The fix is to name framework
        // loggers under taxonomy.*; this test documents the failure mode the fix avoids.
        val ctx = LoggerFactory.getILoggerFactory() as LoggerContext
        val root = ctx.getLogger(Logger.ROOT_LOGGER_NAME)
        val appender = freshAppender(ctx)
        root.addAppender(appender)
        root.level = Level.WARN
        // Ensure the taxonomy logger itself is INFO, mirroring application.yml.
        ctx.getLogger("taxonomy").level = Level.INFO
        try {
            val before = TuiLogAppender.logs.size

            // A short-named logger ("Engine") is NOT a child of taxonomy -> filtered at WARN.
            LoggerFactory.getLogger("Engine").info("this must be dropped")
            assertEquals(before, TuiLogAppender.logs.size, "non-taxonomy INFO must be filtered out")

            // The same message on a taxonomy.* logger passes the INFO threshold and lands.
            LoggerFactory.getLogger("taxonomy.Engine").info("this must land")
            assertTrue(TuiLogAppender.logs.size > before, "taxonomy.* INFO must reach the appender")
        } finally {
            root.detachAppender("TUI")
            ctx.getLogger("taxonomy").level = null
            root.level = Level.INFO
        }
    }
}
