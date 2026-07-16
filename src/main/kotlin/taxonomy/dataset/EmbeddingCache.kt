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

@Service
class EmbeddingCache(
    private val config: TaxonomyConfig,
    private val embeddingModel: EmbeddingModel
) {
    private val log = LoggerFactory.getLogger("taxonomy.EmbeddingCache")

    // In-memory cache for the CURRENT run only. Prevents repeated DB calls for the same query.
    private val sessionCache = ConcurrentHashMap<String, FloatArray>()

    private val dbUrl = "jdbc:sqlite:embeddings_cache.db?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000"
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
                            ground_truth_category TEXT DEFAULT ''
                        )
                    """.trimIndent()
                    )

                    try {
                        stmt.execute("ALTER TABLE queries ADD COLUMN ground_truth_category TEXT DEFAULT ''")
                    } catch (_: Exception) {}
                }
            }
            log.info("SQLite Embedding, GMM & Query Cache initialized successfully.")
        } catch (e: Exception) {
            log.error("Failed to initialize SQLite database.", e)
        }
    }

    fun putQuery(id: String, raw: String, distilled: String, groundTruthCategory: String = "") {
        try {
            withConn { conn ->
                conn.prepareStatement("INSERT OR REPLACE INTO queries (id, raw_text, distilled_text, ground_truth_category) VALUES (?, ?, ?, ?)")
                    .use { pstmt ->
                        pstmt.setString(1, id)
                        pstmt.setString(2, raw)
                        pstmt.setString(3, distilled)
                        pstmt.setString(4, groundTruthCategory)
                        pstmt.executeUpdate()
                    }
            }
        } catch (e: Exception) {
            log.error("Failed to save query metadata to SQL", e)
        }
    }

    fun getQuery(id: String): Triple<String, String, String>? {
        try {
            withConn { conn ->
                conn.prepareStatement("SELECT raw_text, distilled_text, ground_truth_category FROM queries WHERE id = ?").use { pstmt ->
                    pstmt.setString(1, id)
                    val rs = pstmt.executeQuery()
                    if (rs.next()) {
                        return Triple(
                            rs.getString("raw_text") ?: "",
                            rs.getString("distilled_text") ?: "",
                            rs.getString("ground_truth_category") ?: ""
                        )
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to retrieve query metadata from SQL", e)
        }
        return null
    }

    fun getQueriesBatch(ids: Collection<String>): Map<String, Triple<String, String, String>> {
        if (ids.isEmpty()) return emptyMap()
        val result = mutableMapOf<String, Triple<String, String, String>>()
        try {
            withConn { conn ->
                // SQLite has a 999-variable limit; chunk to be safe
                ids.chunked(900).forEach { chunk ->
                    val placeholders = chunk.joinToString(",") { "?" }
                    conn.prepareStatement(
                        "SELECT id, raw_text, distilled_text, ground_truth_category FROM queries WHERE id IN ($placeholders)"
                    ).use { pstmt ->
                        chunk.forEachIndexed { i, id -> pstmt.setString(i + 1, id) }
                        val rs = pstmt.executeQuery()
                        while (rs.next()) {
                            result[rs.getString("id")] = Triple(
                                rs.getString("raw_text") ?: "",
                                rs.getString("distilled_text") ?: "",
                                rs.getString("ground_truth_category") ?: ""
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
}

class EmbeddedQuery(val text: String, val embedding: FloatArray) {
    val id: String = text
}
