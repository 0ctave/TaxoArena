package org.eclipse.lmos.arc.app.taxonomy

import kotlin.math.sqrt

/**
 * Optimized mathematical engine for unsupervised high-dimensional clustering.
 * Used to discover proto-domains before statistical boundaries are applied.
 */
object Geometry {

    /**
     * Cosine Distance for embedding comparisons.
     * Returns a value between 0.0 (identical) and 2.0 (opposite).
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
     * Uses parallel stream for region queries to eliminate the N^2 bottleneck
     * when scanning dense nodes for potential sub-domains.
     */
    fun dbscan(points: List<EmbeddedQuery>, eps: Float, minPts: Int): List<List<EmbeddedQuery>> {
        if (points.isEmpty()) return emptyList()

        val clusters = mutableListOf<MutableList<EmbeddedQuery>>()
        val visited = java.util.concurrent.ConcurrentHashMap.newKeySet<String>()
        val inCluster = java.util.concurrent.ConcurrentHashMap.newKeySet<String>()

        for (p in points) {
            // Skip if already visited
            if (!visited.add(p.id)) continue

            // Parallel neighbor search based on geometric proximity
            val neighbors = points.parallelStream()
                .filter { q -> cosineDistance(p.embedding, q.embedding) <= eps }
                .toList()

            // If we hit the minimum density threshold, a new proto-domain is formed
            if (neighbors.size >= minPts) {
                val cluster = java.util.Collections.synchronizedList(mutableListOf<EmbeddedQuery>())
                clusters.add(cluster)

                cluster.add(p)
                inCluster.add(p.id)

                val queue = java.util.concurrent.LinkedBlockingQueue<EmbeddedQuery>(neighbors)
                val neighborsSet = java.util.concurrent.ConcurrentHashMap.newKeySet<String>()
                neighbors.forEach { neighborsSet.add(it.id) }

                // Expand the cluster to all reachable dense neighbors
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
}