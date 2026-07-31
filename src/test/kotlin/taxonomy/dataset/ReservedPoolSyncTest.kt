package taxonomy.dataset

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import java.io.File
import java.nio.file.Files

/**
 * Guards that the two code paths which record a reserved pool converge on ONE pool.
 *
 * [MMLUDatasetFetcher.splitTrainTest] records the pool at split time, where the seed, ratio and
 * corpus size are known. [ModelEvalLoader.syncReservedPool] records it from
 * reserved_test_queries.json, which is also the path a restored snapshot goes through. Because
 * the id is a hash of the contents, the two agree only if they hash the same id set — and the
 * JSON contains sentinel ids that the fetcher excludes. Hashing the raw JSON here would mint a
 * second pool id for the identical split, quietly reintroducing the duplication the
 * content-addressing exists to prevent.
 */
class ReservedPoolSyncTest {

    private lateinit var tmp: File
    private lateinit var store: ModelEvalStore
    private lateinit var loader: ModelEvalLoader
    private lateinit var reservedFile: File

    // Two real ids per domain plus one sentinel, mirroring what splitTrainTest writes when a
    // question has no eval_question_link entry.
    private val positives = mapOf("Math" to listOf(101, 102), "Physics" to listOf(201, 202))
    private val sentinel = -1_000_042

    @BeforeEach
    fun setUp() {
        tmp = Files.createTempDirectory("reserved-sync-test").toFile()
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
        loader = ModelEvalLoader(
            store = store,
            datasetFetcher = mock(MMLUDatasetFetcher::class.java),
            datasetDbPath = datasetDb,
            embeddingDbPath = File(tmp, "emb.db").absolutePath,
            reservedFilePath = reservedFile.absolutePath
        )
    }

    @AfterEach
    fun tearDown() {
        tmp.deleteRecursively()
    }

    @Test
    fun `sync records the judgeable pool and ignores sentinels`() {
        loader.syncReservedPool(reservedFile)

        val expected = ReservedPool.computePoolId(positives)
        assertEquals(
            expected, store.activeReservedPoolId(),
            "the sync must hash only the judgeable ids, so it lands on the same pool the " +
                "fetcher recorded at split time"
        )
        assertEquals(1, store.listReservedPools().size, "exactly one pool, not one per code path")
        assertEquals(setOf(101, 102, 201, 202), store.reservedPoolQuestionIds(expected))
    }

    @Test
    fun `re-syncing the same file does not create a second pool`() {
        loader.syncReservedPool(reservedFile)
        loader.syncReservedPool(reservedFile)
        assertEquals(1, store.listReservedPools().size)
    }

    @Test
    fun `a narrower split becomes a separate pool and the first survives`() {
        // The destructive sequence this guards against: a single-domain smoke run follows a
        // multi-domain baseline. Both pools must remain recorded.
        loader.syncReservedPool(reservedFile)
        val baseline = store.activeReservedPoolId()!!

        reservedFile.writeText("""{ "Math": [101] }""")
        loader.syncReservedPool(reservedFile)
        val smoke = store.activeReservedPoolId()!!

        assert(baseline != smoke)
        assertEquals(2, store.listReservedPools().size)
        // Recovery is now an activation, not a file restore.
        store.activateReservedPool(baseline)
        assertEquals(baseline, store.activeReservedPoolId())
        assertEquals(setOf(101, 102, 201, 202), store.reservedPoolQuestionIds(baseline))
    }
}
