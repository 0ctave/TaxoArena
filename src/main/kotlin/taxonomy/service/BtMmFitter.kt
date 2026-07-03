package taxonomy.service

import taxonomy.model.NodePairStats
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.sqrt

object BtMmFitter {

    fun fit(
        models: List<String>,
        pairStats: List<NodePairStats>,
        maxIter: Int = 200,
        tol: Double = 1e-6
    ): Map<String, Double> {
        if (models.size < 2) return models.associateWith { 0.0 }

        val idx = models.withIndex().associate { (i, m) -> m to i }
        val K = models.size
        val w = Array(K) { DoubleArray(K) }   // w[i][j] = wins of i when playing j

        for (ps in pairStats) {
            val i = idx[ps.modelA] ?: continue
            val j = idx[ps.modelB] ?: continue
            w[i][j] += ps.winsA
            w[j][i] += ps.winsB
        }

        var s = DoubleArray(K) { 0.0 }

        repeat(maxIter) {
            val sNew = DoubleArray(K)
            for (i in 0 until K) {
                val Wi = (0 until K).sumOf { j -> w[i][j] }
                if (Wi == 0.0) { 
                    sNew[i] = s[i]
                    continue
                }
                val denom = (0 until K).filter { j -> j != i }
                    .sumOf { j ->
                        val nij = w[i][j] + w[j][i]
                        if (nij == 0.0) 0.0
                        else nij / (exp(s[i]) + exp(s[j]))
                    }
                sNew[i] = if (denom == 0.0) s[i] else ln(Wi / denom)
            }
            // normalize
            val mean = sNew.average()
            for (i in 0 until K) sNew[i] -= mean

            val delta = sNew.zip(s.toList()).maxOf { (a, b) -> abs(a - b) }
            s = sNew
            if (delta < tol) return@repeat
        }

        return models.zip(s.toList()).toMap()
    }

    fun estimateStdErrors(
        models: List<String>,
        scores: Map<String, Double>,
        pairStats: List<NodePairStats>
    ): Map<String, Double> {
        val idx = models.withIndex().associate { (i, m) -> m to i }
        val K = models.size
        val fisher = DoubleArray(K)

        for (ps in pairStats) {
            val i = idx[ps.modelA] ?: continue
            val j = idx[ps.modelB] ?: continue
            val si = scores[ps.modelA] ?: 0.0
            val sj = scores[ps.modelB] ?: 0.0
            val denom = exp(si) + exp(sj)
            val pij = if (denom == 0.0) 0.5 else exp(si) / denom
            val nij = ps.winsA + ps.winsB
            val info = nij * pij * (1.0 - pij)
            fisher[i] += info
            fisher[j] += info
        }

        return models.mapIndexed { i, m ->
            m to if (fisher[i] > 0.0) 1.0 / sqrt(fisher[i]) else 10.0
        }.toMap()
    }
}
