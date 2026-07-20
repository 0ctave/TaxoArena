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

    private val calibratedRatios = java.util.concurrent.ConcurrentHashMap<Int, Double>()

    private fun computePrefixKappa(node: GraphNode, queries: List<Embedding>, dPrefix: Int): Double {
        val n = queries.size
        if (n < 2) return 1.0
        
        val actualDPrefix = minOf(dPrefix, node.sliceDim)
        val projected = queries.map { it.projectTo(actualDPrefix) }
        
        val sumVec = DoubleArray(actualDPrefix)
        for (vec in projected) {
            for (i in 0 until actualDPrefix) {
                sumVec[i] += vec[i].toDouble()
            }
        }
        
        var normVec = 0.0
        for (i in 0 until actualDPrefix) normVec += sumVec[i] * sumVec[i]
        normVec = sqrt(normVec)
        
        val prefixMu = DoubleArray(actualDPrefix) { i -> if (normVec > 0.0) sumVec[i] / normVec else 0.0 }
        if (normVec == 0.0 && actualDPrefix > 0) prefixMu[0] = 1.0
        
        var dotSum = 0.0
        for (vec in projected) {
            for (i in 0 until actualDPrefix) {
                dotSum += prefixMu[i] * vec[i]
            }
        }
        val rBarPrefix = (dotSum / n.coerceAtLeast(1)).coerceAtLeast(0.0)
        
        return StatisticsUtils.correctedKappa(rBarPrefix, actualDPrefix, n)
    }

    private fun calibrateKappaPrior(root: GraphNode) {
        calibratedRatios.clear()
        val depthRatios = mutableMapOf<Int, MutableList<Double>>()
        val visited = mutableSetOf<String>()
        val queue = ArrayDeque<GraphNode>().apply { add(root) }
        
        while (queue.isNotEmpty()) {
            val node = queue.removeFirst()
            if (!visited.add(node.id)) continue
            
            val branchQueries = node.getAllQueriesInRegion()
            val n = branchQueries.size
            val d = node.sliceDim
            
            if (n >= 2 * d && n >= 10) {
                val projected = branchQueries.map { it.projectTo(d) }
                val sumVec = DoubleArray(d)
                for (vec in projected) for (i in 0 until d) sumVec[i] += vec[i]
                var normVec = 0.0
                for (i in 0 until d) normVec += sumVec[i] * sumVec[i]
                normVec = sqrt(normVec)
                val rBar = normVec / n
                
                val rawKappa = StatisticsUtils.correctedKappa(rBar, d, n)
                val kappaPrefix = computePrefixKappa(node, branchQueries, config.formalism.dPrefix)
                
                if (kappaPrefix > 0.0) {
                    depthRatios.getOrPut(node.depth) { mutableListOf() }.add(rawKappa / kappaPrefix)
                }
            }
            queue.addAll(node.children)
            queue.addAll(node.crossLinkChildren)
        }
        
        depthRatios.forEach { (depth, ratios) ->
            calibratedRatios[depth] = ratios.average()
            log.info("[FITTER] Calibrated kappa ratio for depth $depth: ${"%.4f".format(ratios.average())} (based on ${ratios.size} well-behaved nodes)")
        }
    }

    private fun getCalibratedRatio(depth: Int, dFull: Int, dPrefix: Int): Double {
        val observed = calibratedRatios[depth]
        if (observed != null) return observed
        return dFull.toDouble() / dPrefix.toDouble().coerceAtLeast(1.0)
    }

    private fun mapPrefixToPrior(depth: Int, dFull: Int, dPrefix: Int, kappaPrefix: Double): Double {
        val ratio = getCalibratedRatio(depth, dFull, dPrefix)
        return ratio * kappaPrefix
    }

    suspend fun fitNodeRecursive(root: GraphNode, isFinalIteration: Boolean = false) = withContext(Dispatchers.Default) {
        log.info("Starting level-by-level parallel vMF/NiW fitting...")
        highDOverNCount.set(0)
        
        // 1. Empirical prior calibration pre-pass
        calibrateKappaPrior(root)

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
                
                val d = node.sliceDim
                val branchQueries = node.getAllQueriesInRegion()
                val n = branchQueries.size
                
                val kappaPrefix = computePrefixKappa(node, branchQueries, config.formalism.dPrefix)
                
                val rawKappa = run {
                    val projected = branchQueries.map { it.projectTo(d) }
                    var dotSum = 0.0
                    val mu = node.vmfMu.takeIf { it.size == d } ?: FloatArray(d) { 0.0f }.apply { if (d > 0) this[0] = 1.0f }
                    for (vec in projected) {
                        for (i in 0 until d) dotSum += mu[i] * vec[i]
                    }
                    val rBar = (dotSum / branchQueries.size.coerceAtLeast(1)).coerceAtLeast(0.0)
                    StatisticsUtils.correctedKappa(rBar, d, branchQueries.size)
                }
                
                val avgKappaPrefixAtParent = if (node.parents.isNotEmpty()) {
                    node.parents.map { parent ->
                        val pq = parent.getAllQueriesInRegion()
                        computePrefixKappa(parent, pq, config.formalism.dPrefix)
                    }.average()
                } else {
                    0.0
                }
                val kappa0Parent = if (node.parents.isNotEmpty()) {
                    mapPrefixToPrior(node.depth, d, config.formalism.dPrefix, avgKappaPrefixAtParent)
                } else {
                    config.formalism.defaultKappaPrior
                }
                
                val stats = depthDiag.getOrPut(node.depth) { DiagStats() }
                stats.count++
                stats.sumPrefix += kappaPrefix
                stats.sumPrior += kappa0Parent
                
                if (node.isLeaf && n < 30) {
                    stats.smallLeafCount++
                    stats.sumMlMinusPrefix += (rawKappa - kappaPrefix)
                    stats.sumMlMinusNew += (rawKappa - node.vmfKappa)
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

    private fun fitVmfFromQueryList(node: GraphNode, queries: List<Embedding>, d: Int, kappa0Parent: Double) {
        val n = queries.size
        if (n == 0) return

        val projected = queries.map { it.projectTo(d) }

        val sumVec = DoubleArray(d)
        for (vec in projected) for (i in 0 until d) sumVec[i] += vec[i]

        var normVec = 0.0
        for (i in 0 until d) normVec += sumVec[i] * sumVec[i]
        normVec = sqrt(normVec)

        val mu = FloatArray(d) { i ->
            if (normVec > 0.0) (sumVec[i] / normVec).toFloat() else 0.0f
        }
        if (normVec == 0.0 && d > 0) mu[0] = 1.0f

        val oldMu = node.vmfMu
        if (oldMu.isNotEmpty() && oldMu.size == d) {
            val dot = StatisticsUtils.dotProduct(oldMu.map { it.toDouble() }.toDoubleArray(), mu)
            if (dot >= 0.9975) {
                node.vmfMu = oldMu
            } else {
                val emaAlpha = config.formalism.emaAlpha
                val blended = DoubleArray(d) { i -> (1.0 - emaAlpha) * mu[i].toDouble() + emaAlpha * oldMu[i].toDouble() }
                var norm = 0.0
                for (i in 0 until d) norm += blended[i] * blended[i]
                norm = sqrt(norm)
                val newMu = FloatArray(d) { i -> if (norm > 0.0) (blended[i] / norm).toFloat() else 0.0f }
                if (norm == 0.0 && d > 0) newMu[0] = 1.0f
                node.vmfMu = newMu
            }
        } else {
            node.vmfMu = mu
        }

        val rBar = normVec / n
        val rho = d.toDouble() / n.coerceAtLeast(1)
        node.dOverN = rho
        val alphaD = dOverNAlpha(rho)
        val rawKappa = StatisticsUtils.correctedKappa(rBar, d, n)
        val priorKappa = kappa0Parent.coerceAtLeast(1.0)
        node.vmfKappa = (1.0 - alphaD) * rawKappa + alphaD * priorKappa
        node.vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(d, node.vmfKappa)

        if (rho > 10.0) {
            highDOverNCount.incrementAndGet()
            log.debug("[FITTER] High d/N (${"%.2f".format(rho)}) at node ${node.id} (${node.label}). rawKappa=${"%.2f".format(rawKappa)}, priorKappa=${"%.2f".format(priorKappa)}, newKappa=${"%.2f".format(node.vmfKappa)}")
        }
    }

    fun fitSingleNode(node: GraphNode, isFinalIteration: Boolean = false) {
        val d = node.sliceDim
        val parents = node.parents
        val avgKappaPrefixAtParent = if (parents.isNotEmpty()) {
            parents.map { parent ->
                val parentQueries = parent.getAllQueriesInRegion()
                computePrefixKappa(parent, parentQueries, config.formalism.dPrefix)
            }.average()
        } else {
            0.0
        }

        val kappa0Parent = if (parents.isNotEmpty()) {
            mapPrefixToPrior(node.depth, d, config.formalism.dPrefix, avgKappaPrefixAtParent)
        } else {
            config.formalism.defaultKappaPrior
        }

        // ── n for NiW (always branch-based for routing confidence) ───────────────
        val branchQueries = node.getAllQueriesInRegion()
        val n = branchQueries.size
        val kappaQueries = if (config.formalism.enableResidualRouting) {
            branchQueries.filter { emb ->
                val qId = if (emb.queryId != -1) emb.queryId.toString() else taxonomy.model.TextNormalizer.cleanText(emb.rawText)
                qId !in node.residualQueries
            }.ifEmpty { branchQueries }
        } else {
            branchQueries
        }

        if (n == 0) {
            node.vmfMu = FloatArray(d) { 0.0f }.apply { if (d > 0) this[0] = 1.0f }
            node.vmfKappa = 1e-3
            node.vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(d, node.vmfKappa)
            node.niwM0 = node.vmfMu.copyOf()
            node.niwKappa0 = 1.0
            node.niwNu0 = (d + 2).toDouble()
            node.niwLambda = FloatArray(d) { (1.0 / d).toFloat() }
            node.phaseCompleted = node.phaseCompleted or PHASE_VMF_FIT or PHASE_NIW_FIT
            return
        }

        // ── vMF fit ───────────────────────────────────────────────────────────────
        // Three cases, in priority order:
        //
        // 1. Splitter already fitted vMF (PHASE_SPLIT_EVAL set): trust it.
        //    Those values were fitted from the original embeddings at the correct
        //    childDim during bisection. Re-computing would destroy the separation.
        //
        // 2. Internal node (has tree children, not yet fitted): fit vMF from the
        //    weighted centroid of direct tree children's vmfMu vectors.
        //    This gives the node a directional identity that is the geometric
        //    parent of its children, rather than a blurred union of all subtree
        //    queries (which collapses to near-uniform when sub-domains cancel out).
        //
        // 3. Leaf node (no tree children): fit vMF from node.queries directly.
        //    Fall back to branchQueries only if node.queries is empty.
        val muAlreadyFit = ((node.phaseCompleted and PHASE_SPLIT_EVAL) != 0) &&
                !(config.formalism.refitMuPerIteration || isFinalIteration)

        if (!muAlreadyFit) {
            if (!node.isLeaf && node.children.isNotEmpty()) {
                val fittedChildren = node.children.filter { it.vmfMu.isNotEmpty() }
                if (fittedChildren.isNotEmpty()) {
                    // --- Step 1: derive mu from weighted child means (unchanged) ---
                    val childCounts = fittedChildren.associateWith { it.getRecursiveQueryCount().toDouble() }
                    val totalChildN = childCounts.values.sum().coerceAtLeast(1.0)

                    val weightedMu = DoubleArray(d)
                    for (child in fittedChildren) {
                        val w = if (fittedChildren.size == 1) 1.0
                        else (childCounts[child] ?: 0.0) / totalChildN
                        val childMu = StatisticsUtils.projectVector(child.vmfMu, d)
                        for (i in 0 until d) weightedMu[i] += w * childMu[i]
                    }
                    var norm = 0.0
                    for (i in 0 until d) norm += weightedMu[i] * weightedMu[i]
                    norm = sqrt(norm)

                    val mu = FloatArray(d) { i ->
                        if (norm > 0.0) (weightedMu[i] / norm).toFloat() else 0.0f
                    }
                    if (norm == 0.0 && d > 0) mu[0] = 1.0f
                    node.vmfMu = mu

                    // --- Step 2: derive kappa from ACTUAL query alignment against mu ---
                    // This measures "how broad is this domain really?" from the queries,
                    // not from the child mean coherence (which is always high for 2 child-means).
                    var dotSum = 0.0
                    val kappaVecs = kappaQueries.map { it.projectTo(d) }
                    for (vec in kappaVecs) {
                        for (i in 0 until d) dotSum += mu[i] * vec[i]
                    }
                    val rBar = (dotSum / kappaVecs.size.coerceAtLeast(1)).coerceAtLeast(0.0)
                    val rawKappa = StatisticsUtils.correctedKappa(rBar, d, kappaVecs.size)
                    val rho = d.toDouble() / kappaVecs.size.coerceAtLeast(1)
                    node.dOverN = rho
                    val alphaD = dOverNAlpha(rho)
                    val priorKappa = kappa0Parent.coerceAtLeast(1.0)
                    node.vmfKappa = (1.0 - alphaD) * rawKappa + alphaD * priorKappa
                    node.vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(d, node.vmfKappa)

                    if (rho > 10.0) {
                        highDOverNCount.incrementAndGet()
                        log.debug("[FITTER] High d/N (${"%.2f".format(rho)}) at node ${node.id} (${node.label}). rawKappa=${"%.2f".format(rawKappa)}, priorKappa=${"%.2f".format(priorKappa)}, newKappa=${"%.2f".format(node.vmfKappa)}")
                    }
                } else {
                    fitVmfFromQueryList(node, node.queries.ifEmpty { branchQueries }, d, kappa0Parent)
                }
            } else {
                val vmfSrc = node.queries.ifEmpty { branchQueries }
                fitVmfFromQueryList(node, vmfSrc, d, kappa0Parent)
            }
        } else {
            // mu trusted from splitter — recompute kappa from current branch to reflect
            // who is actually here now, not who was here at split time
            val muSize = node.vmfMu.size
            val rBar = run {
                val projected = kappaQueries.map { it.projectTo(muSize) }
                var dot = 0.0
                for (vec in projected) for (i in 0 until muSize) dot += node.vmfMu[i] * vec[i]
                (dot / kappaQueries.size.coerceAtLeast(1)).coerceAtLeast(0.0)
            }
            val rawKappa = StatisticsUtils.correctedKappa(rBar, muSize, kappaQueries.size)
            val rho = muSize.toDouble() / kappaQueries.size.coerceAtLeast(1)
            node.dOverN = rho
            val alphaD = dOverNAlpha(rho)
            val priorKappa = kappa0Parent.coerceAtLeast(1.0)
            node.vmfKappa = (1.0 - alphaD) * rawKappa + alphaD * priorKappa
            node.vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(muSize, node.vmfKappa)

            if (rho > 10.0) {
                highDOverNCount.incrementAndGet()
                log.debug("[FITTER] High d/N (${"%.2f".format(rho)}) at node ${node.id} (${node.label}). rawKappa=${"%.2f".format(rawKappa)}, priorKappa=${"%.2f".format(priorKappa)}, newKappa=${"%.2f".format(node.vmfKappa)}")
            }
        }

        // ── NiW posterior ─────────────────────────────────────────────────────────
        // Always recompute — NiW is used for routing and needs fresh sample stats.
        // Project using the node's own sliceDim (same as vmfMu.size for consistency).
        val fitDim = node.vmfMu.size   // use actual mu size, not sliceDim, to stay consistent
        val projected = branchQueries.map { it.projectTo(fitDim) }

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
            else if (fitDim > 0) m0[0] = 1.0
        } else {
            if (fitDim > 0) m0[0] = 1.0
        }

        val kappa0 = 1.0
        val nu0 = (fitDim + 2).toDouble()
        val lambda = 1.0 / (kappa0Parent.coerceAtLeast(1e-3) * fitDim)

        val sampleMean = DoubleArray(fitDim)
        for (vec in projected) for (i in 0 until fitDim) sampleMean[i] += vec[i]
        for (i in 0 until fitDim) sampleMean[i] /= n.toDouble()

        val effectiveN = if (node.isBridge) {
            (config.formalism.minClusterSize * 1.5).coerceAtMost(n.toDouble())
        } else {
            n.toDouble()
        }

        val kappaN = kappa0 + effectiveN
        val nuN = nu0 + effectiveN

        val mN = FloatArray(fitDim) { i ->
            ((kappa0 * m0[i] + effectiveN * sampleMean[i]) / kappaN).toFloat()
        }

        val lambdaN = FloatArray(fitDim)
        for (vec in projected) {
            for (i in 0 until fitDim) {
                val diff = vec[i] - sampleMean[i]
                lambdaN[i] += (diff * diff).toFloat()
            }
        }
        for (i in 0 until fitDim) {
            val meanDiff = sampleMean[i] - m0[i]
            val updatePart = (kappa0 * effectiveN / kappaN) * meanDiff * meanDiff
            lambdaN[i] = (lambda + lambdaN[i] + updatePart).toFloat()
        }

        node.niwM0 = mN
        node.niwKappa0 = kappaN
        node.niwNu0 = nuN
        node.niwLambda = lambdaN

        node.phaseCompleted = node.phaseCompleted or PHASE_VMF_FIT or PHASE_NIW_FIT
    }
}