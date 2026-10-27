package taxonomy.dataset

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Test

/**
 * EMBEDDER-PLUMBING (b), P-2 branch (iv) (docs/judge_v2_program.md L21754-L21772): the canonical-name guard of
 * EmbeddingCache. Only a blank tag or a canonical tag of record routes to embeddings_cache.db; every other
 * qwen3-embedding* variant gets its own per-model file (the declared rule: own file, not refusal); every
 * non-qwen3 tag keeps its historical file name exactly.
 */
class EmbeddingCacheRoutingTest {

    /** The pre-RP08 rule, verbatim, as the inertness reference for every tag it routed correctly. */
    private fun legacy(m: String): String =
        if (m.isBlank() || m.startsWith("qwen3-embedding")) "embeddings_cache.db"
        else "embeddings_cache_" + m.replace(Regex("[^A-Za-z0-9._-]"), "_") + ".db"

    @Test
    fun `blank and the canonical tags of record route to the DB of record (byte-inert)`() {
        for (m in listOf("", "   ", "qwen3-embedding", "qwen3-embedding:latest")) {
            assertEquals("embeddings_cache.db", EmbeddingCache.cacheFileFor(m), "tag '$m'")
            assertEquals(legacy(m), EmbeddingCache.cacheFileFor(m), "tag '$m' must route as before")
        }
        assertEquals("embeddings_cache.db", EmbeddingCache.DB_OF_RECORD)
    }

    @Test
    fun `a qwen3-embedding variant routes to its OWN file, never to the DB of record`() {
        val cases = mapOf(
            "qwen3-embedding:8b" to "embeddings_cache_qwen3-embedding_8b.db",
            "qwen3-embedding:0.6b" to "embeddings_cache_qwen3-embedding_0.6b.db",
            "qwen3-embedding:4b-q8_0" to "embeddings_cache_qwen3-embedding_4b-q8_0.db",
            "qwen3-embedding-instruct" to "embeddings_cache_qwen3-embedding-instruct.db",
            "qwen3-embedding:Latest" to "embeddings_cache_qwen3-embedding_Latest.db",   // exact, case-sensitive
            " qwen3-embedding:latest" to "embeddings_cache__qwen3-embedding_latest.db", // exact, untrimmed
        )
        for ((m, f) in cases) {
            val got = EmbeddingCache.cacheFileFor(m)
            assertEquals(f, got, "tag '$m'")
            assertNotEquals("embeddings_cache.db", got, "tag '$m' must not reach the DB of record")
        }
        // The change is exactly these variants: the old rule sent them to the record.
        assertEquals("embeddings_cache.db", legacy("qwen3-embedding:8b"))
    }

    @Test
    fun `non-qwen3 tags keep their historical file names`() {
        for (m in listOf("nomic-embed-text:latest", "nomic-embed-text", "embeddinggemma:latest", "mxbai-embed-large:latest", "text-embedding-3-large")) {
            assertEquals(legacy(m), EmbeddingCache.cacheFileFor(m), "tag '$m'")
        }
        assertEquals("embeddings_cache_nomic-embed-text_latest.db", EmbeddingCache.cacheFileFor("nomic-embed-text:latest"))
    }
}
