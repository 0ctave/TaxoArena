package taxonomy.tui.service

import taxonomy.model.GraphNode
import taxonomy.tui.BatchTrickleTestResults
import taxonomy.tui.DomainF1

/**
 * Per-leaf domain summary derived from the training-query distribution that landed in a leaf.
 * [dominantDomain] is the most frequent MMLU-Pro domain among the leaf's labeled queries and
 * [purity] is its share — a cluster-coherence signal. Leaves with no labeled queries are excluded
 * upstream (they carry no domain signal and would only add noise).
 */
data class LeafDomainProfile(
    val leafId: String,
    val label: String,
    val depth: Int,
    val size: Int,
    val dominantDomain: String,
    val purity: Double,
    val domainHistogram: Map<String, Int>,
    val domainHistogramDouble: Map<String, Double> = emptyMap(),
    val sizeDouble: Double = size.toDouble()
)

/**
 * Pure metric core for the batch-trickle benchmark. Kept free of Spring/IO so it can be unit
 * tested directly: callers supply the leaf profiles, the (domain, queryText) test pairs, and a
 * routing function that maps a query to matched (leafId, confidence) pairs. [TuiGatewayImpl]
 * is a thin orchestrator that builds these inputs from the live DAG and dataset.
 */
object BatchTrickleEvaluator {

    /**
     * Walk every (tree) leaf reachable from [root], deduplicating by id since the graph is a DAG.
     */
    fun collectLeaves(root: GraphNode): List<GraphNode> {
        val out = LinkedHashMap<String, GraphNode>()
        val seen = HashSet<String>()
        fun walk(node: GraphNode) {
            if (!seen.add(node.id)) return
            if (node.isLeaf) {
                out[node.id] = node
            } else {
                node.treeChildren.forEach { walk(it) }
            }
        }
        walk(root)
        return out.values.toList()
    }

    enum class ProfileMode {
        PARTITION, SOFT
    }

    private fun computeSimilarity(emb: taxonomy.model.Embedding, leaf: GraphNode): Double {
        val targetDim = leaf.vmfMu.size
        if (targetDim == 0) return -1.0
        val projected = taxonomy.utils.StatisticsUtils.projectVector(emb.values, targetDim)
        var dot = 0.0
        for (i in 0 until targetDim) {
            dot += projected[i] * leaf.vmfMu[i]
        }
        return dot
    }

    fun buildLeafProfiles(
        leaves: List<GraphNode>,
        textToDomain: Map<String, String>,
        profileMode: ProfileMode = ProfileMode.PARTITION
    ): Map<String, LeafDomainProfile> {
        val out = LinkedHashMap<String, LeafDomainProfile>()
        val queryToLeaves = HashMap<String, MutableList<Pair<GraphNode, Double>>>()
        
        for (leaf in leaves) {
            for (emb in leaf.queries) {
                val queryKey = if (emb.queryId != -1) emb.queryId.toString() else taxonomy.model.TextNormalizer.cleanText(emb.rawText)
                val score = computeSimilarity(emb, leaf)
                queryToLeaves.getOrPut(queryKey) { mutableListOf() }.add(leaf to score)
            }
        }

        val queryAssignments = HashMap<String, Map<String, Double>>()
        for ((queryKey, leafList) in queryToLeaves) {
            if (profileMode == ProfileMode.PARTITION) {
                val bestLeaf = leafList.maxByOrNull { it.second }?.first ?: continue
                queryAssignments[queryKey] = mapOf(bestLeaf.id to 1.0)
            } else {
                val tau = 1.0
                val exponents = leafList.map { it.first.id to kotlin.math.exp(it.second / tau) }
                val sumExp = exponents.sumOf { it.second }
                if (sumExp > 0.0) {
                    queryAssignments[queryKey] = exponents.associate { it.first to (it.second / sumExp) }
                } else {
                    val bestLeaf = leafList.maxByOrNull { it.second }?.first ?: continue
                    queryAssignments[queryKey] = mapOf(bestLeaf.id to 1.0)
                }
            }
        }

        for (leaf in leaves) {
            val countsDouble = HashMap<String, Double>()
            for (emb in leaf.queries) {
                val queryKey = if (emb.queryId != -1) emb.queryId.toString() else taxonomy.model.TextNormalizer.cleanText(emb.rawText)
                val domain = textToDomain[emb.rawText] ?: continue
                val weight = queryAssignments[queryKey]?.get(leaf.id) ?: 0.0
                if (weight > 0.0) {
                    countsDouble[domain] = (countsDouble[domain] ?: 0.0) + weight
                }
            }

            val sizeDouble = countsDouble.values.sum()
            if (sizeDouble < 1e-9) continue

            val dominant = countsDouble.maxByOrNull { it.value }!!
            val countsInt = countsDouble.mapValues { Math.round(it.value).toInt() }.filterValues { it > 0 }
            val sizeInt = Math.round(sizeDouble).toInt()

            out[leaf.id] = LeafDomainProfile(
                leafId = leaf.id,
                label = leaf.label ?: leaf.id,
                depth = leaf.depth,
                size = sizeInt,
                dominantDomain = dominant.key,
                purity = dominant.value / sizeDouble,
                domainHistogram = countsInt,
                domainHistogramDouble = countsDouble,
                sizeDouble = sizeDouble
            )
        }
        return out
    }

