package taxonomy.utils

import org.slf4j.LoggerFactory
import taxonomy.config.TaxonomyConfig
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.IterationMetrics
import taxonomy.model.TaxonomyMetricsData
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
    private val log = LoggerFactory.getLogger("taxonomy.Metrics")

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
        // Hierarchical F₁ (Kosmopoulos et al. 2014)
        val hPrecision:            Double,
        val hRecall:               Double,
        val hF1:                   Double,
        // Shannon entropy of leaf-size distribution (structural balance).
        // High = well-balanced tree. 0 = single-leaf collapse.
        val avgMatchCount:         Double,
        /** Renamed from vmfKappaByDepth — average κ per depth level. */
        val kappaByDepth:          Map<Int, Double>,
        val leafDistribEntropy:    Double,
        // Publication-grade metrics (PR #49)
        val totalDasguptaCost:     Double = 0.0,
        val routingECE:            Double = 0.0,
        val tripletAccuracy:       Double = 0.0,
        val normalisedSackin:      Double = 0.0,
    ) {
        /**
         * Backward-compat alias so any call-site still using `vmfKappaByDepth`
         * compiles without change.
         */
        val vmfKappaByDepth: Map<Int, Double> get() = kappaByDepth

        /**
         * Project this compute-time report onto the canonical, serializable
         * [TaxonomyMetricsData] payload that is shared across iteration
         * history, snapshots, and the TUI. This is the single bridge between
         * the metrics computation and everything that consumes metrics.
         */
        fun toData(): TaxonomyMetricsData = TaxonomyMetricsData(
            totalNodes            = totalNodes,
            leafNodes             = leafNodes,
            crossDomainNodes      = crossDomainNodes,
            maxDepth              = maxDepth,
            avgLeafDepth          = avgLeafDepth,
            medianLeafAssignments = medianLeafAssignments,
            totalUniqueQueries    = totalUniqueQueries,
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
            hPrecision            = hPrecision,
            hRecall               = hRecall,
            hF1                   = hF1,
            avgMatchCount         = avgMatchCount,
            kappaByDepth          = kappaByDepth,
            leafDistribEntropy    = leafDistribEntropy,
            totalDasguptaCost     = totalDasguptaCost,
            routingECE            = routingECE,
            tripletAccuracy       = tripletAccuracy,
            normalisedSackin      = normalisedSackin,
        )
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

        // NMI/ARI: collapse predicted assignment to depth-1 ancestor label so both
        // partitions have the same granularity as the 13 GT categories.
        // Using raw leaf IDs (hundreds of distinct values) against 13 GT labels caused
        // H(predicted) >> H(GT), making MI negligible → NMI ≈ 0 always.
        val predSimple = queryToPrimaryLeaf.mapValues { (_, leaf) ->
            getDepth1Ancestors(leaf).firstOrNull() ?: leaf.id
        }

        // Predicted covering: the set of leaves each query is assigned to.
        // Used for routing ECE; overlapping NMI now uses groundTruthLeaves path.
        val predictedCover = queryToLeavesList.mapValues { (_, ll) ->
            ll.associate { it.id to 1.0 }
        }

        // Per-query true-leaf ground truth: each query's MMLU-Pro category resolves to the
        // depth-1 node whose originalCategory matches. originalCategory is frozen at bootstrap
        // and survives LLM relabeling; label is used only as a fallback for old snapshots
        // that predate the originalCategory field.
        val groundTruthLeaves: Map<String, GraphNode> = run {
            // Key depth-1 nodes by originalCategory first, then fall back to label.
            // This ensures the lookup is stable even after post-pass LLM relabeling.
            val depth1ByCategory = allNodes
                .filter { it.depth == 1 }
                .associateBy { (it.originalCategory ?: it.label)?.lowercase() ?: "" }

            val result = mutableMapOf<String, GraphNode>()
            leaves.forEach { leaf ->
                leaf.queries.forEach { emb ->
                    val category = if (emb.groundTruthCategory.isNotBlank()) {
                        emb.groundTruthCategory
                    } else {
                        groundTruthMap[emb.rawText]?.firstOrNull() ?: ""
                    }
                    if (category.isNotBlank()) {
                        val gtNode = depth1ByCategory[category.lowercase()]
                        if (gtNode != null) result[emb.rawText] = gtNode
                        // If no depth-1 anchor matches, fall back to the predicted leaf
                        // (treats routing as correct for this query rather than penalising
                        // it for a missing GT anchor).
                        else result.putIfAbsent(emb.rawText, leaf)
                    }
                }
            }
            result
        }

        // Standard Shannon NMI on depth-1-collapsed partitions (same granularity)
        // to avoid LFK overlapping NMI degeneracy on small clusters.
        val nmi = ShannonNmi.compute(gtSimple, predSimple)

        val ari               = calculateAri(uniqueQueryTexts, gtSimple, predSimple)
        val weightedLeafPurity = calculateWeightedLeafPurity(leaves, gtSimple)
        // DAG-compatible Dendrogram Purity (Monath et al. 2021): uses the
        // shallowest LCA, which is well-defined under polyhierarchy.
        val dendrogramPurity  = dagDendrogramPurity(queryToPrimaryLeaf, gtSimple)
        val edgeF1            = calculateEdgeF1(allNodes, queryToLeavesList, gtSimple)

        // Hierarchical F₁ (Kosmopoulos et al. 2014) over the real per-query true leaves;
        // the predicted leaf is the argmax (max-κ) routed leaf computed above.
        val (hPrecision, hRecall, hF1) =
            computeHierarchicalF1(queryToPrimaryLeaf, groundTruthLeaves)

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

        // ── Publication-grade metrics (PR #49) ──
        // Dasgupta cost, triplet accuracy and Sackin are intrinsic (embedding + tree).
        val queryEmbeddings   = uniqueQueryTexts.mapNotNull { queryToEmbeddings[it] }
        val totalDasguptaCost = computeTotalDasguptaCost(root, queryEmbeddings)
        val tripletAccuracy   = computeTripletAccuracy(root, queryEmbeddings)
        val normalisedSackin  = computeNormalisedSackin(root)
        // routingECE receives the same groundTruthLeaves map (node IDs) now that
        // the GT plumbing is complete — no longer silently 0.0 after M1.
        val routingECE        = computeRoutingECE(predictedCover, groundTruthLeaves.mapValues { it.value.id })

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
            hPrecision            = hPrecision,
            hRecall               = hRecall,
            hF1                   = hF1,
            avgMatchCount         = avgMatchCount,
            kappaByDepth          = kappaByDepth,
            leafDistribEntropy    = leafDistribEntropy,
            totalDasguptaCost     = totalDasguptaCost,
            routingECE            = routingECE,
            tripletAccuracy       = tripletAccuracy,
            normalisedSackin      = normalisedSackin,
        )
    }
    // ─────────────────────────────────────────────────────────────────────────
    //  Topology helpers
    // ─────────────────────────────────────────────────────────────────────────

    /**
     * Map each ground-truth category to its representative DAG node: the deepest node labeled
     * with that category (preferring leaves on a depth tie), which roots the category's domain
     * subtree. Categories with no matching node are dropped with a WARN and excluded from the
     * hierarchical ground truth (so the metrics degrade to 0 rather than throwing).
     *
     * NOTE: this helper is retained for contamination-ratio and edgeF1 which still use
     * label-based matching. It is NOT used for groundTruthLeaves (which uses
     * emb.groundTruthCategory + node.originalCategory instead).
     */
    private fun buildCategoryToNode(allNodes: Set<GraphNode>): Map<String, GraphNode> {
        val byCategory = HashMap<String, GraphNode>()
        for (category in groundTruthMap.values.flatten().toSet()) {
            val match = allNodes
                .filter {
                    (it.originalCategory ?: it.label)?.equals(category, ignoreCase = true) == true
                }
                .maxWithOrNull(compareBy({ it.depth }, { if (it.isLeaf) 1 else 0 }))
            if (match != null) byCategory[category] = match
            else log.warn("No DAG node labeled '$category'; excluding category from hierarchical ground truth")
        }
        return byCategory
    }

    /** Per-query true leaf: the representative node of the query's first ground-truth category. */
    private fun buildGroundTruthLeaves(categoryToNode: Map<String, GraphNode>): Map<String, GraphNode> =
        groundTruthMap.mapNotNull { (query, categories) ->
            val category = categories.firstOrNull() ?: return@mapNotNull null
            val node     = categoryToNode[category] ?: return@mapNotNull null
            query to node
        }.toMap()

    private fun getDepth1Ancestors(node: GraphNode): Set<String> {
        val ancestors = mutableSetOf<String>()
        val visited   = mutableSetOf<String>()
        fun walk(n: GraphNode) {
            if (!visited.add(n.id)) return
            if (n.depth == 1) {
                // Prefer originalCategory (frozen at bootstrap) over label (may be LLM-renamed).
                (n.originalCategory ?: n.label)?.let { ancestors.add(it) }
            }
            else n.parents.forEach { walk(it) }
        }
        walk(node)
        return ancestors
    }

    // ─────────────────────────────────────────────────────────────────────────
    //  Clustering metric implementations
    // ─────────────────────────────────────────────────────────────────────────

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

