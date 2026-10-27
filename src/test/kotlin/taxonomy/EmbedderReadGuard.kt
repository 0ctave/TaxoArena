package taxonomy

import taxonomy.dataset.EmbeddingCache
import taxonomy.service.SerialNode
import java.io.File
import kotlin.math.sqrt

/**
 * EMBEDDER-PLUMBING (RP08; registered 2026-09-27, docs/judge_v2_program.md L21754-L21772, commit a357ef0):
 * the read guard of the site-null harness (SeparationNullBySizeTest), so a tree built by one embedder is never
 * scored silently on another embedder's vectors. Zero calls; reads only, every DB opened read-only.
 *
 *  (a) [resolveCacheFile]: -DembeddingCacheFile=<path>, fail-closed. ABSENT -> "embeddings_cache.db" exactly as
 *      before (no validation added, the harness's Assumption path unchanged: byte-inert). PRESENT -> it must be
 *      non-blank, an existing file, carry the SQLite header, and hold the `embeddings` and `queries` tables the
 *      harness joins; otherwise REFUSE (an error, never a skip) before any replicate.
 *  (c) [run]: before any replicate, for EVERY checked site (declared: all accepted split sites of the snapshot,
 *      the harness's own site list, which contains the root family whenever the root split), the cosine between
 *      the normalised unweighted mean of the site's member vectors read from the OPENED cache (sliced to the
 *      harness's slice width and unit-normalised, the arithmetic of Embedding.projectTo) and the snapshot's
 *      vmfMu; REFUSE if the minimum is below [COS_BUDGET] = 0.99. The minimum and the budget are printed on
 *      every run, pass or fail (CONTEXT rule 11); on a refusal every site's cosine is printed.
 *      THE DIMENSION CHECK (real, replacing the vacuous `full.size < sliceDim`): every raw vector read must have
 *      exactly the named model's native dimension ([NATIVE_DIM]); an unknown model, a mixed-length read or
 *      a snapshot vmfMu whose length is not the slice width REFUSES. All findings are printed before refusing.
 *  (d) [resolveModel]: the model is named by the snapshot manifest's embedding_model or by -DembeddingModel
 *      (both present and different -> REFUSE); a manifest present without embedding_model and no -D REFUSES;
 *      no manifest reachable and -DembeddingCacheFile set without -DembeddingModel REFUSES. With NOTHING set
 *      (the site null reaches no manifest: `run_manifest.json` carries no snapshot id and the harness takes
 *      only -DsnapshotId) the read is of the DB of record and the model is its canonical tag -- the only
 *      reading consistent with P-1 ("no new flag, byte-identical"); flagged to the registrar as ambiguity A1.
 */
object EmbedderReadGuard {
    const val PROP_CACHE_FILE = "embeddingCacheFile"
    const val PROP_MODEL = "embeddingModel"
    const val COS_BUDGET = 0.99
    const val CANONICAL_MODEL = "qwen3-embedding:latest"
    private const val TAG = "[EMB-GUARD]"
    private val SQLITE_MAGIC = "SQLite format 3\u0000".toByteArray(Charsets.US_ASCII)

    /**
     * Native output dimension per canonical model tag (plan rev2 embedder table: the model cards). The Python
     * twin tools/analysis/embedder_guard.py NATIVE_DIM must equal this map (its selftest parses this file).
     */
    val NATIVE_DIM: Map<String, Int> = linkedMapOf(
        "qwen3-embedding:latest" to 4096,
        "nomic-embed-text:latest" to 768,
        "embeddinggemma:latest" to 768,
        "mxbai-embed-large:latest" to 1024,
    )

    /** Ollama naming: an untagged model name means ":latest". Used for comparison and the dimension lookup only. */
    fun canonicalModel(tag: String): String = tag.trim().let { if (':' in it) it else "$it:latest" }

    class Refusal(msg: String) : IllegalStateException(msg)

    private fun refuse(msg: String): Nothing {
        println(msg)
        throw Refusal(msg)
    }

    data class CacheChoice(val file: File, val explicit: Boolean)

    /** (a) -DembeddingCacheFile resolution. null -> the historical relative "embeddings_cache.db", unvalidated. */
    fun resolveCacheFile(raw: String?): CacheChoice {
        if (raw == null) return CacheChoice(File(EmbeddingCache.DB_OF_RECORD), explicit = false)
        if (raw.isBlank()) refuse("[EMB-CACHE] REFUSING: -D$PROP_CACHE_FILE is present but blank (absent -> ${EmbeddingCache.DB_OF_RECORD})")
        val f = File(raw.trim())
        validateCacheFile(f)
        return CacheChoice(f, explicit = true)
    }