    /**
     * Score the reserved test queries against the tagged leaves.
     *
     * @param perLeafDomains leaf-id -> profile, from [buildLeafProfiles].
     * @param testQueries (trueDomain, queryText) pairs.
     * @param routeFn maps a query text to matched (leafId, confidence) pairs (any order).
     * @param onProgress invoked per query with (processed, total, runningTop1Accuracy).
     */
    fun computeBatchTrickleMetrics(
        perLeafDomains: Map<String, LeafDomainProfile>,
        testQueries: List<Pair<String, String>>,
        routeFn: (String) -> List<Pair<String, Double>>,
        onProgress: (Int, Int, Double) -> Unit = { _, _, _ -> },
    ): BatchTrickleTestResults {
        if (testQueries.isEmpty()) return BatchTrickleTestResults()

        var top1Correct = 0
        var anyCorrect = 0
        var noMatch = 0
        var top1Matched = 0
        var puritySum = 0.0
        var depthSum = 0.0

        // Confusion tallies for macro-F1 on the top-1 leaf-domain prediction.
        val tp = HashMap<String, Int>()
        val fp = HashMap<String, Int>()
        val fn = HashMap<String, Int>()
        val support = HashMap<String, Int>()

        val predictedMap = HashMap<String, Map<String, Double>>()
        val gtMap = HashMap<String, String>()
        val matchCounts = mutableListOf<Int>()
        var processed = 0
        for ((trueDomain, text) in testQueries) {
            val rawRoute = routeFn(text)
            if (rawRoute.size == 1 && rawRoute[0].first == "OUT_OF_SCOPE") {
                continue
            }
            support[trueDomain] = (support[trueDomain] ?: 0) + 1
            gtMap[text] = trueDomain

            val matched = rawRoute.mapNotNull { (leafId, conf) ->
                perLeafDomains[leafId]?.let { it to conf }
            }
            matchCounts.add(matched.size)

            if (matched.isEmpty()) {
                noMatch++
                fn[trueDomain] = (fn[trueDomain] ?: 0) + 1  // missed: counts against recall
            } else {
                val domainConf = matched.groupBy { it.first.dominantDomain }
                    .mapValues { (_, list) -> list.maxOf { it.second } }
                predictedMap[text] = domainConf

                val top = matched.maxByOrNull { it.second }!!.first
                top1Matched++
                puritySum += top.purity
                depthSum += top.depth
                val predicted = top.dominantDomain
                if (predicted == trueDomain) {
                    top1Correct++
                    tp[trueDomain] = (tp[trueDomain] ?: 0) + 1
                } else {
                    fp[predicted] = (fp[predicted] ?: 0) + 1
                    fn[trueDomain] = (fn[trueDomain] ?: 0) + 1
                }
                if (matched.any { it.first.dominantDomain == trueDomain }) anyCorrect++
            }

            processed++
            onProgress(processed, testQueries.size, top1Correct.toDouble() / processed)
        }

        val n = processed.toDouble()
        val perDomain = LinkedHashMap<String, DomainF1>()
        var f1Sum = 0.0
        for (domain in support.keys) {
            val t = tp[domain] ?: 0
            val p = fp[domain] ?: 0
            val miss = fn[domain] ?: 0
            val precision = if (t + p > 0) t.toDouble() / (t + p) else 0.0
            val recall = if (t + miss > 0) t.toDouble() / (t + miss) else 0.0
            val f1 = if (precision + recall > 0) 2 * precision * recall / (precision + recall) else 0.0
            perDomain[domain] = DomainF1(support[domain] ?: 0, precision, recall, f1)
            f1Sum += f1
        }
        val macroF1 = if (support.isNotEmpty()) f1Sum / support.size else 0.0
        val eceVal = taxonomy.utils.computeRoutingECE(predictedMap, gtMap)

        val p = top1Correct.toDouble() / n
        val num = processed
        val z = 1.96
        val wilsonLow = if (num > 0) {
            val val1 = p + (z * z) / (2.0 * num)
            val val2 = z * kotlin.math.sqrt((p * (1.0 - p)) / num + (z * z) / (4.0 * num * num))
            val denom = 1.0 + (z * z) / num
            ((val1 - val2) / denom).coerceIn(0.0, 1.0)
        } else 0.0
        val wilsonHigh = if (num > 0) {
            val val1 = p + (z * z) / (2.0 * num)
            val val2 = z * kotlin.math.sqrt((p * (1.0 - p)) / num + (z * z) / (4.0 * num * num))
            val denom = 1.0 + (z * z) / num
            ((val1 + val2) / denom).coerceIn(0.0, 1.0)
        } else 0.0

        val avgMatchCountEval = if (matchCounts.isNotEmpty()) matchCounts.average() else 1.0
        val sortedCounts = matchCounts.sorted()
        val medianNodesPerQueryEval = when {
            sortedCounts.isEmpty() -> 1.0
            sortedCounts.size % 2 == 0 ->
                (sortedCounts[sortedCounts.size / 2].toDouble() + sortedCounts[sortedCounts.size / 2 - 1].toDouble()) / 2.0
            else -> sortedCounts[sortedCounts.size / 2].toDouble()
        }

        return BatchTrickleTestResults(
            totalQueries = processed,
            top1Accuracy = top1Correct / n,
            top1WilsonLow = wilsonLow,
            top1WilsonHigh = wilsonHigh,
            anyMatchAccuracy = anyCorrect / n,
            meanLeafPurity = if (top1Matched > 0) puritySum / top1Matched else 0.0,
            macroF1 = macroF1,
            meanRoutingDepth = if (top1Matched > 0) depthSum / top1Matched else 0.0,
            noMatchRate = noMatch / n,
            perDomainF1 = perDomain,
            ece = eceVal,
            avgMatchCountEval = avgMatchCountEval,
            medianNodesPerQueryEval = medianNodesPerQueryEval,
        )
    }
}
