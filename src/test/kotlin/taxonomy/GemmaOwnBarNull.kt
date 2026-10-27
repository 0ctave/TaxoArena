package taxonomy

import java.io.File
import java.security.MessageDigest
import kotlin.math.ceil
import kotlin.math.sqrt

/**
 * GEMMA-OWN-BAR (registered 2026-10-03, docs/judge_v2_program.md L23915-L23927, section "## Registered 2026-10-03 (before any
 * code or call) — GEMMA-OWN-BAR: ..."; _as_of d50c47d4): the pure, file-reading half of the TRAIN-root null calibration arm
 * (`gemmaOwnBar - ...` in SeparationNullBySizeTest, task `gradlew gemmaOwnBar`). Zero calls; every DB opened read-only
 * (SQLITE_OPEN_READONLY + `immutable=1`, after a refusal of a non-empty -wal / -journal sidecar). No construction state.
 *
 * What it reads (HOW THE BAR IS DERIVED: "on S1's MASSIVE TRAIN items only"):
 *  - the INTENT-TRANSFER-S1 build DB (schema intent_s1_build/v1, written by tools/analysis/intent_s1_export.py --export):
 *    the DISTINCT texts of its TRAIN rows (side = 'TRAIN'), in id order. GATE rows are never returned; the build DB holds
 *    no EVAL row by construction (CHECK constraint; re-asserted here: any side other than TRAIN / GATE refuses). The meta
 *    must name corpus massive, salt 1, schema intent_s1_build/v1, and n_train must equal the TRAIN row count.
 *  - an intent embedding WORKING COPY (intent_emb_<e>.db: embeddings(query TEXT PK, vector BLOB big-endian float32),
 *    intent_meta): its sha256 must equal the pin the operator passes (the registrar's intent_transfer_s0_pins.json),
 *    intent_meta.model / native_dim / protocol must equal the arm's, and every TRAIN text must have a vector of exactly
 *    native_dim floats. The slice = the first sliceDim floats, unit-normalised (the arithmetic of the harness's
 *    loadVectorsById and of Embedding.projectTo).
 */
object GemmaOwnBarNull {
    const val TAG = "[GOB]"
    const val SITE_ID = "MASSIVE_TRAIN_ROOT"     // the null's seed key (cpcSeed(seedBase, SITE_ID, rep))
    const val SEED_BASE = 20260908L              // siteNull's plain-null seed base (cpcSiteArm callers use it)
    const val MCS = 55                           // the AF recipe's minClusterSize (m_af_g.toml)
    const val BAR_OF_RECORD = 0.025              // the qwen3-256 bar the rule scales (and the harness default the null runs at)
    const val ISO_N = 406                        // the D1 rule's isotropic node size (isoNullByDim, n 406)
    const val ISO_SIGMA = 0.5                    // isoNullByDim's sigma
    val ISO_DIMS = listOf(256, 512, 768)         // 256 = the rule's denominator; 512 = the record's identity (0.0040); 768 = gemma

    data class Arm(val name: String, val embedder: String, val model: String, val nativeDim: Int, val sliceDim: Int)

    /** The two registered null arms: p95_null(gemma 768) and p95_null(qwen3 256), both on the MASSIVE TRAIN root. */
    val ARMS: Map<String, Arm> = linkedMapOf(
        "gemma768" to Arm("gemma768", "gemma", "embeddinggemma:latest", 768, 768),
        "qwen3_256" to Arm("qwen3_256", "qwen3", "qwen3-embedding:latest", 4096, 256),
    )

    class Refusal(msg: String) : IllegalStateException(msg)

    fun refuse(msg: String): Nothing = throw Refusal("$TAG REFUSED: $msg")

    /** A sidecar with bytes means the file is mid-transaction: a failed precondition (never read through immutable=1). */
    fun checkNoSidecar(db: File) {
        if (!db.isFile) refuse("${db.path} not found")
        for (suf in listOf("-wal", "-journal")) {
            val s = File(db.path + suf)
            if (s.exists() && s.length() > 0) refuse("${s.path} is non-empty (${s.length()} bytes): the DB is mid-transaction")
        }
    }

    fun openRo(db: File): java.sql.Connection {
        checkNoSidecar(db)
        val cfg = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
        // "file:/Z:/dir/x.db?immutable=1" (an SQLite URI; sqlite-jdbc opens URI filenames)
        return java.sql.DriverManager.getConnection("jdbc:sqlite:" + db.absoluteFile.toURI().toString() + "?immutable=1", cfg)
    }

    fun sha256(f: File): String {
        val md = MessageDigest.getInstance("SHA-256")
        f.inputStream().use { ins ->
            val buf = ByteArray(1 shl 20)
            while (true) { val n = ins.read(buf); if (n < 0) break; md.update(buf, 0, n) }
        }
        return md.digest().joinToString("") { "%02x".format(it) }
    }

    /** sha256 over the texts sorted by UTF-8 bytes (unsigned), joined by '\n' (gemma_own_bar.py text_set_sha re-derives it). */
    fun textSetSha(texts: Collection<String>): String {
        val bytes = texts.map { it.toByteArray(Charsets.UTF_8) }.sortedWith { a, b ->
            val n = minOf(a.size, b.size)
            var c = 0
            for (i in 0 until n) { c = (a[i].toInt() and 0xff) - (b[i].toInt() and 0xff); if (c != 0) break }
            if (c != 0) c else a.size - b.size
        }
        val md = MessageDigest.getInstance("SHA-256")
        bytes.forEachIndexed { i, b -> if (i > 0) md.update('\n'.code.toByte()); md.update(b) }
        return md.digest().joinToString("") { "%02x".format(it) }
    }