    /** Must exist, be a file, start with the SQLite header and hold the `embeddings` and `queries` tables. */
    fun validateCacheFile(f: File) {
        val p = f.path
        if (!f.exists()) refuse("[EMB-CACHE] REFUSING: -D$PROP_CACHE_FILE='$p' does not exist")
        if (!f.isFile) refuse("[EMB-CACHE] REFUSING: -D$PROP_CACHE_FILE='$p' is not a regular file")
        val head = ByteArray(SQLITE_MAGIC.size)
        val got = f.inputStream().use { it.readNBytes(head, 0, head.size) }
        if (got != head.size || !head.contentEquals(SQLITE_MAGIC)) {
            refuse("[EMB-CACHE] REFUSING: -D$PROP_CACHE_FILE='$p' is not a SQLite database (header mismatch)")
        }
        val tables = HashSet<String>()
        try {
            val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
            java.sql.DriverManager.getConnection("jdbc:sqlite:${f.absolutePath}", ro).use { conn ->
                conn.createStatement().use { st ->
                    val rs = st.executeQuery("SELECT name FROM sqlite_master WHERE type = 'table'")
                    while (rs.next()) tables.add(rs.getString(1))
                }
            }
        } catch (e: java.sql.SQLException) {
            refuse("[EMB-CACHE] REFUSING: -D$PROP_CACHE_FILE='$p' cannot be opened read-only as SQLite: ${e.message}")
        }
        val missing = listOf("embeddings", "queries").filter { it !in tables }
        if (missing.isNotEmpty()) {
            refuse("[EMB-CACHE] REFUSING: -D$PROP_CACHE_FILE='$p' lacks the table(s) $missing the harness joins (has ${tables.sorted()})")
        }
    }

    data class ModelChoice(val model: String, val source: String)

    /**
     * (d) Which model the opened vectors must come from. [manifest] = the snapshot's run_manifest.json as a map, or
     * null when no manifest is reachable; [explicit] = -DembeddingModel or null; [cacheFileExplicit] = whether
     * -DembeddingCacheFile was set.
     */
    fun resolveModel(manifest: Map<String, Any?>?, explicit: String?, cacheFileExplicit: Boolean): ModelChoice {
        if (explicit != null && explicit.isBlank()) refuse("$TAG REFUSING: -D$PROP_MODEL is present but blank")
        val fromManifest = (manifest?.get("embedding_model") as? String)?.takeIf { it.isNotBlank() }
        if (explicit != null && fromManifest != null && canonicalModel(explicit) != canonicalModel(fromManifest)) {
            refuse("$TAG REFUSING: -D$PROP_MODEL='$explicit' contradicts the snapshot manifest's embedding_model='$fromManifest'")
        }
        return when {
            explicit != null -> ModelChoice(explicit.trim(), "-D$PROP_MODEL")
            fromManifest != null -> ModelChoice(fromManifest, "snapshot manifest embedding_model")
            manifest != null -> refuse("$TAG REFUSING: the snapshot manifest has no embedding_model and no -D$PROP_MODEL names the model")
            cacheFileExplicit -> refuse("$TAG REFUSING: -D$PROP_CACHE_FILE is set but neither a snapshot manifest's embedding_model " +
                "nor -D$PROP_MODEL names the model its vectors must come from")
            else -> ModelChoice(CANONICAL_MODEL, "default (no -D$PROP_CACHE_FILE, no -D$PROP_MODEL, no manifest reachable: " +
                "the DB of record's canonical model)")
        }
    }

    data class SiteCos(val id: String, val label: String, val n: Int, val found: Int, val cos: Double)
    data class Result(val admitted: Boolean, val minCos: Double, val sites: List<SiteCos>, val rawDims: Map<Int, Int>, val reasons: List<String>)

    /** Raw lengths (in floats) of every vector read, and the sliced unit vectors by query id. */
    class Read(val vectors: Map<String, DoubleArray>, val rawDims: Map<Int, Int>)

