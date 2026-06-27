package taxonomy.utils

import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.snapshots.Snapshot
import ch.qos.logback.classic.Level
import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.LoggerContext
import ch.qos.logback.classic.spi.ILoggingEvent
import ch.qos.logback.core.AppenderBase
import org.slf4j.LoggerFactory
import java.time.Instant
import java.util.*
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicReference

/**
 * Logback appender that funnels framework logs into the in-app TUI System Logs panel.
 *
 * NOT a Spring `@Component`: it is constructed exactly once by [LogbackConfigurator] and attached
 * to the root logger. Making it a bean would create a second instance whose [append] never fires
 * (it is never wired into Logback), which historically muddied the diagnostics. The shared buffer
 * and counters live on the companion so the single attached instance and all readers agree.
 */
class TuiLogAppender : AppenderBase<ILoggingEvent>() {

    companion object {
        val logs: MutableList<String> = Collections.synchronizedList(ArrayList<String>())
        val logsVersion = mutableStateOf(0)
        private const val MAX_LOGS = 2000

        // Lifetime instrumentation, written from the logging thread and read by diagnostics().
        // Atomics keep the reads cheap and lock-free; they answer "has the pipeline ever fired?"
        // even when the buffer has since been cleared by a snapshot replay.
        private val appendCounter = AtomicInteger(0)
        private val lastAppendAt = AtomicReference<Instant?>(null)

        /**
         * One-shot health probe for the log pipeline, rendered by [taxonomy.tui.features.logs.LogsPanel]
         * when no lines have appeared yet. Every field answers a distinct "why is the panel empty?"
         * question:
         *  - [infoActive] = the `taxonomy` logger resolves to INFO or finer.
         *  - [appenderAttached] = the TUI appender is wired onto the root logger.
         *  - [attachedAppenderNames] = every appender on the root logger (spots a missing/extra wiring).
         *  - [bufferSize] = current line count in the shared buffer.
         *  - [appendCount] = lifetime appends seen (proves events reached the appender at all).
         *  - [lastAppendAt] = wall-clock of the most recent append (proves recency).
         *  - [loggerContextIdentityHash] = identity of the active LoggerContext (spots a split context).
         */
        data class Diagnostic(
            val infoActive: Boolean,
            val appenderAttached: Boolean,
            val attachedAppenderNames: List<String>,
            val bufferSize: Int,
            val appendCount: Int,
            val lastAppendAt: Instant?,
            val loggerContextIdentityHash: Int,
        )

        fun diagnostics(): Diagnostic {
            val ctx = LoggerFactory.getILoggerFactory() as? LoggerContext
                ?: return Diagnostic(
                    infoActive = false,
                    appenderAttached = false,
                    attachedAppenderNames = emptyList(),
                    bufferSize = logs.size,
                    appendCount = appendCounter.get(),
                    lastAppendAt = lastAppendAt.get(),
                    loggerContextIdentityHash = 0,
                )
            val taxonomyLevel = ctx.getLogger("taxonomy").effectiveLevel
            val infoActive = taxonomyLevel != null && taxonomyLevel.toInt() <= Level.INFO.toInt()
            val rootLogger = ctx.getLogger(Logger.ROOT_LOGGER_NAME)
            val appenderNames = buildList {
                val it = rootLogger.iteratorForAppenders()
                while (it.hasNext()) add(it.next().name ?: "<unnamed>")
            }
            return Diagnostic(
                infoActive = infoActive,
                appenderAttached = rootLogger.getAppender("TUI") != null,
                attachedAppenderNames = appenderNames,
                bufferSize = logs.size,
                appendCount = appendCounter.get(),
                lastAppendAt = lastAppendAt.get(),
                loggerContextIdentityHash = System.identityHashCode(ctx),
            )
        }

        // Session-specific logs recording
        private val sessionLock = Any()
        private var isRecording = false
        private val sessionLogs = ArrayList<String>()

        // The log trace captured during the most recent generation session. saveSnapshot()
        // prefers this over the whole buffer so a snapshot carries exactly the lines produced
        // while building *its* DAG, not unrelated history from earlier in the session.
        private val lastGenerationTraceRef = AtomicReference<List<String>>(emptyList())

        fun startRecording() {
            synchronized(sessionLock) {
                sessionLogs.clear()
                isRecording = true
            }
        }

        fun stopAndGetRecording(): List<String> {
            synchronized(sessionLock) {
                isRecording = false
                val result = sessionLogs.toList()
                sessionLogs.clear()
                return result
            }
        }

        fun isRecording(): Boolean = synchronized(sessionLock) { isRecording }

        /** Stash the trace of the just-finished generation for the next snapshot save to pick up. */
        fun recordGenerationTrace(trace: List<String>) = lastGenerationTraceRef.set(trace)

        /** Trace of the most recent generation session, or empty if none was recorded. */
        fun lastGenerationTrace(): List<String> = lastGenerationTraceRef.get()

        fun loadHistoricalLogs(historicalLogs: List<String>) {
            synchronized(logs) {
                logs.clear()
                logs.addAll(historicalLogs.takeLast(MAX_LOGS))
                logsVersion.value++
            }
            // The buffer was rewritten from an IO coroutine, not the Compose thread; nudge the
            // Recomposer so the panel repaints the replayed trace immediately (see append()).
            notifyCompose()
        }

        /**
         * Push pending snapshot writes to the global Recomposer. [logsVersion] is mutated from
         * Logback's logging thread (a thread Compose never schedules), so without an explicit
         * apply-notification the Recomposer may not observe the write until some other state
         * change happens to flush it. Calling this after every mutation makes log updates land in
         * the panel deterministically rather than depending on an unrelated tick.
         */
        private fun notifyCompose() {
            try {
                Snapshot.sendApplyNotifications()
            } catch (_: Throwable) {
                // Compose runtime may be absent (headless/test) — instrumentation must never throw.
            }
        }
    }

    override fun append(eventObject: ILoggingEvent) {
        val message = eventObject.formattedMessage ?: return

        // Clean up formatting for TUI
        val cleanMsg = message
            .replace(Regex("""\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+\d{2}:\d{2}"""), "")
            .replace(Regex("""\s+INFO \d+ --- \[[^\]]+\] [^\s]+ : """), " » ")
            .trim()

        if (cleanMsg.isNotBlank()) {
            // Prepend the logback level so downstream consumers (e.g. LogsPanel) can
            // reliably colorize lines; the formattedMessage carries no level prefix.
            val taggedMsg = "[${eventObject.level}] $cleanMsg"
            // Append straight onto the shared list and bump the Compose version under the
            // same lock. Logback drives append() from the logging thread, so the buffer must
            // not depend on any UI coroutine to drain it — that pump is starved while DAG
            // generation saturates the main dispatcher, which is exactly when logs vanished.
            synchronized(logs) {
                logs.add(taggedMsg)
                while (logs.size > MAX_LOGS) logs.removeAt(0)
                logsVersion.value++
            }
            appendCounter.incrementAndGet()
            lastAppendAt.set(Instant.now())
            // Notify Compose from this foreign thread so the panel recomposes deterministically.
            notifyCompose()

            // Capture session logs if recording
            synchronized(sessionLock) {
                if (isRecording) {
                    sessionLogs.add(taggedMsg)
                }
            }
        }
    }
}
