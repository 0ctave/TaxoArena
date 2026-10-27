package taxonomy

import ch.qos.logback.classic.Level
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import org.slf4j.LoggerFactory
import taxonomy.model.Embedding
import taxonomy.model.EmbeddingSlice
import taxonomy.model.GraphNode
import java.io.File
import java.nio.ByteBuffer
import java.security.MessageDigest
import kotlin.math.ceil
import kotlin.math.sqrt

/**
 * GEMMA-OWN-BAR: the TRAIN-root null calibration arm (`gemmaOwnBar - ...` in SeparationNullBySizeTest, its file-reading half
 * GemmaOwnBarNull) EXECUTED END TO END on synthetic fixture DBs (an S1-schema build DB, intent_emb working copies; no repo DB
 * read; runs in `test`). Every assertion is on a VALUE known by construction or recomputed here by independent code:
 *  - E-G (gemma768): status COMPLETE; n_train = the 300 TRAIN rows (the 60 GATE rows, planted far away so that reading them
 *    would move the moments, are NOT read); sliceDim 768; the emb sha256 recomputed here from the file bytes; the 8 replicates
 *    BIT-IDENTICAL to an independent run of the reviewed cpcSiteArm on vectors this test decodes itself (TRAIN only, first 768
 *    floats, unit-normalised) with a harness built at -DsliceDim=768, seed base 20260908, site "MASSIVE_TRAIN_ROOT", mcs 55;
 *    the status p95 = the ceil(0.95 n)-th order statistic computed here; the TRAIN text-set sha recomputed here.
 *  - E-Q (qwen3_256): native 4096 with the planted signal in floats 0-255 and large noise in 256-4095: replicates equal the
 *    independent run on the FIRST 256 floats (a full-vector or wrong-slice read differs).
 *  - E-I (iso): the 256 / 512 / 768 replicates equal an independent transcription of runReplicate on isoNullByDim's cloud
 *    (singleModeCloud by reflection, seed 1234 + n 7919 + rep 104729 + dim 13, n 406, sigma 0.5) at each width.
 *  - E-R refusals (each a value: the Refusal, and status.txt "REFUSED: ..." where the out dir was claimed): -DsepBar / -DsliceDim
 *    set, unknown arm, emb sha mismatch, a non-empty out dir (never overwritten), build DB corpus clinc / salt 2 / n_train off /
 *    an off-side row, a TRAIN text without a vector, the gemma working copy passed to the qwen3 arm (model), a non-empty -wal.
 *
 * MUTANTS: see the commit message's table (each a temporary edit, bytes restored, this class run each time).
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class GemmaOwnBarArmTest {
    private val tmp = java.nio.file.Files.createTempDirectory("gob_arm").toFile()
    private val nTrain = 300
    private val nGate = 60
    private val reps = 8
    private var savedWidth = 0
    private val rootLog = LoggerFactory.getLogger(org.slf4j.Logger.ROOT_LOGGER_NAME) as ch.qos.logback.classic.Logger
    private val splitLog = LoggerFactory.getLogger("taxonomy.Splitter") as ch.qos.logback.classic.Logger
    private var savedRoot: Level? = null
    private var savedSplit: Level? = null
    private val props = listOf("gobArm", "outDir", "gobBuildDb", "gobEmbDb", "gobEmbSha256", "nullReps", "sepBar", "sliceDim",
        "dropTop", "whiten", "embeddingCacheFile", "embeddingModel")

    @BeforeAll fun pin() { savedWidth = EmbeddingSlice.width; savedRoot = rootLog.level; savedSplit = splitLog.level }
    @AfterEach fun clear() { props.forEach { System.clearProperty(it) }; rootLog.level = savedRoot; splitLog.level = savedSplit; EmbeddingSlice.width = savedWidth }
    @AfterAll fun restore() { EmbeddingSlice.width = savedWidth; tmp.deleteRecursively() }

    private fun texts(side: String, n: Int) = (0 until n).map { "fixture $side utterance %04d".format(it) }
    private val trainTexts = texts("train", nTrain)
    private val gateTexts = texts("gate", nGate)

    /** Raw native vectors: TRAIN = an anisotropic cloud around e_0 in the first [signal] floats; GATE = around e_5 (far away). */
    private fun rawVectors(nativeDim: Int, signal: Int, seed: Long): Map<String, FloatArray> {
        val r = java.util.Random(seed)
        val out = LinkedHashMap<String, FloatArray>()
        for (t in trainTexts) out[t] = FloatArray(nativeDim) { j ->
            if (j < signal) ((if (j == 0) 1.0 else 0.0) + (if (j < 8) 0.6 else 0.08) * r.nextGaussian()).toFloat() else (5.0 * r.nextGaussian()).toFloat()
        }
        for (t in gateTexts) out[t] = FloatArray(nativeDim) { j ->
            if (j < signal) ((if (j == 5) 3.0 else 0.0) + 0.05 * r.nextGaussian()).toFloat() else (5.0 * r.nextGaussian()).toFloat()
        }
        return out
    }

    private fun sqlite(f: File) = java.sql.DriverManager.getConnection("jdbc:sqlite:${f.absolutePath}")

    private fun writeBuildDb(f: File, corpus: String = "massive", salt: String = "1", nTrainMeta: Int = nTrain, offSide: Boolean = false) {
        sqlite(f).use { c ->
            c.createStatement().use { st ->
                st.execute("PRAGMA journal_mode=DELETE")
                // S1's schema minus the side CHECK when an off-side row must be planted (the refusal is the reader's)
                st.execute("CREATE TABLE intent_corpus (id INTEGER PRIMARY KEY, question TEXT NOT NULL, category TEXT NOT NULL, cot_content TEXT, " +
                    "options TEXT, answer TEXT, side TEXT NOT NULL, fine TEXT NOT NULL, n_items INTEGER NOT NULL)")
                st.execute("CREATE TABLE intent_build_meta (key TEXT PRIMARY KEY, value TEXT)")
            }
            // GATE rows interleaved first in id order: a reader that ignores side would read them
            var id = 1
            c.prepareStatement("INSERT INTO intent_corpus VALUES (?,?,?,'','[]','',?,?,1)").use { ps ->
                for ((i, t) in (gateTexts.map { it to "GATE" } + trainTexts.map { it to "TRAIN" }).withIndex()) {
                    ps.setInt(1, id++); ps.setString(2, t.first); ps.setString(3, "c${i % 3}"); ps.setString(4, t.second); ps.setString(5, "f${i % 7}")
                    ps.executeUpdate()
                }
                if (offSide) { ps.setInt(1, id++); ps.setString(2, "fixture eval row"); ps.setString(3, "c0"); ps.setString(4, "EVAL"); ps.setString(5, "f0"); ps.executeUpdate() }
            }
            val meta = mapOf("schema" to "intent_s1_build/v1", "corpus" to corpus, "arm" to "M-AF-g", "salt" to salt, "n_train" to "$nTrainMeta",
                "n_gate" to "$nGate", "table_sha256" to "fixture-table-sha")
            c.prepareStatement("INSERT INTO intent_build_meta VALUES (?,?)").use { ps -> meta.forEach { (k, v) -> ps.setString(1, k); ps.setString(2, v); ps.executeUpdate() } }
        }
    }

    private fun writeEmbDb(f: File, vecs: Map<String, FloatArray>, model: String, nativeDim: Int, drop: String? = null) {
        sqlite(f).use { c ->
            c.createStatement().use { st ->
                st.execute("PRAGMA journal_mode=DELETE")
                st.execute("CREATE TABLE intent_meta (key TEXT PRIMARY KEY, value TEXT)")
                st.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
            }
            c.prepareStatement("INSERT INTO intent_meta VALUES (?,?)").use { ps ->
                mapOf("model" to model, "native_dim" to "$nativeDim", "protocol" to "RAW", "model_digest" to "fixture").forEach { (k, v) -> ps.setString(1, k); ps.setString(2, v); ps.executeUpdate() }
            }
            c.prepareStatement("INSERT INTO embeddings VALUES (?,?)").use { ps ->
                for ((t, v) in vecs) {
                    if (t == drop) continue
                    val bb = ByteBuffer.allocate(v.size * 4)          // big-endian, as the intent DBs store
                    v.forEach { bb.putFloat(it) }
                    ps.setString(1, t); ps.setBytes(2, bb.array()); ps.executeUpdate()
                }
            }
        }
    }

    private fun sha(f: File) = MessageDigest.getInstance("SHA-256").digest(f.readBytes()).joinToString("") { "%02x".format(it) }

    private val gemmaVecs by lazy { rawVectors(768, 768, 11) }
    private val qwenVecs by lazy { rawVectors(4096, 256, 12) }
    private val buildDb by lazy { File(tmp, "build_ok.db").also { writeBuildDb(it) } }
    private val gemmaDb by lazy { File(tmp, "intent_emb_gemma.db").also { writeEmbDb(it, gemmaVecs, "embeddinggemma:latest", 768) } }
    private val qwenDb by lazy { File(tmp, "intent_emb_qwen3.db").also { writeEmbDb(it, qwenVecs, "qwen3-embedding:latest", 4096) } }

    private fun status(dir: File): Map<String, String> =
        File(dir, "status.txt").readLines().drop(1).filter { "=" in it }.associate { it.substringBefore('=') to it.substringAfter('=') }

    private fun launch(arm: String, out: File, build: File? = buildDb, emb: File? = null, embSha: String? = null, extra: Map<String, String> = emptyMap()) {
        System.setProperty("gobArm", arm)
        System.setProperty("outDir", out.absolutePath)
        System.setProperty("nullReps", "$reps")
        build?.let { System.setProperty("gobBuildDb", it.absolutePath) }
        emb?.let { System.setProperty("gobEmbDb", it.absolutePath) }
        embSha?.let { System.setProperty("gobEmbSha256", it) }
        extra.forEach { (k, v) -> System.setProperty(k, v) }
        try {
            SeparationNullBySizeTest().`gemmaOwnBar - TRAIN-root moment-matched null p95 per embedder and the isotropic width leg`()
        } finally { props.forEach { System.clearProperty(it) } }
    }

    /** Independent leg: decode the TRAIN vectors here, slice + normalise, and run the reviewed cpcSiteArm at the arm's width. */
    private fun independentNull(vecs: Map<String, FloatArray>, sliceDim: Int): DoubleArray {
        val xs = trainTexts.map { t ->
            val v = DoubleArray(sliceDim) { vecs.getValue(t)[it].toDouble() }
            val n = sqrt(v.sumOf { it * it }); DoubleArray(sliceDim) { v[it] / n }
        }
        System.setProperty("sliceDim", "$sliceDim")
        val h = try { SeparationNullBySizeTest() } finally { System.clearProperty("sliceDim") }
        val dim = xs[0].size
        val mu = DoubleArray(dim); for (v in xs) for (i in 0 until dim) mu[i] += v[i] / xs.size
        val centered = xs.map { v -> DoubleArray(dim) { v[it] - mu[it] } }
        val splitter = h.cpcSplitter(55, File(tmp, "corpus-${System.nanoTime()}.db").absolutePath)
        assertEquals(sliceDim, EmbeddingSlice.width)
        return h.cpcSiteArm(splitter, h.cpcNewCapture(), "GOB", 20260908L, "MASSIVE_TRAIN_ROOT", mu, centered, xs.size, reps)
    }

    private fun readReps(f: File): DoubleArray = f.readLines().drop(1).map { it.substringAfterLast(',').toDouble() }.toDoubleArray()
    private fun orderStat95(xs: DoubleArray): Double { val s = xs.sorted(); return s[ceil(0.95 * s.size).toInt() - 1] }
    private fun textSetShaHere(ts: List<String>): String {
        val md = MessageDigest.getInstance("SHA-256")
        val sorted = ts.sortedWith { a, b -> java.util.Arrays.compareUnsigned(a.toByteArray(), b.toByteArray()) }
        md.update(sorted.joinToString("\n").toByteArray()); return md.digest().joinToString("") { "%02x".format(it) }
    }

    @Test fun `E-G gemma768 reads TRAIN only at slice 768 and reproduces the reviewed site-null arm bit for bit`() {
        val out = File(tmp, "out_g")
        launch("gemma768", out, emb = gemmaDb, embSha = sha(gemmaDb))
        assertEquals(savedWidth, EmbeddingSlice.width, "the arm restores the process-global slice width")
        val st = status(out)
        assertEquals("COMPLETE", File(out, "status.txt").readLines()[0])
        assertEquals("$nTrain", st["n_train"]); assertEquals("$nGate", st["build_n_gate_rows_not_read"])
        assertEquals("768", st["sliceDim"]); assertEquals("0.025", st["sepBar"]); assertEquals("55", st["minClusterSize"]); assertEquals("$reps", st["reps"])
        assertEquals(sha(gemmaDb), st["emb_sha256"]); assertEquals(textSetShaHere(trainTexts), st["train_text_set_sha256"])
        assertNotEquals(textSetShaHere(trainTexts + gateTexts), st["train_text_set_sha256"])
        val got = readReps(File(out, "replicates.csv"))
        assertEquals(reps, got.size)
        val want = independentNull(gemmaVecs, 768)
        assertArrayEquals(want, got)
        assertTrue(got.any { it > 0.0 }, "the fixture null reaches the gate (non-vacuous)")
        assertEquals(orderStat95(got), st.getValue("p95").toDouble())
    }

    @Test fun `E-Q qwen3_256 reads the first 256 of 4096 floats`() {
        val out = File(tmp, "out_q")
        launch("qwen3_256", out, emb = qwenDb, embSha = sha(qwenDb))
        val st = status(out)
        assertEquals("256", st["sliceDim"]); assertEquals("4096", st["nativeDim"]); assertEquals("$nTrain", st["n_train"])
        val got = readReps(File(out, "replicates.csv"))
        assertArrayEquals(independentNull(qwenVecs, 256), got)
        assertEquals(orderStat95(got), st.getValue("p95").toDouble())
    }

    @Test fun `E-I iso leg equals an independent transcription of isoNullByDim's replicate at 256, 512, 768`() {
        val out = File(tmp, "out_i")
        launch("iso", out, build = null)
        val st = status(out)
        assertEquals("406", st["n"]); assertEquals("0.5", st["sigma"]); assertEquals("0.025", st["sepBar"])
        val rows = File(out, "iso_replicates.csv").readLines().drop(1).map { it.split(",") }
        assertEquals(3 * reps, rows.size)
        val cloud = SeparationNullBySizeTest::class.java.getDeclaredMethod("singleModeCloud", Int::class.javaPrimitiveType,
            Int::class.javaPrimitiveType, Double::class.javaPrimitiveType, java.util.Random::class.java).apply { isAccessible = true }
        for (dim in listOf(256, 512, 768)) {
            System.setProperty("sliceDim", "$dim")
            val h = try { SeparationNullBySizeTest() } finally { System.clearProperty("sliceDim") }
            val splitter = h.cpcSplitter(55, File(tmp, "corpus-iso-$dim.db").absolutePath)
            val want = DoubleArray(reps) { rep ->
                @Suppress("UNCHECKED_CAST")
                val c = cloud.invoke(h, 406, dim, 0.5, java.util.Random(1234L + 406 * 7919L + rep * 104729L + dim * 13L)) as List<DoubleArray>
                val tag = "ISO_IND_${dim}_$rep"
                val node = GraphNode(label = tag, depth = 1).apply { vmfKappa = 10.0 }
                val keys = c.mapIndexed { i, v ->
                    val key = "$tag#$i"
                    val e = Embedding(rawText = key, distilledText = key, values = FloatArray(v.size) { j -> v[j].toFloat() }, queryId = i)
                    GraphNode.registerEmbedding(e); node.queries.add(e); node.queryWeights[key] = 1.0; key
                }
                try { runBlocking { splitter.splitSingleNode(node) }; node.dasguptaDeltaNorm } finally { keys.forEach { GraphNode.EmbeddingRegistry.remove(it) } }
            }
            val got = rows.filter { it[0] == "$dim" }.sortedBy { it[1].toInt() }.map { it[2].toDouble() }.toDoubleArray()
            assertArrayEquals(want, got, "iso slice $dim")
            assertEquals(orderStat95(got), st.getValue("p95_iso_$dim").toDouble())
        }
        assertFalse(rows.filter { it[0] == "256" }.map { it[2] } == rows.filter { it[0] == "768" }.map { it[2] }, "the width is applied")
    }

    private fun assertRefused(needle: String, statusNeedle: Boolean, block: () -> Unit, out: File? = null) {
        val e = assertThrows(GemmaOwnBarNull.Refusal::class.java) { block() }
        assertTrue(e.message!!.contains(needle), "refusal '${e.message}' lacks '$needle'")
        if (statusNeedle && out != null) assertTrue(File(out, "status.txt").readText().startsWith("REFUSED: ") && File(out, "status.txt").readText().contains(needle))
    }

    @Test fun `E-R every refusal fires with its reason`() {
        val okSha = sha(gemmaDb)
        assertRefused("-DsepBar='0.0145'", false, { launch("gemma768", File(tmp, "r1"), emb = gemmaDb, embSha = okSha, extra = mapOf("sepBar" to "0.0145")) })
        assertRefused("-DsliceDim='768'", false, { launch("gemma768", File(tmp, "r2"), emb = gemmaDb, embSha = okSha, extra = mapOf("sliceDim" to "768")) })
        assertRefused("-DgobArm='nomic'", false, { launch("nomic", File(tmp, "r3")) })
        val r4 = File(tmp, "r4"); assertRefused("!= the pin", true, { launch("gemma768", r4, emb = gemmaDb, embSha = "0".repeat(64)) }, r4)
        val r5 = File(tmp, "r5").apply { mkdirs(); File(this, "status.txt").writeText("COMPLETE\nkeep\n") }
        assertRefused("write-once", false, { launch("gemma768", r5, emb = gemmaDb, embSha = okSha) })
        assertEquals("COMPLETE\nkeep\n", File(r5, "status.txt").readText(), "a refused re-run never overwrites an outcome")
        val clinc = File(tmp, "b_clinc.db").also { writeBuildDb(it, corpus = "clinc") }
        val r6 = File(tmp, "r6"); assertRefused("is not massive", true, { launch("gemma768", r6, build = clinc, emb = gemmaDb, embSha = okSha) }, r6)
        val s2 = File(tmp, "b_s2.db").also { writeBuildDb(it, salt = "2") }
        assertRefused("is not 1", false, { launch("gemma768", File(tmp, "r7"), build = s2, emb = gemmaDb, embSha = okSha) })
        val nOff = File(tmp, "b_n.db").also { writeBuildDb(it, nTrainMeta = nTrain + nGate) }
        assertRefused("meta n_train", false, { launch("gemma768", File(tmp, "r8"), build = nOff, emb = gemmaDb, embSha = okSha) })
        val ev = File(tmp, "b_ev.db").also { writeBuildDb(it, offSide = true) }
        assertRefused("off TRAIN / GATE", false, { launch("gemma768", File(tmp, "r9"), build = ev, emb = gemmaDb, embSha = okSha) })
        val gap = File(tmp, "intent_emb_gap.db").also { writeEmbDb(it, gemmaVecs, "embeddinggemma:latest", 768, drop = trainTexts.last()) }
        assertRefused("1 of $nTrain TRAIN texts have no vector", false, { launch("gemma768", File(tmp, "r10"), emb = gap, embSha = sha(gap)) })
        // a GATE text without a vector is NOT a refusal: GATE is never read
        val gateGap = File(tmp, "intent_emb_gategap.db").also { writeEmbDb(it, gemmaVecs, "embeddinggemma:latest", 768, drop = gateTexts.first()) }
        launch("gemma768", File(tmp, "r10b"), emb = gateGap, embSha = sha(gateGap))
        assertEquals("$nTrain", status(File(tmp, "r10b"))["n_train"])
        assertRefused("qwen3-embedding:latest", false, { launch("qwen3_256", File(tmp, "r11"), emb = gemmaDb, embSha = okSha) })
        val wal = File(gemmaDb.path + "-wal")
        try { wal.writeBytes(ByteArray(16)); assertRefused("-wal is non-empty", false, { launch("gemma768", File(tmp, "r12"), emb = gemmaDb, embSha = okSha) }) } finally { wal.delete() }
    }

    @Test fun `p95 is the ceil(0_95 n)-th order statistic`() {
        val x300 = DoubleArray(300) { ((it * 7919) % 300).toDouble() }          // a permutation of 0..299
        assertEquals(284.0, GemmaOwnBarNull.p95(x300))                           // the 285th smallest
        assertEquals(285.0, GemmaOwnBarNull.p95(DoubleArray(301) { ((it * 7919) % 301).toDouble() }))   // ceil(285.95) = 286th
        assertEquals(3.5, GemmaOwnBarNull.p95(doubleArrayOf(3.5)))
        assertTrue(GemmaOwnBarNull.p95(DoubleArray(0)).isNaN())
    }

    @Test fun `text-set sha orders by unsigned UTF-8 bytes`() {
        // U+FF5E (EF BD 9E) sorts BEFORE U+1F600 (F0 9F 98 80) by UTF-8 bytes but AFTER it by UTF-16 code units
        val a = "～"; val b = "😀"
        val md = MessageDigest.getInstance("SHA-256"); md.update("$a\n$b".toByteArray())
        assertEquals(md.digest().joinToString("") { "%02x".format(it) }, GemmaOwnBarNull.textSetSha(listOf(b, a)))
        // "a" (0x61) sorts BEFORE "é" (C3 A9) by UNSIGNED bytes; a signed-byte compare puts C3 (-61) first
        val md2 = MessageDigest.getInstance("SHA-256"); md2.update("a\né".toByteArray())
        assertEquals(md2.digest().joinToString("") { "%02x".format(it) }, GemmaOwnBarNull.textSetSha(listOf("é", "a")))
    }
}
