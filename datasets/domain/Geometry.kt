package org.eclipse.lmos.arc.app.domain

import kotlinx.serialization.Serializable
import java.util.UUID
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sqrt

/**
 * Wrapper for queries mapped into the continuous embedding space during local node expansion.
 */
class EmbeddedQuery(
    val text: String,
    val embedding: FloatArray,
    val id: String = UUID.randomUUID().toString()
) {
    override fun equals(other: Any?): Boolean = (other as? EmbeddedQuery)?.id == this.id
    override fun hashCode(): Int = id.hashCode()
}

/**
 * Core mathematical engine for defining and operating on continuous embedding spaces.
 */
object Geometry {

    // Padding radius to ensure every query has a non-zero hypercuboid volume
    const val DELTA = 0.02f

    /**
     * An Axis-Aligned Bounding Volume (Hypercuboid) in high-dimensional space.
     */
    @Serializable
    class Hypercuboid(val minBounds: FloatArray, val maxBounds: FloatArray) {

        /**
         * Online Expansion: Relax the boundaries in O(d) time to envelop a new point.
         */
        fun expand(point: FloatArray) {
            for (i in minBounds.indices) {
                if (point[i] - DELTA < minBounds[i]) minBounds[i] = point[i] - DELTA
                if (point[i] + DELTA > maxBounds[i]) maxBounds[i] = point[i] + DELTA
            }
        }
    }

    /**
     * Creates a bounding box around a set of dense embedding vectors.
     */
    fun createHypercuboid(points: List<FloatArray>): Hypercuboid? {
        if (points.isEmpty()) return null
        val d = points.first().size
        val min = FloatArray(d) { Float.MAX_VALUE }
        val max = FloatArray(d) { -Float.MAX_VALUE }

        for (pt in points) {
            for (i in 0 until d) {
                if (pt[i] < min[i]) min[i] = pt[i]
                if (pt[i] > max[i]) max[i] = pt[i]
            }
        }

        // Pad with Delta
        for (i in 0 until d) {
            min[i] -= DELTA
            max[i] += DELTA
        }
        return Hypercuboid(min, max)
    }

    fun createPointBox(point: FloatArray): Hypercuboid = createHypercuboid(listOf(point))!!

    /**
     * Calculates the Intersection over Union (IoU) of two hypercuboids.
     */
    fun calculateIoU(h1: Hypercuboid, h2: Hypercuboid): Float {
        var totalIoU = 0f
        val d = h1.minBounds.size
        for (i in 0 until d) {
            val intersectionW = max(0f, min(h1.maxBounds[i], h2.maxBounds[i]) - max(h1.minBounds[i], h2.minBounds[i]))
            val unionW = max(h1.maxBounds[i], h2.maxBounds[i]) - min(h1.minBounds[i], h2.minBounds[i])
            totalIoU += if (unionW > 0) intersectionW / unionW else 1f
        }
        return totalIoU / d
    }

    /**
     * Calculates what percentage of the 'inner' hypercuboid resides within the 'outer' hypercuboid.
     * A score of 1.0 means it is perfectly subsumed.
     */
    fun calculateInclusionRatio(outer: Hypercuboid, inner: Hypercuboid): Float {
        var totalInclusion = 0f
        val d = outer.minBounds.size
        for (i in 0 until d) {
            val intersectionW = max(0f, min(outer.maxBounds[i], inner.maxBounds[i]) - max(outer.minBounds[i], inner.minBounds[i]))
            val innerW = inner.maxBounds[i] - inner.minBounds[i]
            totalInclusion += if (innerW > 0) intersectionW / innerW else 1f
        }
        return totalInclusion / d
    }

    /**
     * Cosine Distance for embedding comparisons.
     */
    fun cosineDistance(v1: FloatArray, v2: FloatArray): Float {
        var dot = 0f; var n1 = 0f; var n2 = 0f
        for (i in v1.indices) {
            dot += v1[i] * v2[i]
            n1 += v1[i] * v1[i]
            n2 += v2[i] * v2[i]
        }
        return if (n1 == 0f || n2 == 0f) 1f else 1f - (dot / (sqrt(n1.toDouble()) * sqrt(n2.toDouble())).toFloat())
    }

    /**
     * Optimized Parallel DBSCAN.
     * Uses parallel stream for region queries to eliminate the N^2 bottleneck on large unmapped sets.
     */
    fun dbscan(points: List<EmbeddedQuery>, eps: Float, minPts: Int): List<List<EmbeddedQuery>> {
        if (points.isEmpty()) return emptyList()

        val clusters = mutableListOf<MutableList<EmbeddedQuery>>()
        val visited = java.util.concurrent.ConcurrentHashMap.newKeySet<String>()
        val inCluster = java.util.concurrent.ConcurrentHashMap.newKeySet<String>()

        for (p in points) {
            if (!visited.add(p.id)) continue

            // Parallel neighbor search
            val neighbors = points.parallelStream()
                .filter { q -> cosineDistance(p.embedding, q.embedding) <= eps }
                .toList()

            if (neighbors.size >= minPts) {
                val cluster = java.util.Collections.synchronizedList(mutableListOf<EmbeddedQuery>())
                clusters.add(cluster)

                cluster.add(p)
                inCluster.add(p.id)

                val queue = java.util.concurrent.LinkedBlockingQueue<EmbeddedQuery>(neighbors)
                val neighborsSet = java.util.concurrent.ConcurrentHashMap.newKeySet<String>()
                neighbors.forEach { neighborsSet.add(it.id) }

                while (queue.isNotEmpty()) {
                    val q = queue.poll()
                    if (visited.add(q.id)) {
                        val qNeighbors = points.parallelStream()
                            .filter { n -> cosineDistance(q.embedding, n.embedding) <= eps }
                            .toList()

                        if (qNeighbors.size >= minPts) {
                            for (n in qNeighbors) {
                                if (neighborsSet.add(n.id)) {
                                    queue.add(n)
                                }
                            }
                        }
                    }
                    if (inCluster.add(q.id)) {
                        cluster.add(q)
                    }
                }
            }
        }
        return clusters
    }

    private fun regionQuery(p: EmbeddedQuery, points: List<EmbeddedQuery>, eps: Float): List<EmbeddedQuery> {
        return points.filter { q -> cosineDistance(p.embedding, q.embedding) <= eps }
    }
}