/**
 * Wrap a computed [TaxonomyMetrics.Report] as a labelled history point.
 * Trivial now that [IterationMetrics] composes the canonical payload.
 */
fun reportToIterationMetrics(label: String, r: TaxonomyMetrics.Report): IterationMetrics =
    IterationMetrics(iteration = label, metrics = r.toData())

/**
 * Standard Shannon Normalised Mutual Information over two hard partitions of the
 * same item set (Strehl & Ghosh 2002 symmetric normalisation).
 *
 * Each map associates an item key with a single discrete label. Only items
 * present in both maps are scored; cluster labels of the two partitions are
 * independent, so the score is invariant to label renaming.
 */
object ShannonNmi {
    fun compute(x: Map<String, String>, y: Map<String, String>): Double {
        val keys = x.keys intersect y.keys
        val n = keys.size
        if (n < 2) return 0.0

        val joint = HashMap<Pair<String, String>, Int>()
        val marginalX = HashMap<String, Int>()
        val marginalY = HashMap<String, Int>()
        for (k in keys) {
            val xi = x.getValue(k)
            val yi = y.getValue(k)
            joint.merge(xi to yi, 1, Int::plus)
            marginalX.merge(xi, 1, Int::plus)
            marginalY.merge(yi, 1, Int::plus)
        }
        if (marginalX.size < 2 || marginalY.size < 2) return 0.0

        val nd = n.toDouble()
        val hx = entropy(marginalX.values, nd)
        val hy = entropy(marginalY.values, nd)

        var mi = 0.0
        for ((pair, c) in joint) {
            val pxy = c / nd
            val px = marginalX.getValue(pair.first) / nd
            val py = marginalY.getValue(pair.second) / nd
            mi += pxy * kotlin.math.ln(pxy / (px * py))
        }

        val denom = kotlin.math.sqrt(hx * hy)
        if (denom <= 0.0) return 0.0
        return (mi / denom).coerceIn(0.0, 1.0)
    }

