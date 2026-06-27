package taxonomy.utils

import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.LoggerContext
import ch.qos.logback.classic.encoder.PatternLayoutEncoder
import ch.qos.logback.core.ConsoleAppender
import jakarta.annotation.PostConstruct
import org.slf4j.LoggerFactory
import org.springframework.context.annotation.Configuration
import taxonomy.config.TaxonomyConfig

@Configuration
class LogbackConfigurator(private val config: TaxonomyConfig) {
    @PostConstruct
    fun configureLogging() {
        val context = LoggerFactory.getILoggerFactory() as? LoggerContext ?: return
        val rootLogger = context.getLogger(Logger.ROOT_LOGGER_NAME) as? Logger ?: return

        if (!config.execution.enableTui) {
            if (rootLogger.getAppender("CONSOLE") == null) {
                val consoleAppender = ConsoleAppender<ch.qos.logback.classic.spi.ILoggingEvent>()
                consoleAppender.context = context
                consoleAppender.name = "CONSOLE"

                val encoder = PatternLayoutEncoder()
                encoder.context = context
                encoder.charset = java.nio.charset.StandardCharsets.UTF_8
                encoder.pattern = "%d{HH:mm:ss.SSS} [%-5level] %logger{0} - %msg%n"
                encoder.start()

                consoleAppender.encoder = encoder
                consoleAppender.start()

                rootLogger.addAppender(consoleAppender)
            }
            return
        }

        // TUI mode: route logs into the in-app System Logs panel via TuiLogAppender, and
        // detach the console appender so stdout doesn't corrupt the alternate screen buffer.
        if (rootLogger.getAppender("TUI") == null) {
            val tuiAppender = TuiLogAppender()
            tuiAppender.context = context
            tuiAppender.name = "TUI"
            tuiAppender.start()
            rootLogger.addAppender(tuiAppender)
        }
        rootLogger.detachAppender("CONSOLE")
    }
}
