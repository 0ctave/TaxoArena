package taxonomy

import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Test
import taxonomy.utils.StatisticsUtils
import kotlin.math.sqrt

/**
 * SUPERSEDED by SeparationNullBySizeTest. Retained only so its numbers stay
 * reproducible and its provenance auditable; do NOT calibrate against it.
 *
 * It measures a DIFFERENT STATISTIC from the one the bar gates. This harness
 * scores EM's hard assignment in the PCA subspace with the k-gate disabled;
 * production (TaxonomySplitter.splitSingleNode) scores the ROUTED partition at
 * childDim=256 after floor-absorption and weak-pair coarsening. On identical
 * clouds the two differ by roughly 3x, so the isotropic p95 of 0.0209 this file
 * reports is not comparable to the 0.0069 the production path gives at n=406.
 * The header of experiment_configs/canonical_freeze.toml cited the 0.0209 for a
 * time; that citation has been corrected.
 *
 * Its one non-obvious contribution stands: it already swept n
 * ({60,100,150,250,400,700,1200}), so the bar was size-matched to the node it
 * was quoted against, not calibrated at a single small population.
 *
 * Use SeparationNullBySizeTest (`gradlew nullBySize`) instead: it drives the real
 * splitSingleNode and is validated by replaying the frozen Philosophy node.
 * Measured curve: docs/separation_null_by_size.md.
 *
 * ── original description ──────────────────────────────────────────────────
 * CALIBRATION HARNESS (temporary, not for commit): measures the null
 * distribution of the chance-corrected separation under the REAL split pipeline
 * (same pcaProject, same performVmfKMeans, same splitDim tiering) on synthetic
 * single-mode clouds with NO cluster structure. The p95/p99 of the best
 * separation EM finds by pure chance at population n is the statistically
 * correct threshold eps(n); comparing it to eps(n) = 0.01*sqrt(300/n) validates
 * or refutes the N_ref = 300 anchor on this embedding geometry.
 */
class NullSeparationCalibrationTest {

    private fun singleModeCloud(n: Int, dim: Int, sigma: Double, rng: java.util.Random): List<DoubleArray> {
        // x = normalize(mu + sigma * gaussian) — a single isotropic mode on the
        // sphere (vMF-like; sigma controls concentration / kappa).
        return (0 until n).map {
            val v = DoubleArray(dim) { i -> (if (i == 0) 1.0 else 0.0) + sigma * rng.nextGaussian() }
            var norm = 0.0
            for (x in v) norm += x * x
            norm = sqrt(norm)
            DoubleArray(dim) { i -> v[i] / norm }
        }
    }

    private fun splitDimFor(n: Int): Int = when {
        n < 100 -> 32
        n < 500 -> 64
        else -> 128
    }

    private fun bestNullSeparation(n: Int, sigma: Double, minClusterSize: Int, rep: Int): Double {
        val rng = java.util.Random(1234L + n * 7919L + rep * 104729L + (sigma * 1000).toLong())
        val raw = singleModeCloud(n, 256, sigma, rng)
        val splitDim = splitDimFor(n)
        val pca = StatisticsUtils.pcaProject(raw, splitDim)
        val mixture = runBlocking {
            StatisticsUtils.performVmfKMeans(
                embeddings = pca,
                d = splitDim,
                maxK = 4,
                minClusterFrac = minClusterSize.toDouble() / n,
                marginalEps = 1e-9  // no k-gate: measure the max separation EM can manufacture
            )
        } ?: return 0.0
        val k = mixture.components.size
        val clusters = Array(k) { mutableListOf<DoubleArray>() }
        for (i in pca.indices) {
            val resp = mixture.responsibilities[i]
            val best = resp.indices.maxByOrNull { resp[it] } ?: 0
            clusters[best].add(pca[i])
        }
        return StatisticsUtils.chanceCorrectedSeparation(clusters.map { it.toList() })
    }

