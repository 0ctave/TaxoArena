package org.eclipse.lmos.arc.app

import kotlinx.coroutines.*
import org.eclipse.lmos.arc.app.taxonomy.TaxonomyConfig
import org.eclipse.lmos.arc.app.taxonomy.TaxonomyEngine
import org.eclipse.lmos.arc.app.taxonomy.TaxonomyService
import org.slf4j.LoggerFactory
import org.springframework.boot.CommandLineRunner
import org.springframework.core.annotation.Order
import org.springframework.stereotype.Component

@Component
@Order(1) // Start background tasks FIRST
class TaxoAdaptRunner(
    private val config: TaxonomyConfig,
    private val engine: TaxonomyEngine,
    private val service: TaxonomyService,
    private val datasetFetcher: MMLUDatasetFetcher
) : CommandLineRunner {
    private val log = LoggerFactory.getLogger(TaxoAdaptRunner::class.java)

    // Dedicated scope for app logic that survives the runner's exit
    private val appScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    override fun run(vararg args: String?) {
        log.info("Initializing Arc Engine Background Tasks...")
        
        appScope.launch {
            try {
                // 1. Optional Load (Re-hydration happens in background)
                if (config.persistence.loadPath != null) {
                    log.info("Attempting to load existing graph from ${config.persistence.loadPath}")
                    service.loadGraph(config.persistence.loadPath!!)
                }

                // 2. Optional Batch Evolution
                if (config.runBatch) {
                    runBatchMode()
                }

                // 3. Optional Service Mode
                if (config.startService) {
                    runServiceMode()
                }
            } catch (e: Exception) {
                log.error("Background logic failed", e)
            }
        }
    }

    private suspend fun runBatchMode() {
        val dataset = datasetFetcher.fetchDataset(config.sample)
        val root = engine.adaptTaxonomy("MMLU Universal Knowledge", dataset)
        service.setGraph(root)
        
        config.persistence.savePath?.let {
            log.info("Batch run complete. Saving graph to $it")
            service.saveGraph(it)
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
