package org.eclipse.lmos.arc.app.taxonomy.operations

import kotlinx.coroutines.*
import org.eclipse.lmos.arc.app.taxonomy.Embedding
import org.eclipse.lmos.arc.app.taxonomy.GmmParams
import org.eclipse.lmos.arc.app.taxonomy.GraphNode
import org.eclipse.lmos.arc.app.taxonomy.TaxonomyConfig
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.StatisticsUtils
import taxonomy.TaxoPrompts
import java.util.concurrent.ConcurrentHashMap
import kotlin.math.*
import dev.langchain4j.model.chat.request.json.JsonObjectSchema
import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive

/**
 * Implements Phase 5: Optimize (Parenting, Merging & Pruning).
 * Polishes the DAG by deleting empty nodes, combining highly similar sibling domains,
 * creating polyhierarchical cross-links, and enforcing strict transitive reduction.
 * Adjusted to utilize the Thermodynamic Formalism parameters (tauFit, tauReparent, tauMerge).
 */
@Service
class TaxonomyMerger(
    private val config: TaxonomyConfig,
    private val llmClient: TaxonomyLlmClient,
    private val datasetFetcher: org.eclipse.lmos.arc.app.MMLUDatasetFetcher
) {
    private val log = LoggerFactory.getLogger(TaxonomyMerger::class.java)

    suspend fun optimizeHierarchy(root: GraphNode) {
        // 1. Prune dead or starved nodes (Bottom-Up)
        pruneUnrelevantNodes(root)
 
        // 2. Sibling Reparenting & Overarching Synthesis
        synthesizeOverarchingDomains(root)
 
        // 3. Merge highly overlapping siblings
        mergeSimilarSiblings(root)
 
        // 4. Global Redundancy Merging (Cross-branch deduplication)
        mergeGlobalRedundancies(root)
 
        // 5. Parenting (Cross-linking across branches)
        evaluateCrossLinks(root)
 
        // 6. Prune passthrough nodes (Collapse single-child chains)
        prunePassthroughNodes(root)
 
        // 8. Final Clean: Prune any starved/empty leaf nodes created during optimization passes
        pruneUnrelevantNodes(root)
 
        // 7. Global Transitive Reduction (Guarantee DAG topological purity)
        transitiveReduction(root)
    }

    private suspend fun mergeGlobalRedundancies(root: GraphNode) = coroutineScope {
        val allNodes = getAllNodes(root).filter { it.depth > 0 && it.distribution != null }.toList()
        if (allNodes.size < 2) return@coroutineScope

        log.info("Checking for global semantic redundancies across ${allNodes.size} nodes...")

        val mergedIds = ConcurrentHashMap.newKeySet<String>()

        for (i in 0 until allNodes.size) {
            val nodeA = allNodes[i]
            if (mergedIds.contains(nodeA.id)) continue

            val redundancies = (i + 1 until allNodes.size).chunked(50).map { chunk ->
                async(Dispatchers.Default) {
                    chunk.mapNotNull { j ->
                        val nodeB = allNodes[j]
                        val gmmB = nodeB.distribution ?: return@mapNotNull null
                        if (isDescendant(nodeA, nodeB) || isDescendant(nodeB, nodeA)) return@mapNotNull null

                        val similarity = StatisticsUtils.gmmSimilarity(nodeA.distribution!!, gmmB)
                        val sizeA = nodeA.getRecursiveQueryCount()
                        val sizeB = nodeB.getRecursiveQueryCount()
                        val sizeRatio = minOf(sizeA, sizeB).toDouble() / maxOf(sizeA, sizeB).toDouble().coerceAtLeast(1.0)
                        val effectiveTauMerge = config.formalism.tauMerge - (0.05 * (1.0 - sizeRatio))
                        if (similarity >= effectiveTauMerge) {
                            nodeB to similarity
                        } else null
                    }
                }
            }.awaitAll().flatten()

            for ((nodeB, similarity) in redundancies) {
                if (!mergedIds.contains(nodeB.id)) {
                    log.info(
                        "[REDUNDANCY] Fusing '${nodeB.label}' into '${nodeA.label}' (Similarity: ${"%.4f".format(java.util.Locale.US, similarity)})"
                    )
                    fuseNodes(nodeA, nodeB)
                    mergedIds.add(nodeB.id)
                }
            }
        }
    }

    private fun blendGmmParams(distributions: List<GmmParams>): GmmParams? {
        val validDists = distributions.filter { it.components.isNotEmpty() }
        if (validDists.isEmpty()) return null
        if (validDists.size == 1) return validDists[0]
        
        val totalSamples = validDists.sumOf { it.totalSamples }.toDouble().coerceAtLeast(1.0)
        val blendedComponents = validDists.flatMap { dist ->
            val weightMultiplier = dist.totalSamples.toDouble() / totalSamples
            dist.components.map { c ->
                c.copy(weight = c.weight * weightMultiplier)
            }
        }
        val maxEmpiricalThreshold = validDists.maxOf { it.empiricalThreshold }
        return GmmParams(blendedComponents, maxEmpiricalThreshold)
    }

    private fun fuseNodes(target: GraphNode, source: GraphNode) {
        // 1. Combine queries
        target.queries.addAll(source.queries)

        // 2. Statistical GMM blend (Weighted component combination)
        val distA = target.distribution
        val distB = source.distribution
        val blended = if (distA != null && distB != null) {
            blendGmmParams(listOf(distA, distB))
        } else distA ?: distB

        target.distribution = blended

        // 3. Redirect parents
        source.parents.forEach { parent ->
            if (parent != target) {
                parent.children.remove(source)
                parent.children.add(target)
                target.parents.add(parent)
            }
        }

        // 4. Redirect children
        source.children.forEach { child ->
            if (child != target) {
                child.parents.remove(source)
                child.parents.add(target)
                target.children.add(child)
            }
        }

        // 5. Clean up source
        source.parents.clear()
        source.children.clear()
        source.queries.clear()
    }

    private fun pruneUnrelevantNodes(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
        if (visited.contains(node.id)) return
        visited.add(node.id)

        val currentChildren = node.children.toList()
        for (child in currentChildren) {
            pruneUnrelevantNodes(child, visited)
        }

        // RELEVANCE GUARD: Identify nodes that are "starved" or semantically insignificant.
        val nodesToPrune = node.children.filter { child ->
            val totalQueriesInBranch = gatherAllEmbeddingsInBranch(child).size
            
            val isStarved = child.isLeaf && totalQueriesInBranch < 5
            val isEmptyParent = !child.isLeaf && child.children.isEmpty()
            val isDeadLeaf = child.isLeaf && child.queries.isEmpty()

            isStarved || isEmptyParent || isDeadLeaf
        }

        if (nodesToPrune.isNotEmpty()) {
            nodesToPrune.forEach { target ->
                log.info("[PRUNED] '${target.label}' (Reason: Starved or Empty)")
                node.queries.addAll(target.queries)
                node.children.remove(target)
                target.parents.remove(node)
                target.parents.forEach { p -> p.children.remove(target) }
                target.children.forEach { c -> c.parents.remove(target) }
            }
        }
    }

    private suspend fun synthesizeOverarchingDomains(
        node: GraphNode, 
        visited: MutableSet<String> = java.util.concurrent.ConcurrentHashMap.newKeySet()
    ) {
        if (visited.contains(node.id)) return
        visited.add(node.id)

        val children = node.children.toList()
        coroutineScope {
            children.map { child ->
                async(Dispatchers.Default) {
                    synthesizeOverarchingDomains(child, visited)
                }
            }
        }.awaitAll()

        if (children.size < 2) return

        // 1. Identify pairs with high symmetric overlap in parallel
        val pairs = coroutineScope {
            val jobs = mutableListOf<Deferred<Pair<GraphNode, GraphNode>?>>()
            for (i in 0 until children.size) {
                for (j in i + 1 until children.size) {
                    val nodeA = children[i]
                    val nodeB = children[j]
                    jobs.add(async(Dispatchers.Default) {
                        val gmmA = nodeA.distribution ?: return@async null
                        val gmmB = nodeB.distribution ?: return@async null
                        val avgDb = gmmA.components.map { cA ->
                            gmmB.components.minOf { cB ->
                                StatisticsUtils.bhattacharyyaDistance(cA.mean!!, cA.diagonalCovariance!!, cB.mean!!, cB.diagonalCovariance!!)
                            }
                        }.average()
                        if (avgDb < 0.4) {
                            nodeA to nodeB
                        } else null
                    })
                }
            }
            jobs.awaitAll().filterNotNull()
        }

        if (pairs.isEmpty()) return

        // Group highly overlapping siblings using Union-Find to handle multi-node overlapping groups
        val uf = UnionFind(children)
        for ((nodeA, nodeB) in pairs) {
            uf.union(nodeA, nodeB)
        }

        val clusters = children.groupBy { uf.find(it) }.values.filter { it.size > 1 }
        if (clusters.isEmpty()) return

        log.info("[SYNTHESIS] Found ${clusters.size} overarching groups under parent '${node.label}'. Synthesizing hypernyms...")

        // 2. Synthesize Overarching Parents concurrently
        val synthesizedParents = coroutineScope {
            clusters.map { cluster ->
                async(Dispatchers.Default) {
                    val samples = cluster.flatMap { gatherAllEmbeddingsInBranch(it) }
                        .distinctBy { it.rawText }
                        .shuffled()
                        .take(20)
                        .map { it.rawText }

                    val domainAnchors = samples.mapNotNull { question ->
                        datasetFetcher.getDetailsForQuery(question)?.category?.split("_", "-")?.joinToString(" ") { word ->
                            word.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
                        }
                    }.groupBy { it }.mapValues { it.value.size }
                        .entries.sortedByDescending { it.value }
                        .map { "${it.key} (${it.value} queries)" }

                    val prompt = TaxoPrompts.clusterLabeling(
                        querySamples = samples,
                        parentLabel = node.label,
                        siblingLabels = node.children.filter { it !in cluster }.map { it.label },
                        branchHistory = emptyList(),
                        domainAnchors = domainAnchors,
                        depth = node.depth + 1
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
                    val hypernym = try {
                        Json.parseToJsonElement(jsonResponse).jsonObject["label"]?.jsonPrimitive?.content
                            ?: cluster.joinToString(" / ") { it.label }
                    } catch (e: Exception) {
                        log.warn("Structured hypernym parse failed. Raw: $jsonResponse")
                        cluster.joinToString(" / ") { it.label }
                    }
                    
                    Triple(cluster, hypernym, blendGmmParams(cluster.mapNotNull { it.distribution }))
                }
            }.awaitAll()
        }

        // 3. Apply fusions in a single pass sequentially
        for ((cluster, hypernym, combinedGmm) in synthesizedParents) {
            log.info("[SYNTHESIS] Synthesized: Hypernym '$hypernym' for group ${cluster.map { it.label }}")

            val newParent = GraphNode(label = hypernym, depth = node.depth + 1)
            newParent.distribution = combinedGmm

            // Remove cluster children from parent, add newParent
            for (child in cluster) {
                node.children.remove(child)
                child.parents.remove(node)
                
                newParent.children.add(child)
                child.parents.add(newParent)
            }
            node.children.add(newParent)
            newParent.parents.add(node)
        }
    }

    private fun gatherAllEmbeddingsInBranch(node: GraphNode, visited: MutableSet<String> = mutableSetOf()): List<Embedding> {
        if (visited.contains(node.id)) return emptyList()
        visited.add(node.id)
        val result = mutableListOf<Embedding>()
        result.addAll(node.queries)
        node.children.forEach { result.addAll(gatherAllEmbeddingsInBranch(it, visited)) }
        return result
    }

    private suspend fun mergeSimilarSiblings(
        node: GraphNode, 
        visited: MutableSet<String> = java.util.concurrent.ConcurrentHashMap.newKeySet()
    ) {
        if (visited.contains(node.id)) return
        visited.add(node.id)

        val currentChildren = node.children.toList()
        coroutineScope {
            currentChildren.map { child ->
                async(Dispatchers.Default) {
                    mergeSimilarSiblings(child, visited)
                }
            }
        }.awaitAll()

        val children = node.children.toList()
        if (children.size < 2) return

        log.debug("Evaluating sibling merges for parent '${node.label}' with ${children.size} children...")

        // 1. Parallel pairwise GMM similarity calculations
        val pairsToMerge = coroutineScope {
            val jobs = mutableListOf<Deferred<Triple<GraphNode, GraphNode, Double>?>>()
            for (i in 0 until children.size) {
                for (j in i + 1 until children.size) {
                    val nodeA = children[i]
                    val nodeB = children[j]
                    jobs.add(async(Dispatchers.Default) {
                        val gmmA = nodeA.distribution ?: return@async null
                        val gmmB = nodeB.distribution ?: return@async null
                        val similarity = StatisticsUtils.gmmSimilarity(gmmA, gmmB)
                        val sizeA = nodeA.getRecursiveQueryCount()
                        val sizeB = nodeB.getRecursiveQueryCount()
                        val sizeRatio = minOf(sizeA, sizeB).toDouble() / maxOf(sizeA, sizeB).toDouble().coerceAtLeast(1.0)
                        val effectiveTauMerge = config.formalism.tauMerge - (0.05 * (1.0 - sizeRatio))
                        if (similarity >= effectiveTauMerge) {
                            Triple(nodeA, nodeB, similarity)
                        } else null
                    })
                }
            }
            jobs.awaitAll().filterNotNull()
        }

        if (pairsToMerge.isEmpty()) return

        // 2. Build connected components using Union-Find
        val uf = UnionFind(children)
        for ((nodeA, nodeB, _) in pairsToMerge) {
            uf.union(nodeA, nodeB)
        }

        // Group children by their representative root in Union-Find
        val clusters = children.groupBy { uf.find(it) }.values.filter { it.size > 1 }
        if (clusters.isEmpty()) return

        log.info("[MERGE] Found ${clusters.size} merge groups under parent '${node.label}'. Invoking LLM labeling...")

        // 3. Concurrent LLM hypernym labeling via coroutines
        val mergedNodes = coroutineScope {
            clusters.map { cluster ->
                async(Dispatchers.Default) {
                    val combinedQueries = cluster.flatMap { it.queries }.distinctBy { it.rawText }
                    
                    val label = if (combinedQueries.isNotEmpty()) {
                        // Stratified sampling
                        val dims = combinedQueries[0].dimensions
                        val centroid = DoubleArray(dims)
                        for (emb in combinedQueries) {
                            for (d in 0 until dims) centroid[d] += emb.values[d].toDouble()
                        }
                        for (d in 0 until dims) centroid[d] /= combinedQueries.size.toDouble()

                        val sortedByDistance = combinedQueries.map { it to calculateCosineDistance(it.toDoubleArray(), centroid) }
                            .sortedBy { it.second }

                        val representativeSamples = (sortedByDistance.take(10).map { it.first.rawText } + 
                                                     sortedByDistance.takeLast(10).map { it.first.rawText }).distinct()

                        val lineage = mutableListOf<String>()
                        var curr: GraphNode? = node
                        val visitedLineage = mutableSetOf<String>()
                        while (curr != null && visitedLineage.add(curr.id)) {
                            lineage.add(0, curr.label)
                            curr = curr.parents.firstOrNull()
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
                            parentLabel = node.label,
                            siblingLabels = node.children.filter { it !in cluster }.map { it.label },
                            branchHistory = lineage,
                            domainAnchors = domainAnchors,
                            depth = node.depth + 1
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
                                ?: cluster.joinToString(" & ") { it.label }
                        } catch (e: Exception) {
                            log.warn("Structured merge label parse failed. Raw: $jsonResponse")
                            cluster.joinToString(" & ") { it.label }
                        }
                    } else {
                        cluster.joinToString(" & ") { it.label }
                    }
                    
                    Triple(cluster, combinedQueries, label)
                }
            }.awaitAll()
        }

        // 4. Apply fusions in a single pass sequentially
        for ((cluster, combinedQueries, newLabel) in mergedNodes) {
            log.info("[MERGE] Merged: ${cluster.map { it.label }} -> '$newLabel'")
            
            // Create the new merged node
            val mergedNode = GraphNode(label = newLabel, depth = node.depth + 1)
            mergedNode.queries.addAll(combinedQueries)

            // Statistical GMM Blend of the cluster
            val validGmmList = cluster.mapNotNull { it.distribution }
            mergedNode.distribution = blendGmmParams(validGmmList)

            // Redirect children of all nodes in the cluster to the mergedNode
            val allChildren = cluster.flatMap { it.children }
                .filter { it !in cluster }
                .toSet()

            for (child in allChildren) {
                for (srcNode in cluster) {
                    child.parents.remove(srcNode)
                }
                child.parents.add(mergedNode)
                mergedNode.children.add(child)
            }

            // Redirect parents of all nodes in the cluster to the mergedNode
            val rawParents = cluster.flatMap { it.parents }
                .filter { it !in cluster }
                .toSet()

            // Filter parent list: remove parent nodes that are already ancestors of other parents in rawParents
            val optimizedParents = rawParents.filter { p1 ->
                !rawParents.any { p2 -> p1.id != p2.id && isDescendant(p1, p2) }
            }

            for (p in rawParents) {
                for (srcNode in cluster) {
                    p.children.remove(srcNode)
                }
            }

            for (p in optimizedParents) {
                p.children.add(mergedNode)
                mergedNode.parents.add(p)
            }

            // Explicitly clean up all merged source nodes to avoid memory leaks
            for (srcNode in cluster) {
                srcNode.parents.clear()
                srcNode.children.clear()
                srcNode.queries.clear()
            }
        }
    }

    private class UnionFind(nodes: List<GraphNode>) {
        private val parentMap = nodes.associateWith { it }.toMutableMap()
        
        fun find(n: GraphNode): GraphNode {
            var curr = n
            while (parentMap[curr] != curr) {
                parentMap[curr] = parentMap[parentMap[curr]!!]!!
                curr = parentMap[curr]!!
            }
            return curr
        }
        
        fun union(n1: GraphNode, n2: GraphNode) {
            val root1 = find(n1)
            val root2 = find(n2)
            if (root1.id != root2.id) {
                parentMap[root1] = root2
            }
        }
    }

    private fun calculateGmmCentroid(gmm: GmmParams): DoubleArray? {
        val validComponents = gmm.components.filter { it.mean != null }
        if (validComponents.isEmpty()) return null
        
        val firstMean = validComponents.first().mean ?: return null
        val dims = firstMean.size
        val centroid = DoubleArray(dims)
        var totalWeight = 0.0
        
        for (comp in validComponents) {
            val mean = comp.mean ?: continue
            val weight = comp.weight
            for (d in 0 until dims) {
                centroid[d] += mean[d] * weight
            }
            totalWeight += weight
        }
        
        if (totalWeight > 0.0) {
            for (d in 0 until dims) {
                centroid[d] /= totalWeight
            }
        }
        return centroid
    }

    private suspend fun evaluateCrossLinks(root: GraphNode) = coroutineScope {
        val allNodes = getAllNodes(root).filter { it.depth > 0 }

        for (node in allNodes) {
            val nodeGmm = node.distribution ?: continue
            val nodeCentroid = calculateGmmCentroid(nodeGmm) ?: continue

            val potentialParents = allNodes.filter { potentialParent ->
                node != potentialParent &&
                        !node.parents.contains(potentialParent) &&
                        !isDescendant(node, potentialParent) &&
                        !isDescendant(potentialParent, node) &&
                        potentialParent.depth <= node.depth &&
                        (node.depth - potentialParent.depth) <= 3 &&
                        potentialParent.distribution?.let { parentGmm ->
                            calculateGmmCentroid(parentGmm)?.let { parentCentroid ->
                                calculateCosineDistance(nodeCentroid, parentCentroid) <= 0.48
                            }
                        } ?: false
            }

            if (potentialParents.isEmpty()) continue

            val crossLinks = potentialParents.chunked(50).map { chunk ->
                async(Dispatchers.Default) {
                    chunk.mapNotNull { potentialParent ->
                        val parentGmm = potentialParent.distribution ?: return@mapNotNull null

                        // Use the new Asymmetric Entailment Scorer
                        val entailmentScore = StatisticsUtils.calculateEntailmentScore(
                            nodeGmm, parentGmm, config.formalism.inclusionScalingFactor
                        )

                        // If the score exceeds tauReparent, the child is likely a sub-concept of this parent
                        if (entailmentScore >= config.formalism.tauReparent) {
                             potentialParent to entailmentScore
                        } else null
                    }
                }
            }.awaitAll().flatten()

            for ((potentialParent, score) in crossLinks) {
                log.info(
                    "Cross-linked '${node.label}' -> '${potentialParent.label}' (Entailment: ${"%.4f".format(java.util.Locale.US, score)})"
                )
                node.parents.add(potentialParent)
                potentialParent.children.add(node)

                // Clean up redundant shortcuts created by cross-linking
                val redundantParents = node.parents.filter { p ->
                    p.id != potentialParent.id && isDescendant(p, potentialParent)
                }

                for (rp in redundantParents) {
                    log.info("Cross-link Reduction: Severed redundant parent '${rp.label}' from '${node.label}'")
                    node.parents.remove(rp)
                    rp.children.remove(node)
                }
            }
        }
    }

    private fun transitiveReduction(root: GraphNode) {
        val allNodes = getAllNodes(root)
        for (node in allNodes) {
            val redundantParents = node.parents.filter { p1 ->
                node.parents.any { p2 -> p1.id != p2.id && isDescendant(p1, p2) }
            }

            for (rp in redundantParents) {
                log.info("Transitive Reduction: Severed redundant shortcut '${rp.label}' -> '${node.label}'")
                node.parents.remove(rp)
                rp.children.remove(node)
            }
        }
    }

    private fun prunePassthroughNodes(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
        if (visited.contains(node.id)) return
        visited.add(node.id)

        val currentChildren = node.children.toList()
        for (child in currentChildren) {
            prunePassthroughNodes(child, visited)
        }

        // Identify passthrough nodes: 
        // 1. Exactly 1 child AND (0 queries OR statistically identical to child)
        // 2. Not the Root node
        val nodesToBypass = node.children.filter { child ->
            if (child.children.size != 1 || child.depth == 0) return@filter false
            
            val grandchild = child.children.first()
            val sim = child.distribution?.let { cGmm ->
                grandchild.distribution?.let { gGmm ->
                    StatisticsUtils.gmmSimilarity(cGmm, gGmm)
                }
            } ?: 0.0
            
            child.queries.isEmpty() || (sim > 0.98 && child.queries.size < 50)
        }

        for (passthrough in nodesToBypass) {
            val grandchild = passthrough.children.first()
            log.info("Collapsed Chain: '${passthrough.label}' -> '${grandchild.label}'")
            
            // Move any residual queries
            grandchild.queries.addAll(passthrough.queries)
            
            // Redirect parent (node) to grandchild
            node.children.remove(passthrough)
            node.children.add(grandchild)
            
            grandchild.parents.remove(passthrough)
            grandchild.parents.add(node)
            
            // Handle other parents
            passthrough.parents.forEach { p ->
                if (p != node) {
                    p.children.remove(passthrough)
                    p.children.add(grandchild)
                    grandchild.parents.add(p)
                }
            }
            
            passthrough.parents.clear()
            passthrough.children.clear()
            passthrough.queries.clear()
        }
    }

    private fun getAllNodes(node: GraphNode, visited: MutableSet<GraphNode> = mutableSetOf()): Set<GraphNode> {
        if (visited.contains(node)) return visited
        visited.add(node)
        node.children.forEach { getAllNodes(it, visited) }
        return visited
    }

    private fun isDescendant(
        node: GraphNode,
        potentialDescendant: GraphNode,
        visited: MutableSet<String> = mutableSetOf()
    ): Boolean {
        if (node.id == potentialDescendant.id) return true
        if (visited.contains(node.id)) return false
        visited.add(node.id)
        return node.children.any { isDescendant(it, potentialDescendant, visited) }
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
