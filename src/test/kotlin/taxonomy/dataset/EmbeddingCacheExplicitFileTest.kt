package taxonomy.dataset

import dev.langchain4j.data.embedding.Embedding
import dev.langchain4j.data.segment.TextSegment
import dev.langchain4j.model.embedding.EmbeddingModel
import dev.langchain4j.model.output.Response
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.io.TempDir
import taxonomy.config.TaxonomyConfig
import java.io.File
import java.nio.ByteBuffer
import java.sql.DriverManager

/**
 * EMB-TARGET2 C-ET-5 (READY_emb_target 6202766): -Dtaxoarena.embeddingCacheFile lets the JVM read an EMBEDDER-CROSS-FLAT
 * --target-dir file (e.g. a card file). INERTNESS: with the property absent, [EmbeddingCache.resolveCacheFile] returns
 * exactly [EmbeddingCache.cacheFileFor] for every tag (the pre-existing rule). With it present: fail-closed checks, and a
 * CARD file is read-only for vectors (a miss REFUSES and the model is never called), while the raw-named twin still embeds
 * a miss (the discriminator: the card branch is the one that changed behaviour, and it executed).
 */
class EmbeddingCacheExplicitFileTest {

    private val prop = EmbeddingCache.PROP_EXPLICIT_FILE

    private fun makeDb(f: File, rows: Map<String, FloatArray>) {
        DriverManager.getConnection("jdbc:sqlite:${f.absolutePath}").use { c ->
            c.createStatement().use { it.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)") }
            c.prepareStatement("INSERT INTO embeddings VALUES (?, ?)").use { p ->
                for ((q, v) in rows) {
                    val b = ByteBuffer.allocate(v.size * 4); v.forEach { b.putFloat(it) }
                    p.setString(1, q); p.setBytes(2, b.array()); p.executeUpdate()
                }
            }
        }
    }

    private class CountingModel : EmbeddingModel {
        var calls = 0
        override fun embedAll(textSegments: MutableList<TextSegment>): Response<MutableList<Embedding>> {
            calls += textSegments.size
            return Response.from(textSegments.map { Embedding.from(FloatArray(768) { 0.5f }) }.toMutableList())
        }
    }

    private fun <T> withProp(value: String, block: () -> T): T {
        val saved = System.getProperty(prop)
        System.setProperty(prop, value)
        try { return block() } finally { if (saved == null) System.clearProperty(prop) else System.setProperty(prop, saved) }
    }

    private fun gemmaConfig() = TaxonomyConfig().also { it.llm.embeddingModel = "embeddinggemma:latest" }

    @Test
    fun `absent property - resolveCacheFile is cacheFileFor for every tag (byte-inert)`() {
        for (m in listOf("", "qwen3-embedding", "qwen3-embedding:latest", "qwen3-embedding:8b", "nomic-embed-text:latest",
                         "embeddinggemma:latest", "mxbai-embed-large:latest")) {
            assertEquals(EmbeddingCache.cacheFileFor(m), EmbeddingCache.resolveCacheFile(m, null), "tag '$m'")
        }
        assertEquals(null, System.getProperty(prop), "the suite runs without the property")
    }

    @Test
    fun `explicit file - fail-closed checks`(@TempDir td: File) {
        val m = "embeddinggemma:latest"
        val card = File(td, "embeddings_cache_embeddinggemma_latest__card.db").also { makeDb(it, emptyMap()) }
        val raw = File(td, "embeddings_cache_embeddinggemma_latest.db").also { makeDb(it, emptyMap()) }
        assertEquals(card.absolutePath, EmbeddingCache.resolveCacheFile(m, card.path))
        assertEquals(raw.absolutePath, EmbeddingCache.resolveCacheFile(m, raw.path))
        val other = File(td, "embeddings_cache_nomic-embed-text_latest__card.db").also { makeDb(it, emptyMap()) }
        for ((path, needle) in listOf(
            other.path to "the file name must be",
            File(td, "absent", ).resolve("embeddings_cache_embeddinggemma_latest__card.db").path to "does not exist",
            "  " to "blank",
        )) {
            val e = assertThrows<IllegalStateException> { EmbeddingCache.resolveCacheFile(m, path) }
            assertTrue(e.message!!.contains(needle), "'$path': ${e.message}")
        }
        val q = assertThrows<IllegalStateException> { EmbeddingCache.resolveCacheFile("qwen3-embedding:latest", card.path) }
        assertTrue(q.message!!.contains("DB of record is never read"), q.message)
        assertTrue(EmbeddingCache.isCardFile(card.path) && !EmbeddingCache.isCardFile(raw.path))
    }

    @Test
    fun `a card file is read-only for vectors - a miss REFUSES, the model is never called`() {
        // not @TempDir: EmbeddingCache holds its SQLite connection open for the JVM's life (no close()), so JUnit's
        // cleanup would fail on Windows; a plain temp dir, removed best-effort at exit
        val td = taxonomy.TestTmp.dir("emb_explicit")
        val v = FloatArray(768) { it / 768f }
        val card = File(td, "embeddings_cache_embeddinggemma_latest__card.db").also { makeDb(it, mapOf("have" to v)) }
        val model = CountingModel()
        withProp(card.path) {
            val cache = EmbeddingCache(gemmaConfig(), model)
            assertArrayEquals(v, cache.get("have"))
            assertArrayEquals(v, runBlocking { cache.getOrCreate("have") })
            val e1 = assertThrows<IllegalStateException> { runBlocking { cache.getOrCreate("missing") } }
            assertTrue(e1.message!!.contains("never embedded by the JVM"), e1.message)
            val e2 = assertThrows<IllegalStateException> { runBlocking { cache.precompute(listOf("have", "missing", "missing2")) } }
            assertTrue(e2.message!!.contains("2 text(s)"), e2.message)
            runBlocking { cache.precompute(listOf("have")) }        // nothing missing: no refusal
        }
        assertEquals(0, model.calls, "the JVM embedded nothing into a card file")
    }

    @Test
    fun `the raw-named explicit file still embeds a miss (discriminator)`() {
        // not @TempDir: EmbeddingCache holds its SQLite connection open for the JVM's life (no close()), so JUnit's
        // cleanup would fail on Windows; a plain temp dir, removed best-effort at exit
        val td = taxonomy.TestTmp.dir("emb_explicit")
        val raw = File(td, "embeddings_cache_embeddinggemma_latest.db").also { makeDb(it, emptyMap()) }
        val model = CountingModel()
        withProp(raw.path) {
            val cache = EmbeddingCache(gemmaConfig(), model)
            assertEquals(768, runBlocking { cache.getOrCreate("missing") }.size)
        }
        assertEquals(1, model.calls)
    }
}
