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
 * LCB-STAGE0-INTERACTION (docs/judge_v2_program.md L17702-L17982, P1 / A5): DatasetType.LIVECODEBENCH.
 *  1. INERT WHEN ABSENT: appended LAST, so every existing ordinal, table and CorpusRegistry offset is unchanged (0, 6M,
 *     7M, 8M, 9M), and the new namespace (10M) is disjoint from all of them.
 *  2. EXECUTION DISCRIMINATOR: the new fetch branch runs here on a temp Design N DB of the exact shape
 *     tools/analysis/lcb_stage0/ingest.py --construction writes, and namespaces its ids to 10,000,000 + s.
 *  3. NO REMOTE FALLBACK: an absent or empty `livecodebench` table is FATAL (the legacy loaders fetch from Hugging
 *     Face below 2,000 rows).
 *  4. The pool id of a GATE export with bare keys equals the Python mirror's (ingest.pool_id / pool_guard).
 * Temp DBs only; nothing at the repo root is touched.
 */
class LiveCodeBenchDatasetTypeTest {

    private lateinit var tmp: File

    @BeforeEach
    fun setUp() {
        tmp = Files.createTempDirectory("lcb-type").toFile()
        LcbWorkDirGuardState.checked = null            // every test starts as a fresh process
    }

    @AfterEach
    fun tearDown() {
        LcbWorkDirGuardState.checked = null
        tmp.deleteRecursively()
    }

    private fun worktree(name: String): File =
        File(tmp, name).apply { mkdirs(); File(this, ".git").writeText("gitdir: elsewhere\n") }

    private fun warm(dir: File) {
        DriverManager.getConnection("jdbc:sqlite:${File(dir, "embeddings_cache.db").absolutePath}").use { c ->
            c.createStatement().use { st ->
                st.execute("CREATE TABLE IF NOT EXISTS embeddings (query TEXT PRIMARY KEY, vector BLOB)")
                st.execute("CREATE TABLE IF NOT EXISTS queries (id TEXT PRIMARY KEY, raw_text TEXT)")
                st.execute("INSERT INTO embeddings VALUES ('Standard Input N M print the sum', x'00')")
            }
        }
    }

    @Test
    fun `the cold-cache check runs once per process - a second fetch after embedding passes (window incident)`() {
        val db = File(tmp, "lcb_construction.db")
        designN(db, listOf(Triple(2, "Standard Input N M print the sum", "atcoder")))
        val wt = worktree("wt")
        val f = fetcher(db).also { it.lcbWorkDir = wt }
        // first call, cold cache: passes and records the checked dir and cache
        assertEquals(1, runBlocking { f.fetchDataset(Int.MAX_VALUE) }.values.sumOf { it.size })
        assertEquals(wt.canonicalFile.path, LcbWorkDirGuardState.checked?.first)
        // the construction embeds: the cache is warm now; the trickle's second fetch in the SAME process passes
        warm(wt)
        assertEquals(1, runBlocking { f.fetchDataset(Int.MAX_VALUE) }.values.sumOf { it.size })
        // a second fetcher instance in the same process (same dir) passes too
        val g = fetcher(db).also { it.lcbWorkDir = wt }
        assertEquals(1, runBlocking { g.fetchDataset(Int.MAX_VALUE) }.values.sumOf { it.size })
    }

    @Test
    fun `a working dir changed within the process is refused`() {
        val db = File(tmp, "lcb_construction.db")
        designN(db, listOf(Triple(2, "Standard Input N M print the sum", "atcoder")))
        val a = worktree("a")
        val b = worktree("b")
        val f = fetcher(db).also { it.lcbWorkDir = a }
        runBlocking { f.fetchDataset(Int.MAX_VALUE) }
        f.lcbWorkDir = b
        val e = assertThrows(IllegalStateException::class.java) { runBlocking { f.fetchDataset(Int.MAX_VALUE) } }
        assertTrue(e.message!!.contains("changed within this process"), e.message)
        // and a main checkout is refused even after a first pass
        val main = File(tmp, "main").apply { File(this, ".git").mkdirs() }
        f.lcbWorkDir = main
        val e2 = assertThrows(IllegalStateException::class.java) { runBlocking { f.fetchDataset(Int.MAX_VALUE) } }
        assertTrue(e2.message!!.contains("main checkout"), e2.message)
    }

