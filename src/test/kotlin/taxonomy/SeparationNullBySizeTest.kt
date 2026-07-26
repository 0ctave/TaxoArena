package taxonomy

import ch.qos.logback.classic.Level
import ch.qos.logback.classic.spi.ILoggingEvent
import ch.qos.logback.core.AppenderBase
import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Test
import org.slf4j.LoggerFactory
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.operations.TaxonomyFitter
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomySplitter
import taxonomy.utils.StatisticsUtils
import java.util.concurrent.ConcurrentHashMap
import kotlin.math.ceil
import kotlin.math.sqrt

/**
 * SIZE-DEPENDENCE HARNESS (measurement only, zero assertions — excluded from `test`,
 * run with `gradlew nullBySize`).
 *
 * Question: is the null distribution of the split-acceptance separation a function of
 * the node population n? If it is, a single flat `proposalSeparationBar` is
 * simultaneously too permissive at small n and too strict at large n.
 *
 * Unlike NullSeparationCalibrationTest — which measures a PROXY (EM hard assignment in
 * the PCA subspace, marginalEps disabled) — this harness drives the REAL production
 * entry point, `TaxonomySplitter.splitSingleNode`, on synthetic single-mode populations
 * that contain no cluster structure by construction. Everything the real splitter does
 * is therefore in the loop: the splitDim tiering, the k=2 probe, the maxK=4 run with
 * marginalEps = proposalSeparationBar, the EM floor, the 256-d vMF re-routing, the
 * floor-absorption and weak-pair coarsening loop, the min-pairwise gate and the k-way
 * gate. Any separation it reports is spurious by definition.
 *
 * Statistics recorded per replicate:
 *   sepKway   = node.dasguptaDeltaNorm, i.e. the chance-corrected separation of the
 *               ROUTED partition at childDim — the exact number the k-way gate compares
 *               to the bar. Uncensored: it is stored before either gate fires.
 *   sepMinPair= the min-pairwise separation, recovered from the splitter's own
 *               [NO-SPLIT] reason=min-pair log line when that gate is the binding one.
 *   accepted  = whether the whole pipeline emitted a split at the production bar.
 *
 * Replicates that never reach the gate (EM collapse / EM floor) contribute 0.0, which
 * is both the convention NullSeparationCalibrationTest used and the operationally
 * correct one: the quantity the bar has to control is the rate at which the WHOLE
 * pipeline manufactures a split from structureless data.
 */
class SeparationNullBySizeTest {

    // ── Config: canonical_freeze.toml, verbatim on every split-relevant field ─────
    private fun canonicalConfig(minClusterSize: Int = 30): TaxonomyConfig =
        TaxonomyConfig().apply {
            formalism.maxDepth = 8
            formalism.minClusterSize = minClusterSize
            formalism.proposalSeparationBar = 0.025
            formalism.tau = 1e-6
            formalism.acceptanceZ = 0.0
            formalism.enableRefitGate = false
            formalism.membershipFloor = 0.25
            formalism.routingBeamGamma = 0.2
            formalism.descentMargin = 0.12
            formalism.effectiveSupportFloor = 2.0
            formalism.defaultKappaPrior = 10.0
            formalism.maxLeafAssignments = 5
            formalism.fusionSimilarityThreshold = 0.90
            formalism.enableGtWarmStart = false
            formalism.enableResidualSplitGate = true
            formalism.enableResidualRouting = true
            formalism.enableStableQuestionIds = true
        }

