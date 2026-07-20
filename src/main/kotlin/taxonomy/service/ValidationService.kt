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
        val topKJaccard: Double,
        
        // Thesis adaptation significance metrics
        val adaptedSpearmanRho: Double = 0.0,
        val adaptedSpearmanCiLow: Double = 0.0,
        val adaptedSpearmanCiHigh: Double = 0.0,
        val canonicalSpearmanRho: Double = 0.0,
        val canonicalSpearmanCiLow: Double = 0.0,
        val canonicalSpearmanCiHigh: Double = 0.0,
        val deltaSpearmanRho: Double = 0.0,
        val deltaSpearmanCiLow: Double = 0.0,
        val deltaSpearmanCiHigh: Double = 0.0,
        val deltaSpearmanPermutationPValue: Double = 1.0,

        val adaptedKendallTau: Double = 0.0,
        val adaptedKendallCiLow: Double = 0.0,
        val adaptedKendallCiHigh: Double = 0.0,
        val canonicalKendallTau: Double = 0.0,
        val canonicalKendallCiLow: Double = 0.0,
        val canonicalKendallCiHigh: Double = 0.0,
        val deltaKendallTau: Double = 0.0,
        val deltaKendallCiLow: Double = 0.0,
        val deltaKendallCiHigh: Double = 0.0,
        val deltaKendallPermutationPValue: Double = 1.0,

        // Soft membership metrics
        val rhoHardCanonical: Double = 0.0,
        val rhoHardAdapted: Double = 0.0,
        val rhoSoftAdapted: Double = 0.0,
        val deltaRhoGeom: Double = 0.0,
        val deltaRhoSoft: Double = 0.0,
        val deltaRhoTotal: Double = 0.0,
        val rhoSoftAdaptedCiLow: Double = 0.0,
        val rhoSoftAdaptedCiHigh: Double = 0.0,
        val deltaRhoSoftCiLow: Double = 0.0,
        val deltaRhoSoftCiHigh: Double = 0.0,
        val deltaRhoTotalCiLow: Double = 0.0,
        val deltaRhoTotalCiHigh: Double = 0.0
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

        val canonicalBtScores = computeCanonicalBtScores(domainResults, models)
        val adaptedBtScores = computeAdaptedBtScoresFromResults(domainResults, models)
        val softBtScores = computeSoftAdaptedBtScores(domainResults, models)

        // 3. Compute base Spearman, Kendall, Pairwise Winner, Jaccard
        val accVector = models.map { modelAccuracies[it] ?: 0.0 }
        val btVector = models.map { originalBtScores[it] ?: 0.0 }

        val adaptedBtVector = models.map { adaptedBtScores[it] ?: 0.0 }
        val canonicalBtVector = models.map { canonicalBtScores[it] ?: 0.0 }
        val softBtVector = models.map { softBtScores[it] ?: 0.0 }

        val baseSpearman = computeSpearman(accVector, btVector)
        val baseKendall = computeKendall(accVector, btVector)
        val basePairwise = computePairwiseWinnerAccuracy(accVector, btVector)
        val baseJaccard = computeTopKJaccard(accVector, btVector, models, k)

        val adaptedSpearman = computeSpearman(accVector, adaptedBtVector)
        val canonicalSpearman = computeSpearman(accVector, canonicalBtVector)
        val deltaSpearman = adaptedSpearman - canonicalSpearman

        val adaptedKendall = computeKendall(accVector, adaptedBtVector)
        val canonicalKendall = computeKendall(accVector, canonicalBtVector)
        val deltaKendall = adaptedKendall - canonicalKendall

        // Soft membership base metrics
        val softSpearman = computeSpearman(accVector, softBtVector)
        val deltaRhoGeom = deltaSpearman
        val deltaRhoSoft = softSpearman - adaptedSpearman
        val deltaRhoTotal = softSpearman - canonicalSpearman

        // 4. Bootstrap CI
        val spearmanList = mutableListOf<Double>()
        val kendallList = mutableListOf<Double>()

        val adaptedSpearmanList = mutableListOf<Double>()
        val canonicalSpearmanList = mutableListOf<Double>()
        val deltaSpearmanList = mutableListOf<Double>()

        val adaptedKendallList = mutableListOf<Double>()
        val canonicalKendallList = mutableListOf<Double>()
        val deltaKendallList = mutableListOf<Double>()

        val rhoSoftAdaptedList = mutableListOf<Double>()
        val deltaRhoSoftList = mutableListOf<Double>()
        val deltaRhoTotalList = mutableListOf<Double>()

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

            val resampledBtAdapted = computeAdaptedBtScoresFromResults(resampled, models)
            val resampledBtCanonical = computeCanonicalBtScores(resampled, models)
            val resampledBtSoft = computeSoftAdaptedBtScores(resampled, models)

            val resampledBtAdaptedVec = models.map { resampledBtAdapted[it] ?: 0.0 }
            val resampledBtCanonicalVec = models.map { resampledBtCanonical[it] ?: 0.0 }
            val resampledBtSoftVec = models.map { resampledBtSoft[it] ?: 0.0 }

            val rho = computeSpearman(resampledAcc, resampledBt)
            val tau = computeKendall(resampledAcc, resampledBt)

            val rhoAdapted = computeSpearman(resampledAcc, resampledBtAdaptedVec)
            val rhoCanonical = computeSpearman(resampledAcc, resampledBtCanonicalVec)
            val deltaRho = rhoAdapted - rhoCanonical

            val rhoSoft = computeSpearman(resampledAcc, resampledBtSoftVec)
            val deltaRhoS = rhoSoft - rhoAdapted
            val deltaRhoT = rhoSoft - rhoCanonical

            val tauAdapted = computeKendall(resampledAcc, resampledBtAdaptedVec)
            val tauCanonical = computeKendall(resampledAcc, resampledBtCanonicalVec)
            val deltaTau = tauAdapted - tauCanonical

            if (!rho.isNaN()) spearmanList.add(rho)
            if (!tau.isNaN()) kendallList.add(tau)

            if (!rhoAdapted.isNaN()) adaptedSpearmanList.add(rhoAdapted)
            if (!rhoCanonical.isNaN()) canonicalSpearmanList.add(rhoCanonical)
            if (!deltaRho.isNaN()) deltaSpearmanList.add(deltaRho)

            if (!tauAdapted.isNaN()) adaptedKendallList.add(tauAdapted)
            if (!tauCanonical.isNaN()) canonicalKendallList.add(tauCanonical)
            if (!deltaTau.isNaN()) deltaKendallList.add(deltaTau)

            if (!rhoSoft.isNaN()) rhoSoftAdaptedList.add(rhoSoft)
            if (!deltaRhoS.isNaN()) deltaRhoSoftList.add(deltaRhoS)
            if (!deltaRhoT.isNaN()) deltaRhoTotalList.add(deltaRhoT)
        }

        spearmanList.sort()
        kendallList.sort()
        adaptedSpearmanList.sort()
        canonicalSpearmanList.sort()
        deltaSpearmanList.sort()
        adaptedKendallList.sort()
        canonicalKendallList.sort()
        deltaKendallList.sort()

        rhoSoftAdaptedList.sort()
        deltaRhoSoftList.sort()
        deltaRhoTotalList.sort()

        val spearmanCiLow = if (spearmanList.isNotEmpty()) spearmanList[(spearmanList.size * 0.025).toInt()] else 0.0
        val spearmanCiHigh = if (spearmanList.isNotEmpty()) spearmanList[(spearmanList.size * 0.975).toInt().coerceAtMost(spearmanList.size - 1)] else 0.0

        val kendallCiLow = if (kendallList.isNotEmpty()) kendallList[(kendallList.size * 0.025).toInt()] else 0.0
        val kendallCiHigh = if (kendallList.isNotEmpty()) kendallList[(kendallList.size * 0.975).toInt().coerceAtMost(kendallList.size - 1)] else 0.0

        val adaptedSpearmanCiLow = if (adaptedSpearmanList.isNotEmpty()) adaptedSpearmanList[(adaptedSpearmanList.size * 0.025).toInt()] else 0.0
        val adaptedSpearmanCiHigh = if (adaptedSpearmanList.isNotEmpty()) adaptedSpearmanList[(adaptedSpearmanList.size * 0.975).toInt().coerceAtMost(adaptedSpearmanList.size - 1)] else 0.0

        val canonicalSpearmanCiLow = if (canonicalSpearmanList.isNotEmpty()) canonicalSpearmanList[(canonicalSpearmanList.size * 0.025).toInt()] else 0.0
        val canonicalSpearmanCiHigh = if (canonicalSpearmanList.isNotEmpty()) canonicalSpearmanList[(canonicalSpearmanList.size * 0.975).toInt().coerceAtMost(canonicalSpearmanList.size - 1)] else 0.0

        val deltaSpearmanCiLow = if (deltaSpearmanList.isNotEmpty()) deltaSpearmanList[(deltaSpearmanList.size * 0.025).toInt()] else 0.0
        val deltaSpearmanCiHigh = if (deltaSpearmanList.isNotEmpty()) deltaSpearmanList[(deltaSpearmanList.size * 0.975).toInt().coerceAtMost(deltaSpearmanList.size - 1)] else 0.0

        val adaptedKendallCiLow = if (adaptedKendallList.isNotEmpty()) adaptedKendallList[(adaptedKendallList.size * 0.025).toInt()] else 0.0
        val adaptedKendallCiHigh = if (adaptedKendallList.isNotEmpty()) adaptedKendallList[(adaptedKendallList.size * 0.975).toInt().coerceAtMost(adaptedKendallList.size - 1)] else 0.0

        val canonicalKendallCiLow = if (canonicalKendallList.isNotEmpty()) canonicalKendallList[(canonicalKendallList.size * 0.025).toInt()] else 0.0
        val canonicalKendallCiHigh = if (canonicalKendallList.isNotEmpty()) canonicalKendallList[(canonicalKendallList.size * 0.975).toInt().coerceAtMost(canonicalKendallList.size - 1)] else 0.0

        val deltaKendallCiLow = if (deltaKendallList.isNotEmpty()) deltaKendallList[(deltaKendallList.size * 0.025).toInt()] else 0.0
        val deltaKendallCiHigh = if (deltaKendallList.isNotEmpty()) deltaKendallList[(deltaKendallList.size * 0.975).toInt().coerceAtMost(deltaKendallList.size - 1)] else 0.0

        val rhoSoftAdaptedCiLow = if (rhoSoftAdaptedList.isNotEmpty()) rhoSoftAdaptedList[(rhoSoftAdaptedList.size * 0.025).toInt()] else 0.0
        val rhoSoftAdaptedCiHigh = if (rhoSoftAdaptedList.isNotEmpty()) rhoSoftAdaptedList[(rhoSoftAdaptedList.size * 0.975).toInt().coerceAtMost(rhoSoftAdaptedList.size - 1)] else 0.0

        val deltaRhoSoftCiLow = if (deltaRhoSoftList.isNotEmpty()) deltaRhoSoftList[(deltaRhoSoftList.size * 0.025).toInt()] else 0.0
        val deltaRhoSoftCiHigh = if (deltaRhoSoftList.isNotEmpty()) deltaRhoSoftList[(deltaRhoSoftList.size * 0.975).toInt().coerceAtMost(deltaRhoSoftList.size - 1)] else 0.0

        val deltaRhoTotalCiLow = if (deltaRhoTotalList.isNotEmpty()) deltaRhoTotalList[(deltaRhoTotalList.size * 0.025).toInt()] else 0.0
        val deltaRhoTotalCiHigh = if (deltaRhoTotalList.isNotEmpty()) deltaRhoTotalList[(deltaRhoTotalList.size * 0.975).toInt().coerceAtMost(deltaRhoTotalList.size - 1)] else 0.0

        val deltaSpearmanPVal = computePermutationPValue(accVector, adaptedBtVector, canonicalBtVector, deltaSpearman)
        val deltaKendallPVal = computePermutationPValue(accVector, adaptedBtVector, canonicalBtVector, deltaKendall)

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
            topKJaccard = baseJaccard,
            adaptedSpearmanRho = if (adaptedSpearman.isNaN()) 0.0 else adaptedSpearman,
            adaptedSpearmanCiLow = adaptedSpearmanCiLow,
            adaptedSpearmanCiHigh = adaptedSpearmanCiHigh,
            canonicalSpearmanRho = if (canonicalSpearman.isNaN()) 0.0 else canonicalSpearman,
            canonicalSpearmanCiLow = canonicalSpearmanCiLow,
            canonicalSpearmanCiHigh = canonicalSpearmanCiHigh,
            deltaSpearmanRho = if (deltaSpearman.isNaN()) 0.0 else deltaSpearman,
            deltaSpearmanCiLow = deltaSpearmanCiLow,
            deltaSpearmanCiHigh = deltaSpearmanCiHigh,
            deltaSpearmanPermutationPValue = deltaSpearmanPVal,
            adaptedKendallTau = if (adaptedKendall.isNaN()) 0.0 else adaptedKendall,
            adaptedKendallCiLow = adaptedKendallCiLow,
            adaptedKendallCiHigh = adaptedKendallCiHigh,
            canonicalKendallTau = if (canonicalKendall.isNaN()) 0.0 else canonicalKendall,
            canonicalKendallCiLow = canonicalKendallCiLow,
            canonicalKendallCiHigh = canonicalKendallCiHigh,
            deltaKendallTau = if (deltaKendall.isNaN()) 0.0 else deltaKendall,
            deltaKendallCiLow = deltaKendallCiLow,
            deltaKendallCiHigh = deltaKendallCiHigh,
            deltaKendallPermutationPValue = deltaKendallPVal,
            
            // Soft membership metrics
            rhoHardCanonical = if (canonicalSpearman.isNaN()) 0.0 else canonicalSpearman,
            rhoHardAdapted = if (adaptedSpearman.isNaN()) 0.0 else adaptedSpearman,
            rhoSoftAdapted = if (softSpearman.isNaN()) 0.0 else softSpearman,
            deltaRhoGeom = if (deltaRhoGeom.isNaN()) 0.0 else deltaRhoGeom,
            deltaRhoSoft = if (deltaRhoSoft.isNaN()) 0.0 else deltaRhoSoft,
            deltaRhoTotal = if (deltaRhoTotal.isNaN()) 0.0 else deltaRhoTotal,
            rhoSoftAdaptedCiLow = rhoSoftAdaptedCiLow,
            rhoSoftAdaptedCiHigh = rhoSoftAdaptedCiHigh,
            deltaRhoSoftCiLow = deltaRhoSoftCiLow,
            deltaRhoSoftCiHigh = deltaRhoSoftCiHigh,
            deltaRhoTotalCiLow = deltaRhoTotalCiLow,
            deltaRhoTotalCiHigh = deltaRhoTotalCiHigh
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
                        existing.ties += if (isTie) 1.0 else 0.0
                        existing.totalComparisons += 1.0
                    } else {
                        statsMap[k] = NodePairStats(
                            nodeId = domain,
                            modelA = minOf(mA, mB),
                            modelB = maxOf(mA, mB),
                            winsA = if (mA < mB) wA else wB,
                            winsB = if (mA < mB) wB else wA,
                            ties = if (isTie) 1.0 else 0.0,
                            totalComparisons = 1.0
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

    private fun buildPairStatsWithAgreement(
        results: List<QueryBenchmarkResult>, 
        models: List<String>, 
        domain: String
    ): List<NodePairStats> {
        val statsMap = mutableMapOf<String, NodePairStats>()
        for (qr in results) {
            qr.pairEvaluations.forEach { (pairKey, evals) ->
                val parts = pairKey.split("_vs_")
                val mA = parts.getOrNull(0) ?: return@forEach
                 val mB = parts.getOrNull(1) ?: return@forEach
                if (mA !in models || mB !in models) return@forEach

                val isCorrectA = qr.modelCorrect[mA] ?: false
                val isCorrectB = qr.modelCorrect[mB] ?: false

                evals.forEach { eval ->
                    val isTie = eval.winner.equals("TIE", ignoreCase = true)
                    val isA = eval.winner.equals("Model A", ignoreCase = true)
                    val winner = if (isTie) "TIE" else if (isA) mA else mB
                    val accuracyAgreed = (isCorrectA && winner == mA) || (isCorrectB && winner == mB) || (!isCorrectA && !isCorrectB && isTie)

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
                        existing.ties += if (isTie) 1.0 else 0.0
                        existing.totalComparisons += 1.0
                        existing.agreementChecks += 1
                        existing.agreementWins += if (accuracyAgreed) 1 else 0
                    } else {
                        statsMap[k] = NodePairStats(
                            nodeId = domain,
                            modelA = minOf(mA, mB),
                            modelB = maxOf(mA, mB),
                            winsA = if (mA < mB) wA else wB,
                            winsB = if (mA < mB) wB else wA,
                            ties = if (isTie) 1.0 else 0.0,
                            totalComparisons = 1.0,
                            agreementChecks = 1,
                            agreementWins = if (accuracyAgreed) 1 else 0
                        )
                    }
                }
            }
        }
        return statsMap.values.toList()
    }

    fun computeCanonicalBtScores(results: List<QueryBenchmarkResult>, models: List<String>): Map<String, Double> {
        val byCategory = results.groupBy { it.gtCategory }
        val eligibleStats = mutableListOf<NodePairStats>()
        for ((category, queries) in byCategory) {
            val domainStats = buildPairStatsWithAgreement(queries, models, category)
            val totalComparisons = domainStats.sumOf { it.totalComparisons }
            if (totalComparisons < 5) continue
            
            val isConsistent = domainStats.none { 
                it.agreementChecks >= 5 && (it.agreementWins.toDouble() / it.agreementChecks) < 0.50 
            }
            if (isConsistent) {
                eligibleStats.addAll(domainStats)
            }
        }
        if (eligibleStats.isEmpty()) return emptyMap()
        
        val pooled = mutableMapOf<String, NodePairStats>()
        for (ps in eligibleStats) {
            val mA = minOf(ps.modelA, ps.modelB)
            val mB = maxOf(ps.modelA, ps.modelB)
            val key = "$mA|$mB"
            val existing = pooled[key]
            if (existing != null) {
                existing.winsA += ps.winsA
                existing.winsB += ps.winsB
                existing.ties += ps.ties
                existing.totalComparisons += ps.totalComparisons
            } else {
                pooled[key] = NodePairStats(
                    nodeId = "pooled",
                    modelA = mA,
                    modelB = mB,
                    winsA = ps.winsA,
                    winsB = ps.winsB,
                    ties = ps.ties,
                    totalComparisons = ps.totalComparisons
                )
            }
        }
        return BtMmFitter.fit(models, pooled.values.toList())
    }

    fun computeAdaptedBtScoresFromResults(results: List<QueryBenchmarkResult>, models: List<String>): Map<String, Double> {
        val byLeaf = mutableMapOf<String, MutableList<QueryBenchmarkResult>>()
        for (qr in results) {
            val leaves = qr.matchedLeafLabels.ifEmpty { listOf(qr.gtCategory) }
            for (lf in leaves) {
                byLeaf.computeIfAbsent(lf) { mutableListOf() }.add(qr)
            }
        }
        val eligibleStats = mutableListOf<NodePairStats>()
        for ((leafLabel, queries) in byLeaf) {
            val leafStats = buildPairStatsWithAgreement(queries, models, leafLabel)
            val totalComparisons = leafStats.sumOf { it.totalComparisons }
            if (totalComparisons < 5) continue
            val isConsistent = leafStats.none {
                it.agreementChecks >= 5 && (it.agreementWins.toDouble() / it.agreementChecks) < 0.50
            }
            if (isConsistent) {
                eligibleStats.addAll(leafStats)
            }
        }
        if (eligibleStats.isEmpty()) return emptyMap()
        
        val pooled = mutableMapOf<String, NodePairStats>()
        for (ps in eligibleStats) {
            val mA = minOf(ps.modelA, ps.modelB)
            val mB = maxOf(ps.modelA, ps.modelB)
            val key = "$mA|$mB"
            val existing = pooled[key]
            if (existing != null) {
                existing.winsA += ps.winsA
                existing.winsB += ps.winsB
                existing.ties += ps.ties
                existing.totalComparisons += ps.totalComparisons
            } else {
                pooled[key] = NodePairStats(
                    nodeId = "pooled",
                    modelA = mA,
                    modelB = mB,
                    winsA = ps.winsA,
                    winsB = ps.winsB,
                    ties = ps.ties,
                    totalComparisons = ps.totalComparisons
                )
            }
        }
        return BtMmFitter.fit(models, pooled.values.toList())
    }

    fun computePermutationPValue(
        acc: List<Double>, 
        adapted: List<Double>, 
        canonical: List<Double>, 
        baseDelta: Double, 
        permutations: Int = 10000
    ): Double {
        val random = java.util.Random(42)
        var extremeCount = 0
        val n = acc.size
        val absBaseDelta = kotlin.math.abs(baseDelta)
        repeat(permutations) {
            val permAdapted = DoubleArray(n)
            val permCanonical = DoubleArray(n)
            for (i in 0 until n) {
                if (random.nextBoolean()) {
                    permAdapted[i] = adapted[i]
                    permCanonical[i] = canonical[i]
                } else {
                    permAdapted[i] = canonical[i]
                    permCanonical[i] = adapted[i]
                }
            }
            val rhoA = computeSpearman(acc, permAdapted.toList())
            val rhoC = computeSpearman(acc, permCanonical.toList())
            val delta = rhoA - rhoC
            if (kotlin.math.abs(delta) >= absBaseDelta) {
                extremeCount++
            }
        }
        return extremeCount.toDouble() / permutations.toDouble()
    }

    fun computeWilcoxonPValue(adaptedList: List<Double>, canonicalList: List<Double>): Double {
        val diffs = adaptedList.zip(canonicalList).map { it.first - it.second }.filter { it != 0.0 }
        val nr = diffs.size
        if (nr < 3) return 1.0

        val absoluteDiffsWithIndices = diffs.mapIndexed { idx, d -> idx to kotlin.math.abs(d) }
        val sorted = absoluteDiffsWithIndices.sortedBy { it.second }

        val ranks = DoubleArray(nr)
        var i = 0
        while (i < nr) {
            var j = i
            while (j < nr && sorted[j].second == sorted[i].second) {
                j++
            }
            val avgRank = (i + 1 + j).toDouble() / 2.0
            for (k in i until j) {
                ranks[sorted[k].first] = avgRank
            }
            i = j
        }

        var wPlus = 0.0
        var wMinus = 0.0
        for (k in 0 until nr) {
            if (diffs[k] > 0.0) {
                wPlus += ranks[k]
            } else {
                wMinus += ranks[k]
            }
        }

        val w = minOf(wPlus, wMinus)
        val mu = nr.toDouble() * (nr + 1) / 4.0
        val sigma = sqrt(nr.toDouble() * (nr + 1) * (2 * nr + 1) / 24.0)
        if (sigma == 0.0) return 1.0
        val z = (w - mu) / sigma
        return 2.0 * (1.0 - normalCdf(kotlin.math.abs(z)))
    }

    fun chiSquaredToPValue(chi2: Double): Double {
        if (chi2 <= 0.0) return 1.0
        val z = sqrt(chi2)
        return 2.0 * (1.0 - normalCdf(z))
    }

    fun normalCdf(x: Double): Double {
        val absX = kotlin.math.abs(x)
        val t = 1.0 / (1.0 + 0.2316419 * absX)
        val d = 0.3989422804014327 * kotlin.math.exp(-x * x / 2.0)
        val p = d * t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
        return if (x >= 0.0) 1.0 - p else p
    }

    fun computeSoftAdaptedBtScores(results: List<QueryBenchmarkResult>, models: List<String>): Map<String, Double> {
        val byLeafWeighted = mutableMapOf<String, MutableList<Pair<QueryBenchmarkResult, Double>>>()
        for (qr in results) {
            val primaryLabel = qr.matchedLeafLabels.firstOrNull() ?: qr.gtCategory
            val wPrimary = (1.0 - qr.secondaryMemberships.values.sum()).coerceIn(0.0, 1.0)
            
            byLeafWeighted.computeIfAbsent(primaryLabel) { mutableListOf() }.add(qr to wPrimary)
            for ((secondaryLabel, weight) in qr.secondaryMemberships) {
                byLeafWeighted.computeIfAbsent(secondaryLabel) { mutableListOf() }.add(qr to weight)
            }
        }
        
        val eligibleStats = mutableListOf<NodePairStats>()
        for ((leafLabel, weightedQueries) in byLeafWeighted) {
            val leafStats = buildPairStatsWithWeights(weightedQueries, models, leafLabel)
            val totalComparisons = leafStats.sumOf { it.totalComparisons }
            if (totalComparisons < 5.0) continue
            val isConsistent = leafStats.none {
                it.agreementChecks >= 5 && (it.agreementWins.toDouble() / it.agreementChecks) < 0.50
            }
            if (isConsistent) {
                eligibleStats.addAll(leafStats)
            }
        }
        if (eligibleStats.isEmpty()) return emptyMap()
        
        val pooled = mutableMapOf<String, NodePairStats>()
        for (ps in eligibleStats) {
            val mA = minOf(ps.modelA, ps.modelB)
            val mB = maxOf(ps.modelA, ps.modelB)
            val key = "$mA|$mB"
            val existing = pooled[key]
            if (existing != null) {
                existing.winsA += ps.winsA
                existing.winsB += ps.winsB
                existing.ties += ps.ties
                existing.totalComparisons += ps.totalComparisons
            } else {
                pooled[key] = NodePairStats(
                    nodeId = "pooled",
                    modelA = mA,
                    modelB = mB,
                    winsA = ps.winsA,
                    winsB = ps.winsB,
                    ties = ps.ties,
                    totalComparisons = ps.totalComparisons
                )
            }
        }
        return BtMmFitter.fit(models, pooled.values.toList())
    }

    private fun buildPairStatsWithWeights(
        results: List<Pair<QueryBenchmarkResult, Double>>, 
        models: List<String>, 
        domain: String
    ): List<NodePairStats> {
        val statsMap = mutableMapOf<String, NodePairStats>()
        for ((qr, weight) in results) {
            if (weight <= 0.0) continue
            qr.pairEvaluations.forEach { (pairKey, evals) ->
                val parts = pairKey.split("_vs_")
                val mA = parts.getOrNull(0) ?: return@forEach
                val mB = parts.getOrNull(1) ?: return@forEach
                if (mA !in models || mB !in models) return@forEach

                val isCorrectA = qr.modelCorrect[mA] ?: false
                val isCorrectB = qr.modelCorrect[mB] ?: false

                evals.forEach { eval ->
                    val isTie = eval.winner.equals("TIE", ignoreCase = true)
                    val isA = eval.winner.equals("Model A", ignoreCase = true)
                    val winner = if (isTie) "TIE" else if (isA) mA else mB
                    val accuracyAgreed = (isCorrectA && winner == mA) || (isCorrectB && winner == mB) || (!isCorrectA && !isCorrectB && isTie)

                    val wA = (if (isTie) 0.5 else if (isA) 1.0 else 0.0) * weight
                    val wB = (if (isTie) 0.5 else if (isA) 0.0 else 1.0) * weight

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
                        existing.ties += (if (isTie) 1.0 else 0.0) * weight
                        existing.totalComparisons += 1.0 * weight
                        existing.agreementChecks += 1
                        existing.agreementWins += if (accuracyAgreed) 1 else 0
                    } else {
                        statsMap[k] = NodePairStats(
                            nodeId = domain,
                            modelA = minOf(mA, mB),
                            modelB = maxOf(mA, mB),
                            winsA = if (mA < mB) wA else wB,
                            winsB = if (mA < mB) wB else wA,
                            ties = (if (isTie) 1.0 else 0.0) * weight,
                            totalComparisons = 1.0 * weight,
                            agreementChecks = 1,
                            agreementWins = if (accuracyAgreed) 1 else 0
                        )
                    }
                }
            }
        }
        return statsMap.values.toList()
    }
}
