package taxonomy.dataset

import kotlinx.coroutines.runBlocking
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`
import taxonomy.config.TaxonomyConfig
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.TrainOnlyGuard
import taxonomy.service.SnapshotSettings
import taxonomy.service.TaxonomyPersistence
import taxonomy.service.TaxonomySnapshotManager
import taxonomy.utils.TaxonomyPerformanceTracker
import java.io.File
import java.nio.file.Files
import java.sql.DriverManager

/**
 * RP12 ARCH-V2-E-T prerequisite 5, the DECLARED-CHANGE PROOF: every existing path is byte-identical when
 * the new inputs (v2PoolFile, a build stamp, installed global reserved keys) are absent, and each proof
 * shows the changed code EXECUTED on that absent path (the vacuity rule; memory note inertness-proof-vacuity):
 *
 *  G1 legacy splits (splitByReservedFile, seeded splitTrainTest): the digest of pool id, closure count,
 *     train / test / gate ids and the reserved JSON's sha equals the golden taken on base 32c4c72 BEFORE
 *     any main-code edit (V2GoldenProbe, deleted). Discriminator: V2Fixture's legacy file on the same
 *     fetcher, then splitByV2Pool on the v2 fixture runs and gives a different, asserted split.
 *  G2 SnapshotSettings JSON (encodeDefaults = true, the snapshot manager's encoder) of a fixed settings
 *     object: sha equals the base golden, and no "buildStamp" key. Discriminator: the serializer's
 *     descriptor HAS the new element (the compiled class carries the change) and a stamped object
 *     encodes it and round-trips.
 *  G3 TrainOnlyGuard sites with nothing installed: withGlobal returns an equal set, and the global-key
 *     read counter moves (the new line ran). Installed: a tree holding a text keyed ONLY by the global
 *     set is refused by saveSnapshot and the same tree is accepted with nothing installed (non-vacuous).
 *  G4 judge induction with nothing installed withholds exactly the pool texts (historical predicate)
 *     and the counter moves; installed, a globally reserved region text is withheld from the prompt.
 *  G5 saveSnapshot without a stamp stores settings with no "buildStamp" key (raw column read); with a
 *     stamp, the stored stamp equals the manifest map's values (G10's stamp == manifest).
 */
class V2SplitInertnessTest {

    private lateinit var tmp: File
    private val reservedFile = File("reserved_test_queries.json")
    private var originalReserved: String? = null

    @BeforeEach
    fun setUp() {
        tmp = Files.createTempDirectory("v2-inert").toFile()
        originalReserved = if (reservedFile.exists()) reservedFile.readText() else null
        TrainOnlyGuard.GlobalReserved.clear()
    }

    @AfterEach
    fun tearDown() {
        TrainOnlyGuard.GlobalReserved.clear()
        if (originalReserved != null) reservedFile.writeText(originalReserved!!) else reservedFile.delete()
        tmp.deleteRecursively()
    }

    private fun fetcher(name: String) = MMLUDatasetFetcher(TaxonomyConfig(), "", dbPath = File(tmp, "$name.db").absolutePath)
        .also { it.reservedJsonFile = File(tmp, "$name.json") }

    // ── G1 ────────────────────────────────────────────────────────────────────────────────────────────────
    @Test
    fun `G1 legacy splits are byte-identical to the base goldens and the v2 split is different and ran`() {
        val f = fetcher("a")
        val pinned = File(tmp, "pinned.json").also { it.writeText(V2Fixture.PINNED_JSON) }
        val a = f.splitByReservedFile(V2Fixture.dataset(), pinned)
        assertEquals(
            "p122635da994f4f5b|2|103,104,204,205,206,207,208,209,210,211,212|-1000007,101,102,105,201,202,203|204,210|" +
                "0425759a375065cba10d77b47da1da4d2adaea451cea47be4423e301a6ebe7e9",
            V2Fixture.digest(a, f.reservedJsonFile.readText())
        )
        val b = f.splitTrainTest(V2Fixture.dataset(), testRatio = 0.3, seed = 7L)
        assertEquals(
            "p91a968fd56a5aaac|1|102,103,104,202,203,204,205,207,208,209,212|-1000007,101,105,201,206,210,211|204|" +
                "24537fe42bbef26e99dbcd1fb90b79bc55da2b5c0e33ac6310d3b2a9e0af5336",
            V2Fixture.digest(b, f.reservedJsonFile.readText())
        )
        // discriminator: the new split path on the same fetcher class executes and gives its own asserted split
        val v2 = f.splitByV2Pool(
            listOf(1 to "Alpha question", 2 to "Beta question", 3 to "Gamma question", 4 to "Delta question",
                5 to "Epsilon question", 6 to "Zeta question", 7 to "Eta question", 8 to "Theta question",
                9 to "Iota question", 10 to "Kappa question", 12 to "Lambda question")
                .map { (i, t) -> MMLUQuery(if (i == 9) UNLINKED_QUERY_ID_BASE - 9 else 500 + i, t, "Cat${i % 2}") }
                .groupBy { it.category },
            V2EnginePool.load(File("src/test/resources/v2pool/engine_pool.json"))
        )
        assertEquals(setOf(503, 508), v2.gate)
        assertEquals(5, v2.train.values.sumOf { it.size })
    }

    // ── G2 ────────────────────────────────────────────────────────────────────────────────────────────────
    private val snapJson = Json { prettyPrint = true; ignoreUnknownKeys = true; encodeDefaults = true }

    private fun stamp() = V2EnginePool.load(File("src/test/resources/v2pool/engine_pool.json"))
        .stamp("pabc", 5, 6, 2, 1, "c".repeat(64), 42L, null)

    @Test
    fun `G2 settings JSON without a stamp is byte-identical to the base golden and the stamp encodes when set`() {
        val legacy = snapJson.encodeToString(V2Fixture.settings())
        assertEquals("e9329be473f4b5fdb79bdfdee1e1afa732e369f5c4ad6b0b56e423a6922f984f", V2Fixture.sha(legacy))
        assertFalse(legacy.contains("buildStamp"))
        // discriminator: the compiled serializer carries the new element
        val d = SnapshotSettings.serializer().descriptor
        assertTrue((0 until d.elementsCount).any { d.getElementName(it) == "buildStamp" })
        val stamped = snapJson.encodeToString(V2Fixture.settings().copy(buildStamp = stamp()))
        assertTrue(stamped.contains("\"buildStamp\""))
        assertTrue(stamped.contains("\"poolId\": \"pv2_e128cadc0153dccd\""))
        assertEquals(stamp(), snapJson.decodeFromString<SnapshotSettings>(stamped).buildStamp)
        // a legacy row (no key) still decodes to null
        assertEquals(null, snapJson.decodeFromString<SnapshotSettings>(legacy).buildStamp)
    }

    // ── G3 / G5: TrainOnlyGuard and saveSnapshot ─────────────────────────────────────────────────────────
    private val evalText = "Which planet is known as the red planet?"
    private val foreignText = "Foreign union question"

    private fun emb(text: String) = Embedding(rawText = text, distilledText = text, values = floatArrayOf(0.1f, 0.2f))

    private fun tree(vararg texts: String): GraphNode {
        val root = GraphNode(id = "root", label = "Root", depth = 0)
        val leaf = GraphNode(id = "leaf", label = "Leaf", depth = 1)
        root.children.add(leaf); leaf.parents.add(root)
        leaf.queries.add(emb("What is 2+2?"))
        texts.forEach { leaf.queries.add(emb(it)) }
        return root
    }

    private fun manager(): Pair<TaxonomySnapshotManager, String> {
        val dbPath = File(tmp, "dataset.db").absolutePath
        val store = ModelEvalStore(dbPath = dbPath)
        DriverManager.getConnection("jdbc:sqlite:$dbPath").use { c ->
            c.createStatement().use { s ->
                s.execute("CREATE TABLE IF NOT EXISTS mmlu_pro (id INTEGER PRIMARY KEY, question TEXT, category TEXT, cot_content TEXT, options TEXT, answer TEXT)")
                s.execute("INSERT INTO mmlu_pro (id, question, category, cot_content, options, answer) VALUES (7, '$evalText', 'astronomy', '', '[]', 'A')")
            }
        }
        store.saveLinks(listOf(EvalQuestionLink(7007, 7, evalText, true)))
        val poolId = store.recordReservedPool(mapOf("astronomy" to listOf(7007)))
        reservedFile.writeText("""{ "astronomy": [7007] }""")
        val config = TaxonomyConfig()
        val loader = ModelEvalLoader(store, mock(MMLUDatasetFetcher::class.java), dbPath, File(tmp, "emb.db").absolutePath, File(tmp, "r.json").absolutePath)
        return TaxonomySnapshotManager(config, TaxonomyPersistence(config, mock(EmbeddingCache::class.java)), loader, TaxonomyPerformanceTracker()) to poolId
    }

    private fun storedSettingsJson(id: String): String =
        DriverManager.getConnection("jdbc:sqlite:snapshots_test.db").use { c ->
            c.prepareStatement("SELECT settings FROM snapshots WHERE id = ?").use { ps ->
                ps.setString(1, id); ps.executeQuery().use { rs -> check(rs.next()); rs.getString(1) }
            }
        }

    @Test
    fun `G3 withGlobal is the identity with nothing installed and the read counter proves it ran`() {
        val keys = TrainOnlyGuard.keysOf(listOf(evalText))
        val before = TrainOnlyGuard.GlobalReserved.consultations()
        assertEquals(keys, TrainOnlyGuard.withGlobal(keys))
        assertFalse(TrainOnlyGuard.isGloballyReserved(foreignText))
        assertEquals(before + 2, TrainOnlyGuard.GlobalReserved.consultations())
        assertEquals(0, TrainOnlyGuard.evalMembers(tree(foreignText), TrainOnlyGuard.withGlobal(keys)).count)
        TrainOnlyGuard.GlobalReserved.install(setOf(SplitSide.stemKey(foreignText)), "pv2_test")
        assertEquals(keys + SplitSide.stemKey(foreignText), TrainOnlyGuard.withGlobal(keys))
        assertTrue(TrainOnlyGuard.isGloballyReserved("  FOREIGN union question "))
        assertEquals(1, TrainOnlyGuard.evalMembers(tree(foreignText), TrainOnlyGuard.withGlobal(keys)).count)
        assertThrows(IllegalArgumentException::class.java) { TrainOnlyGuard.GlobalReserved.install(emptySet(), "x") }
    }

    @Test
    fun `G3 G5 saveSnapshot - absent inputs store no stamp key and accept a globally-keyed text, installed refuses it`() {
        val (mgr, poolId) = manager()
        val before = TrainOnlyGuard.GlobalReserved.consultations()
        val legacy = mgr.saveSnapshot(tree(foreignText), "legacy", expectedPoolId = poolId)
        try {
            assertTrue(TrainOnlyGuard.GlobalReserved.consultations() > before, "saveSnapshot's new withGlobal line ran")
            val raw = storedSettingsJson(legacy.id)
            assertFalse(raw.contains("buildStamp"), raw)
            assertTrue(raw.contains("\"splitFunction\""))
            assertEquals(null, mgr.readBuildStamp(legacy.id))
        } finally { mgr.deleteSnapshot(legacy.id) }

        TrainOnlyGuard.GlobalReserved.install(setOf(SplitSide.stemKey(foreignText)), "pv2_test")
        val e = assertThrows(IllegalStateException::class.java) { mgr.saveSnapshot(tree(foreignText), "v2dirty", expectedPoolId = poolId) }
        assertTrue(e.message!!.startsWith("[TRAIN-ONLY] saveSnapshot($poolId): 1 EVAL items are members of 1 nodes"), e.message)

        val s = stamp()
        val clean = mgr.saveSnapshot(tree(), "v2clean", expectedPoolId = poolId, buildStamp = s)
        try {
            val stored = mgr.listSnapshots().first { it.id == clean.id }
            assertEquals(s, stored.settings.buildStamp)
            // G10: the stored stamp's values are the manifest map's values, field for field
            val m = s.toManifest()
            assertEquals(listOf(s.poolId, s.sideExportSha256Lf, s.enginePoolSha256Lf, s.configSha256Lf, s.trainRows, s.gateRows),
                listOf(m["pool_id"], m["side_export_sha256_lf"], m["engine_pool_sha256_lf"], m["config_sha256_lf"], m["train_rows"], m["gate_rows"]))
            assertEquals(18, m.size)
            // RP12 B2: readBuildStamp returns the stored stamp (the union graft reads its members' stamps with it)
            assertEquals(s, mgr.readBuildStamp(clean.id))
        } finally { mgr.deleteSnapshot(clean.id) }
        val noPool = assertThrows(IllegalStateException::class.java) { mgr.saveSnapshot(tree(), "nopool", buildStamp = s) }
        assertTrue(noPool.message!!.startsWith("[SPLIT-V2] refusing to save a v2-stamped snapshot (pv2_e128cadc0153dccd)"))
    }

    // ── G4: judge induction ──────────────────────────────────────────────────────────────────────────────
    private class CapturingLlm : taxonomy.operations.TaxonomyLlmClient {
        val prompts = java.util.Collections.synchronizedList(ArrayList<String>())
        override suspend fun generateClusterLabel(prompt: String): String = ""
        override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String {
            prompts += userPrompt
            return """{"judge_system_prompt": "p", "judge_rubric": {"criteria": ["Accuracy"], "failure_modes": []}}"""
        }
        override suspend fun queryModelStructured(modelName: String, systemPrompt: String?, userPrompt: String, schema: dev.langchain4j.model.chat.request.json.JsonSchema) = ""
        override fun setMaxParallel(limit: Int) {}
    }

    private fun induce(): List<String> = runBlocking {
        // texts chosen so the induction's hashCode % 5 sampling keeps all three
        val texts = listOf("Train item one about orbits", foreignText, "Train item two about comets")
        check(texts.all { kotlin.math.abs(it.hashCode()) % 5 != 0 }) { "fixture texts must survive the sampling" }
        val fetcher = mock(MMLUDatasetFetcher::class.java)
        `when`(fetcher.getDetailsForQueries(texts)).thenReturn(texts.associateWith { HFProRowData(question = it, options = listOf("A", "B"), answer = "A") })
        val store = mock(ModelEvalStore::class.java)
        `when`(store.getReservedQuestionTexts("ptest0000000000000")).thenReturn(emptySet())
        val llm = CapturingLlm()
        val svc = taxonomy.service.TaxonomyJudgeService(fetcher, llm, TaxonomyConfig(), mock(taxonomy.service.TaxonomyArenaService::class.java), store)
        val leaf = GraphNode(id = "leaf", label = "Leaf", depth = 0)
        texts.forEach { leaf.queries.add(emb(it)) }
        svc.generateJudgeForNode(leaf, emptySet())
        llm.prompts.toList()
    }

    @Test
    fun `G4 judge induction withholds a globally reserved text only when the set is installed`() {
        val before = TrainOnlyGuard.GlobalReserved.consultations()
        val legacy = induce()
        assertTrue(TrainOnlyGuard.GlobalReserved.consultations() >= before + 3, "the new predicate ran per region item")
        assertTrue(legacy.first().contains(foreignText), "absent: the historical predicate withholds nothing here")
        TrainOnlyGuard.GlobalReserved.install(setOf(SplitSide.stemKey(foreignText)), "pv2_test")
        val v2 = induce()
        assertFalse(v2.any { it.contains(foreignText) }, "installed: the globally reserved text never reaches a prompt")
        assertTrue(v2.first().contains("Train item one about orbits"))
    }
}
