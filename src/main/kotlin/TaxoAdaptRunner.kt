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
@Order(1) // Start background tasks/loading BEFORE TUI is initialized
class TaxoAdaptRunner(
    private val config: TaxonomyConfig,
    private val engine: TaxonomyEngine,
    private val service: TaxonomyService,
    private val datasetFetcher: MMLUDatasetFetcher,
    private val calibrator: org.eclipse.lmos.arc.app.taxonomy.operations.TaxonomyCalibrator,
    private val validator: org.eclipse.lmos.arc.app.taxonomy.operations.TaxonomyValidator
) : CommandLineRunner {
    private val log = LoggerFactory.getLogger(TaxoAdaptRunner::class.java)

    // Dedicated scope for app logic that survives the runner's exit
    private val appScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    override fun run(vararg args: String?) {
        log.info("Initializing Arc Engine Background Tasks...")
        
        // 1. Optional Load (Re-hydration happens synchronously before other runners start)
        if (config.persistence.loadPath != null) {
            try {
                log.info("Attempting to load existing graph from ${config.persistence.loadPath}")
                service.loadGraph(config.persistence.loadPath!!)
            } catch (e: Exception) {
                log.error("Failed to load existing graph on startup", e)
            }
        }
        
        appScope.launch {
            try {
                // 2. Optional Batch Evolution
                if (config.execution.runBatch) {
                    runBatchMode()
                }

                // 3. Optional Service Mode
                if (config.execution.startService) {
                    runServiceMode()
                } else {
                    log.info("Process complete. Exiting application...")
                    if (System.getProperty("org.gradle.test.worker") == null) {
                        System.exit(0)
                    }
                }
            } catch (e: Exception) {
                log.error("Background logic failed", e)
                if (!config.execution.startService) {
                    if (System.getProperty("org.gradle.test.worker") == null) {
                        System.exit(1)
                    }
                }
            }
        }
    }

    private suspend fun runBatchMode() {
        val rawDataset = datasetFetcher.fetchDataset(selectedDomains = config.dataset.selectedDomains)
        val dataset = if (config.dataset.splitDataset) {
            val (train, _) = datasetFetcher.splitTrainTest(rawDataset, config.dataset.testSplitRatio)
            train
        } else {
            rawDataset
        }
        
        val groundTruthMap = dataset.flatMap { (cat, queries) ->
            queries.map { q -> q to cat }
        }.groupBy({ it.first }, { it.second }).mapValues { it.value.toSet() }

        if (config.execution.calibrate) {
            calibrator.calibrate("MMLU Universal Knowledge", dataset, groundTruthMap)
        } else {
            val root = engine.adaptTaxonomy("MMLU Universal Knowledge", dataset)
            service.setGraph(root)
            
            // Print expanded metrics report with ground-truth contamination tracking
            val metrics = org.eclipse.lmos.arc.app.taxonomy.TaxonomyMetrics(root, groundTruthMap)
            metrics.printReport()

            // Run automated LLM-based evaluation suite
            try {
                validator.validateTaxonomy(root)
            } catch (e: Exception) {
                log.warn("Automated LLM Evaluation Suite failed: ${e.message}")
            }

            config.persistence.savePath?.let {
                log.info("Batch run complete. Saving graph to $it")
                service.saveGraph(it)
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
