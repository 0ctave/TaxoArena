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
import taxonomy.model.projectTo   // CERT-POSITIVE-CONTROL's declaredSiteStatistic (the splitter's call)
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
    /**
     * D1 dimension-sweep overrides: -DsliceDim / -DdropTop / -Dwhiten put the harness on
     * the same geometry as the build under test, so a null measured here drives the
     * production splitter exactly as that build's construction did. Absent = frozen
     * geometry (256 / 0 / false). Applied at config time; the slice width is process-global.
     */
    private val sliceDimProp = System.getProperty("sliceDim")?.toIntOrNull() ?: 256
    private val dropTopProp = System.getProperty("dropTop")?.toIntOrNull() ?: 0
    private val whitenProp = System.getProperty("whiten")?.toBoolean() ?: false
    /**
     * TOPIC-PARTITION-20NG (registration I5, docs/judge_v2_program.md L10030-L10390): -DsepBar puts
     * the harness on the build's OWN proposalSeparationBar, so the floor-absorption / weak-pair
     * coarsening loop and the min-pair gate the null drives run against the bar the arm built with
     * (T1b 0.0145; T2 its computed bar). ABSENT -> [DEFAULT_SEP_BAR] = 0.025, the value this method
     * hardcoded since P2, so every existing site-null CSV reproduces (byte-inert: the config object
     * is identical, SepBarDefaultTest). Fail-closed: a present but unparseable or non-positive value
     * is fatal (never silently the default). Printed as a "[SEPBAR]" line by the siteNull arm.
     */
    private val sepBarProp = resolveSepBar(System.getProperty("sepBar"))
    // In-test override of the slice width (isoNullByDim loops over widths inside one JVM).
    @Volatile private var sliceDimOverride: Int? = null

    companion object {
        /** The bar canonicalConfig always used (canonical_freeze.toml, verbatim). */
        const val DEFAULT_SEP_BAR = 0.025

        /** -DsepBar resolution: null/blank -> [DEFAULT_SEP_BAR]; a value must parse to a finite Double > 0. */
        fun resolveSepBar(raw: String?): Double {
            if (raw == null || raw.isBlank()) return DEFAULT_SEP_BAR
            val v = raw.trim().toDoubleOrNull()
            require(v != null && v.isFinite() && v > 0.0) {
                "[SEPBAR] -DsepBar='$raw' is not a positive finite number; refusing (absent -> $DEFAULT_SEP_BAR)"
            }
            return v
        }
    }

    internal fun canonicalConfig(minClusterSize: Int = 30): TaxonomyConfig =
        TaxonomyConfig().apply {
            val dim = sliceDimOverride ?: sliceDimProp
            formalism.maxDepth = 8
            formalism.minClusterSize = minClusterSize
            formalism.proposalSeparationBar = sepBarProp
            formalism.embeddingSliceDim = dim
            formalism.splitDropTopPcs = dropTopProp
            formalism.splitWhiten = whitenProp
            taxonomy.model.EmbeddingSlice.width = dim
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

    /**
     * ISOTROPIC NULL BY SLICE WIDTH (`gradlew isoNullByDim`) — the D1 sweep's confound
     * readout. The flat bar (0.025) was calibrated at 256 dims; the isotropic null of the
     * production splitter scales with the width (random-direction cosine sd ~ 1/sqrt(d)),
     * so the SAME bar is looser at 128 and tighter at 512. This measures that ratio at
     * three node sizes so the sweep's build-level readouts (leaf count, Top-1) can be
     * read against it; the site-level certification metric is self-calibrated per arm
     * and does not need it.
     */
    @Test
    fun `isoNullByDim - isotropic null p95 of the production splitter at 128, 256, 512 dims`() {
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val r = reps(300)
        val sigma = 0.5
        val saved = taxonomy.model.EmbeddingSlice.width
        try {
            // -DisoDims=1024 (comma-separated) restricts the sweep; default = the D1 trio.
            val dims = System.getProperty("isoDims")?.split(",")?.mapNotNull { it.trim().toIntOrNull() }
                ?: listOf(128, 256, 512)
            for (dim in dims) {
                sliceDimOverride = dim
                sweep(
                    "ISO-NULL sliceDim=$dim (sigma=$sigma), minClusterSize=55",
                    listOf(130, 406, 900), r, 55
                ) { n, rep -> singleModeCloud(n, dim, sigma, java.util.Random(1234L + n * 7919L + rep * 104729L + dim * 13L)) }
            }
        } finally {
            sliceDimOverride = null
            taxonomy.model.EmbeddingSlice.width = saved
        }
    }

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
        val dim = taxonomy.model.dimForDepth(0)
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
                    if (full.size < dim) continue
                    val v = DoubleArray(dim) { full[it].toDouble() }
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
        val embDb = unguardedEmbDb("within-node null on every accepted split")
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
        val embDb = unguardedEmbDb("Philosophy 256-slice seam")
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
        val embDb = unguardedEmbDb("slice vs full seam")
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
        val embDb = unguardedEmbDb("why are the largest leaves leaves")
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
        val embDb = unguardedEmbDb("fidelity replay")
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
     * EMBEDDER-PLUMBING (a): the six arms WITHOUT the vmfMu guard read only the DB of record. A set
     * -DembeddingCacheFile or -DembeddingModel REFUSES here (only the siteNull task forwards them, and only the
     * siteNull arm carries the guard), so no unguarded arm can read another embedder's vectors. Absent -> the
     * historical relative "embeddings_cache.db", byte-inert.
     */
    private fun unguardedEmbDb(arm: String): java.io.File {
        for (p in listOf(EmbedderReadGuard.PROP_CACHE_FILE, EmbedderReadGuard.PROP_MODEL)) {
            val v = System.getProperty(p)
            check(v == null) {
                "[EMB-CACHE] REFUSING: -D$p='$v' is admitted only by the siteNull arm (the one arm with the vmfMu guard); " +
                    "arm '$arm' reads ${taxonomy.dataset.EmbeddingCache.DB_OF_RECORD} only"
            }
        }
        return EmbedderReadGuard.resolveCacheFile(null).file
    }

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
        val embDb = unguardedEmbDb("withinNull")
        org.junit.jupiter.api.Assumptions.assumeTrue(embDb.exists(), "embeddings_cache.db not present")
        val frozen = System.getProperty("snapshotId") ?: "20260727_042523_Headless_Run_Auto_ge"
        val loaded = loadFrozenGraph(frozen)
        org.junit.jupiter.api.Assumptions.assumeTrue(loaded != null, "frozen snapshot $frozen not available")
        val (snapId, g) = loaded!!
        val byId = g.nodes.associateBy { it.id }
        val anchors = g.nodes.filter { it.depth == 1 }
            .map { it to regionQueryIds(it, byId) }
            .sortedByDescending { it.second.size }
        val anchorReps = reps(300)
        val anchorMcs = 55

        val anchorConfig = canonicalConfig(anchorMcs)
        val anchorSplitter = TaxonomySplitter(anchorConfig, NoLlm, MMLUDatasetFetcher(anchorConfig, ""), TaxonomyFitter(anchorConfig))
        val anchorCapture = Capture()
        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        anchorCapture.context = splitLog.loggerContext
        anchorCapture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(anchorCapture)

        println("=".repeat(120))
        println("WITHIN-NODE NULL — FROZEN ARTIFACT.  snapshot=$snapId  minClusterSize=$anchorMcs  bar=${anchorConfig.formalism.proposalSeparationBar}")
        println("${anchors.size} depth-1 anchors, reps=$anchorReps each. Null = anisotropy-preserving parametric bootstrap")
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
                        (0 until anchorReps).map { rep ->
                            async(Dispatchers.Default) {
                                val rng = java.util.Random(
                                    20260907L + anchor.id.hashCode().toLong() * 2654435761L + rep * 104729L
                                )
                                runReplicate(
                                    anchorSplitter, anchorCapture, "WNF_${anchor.id}_$rep",
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
                        100.0 * reached.size / anchorReps, 100.0 * acc / anchorReps
                    )
                )
            }
        }
        splitLog.detachAppender(anchorCapture); anchorCapture.stop(); splitLog.isAdditive = true

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
        println("SUMMARY  (snapshot=$snapId, reps=$anchorReps, minClusterSize=$anchorMcs)")
        println("  anchor null p95 band: %.5f .. %.5f  (bar = %.4f)".format(
            java.util.Locale.US,
            nulls.values.minOf { percentile(it.all, 0.95) },
            nulls.values.maxOf { percentile(it.all, 0.95) },
            anchorConfig.formalism.proposalSeparationBar))
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
        val dim = taxonomy.model.dimForDepth(0)
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
                    if (full.size < dim) continue
                    val v = DoubleArray(dim) { full[it].toDouble() }
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
        // THREAD-CAP delta (READY_w0_rp07 H2): the FIRST statement, before either Assumption, so the
        // line prints on EVERY run including the two skip paths (rule 11); the guard-site line below
        // carries the heap estimate on runs that reach the guard.
        println(taxonomy.runner.ThreadCap.line(null, (Runtime.getRuntime().maxMemory() * 0.90).toLong()))
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        // EMBEDDER-PLUMBING (a)/(d): -DembeddingCacheFile (fail-closed; absent -> embeddings_cache.db) and the model its vectors
        // must come from (-DembeddingModel; absent with no cache flag -> the DB of record's canonical model).
        val embChoice = EmbedderReadGuard.resolveCacheFile(System.getProperty(EmbedderReadGuard.PROP_CACHE_FILE))
        val embModel = EmbedderReadGuard.resolveModel(null, System.getProperty(EmbedderReadGuard.PROP_MODEL), embChoice.explicit)
        val embDb = embChoice.file
        println("[EMB-CACHE] siteNull reads ${embDb.path} (${if (embChoice.explicit) "-D${EmbedderReadGuard.PROP_CACHE_FILE}, validated" else "absent -> default"}); " +
            "model ${embModel.model} (${embModel.source})")
        if (!embDb.exists()) println("[EMB-GUARD] not run: ${embDb.path} not present (the test is skipped)")
        org.junit.jupiter.api.Assumptions.assumeTrue(embDb.exists(), "embeddings_cache.db not present")
        val frozen = System.getProperty("snapshotId") ?: "20260727_042523_Headless_Run_Auto_ge"
        val loaded = loadFrozenGraph(frozen)
        if (loaded == null) println("[EMB-GUARD] not run: frozen snapshot $frozen not available (the test is skipped)")
        org.junit.jupiter.api.Assumptions.assumeTrue(loaded != null, "frozen snapshot $frozen not available")
        val (snapId, g) = loaded!!
        val byId = g.nodes.associateBy { it.id }
        // Site enumeration: identical to the withinNull stage-2 arm (66 accepted splits).
        val sites = g.nodes.filter { it.childIds.size >= 2 && it.dasguptaDeltaNorm > 0.0 }
            .sortedWith(compareBy({ it.depth }, { -(regionQueryIds(it, byId).size) }))
        val siteReps = reps(300)
        val siteMcs = 55

        val siteConfig = canonicalConfig(siteMcs)
        val siteSplitter = TaxonomySplitter(siteConfig, NoLlm, MMLUDatasetFetcher(siteConfig, ""), TaxonomyFitter(siteConfig))
        val siteCapture = Capture()

        // ── HEAP GUARD: refuse BEFORE the first replicate, never mid-run ─────────
        //
        // Placement is load-bearing. `taxonomy.model.EmbeddingSlice.width` -- what
        // dimForDepth(0) returns -- is assigned by canonicalConfig() above, so a guard sited
        // one line EARLIER reads the stale default (256) and waves a 512-dim arm through: that
        // is exactly how the first version of this guard let T1b OOM a second time on
        // 2026-09-23 (estimate 4.08 GB at the stale 256 instead of 7.28 GB at the real 512).
        // The dim is therefore taken from `siteConfig`, which cannot be stale, and the guard runs
        // after the siteConfig exists and before the site loop opens the DB -- and before the
        // embedder guard opens it (w0-delta3, C7-3: this guard reads no DB).
        //
        // T1b of TOPIC-PARTITION-20NG (sliceDim 512, root site n=11845) died 168 s into its
        // first attempt with "OutOfMemoryError: Java heap space: failed reallocation of scalar
        // replaced objects" inside runArm, and 162 s into its second with the same error at
        // withinNodeCloud. JUnit recorded the test SKIPPED with an EMPTY system-err both times
        // and Gradle failed at SuiteTestClassProcessor.stop, so the arm read UNDETERMINED with
        // no diagnosis in its own artefacts. A refusal up front costs seconds and says what to do.
        //
        // Model. min(reps, cores) replicates are live at once (async on Dispatchers.Default,
        // parallelism = availableProcessors), and every live replicate holds, simultaneously,
        // at the pcaProject peak, for its site's population n:
        //   5 x n*D doubles  - the synthetic cloud withinNodeCloud builds, Embedding
        //                      .cachedProjection (projectTo), pcaProjectMemo's `input` copy,
        //                      pcaProject's `centered`, and its `residual` copy
        //   1 x n*D floats   - Embedding.values                      (= 0.5 of a double slot)
        //   3 x n*128 doubles- pcaProject's output and its two copyOf passes (splitDim is 128
        //                      for any n >= 500, so this term does NOT scale with D)
        // => peak live ~= live * n_max * (5.5*D + 3*128) * 8 bytes.
        //
        // n is the site's DISTINCT-id population, which is exactly what the cloud allocates:
        // withinNodeCloud builds `n` rows, called with n = vectors.size = vecById.size, and the
        // site loop hard-checks vecById.size == regionQueryIds(site).size. Leaf SLOT counts
        // (12772 for 20NG against 11845 distinct ids) are multi-assignment and are NOT
        // allocated here -- regionQueryIds returns a LinkedHashSet.
        //
        // The 0.90 coefficient is calibrated against the record, not against GC theory: the
        // estimator over-counts (the threads are not all inside pcaProject at the same instant),
        // so the bound is set to admit every arm that DID complete at 6g and refuse the one that
        // did not. Checked against the `n` column of all 57 site-null CSVs of record -- that
        // column is the very m the cloud is built from -- at 24 cores / 6g / 300 reps
        // (maxMemory 6.00 GiB, 0.90x = 5.80 GB):
        //   af_bareq512_s42   D=512 n_max=8133  -> 5.00 GB  completed  (binding; ADMITTED, 16% margin)
        //   ng_af_s42 (T1)    D=256 n_max=11845 -> 4.08 GB  completed  ADMITTED
        //   af_full_s42       D=256 n_max=11757 -> 4.04 GB  completed  ADMITTED
        //   every other arm (anchorfree, dimsweep*, splitratio*, promoted, h9_order,
        //   multicorpus, frozen): n_max <= 8133 at D <= 1024 -> <= 5.00 GB  ADMITTED
        //   ng_af_bareq512_s42 (T1b) D=512 n_max=11845 -> 7.28 GB  OOM      REFUSED, 26% margin
        // Admissible band is (0.776, 1.130); a 0.70 coefficient would have REFUSED
        // af_bareq512_s42 (5.00 > 4.51) and is unusable.
        val guardDim = siteConfig.formalism.embeddingSliceDim
        val guardNMax = sites.maxOfOrNull { regionQueryIds(it, byId).size } ?: 0
        val guardLive = minOf(siteReps, Runtime.getRuntime().availableProcessors().coerceAtLeast(2))
        val guardPeak = guardLive.toLong() * guardNMax.toLong() * (55L * guardDim / 10L + 3L * 128L) * 8L
        val guardMax = Runtime.getRuntime().maxMemory()
        val guardBudget = (guardMax * 0.90).toLong()
        // THREAD-CAP (RP07): printed before the heap guard can refuse, so it appears on every run
        // that reaches the guard, pass or fail; availableProcessors is the cap's execution witness.
        println(taxonomy.runner.ThreadCap.line(guardPeak, guardBudget))
        println("[SITENULL-HEAP] sliceDim=%d largest site n=%d live=%d -> peak live %.2f GB; budget 0.90 * maxMemory(%.2f GB) = %.2f GB"
            .format(java.util.Locale.US, guardDim, guardNMax, guardLive, guardPeak / 1e9, guardMax / 1e9, guardBudget / 1e9))
        if (guardPeak > guardBudget) {
            // 2x the live set is the working headroom G1 needs; 14g for T1b, the value the
            // record confirmed independently. House ceiling 24g -- above that, ask first.
            val needGib = kotlin.math.ceil(2.0 * guardPeak / (1L shl 30)).toInt()
            val msg = buildString {
                appendLine("[SITENULL-HEAP] REFUSING before the first replicate: this arm does not fit the heap.")
                appendLine("  sliceDim=%d  largest site n=%d  reps=%d  cores=%d  live replicates=%d"
                    .format(java.util.Locale.US, guardDim, guardNMax, siteReps,
                        Runtime.getRuntime().availableProcessors(), guardLive))
                appendLine("  peak live ~= live * n * (5.5*sliceDim + 3*128) * 8 = %.2f GB"
                    .format(java.util.Locale.US, guardPeak / 1e9))
                appendLine("  budget    =  0.90 * maxMemory(%.2f GB) = %.2f GB"
                    .format(java.util.Locale.US, guardMax / 1e9, guardBudget / 1e9))
                append("  relaunch with -DsiteNullHeap=" + needGib + "g")
                if (needGib > 24) append("  -- ABOVE the 24g house ceiling: ask before running")
            }
            println(msg)
            error(msg)
        }

        // ── EMBEDDER-PLUMBING (c): vmfMu cosine + dimension guard, BEFORE any replicate ──
        // Every accepted split site: cos(normalised mean of its member vectors read from the OPENED cache, the
        // snapshot's vmfMu) >= 0.99, raw vectors of exactly the model's native dimension, vmfMu of the slice
        // width; prints its minimum and budget pass or fail and REFUSES on any finding (EmbedderReadGuard). The slice
        // width is read from siteConfig (CONTEXT rule 11), never from the process-global.
        // [w0-delta3, READY_w0_delta2 C7-3] Sited AFTER the heap guard: the heap guard needs only the snapshot's site
        // sizes and siteConfig (no DB), so it refuses first and without opening the cache; on the merged code the
        // embedder guard had refused a stub cache before the heap guard could run, and the heap refusal lost its
        // execution witness. On a run that fits the heap this guard still runs BEFORE any replicate.
        run {
            val guardRo = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
            java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", guardRo).use { guardConn ->
                EmbedderReadGuard.run(guardConn, embDb.path, sites, { regionQueryIds(it, byId) },
                    siteConfig.formalism.embeddingSliceDim, embModel)
            }
        }
        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        siteCapture.context = splitLog.loggerContext
        siteCapture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(siteCapture)

        println("=".repeat(132))
        println("SITE-LEVEL + DEFLATED WITHIN-NODE NULLS — FROZEN ARTIFACT.  snapshot=$snapId  minClusterSize=$siteMcs  bar=${siteConfig.formalism.proposalSeparationBar}")
        println("${sites.size} accepted split sites, reps=$siteReps per site per arm. Null fitted to each SITE'S OWN population.")
        println("[SEPBAR] proposalSeparationBar=${siteConfig.formalism.proposalSeparationBar} (-DsepBar ${System.getProperty("sepBar")?.let { "'$it'" } ?: "absent -> default $DEFAULT_SEP_BAR"}); sliceDim=${taxonomy.model.dimForDepth(0)} dropTop=$dropTopProp whiten=$whitenProp reps=$siteReps")
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
                    (0 until siteReps).map { rep ->
                        async(Dispatchers.Default) {
                            val rng = java.util.Random(
                                seedBase + siteId.hashCode().toLong() * 2654435761L + rep * 104729L
                            )
                            runReplicate(
                                siteSplitter, siteCapture, "${tagPrefix}_${siteId}_$rep",
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
                if (m < 2 * siteMcs) {
                    // Cannot be driven through splitSingleNode: record, don't fabricate.
                    rows.add(SiteNullRow(site.id, label, site.depth, m, site.childIds.size, obs,
                        Double.NaN, Double.NaN, Double.NaN, 0.0, 0.0, 0,
                        Double.NaN, Double.NaN, Double.NaN, 0.0, 0.0,
                        "NULL-INFEASIBLE", certSite = false, certDefl = false))
                    println("%-46s %5d %5d %3d | %8.5f | NULL-INFEASIBLE (n < 2*minClusterSize=%d)".format(
                        java.util.Locale.US, label.take(46), site.depth, m, site.childIds.size, obs, 2 * siteMcs))
                    continue
                }
                val dim = taxonomy.model.dimForDepth(0)
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
        splitLog.detachAppender(siteCapture); siteCapture.stop(); splitLog.isAdditive = true

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
        // -DoutCsv redirects a non-frozen build's table (D1 sweep) so the frozen artifact's
        // registered P2 table is never overwritten by a sweep arm.
        val outFile = java.io.File(System.getProperty("outCsv") ?: "docs/data/site_null_frozen.csv")
        outFile.absoluteFile.parentFile?.mkdirs()
        outFile.printWriter().use { w ->
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
                    "${row.certSite},${row.certDefl},${inTrunk(row.id)},${row.feasibility},$siteReps")
            }
        }
        println()
        println("wrote ${outFile.path}  (${rows.size} sites; geometry sliceDim=${taxonomy.model.dimForDepth(0)} dropTop=$dropTopProp whiten=$whitenProp)")

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

    // ── certPositiveControl: CERT-POSITIVE-CONTROL declared-site arm (registered 2026-10-02) ──────
    //
    // ADDITIONS ONLY, placed after every existing member so no existing method, field, lambda or
    // synthetic class of this file changes (the inertness proof compares the javap listing of every
    // pre-existing member before and after: identical). The siteNull task's filter
    // ("*SeparationNullBySizeTest*siteNull*") does not match this method's name, so `gradlew siteNull`
    // runs exactly the method it ran before; this arm runs only under `gradlew certPositiveControl`.

    /**
     * The instrument's site statistic for a GIVEN partition: exactly the call
     * TaxonomySplitter.splitSingleNode makes to compute the value it persists as dasguptaDeltaNorm,
     * `StatisticsUtils.chanceCorrectedSeparation(routedClusters.map { cluster -> cluster.map { it.projectTo(childDim) } })`,
     * with the declared groups in place of the routed clusters (CERT-POSITIVE-CONTROL INSTRUMENT (i)).
     */
    internal fun declaredSiteStatistic(groups: List<List<Embedding>>, childDim: Int): Double =
        StatisticsUtils.chanceCorrectedSeparation(groups.map { cluster -> cluster.map { it.projectTo(childDim) } })

    /** The splitter and log capture this arm drives (siteNull's: canonicalConfig(mcs), the stub LLM), for the unit test: the
     *  fetcher's corpus DB at [corpusDb] (a temp file), never the cwd's mmlu_pro_dataset_cache_v2.db. */
    internal fun cpcSplitter(mcs: Int, corpusDb: String): TaxonomySplitter {
        val c = canonicalConfig(mcs)
        return TaxonomySplitter(c, NoLlm, MMLUDatasetFetcher(c, "", corpusDb), TaxonomyFitter(c))
    }
    internal fun cpcNewCapture(): AppenderBase<ILoggingEvent> = Capture()

    /** Seed of one site-null replicate: siteNull's runArm formula, verbatim (I-2 depends on it). */
    internal fun cpcSeed(seedBase: Long, siteId: String, rep: Int): Long =
        seedBase + siteId.hashCode().toLong() * 2654435761L + rep * 104729L

    /** One site null arm: siteNull's runArm, verbatim in seed, tag and generator; returns sepKway per replicate, in rep order. */
    internal fun cpcSiteArm(
        splitter: TaxonomySplitter, capture: AppenderBase<ILoggingEvent>, tagPrefix: String, seedBase: Long, siteId: String,
        mu: DoubleArray, centered: List<DoubleArray>, n: Int, reps: Int
    ): DoubleArray {
        val cap = capture as Capture
        val res = runBlocking {
            coroutineScope {
                (0 until reps).map { rep ->
                    async(Dispatchers.Default) {
                        val rng = java.util.Random(cpcSeed(seedBase, siteId, rep))
                        runReplicate(splitter, cap, "${tagPrefix}_${siteId}_$rep", withinNodeCloud(mu, centered, n, rng))
                    }
                }.awaitAll()
            }
        }
        return DoubleArray(res.size) { res[it].sepKway }
    }

    /** siteNull's population moments: mu = the mean of the slice vectors (the same loop), centered rows. */
    internal fun cpcMoments(vectors: List<DoubleArray>): Pair<DoubleArray, List<DoubleArray>> {
        val dim = vectors[0].size
        val m = vectors.size
        val mu = DoubleArray(dim)
        for (v in vectors) for (i in 0 until dim) mu[i] += v[i] / m
        return mu to vectors.map { v -> DoubleArray(dim) { i -> v[i] - mu[i] } }
    }

    /** siteNull's deflation: the between-group-centroid subspace (<= k-1 dims) projected out of the centered rows. */
    internal fun cpcDeflate(vectors: List<DoubleArray>, centered: List<DoubleArray>, groups: List<List<Int>>): Pair<List<DoubleArray>, Int> {
        val dim = vectors[0].size
        val centroids = groups.filter { it.isNotEmpty() }.map { g ->
            val c = DoubleArray(dim)
            for (i in g) { val v = vectors[i]; for (j in 0 until dim) c[j] += v[j] / g.size }
            c
        }
        val basis = betweenCentroidBasis(centroids)
        val out = centered.map { c ->
            val o = c.copyOf()
            for (u in basis) {
                var dot = 0.0
                for (i in o.indices) dot += o[i] * u[i]
                for (i in o.indices) o[i] -= dot * u[i]
            }
            o
        }
        return out to basis.size
    }

    /**
     * PC3's declared partition inside an anchor: one child per src with >= [minSize] items of the anchor; every smaller
     * src and every item without a src pooled into ONE child (if non-empty). Children ordered by src name, the pooled
     * child last. Returns (children as index lists into [ids], pooled count).
     */
    internal fun cpcSrcGroups(ids: List<String>, srcOf: Map<String, String>, minSize: Int): Pair<List<List<Int>>, Int> {
        val bySrc = java.util.TreeMap<String, MutableList<Int>>()
        val pooled = mutableListOf<Int>()
        ids.forEachIndexed { i, id ->
            val s = srcOf[id].orEmpty()
            if (s.isEmpty()) pooled.add(i) else bySrc.getOrPut(s) { mutableListOf() }.add(i)
        }
        val kids = mutableListOf<List<Int>>()
        for ((_, g) in bySrc) if (g.size >= minSize) kids.add(g) else pooled.addAll(g)
        if (pooled.isNotEmpty()) kids.add(pooled.sorted())
        return kids to pooled.size
    }

    /** C0: [reps] uniformly random size-matched relabellings of [labels] (Fisher-Yates, seeded), each scored by the routine. */
    internal fun cpcRelabelNull(embs: List<Embedding>, labels: IntArray, nGroups: Int, reps: Int, seed: Long, childDim: Int): DoubleArray {
        val rng = java.util.Random(seed)
        val perm = labels.copyOf()
        return DoubleArray(reps) {
            for (i in perm.size - 1 downTo 1) {
                val j = rng.nextInt(i + 1)
                val t = perm[i]; perm[i] = perm[j]; perm[j] = t
            }
            val groups = List(nGroups) { mutableListOf<Embedding>() }
            perm.forEachIndexed { i, g -> groups[g].add(embs[i]) }
            declaredSiteStatistic(groups, childDim)
        }
    }

    internal data class CpcLive(val accepted: Boolean, val persisted: Double, val recomputed: Double, val k: Int,
                                val groups: List<List<Embedding>>)

    /**
     * I-1 live leg: the REAL population of a site through the production splitSingleNode (as runReplicate drives it);
     * when the split is accepted, the routine applied to the children's routed populations must return the splitter's
     * own dasguptaDeltaNorm bit for bit. Cleans up exactly as runReplicate does.
     */
    internal fun cpcLiveIdentity(splitter: TaxonomySplitter, tag: String, embs: List<Embedding>, depth: Int): CpcLive {
        val keys = ArrayList<String>(embs.size)
        val node = GraphNode(label = tag, depth = depth)
        node.vmfKappa = 10.0
        embs.forEachIndexed { i, e ->
            val key = "$tag#$i"
            keys.add(key)
            val emb = Embedding(rawText = key, distilledText = key, values = e.values, queryId = i)
            GraphNode.registerEmbedding(emb)
            node.queries.add(emb)
            node.queryWeights[key] = 1.0
        }
        try {
            val accepted = runBlocking { splitter.splitSingleNode(node) }
            val childDim = taxonomy.model.dimForDepth(depth + 1)
            // children is a hash set: restore the splitter's cluster order (ids are created in routedClusters order)
            val groups = node.children.sortedWith(compareBy({ it.id.length }, { it.id })).map { it.queries.toList() }
            val rec = if (accepted) declaredSiteStatistic(groups, childDim) else Double.NaN
            return CpcLive(accepted, node.dasguptaDeltaNorm, rec, node.children.size, groups)
        } finally {
            keys.forEach { GraphNode.EmbeddingRegistry.remove(it) }
            node.children.forEach { c -> c.queries.clear(); c.queryWeights.clear() }
            node.children.clear()
            node.queries.clear()
            node.queryWeights.clear()
        }
    }

    internal data class CpcSite(
        val declared: Double, val plain: DoubleArray, val defl: DoubleArray?, val deflDims: Int,
        val kDeclared: Int, val kDeflDeclared: Int
    )

    /**
     * One declared site: the declared statistic of [groups] (index lists into [embs]) by the routine, the site's own plain
     * null (seedBase 20260908, siteNull's), and, when [deflated], the deflated null on the declared groups' centroid
     * subspace (seedBase 88820260908, siteNull's). [vectors] are the slice vectors the null is moment-matched to (siteNull
     * reads them with loadVectorsById); [embs] carry the raw slice floats the routine projects (production's projectTo).
     * k = the number of replicates >= the declared statistic (the registration's ">=").
     */
    internal fun cpcDeclaredSite(
        splitter: TaxonomySplitter, capture: AppenderBase<ILoggingEvent>, siteId: String, depth: Int,
        vectors: List<DoubleArray>, embs: List<Embedding>, groups: List<List<Int>>, reps: Int, deflated: Boolean,
        plainIn: DoubleArray? = null
    ): CpcSite {
        val declared = declaredSiteStatistic(groups.map { g -> g.map { embs[it] } }, taxonomy.model.dimForDepth(depth + 1))
        val (mu, centered) = cpcMoments(vectors)
        val plain = plainIn ?: cpcSiteArm(splitter, capture, "SN", 20260908L, siteId, mu, centered, vectors.size, reps)
        var defl: DoubleArray? = null
        var dims = 0
        if (deflated) {
            val (dc, d) = cpcDeflate(vectors, centered, groups)
            dims = d
            defl = cpcSiteArm(splitter, capture, "SND", 88820260908L, siteId, mu, dc, vectors.size, reps)
        }
        return CpcSite(declared, plain, defl, dims, plain.count { it >= declared }, defl?.count { it >= declared } ?: -1)
    }

    /** Raw slice floats (the first [dim] of each cached vector, as Embedding.projectTo slices them), keyed by query id. */
    private fun cpcLoadSliceFloats(conn: java.sql.Connection, ids: Collection<String>, dim: Int): Map<String, FloatArray> {
        val out = LinkedHashMap<String, FloatArray>()
        ids.chunked(400).forEach { chunk ->
            conn.prepareStatement(
                "SELECT q.id, e.vector FROM queries q JOIN embeddings e ON e.query = q.distilled_text " +
                    "WHERE q.id IN (${chunk.joinToString(",") { "?" }})"
            ).use { stmt ->
                chunk.forEachIndexed { i, id -> stmt.setString(i + 1, id) }
                val rs = stmt.executeQuery()
                while (rs.next()) {
                    val bytes = rs.getBytes(2) ?: continue
                    if (bytes.size / 4 < dim) continue
                    val buf = java.nio.ByteBuffer.wrap(bytes)
                    out[rs.getString(1)] = FloatArray(dim) { buf.getFloat() }
                }
            }
        }
        return out
    }

    /**
     * CERT-POSITIVE-CONTROL (`gradlew certPositiveControl`; registration docs/judge_v2_program.md "## Registered 2026-10-02
     * (before any code or call) — CERT-POSITIVE-CONTROL: ..."; readout tools/analysis/cert_positive_control.py --analyze).
     * Zero calls. The INSTRUMENT is siteNull's: the anisotropy-preserving generator moment-matched to the site population,
     * the production splitSingleNode at canonicalConfig(55) with the run's -DsliceDim/-DsepBar/-DdropTop/-Dwhiten, the
     * unconditional convention (non-reached replicates score 0), siteNull's seeds. What is new is the OBSERVED statistic:
     * a DECLARED partition scored by [declaredSiteStatistic] instead of the persisted value of an accepted split.
     *
     * Order (each gate refuses before the next costs CPU): I-1 (registered form: the routine on each of the snapshot's
     * sites' persisted child regions reproduces the persisted dasguptaDeltaNorm at 6 printed digits; live leg beside, see
     * [cpcLiveIdentity]; -Di1Form=live with a non-blank -Di1Bracket switches the gate to the live leg and is admitted only
     * as a registrar's bracket) -> the depth-1 anchors (their plain nulls = G12's; I-2: k against the persisted statistic
     * equals G12_sites.csv's k for chemistry, math and the TOP site with the smallest k; PC3's src partitions scored on the
     * same replicates, deflated beside) -> the member root (PC1: the 14 declared categories; its plain null, the deflated
     * null, and C0's 300 seeded size-matched relabellings scored by the same routine).
     * Writes, write-once into -DoutDir (refused if it exists non-empty): identity.csv, sites.csv, replicates.csv,
     * status.txt (COMPLETE, or REFUSED with the reason). Verdicts are the readout's, never printed here.
     */
    @Test
    fun `certPositiveControl - declared partitions scored against their own site nulls`() {
        println(taxonomy.runner.ThreadCap.line(null, (Runtime.getRuntime().maxMemory() * 0.90).toLong()))
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val tag = "[CPC]"
        var outDirForStatus: java.io.File? = null
        fun refuse(msg: String): Nothing {
            println("$tag REFUSING: $msg")
            outDirForStatus?.let { d -> runCatching { java.io.File(d, "status.txt").writeText("REFUSED: $msg\n") } }
            error("$tag REFUSED: $msg")
        }
        fun prop(k: String): String = System.getProperty(k)?.takeIf { it.isNotBlank() } ?: refuse("-D$k is required")
        val snapshotId = prop("snapshotId")
        val labelsPath = java.io.File(prop("declaredLabels"))
        val g12Path = java.io.File(prop("g12Sites"))
        val outDir = java.io.File(prop("outDir"))
        val i1Form = when (val f = System.getProperty("i1Form")) {
            null, "", "registered" -> "registered"
            "live" -> "live"
            else -> refuse("-Di1Form='$f' is not registered|live (absent -> registered)")
        }
        val i1Bracket = System.getProperty("i1Bracket")?.trim().orEmpty()
        if (i1Form == "live" && i1Bracket.isEmpty()) refuse("-Di1Form=live needs -Di1Bracket=<the registrar's bracket, programme line>")
        if (i1Form == "registered" && i1Bracket.isNotEmpty()) refuse("-Di1Bracket is admitted only with -Di1Form=live")
        val embDb = unguardedEmbDb("certPositiveControl")
        println("$tag reads ${embDb.path} (the qwen3 cache of record; -DembeddingCacheFile / -DembeddingModel refused)")
        if (!embDb.exists()) refuse("${embDb.path} not present")
        val reps = reps(300)
        if (outDir.exists() && (outDir.listFiles()?.isNotEmpty() == true)) refuse("${outDir.path} exists and is not empty (write-once)")
        outDir.mkdirs()
        outDirForStatus = outDir
        val c0Seed = 20261002L
        val mcs = 55

        val (snapId, g) = loadFrozenGraph(snapshotId) ?: refuse("snapshot $snapshotId not available")
        val byId = g.nodes.associateBy { it.id }
        val root = byId[g.rootId] ?: refuse("rootId ${g.rootId} not among the nodes")
        if (root.depth != 0) refuse("root ${root.id} has depth ${root.depth}")
        val isSite = { nd: taxonomy.service.SerialNode -> nd.childIds.size >= 2 && nd.dasguptaDeltaNorm > 0.0 }
        val sites = g.nodes.filter(isSite).sortedWith(compareBy({ it.depth }, { -(regionQueryIds(it, byId).size) }))
        val rootIds = regionQueryIds(root, byId).toList()

        // ── labels (written by cert_positive_control.py --prepare) ───────────────────────────────
        val labelBytes = labelsPath.takeIf { it.isFile }?.readBytes() ?: refuse("labels ${labelsPath.path} not found")
        val labelSha = java.security.MessageDigest.getInstance("SHA-256").digest(labelBytes).joinToString("") { "%02x".format(it) }
        val lines = String(labelBytes, Charsets.UTF_8).split("\n").let { if (it.last().isEmpty()) it.dropLast(1) else it }
        if (lines.isEmpty() || lines[0] != "query_id\tcategory\tsrc") refuse("labels header is not 'query_id<TAB>category<TAB>src'")
        val catOf = LinkedHashMap<String, String>()
        val srcOf = HashMap<String, String>()
        for (ln in lines.drop(1)) {
            val p = ln.split("\t")
            if (p.size != 3 || p[0].isEmpty() || p[1].isEmpty()) refuse("malformed label row '$ln'")
            if (catOf.put(p[0], p[1]) != null) refuse("duplicate label row for ${p[0]}")
            srcOf[p[0]] = p[2]
        }
        if (catOf.keys != rootIds.toSet()) refuse("labels cover ${catOf.size} ids; the member root region holds ${rootIds.size} (sets differ)")
        val cats = catOf.values.toSortedSet().toList()
        if (cats.size != 14) refuse("${cats.size} declared categories, not the registered 14")
        println("$tag snapshot $snapId root ${root.id} '${root.label}' n=${rootIds.size}; sites ${sites.size}; labels ${labelsPath.path} sha256 $labelSha; categories ${cats.size}")

        // ── G12_sites.csv: node_id -> (k, family, label) ─────────────────────────────────────────
        val g12 = HashMap<String, Triple<Int, String, String>>()
        run {
            val gl = g12Path.takeIf { it.isFile }?.readLines() ?: refuse("G12 sites ${g12Path.path} not found")
            val h = gl[0].split(",")
            val ix = { c: String -> h.indexOf(c).also { if (it < 0) refuse("G12 sites: no column $c") } }
            val iId = ix("node_id"); val iK = ix("k"); val iF = ix("family_key"); val iL = ix("label")
            for (ln in gl.drop(1).filter { it.isNotBlank() }) {
                val p = ln.split(",")
                g12[p[iId]] = Triple(p[iK].toIntOrNull() ?: refuse("G12 sites: k '${p[iK]}'"), p[iF], p[iL])
            }
        }

        val config = canonicalConfig(mcs)
        val dim = config.formalism.embeddingSliceDim
        val splitter = TaxonomySplitter(config, NoLlm, MMLUDatasetFetcher(config, ""), TaxonomyFitter(config))
        val capture = Capture()
        println("[SEPBAR] proposalSeparationBar=${config.formalism.proposalSeparationBar} (-DsepBar ${System.getProperty("sepBar")?.let { "'$it'" } ?: "absent -> default $DEFAULT_SEP_BAR"}); sliceDim=$dim dropTop=$dropTopProp whiten=$whitenProp reps=$reps minClusterSize=$mcs")

        // ── heap guard: siteNull's model, at the largest population (the member root) ───────────
        val live = minOf(reps, Runtime.getRuntime().availableProcessors().coerceAtLeast(2))
        val peak = live.toLong() * rootIds.size.toLong() * (55L * dim / 10L + 3L * 128L) * 8L
        val budget = (Runtime.getRuntime().maxMemory() * 0.90).toLong()
        println(taxonomy.runner.ThreadCap.line(peak, budget))
        println("[SITENULL-HEAP] sliceDim=%d largest site n=%d live=%d -> peak live %.2f GB; budget %.2f GB"
            .format(java.util.Locale.US, dim, rootIds.size, live, peak / 1e9, budget / 1e9))
        if (peak > budget) refuse("heap: peak %.2f GB > budget %.2f GB; relaunch with -DsiteNullHeap=%dg"
            .format(java.util.Locale.US, peak / 1e9, budget / 1e9, kotlin.math.ceil(2.0 * peak / (1L shl 30)).toInt()))

        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        val vecById: Map<String, DoubleArray>
        val floats: Map<String, FloatArray>
        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { conn ->
            EmbedderReadGuard.run(conn, embDb.path, sites, { regionQueryIds(it, byId) }, dim,
                EmbedderReadGuard.resolveModel(null, null, false))
            vecById = loadVectorsById(conn, rootIds)
            floats = cpcLoadSliceFloats(conn, rootIds, dim)
        }
        if (vecById.size != rootIds.size || floats.size != rootIds.size)
            refuse("embedding cache miss: ${vecById.size} / ${floats.size} of ${rootIds.size} vectors")
        val embOf = HashMap<String, Embedding>()
        for (id in rootIds) embOf[id] = Embedding(rawText = id, distilledText = id, values = floats.getValue(id))

        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        capture.context = splitLog.loggerContext
        capture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(capture)
        fun esc(s: String) = "\"" + s.replace("\"", "\"\"") + "\""
        fun f6(x: Double) = "%.6f".format(java.util.Locale.US, x)
        fun newWriter(name: String) = java.nio.file.Files.newBufferedWriter(
            java.io.File(outDir, name).toPath(), Charsets.UTF_8, java.nio.file.StandardOpenOption.CREATE_NEW,
            java.nio.file.StandardOpenOption.WRITE)
        val idw = newWriter("identity.csv")
        idw.write("leg,site_id,label,depth,n,k_children,persisted,recomputed,match\n")
        try {
            // ── I-1 ─────────────────────────────────────────────────────────────────────────────
            var regOk = 0
            for (s in sites) {
                val groups = s.childIds.mapNotNull { byId[it] }.map { c -> regionQueryIds(c, byId).map { embOf.getValue(it) } }
                val rec = declaredSiteStatistic(groups, taxonomy.model.dimForDepth(s.depth + 1))
                val ok = f6(rec) == f6(s.dasguptaDeltaNorm)
                if (ok) regOk++
                idw.write("I1_REGISTERED,${esc(s.id)},${esc(s.label ?: s.id)},${s.depth},${regionQueryIds(s, byId).size},${groups.size}," +
                    "${s.dasguptaDeltaNorm},$rec,$ok\n")
            }
            var liveAcc = 0
            var liveOk = 0
            for (s in sites) {
                val embs = regionQueryIds(s, byId).map { embOf.getValue(it) }
                val r = cpcLiveIdentity(splitter, "CPC_LIVE_${s.id}", embs, s.depth)
                val ok = r.accepted && r.recomputed.toRawBits() == r.persisted.toRawBits()
                if (r.accepted) liveAcc++
                if (ok) liveOk++
                idw.write("I1_LIVE,${esc(s.id)},${esc(s.label ?: s.id)},${s.depth},${embs.size},${r.k},${r.persisted},${r.recomputed}," +
                    "${if (r.accepted) ok.toString() else "not-accepted"}\n")
            }
            idw.flush()
            val i1Reg = regOk == sites.size && sites.isNotEmpty()
            val i1Live = liveAcc >= 1 && liveOk == liveAcc
            println("$tag I-1 registered form: $regOk of ${sites.size} sites reproduce the persisted dasguptaDeltaNorm at 6 printed digits")
            println("$tag I-1 live leg: $liveAcc of ${sites.size} real site populations accepted by splitSingleNode; $liveOk of $liveAcc reproduce node.dasguptaDeltaNorm bit for bit")
            when (i1Form) {
                "registered" -> if (!i1Reg) refuse("I-1 FAILED (registered form): $regOk of ${sites.size} sites reproduce; no readout")
                else -> {
                    println("$tag I-1 gate = the LIVE leg under the registrar's bracket: $i1Bracket")
                    if (!i1Live) refuse("I-1 FAILED (live leg): $liveOk of $liveAcc accepted reproduce")
                }
            }

            // ── anchors: plain nulls (= G12's), I-2, PC3 ─────────────────────────────────────────
            val anchors = root.childIds.mapNotNull { byId[it] }.filter(isSite)
            if (anchors.size != root.childIds.size) refuse("${root.childIds.size - anchors.size} of the root's ${root.childIds.size} children are not sites (G12's TOP family is every depth-1 anchor)")
            val siteRows = mutableListOf<String>()
            val repw = newWriter("replicates.csv")
            repw.write("site_id,arm,rep,stat\n")
            fun dumpReps(id: String, arm: String, xs: DoubleArray) { xs.forEachIndexed { i, x -> repw.write("${esc(id)},$arm,$i,$x\n") } }
            val kPersisted = HashMap<String, Int>()
            try {
                for (a in anchors) {
                    val ids = regionQueryIds(a, byId).toList()
                    val vectors = ids.map { vecById.getValue(it) }
                    val embs = ids.map { embOf.getValue(it) }
                    val (mu, centered) = cpcMoments(vectors)
                    val plain = cpcSiteArm(splitter, capture, "SN", 20260908L, a.id, mu, centered, ids.size, reps)
                    val kp = plain.count { it >= a.dasguptaDeltaNorm }
                    kPersisted[a.id] = kp
                    dumpReps(a.id, "SN", plain)
                    val (groups, pooled) = cpcSrcGroups(ids, srcOf, mcs)
                    val scored = groups.size >= 2
                    val res = if (scored) cpcDeclaredSite(splitter, capture, a.id, a.depth, vectors, embs, groups, reps, deflated = true, plainIn = plain) else null
                    res?.defl?.let { dumpReps(a.id, "SND", it) }
                    val g12k = g12[a.id]?.first ?: -1
                    idw.write("I2,${esc(a.id)},${esc(a.label ?: a.id)},${a.depth},${ids.size},${a.childIds.size},$g12k,$kp,${g12k == kp}\n")
                    siteRows.add(listOf("ANCHOR", esc(a.id), esc(a.label ?: a.id), a.depth, ids.size, groups.size, pooled, scored,
                        res?.declared ?: "", a.dasguptaDeltaNorm, res?.kDeclared ?: "", kp, g12k, res?.deflDims ?: "",
                        res?.kDeflDeclared ?: "", "", reps).joinToString(","))
                    println("$tag anchor %-40s n=%4d src children %2d (pooled %3d) %s k_persisted=%3d (G12 %3d)".format(
                        java.util.Locale.US, (a.label ?: a.id).take(40), ids.size, groups.size, pooled,
                        if (scored) "scored" else "NOT SCORED (< 2 children)", kp, g12k))
                }
                idw.flush(); repw.flush()
                // I-2: chemistry, math and the TOP site with the smallest G12 k (ties: node id)
                val topMin = g12.entries.filter { it.value.second == "TOP" }.minWithOrNull(compareBy({ it.value.first }, { it.key }))?.key
                val named = listOfNotNull(
                    anchors.firstOrNull { (it.label ?: "").endsWith("/chemistry") }?.id,
                    anchors.firstOrNull { (it.label ?: "").endsWith("/math") }?.id,
                    topMin
                )
                if (named.size != 3) refuse("I-2: cannot name chemistry, math and the smallest-k TOP site among the anchors ($named)")
                val bad = named.filter { kPersisted[it] == null || kPersisted[it] != g12[it]?.first }
                println("$tag I-2: ${named.joinToString { "$it k=${kPersisted[it]} (G12 ${g12[it]?.first})" }} -> ${if (bad.isEmpty()) "REPRODUCED" else "MISMATCH $bad"}")
                if (bad.isNotEmpty()) refuse("I-2 FAILED: $bad do not reproduce G12_sites.csv's k; no readout")

                // ── the member root: PC1, deflated, C0 ───────────────────────────────────────────
                val catIdx = cats.withIndex().associate { it.value to it.index }
                val labels = IntArray(rootIds.size) { catIdx.getValue(catOf.getValue(rootIds[it])) }
                val groups = List(cats.size) { c -> labels.indices.filter { labels[it] == c } }
                val vectors = rootIds.map { vecById.getValue(it) }
                val embs = rootIds.map { embOf.getValue(it) }
                val res = cpcDeclaredSite(splitter, capture, root.id, root.depth, vectors, embs, groups, reps, deflated = true)
                val c0 = cpcRelabelNull(embs, labels, cats.size, reps, c0Seed, taxonomy.model.dimForDepth(root.depth + 1))
                dumpReps(root.id, "SN", res.plain); dumpReps(root.id, "SND", res.defl!!); dumpReps(root.id, "C0", c0)
                val c0p95 = percentile(c0.sorted(), 0.95)
                siteRows.add(0, listOf("ROOT", esc(root.id), esc(root.label ?: root.id), root.depth, rootIds.size, groups.size, 0, true,
                    res.declared, root.dasguptaDeltaNorm, res.kDeclared, "", "", res.deflDims, res.kDeflDeclared, c0p95, reps).joinToString(","))
                println("$tag root n=${rootIds.size} declared=%.6f k_declared=%d plain p95=%.6f deflated dims=%d k=%d C0 p95=%.6f (seed %d)".format(
                    java.util.Locale.US, res.declared, res.kDeclared, percentile(res.plain.sorted(), 0.95), res.deflDims, res.kDeflDeclared, c0p95, c0Seed))
            } finally {
                repw.close()
            }
            newWriter("sites.csv").use { w ->
                w.write("role,site_id,label,depth,n,groups,pooled,scored,declared_stat,persisted_stat,k_declared,k_persisted,g12_k," +
                    "defl_dims,defl_k_declared,c0_p95,reps\n")
                siteRows.forEach { w.write(it + "\n") }
            }
            newWriter("status.txt").use { w ->
                w.write("COMPLETE\nsnapshot=$snapId\nlabels_sha256=$labelSha\nreps=$reps\nsliceDim=$dim\nsepBar=${config.formalism.proposalSeparationBar}\n" +
                    "dropTop=$dropTopProp\nwhiten=$whitenProp\nminClusterSize=$mcs\nc0Seed=$c0Seed\ni1Form=$i1Form\ni1Bracket=$i1Bracket\n" +
                    "threads=${Runtime.getRuntime().availableProcessors()}\n")
            }
            println("$tag wrote ${outDir.path}: identity.csv, sites.csv, replicates.csv, status.txt (COMPLETE); verdicts are the readout's")
        } finally {
            runCatching { idw.close() }
            splitLog.detachAppender(capture); capture.stop(); splitLog.isAdditive = true
        }
    }

    // ── certPcSize: CERT-PC-SIZE subsampled declared sites (registered 2026-10-03) ──────────────
    //
    // ADDITIONS ONLY, placed after every existing member (the certPositiveControl arm included) so no existing method,
    // field, lambda or synthetic class of this file changes (proof in the commit message: every pre-existing
    // SeparationNullBySizeTest*.class is byte-identical and the main class's pre-existing members disassemble identically).
    // The filters of siteNull, withinNull, isoNullByDim and certPositiveControl do not match this method's name; nullBySize
    // excludes it explicitly. It runs only under `gradlew certPcSize`. It REUSES the reviewed certPositiveControl members
    // (declaredSiteStatistic, cpcSiteArm through cpcDeclaredSite, cpcRelabelNull, cpcSeed) unchanged.

    /**
     * CERT-PC-SIZE site file (written by tools/analysis/cert_pc_size.py --prepare): header `site<TAB>query_id<TAB>category`,
     * one row per (site, item). Returns the sites in order of first appearance, each with its id -> category map in file
     * order. Refuses (IllegalArgumentException) a wrong header, a malformed row, a duplicate (site, id) and an empty file.
     */
    internal fun pcsParseSites(text: String): List<Pair<String, LinkedHashMap<String, String>>> {
        val lines = text.split("\n").map { it.removeSuffix("\r") }.let { if (it.isNotEmpty() && it.last().isEmpty()) it.dropLast(1) else it }
        require(lines.isNotEmpty() && lines[0] == "site\tquery_id\tcategory") { "site file header is not 'site<TAB>query_id<TAB>category'" }
        val out = LinkedHashMap<String, LinkedHashMap<String, String>>()
        for (ln in lines.drop(1)) {
            val p = ln.split("\t")
            require(p.size == 3 && p.all { it.isNotEmpty() }) { "malformed site row '$ln'" }
            val m = out.getOrPut(p[0]) { LinkedHashMap() }
            require(m.put(p[1], p[2]) == null) { "duplicate row for site ${p[0]} id ${p[1]}" }
        }
        require(out.isNotEmpty()) { "site file holds no rows" }
        return out.entries.map { it.key to it.value }
    }

    /**
     * One site's population IN THE ROOT REGION'S ORDER (never the file's), and its declared groups exactly as the
     * certPositiveControl arm builds PC1's: categories sorted, group c = the indices whose label is category c, in population
     * order. For the full root region this is PC1's population and partition element for element (so its declared statistic
     * and its plain null, seeded by the root id, are PC1's bit for bit: the IDENTITY precondition). Refuses an id outside the
     * root region. Returns (ids, sorted categories, groups).
     */
    internal fun pcsPopulation(rootIds: List<String>, catOf: Map<String, String>): Triple<List<String>, List<String>, List<List<Int>>> {
        val inRoot = rootIds.toHashSet()
        val outside = catOf.keys.filter { it !in inRoot }
        require(outside.isEmpty()) { "${outside.size} site ids are not in the member root region (e.g. ${outside.take(3)})" }
        val ids = rootIds.filter { it in catOf }
        val cats = catOf.values.toSortedSet().toList()
        val catIdx = cats.withIndex().associate { it.value to it.index }
        val labels = IntArray(ids.size) { catIdx.getValue(catOf.getValue(ids[it])) }
        val groups = List(cats.size) { c -> labels.indices.filter { labels[it] == c } }
        return Triple(ids, cats, groups)
    }

    /** C0 seed of one CERT-PC-SIZE subsample: siteNull's seed formula on the C0 base 20261002 (CERT-POSITIVE-CONTROL's) and the
     *  site name, rep 0, so the 15 subsamples draw distinct relabelling streams (builder's reading PCS-3). */
    internal fun pcsC0Seed(site: String): Long = cpcSeed(20261002L, site, 0)

    /**
     * CERT-PC-SIZE (`gradlew certPcSize`; registration docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or
     * call) — CERT-PC-SIZE: ..." L23722-L23750; readout tools/analysis/cert_pc_size.py --analyze). Zero calls. The instrument is
     * the certPositiveControl arm's (siteNull's generator and splitter at canonicalConfig(55) with the run's -DsliceDim/-DsepBar/
     * -DdropTop/-Dwhiten, siteNull's seeds, the declared-site routine); what is new is the SITE: a stratified subsample of the
     * member root's TRAIN items with its 14 declared labels.
     * Order: IDENTITY (the full root region from the site file's first site, named IDENTITY: declared statistic and plain null
     * seeded by the root id as PC1's; refuses unless the statistic prints 0.107803 and k = 0, before any subsample costs CPU)
     * -> each subsample PS_n<n>_d<draw> (its own plain null seeded by its name, the deflated null beside, C0 = 300 relabellings
     * seeded by [pcsC0Seed]). Writes, write-once into -DoutDir: sites.csv, replicates.csv, status.txt (COMPLETE, or REFUSED
     * with the reason). Verdicts are the readout's, never printed here.
     */
    @Test
    fun `certPcSize - subsampled declared sites scored against their own site nulls`() {
        println(taxonomy.runner.ThreadCap.line(null, (Runtime.getRuntime().maxMemory() * 0.90).toLong()))
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val tag = "[PCS]"
        var outDirForStatus: java.io.File? = null
        fun refuse(msg: String): Nothing {
            println("$tag REFUSING: $msg")
            outDirForStatus?.let { d -> runCatching { java.io.File(d, "status.txt").writeText("REFUSED: $msg\n") } }
            error("$tag REFUSED: $msg")
        }
        fun prop(k: String): String = System.getProperty(k)?.takeIf { it.isNotBlank() } ?: refuse("-D$k is required")
        val snapshotId = prop("snapshotId")
        val sitesPath = java.io.File(prop("siteLabels"))
        val outDir = java.io.File(prop("outDir"))
        val embDb = unguardedEmbDb("certPcSize")
        println("$tag reads ${embDb.path} (the qwen3 cache of record; -DembeddingCacheFile / -DembeddingModel refused)")
        if (!embDb.exists()) refuse("${embDb.path} not present")
        val reps = reps(300)
        if (outDir.exists() && (outDir.listFiles()?.isNotEmpty() == true)) refuse("${outDir.path} exists and is not empty (write-once)")
        outDir.mkdirs()
        outDirForStatus = outDir
        val mcs = 55
        val identityDeclared = "0.107803"   // the registration's IDENTITY PRECONDITION (PC1 of record)
        val identityK = 0

        val (snapId, g) = loadFrozenGraph(snapshotId) ?: refuse("snapshot $snapshotId not available")
        val byId = g.nodes.associateBy { it.id }
        val root = byId[g.rootId] ?: refuse("rootId ${g.rootId} not among the nodes")
        if (root.depth != 0) refuse("root ${root.id} has depth ${root.depth}")
        val isSite = { nd: taxonomy.service.SerialNode -> nd.childIds.size >= 2 && nd.dasguptaDeltaNorm > 0.0 }
        val sites = g.nodes.filter(isSite)
        val rootIds = regionQueryIds(root, byId).toList()

        val siteBytes = sitesPath.takeIf { it.isFile }?.readBytes() ?: refuse("site file ${sitesPath.path} not found")
        val siteSha = java.security.MessageDigest.getInstance("SHA-256").digest(siteBytes).joinToString("") { "%02x".format(it) }
        val parsed = try { pcsParseSites(String(siteBytes, Charsets.UTF_8)) } catch (e: IllegalArgumentException) { refuse(e.message ?: "site file") }
        if (parsed[0].first != "IDENTITY") refuse("the site file's first site is '${parsed[0].first}', not IDENTITY")
        if (parsed[0].second.keys != rootIds.toSet()) refuse("IDENTITY covers ${parsed[0].second.size} ids; the member root region holds ${rootIds.size} (sets differ)")
        val nameRx = Regex("^PS_n([0-9]+)_d([0-9]+)$")
        for ((name, m) in parsed.drop(1)) {
            val mt = nameRx.matchEntire(name) ?: refuse("site '$name' is not PS_n<n>_d<draw>")
            if (mt.groupValues[1].toInt() != m.size) refuse("site $name holds ${m.size} items, not ${mt.groupValues[1]}")
        }
        val pops = parsed.map { (name, m) ->
            val pop = try { pcsPopulation(rootIds, m) } catch (e: IllegalArgumentException) { refuse("site $name: ${e.message}") }
            if (pop.second.size != 14) refuse("site $name holds ${pop.second.size} declared categories, not the registered 14")
            name to pop
        }
        println("$tag snapshot $snapId root ${root.id} '${root.label}' n=${rootIds.size}; site file ${sitesPath.path} sha256 $siteSha; " +
            "sites ${pops.size} (${pops.joinToString { "${it.first}:${it.second.first.size}" }})")

        val config = canonicalConfig(mcs)
        val dim = config.formalism.embeddingSliceDim
        val splitter = TaxonomySplitter(config, NoLlm, MMLUDatasetFetcher(config, ""), TaxonomyFitter(config))
        val capture = Capture()
        println("[SEPBAR] proposalSeparationBar=${config.formalism.proposalSeparationBar} (-DsepBar ${System.getProperty("sepBar")?.let { "'$it'" } ?: "absent -> default $DEFAULT_SEP_BAR"}); sliceDim=$dim dropTop=$dropTopProp whiten=$whitenProp reps=$reps minClusterSize=$mcs")

        val live = minOf(reps, Runtime.getRuntime().availableProcessors().coerceAtLeast(2))
        val peak = live.toLong() * rootIds.size.toLong() * (55L * dim / 10L + 3L * 128L) * 8L
        val budget = (Runtime.getRuntime().maxMemory() * 0.90).toLong()
        println(taxonomy.runner.ThreadCap.line(peak, budget))
        println("[SITENULL-HEAP] sliceDim=%d largest site n=%d live=%d -> peak live %.2f GB; budget %.2f GB"
            .format(java.util.Locale.US, dim, rootIds.size, live, peak / 1e9, budget / 1e9))
        if (peak > budget) refuse("heap: peak %.2f GB > budget %.2f GB; relaunch with -DsiteNullHeap=%dg"
            .format(java.util.Locale.US, peak / 1e9, budget / 1e9, kotlin.math.ceil(2.0 * peak / (1L shl 30)).toInt()))

        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        val vecById: Map<String, DoubleArray>
        val floats: Map<String, FloatArray>
        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { conn ->
            EmbedderReadGuard.run(conn, embDb.path, sites, { regionQueryIds(it, byId) }, dim,
                EmbedderReadGuard.resolveModel(null, null, false))
            vecById = loadVectorsById(conn, rootIds)
            floats = cpcLoadSliceFloats(conn, rootIds, dim)
        }
        if (vecById.size != rootIds.size || floats.size != rootIds.size)
            refuse("embedding cache miss: ${vecById.size} / ${floats.size} of ${rootIds.size} vectors")
        val embOf = HashMap<String, Embedding>()
        for (id in rootIds) embOf[id] = Embedding(rawText = id, distilledText = id, values = floats.getValue(id))

        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        capture.context = splitLog.loggerContext
        capture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(capture)
        fun esc(s: String) = "\"" + s.replace("\"", "\"\"") + "\""
        fun f6(x: Double) = "%.6f".format(java.util.Locale.US, x)
        fun newWriter(name: String) = java.nio.file.Files.newBufferedWriter(
            java.io.File(outDir, name).toPath(), Charsets.UTF_8, java.nio.file.StandardOpenOption.CREATE_NEW,
            java.nio.file.StandardOpenOption.WRITE)
        val childDim = taxonomy.model.dimForDepth(root.depth + 1)
        val siteRows = mutableListOf<String>()
        val repw = newWriter("replicates.csv")
        try {
            repw.write("site_id,arm,rep,stat\n")
            fun dumpReps(id: String, arm: String, xs: DoubleArray) { xs.forEachIndexed { i, x -> repw.write("${esc(id)},$arm,$i,$x\n") } }
            for ((idx, entry) in pops.withIndex()) {
                val (name, pop) = entry
                val (ids, cats, groups) = pop
                val vectors = ids.map { vecById.getValue(it) }
                val embs = ids.map { embOf.getValue(it) }
                val identity = idx == 0
                val seedId = if (identity) root.id else name
                val res = cpcDeclaredSite(splitter, capture, seedId, root.depth, vectors, embs, groups, reps, deflated = !identity)
                dumpReps(name, "SN", res.plain)
                var c0p95 = Double.NaN
                var c0Seed = -1L
                if (identity) {
                    println("$tag IDENTITY n=${ids.size} declared=%s k=%d (registered %s, k %d) plain p95=%.6f max=%.6f".format(
                        java.util.Locale.US, f6(res.declared), res.kDeclared, identityDeclared, identityK,
                        percentile(res.plain.sorted(), 0.95), res.plain.maxOrNull() ?: Double.NaN))
                    repw.flush()
                    if (f6(res.declared) != identityDeclared || res.kDeclared != identityK)
                        refuse("IDENTITY FAILED: the full-size root gives declared ${f6(res.declared)} k ${res.kDeclared}, not $identityDeclared k $identityK; no subsample run")
                } else {
                    res.defl?.let { dumpReps(name, "SND", it) }
                    c0Seed = pcsC0Seed(name)
                    val labels = IntArray(ids.size)
                    groups.forEachIndexed { c, g -> g.forEach { labels[it] = c } }
                    val c0 = cpcRelabelNull(embs, labels, cats.size, reps, c0Seed, childDim)
                    dumpReps(name, "C0", c0)
                    c0p95 = percentile(c0.sorted(), 0.95)
                    println("$tag site %-12s n=%3d declared=%.6f k=%3d plain p95=%.6f reached=%3d deflated dims=%d k=%3d C0 p95=%.6f (seed %d)".format(
                        java.util.Locale.US, name, ids.size, res.declared, res.kDeclared, percentile(res.plain.sorted(), 0.95),
                        res.plain.count { it > 0.0 }, res.deflDims, res.kDeflDeclared, c0p95, c0Seed))
                }
                siteRows.add(listOf(if (identity) "IDENTITY" else "SUBSAMPLE", esc(name), ids.size, groups.size, res.declared,
                    res.kDeclared, if (identity) "" else res.deflDims, if (identity) "" else res.kDeflDeclared,
                    if (identity) "" else c0p95, if (identity) "" else c0Seed, seedId, reps).joinToString(","))
                repw.flush()
            }
        } finally {
            runCatching { repw.close() }
            splitLog.detachAppender(capture); capture.stop(); splitLog.isAdditive = true
        }
        newWriter("sites.csv").use { w ->
            w.write("role,site_id,n,groups,declared_stat,k_declared,defl_dims,defl_k_declared,c0_p95,c0_seed,null_seed_id,reps\n")
            siteRows.forEach { w.write(it + "\n") }
        }
        newWriter("status.txt").use { w ->
            w.write("COMPLETE\nsnapshot=$snapId\nsites_sha256=$siteSha\nreps=$reps\nsliceDim=$dim\nsepBar=${config.formalism.proposalSeparationBar}\n" +
                "dropTop=$dropTopProp\nwhiten=$whitenProp\nminClusterSize=$mcs\nc0Seed=20261002\n" +
                "threads=${Runtime.getRuntime().availableProcessors()}\n")
        }
        println("$tag wrote ${outDir.path}: sites.csv, replicates.csv, status.txt (COMPLETE); verdicts are the readout's")
    }

    // ── certPcK2: CERT-PC-K2 declared 2-way source-family sites inside one category (registered 2026-10-03) ─────
    //
    // ADDITIONS ONLY, placed after every existing member (certPcSize included) so no existing method, field, lambda or
    // synthetic class of this file changes (proof in the commit message: the pre-existing members disassemble identically).
    // The filters of siteNull, withinNull, isoNullByDim, certPositiveControl and certPcSize do not match this method's name;
    // nullBySize excludes it explicitly. It runs only under `gradlew certPcK2`. It REUSES the reviewed members unchanged
    // (pcsParseSites, pcsPopulation, pcsC0Seed, cpcDeclaredSite, cpcRelabelNull, declaredSiteStatistic). What differs from
    // certPcSize is only the SITE check ([pk2SiteError]): K2_<anchor>_n<n>_d<draw> sites holding exactly the two declared
    // source families of ONE category, IDENTITY (the full root, 14 categories) unchanged as the instrument precondition.

    /**
     * CERT-PC-K2 site-file check (null = accepted, else the refusal reason). The first site is IDENTITY: the member root
     * region exactly ([rootIds]) with 14 declared categories. Every other site is named K2_<anchor>_n<n>_d<draw> with a
     * registered anchor, holds exactly n items, and its labels are exactly the two source families (both
     * present): anchors economics / math / physics, families 'added' / 'ori_mmlu'. At least one K2 site.
     */
    internal fun pk2SiteError(parsed: List<Pair<String, Map<String, String>>>, rootIds: Set<String>): String? {
        // local, never class properties: a property would add a field initialiser to the existing constructor
        val pk2Anchors = listOf("economics", "math", "physics")      // the registered anchors ("ANCHORS AND SUB-GROUPS")
        val pk2Families = setOf("added", "ori_mmlu")                  // the two family labels the site file carries
        if (parsed.isEmpty() || parsed[0].first != "IDENTITY") return "the site file's first site is '${parsed.firstOrNull()?.first}', not IDENTITY"
        val ident = parsed[0].second
        if (ident.keys != rootIds) return "IDENTITY covers ${ident.size} ids; the member root region holds ${rootIds.size} (sets differ)"
        if (ident.values.toSet().size != 14) return "IDENTITY holds ${ident.values.toSet().size} declared categories, not the registered 14"
        if (parsed.size < 2) return "the site file holds no K2 site"
        val rx = Regex("^K2_([a-z]+)_n([0-9]+)_d([0-9]+)$")
        for ((name, m) in parsed.drop(1)) {
            val mt = rx.matchEntire(name) ?: return "site '$name' is not K2_<anchor>_n<n>_d<draw>"
            if (mt.groupValues[1] !in pk2Anchors) return "site $name: anchor '${mt.groupValues[1]}' is not one of $pk2Anchors"
            if (mt.groupValues[2].toInt() != m.size) return "site $name holds ${m.size} items, not ${mt.groupValues[2]}"
            if (m.values.toSet() != pk2Families) return "site $name holds the labels ${m.values.toSortedSet()}, not exactly $pk2Families"
        }
        return null
    }

    /**
     * CERT-PC-K2 (`gradlew certPcK2`; registration docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or
     * call) — CERT-PC-K2: ..." L23901-L23913; readout tools/analysis/cert_pc_k2.py --analyze). Zero calls. The instrument is
     * certPcSize's (siteNull's generator and splitter at canonicalConfig(55) with the run's -DsliceDim/-DsepBar/-DdropTop/
     * -Dwhiten, siteNull's seeds, the declared-site routine); what is new is the SITE: a stratified subsample of ONE declared
     * category's TRAIN items with its 2 declared source families (MMLU-original vs added sources).
     * Order: IDENTITY (the full root region, 14 categories, plain null seeded by the root id: PC1's; refuses unless 0.107803 and
     * k = 0, before any subsample costs CPU) -> each K2 site (its own plain null seeded by its name, the deflated null beside,
     * C0 = 300 size-matched 2-group relabellings seeded by [pcsC0Seed]). Writes, write-once into -DoutDir: sites.csv,
     * replicates.csv, status.txt (COMPLETE, or REFUSED with the reason). Verdicts are the readout's, never printed here.
     */
    @Test
    fun `certPcK2 - declared two-family sites inside one category scored against their own site nulls`() {
        println(taxonomy.runner.ThreadCap.line(null, (Runtime.getRuntime().maxMemory() * 0.90).toLong()))
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val tag = "[PK2]"
        var outDirForStatus: java.io.File? = null
        fun refuse(msg: String): Nothing {
            println("$tag REFUSING: $msg")
            outDirForStatus?.let { d -> runCatching { java.io.File(d, "status.txt").writeText("REFUSED: $msg\n") } }
            error("$tag REFUSED: $msg")
        }
        fun prop(k: String): String = System.getProperty(k)?.takeIf { it.isNotBlank() } ?: refuse("-D$k is required")
        val snapshotId = prop("snapshotId")
        val sitesPath = java.io.File(prop("siteLabels"))
        val outDir = java.io.File(prop("outDir"))
        val embDb = unguardedEmbDb("certPcK2")
        println("$tag reads ${embDb.path} (the qwen3 cache of record; -DembeddingCacheFile / -DembeddingModel refused)")
        if (!embDb.exists()) refuse("${embDb.path} not present")
        val reps = reps(300)
        if (outDir.exists() && (outDir.listFiles()?.isNotEmpty() == true)) refuse("${outDir.path} exists and is not empty (write-once)")
        outDir.mkdirs()
        outDirForStatus = outDir
        val mcs = 55
        val identityDeclared = "0.107803"   // CERT-PC-SIZE's IDENTITY PRECONDITION (PC1 of record), kept as the instrument check
        val identityK = 0

        val (snapId, g) = loadFrozenGraph(snapshotId) ?: refuse("snapshot $snapshotId not available")
        val byId = g.nodes.associateBy { it.id }
        val root = byId[g.rootId] ?: refuse("rootId ${g.rootId} not among the nodes")
        if (root.depth != 0) refuse("root ${root.id} has depth ${root.depth}")
        val isSite = { nd: taxonomy.service.SerialNode -> nd.childIds.size >= 2 && nd.dasguptaDeltaNorm > 0.0 }
        val sites = g.nodes.filter(isSite)
        val rootIds = regionQueryIds(root, byId).toList()

        val siteBytes = sitesPath.takeIf { it.isFile }?.readBytes() ?: refuse("site file ${sitesPath.path} not found")
        val siteSha = java.security.MessageDigest.getInstance("SHA-256").digest(siteBytes).joinToString("") { "%02x".format(it) }
        val parsed = try { pcsParseSites(String(siteBytes, Charsets.UTF_8)) } catch (e: IllegalArgumentException) { refuse(e.message ?: "site file") }
        pk2SiteError(parsed, rootIds.toSet())?.let { refuse(it) }
        val pops = parsed.map { (name, m) ->
            val pop = try { pcsPopulation(rootIds, m) } catch (e: IllegalArgumentException) { refuse("site $name: ${e.message}") }
            name to pop
        }
        println("$tag snapshot $snapId root ${root.id} '${root.label}' n=${rootIds.size}; site file ${sitesPath.path} sha256 $siteSha; " +
            "sites ${pops.size} (${pops.joinToString { "${it.first}:${it.second.first.size}/${it.second.third.size}g" }})")

        val config = canonicalConfig(mcs)
        val dim = config.formalism.embeddingSliceDim
        val splitter = TaxonomySplitter(config, NoLlm, MMLUDatasetFetcher(config, ""), TaxonomyFitter(config))
        val capture = Capture()
        println("[SEPBAR] proposalSeparationBar=${config.formalism.proposalSeparationBar} (-DsepBar ${System.getProperty("sepBar")?.let { "'$it'" } ?: "absent -> default $DEFAULT_SEP_BAR"}); sliceDim=$dim dropTop=$dropTopProp whiten=$whitenProp reps=$reps minClusterSize=$mcs")

        val live = minOf(reps, Runtime.getRuntime().availableProcessors().coerceAtLeast(2))
        val peak = live.toLong() * rootIds.size.toLong() * (55L * dim / 10L + 3L * 128L) * 8L
        val budget = (Runtime.getRuntime().maxMemory() * 0.90).toLong()
        println(taxonomy.runner.ThreadCap.line(peak, budget))
        println("[SITENULL-HEAP] sliceDim=%d largest site n=%d live=%d -> peak live %.2f GB; budget %.2f GB"
            .format(java.util.Locale.US, dim, rootIds.size, live, peak / 1e9, budget / 1e9))
        if (peak > budget) refuse("heap: peak %.2f GB > budget %.2f GB; relaunch with -DsiteNullHeap=%dg"
            .format(java.util.Locale.US, peak / 1e9, budget / 1e9, kotlin.math.ceil(2.0 * peak / (1L shl 30)).toInt()))

        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        val vecById: Map<String, DoubleArray>
        val floats: Map<String, FloatArray>
        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { conn ->
            EmbedderReadGuard.run(conn, embDb.path, sites, { regionQueryIds(it, byId) }, dim,
                EmbedderReadGuard.resolveModel(null, null, false))
            vecById = loadVectorsById(conn, rootIds)
            floats = cpcLoadSliceFloats(conn, rootIds, dim)
        }
        if (vecById.size != rootIds.size || floats.size != rootIds.size)
            refuse("embedding cache miss: ${vecById.size} / ${floats.size} of ${rootIds.size} vectors")
        val embOf = HashMap<String, Embedding>()
        for (id in rootIds) embOf[id] = Embedding(rawText = id, distilledText = id, values = floats.getValue(id))

        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        capture.context = splitLog.loggerContext
        capture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(capture)
        fun esc(s: String) = "\"" + s.replace("\"", "\"\"") + "\""
        fun f6(x: Double) = "%.6f".format(java.util.Locale.US, x)
        fun newWriter(name: String) = java.nio.file.Files.newBufferedWriter(
            java.io.File(outDir, name).toPath(), Charsets.UTF_8, java.nio.file.StandardOpenOption.CREATE_NEW,
            java.nio.file.StandardOpenOption.WRITE)
        val childDim = taxonomy.model.dimForDepth(root.depth + 1)
        val siteRows = mutableListOf<String>()
        val repw = newWriter("replicates.csv")
        try {
            repw.write("site_id,arm,rep,stat\n")
            fun dumpReps(id: String, arm: String, xs: DoubleArray) { xs.forEachIndexed { i, x -> repw.write("${esc(id)},$arm,$i,$x\n") } }
            for ((idx, entry) in pops.withIndex()) {
                val (name, pop) = entry
                val (ids, cats, groups) = pop
                val vectors = ids.map { vecById.getValue(it) }
                val embs = ids.map { embOf.getValue(it) }
                val identity = idx == 0
                val seedId = if (identity) root.id else name
                val res = cpcDeclaredSite(splitter, capture, seedId, root.depth, vectors, embs, groups, reps, deflated = !identity)
                dumpReps(name, "SN", res.plain)
                var c0p95 = Double.NaN
                var c0Seed = -1L
                if (identity) {
                    println("$tag IDENTITY n=${ids.size} declared=%s k=%d (registered %s, k %d) plain p95=%.6f max=%.6f".format(
                        java.util.Locale.US, f6(res.declared), res.kDeclared, identityDeclared, identityK,
                        percentile(res.plain.sorted(), 0.95), res.plain.maxOrNull() ?: Double.NaN))
                    repw.flush()
                    if (f6(res.declared) != identityDeclared || res.kDeclared != identityK)
                        refuse("IDENTITY FAILED: the full-size root gives declared ${f6(res.declared)} k ${res.kDeclared}, not $identityDeclared k $identityK; no K2 site run")
                } else {
                    res.defl?.let { dumpReps(name, "SND", it) }
                    c0Seed = pcsC0Seed(name)
                    val labels = IntArray(ids.size)
                    groups.forEachIndexed { c, gg -> gg.forEach { labels[it] = c } }
                    val c0 = cpcRelabelNull(embs, labels, cats.size, reps, c0Seed, childDim)
                    dumpReps(name, "C0", c0)
                    c0p95 = percentile(c0.sorted(), 0.95)
                    println("$tag site %-20s n=%3d groups=%s declared=%.6f k=%3d plain p95=%.6f reached=%3d deflated dims=%d k=%3d C0 p95=%.6f (seed %d)".format(
                        java.util.Locale.US, name, ids.size, groups.map { it.size }, res.declared, res.kDeclared,
                        percentile(res.plain.sorted(), 0.95), res.plain.count { it > 0.0 }, res.deflDims, res.kDeflDeclared, c0p95, c0Seed))
                }
                siteRows.add(listOf(if (identity) "IDENTITY" else "K2", esc(name), ids.size, groups.size,
                    groups.joinToString("/") { it.size.toString() }, res.declared,
                    res.kDeclared, if (identity) "" else res.deflDims, if (identity) "" else res.kDeflDeclared,
                    if (identity) "" else c0p95, if (identity) "" else c0Seed, seedId, reps).joinToString(","))
                repw.flush()
            }
        } finally {
            runCatching { repw.close() }
            splitLog.detachAppender(capture); capture.stop(); splitLog.isAdditive = true
        }
        newWriter("sites.csv").use { w ->
            w.write("role,site_id,n,groups,group_sizes,declared_stat,k_declared,defl_dims,defl_k_declared,c0_p95,c0_seed,null_seed_id,reps\n")
            siteRows.forEach { w.write(it + "\n") }
        }
        newWriter("status.txt").use { w ->
            w.write("COMPLETE\narm=certPcK2\nsnapshot=$snapId\nsites_sha256=$siteSha\nreps=$reps\nsliceDim=$dim\nsepBar=${config.formalism.proposalSeparationBar}\n" +
                "dropTop=$dropTopProp\nwhiten=$whitenProp\nminClusterSize=$mcs\nc0Seed=20261002\n" +
                "threads=${Runtime.getRuntime().availableProcessors()}\n")
        }
        println("$tag wrote ${outDir.path}: sites.csv, replicates.csv, status.txt (COMPLETE); verdicts are the readout's")
    }

    // ── gemmaOwnBar: GEMMA-OWN-BAR TRAIN-root null calibration (registered 2026-10-03) ─────────────────────────────────────
    //
    // ADDITIONS ONLY, placed after every existing member (certPcSize and certPcK2 included) so no existing method, field, lambda or synthetic
    // class of this file changes (proof in the commit message: every pre-existing SeparationNullBySizeTest*.class is
    // byte-identical). The filters of siteNull, withinNull, isoNullByDim, certPositiveControl, certPcSize and certPcK2 do not match this
    // method's name; nullBySize excludes it explicitly. It runs only under `gradlew gemmaOwnBar` (and, on fixtures, from
    // GemmaOwnBarArmTest). It REUSES the reviewed certPositiveControl members cpcMoments / cpcSiteArm / cpcSplitter / cpcNewCapture
    // unchanged; its file-reading half is GemmaOwnBarNull.

    /**
     * GEMMA-OWN-BAR (`gradlew gemmaOwnBar`; registration docs/judge_v2_program.md L23915-L23927, "## Registered 2026-10-03 (before
     * any code or call) — GEMMA-OWN-BAR: ..."; read by tools/analysis/gemma_own_bar.py --calibrate). Zero calls. HOW THE BAR IS
     * DERIVED: bar_g = 0.025 x p95_null(gemma 768, MASSIVE TRAIN root) / p95_null(qwen3 256, MASSIVE TRAIN root), each p95 from the
     * site null's moment-matched generator (withinNodeCloud: Gaussian matched to the population's slice mean and covariance,
     * projected to the sphere) driven through the production splitSingleNode at canonicalConfig(55), 300 reps, the unconditional
     * convention (a replicate that never reaches the gate scores 0), siteNull's seeds (cpcSeed(20260908, "MASSIVE_TRAIN_ROOT", rep)).
     * Printed beside (descriptive): the width-only isotropic bar, isoNullByDim's generator, config and seeds at n 406.
     *
     * -DgobArm selects ONE leg per launch (one heavy process at a time):
     *   gemma768 | qwen3_256  the TRAIN-root null: -DgobBuildDb (S1's MASSIVE salt-1 build DB; TRAIN rows only are read),
     *                         -DgobEmbDb (an intent_emb_<e>.db WORKING COPY), -DgobEmbSha256 (its pin; a mismatch refuses);
     *                         writes replicates.csv (rep,stat) and status.txt.
     *   iso                   the isotropic width leg at n 406 for slices 256 / 512 / 768 (isoNullByDim's cloud, seed formula and
     *                         canonicalConfig(55)); writes iso_replicates.csv (dim,rep,stat) and status.txt.
     * Fixed by the registration, refused if set: -DsliceDim (the arm sets the slice), -DsepBar (both nulls run at the recipe's
     * 0.025, the harness default and the bar the rule scales; builder's reading GOB-K1), -DdropTop, -Dwhiten, and the embedder
     * flags of the siteNull arm. -DoutDir is write-once (absent or empty). status.txt reads COMPLETE, or REFUSED with the reason.
     * The bar itself is computed by the readout script, never here.
     */
    @Test
    fun `gemmaOwnBar - TRAIN-root moment-matched null p95 per embedder and the isotropic width leg`() {
        println(taxonomy.runner.ThreadCap.line(null, (Runtime.getRuntime().maxMemory() * 0.90).toLong()))
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val tag = GemmaOwnBarNull.TAG
        var outDirForStatus: java.io.File? = null
        fun refuse(msg: String): Nothing {
            println("$tag REFUSING: $msg")
            outDirForStatus?.let { d -> runCatching { java.io.File(d, "status.txt").let { f -> if (!f.exists()) f.writeText("REFUSED: $msg\n") } } }
            throw GemmaOwnBarNull.Refusal("$tag REFUSED: $msg")
        }
        fun prop(k: String): String = System.getProperty(k)?.takeIf { it.isNotBlank() } ?: refuse("-D$k is required")
        val armName = prop("gobArm")
        val outDir = java.io.File(prop("outDir"))
        for (p in listOf("sliceDim", "sepBar", "dropTop", "whiten", EmbedderReadGuard.PROP_CACHE_FILE, EmbedderReadGuard.PROP_MODEL))
            System.getProperty(p)?.let { refuse("-D$p='$it' is not admitted by the gemmaOwnBar arm (fixed by the registration)") }
        if (armName != "iso" && armName !in GemmaOwnBarNull.ARMS) refuse("-DgobArm='$armName' is not iso, ${GemmaOwnBarNull.ARMS.keys.joinToString(", ")}")
        val reps = reps(300)
        if (reps < 2) refuse("-DnullReps=$reps < 2")
        try { GemmaOwnBarNull.claimOutDir(outDir) } catch (e: GemmaOwnBarNull.Refusal) { refuse(e.message ?: "outDir") }
        outDirForStatus = outDir
        val savedWidth = taxonomy.model.EmbeddingSlice.width
        val scratchDb = java.io.File.createTempFile("gob_fetcher_", ".db").apply { delete(); deleteOnExit() }
        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        val capture = cpcNewCapture()
        capture.context = splitLog.loggerContext
        capture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(capture)
        fun f6(x: Double) = "%.6f".format(java.util.Locale.US, x)
        try {
            if (armName == "iso") {
                val n = GemmaOwnBarNull.ISO_N
                val sb = StringBuilder("dim,rep,stat\n")
                val p95s = LinkedHashMap<Int, Double>()
                for (dim in GemmaOwnBarNull.ISO_DIMS) {
                    sliceDimOverride = dim
                    val splitter = cpcSplitter(GemmaOwnBarNull.MCS, scratchDb.absolutePath)
                    val cfg = canonicalConfig(GemmaOwnBarNull.MCS)
                    if (cfg.formalism.embeddingSliceDim != dim || taxonomy.model.EmbeddingSlice.width != dim) refuse("slice $dim not applied")
                    val cap = capture as Capture
                    val res = runBlocking {
                        coroutineScope {
                            (0 until reps).map { rep ->
                                async(Dispatchers.Default) {
                                    // isoNullByDim's cloud and seed formula, verbatim (sweep's NULL_<mcs>_<n>_<rep> tag)
                                    runReplicate(splitter, cap, "NULL_${GemmaOwnBarNull.MCS}_${n}_$rep",
                                        singleModeCloud(n, dim, GemmaOwnBarNull.ISO_SIGMA, java.util.Random(1234L + n * 7919L + rep * 104729L + dim * 13L)))
                                }
                            }.awaitAll()
                        }
                    }
                    val xs = DoubleArray(res.size) { res[it].sepKway }
                    xs.forEachIndexed { i, x -> sb.append("$dim,$i,$x\n") }
                    p95s[dim] = GemmaOwnBarNull.p95(xs)
                    println("$tag ISO slice=$dim n=$n reps=$reps p95=${f6(p95s.getValue(dim))} reached=${xs.count { it > 0.0 }} bar=${cfg.formalism.proposalSeparationBar}")
                }
                GemmaOwnBarNull.writeNew(java.io.File(outDir, "iso_replicates.csv"), sb.toString())
                GemmaOwnBarNull.writeNew(java.io.File(outDir, "status.txt"),
                    "COMPLETE\nleg=iso\nn=$n\nsigma=${GemmaOwnBarNull.ISO_SIGMA}\nreps=$reps\nminClusterSize=${GemmaOwnBarNull.MCS}\n" +
                        "sepBar=$sepBarProp\n" + p95s.entries.joinToString("") { "p95_iso_${it.key}=${it.value}\n" } +
                        "threads=${Runtime.getRuntime().availableProcessors()}\n")
                println("$tag wrote ${outDir.path}: iso_replicates.csv, status.txt (COMPLETE); the bar is the readout's")
                return
            }
            val arm = GemmaOwnBarNull.ARMS.getValue(armName)
            val buildDb = java.io.File(prop("gobBuildDb"))
            val embDb = java.io.File(prop("gobEmbDb"))
            val wantSha = prop("gobEmbSha256").lowercase()
            val train = try { GemmaOwnBarNull.loadTrain(buildDb) } catch (e: GemmaOwnBarNull.Refusal) { refuse(e.message ?: "build DB") }
            try { GemmaOwnBarNull.checkNoSidecar(embDb) } catch (e: GemmaOwnBarNull.Refusal) { refuse(e.message ?: "emb DB") }
            val embSha = GemmaOwnBarNull.sha256(embDb)
            println("$tag emb working copy ${embDb.path} sha256 $embSha (pin $wantSha) ${if (embSha == wantSha) "PIN OK" else "PIN MISMATCH"}")
            if (embSha != wantSha) refuse("${embDb.path} sha256 $embSha != the pin $wantSha")
            val embMeta = try { GemmaOwnBarNull.checkEmbMeta(embDb, arm) } catch (e: GemmaOwnBarNull.Refusal) { refuse(e.message ?: "emb meta") }
            val buildSha = GemmaOwnBarNull.sha256(buildDb)
            val textSha = GemmaOwnBarNull.textSetSha(train.texts)
            println("$tag build DB ${buildDb.path} sha256 $buildSha; meta arm=${train.meta["arm"]} corpus=${train.meta["corpus"]} salt=${train.meta["salt"]} " +
                "table_sha256=${train.meta["table_sha256"]}; TRAIN rows read ${train.texts.size} (GATE rows ${train.nGateRows} NOT read); " +
                "TRAIN text-set sha256 $textSha")
            val vectors = try { GemmaOwnBarNull.loadSlices(embDb, train.texts, arm.nativeDim, arm.sliceDim) } catch (e: GemmaOwnBarNull.Refusal) { refuse(e.message ?: "vectors") }
            if (GemmaOwnBarNull.sha256(embDb) != embSha) refuse("${embDb.path} changed during the read")
            sliceDimOverride = arm.sliceDim
            val config = canonicalConfig(GemmaOwnBarNull.MCS)
            if (config.formalism.embeddingSliceDim != arm.sliceDim || taxonomy.model.EmbeddingSlice.width != arm.sliceDim)
                refuse("slice ${arm.sliceDim} not applied (config ${config.formalism.embeddingSliceDim}, width ${taxonomy.model.EmbeddingSlice.width})")
            if (config.formalism.proposalSeparationBar != GemmaOwnBarNull.BAR_OF_RECORD) refuse("the null's bar ${config.formalism.proposalSeparationBar} != 0.025")
            val n = vectors.size
            val dim = arm.sliceDim
            val live = minOf(reps, Runtime.getRuntime().availableProcessors().coerceAtLeast(2))
            val peak = live.toLong() * n.toLong() * (55L * dim / 10L + 3L * 128L) * 8L     // certPcSize's heap formula
            val budget = (Runtime.getRuntime().maxMemory() * 0.90).toLong()
            println(taxonomy.runner.ThreadCap.line(peak, budget))
            println("[SITENULL-HEAP] sliceDim=%d n=%d live=%d -> peak live %.2f GB; budget %.2f GB".format(java.util.Locale.US, dim, n, live, peak / 1e9, budget / 1e9))
            if (peak > budget) refuse("heap: peak %.2f GB > budget %.2f GB; relaunch with -DsiteNullHeap=%dg"
                .format(java.util.Locale.US, peak / 1e9, budget / 1e9, kotlin.math.ceil(2.0 * peak / (1L shl 30)).toInt()))
            println("[SEPBAR] proposalSeparationBar=${config.formalism.proposalSeparationBar} (fixed 0.025); arm=${arm.name} model=${arm.model} sliceDim=$dim " +
                "dropTop=$dropTopProp whiten=$whitenProp reps=$reps minClusterSize=${GemmaOwnBarNull.MCS} n=$n")
            val splitter = cpcSplitter(GemmaOwnBarNull.MCS, scratchDb.absolutePath)
            val (mu, centered) = cpcMoments(vectors)
            val xs = cpcSiteArm(splitter, capture, "GOB", GemmaOwnBarNull.SEED_BASE, GemmaOwnBarNull.SITE_ID, mu, centered, n, reps)
            val p95 = GemmaOwnBarNull.p95(xs)
            println("$tag NULL arm=${arm.name} n=$n reps=$reps p95=${f6(p95)} max=${f6(xs.maxOrNull() ?: Double.NaN)} reached=${xs.count { it > 0.0 }}")
            GemmaOwnBarNull.writeNew(java.io.File(outDir, "replicates.csv"), "rep,stat\n" + xs.withIndex().joinToString("") { "${it.index},${it.value}\n" })
            GemmaOwnBarNull.writeNew(java.io.File(outDir, "status.txt"),
                "COMPLETE\nleg=null\narm=${arm.name}\nembedder=${arm.embedder}\nmodel=${arm.model}\nmodel_digest=${embMeta["model_digest"]}\n" +
                    "sliceDim=$dim\nnativeDim=${arm.nativeDim}\nsepBar=${config.formalism.proposalSeparationBar}\nminClusterSize=${GemmaOwnBarNull.MCS}\n" +
                    "dropTop=$dropTopProp\nwhiten=$whitenProp\nreps=$reps\nn_train=$n\nseedBase=${GemmaOwnBarNull.SEED_BASE}\nsiteId=${GemmaOwnBarNull.SITE_ID}\n" +
                    "build_db=${buildDb.path}\nbuild_db_sha256=$buildSha\nbuild_arm=${train.meta["arm"]}\nbuild_table_sha256=${train.meta["table_sha256"]}\n" +
                    "build_n_gate_rows_not_read=${train.nGateRows}\ntrain_text_set_sha256=$textSha\nemb_db=${embDb.path}\nemb_sha256=$embSha\n" +
                    "p95=$p95\nreached=${xs.count { it > 0.0 }}\nthreads=${Runtime.getRuntime().availableProcessors()}\n")
            println("$tag wrote ${outDir.path}: replicates.csv, status.txt (COMPLETE); the bar is the readout's")
        } finally {
            splitLog.detachAppender(capture); capture.stop(); splitLog.isAdditive = true
            sliceDimOverride = null
            taxonomy.model.EmbeddingSlice.width = savedWidth
            scratchDb.delete()
        }
    }

    // ── certKnownPair: CERT-PC-K2-KNOWN merged-pair sites (two declared categories merged; registered 2026-10-03) ──────────
    //
    // ADDITIONS ONLY, placed after every existing member (gemmaOwnBar included) so no existing method, field, lambda or
    // synthetic class of this file changes (proof in the commit message: every pre-existing member disassembles identically).
    // The method name contains none of the strings the existing filters match (siteNull, withinNull, isoNullByDim,
    // certPositiveControl, certPcSize, certPcK2, gemmaOwnBar); nullBySize excludes it explicitly. It runs only under
    // `gradlew certKnownPair`. It REUSES the reviewed members unchanged (pcsParseSites, pcsPopulation, pcsC0Seed, cpcDeclaredSite,
    // cpcRelabelNull, declaredSiteStatistic). What differs from certPcK2 is the SITE check ([kkpSiteError]) and no deflated null
    // (not registered for this test).

    /**
     * CERT-PC-K2-KNOWN site-file check (null = accepted, else the refusal reason). The first site is IDENTITY: the member root
     * region exactly ([rootIds]) with 14 declared categories. Then exactly three blocks, roles STRONG, MID, EDGE in that order,
     * each of 11 sites: KK_<role>_n<N>_d0 (the pair's FULL site, N its size), KK_<role>_n486_d1..5, KK_<role>_n441_d1..5. Every
     * site holds exactly its named n items; every label is the id's IDENTITY category; a block's labels are exactly two
     * categories (both present, each >= 100 items in the full site, the full site >= 972 items: the registered eligibility); every
     * subsample lies inside its full site; the three pairs differ.
     */
    internal fun kkpSiteError(parsed: List<Pair<String, Map<String, String>>>, rootIds: Set<String>): String? {
        // locals, never class properties: a property would add a field initialiser to the existing constructor
        val kkpRoles = listOf("STRONG", "MID", "EDGE")              // the registered roles, in the site file's order
        val kkpSizes = listOf(486, 441)                             // G12's depth-1 sizes (the registration)
        if (parsed.isEmpty() || parsed[0].first != "IDENTITY") return "the site file's first site is '${parsed.firstOrNull()?.first}', not IDENTITY"
        val ident = parsed[0].second
        if (ident.keys != rootIds) return "IDENTITY covers ${ident.size} ids; the member root region holds ${rootIds.size} (sets differ)"
        if (ident.values.toSet().size != 14) return "IDENTITY holds ${ident.values.toSet().size} declared categories, not the registered 14"
        val body = parsed.drop(1)
        if (body.size != kkpRoles.size * 11) return "the site file holds ${body.size} KK sites, not ${kkpRoles.size * 11} (3 pairs x (1 full + 2 sizes x 5 draws))"
        val rx = Regex("^KK_([A-Z]+)_n([0-9]+)_d([0-9]+)$")
        val pairs = mutableListOf<Set<String>>()
        for ((ri, role) in kkpRoles.withIndex()) {
            val block = body.subList(ri * 11, ri * 11 + 11)
            val (fullName, fullMap) = block[0]
            val mf = rx.matchEntire(fullName) ?: return "site '$fullName' is not KK_<role>_n<n>_d<draw>"
            if (mf.groupValues[1] != role || mf.groupValues[3] != "0") return "site '$fullName' where the $role full site KK_${role}_n<n>_d0 is expected"
            val cats = fullMap.values.toSet()
            if (cats.size != 2) return "site $fullName holds the labels ${cats.toSortedSet()}, not exactly two declared categories"
            val expected = listOf(fullName) + kkpSizes.flatMap { n -> (1..5).map { d -> "KK_${role}_n${n}_d$d" } }
            for ((j, entry) in block.withIndex()) {
                val (name, m) = entry
                if (name != expected[j]) return "site '$name' where '${expected[j]}' is expected"
                val mt = rx.matchEntire(name) ?: return "site '$name' is not KK_<role>_n<n>_d<draw>"
                if (mt.groupValues[2].toInt() != m.size) return "site $name holds ${m.size} items, not ${mt.groupValues[2]}"
                for ((id, c) in m) if (ident[id] != c) return "site $name: id $id is labelled '$c', IDENTITY says '${ident[id]}'"
                if (m.values.toSet() != cats) return "site $name holds the labels ${m.values.toSortedSet()}, not its pair's ${cats.toSortedSet()}"
                if (j > 0 && !fullMap.keys.containsAll(m.keys)) return "site $name holds ids outside its pair's full site $fullName"
            }
            if (fullMap.size < 2 * kkpSizes[0]) return "full site $fullName holds ${fullMap.size} items, fewer than ${2 * kkpSizes[0]} (eligibility)"
            val small = cats.map { c -> c to fullMap.values.count { it == c } }.filter { it.second < 100 }
            if (small.isNotEmpty()) return "full site $fullName: ${small.joinToString { "${it.first} ${it.second}" }} below 100 items (eligibility)"
            pairs.add(cats)
        }
        if (pairs.toSet().size != kkpRoles.size) return "the three roles do not name three different pairs: $pairs"
        return null
    }

    /**
     * CERT-PC-K2-KNOWN (`gradlew certKnownPair`; registration docs/judge_v2_program.md "## Registered 2026-10-03 (before any code
     * or call) — CERT-PC-K2-KNOWN: ..." L24036-L24052; site file and readout tools/analysis/cert_pc_k2_known.py --prepare /
     * --analyze). Zero calls. The instrument is certPcK2's (siteNull's generator and splitter at canonicalConfig(55) with the
     * run's -DsliceDim/-DsepBar/-DdropTop/-Dwhiten, siteNull's seeds, the declared-site routine); what is new is the SITE: two
     * declared categories merged, labelled by category (STRONG / MID / EDGE pairs chosen by the readout script's TRAIN-only stage 0,
     * pinned before this arm runs): the full pair site and stratified subsamples at n 486 / 441.
     * Order: IDENTITY (the full root region, 14 categories, plain null seeded by the root id: PC1's; refuses unless 0.107803 and
     * k = 0, before any pair site costs CPU) -> each KK site (its own plain null seeded by its name, C0 = 300 size-matched 2-group
     * relabellings seeded by [pcsC0Seed]; no deflated null). Writes, write-once into -DoutDir: sites.csv, replicates.csv,
     * status.txt (COMPLETE, or REFUSED with the reason). Verdicts are the readout's, never printed here.
     */
    @Test
    fun `certKnownPair - two declared categories merged into one site scored against their own site nulls`() {
        println(taxonomy.runner.ThreadCap.line(null, (Runtime.getRuntime().maxMemory() * 0.90).toLong()))
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val tag = "[PKK]"
        var outDirForStatus: java.io.File? = null
        fun refuse(msg: String): Nothing {
            println("$tag REFUSING: $msg")
            outDirForStatus?.let { d -> runCatching { java.io.File(d, "status.txt").writeText("REFUSED: $msg\n") } }
            error("$tag REFUSED: $msg")
        }
        fun prop(k: String): String = System.getProperty(k)?.takeIf { it.isNotBlank() } ?: refuse("-D$k is required")
        val snapshotId = prop("snapshotId")
        val sitesPath = java.io.File(prop("siteLabels"))
        val outDir = java.io.File(prop("outDir"))
        val embDb = unguardedEmbDb("certKnownPair")
        println("$tag reads ${embDb.path} (the qwen3 cache of record; -DembeddingCacheFile / -DembeddingModel refused)")
        if (!embDb.exists()) refuse("${embDb.path} not present")
        val reps = reps(300)
        if (outDir.exists() && (outDir.listFiles()?.isNotEmpty() == true)) refuse("${outDir.path} exists and is not empty (write-once)")
        outDir.mkdirs()
        outDirForStatus = outDir
        val mcs = 55
        val identityDeclared = "0.107803"   // CERT-PC-SIZE's IDENTITY PRECONDITION (PC1 of record), kept as the instrument check
        val identityK = 0

        val (snapId, g) = loadFrozenGraph(snapshotId) ?: refuse("snapshot $snapshotId not available")
        val byId = g.nodes.associateBy { it.id }
        val root = byId[g.rootId] ?: refuse("rootId ${g.rootId} not among the nodes")
        if (root.depth != 0) refuse("root ${root.id} has depth ${root.depth}")
        val isSite = { nd: taxonomy.service.SerialNode -> nd.childIds.size >= 2 && nd.dasguptaDeltaNorm > 0.0 }
        val sites = g.nodes.filter(isSite)
        val rootIds = regionQueryIds(root, byId).toList()

        val siteBytes = sitesPath.takeIf { it.isFile }?.readBytes() ?: refuse("site file ${sitesPath.path} not found")
        val siteSha = java.security.MessageDigest.getInstance("SHA-256").digest(siteBytes).joinToString("") { "%02x".format(it) }
        val parsed = try { pcsParseSites(String(siteBytes, Charsets.UTF_8)) } catch (e: IllegalArgumentException) { refuse(e.message ?: "site file") }
        kkpSiteError(parsed, rootIds.toSet())?.let { refuse(it) }
        val pops = parsed.map { (name, m) ->
            val pop = try { pcsPopulation(rootIds, m) } catch (e: IllegalArgumentException) { refuse("site $name: ${e.message}") }
            name to pop
        }
        println("$tag snapshot $snapId root ${root.id} '${root.label}' n=${rootIds.size}; site file ${sitesPath.path} sha256 $siteSha; " +
            "sites ${pops.size}; pairs ${pops.filter { it.first.endsWith("_d0") }.joinToString { "${it.first}=${it.second.second.joinToString(" + ")}" }}")

        val config = canonicalConfig(mcs)
        val dim = config.formalism.embeddingSliceDim
        val splitter = TaxonomySplitter(config, NoLlm, MMLUDatasetFetcher(config, ""), TaxonomyFitter(config))
        val capture = Capture()
        println("[SEPBAR] proposalSeparationBar=${config.formalism.proposalSeparationBar} (-DsepBar ${System.getProperty("sepBar")?.let { "'$it'" } ?: "absent -> default $DEFAULT_SEP_BAR"}); sliceDim=$dim dropTop=$dropTopProp whiten=$whitenProp reps=$reps minClusterSize=$mcs")

        val live = minOf(reps, Runtime.getRuntime().availableProcessors().coerceAtLeast(2))
        val peak = live.toLong() * rootIds.size.toLong() * (55L * dim / 10L + 3L * 128L) * 8L
        val budget = (Runtime.getRuntime().maxMemory() * 0.90).toLong()
        println(taxonomy.runner.ThreadCap.line(peak, budget))
        println("[SITENULL-HEAP] sliceDim=%d largest site n=%d live=%d -> peak live %.2f GB; budget %.2f GB"
            .format(java.util.Locale.US, dim, rootIds.size, live, peak / 1e9, budget / 1e9))
        if (peak > budget) refuse("heap: peak %.2f GB > budget %.2f GB; relaunch with -DsiteNullHeap=%dg"
            .format(java.util.Locale.US, peak / 1e9, budget / 1e9, kotlin.math.ceil(2.0 * peak / (1L shl 30)).toInt()))

        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        val vecById: Map<String, DoubleArray>
        val floats: Map<String, FloatArray>
        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { conn ->
            EmbedderReadGuard.run(conn, embDb.path, sites, { regionQueryIds(it, byId) }, dim,
                EmbedderReadGuard.resolveModel(null, null, false))
            vecById = loadVectorsById(conn, rootIds)
            floats = cpcLoadSliceFloats(conn, rootIds, dim)
        }
        if (vecById.size != rootIds.size || floats.size != rootIds.size)
            refuse("embedding cache miss: ${vecById.size} / ${floats.size} of ${rootIds.size} vectors")
        val embOf = HashMap<String, Embedding>()
        for (id in rootIds) embOf[id] = Embedding(rawText = id, distilledText = id, values = floats.getValue(id))

        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        capture.context = splitLog.loggerContext
        capture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(capture)
        fun esc(s: String) = "\"" + s.replace("\"", "\"\"") + "\""
        fun f6(x: Double) = "%.6f".format(java.util.Locale.US, x)
        fun newWriter(name: String) = java.nio.file.Files.newBufferedWriter(
            java.io.File(outDir, name).toPath(), Charsets.UTF_8, java.nio.file.StandardOpenOption.CREATE_NEW,
            java.nio.file.StandardOpenOption.WRITE)
        val childDim = taxonomy.model.dimForDepth(root.depth + 1)
        val siteRows = mutableListOf<String>()
        val repw = newWriter("replicates.csv")
        try {
            repw.write("site_id,arm,rep,stat\n")
            fun dumpReps(id: String, arm: String, xs: DoubleArray) { xs.forEachIndexed { i, x -> repw.write("${esc(id)},$arm,$i,$x\n") } }
            for ((idx, entry) in pops.withIndex()) {
                val (name, pop) = entry
                val (ids, cats, groups) = pop
                val vectors = ids.map { vecById.getValue(it) }
                val embs = ids.map { embOf.getValue(it) }
                val identity = idx == 0
                val seedId = if (identity) root.id else name
                val res = cpcDeclaredSite(splitter, capture, seedId, root.depth, vectors, embs, groups, reps, deflated = false)
                dumpReps(name, "SN", res.plain)
                var c0p95 = Double.NaN
                var c0Seed = -1L
                if (identity) {
                    println("$tag IDENTITY n=${ids.size} declared=%s k=%d (registered %s, k %d) plain p95=%.6f max=%.6f".format(
                        java.util.Locale.US, f6(res.declared), res.kDeclared, identityDeclared, identityK,
                        percentile(res.plain.sorted(), 0.95), res.plain.maxOrNull() ?: Double.NaN))
                    repw.flush()
                    if (f6(res.declared) != identityDeclared || res.kDeclared != identityK)
                        refuse("IDENTITY FAILED: the full-size root gives declared ${f6(res.declared)} k ${res.kDeclared}, not $identityDeclared k $identityK; no KK site run")
                } else {
                    c0Seed = pcsC0Seed(name)
                    val labels = IntArray(ids.size)
                    groups.forEachIndexed { c, gg -> gg.forEach { labels[it] = c } }
                    val c0 = cpcRelabelNull(embs, labels, cats.size, reps, c0Seed, childDim)
                    dumpReps(name, "C0", c0)
                    c0p95 = percentile(c0.sorted(), 0.95)
                    println("$tag site %-20s n=%4d groups=%s %s declared=%.6f k=%3d plain p95=%.6f reached=%3d C0 p95=%.6f (seed %d)".format(
                        java.util.Locale.US, name, ids.size, groups.map { it.size }, cats, res.declared, res.kDeclared,
                        percentile(res.plain.sorted(), 0.95), res.plain.count { it > 0.0 }, c0p95, c0Seed))
                }
                siteRows.add(listOf(if (identity) "IDENTITY" else "KK", esc(name), ids.size, groups.size,
                    groups.joinToString("/") { it.size.toString() },
                    res.declared, res.kDeclared, "", "",
                    if (identity) "" else c0p95, if (identity) "" else c0Seed, seedId, reps).joinToString(","))
                repw.flush()
            }
        } finally {
            runCatching { repw.close() }
            splitLog.detachAppender(capture); capture.stop(); splitLog.isAdditive = true
        }
        newWriter("sites.csv").use { w ->
            w.write("role,site_id,n,groups,group_sizes,declared_stat,k_declared,defl_dims,defl_k_declared,c0_p95,c0_seed,null_seed_id,reps\n")
            siteRows.forEach { w.write(it + "\n") }
        }
        newWriter("status.txt").use { w ->
            w.write("COMPLETE\narm=certKnownPair\nsnapshot=$snapId\nsites_sha256=$siteSha\nreps=$reps\nsliceDim=$dim\nsepBar=${config.formalism.proposalSeparationBar}\n" +
                "dropTop=$dropTopProp\nwhiten=$whitenProp\nminClusterSize=$mcs\nc0Seed=20261002\n" +
                "threads=${Runtime.getRuntime().availableProcessors()}\n")
        }
        println("$tag wrote ${outDir.path}: sites.csv, replicates.csv, status.txt (COMPLETE); verdicts are the readout's")
    }

    // ── certK2Deflated: CERT-K2-DEFLATED deflated-only declared sites, fresh seeds (registered 2026-10-04) ───────────────
    //
    // ADDITIONS ONLY, placed after every existing member (certKnownPair included) so no existing method, field, lambda or
    // synthetic class of this file changes (proof in the commit message: every pre-existing member disassembles identically).
    // The method name contains none of the strings the existing filters match (siteNull, withinNull, isoNullByDim,
    // certPositiveControl, certPcSize, certPcK2, gemmaOwnBar, certKnownPair); nullBySize excludes it explicitly. It runs only under
    // `gradlew certK2Deflated`. It REUSES the reviewed members unchanged (pcsParseSites, pcsPopulation, kkpSiteError, pk2SiteError,
    // cpcMoments, cpcDeflate, cpcSiteArm, cpcSeed, declaredSiteStatistic). What is new: the site check [dflSiteError] (the KK and K2
    // blocks through the existing checks, the K2 block's structure, the negative-control block) and [dflDeflatedSite] (the deflated
    // null alone, seed base [dflSeedBase] = the registration's fresh 20261004; no plain null, no C0: not registered).

    /**
     * CERT-K2-DEFLATED site-file check (null = accepted, else the refusal reason). IDENTITY (the member root, 14 categories), then
     * exactly 86 sites: (i) the 33 KK sites of CERT-PC-K2-KNOWN (checked by [kkpSiteError] unchanged); (ii) 33 K2 sites, per anchor
     * economics, math, physics in that order K2_<a>_n<N>_d0 (the anchor's FULL source-split site, N >= 486), K2_<a>_n486_d1..5,
     * K2_<a>_n441_d1..5 (checked by [pk2SiteError] unchanged; here also: the order, every id's IDENTITY category is the anchor, every
     * subsample inside its full site); (iii) 20 negative-control sites NC_STRONG_n486_s1..10 (the ids of KK_STRONG_n486_d1) and
     * NC_math_n486_s1..10 (the ids of K2_math_n486_d1), labels exactly rel_a / rel_b, size-matched (rel_a's count = the count of the
     * source site's first label in sorted order), and the relabelling is not the source partition (nor its complement).
     */
    internal fun dflSiteError(parsed: List<Pair<String, Map<String, String>>>, rootIds: Set<String>): String? {
        // locals, never class properties: a property would add a field initialiser to the existing constructor
        val dflAnchors = listOf("economics", "math", "physics")
        val dflNcSources = listOf("STRONG" to "KK_STRONG_n486_d1", "math" to "K2_math_n486_d1")
        if (parsed.isEmpty() || parsed[0].first != "IDENTITY") return "the site file's first site is '${parsed.firstOrNull()?.first}', not IDENTITY"
        if (parsed.size != 1 + 33 + 33 + 20) return "the site file holds ${parsed.size - 1} sites after IDENTITY, not 86 (33 KK + 33 K2 + 20 NC)"
        val ident = parsed[0].second
        val kk = parsed.subList(1, 34)
        val k2 = parsed.subList(34, 67)
        val nc = parsed.subList(67, 87)
        kkpSiteError(listOf(parsed[0]) + kk, rootIds)?.let { return "KK block: $it" }
        pk2SiteError(listOf(parsed[0]) + k2, rootIds)?.let { return "K2 block: $it" }
        val full = Regex("^K2_([a-z]+)_n([0-9]+)_d0$")
        for ((ai, a) in dflAnchors.withIndex()) {
            val block = k2.subList(ai * 11, ai * 11 + 11)
            val (fullName, fullMap) = block[0]
            val mf = full.matchEntire(fullName)
            if (mf == null || mf.groupValues[1] != a) return "site '$fullName' where the $a full site K2_${a}_n<N>_d0 is expected"
            if (fullMap.size < 486) return "full site $fullName holds ${fullMap.size} items, fewer than 486"
            val expected = listOf(fullName) + listOf(486, 441).flatMap { n -> (1..5).map { d -> "K2_${a}_n${n}_d$d" } }
            for ((j, entry) in block.withIndex()) {
                val (name, m) = entry
                if (name != expected[j]) return "site '$name' where '${expected[j]}' is expected"
                for (id in m.keys) if (ident[id] != a) return "site $name: id $id is IDENTITY category '${ident[id]}', not the anchor '$a'"
                if (j > 0 && !fullMap.keys.containsAll(m.keys)) return "site $name holds ids outside its anchor's full site $fullName"
            }
        }
        val byName = parsed.associate { it.first to it.second }
        val ncLabels = setOf("rel_a", "rel_b")
        for ((bi, src) in dflNcSources.withIndex()) {
            val (tag, srcName) = src
            val srcMap = byName.getValue(srcName)
            val first = srcMap.values.toSortedSet().first()
            val srcFirstIds = srcMap.filterValues { it == first }.keys
            val srcOtherIds = srcMap.keys - srcFirstIds
            for (s in 1..10) {
                val (name, m) = nc[bi * 10 + s - 1]
                val want = "NC_${tag}_n486_s$s"
                if (name != want) return "site '$name' where '$want' is expected"
                if (m.keys != srcMap.keys) return "site $name does not hold exactly the ids of its source $srcName"
                if (m.values.toSet() != ncLabels) return "site $name holds the labels ${m.values.toSortedSet()}, not exactly $ncLabels"
                val relA = m.filterValues { it == "rel_a" }.keys
                if (relA.size != srcFirstIds.size) return "site $name: rel_a holds ${relA.size} ids, its source's '$first' ${srcFirstIds.size} (not size-matched)"
                if (relA == srcFirstIds || relA == srcOtherIds) return "site $name reproduces its source's declared partition"
            }
        }
        return null
    }

    /** CERT-K2-DEFLATED's fresh seed base (the registration's "seed base 20261004, per site name"): cpcSeed(DFL_SEED_BASE, site, rep). */
    internal fun dflSeedBase(): Long = 20261004L

    /**
     * CERT-K2-DEFLATED amended site file (pre-data amendment 26605924, READY_cert_k2_deflated B-1 option (b)): the 87 sites of
     * [dflSiteError] (checked unchanged on the first 87) followed by exactly 10 ELONGATION-CUT CONTROL sites EC_STRONG_n486_d1..5,
     * EC_MID_n486_d1..5: each holds exactly the ids of KK_<role>_n486_d<d>, the labels exactly pc_hi / pc_lo (the cut at the median
     * of the site's first principal axis, computed by the readout script and rebuild-checked there; ties to the lower half, so pc_lo
     * holds at least half), and the cut is not the site's declared partition (nor its complement). Null = accepted.
     */
    internal fun dflEcError(parsed: List<Pair<String, Map<String, String>>>, rootIds: Set<String>): String? {
        if (parsed.size != 87 + 10) return "the site file holds ${parsed.size - 1} sites after IDENTITY, not 96 (33 KK + 33 K2 + 20 NC + 10 EC)"
        dflSiteError(parsed.subList(0, 87), rootIds)?.let { return it }
        val byName = parsed.subList(0, 87).associate { it.first to it.second }
        val ecLabels = setOf("pc_hi", "pc_lo")
        var i = 87
        for (role in listOf("STRONG", "MID")) for (d in 1..5) {
            val (name, m) = parsed[i++]
            val want = "EC_${role}_n486_d$d"
            if (name != want) return "site '$name' where '$want' is expected"
            val src = byName.getValue("KK_${role}_n486_d$d")
            if (m.keys != src.keys) return "site $name does not hold exactly the ids of KK_${role}_n486_d$d"
            if (m.values.toSet() != ecLabels) return "site $name holds the labels ${m.values.toSortedSet()}, not exactly $ecLabels"
            val lo = m.filterValues { it == "pc_lo" }.keys
            if (2 * lo.size < m.size) return "site $name: pc_lo holds ${lo.size} of ${m.size} ids, fewer than half (ties go to the lower half)"
            val first = src.values.toSortedSet().first()
            val srcFirst = src.filterValues { it == first }.keys
            if (lo == srcFirst || lo == src.keys - srcFirst) return "site $name reproduces the declared partition of KK_${role}_n486_d$d"
        }
        return null
    }

    internal data class DflSite(val declared: Double, val defl: DoubleArray, val deflDims: Int, val kDefl: Int)

    /**
     * One CERT-K2-DEFLATED site: the declared statistic of [groups] by the routine, and the DEFLATED null alone: the declared groups'
     * between-centroid subspace (k - 1 dims; [cpcDeflate], siteNull's deflation) projected out of the centred rows, the mean kept,
     * driven through [cpcSiteArm] with tag SNDF and the fresh seed base [dflSeedBase] (never siteNull's 88820260908, whose replicates
     * of the same site names are on disk). k = the number of deflated replicates >= the declared statistic.
     */
    internal fun dflDeflatedSite(
        splitter: TaxonomySplitter, capture: AppenderBase<ILoggingEvent>, siteId: String, depth: Int,
        vectors: List<DoubleArray>, embs: List<Embedding>, groups: List<List<Int>>, reps: Int
    ): DflSite {
        val declared = declaredSiteStatistic(groups.map { g -> g.map { embs[it] } }, taxonomy.model.dimForDepth(depth + 1))
        val (mu, centered) = cpcMoments(vectors)
        val (dc, d) = cpcDeflate(vectors, centered, groups)
        val defl = cpcSiteArm(splitter, capture, "SNDF", dflSeedBase(), siteId, mu, dc, vectors.size, reps)
        return DflSite(declared, defl, d, defl.count { it >= declared })
    }

    /**
     * CERT-K2-DEFLATED (`gradlew certK2Deflated`; registration docs/judge_v2_program.md "## Registered 2026-10-04 (before any code
     * or call) — CERT-K2-DEFLATED: ..." L24123-L24141; site file and readout tools/analysis/cert_k2_deflated.py --prepare /
     * --analyze). Zero calls. The instrument is certKnownPair's (siteNull's generator and splitter at canonicalConfig(55) with the
     * run's -DsliceDim/-DsepBar/-DdropTop/-Dwhiten, the declared-site routine); what differs: the null is the DEFLATED one only
     * ([dflDeflatedSite], fresh seed base 20261004 per site name), no plain null and no C0 (not registered), and the sites are
     * [dflEcError]'s 96 (amended 26605924: + 10 elongation-cut controls). Order: IDENTITY (the full root region, 14 categories: the declared statistic only, no null; refuses unless
     * it prints 0.107803, before any site costs CPU) -> each site (its deflated null). Writes, write-once into -DoutDir: sites.csv,
     * replicates.csv (arm SNDF), status.txt (COMPLETE, or REFUSED with the reason). Verdicts are the readout's, never printed here.
     */
    @Test
    fun `certK2Deflated - declared two-group sites scored against their own deflated null with fresh seeds`() {
        println(taxonomy.runner.ThreadCap.line(null, (Runtime.getRuntime().maxMemory() * 0.90).toLong()))
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val tag = "[DFL]"
        var outDirForStatus: java.io.File? = null
        fun refuse(msg: String): Nothing {
            println("$tag REFUSING: $msg")
            outDirForStatus?.let { d -> runCatching { java.io.File(d, "status.txt").writeText("REFUSED: $msg\n") } }
            error("$tag REFUSED: $msg")
        }
        fun prop(k: String): String = System.getProperty(k)?.takeIf { it.isNotBlank() } ?: refuse("-D$k is required")
        val snapshotId = prop("snapshotId")
        val sitesPath = java.io.File(prop("siteLabels"))
        val outDir = java.io.File(prop("outDir"))
        val embDb = unguardedEmbDb("certK2Deflated")
        println("$tag reads ${embDb.path} (the qwen3 cache of record; -DembeddingCacheFile / -DembeddingModel refused)")
        if (!embDb.exists()) refuse("${embDb.path} not present")
        val reps = reps(300)
        if (outDir.exists() && (outDir.listFiles()?.isNotEmpty() == true)) refuse("${outDir.path} exists and is not empty (write-once)")
        outDir.mkdirs()
        outDirForStatus = outDir
        val mcs = 55
        val identityDeclared = "0.107803"   // CERT-PC-SIZE's IDENTITY statistic (PC1 of record), kept as the instrument check
        val seedBase = dflSeedBase()

        val (snapId, g) = loadFrozenGraph(snapshotId) ?: refuse("snapshot $snapshotId not available")
        val byId = g.nodes.associateBy { it.id }
        val root = byId[g.rootId] ?: refuse("rootId ${g.rootId} not among the nodes")
        if (root.depth != 0) refuse("root ${root.id} has depth ${root.depth}")
        val isSite = { nd: taxonomy.service.SerialNode -> nd.childIds.size >= 2 && nd.dasguptaDeltaNorm > 0.0 }
        val sites = g.nodes.filter(isSite)
        val rootIds = regionQueryIds(root, byId).toList()

        val siteBytes = sitesPath.takeIf { it.isFile }?.readBytes() ?: refuse("site file ${sitesPath.path} not found")
        val siteSha = java.security.MessageDigest.getInstance("SHA-256").digest(siteBytes).joinToString("") { "%02x".format(it) }
        val parsed = try { pcsParseSites(String(siteBytes, Charsets.UTF_8)) } catch (e: IllegalArgumentException) { refuse(e.message ?: "site file") }
        dflEcError(parsed, rootIds.toSet())?.let { refuse(it) }
        val pops = parsed.map { (name, m) ->
            val pop = try { pcsPopulation(rootIds, m) } catch (e: IllegalArgumentException) { refuse("site $name: ${e.message}") }
            name to pop
        }
        println("$tag snapshot $snapId root ${root.id} '${root.label}' n=${rootIds.size}; site file ${sitesPath.path} sha256 $siteSha; " +
            "sites ${pops.size} (IDENTITY + 33 KK + 33 K2 + 20 NC + 10 EC); deflated seed base $seedBase")

        val config = canonicalConfig(mcs)
        val dim = config.formalism.embeddingSliceDim
        val splitter = TaxonomySplitter(config, NoLlm, MMLUDatasetFetcher(config, ""), TaxonomyFitter(config))
        val capture = Capture()
        println("[SEPBAR] proposalSeparationBar=${config.formalism.proposalSeparationBar} (-DsepBar ${System.getProperty("sepBar")?.let { "'$it'" } ?: "absent -> default $DEFAULT_SEP_BAR"}); sliceDim=$dim dropTop=$dropTopProp whiten=$whitenProp reps=$reps minClusterSize=$mcs")

        val nMax = pops.drop(1).maxOf { it.second.first.size }      // IDENTITY runs no null: the largest null site
        val live = minOf(reps, Runtime.getRuntime().availableProcessors().coerceAtLeast(2))
        val peak = live.toLong() * nMax.toLong() * (55L * dim / 10L + 3L * 128L) * 8L
        val budget = (Runtime.getRuntime().maxMemory() * 0.90).toLong()
        println(taxonomy.runner.ThreadCap.line(peak, budget))
        println("[SITENULL-HEAP] sliceDim=%d largest null site n=%d live=%d -> peak live %.2f GB; budget %.2f GB"
            .format(java.util.Locale.US, dim, nMax, live, peak / 1e9, budget / 1e9))
        if (peak > budget) refuse("heap: peak %.2f GB > budget %.2f GB; relaunch with -DsiteNullHeap=%dg"
            .format(java.util.Locale.US, peak / 1e9, budget / 1e9, kotlin.math.ceil(2.0 * peak / (1L shl 30)).toInt()))

        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        val vecById: Map<String, DoubleArray>
        val floats: Map<String, FloatArray>
        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { conn ->
            EmbedderReadGuard.run(conn, embDb.path, sites, { regionQueryIds(it, byId) }, dim,
                EmbedderReadGuard.resolveModel(null, null, false))
            vecById = loadVectorsById(conn, rootIds)
            floats = cpcLoadSliceFloats(conn, rootIds, dim)
        }
        if (vecById.size != rootIds.size || floats.size != rootIds.size)
            refuse("embedding cache miss: ${vecById.size} / ${floats.size} of ${rootIds.size} vectors")
        val embOf = HashMap<String, Embedding>()
        for (id in rootIds) embOf[id] = Embedding(rawText = id, distilledText = id, values = floats.getValue(id))

        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        capture.context = splitLog.loggerContext
        capture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(capture)
        fun esc(s: String) = "\"" + s.replace("\"", "\"\"") + "\""
        fun f6(x: Double) = "%.6f".format(java.util.Locale.US, x)
        fun newWriter(name: String) = java.nio.file.Files.newBufferedWriter(
            java.io.File(outDir, name).toPath(), Charsets.UTF_8, java.nio.file.StandardOpenOption.CREATE_NEW,
            java.nio.file.StandardOpenOption.WRITE)
        val siteRows = mutableListOf<String>()
        val repw = newWriter("replicates.csv")
        try {
            repw.write("site_id,arm,rep,stat\n")
            for ((idx, entry) in pops.withIndex()) {
                val (name, pop) = entry
                val (ids, _, groups) = pop
                val embs = ids.map { embOf.getValue(it) }
                if (idx == 0) {
                    val d0 = declaredSiteStatistic(groups.map { gg -> gg.map { embs[it] } }, taxonomy.model.dimForDepth(root.depth + 1))
                    println("$tag IDENTITY n=${ids.size} declared=%s (registered %s; no null drawn)".format(java.util.Locale.US, f6(d0), identityDeclared))
                    if (f6(d0) != identityDeclared) refuse("IDENTITY FAILED: the full-size root gives declared ${f6(d0)}, not $identityDeclared; no site run")
                    siteRows.add(listOf("IDENTITY", esc(name), ids.size, groups.size, groups.joinToString("/") { it.size.toString() },
                        d0, "", "", "", "", "", "", root.id, reps).joinToString(","))
                    continue
                }
                val vectors = ids.map { vecById.getValue(it) }
                val res = dflDeflatedSite(splitter, capture, name, root.depth, vectors, embs, groups, reps)
                res.defl.forEachIndexed { i, x -> repw.write("${esc(name)},SNDF,$i,$x\n") }
                val sorted = res.defl.sorted()
                val reached = res.defl.count { it > 0.0 }
                val role = name.substringBefore('_')
                println("$tag site %-20s n=%4d groups=%s declared=%.6f deflated dims=%d k=%3d p50=%.6f p95=%.6f reached=%3d (seed base %d)".format(
                    java.util.Locale.US, name, ids.size, groups.map { it.size }, res.declared, res.deflDims, res.kDefl,
                    percentile(sorted, 0.50), percentile(sorted, 0.95), reached, seedBase))
                siteRows.add(listOf(role, esc(name), ids.size, groups.size, groups.joinToString("/") { it.size.toString() },
                    res.declared, res.deflDims, res.kDefl, percentile(sorted, 0.50), percentile(sorted, 0.95), reached, seedBase,
                    name, reps).joinToString(","))
                repw.flush()
            }
        } finally {
            runCatching { repw.close() }
            splitLog.detachAppender(capture); capture.stop(); splitLog.isAdditive = true
        }
        newWriter("sites.csv").use { w ->
            w.write("role,site_id,n,groups,group_sizes,declared_stat,defl_dims,defl_k_declared,defl_p50,defl_p95,defl_reached,defl_seed_base,null_seed_id,reps\n")
            siteRows.forEach { w.write(it + "\n") }
        }
        newWriter("status.txt").use { w ->
            w.write("COMPLETE\narm=certK2Deflated\nsnapshot=$snapId\nsites_sha256=$siteSha\nreps=$reps\nsliceDim=$dim\nsepBar=${config.formalism.proposalSeparationBar}\n" +
                "dropTop=$dropTopProp\nwhiten=$whitenProp\nminClusterSize=$mcs\ndeflSeedBase=$seedBase\n" +
                "threads=${Runtime.getRuntime().availableProcessors()}\n")
        }
        println("$tag wrote ${outDir.path}: sites.csv, replicates.csv, status.txt (COMPLETE); verdicts are the readout's")
    }

    // ── certPlanted: CERT-PLANTED planted two-way shift sites (registered 2026-10-04) ─────────────────────────────────────────
    //
    // ADDITIONS ONLY, placed after every existing member (certKnownPair included) so no existing method, field, lambda or
    // synthetic class of this file changes (proof in the commit message: every pre-existing member disassembles identically).
    // The filters of siteNull, withinNull, isoNullByDim, certPositiveControl, certPcSize, certPcK2, gemmaOwnBar and certKnownPair
    // do not match this method's name; nullBySize excludes it explicitly. It runs only under `gradlew certPlanted` (and, on
    // fixtures, its members from CertPlantedArmTest). It REUSES the reviewed members unchanged (pcsParseSites, pcsPopulation,
    // cpcDeclaredSite, declaredSiteStatistic, loadVectorsById, cpcLoadSliceFloats). What is new is the INPUT MODE: the site's
    // vectors are read from a planted-vector file written by tools/analysis/cert_planted.py --prepare (TRAIN only, seeds and
    // directions pinned there), not from the cache; the cache is read for IDENTITY and for the PLANT CHECK only.

    /**
     * CERT-PLANTED site-file check (null = accepted, else the refusal reason). [siteSeq] = the site column of every data row in
     * file order. The first site is IDENTITY: the member root region exactly ([rootIds]) with 14 declared categories. Every other
     * site is PL_<anchor>_n<n>_d<draw>_D<delta> (anchor economics / math / physics, delta 0 / 2 / 4 / 6 / 8 / 10 / 12; amended 2fc67857), holds exactly n items
     * labelled exactly {hi, lo} with half sizes differing by at most one; the deltas of one population PL_<anchor>_n<n>_d<draw>
     * hold the same ids with the same halves, and every population carries its delta-0 site (the PLANT CHECK's anchor). Rows are
     * contiguous per site (the vector file follows the site file's row order).
     */
    internal fun cplSiteError(parsed: List<Pair<String, Map<String, String>>>, rootIds: Set<String>, siteSeq: List<String>): String? {
        // locals, never class properties: a property would add a field initialiser to the existing constructor
        val cplAnchors = listOf("economics", "math", "physics")      // the registered categories
        val cplLabels = setOf("hi", "lo")                            // the planted halves (+delta / -delta)
        if (parsed.isEmpty() || parsed[0].first != "IDENTITY") return "the site file's first site is '${parsed.firstOrNull()?.first}', not IDENTITY"
        val ident = parsed[0].second
        if (ident.keys != rootIds) return "IDENTITY covers ${ident.size} ids; the member root region holds ${rootIds.size} (sets differ)"
        if (ident.values.toSet().size != 14) return "IDENTITY holds ${ident.values.toSet().size} declared categories, not the registered 14"
        if (parsed.size < 2) return "the site file holds no PL site"
        val runs = siteSeq.indices.count { it == 0 || siteSeq[it] != siteSeq[it - 1] }
        if (runs != parsed.size) return "the site file's rows are not contiguous per site ($runs runs for ${parsed.size} sites)"
        val rx = Regex("^PL_([a-z]+)_n([0-9]+)_d([0-9]+)_D(0|2|4|6|8|10|12)$")
        val byPop = LinkedHashMap<String, Map<String, String>>()
        val withD0 = HashSet<String>()
        for ((name, m) in parsed.drop(1)) {
            val mt = rx.matchEntire(name) ?: return "site '$name' is not PL_<anchor>_n<n>_d<draw>_D<delta> (delta 0 / 2 / 4 / 6 / 8 / 10 / 12)"
            if (mt.groupValues[1] !in cplAnchors) return "site $name: anchor '${mt.groupValues[1]}' is not one of $cplAnchors"
            if (mt.groupValues[2].toInt() != m.size) return "site $name holds ${m.size} items, not ${mt.groupValues[2]}"
            if (m.values.toSet() != cplLabels) return "site $name holds the labels ${m.values.toSortedSet()}, not exactly $cplLabels"
            val hi = m.values.count { it == "hi" }
            if (kotlin.math.abs(hi - (m.size - hi)) > 1) return "site $name: halves hi $hi / lo ${m.size - hi} are not a half-split"
            val pop = "PL_${mt.groupValues[1]}_n${mt.groupValues[2]}_d${mt.groupValues[3]}"
            val prev = byPop.putIfAbsent(pop, m)
            if (prev != null && prev != m) return "site $name: ids or halves differ from the other deltas of $pop"
            if (mt.groupValues[4] == "0") withD0.add(pop)
        }
        val noD0 = byPop.keys.filter { it !in withD0 }
        if (noD0.isNotEmpty()) return "population(s) without a delta-0 site: ${noD0.take(3)}"
        return null
    }

    /**
     * The planted-vector file: big-endian float32 (the cache's byte order), [dim] floats per row, one row per PL-site row in the
     * site file's order (IDENTITY carries no row). Returns site -> (id -> floats). Refuses (IllegalArgumentException) a file whose
     * size is not rows x dim x 4.
     */
    internal fun cplReadVectors(bytes: ByteArray, parsed: List<Pair<String, Map<String, String>>>, dim: Int): Map<String, Map<String, FloatArray>> {
        val rows = parsed.drop(1).sumOf { it.second.size }
        require(bytes.size.toLong() == rows.toLong() * dim * 4L) {
            "the planted-vector file holds ${bytes.size} bytes, not $rows rows x $dim floats x 4 = ${rows.toLong() * dim * 4L}"
        }
        val buf = java.nio.ByteBuffer.wrap(bytes)
        val out = LinkedHashMap<String, Map<String, FloatArray>>()
        for ((name, m) in parsed.drop(1)) {
            val per = LinkedHashMap<String, FloatArray>()
            for (id in m.keys) per[id] = FloatArray(dim) { buf.getFloat() }
            out[name] = per
        }
        return out
    }

    /** loadVectorsById's row rule on a float row: the floats as doubles divided by their L2 norm (a zero row stays zero). */
    internal fun cplUnit(f: FloatArray): DoubleArray {
        val v = DoubleArray(f.size) { f[it].toDouble() }
        var norm = 0.0
        for (x in v) norm += x * x
        norm = sqrt(norm)
        if (norm > 0) for (i in v.indices) v[i] /= norm
        return v
    }

    internal data class CplCheck(val error: String?, val d0MaxDiff: Double, val normMaxDev: Double, val d0Sites: Int)

    /**
     * PLANT CHECK (before any null costs CPU): (a) every planted row's float L2 norm lies within 1e-5 of 1 (the script renormalises
     * every row); (b) every delta-0 site's rows equal the cache's slice vectors of the same ids as loadVectorsById normalises them,
     * max |diff| <= 1e-6 (so the planted file was built from these ids' vectors, in this slice, in this row order).
     */
    internal fun cplPlantCheck(planted: Map<String, Map<String, FloatArray>>, vecById: Map<String, DoubleArray>): CplCheck {
        var d0Max = 0.0
        var normMax = 0.0
        var d0Sites = 0
        for ((name, rows) in planted) {
            val isD0 = name.endsWith("_D0")
            if (isD0) d0Sites++
            for ((id, f) in rows) {
                var nn = 0.0
                for (x in f) nn += x.toDouble() * x.toDouble()
                val dev = kotlin.math.abs(sqrt(nn) - 1.0)
                if (dev > normMax) normMax = dev
                if (dev > 1e-5) return CplCheck("site $name id $id: planted row norm ${sqrt(nn)} is not 1 (|dev| > 1e-5)", d0Max, normMax, d0Sites)
                if (isD0) {
                    val ref = vecById[id] ?: return CplCheck("site $name id $id: no cache vector for the PLANT CHECK", d0Max, normMax, d0Sites)
                    if (ref.size != f.size) return CplCheck("site $name id $id: cache slice ${ref.size} floats, planted ${f.size}", d0Max, normMax, d0Sites)
                    val u = cplUnit(f)
                    for (i in u.indices) { val d = kotlin.math.abs(u[i] - ref[i]); if (d > d0Max) d0Max = d }
                    if (d0Max > 1e-6) return CplCheck("site $name id $id: the delta-0 row differs from the cache's slice vector (max |diff| $d0Max > 1e-6)", d0Max, normMax, d0Sites)
                }
            }
        }
        if (d0Sites == 0) return CplCheck("no delta-0 site: the PLANT CHECK has no anchor", d0Max, normMax, 0)
        return CplCheck(null, d0Max, normMax, d0Sites)
    }

    /**
     * CERT-PLANTED (`gradlew certPlanted`; registration docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or
     * call) — CERT-PLANTED: ..." L24304-L24315; planted files and readout tools/analysis/cert_planted.py --prepare / --analyze).
     * Zero calls. The instrument is certPcK2's declared-site path (siteNull's generator and splitter at canonicalConfig(55) with the
     * run's -DsliceDim/-DsepBar/-DdropTop/-Dwhiten, siteNull's seeds, the declared-site routine, the plain site null of record);
     * what is new is the INPUT MODE: each PL site's vectors are the planted rows of -DplantedVectors and its declared 2-way groups
     * are the planted halves (hi / lo) of -DsiteLabels.
     * Order: IDENTITY (the full root region from the cache, 14 categories, plain null seeded by the root id: PC1's; refuses unless
     * 0.107803 and k = 0) after the PLANT CHECK ([cplPlantCheck]) and before any PL site costs CPU -> each PL site (its own plain
     * null seeded by its name, moment-matched to its PLANTED population; no deflated null, no C0: not registered). Writes,
     * write-once into -DoutDir: sites.csv, replicates.csv, status.txt (COMPLETE, or REFUSED with the reason). Verdicts are the
     * readout's, never printed here.
     */
    @Test
    fun `certPlanted - planted two-way shift sites scored against their own site nulls`() {
        println(taxonomy.runner.ThreadCap.line(null, (Runtime.getRuntime().maxMemory() * 0.90).toLong()))
        (LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger).level = Level.WARN
        val tag = "[CPL]"
        var outDirForStatus: java.io.File? = null
        fun refuse(msg: String): Nothing {
            println("$tag REFUSING: $msg")
            outDirForStatus?.let { d -> runCatching { java.io.File(d, "status.txt").writeText("REFUSED: $msg\n") } }
            error("$tag REFUSED: $msg")
        }
        fun prop(k: String): String = System.getProperty(k)?.takeIf { it.isNotBlank() } ?: refuse("-D$k is required")
        fun sha256(b: ByteArray) = java.security.MessageDigest.getInstance("SHA-256").digest(b).joinToString("") { "%02x".format(it) }
        val snapshotId = prop("snapshotId")
        val sitesPath = java.io.File(prop("siteLabels"))
        val vecPath = java.io.File(prop("plantedVectors"))
        val outDir = java.io.File(prop("outDir"))
        val embDb = unguardedEmbDb("certPlanted")
        println("$tag reads ${embDb.path} (the qwen3 cache of record, for IDENTITY and the PLANT CHECK; -DembeddingCacheFile / -DembeddingModel refused)")
        if (!embDb.exists()) refuse("${embDb.path} not present")
        val reps = reps(300)
        if (outDir.exists() && (outDir.listFiles()?.isNotEmpty() == true)) refuse("${outDir.path} exists and is not empty (write-once)")
        outDir.mkdirs()
        outDirForStatus = outDir
        val mcs = 55
        val identityDeclared = "0.107803"   // CERT-PC-SIZE's IDENTITY PRECONDITION (PC1 of record), kept as the instrument check
        val identityK = 0

        val (snapId, g) = loadFrozenGraph(snapshotId) ?: refuse("snapshot $snapshotId not available")
        val byId = g.nodes.associateBy { it.id }
        val root = byId[g.rootId] ?: refuse("rootId ${g.rootId} not among the nodes")
        if (root.depth != 0) refuse("root ${root.id} has depth ${root.depth}")
        val isSite = { nd: taxonomy.service.SerialNode -> nd.childIds.size >= 2 && nd.dasguptaDeltaNorm > 0.0 }
        val sites = g.nodes.filter(isSite)
        val rootIds = regionQueryIds(root, byId).toList()

        val siteBytes = sitesPath.takeIf { it.isFile }?.readBytes() ?: refuse("site file ${sitesPath.path} not found")
        val siteSha = sha256(siteBytes)
        val siteText = String(siteBytes, Charsets.UTF_8)
        val parsed = try { pcsParseSites(siteText) } catch (e: IllegalArgumentException) { refuse(e.message ?: "site file") }
        val siteSeq = siteText.split("\n").drop(1).map { it.removeSuffix("\r") }.filter { it.isNotEmpty() }.map { it.substringBefore("\t") }
        cplSiteError(parsed, rootIds.toSet(), siteSeq)?.let { refuse(it) }
        val pops = parsed.map { (name, m) ->
            val pop = try { pcsPopulation(rootIds, m) } catch (e: IllegalArgumentException) { refuse("site $name: ${e.message}") }
            name to pop
        }

        val config = canonicalConfig(mcs)
        val dim = config.formalism.embeddingSliceDim
        val vecBytes = vecPath.takeIf { it.isFile }?.readBytes() ?: refuse("planted-vector file ${vecPath.path} not found")
        val vecSha = sha256(vecBytes)
        val planted = try { cplReadVectors(vecBytes, parsed, dim) } catch (e: IllegalArgumentException) { refuse(e.message ?: "vector file") }
        println("$tag snapshot $snapId root ${root.id} '${root.label}' n=${rootIds.size}; site file ${sitesPath.path} sha256 $siteSha; " +
            "planted vectors ${vecPath.path} sha256 $vecSha (${vecBytes.size} bytes, dim $dim); sites ${pops.size} " +
            "(${pops.joinToString { "${it.first}:${it.second.first.size}/${it.second.third.size}g" }})")
        val splitter = TaxonomySplitter(config, NoLlm, MMLUDatasetFetcher(config, ""), TaxonomyFitter(config))
        val capture = Capture()
        println("[SEPBAR] proposalSeparationBar=${config.formalism.proposalSeparationBar} (-DsepBar ${System.getProperty("sepBar")?.let { "'$it'" } ?: "absent -> default $DEFAULT_SEP_BAR"}); sliceDim=$dim dropTop=$dropTopProp whiten=$whitenProp reps=$reps minClusterSize=$mcs")

        val live = minOf(reps, Runtime.getRuntime().availableProcessors().coerceAtLeast(2))
        val peak = live.toLong() * rootIds.size.toLong() * (55L * dim / 10L + 3L * 128L) * 8L
        val budget = (Runtime.getRuntime().maxMemory() * 0.90).toLong()
        println(taxonomy.runner.ThreadCap.line(peak, budget))
        println("[SITENULL-HEAP] sliceDim=%d largest site n=%d live=%d -> peak live %.2f GB; budget %.2f GB"
            .format(java.util.Locale.US, dim, rootIds.size, live, peak / 1e9, budget / 1e9))
        if (peak > budget) refuse("heap: peak %.2f GB > budget %.2f GB; relaunch with -DsiteNullHeap=%dg"
            .format(java.util.Locale.US, peak / 1e9, budget / 1e9, kotlin.math.ceil(2.0 * peak / (1L shl 30)).toInt()))

        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        val vecById: Map<String, DoubleArray>
        val floats: Map<String, FloatArray>
        java.sql.DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { conn ->
            EmbedderReadGuard.run(conn, embDb.path, sites, { regionQueryIds(it, byId) }, dim,
                EmbedderReadGuard.resolveModel(null, null, false))
            vecById = loadVectorsById(conn, rootIds)
            floats = cpcLoadSliceFloats(conn, rootIds, dim)
        }
        if (vecById.size != rootIds.size || floats.size != rootIds.size)
            refuse("embedding cache miss: ${vecById.size} / ${floats.size} of ${rootIds.size} vectors")
        val chk = cplPlantCheck(planted, vecById)
        println("$tag PLANT CHECK: delta-0 sites %d, max |diff| vs the cache %.3e (<= 1e-6), max |norm - 1| %.3e (<= 1e-5) -> %s".format(
            java.util.Locale.US, chk.d0Sites, chk.d0MaxDiff, chk.normMaxDev, chk.error ?: "OK"))
        chk.error?.let { refuse("PLANT CHECK FAILED: $it") }
        val embOf = HashMap<String, Embedding>()
        for (id in rootIds) embOf[id] = Embedding(rawText = id, distilledText = id, values = floats.getValue(id))

        val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
        capture.context = splitLog.loggerContext
        capture.start(); splitLog.level = Level.DEBUG; splitLog.isAdditive = false; splitLog.addAppender(capture)
        fun esc(s: String) = "\"" + s.replace("\"", "\"\"") + "\""
        fun f6(x: Double) = "%.6f".format(java.util.Locale.US, x)
        fun newWriter(name: String) = java.nio.file.Files.newBufferedWriter(
            java.io.File(outDir, name).toPath(), Charsets.UTF_8, java.nio.file.StandardOpenOption.CREATE_NEW,
            java.nio.file.StandardOpenOption.WRITE)
        val siteRows = mutableListOf<String>()
        val repw = newWriter("replicates.csv")
        try {
            repw.write("site_id,arm,rep,stat\n")
            fun dumpReps(id: String, arm: String, xs: DoubleArray) { xs.forEachIndexed { i, x -> repw.write("${esc(id)},$arm,$i,$x\n") } }
            for ((idx, entry) in pops.withIndex()) {
                val (name, pop) = entry
                val (ids, _, groups) = pop
                val identity = idx == 0
                val vectors: List<DoubleArray>
                val embs: List<Embedding>
                if (identity) {
                    vectors = ids.map { vecById.getValue(it) }
                    embs = ids.map { embOf.getValue(it) }
                } else {
                    val rows = planted.getValue(name)
                    vectors = ids.map { cplUnit(rows.getValue(it)) }
                    embs = ids.map { Embedding(rawText = "$name#$it", distilledText = "$name#$it", values = rows.getValue(it)) }
                }
                val seedId = if (identity) root.id else name
                val res = cpcDeclaredSite(splitter, capture, seedId, root.depth, vectors, embs, groups, reps, deflated = false)
                dumpReps(name, "SN", res.plain)
                val np95 = percentile(res.plain.sorted(), 0.95)
                val reached = res.plain.count { it > 0.0 }
                if (identity) {
                    println("$tag IDENTITY n=${ids.size} declared=%s k=%d (registered %s, k %d) plain p95=%.6f max=%.6f".format(
                        java.util.Locale.US, f6(res.declared), res.kDeclared, identityDeclared, identityK,
                        np95, res.plain.maxOrNull() ?: Double.NaN))
                    repw.flush()
                    if (f6(res.declared) != identityDeclared || res.kDeclared != identityK)
                        refuse("IDENTITY FAILED: the full-size root gives declared ${f6(res.declared)} k ${res.kDeclared}, not $identityDeclared k $identityK; no PL site run")
                } else {
                    println("$tag site %-26s n=%3d groups=%s declared=%.6f k=%3d plain p95=%.6f reached=%3d".format(
                        java.util.Locale.US, name, ids.size, groups.map { it.size }, res.declared, res.kDeclared, np95, reached))
                }
                siteRows.add(listOf(if (identity) "IDENTITY" else "PL", esc(name), ids.size, groups.size,
                    groups.joinToString("/") { it.size.toString() }, res.declared, res.kDeclared, reached, np95, seedId, reps).joinToString(","))
                repw.flush()
            }
        } finally {
            runCatching { repw.close() }
            splitLog.detachAppender(capture); capture.stop(); splitLog.isAdditive = true
        }
        newWriter("sites.csv").use { w ->
            w.write("role,site_id,n,groups,group_sizes,declared_stat,k_declared,reached,null_p95,null_seed_id,reps\n")
            siteRows.forEach { w.write(it + "\n") }
        }
        newWriter("status.txt").use { w ->
            w.write("COMPLETE\narm=certPlanted\nsnapshot=$snapId\nsites_sha256=$siteSha\nvectors_sha256=$vecSha\nreps=$reps\nsliceDim=$dim\n" +
                "sepBar=${config.formalism.proposalSeparationBar}\ndropTop=$dropTopProp\nwhiten=$whitenProp\nminClusterSize=$mcs\n" +
                "plant_check=OK\nd0_sites=${chk.d0Sites}\nd0_max_abs_diff=${chk.d0MaxDiff}\nnorm_max_dev=${chk.normMaxDev}\n" +
                "threads=${Runtime.getRuntime().availableProcessors()}\n")
        }
        println("$tag wrote ${outDir.path}: sites.csv, replicates.csv, status.txt (COMPLETE); verdicts are the readout's")
    }
}
