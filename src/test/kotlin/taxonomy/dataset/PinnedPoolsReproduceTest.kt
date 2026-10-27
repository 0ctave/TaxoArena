package taxonomy.dataset

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.File

/**
 * The pinned pools of record reproduce AS LISTS from their id files (FRAMEWORK item 18,
 * criterion "3/3 rebuilds reproduce the pinned pools as lists"): p2dca21ab5f4ef3ae (MMLU-Pro,
 * 3,445 judgeable / 154 sentinels) and paeec37aa28063c75 (union, 6,482 ids over 52 keys, six
 * member pools). No database is opened; the registry and the two id files are the inputs.
 */
class PinnedPoolsReproduceTest {

    @Test
    fun `p2dca reproduces from its id file`() {
        val entry = ReservedPoolRegistry.resolve("p2dca21ab5f4ef3ae")
        val raw = ReservedPoolRegistry.idFile(entry)
        assertEquals(14, raw.size)
        assertEquals(3599, raw.values.sumOf { it.size })
        assertEquals(154, raw.values.sumOf { ids -> ids.count { it <= 0 } })
        val ids = ReservedPoolRegistry.reproduce("p2dca21ab5f4ef3ae")
        assertEquals(3445, ids.values.sumOf { it.size })
        assertEquals("p2dca21ab5f4ef3ae", ReservedPool.computePoolId(ids))
        assertEquals(listOf("MMLU_PRO"), entry.corpus_set)
    }

    @Test
    fun `paeec reproduces from its id file with its six member pools`() {
        val entry = ReservedPoolRegistry.resolve("paeec37aa28063c75")
        val raw = ReservedPoolRegistry.idFile(entry)
        assertEquals(52, raw.size)
        assertEquals(6482, raw.values.sumOf { it.size })
        assertEquals(0, raw.values.sumOf { ids -> ids.count { it <= 0 } })
        val ids = ReservedPoolRegistry.reproduce("paeec37aa28063c75")
        assertEquals("paeec37aa28063c75", ReservedPool.computePoolId(ids))
        assertEquals(6, entry.member_pools.size)
        assertEquals(entry.corpus_set.toSet(), entry.member_pools.keys)
        assertEquals("mc6-2026-09-11", entry.corpus_set_version)
        // The union id is the SOURCE|domain form; the bare form would be a different pool.
        val bare = ids.entries.flatMap { (k, v) -> v.map { "$k:$it" } }.sorted().joinToString("\n")
        val bareId = "p" + java.security.MessageDigest.getInstance("SHA-256").digest(bare.toByteArray())
            .take(8).joinToString("") { "%02x".format(it) }
        assertTrue(bareId != "paeec37aa28063c75", "the union pool must hash under canonicalLine, not the bare key")
    }

    @Test
    fun `canonical lines are the registered forms`() {
        assertEquals("MATH|Algebra:7", ReservedPool.canonicalLine("MATH/Algebra", 7))
        assertEquals("Business:7", ReservedPool.canonicalLine("Business", 7))
        assertEquals("MMLU_PRO/law:7", ReservedPool.canonicalLine("MMLU_PRO/law", 7))
    }

    @Test
    fun `the Python guard knows exactly the corpora CorpusRegistry knows`() {
        val py = File("tools/analysis/pool_guard.py").readText()
        val m = Regex("KNOWN_SOURCES = \\((.*?)\\)", RegexOption.DOT_MATCHES_ALL).find(py)!!.groupValues[1]
        val pySources = Regex("\"([A-Z_]+)\"").findAll(m).map { it.groupValues[1] }.toList()
        // LCB-STAGE0-INTERACTION (programme L17733, H5): pool_guard.py is a pinned blob of record and has NO LCB source by
        // registration; stage 0 uses its unregistered --pool/--db/--id-file path with BARE keys. The one corpus the
        // guard deliberately does not know is excluded here, and only because its keys never take canonicalLine's
        // source branch (asserted below), so the Kotlin and Python pool ids agree on every key the LCB export carries.
        // INTENT-TRANSFER-S1: INTENT likewise (pool_guard stays a pinned blob; the intent GATE exports carry BARE keys, the
        // coarse labels as MMLUDatasetFetcher.formatData writes them, asserted below; intent_s1_export.pool_id mirrors them).
        val notInGuard = setOf("LIVECODEBENCH", "INTENT")
        assertEquals(CorpusRegistry.KNOWN.keys.filter { it !in notInGuard }, pySources)
        assertTrue(notInGuard.all { it in CorpusRegistry.KNOWN }, "the excluded source must exist in the registry")
        for (bare in listOf("Atcoder", "Leetcode", "Codeforces")) {
            assertEquals("$bare:10000007", ReservedPool.canonicalLine(bare, 10_000_007), "LCB bare keys hash as key:id")
        }
        for (bare in listOf("Smart Home", "Iot", "Kitchen And Dining", "Small Talk")) {
            assertEquals("$bare:11000007", ReservedPool.canonicalLine(bare, 11_000_007), "INTENT bare keys hash as key:id")
        }
        assertTrue(py.contains("DEFAULT_SOURCE = \"${CorpusRegistry.DEFAULT_SOURCE}\""))
    }

    @Test
    fun `an unknown pool id is refused with the registry path`() {
        val e = assertThrows(IllegalArgumentException::class.java) { ReservedPoolRegistry.resolve("pdeadbeefdeadbeef") }
        assertTrue(e.message!!.contains("reserved_pools.json") && e.message!!.contains("p2dca21ab5f4ef3ae"), e.message)
        assertThrows(IllegalArgumentException::class.java) { ReservedPoolRegistry.resolve("") }
    }
}
