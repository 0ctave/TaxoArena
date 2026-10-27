package taxonomy.diagnostics

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.io.TempDir
import taxonomy.dataset.EmbeddingCache
import java.io.File

/**
 * E1-ROUTE R2 and C-ET2-2 (READY_emb_target2 f66c360; registration docs/judge_v2_program.md L22182-L22206): the runner's
 * manifest carries NO embedding_cache_file / embedding_cache_source_sha256 key when the properties are absent (C4's "the new
 * test, run and not skipped"); with the file property it carries the file; with both, the working copy's source sha256 (the
 * registrar's pin the launcher passed). A source sha without the file property, or a malformed one, REFUSES. The runner makes
 * exactly this call (a source scan), so the tested function is what runs.
 */
class EmbeddingCacheManifestTest {

    @AfterEach
    fun close() { if (DiagnosticsBundle.isOpen()) DiagnosticsBundle.close("test-teardown") }

    private val sha = "53d1540a811e819ff9af27006b6929e7e89cdff6cfb96f6e2803691e85f8cb95"

    private fun manifest(dir: File): String = File(dir, "diagnostics/run_manifest.json").readText()

    private fun props(vararg kv: Pair<String, String>): (String) -> String? = kv.toMap()::get

    @Test
    fun `C-ET2-2 - absent properties record nothing and the manifest has neither key`(@TempDir td: File) {
        DiagnosticsBundle.open(td, null)
        assertFalse(DiagnosticsBundle.recordEmbeddingCacheFromProperties(props()))
        DiagnosticsBundle.recordConstructionOrder(null)          // forces a manifest write
        val m = manifest(td)
        assertFalse(m.contains("embedding_cache_file"), m)
        assertFalse(m.contains("embedding_cache_source_sha256"), m)
        assertEquals(null, System.getProperty(EmbeddingCache.PROP_EXPLICIT_FILE), "the suite runs without the property")
        assertEquals(null, System.getProperty(EmbeddingCache.PROP_SOURCE_SHA))
        assertEquals(emptyMap<String, String>(), EmbeddingCache.explicitFileManifest(null, null))
    }

    @Test
    fun `the file property alone records the file, both record the source sha256`(@TempDir td: File) {
        DiagnosticsBundle.open(td, null)
        assertTrue(DiagnosticsBundle.recordEmbeddingCacheFromProperties(props(EmbeddingCache.PROP_EXPLICIT_FILE to "W/a.db")))
        var m = manifest(td)
        assertTrue(m.contains("\"embedding_cache_file\": \"W/a.db\""), m)
        assertFalse(m.contains("embedding_cache_source_sha256"), m)
        assertTrue(DiagnosticsBundle.recordEmbeddingCacheFromProperties(
            props(EmbeddingCache.PROP_EXPLICIT_FILE to "W/b.db", EmbeddingCache.PROP_SOURCE_SHA to sha)))
        m = manifest(td)
        assertTrue(m.contains("\"embedding_cache_file\": \"W/b.db\",\n  \"embedding_cache_source_sha256\": \"$sha\""), m)
    }

    @Test
    fun `a source sha without the file, or a malformed one, refuses`() {
        val e1 = assertThrows<IllegalStateException> { EmbeddingCache.explicitFileManifest(null, sha) }
        assertEquals("[EMB-CACHE] -Dtaxoarena.embeddingCacheSourceSha256 is set without -Dtaxoarena.embeddingCacheFile, REFUSED", e1.message)
        for (bad in listOf(sha.uppercase(), sha.dropLast(1), "")) {
            val e = assertThrows<IllegalStateException> { EmbeddingCache.explicitFileManifest("W/a.db", bad) }
            assertTrue(e.message!!.contains("is not a sha256 (64 lowercase hex), REFUSED"), e.message)
        }
    }

    @Test
    fun `the runner records the explicit file only through recordEmbeddingCacheFromProperties`() {
        val src = File("src/main/kotlin/taxonomy/runner/HeadlessBenchmarkRunner.kt").readText()
        assertEquals(1, Regex("DiagnosticsBundle\\.recordEmbeddingCacheFromProperties \\{ System\\.getProperty\\(it\\) \\}").findAll(src).count())
        assertFalse(src.contains("recordEmbeddingCacheFile("), "no direct, unconditional record left in the runner")
    }
}
