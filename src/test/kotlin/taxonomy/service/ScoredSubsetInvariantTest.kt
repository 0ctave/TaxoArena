package taxonomy.service

import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.spi.ILoggingEvent
import ch.qos.logback.core.read.ListAppender
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import org.mockito.Mockito.mock
import org.slf4j.LoggerFactory
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.dataset.EvalIngestValidator
import taxonomy.dataset.EvalQuestionLink
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.ModelEvalResult
import taxonomy.dataset.ModelEvalStore
import taxonomy.model.BenchmarkRequest
import taxonomy.model.GraphNode
import taxonomy.model.ModelSource
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomyOperations
import taxonomy.utils.TaxonomyPerformanceTracker
import java.io.File
import java.nio.file.Files

/**
 * |scored \ eval| == 0 (FRAMEWORK guard 1, item 18): a scored run prints `reserved_pool_id=`
 * and `scored_minus_eval=` as the first two lines of its scored section and refuses to continue
 * unless the count is 0. The count is computed against the pool's RECORDED ids, not against the
 * predicate that drew the matrix, so a store that hands back a foreign question is caught.
 * Temp DBs only.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class ScoredSubsetInvariantTest {

    private lateinit var tmp: File
    private lateinit var dbPath: String
    private lateinit var poolId: String
    private val models = listOf("m-a", "m-b")

    /** A store that, when asked, adds one question OUTSIDE the pool to the matrix. */
    private class LeakyStore(dbPath: String) : ModelEvalStore(dbPath = dbPath) {
        var leak = false
        override fun getResultsMatrix(models: List<String>, category: String?, poolId: String?, limit: Int, minModelCount: Int): Map<Int, Map<String, ModelEvalResult>> {
            val m = super.getResultsMatrix(models, category, poolId, limit, minModelCount)
            if (!leak) return m
            val extra = super.getResultsMatrix(models, category, null, 0, minModelCount).filterKeys { it !in m.keys }.entries.first()
            return m + (extra.key to extra.value)
        }
    }

    private lateinit var store: LeakyStore

    private class FakeArena(ops: TaxonomyOperations, tax: TaxonomyService, emb: EmbeddingCache) : TaxonomyArenaService(
        TaxonomyConfig(), tax, mock(TaxonomyLlmClient::class.java), emb, ops, mock(ModelEvalStore::class.java),
        mock(TaxonomyRankingService::class.java), TaxonomyPerformanceTracker()
    ) {
        override suspend fun evaluateWithPrecomputedTraces(
            query: String, options: List<String>, modelA: String, traceA: String, modelB: String, traceB: String,
            expectedNodeId: String?, frozenLeafIds: Set<String>?, gtAnswer: String?, assignedLeafIds: List<String>?,
            condition: String, isCorrectA: Boolean?, isCorrectB: Boolean?, evalQuestionId: Int?
        ): List<DomainEvaluation> = listOf(DomainEvaluation(domain = "stub", winner = "Model A", rationale = "fixed", confidence = 0.95, nodeId = expectedNodeId ?: "root"))
    }

    @BeforeAll
    fun setUp() {
        tmp = Files.createTempDirectory("scored-eval").toFile()
        dbPath = File(tmp, "dataset.db").absolutePath
        store = LeakyStore(dbPath)
        val rows = ArrayList<ModelEvalResult>()
        val links = ArrayList<EvalQuestionLink>()
        for (q in 1..6) {
            for (m in models) rows.add(ModelEvalResult(q, m, "math", "question $q", listOf("a", "b"), "A", "A", "trace", true))
            links.add(EvalQuestionLink(q, q, "question $q", true))
        }
        store.saveBatch(rows)
        store.saveLinks(links)
        poolId = store.recordReservedPool(mapOf("math" to listOf(1, 2, 3, 4)))
    }

    @AfterAll
    fun tearDown() {
        System.clearProperty("ranking.db.path")
        tmp.deleteRecursively()
    }

    private fun service(): TaxonomyBenchmarkService {
        System.setProperty("ranking.db.path", File(tmp, "ratings_${System.nanoTime()}.db").absolutePath)
        val tax = mock(TaxonomyService::class.java)
        val root = GraphNode(id = "root", label = "stub", depth = 0, judgePrompt = "stub prompt")
        org.mockito.Mockito.`when`(tax.getGraph()).thenReturn(root)
        org.mockito.Mockito.`when`(tax.activeSnapshotId()).thenReturn("stub-snapshot")
        val emb = mock(EmbeddingCache::class.java)
        runBlocking { org.mockito.Mockito.`when`(emb.getOrCreate(org.mockito.ArgumentMatchers.anyString() ?: "")).thenReturn(floatArrayOf(0.1f, 0.2f)) }
        return TaxonomyBenchmarkService(
            arenaService = FakeArena(mock(TaxonomyOperations::class.java), tax, emb),
            rankingService = TaxonomyRankingService(),
            datasetFetcher = mock(MMLUDatasetFetcher::class.java),
            taxonomyService = tax,
            evalStore = store,
            config = TaxonomyConfig(),
            perfTracker = TaxonomyPerformanceTracker(),
            ingestValidator = EvalIngestValidator(dbPath)
        )
    }

    private fun capture(block: () -> Unit): List<String> {
        val logger = LoggerFactory.getLogger("taxonomy.BenchmarkService") as Logger
        val appender = ListAppender<ILoggingEvent>().also { it.start() }
        logger.addAppender(appender)
        try { block() } finally { logger.detachAppender(appender) }
        return appender.list.map { it.formattedMessage }
    }

    private fun request(pool: String?) = BenchmarkRequest(models = models.map { ModelSource(it) }, updateRankings = false, parallelism = 1, poolId = pool)

    @Test
    fun `a clean matrix prints the pool id and 0, and the run proceeds`() {
        store.leak = false
        val lines = capture { runBlocking { service().runBenchmark(request(poolId)) } }
        val i = lines.indexOfFirst { it.startsWith("reserved_pool_id=") }
        assertTrue(i >= 0, lines.joinToString("\n"))
        assertEquals("reserved_pool_id=$poolId", lines[i])
        assertEquals("scored_minus_eval=0", lines[i + 1])
        // Nothing about the matrix is printed before the two lines.
        assertTrue(lines.take(i).none { it.startsWith("Benchmark:") || it.startsWith("[ARENA-POOL]") }, lines.take(i).joinToString("\n"))
    }

    @Test
    fun `one scored question outside the pool refuses the run after printing 1`() {
        store.leak = true
        var thrown: Throwable? = null
        val lines = try {
            capture { thrown = runCatching { runBlocking { service().runBenchmark(request(poolId)) } }.exceptionOrNull() }
        } finally {
            store.leak = false
        }
        val t = thrown
        assertTrue(t is IllegalStateException, "expected a refusal, got $t")
        assertTrue(t!!.message!!.startsWith("[SCORED-EVAL] 1 scored question(s) are not in pool $poolId"), t.message)
        // The lines were emitted before the refusal.
        val i = lines.indexOfFirst { it.startsWith("reserved_pool_id=") }
        assertEquals("reserved_pool_id=$poolId", lines[i])
        assertEquals("scored_minus_eval=1", lines[i + 1])
        assertTrue(lines.drop(i + 2).none { it.startsWith("Benchmark:") }, "no number is printed after a refusal")
    }

    @Test
    fun `no pool prints NONE and the existing WARN`() {
        store.leak = false
        val lines = capture { runBlocking { service().runBenchmark(request(null)) } }
        val i = lines.indexOfFirst { it.startsWith("reserved_pool_id=") }
        assertEquals("reserved_pool_id=NONE", lines[i])
        assertEquals("scored_minus_eval=NONE", lines[i + 1])
        assertTrue(lines.any { it.startsWith("[ARENA-POOL] no pool") }, lines.joinToString("\n"))
    }
}