    @Test
    fun `measure null separation percentiles across populations`() {
        val minClusterSize = 30
        val baseEps = 0.01
        val reps = 60
        val grid = listOf(60, 100, 150, 250, 400, 700, 1200)

        println("sigma=0.5 (moderate concentration), reps=$reps, minClusterSize=$minClusterSize")
        println("%6s %5s %9s %9s %9s | %9s %9s | %8s".format(
            "n", "d", "p50", "p95", "p99", "flat.01", "flat.02", "p95*sqrt(n)"))
        for (n in grid) {
            val seps = (0 until reps).map { bestNullSeparation(n, 0.5, minClusterSize, it) }.sorted()
            val p50 = seps[reps / 2]
            val p95 = seps[(reps * 95) / 100]
            val p99 = seps[(reps * 99) / 100 - 1]
            println("%6d %5d %9.5f %9.5f %9.5f | %9.5f %9.5f | %8.4f".format(
                n, splitDimFor(n), p50, p95, p99, baseEps, 0.02, p95 * sqrt(n.toDouble())))
        }

        println()
        println("Concentration sensitivity at n=300:")
        for (sigma in listOf(0.3, 0.5, 1.0)) {
            val seps = (0 until reps).map { bestNullSeparation(300, sigma, minClusterSize, it) }.sorted()
            val p95 = seps[(reps * 95) / 100]
            println("  sigma=%.1f  p95=%.5f".format(sigma, p95))
        }
    }

    /**
     * REAL-SPECTRUM null: parametric bootstrap on the actual corpus embeddings.
     * x_null = mu + sum_i g_i (x_i - mu)/sqrt(m), g_i ~ N(0,1), then renormalized
     * to the unit sphere — exactly Gaussian with the SAMPLE COVARIANCE of the
     * real embedding cloud (full anisotropy preserved), but unimodal (all cluster
     * structure destroyed). Using the global corpus covariance is the hardest
     * (most anisotropic) case, so its p95 upper-bounds the within-node null.
     */
    @Test
    fun `measure null separation on real embedding spectrum`() {
        val dbFile = java.io.File("embeddings_cache.db")
        org.junit.jupiter.api.Assumptions.assumeTrue(dbFile.exists(), "embeddings_cache.db not present")

        val base = mutableListOf<DoubleArray>()
        java.sql.DriverManager.getConnection("jdbc:sqlite:${dbFile.absolutePath}").use { conn ->
            conn.createStatement().use { stmt ->
                val rs = stmt.executeQuery("SELECT vector FROM embeddings ORDER BY query LIMIT 1500")
                while (rs.next()) {
                    val bytes = rs.getBytes(1) ?: continue
                    val buf = java.nio.ByteBuffer.wrap(bytes)
                    val full = FloatArray(bytes.size / 4) { buf.getFloat() }
                    if (full.size < 256) continue
                    // Same head-slice + renormalize the pipeline's projectTo uses.
                    val v = DoubleArray(256) { full[it].toDouble() }
                    var norm = 0.0
                    for (x in v) norm += x * x
                    norm = sqrt(norm)
                    if (norm > 0) { for (i in v.indices) v[i] /= norm; base.add(v) }
                }
            }
        }
        println("Loaded ${base.size} real embedding vectors (256-d head slice, renormalized).")
        org.junit.jupiter.api.Assumptions.assumeTrue(base.size >= 500, "not enough vectors")

        val m = base.size
        val dim = 256
        val mu = DoubleArray(dim)
        for (v in base) for (i in 0 until dim) mu[i] += v[i] / m
        val centered = base.map { v -> DoubleArray(dim) { i -> v[i] - mu[i] } }
        val invSqrtM = 1.0 / sqrt(m.toDouble())

        fun bootstrapCloud(n: Int, rng: java.util.Random): List<DoubleArray> {
            return (0 until n).map {
                val out = mu.copyOf()
                for (c in centered) {
                    val g = rng.nextGaussian() * invSqrtM
                    for (i in 0 until dim) out[i] += g * c[i]
                }
                var norm = 0.0
                for (x in out) norm += x * x
                norm = sqrt(norm)
                DoubleArray(dim) { i -> out[i] / norm }
            }
        }

        val minClusterSize = 30
        val reps = 40
        val grid = listOf(100, 250, 400, 700)
        println("%6s %5s %9s %9s %9s".format("n", "d", "p50", "p95", "max"))
        for (n in grid) {
            val seps = (0 until reps).map { rep ->
                val rng = java.util.Random(777L + n * 7919L + rep * 104729L)
                val raw = bootstrapCloud(n, rng)
                val splitDim = splitDimFor(n)
                val pca = StatisticsUtils.pcaProject(raw, splitDim)
                val mixture = runBlocking {
                    StatisticsUtils.performVmfKMeans(
                        embeddings = pca, d = splitDim, maxK = 4,
                        minClusterFrac = minClusterSize.toDouble() / n, marginalEps = 1e-9
                    )
                } ?: return@map 0.0
                val k = mixture.components.size
                val clusters = Array(k) { mutableListOf<DoubleArray>() }
                for (i in pca.indices) {
                    val resp = mixture.responsibilities[i]
                    clusters[resp.indices.maxByOrNull { resp[it] } ?: 0].add(pca[i])
                }
                StatisticsUtils.chanceCorrectedSeparation(clusters.map { it.toList() })
            }.sorted()
            println("%6d %5d %9.5f %9.5f %9.5f".format(
                n, splitDimFor(n), seps[reps / 2], seps[(reps * 95) / 100], seps[reps - 1]))
        }
    }

