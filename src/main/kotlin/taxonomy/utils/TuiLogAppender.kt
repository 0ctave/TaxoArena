package taxonomy.utils

import androidx.compose.runtime.mutableStateOf
import ch.qos.logback.classic.spi.ILoggingEvent
import ch.qos.logback.core.AppenderBase
import org.springframework.stereotype.Component
import java.util.*
import java.util.concurrent.ConcurrentLinkedQueue

@Component
class TuiLogAppender : AppenderBase<ILoggingEvent>() {

    companion object {
        val logQueue = ConcurrentLinkedQueue<String>()
        val logs: MutableList<String> = Collections.synchronizedList(ArrayList<String>())
        val logsVersion = mutableStateOf(0)
        private const val MAX_LOGS = 2000

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
                logQueue.clear()
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
            logQueue.add(taggedMsg)
            while (logQueue.size > MAX_LOGS) {
                logQueue.poll()
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