    @Test
    fun `a fresh process with a warm cache is refused`() {
        val db = File(tmp, "lcb_construction.db")
        designN(db, listOf(Triple(2, "Standard Input N M print the sum", "atcoder")))
        val wt = worktree("wt")
        val f = fetcher(db).also { it.lcbWorkDir = wt }
        runBlocking { f.fetchDataset(Int.MAX_VALUE) }
        warm(wt)
        LcbWorkDirGuardState.checked = null                 // a new JVM
        val e = assertThrows(IllegalStateException::class.java) { runBlocking { f.fetchDataset(Int.MAX_VALUE) } }
        assertTrue(e.message!!.contains("warm cache") && e.message!!.contains("embeddings"), e.message)
        assertEquals(null, LcbWorkDirGuardState.checked, "a refused check records nothing")
    }

    @Test
    fun `LIVECODEBENCH is appended last and leaves every existing ordinal, table and offset unchanged`() {
        val before = listOf(DatasetType.MMLU_PRO, DatasetType.MMLU_ORIGINAL, DatasetType.ARC, DatasetType.TWENTY_NEWSGROUPS, DatasetType.AG_NEWS)
        assertEquals(before, DatasetType.entries.take(5))
        // INTENT-TRANSFER-S1 appended INTENT after it (IntentDatasetTypeTest); LIVECODEBENCH keeps ordinal 5.
        assertEquals(DatasetType.LIVECODEBENCH, DatasetType.entries[5])
        assertEquals(7, DatasetType.entries.size)
        assertEquals(
            mapOf("MMLU_PRO" to 0, "MMLU_ORIGINAL" to 6_000_000, "ARC" to 7_000_000, "TWENTY_NEWSGROUPS" to 8_000_000,
                "AG_NEWS" to 9_000_000, "LIVECODEBENCH" to 10_000_000, "INTENT" to 11_000_000),
            CorpusRegistry.BUILTIN_OFFSETS
        )
        val registry = CorpusRegistry()
        assertEquals("livecodebench", registry.tableFor("LIVECODEBENCH"))
        assertEquals("twenty_newsgroups", registry.tableFor("TWENTY_NEWSGROUPS"))
        assertEquals(10_000_007, CorpusIds.namespaced("LIVECODEBENCH", 7))
        assertEquals("LIVECODEBENCH", CorpusIds.sourceOf(10_000_007))
        assertEquals("AG_NEWS", CorpusIds.sourceOf(9_999_999))
        val offsets = CorpusRegistry.KNOWN_OFFSETS.filterKeys { it != "MMLU_PRO_LB" }.values.toList()
        assertEquals(offsets.size, offsets.toSet().size, "namespaces must stay disjoint: $offsets")
    }

    private fun designN(path: File, rows: List<Triple<Int, String, String>>?) {
        DriverManager.getConnection("jdbc:sqlite:${path.absolutePath}").use { c ->
            c.createStatement().use { st ->
                if (rows != null) {
                    st.execute("CREATE TABLE livecodebench (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, category TEXT, cot_content TEXT, options TEXT, answer TEXT)")
                }
                st.execute("CREATE TABLE eval_question_link (question_id INTEGER PRIMARY KEY, mmlu_pro_row_id INTEGER, question_text TEXT, has_embedding INTEGER DEFAULT 0)")
                st.execute("CREATE TABLE corpus_questions (question_id INTEGER PRIMARY KEY, text TEXT)")
            }
            for ((s, text, platform) in rows.orEmpty()) {
                c.prepareStatement("INSERT INTO livecodebench (id, question, category, cot_content, options, answer) VALUES (?,?,?,'','[]','')").use {
                    it.setInt(1, s); it.setString(2, text); it.setString(3, platform); it.executeUpdate()
                }
                c.prepareStatement("INSERT INTO eval_question_link (question_id, mmlu_pro_row_id, question_text, has_embedding) VALUES (?,?,?,0)").use {
                    it.setInt(1, s); it.setInt(2, s); it.setString(3, text); it.executeUpdate()
                }
                c.prepareStatement("INSERT INTO corpus_questions (question_id, text) VALUES (?,?)").use {
                    it.setInt(1, 10_000_000 + s); it.setString(2, text); it.executeUpdate()
                }
            }
        }
    }

    private fun fetcher(db: File): MMLUDatasetFetcher {
        val config = TaxonomyConfig()
        config.dataset.datasetType = DatasetType.LIVECODEBENCH
        return MMLUDatasetFetcher(config, "", dbPath = db.absolutePath).also {
            it.reservedJsonFile = File(tmp, "reserved.json")
            it.lcbWorkDir = File(tmp, "workdir").apply { mkdirs() }       // a clean, non-checkout working dir
        }
    }

