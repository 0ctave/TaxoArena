package taxonomy.dataset

import dev.langchain4j.model.embedding.EmbeddingModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.model.dimForDepth
import java.sql.DriverManager
import java.util.concurrent.ConcurrentHashMap

data class CachedQuery(
    val rawText: String,
    val distilledText: String,
    val groundTruthCategory: String,
    val queryId: Int
)

@Service
class EmbeddingCache(
    private val config: TaxonomyConfig,
    private val embeddingModel: EmbeddingModel
) {
    private val log = LoggerFactory.getLogger("taxonomy.EmbeddingCache")

    // In-memory cache for the CURRENT run only. Prevents repeated DB calls for the same query.
    private val sessionCache = ConcurrentHashMap<String, FloatArray>()

    // The cache is keyed by query TEXT alone, so vectors from different embedding
    // models must never share a file: a model switch with the shared cache would
    // silently reuse the old model's vectors (H9 embedder-swap hazard, 2026-09-08).
    // The historical file name is preserved for the canonical qwen3 model so every
    // existing run and fixture keeps working; any other model gets its own file.
    //
    // EMBEDDER-PLUMBING (b), 2026-09-27 (docs/judge_v2_program.md L21754-L21772): the historical rule
    // `m.startsWith("qwen3-embedding")` routed EVERY qwen3-embedding* tag (":0.6b", ":8b", "-instruct", ...)
    // to the DB of record, so a different qwen3 model would silently reuse the record's vectors. The rule
    // is now [cacheFileFor]: only a blank tag or the exact canonical tag of record routes there; any other
    // qwen3-embedding* variant gets its OWN per-model file like every other model (declared choice: own
    // file, not refusal). Byte-inert for the record: "" / "qwen3-embedding" / "qwen3-embedding:latest"
    // still route to embeddings_cache.db, and every non-qwen3 tag keeps its exact previous file name.
    //
    // EMB-TARGET2 C-ET-5 (READY_emb_target 6202766), 2026-09-29: -Dtaxoarena.embeddingCacheFile=<path> names the file
    // EXPLICITLY (an EMBEDDER-CROSS-FLAT --target-dir copy, e.g. a card file). Absent -> [cacheFileFor], unchanged
    // (byte-inert). Present -> [resolveCacheFile]'s fail-closed checks, a warn line, and for a card file a READ-ONLY
    // vector cache: a miss is never embedded by the JVM (its route has no card prefix / transform).
    private val explicitFile: String? = System.getProperty(PROP_EXPLICIT_FILE)
    private val dbFile: String = resolveCacheFile(config.llm.embeddingModel, explicitFile).also { f ->
        if (f != DB_OF_RECORD && config.llm.embeddingModel.startsWith("qwen3-embedding")) {
            log.warn("[EMB-CACHE] embedding model '${config.llm.embeddingModel}' is a qwen3-embedding VARIANT, not the " +
                "canonical tag of record ($CANONICAL_TAGS): routed to its own cache file $f, never to $DB_OF_RECORD")
        }
        if (explicitFile != null) {
            log.warn("[EMB-CACHE] -D$PROP_EXPLICIT_FILE: model '${config.llm.embeddingModel}' reads the EXPLICIT cache file $f" +
                (if (isCardFile(f)) " (a CARD file: read-only for vectors; a missing text REFUSES, it is never embedded here)" else ""))
        }
    }
    private val cardReadOnly: Boolean = isCardFile(dbFile)
    // INTENT-TRANSFER-S1: an intent working copy (reachable only through -D$PROP_EXPLICIT_FILE naming intent_emb_*.db, a name
    // every earlier route REFUSED) is READ-ONLY for vectors: an INTENT build never embeds; a miss REFUSES. false otherwise.
    private val intentReadOnly: Boolean = explicitFile != null && isIntentWorkingCopy(dbFile)

    private fun refuseCardMiss(n: Int) {
        if (cardReadOnly) throw IllegalStateException(
            "[EMB-CACHE] $n text(s) have no vector in the card file $dbFile: a card vector is never embedded by the JVM " +
                "(its route carries no card prefix / transform); embed them with embedder_arms --embed-card, REFUSED")
        if (intentReadOnly) throw IllegalStateException(
            "[EMB-CACHE] $n text(s) have no vector in the intent working copy $dbFile: an INTENT build never embeds (every " +
                "TRAIN+GATE text is in the pinned intent_emb file the copy was made from), REFUSED")
    }
    private val dbUrl = "jdbc:sqlite:$dbFile?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000"
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }

    val dimensionality: Int
        get() = sessionCache.values.firstOrNull()?.size ?: config.formalism.let { dimForDepth(4) }

    // Single held-open connection (WAL mode) guarded by a lock to avoid the cost
    // and contention of opening a new SQLite connection on every call.
    private val dbLock = Any()
    private val connection: java.sql.Connection by lazy {
        DriverManager.getConnection(dbUrl).also { conn ->
            conn.autoCommit = true
        }
    }

    private inline fun <T> withConn(block: (java.sql.Connection) -> T): T = synchronized(dbLock) {
        block(connection)
    }

    init {
        initDatabase()
    }

    private fun initDatabase() {
        try {
            withConn { conn ->
                conn.createStatement().use { stmt ->
                    // 1. Existing embeddings table
                    stmt.execute(
                        """
                        CREATE TABLE IF NOT EXISTS embeddings (
                            query TEXT PRIMARY KEY,
                            vector BLOB
                        )
                    """.trimIndent()
                    )

                    // 2. NEW: GMM Distribution vectors table
                    stmt.execute(
                        """
                        CREATE TABLE IF NOT EXISTS gmm_vectors (
                            id TEXT PRIMARY KEY,
                            mean_json TEXT,
                            cov_json TEXT
                        )
                    """.trimIndent()
                    )

                    // 3. NEW: Query references table with ground_truth_category
                    stmt.execute(
                        """
                        CREATE TABLE IF NOT EXISTS queries (
                            id TEXT PRIMARY KEY,
                            raw_text TEXT,
                            distilled_text TEXT,
                            ground_truth_category TEXT DEFAULT '',
                            query_id INTEGER DEFAULT -1
                        )
                    """.trimIndent()
                    )

                    try {
                        stmt.execute("ALTER TABLE queries ADD COLUMN ground_truth_category TEXT DEFAULT ''")
                    } catch (_: Exception) {}
                    try {
                        stmt.execute("ALTER TABLE queries ADD COLUMN query_id INTEGER DEFAULT -1")
                    } catch (_: Exception) {}
                }
            }
            log.info("SQLite Embedding, GMM & Query Cache initialized successfully.")
        } catch (e: Exception) {
            log.error("Failed to initialize SQLite database.", e)
        }
    }

    fun putQuery(id: String, raw: String, distilled: String, groundTruthCategory: String = "", queryId: Int = -1) {
        try {
            withConn { conn ->
                conn.prepareStatement("INSERT OR REPLACE INTO queries (id, raw_text, distilled_text, ground_truth_category, query_id) VALUES (?, ?, ?, ?, ?)")
                    .use { pstmt ->
                        pstmt.setString(1, id)
                        pstmt.setString(2, raw)
                        pstmt.setString(3, distilled)
                        pstmt.setString(4, groundTruthCategory)
                        pstmt.setInt(5, queryId)
                        pstmt.executeUpdate()
                    }
            }
        } catch (e: Exception) {
            log.error("Failed to save query metadata to SQL", e)
        }
    }

    fun getQuery(id: String): CachedQuery? {
        try {
            withConn { conn ->
                conn.prepareStatement("SELECT raw_text, distilled_text, ground_truth_category, query_id FROM queries WHERE id = ?").use { pstmt ->
                    pstmt.setString(1, id)
                    val rs = pstmt.executeQuery()
                    if (rs.next()) {
                        return CachedQuery(
                            rawText = rs.getString("raw_text") ?: "",
                            distilledText = rs.getString("distilled_text") ?: "",
                            groundTruthCategory = rs.getString("ground_truth_category") ?: "",
                            queryId = rs.getInt("query_id")
                        )
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to retrieve query metadata from SQL", e)
        }
        return null
    }

    fun getQueriesBatch(ids: Collection<String>): Map<String, CachedQuery> {
        if (ids.isEmpty()) return emptyMap()
        val result = mutableMapOf<String, CachedQuery>()
        try {
            withConn { conn ->
                // SQLite has a 999-variable limit; chunk to be safe
                ids.chunked(900).forEach { chunk ->
                    val placeholders = chunk.joinToString(",") { "?" }
                    conn.prepareStatement(
                        "SELECT id, raw_text, distilled_text, ground_truth_category, query_id FROM queries WHERE id IN ($placeholders)"
                    ).use { pstmt ->
                        chunk.forEachIndexed { i, id -> pstmt.setString(i + 1, id) }
                        val rs = pstmt.executeQuery()
                        while (rs.next()) {
                            result[rs.getString("id")] = CachedQuery(
                                rawText = rs.getString("raw_text") ?: "",
                                distilledText = rs.getString("distilled_text") ?: "",
                                groundTruthCategory = rs.getString("ground_truth_category") ?: "",
                                queryId = rs.getInt("query_id")
                            )
                        }
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to batch-retrieve query metadata from SQL", e)
        }
        return result
    }

    fun putGmmVectors(id: String, mean: DoubleArray, cov: DoubleArray) {
        try {
            withConn { conn ->
                conn.prepareStatement("INSERT OR REPLACE INTO gmm_vectors (id, mean_json, cov_json) VALUES (?, ?, ?)")
                    .use { pstmt ->
                        pstmt.setString(1, id)
                        pstmt.setString(2, json.encodeToString(mean))
                        pstmt.setString(3, json.encodeToString(cov))
                        pstmt.executeUpdate()
                    }
            }
        } catch (e: Exception) {
            log.error("Failed to save GMM vectors to SQL", e)
        }
    }

    fun getGmmVectors(id: String): Pair<DoubleArray, DoubleArray>? {
        try {
            withConn { conn ->
                conn.prepareStatement("SELECT mean_json, cov_json FROM gmm_vectors WHERE id = ?").use { pstmt ->
                    pstmt.setString(1, id)
                    val rs = pstmt.executeQuery()
                    if (rs.next()) {
                        val mean = json.decodeFromString<DoubleArray>(rs.getString("mean_json"))
                        val cov = json.decodeFromString<DoubleArray>(rs.getString("cov_json"))
                        return mean to cov
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to retrieve GMM vectors from SQL", e)
        }
        return null
    }

    fun get(query: String): FloatArray? {
        sessionCache[query]?.let { return it }
        try {
            withConn { conn ->
                conn.prepareStatement("SELECT vector FROM embeddings WHERE query = ?").use { pstmt ->
                    pstmt.setString(1, query)
                    val rs = pstmt.executeQuery()
                    if (rs.next()) {
                        val bytes = rs.getBytes("vector") ?: return null
                        val buf = java.nio.ByteBuffer.wrap(bytes)
                        val vector = FloatArray(bytes.size / 4) { buf.getFloat() }
                        sessionCache[query] = vector
                        return vector
                    }
                }
            }
        } catch (e: Exception) {
            log.warn("Failed to retrieve embedding from SQLite for query.", e)
        }
        return null
    }

    fun getBatch(queries: Collection<String>): Map<String, FloatArray> {
        if (queries.isEmpty()) return emptyMap()
        val result = mutableMapOf<String, FloatArray>()
        val missing = mutableListOf<String>()
        for (q in queries) {
            val memo = sessionCache[q]
            if (memo != null) {
                result[q] = memo
            } else {
                missing.add(q)
            }
        }
        if (missing.isEmpty()) return result

        try {
            withConn { conn ->
                missing.chunked(900).forEach { chunk ->
                    val placeholders = chunk.joinToString(",") { "?" }
                    conn.prepareStatement("SELECT query, vector FROM embeddings WHERE query IN ($placeholders)").use { pstmt ->
                        chunk.forEachIndexed { idx, q -> pstmt.setString(idx + 1, q) }
                        val rs = pstmt.executeQuery()
                        while (rs.next()) {
                            val q = rs.getString("query")
                            val bytes = rs.getBytes("vector")
                            if (bytes != null) {
                                val buf = java.nio.ByteBuffer.wrap(bytes)
                                val vector = FloatArray(bytes.size / 4) { buf.getFloat() }
                                sessionCache[q] = vector
                                result[q] = vector
                            }
                        }
                    }
                }
            }
        } catch (e: Exception) {
            log.warn("Failed to batch-retrieve embeddings from SQLite.", e)
        }
        return result
    }

    suspend fun getOrCreate(query: String): FloatArray {
        if (query.isBlank()) {
            return FloatArray(4096)
        }
        get(query)?.let { return it }
        refuseCardMiss(1)

        log.debug("Generating new embedding for: ${if (query.length > 20) query.take(20) + "..." else query}")
        val vector = withContext(Dispatchers.IO) {
            embeddingModel.embed(query).content().vector()
        }

        sessionCache[query] = vector
        saveBatchToDisk(listOf(query to vector))
        return vector
    }

    suspend fun precompute(queries: List<String>, onProgress: (Int, Int) -> Unit = { _, _ -> }) {
        val nonBlank = queries.filter { it.isNotBlank() }
        val missing = nonBlank.filter { get(it) == null }
        val total = missing.size
        if (total == 0) {
            log.info("All ${queries.size} requested embeddings are already cached on disk.")
            return
        }
        refuseCardMiss(total)

        log.info("Computing and caching embeddings for $total new queries...")
        val completed = java.util.concurrent.atomic.AtomicInteger(0)
        onProgress(0, total)

        coroutineScope {
            missing.chunked(50).forEach { chunk ->
                launch(Dispatchers.IO) {
                    val newEmbeddings = mutableListOf<Pair<String, FloatArray>>()

                    chunk.forEach { text ->
                        if (text.isNotBlank()) {
                            val vector = embeddingModel.embed(text).content().vector()
                            sessionCache[text] = vector
                            newEmbeddings.add(text to vector)
                        }
                        val currentCompleted = completed.incrementAndGet()
                        onProgress(currentCompleted, total)
                    }

                    saveBatchToDisk(newEmbeddings)
                }
            }
        }
        log.info("Finished precomputing and saving new embeddings.")
    }

    private fun saveBatchToDisk(embeddings: List<Pair<String, FloatArray>>) {
        try {
            withConn { conn ->
                conn.autoCommit = false
                try {
                    conn.prepareStatement("INSERT OR REPLACE INTO embeddings (query, vector) VALUES (?, ?)").use { pstmt ->
                        for ((query, vector) in embeddings) {
                            val buf = java.nio.ByteBuffer.allocate(vector.size * 4)
                            vector.forEach { buf.putFloat(it) }
                            pstmt.setString(1, query)
                            pstmt.setBytes(2, buf.array())
                            pstmt.addBatch()
                        }
                        pstmt.executeBatch()
                    }
                    conn.commit()
                } catch (e: Exception) {
                    conn.rollback()
                    throw e
                } finally {
                    conn.autoCommit = true
                }
            }
        } catch (e: Exception) {
            log.error("Failed to batch save embeddings to SQLite", e)
        }
    }

    companion object {
        /** The embedding cache of record (qwen3-embedding:latest vectors, 4096-d). */
        const val DB_OF_RECORD = "embeddings_cache.db"

        /**
         * The canonical tags of record: TaxonomyConfig's default "qwen3-embedding" and application.yml's
         * "qwen3-embedding:latest" (Ollama resolves an untagged name to ":latest", so they name ONE model).
         * Exact, case-sensitive, untrimmed match: anything else is not the record's model.
         */
        val CANONICAL_TAGS: Set<String> = setOf("qwen3-embedding", "qwen3-embedding:latest")

        /**
         * EMBEDDER-PLUMBING (b): the cache file an embedding model's vectors live in. A blank tag or a
         * canonical tag of record -> [DB_OF_RECORD]; ANY other tag, including every other qwen3-embedding*
         * variant, -> its own "embeddings_cache_<sanitised tag>.db" (the sanitisation is the historical one,
         * so every existing non-qwen3 file name is unchanged).
         */
        fun cacheFileFor(model: String): String =
            if (model.isBlank() || model in CANONICAL_TAGS) DB_OF_RECORD
            else "embeddings_cache_" + model.replace(Regex("[^A-Za-z0-9._-]"), "_") + ".db"

        /** EMB-TARGET2 C-ET-5: the explicit cache-file system property (forwarded by bootRun only when given). */
        const val PROP_EXPLICIT_FILE = "taxoarena.embeddingCacheFile"

        /**
         * E1-ROUTE R2 (docs/judge_v2_program.md L22182-L22206): the sha256 of the pinned DIR file the explicit working copy was
         * made from (tools/analysis/e1_route_launch.py passes the registrar's pin). Forwarded by bootRun only when given.
         */
        const val PROP_SOURCE_SHA = "taxoarena.embeddingCacheSourceSha256"
        private val SHA256_HEX = Regex("[0-9a-f]{64}")

        /**
         * E1-ROUTE R2: the manifest entries of the explicit embedding cache file, from the two properties. Both absent -> EMPTY
         * (every run without the property keeps its manifest keys: C-ET2-2). The file only -> embedding_cache_file. Both ->
         * embedding_cache_file then embedding_cache_source_sha256. Fail-closed: a source sha without the file property, or one
         * that is not 64 lowercase hex, REFUSES.
         */
        fun explicitFileManifest(filePath: String?, sourceSha: String?): Map<String, String> {
            if (filePath == null) {
                check(sourceSha == null) { "[EMB-CACHE] -D$PROP_SOURCE_SHA is set without -D$PROP_EXPLICIT_FILE, REFUSED" }
                return emptyMap()
            }
            val out = linkedMapOf("embedding_cache_file" to filePath)
            if (sourceSha != null) {
                check(SHA256_HEX.matches(sourceSha)) { "[EMB-CACHE] -D$PROP_SOURCE_SHA='$sourceSha' is not a sha256 (64 lowercase hex), REFUSED" }
                out["embedding_cache_source_sha256"] = sourceSha
            }
            return out
        }

        fun isCardFile(path: String): Boolean = java.io.File(path).name.endsWith("__card.db")

        /**
         * EMB-TARGET2 C-ET-5: [explicit] null -> [cacheFileFor] (the pre-existing rule, byte-inert). Otherwise, fail-closed:
         * not blank; the model is not the record's (the DB of record is never read through an explicit path); the file's
         * name is the model's own cache file or its "__card" twin (the pre-embedder's names); the file EXISTS (never created
         * here). Returns the absolute path.
         */
        fun resolveCacheFile(
            model: String,
            explicit: String?,
            cwd: java.io.File = java.io.File(System.getProperty("user.dir") ?: ".")
        ): String {
            if (explicit == null) return cacheFileFor(model)
            check(explicit.isNotBlank()) { "[EMB-CACHE] -D$PROP_EXPLICIT_FILE is present but blank, REFUSED" }
            // INTENT-TRANSFER-S1: an intent_emb_*.db name was REFUSED by every check below (it is never a model's own file or
            // its card twin), so this branch only turns that refusal into an admission, under its own fail-closed checks.
            if (isIntentWorkingCopy(explicit)) return resolveIntentWorkingCopy(model, explicit, cwd)
            val own = cacheFileFor(model)
            check(own != DB_OF_RECORD) {
                "[EMB-CACHE] -D$PROP_EXPLICIT_FILE with model '$model' (the record's, $DB_OF_RECORD): the DB of record is never read " +
                    "through an explicit path, REFUSED"
            }
            val f = java.io.File(explicit)
            val card = own.removeSuffix(".db") + "__card.db"
            check(f.name == own || f.name == card) {
                "[EMB-CACHE] -D$PROP_EXPLICIT_FILE=$explicit: the file name must be $own or $card for model '$model', REFUSED"
            }
            check(f.isFile) { "[EMB-CACHE] -D$PROP_EXPLICIT_FILE=$explicit does not exist (never created by the JVM), REFUSED" }
            return f.absolutePath
        }

        /** INTENT-TRANSFER-S1: the file name of an intent working copy (a per-run copy of a pinned intent_emb_<e>.db). */
        private val INTENT_COPY_NAME = Regex("intent_emb_[A-Za-z0-9._-]+\\.db")

        fun isIntentWorkingCopy(path: String): Boolean = INTENT_COPY_NAME.matches(java.io.File(path).name)

        /** Ollama resolves an untagged name to ":latest"; the comparison of an intent file's model with the configured tag. */
        fun normalisedTag(model: String): String = if (':' in model) model else "$model:latest"

        /** The intent_meta table of an intent embedding file (opened READ-ONLY); empty when the table is absent. */
        fun readIntentMeta(file: java.io.File): Map<String, String> {
            val cfg = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }
            cfg.createConnection("jdbc:sqlite:${file.path}").use { c ->
                val present = c.prepareStatement("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'intent_meta'")
                    .use { ps -> ps.executeQuery().use { rs -> rs.next() && rs.getInt(1) == 1 } }
                if (!present) return emptyMap()
                val out = LinkedHashMap<String, String>()
                c.createStatement().use { st ->
                    st.executeQuery("SELECT key, value FROM intent_meta").use { rs -> while (rs.next()) out[rs.getString(1)] = rs.getString(2) }
                }
                return out
            }
        }

        /**
         * INTENT-TRANSFER-S1 (docs/judge_v2_program.md L22682-L22710, HYGIENE "the working-copy route"): the explicit file is a
         * per-run WORKING COPY of a pinned intent_emb_<e>.db. Fail-closed: it EXISTS; it does NOT lie in the JVM's working dir
         * [cwd] (where the pinned intent_emb files and every cache of record live: the JVM mutates what it opens, C-ET2-1);
         * its intent_meta exists, its protocol is RAW, and its model equals the configured embedding model ([normalisedTag]).
         * The record's tag is admitted here (unlike the branch above): the copy is not the DB of record, by name and by
         * directory. Returns the absolute path.
         */
        fun resolveIntentWorkingCopy(model: String, explicit: String, cwd: java.io.File): String {
            val f = java.io.File(explicit)
            check(f.isFile) { "[EMB-CACHE] -D$PROP_EXPLICIT_FILE=$explicit (an intent working copy) does not exist (never created by the JVM), REFUSED" }
            val dir = f.canonicalFile.parentFile?.canonicalPath
            check(dir != cwd.canonicalPath) {
                "[EMB-CACHE] -D$PROP_EXPLICIT_FILE=$explicit lies in the JVM's working dir ${cwd.canonicalPath} (the pinned intent_emb files' " +
                    "directory): an INTENT build reads a per-run WORKING COPY, never a pinned file, REFUSED"
            }
            val meta = readIntentMeta(f)
            check(meta.isNotEmpty()) { "[EMB-CACHE] -D$PROP_EXPLICIT_FILE=$explicit has no intent_meta table (not an intent embedding file), REFUSED" }
            check(meta["protocol"] == "RAW") {
                "[EMB-CACHE] -D$PROP_EXPLICIT_FILE=$explicit: intent_meta protocol '${meta["protocol"]}' is not RAW (the registered protocol), REFUSED"
            }
            val fileModel = meta["model"]
            check(fileModel != null && normalisedTag(fileModel) == normalisedTag(model)) {
                "[EMB-CACHE] -D$PROP_EXPLICIT_FILE=$explicit holds vectors of model '$fileModel', but the configured embedding model is " +
                    "'$model', REFUSED"
            }
            return f.absolutePath
        }
    }
}

class EmbeddedQuery(val text: String, val embedding: FloatArray) {
    val id: String = text
}
