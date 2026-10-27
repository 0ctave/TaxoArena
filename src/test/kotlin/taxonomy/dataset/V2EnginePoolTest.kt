package taxonomy.dataset

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.jsonObject
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import taxonomy.config.TaxonomyConfig
import java.io.File
import java.nio.file.Files

/**
 * RP12 ARCH-V2-E-T prerequisites 1 and 3 (the engine reserved-pool file of a v2 pool; the sentinel /
 * global closure), executed on the TWO-LANGUAGE fixture src/test/resources/v2pool/ (engine_pool.json and
 * side.tsv written by tools/analysis/v2_engine_pool.py's own build() on its selftest fixture, so the
 * Kotlin loader reads what the Python writer writes) and on the committed side export of the draw of
 * record (pool id reproduced in Kotlin). Every assertion is on a VALUE: ids per side, counts, the
 * recorded legacy pool id, the refusal message.
 *
 * MUTANTS: 27 main-code mutants K1-K27 over V2EnginePool, splitByV2Pool, TrainOnlyGuard, the judge filter, the snapshot
 * stamp and the config (run 2026-09-29 by a harness, one temporary edit at a time, reverted; control K0 survived): 27 of 27
 * killed by this class, V2SplitInertnessTest and V2PoolConfigTest. The table (mutant, killing test) is in the commit message.
 */
class V2EnginePoolTest {

    private lateinit var tmp: File
    private lateinit var fetcher: MMLUDatasetFetcher
    private val fixtureDir = File("src/test/resources/v2pool")
    private val poolFile = File(fixtureDir, "engine_pool.json")

    @BeforeEach
    fun setUp() {
        tmp = Files.createTempDirectory("v2pool").toFile()
        fetcher = MMLUDatasetFetcher(TaxonomyConfig(), "", dbPath = File(tmp, "dataset.db").absolutePath)
        fetcher.reservedJsonFile = File(tmp, "reserved_test_queries.json")
    }

    @AfterEach
    fun tearDown() { tmp.deleteRecursively() }

    /** The engine's view of the Python fixture's rows (row 11 is blank and dropped; row 9 is unlinked). */
    private fun dataset(extra: List<MMLUQuery> = emptyList(), drop: Set<Int> = emptySet()): Map<String, List<MMLUQuery>> {
        val rows = listOf(
            1 to "Alpha question", 2 to "Beta question", 3 to "Gamma question", 4 to "Delta question", 5 to "Epsilon question",
            6 to "Zeta question", 7 to "Eta question", 8 to "Theta question", 9 to "Iota question", 10 to "Kappa question",
            12 to "Lambda question"
        )
        val qs = rows.map { (i, t) -> MMLUQuery(if (i == 9) UNLINKED_QUERY_ID_BASE - 9 else 500 + i, t, "Cat${i % 2}") }
            .filter { it.id !in drop } + extra
        return qs.groupBy { it.category }.toSortedMap()
    }

    private fun ids(m: Map<String, List<MMLUQuery>>) = m.values.flatten().map { it.id }.toSet()

    private fun mutated(edit: (MutableMap<String, kotlinx.serialization.json.JsonElement>) -> Unit): File {
        val o = Json.parseToJsonElement(poolFile.readText()).jsonObject.toMutableMap()
        edit(o)
        val f = File(tmp, "pool_${System.nanoTime()}.json")
        f.writeText(JsonObject(o).toString())
        return f
    }

    private fun intArray(vararg v: Int) = JsonArray(v.map { JsonPrimitive(it) })

    // ── the committed export of the draw of record: the Kotlin half of the pool-id check ─────────────────
    @Test
    fun `the committed side export reproduces pv2_41dbd3dbcd399df0 in Kotlin`() {
        val side = File("data_v2/manifests/REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2_side.tsv")
        val (items, hdr) = V2EnginePool.readSideExport(String(V2EnginePool.lfBytes(side), Charsets.UTF_8), side.path)
        assertEquals(20544, hdr.first)
        assertEquals("pv2_41dbd3dbcd399df0" to 3400, V2EnginePool.poolIdOf(items, "mmlu-pro-v2"))
        assertEquals(3492, items.values.count { it.side == Side.EVAL && "mmlu-pro-v2" in it.corpora })
        // the global reserved set spans BOTH corpora: 3,492 + 2,661 EVAL and 1,157 + 876 GATE items
        assertEquals(3492 + 2661 + 1157 + 876, items.values.count { it.side != Side.TRAIN })
    }