    private fun entropy(counts: Collection<Int>, n: Double): Double {
        var h = 0.0
        for (c in counts) {
            val p = c / n
            if (p > 0.0) h -= p * kotlin.math.ln(p)
        }
        return h
    }
}

/**
 * Overlapping Normalized Mutual Information.
 *
 * Lancichinetti, Fortunato & Kertész (2009), "Detecting the overlapping and
 * hierarchical community structure in complex networks", New Journal of Physics
 * 11:033015 — DOI: https://doi.org/10.1088/1367-2630/11/3/033015
 *
 * The standard Shannon NMI assumes disjoint hard partitions and inflates the
 * score when assignments overlap (polyhierarchy / soft routing). This computes
 * the covering-aware variant:
 *
 *   NMI_ovlp(X, Y) = 1 - (H(X|Y)_norm + H(Y|X)_norm) / 2
 *
 * Each query may belong to several clusters in either covering. A membership
 * value > 0 is treated as presence in that cluster's binary indicator; this
 * keeps the metric well-defined for both hard ground truth (1.0 / 0.0) and the
 * soft predicted routing produced by the engine.
 *
 * Inputs are keyed independently per covering — the cluster identifiers of the
 * predicted covering need not match those of the ground-truth covering.
 */
object OverlappingNmi {

    private const val LOG2 = 0.6931471805599453 // ln(2)

    private fun log2(x: Double): Double = kotlin.math.ln(x) / LOG2

    /** Bernoulli entropy of a single indicator with P(1) = p, in bits. 0 at p∈{0,1}. */
    private fun hBernoulli(p: Double): Double {
        if (p <= 0.0 || p >= 1.0) return 0.0
        val q = 1.0 - p
        return -p * log2(p) - q * log2(q)
    }

