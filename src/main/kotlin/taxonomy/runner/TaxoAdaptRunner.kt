package taxonomy.runner

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import org.slf4j.LoggerFactory
import org.springframework.boot.CommandLineRunner
import org.springframework.core.annotation.Order
import org.springframework.stereotype.Component
import taxonomy.TaxonomyEngine
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.operations.TaxonomyValidator
import taxonomy.service.TaxonomyService

@Component
@Order(1) // Start background tasks/loading BEFORE TUI is initialized
class TaxoAdaptRunner(
    private val config: TaxonomyConfig,
    private val engine: TaxonomyEngine,
    private val service: TaxonomyService,
    private val datasetFetcher: MMLUDatasetFetcher,
    private val validator: TaxonomyValidator
) : CommandLineRunner {
    private val log = LoggerFactory.getLogger("taxonomy.Runner")

    // Dedicated scope for app logic that survives the runner's exit
    private val appScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    override fun run(vararg args: String?) {
        log.info("Initializing Arc Engine Background Tasks...")

        appScope.launch {
            try {
                // Optional Service Mode
                if (config.execution.startService) {
                    runServiceMode()
                } else if (!config.execution.enableTui) {
                    log.info("Process complete. Exiting application...")
                    if (System.getProperty("org.gradle.test.worker") == null) {
                        System.exit(0)
                    }
                }
            } catch (e: Exception) {
                log.error("Background logic failed", e)
                if (!config.execution.startService && !config.execution.enableTui) {
                    if (System.getProperty("org.gradle.test.worker") == null) {
                        System.exit(1)
                    }
                }
            }
        }
    }

    private fun runServiceMode() {
        if (service.getGraph() == null) {
            log.warn("Service mode started without an existing graph. Waiting for re-hydration or batch completion...")
        } else {
            log.info("Service mode active. REST API is listening for queries.")
        }
    }
}
