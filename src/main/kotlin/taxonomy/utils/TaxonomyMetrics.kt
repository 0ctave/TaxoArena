package taxonomy.utils

import org.slf4j.LoggerFactory
import taxonomy.config.TaxonomyConfig
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.IterationMetrics
import taxonomy.model.projectTo

/**
 * Computes structural, geometric, and clustering metrics for the Taxonomy DAG.
 *
 * Naming change: the report field was `vmfKappaByDepth` — renamed to
 * `kappaByDepth` to match the public API declared in the framework reference
 * (`Report.kappaByDepth: Map<Int, Double>`).
 */
class TaxonomyMetrics(
    private val root:           GraphNode,
    private val groundTruthMap: Map<String, List<String>> = emptyMap()
) {
    private val log = LoggerFactory.getLogger("Metrics")

    // ─────────────────────────────────────────────────────────────────────────
    //  Report data class  (matches the canonical definition in framework ref)
    // ─────────────────────────────────────────────────────────────────────────
    data class Report(
        val totalNodes:            Int,
        val leafNodes:             Int,
        val crossDomainNodes:      Int,
        val maxDepth:              Int,
        val avgLeafDepth:          Double,
        val medianLeafAssignments: Double,
        val totalUniqueQueries:    Int,
        val residualQueries:       Int,
        val residualRatio:         Double,
        val maxLeafConcentration:  Double,
        val contaminationRatio:    Double,
        val equilibriumIndex:      Double,
        // vMF / NiW metrics
        val nmi:                   Double,
        val ari:                   Double,
        val dendrogramPurity:      Double,
        val weightedLeafPurity:    Double,
        val edgeF1:                Double,
        val sphericalSilhouette:   Double,
        val ancestorCorrectRate:   Double,
        // Shannon entropy of leaf-size distribution (structural balance).
        // High = well-balanced tree. 0 = single-leaf collapse.
        val avgMatchCount:         Double,
        /** Renamed from vmfKappaByDepth — average κ per depth level. */
        val kappaByDepth:          Map<Int, Double>,
        val leafDistribEntropy:    Double,
    ) {
        /**
         * Backward-compat alias so any call-site still using `vmfKappaByDepth`
         * compiles without change.
         */
        val vmfKappaByDepth: Map<Int, Double> get() = kappaByDepth
    }

    // ─────────────────────────────────────────────────────────────────────────
    //  generateReport
    // ─────────────────────────────────────────────────────────────────────────
    fun generateReport(): Report {
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) { if (allNodes.add(n)) n.children.forEach { walk(it) } }
        walk(root)

        val leaves      = allNodes.filter { it.isLeaf }
        val crossDomain = allNodes.count { it.parents.size > 1 }

        // ── Leaf assignment counts ──
        val queryToLeafNodes   = mutableMapOf<String, MutableSet<String>>()
        val queryToEmbeddings  = mutableMapOf<String, Embedding>()
        leaves.forEach { leaf ->
            leaf.queries.forEach { emb ->
                queryToLeafNodes.getOrPut(emb.rawText) { mutableSetOf() }.add(leaf.id)
                queryToEmbeddings[emb.rawText] = emb
            }
        }

        val allQueryTexts = mutableSetOf<String>()
        allNodes.forEach { node -> node.queries.forEach { allQueryTexts.add(it.rawText) } }

        val assignmentCounts   = queryToLeafNodes.values.map { it.size }.sorted()
        val medianAssignments  = when {
            assignmentCounts.isEmpty()            -> 0.0
            assignmentCounts.size % 2 == 0        ->
                (assignmentCounts[assignmentCounts.size / 2].toDouble() +
                 assignmentCounts[assignmentCounts.size / 2 - 1].toDouble()) / 2.0
            else                                  -> assignmentCounts[assignmentCounts.size / 2].toDouble()
        }

        // ── Depth stats ──
        val leafDepths = leaves.map { it.depth }
        val maxDepth   = leafDepths.maxOrNull() ?: 0
        val avgDepth   = if (leafDepths.isNotEmpty()) leafDepths.average() else 0.0

        // ── Residuals: queries stuck in internal nodes, never reaching a leaf ──
        val leafQueryTexts     = queryToEmbeddings.keys
        val internalQueryTexts = mutableSetOf<String>()
        allNodes.filter { !it.isLeaf }.forEach { node ->
            node.queries.forEach { internalQueryTexts.add(it.rawText) }
        }
        val residualQueries    = (internalQueryTexts - leafQueryTexts).size

        val totalUnique        = maxOf(1, allQueryTexts.size)
        val residualRatio      = residualQueries.toDouble() / totalUnique.toDouble()

        val maxLeafSize        = leaves.maxOfOrNull { it.queries.size } ?: 0
        val maxLeafConcentration = maxLeafSize.toDouble() / totalUnique.toDouble()

        // ── Contamination (leaf-assigned queries only) ──
        var contaminatedCount      = 0
        var totalMappedLeafQueries = 0
        leaves.forEach { leaf ->
            val leafDomains = getDepth1Ancestors(leaf).map { it.lowercase() }.toSet()
            leaf.queries.forEach { emb ->
                val gt = groundTruthMap[emb.rawText]
                if (gt != null && leafDomains.isNotEmpty()) {
                    totalMappedLeafQueries++
                    if (!gt.any { g -> leafDomains.any { ld -> ld.equals(g, ignoreCase = true) } })
                        contaminatedCount++
                }
            }
        }
        val contaminationRatio = if (totalMappedLeafQueries > 0)
            contaminatedCount.toDouble() / totalMappedLeafQueries.toDouble() else 0.0

        // ── Gini-based tree equilibrium ──
        val leafSizes       = leaves.map { it.queries.size.toDouble() }.sorted()
        val totalLeafQ      = leafSizes.sum()
        val gini = if (totalLeafQ == 0.0 || leafSizes.size < 2) 0.0 else {
            var sumDiff = 0.0; val n = leafSizes.size
            for (i in 0 until n) for (j in 0 until n) sumDiff += Math.abs(leafSizes[i] - leafSizes[j])
            sumDiff / (2.0 * n * totalLeafQ)
        }
        val equilibriumIndex = 1.0 - gini

        // ── Clustering metrics ──
        val gtSimple          = groundTruthMap.mapValues { it.value.firstOrNull() ?: "Unknown" }
        val uniqueQueryTexts  = queryToEmbeddings.keys.toList()

        val queryToLeavesList = mutableMapOf<String, MutableList<GraphNode>>()
        leaves.forEach { leaf ->
            leaf.queries.forEach { emb ->
                queryToLeavesList.getOrPut(emb.rawText) { mutableListOf() }.add(leaf)
            }
        }

        val queryToPrimaryLeaf = queryToLeavesList.mapValues { (_, ll) ->
            ll.maxByOrNull { it.vmfKappa } ?: ll.first()
        }

        // NMI/ARI use flat leaf identity (correct for clustering papers)
        val predSimple = queryToPrimaryLeaf.mapValues { (_, leaf) -> leaf.id }

        val nmi               = calculateNmi(uniqueQueryTexts, gtSimple, predSimple)
        val ari               = calculateAri(uniqueQueryTexts, gtSimple, predSimple)
        val weightedLeafPurity = calculateWeightedLeafPurity(leaves, gtSimple)
        val dendrogramPurity  = calculateDendrogramPurity(queryToEmbeddings.values.toList(), gtSimple, queryToPrimaryLeaf)
        val edgeF1            = calculateEdgeF1(allNodes, queryToLeavesList, gtSimple)

        val sphericalSilhouette = run {
            val byDepth    = leaves.filter { it.vmfMu.isNotEmpty() }.groupBy { it.depth }
            var weightedSum = 0.0; var totalWeight = 0.0
            for ((_, depthLeaves) in byDepth) {
                if (depthLeaves.size < 2) continue
                val d           = depthLeaves.first().vmfMu.size
                val queries     = depthLeaves.flatMap { it.queries }.distinctBy { it.rawText }
                if (queries.isEmpty()) continue
                val projQ       = queries.map { it.projectTo(d) }
                val projC       = depthLeaves.map { StatisticsUtils.projectVector(it.vmfMu, d) }
                val s           = StatisticsUtils.calculateSphericalSilhouette(projQ, projC)
                val w           = queries.size.toDouble()
                weightedSum    += s * w; totalWeight += w
            }
            if (totalWeight > 0.0) weightedSum / totalWeight else 0.0
        }

        val avgMatchCount = if (queryToLeavesList.isNotEmpty())
            queryToLeavesList.values.map { it.size }.average() else 1.0

        // κ profile by depth (renamed field)
        val kappaByDepth = allNodes
            .filter { it.vmfKappa > 0.0 }
            .groupBy { it.depth }
            .mapValues { (_, nodes) -> nodes.map { it.vmfKappa }.average() }

        val ancestorCorrectRate = calculateAncestorCorrectRate(queryToLeavesList, gtSimple)
        val leafDistribEntropy  = calculateLeafDistributionEntropy(leaves)

        return Report(
            totalNodes            = allNodes.size,
            leafNodes             = leaves.size,
            crossDomainNodes      = crossDomain,
            maxDepth              = maxDepth,
            avgLeafDepth          = avgDepth,
            medianLeafAssignments = medianAssignments,
            totalUniqueQueries    = allQueryTexts.size,
            residualQueries       = residualQueries,
            residualRatio         = residualRatio,
            maxLeafConcentration  = maxLeafConcentration,
            contaminationRatio    = contaminationRatio,
            equilibriumIndex      = equilibriumIndex,
            nmi                   = nmi,
            ari                   = ari,
            dendrogramPurity      = dendrogramPurity,
            weightedLeafPurity    = weightedLeafPurity,
            edgeF1                = edgeF1,
            sphericalSilhouette   = sphericalSilhouette,
            ancestorCorrectRate   = ancestorCorrectRate,
            avgMatchCount         = avgMatchCount,
            kappaByDepth          = kappaByDepth,
            leafDistribEntropy    = leafDistribEntropy,
        )
    }

    // ─────────────────────────────────────────────────────────────────────────
    //  Topology helpers
    // ─────────────────────────────────────────────────────────────────────────

    private fun getDepth1Ancestors(node: GraphNode): Set<String> {
        val ancestors = mutableSetOf<String>()
        val visited   = mutableSetOf<String>()
        fun walk(n: GraphNode) {
            if (!visited.add(n.id)) return
            if (n.depth == 1) n.label?.let { ancestors.add(it) }
            else n.parents.forEach { walk(it) }
        }
        walk(node)
        return ancestors
    }

    private fun findLca(nodeA: GraphNode, nodeB: GraphNode): GraphNode {
        if (nodeA == nodeB) return nodeA
        val ancestorsA = mutableSetOf<GraphNode>()
        fun collectA(n: GraphNode) { if (ancestorsA.add(n)) n.parents.forEach { collectA(it) } }
        collectA(nodeA)
        val ancestorsB = mutableSetOf<GraphNode>()
        fun collectB(n: GraphNode) { if (ancestorsB.add(n)) n.parents.forEach { collectB(it) } }
        collectB(nodeB)
        val common = ancestorsA.intersect(ancestorsB)
        return if (common.isEmpty()) root else common.maxByOrNull { it.depth } ?: root
    }

    // ─────────────────────────────────────────────────────────────────────────
    //  Clustering metric implementations
    // ─────────────────────────────────────────────────────────────────────────

    private fun calculateNmi(
        queries: List<String>, gt: Map<String, String>, pred: Map<String, String>
    ): Double {
        val n = queries.size.toDouble(); if (n == 0.0) return 0.0
        val uC = mutableMapOf<String, Double>(); val vC = mutableMapOf<String, Double>()
        val uvC = mutableMapOf<Pair<String, String>, Double>()
        for (q in queries) {
            val u = gt[q] ?: "Unknown"; val v = pred[q] ?: "Unknown"
            uC[u] = (uC[u] ?: 0.0) + 1.0; vC[v] = (vC[v] ?: 0.0) + 1.0
            val pair = u to v; uvC[pair] = (uvC[pair] ?: 0.0) + 1.0
        }
        var hU = 0.0; for ((_, c) in uC) { val p = c / n; hU -= p * Math.log(p) }
        var hV = 0.0; for ((_, c) in vC) { val p = c / n; hV -= p * Math.log(p) }
        var iUV = 0.0
        for ((pair, c) in uvC) {
            val pUV = c / n; val pU = (uC[pair.first] ?: 0.0) / n; val pV = (vC[pair.second] ?: 0.0) / n
            if (pU > 0.0 && pV > 0.0) iUV += pUV * Math.log(pUV / (pU * pV))
        }
        val denom = hU + hV; return if (denom > 0.0) (2.0 * iUV) / denom else 0.0
    }

    private fun calculateAri(
        queries: List<String>, gt: Map<String, String>, pred: Map<String, String>
    ): Double {
        val n = queries.size.toDouble(); if (n < 2.0) return 0.0
        val uC = mutableMapOf<String, Int>(); val vC = mutableMapOf<String, Int>()
        val uvC = mutableMapOf<Pair<String, String>, Int>()
        for (q in queries) {
            val u = gt[q] ?: "Unknown"; val v = pred[q] ?: "Unknown"
            uC[u] = (uC[u] ?: 0) + 1; vC[v] = (vC[v] ?: 0) + 1
            val pair = u to v; uvC[pair] = (uvC[pair] ?: 0) + 1
        }
        fun comb2(x: Int): Double = x.toDouble() * (x - 1).toDouble() / 2.0
        val sumUV = uvC.values.sumOf { comb2(it) }
        val sumU  = uC.values.sumOf  { comb2(it) }
        val sumV  = vC.values.sumOf  { comb2(it) }
        val nC    = comb2(n.toInt())
        val exp   = (sumU * sumV) / nC
        val maxA  = 0.5 * (sumU + sumV)
        val denom = maxA - exp
        return if (denom > 0.0) (sumUV - exp) / denom else 0.0
    }

    private fun calculateWeightedLeafPurity(
        leaves: List<GraphNode>, gt: Map<String, String>
    ): Double {
        var totalIntersect = 0.0; var totalN = 0.0
        for (leaf in leaves) {
            if (leaf.queries.isEmpty()) continue
            val counts = mutableMapOf<String, Int>()
            for (q in leaf.queries) counts[gt[q.rawText] ?: "Unknown"] = (counts[gt[q.rawText] ?: "Unknown"] ?: 0) + 1
            totalIntersect += (counts.values.maxOrNull() ?: 0).toDouble()
            totalN         += leaf.queries.size.toDouble()
        }
        return if (totalN > 0.0) totalIntersect / totalN else 0.0
    }

    private fun calculateDendrogramPurity(
        queries:             List<Embedding>,
        gt:                  Map<String, String>,
        queryToPrimaryLeaf:  Map<String, GraphNode>,
        sampleSize:          Int = 1000
    ): Double {
        val classToQ = queries.groupBy { gt[it.rawText] ?: "Unknown" }
            .filter { it.key != "Unknown" && it.value.size >= 2 }
        if (classToQ.isEmpty()) return 0.0

        var totalPurity = 0.0; var count = 0
        val rng = java.util.Random(42); val classes = classToQ.keys.toList()
        repeat(sampleSize) {
            val cls  = classes[rng.nextInt(classes.size)]
            val list = classToQ[cls]!!
            val i    = rng.nextInt(list.size); var j = rng.nextInt(list.size)
            while (j == i) j = rng.nextInt(list.size)
            val leafA = queryToPrimaryLeaf[list[i].rawText]; val leafB = queryToPrimaryLeaf[list[j].rawText]
            if (leafA != null && leafB != null) {
                val lca          = findLca(leafA, leafB)
                val branchQ      = lca.getAllQueriesInBranch()
                if (branchQ.isNotEmpty()) {
                    val maxClassC = branchQ.map { gt[it.rawText] ?: "Unknown" }.groupBy { it }.values.maxOfOrNull { it.size } ?: 0
                    totalPurity += maxClassC.toDouble() / branchQ.size.toDouble()
                    count++
                }
            }
        }
        return if (count > 0) totalPurity / count else 0.0
    }

    private fun calculateEdgeF1(
        allNodes:          Set<GraphNode>,
        queryToLeavesList: Map<String, List<GraphNode>>,
        gt:                Map<String, String>
    ): Double {
        val nonRootNodes = allNodes.filter { it.depth > 0 }
        var totalEdges = 0; var correctEdges = 0
        for (node in nonRootNodes) for (p in node.parents) {
            totalEdges++
            if (p.depth == 0 || getDepth1Ancestors(p).intersect(getDepth1Ancestors(node)).isNotEmpty())
                correctEdges++
        }
        val precision = if (totalEdges > 0) correctEdges.toDouble() / totalEdges else 1.0

        var recovered = 0
        val leafQ = queryToLeavesList.keys
        for (text in leafQ) {
            val gtCat       = gt[text] ?: continue
            val primaryLeaf = queryToLeavesList[text]?.maxByOrNull { it.vmfKappa } ?: continue
            if (getDepth1Ancestors(primaryLeaf).any { it.equals(gtCat, ignoreCase = true) }) recovered++
        }
        val recall = if (leafQ.isNotEmpty()) recovered.toDouble() / leafQ.size else 1.0

        val denom = precision + recall
        return if (denom > 0.0) (2.0 * precision * recall) / denom else 0.0
    }

    fun calculateAncestorCorrectRate(
        queryToLeavesList: Map<String, List<GraphNode>>,
        gt:                Map<String, String>
    ): Double {
        if (gt.isEmpty()) return 0.0
        var correct = 0; var total = 0; var skipped = 0
        for ((text, domain) in gt) {
            val matchedLeaves = queryToLeavesList[text]
            if (matchedLeaves == null) { skipped++; continue }
            total++
            if (matchedLeaves.any { leaf ->
                    getDepth1Ancestors(leaf).any { it.equals(domain, ignoreCase = true) }
                }) correct++
        }
        if (skipped > 0) log.debug("ancestorCorrectRate: $skipped queries excluded (residuals)")
        return if (total > 0) correct.toDouble() / total else 0.0
    }

    /**
     * Shannon entropy of the leaf-size distribution.
     * High entropy = balanced tree.  Zero = fully collapsed (single leaf).
     */
    fun calculateLeafDistributionEntropy(leaves: List<GraphNode>): Double {
        if (leaves.isEmpty()) return 0.0
        val total = leaves.sumOf { it.queries.size }.toDouble()
        if (total == 0.0) return 0.0
        return -leaves.sumOf { leaf ->
            val p = leaf.queries.size.toDouble() / total
            if (p > 0.0) p * Math.log(p) else 0.0
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    //  Logging
    // ─────────────────────────────────────────────────────────────────────────

    fun printReport(config: TaxonomyConfig) {
        val r  = generateReport()
        val US = java.util.Locale.US
        val sb = StringBuilder()
        sb.append(config.formatConfigReport()).append("\n")
        sb.append("| TAXONOMY ARCHITECTURAL METRICS\n")
        sb.append("+----------------------------------------------------------\n")
        sb.append("| Topology Stats:\n")
        sb.append("|   Total Nodes:         ${r.totalNodes}\n")
        sb.append("|   Leaf Nodes:          ${r.leafNodes}\n")
        sb.append("|   Cross-Domain Nodes:  ${r.crossDomainNodes}\n")
        sb.append("|   Max Depth:           ${r.maxDepth}\n")
        sb.append("|   Avg Leaf Depth:      ${"%.2f".format(US, r.avgLeafDepth)}\n")
        sb.append("+----------------------------------------------------------\n")
        sb.append("| Assignment Stats:\n")
        sb.append("|   Unique Queries:      ${r.totalUniqueQueries}\n")
        sb.append("|   Median Nodes/Query:  ${"%.2f".format(US, r.medianLeafAssignments)}\n")
        sb.append("|   Residual Queries:    ${r.residualQueries}\n")
        sb.append("|   Avg Match Count:     ${"%.2f".format(US, r.avgMatchCount)} leaves/query\n")
        sb.append("+----------------------------------------------------------\n")
        sb.append("| Structural & Semantic Diagnostics:\n")
        sb.append("|   Residual Ratio:      ${"%.2f%%".format(US, r.residualRatio * 100.0)}\n")
        sb.append("|   Max Concentration:   ${"%.2f%%".format(US, r.maxLeafConcentration * 100.0)}\n")
        sb.append("|   Tree Equilibrium:    ${"%.2f%%".format(US, r.equilibriumIndex * 100.0)}\n")
        sb.append("|   Contamination:       ${"%.2f%%".format(US, r.contaminationRatio * 100.0)}\n")
        sb.append("|   vMF κ by depth:\n")
        r.kappaByDepth.entries.sortedBy { it.key }.forEach { (depth, kappa) ->
            sb.append("|     Depth $depth: ${"%.3f".format(US, kappa)}\n")
        }
        sb.append("+----------------------------------------------------------\n")
        sb.append("| External Validation & Geometric Metrics:\n")
        sb.append("|   NMI:                 ${"%.4f".format(US, r.nmi)}\n")
        sb.append("|   ARI:                 ${"%.4f".format(US, r.ari)}\n")
        sb.append("|   Dendrogram Purity:   ${"%.4f".format(US, r.dendrogramPurity)}\n")
        sb.append("|   Weighted Leaf Purity:${"%.4f".format(US, r.weightedLeafPurity)}\n")
        sb.append("|   Edge F1 vs Gold:     ${"%.4f".format(US, r.edgeF1)}\n")
        sb.append("|   Spherical Silhouette:${"%.4f".format(US, r.sphericalSilhouette)}\n")
        sb.append("|   Ancestor Correct:    ${"%.4f".format(US, r.ancestorCorrectRate)}\n")
        sb.append("|   Leaf Entropy:        ${"%.4f".format(US, r.leafDistribEntropy)} nats\n")
        sb.append("+----------------------------------------------------------\n")
        log.info(sb.toString())
    }
}

fun reportToIterationMetrics(label: String, r: TaxonomyMetrics.Report): IterationMetrics =
    IterationMetrics(
        iteration             = label,
        totalNodes            = r.totalNodes,
        leafNodes             = r.leafNodes,
        crossDomainNodes      = r.crossDomainNodes,
        maxDepth              = r.maxDepth,
        avgLeafDepth          = r.avgLeafDepth,
        totalUniqueQueries    = r.totalUniqueQueries,
        residualQueries       = r.residualQueries,
        residualRatio         = r.residualRatio,
        maxLeafConcentration  = r.maxLeafConcentration,
        contaminationRatio    = r.contaminationRatio,
        equilibriumIndex      = r.equilibriumIndex,
        nmi                   = r.nmi,
        ari                   = r.ari,
        dendrogramPurity      = r.dendrogramPurity,
        weightedLeafPurity    = r.weightedLeafPurity,
        edgeF1                = r.edgeF1,
        sphericalSilhouette   = r.sphericalSilhouette,
        ancestorCorrectRate   = r.ancestorCorrectRate,
        avgMatchCount         = r.avgMatchCount,
        leafDistribEntropy    = r.leafDistribEntropy
    )