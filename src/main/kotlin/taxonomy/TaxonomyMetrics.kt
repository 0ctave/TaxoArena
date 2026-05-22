package org.eclipse.lmos.arc.app.taxonomy

import org.slf4j.LoggerFactory
import taxonomy.StatisticsUtils

/**
 * Utility class to calculate and display structural and statistical metrics for the Taxonomy DAG.
 */
class TaxonomyMetrics(private val root: GraphNode) {
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
        val totalLogVolume: Double
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
            totalLogVolume = totalVol
        )
    }

    fun printReport() {
        val r = generateReport()
        val separator = "=".repeat(50)
        
        log.info(separator)
        log.info("      TAXONOMY ARCHITECTURAL METRICS")
        log.info(separator)
        log.info("Topology Stats:")
        log.info("  - Total Nodes:          ${r.totalNodes}")
        log.info("  - Leaf Nodes:           ${r.leafNodes}")
        log.info("  - Cross-Domain Nodes:   ${r.crossDomainNodes} (Nodes with multiple parents)")
        log.info("  - Path Redundancy:      ${"%.2f".format(r.totalPathRedundancy)} (Avg parents per node)")
        log.info("  - Max Depth:            ${r.maxDepth}")
        log.info("  - Avg Leaf Depth:       ${"%.2f".format(r.avgLeafDepth)}")
        
        log.info("Assignment Stats:")
        log.info("  - Unique Queries:       ${r.totalUniqueQueries}")
        log.info("  - Median Nodes/Query:    ${r.medianLeafAssignments}")
        log.info("  - Residual Queries:     ${r.residualQueries} (Stuck in internal nodes)")
        
        log.info("Statistical Stats:")
        log.info("  - Total Log Volume:     ${"%.2f".format(r.totalLogVolume)} (Minimization indicates zoom)")
        log.info(separator)
    }
}