    // ── load (L1-L5) ─────────────────────────────────────────────────────────────────────────────────────
    @Test
    fun `load accepts the Python writer's file and exposes the lists and the global keys`() {
        val p = V2EnginePool.load(poolFile)
        assertEquals("pv2_e128cadc0153dccd", p.poolId)
        assertEquals(setOf(UNLINKED_QUERY_ID_BASE - 9, 501, 502, 507), p.evalIds)
        assertEquals(setOf(503, 508), p.gateIds)
        assertEquals(setOf(504, 505, 506, 510, 512), p.trainIds)
        assertEquals(setOf(UNLINKED_QUERY_ID_BASE - 9), p.sentinelIds)
        assertEquals(4, p.evalComponents)
        // L5: 4 EVAL + 2 GATE of the corpus + 1 EVAL + 1 GATE of the other corpus; no TRAIN key
        assertEquals(8, p.globalReservedKeys.size)
        assertTrue(SplitSide.stemKey("Foreign union question") in p.globalReservedKeys)
        assertTrue(SplitSide.stemKey("Foreign gate question") in p.globalReservedKeys)
        assertTrue(SplitSide.stemKey("Gamma question") in p.globalReservedKeys)
        assertTrue(SplitSide.stemKey("Delta question") !in p.globalReservedKeys)
    }

    @Test
    fun `a CRLF rendering of both files loads to the same pins`() {
        val side = File(tmp, "side.tsv"); side.writeText(File(fixtureDir, "side.tsv").readText().replace("\r\n", "\n").replace("\n", "\r\n"))
        val f = mutated { o ->
            val se = o["side_export"]!!.jsonObject.toMutableMap(); se["path"] = JsonPrimitive(side.absolutePath); o["side_export"] = JsonObject(se)
        }
        val crlf = File(tmp, "crlf.json"); crlf.writeText(f.readText().replace("\n", "\r\n"))
        val a = V2EnginePool.load(poolFile)
        val b = V2EnginePool.load(crlf)
        assertEquals(a.sideSha256Lf, b.sideSha256Lf)
        assertEquals(a.globalReservedKeys, b.globalReservedKeys)
    }

    @Test
    fun `load refuses L1 L2 L3 L4 defects with the named reason`() {
        fun refusal(f: File): String = assertThrows(IllegalStateException::class.java) { V2EnginePool.load(f) }.message!!
        assertTrue(refusal(mutated { it["format"] = JsonPrimitive("x") }).contains("format 'x' is not taxoarena-engine-pool-v2"))
        assertTrue(refusal(mutated { it["pool_id"] = JsonPrimitive("p2dca21ab5f4ef3ae") }).contains("is not pv2_ + 16 hex"))
        assertTrue(refusal(mutated { it["gate_ids"] = intArray(503, 508, 504) }).contains("the eval / gate / train lists intersect (0 / 0 / 1)"))
        assertTrue(refusal(mutated { it["sentinel_ids"] = intArray() }).contains("a negative reserved id is not listed as a sentinel"))
        assertTrue(refusal(mutated { it["sentinel_ids"] = intArray(504) }).contains("sentinel ids must be negative reserved ids ([504])"))
        assertTrue(refusal(mutated { it["train_ids"] = intArray(504, 505, 506, 510) }).contains("counts.train = 5 but the list holds 4"))
        assertTrue(refusal(mutated { o ->
            val se = o["side_export"]!!.jsonObject.toMutableMap(); se["sha256_lf"] = JsonPrimitive("0".repeat(64)); o["side_export"] = JsonObject(se)
        }).contains("!= the pinned 0000"))
        val l4 = refusal(mutated { it["pool_id"] = JsonPrimitive("pv2_0000000000000000") })
        assertTrue(l4.endsWith("the side export's mmlu-pro-v2 pool is pv2_e128cadc0153dccd, not pv2_0000000000000000"), l4)
    }

    // ── splitByV2Pool: the accept path's values ──────────────────────────────────────────────────────────
    @Test
    fun `splitByV2Pool reserves EVAL GATE and the sentinel and keeps TRAIN one-to-one`() {
        val p = V2EnginePool.load(poolFile)
        val split = fetcher.splitByV2Pool(dataset(), p)
        assertEquals(setOf(504, 505, 506, 510, 512), ids(split.train))
        assertEquals(setOf(UNLINKED_QUERY_ID_BASE - 9, 501, 502, 507, 503, 508), ids(split.test))
        assertEquals(setOf(503, 508), split.gate)
        assertEquals(0, split.closedByContent)
        // reserved_test_queries.json carries EVAL + GATE + the sentinel, by domain in the dataset's order
        val written: Map<String, List<Int>> = Json.decodeFromString(fetcher.reservedJsonFile.readText())
        assertEquals(mapOf("Cat0" to listOf(502, 508), "Cat1" to listOf(501, 503, 507, UNLINKED_QUERY_ID_BASE - 9)), written)
        // the legacy id-list pool of the judgeable reserved ids (the sentinel excluded), recorded
        val expected = ReservedPool.computePoolId(mapOf("Cat0" to listOf(502, 508), "Cat1" to listOf(501, 503, 507)))
        assertEquals(expected, split.poolId)
        assertEquals(setOf(501, 502, 503, 507, 508), java.sql.DriverManager.getConnection("jdbc:sqlite:${File(tmp, "dataset.db").absolutePath}").use { c ->
            ReservedPool.questionIds(c, expected)
        })
    }

