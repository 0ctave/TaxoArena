package org.eclipse.lmos.arc.app.taxonomy

import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.LoggerContext
import ch.qos.logback.classic.encoder.PatternLayoutEncoder
import ch.qos.logback.core.ConsoleAppender
import org.slf4j.LoggerFactory
import org.springframework.context.annotation.Configuration
import jakarta.annotation.PostConstruct

@Configuration
class LogbackConfigurator(private val config: TaxonomyConfig) {
    @PostConstruct
    fun configureLogging() {
        if (!config.execution.enableTui) {
            val context = LoggerFactory.getILoggerFactory() as? LoggerContext ?: return
            val rootLogger = context.getLogger(Logger.ROOT_LOGGER_NAME) as? Logger ?: return
            
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
        }
    }
}
