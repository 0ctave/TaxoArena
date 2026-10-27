package taxonomy.runner

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

/**
 * INTENT-TRANSFER-S1: the HeadlessCliConfig init block's INTENT cross-check (shared by the TOML parser and the JSON decoder).
 * The admitted shape (one arm, constructing, zero-call, build DB + GATE export + pool pin) constructs; each departure is
 * refused with its own message; a config without INTENT is untouched by the block (every existing shape still constructs).
 */
class IntentConfigCrossCheckTest {

    private fun ok(
        datasetType: String? = "INTENT",
        corpora: List<String>? = null,
        runPipeline: Boolean = true,
        unionSnapshots: List<String> = emptyList(),
        corpusDbPath: String? = "intent_s1_build/M-AF.db",
        reservedPoolFile: String? = "experiment_configs/intent_s1/gate_ids_M-AF.json",
        v2PoolFile: String? = null,
        pool: String? = "p0123456789abcdef",
        runBenchmark: Boolean = false,
        judgeInduction: Boolean = false,
        enableLabeling: Boolean? = false,
        judgeRecipe: String? = null,
        models: List<String> = emptyList(),
    ) = HeadlessCliConfig(
        models = models, datasetType = datasetType, corpora = corpora, runPipeline = runPipeline, unionSnapshots = unionSnapshots,
        corpusDbPath = corpusDbPath, reservedPoolFile = reservedPoolFile, v2PoolFile = v2PoolFile, pool = pool,
        runBenchmark = runBenchmark, judgeInduction = judgeInduction, enableLabeling = enableLabeling, judgeRecipe = judgeRecipe
    )

    private fun refused(needle: String, block: () -> Any) {
        val e = assertThrows<IllegalArgumentException> { block() }
        assertTrue(e.message!!.contains(needle), "expected '$needle' in: ${e.message}")
    }

    @Test
    fun `the admitted INTENT shape constructs, in either case of the key`() {
        assertEquals("INTENT", ok().datasetType)
        assertEquals("intent", ok(datasetType = "intent").datasetType)
        assertEquals(listOf("INTENT"), ok(datasetType = null, corpora = listOf("INTENT")).corpora)
    }

    @Test
    fun `every departure from the admitted shape is refused`() {
        refused("needs a constructing run") { ok(runPipeline = false) }
        refused("needs a constructing run") { ok(unionSnapshots = listOf("s")) }
        refused("is single-corpus") { ok(corpora = listOf("INTENT", "MMLU_PRO")) }
        refused("is single-corpus") { ok(datasetType = null, corpora = listOf("MMLU_PRO", "INTENT")) }
        refused("needs corpusDbPath") { ok(corpusDbPath = null) }
        refused("needs corpusDbPath") { ok(corpusDbPath = " ") }
        refused("needs reservedPoolFile") { ok(reservedPoolFile = null) }
        refused("needs reservedPoolFile") { ok(v2PoolFile = "experiment_configs/engine_pool_x.json", reservedPoolFile = null) }
        refused("needs the [POOL-PIN] pool") { ok(pool = null) }
        refused("is a zero-call build") { ok(runBenchmark = true) }
        refused("is a zero-call build") { ok(judgeInduction = true) }
        refused("is a zero-call build") { ok(enableLabeling = true) }
        refused("is a zero-call build") { ok(judgeRecipe = "STACK-v2") }
        refused("is a zero-call build") { ok(models = listOf("gpt-4o-2024-08-06")) }
        // the key is matched case-insensitively (the runner applies DatasetType.valueOf(uppercase())), and via corpora too
        refused("is a zero-call build") { ok(datasetType = "intent", runBenchmark = true) }
        refused("needs the [POOL-PIN] pool") { ok(datasetType = null, corpora = listOf("INTENT"), pool = null) }
    }

    @Test
    fun `a config without INTENT is untouched by the block`() {
        // each of these would be refused under INTENT; without it they construct as before
        val c = HeadlessCliConfig(models = listOf("m"), datasetType = "MMLU_PRO", runPipeline = false, runBenchmark = true, enableLabeling = true)
        assertEquals("MMLU_PRO", c.datasetType)
        val d = HeadlessCliConfig(models = emptyList(), datasetType = "LIVECODEBENCH", runPipeline = true, corpusDbPath = null, pool = null)
        assertEquals(null, d.pool)
        val e = HeadlessCliConfig(models = emptyList())
        assertEquals(null, e.datasetType)
    }
}
