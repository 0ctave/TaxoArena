package taxonomy.dataset

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import taxonomy.config.TaxonomyConfig
import java.io.File
import java.nio.file.Files

/**
 * RP12 B2: the union member pool (a namespaced engine pool file over corpus_questions, written by
 * tools/analysis/v2_union_pool.py's own build() on its selftest fixture: src/test/resources/v2pool_union/) and the
 * union graft's member check. Every assertion is on a value or a refusal message. Mutants in the commit message.
 */
class V2UnionPoolTest {

    private lateinit var tmp: File
    private lateinit var fetcher: MMLUDatasetFetcher
    private val poolFile = File("src/test/resources/v2pool_union/engine_pool.json")

    @BeforeEach
    fun setUp() {
        tmp = Files.createTempDirectory("v2union").toFile()
        fetcher = MMLUDatasetFetcher(TaxonomyConfig(), "", dbPath = File(tmp, "dataset.db").absolutePath)
        fetcher.reservedJsonFile = File(tmp, "reserved_test_queries.json")
        taxonomy.model.TrainOnlyGuard.GlobalReserved.clear()
    }

    @AfterEach
    fun tearDown() {
        taxonomy.model.TrainOnlyGuard.GlobalReserved.clear()
        tmp.deleteRecursively()
    }

    private val rows = mapOf(
        70 to ("MMLU_PRO" to "Union mmlu one"), 71 to ("MMLU_PRO" to "Union mmlu two"),
        1000001 to ("BBH" to "Bbh alpha"), 1000002 to ("BBH" to "Bbh beta"), 1000003 to ("BBH" to "Bbh gamma"),
        2000005 to ("MATH" to "Math delta"), 2000006 to ("MATH" to "Math epsilon")
    )

    /** A per-corpus member's load: the rows of [sources] only, keyed "<SOURCE>/d" like LeaderboardCorpusSource. */
    private fun load(vararg sources: String, drop: Set<Int> = emptySet()): Map<String, List<MMLUQuery>> =
        rows.filter { (id, sv) -> sv.first in sources && id !in drop }
            .map { (id, sv) -> MMLUQuery(id, sv.second, "${sv.first}/d", sv.first) }
            .groupBy { it.category }

    private fun ids(m: Map<String, List<MMLUQuery>>) = m.values.flatten().map { it.id }.toSet()

    @Test
    fun `load reads the namespaces and the member split is checked on its own namespace`() {
        val p = V2EnginePool.load(poolFile)
        assertEquals(mapOf("BBH" to 1000000, "MATH" to 2000000, "MMLU_PRO" to 0), p.namespaces)
        assertEquals(listOf("BBH"), p.namespacesOf(listOf(1000001, 1000003)))
        val bbh = fetcher.splitByV2Pool(load("BBH"), p)
        assertEquals(setOf(1000003), ids(bbh.train))
        assertEquals(setOf(1000001, 1000002), ids(bbh.test))
        assertEquals(setOf(1000002), bbh.gate)
        val two = fetcher.splitByV2Pool(load("BBH", "MATH"), p)
        assertEquals(setOf(1000003, 2000005), ids(two.train))
        assertEquals(setOf(1000002), two.gate)
    }

    @Test
    fun `a member missing one of its namespace's ids refuses one-to-one`() {
        val p = V2EnginePool.load(poolFile)
        val e = assertThrows(IllegalStateException::class.java) { fetcher.splitByV2Pool(load("MATH", drop = setOf(2000005)), p) }
        assertEquals("[SPLIT-V2] ONE-TO-ONE TRAIN: loaded 0 vs file 1 (only loaded: []; only in the file: [2000005])", e.message)
        // the pv2_41 (single-corpus, no namespaces) file keeps the whole-list check: a BBH load against it is unlisted
        val single = V2EnginePool.load(File("src/test/resources/v2pool/engine_pool.json"))
        assertNull(single.namespaces)
        assertTrue(assertThrows(IllegalStateException::class.java) { fetcher.splitByV2Pool(load("BBH"), single) }
            .message!!.startsWith("[SPLIT-V2] 3 loaded row(s) are in no list of"))
    }