    fun read(conn: java.sql.Connection, ids: Collection<String>, sliceDim: Int): Read {
        val out = HashMap<String, DoubleArray>()
        val dims = java.util.TreeMap<Int, Int>()
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
                    val len = bytes.size / 4
                    dims.merge(len, 1, Int::plus)
                    if (len < sliceDim) continue
                    val buf = java.nio.ByteBuffer.wrap(bytes)
                    val v = DoubleArray(sliceDim) { buf.getFloat().toDouble() }
                    var norm = 0.0
                    for (x in v) norm += x * x
                    norm = sqrt(norm)
                    if (norm > 0) { for (i in v.indices) v[i] /= norm; out[qid] = v }
                }
            }
        }
        return Read(out, dims)
    }

    /** cos(normalised mean of [vectors], [mu] normalised); NaN when either is degenerate. */
    fun cosine(vectors: List<DoubleArray>, mu: FloatArray): Double {
        if (vectors.isEmpty()) return Double.NaN
        val d = mu.size
        val m = DoubleArray(d)
        for (v in vectors) for (i in 0 until d) m[i] += v[i]
        var nm = 0.0; var nu = 0.0; var dot = 0.0
        for (i in 0 until d) { nm += m[i] * m[i]; nu += mu[i].toDouble() * mu[i]; dot += m[i] * mu[i] }
        if (nm <= 0.0 || nu <= 0.0) return Double.NaN
        return dot / (sqrt(nm) * sqrt(nu))
    }

    /**
     * (c) + the dimension check. Reads the union of the sites' member ids from [conn] ONCE, prints its lines, and
     * REFUSES (throws [Refusal]) on any finding; returns the result when admitted.
     */
    fun run(
        conn: java.sql.Connection, cachePath: String, sites: List<SerialNode>,
        regionIds: (SerialNode) -> Set<String>, sliceDim: Int, model: ModelChoice
    ): Result {
        val idsBySite = sites.associate { it.id to regionIds(it) }
        val union = LinkedHashSet<String>().apply { idsBySite.values.forEach { addAll(it) } }
        val rd = read(conn, union, sliceDim)
        val native = NATIVE_DIM[canonicalModel(model.model)]
        val reasons = mutableListOf<String>()
        if (sites.isEmpty()) reasons.add("no site to check")
        if (native == null) reasons.add("model '${model.model}' has no declared native dimension (EmbedderReadGuard.NATIVE_DIM: ${NATIVE_DIM.keys})")
        else if (rd.rawDims.keys != setOf(native)) reasons.add("raw vector dimensions ${rd.rawDims} != {$native} (the native dimension of ${canonicalModel(model.model)})")
        val rows = sites.map { s ->
            val ids = idsBySite.getValue(s.id)
            val vs = ids.mapNotNull { rd.vectors[it] }
            val mu = s.vmfMu
            val cos = if (mu == null || mu.size != sliceDim) Double.NaN else cosine(vs, mu)
            if (mu == null) reasons.add("site ${s.id} has no vmfMu")
            else if (mu.size != sliceDim) reasons.add("site ${s.id} vmfMu length ${mu.size} != slice width $sliceDim")
            if (vs.isEmpty()) reasons.add("site ${s.id}: no member vector recovered from the opened cache (${ids.size} ids)")
            SiteCos(s.id, s.label ?: s.id, ids.size, vs.size, cos)
        }
        val finite = rows.filter { !it.cos.isNaN() }
        val worst = finite.minByOrNull { it.cos }
        val minCos = if (finite.size == rows.size && worst != null) worst.cos else Double.NaN
        if (!minCos.isNaN() && minCos < COS_BUDGET) reasons.add("min cosine %.4f < budget %.2f".format(java.util.Locale.US, minCos, COS_BUDGET))
        if (minCos.isNaN() && rows.isNotEmpty()) reasons.add("the cosine is undefined on ${rows.size - finite.size} site(s)")
        val admitted = reasons.isEmpty()
        val sorted = finite.map { it.cos }.sorted()
        val median = if (sorted.isEmpty()) Double.NaN else sorted[sorted.size / 2]
        println("$TAG model=${model.model} (${model.source}); cache=$cachePath; native dim expected ${native ?: "UNKNOWN"}; " +
            "vectors read ${rd.vectors.size} of ${union.size} ids, raw dims ${rd.rawDims}; slice width $sliceDim")
        println("$TAG vmfMu cosine over ${rows.size} sites: min %s (site %s), median %s; budget %.2f -> %s".format(
            java.util.Locale.US, if (minCos.isNaN()) "NaN" else "%.4f".format(java.util.Locale.US, minCos),
            worst?.let { "${it.id} '${it.label.take(40)}' n=${it.n}" } ?: "-",
            if (median.isNaN()) "NaN" else "%.4f".format(java.util.Locale.US, median), COS_BUDGET,
            if (admitted) "ADMIT" else "REFUSE"))
        val show = if (admitted) finite.sortedBy { it.cos }.take(3) else rows
        show.forEach { println("$TAG   site %-10s n=%-5d found=%-5d cos=%s  %s".format(java.util.Locale.US, it.id, it.n, it.found,
            if (it.cos.isNaN()) "NaN" else "%.4f".format(java.util.Locale.US, it.cos), it.label.take(50))) }
        val result = Result(admitted, minCos, rows, rd.rawDims, reasons)
        if (!admitted) refuse("$TAG REFUSING before any replicate: " + reasons.joinToString("; "))
        return result
    }
}