    /**
     * WITHIN-DOMAIN null: the honest node-level null. A depth-1 node's population
     * is one domain's queries; bootstrapping with THAT domain's covariance asks
     * exactly the right question: "how much separation would the pipeline find in
     * this node's cloud if it had no sub-cluster structure — only its real
     * within-domain anisotropy?" The observed split separation must exceed this
     * p95 to count as evidence of genuine sub-topics.
     */
    @Test
    fun `measure within-domain null separation at real node sizes`() {
        val dbFile = java.io.File("embeddings_cache.db")
        org.junit.jupiter.api.Assumptions.assumeTrue(dbFile.exists(), "embeddings_cache.db not present")

        val byDomain = mutableMapOf<String, MutableList<DoubleArray>>()
        java.sql.DriverManager.getConnection("jdbc:sqlite:${dbFile.absolutePath}").use { conn ->
            conn.createStatement().use { stmt ->
                val cats = stmt.executeQuery(
                    "SELECT ground_truth_category, COUNT(*) FROM queries GROUP BY 1 ORDER BY 2 DESC LIMIT 20"
                )
                while (cats.next()) {
                    println("category '${cats.getString(1)}' -> ${cats.getInt(2)}")
                }
                val rs = stmt.executeQuery(
                    "SELECT LOWER(q.ground_truth_category), e.vector FROM queries q " +
                    "JOIN embeddings e ON e.query = q.distilled_text " +
                    "WHERE LOWER(q.ground_truth_category) IN ('history','engineering','business','psychology') "
                )
                while (rs.next()) {
                    val cat = rs.getString(1) ?: continue
                    val bytes = rs.getBytes(2) ?: continue
                    val buf = java.nio.ByteBuffer.wrap(bytes)
                    val full = FloatArray(bytes.size / 4) { buf.getFloat() }
                    if (full.size < 256) continue
                    val v = DoubleArray(256) { full[it].toDouble() }
                    var norm = 0.0
                    for (x in v) norm += x * x
                    norm = sqrt(norm)
                    if (norm > 0) {
                        for (i in v.indices) v[i] /= norm
                        byDomain.getOrPut(cat) { mutableListOf() }.add(v)
                    }
                }
            }
        }
        byDomain.forEach { (cat, vs) -> println("domain=$cat  m=${vs.size}") }
        org.junit.jupiter.api.Assumptions.assumeTrue(byDomain.values.any { it.size >= 200 }, "not enough domain vectors")

        val minClusterSize = 30
        val reps = 40
        val dim = 256
        println("%-14s %6s %5s %9s %9s %9s".format("domain", "n", "d", "p50", "p95", "max"))
        for ((cat, vectors) in byDomain.entries.sortedBy { it.key }) {
            val m = vectors.size
            if (m < 200) continue
            // Deduplicate exact duplicates (train/test text collisions) then bootstrap
            // at the node's own real population size.
            val n = minOf(m, 700)
            val mu = DoubleArray(dim)
            for (v in vectors) for (i in 0 until dim) mu[i] += v[i] / m
            val centered = vectors.map { v -> DoubleArray(dim) { i -> v[i] - mu[i] } }
            val invSqrtM = 1.0 / sqrt(m.toDouble())

            val seps = (0 until reps).map { rep ->
                val rng = java.util.Random(555L + cat.hashCode() + rep * 104729L)
                val cloud = (0 until n).map {
                    val out = mu.copyOf()
                    for (c in centered) {
                        val g = rng.nextGaussian() * invSqrtM
                        for (i in 0 until dim) out[i] += g * c[i]
                    }
                    var norm = 0.0
                    for (x in out) norm += x * x
                    norm = sqrt(norm)
                    DoubleArray(dim) { i -> out[i] / norm }
                }
                val splitDim = splitDimFor(n)
                val pca = StatisticsUtils.pcaProject(cloud, splitDim)
                val mixture = runBlocking {
                    StatisticsUtils.performVmfKMeans(
                        embeddings = pca, d = splitDim, maxK = 4,
                        minClusterFrac = minClusterSize.toDouble() / n, marginalEps = 1e-9
                    )
                } ?: return@map 0.0
                val k = mixture.components.size
                val clusters = Array(k) { mutableListOf<DoubleArray>() }
                for (i in pca.indices) {
                    val resp = mixture.responsibilities[i]
                    clusters[resp.indices.maxByOrNull { resp[it] } ?: 0].add(pca[i])
                }
                StatisticsUtils.chanceCorrectedSeparation(clusters.map { it.toList() })
            }.sorted()
            println("%-14s %6d %5d %9.5f %9.5f %9.5f".format(
                cat, n, splitDimFor(n), seps[reps / 2], seps[(reps * 95) / 100], seps[reps - 1]))
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // PCA-necessity study: is the split-time PCA reduction statistically load-
    // bearing, or only a speed optimization? Arm 1 measures the isotropic null
    // and wall-clock with and without pcaProject on identical clouds; arm 2
    // replays the real split-proposal path on actual snapshot node populations.
    // ─────────────────────────────────────────────────────────────────────────

    private data class ArmResult(val p50: Double, val p95: Double, val msPerFit: Double)

    private fun nullArm(n: Int, usePca: Boolean, minClusterSize: Int, reps: Int): ArmResult {
        val seps = mutableListOf<Double>()
        var totalMs = 0.0
        for (rep in 0 until reps) {
            val rng = java.util.Random(1234L + n * 7919L + rep * 104729L)  // identical clouds in both arms
            val raw = singleModeCloud(n, 256, 0.5, rng)
            val t0 = System.nanoTime()
            val (emb, d) = if (usePca) {
                val sd = splitDimFor(n)
                StatisticsUtils.pcaProject(raw, sd) to sd
            } else raw to 256
            val mixture = runBlocking {
                StatisticsUtils.performVmfKMeans(
                    embeddings = emb, d = d, maxK = 4,
                    minClusterFrac = minClusterSize.toDouble() / n, marginalEps = 1e-9
                )
            }
            totalMs += (System.nanoTime() - t0) / 1e6
            if (mixture == null) { seps.add(0.0); continue }
            val k = mixture.components.size
            val clusters = Array(k) { mutableListOf<DoubleArray>() }
            for (i in emb.indices) {
                val resp = mixture.responsibilities[i]
                clusters[resp.indices.maxByOrNull { resp[it] } ?: 0].add(emb[i])
            }
            seps.add(StatisticsUtils.chanceCorrectedSeparation(clusters.map { it.toList() }))
        }
        seps.sort()
        return ArmResult(seps[reps / 2], seps[(reps * 95) / 100], totalMs / reps)
    }

    @Test
    fun `pca necessity - isotropic null and cost with vs without pca`() {
        val minClusterSize = 30
        val reps = 40
        val grid = listOf(60, 100, 150, 250, 400, 700, 1200)
        println("%6s | %9s %9s %8s | %9s %9s %8s".format(
            "n", "pca p50", "pca p95", "ms/fit", "raw p50", "raw p95", "ms/fit"))
        for (n in grid) {
            val pca = nullArm(n, usePca = true, minClusterSize, reps)
            val raw = nullArm(n, usePca = false, minClusterSize, reps)
            println("%6d | %9.5f %9.5f %8.1f | %9.5f %9.5f %8.1f".format(
                n, pca.p50, pca.p95, pca.msPerFit, raw.p50, raw.p95, raw.msPerFit))
        }
    }

    private fun fitVmf(cluster: List<DoubleArray>, d: Int): StatisticsUtils.VmfParameters {
        if (cluster.isEmpty()) {
            val mu = FloatArray(d).apply { if (d > 0) this[0] = 1.0f }
            return StatisticsUtils.VmfParameters(mu, 1e-3, StatisticsUtils.logVmfNormalizer(d, 1e-3))
        }
        val sum = DoubleArray(d)
        for (v in cluster) for (i in 0 until d) sum[i] += v[i]
        var norm = 0.0
        for (x in sum) norm += x * x
        norm = sqrt(norm)
        val mu = FloatArray(d) { i -> if (norm > 0) (sum[i] / norm).toFloat() else 0f }
        if (norm == 0.0 && d > 0) mu[0] = 1f
        val kappa = StatisticsUtils.correctedKappa(norm / cluster.size, d, cluster.size)
        return StatisticsUtils.VmfParameters(mu, kappa, StatisticsUtils.logVmfNormalizer(d, kappa))
    }

    /** Replays the production proposal path (EM -> proposal vMFs -> routed re-assignment -> k-fallback -> gates). */
    private fun proposeSplit(vectors: List<DoubleArray>, usePca: Boolean, minClusterSize: Int, eps: Double): String {
        val n = vectors.size
        val t0 = System.nanoTime()
        val (emb, d) = if (usePca) {
            val sd = splitDimFor(n)
            StatisticsUtils.pcaProject(vectors, sd) to sd
        } else vectors to 256
        val mixture = runBlocking {
            StatisticsUtils.performVmfKMeans(
                embeddings = emb, d = d, maxK = 4,
                minClusterFrac = minClusterSize.toDouble() / n, marginalEps = eps
            )
        } ?: return "EM collapsed"
        val emK = mixture.components.size
        val emClusters = Array(emK) { mutableListOf<Int>() }
        for (i in emb.indices) {
            val resp = mixture.responsibilities[i]
            emClusters[resp.indices.maxByOrNull { resp[it] } ?: 0].add(i)
        }
        if (emClusters.any { it.size < minClusterSize }) return "EM floor reject (sizes=${emClusters.map { it.size }})"

        fun route(vmfs: List<StatisticsUtils.VmfParameters>): List<MutableList<Int>> {
            val out = List(vmfs.size) { mutableListOf<Int>() }
            for (i in vectors.indices) {
                var best = 0; var bestScore = Double.NEGATIVE_INFINITY
                for (c in vmfs.indices) {
                    val vmf = vmfs[c]
                    var dot = 0.0
                    for (j in 0 until 256) dot += vectors[i][j] * vmf.mu[j]
                    val score = vmf.logNormalizer + vmf.kappa * dot
                    if (score > bestScore) { bestScore = score; best = c }
                }
                out[best].add(i)
            }
            return out
        }

        var vmfs = emClusters.map { idx -> fitVmf(idx.map { vectors[it] }, 256) }
        var routed = route(vmfs)
        while (routed.any { it.size < minClusterSize } && routed.size > 2) {
            val survivors = routed.filter { it.size >= minClusterSize }
            if (survivors.size < 2) break
            vmfs = survivors.map { idx -> fitVmf(idx.map { vectors[it] }, 256) }
            routed = route(vmfs)
        }
        val ms = (System.nanoTime() - t0) / 1e6
        if (routed.any { it.size < minClusterSize })
            return "not routing-sustainable (sizes=${routed.map { it.size }}) [emK=$emK, %.0f ms]".format(ms)
        val sep = StatisticsUtils.chanceCorrectedSeparation(routed.map { idx -> idx.map { vectors[it] } })
        val bar = if (n < 2 * minClusterSize) 2 * eps else eps
        val verdict = if (sep >= bar) "ACCEPT" else "reject (sep < bar)"
        return "$verdict k=${routed.size} (emK=$emK) sizes=${routed.map { it.size }} sep=%.4f bar=%.3f [%.0f ms]".format(sep, bar, ms)
    }

    @Test
    fun `pca necessity - real snapshot node proposals with vs without pca`() {
        val snapDb = java.io.File("snapshots.db")
        val embDb = java.io.File("embeddings_cache.db")
        org.junit.jupiter.api.Assumptions.assumeTrue(snapDb.exists() && embDb.exists(), "DBs not present")

        val json = kotlinx.serialization.json.Json { ignoreUnknownKeys = true }
        var graph: taxonomy.service.SerializedGraph? = null
        var snapId = ""
        java.sql.DriverManager.getConnection("jdbc:sqlite:${snapDb.absolutePath}").use { conn ->
            conn.createStatement().use { stmt ->
                val rs = stmt.executeQuery("SELECT id, graph FROM snapshots ORDER BY timestamp DESC LIMIT 1")
                if (rs.next()) {
                    snapId = rs.getString(1)
                    graph = json.decodeFromString<taxonomy.service.SerializedGraph>(rs.getString(2))
                }
            }
        }
        val g = graph ?: return
        println("Snapshot: $snapId (${g.nodes.size} nodes)")

        val byLabel = g.nodes.associateBy { it.label ?: it.id }
        val targets = mutableListOf<taxonomy.service.SerialNode>()
        listOf("History", "Engineering").forEach { byLabel[it]?.let { n -> targets.add(n) } }
        // A ~100-query leaf, deterministic pick.
        g.nodes.filter { it.childIds.isEmpty() && it.queryIds.size in 80..130 }
            .minByOrNull { it.id }?.let { targets.add(it) }

        // Region population = union of subtree queryIds (an internal node's own
        // direct list is empty after its split moved the queries to children).
        val nodeById = g.nodes.associateBy { it.id }
        fun regionQueryIds(root: taxonomy.service.SerialNode): List<String> {
            val out = LinkedHashSet<String>()
            val seen = HashSet<String>()
            val stack = ArrayDeque<taxonomy.service.SerialNode>().apply { add(root) }
            while (stack.isNotEmpty()) {
                val cur = stack.removeLast()
                if (!seen.add(cur.id)) continue
                out.addAll(cur.queryIds)
                cur.childIds.forEach { nodeById[it]?.let { c -> stack.add(c) } }
            }
            return out.toList()
        }

        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}").use { conn ->
            for (node in targets) {
                // queryIds (q_<hash>) -> distilled text -> vector
                val regionIds = regionQueryIds(node)
                val vectors = mutableListOf<DoubleArray>()
                regionIds.chunked(400).forEach { chunk ->
                    val placeholders = chunk.joinToString(",") { "?" }
                    conn.prepareStatement(
                        "SELECT e.vector FROM queries q JOIN embeddings e ON e.query = q.distilled_text WHERE q.id IN ($placeholders)"
                    ).use { stmt ->
                        chunk.forEachIndexed { i, id -> stmt.setString(i + 1, id) }
                        val rs = stmt.executeQuery()
                        while (rs.next()) {
                            val bytes = rs.getBytes(1) ?: continue
                            val buf = java.nio.ByteBuffer.wrap(bytes)
                            val full = FloatArray(bytes.size / 4) { buf.getFloat() }
                            if (full.size < 256) continue
                            val v = DoubleArray(256) { full[it].toDouble() }
                            var norm = 0.0
                            for (x in v) norm += x * x
                            norm = sqrt(norm)
                            if (norm > 0) { for (i in v.indices) v[i] /= norm; vectors.add(v) }
                        }
                    }
                }
                println()
                println("Node '${node.label}' (regionQueryIds=${regionIds.size}, vectors=${vectors.size})")
                if (vectors.size < 60) { println("  too few vectors, skipping"); continue }
                println("  PCA: " + proposeSplit(vectors, usePca = true, 30, 0.02))
                println("  RAW: " + proposeSplit(vectors, usePca = false, 30, 0.02))
            }
        }
    }
}