    private object NoLlm : TaxonomyLlmClient {
        override suspend fun generateClusterLabel(prompt: String): String = "stub"
        override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String) = "stub"
        override suspend fun queryModelStructured(
            modelName: String, systemPrompt: String?, userPrompt: String, schema: JsonSchema
        ): String = "{}"
        override fun setMaxParallel(limit: Int) {}
    }

    // ── Null generators ──────────────────────────────────────────────────────────

    /**
     * The project's OWN null cloud, copied verbatim from
     * NullSeparationCalibrationTest.singleModeCloud so that the numbers below are
     * directly comparable with the 0.0209 the bar was calibrated against:
     * x = normalize(mu + sigma * gaussian), a single isotropic mode on the sphere.
     */
    private fun singleModeCloud(n: Int, dim: Int, sigma: Double, rng: java.util.Random): List<DoubleArray> =
        (0 until n).map {
            val v = DoubleArray(dim) { i -> (if (i == 0) 1.0 else 0.0) + sigma * rng.nextGaussian() }
            var norm = 0.0
            for (x in v) norm += x * x
            norm = sqrt(norm)
            DoubleArray(dim) { i -> v[i] / norm }
        }

    /**
     * Exact vMF(mu = e_1, kappa) sampler (Wood 1994) — the same family the external
     * simulation used, so the trend can be checked against a generator that is a vMF by
     * construction rather than vMF-like.
     */
    private fun vmfCloud(n: Int, dim: Int, kappa: Double, rng: java.util.Random): List<DoubleArray> {
        val d = dim - 1.0
        val b = d / (sqrt(4.0 * kappa * kappa + d * d) + 2.0 * kappa)
        val x0 = (1.0 - b) / (1.0 + b)
        val c = kappa * x0 + d * kotlin.math.ln(1.0 - x0 * x0)
        return (0 until n).map {
            var w: Double
            while (true) {
                val z = sampleBeta(d / 2.0, d / 2.0, rng)
                w = (1.0 - (1.0 + b) * z) / (1.0 - (1.0 - b) * z)
                val u = rng.nextDouble()
                if (kappa * w + d * kotlin.math.ln(1.0 - x0 * w) - c >= kotlin.math.ln(u)) break
            }
            // tangent direction: uniform on the sphere orthogonal to e_1
            val t = DoubleArray(dim)
            var tn = 0.0
            for (i in 1 until dim) { t[i] = rng.nextGaussian(); tn += t[i] * t[i] }
            tn = sqrt(tn)
            val s = sqrt(1.0 - w * w)
            DoubleArray(dim) { i -> if (i == 0) w else s * t[i] / tn }
        }
    }

    private fun sampleBeta(a: Double, bb: Double, rng: java.util.Random): Double {
        val x = sampleGamma(a, rng)
        val y = sampleGamma(bb, rng)
        return x / (x + y)
    }

    /** Marsaglia-Tsang gamma(shape, 1). */
    private fun sampleGamma(shape: Double, rng: java.util.Random): Double {
        if (shape < 1.0) return sampleGamma(shape + 1.0, rng) * Math.pow(rng.nextDouble(), 1.0 / shape)
        val d = shape - 1.0 / 3.0
        val c = 1.0 / sqrt(9.0 * d)
        while (true) {
            var x: Double
            var v: Double
            do { x = rng.nextGaussian(); v = 1.0 + c * x } while (v <= 0.0)
            v = v * v * v
            val u = rng.nextDouble()
            if (u < 1.0 - 0.0331 * x * x * x * x) return d * v
            if (kotlin.math.ln(u) < 0.5 * x * x + d * (1.0 - v + kotlin.math.ln(v))) return d * v
        }
    }

    // ── Log capture: the splitter reports the binding statistic only in its log ───

    private class Capture : AppenderBase<ILoggingEvent>() {
        val byLabel = ConcurrentHashMap<String, MutableList<String>>()
        /** Batch-scoped tally of messages the splitter logs WITHOUT a node label
         *  (notably "Split Floor Rejected"), attributable to n because batches are
         *  sequential even though replicates inside a batch are not. */
        val unlabelled = ConcurrentHashMap<String, java.util.concurrent.atomic.AtomicInteger>()
        private val labelRe = Regex("'([^']*)'")
        override fun append(e: ILoggingEvent) {
            val msg = e.formattedMessage ?: return
            val label = labelRe.find(msg)?.groupValues?.get(1)
            if (label == null) {
                unlabelled.computeIfAbsent(msg.substringBefore(':').take(40)) {
                    java.util.concurrent.atomic.AtomicInteger(0)
                }.incrementAndGet()
                return
            }
            byLabel.computeIfAbsent(label) { java.util.Collections.synchronizedList(mutableListOf()) }.add(msg)
        }
    }

    private data class Rep(
        val accepted: Boolean,
        val sepKway: Double,
        val sepBinding: Double,
        val reason: String,
        val emK: Int
    )

    private fun percentile(sorted: List<Double>, q: Double): Double {
        if (sorted.isEmpty()) return Double.NaN
        val rank = ceil(q * sorted.size).toInt().coerceIn(1, sorted.size)
        return sorted[rank - 1]
    }

    /**
     * Distribution-free 95% CI for a quantile from the binomial order statistics —
     * this is what says whether the replicate count is enough for the p95 to be stable.
     */
    private fun quantileCi(sorted: List<Double>, q: Double): Pair<Double, Double> {
        val r = sorted.size
        if (r < 2) return Double.NaN to Double.NaN
        val sd = sqrt(r * q * (1 - q))
        val lo = kotlin.math.floor(r * q - 1.96 * sd).toInt().coerceIn(1, r)
        val hi = ceil(r * q + 1.96 * sd).toInt().coerceIn(1, r)
        return sorted[lo - 1] to sorted[hi - 1]
    }

    // ── One replicate through the REAL splitter ──────────────────────────────────

    private suspend fun runReplicate(
        splitter: TaxonomySplitter,
        capture: Capture,
        tag: String,
        cloud: List<DoubleArray>
    ): Rep {
        val keys = ArrayList<String>(cloud.size)
        val node = GraphNode(label = tag, depth = 1)
        // kappa >= 0.5 keeps the isDiffuse branch out of the way: a real 406-query node
        // is above 10*minClusterSize anyway, and a concentrated single mode fits a high
        // kappa by construction.
        node.vmfKappa = 10.0
        cloud.forEachIndexed { i, v ->
            val key = "$tag#$i"
            keys.add(key)
            val emb = Embedding(
                rawText = key,
                distilledText = key,
                values = FloatArray(v.size) { j -> v[j].toFloat() },
                queryId = i
            )
            GraphNode.registerEmbedding(emb)
            node.queries.add(emb)
            node.queryWeights[key] = 1.0
        }
        try {
            val accepted = splitter.splitSingleNode(node)
            val lines = capture.byLabel.remove(tag) ?: emptyList<String>()
            val noSplit = lines.firstOrNull { it.startsWith("[NO-SPLIT]") }
            val splitLine = lines.firstOrNull { it.startsWith("Split '") }
            val sepKway = node.dasguptaDeltaNorm
            val reason = when {
                accepted -> "ACCEPT"
                noSplit != null -> Regex("reason=(\\S+)").find(noSplit)?.groupValues?.get(1) ?: "no-split"
                lines.any { it.startsWith("Split Failed: k-means collapsed") } -> "em-collapsed"
                lines.any { it.startsWith("Split Failed: k=2 probe") } -> "probe-insufficient"
                lines.any { it.startsWith("Split Skipped") } -> "diffuse-skip"
                lines.any { it.startsWith("Split Boundary") } -> "max-depth"
                // "Split Floor Rejected" / "Split Rejected: child too similar" carry no
                // node label, so they land in the batch-level unlabelled tally instead.
                else -> "em-floor-or-sibling"
            }
            val loggedSep = (noSplit ?: splitLine)?.let {
                Regex("sep=([0-9.]+)").find(it)?.groupValues?.get(1)?.toDoubleOrNull()
            }
            // The gate that actually binds: min-pair rejections report the min-pair
            // statistic, everything else reports/uses the k-way statistic.
            val binding = when (reason) {
                "min-pair" -> loggedSep ?: sepKway
                else -> sepKway
            }
            // The [NO-SPLIT] lines report BOTH k values since the instrumentation fix
            // (k = routed, emK = EM's proposal). Prefer emK; fall back to the bare k=
            // for the accepted-split line, which only carries EM's k.
            val emK = (noSplit ?: splitLine)?.let { line ->
                Regex("emK=(\\d+)").find(line)?.groupValues?.get(1)?.toIntOrNull()
                    ?: Regex("k=(\\d+)").find(line)?.groupValues?.get(1)?.toIntOrNull()
            } ?: 0
            return Rep(accepted, sepKway, binding, reason, emK)
        } finally {
            keys.forEach { GraphNode.EmbeddingRegistry.remove(it) }
            node.children.forEach { c -> c.queries.clear(); c.queryWeights.clear() }
            node.children.clear()
            node.queries.clear()
            node.queryWeights.clear()
        }
    }

    private fun sweep(
        title: String,
        grid: List<Int>,
        reps: Int,
        minClusterSize: Int,
        cloudOf: (n: Int, rep: Int) -> List<DoubleArray>
    ) {
        val config = canonicalConfig(minClusterSize)
        val splitter = TaxonomySplitter(config, NoLlm, MMLUDatasetFetcher(config, ""), TaxonomyFitter(config))
        val capture = Capture()
        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        capture.context = splitLog.loggerContext
        capture.start()
        // DEBUG so the pre-gate rejections (EM collapse / EM floor) are visible too.
        splitLog.level = Level.DEBUG
        splitLog.isAdditive = false
        splitLog.addAppender(capture)

        println()
        println("── $title  (reps=$reps, minClusterSize=$minClusterSize, bar=${config.formalism.proposalSeparationBar}) ──")
        println(
            "%6s %5s | %9s %9s %9s %9s | %19s | %9s | %7s %7s".format(
                "n", "d", "p50", "p90", "p95", "p99", "p95 95%CI", "bindP95", "reach%", "acc%"
            )
        )
        for (n in grid) {
            capture.unlabelled.clear()
            val reults = runBlocking {
                coroutineScope {
                    (0 until reps).map { rep ->
                        async(Dispatchers.Default) {
                            runReplicate(splitter, capture, "NULL_${minClusterSize}_${n}_$rep", cloudOf(n, rep))
                        }
                    }.awaitAll()
                }
            }
            val kway = reults.map { it.sepKway }.sorted()
            val bind = reults.map { it.sepBinding }.sorted()
            val reach = reults.count { it.sepKway > 0.0 }
            val acc = reults.count { it.accepted }
            val splitDim = when { n < 100 -> 32; n < 500 -> 64; else -> 128 }
            val ci = quantileCi(kway, 0.95)
            println(
                "%6d %5d | %9.5f %9.5f %9.5f %9.5f | [%8.5f,%8.5f] | %9.5f | %6.1f%% %6.1f%%".format(
                    java.util.Locale.US,
                    n, splitDim,
                    percentile(kway, 0.50), percentile(kway, 0.90),
                    percentile(kway, 0.95), percentile(kway, 0.99),
                    ci.first, ci.second,
                    percentile(bind, 0.95),
                    100.0 * reach / reps, 100.0 * acc / reps
                )
            )
            val reasons = reults.groupingBy { it.reason }.eachCount().entries.sortedByDescending { it.value }
            val emKs = reults.filter { it.emK > 0 }.groupingBy { it.emK }.eachCount().entries.sortedBy { it.key }
            println("        outcomes: " + reasons.joinToString(", ") { "${it.key}=${it.value}" } +
                "  | emK: " + emKs.joinToString(", ") { "k${it.key}=${it.value}" } +
                (if (capture.unlabelled.isNotEmpty())
                    "  | unlabelled: " + capture.unlabelled.entries.joinToString(", ") { "${it.key}=${it.value.get()}" }
                else ""))
        }
        splitLog.detachAppender(capture)
        capture.stop()
        splitLog.isAdditive = true
    }

    private fun reps(default: Int) = System.getProperty("nullReps")?.toIntOrNull() ?: default

    @Test
    fun `null separation as a function of node population - production splitter`() {
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val r = reps(400)
        val sigma = 0.5

        println("=".repeat(110))
        println("Driving taxonomy.operations.TaxonomySplitter.splitSingleNode on structureless clouds.")
        println("sepKway = node.dasguptaDeltaNorm (routed partition, childDim=256) — the k-way gate's statistic.")
        println("bind    = the statistic of whichever gate bound (min-pair rejections report min-pair).")
        println("reach%  = replicates whose proposal survived to the separation gates.")
        println("acc%    = replicates the FULL pipeline accepted at bar=0.025 (= null false-positive rate).")
        println("=".repeat(110))

        // n=40 cannot split at minClusterSize=30: splitSingleNode requires mass >= 2*mcs.
        //
        // Grid = the frozen tree's own split-eligible population. Its 88 leaves run
        // 30..406 (median 75, p75 111), but 32 of them sit below 2*minClusterSize=60
        // and can never be split candidates again, so the prefilter only ever sees
        // n >= 60. Points below track the dense 60..130 body of that distribution
        // (where most decisions are actually made) and thin out over the tail;
        // 500/700/900 cover internal nodes, which split at larger n than any leaf.
        sweep(
            "A. isotropic single-mode (sigma=$sigma), canonical minClusterSize=30",
            listOf(60, 75, 90, 110, 130, 160, 200, 250, 300, 350, 406, 500, 700, 900), r, 30
        ) { n, rep -> singleModeCloud(n, 256, sigma, java.util.Random(1234L + n * 7919L + rep * 104729L + (sigma * 1000).toLong())) }

        // Supplementary: n=40 is only reachable with a smaller floor. Reported separately
        // and NOT mixed into the canonical table.
        sweep(
            "B. isotropic single-mode (sigma=$sigma), minClusterSize=20 (only way to reach n=40)",
            listOf(40, 60, 100), r, 20
        ) { n, rep -> singleModeCloud(n, 256, sigma, java.util.Random(1234L + n * 7919L + rep * 104729L + (sigma * 1000).toLong())) }
    }

    @Test
    fun `null separation as a function of node population - exact vMF generator`() {
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val r = reps(200)
        // Concentration matched to the sigma=0.5 cloud through the project's own
        // estimator: fit kappa to a large sigma=0.5 sample with correctedKappa.
        val ref = singleModeCloud(4000, 256, 0.5, java.util.Random(99L))
        val sum = DoubleArray(256)
        for (v in ref) for (i in 0 until 256) sum[i] += v[i]
        var nrm = 0.0
        for (x in sum) nrm += x * x
        val kappa = StatisticsUtils.correctedKappa(sqrt(nrm) / ref.size, 256, ref.size)
        println("Matched vMF concentration: kappa=%.3f (correctedKappa on a sigma=0.5 sample)".format(java.util.Locale.US, kappa))
        sweep(
            "C. exact vMF(kappa=%.2f) generator, canonical minClusterSize=30".format(java.util.Locale.US, kappa),
            listOf(60, 100, 250, 406, 900), r, 30
        ) { n, rep -> vmfCloud(n, 256, kappa, java.util.Random(4242L + n * 7919L + rep * 104729L)) }
    }

    /**
     * Concentration sensitivity: sigma=0.5 is a very diffuse mode (rbar ~ 0.12 in 256-d).
     * If the size trend is an artefact of that particular concentration it will not
     * survive tightening the mode.
     */
    @Test
    fun `null separation vs n at several concentrations`() {
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val r = reps(200)
        for (sigma in listOf(0.15, 0.3, 1.0)) {
            sweep(
                "D. isotropic single-mode sigma=$sigma, canonical minClusterSize=30",
                listOf(100, 250, 406, 900), r, 30
            ) { n, rep ->
                singleModeCloud(n, 256, sigma, java.util.Random(1234L + n * 7919L + rep * 104729L + (sigma * 1000).toLong()))
            }
        }
    }

    // ── Frozen-snapshot access (read-only) ───────────────────────────────────────

    private fun loadGraph(snapshotId: String?): Pair<String, taxonomy.service.SerializedGraph>? {
        val snapDb = java.io.File("snapshots.db")
        if (!snapDb.exists()) return null
        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        val json = kotlinx.serialization.json.Json { ignoreUnknownKeys = true }
        java.sql.DriverManager.getConnection("jdbc:sqlite:${snapDb.absolutePath}", ro).use { conn ->
            val sql = if (snapshotId != null) "SELECT id, graph FROM snapshots WHERE id = ?"
            else "SELECT id, graph FROM snapshots ORDER BY timestamp DESC LIMIT 1"
            conn.prepareStatement(sql).use { stmt ->
                if (snapshotId != null) stmt.setString(1, snapshotId)
                val rs = stmt.executeQuery()
                if (rs.next()) return rs.getString(1) to json.decodeFromString(rs.getString(2))
            }
        }
        return null
    }

    /** Every queryId in a node's subtree — internal nodes hold none directly. */
    private fun regionQueryIds(
        root: taxonomy.service.SerialNode,
        byId: Map<String, taxonomy.service.SerialNode>
    ): Set<String> {
        val ids = LinkedHashSet<String>()
        val stack = ArrayDeque<taxonomy.service.SerialNode>().apply { add(root) }
        val seen = HashSet<String>()
        while (stack.isNotEmpty()) {
            val cur = stack.removeLast()
            if (!seen.add(cur.id)) continue
            ids.addAll(cur.queryIds)
            cur.childIds.forEach { byId[it]?.let { c -> stack.add(c) } }
        }
        return ids
    }

    private fun loadVectors(conn: java.sql.Connection, ids: Collection<String>): List<DoubleArray> {
        val out = mutableListOf<DoubleArray>()
        ids.chunked(400).forEach { chunk ->
            conn.prepareStatement(
                "SELECT e.vector FROM queries q JOIN embeddings e ON e.query = q.distilled_text " +
                    "WHERE q.id IN (${chunk.joinToString(",") { "?" }})"
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
                    if (norm > 0) { for (i in v.indices) v[i] /= norm; out.add(v) }
                }
            }
        }
        return out
    }

    /**
     * Parametric bootstrap on a node's OWN covariance: mu + C^T g / sqrt(m), then
     * renormalised to the sphere. Gaussian by construction, so every discrete
     * sub-cluster is destroyed while the node's anisotropy — its elongation — is
     * preserved exactly. This is the null that asks "more than elongation?".
     */
    private fun withinNodeCloud(
        mu: DoubleArray,
        centered: List<DoubleArray>,
        n: Int,
        rng: java.util.Random
    ): List<DoubleArray> {
        val dim = mu.size
        val invSqrtM = 1.0 / sqrt(centered.size.toDouble())
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

    /**
     * STAGE 2 — where does each ACCEPTED split fall in its own within-node null?
     *
     * The bar (0.025) sits between two nulls: the isotropic one ("is this more than
     * nothing?", p95 0.0055-0.0093) and each node's own ("is this more than that
     * node's elongation?"). J is a scatter-reduction criterion with a random-partition
     * correction, so cutting an elongated unimodal cloud along its principal axis
     * scores well above the isotropic null with no discrete structure present. Only
     * the within-node null can tell the two apart, and dJ cannot: it rewards exactly
     * the thing being mistaken for structure.
     *
     * Observed value = the node's persisted dasguptaDeltaNorm, i.e. the sepScore the
     * splitter itself computed when it accepted the split. No log parsing, no
     * recomputation, full precision.
     *
     * The null is read CONDITIONAL on reaching the separation gate, because the
     * observed value is by construction one that reached it. Replicates where EM
     * collapses score 0 and would drag the quantiles down, flattering every split.
     *
     * Read: splits below their own null p50 are consistent with anisotropy-carving —
     * a partition of continuous elongation into cells that an LLM will still label.
     */
    @Test
    fun `within-node null on every accepted split`() {
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val embDb = java.io.File("embeddings_cache.db")
        org.junit.jupiter.api.Assumptions.assumeTrue(embDb.exists(), "embeddings_cache.db not present")
        val frozen = System.getProperty("snapshotId") ?: "20260726_200711_Headless_Run_Auto_ge"
        val loaded = loadGraph(frozen) ?: loadGraph(null)
        org.junit.jupiter.api.Assumptions.assumeTrue(loaded != null, "no snapshot available")
        val (snapId, g) = loaded!!
        val byId = g.nodes.associateBy { it.id }
        val sites = g.nodes
            .filter { it.childIds.size >= 2 && it.dasguptaDeltaNorm > 0.0 }
            .sortedBy { it.dasguptaDeltaNorm }

        val r = reps(150)
        println("=".repeat(120))
        println("STAGE 2 — within-node null on every accepted split.  snapshot=$snapId")
        println("${sites.size} accepted splits (childIds>=2 and dasguptaDeltaNorm>0), reps=$r each.")
        println("null = parametric bootstrap on the node's own covariance, driven through the real splitSingleNode.")
        println("nullP50/P95 are CONDITIONAL on the replicate reaching the separation gate.")
        println("q = fraction of the conditional null BELOW the observed separation (low q = split looks like the null).")
        println("=".repeat(120))
        println(
            "%-46s %5s %5s %3s | %8s | %8s %8s | %6s | %6s".format(
                "node", "depth", "n", "k", "observed", "nullP50", "nullP95", "q", "reach%"
            )
        )

        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        val config = canonicalConfig(30)
        val splitter = TaxonomySplitter(config, NoLlm, MMLUDatasetFetcher(config, ""), TaxonomyFitter(config))
        val capture = Capture()
        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        capture.context = splitLog.loggerContext
        capture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(capture)

        data class Row(
            val label: String, val depth: Int, val n: Int, val k: Int,
            val observed: Double, val p50: Double, val p95: Double,
            val q: Double, val reach: Double
        )
        val rows = mutableListOf<Row>()

        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { conn ->
            for (site in sites) {
                val ids = regionQueryIds(site, byId)
                val vectors = loadVectors(conn, ids)
                val m = vectors.size
                val label = (site.label ?: site.id).take(45)
                if (m < 2 * 30) {
                    println("%-46s %5d %5d %3d | %8.5f | %s".format(
                        java.util.Locale.US, label, site.depth, m, site.childIds.size,
                        site.dasguptaDeltaNorm, "SKIPPED (n < 2*minClusterSize; cannot be driven)"))
                    continue
                }
                val dim = 256
                val mu = DoubleArray(dim)
                for (v in vectors) for (i in 0 until dim) mu[i] += v[i] / m
                val centered = vectors.map { v -> DoubleArray(dim) { i -> v[i] - mu[i] } }

                val results = runBlocking {
                    coroutineScope {
                        (0 until r).map { rep ->
                            async(Dispatchers.Default) {
                                val rng = java.util.Random(777L + site.id.hashCode() * 31L + rep * 104729L)
                                runReplicate(
                                    splitter, capture, "WN_${site.id}_$rep",
                                    withinNodeCloud(mu, centered, m, rng)
                                )
                            }
                        }.awaitAll()
                    }
                }
                val reached = results.filter { it.sepKway > 0.0 }.map { it.sepKway }.sorted()
                val reachPct = 100.0 * reached.size / r
                if (reached.size < 20) {
                    println("%-46s %5d %5d %3d | %8.5f | %s".format(
                        java.util.Locale.US, label, site.depth, m, site.childIds.size,
                        site.dasguptaDeltaNorm,
                        "null degenerate (only ${reached.size}/$r replicates reached the gate)"))
                    continue
                }
                val p50 = percentile(reached, 0.50)
                val p95 = percentile(reached, 0.95)
                val q = reached.count { it < site.dasguptaDeltaNorm }.toDouble() / reached.size
                rows.add(Row(label, site.depth, m, site.childIds.size, site.dasguptaDeltaNorm, p50, p95, q, reachPct))
                println(
                    "%-46s %5d %5d %3d | %8.5f | %8.5f %8.5f | %6.3f | %5.1f%%".format(
                        java.util.Locale.US, label, site.depth, m, site.childIds.size,
                        site.dasguptaDeltaNorm, p50, p95, q, reachPct
                    )
                )
            }
        }
        splitLog.detachAppender(capture); capture.stop(); splitLog.isAdditive = true

        if (rows.isEmpty()) { println("\nno usable rows"); return }
        println()
        println("=".repeat(120))
        val belowP50 = rows.count { it.observed < it.p50 }
        val belowP95 = rows.count { it.observed < it.p95 }
        println("SUMMARY over ${rows.size} accepted splits with a usable null:")
        println("  below own null p50 : %d (%.1f%%)".format(java.util.Locale.US, belowP50, 100.0 * belowP50 / rows.size))
        println("  below own null p95 : %d (%.1f%%)".format(java.util.Locale.US, belowP95, 100.0 * belowP95 / rows.size))
        println("  above own null p95 : %d (%.1f%%)".format(
            java.util.Locale.US, rows.size - belowP95, 100.0 * (rows.size - belowP95) / rows.size))
        println("  median q           : %.3f".format(java.util.Locale.US, rows.map { it.q }.sorted().let { percentile(it, 0.5) }))
        println()
        println("  by depth:")
        rows.groupBy { it.depth }.toSortedMap().forEach { (d, rs) ->
            println("    depth %d: n=%2d  below p50 %2d (%4.1f%%)  below p95 %2d (%4.1f%%)  median q %.3f".format(
                java.util.Locale.US, d, rs.size,
                rs.count { it.observed < it.p50 }, 100.0 * rs.count { it.observed < it.p50 } / rs.size,
                rs.count { it.observed < it.p95 }, 100.0 * rs.count { it.observed < it.p95 } / rs.size,
                rs.map { it.q }.sorted().let { percentile(it, 0.5) }))
        }
        println("=".repeat(120))
    }

    /**
     * FIDELITY CHECK — not a null measurement. Replays the SAME driver on the real
     * Philosophy population from the frozen snapshot. If the driver is faithful, the
     * splitter must reject it on the min-pair gate at a separation close to the 0.0209
     * the canonical run logged. Databases are opened READ-ONLY.
     */
    @Test
    fun `fidelity - replay the real Philosophy node through this driver`() {
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val snapDb = java.io.File("snapshots.db")
        val embDb = java.io.File("embeddings_cache.db")
        org.junit.jupiter.api.Assumptions.assumeTrue(snapDb.exists() && embDb.exists(), "DBs not present")
        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()

        val json = kotlinx.serialization.json.Json { ignoreUnknownKeys = true }
        var graph: taxonomy.service.SerializedGraph? = null
        var snapId = ""
        java.sql.DriverManager.getConnection("jdbc:sqlite:${snapDb.absolutePath}", ro).use { conn ->
            conn.createStatement().use { stmt ->
                val rs = stmt.executeQuery("SELECT id, graph FROM snapshots ORDER BY timestamp DESC LIMIT 1")
                if (rs.next()) { snapId = rs.getString(1); graph = json.decodeFromString(rs.getString(2)) }
            }
        }
        val g = graph ?: return
        val nodeById = g.nodes.associateBy { it.id }
        val target = g.nodes.firstOrNull { it.label == "Philosophy" } ?: run {
            println("No 'Philosophy' node in snapshot $snapId"); return
        }
        val ids = LinkedHashSet<String>()
        val stack = ArrayDeque<taxonomy.service.SerialNode>().apply { add(target) }
        val seen = HashSet<String>()
        while (stack.isNotEmpty()) {
            val cur = stack.removeLast()
            if (!seen.add(cur.id)) continue
            ids.addAll(cur.queryIds)
            cur.childIds.forEach { nodeById[it]?.let { c -> stack.add(c) } }
        }

        val vectors = mutableListOf<DoubleArray>()
        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { conn ->
            ids.chunked(400).forEach { chunk ->
                conn.prepareStatement(
                    "SELECT e.vector FROM queries q JOIN embeddings e ON e.query = q.distilled_text " +
                        "WHERE q.id IN (${chunk.joinToString(",") { "?" }})"
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
        }
        println("Snapshot $snapId — Philosophy region: ${ids.size} queryIds, ${vectors.size} vectors recovered.")
        if (vectors.size < 60) { println("too few vectors; fidelity check skipped"); return }

        val config = canonicalConfig(30)
        val splitter = TaxonomySplitter(config, NoLlm, MMLUDatasetFetcher(config, ""), TaxonomyFitter(config))
        val capture = Capture()
        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        capture.context = splitLog.loggerContext
        capture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(capture)
        val rep = runBlocking { runReplicate(splitter, capture, "PHILOSOPHY_REPLAY", vectors) }
        splitLog.detachAppender(capture); capture.stop(); splitLog.isAdditive = true
        println("Replay result: reason=${rep.reason} emK=${rep.emK} sepKway=%.5f binding=%.5f accepted=${rep.accepted}"
            .format(java.util.Locale.US, rep.sepKway, rep.sepBinding))
        println("Canonical run logged: reason=min-pair n=428 k=3 sep=0.0209 bar=0.0250")

        // ── Arm E: the WITHIN-NODE null, swept over n ────────────────────────
        // Parametric bootstrap on Philosophy's OWN embeddings: unimodal by
        // construction (all sub-cluster structure destroyed) but carrying that
        // node's real anisotropy. This is the honest null for this node, and
        // sweeping n over it answers the size question on real geometry.
        val m = vectors.size
        val dim = 256
        val mu = DoubleArray(dim)
        for (v in vectors) for (i in 0 until dim) mu[i] += v[i] / m
        val centered = vectors.map { v -> DoubleArray(dim) { i -> v[i] - mu[i] } }
        val invSqrtM = 1.0 / sqrt(m.toDouble())
        val r = reps(300)
        sweep(
            "E. within-node parametric bootstrap on Philosophy's own covariance (m=$m), minClusterSize=30",
            listOf(100, 250, 406, 900), r, 30
        ) { n, rp ->
            val rng = java.util.Random(555L + n * 7919L + rp * 104729L)
            (0 until n).map {
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
    }
}
