package taxonomy.utils

import androidx.compose.runtime.mutableStateOf
import ch.qos.logback.classic.Level
import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.LoggerContext
import ch.qos.logback.classic.spi.ILoggingEvent
import ch.qos.logback.core.AppenderBase
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component
import java.util.*

@Component
class TuiLogAppender : AppenderBase<ILoggingEvent>() {

    companion object {
        val logs: MutableList<String> = Collections.synchronizedList(ArrayList<String>())
        val logsVersion = mutableStateOf(0)
        private const val MAX_LOGS = 2000

        /**
         * One-shot health probe for the log pipeline, rendered by [taxonomy.tui.features.logs.LogsPanel]
         * when no lines have appeared yet. [infoActive] = the `taxonomy` logger resolves to INFO or
         * finer; [appenderAttached] = the TUI appender is wired onto the root logger.
         */
        data class Diagnostic(val infoActive: Boolean, val appenderAttached: Boolean)

        fun diagnostics(): Diagnostic {
            val ctx = LoggerFactory.getILoggerFactory() as? LoggerContext
                ?: return Diagnostic(infoActive = false, appenderAttached = false)
            val taxonomyLevel = ctx.getLogger("taxonomy").effectiveLevel
            val infoActive = taxonomyLevel != null && taxonomyLevel.toInt() <= Level.INFO.toInt()
            val attached = ctx.getLogger(Logger.ROOT_LOGGER_NAME).getAppender("TUI") != null
            return Diagnostic(infoActive = infoActive, appenderAttached = attached)
        }

        // Session-specific logs recording
        private val sessionLock = Any()
        private var isRecording = false
        private val sessionLogs = ArrayList<String>()

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

        fun loadHistoricalLogs(historicalLogs: List<String>) {
            synchronized(logs) {
                logs.clear()
                logs.addAll(historicalLogs.takeLast(MAX_LOGS))
                logsVersion.value++
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

            // Capture session logs if recording
            synchronized(sessionLock) {
                if (isRecording) {
                    sessionLogs.add(taggedMsg)
                }
            }
        }
    }
}
