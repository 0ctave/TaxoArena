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

/**
 * Implements Phase 5: Optimize (Parenting, Merging & Pruning).
 * Polishes the DAG by deleting empty nodes, combining highly similar sibling domains,
 * creating polyhierarchical cross-links, and enforcing strict transitive reduction.
 * Adjusted to utilize the Thermodynamic Formalism parameters (tauFit, tauReparent, tauMerge).
 */
@Service
class TaxonomyMerger(
    private val config: TaxonomyConfig,
    private val llmClient: TaxonomyLlmClient
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

                        // Using Hausdorff-like GMM similarity to preserve multi-modal identities
                        val similarity = StatisticsUtils.gmmSimilarity(nodeA.distribution!!, gmmB)

                        if (similarity >= config.formalism.tauMerge) {
                            nodeB to similarity
                        } else null
                    }
                }
            }.awaitAll().flatten()

            for ((nodeB, similarity) in redundancies) {
                if (!mergedIds.contains(nodeB.id)) {
                    log.info(
                        "Global Redundancy Found: '${nodeA.label}' and '${nodeB.label}' (Similarity: ${"%.4f".format(similarity)}). Fusing branches."
                    )
                    fuseNodes(nodeA, nodeB)
                    mergedIds.add(nodeB.id)
                }
            }
        }
    }

    private fun fuseNodes(target: GraphNode, source: GraphNode) {
        // 1. Combine queries
        target.queries.addAll(source.queries)

        // 2. Redirect parents
        source.parents.forEach { parent ->
            if (parent != target) {
                parent.children.remove(source)
                parent.children.add(target)
                target.parents.add(parent)
            }
        }

        // 3. Redirect children
        source.children.forEach { child ->
            if (child != target) {
                child.parents.remove(source)
                child.parents.add(target)
                target.children.add(child)
            }
        }

        // 4. Clean up source
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
                log.info("Pruning unrelevant node: '${target.label}' (Reason: Starved or Empty)")
                node.queries.addAll(target.queries)
                node.children.remove(target)
                target.parents.remove(node)
                target.parents.forEach { p -> p.children.remove(target) }
                target.children.forEach { c -> c.parents.remove(target) }
            }
        }
    }

    private suspend fun synthesizeOverarchingDomains(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
        if (visited.contains(node.id)) return
        visited.add(node.id)

        val children = node.children.toList()
        for (child in children) {
            synthesizeOverarchingDomains(child, visited)
        }

        if (children.size < 2) return

        // 1. Identify pairs with high symmetric overlap
        val pairs = mutableListOf<Pair<GraphNode, GraphNode>>()
        for (i in 0 until children.size) {
            for (j in i + 1 until children.size) {
                val nodeA = children[i]
                val nodeB = children[j]
                val gmmA = nodeA.distribution ?: continue
                val gmmB = nodeB.distribution ?: continue

                // Check symmetric overlap using Bhattacharyya
                val avgDb = gmmA.components.map { cA ->
                    gmmB.components.minOf { cB ->
                        StatisticsUtils.bhattacharyyaDistance(cA.mean!!, cA.diagonalCovariance!!, cB.mean!!, cB.diagonalCovariance!!)
                    }
                }.average()

                if (avgDb < 0.4) { // Heuristic: high symmetric overlap
                    pairs.add(nodeA to nodeB)
                }
            }
        }

        // 2. Synthesize Overarching Parent
        for ((nodeA, nodeB) in pairs) {
            if (!node.children.contains(nodeA) || !node.children.contains(nodeB)) continue

            log.info("Detected deep semantic overlap between '${nodeA.label}' and '${nodeB.label}'. Synthesizing hypernym.")

            val samples = (gatherAllEmbeddingsInBranch(nodeA).shuffled().take(10) + 
                          gatherAllEmbeddingsInBranch(nodeB).shuffled().take(10)).map { it.rawText }

            val prompt = TaxoPrompts.clusterLabeling(
                querySamples = samples,
                parentLabel = node.label,
                siblingLabels = node.children.filter { it != nodeA && it != nodeB }.map { it.label },
                branchHistory = emptyList()
            )

            val jsonResponse = llmClient.generateClusterLabel(prompt)
            val hypernym = extractLabelFromJson(jsonResponse) ?: "${nodeA.label} & ${nodeB.label}"

            log.info("Synthesized hypernym: '$hypernym' to group '${nodeA.label}' and '${nodeB.label}'")

            val newParent = GraphNode(label = hypernym, depth = node.depth + 1)
            
            node.children.remove(nodeA)
            node.children.remove(nodeB)
            node.children.add(newParent)
            newParent.parents.add(node)

            newParent.children.add(nodeA)
            newParent.children.add(nodeB)
            nodeA.parents.remove(node)
            nodeB.parents.remove(node)
            nodeA.parents.add(newParent)
            nodeB.parents.add(newParent)
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

    private suspend fun mergeSimilarSiblings(node: GraphNode, visited: MutableSet<String> = mutableSetOf()) {
        if (visited.contains(node.id)) return
        visited.add(node.id)

        val currentChildren = node.children.toList()
        for (child in currentChildren) {
            mergeSimilarSiblings(child, visited)
        }

        var merged = true
        while (merged) {
            merged = false
            val children = node.children.toList()
            if (children.size < 2) break

            for (i in 0 until children.size) {
                for (j in i + 1 until children.size) {
                    val nodeA = children[i]
                    val nodeB = children[j]
                    
                    if (nodeA.id == nodeB.id || nodeA.parents.isEmpty() || nodeB.parents.isEmpty()) continue

                    val gmmA = nodeA.distribution ?: continue
                    val gmmB = nodeB.distribution ?: continue

                    val similarity = StatisticsUtils.gmmSimilarity(gmmA, gmmB)

                    if (similarity >= config.formalism.tauMerge) {
                        log.info(
                            "Merging siblings '${nodeA.label}' and '${nodeB.label}' (Similarity: ${"%.4f".format(similarity)} >= ${config.formalism.tauMerge})"
                        )
                        executeMerge(node, nodeA, nodeB)
                        merged = true
                        break
                    }
                }
                if (merged) break
            }
        }
    }

    private suspend fun executeMerge(parent: GraphNode, nodeA: GraphNode, nodeB: GraphNode) {
        val combinedQueries = (nodeA.queries + nodeB.queries).distinctBy { it.rawText }
        
        parent.children.remove(nodeA)
        parent.children.remove(nodeB)
        nodeA.parents.remove(parent)
        nodeB.parents.remove(parent)

        if (combinedQueries.isEmpty() && nodeA.children.isEmpty() && nodeB.children.isEmpty()) {
            log.info("Merged empty nodes '${nodeA.label}' + '${nodeB.label}' -> Pruned.")
            return
        }

        val representativeSamples = if (combinedQueries.isNotEmpty()) {
            val dims = combinedQueries[0].dimensions
            val centroid = DoubleArray(dims)
            for (emb in combinedQueries) {
                for (d in 0 until dims) centroid[d] += emb.values[d].toDouble()
            }
            for (d in 0 until dims) centroid[d] /= combinedQueries.size.toDouble()

            val sortedByDistance = combinedQueries.map { it to calculateCosineDistance(it.toDoubleArray(), centroid) }
                .sortedBy { it.second }

            (sortedByDistance.take(10).map { it.first.rawText } + 
             sortedByDistance.takeLast(10).map { it.first.rawText }).distinct()
        } else {
            listOf(nodeA.label, nodeB.label)
        }

        val lineage = mutableListOf<String>()
        var curr: GraphNode? = parent
        while (curr != null) {
            lineage.add(0, curr.label)
            curr = curr.parents.firstOrNull()
        }

        val prompt = TaxoPrompts.clusterLabeling(
            querySamples = representativeSamples,
            parentLabel = parent.label,
            siblingLabels = parent.children.filter { it != nodeA && it != nodeB }.map { it.label },
            branchHistory = lineage
        )

        val jsonResponse = llmClient.generateClusterLabel(prompt)
        val newLabel = extractLabelFromJson(jsonResponse) ?: "${nodeA.label} & ${nodeB.label}"

        log.info("Merged '${nodeA.label}' + '${nodeB.label}' -> '$newLabel'")

        val mergedNode = GraphNode(label = newLabel, depth = parent.depth + 1)
        mergedNode.queries.addAll(combinedQueries)

        val allChildren = (nodeA.children + nodeB.children)
            .filter { it.id != nodeA.id && it.id != nodeB.id }
            .toSet()

        for (child in allChildren) {
            child.parents.remove(nodeA)
            child.parents.remove(nodeB)
            child.parents.add(mergedNode)
            mergedNode.children.add(child)
        }

        val rawParents = (nodeA.parents + nodeB.parents + setOf(parent))
            .filter { it.id != nodeA.id && it.id != nodeB.id }
            .toSet()

        val optimizedParents = rawParents.filter { p1 ->
            !rawParents.any { p2 -> p1.id != p2.id && isDescendant(p1, p2) }
        }

        for (p in rawParents) {
            p.children.remove(nodeA)
            p.children.remove(nodeB)
        }

        for (p in optimizedParents) {
            p.children.add(mergedNode)
            mergedNode.parents.add(p)
        }

        nodeA.parents.clear()
        nodeA.children.clear()
        nodeA.queries.clear()
        nodeB.parents.clear()
        nodeB.children.clear()
        nodeB.queries.clear()
    }

    private suspend fun evaluateCrossLinks(root: GraphNode) = coroutineScope {
        val allNodes = getAllNodes(root).filter { it.depth > 0 }

        for (node in allNodes) {
            val potentialParents = allNodes.filter { potentialParent ->
                node != potentialParent &&
                        !node.parents.contains(potentialParent) &&
                        !isDescendant(node, potentialParent) &&
                        !isDescendant(potentialParent, node)
            }

            val crossLinks = potentialParents.chunked(50).map { chunk ->
                async(Dispatchers.Default) {
                    chunk.mapNotNull { potentialParent ->
                        val nodeGmm = node.distribution ?: return@mapNotNull null
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
                    "Cross-linking '${node.label}' to additional parent '${potentialParent.label}' (Entailment Score: ${"%.4f".format(score)})"
                )
                node.parents.add(potentialParent)
                potentialParent.children.add(node)

                // Clean up redundant shortcuts created by cross-linking
                val redundantParents = node.parents.filter { p ->
                    p.id != potentialParent.id && isDescendant(p, potentialParent)
                }

                for (rp in redundantParents) {
                    log.info("Removing redundant transitive parent '${rp.label}' from '${node.label}' after cross-linking.")
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
                log.info("Transitive reduction: Severing redundant shortcut '${rp.label}' -> '${node.label}'")
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
            log.info("Collapsing redundant unary chain: '${passthrough.label}' -> '${grandchild.label}'")
            
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

    private fun extractLabelFromJson(json: String): String? {
        val regex = """"label"\s*:\s*"([^"]+)"""".toRegex()
        return regex.find(json)?.groups?.get(1)?.value
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
