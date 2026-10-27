package taxonomy.dataset

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import taxonomy.config.DatasetType

/**
 * Stage 0a identity plumbing (docs/multi_corpus_design.md §3.2): MMLU_PRO keeps offset 0 so no
 * existing `eval_results.question_id` changes; other corpora get disjoint namespaces; the
 * registry's table names equal the former `when (datasetType)` mapping.
 */
class CorpusIdsTest {

    @Test
    fun `MMLU_PRO ids are unchanged by namespacing`() {
        for (id in listOf(0, 1, 70, 12256, 999_999)) {
            assertEquals(id, CorpusIds.namespaced("MMLU_PRO", id))
            assertEquals("MMLU_PRO", CorpusIds.sourceOf(id))
            assertEquals(id, CorpusIds.upstreamId(id))
        }
    }

    @Test
    fun `other corpora occupy disjoint million-wide namespaces and round-trip`() {
        val offsets = mapOf("MMLU_PRO" to 0, "BBH" to 1_000_000, "MATH" to 2_000_000)
        assertEquals(1_000_042, CorpusIds.namespaced("BBH", 42, offsets))
        assertEquals("BBH", CorpusIds.sourceOf(1_000_042, offsets))
        assertEquals(42, CorpusIds.upstreamId(1_000_042, offsets))
        assertEquals("MATH", CorpusIds.sourceOf(2_999_999, offsets))
        assertEquals("MMLU_PRO", CorpusIds.sourceOf(999_999, offsets))
        assertThrows(IllegalArgumentException::class.java) { CorpusIds.namespaced("BBH", 1_000_000, offsets) }
        assertThrows(IllegalArgumentException::class.java) { CorpusIds.namespaced("NOPE", 1, offsets) }
        assertThrows(IllegalArgumentException::class.java) { CorpusIds.sourceOf(3_000_000, offsets) }
        assertThrows(IllegalArgumentException::class.java) { CorpusIds.sourceOf(-5, offsets) }
    }

    @Test
    fun `registry table names equal the former when-block mapping and MMLU_PRO is offset 0`() {
        val registry = CorpusRegistry()
        val expected = mapOf(
            DatasetType.MMLU_PRO to "mmlu_pro",
            DatasetType.MMLU_ORIGINAL to "mmlu_original",
            DatasetType.ARC to "arc",
            DatasetType.TWENTY_NEWSGROUPS to "twenty_newsgroups",
            DatasetType.AG_NEWS to "ag_news"
        )
        assertEquals(DatasetType.entries.map { it.name }.toSet() + CorpusRegistry.LEADERBOARD.keys, registry.names)
        for ((type, table) in expected) assertEquals(table, registry.tableFor(type.name))
        assertEquals(0, registry.idOffsetFor("MMLU_PRO"))
        assertEquals(McLetter, registry.verifierFor("MMLU_PRO"))
        val offsets = CorpusRegistry.BUILTIN_OFFSETS.values.toList()
        assertEquals(offsets.size, offsets.toSet().size, "namespaces must be disjoint")
        assertThrows(IllegalArgumentException::class.java) { registry.tableFor("NOPE") }
        assertThrows(IllegalStateException::class.java) { registry.source("MMLU_PRO") }
    }

    @Test
    fun `leaderboard descriptors match the multi-corpus DB builder and share nothing but MMLU_PRO_LB's offset 0`() {
        val registry = CorpusRegistry()
        // tools/ingest/multicorpus_db.py: BBH 1M, MATH 2M, MUSR 3M, IFEVAL 4M, GPQA 5M, MMLU_PRO 0.
        assertEquals(1_000_000, registry.idOffsetFor("BBH"))
        assertEquals(2_000_000, registry.idOffsetFor("MATH"))
        assertEquals(3_000_000, registry.idOffsetFor("MUSR"))
        assertEquals(4_000_000, registry.idOffsetFor("IFEVAL"))
        assertEquals(5_000_000, registry.idOffsetFor("GPQA"))
        assertEquals(0, registry.idOffsetFor("MMLU_PRO_LB"))
        assertEquals("MMLU_PRO", registry.descriptor("MMLU_PRO_LB").dbSource)
        assertEquals("BBH", registry.descriptor("BBH").dbSource)
        assertEquals(McLetter, registry.verifierFor("MMLU_PRO_LB"))
        assertEquals(Imported("acc_norm"), registry.verifierFor("BBH"))
        assertEquals(Imported("exact_match"), registry.verifierFor("MATH"))
        assertEquals(Imported("prompt_level_strict_acc"), registry.verifierFor("IFEVAL"))
        CorpusRegistry.LEADERBOARD.keys.forEach { assertEquals("corpus_questions", registry.tableFor(it)) }
        // Every namespace but the deliberate MMLU_PRO / MMLU_PRO_LB alias is disjoint.
        val offsets = CorpusRegistry.KNOWN_OFFSETS.filterKeys { it != "MMLU_PRO_LB" }.values.toList()
        assertEquals(offsets.size, offsets.toSet().size, "namespaces must be disjoint: $offsets")
        // A TIGER-Lab id resolves to MMLU_PRO (first entry), never to the alias.
        assertEquals("MMLU_PRO", CorpusIds.sourceOf(70))
        assertEquals("BBH", CorpusIds.sourceOf(1_000_000))
        assertEquals("GPQA", CorpusIds.sourceOf(5_020_447))
        assertEquals(1_000_042, CorpusIds.namespacedOrSentinel("BBH", 42))
        assertEquals(-1_000_005, CorpusIds.namespacedOrSentinel("BBH", -1_000_005), "sentinels pass through")
        assertEquals(70, CorpusIds.namespacedOrSentinel("MMLU_PRO", 70))
        assertTrue(CorpusRegistry.isLeaderboard("MUSR"))
        assertFalse(CorpusRegistry.isLeaderboard("MMLU_PRO"))
    }

    @Test
    fun `domain keys carry the source prefix only for a known source`() {
        assertEquals("BBH/boolean_expressions", CorpusDomains.key("BBH", "boolean_expressions"))
        assertEquals("BBH", CorpusDomains.sourceOfKey("BBH/boolean_expressions"))
        assertEquals("boolean_expressions", CorpusDomains.domainOfKey("BBH/boolean_expressions"))
        assertEquals("MATH", CorpusDomains.sourceOfKey("MATH/Counting & Probability"))
        assertNull(CorpusDomains.sourceOfKey("Philosophy"))
        assertNull(CorpusDomains.sourceOfKey("Computer Science"))
        assertNull(CorpusDomains.sourceOfKey("Nope/x"), "an unknown prefix is part of the domain string")
        assertEquals("Nope/x", CorpusDomains.domainOfKey("Nope/x"))
        assertNull(CorpusDomains.sourceOfKey("/x"))
    }

    @Test
    fun `corpusDbPath is lifted from a TOML only when declared`() {
        assertNull(CorpusRegistry.corpusDbPathFromToml("datasetType = \"MMLU_PRO\"\nseed = 137\n"))
        assertEquals(
            "runs/union.db",
            CorpusRegistry.corpusDbPathFromToml("# c\ndatasetType = \"MMLU_PRO\"\ncorpusDbPath = \"runs/union.db\"  # new DB\n")
        )
        assertEquals("x.db", CorpusRegistry.corpusDbPathFromToml("corpusDbPath='x.db'"))
        assertNull(CorpusRegistry.corpusDbPathFromToml("corpusDbPath = \"\""))
    }
}
