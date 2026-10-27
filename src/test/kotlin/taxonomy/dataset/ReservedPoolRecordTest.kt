package taxonomy.dataset

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import java.io.File
import java.nio.file.Files
import java.sql.DriverManager

/**
 * Guards that recording a pool from an id file converges on the ONE pool the fetcher records
 * at split time, and that recording is all a writer can do (record-only semantics, FRAMEWORK
 * item 18): nothing is activated, no `eval_results` row is flagged, and the pool tables carry
 * no active pointer.
 *
 * Because the id is a hash of the contents, the file path and the split path agree only if
 * they hash the same id set — and an id file contains sentinel ids that the fetcher excludes.
 * Hashing the raw file would mint a second pool id for the identical split.
 */
class ReservedPoolRecordTest {

    private lateinit var tmp: File
    private lateinit var store: ModelEvalStore
    private lateinit var reservedFile: File

    // Two real ids per domain plus one sentinel, mirroring what splitTrainTest writes when a
    // question has no eval_question_link entry.
    private val positives = mapOf("Math" to listOf(101, 102), "Physics" to listOf(201, 202))
    private val sentinel = -1_000_042

    @BeforeEach
    fun setUp() {
        tmp = Files.createTempDirectory("reserved-record-test").toFile()
        val datasetDb = File(tmp, "dataset.db").absolutePath
        reservedFile = File(tmp, "reserved_test_queries.json")
        reservedFile.writeText(
            """
            {
              "Math": [101, 102],
              "Physics": [201, 202, $sentinel]
            }
            """.trimIndent()
        )
        store = ModelEvalStore(dbPath = datasetDb)
    }

    @AfterEach
    fun tearDown() {
        tmp.deleteRecursively()
    }

    private fun recordFromFile(file: File): String {
        val raw: Map<String, List<Int>> = kotlinx.serialization.json.Json.decodeFromString(file.readText())
        return store.recordReservedPool(ReservedPoolRegistry.judgeable(raw))
    }

    private fun columnsOf(table: String): List<String> {
        val out = ArrayList<String>()
        DriverManager.getConnection("jdbc:sqlite:${store.dbPath}").use { c ->
            c.createStatement().use { s -> s.executeQuery("PRAGMA table_info($table)").use { rs -> while (rs.next()) out.add(rs.getString("name")) } }
        }
        return out
    }

    private fun tables(): Set<String> {
        val out = HashSet<String>()
        DriverManager.getConnection("jdbc:sqlite:${store.dbPath}").use { c ->
            c.createStatement().use { s -> s.executeQuery("SELECT name FROM sqlite_master WHERE type = 'table'").use { rs -> while (rs.next()) out.add(rs.getString(1)) } }
        }
        return out
    }

    @Test
    fun `recording from an id file mints the same id as the split and ignores sentinels`() {
        val recorded = recordFromFile(reservedFile)
        val expected = ReservedPool.computePoolId(positives)
        assertEquals(
            expected, recorded,
            "the file must hash only the judgeable ids, so it lands on the same pool the fetcher recorded at split time"
        )
        assertEquals(1, store.listReservedPools().size, "exactly one pool, not one per code path")
        assertEquals(setOf(101, 102, 201, 202), store.reservedPoolQuestionIds(expected))
        assertTrue(store.isReservedPoolRecorded(expected))
    }

    @Test
    fun `re-recording the same file is idempotent`() {
        recordFromFile(reservedFile)
        recordFromFile(reservedFile)
        assertEquals(1, store.listReservedPools().size)
    }

    @Test
    fun `a narrower pool is a separate pool and the first survives`() {
        // The destructive sequence this guards against: a single-domain smoke run follows a
        // multi-domain baseline. Both pools must remain recorded and readable by id.
        val baseline = recordFromFile(reservedFile)
        reservedFile.writeText("""{ "Math": [101] }""")
        val smoke = recordFromFile(reservedFile)

        assertNotEquals(baseline, smoke)
        assertEquals(2, store.listReservedPools().size)
        assertEquals(setOf(101, 102, 201, 202), store.reservedPoolQuestionIds(baseline))
        assertEquals(setOf(101), store.reservedPoolQuestionIds(smoke))
    }

    @Test
    fun `nothing is activated and no row carries a side flag`() {
        recordFromFile(reservedFile)
        assertFalse("active_reserved_pool" in tables(), "no active pool table: ${tables()}")
        assertFalse("is_reserved" in columnsOf("eval_results"), "a fresh eval_results has no side column: ${columnsOf("eval_results")}")
        assertEquals(0, store.getStats()["totalRows"])
        assertEquals(1, store.getStats()["recordedPools"])
    }
}
