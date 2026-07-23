package taxonomy.operations

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.withContext
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.model.*
import taxonomy.utils.StatisticsUtils
import kotlin.math.sqrt

/**
 * Implements Phase 2: Fit (Context-Aware Distribution Modeling).
 * Fits a single-component vMF model and updates a diagonal NiW posterior at each node.
 */
@Service
class TaxonomyFitter(
    private val config: TaxonomyConfig
) {
    private val log = LoggerFactory.getLogger("taxonomy.Fitter")
    private val highDOverNCount = java.util.concurrent.atomic.AtomicInteger(0)
    private val muHistory = java.util.concurrent.ConcurrentHashMap<String, MutableList<FloatArray>>()
    private val driftSums = java.util.concurrent.CopyOnWriteArrayList<Double>()
    private val oscillationCount = java.util.concurrent.atomic.AtomicInteger(0)
    private val earlyOutCount = java.util.concurrent.atomic.AtomicInteger(0)
    private val totalMuCount = java.util.concurrent.atomic.AtomicInteger(0)

    private val kappaList = java.util.concurrent.CopyOnWriteArrayList<Double>()
    private val alphaList = java.util.concurrent.CopyOnWriteArrayList<Double>()

    suspend fun fitNodeRecursive(root: GraphNode, currentIteration: Int = 0, isFinalIteration: Boolean = false) = withContext(Dispatchers.Default) {
        log.info("Starting level-by-level parallel vMF/NiW fitting...")
        highDOverNCount.set(0)

        driftSums.clear()
        oscillationCount.set(0)
        earlyOutCount.set(0)
        totalMuCount.set(0)
        kappaList.clear()
        alphaList.clear()

        val byDepth = mutableMapOf<Int, MutableList<GraphNode>>()
        val visited = mutableSetOf<String>()
        val treeQueue = ArrayDeque<GraphNode>().apply { add(root) }
        while (treeQueue.isNotEmpty()) {
            val n = treeQueue.removeFirst()
            if (!visited.add(n.id)) continue
            byDepth.getOrPut(n.depth) { mutableListOf() }.add(n)
            treeQueue.addAll(n.children)
        }

        val clVisited = visited.toMutableSet()
        for (depth in byDepth.keys.sorted()) {
            for (n in byDepth[depth]!!.toList()) {
                for (clChild in n.crossLinkChildren) {
                    if (clVisited.add(clChild.id)) {
                        byDepth.getOrPut(clChild.depth) { mutableListOf() }.add(clChild)
                    }
                }
            }
        }

        val depthsCount = byDepth.keys.size
        val totalNodesFitted = byDepth.values.sumOf { it.size }
        byDepth.keys.sorted().forEach { depth ->
            val nodesAtDepth = byDepth[depth]!!
            nodesAtDepth.map { node ->
                async {
                    fitSingleNode(node, isFinalIteration)
                }
            }.awaitAll()
        }
        val highCount = highDOverNCount.get()
        if (highCount > 0) {
            log.info("[FITTER] $highCount nodes had high d/N ratio (> 10.0) and were prior-dominated")
        }

        if (currentIteration > 0) {
            val driftAvg = if (driftSums.isNotEmpty()) driftSums.average() else 0.0
            val oscVal = oscillationCount.get()
            val totalMu = totalMuCount.get()
            val earlyOutVal = earlyOutCount.get()
            val earlyOutRate = if (totalMu > 0) earlyOutVal.toDouble() / totalMu else 0.0

            log.info("[FIT-μ]  iter=$currentIteration: mean_MLE_drift=${"%.3f".format(java.util.Locale.US, driftAvg)}, oscillating_nodes=$oscVal/$totalMu, earlyout_rate=${"%.2f".format(java.util.Locale.US, earlyOutRate)}")

            val priorDominated = alphaList.count { it > 0.5 }
            val totalAlpha = alphaList.size
            val pct = if (totalAlpha > 0) (priorDominated.toDouble() / totalAlpha * 100.0) else 0.0
            val sortedK = kappaList.sorted()
            val medianK = if (sortedK.isNotEmpty()) sortedK[sortedK.size / 2] else 0.0
            val sortedAlpha = alphaList.sorted()
            val medianAlpha = if (sortedAlpha.isNotEmpty()) sortedAlpha[sortedAlpha.size / 2] else 0.0

            log.info("[FIT-κ]  iter=$currentIteration: prior_dominated=$priorDominated/$totalAlpha (${"%.1f".format(java.util.Locale.US, pct)}%), median_kfinal=${"%.2f".format(java.util.Locale.US, medianK)}, median_alpha=${"%.2f".format(java.util.Locale.US, medianAlpha)}")
        }

        log.info("[FITTER] Fitting complete ($depthsCount depths, $totalNodesFitted nodes)")

        // 2. Diagnostics logging per run
        try {
            val visitedDiag = mutableSetOf<String>()
            val queueDiag = ArrayDeque<GraphNode>().apply { add(root) }
            
            data class DiagStats(
                var count: Int = 0,
                var sumPrefix: Double = 0.0,
                var sumPrior: Double = 0.0,
                var smallLeafCount: Int = 0,
                var sumMlMinusPrefix: Double = 0.0,
                var sumMlMinusNew: Double = 0.0
            )
            
            val depthDiag = mutableMapOf<Int, DiagStats>()
            
            while (queueDiag.isNotEmpty()) {
                val node = queueDiag.removeFirst()
                if (!visitedDiag.add(node.id)) continue

                val branchQueries = node.getAllQueriesInRegion()
                val n = branchQueries.size
                
                val kappa0Parent = if (node.parents.isNotEmpty()) {
                    val validParentKappas = node.parents.map { it.vmfKappa }.filter { it > 0.0 }
                    if (validParentKappas.isNotEmpty()) validParentKappas.average() else config.formalism.defaultKappaPrior
                } else {
                    config.formalism.defaultKappaPrior
                }
                
                val stats = depthDiag.getOrPut(node.depth) { DiagStats() }
                stats.count++
                stats.sumPrefix += node.vmfKappa
                stats.sumPrior += kappa0Parent
                
                if (node.isLeaf && n < 30) {
                    stats.smallLeafCount++
                }
                
                queueDiag.addAll(node.children)
                queueDiag.addAll(node.crossLinkChildren)
            }
            
            val diagSb = StringBuilder()
            diagSb.append("\n┌── FITTER DIAGNOSTICS SUMMARY ───────────────────────────\n")
            diagSb.append("│ %-5s | %-12s | %-12s | %-15s | %-18s | %-18s\n".format(
                "Depth", "Avg Prefix K", "Avg Prior K", "Small Leaves", "Avg (K_ML - K_pref)", "Avg (K_ML - K_new)"
            ))
            diagSb.append("├─────────────────────────────────────────────────────────\n")
            depthDiag.keys.sorted().forEach { depth ->
                val stats = depthDiag.getValue(depth)
                val avgPrefix = stats.sumPrefix / stats.count.coerceAtLeast(1)
                val avgPrior = stats.sumPrior / stats.count.coerceAtLeast(1)
                val avgDiffPrefix = if (stats.smallLeafCount > 0) stats.sumMlMinusPrefix / stats.smallLeafCount else 0.0
                val avgDiffNew = if (stats.smallLeafCount > 0) stats.sumMlMinusNew / stats.smallLeafCount else 0.0
                
                diagSb.append(String.format(
                    java.util.Locale.US,
                    "│ %-5d | %-12.4f | %-12.4f | %-15d | %-18.4f | %-18.4f\n",
                    depth, avgPrefix, avgPrior, stats.smallLeafCount, avgDiffPrefix, avgDiffNew
                ))
            }
            diagSb.append("└─────────────────────────────────────────────────────────")
            log.info(diagSb.toString())
        } catch (diagEx: Exception) {
            log.warn("Diagnostics logging failed: ${diagEx.message}")
        }
    }

    private fun dOverNAlpha(rho: Double): Double {
        return when {
            rho <= 2.0  -> 0.0             // trust κ_ML
            rho <= 10.0 -> (rho - 2.0) / 8.0 // ramp up
            else        -> 1.0             // fully prior-dominated
        }
    }

    private fun GraphNode.getRegionQueryWeights(): Map<String, Double> {
        val weights = mutableMapOf<String, Double>()
        val visited = mutableSetOf<String>()

        fun walk(node: GraphNode) {
            if (!visited.add(node.id)) return
            for ((q, w) in node.queryWeights) {
                weights[q] = (weights[q] ?: 0.0) + w
            }
            node.treeChildren.forEach { walk(it) }
            node.crossLinkChildren.forEach { walk(it) }
        }
        walk(this)
        return weights
    }

    fun fitSingleNode(node: GraphNode, isFinalIteration: Boolean = false) {
        val parents = node.parents
        
        // 1. Get query weights in the region and total effective count
        val queryWeightsMap = node.getRegionQueryWeights()
        val nEffective = queryWeightsMap.values.sum()
        
        // 2. Fixed MRL slice selection (single source of truth: dimForDepth)
        val fitDim = dimForDepth(node.depth)
        node.sliceDim = fitDim
        
        // 3. Prior calculation (kappa0Parent)
        val kappa0Parent = if (parents.isNotEmpty()) {
            val validParentKappas = parents.map { it.vmfKappa }.filter { it > 0.0 }
            if (validParentKappas.isNotEmpty()) validParentKappas.average() else config.formalism.defaultKappaPrior
        } else {
            config.formalism.defaultKappaPrior
        }

        if (nEffective <= 1e-4) {
            node.vmfMu = FloatArray(fitDim) { 0.0f }.apply { this[0] = 1.0f }
            node.vmfKappa = 1e-3
            node.vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(fitDim, node.vmfKappa)
            node.niwM0 = node.vmfMu.copyOf()
            node.niwKappa0 = 1.0
            node.niwNu0 = (fitDim + 2).toDouble()
            node.niwLambda = FloatArray(fitDim) { (1.0 / fitDim).toFloat() }
            node.phaseCompleted = node.phaseCompleted or PHASE_VMF_FIT or PHASE_NIW_FIT
            return
        }

        // 4. Compute Weighted Centroid Vector (mu)
        val sumVec = DoubleArray(fitDim)
        for ((qText, w) in queryWeightsMap) {
            val emb = GraphNode.getEmbedding(qText) ?: continue
            val projected = emb.projectTo(fitDim) // systemic MRL projection & L2 normalization
            for (i in 0 until fitDim) {
                sumVec[i] += w * projected[i]
            }
        }

        var normVec = 0.0
        for (i in 0 until fitDim) normVec += sumVec[i] * sumVec[i]
        normVec = sqrt(normVec)

        val mu = FloatArray(fitDim) { i ->
            if (normVec > 0.0) (sumVec[i] / normVec).toFloat() else 0.0f
        }
        if (normVec == 0.0) mu[0] = 1.0f

        // Track drift/oscillation diagnostics against the previous iteration's mu, then
        // adopt the fresh MLE directly. EMA blending was removed: matched-config A/B runs
        // (emaAlpha=0.7 vs 0.0) showed blending amplifies oscillation and prior-domination
        // instead of stabilizing it, and never converges within the iteration budget.
        val oldMu = node.vmfMu
        if (oldMu.isNotEmpty() && oldMu.size == fitDim) {
            val dot = StatisticsUtils.dotProduct(oldMu.map { it.toDouble() }.toDoubleArray(), mu)
            driftSums.add(dot)
            totalMuCount.incrementAndGet()
            if (dot >= 0.9975) {
                earlyOutCount.incrementAndGet()
                node.vmfMu = oldMu
            } else {
                node.vmfMu = mu
            }

            // Oscillation detection: dot with mu_{t-2} > dot with mu_{t-1}
            val history = muHistory[node.id]
            if (history != null && history.size >= 2) {
                val mu_t_minus_2 = history[history.size - 2]
                val mu_t_minus_1 = oldMu
                val dot_t_minus_2 = StatisticsUtils.dotProduct(mu_t_minus_2.map { it.toDouble() }.toDoubleArray(), mu)
                val dot_t_minus_1 = StatisticsUtils.dotProduct(mu_t_minus_1.map { it.toDouble() }.toDoubleArray(), mu)
                if (dot_t_minus_2 > dot_t_minus_1) {
                    oscillationCount.incrementAndGet()
                }
            }
        } else {
            node.vmfMu = mu
        }
        muHistory.getOrPut(node.id) { mutableListOf() }.add(node.vmfMu.copyOf())

        // 5. Compute Weighted Concentration (kappa)
        val rBar = normVec / nEffective
        node.dOverN = fitDim.toDouble() / nEffective

        val priorKappa = kappa0Parent.coerceAtLeast(1.0)

        val alphaD = if (nEffective < config.formalism.effectiveSupportFloor) {
            node.vmfKappa = priorKappa
            1.0
        } else {
            val rawKappa = StatisticsUtils.correctedKappa(rBar, fitDim, nEffective.toInt())
            val rho = fitDim.toDouble() / nEffective
            val a = dOverNAlpha(rho)
            node.vmfKappa = (1.0 - a) * rawKappa + a * priorKappa
            a
        }
        node.vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(fitDim, node.vmfKappa)

        kappaList.add(node.vmfKappa)
        alphaList.add(alphaD)

        if (node.dOverN > 10.0) {
            highDOverNCount.incrementAndGet()
        }

        // 6. NiW posterior (adapted to soft weighting queryWeights)
        val m0 = DoubleArray(fitDim)
        if (parents.isNotEmpty()) {
            for (parent in parents) {
                val projParentMu = StatisticsUtils.projectVector(parent.vmfMu, fitDim)
                for (i in 0 until fitDim) m0[i] += projParentMu[i].toDouble()
            }
            var m0Norm = 0.0
            for (i in 0 until fitDim) {
                m0[i] /= parents.size.toDouble()
                m0Norm += m0[i] * m0[i]
            }
            m0Norm = sqrt(m0Norm)
            if (m0Norm > 0.0) for (i in 0 until fitDim) m0[i] /= m0Norm
            else m0[0] = 1.0
        } else {
            m0[0] = 1.0
        }

        val kappa0 = 1.0
        val nu0 = (fitDim + 2).toDouble()
        val lambda = 1.0 / (priorKappa.coerceAtLeast(1e-3) * fitDim)

        val sampleMean = DoubleArray(fitDim)
        for ((qText, w) in queryWeightsMap) {
            val emb = GraphNode.getEmbedding(qText) ?: continue
            val proj = emb.projectTo(fitDim)
            for (i in 0 until fitDim) {
                sampleMean[i] += w * proj[i]
            }
        }
        for (i in 0 until fitDim) sampleMean[i] /= nEffective

        val kappaN = kappa0 + nEffective
        val nuN = nu0 + nEffective

        val mN = FloatArray(fitDim) { i ->
            ((kappa0 * m0[i] + nEffective * sampleMean[i]) / kappaN).toFloat()
        }

        val lambdaN = FloatArray(fitDim)
        for ((qText, w) in queryWeightsMap) {
            val emb = GraphNode.getEmbedding(qText) ?: continue
            val proj = emb.projectTo(fitDim)
            for (i in 0 until fitDim) {
                val diff = proj[i] - sampleMean[i]
                lambdaN[i] += (w * diff * diff).toFloat()
            }
        }
        for (i in 0 until fitDim) {
            val meanDiff = sampleMean[i] - m0[i]
            val updatePart = (kappa0 * nEffective / kappaN) * meanDiff * meanDiff
            lambdaN[i] = (lambda + lambdaN[i] + updatePart).toFloat()
        }

        node.niwM0 = mN
        node.niwKappa0 = kappaN
        node.niwNu0 = nuN
        node.niwLambda = lambdaN

        node.phaseCompleted = node.phaseCompleted or PHASE_VMF_FIT or PHASE_NIW_FIT
    }
}