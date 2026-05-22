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

/**
 * Implements Phase 4: Discover (Adaptive Splitting).
 * Upgraded with Angular Metrics (Cosine Distance), Maximum Curvature (Knee Detection),
 * Context-Aware Epsilon Relaxation, and Maximum Depth Boundary restrictions.
 */
@Service
class TaxonomySplitter(
    private val config: TaxonomyConfig,
    private val llmClient: TaxonomyLlmClient
) {
    private val log = LoggerFactory.getLogger(TaxonomySplitter::class.java)
    private val llmSemaphore = Semaphore(5) // Throttle parallel LLM calls

    suspend fun splitNodesRecursive(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
        if (visited.contains(node.id)) return
        visited.add(node.id)

        val currentChildren = node.children.toList()
        for (child in currentChildren) {
            splitNodesRecursive(child, visited)
        }

        // Use splitBaseThreshold from the new Thermodynamic Formalism
        val threshold = config.formalism.splitBaseThreshold

        if (node.queries.size > threshold) {
            // BOUNDARY ENFORCEMENT: Check if the node has hit the maximum allowed depth
            if (node.depth >= config.formalism.maxDepth) {
                log.info("Node '${node.label}' exceeds density threshold (${node.queries.size} > $threshold) but has reached max depth (${config.formalism.maxDepth}). Preventing further splits.")
                return
            }

            log.info("Node '${node.label}' exceeds density threshold (${node.queries.size} > $threshold). Scanning for emergent concepts...")

            // 1. Try splitting based on GMM component "clues" first (Partitioning)
            var clusters = if (node.distribution != null && node.distribution!!.components.size > 1) {
                partitionByGmm(node)
            } else emptyList()

            // 2. Fallback to DBSCAN if GMM is monolithic or partitioning failed to diversify
            if (clusters.size <= 1) {
                clusters = performDbscan(node.queries, config.formalism.splitMinThreshold, node.isLeaf)
            }

            if (clusters.isNotEmpty()) {
                val validClusters = clusters.filter { cluster ->
                    // 1. Check Relative Max Size ceiling
                    // DYNAMIC CEILING: Root (0) and Macro-Nodes (1) must split to bootstrap growth.
                    // Ceiling starts at 1.0 and decays to the configured relative-max-size.
                    val effectiveRelativeMaxSize = if (node.depth <= 1) 1.0 else config.formalism.relativeMaxSize
                    
                    if (cluster.size > node.queries.size * effectiveRelativeMaxSize) {
                        log.warn("Cluster in '${node.label}' (depth ${node.depth}) violates Relative Max Size ceiling (${cluster.size} > ${node.queries.size} * $effectiveRelativeMaxSize). Skipping.")
                        return@filter false
                    }

                    // 2. p-BIC Validation
                    val currentGmm = node.distribution ?: return@filter true
                    
                    // Current Log-Likelihood (Stable)
                    val currentLL = StatisticsUtils.calculateLogLikelihood(currentGmm, node.queries)
                    val currentPBic = StatisticsUtils.calculatePBic(currentGmm, node.queries, config.formalism.pBicLambda)
                    
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
                    val proposedPBic = StatisticsUtils.calculatePBic(proposedGmm, combinedDataset, config.formalism.pBicLambda)
                    
                    // Recalculate current for same dataset
                    val currentLL_on_all = StatisticsUtils.calculateLogLikelihood(currentGmm, combinedDataset)
                    val currentPBic_on_all = StatisticsUtils.calculatePBic(currentGmm, combinedDataset, config.formalism.pBicLambda)

                    log.info("Split Evaluation for '${node.label}': CurrentBIC=$currentPBic_on_all, ProposedBIC=$proposedPBic")
                    
                    if (node.depth == 1) {
                        val improvement = (proposedLL - currentLL_on_all)
                        log.info("p-BIC failed for Macro-Node '${node.label}', LL improvement: $improvement")
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
                        log.info("Cluster in '${node.label}' too similar to existing sibling. Skipping.")
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
                        // Only create a child if it partitions a specific subset (< 80% of parent mass)
                        cluster.size < node.queries.size * 0.8
                    } else true

                    if (shouldDiversify) {
                        log.info("Discovered ${validClusters.size} valid sub-clusters in '${node.label}'. Spawning new children...")
                        
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
                    } else {
                        log.info("Single sub-cluster in '${node.label}' is too redundant. Skipping child creation to prevent clones.")
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
        return clusters.filter { it.size >= config.formalism.splitMinThreshold }
    }

    private suspend fun createNodeFromCluster(cluster: List<Embedding>, parent: GraphNode): GraphNode {
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
        
        val representativeSamples = (innerCore + middleShell + outerBoundary).map { it.first.rawText }.distinct()

        // 3. Get branch lineage
        val lineage = mutableListOf<String>()
        var current: GraphNode? = parent
        while (current != null) {
            lineage.add(0, current.label)
            current = current.parents.firstOrNull()
        }

        val siblingLabels = parent.children.map { it.label }
        val prompt = TaxoPrompts.clusterLabeling(
            querySamples = representativeSamples,
            parentLabel = parent.label,
            siblingLabels = siblingLabels,
            branchHistory = lineage
        )

        val jsonResponse = llmClient.generateClusterLabel(prompt)
        val label = extractLabelFromJson(jsonResponse) ?: "Discovered Concept"

        log.info("LLM mapped new cluster (${cluster.size} items) -> '$label' using Stratified Sampling")

        val newNode = GraphNode(label = label, depth = parent.depth + 1)
        newNode.queries.addAll(cluster)
        
        // RECURSIVE DECOMPOSITION: If the new cluster is still too large (> 500 items), 
        // try to split it immediately to prevent "Domain Eating".
        if (cluster.size > config.formalism.splitBaseThreshold * 5 && newNode.depth < config.formalism.maxDepth) {
            log.info("Node '$label' is a macro-cluster. Triggering immediate sub-decomposition.")
            splitNodesRecursive(newNode)
        }

        return newNode
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
    private fun performDbscan(embeddings: List<Embedding>, minPts: Int, isLeaf: Boolean): List<List<Embedding>> {
        if (embeddings.size < minPts) return emptyList()

        val n = embeddings.size
        val distMatrix = Array(n) { DoubleArray(n) }

        // 1. Parallelize Pairwise Cosine Distances calculation
        runBlocking(Dispatchers.Default) {
            (0 until n).chunked(maxOf(1, n / Runtime.getRuntime().availableProcessors())).map { chunk ->
                launch {
                    for (i in chunk) {
                        for (j in i + 1 until n) {
                            var dotProduct = 0.0
                            var normI = 0.0
                            var normJ = 0.0
                            val dims = embeddings[i].dimensions

                            for (d in 0 until dims) {
                                val vi = embeddings[i].values[d].toDouble()
                                val vj = embeddings[j].values[d].toDouble()
                                dotProduct += vi * vj
                                normI += vi * vi
                                normJ += vj * vj
                            }

                            val similarity = if (normI > 0 && normJ > 0) dotProduct / (sqrt(normI) * sqrt(normJ)) else 0.0
                            val dist = (1.0 - similarity).coerceAtLeast(0.0)

                            distMatrix[i][j] = dist
                            distMatrix[j][i] = dist
                        }
                    }
                }
            }.forEach { it.join() }
        }

        // 2. Compute k-NN distances for each point
        val kDistances = DoubleArray(n)
        val k = minPts.coerceAtMost(n - 1)
        for (i in 0 until n) {
            val distancesFromI = distMatrix[i].sorted()
            kDistances[i] = distancesFromI[k]
        }
        kDistances.sort() // Sort to form the K-Distance Graph

        // 3. Mathematical Knee/Elbow Detection for Optimal Epsilon
        val kneeEps = findMaximumCurvature(kDistances)

        // --- MACRO-CONCEPT RELAXATION ---
        // Leaves require strict, tight granularization (Knee Epsilon) to split logically.
        // Parents (like the Root) contain disconnected, sparse outliers. The strict knee traps them as noise.
        // Relaxing the radius to the mean of the k-distances allows macro-concepts to form and drains the Root.
        // MEGA-NODE EXCEPTION: If a leaf is massive (> 250 q), it has become a "de-facto root" and needs relaxation.
        val isMegaNode = embeddings.size > 250
        val eps = if (isLeaf && !isMegaNode) kneeEps else maxOf(kneeEps, kDistances.average())

        log.debug("Auto-tuned Cosine Epsilon (isLeaf=$isLeaf): Knee=$kneeEps, Final=$eps")

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

                cluster.add(embeddings[i])
                inCluster[i] = true

                val seeds = neighbors.toMutableList()
                var seedIdx = 0

                while (seedIdx < seeds.size) {
                    val currentP = seeds[seedIdx]
                    if (!visited[currentP]) {
                        visited[currentP] = true
                        val currentNeighbors = getNeighbors(currentP, distMatrix, eps)
                        if (currentNeighbors.size >= minPts) {
                            for (cn in currentNeighbors) {
                                if (!seeds.contains(cn)) seeds.add(cn)
                            }
                        }
                    }
                    if (!inCluster[currentP]) {
                        cluster.add(embeddings[currentP])
                        inCluster[currentP] = true
                    }
                    seedIdx++
                }
            }
        }

        return clusters.filter { it.size >= minPts }
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

    private fun extractLabelFromJson(json: String): String? {
        val regex = """"label"\s*:\s*"([^"]+)"""".toRegex()
        return regex.find(json)?.groups?.get(1)?.value
    }
}
