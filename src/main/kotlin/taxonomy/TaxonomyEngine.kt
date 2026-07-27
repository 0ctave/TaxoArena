package taxonomy

import kotlinx.coroutines.coroutineScope
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.model.*
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomyOperations
import taxonomy.operations.TaxonomyStabilizer
import taxonomy.operations.TaxonomyVisualizer
import taxonomy.service.TaxonomyService
import taxonomy.utils.TaxonomyMetrics
import taxonomy.utils.TaxonomyPerformanceTracker
import taxonomy.utils.reportToIterationMetrics
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.operations.TaxonomyTrickler
import java.io.File
import kotlin.system.measureTimeMillis

/**
 * High-level orchestrator for the Taxonomy adaptation workflow.
 * Executing Phase 1 (Extract), Phase 2 (Fit), and Phase 3 (Trickle).
 */
@Service
class TaxonomyEngine(
    private val config: TaxonomyConfig,
    private val embeddingCache: EmbeddingCache,
    internal val ops: TaxonomyOperations,
    private val llmClient: TaxonomyLlmClient,
    private val visualizer: TaxonomyVisualizer,
    private val stabilizer: TaxonomyStabilizer,
    private val taxonomyService: TaxonomyService,
    private val perfTracker: TaxonomyPerformanceTracker,
    private val datasetFetcher: MMLUDatasetFetcher,
    private val trickler: TaxonomyTrickler
) {
    private val log = LoggerFactory.getLogger("taxonomy.Engine")

    suspend fun adaptTaxonomy(rootLabel: String, dataset: Map<String, List<String>>): GraphNode = coroutineScope {
        log.info("Starting Taxonomy Adaptation: $rootLabel")
        log.info(config.formatConfigReport())
        perfTracker.clear()
        ops.resetConceptCounter()
        GraphNode.resetIdCounter()
        taxonomyService.clearMetricsHistory()

        val totalIters = config.execution.numIterations
        try {
            // 1. EMBEDDING PRECOMPUTATION: Precompute query embeddings using cache
            log.info("Phase 1: Precomputing Embeddings...")
            taxonomyService.updateGenerationProgress(
                GenerationProgress(
                    currentIteration = 0,
                    totalIterations = totalIters,
                    currentStep = "Phase 1: Precomputing Embeddings",
                    stepIndex = 1,
                    totalSteps = 2,
                    percentComplete = 5.0,
                    statusText = "Precomputing and loading query embeddings..."
                )
            )

            val distilledData: List<Triple<String, String, String>>
            var allTextsCount = 0L
            val phase1Time = measureTimeMillis {
                distilledData = dataset.flatMap { (category, queries) ->
                    queries.map { rawText ->
                        Triple(category, rawText, rawText)
                    }
                }

                val allTexts = distilledData.map { it.third }.distinct()
                allTextsCount = allTexts.size.toLong()
                embeddingCache.precompute(allTexts) { current, total ->
                    taxonomyService.updateEmbeddingProgress(current, total)
                }
                taxonomyService.clearEmbeddingProgress()
            }
            perfTracker.recordTime("construction.phase1_precompute", phase1Time, allTextsCount)

            // ── Dimension fast-fail ──────────────────────────────────────────
            // Validate that the embedding model produces vectors with enough
            // dimensions to cover the deepest MRL level (dimForDepth(maxDepth)).
            // The model stores full-size vectors; slicing to dimForDepth(depth) is
            // done later by projectTo(). Comparing against dimForDepth(0) was wrong —
            // it always threw because the model produces e.g. 1024-dim vectors.
            // (dimForDepth is flat 256 at every depth now, so this check and the old
            // per-depth one coincide; see its KDoc for why the seam is kept.)
            val maxDepth    = config.formalism.maxDepth
            val minRequired = dimForDepth(maxDepth)
            val actualDim   = embeddingCache.dimensionality
            check(actualDim >= minRequired) {
                "Embedding dimension mismatch: model produces $actualDim-dim vectors " +
                "but dimForDepth(maxDepth=$maxDepth) = $minRequired. " +
                "Switch to a model that outputs at least $minRequired dimensions, " +
                "or reduce maxDepth in application.yml."
            }
            log.info("Dimension check passed: model=$actualDim dims, minRequired=$minRequired (maxDepth=$maxDepth)")
            // ────────────────────────────────────────────────────────────────

            val root = GraphNode(label = rootLabel, depth = 0)
            val dagRoot = DagRoot(root)

            // 2. Initial Structural Setup & Bootstrap Fitting
            taxonomyService.updateGenerationProgress(
                GenerationProgress(
                    currentIteration = 0,
                    totalIterations = totalIters,
                    currentStep = "Bootstrap Fitting",
                    stepIndex = 2,
                    totalSteps = 2,
                    percentComplete = 10.0,
                    statusText = "Seeding GMM bounds with ground-truth anchors..."
                )
            )

            var withheldCount = 0
            val bootstrapTime = measureTimeMillis {
                // Anchor grouping only. distilledData itself is untouched, so the
                // groundTruthMap below and the routable corpus both still contain these
                // queries — they lose their anchor, not their existence.
                val excluded = config.formalism.excludeFromAnchoring
                // Membership check against the ACTUAL dataset keys. Dataset keys are
                // lowercase ("chemistry"); depth-1 tree labels are capitalised
                // ("Chemistry"), and `it.first in excluded` is exact string equality —
                // so the wrong case silently excludes nothing. Deliberately not
                // case-insensitive: normalising would paper over the two-space problem
                // rather than surfacing it.
                if (excluded.isNotEmpty()) {
                    val available = dataset.keys
                    val unknown = excluded.filterNot { it in available }
                    require(unknown.isEmpty()) {
                        "excludeFromAnchoring names categor(ies) absent from the dataset: $unknown. " +
                            "Matching is case-sensitive and exact. Available keys: ${available.sorted()}"
                    }
                }
                val anchorable = if (excluded.isEmpty()) distilledData
                                 else distilledData.filterNot { it.first in excluded }
                withheldCount = distilledData.size - anchorable.size
                if (excluded.isNotEmpty()) {
                    log.warn(
                        "[HOLD-OUT] excluding ${excluded.size} categor(ies) from anchoring: $excluded" +
                            " — ${distilledData.size - anchorable.size} queries will enter unanchored"
                    )
                }
                val categoryGroups = anchorable.groupBy { it.first }
                categoryGroups.forEach { (name, items) ->
                    val node = GraphNode(label = name, depth = 1)
                    node.originalCategory = name
                    val embs = items.mapNotNull { (_, raw, keywords) ->
                        embeddingCache.get(keywords)?.let { vec -> Embedding(raw, keywords, vec, name) }
                    }
                    if (embs.isNotEmpty()) {
                        node.queries.addAll(embs)
                        for (q in embs) {
                            node.queryWeights[q.rawText] = 1.0
                            GraphNode.registerEmbedding(q)
                        }
                        node.parents.add(root)
                        root.children.add(node)
                    }
                }

                // Normalize bootstrap query weights across category leaves to conserve mass
                val categoryLeaves = root.children.toList()
                val bootstrapTotals = mutableMapOf<String, Double>()
                for (leaf in categoryLeaves) {
                    for ((q, w) in leaf.queryWeights) {
                        bootstrapTotals[q] = (bootstrapTotals[q] ?: 0.0) + w
                    }
                }
                for (leaf in categoryLeaves) {
                    for (q in leaf.queryWeights.keys.toList()) {
                        val tot = bootstrapTotals[q] ?: 1.0
                        if (tot > 0.0) {
                            leaf.queryWeights[q] = leaf.queryWeights[q]!! / tot
                        }
                    }
                }

                taxonomyService.setGraph(root)
                taxonomyService.notifyGraphUpdated()

                log.info("Bootstrap: Seeding GMMs with 100% ground-truth data...")
                ops.fitNodeRecursive(root)
                taxonomyService.notifyGraphUpdated()
            }
            perfTracker.recordTime("construction.phase2_bootstrap", bootstrapTime, 1L)

            // Ground truth map — deliberately over the FULL distilledData, so withheld
            // categories keep their labels and recovery can be scored against them.
            val groundTruthMap = distilledData.groupBy({ it.second }, { it.first })
                .mapValues { it.value.toList() }

            // Guard the hold-out invariants. Without these the experiment can go
            // silently vacuous: a filter that dropped the queries entirely, rather than
            // just their anchor, would produce "no new domain discovered" for the wrong
            // reason and look like a negative result.
            config.formalism.excludeFromAnchoring.takeIf { it.isNotEmpty() }?.let { ex ->
                val anchorLabels = root.children.mapNotNull { it.label }.toSet()
                val leaked = anchorLabels intersect ex
                check(leaked.isEmpty()) { "[HOLD-OUT] excluded categories were anchored anyway: $leaked" }
                val retained = groundTruthMap.values.count { labels -> labels.any { it in ex } }
                check(retained > 0) {
                    "[HOLD-OUT] excluded categories vanished from groundTruthMap — the filter removed" +
                        " the queries, not just their anchor; recovery could not be scored"
                }
                log.warn("[HOLD-OUT] ${root.children.size} anchors seeded; $retained withheld queries retained unanchored")
                // The one guard that can fail. Presence checks pass on a vacuous run;
                // a count check does not.
                val expected = config.formalism.expectedWithheldQueries
                if (expected >= 0) {
                    check(withheldCount == expected) {
                        "[HOLD-OUT] withheld $withheldCount queries but expectedWithheldQueries=$expected." +
                            " Either the category names are wrong (case-sensitive) or the expected value" +
                            " was derived in the wrong space — it must be the TRAIN-split count, not the" +
                            " leaf-region count."
                    }
                }
            }

            // --- NEW: Print Initial State ---
            log.info("Initial DAG Structure (Before Statistical Fitting)")
            ops.printHierarchy(root)

            val uniqueEmbs = root.children.flatMap { gatherAllEmbeddingsInBranch(it) }.distinctBy { it.rawText }

            stabilizer.reset()
            val activeNodeHashes = mutableListOf<Int>()
            var lastIterationJAfterRefit: Double? = null
            // Retained for the fixed-point certificate emitted after the loop.
            var lastTrickleDelta = Double.NaN
            var lastEditsDelta = Double.NaN
            var lastIterationRun = 0

            // State captured immediately before each refit, so the refit can be treated as a
            // proposal like every other J-changing operation. J does not read vmfMu or vmfKappa,
            // so a refit's effect on J is realised only by the routing it drives at the start of
            // the next iteration — refit and that re-route are therefore ONE move, and the point
            // where its delta becomes measurable is where the gate has to sit.
            var refitBackup: taxonomy.model.GraphStateBackup? = null
            var refitRegistry: Map<String, GraphNode>? = null
            // Parameter state captured immediately before each refit, so the certificate can
            // assert that theta is stationary too. editsDelta and trickleDelta together show the
            // structure and the objective have settled, but a refit can still move mu and kappa
            // inside a J-equivalent set — and theta is what held-out queries route through, so a
            // certificate that ignores it does not cover the object being frozen.
            var preRefitTheta: Map<String, Pair<FloatArray, Double>> = emptyMap()
            var lastMaxMuDelta = Double.NaN
            var lastMaxKappaRel = Double.NaN
            // Consecutive iterations with both J deltas inside tau. GED cannot see this: the
            // structure can oscillate by one node while J sits still, which is convergence of the
            // quantity being optimised.
            var jStationaryStreak = 0
            // Diagnostic count of refits the gate turned down over the whole run.
            var refitRejectedCount = 0

            var previousDagState: Map<String, NodeState>? = null
            for (i in 1..totalIters) {
                log.info("STARTING EVOLUTION ITERATION $i")

                clearFitPhases(root)
                val iterationTime = measureTimeMillis {
                    if (uniqueEmbs.isNotEmpty()) {
                        // Phase 3: Trickle (Top-Down Restrictive Funnel Routing)
                        log.debug("Phase 3: Trickling (Reassigning Queries)...")
                        val tricklePercent = 10.0 + ((i - 1).toDouble() / totalIters) * 80.0 + (1.0 / 5.0) * (80.0 / totalIters)
                        taxonomyService.updateGenerationProgress(
                            GenerationProgress(
                                currentIteration = i,
                                totalIterations = totalIters,
                                currentStep = "Phase 3: Trickle Routing",
                                stepIndex = 1,
                                totalSteps = 5,
                                percentComplete = tricklePercent,
                                statusText = "Routing queries down parent-child nodes..."
                            )
                        )

                        val trickleTime = measureTimeMillis {
                            // Skip on the first iteration: the bootstrap step above already
                            // assigned every query to its ground-truth anchor with weight 1.0.
                            // Re-routing immediately via embedding-based trickle (even with the
                            // enableGtBias nudge) let queries drift onto merely-similar wrong
                            // anchors before any real structure existed, inflating some anchors
                            // several-fold over their true ground-truth size. Keeping the
                            // ground-truth assignment for the first split/optimize/refit pass and
                            // only starting trickle-based reassignment from iteration 2 removes
                            // the need for that bias entirely.
                            if (i > 1) {
                                ops.invalidateCachedJ()
                                ops.clearGraphQueries(root)
                                ops.reassignQueries(dagRoot, uniqueEmbs, groundTruthMap, i)
                            }
                        }
                        perfTracker.recordTime("construction.phase3_trickle", trickleTime, uniqueEmbs.size.toLong())
                        perfTracker.recordTime("construction.phase3_trickle@iter=$i", trickleTime, uniqueEmbs.size.toLong())
                        taxonomyService.notifyGraphUpdated()

                        var jBeforeEdits = taxonomy.utils.StatisticsUtils.computeDagSeparationJ(root, uniqueEmbs)
                        var drift = if (lastIterationJAfterRefit != null) jBeforeEdits - lastIterationJAfterRefit!! else 0.0

                        // ── REFIT GATE ──────────────────────────────────────────────────
                        // The composite (refit, re-route) has now been applied and its effect on
                        // J is exactly `drift`. Judge it by the same rule every structural edit
                        // faces: if it lowered J beyond the tolerance, restore the pre-refit
                        // parameters AND assignment — and then CONTINUE. A rejected proposal has
                        // never ended a run anywhere else in this system and must not here: a
                        // refit failing to help says nothing about whether a split would, and
                        // treating it as termination stops construction on a stunted tree (seen
                        // directly: rejecting at iteration 3 froze a two-iteration taxonomy that
                        // the fixed-point certificate then correctly refused to certify).
                        //
                        // Livelock is not possible while structural edits keep landing, because
                        // each accepted edit changes the structure and so changes the next refit
                        // proposal. When edits stop AND the refit is rejected, nothing in the
                        // loop can change anything, and the J-stationarity criterion below sees
                        // both deltas at zero and terminates.
                        //
                        // This closes the one exception to the framework's rule that every
                        // J-changing operation is measured. Without it the edit gate can raise J
                        // and the ungated re-route hand it straight back — observed at
                        // -4.67e-04, the same order as a median accepted split (+5.19e-04).
                        if (config.formalism.enableRefitGate &&
                            drift < -config.formalism.tau && refitBackup != null && refitRegistry != null) {
                            log.info(
                                "[REFIT REJECTED] Iteration $i | the refit and its re-route lowered J by " +
                                    "${"%.3e".format(java.util.Locale.US, -drift)} (tol " +
                                    "${"%.3e".format(java.util.Locale.US, config.formalism.tau)}). Restoring the " +
                                    "pre-refit parameters and assignment; continuing from there."
                            )
                            refitBackup!!.restore(refitRegistry!!)
                            root.updateAllShrinkages()
                            refitRejectedCount++
                            // J is back to the previous iteration's post-refit value by
                            // construction, so this iteration's edits are measured against that.
                            jBeforeEdits = lastIterationJAfterRefit!!
                            drift = 0.0
                        }

                        // Phase 4: Discover (Adaptive Splitting)
                        log.debug("Phase 4: Discovering emergent concepts (Splitting)...")
                        val splitPercent = 10.0 + ((i - 1).toDouble() / totalIters) * 80.0 + (3.0 / 5.0) * (80.0 / totalIters)
                        taxonomyService.updateGenerationProgress(
                            GenerationProgress(
                                currentIteration = i,
                                totalIterations = totalIters,
                                currentStep = "Phase 4: Adaptive Splitting",
                                stepIndex = 3,
                                totalSteps = 5,
                                percentComplete = splitPercent,
                                statusText = "Clustering density anomalies and splitting concepts..."
                            )
                        )

                        val splitTime = measureTimeMillis {
                            ops.splitNodesRecursive(dagRoot, uniqueEmbs, groundTruthMap, i)
                        }
                        perfTracker.recordTime("construction.phase4_split", splitTime, 1L)
                        perfTracker.recordTime("construction.phase4_split@iter=$i", splitTime, 1L)
                        taxonomyService.notifyGraphUpdated(true)

                        // Phase 5: Optimize (Structural Refinement)
                        log.debug("Phase 5: Optimizing hierarchy (Merging & Cross-linking)...")
                        val optimizePercent = 10.0 + ((i - 1).toDouble() / totalIters) * 80.0 + (4.0 / 5.0) * (80.0 / totalIters)
                        taxonomyService.updateGenerationProgress(
                            GenerationProgress(
                                currentIteration = i,
                                totalIterations = totalIters,
                                currentStep = "Phase 5: Hierarchy Optimization",
                                stepIndex = 4,
                                totalSteps = 5,
                                percentComplete = optimizePercent,
                                statusText = "Merging sibling domains and establishing cross-links..."
                            )
                        )

                        val optimizeTime = measureTimeMillis {
                            ops.optimizeHierarchy(dagRoot, uniqueEmbs, groundTruthMap, i, learningPhase = false)
                        }
                        perfTracker.recordTime("construction.phase5_optimize", optimizeTime, 1L)
                        perfTracker.recordTime("construction.phase5_optimize@iter=$i", optimizeTime, 1L)
                        taxonomyService.notifyGraphUpdated(true)

                        val jAfterEdits = taxonomy.utils.StatisticsUtils.computeDagSeparationJ(root, uniqueEmbs)
                        
                        // Final Refit after optimization
                        log.debug("Phase 2 Refit: Refitting bounds after optimization...")
                        val refitPercent = 10.0 + ((i - 1).toDouble() / totalIters) * 80.0 + (5.0 / 5.0) * (80.0 / totalIters)
                        taxonomyService.updateGenerationProgress(
                            GenerationProgress(
                                currentIteration = i,
                                totalIterations = totalIters,
                                currentStep = "Refit after Optimization",
                                stepIndex = 5,
                                totalSteps = 5,
                                percentComplete = refitPercent,
                                statusText = "Refitting vMF/NiW bounds after topology edits..."
                            )
                        )

                        // Snapshot before the refit so the gate at the next iteration's drift
                        // measurement can restore it. Captured here because this is the last
                        // point at which the pre-refit parameters and assignment coexist.
                        refitBackup = taxonomy.model.GraphStateBackup(root)
                        refitRegistry = buildMap {
                            val seen = mutableSetOf<String>()
                            fun walkReg(n: GraphNode) {
                                if (!seen.add(n.id)) return
                                put(n.id, n)
                                n.children.forEach { walkReg(it) }
                                n.crossLinkChildren.forEach { walkReg(it) }
                            }
                            walkReg(root)
                        }

                        preRefitTheta = refitRegistry!!.mapValues { (_, n) -> n.vmfMu.copyOf() to n.vmfKappa }

                        val refitTime = measureTimeMillis {
                            ops.fitNodeRecursive(root, currentIteration = i, isFinalIteration = (i == totalIters))
                            ops.invalidateCachedJ()
                        }

                        // How far the refit actually moved theta. 1 - cos on the direction, and a
                        // relative change on the concentration.
                        run {
                            var maxMu = 0.0
                            var maxKap = 0.0
                            for ((id, node) in refitRegistry!!) {
                                val (oldMu, oldKappa) = preRefitTheta[id] ?: continue
                                val d = minOf(oldMu.size, node.vmfMu.size)
                                if (d > 0) {
                                    var dot = 0.0; var na = 0.0; var nb = 0.0
                                    for (j in 0 until d) {
                                        dot += oldMu[j].toDouble() * node.vmfMu[j].toDouble()
                                        na += oldMu[j].toDouble() * oldMu[j].toDouble()
                                        nb += node.vmfMu[j].toDouble() * node.vmfMu[j].toDouble()
                                    }
                                    if (na > 1e-18 && nb > 1e-18) {
                                        val cos = (dot / (Math.sqrt(na) * Math.sqrt(nb))).coerceIn(-1.0, 1.0)
                                        maxMu = maxOf(maxMu, 1.0 - cos)
                                    }
                                }
                                if (oldKappa > 1e-12) {
                                    maxKap = maxOf(maxKap, kotlin.math.abs(node.vmfKappa - oldKappa) / oldKappa)
                                }
                            }
                            lastMaxMuDelta = maxMu
                            lastMaxKappaRel = maxKap
                        }
                        perfTracker.recordTime("construction.phase2_refit", refitTime, 1L)
                        perfTracker.recordTime("construction.phase2_refit@iter=$i", refitTime, 1L)
                        taxonomyService.notifyGraphUpdated()

                        // The refit is asserted to leave J untouched because J reads only
                        // queryWeights and the embeddings — never vmfMu or vmfKappa. That makes
                        // the M-step inert with respect to J, and means the parameter update can
                        // only move J indirectly, through the routing it drives next iteration.
                        // The whole composite E o S o M therefore has exactly one ungated J
                        // mover, E, which is where any damping has to act. Measure rather than
                        // assume: if this ever prints non-zero, the claim above is false and the
                        // termination discussion changes.
                        val jAfterRefit = if (config.diagnostics.enableProfiling) {
                            val measured = taxonomy.utils.StatisticsUtils.computeDagSeparationJ(root, uniqueEmbs)
                            val refitDelta = measured - jAfterEdits
                            if (kotlin.math.abs(refitDelta) > 1e-12) {
                                log.warn(
                                    "[REFIT-DELTA] Iteration $i | refit moved J by " +
                                        "${"%.3e".format(java.util.Locale.US, refitDelta)} — the M-step is NOT " +
                                        "inert with respect to J, contrary to the assumption in the descent analysis."
                                )
                            } else {
                                log.info("[REFIT-DELTA] Iteration $i | 0.000e+00 (M-step inert, as expected)")
                            }
                            measured
                        } else {
                            jAfterEdits
                        }
                        lastIterationJAfterRefit = jAfterRefit
                        lastTrickleDelta = drift
                        lastEditsDelta = jAfterEdits - jBeforeEdits
                        lastIterationRun = i
                        // Locale.US is required: the JVM runs under -Duser.language=fr, so a
                        // bare format() emits "0,265920" and every downstream parse of the J
                        // trajectory silently fails. Six decimals because the per-iteration
                        // deltas that reveal a split/route limit cycle are O(1e-5).
                        log.info(
                            "[J-TRACK] Iteration $i | J_after_trickle: ${"%.6f".format(java.util.Locale.US, jBeforeEdits)}" +
                                " (Trickle Delta: ${"%.6f".format(java.util.Locale.US, drift)})" +
                                " | J_after_edits: ${"%.6f".format(java.util.Locale.US, jAfterEdits)}" +
                                " (Edits Delta: ${"%.6f".format(java.util.Locale.US, jAfterEdits - jBeforeEdits)})"
                        )

                        // Diagnostic only — nothing reads this back into a decision. It reports the
                        // sampling resolution of J against the tolerance the gate actually uses,
                        // so that "accepted at dJ = 3.7e-5 under tau = 1e-6" can be judged as
                        // evidence or as noise.
                        if (config.diagnostics.enableProfiling) {
                            // How far each node's own fitted direction sits from its children's
                            // mass-weighted resultant. The descent-gate derivation assumes these
                            // coincide; the shortfall is exactly what descentMargin absorbs.
                            val cosines = mutableListOf<Double>()
                            run {
                                val seen = mutableSetOf<String>()
                                fun walkCos(n: GraphNode) {
                                    if (!seen.add(n.id)) return
                                    if (n.children.isNotEmpty() && !n.muResultantCosine.isNaN()) {
                                        cosines.add(n.muResultantCosine)
                                    }
                                    n.children.forEach { walkCos(it) }
                                }
                                walkCos(root)
                            }
                            if (cosines.isNotEmpty()) {
                                val sorted = cosines.sorted()
                                fun pct(p: Double) = sorted[(sorted.size * p).toInt().coerceAtMost(sorted.size - 1)]
                                log.info(
                                    "[MU-GAP] Iteration $i | internal nodes=${cosines.size}" +
                                        " cos(mu_v, resultant) min=${"%.4f".format(java.util.Locale.US, sorted.first())}" +
                                        " p10=${"%.4f".format(java.util.Locale.US, pct(0.10))}" +
                                        " median=${"%.4f".format(java.util.Locale.US, pct(0.50))}" +
                                        " max=${"%.4f".format(java.util.Locale.US, sorted.last())}"
                                )
                            }
                            val boot = taxonomy.utils.JBootstrap.estimate(root, uniqueEmbs)
                            val ratio = if (config.formalism.tau > 0.0) boot.seBoot / config.formalism.tau else Double.NaN
                            log.info(
                                "[J-RESOLUTION] Iteration $i | J=${"%.6f".format(java.util.Locale.US, boot.j)}" +
                                    " SE_boot=${"%.3e".format(java.util.Locale.US, boot.seBoot)}" +
                                    " (B=${boot.replicates})" +
                                    " | tau=${"%.3e".format(java.util.Locale.US, config.formalism.tau)}" +
                                    " SE/tau=${"%.1f".format(java.util.Locale.US, ratio)}" +
                                    " | 2*SE=${"%.3e".format(java.util.Locale.US, 2.0 * boot.seBoot)}"
                            )
                        }
                    }
                }

                log.info("Iteration $i completed in ${iterationTime}ms.")

                // Calculate and store iteration metrics
                if (config.execution.enableIterationMetrics) {
                    val iterMetrics = TaxonomyMetrics(root, groundTruthMap).generateReport()
                    taxonomyService.addIterationMetrics(reportToIterationMetrics("Iter $i", iterMetrics))
                }

                logNodeDiagnostics(root, distilledData.size)

                if (config.diagnostics.enableProfiling) {
                    dumpIterationSnapshot(root, i)
                }

                // Print intermediate DAG structure / changes to save log size
                val currentDagState = captureDagState(root)
                if (previousDagState == null) {
                    log.info("=== DAG after iteration $i ===")
                    ops.printHierarchyCompact(root)
                } else {
                    log.info("=== DAG Changes in iteration $i ===")
                    log.info(diffDagState(previousDagState!!, currentDagState, root))
                }
                previousDagState = currentDagState

                // Topology cycle detection
                val activeTopologyRepresentations = currentDagState.values.map { nodeState ->
                    nodeState.id + "<-" + nodeState.parents.sorted().joinToString(",") + "->" + nodeState.children.sorted().joinToString(",")
                }.sorted()
                val topologyHash = activeTopologyRepresentations.hashCode()
                
                val k = 10
                val cycleStartIndex = activeNodeHashes.lastIndexOf(topologyHash)
                if (cycleStartIndex != -1 && (activeNodeHashes.size - cycleStartIndex) <= k) {
                    val period = activeNodeHashes.size - cycleStartIndex
                    if (period >= 2) {
                        log.warn("[CYCLE DETECTED] Limit cycle of period $period detected at iteration $i! Same topology state recurred from iteration ${cycleStartIndex + 1}.")
                        if (config.execution.enableEarlyStopping) {
                            log.info("Early stopping triggered in iteration $i due to limit cycle detection.")
                            break
                        }
                    }
                }
                activeNodeHashes.add(topologyHash)

                log.info("=== PROPOSAL SUMMARY (ITERATION $i) ===")
                log.info(ops.proposalStats.summary())
                // Snapshot BEFORE clearing. recordIteration below reads these counts ~30
                // lines further down, by which point proposalStats has been reset — which
                // is why every attempted/accepted/rejected/no_proposal column in
                // iteration_metrics.csv was 0 while the file itself looked healthy. The
                // header-and-rows guard at bundle close cannot catch this: the rows exist,
                // they are just all zero.
                val iterAttempted = ops.proposalStats.attempted.values.sum()
                val iterAccepted = ops.proposalStats.accepted.values.sum()
                val iterRejected = ops.proposalStats.rejected.values.sum()
                val iterNoProposal = ops.proposalStats.noProposal.values.sum()
                ops.proposalStats.clear()
                
                // Phase 6: Stabilize Convergence Check
                //
                // Two criteria, reported jointly. GED asks whether the node and edge sets stopped
                // changing; J-stationarity asks whether the objective stopped changing. They are
                // not the same question, and GED is the weaker one: a structure can alternate
                // between 174 and 175 nodes for 44 iterations while J sits at 0.2659 +/- 4e-5,
                // which GED reads as perpetual churn and stationarity reads as converged.
                val stabilizationResult = stabilizer.evaluateConvergence(root, i)
                val jStationary = !lastEditsDelta.isNaN() && !lastTrickleDelta.isNaN() &&
                    kotlin.math.abs(lastEditsDelta) <= config.formalism.tau &&
                    kotlin.math.abs(lastTrickleDelta) <= config.formalism.tau
                jStationaryStreak = if (jStationary) jStationaryStreak + 1 else 0
                log.info(
                    "[CONVERGENCE] Iteration $i | GED converged=${stabilizationResult.isConverged}" +
                        " | J stationary=$jStationary (streak $jStationaryStreak/5," +
                        " editsDelta=${"%.3e".format(java.util.Locale.US, lastEditsDelta)}," +
                        " trickleDelta=${"%.3e".format(java.util.Locale.US, lastTrickleDelta)})"
                )

                // Second sink for the values just logged. This is the iteration hook that was
                // missing: the bundle wrote a header at open() and never a row, which is the
                // failure mode that looks like success — a valid file, a clean parse, no data.
                run {
                    val all = mutableListOf<GraphNode>()
                    val seen = mutableSetOf<String>()
                    fun walk(n: GraphNode) {
                        if (!seen.add(n.id)) return
                        all.add(n); n.children.forEach { walk(it) }
                    }
                    walk(root)
                    taxonomy.diagnostics.DiagnosticsBundle.recordIteration(
                        iter = i,
                        nodes = all.size,
                        leaves = all.count { it.isLeaf },
                        maxDepth = all.maxOfOrNull { it.depth } ?: 0,
                        jAfterRoute = lastIterationJAfterRefit ?: Double.NaN,
                        jAfterEdits = lastIterationJAfterRefit ?: Double.NaN,
                        trickleDelta = lastTrickleDelta,
                        editsDelta = lastEditsDelta,
                        // StabilizationResult reports GED as a single edit distance, not as
                        // separate add/remove counts; volumeDelta carries the signed size change.
                        gedAdd = stabilizationResult.ged,
                        gedRem = stabilizationResult.volumeDelta.toInt(),
                        attempted = iterAttempted,
                        accepted = iterAccepted,
                        rejected = iterRejected,
                        noProposal = iterNoProposal,
                        mass = all.sumOf { it.queryWeights.values.sum() },
                        wallMs = 0L
                    )
                }
                if (stabilizationResult.isConverged) {
                    log.info("Early stopping triggered in iteration $i due to convergence (GED quiescence).")
                    break
                }
                if (jStationaryStreak >= 5) {
                    log.info("Early stopping triggered in iteration $i due to convergence (J stationarity).")
                    break
                }
            }

            // ── FIXED-POINT CERTIFICATE ─────────────────────────────────────
            // The claim a reader actually needs is not that construction converges from every
            // starting point — it is that the artifact being frozen is a fixed point of the
            // construction operator: one more iteration would change nothing. That is checkable
            // at freeze time rather than provable in general, and it is currently satisfied but
            // never asserted anywhere.
            //
            // Both components must vanish. Edits delta = 0 means the structural gate accepted
            // nothing; trickle delta = 0 means re-routing under the final parameters reproduced
            // the same assignment. Only the pair certifies the composite E o S o M is stationary
            // — edits alone would miss the ungated routing step, which is the one operation in
            // the loop that moves J without a gate.
            run {
                val tol = config.formalism.tau
                // Theta tolerance is separate from tau: tau bounds a change in J, these bound a
                // change in the parameters that produce it. 1e-6 on (1 - cos) is roughly a
                // milliradian of direction change.
                val epsMu = 1e-6
                val epsKappa = 1e-6
                val editsOk = !lastEditsDelta.isNaN() && kotlin.math.abs(lastEditsDelta) <= tol
                val trickleOk = !lastTrickleDelta.isNaN() && kotlin.math.abs(lastTrickleDelta) <= tol
                val muOk = !lastMaxMuDelta.isNaN() && lastMaxMuDelta <= epsMu
                val kappaOk = !lastMaxKappaRel.isNaN() && lastMaxKappaRel <= epsKappa
                val certified = editsOk && trickleOk && muOk && kappaOk
                val line = "[FIXED-POINT] iteration=$lastIterationRun" +
                    " editsDelta=${"%.3e".format(java.util.Locale.US, lastEditsDelta)}" +
                    " trickleDelta=${"%.3e".format(java.util.Locale.US, lastTrickleDelta)}" +
                    " maxMuDelta=${"%.3e".format(java.util.Locale.US, lastMaxMuDelta)}" +
                    " maxKappaRel=${"%.3e".format(java.util.Locale.US, lastMaxKappaRel)}" +
                    " tol=${"%.3e".format(java.util.Locale.US, tol)}" +
                    " certified=$certified"
                if (certified) log.info(line) else log.warn("$line — the frozen artifact is NOT a fixed point")

                taxonomy.model.ExperimentOutputContext.activeBaseDir?.let { dir ->
                    runCatching {
                        java.io.File(dir, "fixed_point_certificate.txt").writeText(
                            buildString {
                                appendLine("Fixed-point certificate for the frozen construction artifact")
                                appendLine("===========================================================")
                                appendLine()
                                appendLine("final iteration : $lastIterationRun")
                                appendLine("edits delta     : ${"%.6e".format(java.util.Locale.US, lastEditsDelta)}")
                                appendLine("trickle delta   : ${"%.6e".format(java.util.Locale.US, lastTrickleDelta)}")
                                appendLine("max 1-cos(mu)   : ${"%.6e".format(java.util.Locale.US, lastMaxMuDelta)}")
                                appendLine("max rel d kappa : ${"%.6e".format(java.util.Locale.US, lastMaxKappaRel)}")
                                appendLine("tolerance (tau) : ${"%.6e".format(java.util.Locale.US, tol)}")
                                appendLine("tolerance (theta): ${"%.6e".format(java.util.Locale.US, epsMu)}")
                                appendLine("CERTIFIED       : $certified")
                                appendLine()
                                appendLine("Certified means one further iteration of the construction operator would")
                                appendLine("change nothing that the frozen artifact consists of: the structural gate")
                                appendLine("accepted no edit, re-routing reproduced the same partition, and the refit")
                                appendLine("moved no node's direction or concentration. The last of those matters")
                                appendLine("because held-out queries route through theta, so a certificate over")
                                appendLine("structure and objective alone would not cover the object being frozen.")
                                appendLine()
                                appendLine("This certifies THIS artifact. It is not a claim that the construction")
                                appendLine("loop terminates from an arbitrary starting point — it does not.")
                            }
                        )
                    }
                }
            }

            // ── FINALIZATION PHASE ──────────────────────────────────────────
            log.info("=== STARTING FINALIZATION PHASE ===")
            val finalizationTime = measureTimeMillis {
                // 1. Refit bounds after final structural changes
                ops.fitNodeRecursive(root, isFinalIteration = true)
            }
            log.info("Finalization phase completed in ${finalizationTime}ms.")

            if (config.execution.enableLabeling) {
                log.info("Performing post-pass labeling on all nodes.")
                taxonomyService.updateGenerationProgress(
                    GenerationProgress(
                        currentIteration = totalIters,
                        totalIterations = totalIters,
                        currentStep = "Post-Pass Labeling",
                        stepIndex = 1,
                        totalSteps = 1,
                        percentComplete = 95.0,
                        statusText = "Synthesizing descriptive labels using LLM..."
                    )
                )

                val postLabelTime = measureTimeMillis {
                    ops.generateLabelsPostPass(root) { current, total ->
                        taxonomyService.updateLabelingProgress(current, total)
                    }
                }
                perfTracker.recordTime("construction.post_labeling", postLabelTime, 1L)
                taxonomyService.notifyGraphUpdated()
            }

            assignQueryIds(root, config.formalism.enableStableQuestionIds)
            log.info("--- ${config.execution.numIterations}-Iteration Evolution Completed ---")
            ops.printHierarchy(root)

            
            // Final Exports
            if (config.execution.enableVisualization) {
                visualizer.exportForVisualization(root, groundTruthMap, "taxonomy_visualization.json")
            }

            // Log final performance report
            val perfReport = perfTracker.printReport()
            log.info(perfReport)

            taxonomyService.updateGenerationProgress(
                GenerationProgress(
                    currentIteration = totalIters,
                    totalIterations = totalIters,
                    currentStep = "Complete",
                    stepIndex = 1,
                    totalSteps = 1,
                    percentComplete = 100.0,
                    statusText = "Taxonomy DAG generation completed successfully!"
                )
            )

            // GENERATE ARCHITECTURAL REPORT
            if (config.execution.enableFinalMetrics) {
                val finalReport = TaxonomyMetrics(root, groundTruthMap)
                val report = finalReport.generateReport()
                finalReport.printReport(config, report)
                taxonomyService.addIterationMetrics(reportToIterationMetrics("Final", report))
            }
            
            return@coroutineScope root
        } finally {
            taxonomyService.clearGenerationProgress()
        }
    }



    private fun gatherAllEmbeddingsInBranch(node: GraphNode, visited: MutableSet<String> = mutableSetOf()): List<Embedding> {
        if (visited.contains(node.id)) return emptyList()
        visited.add(node.id)

        val result = mutableListOf<Embedding>()
        result.addAll(node.queries) // Add local data (leaf data or parent residuals)
        node.treeChildren.forEach { result.addAll(gatherAllEmbeddingsInBranch(it, visited)) }
        return result
    }

    fun clearFitPhases(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
        log.debug("Clearing fit phases for ${node.label} (phase was ${node.phaseCompleted})")
        if (!visited.add(node.id)) return
        // Keep only SPLIT_EVAL and EMBEDDED, clear VMF_FIT(2), NIW_FIT(8), OPTIMIZED(16)
        node.phaseCompleted = node.phaseCompleted and (PHASE_SPLIT_EVAL or PHASE_EMBEDDED)
        node.treeChildren.forEach { clearFitPhases(it, visited) }
        node.crossLinkChildren.forEach { clearFitPhases(it, visited) }
    }

    private fun captureDagState(root: GraphNode): Map<String, NodeState> {
        val stateMap = mutableMapOf<String, NodeState>()
        fun walk(n: GraphNode, visited: MutableSet<String>) {
            if (!visited.add(n.id)) return
            stateMap[n.id] = NodeState(
                id = n.id,
                label = n.label,
                depth = n.depth,
                isLeaf = n.isLeaf,
                parents = n.parents.map { it.id }.toSet(),
                children = n.children.map { it.id }.toSet(),
                kappa = n.vmfKappa,
                directQueries = n.queries.size,
                totalQueries = n.getRecursiveQueryCount()
            )
            n.children.forEach { walk(it, visited) }
            n.crossLinkChildren.forEach { walk(it, visited) }
        }
        walk(root, mutableSetOf())
        return stateMap
    }

    private fun diffDagState(prev: Map<String, NodeState>, curr: Map<String, NodeState>, root: GraphNode): String {
        val sb = StringBuilder()
        sb.append("┌── TAXONOMY CHANGES (WITH CONTEXT) ────────────────────────────\n")

        val addedIds = curr.keys - prev.keys
        val removedIds = prev.keys - curr.keys
        val commonIds = prev.keys intersect curr.keys

        // Compute diff for each node
        val diffs = mutableMapOf<String, NodeDiff>()
        addedIds.forEach { id ->
            val state = curr[id]!!
            diffs[id] = NodeDiff(id, state.label, isAdded = true, isRemoved = false, isMutated = false, emptyList(), state)
        }
        removedIds.forEach { id ->
            val state = prev[id]!!
            diffs[id] = NodeDiff(id, state.label, isAdded = false, isRemoved = true, isMutated = false, emptyList(), null)
        }
        commonIds.forEach { id ->
            val p = prev[id]!!
            val c = curr[id]!!
            val details = mutableListOf<String>()
            if (p.isLeaf != c.isLeaf) {
                details.add("type changed: ${if (p.isLeaf) "Leaf" else "Parent"} -> ${if (c.isLeaf) "Leaf" else "Parent"}")
            }
            if (p.label != c.label) {
                details.add("label updated: \"${p.label}\" -> \"${c.label}\"")
            }
            if (p.parents != c.parents) {
                val addedParents = c.parents - p.parents
                val removedParents = p.parents - c.parents
                val parentChanges = mutableListOf<String>()
                if (addedParents.isNotEmpty()) {
                    parentChanges.add("added parents: " + addedParents.map { curr[it]?.label ?: it }.joinToString(", "))
                }
                if (removedParents.isNotEmpty()) {
                    parentChanges.add("removed parents: " + removedParents.map { prev[it]?.label ?: it }.joinToString(", "))
                }
                details.add("relationships updated (" + parentChanges.joinToString("; ") + ")")
            }

            diffs[id] = NodeDiff(id, c.label, isAdded = false, isRemoved = false, isMutated = details.isNotEmpty(), details, c)
        }

        // Find closest surviving ancestor in curr for each removed node
        val removedChildren = mutableMapOf<String, MutableList<NodeDiff>>()
        removedIds.forEach { rId ->
            val rDiff = diffs[rId]!!
            val parentId = findClosestSurvivingAncestor(rId, prev, curr) ?: root.id
            removedChildren.getOrPut(parentId) { mutableListOf() }.add(rDiff)
        }

        // Check recursively if a node has changes in its subtree
        val memoHasChanges = mutableMapOf<String, Boolean>()
        fun hasChangesInSubtree(nodeId: String): Boolean {
            memoHasChanges[nodeId]?.let { return it }
            // In-progress guard: a cycle in the captured state must not recurse
            // forever (StackOverflowError at iteration 35, seed 2048) — treat a
            // back-edge as "no additional changes" until the node's own result lands.
            memoHasChanges[nodeId] = false
            val diff = diffs[nodeId]
            val selfChanged = diff != null && (diff.isAdded || diff.isMutated)
            val hasRemoved = removedChildren.containsKey(nodeId)
            var childrenChanged = false
            val nodeState = curr[nodeId]
            if (nodeState != null) {
                for (childId in nodeState.children) {
                    if (hasChangesInSubtree(childId)) {
                        childrenChanged = true
                    }
                }
            }
            val result = selfChanged || hasRemoved || childrenChanged
            memoHasChanges[nodeId] = result
            return result
        }

        // If root has no changes in its subtree, return no changes
        if (!hasChangesInSubtree(root.id)) {
            sb.append("│   (No structural changes in this iteration)\n")
            sb.append("└──────────────────────────────────────────────────────────")
            return sb.toString()
        }

        // Build tree recursively
        fun buildTree(
            nodeId: String,
            prefix: String,
            isTail: Boolean,
            visited: MutableSet<String>
        ) {
            val diff = diffs[nodeId]
            val state = curr[nodeId] ?: return
            val cross = if (visited.contains(nodeId)) " [CROSS-LINK]" else ""
            
            val type = if (state.isLeaf) "Leaf" else "Parent"
            val nodeLabel = when {
                diff?.isAdded == true -> "[ADDED] \"${state.label}\" ($type, kappa: ${"%.1f".format(java.util.Locale.US, state.kappa)}, q=${state.directQueries}/${state.totalQueries})"
                diff?.isMutated == true -> "[MUTATED] \"${state.label}\" ($type, kappa: ${"%.1f".format(java.util.Locale.US, state.kappa)}, q=${state.directQueries}/${state.totalQueries}) -> ${diff.mutationDetails.joinToString(", ")}"
                else -> "\"${state.label}\" ($type, q=${state.directQueries}/${state.totalQueries})"
            }

            val connector = if (state.depth == 0) "" else if (isTail) "└── " else "├── "
            sb.append(prefix).append(connector).append(nodeLabel).append(cross).append("\n")

            if (!visited.add(nodeId)) return

            // Gather children to print
            val childrenToPrint = mutableListOf<PrintItem>()
            state.children.forEach { childId ->
                if (hasChangesInSubtree(childId)) {
                    val childState = curr[childId]!!
                    childrenToPrint.add(PrintItem.Surviving(childState))
                }
            }
            removedChildren[nodeId]?.forEach { rDiff ->
                childrenToPrint.add(PrintItem.Removed(rDiff))
            }

            for (i in 0 until childrenToPrint.size) {
                val item = childrenToPrint[i]
                val childIsTail = i == childrenToPrint.size - 1
                val nextPrefix = prefix + if (state.depth == 0) "" else if (isTail) "    " else "│   "
                
                when (item) {
                    is PrintItem.Surviving -> {
                        buildTree(item.state.id, nextPrefix, childIsTail, visited)
                    }
                    is PrintItem.Removed -> {
                        val rConnector = if (childIsTail) "└── " else "├── "
                        sb.append(nextPrefix).append(rConnector).append("[REMOVED] \"${item.diff.label ?: item.diff.id}\"\n")
                    }
                }
            }
        }

        buildTree(root.id, "│ ", true, mutableSetOf())

        sb.append("└──────────────────────────────────────────────────────────")
        return sb.toString()
    }

    private fun findClosestSurvivingAncestor(rId: String, prev: Map<String, NodeState>, curr: Map<String, NodeState>): String? {
        val visited = mutableSetOf<String>()
        val queue = java.util.ArrayDeque<String>()
        queue.add(rId)
        visited.add(rId)
        
        while (queue.isNotEmpty()) {
            val currentId = queue.removeFirst()
            val state = prev[currentId] ?: continue
            for (parentId in state.parents) {
                if (parentId in curr) {
                    return parentId
                }
                if (visited.add(parentId)) {
                    queue.addLast(parentId)
                }
            }
        }
        return null
    }

    private fun logNodeDiagnostics(root: GraphNode, totalCorpusSize: Int) {
        val allNodes = mutableListOf<GraphNode>()
        fun walk(n: GraphNode, visited: MutableSet<String>) {
            if (!visited.add(n.id)) return
            allNodes.add(n)
            n.children.forEach { walk(it, visited) }
        }
        walk(root, mutableSetOf())

        val totalNodes = allNodes.size
        val leafCount = allNodes.count { it.children.isEmpty() }
        val totalLocalMass = allNodes.sumOf { it.queryWeights.values.sum() }

        log.info(String.format(
            java.util.Locale.US,
            "=== DAG DIAGNOSTICS | Nodes: %d (%d leaves, %d internal) | Total Mass: %.2f ===",
            totalNodes, leafCount, totalNodes - leafCount, totalLocalMass
        ))

        for (n in allNodes) {
            val localMass = n.queryWeights.values.sum()
            val localESS = if (localMass > 0.0) (localMass * localMass / n.queryWeights.values.sumOf { it * it }) else 0.0
            
            // Region effect (sum of weights in the subtree)
            val regionWeights = mutableMapOf<String, Double>()
            val subVisited = mutableSetOf<String>()
            fun subWalk(curr: GraphNode) {
                if (!subVisited.add(curr.id)) return
                for ((q, w) in curr.queryWeights) {
                    regionWeights[q] = (regionWeights[q] ?: 0.0) + w
                }
                curr.treeChildren.forEach { subWalk(it) }
                curr.crossLinkChildren.forEach { subWalk(it) }
            }
            subWalk(n)
            val regionEff = regionWeights.values.sum()

            val isLeaf = n.children.isEmpty()
            val queriesSize = n.queries.size

            if (log.isDebugEnabled) {
                log.debug(String.format(
                    java.util.Locale.US,
                    "Node ID: %s | Depth: %d | Leaf: %b | localMass: %.2f | localESS: %.2f | regionEff: %.2f | queriesSize: %d",
                    n.id, n.depth, isLeaf, localMass, localESS, regionEff, queriesSize
                ))
            }

            // Invariant Check Warnings
            if (regionEff > totalCorpusSize + 1e-4) {
                log.warn("WARNING: Node ${n.id} (${n.label}) violates C1/C4! regionEff ($regionEff) > totalCorpusSize ($totalCorpusSize).")
            }
            if (!isLeaf && n.queries.isNotEmpty() && n.residualQueries.isEmpty()) {
                log.warn("WARNING: Internal Node ${n.id} (${n.label}) violates C3! Has non-empty hard queries size ($queriesSize) but empty residualQueries.")
            }
        }
    }

    /**
     * Appends one JSON line per iteration to `dag_snapshots.jsonl` in the active experiment
     * output dir: the full node list with enough fields (id, label, depth, parent/child ids,
     * kappa, direct/residual/subtree query counts) to reconstruct topology, detect single-child
     * chains, and inspect query repartition per iteration without re-parsing the text log's
     * diff-only iteration entries (only iteration 1 and the final state get a full text dump;
     * everything in between is a diff). One line = one iteration = independently parseable.
     */
    private fun dumpIterationSnapshot(root: GraphNode, iteration: Int) {
        val baseDir = ExperimentOutputContext.activeBaseDir ?: File(".")
        val outFile = File(baseDir, "dag_snapshots.jsonl")
        try {
            outFile.parentFile?.mkdirs()
            val allNodes = mutableListOf<GraphNode>()
            val visited = mutableSetOf<String>()
            fun walk(n: GraphNode) {
                if (!visited.add(n.id)) return
                allNodes.add(n)
                n.children.forEach { walk(it) }
                n.crossLinkChildren.forEach { walk(it) }
            }
            walk(root)

            fun esc(s: String?) = (s ?: "").replace("\\", "\\\\").replace("\"", "\\\"")

            val sb = StringBuilder()
            sb.append("{\"iteration\":").append(iteration).append(",\"nodes\":[")
            allNodes.forEachIndexed { idx, n ->
                if (idx > 0) sb.append(",")
                sb.append("{")
                sb.append("\"id\":\"").append(esc(n.id)).append("\",")
                sb.append("\"label\":\"").append(esc(n.label)).append("\",")
                sb.append("\"depth\":").append(n.depth).append(",")
                sb.append("\"isLeaf\":").append(n.isLeaf).append(",")
                sb.append("\"isBridge\":").append(n.isBridge).append(",")
                sb.append("\"kappa\":").append(String.format(java.util.Locale.US, "%.4f", n.vmfKappa)).append(",")
                sb.append("\"directQueries\":").append(n.queries.size).append(",")
                sb.append("\"residualQueries\":").append(n.residualQueries.size).append(",")
                sb.append("\"subtreeQueries\":").append(n.getRecursiveQueryCount()).append(",")
                sb.append("\"parentIds\":[").append(n.parents.joinToString(",") { "\"${esc(it.id)}\"" }).append("],")
                sb.append("\"childIds\":[").append(n.children.joinToString(",") { "\"${esc(it.id)}\"" }).append("],")
                // vmfMu, the node's direction on the sphere. Without it a snapshot cannot be
                // compared to another run's snapshot at all: matching leaves ACROSS SEEDS needs a
                // shared space, and every proxy fails. Query-set overlap is meaningless when each
                // seed draws a different held-out split, and recomputing centroids from member
                // embeddings requires the embedding cache, its exact byte order, and the router's
                // assignments — three external dependencies for a quantity the node already holds.
                // Emitted at 6 dp: mu is unit-norm, so that is well inside float32 precision.
                sb.append("\"vmfMu\":[").append(
                    n.vmfMu.joinToString(",") { String.format(java.util.Locale.US, "%.6f", it) }
                ).append("],")
                sb.append("\"sliceDim\":").append(n.sliceDim)
                sb.append("}")
            }
            sb.append("]}")

            outFile.appendText(sb.toString() + "\n")
        } catch (e: Exception) {
            log.warn("Failed to write DAG snapshot for iteration $iteration: ${e.message}")
        }
    }
}

private data class NodeState(
    val id: String,
    val label: String?,
    val depth: Int,
    val isLeaf: Boolean,
    val parents: Set<String>,
    val children: Set<String>,
    val kappa: Double,
    val directQueries: Int,
    val totalQueries: Int
)

private data class NodeDiff(
    val id: String,
    val label: String?,
    val isAdded: Boolean,
    val isRemoved: Boolean,
    val isMutated: Boolean,
    val mutationDetails: List<String>,
    val state: NodeState?
)

private sealed class PrintItem {
    data class Surviving(val state: NodeState) : PrintItem()
    data class Removed(val diff: NodeDiff) : PrintItem()
}