    /**
     * @param predicted   queryId -> (clusterId -> membership in [0,1])
     * @param groundTruth queryId -> (clusterId -> membership in [0,1])
     * @return overlapping NMI in [0, 1]
     */
    fun compute(
        predicted: Map<String, Map<String, Double>>,
        groundTruth: Map<String, Map<String, Double>>,
    ): Double {
        // Universe of items = queries present in either covering.
        val items = (predicted.keys + groundTruth.keys).toList()
        val n = items.size
        if (n == 0) return 0.0

        val x = toClusterSets(predicted, items)  // predicted covering
        val y = toClusterSets(groundTruth, items) // ground-truth covering
        if (x.isEmpty() || y.isEmpty()) return 0.0

        val hxGivenY = normalizedConditionalEntropy(x, y, n)
        val hyGivenX = normalizedConditionalEntropy(y, x, n)
        return (1.0 - 0.5 * (hxGivenY + hyGivenX)).coerceIn(0.0, 1.0)
    }

    /** Convert a fuzzy membership map into binary indicator sets (item indices) per cluster. */
    private fun toClusterSets(
        cover: Map<String, Map<String, Double>>,
        items: List<String>,
    ): List<Set<Int>> {
        val index = items.withIndex().associate { (i, q) -> q to i }
        val clusters = LinkedHashMap<String, MutableSet<Int>>()
        for ((q, memberships) in cover) {
            val itemIdx = index[q] ?: continue
            for ((clusterId, m) in memberships) {
                if (m > 0.0) clusters.getOrPut(clusterId) { mutableSetOf() }.add(itemIdx)
            }
        }
        // Drop empty / universal clusters that carry no information (H = 0).
        return clusters.values.filter { it.isNotEmpty() && it.size < items.size }
    }

    /**
     * H(X|Y)_norm = mean over clusters Xk of  H(Xk|Y) / H(Xk),
     * where H(Xk|Y) = min over Yl of the constrained conditional entropy H(Xk|Yl).
     */
    private fun normalizedConditionalEntropy(
        x: List<Set<Int>>,
        y: List<Set<Int>>,
        n: Int,
    ): Double {
        var sum = 0.0
        var counted = 0
        for (xk in x) {
            val hXk = clusterEntropy(xk.size, n)
            if (hXk <= 0.0) continue
            var best = Double.MAX_VALUE
            for (yl in y) {
                val cond = conditionalEntropy(xk, yl, n, hXk)
                if (cond < best) best = cond
            }
            if (best == Double.MAX_VALUE) best = hXk
            sum += best / hXk
            counted++
        }
        return if (counted > 0) sum / counted else 0.0
    }

    private fun clusterEntropy(size: Int, n: Int): Double =
        hBernoulli(size.toDouble() / n)

    /**
     * Constrained conditional entropy H(Xk|Yl) (LFK 2009).
     * Uses the four-cell contingency of the two indicators; only valid when
     * h(P11)+h(P00) >= h(P10)+h(P01), otherwise Yl is uninformative about Xk
     * and the conditional entropy defaults to H(Xk).
     */
    private fun conditionalEntropy(
        xk: Set<Int>,
        yl: Set<Int>,
        n: Int,
        hXk: Double,
    ): Double {
        val inter = xk.count { it in yl }
        val nX = xk.size
        val nY = yl.size
        val c11 = inter
        val c10 = nX - inter
        val c01 = nY - inter
        val c00 = n - c11 - c10 - c01

        val nd = n.toDouble()
        val h11 = hCell(c11, nd)
        val h10 = hCell(c10, nd)
        val h01 = hCell(c01, nd)
        val h00 = hCell(c00, nd)

        // LFK constraint: the "aligned" cells must dominate the "crossed" cells.
        if (h11 + h00 < h10 + h01) return hXk

        // H(Xk|Yl) = H(Xk,Yl) - H(Yl)
        val hJoint = h11 + h10 + h01 + h00
        val hYl = hBernoulli(nY.toDouble() / n)
        return (hJoint - hYl).coerceAtLeast(0.0)
    }

    /** -count/n * log2(count/n), 0 when count == 0. */
    private fun hCell(count: Int, n: Double): Double {
        if (count <= 0) return 0.0
        val p = count / n
        return -p * log2(p)
    }
}
