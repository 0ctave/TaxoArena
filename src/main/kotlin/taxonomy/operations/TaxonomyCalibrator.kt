package org.eclipse.lmos.arc.app.taxonomy.operations

import org.eclipse.lmos.arc.app.taxonomy.GraphNode
import org.eclipse.lmos.arc.app.taxonomy.TaxonomyConfig
import org.eclipse.lmos.arc.app.taxonomy.TaxonomyEngine
import org.eclipse.lmos.arc.app.taxonomy.TaxonomyMetrics
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service

/**
 * Automates the calibration of physical and trickling hyperparameters (inclusion scaling, thermodynamic tau constraints,
 * and depth decay) over a query validation subset, optimizing the structural equilibrium (Gini) and minimizing residual stagnation.
 */
@Service
class TaxonomyCalibrator(
    private val config: TaxonomyConfig,
    private val engine: TaxonomyEngine
) {
    private val log = LoggerFactory.getLogger(TaxonomyCalibrator::class.java)

    data class CalibrationResult(
        val inclusionScaling: Double,
        val tauFit: Double,
        val depthDecay: Double,
        val loss: Double,
        val report: TaxonomyMetrics.Report
    )

    suspend fun calibrate(
        rootLabel: String,
        dataset: Map<String, List<String>>,
        groundTruthMap: Map<String, Set<String>>
    ): Map<String, Any> {
        log.info("==========================================================")
        log.info("   LAUNCHING AUTOMATED HYPERPARAMETER CALIBRATION")
        log.info("   Tree Equilibrium (Gini Minimization) Enabled")
        log.info("==========================================================")
        
        // Define hyperparameter grid search search space (Optimized targeted space)
        val inclusionGrid = listOf(1.2, 1.5)
        val tauFitGrid = listOf(0.88)
        val depthDecayGrid = listOf(0.08, 0.12)
        
        val results = mutableListOf<CalibrationResult>()
        
        for (inc in inclusionGrid) {
            for (tau in tauFitGrid) {
                for (decay in depthDecayGrid) {
                    // Backup original configuration parameters
                    val backupInc = config.formalism.inclusionScalingFactor
                    val backupTau = config.formalism.tauFit
                    val backupDecay = config.formalism.depthDecayLambda
                    val backupIterations = config.execution.numIterations
                    val backupTui = config.execution.enableTui
                    
                    config.formalism.inclusionScalingFactor = inc
                    config.formalism.tauFit = tau
                    config.formalism.depthDecayLambda = decay
                    config.execution.numIterations = 3 // Fast iterations for calibration runs
                    config.execution.enableTui = false // Avoid TUI layout rendering
                    
                    try {
                        val testRoot = engine.adaptTaxonomy(rootLabel, dataset)
                        val metrics = TaxonomyMetrics(testRoot, groundTruthMap)
                        val report = metrics.generateReport()
                        
                        // Compute Taxonomy Structural Loss (TSL)
                        val normDepth = report.avgLeafDepth / maxOf(1.0, config.formalism.maxDepth.toDouble())
                        
                        // Minimize residuals, minimize generic concentration, maximize Gini leaf equilibrium,
                        // minimize branch cross-contamination, and encourage balanced depth.
                        val tsl = (0.35 * report.residualRatio * report.residualRatio) +
                                  (0.25 * report.maxLeafConcentration * report.maxLeafConcentration) +
                                  (0.20 * (1.0 - report.equilibriumIndex) * (1.0 - report.equilibriumIndex)) +
                                  (0.10 * report.contaminationRatio * report.contaminationRatio) +
                                  (0.10 * (1.0 - normDepth) * (1.0 - normDepth))
                        
                        results.add(CalibrationResult(inc, tau, decay, tsl, report))
                        
                        log.info("  - Grid: inc=$inc, tau=$tau, decay=$decay -> Loss=${"%.4f".format(java.util.Locale.US, tsl)} " +
                                 "(Res: ${"%.1f%%".format(java.util.Locale.US, report.residualRatio * 100.0)}, " +
                                 "Equil: ${"%.1f%%".format(java.util.Locale.US, report.equilibriumIndex * 100.0)}, " +
                                 "Contam: ${"%.1f%%".format(java.util.Locale.US, report.contaminationRatio * 100.0)})")
                    } catch (e: Exception) {
                        log.warn("Calibration candidate inc=$inc, tau=$tau, decay=$decay failed: ${e.message}")
                    } finally {
                        // Restore original configuration parameters
                        config.formalism.inclusionScalingFactor = backupInc
                        config.formalism.tauFit = backupTau
                        config.formalism.depthDecayLambda = backupDecay
                        config.execution.numIterations = backupIterations
                        config.execution.enableTui = backupTui
                    }
                }
            }
        }
        
        val best = results.minByOrNull { it.loss }
        if (best != null) {
            log.info("\n==========================================================\n" +
                     "             CALIBRATION MATRIX SEARCH RESULTS\n" +
                     "==========================================================\n" +
                     "Optimal Hyperparameters Identified:\n" +
                     "  - inclusionScalingFactor: ${best.inclusionScaling}\n" +
                     "  - tauFit:                 ${best.tauFit}\n" +
                     "  - depthDecayLambda:       ${best.depthDecay}\n" +
                     "\n" +
                     "Resulting Diagnostics:\n" +
                     "  - Minimal Taxonomy Loss:  ${"%.4f".format(java.util.Locale.US, best.loss)}\n" +
                     "  - Tree Equilibrium Index: ${"%.2f%%".format(java.util.Locale.US, best.report.equilibriumIndex * 100.0)}\n" +
                     "  - Residual Stagnation:    ${"%.2f%%".format(java.util.Locale.US, best.report.residualRatio * 100.0)}\n" +
                     "  - Domain Contamination:   ${"%.2f%%".format(java.util.Locale.US, best.report.contaminationRatio * 100.0)}\n" +
                     "==========================================================")
        } else {
            log.warn("Calibration search grid completed with no viable configurations.")
        }
        return emptyMap()
    }
}
