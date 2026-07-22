package taxonomy.utils

import taxonomy.model.GraphNode
import taxonomy.model.Embedding
import taxonomy.model.TextNormalizer
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.operations.TaxonomyTrickler
import taxonomy.operations.RoutingResult
import taxonomy.operations.ResidualHit
import org.slf4j.LoggerFactory
import java.io.File
import java.util.Locale
import kotlin.math.*

class BridgeDiagnosticsExporter(
    private val config: TaxonomyConfig,
    private val datasetFetcher: MMLUDatasetFetcher,
    private val trickler: TaxonomyTrickler
) {
    private val log = LoggerFactory.getLogger(BridgeDiagnosticsExporter::class.java)

    fun exportDiagnostics(root: GraphNode, uniqueEmbs: List<Embedding>, outputDir: String) {
        log.info("Generating bridge and soft routing diagnostics...")
        File(outputDir).mkdirs()

        // Cache all categories to prevent millions of SQLite queries (performance fix)
        val queryCategories = uniqueEmbs.associate { it.rawText to (datasetFetcher.getDetailsForQuery(it.rawText)?.category ?: "Other") }

        // 1. Run trickle routing to gather fresh routing details for all queries
        val routingResults = uniqueEmbs.associateWith { emb ->
            trickler.routeQuery(emb, root, currentIteration = config.execution.numIterations)
        }

        // 2. Export secondary_membership_dump.csv (top 200 most ambiguous)
        exportSecondaryMembershipDump(routingResults, queryCategories, outputDir)

        // 3. Export residual_bridge_readiness.csv
        exportResidualBridgeReadiness(root, routingResults, queryCategories, outputDir)

        // 4. Export bridge_candidate_audit.csv and bridge_rejection_summary.csv
        exportBridgeCandidateAuditAndSummary(root, queryCategories, outputDir)
    }

    private fun exportSecondaryMembershipDump(
        routingResults: Map<Embedding, RoutingResult>,
        queryCategories: Map<String, String>,
        outputDir: String
    ) {
        val file = File(outputDir, "secondary_membership_dump.csv")
        val records = mutableListOf<SecondaryMembershipRecord>()

        for ((emb, res) in routingResults) {
            val trueDomain = queryCategories[emb.rawText] ?: "Other"
            val sortedLeaves = res.leaves.entries.sortedByDescending { it.value }

            val pLeaf = if (sortedLeaves.isNotEmpty()) sortedLeaves[0] else null
            val sLeaf = if (sortedLeaves.size > 1) sortedLeaves[1] else null
            val tLeaf = if (sortedLeaves.size > 2) sortedLeaves[2] else null

            val pProb = pLeaf?.let { entry -> exp(entry.value) } ?: 0.0
            val sProb = sLeaf?.let { entry -> exp(entry.value) } ?: 0.0
            val tProb = tLeaf?.let { entry -> exp(entry.value) } ?: 0.0

            // Entropy calculation
            var entropy = 0.0
            for (i in sortedLeaves.indices) {
                val entry = sortedLeaves[i]
                val prob = exp(entry.value)
                if (prob > 1e-9) {
                    entropy -= prob * ln(prob)
                }
            }

            val marginNats = if (pLeaf != null && sLeaf != null) {
                pLeaf.value - sLeaf.value
            } else {
                Double.POSITIVE_INFINITY
            }

            val bridgeDiagnosticBand = 0.15
            val withinBand = sLeaf != null && marginNats <= bridgeDiagnosticBand

            val routedToResidual = res.residualHits.isNotEmpty()
            val candidateBridgePair = if (pLeaf != null && sLeaf != null) {
                val pairStr = "${pLeaf.key.label ?: pLeaf.key.id} <-> ${sLeaf.key.label ?: sLeaf.key.id}"
                "\"${pairStr.replace("\"", "\"\"")}\""
            } else {
                "None"
            }

            records.add(
                SecondaryMembershipRecord(
                    queryId = emb.queryId.toString(),
                    trueDomain = trueDomain,
                    primaryLeafId = pLeaf?.key?.id ?: "None",
                    primaryProb = pProb,
                    secondaryLeafId = sLeaf?.key?.id ?: "None",
                    secondaryProb = sProb,
                    tertiaryLeafId = tLeaf?.key?.id ?: "None",
                    tertiaryProb = tProb,
                    entropy = entropy,
                    marginNats = marginNats,
                    withinBand = withinBand,
                    routedToResidual = routedToResidual,
                    candidateBridgePair = candidateBridgePair
                )
            )
        }

        // Sort by entropy descending (most ambiguous first) and take top 200
        val sampled = records.sortedByDescending { it.entropy }.take(200)

        file.bufferedWriter().use { writer ->
            writer.write("query_id,true_domain,primary_leaf_id,primary_prob,secondary_leaf_id,secondary_prob,tertiary_leaf_id,tertiary_prob,entropy,margin_nats,within_band,routed_to_residual,candidate_bridge_pair\n")
            for (r in sampled) {
                writer.write(
                    String.format(
                        Locale.US,
                        "%s,%s,%s,%.4f,%s,%.4f,%s,%.4f,%.4f,%.4f,%b,%b,%s\n",
                        r.queryId, r.trueDomain, r.primaryLeafId, r.primaryProb,
                        r.secondaryLeafId, r.secondaryProb, r.tertiaryLeafId, r.tertiaryProb,
                        r.entropy, r.marginNats, r.withinBand, r.routedToResidual, r.candidateBridgePair
                    )
                )
            }
        }
        log.info("Exported ${sampled.size} secondary membership dump records to secondary_membership_dump.csv")
    }

    private fun exportResidualBridgeReadiness(
        root: GraphNode,
        routingResults: Map<Embedding, RoutingResult>,
        queryCategories: Map<String, String>,
        outputDir: String
    ) {
        val file = File(outputDir, "residual_bridge_readiness.csv")
        val allNodes = gatherAllNodes(root)
        val internalNodes = allNodes.filter { !it.isLeaf && it.residualQueries.isNotEmpty() }

        file.bufferedWriter().use { writer ->
            writer.write("node_id,label,depth,region_query_count,local_query_count,residual_count,residual_rate,residual_domains,residual_domain_entropy,avg_best_conf,avg_second_conf,avg_conf_gap,queries_with_second_match,queries_with_third_match,avg_secondary_mass,top_secondary_leaf_ids,top_secondary_leaf_masses\n")

            for (node in internalNodes) {
                val regionWeights = getRegionWeights(node)
                val regionQueryCount = regionWeights.size
                val localQueryCount = node.queryWeights.size
                val residualCount = node.residualQueries.size
                val residualRate = residualCount.toDouble() / regionQueryCount.coerceAtLeast(1)

                // Gather categories of actual queries matching residual IDs
                val residualQueryStrings = node.residualQueries.toSet()
                val matchingEmbs = routingResults.keys.filter { emb ->
                    val qId = if (emb.queryId != -1) emb.queryId.toString() else TextNormalizer.cleanText(emb.rawText)
                    qId in residualQueryStrings
                }

                val categories = matchingEmbs.map { queryCategories[it.rawText] ?: "Other" }
                val catCounts = categories.groupingBy { it }.eachCount()
                val rawResidualDomains = catCounts.keys.joinToString(";")
                val residualDomains = "\"${rawResidualDomains.replace("\"", "\"\"")}\""

                // Entropy
                val totalCat = catCounts.values.sum().toDouble()
                var domainEntropy = 0.0
                if (totalCat > 0.0) {
                    for (count in catCounts.values) {
                        val p = count.toDouble() / totalCat
                        domainEntropy -= p * log2(p)
                    }
                }

                // Confidence gaps & secondary matches for residual queries
                val confidences = node.residualConfidences
                val avgBestConf = if (confidences.isNotEmpty()) confidences.values.average() else 0.0

                var sumSecondConf = 0.0
                var sumConfGap = 0.0
                var secondMatchCount = 0
                var thirdMatchCount = 0
                var sumSecondaryMass = 0.0

                val secondaryLeafMasses = mutableMapOf<String, Double>()

                for (emb in matchingEmbs) {
                    val res = routingResults[emb] ?: continue
                    val sorted = res.leaves.entries.sortedByDescending { it.value }
                    val pLeaf = if (sorted.isNotEmpty()) sorted[0] else null
                    val sLeaf = if (sorted.size > 1) sorted[1] else null
                    val tLeaf = if (sorted.size > 2) sorted[2] else null

                    if (sLeaf != null) {
                        val sProb = exp(sLeaf.value)
                        sumSecondConf += sProb
                        sumConfGap += (pLeaf?.let { entry -> exp(entry.value) } ?: 0.0) - sProb
                        secondMatchCount++
                        sumSecondaryMass += sProb
                        secondaryLeafMasses.merge(sLeaf.key.id, sProb, Double::plus)
                    }
                    if (tLeaf != null) {
                        thirdMatchCount++
                    }
                }

                val avgSecondConf = if (secondMatchCount > 0) sumSecondConf / secondMatchCount else 0.0
                val avgConfGap = if (secondMatchCount > 0) sumConfGap / secondMatchCount else 0.0
                val avgSecondaryMass = if (secondMatchCount > 0) sumSecondaryMass / secondMatchCount else 0.0

                val topSecondaries = secondaryLeafMasses.entries.sortedByDescending { it.value }.take(3)
                val topSecondaryLeafIds = "\"${topSecondaries.joinToString(";") { it.key }}\""
                val topSecondaryLeafMasses = "\"${topSecondaries.joinToString(";") { String.format(Locale.US, "%.2f", it.value) }}\""

                val rawLabel = node.label ?: node.id
                val escLabel = rawLabel.replace("\"", "\"\"")

                writer.write(
                    String.format(
                        Locale.US,
                        "%s,\"%s\",%d,%d,%d,%d,%.4f,%s,%.4f,%.4f,%.4f,%.4f,%d,%d,%.4f,%s,%s\n",
                        node.id, escLabel, node.depth, regionQueryCount, localQueryCount, residualCount,
                        residualRate, residualDomains, domainEntropy, avgBestConf, avgSecondConf, avgConfGap,
                        secondMatchCount, thirdMatchCount, avgSecondaryMass, topSecondaryLeafIds, topSecondaryLeafMasses
                    )
                )
            }
        }
        log.info("Exported residual bridge readiness metrics for ${internalNodes.size} nodes.")
    }

    private fun exportBridgeCandidateAuditAndSummary(
        root: GraphNode,
        queryCategories: Map<String, String>,
        outputDir: String
    ) {
        val auditFile = File(outputDir, "bridge_candidate_audit.csv")
        val summaryFile = File(outputDir, "bridge_rejection_summary.csv")

        val leaves = gatherAllNodes(root).filter { it.isLeaf }
        val candidatePairs = mutableListOf<Pair<GraphNode, GraphNode>>()

        // Total candidates
        for (i in leaves.indices) {
            for (j in i + 1 until leaves.size) {
                candidatePairs.add(leaves[i] to leaves[j])
            }
        }

        val numSecondaryCandidatesTotal = candidatePairs.size
        var numPassCrossDomain = 0
        var numPassSecondaryMassFloor = 0
        var numPassDistinctnessGate = 0
        var numPassCoherenceGate = 0
        var numPassSupportFloor = 0
        var numPassLcaLegalityCheck = 0
        var numFinalBridges = 0

        auditFile.bufferedWriter().use { writer ->
            writer.write("candidate_id,source_node_id,source_label,source_depth,primary_leaf_id,secondary_leaf_id,lca_id,shared_query_count,shared_query_ids_sample,secondary_mass_sum,secondary_mass_mean,secondary_mass_max,distinct_query_count,member_domains,domain_entropy,cosine_primary_secondary,js_divergence_primary_secondary,coherence_after_attach,bridge_score,accepted,reject_reason\n")

            for (pair in candidatePairs) {
                val u = pair.first
                val v = pair.second
                val candidateId = "cand_${u.id.take(4)}_${v.id.take(4)}"
                val sourceNodeId = "${u.id}_${v.id}"
                val rawSourceLabel = "${u.label ?: u.id} + ${v.label ?: v.id}"
                val sourceLabel = "\"${rawSourceLabel.replace("\"", "\"\"")}\""
                val sourceDepth = maxOf(u.depth, v.depth)

                // 1. LCA & Depth-1 cross-domain check
                val lca = getLCA(u, v)
                val uAncestors = getDepth1Ancestors(u)
                val vAncestors = getDepth1Ancestors(v)
                val crossDomain = uAncestors.intersect(vAncestors).isEmpty()

                // 2. Shared query support & secondary masses
                val uWeights = u.queryWeights
                val vWeights = v.queryWeights
                val sharedQueries = uWeights.keys.intersect(vWeights.keys)
                val sharedQueryCount = sharedQueries.size
                val rawSharedQuerySample = sharedQueries.take(5).joinToString(";")
                val sharedQuerySample = "\"${rawSharedQuerySample.replace("\"", "\"\"")}\""

                val sharedWeights = sharedQueries.map { minOf(uWeights[it] ?: 0.0, vWeights[it] ?: 0.0) }
                val secondaryMassSum = sharedWeights.sum()
                val secondaryMassMean = if (sharedWeights.isNotEmpty()) sharedWeights.average() else 0.0
                val secondaryMassMax = if (sharedWeights.isNotEmpty()) sharedWeights.maxOrNull() ?: 0.0 else 0.0

                val distinctQueryCount = (uWeights.keys + vWeights.keys).size

                // Member domains & entropy
                val catCounts = (uWeights.keys + vWeights.keys).map {
                    queryCategories[it] ?: "Other"
                }.groupingBy { it }.eachCount()
                val rawMemberDomains = catCounts.keys.joinToString(";")
                val memberDomains = "\"${rawMemberDomains.replace("\"", "\"\"")}\""

                val totalCat = catCounts.values.sum().toDouble()
                var domainEntropy = 0.0
                if (totalCat > 0.0) {
                    for (count in catCounts.values) {
                        val p = count.toDouble() / totalCat
                        domainEntropy -= p * log2(p)
                    }
                }

                // Divergence & Cosine
                val commonDim = minOf(u.vmfMu.size, v.vmfMu.size)
                var cosine = 0.0
                var div = 0.0
                if (commonDim > 0) {
                    val projU = StatisticsUtils.projectVector(u.vmfMu, commonDim)
                    val projV = StatisticsUtils.projectVector(v.vmfMu, commonDim)
                    var dot = 0.0
                    for (i in 0 until commonDim) dot += projU[i] * projV[i]
                    cosine = dot.toDouble()
                    div = StatisticsUtils.vmfJsDivergence(projU, u.vmfKappa, projV, v.vmfKappa, commonDim)
                }

                // Independent gate counts
                if (crossDomain) {
                    numPassCrossDomain++
                }
                if (secondaryMassSum >= config.diagnostics.secondaryMassFloor) {
                    numPassSecondaryMassFloor++
                }
                if (cosine in 0.3..0.95) {
                    numPassDistinctnessGate++
                }
                val uMass = uWeights.values.sum()
                val vMass = vWeights.values.sum()
                val uESS = if (uMass > 0.0) (uMass * uMass / uWeights.values.sumOf { it * it }) else 0.0
                val vESS = if (vMass > 0.0) (vMass * vMass / vWeights.values.sumOf { it * it }) else 0.0
                if (uESS >= 10.0 && vESS >= 10.0 && u.vmfKappa >= 1.0 && v.vmfKappa >= 1.0) {
                    numPassCoherenceGate++
                }
                val relFraction = config.diagnostics.bridgeSupportRelFraction * minOf(uMass, vMass)
                if (secondaryMassSum >= config.diagnostics.bridgeSupportFloor && secondaryMassSum >= relFraction) {
                    numPassSupportFloor++
                }
                val cycleExists = isAncestor(u, v) || isAncestor(v, u)
                if (!cycleExists) {
                    numPassLcaLegalityCheck++
                }

                // GATES VALIDATION (Sequential Flow)
                var accepted = true
                var rejectReason = "None"

                // Gate A: Cross Domain (Different depth-1 domains)
                if (!crossDomain) {
                    accepted = false
                    rejectReason = "Leaves belong to same depth-1 domains (${uAncestors.joinToString(";")} vs ${vAncestors.joinToString(";")})"
                }

                // Gate B: Secondary mass floor check
                if (accepted) {
                    if (secondaryMassSum < config.diagnostics.secondaryMassFloor) {
                        rejectReason = "Shared support mass below soft floor ($secondaryMassSum < ${config.diagnostics.secondaryMassFloor})"
                        accepted = false
                    }
                }

                // Gate C: Distinctness gate check (Cosine-based)
                if (accepted) {
                    if (cosine < 0.3 || cosine > 0.95) {
                        rejectReason = "Cosine out of bridge bounds (cos=$cosine not in [0.3, 0.95])"
                        accepted = false
                    }
                }

                // Gate D: Coherence gate check
                if (accepted) {
                    if (uESS < 10.0 || vESS < 10.0 || u.vmfKappa < 1.0 || v.vmfKappa < 1.0) {
                        rejectReason = "Adequate support or kappa check failed (ESS: u=$uESS, v=$vESS; Kappa: u=${u.vmfKappa}, v=${v.vmfKappa})"
                        accepted = false
                    }
                }

                // Gate E: Strict support floor check
                if (accepted) {
                    if (secondaryMassSum < config.diagnostics.bridgeSupportFloor || secondaryMassSum < relFraction) {
                        rejectReason = "Strict support floor or relative fraction check failed ($secondaryMassSum < ${config.diagnostics.bridgeSupportFloor} or < ${(config.diagnostics.bridgeSupportRelFraction * 100).toInt()}% minLeafMass)"
                        accepted = false
                    }
                }

                // Gate F: LCA / Cycle Legality check
                if (accepted) {
                    if (cycleExists) {
                        rejectReason = "Cycle or transitive duplicate legality violation detected"
                        accepted = false
                    }
                }

                if (accepted) {
                    numFinalBridges++
                }

                writer.write(
                    String.format(
                        Locale.US,
                        "%s,%s,%s,%d,%s,%s,%s,%d,%s,%.4f,%.4f,%.4f,%d,%s,%.4f,%.4f,%.4f,1.0000,%.4f,%b,%s\n",
                        candidateId, sourceNodeId, sourceLabel, sourceDepth, u.id, v.id, lca?.id ?: "None",
                        sharedQueryCount, sharedQuerySample, secondaryMassSum, secondaryMassMean, secondaryMassMax,
                        distinctQueryCount, memberDomains, domainEntropy, cosine, div, secondaryMassSum, accepted,
                        "\"${rejectReason.replace("\"", "\"\"")}\""
                    )
                )
            }
        }

        // Export summary
        summaryFile.bufferedWriter().use { writer ->
            writer.write("num_secondary_candidates_total,num_pass_secondary_mass_floor,num_pass_distinctness_gate,num_pass_coherence_gate,num_pass_support_floor,num_pass_lca_legality_check,num_removed_transitive_reduction,num_final_bridges\n")
            writer.write(
                String.format(
                    Locale.US,
                    "%d,%d,%d,%d,%d,%d,0,%d\n",
                    numSecondaryCandidatesTotal, numPassSecondaryMassFloor, numPassDistinctnessGate,
                    numPassCoherenceGate, numPassSupportFloor, numPassLcaLegalityCheck, numFinalBridges
                )
            )
        }
        log.info("Bridge diagnostics: $numPassCrossDomain / $numSecondaryCandidatesTotal candidates are cross-domain (passed Gate A).")
        log.info("Exported bridge candidate audit and rejection summary ($numFinalBridges final bridges passed).")
    }

    // Helper functions
    private fun gatherAllNodes(root: GraphNode): Set<GraphNode> {
        val visited = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (!visited.add(n)) return
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)
        return visited
    }

    private fun getRegionWeights(node: GraphNode): Map<String, Double> {
        val weights = mutableMapOf<String, Double>()
        val visited = mutableSetOf<String>()
        fun walk(n: GraphNode) {
            if (!visited.add(n.id)) return
            for ((q, w) in n.queryWeights) {
                weights[q] = (weights[q] ?: 0.0) + w
            }
            n.treeChildren.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(node)
        return weights
    }

    private fun getLCA(u: GraphNode, v: GraphNode): GraphNode? {
        val uAncestors = mutableSetOf<String>()
        var curr: GraphNode? = u
        while (curr != null) {
            uAncestors.add(curr.id)
            curr = curr.parents.find { it.id == curr?.treeParentId }
        }
        curr = v
        while (curr != null) {
            if (curr.id in uAncestors) return curr
            curr = curr.parents.find { it.id == curr?.treeParentId }
        }
        return null
    }

    private fun getDepth1Ancestors(node: GraphNode): Set<String> {
        val ancestors = mutableSetOf<String>()
        val visited = mutableSetOf<String>()
        fun walk(n: GraphNode) {
            if (!visited.add(n.id)) return
            if (n.depth == 1) {
                (n.originalCategory ?: n.label)?.let { ancestors.add(it) }
            } else {
                val treeParent = n.parents.find { it.id == n.treeParentId }
                if (treeParent != null) {
                    walk(treeParent)
                }
            }
        }
        walk(node)
        return ancestors
    }

    private fun isAncestor(ancestor: GraphNode, descendant: GraphNode): Boolean {
        val visited = mutableSetOf<String>()
        fun check(curr: GraphNode): Boolean {
            if (curr.id == descendant.id) return true
            if (!visited.add(curr.id)) return false
            return curr.children.any { check(it) } || curr.crossLinkChildren.any { check(it) }
        }
        return check(ancestor)
    }

    private data class SecondaryMembershipRecord(
        val queryId: String,
        val trueDomain: String,
        val primaryLeafId: String,
        val primaryProb: Double,
        val secondaryLeafId: String,
        val secondaryProb: Double,
        val tertiaryLeafId: String,
        val tertiaryProb: Double,
        val entropy: Double,
        val marginNats: Double,
        val withinBand: Boolean,
        val routedToResidual: Boolean,
        val candidateBridgePair: String
    )
}
