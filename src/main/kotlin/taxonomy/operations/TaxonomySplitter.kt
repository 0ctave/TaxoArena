package org.eclipse.lmos.arc.app.taxonomy.operations

import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import org.eclipse.lmos.arc.app.taxonomy.Embedding
import org.eclipse.lmos.arc.app.taxonomy.GraphNode
import org.eclipse.lmos.arc.app.taxonomy.TaxonomyConfig
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.StatisticsUtils
import taxonomy.TaxoPrompts
import kotlin.math.*
import dev.langchain4j.model.chat.request.json.JsonObjectSchema
import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive

/**
 * Implements Phase 4: Discover (Adaptive Splitting).
 * Upgraded with Angular Metrics (Cosine Distance), Maximum Curvature (Knee Detection),
 * Context-Aware Epsilon Relaxation, and Maximum Depth Boundary restrictions.
 */
@Service
class TaxonomySplitter(
    private val config: TaxonomyConfig,
    private val llmClient: TaxonomyLlmClient,
    private val datasetFetcher: org.eclipse.lmos.arc.app.MMLUDatasetFetcher
) {
    private val log = LoggerFactory.getLogger(TaxonomySplitter::class.java)
    private val llmSemaphore = Semaphore(5) // Throttle parallel LLM calls
    private val conceptCounter = java.util.concurrent.atomic.AtomicInteger(1)

    fun resetConceptCounter() {
        conceptCounter.set(1)
    }

    suspend fun splitNodesRecursive(node: GraphNode, visited: MutableSet<String> = java.util.concurrent.ConcurrentHashMap.newKeySet()) {
        if (visited.contains(node.id)) return
        visited.add(node.id)

        val currentChildren = node.children.toList()
        coroutineScope {
            currentChildren.map { child ->
                async(Dispatchers.Default) {
                    splitNodesRecursive(child, visited)
                }
            }
        }.awaitAll()

        // Use splitBaseThreshold from the new Thermodynamic Formalism
        val threshold = config.formalism.splitBaseThreshold

        if (node.queries.size > threshold) {
            // BOUNDARY ENFORCEMENT: Check if the node has hit the maximum allowed depth
            if (node.depth >= config.formalism.maxDepth) {
                log.info("Split Boundary: '${node.label}' reached max depth (${config.formalism.maxDepth}). Preventing split.")
                return
            }

            log.info("Split Scan: '${node.label}' exceeds threshold (${node.queries.size} > $threshold). Scanning emergent concepts...")

            val root = getRoot(node)
            val totalTaxonomyQueries = root.getAllQueriesInBranch().distinctBy { it.rawText }.size

            // 1. Try splitting based on GMM component "clues" first (Partitioning)
            var clusters = if (node.distribution != null && node.distribution!!.components.size > 1) {
                partitionByGmm(node)
            } else emptyList()

            // 2. Fallback to DBSCAN if GMM is monolithic or partitioning failed to diversify
            if (clusters.size <= 1) {
                val splitMinThreshold = maxOf(5, (config.formalism.splitBaseThreshold * 0.5).toInt())
                clusters = performDbscan(node.queries, splitMinThreshold, node.isLeaf, totalTaxonomyQueries)
            }

            if (clusters.isNotEmpty()) {
                val baseDeff = config.formalism.fixedMrlDimension.coerceIn(1, node.queries.firstOrNull()?.dimensions ?: 4096)
                
                val dEff = if (config.formalism.enableDynamicDimension) {
                    val queryCount = node.queries.size.coerceAtLeast(1)
                    val adaptive = (queryCount * config.formalism.dynamicDimensionFactor).toInt()
                        .coerceAtLeast(config.formalism.dynamicDimensionFloor)
                    minOf(baseDeff, adaptive)
                } else {
                    baseDeff
                }

                val validClusters = clusters.filter { cluster ->
                    // 1. Check Relative Max Size ceiling
                    // DYNAMIC CEILING: Root (0) and Macro-Nodes (1) must split to bootstrap growth.
                    // Ceiling starts at 1.0 and decays to the configured relative-max-size.
                    val effectiveRelativeMaxSize = if (node.depth <= 1) 1.0 else config.formalism.relativeMaxSize
                    val isMegaNode = (node.queries.size > 500 || node.queries.size > (totalTaxonomyQueries * 0.3)) && node.depth < 4
                    
                    if (!isMegaNode && cluster.size > node.queries.size * effectiveRelativeMaxSize) {
                        log.warn("Split Ceiling: Cluster in '${node.label}' violates max relative size (${cluster.size} > ${node.queries.size} * ${"%.2f".format(java.util.Locale.US, effectiveRelativeMaxSize)}). Skipping.")
                        return@filter false
                    }

                    val effectiveMinRelativeSize = if (node.depth <= 1) 0.02 else config.formalism.minRelativeSplitSize
                    if (cluster.size < node.queries.size * effectiveMinRelativeSize) {
                        log.warn("Split Floor: Cluster in '${node.label}' is too small (${cluster.size} < ${node.queries.size} * $effectiveMinRelativeSize). Skipping.")
                        return@filter false
                    }

                    // 2. p-BIC Validation
                    val currentGmm = node.distribution ?: return@filter true
                    
                    // Current Log-Likelihood (Stable)
                    val currentLL = StatisticsUtils.calculateLogLikelihood(currentGmm, node.queries)
                    val currentPBic = StatisticsUtils.calculatePBic(currentGmm, node.queries, config.formalism.pBicLambda, dEff)
                    
                    // Proposed GMM: Current components + new cluster component
                    val clusterGmm = StatisticsUtils.computeLeafGmm(cluster, 1, config.formalism.oasShrinkage) ?: return@filter false
                    
                    // Correct Weight Calculation: 
                    // New model should reflect the combined population.
                    val nParent = node.queries.size.toDouble()
                    val nCluster = cluster.size.toDouble()
                    val nTotal = nParent + nCluster
                    
                    val proposedComponents = currentGmm.components.map { it.copy(weight = it.weight * (nParent / nTotal)) } + 
                                         clusterGmm.components.map { it.copy(weight = it.weight * (nCluster / nTotal)) }
                    
                    val proposedGmm = org.eclipse.lmos.arc.app.taxonomy.GmmParams(proposedComponents)
                    
                    val combinedDataset = node.queries + cluster
                    val proposedLL = StatisticsUtils.calculateLogLikelihood(proposedGmm, combinedDataset)
                    val proposedPBic = StatisticsUtils.calculatePBic(proposedGmm, combinedDataset, config.formalism.pBicLambda, dEff)
                    
                    // Recalculate current for same dataset
                    val currentLL_on_all = StatisticsUtils.calculateLogLikelihood(currentGmm, combinedDataset)
                    val currentPBic_on_all = StatisticsUtils.calculatePBic(currentGmm, combinedDataset, config.formalism.pBicLambda, dEff)

                    log.info("Split Eval '${node.label}': CurrentBIC=${"%.4f".format(java.util.Locale.US, currentPBic_on_all)}, ProposedBIC=${"%.4f".format(java.util.Locale.US, proposedPBic)}")
                    
                    if (isMegaNode) {
                        val improvement = proposedLL - currentLL_on_all
                        log.info("Split Eval '${node.label}': Mega-node detected, bypassing strict p-BIC check (LL improvement: ${"%.4f".format(java.util.Locale.US, improvement)})")
                        if (improvement <= 0.1) return@filter false
                    } else if (node.depth == 1) {
                        val improvement = (proposedLL - currentLL_on_all)
                        log.info("Split Eval '${node.label}': p-BIC rejected macro-split (LL improvement: ${"%.4f".format(java.util.Locale.US, improvement)})")
                        if (improvement <= 1.0) return@filter false
                    } else {
                        if (proposedPBic >= currentPBic_on_all) return@filter false
                    }

                    // 3. Sibling Distinctness Guard: 
                    // Ensure the new cluster is not already "covered" by an existing sibling.
                    val isUnique = node.children.all { sibling ->
                        val siblingGmm = sibling.distribution ?: return@all true
                        val similarity = StatisticsUtils.gmmSimilarity(clusterGmm, siblingGmm)
                        similarity < config.formalism.tauMerge
                    }
                    
                    if (!isUnique) {
                        log.info("Split Distinctness: Sub-cluster in '${node.label}' too similar to existing sibling. Skipping.")
                        return@filter false
                    }

                    true
                }

                if (validClusters.isNotEmpty()) {
                    // DIVERSIFICATION GUARD: 
                    // Only diversify if we actually found multiple concepts,
                    // OR if the single child is a significant "zoom" (smaller volume).
                    val shouldDiversify = if (validClusters.size == 1) {
                        val cluster = validClusters[0]
                        // Only create a child if it partitions a specific subset (< 75% or 65% at depth >= 3)
                        val maxRatio = if (node.depth >= 3) 0.65 else 0.75
                        cluster.size < node.queries.size * maxRatio
                    } else true

                    if (shouldDiversify) {
                        log.info("Concept Discovered: Spawning ${validClusters.size} sub-clusters in '${node.label}'")
                        
                        val newChildren = coroutineScope {
                            validClusters.map { cluster ->
                                async(Dispatchers.Default) {
                                    llmSemaphore.withPermit {
                                        createNodeFromCluster(cluster, node)
                                    }
                                }
                            }.awaitAll().filterNotNull()
                        }

                        newChildren.forEach { newChild ->
                            node.children.add(newChild)
                            newChild.parents.add(node)
                            val clusterRawTexts = newChild.queries.map { it.rawText }.toSet()
                            node.queries.removeIf { it.rawText in clusterRawTexts }
                        }

                        // Parallelize recursive decomposition of macro-clusters safely AFTER all sibling permits are fully released!
                        coroutineScope {
                            newChildren.forEach { newChild ->
                                if (newChild.queries.size > config.formalism.splitBaseThreshold * 5 && newChild.depth < config.formalism.maxDepth) {
                                    log.info("Macro-Concept: '${newChild.label}' is a macro-cluster. Decomposing immediately.")
                                    async(Dispatchers.Default) {
                                        splitNodesRecursive(newChild, visited)
                                    }
                                }
                            }
                        }
                    } else {
                        log.info("Split Redundancy: Single sub-cluster in '${node.label}' is too redundant. Skipping to prevent clone.")
                    }
                }
            }
        }
    }

    private fun partitionByGmm(node: GraphNode): List<List<Embedding>> {
        val gmm = node.distribution ?: return emptyList()
        val nComp = gmm.components.size
        if (nComp <= 1) return emptyList()
        
        val clusters = List(nComp) { mutableListOf<Embedding>() }
        for (emb in node.queries) {
            var bestIdx = -1
            var minD2 = Double.MAX_VALUE
            for (i in 0 until nComp) {
                val comp = gmm.components[i]
                val d2 = StatisticsUtils.minMahalanobisDistance(emb, org.eclipse.lmos.arc.app.taxonomy.GmmParams(listOf(comp)))
                if (d2 < minD2) {
                    minD2 = d2
                    bestIdx = i
                }
            }
            if (bestIdx != -1) clusters[bestIdx].add(emb)
        }
        val splitMinThreshold = maxOf(5, (config.formalism.splitBaseThreshold * 0.5).toInt())
        return clusters.filter { it.size >= splitMinThreshold }
    }

    fun selectRepresentativeQueries(cluster: List<Embedding>): List<String> {
        if (cluster.isEmpty()) return emptyList()
        // STRATIFIED DIVERSIFIED SAMPLING (To combat sampling bias)
        // 1. Calculate centroid
        val dims = cluster[0].dimensions
        val centroid = DoubleArray(dims)
        for (emb in cluster) {
            for (d in 0 until dims) centroid[d] += emb.values[d].toDouble()
        }
        for (d in 0 until dims) centroid[d] /= cluster.size.toDouble()

        // 2. Stratify cluster into 3 strata: Inner Core, Middle Shell, Outer Boundary
        val sortedByDistance = cluster.map { it to calculateCosineDistance(it.toDoubleArray(), centroid) }
            .sortedBy { it.second }
        
        val n = sortedByDistance.size
        val innerCore = sortedByDistance.take(n / 10).shuffled().take(7)
        val middleShell = sortedByDistance.subList(n / 10, (9 * n) / 10).shuffled().take(7)
        val outerBoundary = sortedByDistance.takeLast(n / 10).shuffled().take(6)
        
        return (innerCore + middleShell + outerBoundary).map { it.first.rawText }.distinct()
    }

    private suspend fun createNodeFromCluster(cluster: List<Embedding>, parent: GraphNode): GraphNode {
        val representativeSamples = selectRepresentativeQueries(cluster)

        // 3. Get branch lineage
        val lineage = mutableListOf<String>()
        var current: GraphNode? = parent
        val visitedLineage = mutableSetOf<String>()
        while (current != null && visitedLineage.add(current.id)) {
            lineage.add(0, current.label)
            current = current.parents.firstOrNull()
        }

        val siblingLabels = parent.children.map { it.label }
        val domainAnchors = representativeSamples.mapNotNull { question ->
            datasetFetcher.getDetailsForQuery(question)?.category?.split("_", "-")?.joinToString(" ") { word ->
                word.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
            }
        }.groupBy { it }.mapValues { it.value.size }
            .entries.sortedByDescending { it.value }
            .map { "${it.key} (${it.value} queries)" }

        val label = if (config.formalism.enableLiveLabeling) {
            val prompt = TaxoPrompts.clusterLabeling(
                querySamples = representativeSamples,
                parentLabel = parent.label,
                siblingLabels = siblingLabels,
                branchHistory = lineage,
                domainAnchors = domainAnchors,
                depth = parent.depth + 1
            )

            val labelSchema = JsonSchema.builder()
                .name("ClusterLabel")
                .rootElement(
                    JsonObjectSchema.builder()
                        .addStringProperty("label", "A concise, domain-specific label for the concept cluster (3-7 words)")
                        .required("label")
                        .build()
                )
                .build()
            val jsonResponse = llmClient.queryModelStructured(
                modelName = System.getenv("ARC_MODEL") ?: config.llm.labelingModel,
                systemPrompt = null,
                userPrompt = prompt,
                schema = labelSchema
            )
            try {
                Json.parseToJsonElement(jsonResponse).jsonObject["label"]?.jsonPrimitive?.content
                    ?: "Discovered Concept"
            } catch (e: Exception) {
                log.warn("Structured label parse failed, using fallback. Raw response: $jsonResponse")
                "Discovered Concept"
            }
        } else {
            "Emergent Concept #${conceptCounter.getAndIncrement()}"
        }

        log.info("Concept Mapped: Mapped cluster (${cluster.size} items) -> '$label' (Live Labeling: ${config.formalism.enableLiveLabeling})")

        val newNode = GraphNode(label = label, depth = parent.depth + 1)
        newNode.queries.addAll(cluster)
        
        return newNode
    }

    suspend fun generateLabelsPostPass(root: GraphNode) = coroutineScope {
        log.info("Starting post-pass labeling of the DAG...")
        val allNodes = mutableListOf<GraphNode>()
        fun walk(n: GraphNode, visited: MutableSet<String>) {
            if (!visited.add(n.id)) return
            allNodes.add(n)
            n.children.forEach { walk(it, visited) }
        }
        walk(root, mutableSetOf())

        val nodesToLabel = allNodes.filter { it.depth > 0 }.sortedBy { it.depth }
        val maxDepth = nodesToLabel.map { it.depth }.maxOrNull() ?: 0

        for (d in 1..maxDepth) {
            val levelNodes = nodesToLabel.filter { it.depth == d }
            levelNodes.map { node ->
                async(Dispatchers.Default) {
                    llmSemaphore.withPermit {
                        val branchQueries = node.getAllQueriesInBranch()
                        if (branchQueries.isEmpty()) {
                            node.label = "Emergent Concept #${node.id.take(4)}"
                            return@withPermit
                        }

                        val representativeSamples = selectRepresentativeQueries(branchQueries)

                        val parents = node.parents
                        val siblingLabels = parents.flatMap { it.children }.map { it.label }.filter { it != node.label }

                        val lineage = mutableListOf<String>()
                        var current: GraphNode? = parents.firstOrNull()
                        val visitedLineage = mutableSetOf<String>()
                        while (current != null && visitedLineage.add(current.id)) {
                            lineage.add(0, current.label)
                            current = current.parents.firstOrNull()
                        }

                        val domainAnchors = representativeSamples.mapNotNull { question ->
                            datasetFetcher.getDetailsForQuery(question)?.category?.split("_", "-")?.joinToString(" ") { word ->
                                word.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
                            }
                        }.groupBy { it }.mapValues { it.value.size }
                            .entries.sortedByDescending { it.value }
                            .map { "${it.key} (${it.value} queries)" }

                        val prompt = TaxoPrompts.clusterLabeling(
                            querySamples = representativeSamples,
                            parentLabel = parents.firstOrNull()?.label ?: "Universal Knowledge",
                            siblingLabels = siblingLabels,
                            branchHistory = lineage,
                            domainAnchors = domainAnchors,
                            depth = node.depth
                        )

                        val labelSchema = JsonSchema.builder()
                            .name("ClusterLabel")
                            .rootElement(
                                JsonObjectSchema.builder()
                                    .addStringProperty("label", "A concise, domain-specific label for the concept cluster (3-7 words)")
                                    .required("label")
                                    .build()
                            )
                            .build()

                        val jsonResponse = llmClient.queryModelStructured(
                            modelName = System.getenv("ARC_MODEL") ?: config.llm.labelingModel,
                            systemPrompt = null,
                            userPrompt = prompt,
                            schema = labelSchema
                        )

                        val newLabel = try {
                            Json.parseToJsonElement(jsonResponse).jsonObject["label"]?.jsonPrimitive?.content
                                ?: "Discovered Concept"
                        } catch (e: Exception) {
                            log.warn("Structured label parse failed, using fallback. Raw response: $jsonResponse")
                            "Discovered Concept"
                        }

                        log.info("Concept Mapped (Post-Pass): Mapped node ${node.label} (${branchQueries.size} branch items) -> '$newLabel'")
                        node.label = newLabel
                    }
                }
            }.awaitAll()
        }
        log.info("Finished post-pass labeling of the DAG.")
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

    /**
     * Advanced High-Dimensional DBSCAN using Cosine Distance and Knee Detection.
     */
    private suspend fun performDbscan(
        embeddings: List<Embedding>,
        minPts: Int,
        isLeaf: Boolean,
        totalTaxonomyQueries: Int
    ): List<List<Embedding>> {
        if (embeddings.size < minPts) return emptyList()

        val maxSample = 500
        val isDownsampled = embeddings.size > maxSample
        val sampledEmbeddings = if (isDownsampled) {
            embeddings.shuffled(kotlin.random.Random(42)).take(maxSample)
        } else {
            embeddings
        }

        val n = sampledEmbeddings.size
        val distMatrix = Array(n) { DoubleArray(n) }

        // Precompute L2 norms once for fast cosine similarity
        val norms = DoubleArray(n) { idx ->
            val emb = sampledEmbeddings[idx]
            var sumSq = 0.0
            for (d in 0 until emb.dimensions) {
                val v = emb.values[d].toDouble()
                sumSq += v * v
            }
            sqrt(sumSq)
        }

        // 1. Parallelize Pairwise Cosine Distances calculation using precomputed norms
        coroutineScope {
            (0 until n).chunked(maxOf(1, n / Runtime.getRuntime().availableProcessors())).map { chunk ->
                launch(Dispatchers.Default) {
                    for (i in chunk) {
                        val viVals = sampledEmbeddings[i].values
                        val normI = norms[i]
                        for (j in i + 1 until n) {
                            val vjVals = sampledEmbeddings[j].values
                            var dotProduct = 0.0f
                            val dims = viVals.size

                            for (d in 0 until dims) {
                                dotProduct += viVals[d] * vjVals[d]
                            }

                            val normProduct = normI * norms[j]
                            val similarity = if (normProduct > 0.0) dotProduct.toDouble() / normProduct else 0.0
                            val dist = (1.0 - similarity).coerceAtLeast(0.0)

                            distMatrix[i][j] = dist
                            distMatrix[j][i] = dist
                        }
                    }
                }
            }
        }

        // 2. Compute k-NN distances dynamically based on node size N
        val kDistances = DoubleArray(n)
        val k = maxOf(4, round(ln(n.toDouble()) * 2.0).toInt()).coerceAtMost(n - 1)
        for (i in 0 until n) {
            val distancesFromI = distMatrix[i].sorted()
            kDistances[i] = distancesFromI[k]
        }
        kDistances.sort() // Sort to form the K-Distance Graph

        // 3. Mathematical Knee/Elbow Detection for Optimal Epsilon
        // If N > 500, downsample the k-distances curve to exactly 500 points to keep knee detection instant
        val kneeEps = if (n > 500) {
            val downsampled = DoubleArray(500) { idx ->
                val sourceIdx = (idx * (n - 1)) / 499
                kDistances[sourceIdx]
            }
            findMaximumCurvature(downsampled)
        } else {
            findMaximumCurvature(kDistances)
        }

        // --- MACRO-CONCEPT RELAXATION ---
        // Leaves require strict, tight granularization (Knee Epsilon) to split logically.
        // Parents (like the Root) contain disconnected, sparse outliers. The strict knee traps them as noise.
        // Relaxing the radius to the robust median of the k-distances allows macro-concepts to form.
        // DYNAMIC MEGA-NODE EXCEPTION: If a leaf contains > 30% of total taxonomy queries, it is a mega-node.
        val isMegaNode = n.toDouble() > (totalTaxonomyQueries * 0.3)
        val medianEps = kDistances[n / 2]
        val baseEps = if (isLeaf && !isMegaNode) kneeEps else maxOf(kneeEps, medianEps)

        // DENSITY-BASED CONSERVATIVE LINEAR SCALING
        // Epsilon shrinks proportionally to the node's local query size relative to the total active query pool, floor at 0.70
        val ratio = n.toDouble() / totalTaxonomyQueries
        val densityMultiplier = (1.0 - (ratio * 0.3)).coerceIn(0.7, 1.0)
        val eps = (baseEps * densityMultiplier).coerceIn(config.formalism.dbscanEpsFloor, config.formalism.dbscanEpsCeiling)

        log.debug("Auto-tuned Cosine Epsilon (isLeaf=$isLeaf, totalTaxonomyQueries=$totalTaxonomyQueries, isMegaNode=$isMegaNode): Knee=$kneeEps, Median=$medianEps, Base=$baseEps, DensityMultiplier=${"%.4f".format(java.util.Locale.US, densityMultiplier)}, Final=$eps")

        // 4. Standard DBSCAN Execution
        val visited = BooleanArray(n)
        val inCluster = BooleanArray(n)
        val clusters = mutableListOf<List<Embedding>>()

        for (i in 0 until n) {
            if (visited[i]) continue
            visited[i] = true

            val neighbors = getNeighbors(i, distMatrix, eps)
            if (neighbors.size >= minPts) {
                val cluster = mutableListOf<Embedding>()
                clusters.add(cluster)

                cluster.add(sampledEmbeddings[i])
                inCluster[i] = true

                val seeds = neighbors.toMutableList()
                val inSeeds = BooleanArray(n)
                for (idx in seeds) {
                    inSeeds[idx] = true
                }
                var seedIdx = 0

                while (seedIdx < seeds.size) {
                    val currentP = seeds[seedIdx]
                    if (!visited[currentP]) {
                        visited[currentP] = true
                        val currentNeighbors = getNeighbors(currentP, distMatrix, eps)
                        if (currentNeighbors.size >= minPts) {
                            for (cn in currentNeighbors) {
                                if (!inSeeds[cn]) {
                                    seeds.add(cn)
                                    inSeeds[cn] = true
                                }
                            }
                        }
                    }
                    if (!inCluster[currentP]) {
                        cluster.add(sampledEmbeddings[currentP])
                        inCluster[currentP] = true
                    }
                    seedIdx++
                }
            }
        }

        val filteredClusters = clusters.filter { it.size >= minPts }

        if (!isDownsampled || filteredClusters.isEmpty()) {
            return filteredClusters
        }

        // Calculate centroid for each cluster
        val centroids = filteredClusters.map { cluster ->
            val dims = cluster[0].dimensions
            val mean = DoubleArray(dims)
            for (emb in cluster) {
                for (d in 0 until dims) {
                    mean[d] += emb.values[d].toDouble()
                }
            }
            for (d in 0 until dims) {
                mean[d] /= cluster.size.toDouble()
            }
            mean
        }

        // Assign all original embeddings to the closest cluster centroid if within eps
        val fullClusters = List(filteredClusters.size) { mutableListOf<Embedding>() }
        for (emb in embeddings) {
            var bestIdx = -1
            var minDist = Double.MAX_VALUE
            for (idx in centroids.indices) {
                val dist = calculateCosineDistance(emb.toDoubleArray(), centroids[idx])
                if (dist < minDist) {
                    minDist = dist
                    bestIdx = idx
                }
            }
            if (bestIdx != -1 && minDist <= eps) {
                fullClusters[bestIdx].add(emb)
            }
        }

        return fullClusters.filter { it.size >= minPts }
    }

    /**
     * Finds the point of maximum orthogonal curvature (the "knee") in a sorted curve.
     * This mathematically separates dense cluster inliers from sparse spatial outliers.
     */
    private fun findMaximumCurvature(sortedDistances: DoubleArray): Double {
        if (sortedDistances.size < 3) return sortedDistances.lastOrNull() ?: 0.1

        val n = sortedDistances.size
        val yMin = sortedDistances.first()
        val yMax = sortedDistances.last()

        // Line equation components from first point (0, yMin) to last point (n-1, yMax): Ax + By + C = 0
        val a = yMax - yMin
        val b = -(n - 1.0)
        val c = (n - 1.0) * yMin

        var maxDist = -1.0
        var bestIndex = 0

        // Find the point on the curve furthest away from the straight line
        for (i in 0 until n) {
            val y = sortedDistances[i]
            val distToLine = abs(a * i + b * y + c) / sqrt(a * a + b * b)

            if (distToLine > maxDist) {
                maxDist = distToLine
                bestIndex = i
            }
        }

        return sortedDistances[bestIndex].coerceAtLeast(1e-4)
    }

    private fun getNeighbors(index: Int, distMatrix: Array<DoubleArray>, eps: Double): List<Int> {
        val neighbors = mutableListOf<Int>()
        for (i in distMatrix.indices) {
            if (distMatrix[index][i] <= eps) {
                neighbors.add(i)
            }
        }
        return neighbors
    }

    private fun getRoot(node: GraphNode): GraphNode {
        var curr = node
        val visited = mutableSetOf<String>()
        while (curr.parents.isNotEmpty() && visited.add(curr.id)) {
            curr = curr.parents.first()
        }
        return curr
    }

}
