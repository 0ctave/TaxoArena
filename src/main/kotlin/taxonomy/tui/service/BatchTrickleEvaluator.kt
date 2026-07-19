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

    /**
     * Tag each leaf with the dominant domain of the training queries it holds. [textToDomain] maps
     * a query's raw text to its true domain (built from the train set). Leaves whose queries carry
     * no domain label (post-merge orphans) are skipped.
     */
    fun buildLeafProfiles(
        leaves: List<GraphNode>,
        textToDomain: Map<String, String>,
    ): Map<String, LeafDomainProfile> {
        val out = LinkedHashMap<String, LeafDomainProfile>()
        for (leaf in leaves) {
            val counts = HashMap<String, Int>()
            for (emb in leaf.queries) {
                val domain = textToDomain[emb.rawText] ?: continue
                counts[domain] = (counts[domain] ?: 0) + 1
            }
            val labeled = counts.values.sum()
            if (labeled == 0) continue
            val dominant = counts.maxByOrNull { it.value }!!
            out[leaf.id] = LeafDomainProfile(
                leafId = leaf.id,
                label = leaf.label ?: leaf.id,
                depth = leaf.depth,
                size = labeled,
                dominantDomain = dominant.key,
                purity = dominant.value.toDouble() / labeled,
                domainHistogram = counts,
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

        var processed = 0
        for ((trueDomain, text) in testQueries) {
            support[trueDomain] = (support[trueDomain] ?: 0) + 1
            gtMap[text] = trueDomain

            val matched = routeFn(text).mapNotNull { (leafId, conf) ->
                perLeafDomains[leafId]?.let { it to conf }
            }

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

        val n = testQueries.size.toDouble()
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

        return BatchTrickleTestResults(
            totalQueries = testQueries.size,
            top1Accuracy = top1Correct / n,
            anyMatchAccuracy = anyCorrect / n,
            meanLeafPurity = if (top1Matched > 0) puritySum / top1Matched else 0.0,
            macroF1 = macroF1,
            meanRoutingDepth = if (top1Matched > 0) depthSum / top1Matched else 0.0,
            noMatchRate = noMatch / n,
            perDomainF1 = perDomain,
            ece = eceVal,
        )
    }
}