    data class Train(val texts: List<String>, val meta: Map<String, String>, val nGateRows: Int)

    /** The build DB's TRAIN texts (distinct, id order) and meta; refuses every off-registration input listed in the KDoc. */
    fun loadTrain(buildDb: File): Train {
        openRo(buildDb).use { c ->
            val meta = LinkedHashMap<String, String>()
            c.createStatement().use { st -> st.executeQuery("SELECT key, value FROM intent_build_meta").use { rs -> while (rs.next()) meta[rs.getString(1)] = rs.getString(2) } }
            if (meta["schema"] != "intent_s1_build/v1") refuse("build DB schema '${meta["schema"]}' is not intent_s1_build/v1")
            if (meta["corpus"] != "massive") refuse("build DB corpus '${meta["corpus"]}' is not massive (the registered root is MASSIVE TRAIN)")
            if (meta["salt"] != "1") refuse("build DB salt '${meta["salt"]}' is not 1 (S1's salt-1 sides)")
            val off = c.createStatement().use { st -> st.executeQuery("SELECT COUNT(*) FROM intent_corpus WHERE side NOT IN ('TRAIN','GATE')").use { it.next(); it.getInt(1) } }
            if (off != 0) refuse("build DB holds $off rows off TRAIN / GATE (an EVAL row would be one)")
            val nGate = c.createStatement().use { st -> st.executeQuery("SELECT COUNT(*) FROM intent_corpus WHERE side = 'GATE'").use { it.next(); it.getInt(1) } }
            val texts = ArrayList<String>()
            c.createStatement().use { st -> st.executeQuery("SELECT question FROM intent_corpus WHERE side = 'TRAIN' ORDER BY id").use { rs -> while (rs.next()) texts.add(rs.getString(1)) } }
            if (texts.isEmpty()) refuse("build DB holds no TRAIN row")
            if (texts.toHashSet().size != texts.size) refuse("build DB TRAIN texts are not distinct (B2: one row per distinct text)")
            if (meta["n_train"] != texts.size.toString()) refuse("build DB meta n_train '${meta["n_train"]}' != ${texts.size} TRAIN rows")
            return Train(texts, meta, nGate)
        }
    }

    /** intent_meta of an embedding working copy, checked against the arm (model, native_dim, protocol RAW). */
    fun checkEmbMeta(embDb: File, arm: Arm): Map<String, String> {
        openRo(embDb).use { c ->
            val meta = LinkedHashMap<String, String>()
            c.createStatement().use { st -> st.executeQuery("SELECT key, value FROM intent_meta").use { rs -> while (rs.next()) meta[rs.getString(1)] = rs.getString(2) } }
            if (meta["model"] != arm.model) refuse("${embDb.name}: intent_meta.model '${meta["model"]}' != arm ${arm.name}'s ${arm.model}")
            if (meta["native_dim"] != arm.nativeDim.toString()) refuse("${embDb.name}: native_dim '${meta["native_dim"]}' != ${arm.nativeDim}")
            if (meta["protocol"] != "RAW") refuse("${embDb.name}: protocol '${meta["protocol"]}' is not RAW (the S1 arms' protocol)")
            return meta
        }
    }

    /** Unit-normalised slices (first [sliceDim] floats of each native vector), in [texts] order; any gap or wrong length refuses. */
    fun loadSlices(embDb: File, texts: List<String>, nativeDim: Int, sliceDim: Int): List<DoubleArray> {
        require(sliceDim in 1..nativeDim)
        val out = ArrayList<DoubleArray>(texts.size)
        var missing = 0
        var badLen = 0
        openRo(embDb).use { c ->
            c.prepareStatement("SELECT vector FROM embeddings WHERE query = ?").use { ps ->
                for (t in texts) {
                    ps.setString(1, t)
                    ps.executeQuery().use { rs ->
                        if (!rs.next()) { missing++; return@use }
                        val b = rs.getBytes(1)
                        if (b == null || b.size != nativeDim * 4) { badLen++; return@use }
                        val buf = java.nio.ByteBuffer.wrap(b)          // big-endian, as the intent DBs store (">f4")
                        val v = DoubleArray(sliceDim) { buf.getFloat().toDouble() }
                        var norm = 0.0
                        for (x in v) norm += x * x
                        norm = sqrt(norm)
                        if (norm <= 0.0) { badLen++; return@use }
                        for (i in v.indices) v[i] /= norm
                        out.add(v)
                    }
                }
            }
        }
        if (missing > 0 || badLen > 0) refuse("${embDb.name}: $missing of ${texts.size} TRAIN texts have no vector, $badLen a vector of the wrong length or norm 0")
        return out
    }

    /** The harness's quantile rule (SeparationNullBySizeTest.percentile): the ceil(q n)-th order statistic. */
    fun p95(xs: DoubleArray): Double {
        if (xs.isEmpty()) return Double.NaN
        val s = xs.sorted()
        val rank = ceil(0.95 * s.size).toInt().coerceIn(1, s.size)
        return s[rank - 1]
    }

    /** Write-once output directory: absent or empty, else refuse. */
    fun claimOutDir(outDir: File) {
        if (outDir.exists() && (outDir.listFiles()?.isNotEmpty() == true)) refuse("${outDir.path} exists and is not empty (write-once)")
        outDir.mkdirs()
    }

    fun writeNew(f: File, text: String) {
        java.nio.file.Files.newBufferedWriter(f.toPath(), Charsets.UTF_8, java.nio.file.StandardOpenOption.CREATE_NEW,
            java.nio.file.StandardOpenOption.WRITE).use { it.write(text) }
    }
}
