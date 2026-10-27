package taxonomy.dataset

import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import java.io.File
import java.nio.file.Path
import java.sql.DriverManager

/**
 * [LeaderboardCorpusSource] against a throwaway DB shaped like `multicorpus_cache_v1.db`
 * (`tools/ingest/multicorpus_db.py`): the real DB is never opened.
 */
class LeaderboardCorpusSourceTest {

    private fun buildDb(dir: Path, registry: List<Triple<String, Int, String>>, rows: List<List<Any?>>): String {
        val path = File(dir.toFile(), "mc.db").absolutePath
        DriverManager.getConnection("jdbc:sqlite:$path").use { c ->
            c.createStatement().use { s ->
                s.execute("CREATE TABLE corpus_registry (source TEXT PRIMARY KEY, table_name TEXT, id_offset INTEGER, verifier TEXT)")
                s.execute(
                    """
                    CREATE TABLE corpus_questions (question_id INTEGER PRIMARY KEY, source TEXT NOT NULL, upstream_id INTEGER NOT NULL,
                        task TEXT NOT NULL, domain TEXT NOT NULL, text TEXT NOT NULL, options_json TEXT, target TEXT,
                        verifier TEXT NOT NULL, generative INTEGER NOT NULL)
                    """.trimIndent()
                )
            }
            c.prepareStatement("INSERT INTO corpus_registry VALUES (?, 'corpus_questions', ?, ?)").use { ps ->
                registry.forEach { (src, off, ver) -> ps.setString(1, src); ps.setInt(2, off); ps.setString(3, ver); ps.addBatch() }
                ps.executeBatch()
            }
            c.prepareStatement("INSERT INTO corpus_questions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)").use { ps ->
                rows.forEach { r ->
                    r.forEachIndexed { i, v -> ps.setObject(i + 1, v) }
                    ps.addBatch()
                }
                ps.executeBatch()
            }
        }
        return path
    }

    private val registry = listOf(
        Triple("MMLU_PRO", 0, "MC_LETTER"),
        Triple("BBH", 1_000_000, "IMPORTED:acc_norm"),
        Triple("MATH", 2_000_000, "IMPORTED:exact_match")
    )

    // question_id, source, upstream_id, task, domain, text, options_json, target, verifier
    private val rows = listOf(
        listOf(1_000_003, "BBH", 3, "bbh_navigate", "navigate", "turn left", "[\"Yes\",\"No\"]", "Yes", "IMPORTED:acc_norm"),
        listOf(1_000_000, "BBH", 0, "bbh_boolean_expressions", "boolean_expressions", "not True is", "[\"True\",\"False\"]", "False", "IMPORTED:acc_norm"),
        listOf(1_000_001, "BBH", 1, "bbh_boolean_expressions", "boolean_expressions", "True and True is", "[\"True\",\"False\"]", "True", "IMPORTED:acc_norm"),
        listOf(2_000_000, "MATH", 0, "math_algebra_hard", "Algebra", "Solve x+1=2", null, "1", "IMPORTED:exact_match"),
        listOf(70, "MMLU_PRO", 70, "mmlu_pro", "business", "Adverts must not", "[\"a\",\"b\"]", "B", "MC_LETTER"),
        listOf(71, "MMLU_PRO", 71, "mmlu_pro", "law", "  ", "[\"a\",\"b\"]", "A", "MC_LETTER")
    )

