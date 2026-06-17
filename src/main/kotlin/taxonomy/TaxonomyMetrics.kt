package org.eclipse.lmos.arc.app.taxonomy

import org.slf4j.LoggerFactory
import taxonomy.StatisticsUtils

/**
 * Utility class to calculate and display structural and statistical metrics for the Taxonomy DAG.
 */
class TaxonomyMetrics(
    private val root: GraphNode,
    private val groundTruthMap: Map<String, Set<String>> = emptyMap()
) {
    private val log = LoggerFactory.getLogger(TaxonomyMetrics::class.java)

    data class Report(
        val totalNodes: Int,
        val leafNodes: Int,
        val crossDomainNodes: Int,
        val maxDepth: Int,
        val avgLeafDepth: Double,
        val medianLeafAssignments: Double,
        val totalUniqueQueries: Int,
        val residualQueries: Int,
        val totalPathRedundancy: Double,
        val totalLogVolume: Double,
        val residualRatio: Double,
        val maxLeafConcentration: Double,
        val contaminationRatio: Double,
        val equilibriumIndex: Double,
        val relevanceComplianceRatio: Double
    )

    fun generateReport(): Report {
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (allNodes.add(n)) n.children.forEach { walk(it) }
        }
        walk(root)

        val leaves = allNodes.filter { it.isLeaf }
        val crossDomain = allNodes.count { it.parents.size > 1 }
        
        // Median Assignments per Query (ALL NODES)
        val queryToNodes = mutableMapOf<String, MutableSet<String>>()
        allNodes.forEach { node ->
            node.queries.forEach { emb ->
                queryToNodes.getOrPut(emb.rawText) { mutableSetOf() }.add(node.id)
            }
        }
        
        val assignmentCounts = queryToNodes.values.map { it.size }.sorted()
        val medianAssignments = if (assignmentCounts.isEmpty()) 0.0 
            else if (assignmentCounts.size % 2 == 0) 
                (assignmentCounts[assignmentCounts.size / 2].toDouble() + assignmentCounts[assignmentCounts.size / 2 - 1].toDouble()) / 2.0
            else assignmentCounts[assignmentCounts.size / 2].toDouble()

        // Depth Stats
        val leafDepths = leaves.map { it.depth }
        val maxDepth = leafDepths.maxOrNull() ?: 0
        val avgDepth = if (leafDepths.isNotEmpty()) leafDepths.average() else 0.0

        // Path Redundancy (Avg parents per node for nodes with parents)
        val nonRootNodes = allNodes.filter { it.depth > 0 }
        val avgParents = if (nonRootNodes.isNotEmpty()) nonRootNodes.map { it.parents.size }.average() else 0.0

        // Residuals
        val residualQueries = allNodes.filter { !it.isLeaf }.sumOf { it.queries.size }

        // Semantic Volume (Log-Determinant sum)
        val totalVol = leaves.mapNotNull { it.distribution }.sumOf { StatisticsUtils.calculateLogSemanticVolume(it) }

        // 1. Residual Ratio
        val totalUnique = maxOf(1, queryToNodes.size)
        val residualRatio = residualQueries.toDouble() / totalUnique.toDouble()

        // 2. Max Leaf Concentration
        val maxLeafSize = if (leaves.isNotEmpty()) leaves.maxOf { it.queries.size } else 0
        val maxLeafConcentration = maxLeafSize.toDouble() / totalUnique.toDouble()

        // 3. High-Level Domain Contamination
        var contaminatedCount = 0
        var totalMappedQueries = 0
        allNodes.filter { it.depth > 0 }.forEach { node ->
            val categoryRoots = mutableSetOf<String>()
            val visitedNodes = mutableSetOf<String>()
            fun collectAncestorsAtDepth1(n: GraphNode) {
                if (!visitedNodes.add(n.id)) return
                if (n.depth == 1) {
                    categoryRoots.add(n.label.lowercase())
                } else {
                    n.parents.forEach { collectAncestorsAtDepth1(it) }
                }
            }
            collectAncestorsAtDepth1(node)

            node.queries.forEach { emb ->
                totalMappedQueries++
                val groundTruth = groundTruthMap[emb.rawText]
                if (groundTruth != null && categoryRoots.isNotEmpty()) {
                    val matches = groundTruth.any { gt -> categoryRoots.any { cr -> cr.contains(gt.lowercase()) || gt.lowercase().contains(cr) } }
                    if (!matches) contaminatedCount++
                }
            }
        }
        val contaminationRatio = if (totalMappedQueries > 0) contaminatedCount.toDouble() / totalMappedQueries.toDouble() else 0.0

        // 4. Gini-based Tree Equilibrium
        val leafSizes = leaves.map { it.queries.size.toDouble() }.sorted()
        val totalLeafQueries = leafSizes.sum()
        val gini = if (totalLeafQueries == 0.0 || leafSizes.size < 2) 0.0 else {
            var sumDiff = 0.0
            val n = leafSizes.size
            for (i in 0 until n) {
                for (j in 0 until n) {
                    sumDiff += Math.abs(leafSizes[i] - leafSizes[j])
                }
            }
            sumDiff / (2.0 * n * totalLeafQueries)
        }
        val equilibriumIndex = 1.0 - gini

        // 5. 5% Relevance Compliance (Node-wise Paper Relevance)
        val fivePercentThreshold = totalUnique.toDouble() * 0.05
        val nonRootCount = allNodes.count { it.depth > 0 }
        val relevanceCompliantCount = allNodes.count { it.depth > 0 && it.queries.size >= fivePercentThreshold }
        val relevanceComplianceRatio = if (nonRootCount > 0) relevanceCompliantCount.toDouble() / nonRootCount.toDouble() else 1.0

        return Report(
            totalNodes = allNodes.size,
            leafNodes = leaves.size,
            crossDomainNodes = crossDomain,
            maxDepth = maxDepth,
            avgLeafDepth = avgDepth,
            medianLeafAssignments = medianAssignments,
            totalUniqueQueries = queryToNodes.size,
            residualQueries = residualQueries,
            totalPathRedundancy = avgParents,
            totalLogVolume = totalVol,
            residualRatio = residualRatio,
            maxLeafConcentration = maxLeafConcentration,
            contaminationRatio = contaminationRatio,
            equilibriumIndex = equilibriumIndex,
            relevanceComplianceRatio = relevanceComplianceRatio
        )
    }

    fun printReport() {
        val r = generateReport()
        val sb = java.lang.StringBuilder()
        sb.append("\n+----------------------------------------------------------\n")
        sb.append("|              TAXONOMY ARCHITECTURAL METRICS\n")
        sb.append("+----------------------------------------------------------\n")
        sb.append("| Topology Stats:\n")
        sb.append("|   - Total Nodes:          ${r.totalNodes}\n")
        sb.append("|   - Leaf Nodes:           ${r.leafNodes}\n")
        sb.append("|   - Cross-Domain Nodes:   ${r.crossDomainNodes} (Nodes with multiple parents)\n")
        sb.append("|   - Path Redundancy:      ${"%.2f".format(java.util.Locale.US, r.totalPathRedundancy)} (Avg parents per node)\n")
        sb.append("|   - Max Depth:            ${r.maxDepth}\n")
        sb.append("|   - Avg Leaf Depth:       ${"%.2f".format(java.util.Locale.US, r.avgLeafDepth)}\n")
        sb.append("+----------------------------------------------------------\n")
        sb.append("| Assignment Stats:\n")
        sb.append("|   - Unique Queries:       ${r.totalUniqueQueries}\n")
        sb.append("|   - Median Nodes/Query:   ${"%.2f".format(java.util.Locale.US, r.medianLeafAssignments)}\n")
        sb.append("|   - Residual Queries:     ${r.residualQueries} (Stuck in internal nodes)\n")
        sb.append("+----------------------------------------------------------\n")
        sb.append("| Structural & Semantic Diagnostics:\n")
        sb.append("|   - Residual Query Ratio: ${"%.2f%%".format(java.util.Locale.US, r.residualRatio * 100.0)}\n")
        sb.append("|   - Max Leaf Concentration: ${"%.2f%%".format(java.util.Locale.US, r.maxLeafConcentration * 100.0)}\n")
        sb.append("|   - Tree Equilibrium (1-Gini): ${"%.2f%%".format(java.util.Locale.US, r.equilibriumIndex * 100.0)}\n")
        sb.append("|   - Domain Contamination: ${"%.2f%%".format(java.util.Locale.US, r.contaminationRatio * 100.0)}\n")
        sb.append("|   - 5%% Relevance Compliance: ${"%.2f%%".format(java.util.Locale.US, r.relevanceComplianceRatio * 100.0)}\n")
        sb.append("+----------------------------------------------------------\n")
        sb.append("| Statistical Stats:\n")
        sb.append("|   - Total Log Volume:     ${"%.2f".format(java.util.Locale.US, r.totalLogVolume)} (Minimization indicates zoom)\n")
        sb.append("+----------------------------------------------------------")
        log.info(sb.toString())
    }
}
