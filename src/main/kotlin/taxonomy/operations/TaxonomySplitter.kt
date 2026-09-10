package taxonomy.operations

import dev.langchain4j.model.chat.request.json.JsonObjectSchema
import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.model.*
import taxonomy.prompts.TaxoPrompts
import taxonomy.utils.StatisticsUtils
import kotlin.math.sqrt

/**
 * Implements Phase 4: Discover (Adaptive Splitting).
 * Splits nodes using k-ary vMF-k-Means (k selected by Dasgupta marginal improvement)
 * and validates them using the Dasgupta Cost Delta.
 */
@Service
class TaxonomySplitter(
    private val config: TaxonomyConfig,
    private val llmClient: TaxonomyLlmClient,
    private val datasetFetcher: MMLUDatasetFetcher,
    private val fitter: TaxonomyFitter
) {
    private val log = LoggerFactory.getLogger("taxonomy.Splitter")
    private val conceptCounter = java.util.concurrent.atomic.AtomicInteger(1)

    private var currentLimit = config.execution.llmParallelism
    private var llmSemaphore = Semaphore(currentLimit)

    private fun checkAndSyncSemaphore() {
        val limit = config.execution.llmParallelism
        if (limit != currentLimit) {
            log.info("Updating splitter semaphore capacity from $currentLimit to $limit")
            currentLimit = limit
            llmSemaphore = Semaphore(limit.coerceAtLeast(1))
        }
    }

    fun resetConceptCounter() {
        conceptCounter.set(1)
    }

    // Note: all production splitting goes through TaxonomyOperations.splitNodesRecursive,
    // which wraps each node in tryProposal so every edit is gated on dJ. Do not add an
    // ungated bulk-split entry point here — it would commit splits without the global
    // acceptance test.

    /**
     * [forcedK] non-null runs the mixture search at EXACTLY that k instead of letting
     * performVmfKMeans pick one. Every downstream gate is unchanged: floor absorption,
     * weak-pair coarsening, the routed min-pair bar. A forced candidate is therefore
     * not privileged — it still has to survive everything a self-selected one does,
     * and coarsening may reduce it below k before it gets there.
     */
    suspend fun splitSingleNode(node: GraphNode, forcedK: Int? = null, currentIteration: Int = -1): Boolean {
        if (!node.isLeaf) return false
        val localWeights = node.queryWeights
        val mass = taxonomy.utils.orderedSum(localWeights)
        val ess = if (mass > 0.0) (mass * mass / taxonomy.utils.orderedSumOf(localWeights) { it * it }) else 0.0
        val threshold = 2 * config.formalism.minClusterSize
        if (mass < threshold || ess < threshold) return false

        if (node.depth >= config.formalism.maxDepth) {
            log.debug("Split Boundary: '${node.label}' reached max depth (${config.formalism.maxDepth}). Preventing split.")
            return false
        }

        val isDiffuse = node.vmfKappa < 0.5 && mass < 10 * config.formalism.minClusterSize
        if (isDiffuse) {
            var viable = false
            if (config.formalism.enableResidualSplitGate) {
                val minClusterSize = config.formalism.minClusterSize
                val allSubtreeQueries = node.getAllQueriesInRegion()
                val residualEmbeddings = allSubtreeQueries.filter { emb ->
                    val qId = if (emb.queryId != -1) emb.queryId.toString() else emb.rawText
                    qId in node.residualQueries
                }
                
                if (residualEmbeddings.size >= minClusterSize) {
                    val resDim = node.sliceDim
                    val resStats = clusterStats(residualEmbeddings, resDim)

                    // Residual cluster is viable iff it separates from every sibling on
                    // the same chance-corrected scale that gates splits and merges.
                    val siblings = node.parents.flatMap { it.children }.filter { it.id != node.id }
                    viable = siblings.isEmpty() || siblings.all { sib ->
                        val sibQueries = sib.getAllQueriesInBranch().distinctBy { it.rawText }
                        if (sibQueries.isEmpty()) true
                        else {
                            val sep = StatisticsUtils.chanceCorrectedSeparation(
                                listOf(resStats, clusterStats(sibQueries, resDim))
                            )
                            sep >= barFor(config, node)
                        }
                    }
                }
            }
            
            if (!viable) {
                log.debug("Split Skipped: '${node.label}' kappa=${node.vmfKappa} too diffuse.")
                return false
            } else {
                log.debug("Split Allowed via Residual Viability Gate: '${node.label}' is diffuse but has coherent residual cluster.")
            }
        }

        // Stable input order: queryWeights is a ConcurrentHashMap, whose key iteration
        // order varies run-to-run with parallel insertion history. EM/PCA consume this
        // list order (floating-point sums, argmax ties), so an unstable order breaks
        // seed reproducibility at decision boundaries. Sort by queryId (rawText fallback).
        val targetQueries = (if (isDiffuse && config.formalism.enableResidualSplitGate) {
            val allSubtreeQueries = node.getAllQueriesInRegion()
            allSubtreeQueries.filter { emb ->
                val qId = if (emb.queryId != -1) emb.queryId.toString() else emb.rawText
                qId in node.residualQueries
            }.ifEmpty { localWeights.keys.mapNotNull { GraphNode.getEmbedding(it) } }
        } else {
            localWeights.keys.mapNotNull { GraphNode.getEmbedding(it) }
        }).sortedWith(compareBy({ it.queryId }, { it.rawText }))

        log.debug("Scanning '${node.label}' (${targetQueries.size} q) for split...")

        val childDim =  dimForDepth(node.depth + 1)
        val minClusterSize = config.formalism.minClusterSize

        val rawVectors = targetQueries.map { it.projectTo(childDim) }

        val splitDim = when {
            targetQueries.size < 100 -> 32
            targetQueries.size < 500 -> 64
            else                    -> 128
        }.coerceAtMost(rawVectors.first().size)

        // Memoised on exact input content: the k = 2..4 fallback loop re-enters here with
        // the same node and population, and only `forcedK` differs (see pcaProjectMemo).
        val pcaProjected = StatisticsUtils.pcaProjectMemo(
            rawVectors, splitDim,
            dropTop = config.formalism.splitDropTopPcs,
            whiten = config.formalism.splitWhiten
        )

        // ── k-ary mixture selection ───────────────────────────────────────────
        //
        // KNOWN REMAINING COUPLING. proposalSeparationBar is passed below as
        // `marginalEps` while also serving as the min-pair bar further down, and the
        // two are different quantities:
        //   marginalEps  — "how much must cluster k+1 ADD?"  a DIFFERENCE of separations
        //   min-pair bar — "is every pair distinct?"          a LEVEL
        // One constant, two meanings. Removing the k-way gate took this overload from
        // three jobs to two; this is the half that remains.
        //
        // The consequence is that k is chosen by a threshold rather than by the
        // objective, and the coarsening loop below can then change k again — so the k
        // that EM selects is not the k that reaches the gates. (Which is exactly why
        // the diagnostics now report both, as k= and emK=.)
        //
        // The clean fix is to emit every k candidate and let dJ select, but that costs
        // 3x the re-routes and bootstraps per proposing node, so it is deliberately
        // not done. The cheaper variant if it is ever worth revisiting: rank the
        // candidates by local separation and evaluate dJ on the top two only.
        val minClusterFrac = minClusterSize.toDouble() / targetQueries.size
        // Negative marginalEps means "not set" -> keep the historical coupling.
        val marginal = config.formalism.marginalEps.let {
            if (it >= 0.0) it else barFor(config, node)
        }

        // No separate maxK=2 probe is needed before this call: runVmfEm has NO
        // randomness (mu_1 is the normalized centroid, mu_2..k deterministic
        // farthest-point maximin), so performVmfKMeans evaluates k=2 identically at
        // any maxK and returns null exactly when a k=2 probe would.
        // Forcing k: cap maxK at k and drive marginalEps negative so every increment
        // up to k is taken, which makes performVmfKMeans return exactly k rather than
        // its own choice. Without the negative eps it would still stop early at the
        // increment test and the "forced" candidate would silently be a smaller one.
        val mixture = StatisticsUtils.performVmfKMeans(
            embeddings = pcaProjected,
            d = splitDim,
            maxK = forcedK ?: config.formalism.maxK,
            minClusterFrac = minClusterFrac,
            marginalEps = if (forcedK != null) -1.0e9 else marginal
        )

        if (mixture == null) {
            log.debug("Split Failed: k-means collapsed for '${node.label}'.")
            return false
        }

        val k = mixture.components.size

        // ── Hard-assign queries to EM clusters (proposal only) ───────────────
        val clusters = Array(k) { mutableListOf<Embedding>() }

        for (i in targetQueries.indices) {
            val resp = mixture.responsibilities[i]
            val best = resp.indices.maxByOrNull { resp[it] } ?: 0
            clusters[best].add(targetQueries[i])
        }

        // ── EM floor pre-check (cheap early-out before any 256-dim work) ──────
        if (clusters.any { it.size < minClusterSize }) {
            log.debug("Split Floor Rejected: a cluster is below minClusterSize=$minClusterSize (sizes: ${clusters.map { it.size }}).")
            return false
        }

        // ── Fit proposal vMFs, then re-assign in ROUTING geometry ────────────
        // EM clustering in the PCA subspace only *proposes* children; from the next
        // iteration onward each child's population is decided by the trickler's
        // level-local vMF posterior at fitDim. Populating and gating the split with
        // the clustering assignment let children be born with >= minClusterSize
        // queries that routing immediately took away — pruned as starved within 1-2
        // iterations, driving a permanent split/prune oscillation (~60 spawned/~40
        // pruned per iteration, 63% of pruned nodes dead within 2 iterations of
        // birth). Assigning here with the same posterior the trickler applies makes
        // the birth state a routing fixed point at this level: a split only happens
        // if routing will sustain every child it creates.
        fun routeToVmfs(vmfs: List<StatisticsUtils.VmfParameters>): List<MutableList<Embedding>> {
            val out = List(vmfs.size) { mutableListOf<Embedding>() }
            // SHARED kappa, no per-child normalizer — matching TaxonomyTrickler's
            // `meanKappa * dots[i]` exactly. The per-child density form
            // (`vmf.logNormalizer + vmf.kappa * dot`) must NOT be used here: it lets a
            // concentrated sibling absorb a diffuse one's queries on concentration
            // bookkeeping rather than on direction, and the check this feeds is routing
            // sustainability — it must re-assign with the SAME level-local posterior
            // the trickler uses, or it is asking whether the children survive under a
            // router the tree does not use.
            //
            // meanKappa is a positive constant across children, so it cannot change
            // the argmax; it is kept only so this line reads identically to the
            // trickler's and cannot drift from it silently.
            val meanKappa = vmfs.map { it.kappa }.average().coerceAtLeast(1e-9)
            for (q in targetQueries) {
                val x = q.projectTo(childDim)
                var best = 0
                var bestScore = Double.NEGATIVE_INFINITY
                for (idx in vmfs.indices) {
                    val score = meanKappa * StatisticsUtils.dotProduct(x, vmfs[idx].mu)
                    if (score > bestScore) {
                        bestScore = score
                        best = idx
                    }
                }
                out[best].add(q)
            }
            return out
        }

        var activeVmfs = clusters.map { cluster -> fitVmfParams(cluster, childDim) }
        var routedClusters = routeToVmfs(activeVmfs)

        // ── Constrained k: project the proposal onto the routing-feasible set ─
        // EM's k is an unconstrained separation argmax; under the routed re-
        // assignment the partition of a large coherent node routinely lands as
        // "m sustainable clusters + tiny fragments" (observed: History
        // [147,164,1,28], Engineering [306,193,120,25]), and the all-or-nothing
        // floor check vetoed the entire split forever. Instead of discarding the
        // proposal, absorb under-floor fragments by DROPPING their components and
        // re-routing every query among the survivors — the same winner-take-all
        // vMF posterior, so no query is force-assigned anywhere. Each pass
        // removes >= 1 component, terminating at k' >= 2 or rejection. Nothing
        // is forced: the resulting coarser partition must still clear the SAME
        // acceptance bar below (floor, chance-corrected separation on the routed
        // partition, sibling distinctness); an incoherent merge fails separation
        // and dies exactly as before.
        // Flat bar, positioned BETWEEN two nulls. Both are measured by driving this
        // very function on synthetic clouds (SeparationNullBySizeTest); the curve is
        // tabulated in docs/separation_null_by_size.md.
        //
        //   isotropic null  p95 = 0.0055 .. 0.0093 over n = 75..900   ("more than nothing?")
        //   this bar             0.025
        //   within-node null p50 = 0.0396 at n = 406 (Philosophy)       ("more than elongation?")
        //
        // The gap matters. J is a scatter-reduction criterion with a random-partition
        // correction, so cutting an elongated UNIMODAL cloud along its principal axis
        // scores well above the isotropic null without any discrete structure being
        // present. Dropping the bar to the isotropic floor would therefore admit
        // anisotropy-carving, and no amount of resampling confidence on dJ would catch
        // it — dJ rewards exactly the thing being mistaken for structure. The bar is
        // the only gate that asks the second question.
        //
        // Flat rather than a function of n because the size effect is small and
        // two-regime: for n >= 160 the null is a clean quantile decaying 0.0090 ->
        // 0.0055 (1.64x over a 5.6x span of n); below n ~ 160 minClusterFrac does the
        // rejecting (at n = 75, EM collapses on 94% of structureless clouds before the
        // statistic is computed) and the measured p95 there is censored, not small.
        // One constant at the curve's maximum is conservative across the whole range.
        //
        // One flat bar for every proposal, regardless of node size. (A small-node
        // margin that doubled the bar below 2*minClusterSize is unreachable here: the
        // feasibility check at the top of this function already requires
        // mass >= 2*minClusterSize.)
        val requiredEps = barFor(config, node)

        // ── Stabilize the proposal onto the feasible set ─────────────────────
        // Two coarsening moves, both of which strictly reduce k and re-route with
        // the same winner-take-all vMF posterior (no query is force-assigned):
        //  1) FLOOR: an under-floor fragment's component is dropped and its mass
        //     re-routes among the survivors (History [147,164,1,28] -> k=2).
        //  2) GATE CONSISTENCY (weak pair): if any routed PAIR falls below the
        //     same pairwise bar the sibling-merger fuses at, the pair is merged
        //     and re-routed. Gating on the JOINT k-way separation alone would not
        //     do: a k=4 partition with joint sep 0.06 can contain a pair at 0.015,
        //     which the sibling-merger then immediately fuses — a split/fuse limit
        //     cycle. Creation and destruction must read the same statistic at the
        //     same granularity and bar, so their acceptance regions are disjoint
        //     by construction.
        while (true) {
            if (routedClusters.any { it.size < minClusterSize }) {
                if (routedClusters.size <= 2) break
                val survivors = routedClusters.filter { it.size >= minClusterSize }
                if (survivors.size < 2) break
                log.debug("Split fallback: absorbing under-floor fragments (routed sizes: ${routedClusters.map { it.size }}, floor=$minClusterSize), k ${routedClusters.size} -> ${survivors.size}")
                activeVmfs = survivors.map { cluster -> fitVmfParams(cluster, childDim) }
                routedClusters = routeToVmfs(activeVmfs)
                continue
            }
            val stats = routedClusters.map { clusterStats(it, childDim) }
            var weakI = -1
            var weakJ = -1
            var weakSep = Double.MAX_VALUE
            for (i in stats.indices) {
                for (j in i + 1 until stats.size) {
                    val sep = StatisticsUtils.chanceCorrectedSeparation(listOf(stats[i], stats[j]))
                    if (sep < weakSep) {
                        weakSep = sep
                        weakI = i
                        weakJ = j
                    }
                }
            }
            if (weakI >= 0 && weakSep < requiredEps && routedClusters.size > 2) {
                log.debug("Split fallback: pair sep ${"%.4f".format(java.util.Locale.US, weakSep)} < ${"%.4f".format(java.util.Locale.US, requiredEps)}, coarsening k ${routedClusters.size} -> ${routedClusters.size - 1}")
                val mergedClusters = mutableListOf<MutableList<Embedding>>()
                for (idx in routedClusters.indices) {
                    if (idx == weakJ) continue
                    if (idx == weakI) {
                        mergedClusters.add((routedClusters[weakI] + routedClusters[weakJ]).toMutableList())
                    } else {
                        mergedClusters.add(routedClusters[idx])
                    }
                }
                activeVmfs = mergedClusters.map { cluster -> fitVmfParams(cluster, childDim) }
                routedClusters = routeToVmfs(activeVmfs)
                continue
            }
            break
        }

        if (routedClusters.any { it.size < minClusterSize }) {
            // [NO-SPLIT] is the instrumentation for the no-proposal path. Without the
            // measured value the sweep only shows THAT a node did not split, not whether
            // it was a near-miss at the bar or genuinely atomic — which is the difference
            // between "lower the bar" and "this domain has one large concept".
            log.info(
                "[NO-SPLIT] '${node.label}' reason=not-routing-sustainable" +
                    " k=${routedClusters.size} sizes=${routedClusters.map { it.size }} floor=$minClusterSize"
            )
            taxonomy.diagnostics.DiagnosticsBundle.recordProposal(
                iter = currentIteration, type = "GROW", siteId = node.id, siteLabel = node.label,
                dJ = null, seDJ = null, z = null, dV = null,
                decision = "NO_PROPOSAL",
                // Carry the binding value: min_child against the floor is what distinguishes
                // a near-miss at the bar from a genuinely atomic node.
                reason = "not_routing_sustainable(min_child=${routedClusters.minOf { it.size }}" +
                    ",floor=$minClusterSize,k=${routedClusters.size})",
                nSite = node.queryWeights.size
            )
            return false
        }

        // Refit each child on the population routing actually gives it
        val childVmfs = routedClusters.map { cluster -> fitVmfParams(cluster, childDim) }

        // ── k-way separation validation on the ROUTED partition ──────────────
        val sepScore = StatisticsUtils.chanceCorrectedSeparation(
            routedClusters.map { cluster -> cluster.map { it.projectTo(childDim) } }
        )
        node.dasguptaDeltaNorm = sepScore

        // Min-pairwise gate: every child pair must clear the same bar the
        // sibling-merger tests, or the proposal is rejected outright.
        //
        // This is the load-bearing separation gate — in the repo's logs it accounts
        // for 5682 rejections against 0 for the k-way gate below. Two facts explain
        // the asymmetry. At routed k=2 there is exactly one pair, and clusterStats()
        // builds the same ClusterStats(n, sum) the k-way overload builds internally,
        // so minPairSep and sepScore are the SAME NUMBER and this gate always fires
        // first. Above k=2 the coarsening loop has already merged every pair below
        // the bar, so this gate cannot fire and the joint score is bounded below by
        // its pairs. Confirmed independently on synthetic clouds: bindP95 matches the
        // k-way p95 to five decimals at every n (docs/separation_null_by_size.md).
        val finalStats = routedClusters.map { clusterStats(it, childDim) }
        var minPairSep = Double.MAX_VALUE
        for (i in finalStats.indices) {
            for (j in i + 1 until finalStats.size) {
                val sep = StatisticsUtils.chanceCorrectedSeparation(listOf(finalStats[i], finalStats[j]))
                if (sep < minPairSep) minPairSep = sep
            }
        }
        if (minPairSep < requiredEps) {
            log.info(
                "[NO-SPLIT] '${node.label}' reason=min-pair n=${targetQueries.size}" +
                    " k=${routedClusters.size} emK=$k" +
                    " sep=${"%.4f".format(java.util.Locale.US, minPairSep)}" +
                    " bar=${"%.4f".format(java.util.Locale.US, requiredEps)}"
            )
            taxonomy.diagnostics.DiagnosticsBundle.recordProposal(
                iter = currentIteration, type = "GROW", siteId = node.id, siteLabel = node.label,
                dJ = null, seDJ = null, z = null, dV = null,
                decision = "NO_PROPOSAL",
                reason = "min_pair_sep_below_bar(sep=" +
                    "${DiagFmt.f(minPairSep, 5)},bar=${DiagFmt.f(requiredEps, 5)}" +
                    ",k=${routedClusters.size},emK=$k)",
                nSite = targetQueries.size
            )
            return false
        }

        log.debug("Eval '${node.label}': k=$k, sep=${"%.3f".format(java.util.Locale.US, sepScore)} (req: ${"%.3f".format(java.util.Locale.US, requiredEps)})")

        // Min-pair is the splitter's ONLY separation gate. At routed k=2 the joint
        // k-way score and the min-pair score are the same number, and above k=2 the
        // coarsening loop has already merged every pair below the bar, so a separate
        // joint gate would be dead by construction. What min-pair asks is "is this
        // partition more than a cut through the node's own elongation?", which dJ
        // structurally cannot ask, because dJ rewards elongation. sepScore is still
        // computed — it is the value persisted as dasguptaDeltaNorm and the one the
        // within-node null diagnostic reads (docs/separation_null_by_size.md).

        log.info("Split '${node.label}' (q=${targetQueries.size}, k=${routedClusters.size}${if (routedClusters.size != k) " (em k=$k)" else ""}, sep=${"%.3f".format(java.util.Locale.US, sepScore)}, routed=${routedClusters.map { it.size }}, converged=${mixture.converged}) -> Spawning ${routedClusters.size} children")

        // ── Create children and wire topology ────────────────────────────────
        // Oversized children are NOT re-split in this pass: immediate recursion peeled
        // depth mechanically before trickle/collapse/refit could ever evaluate the new
        // level, manufacturing wrapper spines. The bottom-up sweep revisits every node
        // next iteration, so a genuinely oversized child splits then — under feedback.
        for (idx in routedClusters.indices) {
            val cluster = routedClusters[idx]
            val vmf = childVmfs[idx]

            val child = createNodeFromCluster(cluster, node, vmf)
            node.children.add(child)
            child.parents.add(node)
            fitter.fitSingleNode(child)
        }
        return true
    }

    private fun clusterStats(embeddings: List<Embedding>, dim: Int): StatisticsUtils.ClusterStats {
        val sum = DoubleArray(dim)
        for (emb in embeddings) {
            val v = emb.projectTo(dim)
            for (i in 0 until dim) sum[i] += v[i]
        }
        return StatisticsUtils.ClusterStats(embeddings.size.toDouble(), sum)
    }

    fun selectRepresentativeQueries(
        cluster: List<Embedding>,
        depth: Int
    ): List<String> {
        if (cluster.isEmpty()) return emptyList()
        if (cluster.size < 10) return cluster.map { it.rawText }.distinct()

        val dims = cluster[0].dimensions
        val centroid = DoubleArray(dims)
        for (emb in cluster) {
            for (d in 0 until dims) centroid[d] += emb.values[d].toDouble()
        }
        for (d in 0 until dims) centroid[d] /= cluster.size.toDouble()

        val sortedByDistance = cluster
            .map { it to calculateCosineDistance(it.toDoubleArray(), centroid) }
            .sortedBy { it.second }

        val n = sortedByDistance.size

        // Depth- and size-aware target sample count
        val targetSamples = when {
            depth <= 2 && n >= 150 -> 40
            depth <= 3 && n >= 100 -> 32
            n >= 100               -> 24
            else                   -> 20
        }.coerceAtMost(n)

        val innerCount = (targetSamples * 0.3).toInt().coerceAtLeast(4)
        val outerCount = (targetSamples * 0.2).toInt().coerceAtLeast(3)
        val middleCount = (targetSamples - innerCount - outerCount).coerceAtLeast(3)

        // Seeded shuffles: representative sampling feeds LLM labeling only, but an
        // unseeded shuffle still makes labels non-reproducible across runs.
        val sampleRng = kotlin.random.Random(n * 31 + depth)
        val innerCore = sortedByDistance
            .take((n / 10).coerceAtLeast(innerCount))
            .shuffled(sampleRng)
            .take(innerCount)

        val outerBoundary = sortedByDistance
            .takeLast((n / 10).coerceAtLeast(outerCount))
            .shuffled(sampleRng)
            .take(outerCount)

        val middleStart = n / 10
        val middleEnd = (9 * n) / 10
        val middleShell = sortedByDistance
            .subList(middleStart, middleEnd)
            .shuffled(sampleRng)
            .take(middleCount)

        return (innerCore + middleShell + outerBoundary)
            .map { it.first.rawText }
            .distinct()
    }

    private suspend fun createNodeFromCluster(
        cluster: List<Embedding>,
        parent: GraphNode,
        vmf: StatisticsUtils.VmfParameters
    ): GraphNode {
        val label = "Emergent Concept #${conceptCounter.getAndIncrement()}"

        val newNode = GraphNode(label = label, depth = parent.depth + 1).apply {
            vmfMu = vmf.mu
            vmfKappa = vmf.kappa
            vmfLogNormalizer = vmf.logNormalizer
            phaseCompleted = phaseCompleted or PHASE_SPLIT_EVAL
            treeParentId = parent.id
        }
        newNode.queries.addAll(cluster)
        
        synchronized(parent.queryWeights) {
            for (q in cluster) {
                val parentW = parent.queryWeights[q.rawText] ?: 1.0
                newNode.queryWeights[q.rawText] = parentW
                parent.queryWeights.remove(q.rawText)
                parent.queries.removeIf { it.rawText == q.rawText }
                GraphNode.registerEmbedding(q)
            }
        }

        return newNode
    }

    suspend fun generateLabelsPostPass(root: GraphNode, onProgress: (Int, Int) -> Unit = { _, _ -> }) = coroutineScope {
        log.info("Starting post-pass labeling of the DAG...")
        val allNodes = mutableListOf<GraphNode>()
        fun walk(n: GraphNode, visited: MutableSet<String>) {
            if (!visited.add(n.id)) return
            allNodes.add(n)
            n.children.forEach { walk(it, visited) }
        }
        walk(root, mutableSetOf())

        // depth-1 nodes are ground-truth domain anchors — NEVER relabel them.
        val nodesToLabel = allNodes.filter { it.depth > 1 }.sortedBy { it.depth }
        val maxDepth = nodesToLabel.map { it.depth }.maxOrNull() ?: 0
        val totalNodesToLabel = nodesToLabel.size
        val completed = java.util.concurrent.atomic.AtomicInteger(0)

        // Notify initial progress
        onProgress(0, totalNodesToLabel)

        for (d in maxDepth downTo 2) {
            val levelNodes = nodesToLabel.filter { it.depth == d }
            // Parallelize across PARENTS but label siblings SEQUENTIALLY: the prompt's
            // sibling-differentiation context only works if earlier siblings' labels
            // are already real. Fully parallel levels read placeholder labels
            // ("Emergent Concept #x", filtered out), so the LLM never saw its
            // neighborhood and produced near-duplicate sibling names.
            levelNodes.groupBy { it.treeParentId ?: it.parents.firstOrNull()?.id ?: it.id }.values.map { siblingGroup ->
                async(Dispatchers.Default) {
                    for (node in siblingGroup) {
                        labelSingleNode(node, completed, totalNodesToLabel, onProgress)
                    }
                }
            }.awaitAll()
        }
        log.info("Post-Pass complete. {} nodes labeled across {} depth levels.", totalNodesToLabel, maxDepth - 1)
    }

    private suspend fun labelSingleNode(
        node: GraphNode,
        completed: java.util.concurrent.atomic.AtomicInteger,
        totalNodesToLabel: Int,
        onProgress: (Int, Int) -> Unit
    ) {
        run {
            run {
                run {
                    // 1) Determine query source: leaves vs internal
                    val isLeaf = node.children.isEmpty()

                    val queryTexts: List<String> = if (isLeaf) {
                        // Leaf: use only own queries
                        node.queries.map { it.rawText }
                    } else {
                        // Internal: union of child representative samples
                        node.children
                            .flatMap { child ->
                                val branchQueries = child.getAllQueriesInBranch()
                                if (branchQueries.isEmpty()) emptyList()
                                else selectRepresentativeQueries(branchQueries, child.depth)
                            }
                            .distinct()
                    }

                    if (queryTexts.isEmpty()) {
                        node.label = "Emergent Concept #${node.id.take(4)}"
                        val finished = completed.incrementAndGet()
                        onProgress(finished, totalNodesToLabel)
                        return
                    }

                    val parents = node.parents
                    val siblingLabels = parents
                        .flatMap { it.children }
                        .filter { it.id != node.id }
                        .mapNotNull { it.label }
                        .filter { it.isNotEmpty() && !it.startsWith("Emergent Concept") && !it.startsWith("Discovered Concept") }
                        .distinct()

                    // Child labels (for internal nodes)
                    val childLabels = if (isLeaf) {
                        emptyList()
                    } else {
                        node.children
                            .mapNotNull { it.label }
                            .filter { it.isNotEmpty() && !it.startsWith("Emergent Concept") && !it.startsWith("Discovered Concept") }
                            .distinct()
                    }

                    val treeParentId = node.treeParentId
                    val lineage = mutableListOf<String>()
                    var current: GraphNode? = parents.find { it.id == treeParentId } ?: parents.firstOrNull()
                    val visitedLineage = mutableSetOf<String>()
                    while (current != null && visitedLineage.add(current.id)) {
                        lineage.add(0, current.label ?: "Emergent Concept")
                        val nextTreeParentId = current.treeParentId
                        current = current.parents.find { it.id == nextTreeParentId } ?: current.parents.firstOrNull()
                    }

                    // Domain anchors: top 1–2 domain names, no counts
                    val domainAnchors = queryTexts
                        .mapNotNull { question ->
                            datasetFetcher.getDetailsForQuery(question)?.category
                        }
                        .map { cat ->
                            cat.split("_", "-")
                                .joinToString(" ") { word ->
                                    word.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
                                }
                        }
                        .groupBy { it }
                        .mapValues { it.value.size }
                        .entries
                        .sortedByDescending { it.value }
                        .take(2)
                        .map { it.key }

                    // Centroid-ranked samples: the prompt should describe what the node
                    // ACTUALLY contains — its most typical members by vMF alignment —
                    // not a uniform shuffle; a spread of every-kth adds tail coverage.
                    val representativeSamples = if (isLeaf && node.vmfMu.isNotEmpty()) {
                        val ranked = node.queries
                            .sortedByDescending { StatisticsUtils.dotProduct(it.projectTo(node.vmfMu.size), node.vmfMu) }
                            .map { it.rawText }
                        val step = (ranked.size / 10).coerceAtLeast(1)
                        (ranked.take(30) + ranked.filterIndexed { i, _ -> i % step == 0 }).distinct().take(40)
                    } else {
                        queryTexts.shuffled(kotlin.random.Random(queryTexts.size)).take(40)
                    }

                    val parentLabelsList = parents
                        .mapNotNull { it.label }
                        .filter { it.isNotEmpty() && !it.startsWith("Emergent Concept") && !it.startsWith("Discovered Concept") }
                        .distinct()
                    val parentContextLabel = if (parentLabelsList.size > 1) {
                        "Cross-Domain Polyhierarchy Bridge linking: ${parentLabelsList.joinToString(" AND ")}"
                    } else {
                        parentLabelsList.firstOrNull() ?: parents.find { it.id == treeParentId }?.label ?: "Universal Knowledge"
                    }

                    val prompt = TaxoPrompts.clusterLabeling(
                        querySamples = representativeSamples,
                        parentLabel = parentContextLabel,
                        siblingLabels = siblingLabels,
                        branchHistory = lineage,
                        domainAnchors = domainAnchors,
                        childLabels = childLabels,
                        depth = node.depth
                    )

                    val labelSchema = JsonSchema.builder()
                        .name("ClusterLabel")
                        .rootElement(
                            JsonObjectSchema.builder()
                                .addStringProperty(
                                    "label",
                                    "A concise, domain-specific label for the concept cluster (3-7 words)"
                                )
                                .required("label")
                                .build()
                        )
                        .build()

                    val jsonResponse = llmSemaphore.withPermit {
                        llmClient.queryModelStructured(
                            modelName = System.getenv("ARC_MODEL") ?: config.llm.labelingModel,
                            systemPrompt = null,
                            userPrompt = prompt,
                            schema = labelSchema
                        )
                    }

                    val labelResult = TaxoPrompts.parseClusterLabelResult(jsonResponse)
                    node.label = labelResult?.first ?: "Discovered Concept"
                    node.description = labelResult?.second?.takeIf { it.isNotBlank() }

                    val finished = completed.incrementAndGet()
                    if (finished % 10 == 0 || finished == totalNodesToLabel) {
                        log.info("Post-Pass: $finished/$totalNodesToLabel nodes labeled")
                    }
                    onProgress(finished, totalNodesToLabel)
                }
            }
        }
    }

    private fun fitVmfParams(embeddings: List<Embedding>, d: Int): StatisticsUtils.VmfParameters {
        val n = embeddings.size
        if (n == 0) {
            val mu = FloatArray(d) { 0.0f }.apply { if (d > 0) this[0] = 1.0f }
            val kappa = 1e-3
            val logNorm = StatisticsUtils.logVmfNormalizer(d, kappa)
            return StatisticsUtils.VmfParameters(mu, kappa, logNorm)
        }
        val projected = embeddings.map { it.projectTo(d) }
        val sumVec = DoubleArray(d)
        for (vec in projected) {
            for (i in 0 until d) sumVec[i] += vec[i]
        }
        var normVec = 0.0
        for (i in 0 until d) normVec += sumVec[i] * sumVec[i]
        normVec = sqrt(normVec)
        val mu = FloatArray(d) { i -> if (normVec > 0.0) (sumVec[i] / normVec).toFloat() else 0.0f }
        if (normVec == 0.0 && d > 0) {
            mu[0] = 1.0f
        }
        val rBar = normVec / n
        val kappa = StatisticsUtils.correctedKappa(rBar, d, n)
        val logNorm = StatisticsUtils.logVmfNormalizer(d, kappa)
        return StatisticsUtils.VmfParameters(mu, kappa, logNorm)
    }

    private fun calculateCosineDistance(v1: DoubleArray, v2: DoubleArray): Double {
        var dotProduct = 0.0
        var norm1 = 0.0
        var norm2 = 0.0
        for (i in v1.indices) {
            dotProduct += v1[i] * v2[i]
            norm1 += v1[i] * v1[i]
            norm2 += v2[i] * v2[i]
        }
        val similarity = if (norm1 > 0 && norm2 > 0) dotProduct / (sqrt(norm1) * sqrt(norm2)) else 0.0
        return 1.0 - similarity
    }
}
