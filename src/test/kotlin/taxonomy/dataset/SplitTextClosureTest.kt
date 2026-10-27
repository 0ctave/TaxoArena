package taxonomy.dataset

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import taxonomy.config.TaxonomyConfig
import java.io.File
import java.nio.file.Files

/**
 * Content closure of the split (FRAMEWORK item 18, TRAIN-ONLY-TREE): the id-list split is not
 * closed under text equality (a sentinel-id row that duplicates an EVAL question, a linked
 * duplicate under another id), so an item whose text equals a test item's text must land in
 * test as a routing-only member, never in train, without changing the file's pool id; the GATE
 * slice is disjoint from every test id; every item's side equals f(item).
 * Temp DB, temp JSON transport; nothing at the repo root is touched.
 */
class SplitTextClosureTest {

    private lateinit var tmp: File
    private lateinit var fetcher: MMLUDatasetFetcher

    private val evalText = "What is the capital of France?"
    private val dataset: Map<String, List<MMLUQuery>> = mapOf(
        "Geography" to listOf(
            MMLUQuery(101, evalText, "Geography"),
            MMLUQuery(102, "What is the capital of Spain?", "Geography"),
            MMLUQuery(103, "What is the capital of Italy?", "Geography"),
            MMLUQuery(104, "What is the capital of Peru?", "Geography"),
            // A sentinel-id (unlinked) duplicate of the EVAL text: must never sit on the train side.
            MMLUQuery(UNLINKED_QUERY_ID_BASE - 7, "  what IS the capital   of France? ", "Geography"),
            // A linked duplicate under another id: same.
            MMLUQuery(105, "What is the capital of France?", "Geography"),
        ),
        "History" to (1..12).map { MMLUQuery(200 + it, "History question number $it", "History") }
    )

    @BeforeEach
    fun setUp() {
        tmp = Files.createTempDirectory("split-closure").toFile()
        fetcher = MMLUDatasetFetcher(TaxonomyConfig(), "", dbPath = File(tmp, "dataset.db").absolutePath)
        fetcher.reservedJsonFile = File(tmp, "reserved_test_queries.json")
    }

    @AfterEach
    fun tearDown() { tmp.deleteRecursively() }

    private fun ids(m: Map<String, List<MMLUQuery>>) = m.values.flatten().map { it.id }.toSet()

    @Test
    fun `splitByReservedFile closes train under content and keeps the file's pool id`() {
        val file = File(tmp, "pinned.json")
        file.writeText("""{ "Geography": [101, 102], "History": [201, 202, 203] }""")
        val filePool = ReservedPool.computePoolId(mapOf("Geography" to listOf(101, 102), "History" to listOf(201, 202, 203)))

        val split = fetcher.splitByReservedFile(dataset, file)

        assertEquals(filePool, split.poolId, "content closure never changes the judgeable id list")
        assertEquals(2, split.closedByContent)
        val test = ids(split.test)
        val train = ids(split.train)
        assertTrue(101 in test && 105 in test && (UNLINKED_QUERY_ID_BASE - 7) in test, "both duplicates are test members: $test")
        assertFalse(105 in train || (UNLINKED_QUERY_ID_BASE - 7) in train)
        assertTrue((train intersect test).isEmpty())
        assertTrue((split.gate intersect test).isEmpty(), "|gate and eval| == 0")
        assertTrue(split.gate.all { it in train })
        // The transport is the file, verbatim: the snapshot stores exactly the pinned list.
        assertEquals(file.readText(), fetcher.reservedJsonFile.readText())
        // The pool is recorded by id, nothing activated.
        assertEquals(setOf(101, 102, 201, 202, 203), java.sql.DriverManager.getConnection("jdbc:sqlite:${File(tmp, "dataset.db").absolutePath}").use { c ->
            ReservedPool.questionIds(c, filePool)
        })
    }

    @Test
    fun `splitTrainTest with a seed closes the same way and gates only train`() {
        var sawClosure = false
        for (seed in 1L..20L) {
            val split = fetcher.splitTrainTest(dataset, testRatio = 0.3, seed = seed)
            val test = ids(split.test)
            val train = ids(split.train)
            val dupIds = setOf(101, 105, UNLINKED_QUERY_ID_BASE - 7)
            val inTest = dupIds.count { it in test }
            // Either none of the three copies was drawn into test, or all three end up there.
            assertTrue(inTest == 0 || inTest == 3, "seed $seed: $inTest of the three copies in test")
            if (split.closedByContent > 0) sawClosure = true
            assertTrue((train intersect test).isEmpty())
            assertTrue((split.gate intersect test).isEmpty(), "seed $seed: |gate and eval| == 0")
            assertTrue(split.gate.all { it in train })
            // The recorded pool id is the id-list hash of the seeded draw (sentinels excluded).
            val drawn: Map<String, List<Int>> = kotlinx.serialization.json.Json.decodeFromString(fetcher.reservedJsonFile.readText())
            assertEquals(ReservedPool.computePoolId(ReservedPoolRegistry.judgeable(drawn)), split.poolId)
        }
        assertTrue(sawClosure, "some seed must draw one copy and not the others")
    }

    @Test
    fun `the per-item side assertion trips on a tampered landing set`() {
        // tierA is the function of record; a train item whose text is EVAL must be EVAL.
        val pinnedIds = setOf(101)
        val pinnedKeys = setOf(SplitSide.stemKey(evalText))
        assertEquals(Side.EVAL, SplitSide.tierA(pinnedIds, pinnedKeys, 105, SplitSide.stemKey("What is the capital of France?")))
        assertEquals(Side.EVAL, SplitSide.tierA(pinnedIds, pinnedKeys, UNLINKED_QUERY_ID_BASE - 7, SplitSide.stemKey("  what IS the capital   of France? ")))
        // A landing set that leaves 104 in TRAIN although the id list pins it: f says EVAL.
        val geo = dataset.getValue("Geography")
        val train = mutableMapOf("Geography" to geo.filter { it.id != 101 })
        val test = mutableMapOf("Geography" to geo.filter { it.id == 101 })
        val e = org.junit.jupiter.api.Assertions.assertThrows(IllegalStateException::class.java) {
            fetcher.finishSplit(train, test, mapOf("Geography" to listOf(101, 104)), "ptest")
        }
        assertTrue(e.message!!.startsWith("[SPLIT-SIDE] item 104 landed in"), e.message)
        assertTrue(e.message!!.endsWith("but f = EVAL"), e.message)
    }
}
