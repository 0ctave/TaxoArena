package taxonomy.dataset

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import java.nio.file.Files
import java.sql.Connection
import java.sql.DriverManager

/**
 * Guards the reserved-pool store.
 *
 * The properties under test are the ones whose absence caused real damage: pools must be able
 * to COEXIST (a Math smoke run previously destroyed a 14-domain baseline pool, and a unit test
 * reduced it to three questions), activation must be an exact round trip so recovery is not a
 * manual file restore, and the id must be a function of contents alone so two code paths
 * recording the same split converge instead of duplicating it.
 *
 * Uses a throwaway temp database; the production cache is never opened.
 */
class ReservedPoolTest {

    private lateinit var dbFile: java.io.File
    private lateinit var c: Connection

    @BeforeEach
    fun setUp() {
        dbFile = Files.createTempFile("reserved-pool-test", ".db").toFile()
        c = DriverManager.getConnection("jdbc:sqlite:${dbFile.absolutePath}").also { it.autoCommit = true }
        // Minimal stand-in for eval_results: activation mirrors onto it.
        c.createStatement().use { s ->
            s.execute(
                """
                CREATE TABLE eval_results (
                    question_id INTEGER NOT NULL, model_name TEXT NOT NULL,
                    is_reserved INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (question_id, model_name)
                )
                """.trimIndent()
            )
            // 6 questions x 2 models
            for (q in 1..6) for (m in listOf("model-a", "model-b")) {
                s.execute("INSERT INTO eval_results (question_id, model_name) VALUES ($q, '$m')")
            }
        }
        ReservedPool.ensureSchema(c)
    }

    @AfterEach
    fun tearDown() {
        runCatching { c.close() }
        dbFile.delete()
    }

    private fun reservedIds(): Set<Int> {
        val out = LinkedHashSet<Int>()
        c.createStatement().use { s ->
            s.executeQuery("SELECT DISTINCT question_id FROM eval_results WHERE is_reserved = 1")
                .use { rs -> while (rs.next()) out.add(rs.getInt(1)) }
        }
        return out
    }

    private fun save(ids: Map<String, List<Int>>) =
        ReservedPool.save(c, ids, dataset = "mmlu_pro", corpusSize = 6, seed = 42L, testRatio = 0.3, nowMillis = 1_000L)

    // ── identity ─────────────────────────────────────────────────────────────────────

    @Test
    fun `pool id depends on contents, not on ordering`() {
        val a = ReservedPool.computePoolId(mapOf("math" to listOf(1, 2, 3), "physics" to listOf(4)))
        val b = ReservedPool.computePoolId(mapOf("physics" to listOf(4), "math" to listOf(3, 1, 2)))
        assertEquals(a, b, "the split shuffles; emission order must not change the pool identity")
    }

    @Test
    fun `pool id changes when the stratification changes`() {
        val a = ReservedPool.computePoolId(mapOf("math" to listOf(1, 2)))
        val b = ReservedPool.computePoolId(mapOf("physics" to listOf(1, 2)))
        assertNotEquals(a, b, "the same ids under a different stratum are a different pool")
    }

    @Test
    fun `pool id changes when a question is added`() {
        val a = ReservedPool.computePoolId(mapOf("math" to listOf(1, 2)))
        val b = ReservedPool.computePoolId(mapOf("math" to listOf(1, 2, 3)))
        assertNotEquals(a, b)
    }

    @Test
    fun `pool id is pinned`() {
        // Pinned so the algorithm cannot drift silently: any out-of-band tool that has to
        // resolve the same pool (a migration, an analysis script) must produce this exact value
        // for this exact input. SHA-256 over the sorted "domain:id" lines joined by newlines,
        // first 8 bytes, hex, prefixed 'p'.
        assertEquals(
            "p91e287c58c93a041",
            ReservedPool.computePoolId(mapOf("math" to listOf(1, 2), "physics" to listOf(3)))
        )
    }

    // ── coexistence: the property whose absence destroyed a baseline pool ────────────

    @Test
    fun `two pools coexist and activation switches between them exactly`() {
        val big = save(mapOf("math" to listOf(1, 2, 3), "physics" to listOf(4, 5)))
        val small = save(mapOf("math" to listOf(6)))
        assertNotEquals(big, small)

        ReservedPool.activate(c, big, 2_000L)
        assertEquals(setOf(1, 2, 3, 4, 5), reservedIds())

        // The destructive scenario this guards against: a small single-domain run follows a large one.
        ReservedPool.activate(c, small, 3_000L)
        assertEquals(setOf(6), reservedIds(), "activation must replace, not union")

        // ...and the large pool is still recorded, so recovery is exact rather than a file restore.
        ReservedPool.activate(c, big, 4_000L)
        assertEquals(setOf(1, 2, 3, 4, 5), reservedIds(), "the earlier pool survived the smaller run")
        assertEquals(2, ReservedPool.list(c).size)
    }

    @Test
    fun `saving the same split twice is idempotent`() {
        val first = save(mapOf("math" to listOf(1, 2)))
        val second = save(mapOf("math" to listOf(2, 1)))
        assertEquals(first, second)
        assertEquals(1, ReservedPool.list(c).size, "content addressing must not create a second pool")
        assertEquals(setOf(1, 2), ReservedPool.questionIds(c, first))
    }

    @Test
    fun `activation flags every model row for a question`() {
        val p = save(mapOf("math" to listOf(1, 2)))
        ReservedPool.activate(c, p, 2_000L)
        c.createStatement().use { s ->
            s.executeQuery("SELECT COUNT(*) FROM eval_results WHERE is_reserved = 1").use { rs ->
                rs.next()
                assertEquals(4, rs.getInt(1), "2 questions x 2 models — the pool is model-independent")
            }
        }
    }

    // ── provenance and guards ────────────────────────────────────────────────────────

    @Test
    fun `metadata and active flag round-trip`() {
        assertNull(ReservedPool.activeId(c), "nothing is active before the first activation")
        val p = save(mapOf("math" to listOf(1, 2, 3)))
        ReservedPool.activate(c, p, 5_000L)

        assertEquals(p, ReservedPool.activeId(c))
        val info = ReservedPool.list(c).single()
        assertEquals(3, info.questionCount)
        assertEquals(1, info.domainCount)
        assertEquals("mmlu_pro", info.dataset)
        assertEquals(42L, info.seed)
        assertEquals(0.3, info.testRatio!!, 1e-12)
        assertEquals(6, info.corpusSize)
        assertTrue(info.isActive)
    }

    @Test
    fun `activating an unknown pool is refused`() {
        val e = assertThrows(IllegalArgumentException::class.java) {
            ReservedPool.activate(c, "pdeadbeefdeadbeef", 1_000L)
        }
        assertTrue(e.message!!.contains("Unknown reserved pool"))
        assertEquals(emptySet<Int>(), reservedIds(), "a failed activation must not clear the mirror")
    }

    @Test
    fun `a pool may contain ids absent from eval_results`() {
        // Sentinel/unlinked questions are excluded upstream, but a pool recorded elsewhere may
        // still name an id no model answered; that must not fail activation.
        val p = save(mapOf("math" to listOf(1, 999)))
        ReservedPool.activate(c, p, 2_000L)
        assertEquals(setOf(1), reservedIds())
        assertEquals(setOf(1, 999), ReservedPool.questionIds(c, p))
    }
}