    @Test
    fun `the LIVECODEBENCH build refuses a main checkout and a warm embeddings cache (READY D7)`() {
        val db = File(tmp, "lcb_construction.db")
        designN(db, listOf(Triple(2, "Standard Input N M print the sum", "atcoder")))
        // a main checkout: .git is a DIRECTORY
        val main = File(tmp, "main").apply { File(this, ".git").mkdirs() }
        val f1 = fetcher(db).also { it.lcbWorkDir = main }
        val e1 = assertThrows(IllegalStateException::class.java) { runBlocking { f1.fetchDataset(Int.MAX_VALUE) } }
        assertTrue(e1.message!!.contains("main checkout"), e1.message)
        // a worktree (.git is a FILE) with a WARM embeddings cache
        val wt = File(tmp, "wt").apply { mkdirs(); File(this, ".git").writeText("gitdir: elsewhere\n") }
        DriverManager.getConnection("jdbc:sqlite:${File(wt, "embeddings_cache.db").absolutePath}").use { c ->
            c.createStatement().use { st ->
                st.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
                st.execute("CREATE TABLE queries (id TEXT PRIMARY KEY, raw_text TEXT)")
                st.execute("INSERT INTO queries VALUES ('q_1', 'x')")
            }
        }
        val f2 = fetcher(db).also { it.lcbWorkDir = wt }
        val e2 = assertThrows(IllegalStateException::class.java) { runBlocking { f2.fetchDataset(Int.MAX_VALUE) } }
        assertTrue(e2.message!!.contains("warm cache") && e2.message!!.contains("queries"), e2.message)
        // the same worktree with a COLD cache passes
        DriverManager.getConnection("jdbc:sqlite:${File(wt, "embeddings_cache.db").absolutePath}").use { c ->
            c.createStatement().use { it.execute("DELETE FROM queries") }
        }
        val f3 = fetcher(db).also { it.lcbWorkDir = wt }
        assertEquals(1, runBlocking { f3.fetchDataset(Int.MAX_VALUE) }.values.sumOf { it.size })
    }

    @Test
    fun `the LIVECODEBENCH branch reads the local Design N table and namespaces ids to 10M plus s`() {
        val db = File(tmp, "lcb_construction.db")
        designN(db, listOf(Triple(2, "Standard Input N M print the sum", "atcoder"),
            Triple(5, "Standard Input a string S print its length", "atcoder"),
            Triple(900, "Given an integer array nums, return the answer. Example 1:", "leetcode")))
        val data = runBlocking { fetcher(db).fetchDataset(maxQueries = Int.MAX_VALUE) }
        assertEquals(setOf("Atcoder", "Leetcode"), data.keys)
        assertEquals(listOf(10_000_002, 10_000_005), data.getValue("Atcoder").map { it.id })
        assertEquals(listOf(10_000_900), data.getValue("Leetcode").map { it.id })
        assertTrue(data.values.flatten().all { it.source == "LIVECODEBENCH" })
    }

    @Test
    fun `an absent or empty livecodebench table is fatal - there is no remote fallback`() {
        val absent = File(tmp, "absent.db")
        designN(absent, null)
        val e1 = assertThrows(IllegalStateException::class.java) { runBlocking { fetcher(absent).fetchDataset(Int.MAX_VALUE) } }
        assertTrue(e1.message!!.contains("[LCB]") && e1.message!!.contains("absent"), e1.message)
        val empty = File(tmp, "empty.db")
        designN(empty, emptyList())
        val e2 = assertThrows(IllegalStateException::class.java) { runBlocking { fetcher(empty).fetchDataset(Int.MAX_VALUE) } }
        assertTrue(e2.message!!.contains("[LCB]") && e2.message!!.contains("0 rows"), e2.message)
    }

    @Test
    fun `a GATE export with bare keys hashes to the Python mirror's pool id`() {
        // tools/analysis/lcb_stage0/ingest.pool_id({"Atcoder": [10000002, 10000005], "Leetcode": [10000900]})
        assertEquals("p18f636cf43ccf660",
            ReservedPool.computePoolId(mapOf("Atcoder" to listOf(10_000_002, 10_000_005), "Leetcode" to listOf(10_000_900))))
    }
}
