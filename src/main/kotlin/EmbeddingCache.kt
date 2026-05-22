package org.eclipse.lmos.arc.app.taxonomy

import dev.langchain4j.model.embedding.EmbeddingModel
import kotlinx.coroutines.*
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import java.sql.DriverManager
import java.util.concurrent.ConcurrentHashMap

@Service
class EmbeddingCache(private val embeddingModel: EmbeddingModel) {
    private val log = LoggerFactory.getLogger(EmbeddingCache::class.java)

    // In-memory cache for the CURRENT run only. Prevents repeated DB calls for the same query.
    private val sessionCache = ConcurrentHashMap<String, FloatArray>()

    private val dbUrl = "jdbc:sqlite:embeddings_cache.db"
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }

    val dimensionality: Int
        get() = sessionCache.values.firstOrNull()?.size ?: 384

    init {
        initDatabase()
    }

    private fun initDatabase() {
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.createStatement().use { stmt ->
                    // 1. Existing embeddings table
                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS embeddings (
                            query TEXT PRIMARY KEY,
                            vector_json TEXT
                        )
                    """.trimIndent())
                    
                    // 2. NEW: GMM Distribution vectors table
                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS gmm_vectors (
                            id TEXT PRIMARY KEY,
                            mean_json TEXT,
                            cov_json TEXT
                        )
                    """.trimIndent())

                    // 3. NEW: Query references table
                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS queries (
                            id TEXT PRIMARY KEY,
                            raw_text TEXT,
                            distilled_text TEXT
                        )
                    """.trimIndent())
                }
            }
            log.info("SQLite Embedding, GMM & Query Cache initialized successfully.")
        } catch (e: Exception) {
            log.error("Failed to initialize SQLite database.", e)
        }
    }

    fun putQuery(id: String, raw: String, distilled: String) {
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.prepareStatement("INSERT OR REPLACE INTO queries (id, raw_text, distilled_text) VALUES (?, ?, ?)").use { pstmt ->
                    pstmt.setString(1, id)
                    pstmt.setString(2, raw)
                    pstmt.setString(3, distilled)
                    pstmt.executeUpdate()
                }
            }
        } catch (e: Exception) {
            log.error("Failed to save query metadata to SQL", e)
        }
    }

    fun getQuery(id: String): Pair<String, String>? {
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.prepareStatement("SELECT raw_text, distilled_text FROM queries WHERE id = ?").use { pstmt ->
                    pstmt.setString(1, id)
                    val rs = pstmt.executeQuery()
                    if (rs.next()) {
                        return rs.getString("raw_text") to rs.getString("distilled_text")
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to retrieve query metadata from SQL", e)
        }
        return null
    }

    fun putGmmVectors(id: String, mean: DoubleArray, cov: DoubleArray) {
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.prepareStatement("INSERT OR REPLACE INTO gmm_vectors (id, mean_json, cov_json) VALUES (?, ?, ?)").use { pstmt ->
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
            DriverManager.getConnection(dbUrl).use { conn ->
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
        // 1. Instant return if we've already loaded it this session
        sessionCache[query]?.let { return it }

        // 2. Fetch ONLY this specific embedding from disk
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.prepareStatement("SELECT vector_json FROM embeddings WHERE query = ?").use { pstmt ->
                    pstmt.setString(1, query)
                    val rs = pstmt.executeQuery()
                    if (rs.next()) {
                        val vectorJson = rs.getString("vector_json")
                        val vector = json.decodeFromString<FloatArray>(vectorJson)

                        // Cache it in memory for the rest of this run
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

    suspend fun getOrCreate(query: String): FloatArray {
        get(query)?.let { return it }
        
        log.info("Generating new embedding for: ${if (query.length > 20) query.take(20) + "..." else query}")
        val vector = withContext(Dispatchers.IO) {
            embeddingModel.embed(query).content().vector()
        }
        
        sessionCache[query] = vector
        saveBatchToDisk(listOf(query to vector))
        return vector
    }

    suspend fun precompute(queries: List<String>) {
        val missing = queries.filter { get(it) == null }
        if (missing.isEmpty()) {
            log.info("All ${queries.size} requested embeddings are already cached on disk.")
            return
        }

        log.info("Computing and caching embeddings for ${missing.size} new queries...")
        coroutineScope {
            missing.chunked(50).forEach { chunk ->
                launch(Dispatchers.IO) {
                    val newEmbeddings = mutableListOf<Pair<String, FloatArray>>()

                    chunk.forEach { text ->
                        val vector = embeddingModel.embed(text).content().vector()
                        sessionCache[text] = vector
                        newEmbeddings.add(text to vector)
                    }

                    saveBatchToDisk(newEmbeddings)
                }
            }
        }
        log.info("Finished precomputing and saving new embeddings.")
    }

    private fun saveBatchToDisk(embeddings: List<Pair<String, FloatArray>>) {
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.autoCommit = false
                try {
                    conn.prepareStatement("INSERT OR REPLACE INTO embeddings (query, vector_json) VALUES (?, ?)").use { pstmt ->
                        for ((query, vector) in embeddings) {
                            pstmt.setString(1, query)
                            pstmt.setString(2, json.encodeToString(vector))
                            pstmt.addBatch()
                        }
                        pstmt.executeBatch()
                    }
                    conn.commit()
                } catch (e: Exception) {
                    conn.rollback()
                    throw e
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
