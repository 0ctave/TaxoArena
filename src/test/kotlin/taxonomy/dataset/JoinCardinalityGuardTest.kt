package taxonomy.dataset

import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import taxonomy.config.DatasetType
import taxonomy.config.TaxonomyConfig
import java.io.File
import java.nio.file.Files
import java.sql.DriverManager

/**
 * JOIN-CARDINALITY-GUARD: MMLUDatasetFetcher.loadFromDb's LEFT JOIN onto eval_question_link may not emit a local row
 * twice. Driven through the REAL entry point (fetchDataset on a LIVECODEBENCH temp DB; that branch is local-only, so no
 * network fallback can mask the load), on temp DBs only.
 *  1. INERT + EXECUTED: a clean link table loads exactly the rows and ids it loaded before the guard (the LCB golden
 *     ids 10,000,002 / 10,000,005 / 10,000,900), and the guard's counters prove it ran over those 3 joined rows.
 *  2. FIRES ON THE ENTRY POINT: a second link row on one local row makes fetchDataset throw JoinCardinalityException
 *     (not a logged partial load), naming table, counts and the ids.
 *  3. Unit edges: empty input, unlinked (null) rows, and fan-out at TWO local rows (all sites counted, not the first).
 *
 * MUTANTS (temporary edits to main, each run against this class, reverted; see the commit message for the table):
 *  K1 `it.size > 1` -> `it.size > 2`; K2 the loader's `catch (e: JoinCardinalityException) { throw e }` removed (fail
 *  open into the generic catch); K3 the guard call removed from loadFromDb; K4 extra = fanned.size (first-site count);
 *  K5 guard returns before checking; K6 the guard reads only the first 1 pair (pairs.take(1)).
 */
class JoinCardinalityGuardTest {

    private lateinit var tmp: File

    @BeforeEach
    fun setUp() {
        tmp = Files.createTempDirectory("join-card").toFile()
        LcbWorkDirGuardState.checked = null
    }

    @AfterEach
    fun tearDown() {
        LcbWorkDirGuardState.checked = null
        tmp.deleteRecursively()
    }

    private fun db(rows: List<Triple<Int, String, String>>, extraLinks: List<Pair<Int, Int>> = emptyList()): File {
        val path = File(tmp, "lcb_construction.db")
        DriverManager.getConnection("jdbc:sqlite:${path.absolutePath}").use { c ->
            c.createStatement().use { st ->
                st.execute("CREATE TABLE livecodebench (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, category TEXT, cot_content TEXT, options TEXT, answer TEXT)")
                st.execute("CREATE TABLE eval_question_link (question_id INTEGER PRIMARY KEY, mmlu_pro_row_id INTEGER, question_text TEXT, has_embedding INTEGER DEFAULT 0)")
                st.execute("CREATE TABLE corpus_questions (question_id INTEGER PRIMARY KEY, text TEXT)")
            }
            for ((s, text, platform) in rows) {
                c.prepareStatement("INSERT INTO livecodebench (id, question, category, cot_content, options, answer) VALUES (?,?,?,'','[]','')").use {
                    it.setInt(1, s); it.setString(2, text); it.setString(3, platform); it.executeUpdate()
                }
                c.prepareStatement("INSERT INTO eval_question_link (question_id, mmlu_pro_row_id, question_text, has_embedding) VALUES (?,?,?,0)").use {
                    it.setInt(1, s); it.setInt(2, s); it.setString(3, text); it.executeUpdate()
                }
            }
            for ((upstream, local) in extraLinks) {
                c.prepareStatement("INSERT INTO eval_question_link (question_id, mmlu_pro_row_id, question_text, has_embedding) VALUES (?,?,'dup',0)").use {
                    it.setInt(1, upstream); it.setInt(2, local); it.executeUpdate()
                }
            }
        }
        return path
    }

    private fun fetcher(db: File): MMLUDatasetFetcher {
        val config = TaxonomyConfig()
        config.dataset.datasetType = DatasetType.LIVECODEBENCH
        return MMLUDatasetFetcher(config, "", dbPath = db.absolutePath).also {
            it.reservedJsonFile = File(tmp, "reserved.json")
            it.lcbWorkDir = File(tmp, "workdir").apply { mkdirs() }
        }
    }

    private val three = listOf(
        Triple(2, "Standard Input N M print the sum", "atcoder"),
        Triple(5, "Standard Input a string S print its length", "atcoder"),
        Triple(900, "Given an integer array nums, return the answer. Example 1:", "leetcode"))

    @Test
    fun `a clean link table loads the same rows and ids, and the guard ran over them`() {
        val checks0 = JoinCardinalityGuard.checks.get()
        val rows0 = JoinCardinalityGuard.rowsChecked.get()
        val data = runBlocking { fetcher(db(three)).fetchDataset(maxQueries = Int.MAX_VALUE) }
        assertEquals(listOf(10_000_002, 10_000_005), data.getValue("Atcoder").map { it.id })
        assertEquals(listOf(10_000_900), data.getValue("Leetcode").map { it.id })
        assertEquals(3, data.values.sumOf { it.size })
        assertEquals(1L, JoinCardinalityGuard.checks.get() - checks0, "the guard must execute exactly once per load")
        assertEquals(3L, JoinCardinalityGuard.rowsChecked.get() - rows0, "the guard must see every joined row")
    }

    @Test
    fun `a local row linked twice is refused at fetchDataset, not loaded twice`() {
        val path = db(three, extraLinks = listOf(99 to 2))
        val e = assertThrows(JoinCardinalityException::class.java) {
            runBlocking { fetcher(path).fetchDataset(maxQueries = Int.MAX_VALUE) }
        }
        val m = e.message!!
        assertTrue(m.startsWith("[JOIN-CARDINALITY] livecodebench LEFT JOIN eval_question_link: 1 local row(s)"), m)
        assertTrue(m.contains("(1 extra row(s) of 4)"), m)
        assertTrue(m.contains("local 2 -> upstream [2, 99]"), m)
        assertTrue(m.endsWith("REFUSED. Repair eval_question_link so each mmlu_pro_row_id is linked at most once."), m)
    }

    @Test
    fun `unit edges - empty, unlinked rows, and fan-out at two local rows counts every site`() {
        JoinCardinalityGuard.assertAtMostOnePerLocalRow("t", emptyList())
        JoinCardinalityGuard.assertAtMostOnePerLocalRow("t", listOf(1 to null, 2 to null, 3 to 30))
        val e = assertThrows(JoinCardinalityException::class.java) {
            JoinCardinalityGuard.assertAtMostOnePerLocalRow("t", listOf(1 to 10, 2 to 20, 1 to 11, 3 to 30, 2 to 21, 2 to 22))
        }
        val m = e.message!!
        assertTrue(m.contains("t LEFT JOIN eval_question_link: 2 local row(s)"), m)
        assertTrue(m.contains("(3 extra row(s) of 6)"), m)
        assertTrue(m.contains("first: local 1 -> upstream [10, 11]; local 2 -> upstream [20, 21, 22]."), m)
    }
}
