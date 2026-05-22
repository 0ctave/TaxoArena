package org.eclipse.lmos.arc.app.taxonomy

import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.snapshots.Snapshot
import ch.qos.logback.classic.spi.ILoggingEvent
import ch.qos.logback.core.AppenderBase
import org.springframework.stereotype.Component

@Component
class TuiLogAppender : AppenderBase<ILoggingEvent>() {

    companion object {
        // GLOBAL STATIC LIST: Accessible by both Logback and Compose
        val logs = mutableStateListOf<String>()
        private const val MAX_LOGS = 200
    }

    override fun append(eventObject: ILoggingEvent) {
        val message = eventObject.formattedMessage ?: return
        
        // Clean up formatting for TUI
        val cleanMsg = message
            .replace(Regex("""\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+\d{2}:\d{2}"""), "")
            .replace(Regex("""\s+INFO \d+ --- \[[^\]]+\] [^\s]+ : """), " » ")
            .trim()

        if (cleanMsg.isNotBlank()) {
            // MUST append in a snapshot-safe way for multi-threaded Logback
            Snapshot.withMutableSnapshot {
                logs.add(cleanMsg)
                if (logs.size > MAX_LOGS) {
                    logs.removeAt(0)
                }
            }
        }
    }
}
