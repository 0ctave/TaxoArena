package taxonomy.runner

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import kotlinx.serialization.builtins.serializer
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest

/**
 * RP12 ARCH-V2-E-T: the `v2PoolFile` key through the fail-closed TOML loader (the same Spring context as
 * ConfigParsesTest / TopicPartitionConfigTest) and the init-block cross-checks shared with the JSON
 * decoder. Every refusal asserts its message. Mutants (commit table): C1 init check on runPipeline
 * removed -> killed here; C2 reservedPoolFile conflict removed -> killed; C3 the key dropped from the
 * parser (unknown-key fatal) -> killed by the parse case.
 */
@SpringBootTest(
    classes = [taxonomy.TaxoAdaptApplication::class],
    properties = [
        "taxoadapt.execution.enable-tui=false",
        "taxoadapt.execution.run-batch=false",
        "taxoadapt.execution.start-service=false",
        "taxoadapt.llm.judge-model=qwen3.6:27b",
        "taxoadapt.llm.labeling-model=gemma4:e4b"
    ]
)
class V2PoolConfigTest {

    @Autowired
    lateinit var runner: HeadlessBenchmarkRunner

    @Test
    fun `v2PoolFile parses on a constructing run and is absent by default`() {
        val c = runner.parseToml("runPipeline = true\nv2PoolFile = \"experiment_configs/engine_pool_pv2_41dbd3dbcd399df0.json\"\n")
        assertEquals("experiment_configs/engine_pool_pv2_41dbd3dbcd399df0.json", c.v2PoolFile)
        assertNull(runner.parseToml("runPipeline = true\n").v2PoolFile)
    }

    @Test
    fun `gate_ids json - no stamp gives the pre-RP12 text byte for byte, a stamp adds split_v2 only`() {
        val json = kotlinx.serialization.json.Json { prettyPrint = true; ignoreUnknownKeys = true }
        val gate = setOf(210, 204, 7)
        // the pre-RP12 inline construction of HeadlessBenchmarkRunner (base 32c4c72), verbatim
        val base = json.encodeToString(kotlinx.serialization.json.JsonObject.serializer(), kotlinx.serialization.json.buildJsonObject {
            put("function", json.encodeToJsonElement(taxonomy.dataset.FunctionStamp.serializer(), taxonomy.dataset.SplitSide.stamp("pabc")))
            put("gate_size", kotlinx.serialization.json.JsonPrimitive(gate.size))
            put("gate_eval_overlap", kotlinx.serialization.json.JsonPrimitive(0))
            put("gate_ids", json.encodeToJsonElement(kotlinx.serialization.builtins.ListSerializer(Int.serializer()), gate.sorted()))
        })
        assertEquals(base, gateIdsJson(json, "pabc", gate, null))
        val stamp = taxonomy.dataset.V2EnginePool.load(java.io.File("src/test/resources/v2pool/engine_pool.json"))
            .stamp("pabc", 5, 6, 2, 1, null, 42L, 7L)
        val v2 = kotlinx.serialization.json.Json.parseToJsonElement(gateIdsJson(json, "pabc", gate, stamp)) as kotlinx.serialization.json.JsonObject
        assertEquals(listOf("function", "gate_size", "gate_eval_overlap", "gate_ids", "split_v2"), v2.keys.toList())
        assertEquals("\"pv2_e128cadc0153dccd\"", (v2["split_v2"] as kotlinx.serialization.json.JsonObject)["poolId"].toString())
        assertEquals("7", (v2["split_v2"] as kotlinx.serialization.json.JsonObject)["constructionOrderShuffleSeed"].toString())
    }

    @Test
    fun `unionRoutingItemKey - strict boolean, union graft only, absent false`() {
        fun msg(block: () -> Unit): String = assertThrows(IllegalArgumentException::class.java) { block() }.message!!
        val union = "unionSnapshots = [\"s1\", \"s2\"]\ncorpora = [\"BBH\", \"MATH\"]\ncorpusDbPath = \"mc.db\"\n"
        assertEquals(true, runner.parseToml(union + "unionRoutingItemKey = true\n").unionRoutingItemKey)
        assertEquals(false, runner.parseToml(union).unionRoutingItemKey)
        assertEquals("[CONFIG] unionRoutingItemKey must be true or false (got 'yes')", msg { runner.parseToml(union + "unionRoutingItemKey = yes\n") })
        assertEquals("[CONFIG] unionRoutingItemKey = true asserts an item-keyed union readout on a run that grafts no union (needs unionSnapshots)",
            msg { runner.parseToml("runPipeline = true\nunionRoutingItemKey = true\n") })
    }

    @Test
    fun `v2PoolFile is refused without runPipeline, with unionSnapshots, beside reservedPoolFile, and empty`() {
        fun msg(block: () -> Unit): String = assertThrows(IllegalArgumentException::class.java) { block() }.message!!
        val want = "[CONFIG] v2PoolFile = a.json needs a constructing run (runPipeline = true, no unionSnapshots)" +
            " or a union graft (unionSnapshots, runPipeline = false)"
        assertEquals(want, msg { runner.parseToml("v2PoolFile = \"a.json\"\n") })
        assertEquals(want, msg { HeadlessCliConfig(models = emptyList(), runPipeline = true, unionSnapshots = listOf("s1"), v2PoolFile = "a.json") })
        // RP12 B2: a union graft (no runPipeline) admits it
        assertEquals("a.json", HeadlessCliConfig(models = emptyList(), unionSnapshots = listOf("s1", "s2"), v2PoolFile = "a.json").v2PoolFile)
        assertEquals("u.json", runner.parseToml("unionSnapshots = [\"s1\", \"s2\"]\ncorpora = [\"BBH\", \"MATH\"]\ncorpusDbPath = \"mc.db\"\nv2PoolFile = \"u.json\"\n").v2PoolFile)
        assertEquals(
            "[CONFIG] v2PoolFile = a.json and reservedPoolFile = r.json are two split sources; give one",
            msg { runner.parseToml("runPipeline = true\nv2PoolFile = \"a.json\"\nreservedPoolFile = \"r.json\"\n") }
        )
        assertEquals("[CONFIG] v2PoolFile is empty", msg { runner.parseToml("runPipeline = true\nv2PoolFile = \"\"\n") })
    }
}
