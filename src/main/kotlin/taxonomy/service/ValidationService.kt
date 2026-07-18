package taxonomy.service

import org.slf4j.LoggerFactory
import taxonomy.model.BenchmarkReport
import taxonomy.model.NodePairStats
import taxonomy.model.QueryBenchmarkResult
import kotlinx.serialization.Serializable
import kotlin.math.sqrt

object ValidationService {
    private val log = LoggerFactory.getLogger(ValidationService::class.java)

    @Serializable
    data class ValidationMetricsReport(
        val domain: String,
        val modelAccuracies: Map<String, Double>,
        val spearmanRho: Double,
        val spearmanCiLow: Double,
        val spearmanCiHigh: Double,
        val kendallTau: Double,
        val kendallCiLow: Double,
        val kendallCiHigh: Double,
        val pairwiseWinnerAccuracy: Double,
        val topKJaccard: Double
    )

    fun computeMetrics(
        report: BenchmarkReport,
        models: List<String>,
        domain: String,
        bootstrapResamples: Int = 2000,
        k: Int = 3
    ): ValidationMetricsReport {
        val domainResults = if (domain.isBlank() || domain.equals("OVERALL", ignoreCase = true)) {
            report.queryResults
        } else {
            report.queryResults.filter { qr ->
                qr.gtCategory.equals(domain, ignoreCase = true) || qr.matchedLeafLabels.any { it.equals(domain, ignoreCase = true) }
            }
        }

        if (domainResults.isEmpty()) {
            return ValidationMetricsReport(domain, emptyMap(), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        }

        // 1. Model Accuracies
        val modelAccuracies = models.associateWith { m ->
            val correct = domainResults.count { it.modelCorrect[m] == true }
            correct.toDouble() / domainResults.size.toDouble()
        }

        // 2. BT Scores from the original run
        val originalStats = buildPairStats(domainResults, models, domain)
        val originalBtScores = BtMmFitter.fit(models, originalStats)

        // 3. Compute base Spearman, Kendall, Pairwise Winner, Jaccard
        val accVector = models.map { modelAccuracies[it] ?: 0.0 }
        val btVector = models.map { originalBtScores[it] ?: 0.0 }

        val baseSpearman = computeSpearman(accVector, btVector)
        val baseKendall = computeKendall(accVector, btVector)
        val basePairwise = computePairwiseWinnerAccuracy(accVector, btVector)
        val baseJaccard = computeTopKJaccard(accVector, btVector, models, k)

        // 4. Bootstrap CI
        val spearmanList = mutableListOf<Double>()
        val kendallList = mutableListOf<Double>()

        val random = java.util.Random(42)
        repeat(bootstrapResamples) {
            val resampled = List(domainResults.size) {
                domainResults[random.nextInt(domainResults.size)]
            }

            val resampledAcc = models.map { m ->
                val correct = resampled.count { it.modelCorrect[m] == true }
                correct.toDouble() / resampled.size.toDouble()
            }

            val resampledStats = buildPairStats(resampled, models, domain)
            val resampledBtScores = BtMmFitter.fit(models, resampledStats)
            val resampledBt = models.map { resampledBtScores[it] ?: 0.0 }

            val rho = computeSpearman(resampledAcc, resampledBt)
            val tau = computeKendall(resampledAcc, resampledBt)

            if (!rho.isNaN()) spearmanList.add(rho)
            if (!tau.isNaN()) kendallList.add(tau)
        }

        spearmanList.sort()
        kendallList.sort()

        val spearmanCiLow = if (spearmanList.isNotEmpty()) spearmanList[(spearmanList.size * 0.025).toInt()] else 0.0
        val spearmanCiHigh = if (spearmanList.isNotEmpty()) spearmanList[(spearmanList.size * 0.975).toInt().coerceAtMost(spearmanList.size - 1)] else 0.0

        val kendallCiLow = if (kendallList.isNotEmpty()) kendallList[(kendallList.size * 0.025).toInt()] else 0.0
        val kendallCiHigh = if (kendallList.isNotEmpty()) kendallList[(kendallList.size * 0.975).toInt().coerceAtMost(kendallList.size - 1)] else 0.0

        return ValidationMetricsReport(
            domain = domain,
            modelAccuracies = modelAccuracies,
            spearmanRho = if (baseSpearman.isNaN()) 0.0 else baseSpearman,
            spearmanCiLow = spearmanCiLow,
            spearmanCiHigh = spearmanCiHigh,
            kendallTau = if (baseKendall.isNaN()) 0.0 else baseKendall,
            kendallCiLow = kendallCiLow,
            kendallCiHigh = kendallCiHigh,
            pairwiseWinnerAccuracy = basePairwise,
            topKJaccard = baseJaccard
        )
    }

    private fun buildPairStats(results: List<QueryBenchmarkResult>, models: List<String>, domain: String): List<NodePairStats> {
        val statsMap = mutableMapOf<String, NodePairStats>()
        for (qr in results) {
            qr.pairEvaluations.forEach { (pairKey, evals) ->
                val parts = pairKey.split("_vs_")
                val mA = parts.getOrNull(0) ?: return@forEach
                val mB = parts.getOrNull(1) ?: return@forEach
                if (mA !in models || mB !in models) return@forEach

                evals.forEach { eval ->
                    val isTie = eval.winner.equals("TIE", ignoreCase = true)
                    val isA = eval.winner.equals("Model A", ignoreCase = true)
                    val wA = if (isTie) 0.5 else if (isA) 1.0 else 0.0
                    val wB = if (isTie) 0.5 else if (isA) 0.0 else 1.0

                    val k = "${minOf(mA, mB)}|${maxOf(mA, mB)}"
                    val existing = statsMap[k]
                    if (existing != null) {
                        if (mA < mB) {
                            existing.winsA += wA
                            existing.winsB += wB
                        } else {
                            existing.winsA += wB
                            existing.winsB += wA
                        }
                        existing.ties += if (isTie) 1 else 0
                        existing.totalComparisons += 1
                    } else {
                        statsMap[k] = NodePairStats(
                            nodeId = domain,
                            modelA = minOf(mA, mB),
                            modelB = maxOf(mA, mB),
                            winsA = if (mA < mB) wA else wB,
                            winsB = if (mA < mB) wB else wA,
                            ties = if (isTie) 1 else 0,
                            totalComparisons = 1
                        )
                    }
                }
            }
        }
        return statsMap.values.toList()
    }

    fun computeSpearman(x: List<Double>, y: List<Double>): Double {
        val n = x.size
        if (n < 2) return 0.0
        val rx = getRanks(x)
        val ry = getRanks(y)
        return computePearson(rx, ry)
    }

    fun computeKendall(x: List<Double>, y: List<Double>): Double {
        val n = x.size
        if (n < 2) return 0.0
        var concordant = 0
        var discordant = 0
        var tiesX = 0
        var tiesY = 0

        for (i in 0 until n) {
            for (j in i + 1 until n) {
                val dx = x[i] - x[j]
                val dy = y[i] - y[j]
                if (dx == 0.0 && dy == 0.0) {
                    // tie in both
                } else if (dx == 0.0) {
                    tiesX++
                } else if (dy == 0.0) {
                    tiesY++
                } else if (dx * dy > 0.0) {
                    concordant++
                } else {
                    discordant++
                }
            }
        }

        val totalPairs = n.toDouble() * (n - 1) / 2.0
        val denom = sqrt((totalPairs - tiesX) * (totalPairs - tiesY))
        if (denom == 0.0) return 0.0
        return (concordant - discordant).toDouble() / denom
    }

    fun computePairwiseWinnerAccuracy(acc: List<Double>, bt: List<Double>): Double {
        var correct = 0
        var total = 0
        val n = acc.size
        for (i in 0 until n) {
            for (j in i + 1 until n) {
                val accDiff = acc[i] - acc[j]
                val btDiff = bt[i] - bt[j]
                if (accDiff != 0.0) {
                    total++
                    if ((accDiff > 0.0 && btDiff > 0.0) || (accDiff < 0.0 && btDiff < 0.0)) {
                        correct++
                    }
                }
            }
        }
        if (total == 0) return 1.0
        return correct.toDouble() / total.toDouble()
    }

    fun computeTopKJaccard(acc: List<Double>, bt: List<Double>, models: List<String>, k: Int): Double {
        val limit = k.coerceAtMost(models.size)
        if (limit <= 0) return 1.0

        val topAcc = models.zip(acc).sortedByDescending { it.second }.map { it.first }.take(limit).toSet()
        val topBt = models.zip(bt).sortedByDescending { it.second }.map { it.first }.take(limit).toSet()

        val intersect = topAcc.intersect(topBt).size.toDouble()
        val union = topAcc.union(topBt).size.toDouble()
        if (union == 0.0) return 1.0
        return intersect / union
    }

    private fun getRanks(x: List<Double>): List<Double> {
        val n = x.size
        val indexed = x.withIndex().sortedBy { it.value }
        val ranks = DoubleArray(n)
        var i = 0
        while (i < n) {
            var j = i + 1
            while (j < n && indexed[j].value == indexed[i].value) {
                j++
            }
            val rankAvg = (i + 1 + j).toDouble() / 2.0
            for (k in i until j) {
                ranks[indexed[k].index] = rankAvg
            }
            i = j
        }
        return ranks.toList()
    }

    private fun computePearson(x: List<Double>, y: List<Double>): Double {
        val n = x.size
        val meanX = x.average()
        val meanY = y.average()
        var num = 0.0
        var denX = 0.0
        var denY = 0.0
        for (i in 0 until n) {
            val dx = x[i] - meanX
            val dy = y[i] - meanY
            num += dx * dy
            denX += dx * dx
            denY += dy * dy
        }
        val den = sqrt(denX * denY)
        if (den == 0.0) return 0.0
        return num / den
    }
}
