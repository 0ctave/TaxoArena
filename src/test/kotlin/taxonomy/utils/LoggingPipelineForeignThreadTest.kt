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
 * Verifies the Compose-safe recomposition path. Logback drives [TuiLogAppender.append] from its
 * own logging thread — a thread the Compose Recomposer never schedules. The appender therefore
 * calls `Snapshot.sendApplyNotifications()` after each mutation so a `snapshotFlow` observer (the
 * same mechanism the LogsPanel relies on via recomposition) actually sees `logsVersion` change.
 */
class LoggingPipelineForeignThreadTest {

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
}
