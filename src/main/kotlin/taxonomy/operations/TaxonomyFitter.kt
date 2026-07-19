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

    /**
     * Parallel BFS level-by-level fitting. Processes root-first (shallow to deep)
     * so parent parameters are available for prior calibration at child nodes.
     */
    suspend fun fitNodeRecursive(root: GraphNode, isFinalIteration: Boolean = false) = withContext(Dispatchers.Default) {
        log.info("Starting level-by-level parallel vMF/NiW fitting...")
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
        log.info("[FITTER] Fitting complete ($depthsCount depths, $totalNodesFitted nodes)")
    }

    private fun fitVmfFromQueryList(node: GraphNode, queries: List<Embedding>, d: Int) {
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
            if (dot >= 0.999) {
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
        val rawKappa = StatisticsUtils.correctedKappa(rBar, d, n)
        val sampleWeight = (n / (4.0 * config.formalism.minClusterSize)).coerceIn(0.0, 1.0)
        val effectiveAlpha = config.formalism.emaAlpha * sampleWeight
        val oldKappa = node.vmfKappa.takeIf { it > 1e-3 } ?: rawKappa
        node.vmfKappa = (1.0 - effectiveAlpha) * rawKappa + effectiveAlpha * oldKappa
        node.vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(d, node.vmfKappa)
    }

    fun fitSingleNode(node: GraphNode, isFinalIteration: Boolean = false) {
        val d = node.sliceDim

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
                    val newKappa = StatisticsUtils.correctedKappa(rBar, d, kappaVecs.size)

                    // EMA dampening (keep if node already has a sensible kappa)
                    val prevKappa = node.vmfKappa
                    val sampleWeight = (kappaVecs.size / (10.0 * config.formalism.minClusterSize))
                        .coerceIn(0.0, 1.0)
                    node.vmfKappa = if (prevKappa > 1e-2)
                        prevKappa + sampleWeight * (newKappa - prevKappa)
                    else
                        newKappa

                    node.vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(d, node.vmfKappa)
                } else {
                    fitVmfFromQueryList(node, node.queries.ifEmpty { branchQueries }, d)
                }
            } else {
                val vmfSrc = node.queries.ifEmpty { branchQueries }
                fitVmfFromQueryList(node, vmfSrc, d)
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
            val sampleWeight = (kappaQueries.size / (4.0 * config.formalism.minClusterSize)).coerceIn(0.0, 1.0)
            val effectiveAlpha = config.formalism.emaAlpha * sampleWeight
            val oldKappa = node.vmfKappa.takeIf { it > 1e-3 } ?: rawKappa
            node.vmfKappa = (1.0 - effectiveAlpha) * rawKappa + effectiveAlpha * oldKappa
            node.vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(muSize, node.vmfKappa)
        }

        // ── NiW posterior ─────────────────────────────────────────────────────────
        // Always recompute — NiW is used for routing and needs fresh sample stats.
        // Project using the node's own sliceDim (same as vmfMu.size for consistency).
        val fitDim = node.vmfMu.size   // use actual mu size, not sliceDim, to stay consistent
        val projected = branchQueries.map { it.projectTo(fitDim) }

        val parents = node.parents
        val m0 = DoubleArray(fitDim)
        var kappa0Parent = 0.0

        if (parents.isNotEmpty()) {
            for (parent in parents) {
                val projParentMu = StatisticsUtils.projectVector(parent.vmfMu, fitDim)
                for (i in 0 until fitDim) m0[i] += projParentMu[i].toDouble()
                kappa0Parent += parent.vmfKappa
            }
            var m0Norm = 0.0
            for (i in 0 until fitDim) {
                m0[i] /= parents.size.toDouble()
                m0Norm += m0[i] * m0[i]
            }
            m0Norm = sqrt(m0Norm)
            if (m0Norm > 0.0) for (i in 0 until fitDim) m0[i] /= m0Norm
            else if (fitDim > 0) m0[0] = 1.0
            kappa0Parent /= parents.size.toDouble()
        } else {
            if (fitDim > 0) m0[0] = 1.0
            kappa0Parent = 10.0
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