    // ── the runner's wiring: activate installs the global keys, records the manifest, returns the stamp ──
    @Test
    fun `activate installs the global keys, stamps the counts and writes split_v2 into the manifest`() {
        val p = V2EnginePool.load(poolFile)
        val split = fetcher.splitByV2Pool(dataset(), p)
        val toml = File(tmp, "run.toml").also { it.writeText("runPipeline = true\r\nv2PoolFile = \"x\"\r\n") }
        taxonomy.diagnostics.DiagnosticsBundle.open(tmp, toml)
        try {
            taxonomy.model.TrainOnlyGuard.GlobalReserved.clear()
            val s = p.activate(split, toml, 42L, 3L)
            assertEquals(p.globalReservedKeys, taxonomy.model.TrainOnlyGuard.GlobalReserved.keys())
            assertEquals("pv2_e128cadc0153dccd", taxonomy.model.TrainOnlyGuard.GlobalReserved.origin)
            assertEquals(listOf(5, 6, 2, 1, 8), listOf(s.trainRows, s.reservedRows, s.gateRows, s.sentinelRows, s.globalReservedKeys))
            assertEquals(split.poolId, s.legacyPoolId)
            // the TOML's LF sha (a CRLF config stamps the same value as its LF rendering)
            assertEquals(V2EnginePool.sha256Hex("runPipeline = true\nv2PoolFile = \"x\"\n".toByteArray()), s.configSha256Lf)
            assertEquals(3L, s.constructionOrderShuffleSeed)
            val manifest = File(tmp, "diagnostics/run_manifest.json").readText()
            assertTrue(manifest.contains("\"split_v2\": {\"rule\": \"CK-CLOSE-v2\",\"pool_id\": \"pv2_e128cadc0153dccd\""), manifest)
            assertTrue(manifest.contains("\"train_rows\": 5,\"reserved_rows\": 6,\"gate_rows\": 2,\"sentinel_rows\": 1,\"global_reserved_keys\": 8"), manifest)
        } finally {
            taxonomy.diagnostics.DiagnosticsBundle.close("test")
            taxonomy.model.TrainOnlyGuard.GlobalReserved.clear()
        }
    }

    // ── splitByV2Pool: every refusal ─────────────────────────────────────────────────────────────────────
    private fun splitRefusal(ds: Map<String, List<MMLUQuery>>, p: V2EnginePool = V2EnginePool.load(poolFile)): String =
        assertThrows(IllegalStateException::class.java) { fetcher.splitByV2Pool(ds, p) }.message!!

    @Test
    fun `an unlisted loaded row refuses`() {
        val m = splitRefusal(dataset(extra = listOf(MMLUQuery(999, "Omega question", "Cat1"))))
        assertEquals("[SPLIT-V2] 1 loaded row(s) are in no list of pv2_e128cadc0153dccd (first: [999])", m)
    }

    @Test
    fun `a TRAIN id of the file that is not loaded refuses one-to-one`() {
        val m = splitRefusal(dataset(drop = setOf(510)))
        assertEquals("[SPLIT-V2] ONE-TO-ONE TRAIN: loaded 4 vs file 5 (only loaded: []; only in the file: [510])", m)
    }

    @Test
    fun `a reserved id of the file that is not loaded refuses one-to-one`() {
        val m = splitRefusal(dataset(drop = setOf(UNLINKED_QUERY_ID_BASE - 9)))
        assertEquals("[SPLIT-V2] ONE-TO-ONE RESERVED: loaded 5 vs file 6 (only in the file: [-1000009])", m)
    }

    @Test
    fun `a TRAIN row keyed to a reserved item of ANOTHER corpus refuses (global closure)`() {
        // row 504's text replaced by a normalised twin of the union corpus's EVAL item
        val ds = dataset(drop = setOf(504), extra = listOf(MMLUQuery(504, "  FOREIGN union   question ", "Cat0")))
        assertEquals(
            "[SPLIT-V2] GLOBAL CLOSURE: 1 TRAIN row(s) share their stem key with a reserved item of the side export" +
                " (sentinels and all corpora included; first: [504])", splitRefusal(ds)
        )
        // the same for a GATE-side twin
        val g = dataset(drop = setOf(505), extra = listOf(MMLUQuery(505, "Foreign gate question", "Cat1")))
        assertTrue(splitRefusal(g).startsWith("[SPLIT-V2] GLOBAL CLOSURE: 1 TRAIN row(s)"))
        // and a sentinel's twin: row 506 carries the unlinked EVAL row's text
        val s = dataset(drop = setOf(506), extra = listOf(MMLUQuery(506, "Iota question", "Cat0")))
        assertTrue(splitRefusal(s).endsWith("first: [506])"))
    }

    @Test
    fun `a reserved row whose text keys to no reserved item refuses`() {
        val ds = dataset(drop = setOf(501), extra = listOf(MMLUQuery(501, "Alpha question, reworded", "Cat1")))
        assertEquals("[SPLIT-V2] 1 reserved row(s) key to no reserved item of the side export (first: [501])", splitRefusal(ds))
    }
}
