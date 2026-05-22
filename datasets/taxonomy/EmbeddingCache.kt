package org.eclipse.lmos.arc.app.taxonomy

import dev.langchain4j.model.embedding.EmbeddingModel
import kotlinx.coroutines.*
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import java.io.File
import java.util.concurrent.ConcurrentHashMap

@Service
class EmbeddingCache(private val embeddingModel: EmbeddingModel) {
    private val log = LoggerFactory.getLogger(EmbeddingCache::class.java)
    private val cache = ConcurrentHashMap<String, FloatArray>()
    private val cacheFile = File("embeddings_cache.json")
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }

    val dimensionality: Int
        get() = cache.values.firstOrNull()?.size ?: 384

    init {
        loadCache()
    }

    private fun loadCache() {
        if (cacheFile.exists()) {
            try {
                val loaded: Map<String, FloatArray> = json.decodeFromString(cacheFile.readText())
                cache.putAll(loaded)
                log.info("Loaded ${loaded.size} embeddings from local vector cache.")
            } catch (e: Exception) {
                log.warn("Failed to load embedding cache from disk. Will compute missing embeddings.", e)
            }
        }
    }

    private fun saveCache() {
        try {
            cacheFile.writeText(json.encodeToString(cache.toMap()))
            log.info("Saved ${cache.size} embeddings to local vector cache.")
        } catch (e: Exception) {
            log.error("Failed to save embedding cache to disk", e)
        }
    }

    fun get(query: String): FloatArray? = cache[query]

    suspend fun precompute(queries: List<String>) {
        val missing = queries.filter { !cache.containsKey(it) }
        if (missing.isEmpty()) return

        log.info("Computing and caching embeddings for ${missing.size} new queries...")
        coroutineScope {
            missing.chunked(50).forEach { chunk ->
                launch(Dispatchers.IO) {
                    chunk.forEach { text ->
                        cache[text] = embeddingModel.embed(text).content().vector()
                    }
                }
            }
        }
        saveCache()
    }
}

class EmbeddedQuery(val text: String, val embedding: FloatArray) {
    // We use the query text itself as the unique ID for the DBSCAN visited sets
    val id: String = text
}