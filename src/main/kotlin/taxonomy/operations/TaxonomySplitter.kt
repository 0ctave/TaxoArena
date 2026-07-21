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

    /**
     * Parallel BFS level-by-level recursive splitting.
     */
    suspend fun splitNodesRecursive(root: GraphNode) = withContext(Dispatchers.Default) {
        checkAndSyncSemaphore()
        log.info("Starting parallel split evaluation across the DAG...")
        val byDepth = mutableMapOf<Int, MutableList<GraphNode>>()
        val visited = mutableSetOf<String>()
        val queue = ArrayDeque<GraphNode>().apply { add(root) }

        while (queue.isNotEmpty()) {
            val n = queue.removeFirst()
            if (!visited.add(n.id)) continue
            byDepth.getOrPut(n.depth) { mutableListOf() }.add(n)
            queue.addAll(n.children)
        }

        // Process bottom-up (deepest first)
        byDepth.keys.sortedDescending().forEach { depth ->
            val nodesAtDepth = byDepth[depth]!!
            nodesAtDepth.map { node ->
                async {
                    splitSingleNode(node)
                }
            }.awaitAll()
        }
        log.info("Finished parallel split evaluation.")
    }

    suspend fun splitSingleNode(node: GraphNode) {
        val localWeights = node.queryWeights
        val mass = localWeights.values.sum()
        val ess = if (mass > 0.0) (mass * mass / localWeights.values.sumOf { it * it }) else 0.0
        val threshold = 2 * config.formalism.minClusterSize
        if (mass < threshold || ess < threshold) return

        if (node.depth >= config.formalism.maxDepth) {
            log.debug("Split Boundary: '${node.label}' reached max depth (${config.formalism.maxDepth}). Preventing split.")
            return
        }

        val isDiffuse = node.vmfKappa < 0.5 && mass < 10 * config.formalism.minClusterSize
        if (isDiffuse) {
            var viable = false
            if (config.formalism.enableResidualSplitGate) {
                val minClusterSize = config.formalism.minClusterSize
                val allSubtreeQueries = node.getAllQueriesInRegion()
                val residualEmbeddings = allSubtreeQueries.filter { emb ->
                    val qId = if (emb.queryId != -1) emb.queryId.toString() else taxonomy.model.TextNormalizer.cleanText(emb.rawText)
                    qId in node.residualQueries
                }
                
                if (residualEmbeddings.size >= minClusterSize) {
                    val resDim = node.sliceDim
                    val projectedRes = residualEmbeddings.map { it.projectTo(resDim) }
                    val resCentroid = DoubleArray(resDim)
                    for (vec in projectedRes) {
                        for (i in 0 until resDim) resCentroid[i] += vec[i]
                    }
                    var resNorm = 0.0
                    for (i in 0 until resDim) resNorm += resCentroid[i] * resCentroid[i]
                    resNorm = kotlin.math.sqrt(resNorm)
                    val resMu = FloatArray(resDim) { i -> if (resNorm > 0.0) (resCentroid[i] / resNorm).toFloat() else 0.0f }
                    if (resNorm == 0.0 && resDim > 0) resMu[0] = 1.0f

                    var resDotSum = 0.0
                    for (vec in projectedRes) {
                        for (i in 0 until resDim) resDotSum += resMu[i] * vec[i]
                    }
                    val resRBar = (resDotSum / projectedRes.size.coerceAtLeast(1)).coerceAtLeast(0.0)
                    val resKappa = StatisticsUtils.correctedKappa(resRBar, resDim, projectedRes.size)

                    val siblings = node.parents.flatMap { it.children }.filter { it.id != node.id }
                    viable = siblings.isEmpty() || siblings.all { sib ->
                        val commonDim = minOf(resDim, sib.vmfMu.size)
                        if (commonDim > 0) {
                            val projResMu = StatisticsUtils.projectVector(resMu, commonDim)
                            val projSibMu = StatisticsUtils.projectVector(sib.vmfMu, commonDim)
                            val div = StatisticsUtils.vmfJsDivergence(projResMu, resKappa, projSibMu, sib.vmfKappa, commonDim)
                            div >= config.formalism.separationEpsilon
                        } else {
                            true
                        }
                    }
                }
            }
            
            if (!viable) {
                log.debug("Split Skipped: '${node.label}' kappa=${node.vmfKappa} too diffuse.")
                return
            } else {
                log.debug("Split Allowed via Residual Viability Gate: '${node.label}' is diffuse but has coherent residual cluster.")
            }
        }

        val targetQueries = if (isDiffuse && config.formalism.enableResidualSplitGate) {
            val allSubtreeQueries = node.getAllQueriesInRegion()
            allSubtreeQueries.filter { emb ->
                val qId = if (emb.queryId != -1) emb.queryId.toString() else taxonomy.model.TextNormalizer.cleanText(emb.rawText)
                qId in node.residualQueries
            }.ifEmpty { localWeights.keys.mapNotNull { GraphNode.getEmbedding(it) } }
        } else {
            localWeights.keys.mapNotNull { GraphNode.getEmbedding(it) }
        }

        log.debug("Scanning '${node.label}' (${targetQueries.size} q) for split...")

        val childDim =  dimForDepth(node.depth + 1)
        val minClusterSize = config.formalism.minClusterSize

        val rawVectors = targetQueries.map { it.toDoubleArray() }

        val splitDim = when {
            targetQueries.size < 100 -> 32
            targetQueries.size < 500 -> 64
            else                    -> 128
        }.coerceAtMost(rawVectors.first().size)

        val pcaProjected = StatisticsUtils.pcaProject(rawVectors, splitDim)

        // ── k-ary mixture selection ───────────────────────────────────────────
        val minClusterFrac = minClusterSize.toDouble() / targetQueries.size

        val probe = StatisticsUtils.performVmfKMeans(
            embeddings = pcaProjected,
            d = splitDim,
            maxK = 2,
            minClusterFrac = minClusterFrac,
            marginalEps = config.formalism.separationEpsilon
        )

        if (probe == null) {
            log.debug("Split Failed: k-means collapsed for '${node.label}'.")
            return
        }


        val mixture = if (probe.components.size < 2) {
            log.debug("Split Failed: k=2 probe insufficient for '${node.label}'.")
            return
        } else {
            StatisticsUtils.performVmfKMeans(
                embeddings = pcaProjected,
                d = splitDim,
                maxK = 4,
                minClusterFrac = minClusterFrac,
                marginalEps = config.formalism.separationEpsilon
            ) ?: probe  // fallback to probe if full run collapses
        }


        val k = mixture.components.size

        // ── Hard-assign queries to clusters ──────────────────────────────────
        val clusters         = Array(k) { mutableListOf<Embedding>() }
        val clustersProjected = Array(k) { mutableListOf<DoubleArray>() }

        for (i in targetQueries.indices) {
            val resp = mixture.responsibilities[i]
            val best = resp.indices.maxByOrNull { resp[it] } ?: 0
            clusters[best].add(targetQueries[i])
            clustersProjected[best].add(pcaProjected[i])
        }

        // ── Floor check ───────────────────────────────────────────────────────
        if (clusters.any { it.size < minClusterSize }) {
            log.debug("Split Floor Rejected: a cluster is below minClusterSize=$minClusterSize (sizes: ${clusters.map { it.size }}).")
            return
        }

        // ── k-way Dasgupta validation ─────────────────────────────────────────
        val deltaNorm = StatisticsUtils.calculateDasguptaDeltaK(clustersProjected.map { it.toList() })
        node.dasguptaDeltaNorm = deltaNorm

        val requiredEps = if (targetQueries.size < 2 * minClusterSize)
            2.0 * config.formalism.separationEpsilon
        else
            config.formalism.separationEpsilon

        log.debug("Eval '${node.label}': k=$k, delta=${"%.3f".format(java.util.Locale.US, deltaNorm)} (req: ${"%.3f".format(java.util.Locale.US, requiredEps)})")

        if (deltaNorm < requiredEps) {
            log.debug("Split Rejected: delta ${"%.3f".format(java.util.Locale.US, deltaNorm)} insufficient")
            return
        }

        // ── Fit child vMF in target dimension ────────────────────────────────
        val childVmfs = clusters.map { cluster -> fitVmfParams(cluster, childDim) }

        // ── Sibling distinctness guard ────────────────────────────────────────
        val siblingMergeThreshold = config.formalism.separationEpsilon
        val isUnique = childVmfs.all { newVmf ->
            node.children.all { sibling ->
                val projSiblingMu = StatisticsUtils.projectVector(sibling.vmfMu, childDim)
                val div = StatisticsUtils.vmfJsDivergence(
                    newVmf.mu, newVmf.kappa, projSiblingMu, sibling.vmfKappa, childDim
                )
                div >= siblingMergeThreshold
            }
        }

        if (!isUnique) {
            log.debug("Split Rejected: child too similar to sibling")
            return
        }

        log.info("Split '${node.label}' (q=${targetQueries.size}, k=$k, delta=${"%.3f".format(java.util.Locale.US, deltaNorm)}) -> Spawning $k children")

        // ── Create children and wire topology ────────────────────────────────
        val allSpawnedLeaves = mutableListOf<GraphNode>()

        for (idx in clusters.indices) {
            val cluster = clusters[idx]
            val vmf = childVmfs[idx]

            // Normal child
            val child = createNodeFromCluster(cluster, node, vmf)
            node.children.add(child)
            child.parents.add(node)
            fitter.fitSingleNode(child)
            allSpawnedLeaves.add(child)
        }

        // ── Macro-concept decomposition (lowered threshold: 3x instead of 5x) ─
        val macroThreshold = threshold * 3
        for (child in allSpawnedLeaves) {
            if (child.queries.size > macroThreshold && child.depth < config.formalism.maxDepth) {
                log.info("Decomposing macro-cluster '${child.label}' immediately (${child.queries.size} q)")
                splitSingleNode(child)
            }
        }
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

        val innerCore = sortedByDistance
            .take((n / 10).coerceAtLeast(innerCount))
            .shuffled()
            .take(innerCount)

        val outerBoundary = sortedByDistance
            .takeLast((n / 10).coerceAtLeast(outerCount))
            .shuffled()
            .take(outerCount)

        val middleStart = n / 10
        val middleEnd = (9 * n) / 10
        val middleShell = sortedByDistance
            .subList(middleStart, middleEnd)
            .shuffled()
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
            levelNodes.map { node ->
                async(Dispatchers.Default) {
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
                        return@async
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

                    // Representative subset from queryTexts for the prompt
                    val representativeSamples = queryTexts.shuffled().take(40)

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
            }.awaitAll()
        }
        log.info("Post-Pass complete. {} nodes labeled across {} depth levels.", totalNodesToLabel, maxDepth - 1)
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