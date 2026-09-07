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
            val id: String, val label: String, val depth: Int, val n: Int, val k: Int,
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
                rows.add(Row(site.id, label, site.depth, m, site.childIds.size, site.dasguptaDeltaNorm, p50, p95, q, reachPct))
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

        // ── Export: per-split, and per-leaf provenance ───────────────────────────
        // The point of writing these out is that every leaf then carries the null
        // quantile of the split that FOUNDED it, so downstream analysis can report a
        // distribution instead of a caveat — and can join low-q cells against the
        // fringe/redundancy/non-recurrence findings per node rather than inferring a
        // shared cause from three separate aggregates.
        //
        // Computed offline from the frozen snapshot on purpose. Doing it inline would
        // cost reps x splitSingleNode per proposing node and would change the freeze;
        // this changes nothing and needs no re-run.
        fun esc(s: String) = "\"" + s.replace("\"", "\"\"") + "\""
        val outDir = java.io.File("docs/data").apply { mkdirs() }
        val byRowId = rows.associateBy { it.id }

        java.io.File(outDir, "within_node_null_splits.csv").printWriter().use { w ->
            w.println("snapshot_id,node_id,label,depth,n,k,observed_sep,null_p50,null_p95,q,reach_pct,reps")
            rows.sortedBy { it.q }.forEach { row ->
                w.println("${esc(snapId)},${esc(row.id)},${esc(row.label)},${row.depth},${row.n},${row.k}," +
                    "%.6f,%.6f,%.6f,%.4f,%.1f,%d".format(
                        java.util.Locale.US, row.observed, row.p50, row.p95, row.q, row.reach, r))
            }
        }

        // A leaf's founding split is the split at its tree parent. But the founding
        // split alone UNDERSTATES exposure: a low-q split high in the tree taints its
        // whole subtree without being any leaf's founding split. Computer science is
        // the case in point — 550 queries under a q=0.007 split, and not one of its
        // leaves is founded by it. So also walk the lineage and record the WORST
        // ancestor quantile, restricted to ancestors whose null was not censored
        // (reach >= 90%), since a censored q is not evidence of anything.
        fun lineage(leaf: taxonomy.service.SerialNode): List<Row> {
            val out = mutableListOf<Row>()
            var cur: taxonomy.service.SerialNode? = leaf
            val guard = HashSet<String>()
            while (cur != null && guard.add(cur.id)) {
                val pid = cur.treeParentId ?: cur.parentIds.firstOrNull() ?: break
                byRowId[pid]?.let { out.add(it) }
                cur = byId[pid]
            }
            return out
        }
        val leaves = g.nodes.filter { it.childIds.isEmpty() }
        var withProvenance = 0
        java.io.File(outDir, "within_node_null_leaves.csv").printWriter().use { w ->
            w.println("snapshot_id,leaf_id,leaf_label,leaf_n,founding_split_id,founding_split_label," +
                "founding_observed_sep,founding_null_p50,founding_q,founding_reach_pct," +
                "min_ancestor_q_clean,min_ancestor_q_clean_node,ancestor_splits_measured")
            leaves.sortedBy { it.label ?: it.id }.forEach { leaf ->
                val parentId = leaf.treeParentId ?: leaf.parentIds.firstOrNull()
                val p = parentId?.let { byRowId[it] }
                if (p != null) withProvenance++
                val anc = lineage(leaf)
                val worstClean = anc.filter { it.reach >= 90.0 }.minByOrNull { it.q }
                w.println(
                    "${esc(snapId)},${esc(leaf.id)},${esc(leaf.label ?: "")}," +
                        "${regionQueryIds(leaf, byId).size},${esc(parentId ?: "")}," +
                        "${esc(p?.label ?: "")}," +
                        (if (p != null) "%.6f,%.6f,%.4f,%.1f,".format(
                            java.util.Locale.US, p.observed, p.p50, p.q, p.reach)
                        else ",,,,") +
                        (if (worstClean != null) "%.4f,${esc(worstClean.label)},".format(
                            java.util.Locale.US, worstClean.q)
                        else ",,") +
                        "${anc.size}"
                )
            }
        }
        println()
        println("wrote docs/data/within_node_null_splits.csv  (${rows.size} splits)")
        println("wrote docs/data/within_node_null_leaves.csv  (${leaves.size} leaves, " +
            "$withProvenance with a founding-split null)")

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
     * PHILOSOPHY: is the single leaf a property of the 256-dim MRL slice, or of the
     * corpus?
     *
     * Every other depth-1 domain splits, so the embedding resolves sub-topics in
     * general. Two candidate explanations for Philosophy, with different implications:
     * either MMLU-Pro's philosophy questions are genuinely uniform, or the 256-slice
     * discards the conceptual axes that would separate them.
     *
     * The naive version of this test — cluster at the full 4096 dims — is worse, not
     * better: d/n = 10.1 at n=406, against 0.63 for the slice, and vMF concentration
     * estimation degrades badly in that regime. PCA-from-full to 64 is the version
     * that isolates "did slicing lose signal" from "is high dimension harder", because
     * it keeps the top-variance directions of the WHOLE space rather than the first
     * 256 coordinates.
     *
     * The yardstick is held fixed. PCA-from-full is used only to FIND the partition;
     * both partitions are then scored with chanceCorrectedSeparation on the same
     * 256-slice vectors. Scoring each in its own space would compare two different
     * quantities and prove nothing — the mistake the superseded calibration harness
     * made, which is how a 3x statistic mismatch reached a config header.
     */
    @Test
    fun `Philosophy - does the 256 slice lose a seam that PCA from full would find`() {
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val embDb = java.io.File("embeddings_cache.db")
        org.junit.jupiter.api.Assumptions.assumeTrue(embDb.exists(), "embeddings_cache.db not present")
        val frozen = System.getProperty("snapshotId") ?: "20260726_200711_Headless_Run_Auto_ge"
        val loaded = loadGraph(frozen) ?: loadGraph(null)
        org.junit.jupiter.api.Assumptions.assumeTrue(loaded != null, "no snapshot available")
        val (snapId, g) = loaded!!
        val byId = g.nodes.associateBy { it.id }
        val target = g.nodes.firstOrNull { it.label == "Philosophy" } ?: run {
            println("no Philosophy node in $snapId"); return
        }
        val ids = regionQueryIds(target, byId)

        // FULL vectors, not the 256 slice.
        val full = mutableListOf<DoubleArray>()
        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { conn ->
            ids.chunked(400).forEach { chunk ->
                conn.prepareStatement(
                    "SELECT e.vector FROM queries q JOIN embeddings e ON e.query = q.distilled_text " +
                        "WHERE q.id IN (${chunk.joinToString(",") { "?" }})"
                ).use { st ->
                    chunk.forEachIndexed { i, id -> st.setString(i + 1, id) }
                    val rs = st.executeQuery()
                    while (rs.next()) {
                        val bytes = rs.getBytes(1) ?: continue
                        val buf = java.nio.ByteBuffer.wrap(bytes)
                        val v = DoubleArray(bytes.size / 4) { buf.getFloat().toDouble() }
                        var nrm = 0.0; for (x in v) nrm += x * x; nrm = sqrt(nrm)
                        if (nrm > 0) { for (i in v.indices) v[i] /= nrm; full.add(v) }
                    }
                }
            }
        }
        if (full.size < 60) { println("only ${full.size} vectors recovered; skipped"); return }
        val d = full[0].size
        val n = full.size

        // The production geometry: first 256 coordinates, renormalised — what
        // Embedding.projectTo(256) yields.
        val slice = full.map { v ->
            val s = DoubleArray(256) { v[it] }
            var nrm = 0.0; for (x in s) nrm += x * x; nrm = sqrt(nrm)
            if (nrm > 0) for (i in s.indices) s[i] /= nrm
            s
        }

        val config = canonicalConfig(30)
        val minClusterSize = config.formalism.minClusterSize
        val frac = minClusterSize.toDouble() / n
        val eps = config.formalism.proposalSeparationBar

        fun partitionFrom(proposalSpace: List<DoubleArray>, pcaDim: Int): List<List<Int>>? {
            val projected = StatisticsUtils.pcaProject(proposalSpace, pcaDim)
            val mix = runBlocking {
                StatisticsUtils.performVmfKMeans(
                    embeddings = projected, d = pcaDim, maxK = 4,
                    minClusterFrac = frac, marginalEps = eps
                )
            } ?: return null
            val k = mix.components.size
            val out = List(k) { mutableListOf<Int>() }
            for (i in 0 until n) {
                val r = mix.responsibilities[i]
                out[r.indices.maxByOrNull { r[it] } ?: 0].add(i)
            }
            return out
        }

        fun scoreOnSlice(part: List<List<Int>>): Double =
            StatisticsUtils.chanceCorrectedSeparation(part.map { idx -> idx.map { slice[it] } })

        println("=".repeat(104))
        println("PHILOSOPHY slice-vs-full test — snapshot=$snapId")
        println("n=$n queries, stored dim=$d, production slice=256 (d/n=%.2f), full d/n=%.1f"
            .format(java.util.Locale.US, 256.0 / n, d.toDouble() / n))
        println("Both partitions scored identically: chanceCorrectedSeparation on the 256-slice vectors.")
        println("Reference: Philosophy's own within-node null at n=406 — p50 0.0396, p95 0.0452;")
        println("           the canonical run logged sep=0.0208 and refused the split at bar=$eps.")
        println("=".repeat(104))
        println("%-34s %4s %-22s %10s %10s".format("proposal space", "k", "cluster sizes", "sep(slice)", "verdict"))

        for ((name, space) in listOf("A. 256 MRL slice (production)" to slice, "B. PCA-64 from full $d-dim" to full)) {
            val part = partitionFrom(space, 64)
            if (part == null) { println("%-34s   -  EM collapsed".format(name)); continue }
            val sizes = part.map { it.size }
            val sep = scoreOnSlice(part)
            val viable = sizes.all { it >= minClusterSize }
            println("%-34s %4d %-22s %10.5f %10s".format(
                java.util.Locale.US, name, part.size, sizes.joinToString(","), sep,
                if (!viable) "below floor" else if (sep >= eps) "clears bar" else "below bar"))
        }
        // ── Like-for-like null for arm B ────────────────────────────────────
        // Arm B's score cannot be read against arm A's null. A search over a richer
        // proposal space finds more separation on STRUCTURELESS data too, so the
        // comparison needs B's own procedure run on unimodal clouds carrying
        // Philosophy's full-space covariance. Without this the result would be
        // exactly the error this file exists to document: a number compared against
        // a null measured on a different statistic.
        val reps = reps(60)
        val mu = DoubleArray(d)
        for (v in full) for (i in 0 until d) mu[i] += v[i] / n
        val centered = full.map { v -> DoubleArray(d) { i -> v[i] - mu[i] } }
        println()
        println("Like-for-like null for arm B: within-node bootstrap on the FULL $d-dim covariance,")
        println("clustered by arm B's own procedure, scored on the 256 slice. reps=$reps")
        val nullSeps = runBlocking {
            coroutineScope {
                (0 until reps).map { rep ->
                    async(Dispatchers.Default) {
                        val rng = java.util.Random(4242L + rep * 104729L)
                        val cloud = withinNodeCloud(mu, centered, n, rng)
                        val cSlice = cloud.map { v ->
                            val s = DoubleArray(256) { v[it] }
                            var nrm = 0.0; for (x in s) nrm += x * x; nrm = sqrt(nrm)
                            if (nrm > 0) for (i in s.indices) s[i] /= nrm
                            s
                        }
                        val proj = StatisticsUtils.pcaProject(cloud, 64)
                        val mix = StatisticsUtils.performVmfKMeans(
                            embeddings = proj, d = 64, maxK = 4,
                            minClusterFrac = frac, marginalEps = eps
                        ) ?: return@async 0.0
                        val k = mix.components.size
                        val part = List(k) { mutableListOf<Int>() }
                        for (i in 0 until n) {
                            val r = mix.responsibilities[i]
                            part[r.indices.maxByOrNull { r[it] } ?: 0].add(i)
                        }
                        StatisticsUtils.chanceCorrectedSeparation(part.map { idx -> idx.map { cSlice[it] } })
                    }
                }.awaitAll()
            }
        }
        val reached = nullSeps.filter { it > 0.0 }.sorted()
        if (reached.size < 10) {
            println("null degenerate (${reached.size}/$reps reached the gate)")
        } else {
            val p50 = percentile(reached, 0.50); val p95 = percentile(reached, 0.95)
            val p99 = percentile(reached, 0.99)
            println("arm B null (n=%d, reach %d/%d): p50=%.5f  p95=%.5f  p99=%.5f".format(
                java.util.Locale.US, n, reached.size, reps, p50, p95, p99))
            val obsB = partitionFrom(full, 64)?.let { scoreOnSlice(it) } ?: Double.NaN
            val below = reached.count { it < obsB }
            val nr = reached.size
            val q = below.toDouble() / nr
            // Wilson score interval — correct near q=0/1 where the Wald interval is not.
            val z = 1.96
            val den = 1.0 + z * z / nr
            val centre = (q + z * z / (2.0 * nr)) / den
            val half = z * sqrt(q * (1 - q) / nr + z * z / (4.0 * nr * nr)) / den
            println("arm B observed = %.5f  ->  q = %.3f  (%d/%d below)".format(
                java.util.Locale.US, obsB, q, below, nr))
            println("  Wilson 95%% CI on q: [%.3f, %.3f]".format(
                java.util.Locale.US, (centre - half).coerceAtLeast(0.0), (centre + half).coerceAtMost(1.0)))
            println("  CAVEAT: this null bootstraps the empirical covariance of $n points in $d dims, so its")
            println("  rank is <= ${n - 1} and every draw lies exactly in the span of the observations. It inherits")
            println("  the data's own subspace structure and is conservative (biased HIGH). The 256-slice null")
            println("  is full-rank (256 < ${n - 1}) and the two nulls are NOT directly comparable.")
            println(if (q >= 0.95)
                "  => the PCA-from-full partition beats what its own search finds on structureless data."
            else
                "  => NOT distinguishable from what the richer search manufactures on noise.")
        }
        println("=".repeat(104))
        println("Read: if B's separation is materially above A's AND above B's own null, the 256-slice")
        println("      was discarding the seam. If B only beats A, the richer search is finding noise.")
    }

    // ── TASK 1 + 2: disentangle marginalEps from the proposal subspace ───────────

    /** Plain line-collector for the "taxonomy.Statistics" k-selection trace. */
    private class LineCapture : AppenderBase<ILoggingEvent>() {
        val lines = java.util.Collections.synchronizedList(mutableListOf<String>())
        override fun append(e: ILoggingEvent) { e.formattedMessage?.let { lines.add(it) } }
        fun drain(): List<String> { val c = lines.toList(); lines.clear(); return c }
    }

    /** Full 4096-d unit vectors for a node's subtree, from embeddings_cache.db. */
    private fun loadFullVectors(conn: java.sql.Connection, ids: Collection<String>): List<DoubleArray> {
        val out = mutableListOf<DoubleArray>()
        ids.chunked(400).forEach { chunk ->
            conn.prepareStatement(
                "SELECT e.vector FROM queries q JOIN embeddings e ON e.query = q.distilled_text " +
                    "WHERE q.id IN (${chunk.joinToString(",") { "?" }})"
            ).use { st ->
                chunk.forEachIndexed { i, id -> st.setString(i + 1, id) }
                val rs = st.executeQuery()
                while (rs.next()) {
                    val bytes = rs.getBytes(1) ?: continue
                    val buf = java.nio.ByteBuffer.wrap(bytes)
                    val v = DoubleArray(bytes.size / 4) { buf.getFloat().toDouble() }
                    var nrm = 0.0; for (x in v) nrm += x * x; nrm = sqrt(nrm)
                    if (nrm > 0) { for (i in v.indices) v[i] /= nrm; out.add(v) }
                }
            }
        }
        return out
    }

    private fun sliceOf(full: List<DoubleArray>): List<DoubleArray> = full.map { v ->
        val s = DoubleArray(256) { v[it] }
        var nrm = 0.0; for (x in s) nrm += x * x; nrm = sqrt(nrm)
        if (nrm > 0) for (i in s.indices) s[i] /= nrm
        s
    }

    private data class Arm(val k: Int, val sizes: List<Int>, val sep: Double, val trace: List<String>)

    /**
     * Propose a partition in [proposalSpace] (PCA-reduced to [pcaDim]) and score it on
     * the FIXED yardstick [yardstick] with chanceCorrectedSeparation.
     * maxK / marginalEps are exposed so the k-selection rule can be neutralised.
     */
    private fun armOn(
        proposalSpace: List<DoubleArray>,
        yardstick: List<DoubleArray>,
        pcaDim: Int,
        maxK: Int,
        marginalEps: Double,
        minClusterFrac: Double,
        cap: LineCapture
    ): Arm? {
        cap.drain()
        val n = proposalSpace.size
        val projected = StatisticsUtils.pcaProject(proposalSpace, pcaDim)
        val mix = runBlocking {
            StatisticsUtils.performVmfKMeans(
                embeddings = projected, d = pcaDim, maxK = maxK,
                minClusterFrac = minClusterFrac, marginalEps = marginalEps
            )
        } ?: return null
        val k = mix.components.size
        val part = List(k) { mutableListOf<Int>() }
        for (i in 0 until n) {
            val r = mix.responsibilities[i]
            part[r.indices.maxByOrNull { r[it] } ?: 0].add(i)
        }
        val sep = StatisticsUtils.chanceCorrectedSeparation(part.map { idx -> idx.map { yardstick[it] } })
        return Arm(k, part.map { it.size }, sep, cap.drain().filter { it.startsWith("k-Means") })
    }

    /**
     * TASK 1 + TASK 2.
     *
     * Arm A (256-slice proposal) and arm B (PCA-64-from-full proposal) differ in TWO
     * ways at once: the subspace they search, and the k that performVmfKMeans ends up
     * selecting (2 vs 3), because the k increment is gated by marginalEps =
     * proposalSeparationBar = 0.025. This separates the two: arm A is re-run with the
     * k-gate neutralised (marginalEps = 0.0, and again forced to k=3), scored on the
     * same fixed 256-slice yardstick.
     *
     * Run over Philosophy AND the five other largest leaves of the frozen tree, chosen
     * programmatically by subtree query count, so the answer is not a Philosophy
     * anecdote.
     */
    @Test
    fun `slice vs full seam on the largest leaves - marginalEps disentangled`() {
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val embDb = java.io.File("embeddings_cache.db")
        org.junit.jupiter.api.Assumptions.assumeTrue(embDb.exists(), "embeddings_cache.db not present")
        val frozen = System.getProperty("snapshotId") ?: "20260726_200711_Headless_Run_Auto_ge"
        val loaded = loadGraph(frozen) ?: loadGraph(null)
        org.junit.jupiter.api.Assumptions.assumeTrue(loaded != null, "no snapshot available")
        val (snapId, g) = loaded!!
        val byId = g.nodes.associateBy { it.id }

        // Largest LEAVES by subtree query count, selected programmatically.
        val leaves = g.nodes.filter { it.childIds.isEmpty() }
            .map { it to regionQueryIds(it, byId) }
            .sortedByDescending { it.second.size }
        val philosophy = leaves.firstOrNull { it.first.label == "Philosophy" }
        val top = (listOfNotNull(philosophy) + leaves.filter { it.first.label != "Philosophy" }.take(5))

        val config = canonicalConfig(30)
        val minClusterSize = config.formalism.minClusterSize
        val eps = config.formalism.proposalSeparationBar

        val statsLog = LoggerFactory.getLogger("taxonomy.Statistics") as ch.qos.logback.classic.Logger
        val cap = LineCapture()
        cap.context = statsLog.loggerContext
        cap.start(); statsLog.level = Level.DEBUG; statsLog.isAdditive = false; statsLog.addAppender(cap)

        println("=".repeat(132))
        println("SLICE-vs-FULL on the ${top.size} largest leaves — snapshot=$snapId")
        println("Every sep below is chanceCorrectedSeparation on the SAME 256-slice vectors. Only the PROPOSAL differs.")
        println("A     = propose from the 256 MRL slice, PCA-64, maxK=4, marginalEps=$eps  (production)")
        println("A(e0) = same, marginalEps=0.0            — k-gate neutralised, subspace unchanged")
        println("A(k3) = same, maxK=3, marginalEps=-1e9   — k=3 forced, subspace unchanged")
        println("B     = propose from PCA-64 of the FULL 4096-dim vectors, maxK=4, marginalEps=$eps")
        println("B(k3) = same, maxK=3, marginalEps=-1e9")
        println("=".repeat(132))
        println("%-40s %5s | %2s %9s | %2s %9s | %2s %9s | %2s %9s | %2s %9s".format(
            "leaf", "n", "k", "A", "k", "A(e0)", "k", "A(k3)", "k", "B", "k", "B(k3)"))

        val traces = mutableListOf<String>()
        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { conn ->
            for ((node, ids) in top) {
                val full = loadFullVectors(conn, ids)
                if (full.size < 2 * minClusterSize) {
                    println("%-40s %5d | too few vectors (${full.size})".format(
                        java.util.Locale.US, (node.label ?: node.id).take(40), ids.size))
                    continue
                }
                val slice = sliceOf(full)
                val frac = minClusterSize.toDouble() / full.size

                val a = armOn(slice, slice, 64, 4, eps, frac, cap)
                val a0 = armOn(slice, slice, 64, 4, 0.0, frac, cap)
                val a3 = armOn(slice, slice, 64, 3, -1e9, frac, cap)
                val b = armOn(full, slice, 64, 4, eps, frac, cap)
                val b3 = armOn(full, slice, 64, 3, -1e9, frac, cap)

                fun f(x: Arm?) = if (x == null) " -        -" else "%2d %9.5f".format(java.util.Locale.US, x.k, x.sep)
                println("%-40s %5d | %s | %s | %s | %s | %s".format(
                    java.util.Locale.US, (node.label ?: node.id).take(40), full.size,
                    f(a), f(a0), f(a3), f(b), f(b3)))

                val lbl = (node.label ?: node.id).take(40)
                traces.add("── $lbl (n=${full.size}) ──")
                traces.add("  A     sizes=${a?.sizes}  " + (a?.trace ?: emptyList<String>()).joinToString(" | "))
                traces.add("  A(e0) sizes=${a0?.sizes}  " + (a0?.trace ?: emptyList<String>()).joinToString(" | "))
                traces.add("  A(k3) sizes=${a3?.sizes}  " + (a3?.trace ?: emptyList<String>()).joinToString(" | "))
                traces.add("  B     sizes=${b?.sizes}  " + (b?.trace ?: emptyList<String>()).joinToString(" | "))
                traces.add("  B(k3) sizes=${b3?.sizes}  " + (b3?.trace ?: emptyList<String>()).joinToString(" | "))
            }
        }
        statsLog.detachAppender(cap); cap.stop(); statsLog.isAdditive = true

        println()
        println("k-SELECTION TRACES (separations inside the trace are in the PCA-64 PROPOSAL space,")
        println("which is where the marginalEps test is applied — NOT the 256-slice yardstick above).")
        traces.forEach { println(it) }
        println("=".repeat(132))
    }

    /**
     * VALIDITY CHECK for the table above. The armOn() numbers are the raw
     * chanceCorrectedSeparation of EM's hard assignment in the PROPOSAL population.
     * The quantity the production gate compares to the bar is the ROUTED partition's
     * dasguptaDeltaNorm at childDim=256, after the EM floor, the floor-absorption and
     * weak-pair coarsening loop, and the min-pairwise gate. If arm A reports 0.05 for a
     * node that is nevertheless a LEAF in the frozen tree, then it is those later stages
     * — not the proposal separation — that refused the split, and the arm A/arm B
     * comparison is about proposal quality only. This drives the real splitSingleNode
     * on the same six populations to establish which.
     */
    @Test
    fun `why are the largest leaves leaves - real splitter on each`() {
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val embDb = java.io.File("embeddings_cache.db")
        org.junit.jupiter.api.Assumptions.assumeTrue(embDb.exists(), "embeddings_cache.db not present")
        val frozen = System.getProperty("snapshotId") ?: "20260726_200711_Headless_Run_Auto_ge"
        val loaded = loadGraph(frozen) ?: loadGraph(null)
        org.junit.jupiter.api.Assumptions.assumeTrue(loaded != null, "no snapshot available")
        val (snapId, g) = loaded!!
        val byId = g.nodes.associateBy { it.id }
        val leaves = g.nodes.filter { it.childIds.isEmpty() }
            .map { it to regionQueryIds(it, byId) }
            .sortedByDescending { it.second.size }
        val philosophy = leaves.firstOrNull { it.first.label == "Philosophy" }
        val top = (listOfNotNull(philosophy) + leaves.filter { it.first.label != "Philosophy" }.take(5))

        val config = canonicalConfig(30)
        val splitter = TaxonomySplitter(config, NoLlm, MMLUDatasetFetcher(config, ""), TaxonomyFitter(config))
        val capture = Capture()
        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        capture.context = splitLog.loggerContext
        capture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(capture)

        println("=".repeat(120))
        println("REAL splitSingleNode on the ${top.size} largest leaves — snapshot=$snapId")
        println("sepKway = routed dasguptaDeltaNorm at childDim=256 (the gate's own statistic).")
        println("=".repeat(120))
        println("%-42s %5s %5s %4s %-18s %9s %9s".format(
            "leaf", "depth", "n", "emK", "reason", "sepKway", "binding"))
        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { conn ->
            for ((node, ids) in top) {
                val vectors = loadVectors(conn, ids)
                if (vectors.size < 2 * config.formalism.minClusterSize) continue
                val rep = runBlocking {
                    runReplicate(splitter, capture, "LEAFCHK_${node.id}", vectors)
                }
                println("%-42s %5d %5d %4d %-18s %9.5f %9.5f".format(
                    java.util.Locale.US, (node.label ?: node.id).take(42), node.depth,
                    vectors.size, rep.emK, rep.reason, rep.sepKway, rep.sepBinding))
            }
        }
        splitLog.detachAppender(capture); capture.stop(); splitLog.isAdditive = true
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

    // ── withinNull: the within-node null RE-DERIVED on the frozen mcs=55 artifact ─

    /**
     * Loader for the FROZEN artifact. Prefers the tracked `snapshots_frozen.db`
     * extract (16 MB, in every clone) over the full local-only `snapshots.db`, and —
     * unlike [loadGraph] — never falls back to "latest": an audit harness that
     * silently measured a different tree would be worse than one that refused to run.
     */
    private fun loadFrozenGraph(snapshotId: String): Pair<String, taxonomy.service.SerializedGraph>? {
        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        val json = kotlinx.serialization.json.Json { ignoreUnknownKeys = true }
        for (name in listOf("snapshots_frozen.db", "snapshots.db")) {
            val db = java.io.File(name)
            if (!db.exists()) continue
            java.sql.DriverManager.getConnection("jdbc:sqlite:${db.absolutePath}", ro).use { conn ->
                conn.prepareStatement("SELECT id, graph FROM snapshots WHERE id = ?").use { stmt ->
                    stmt.setString(1, snapshotId)
                    val rs = stmt.executeQuery()
                    if (rs.next()) return rs.getString(1) to json.decodeFromString(rs.getString(2))
                }
            }
        }
        return null
    }

    /**
     * WITHIN-NODE NULL ON THE FROZEN mcs=55 ARTIFACT (`gradlew withinNull`).
     *
     * Closes construction-audit risk #1: the within-node null values in
     * docs/separation_null_by_size.md were measured pre-freeze on the superseded
     * 88-leaf mcs=30 tree and are VOID as to values. This re-derives them against
     * snapshot 20260727_042523 (154 nodes / 87 leaves / 14 depth-1 anchors,
     * minClusterSize=55) with the METHOD that survived:
     *
     *   Null model (unchanged from the voided run, labelled explicitly): parametric
     *   bootstrap on the anchor's OWN empirical covariance — x = normalize(mu + C^T g),
     *   where C's rows are the centered observations scaled by 1/sqrt(m) and g ~ N(0, I_m).
     *   Draws are Gaussian with exactly the node's mean and covariance (all per-PC
     *   variances preserved, every discrete sub-cluster destroyed), then projected to
     *   the sphere. "Texture but no sub-topics."
     *
     *   Statistic: the PRODUCTION splitter's own — each replicate cloud is driven
     *   through the real `splitSingleNode` at the frozen config (minClusterSize=55,
     *   bar=0.025) and `node.dasguptaDeltaNorm` is recorded UNCENSORED (it is stored
     *   before either separation gate fires), exactly as the isotropic `nullBySize`
     *   arms measure it. acceptanceZ stays 0.0 because the z-gate lives in
     *   TaxonomyOperations' edit acceptance, outside `splitSingleNode`; it cannot
     *   censor the statistic measured here. Replicates that never reach the gate
     *   contribute 0.0 (the file-wide convention).
     *
     * Stage 2 evaluates every accepted split of the frozen tree against its depth-1
     * anchor's null: q = fraction of ALL null replicates >= the split's persisted
     * dasguptaDeltaNorm. For the 14 depth-1 splits this is an EXACTLY matched
     * comparison (same population, same n, same covariance as the null). For deeper
     * sites it is approximate in a known direction: the null narrows with n, so the
     * larger-n anchor null is ANTI-conservative for smaller descendant sites (their
     * own null would be wider). Site-level nulls remain a per-site re-run of the
     * stage-2 harness above with -DsnapshotId set to the frozen id.
     */
    @Test
    fun `withinNull - anisotropy-preserving null per frozen depth-1 anchor`() {
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val embDb = java.io.File("embeddings_cache.db")
        org.junit.jupiter.api.Assumptions.assumeTrue(embDb.exists(), "embeddings_cache.db not present")
        val frozen = System.getProperty("snapshotId") ?: "20260727_042523_Headless_Run_Auto_ge"
        val loaded = loadFrozenGraph(frozen)
        org.junit.jupiter.api.Assumptions.assumeTrue(loaded != null, "frozen snapshot $frozen not available")
        val (snapId, g) = loaded!!
        val byId = g.nodes.associateBy { it.id }
        val anchors = g.nodes.filter { it.depth == 1 }
            .map { it to regionQueryIds(it, byId) }
            .sortedByDescending { it.second.size }
        val r = reps(300)
        val mcs = 55

        val config = canonicalConfig(mcs)
        val splitter = TaxonomySplitter(config, NoLlm, MMLUDatasetFetcher(config, ""), TaxonomyFitter(config))
        val capture = Capture()
        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        capture.context = splitLog.loggerContext
        capture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(capture)

        println("=".repeat(120))
        println("WITHIN-NODE NULL — FROZEN ARTIFACT.  snapshot=$snapId  minClusterSize=$mcs  bar=${config.formalism.proposalSeparationBar}")
        println("${anchors.size} depth-1 anchors, reps=$r each. Null = anisotropy-preserving parametric bootstrap")
        println("(Gaussian moment-matched to the anchor's own mean/covariance, projected to the sphere),")
        println("driven through the real splitSingleNode. Quantiles UNCONDITIONAL (non-reached replicates score 0).")
        println("=".repeat(120))
        println(
            "%-18s %5s | %9s %9s %9s %9s | %19s | %9s | %7s %6s".format(
                "anchor", "n", "p50", "p90", "p95", "p99", "p95 95%CI", "condP95", "reach%", "acc%"
            )
        )

        class AnchorNull(
            val label: String, val n: Int,
            val all: List<Double>, val reached: List<Double>, val accepted: Int
        )
        val nulls = LinkedHashMap<String, AnchorNull>()

        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { conn ->
            for ((anchor, ids) in anchors) {
                val vectors = loadVectors(conn, ids)
                // Cache-only, hard-fail: this harness must never fall back to Ollama
                // or silently measure a subset of the frozen population.
                check(vectors.size == ids.size) {
                    "embedding cache miss for '${anchor.label}': ${vectors.size}/${ids.size} vectors recovered"
                }
                val m = vectors.size
                val dim = 256
                val mu = DoubleArray(dim)
                for (v in vectors) for (i in 0 until dim) mu[i] += v[i] / m
                val centered = vectors.map { v -> DoubleArray(dim) { i -> v[i] - mu[i] } }

                val results = runBlocking {
                    coroutineScope {
                        (0 until r).map { rep ->
                            async(Dispatchers.Default) {
                                val rng = java.util.Random(
                                    20260907L + anchor.id.hashCode().toLong() * 2654435761L + rep * 104729L
                                )
                                runReplicate(
                                    splitter, capture, "WNF_${anchor.id}_$rep",
                                    withinNodeCloud(mu, centered, m, rng)
                                )
                            }
                        }.awaitAll()
                    }
                }
                val all = results.map { it.sepKway }.sorted()
                val reached = all.filter { it > 0.0 }
                val acc = results.count { it.accepted }
                nulls[anchor.id] = AnchorNull(anchor.label ?: anchor.id, m, all, reached, acc)
                val ci = quantileCi(all, 0.95)
                println(
                    "%-18s %5d | %9.5f %9.5f %9.5f %9.5f | [%8.5f,%8.5f] | %9.5f | %6.1f%% %5.1f%%".format(
                        java.util.Locale.US, (anchor.label ?: anchor.id).take(18), m,
                        percentile(all, 0.50), percentile(all, 0.90), percentile(all, 0.95), percentile(all, 0.99),
                        ci.first, ci.second,
                        if (reached.size >= 20) percentile(reached, 0.95) else Double.NaN,
                        100.0 * reached.size / r, 100.0 * acc / r
                    )
                )
            }
        }
        splitLog.detachAppender(capture); capture.stop(); splitLog.isAdditive = true

        // ── Stage 2: every accepted split of the frozen tree vs its anchor's null ──
        fun anchorIdOf(node: taxonomy.service.SerialNode): String? {
            var cur: taxonomy.service.SerialNode? = node
            val guard = HashSet<String>()
            while (cur != null && guard.add(cur.id)) {
                if (cur.depth == 1) return cur.id
                // treeParentId can dangle (parent removed by a later coarsening); fall
                // back to the first RESOLVABLE parent id rather than the first id.
                cur = (listOfNotNull(cur.treeParentId) + cur.parentIds).firstNotNullOfOrNull { byId[it] }
            }
            return null
        }
        val sites = g.nodes.filter { it.childIds.size >= 2 && it.dasguptaDeltaNorm > 0.0 }
            .sortedWith(compareBy({ it.depth }, { -(regionQueryIds(it, byId).size) }))

        println()
        println("=".repeat(120))
        println("ACCEPTED SPLITS vs THEIR ANCHOR'S WITHIN-NODE NULL  (q = fraction of ALL null replicates >= observed)")
        println("depth-1 rows are exactly matched (own population = null population); deeper rows use the anchor null,")
        println("which narrows with n and is therefore ANTI-conservative for smaller descendant sites.")
        println("=".repeat(120))
        println(
            "%-46s %5s %5s %3s | %8s | %-16s %8s %8s | %6s %s".format(
                "split site", "depth", "n", "k", "observed", "anchor", "nullP50", "nullP95", "q", "vs p95"
            )
        )

        data class SiteRow(
            val id: String, val label: String, val depth: Int, val n: Int, val k: Int,
            val observed: Double, val anchorId: String, val anchorLabel: String,
            val nullP50: Double, val nullP95: Double, val q: Double, val clears: Boolean
        )
        val rows = mutableListOf<SiteRow>()
        for (site in sites) {
            val aId = anchorIdOf(site)
            val an = aId?.let { nulls[it] }
            if (an == null) {
                println("%-46s %5d  (no depth-1 anchor null — skipped)".format((site.label ?: site.id).take(46), site.depth))
                continue
            }
            val n = regionQueryIds(site, byId).size
            val obs = site.dasguptaDeltaNorm
            val q = an.all.count { it >= obs }.toDouble() / an.all.size
            val p50 = percentile(an.all, 0.50)
            val p95 = percentile(an.all, 0.95)
            val clears = obs >= p95
            rows.add(SiteRow(site.id, site.label ?: site.id, site.depth, n, site.childIds.size,
                obs, aId, an.label, p50, p95, q, clears))
            println(
                "%-46s %5d %5d %3d | %8.5f | %-16s %8.5f %8.5f | %6.3f %s".format(
                    java.util.Locale.US, (site.label ?: site.id).take(46), site.depth, n, site.childIds.size,
                    obs, an.label.take(16), p50, p95, q,
                    if (clears) "CLEARS" else "below"
                )
            )
        }

        println()
        println("=".repeat(120))
        val d1 = rows.filter { it.depth == 1 }
        val deeper = rows.filter { it.depth > 1 }
        println("SUMMARY  (snapshot=$snapId, reps=$r, minClusterSize=$mcs)")
        println("  anchor null p95 band: %.5f .. %.5f  (bar = %.4f)".format(
            java.util.Locale.US,
            nulls.values.minOf { percentile(it.all, 0.95) },
            nulls.values.maxOf { percentile(it.all, 0.95) },
            config.formalism.proposalSeparationBar))
        fun frac(xs: List<SiteRow>, p: (SiteRow) -> Boolean) =
            "%d/%d (%.0f%%)".format(java.util.Locale.US, xs.count(p), xs.size, 100.0 * xs.count(p) / xs.size)
        if (d1.isNotEmpty()) {
            println("  depth-1 splits (exactly matched null):  clear own p95: " + frac(d1) { it.clears } +
                "   above own p50: " + frac(d1) { it.observed >= it.nullP50 } +
                "   median q: " + "%.3f".format(java.util.Locale.US, d1.map { it.q }.sorted().let { percentile(it, 0.5) }))
        }
        if (deeper.isNotEmpty()) {
            println("  deeper splits (anchor-null approx):     clear anchor p95: " + frac(deeper) { it.clears } +
                "   median q: " + "%.3f".format(java.util.Locale.US, deeper.map { it.q }.sorted().let { percentile(it, 0.5) }))
        }
        println("  all accepted splits:                    clear anchor p95: ${frac(rows) { it.clears }}")
        println("=".repeat(120))

        // ── CSV exports (new files; the voided mcs=30 exports are left untouched) ──
        fun esc(s: String) = "\"" + s.replace("\"", "\"\"") + "\""
        val outDir = java.io.File("docs/data").apply { mkdirs() }
        java.io.File(outDir, "within_null_frozen_anchors.csv").printWriter().use { w ->
            w.println("snapshot_id,anchor_id,label,n,p50,p90,p95,p99,p95_ci_lo,p95_ci_hi,cond_p95,reach_pct,accept_pct,reps")
            nulls.forEach { (id, an) ->
                val ci = quantileCi(an.all, 0.95)
                w.println("${esc(snapId)},${esc(id)},${esc(an.label)},${an.n}," +
                    "%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.1f,%.1f,%d".format(
                        java.util.Locale.US,
                        percentile(an.all, 0.50), percentile(an.all, 0.90),
                        percentile(an.all, 0.95), percentile(an.all, 0.99),
                        ci.first, ci.second,
                        if (an.reached.size >= 20) percentile(an.reached, 0.95) else Double.NaN,
                        100.0 * an.reached.size / an.all.size, 100.0 * an.accepted / an.all.size, an.all.size))
            }
        }
        java.io.File(outDir, "within_null_frozen_splits.csv").printWriter().use { w ->
            w.println("snapshot_id,node_id,label,depth,n,k,observed_sep,anchor_id,anchor_label,anchor_null_p50,anchor_null_p95,q,clears_p95,exact_match")
            rows.forEach { row ->
                w.println("${esc(snapId)},${esc(row.id)},${esc(row.label)},${row.depth},${row.n},${row.k}," +
                    "%.6f,${esc(row.anchorId)},${esc(row.anchorLabel)},%.6f,%.6f,%.4f,${row.clears},${row.depth == 1}".format(
                        java.util.Locale.US, row.observed, row.nullP50, row.nullP95, row.q))
            }
        }
        println("wrote docs/data/within_null_frozen_anchors.csv  (${nulls.size} anchors)")
        println("wrote docs/data/within_null_frozen_splits.csv   (${rows.size} accepted splits)")
    }

    // ── siteNull: SITE-level + DEFLATED nulls on every accepted split (P2) ────────

    /** id -> 256-slice unit vector, so child-region centroids can be resolved
     *  against the site's own vectors without a second DB pass per child. */
    private fun loadVectorsById(conn: java.sql.Connection, ids: Collection<String>): Map<String, DoubleArray> {
        val out = LinkedHashMap<String, DoubleArray>()
        ids.chunked(400).forEach { chunk ->
            conn.prepareStatement(
                "SELECT q.id, e.vector FROM queries q JOIN embeddings e ON e.query = q.distilled_text " +
                    "WHERE q.id IN (${chunk.joinToString(",") { "?" }})"
            ).use { stmt ->
                chunk.forEachIndexed { i, id -> stmt.setString(i + 1, id) }
                val rs = stmt.executeQuery()
                while (rs.next()) {
                    val qid = rs.getString(1)
                    val bytes = rs.getBytes(2) ?: continue
                    val buf = java.nio.ByteBuffer.wrap(bytes)
                    val full = FloatArray(bytes.size / 4) { buf.getFloat() }
                    if (full.size < 256) continue
                    val v = DoubleArray(256) { full[it].toDouble() }
                    var norm = 0.0
                    for (x in v) norm += x * x
                    norm = sqrt(norm)
                    if (norm > 0) { for (i in v.indices) v[i] /= norm; out[qid] = v }
                }
            }
        }
        return out
    }

    /** Orthonormal basis of the between-child-centroid subspace: span{c_j - c_1},
     *  Gram-Schmidt, near-zero residuals dropped. k=2 gives exactly the
     *  between-centroid direction; k children give at most k-1 dims. */
    private fun betweenCentroidBasis(centroids: List<DoubleArray>): List<DoubleArray> {
        if (centroids.size < 2) return emptyList()
        val dirs = mutableListOf<DoubleArray>()
        val base = centroids[0]
        for (j in 1 until centroids.size) {
            val d = DoubleArray(base.size) { centroids[j][it] - base[it] }
            for (u in dirs) {
                var dot = 0.0
                for (i in d.indices) dot += d[i] * u[i]
                for (i in d.indices) d[i] -= dot * u[i]
            }
            var nrm = 0.0
            for (x in d) nrm += x * x
            nrm = sqrt(nrm)
            if (nrm > 1e-9) dirs.add(DoubleArray(d.size) { d[it] / nrm })
        }
        return dirs
    }

    /**
     * SITE-LEVEL + DEFLATED WITHIN-NODE NULLS on the frozen mcs=55 artifact
     * (`gradlew siteNull`). Implements plan P2 (docs/v2_validation_plan.md, criteria
     * frozen 2026-09-08).
     *
     * The anchor-level arm above (`withinNull`) scores every accepted split against
     * its DEPTH-1 anchor's null, which is anti-conservative for smaller descendant
     * sites (the null narrows with n). This arm removes the approximation: each of
     * the accepted split sites is scored against a null fitted to the SITE'S OWN
     * population — the same anisotropy-preserving generator (Gaussian moment-matched
     * to the site's 256-slice mean/covariance, projected to the sphere), same
     * production `splitSingleNode` at the frozen config, same unconditional-quantile
     * convention (non-reached replicates score 0).
     *
     * DEFLATED variant (the "natural projection" version, labelled as such): the
     * observed split's between-child-centroid subspace (child-region centroids of the
     * frozen tree, Gram-Schmidt, <= k-1 dims) is projected out of the CENTERED
     * observations before sampling — C' = (I - UU^T) applied to each centered row —
     * so the null carries the site's texture MINUS the elongation along the very axis
     * the split cut. The mean mu is kept intact (a mean offset creates no
     * bimodality). A genuinely heterogeneous node has covariance elongated along its
     * own between-cluster axis, so the plain within-node null is inflated by the
     * structure under test; the deflated null asks "does the observed separation
     * exceed what the REMAINING texture produces?" and is the statistic meant to
     * separate elongated texture from real heterogeneity the elongated null hides.
     *
     * Certification: a site is certified at site-level p95 iff its persisted
     * dasguptaDeltaNorm >= the unconditional p95 of its own null (q <= ~0.05);
     * analogously for the deflated null. Guards, both recorded as feasibility flags
     * rather than fabricated q's: NULL-INFEASIBLE (n < 2*minClusterSize — the
     * production splitter cannot even be driven) and DEGENERATE (< 20 of the
     * replicates reached the separation gate, the file-wide usability floor; a
     * collapsed null certifies nothing).
     *
     * The CERTIFIED TRUNK is the maximal all-certified prefix of the tree: a site is
     * a trunk member iff it is certified AND every ancestor split site is a trunk
     * member. A view — nothing is deleted.
     */
    @Test
    fun `siteNull - site-level and deflated nulls on every accepted split of the frozen artifact`() {
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val embDb = java.io.File("embeddings_cache.db")
        org.junit.jupiter.api.Assumptions.assumeTrue(embDb.exists(), "embeddings_cache.db not present")
        val frozen = System.getProperty("snapshotId") ?: "20260727_042523_Headless_Run_Auto_ge"
        val loaded = loadFrozenGraph(frozen)
        org.junit.jupiter.api.Assumptions.assumeTrue(loaded != null, "frozen snapshot $frozen not available")
        val (snapId, g) = loaded!!
        val byId = g.nodes.associateBy { it.id }
        // Site enumeration: identical to the withinNull stage-2 arm (66 accepted splits).
        val sites = g.nodes.filter { it.childIds.size >= 2 && it.dasguptaDeltaNorm > 0.0 }
            .sortedWith(compareBy({ it.depth }, { -(regionQueryIds(it, byId).size) }))
        val r = reps(300)
        val mcs = 55

        val config = canonicalConfig(mcs)
        val splitter = TaxonomySplitter(config, NoLlm, MMLUDatasetFetcher(config, ""), TaxonomyFitter(config))
        val capture = Capture()
        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        capture.context = splitLog.loggerContext
        capture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(capture)

        println("=".repeat(132))
        println("SITE-LEVEL + DEFLATED WITHIN-NODE NULLS — FROZEN ARTIFACT.  snapshot=$snapId  minClusterSize=$mcs  bar=${config.formalism.proposalSeparationBar}")
        println("${sites.size} accepted split sites, reps=$r per site per arm. Null fitted to each SITE'S OWN population.")
        println("q = fraction of ALL null replicates >= observed (unconditional; non-reached score 0). cert = observed >= null p95.")
        println("deflated = between-child-centroid subspace (<= k-1 dims) projected out of the centered observations before sampling.")
        println("=".repeat(132))
        println(
            "%-46s %5s %5s %3s | %8s | %8s %8s %6s %6s | %2s %8s %8s %6s %6s | %s".format(
                "site", "depth", "n", "k", "observed",
                "siteP50", "siteP95", "qSite", "reach%",
                "dd", "deflP50", "deflP95", "qDefl", "reach%", "verdict"
            )
        )

        data class SiteNullRow(
            val id: String, val label: String, val depth: Int, val n: Int, val k: Int,
            val observed: Double,
            val siteP50: Double, val siteP95: Double, val qSite: Double,
            val siteReach: Double, val siteAcc: Double,
            val deflDims: Int,
            val deflP50: Double, val deflP95: Double, val qDefl: Double,
            val deflReach: Double, val deflAcc: Double,
            val feasibility: String,        // OK | NULL-INFEASIBLE | DEGENERATE(-DEFL)
            val certSite: Boolean, val certDefl: Boolean
        )
        val rows = mutableListOf<SiteNullRow>()

        fun runArm(tagPrefix: String, seedBase: Long, siteId: String,
                   mu: DoubleArray, centered: List<DoubleArray>, n: Int): List<Rep> =
            runBlocking {
                coroutineScope {
                    (0 until r).map { rep ->
                        async(Dispatchers.Default) {
                            val rng = java.util.Random(
                                seedBase + siteId.hashCode().toLong() * 2654435761L + rep * 104729L
                            )
                            runReplicate(
                                splitter, capture, "${tagPrefix}_${siteId}_$rep",
                                withinNodeCloud(mu, centered, n, rng)
                            )
                        }
                    }.awaitAll()
                }
            }

        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { conn ->
            for (site in sites) {
                val ids = regionQueryIds(site, byId)
                val vecById = loadVectorsById(conn, ids)
                // Cache-only, hard-fail: never silently measure a subset of the frozen population.
                check(vecById.size == ids.size) {
                    "embedding cache miss for '${site.label}': ${vecById.size}/${ids.size} vectors recovered"
                }
                val vectors = ids.map { vecById.getValue(it) }
                val m = vectors.size
                val label = site.label ?: site.id
                val obs = site.dasguptaDeltaNorm
                if (m < 2 * mcs) {
                    // Cannot be driven through splitSingleNode: record, don't fabricate.
                    rows.add(SiteNullRow(site.id, label, site.depth, m, site.childIds.size, obs,
                        Double.NaN, Double.NaN, Double.NaN, 0.0, 0.0, 0,
                        Double.NaN, Double.NaN, Double.NaN, 0.0, 0.0,
                        "NULL-INFEASIBLE", certSite = false, certDefl = false))
                    println("%-46s %5d %5d %3d | %8.5f | NULL-INFEASIBLE (n < 2*minClusterSize=%d)".format(
                        java.util.Locale.US, label.take(46), site.depth, m, site.childIds.size, obs, 2 * mcs))
                    continue
                }
                val dim = 256
                val mu = DoubleArray(dim)
                for (v in vectors) for (i in 0 until dim) mu[i] += v[i] / m
                val centered = vectors.map { v -> DoubleArray(dim) { i -> v[i] - mu[i] } }

                // Deflation basis: centroids of the frozen tree's child regions.
                val childCentroids = site.childIds.mapNotNull { cid ->
                    val child = byId[cid] ?: return@mapNotNull null
                    val cIds = regionQueryIds(child, byId).filter { vecById.containsKey(it) }
                    if (cIds.isEmpty()) return@mapNotNull null
                    val c = DoubleArray(dim)
                    for (qid in cIds) { val v = vecById.getValue(qid); for (i in 0 until dim) c[i] += v[i] / cIds.size }
                    c
                }
                val basis = betweenCentroidBasis(childCentroids)
                val deflated = centered.map { c ->
                    val out = c.copyOf()
                    for (u in basis) {
                        var dot = 0.0
                        for (i in out.indices) dot += out[i] * u[i]
                        for (i in out.indices) out[i] -= dot * u[i]
                    }
                    out
                }

                val plain = runArm("SN", 20260908L, site.id, mu, centered, m)
                val defl = runArm("SND", 88820260908L, site.id, mu, deflated, m)

                fun stats(res: List<Rep>): DoubleArray {
                    val all = res.map { it.sepKway }.sorted()
                    val reached = all.count { it > 0.0 }
                    return doubleArrayOf(
                        percentile(all, 0.50), percentile(all, 0.95),
                        all.count { it >= obs }.toDouble() / all.size,
                        100.0 * reached / all.size,
                        100.0 * res.count { it.accepted } / all.size,
                        reached.toDouble()
                    )
                }
                val ps = stats(plain)
                val pd = stats(defl)
                val plainUsable = ps[5] >= 20
                val deflUsable = pd[5] >= 20
                val feas = when {
                    plainUsable && deflUsable -> "OK"
                    !plainUsable && !deflUsable -> "DEGENERATE"
                    !plainUsable -> "DEGENERATE-SITE"
                    else -> "DEGENERATE-DEFL"
                }
                val certSite = plainUsable && obs >= ps[1]
                val certDefl = deflUsable && obs >= pd[1]
                rows.add(SiteNullRow(site.id, label, site.depth, m, site.childIds.size, obs,
                    ps[0], ps[1], ps[2], ps[3], ps[4], basis.size,
                    pd[0], pd[1], pd[2], pd[3], pd[4], feas, certSite, certDefl))
                println(
                    "%-46s %5d %5d %3d | %8.5f | %8.5f %8.5f %6.3f %5.1f%% | %2d %8.5f %8.5f %6.3f %5.1f%% | %s%s%s".format(
                        java.util.Locale.US, label.take(46), site.depth, m, site.childIds.size, obs,
                        ps[0], ps[1], ps[2], ps[3], basis.size, pd[0], pd[1], pd[2], pd[3],
                        if (certSite) "SITE-CERT" else "site-fail",
                        if (certDefl) " DEFL-CERT" else " defl-fail",
                        if (feas != "OK") " [$feas]" else ""
                    )
                )
            }
        }
        splitLog.detachAppender(capture); capture.stop(); splitLog.isAdditive = true

        // ── Certified trunk: maximal all-certified prefix ────────────────────────
        val rowById = rows.associateBy { it.id }
        val isSite = { node: taxonomy.service.SerialNode -> node.childIds.size >= 2 && node.dasguptaDeltaNorm > 0.0 }
        fun parentOf(node: taxonomy.service.SerialNode): taxonomy.service.SerialNode? =
            (listOfNotNull(node.treeParentId) + node.parentIds).firstNotNullOfOrNull { byId[it] }
        val trunkMemo = HashMap<String, Boolean>()
        fun inTrunk(id: String): Boolean = trunkMemo.getOrPut(id) {
            val row = rowById[id] ?: return@getOrPut false
            if (!row.certSite) return@getOrPut false
            var cur = byId[id]?.let { parentOf(it) }
            val guard = HashSet<String>()
            while (cur != null && guard.add(cur.id)) {
                if (isSite(cur) && !inTrunk(cur.id)) return@getOrPut false
                if (cur.depth <= 0) break
                cur = parentOf(cur)
            }
            true
        }
        val trunk = rows.filter { inTrunk(it.id) }

        // ── CSV export ───────────────────────────────────────────────────────────
        fun esc(s: String) = "\"" + s.replace("\"", "\"\"") + "\""
        fun fmt(x: Double, p: String) = if (x.isNaN()) "" else p.format(java.util.Locale.US, x)
        val outDir = java.io.File("docs/data").apply { mkdirs() }
        java.io.File(outDir, "site_null_frozen.csv").printWriter().use { w ->
            w.println("snapshot_id,node_id,label,depth,n,k,observed_sep," +
                "site_null_p50,site_null_p95,q_site,site_reach_pct,site_accept_pct," +
                "defl_dims,defl_null_p50,defl_null_p95,q_deflated,defl_reach_pct,defl_accept_pct," +
                "cert_site_p95,cert_deflated_p95,trunk_member,feasibility,reps")
            rows.forEach { row ->
                w.println("${esc(snapId)},${esc(row.id)},${esc(row.label)},${row.depth},${row.n},${row.k}," +
                    fmt(row.observed, "%.6f") + "," +
                    fmt(row.siteP50, "%.6f") + "," + fmt(row.siteP95, "%.6f") + "," +
                    fmt(row.qSite, "%.4f") + "," + fmt(row.siteReach, "%.1f") + "," + fmt(row.siteAcc, "%.1f") + "," +
                    "${row.deflDims}," +
                    fmt(row.deflP50, "%.6f") + "," + fmt(row.deflP95, "%.6f") + "," +
                    fmt(row.qDefl, "%.4f") + "," + fmt(row.deflReach, "%.1f") + "," + fmt(row.deflAcc, "%.1f") + "," +
                    "${row.certSite},${row.certDefl},${inTrunk(row.id)},${row.feasibility},$r")
            }
        }
        println()
        println("wrote docs/data/site_null_frozen.csv  (${rows.size} sites)")

        // ── Registered checks (FROZEN in docs/v2_validation_plan.md, P2) ─────────
        println()
        println("=".repeat(132))
        println("REGISTERED CHECKS (P2, frozen 2026-09-08)")
        val cs = rows.firstOrNull { it.depth == 1 && it.label == "Computer science" }
        val phil1 = rows.firstOrNull { it.depth == 1 && it.label == "Philosophy" }
        val phil2 = rows.firstOrNull { it.label == "Core Philosophical Concepts and Theorists" }
        fun v(x: SiteNullRow?, defl: Boolean) = when {
            x == null -> "MISSING"
            defl -> "qDefl=%.3f %s".format(java.util.Locale.US, x.qDefl, if (x.certDefl) "CERT" else "uncert")
            else -> "qSite=%.3f %s".format(java.util.Locale.US, x.qSite, if (x.certSite) "CERT" else "uncert")
        }
        val powerPass = cs?.certDefl == true && phil1 != null && !phil1.certDefl && phil2 != null && !phil2.certDefl
        println("(a) POWER CHECK — deflated null certifies the CS contamination split, leaves Philosophy's two sites uncertified:")
        println("      Computer science depth-1 ............ ${v(cs, true)}   (required: CERT)")
        println("      Philosophy depth-1 (n00000014) ...... ${v(phil1, true)}   (required: uncert)")
        println("      Core Philosophical Concepts/Theorists ${v(phil2, true)}   (required: uncert)")
        println("      => ${if (powerPass) "PASS" else "FAIL"}")
        val certified = rows.filter { it.certSite }
        val chem = rows.firstOrNull { it.depth == 1 && it.label == "Chemistry" }
        val bio = rows.firstOrNull { it.depth == 1 && it.label == "Biology" }
        val trunkPass = certified.size >= 15 && chem?.certSite == true && bio?.certSite == true
        println("(b) TRUNK VIABILITY — >= 15 sites certified at site-level p95, including Chemistry and Biology depth-1:")
        println("      certified at site-level p95 ......... ${certified.size}/${rows.size}   (required: >= 15)")
        println("      Chemistry depth-1 ................... ${v(chem, false)}   (required: CERT)")
        println("      Biology depth-1 ..................... ${v(bio, false)}   (required: CERT)")
        println("      => ${if (trunkPass) "PASS" else "FAIL"}")
        println()
        println("CERTIFIED TRUNK (maximal all-certified prefix, site-level p95): ${trunk.size} sites")
        trunk.sortedWith(compareBy({ it.depth }, { -it.n })).forEach {
            println("      depth=%d  %-52s n=%-4d qSite=%.3f".format(
                java.util.Locale.US, it.depth, it.label.take(52), it.n, it.qSite))
        }
        println()
        println("Summary: site-cert ${certified.size}/${rows.size}, defl-cert ${rows.count { it.certDefl }}/${rows.size}, " +
            "both ${rows.count { it.certSite && it.certDefl }}, trunk ${trunk.size}, " +
            "infeasible ${rows.count { it.feasibility == "NULL-INFEASIBLE" }}, " +
            "degenerate ${rows.count { it.feasibility.startsWith("DEGENERATE") }}")
        println("=".repeat(132))
    }
}