    @Test
    fun `an id outside every declared namespace refuses at load`() {
        val o = kotlinx.serialization.json.Json.parseToJsonElement(poolFile.readText()).let { it as kotlinx.serialization.json.JsonObject }.toMutableMap()
        o["namespaces"] = kotlinx.serialization.json.Json.parseToJsonElement("""{"BBH": 1000000, "MATH": 2000000}""")
        val f = File(tmp, "p.json").also { it.writeText(kotlinx.serialization.json.JsonObject(o).toString()) }
        val e = assertThrows(IllegalStateException::class.java) { V2EnginePool.load(f) }
        assertTrue(e.message!!.endsWith("2 id(s) lie in no declared namespace (first [70, 71])"), e.message)
    }

    private fun memberStamp(p: V2EnginePool, split: MMLUDatasetFetcher.Split): V2BuildStamp {
        val toml = File(tmp, "m.toml").also { it.writeText("runPipeline = true\n") }
        return p.activate(split, toml, 42L, null)
    }

    @Test
    fun `activate stamps the loaded namespaces and the graft admits members of the draw only`() {
        val p = V2EnginePool.load(poolFile)
        val bbhSplit = fetcher.splitByV2Pool(load("BBH"), p)
        val bbh = memberStamp(p, bbhSplit)
        assertEquals(listOf("BBH"), bbh.namespacesLoaded)
        assertEquals(listOf("BBH"), bbh.toManifest()["namespaces_loaded"])
        val mathSplit = fetcher.splitByV2Pool(load("MATH"), p)
        assertEquals(emptySet<Int>(), mathSplit.gate)     // the GATE ids of the loaded namespace only
        val math = memberStamp(p, mathSplit)
        // the MMLU-Pro member on another pool of the same draw (a pv2_41-style stamp): admitted ONLY on the allow-list (D-2)
        val foreign = bbh.copy(poolId = "pv2_41dbd3dbcd399df0", namespacesLoaded = null, enginePoolSha256Lf = "a".repeat(64))
        val members = listOf(
            V2EnginePool.UnionMember("sB", "BBH", bbh, setOf(1000001, 1000002)),
            V2EnginePool.UnionMember("sM", "MATH", math, setOf(2000006)),
            V2EnginePool.UnionMember("sP", "MMLU_PRO", foreign, setOf(501))
        )
        val allow = V2ForeignMembers.parseForeign(listOf("pv2_41dbd3dbcd399df0:" + "a".repeat(64)))
        val ok = p.checkUnionMembers(members, allow)
        assertEquals("[SPLIT-V2] UNION member sB (BBH) on ${p.poolId}, namespaces [BBH]: reserved 2 ids == the file's", ok[0])
        assertEquals("[SPLIT-V2] UNION member sP (MMLU_PRO) on the allow-listed foreign pool pv2_41dbd3dbcd399df0 of the same draw" +
            " (engine pool sha256(LF) ${"a".repeat(64)}); admitted", ok[2])
        // D-2: the stamp alone admits nothing; a wrong sha or a wrong pool on the list refuses too
        for (bad in listOf(emptySet(), V2ForeignMembers.parseForeign(listOf("pv2_41dbd3dbcd399df0:" + "b".repeat(64))),
                V2ForeignMembers.parseForeign(listOf("pv2_0000000000000000:" + "a".repeat(64))))) {
            val m = assertThrows(IllegalStateException::class.java) { p.checkUnionMembers(members, bad) }.message!!
            assertTrue(m.startsWith("[SPLIT-V2] UNION member sP (MMLU_PRO) is on the foreign pool pv2_41dbd3dbcd399df0"), m)
        }
        assertTrue(assertThrows(IllegalArgumentException::class.java) { V2ForeignMembers.parseForeign(listOf("pv2_41dbd3dbcd399df0")) }
            .message!!.startsWith("[CONFIG] v2ForeignMembers entry 'pv2_41dbd3dbcd399df0' is not"))

        fun refusal(m: V2EnginePool.UnionMember): String =
            assertThrows(IllegalStateException::class.java) { p.checkUnionMembers(listOf(m)) }.message!!
        assertEquals("[SPLIT-V2] UNION member s0 (BBH) carries no v2 build stamp: a v2 graft grafts v2 members only",
            refusal(V2EnginePool.UnionMember("s0", "BBH", null, setOf(1000001))))
        assertTrue(refusal(V2EnginePool.UnionMember("s1", "BBH", bbh.copy(sideExportSha256Lf = "f".repeat(64)), setOf(1000001, 1000002)))
            .startsWith("[SPLIT-V2] UNION member s1 (BBH) is of another draw"))
        assertEquals("[SPLIT-V2] UNION member s2 (BBH): reserved 1 ids vs the file's 2 for [BBH] (only in the snapshot: []; only in the file: [1000002])",
            refusal(V2EnginePool.UnionMember("s2", "BBH", bbh, setOf(1000001))))
        assertTrue(refusal(V2EnginePool.UnionMember("s3", "BBH", bbh.copy(namespacesLoaded = null), setOf(1000001, 1000002)))
            .endsWith("names no loaded namespace"))
        // activateUnion: the check, then the global keys installed, then the union stamp
        taxonomy.model.TrainOnlyGuard.GlobalReserved.clear()
        val (lines, us) = p.activateUnion(listOf(
            V2EnginePool.UnionMember("sB", "BBH", bbh, setOf(1000001, 1000002)),
            V2EnginePool.UnionMember("sM", "MATH", math, setOf(2000006))
        ), "punion", 9, mapOf("BBH/d" to listOf(1000001, 1000002), "MATH/d" to listOf(2000006)), 42L,
            File(tmp, "graft.toml").also { it.writeText("unionSnapshots = [\"a\"]\r\nv2PoolFile = \"u\"\r\n") })
        assertEquals(3, lines.size)
        assertEquals("[TRAIN-ONLY] union graft: global reserved keys installed: 5 (${p.poolId})", lines.last())
        assertEquals(p.globalReservedKeys, taxonomy.model.TrainOnlyGuard.GlobalReserved.keys())
        assertEquals(listOf("punion", "BBH,MATH"), listOf(us.legacyPoolId, us.namespacesLoaded!!.joinToString(",")))
        assertEquals(listOf(9, 3, 1, 0), listOf(us.trainRows, us.reservedRows, us.gateRows, us.sentinelRows))
        // D-7: the union stamp carries the graft TOML's LF sha (G10's "stamp equals the TOML")
        assertEquals(V2EnginePool.sha256Hex("unionSnapshots = [\"a\"]\nv2PoolFile = \"u\"\n".toByteArray()), us.configSha256Lf)
        taxonomy.model.TrainOnlyGuard.GlobalReserved.clear()
        assertThrows(IllegalStateException::class.java) {
            p.activateUnion(listOf(V2EnginePool.UnionMember("s0", "BBH", null, emptySet())), "punion", 0, emptyMap(), null)
        }
        assertTrue(!taxonomy.model.TrainOnlyGuard.GlobalReserved.installed(), "a refused graft installs nothing")
        // D-2 through activateUnion: the allow-list passed by the graft admits the foreign member; absent, it refuses
        val (fl, _) = p.activateUnion(members, "punion", 9, emptyMap(), null, null, allow)
        assertTrue(fl[2].endsWith("admitted"), fl[2])
        taxonomy.model.TrainOnlyGuard.GlobalReserved.clear()
        assertThrows(IllegalStateException::class.java) { p.activateUnion(members, "punion", 9, emptyMap(), null) }
        // the single-corpus fixture is of another draw (its own side export): refused as such
        val single = V2EnginePool.load(File("src/test/resources/v2pool/engine_pool.json"))
        assertTrue(assertThrows(IllegalStateException::class.java) {
            p.checkUnionMembers(listOf(V2EnginePool.UnionMember("s4", "MMLU_PRO", single.stamp(null, 1, 1, 0, 0, null, null, null), setOf(501))))
        }.message!!.startsWith("[SPLIT-V2] UNION member s4 (MMLU_PRO) is of another draw"))
    }
}
