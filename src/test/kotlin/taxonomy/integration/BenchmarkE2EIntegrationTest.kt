package taxonomy.integration

import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.add
import kotlinx.serialization.json.buildJsonArray
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import org.mockito.Mockito.mock
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.ModelEvalLoader
import taxonomy.dataset.ModelEvalStore
import taxonomy.model.BenchmarkRequest
import taxonomy.model.ModelSource
import taxonomy.model.GraphNode
import taxonomy.model.Embedding
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomyOperations
import taxonomy.service.DomainEvaluation
import taxonomy.service.TaxonomyArenaService
import taxonomy.service.TaxonomyBenchmarkService
import taxonomy.service.TaxonomyRankingService
import taxonomy.service.TaxonomyService
import java.io.File
import java.nio.file.Files
import java.sql.DriverManager
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

/**
 * End-to-end integration test for the precomputed-results arena benchmark.
 *
 * Drives the *real* data pipeline — ZIP parse → ingest (cross-referencing the
 * mmlu_pro + embeddings tables) → reserved-pool sync → results-matrix intersection →
 * benchmark aggregation — against temp-isolated SQLite files. Only the LLM judge is
 * stubbed: [FakeArenaService] overrides the routing/judging step with a fixed verdict,
 * so the test asserts on the data plumbing rather than on vMF routing math.
 *
 * Synthetic dataset: 2 models × 8 questions (ids 1..8), categories math (1-4) and
 * physics (5-8). Four questions (1, 2, 5, 6 — spanning both categories) are reserved.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class BenchmarkE2EIntegrationTest {

    private data class Q(
        val id: Int,
        val text: String,
        val category: String,
        val answer: String,
        val answerIndex: Int
    )

    private val options = listOf("first", "second", "third", "fourth")

    private val questions = listOf(
        Q(1, "math q1: 2+2?", "math", "A", 0),
        Q(2, "math q2: derivative of x^2?", "math", "B", 1),
        Q(3, "math q3: integral of 1?", "math", "A", 0),
        Q(4, "math q4: prime after 7?", "math", "C", 2),
        Q(5, "physics q5: unit of force?", "physics", "A", 0),
        Q(6, "physics q6: speed of light?", "physics", "B", 1),
        Q(7, "physics q7: Newton's 2nd law?", "physics", "A", 0),
        Q(8, "physics q8: charge of electron?", "physics", "D", 3),
    )

    private val reservedIds = setOf(1, 2, 5, 6)
    private val modelA = "model-alpha"
    private val modelB = "model-beta"

    private lateinit var store: ModelEvalStore
    private lateinit var benchmarkService: TaxonomyBenchmarkService
    private lateinit var tmp: File
    private lateinit var mockOps: TaxonomyOperations
    private lateinit var mockTaxonomyService: TaxonomyService
    private lateinit var mockEmbeddingCache: EmbeddingCache
    private lateinit var datasetFetcher: MMLUDatasetFetcher

    /**
     * Subclass of the real arena service that bypasses embedding/routing/LLM calls and
     * returns a fixed high-confidence verdict — the "stubbed judge". Constructor deps are
     * mocked (Mockito bypasses their constructors), and the only overridden method is the
     * one the benchmark service calls.
     */
    private class FakeArenaService(
        ops: TaxonomyOperations,
        taxService: TaxonomyService,
        embCache: EmbeddingCache
    ) : TaxonomyArenaService(
        mock(TaxonomyConfig::class.java),
        taxService,
        mock(TaxonomyLlmClient::class.java),
        embCache,
        ops,
        mock(ModelEvalStore::class.java),
        mock(TaxonomyRankingService::class.java),
    ) {
        override suspend fun evaluateWithPrecomputedTraces(
            query: String,
            options: List<String>,
            modelA: String,
            traceA: String,
            modelB: String,
            traceB: String,
            expectedNodeId: String?,
            frozenLeafIds: Set<String>?,
            gtAnswer: String?,
            assignedLeafIds: List<String>?
        ): List<DomainEvaluation> = listOf(
            DomainEvaluation(
                domain = "stub-leaf-judge",
                winner = "Model A",
                rationale = "fixed verdict",
                confidence = 0.95,
                nodeId = expectedNodeId ?: "root"
            )
        )
    }

    @BeforeAll
    fun setup() {
        tmp = Files.createTempDirectory("benchmark-e2e").toFile()
        val datasetDb = File(tmp, "dataset.db").absolutePath      // holds mmlu_pro + eval_results
        val embeddingDb = File(tmp, "embeddings.db").absolutePath // holds embeddings cache
        val reservedFile = File(tmp, "reserved_test_queries.json")

        // Seed mmlu_pro (so links resolve mmlu_pro_row_id) in the dataset DB.
        DriverManager.getConnection("jdbc:sqlite:$datasetDb").use { c ->
            c.createStatement().use { s ->
                s.execute("CREATE TABLE IF NOT EXISTS mmlu_pro (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT)")
            }
            c.prepareStatement("INSERT INTO mmlu_pro (question) VALUES (?)").use { ps ->
                questions.forEach { ps.setString(1, it.text); ps.executeUpdate() }
            }
        }

        // Seed embeddings cache (so links get has_embedding = 1) in the embedding DB.
        DriverManager.getConnection("jdbc:sqlite:$embeddingDb").use { c ->
            c.createStatement().use { s ->
                s.execute("CREATE TABLE IF NOT EXISTS embeddings (query TEXT PRIMARY KEY, vector BLOB)")
            }
            c.prepareStatement("INSERT INTO embeddings (query) VALUES (?)").use { ps ->
                questions.forEach { ps.setString(1, it.text); ps.executeUpdate() }
            }
        }

        // reserved_test_queries.json: category -> reserved question texts.
        val reservedByCategory = questions
            .filter { it.id in reservedIds }
            .groupBy { it.category }
            .mapValues { (_, qs) -> qs.map { it.text } }
        reservedFile.writeText(buildReservedJson(reservedByCategory))

        // Build per-model eval ZIPs (model A answers all "A", model B all "B").
        val zipA = buildEvalZip(tmp, "model_outputs_$modelA", predFor = { "A" })
        val zipB = buildEvalZip(tmp, "model_outputs_$modelB", predFor = { "B" })

        store = ModelEvalStore(dbPath = datasetDb)
        datasetFetcher = mock(MMLUDatasetFetcher::class.java)
        val loader = ModelEvalLoader(
            store = store,
            datasetFetcher = datasetFetcher,
            datasetDbPath = datasetDb,
            embeddingDbPath = embeddingDb,
            reservedFilePath = reservedFile.absolutePath
        )

        // Run the real load + reserved-sync chain.
        runBlocking {
            loader.loadFromZip(zipA.absolutePath, modelA)
            loader.loadFromZip(zipB.absolutePath, modelB)
        }
        loader.syncReservedPool(reservedFile)

        val dummyRoot = GraphNode(id = "root", label = "stub-leaf-judge", depth = 0, judgePrompt = "stub prompt")
        mockTaxonomyService = mock(TaxonomyService::class.java)
        org.mockito.Mockito.`when`(mockTaxonomyService.getGraph()).thenReturn(dummyRoot)
        org.mockito.Mockito.`when`(mockTaxonomyService.activeSnapshotId()).thenReturn("stubbed-snapshot")

        mockEmbeddingCache = mock(EmbeddingCache::class.java)
        runBlocking {
            org.mockito.Mockito.`when`(mockEmbeddingCache.getOrCreate(org.mockito.ArgumentMatchers.anyString() ?: ""))
                .thenReturn(floatArrayOf(0.1f, 0.2f))
        }

        mockOps = mock(TaxonomyOperations::class.java)
        org.mockito.Mockito.`when`(mockOps.routeQuery(
            org.mockito.ArgumentMatchers.any(Embedding::class.java) ?: Embedding("", "", floatArrayOf()),
            org.mockito.ArgumentMatchers.any(GraphNode::class.java) ?: dummyRoot,
            org.mockito.ArgumentMatchers.anyInt(),
            org.mockito.ArgumentMatchers.any()
        )).thenReturn(mapOf(dummyRoot to 1.0))
    }

    private fun recreateBenchmarkService() {
        val rankingDb = File(tmp, "ratings_${System.nanoTime()}.db")
        System.setProperty("ranking.db.path", rankingDb.absolutePath)
        val rankingService = TaxonomyRankingService()
        System.clearProperty("ranking.db.path")

        benchmarkService = TaxonomyBenchmarkService(
            arenaService = FakeArenaService(mockOps, mockTaxonomyService, mockEmbeddingCache),
            rankingService = rankingService,
            datasetFetcher = datasetFetcher,
            taxonomyService = mockTaxonomyService,
            evalStore = store
        )
    }

    @BeforeEach
    fun cleanDatabase() {
        recreateBenchmarkService()
    }

    @Test
    fun `pipeline loads both models and links the reserved pool`() {
        assertEquals(setOf(modelA, modelB), store.getLoadedModels().toSet())
        assertEquals(16, store.getStats()["totalRows"], "2 models × 8 questions = 16 rows")
        assertEquals(
            reservedIds.size,
            store.getLinkedReservedQuestionIds(listOf(modelA, modelB)).size,
            "4 reserved questions, all cross-linked to mmlu_pro + embeddings"
        )
    }

    @Test
    fun `runBenchmark over the reserved pool yields one result per reserved question`() = runBlocking {
        val req = BenchmarkRequest(
            models = listOf(ModelSource(modelA), ModelSource(modelB)),
            updateRankings = false,
            parallelism = 2
        )
        val report = benchmarkService.runBenchmark(req)

        // reservedOnly defaults to true -> exactly the 4 reserved questions.
        assertEquals(reservedIds.size, report.queryResults.size)

        // Each query carries the pairwise agreement entry (shape, not value).
        val pairKey = "${modelA}_vs_${modelB}"
        report.queryResults.forEach { qr ->
            assertTrue(pairKey in qr.judgeAccuracyAgreement, "missing pair key for query '${qr.query}'")
        }

        // Per-category stats cover both ground-truth categories present in the reserved pool.
        val categories = report.perCategoryStats.map { it.domain }.toSet()
        assertTrue(categories.containsAll(setOf("math", "physics")), "categories were $categories")

        assertEquals(1, report.totalModelPairs)
    }

    @Test
    fun `reservedOnly=false widens the benchmark to all shared questions`() = runBlocking {
        val reservedReq = BenchmarkRequest(
            models = listOf(ModelSource(modelA), ModelSource(modelB)),
            updateRankings = false,
            reservedOnly = true
        )
        val allReq = reservedReq.copy(reservedOnly = false)

        val reservedReport = benchmarkService.runBenchmark(reservedReq)
        recreateBenchmarkService()
        val allReport = benchmarkService.runBenchmark(allReq)

        assertEquals(reservedIds.size, reservedReport.queryResults.size)
        assertEquals(questions.size, allReport.queryResults.size)
        assertTrue(
            allReport.queryResults.size > reservedReport.queryResults.size,
            "reservedOnly=false (${allReport.queryResults.size}) should exceed reservedOnly=true (${reservedReport.queryResults.size})"
        )
    }

    // ─── helpers ────────────────────────────────────────────────────────────

    private fun buildReservedJson(byCategory: Map<String, List<String>>): String =
        buildJsonObject {
            byCategory.forEach { (cat, texts) ->
                put(cat, buildJsonArray { texts.forEach { add(it) } })
            }
        }.toString()

    private fun buildEvalZip(dir: File, baseName: String, predFor: (Q) -> String): File {
        val arr = buildJsonArray {
            questions.forEach { q ->
                add(buildJsonObject {
                    put("question_id", q.id)
                    put("question", q.text)
                    put("options", buildJsonArray { options.forEach { add(it) } })
                    put("answer", q.answer)
                    put("answer_index", q.answerIndex)
                    put("category", q.category)
                    put("pred", predFor(q))
                    put("model_outputs", "Reasoning for ${q.text}. Final answer: ${predFor(q)}")
                })
            }
        }
        val zip = File(dir, "$baseName.zip")
        ZipOutputStream(zip.outputStream()).use { zos ->
            zos.putNextEntry(ZipEntry("results.json"))
            zos.write(arr.toString().toByteArray(Charsets.UTF_8))
            zos.closeEntry()
        }
        return zip
    }
}