    @Test
    fun `fetch groups by SOURCE slash domain in question_id order with namespaced ids`(@TempDir dir: Path) = runBlocking {
        val db = buildDb(dir, registry, rows)
        val bbh = LeaderboardCorpusSource(db, CorpusRegistry.LEADERBOARD.getValue("BBH"))
        val byDomain = bbh.fetch(Int.MAX_VALUE, emptyList())
        assertEquals(listOf("BBH/boolean_expressions", "BBH/navigate"), byDomain.keys.toList())
        val bool = byDomain.getValue("BBH/boolean_expressions")
        assertEquals(listOf(0, 1), bool.map { it.upstreamId })
        assertEquals(listOf("not True is", "True and True is"), bool.map { it.text })
        assertTrue(bool.all { it.source == "BBH" && it.domain == "BBH/boolean_expressions" && it.task == "bbh_boolean_expressions" })
        assertEquals(1_000_003, CorpusIds.namespacedOrSentinel("BBH", byDomain.getValue("BBH/navigate").single().upstreamId))

        // The leaderboard MMLU-Pro reads source MMLU_PRO under the MMLU_PRO_LB name; blank texts are skipped.
        val lb = LeaderboardCorpusSource(db, CorpusRegistry.LEADERBOARD.getValue("MMLU_PRO_LB"))
        val lbMap = lb.fetch(Int.MAX_VALUE, emptyList())
        assertEquals(listOf("MMLU_PRO_LB/business"), lbMap.keys.toList())
        assertEquals(70, lbMap.getValue("MMLU_PRO_LB/business").single().upstreamId)

        // Domain filter accepts the bare domain or the prefixed key; maxQueries caps the rows.
        assertEquals(listOf("BBH/navigate"), bbh.fetch(Int.MAX_VALUE, listOf("navigate")).keys.toList())
        assertEquals(listOf("BBH/navigate"), bbh.fetch(Int.MAX_VALUE, listOf("bbh/Navigate")).keys.toList())
        assertEquals(1, bbh.fetch(1, emptyList()).values.sumOf { it.size })
        assertEquals(3, bbh.rowCount())
    }

    @Test
    fun `detailsFor renders text, options and target through the item shape`(@TempDir dir: Path) {
        val db = buildDb(dir, registry, rows)
        val bbh = LeaderboardCorpusSource(db, CorpusRegistry.LEADERBOARD.getValue("BBH"))
        val math = LeaderboardCorpusSource(db, CorpusRegistry.LEADERBOARD.getValue("MATH"))
        val d = bbh.detailsFor(listOf("not True is", "Solve x+1=2", "unknown"))
        assertEquals(setOf("not True is"), d.keys)
        val item = d.getValue("not True is")
        assertEquals("BBH/boolean_expressions", item.category)
        assertEquals(listOf("True", "False"), item.options)
        assertEquals("False", item.answer)
        assertEquals(1_000_000, item.id)
        val m = math.detailsFor(listOf("Solve x+1=2")).getValue("Solve x+1=2")
        assertEquals(emptyList<String>(), m.options)
        assertEquals("1", m.answer)
        assertEquals("Q: Solve x+1=2\nTarget: 1", math.verifier.renderItem(m.question, m.options, m.answer))
        assertNull(math.verifier.isCorrect("1", "1", null), "imported metrics are never recomputed")
    }

    @Test
    fun `a DB whose registry disagrees with the descriptor, or an empty source, fails loudly`(@TempDir dir: Path) {
        val db = buildDb(dir, listOf(Triple("BBH", 7_000_000, "IMPORTED:acc_norm"), Triple("MATH", 2_000_000, "IMPORTED:acc")), rows)
        val bbh = LeaderboardCorpusSource(db, CorpusRegistry.LEADERBOARD.getValue("BBH"))
        val offsetErr = assertThrows(IllegalStateException::class.java) { runBlocking { bbh.fetch(Int.MAX_VALUE, emptyList()) } }
        assertTrue(offsetErr.message!!.contains("id_offset"), offsetErr.message)
        val math = LeaderboardCorpusSource(db, CorpusRegistry.LEADERBOARD.getValue("MATH"))
        val verifierErr = assertThrows(IllegalStateException::class.java) { runBlocking { math.fetch(Int.MAX_VALUE, emptyList()) } }
        assertTrue(verifierErr.message!!.contains("verifier"), verifierErr.message)
        val gpqa = LeaderboardCorpusSource(db, CorpusRegistry.LEADERBOARD.getValue("GPQA"))
        assertThrows(IllegalStateException::class.java) { runBlocking { gpqa.fetch(Int.MAX_VALUE, emptyList()) } }
        assertEquals(0, gpqa.rowCount())
        // Not a multi-corpus DB at all (the v2 layout has no corpus_questions table).
        val plain = File(dir.toFile(), "plain.db").absolutePath
        DriverManager.getConnection("jdbc:sqlite:$plain").use { it.createStatement().execute("CREATE TABLE mmlu_pro (id INTEGER)") }
        val onPlain = LeaderboardCorpusSource(plain, CorpusRegistry.LEADERBOARD.getValue("BBH"))
        assertEquals(0, onPlain.rowCount())
        assertThrows(IllegalStateException::class.java) { runBlocking { onPlain.fetch(Int.MAX_VALUE, emptyList()) } }
    }
}
