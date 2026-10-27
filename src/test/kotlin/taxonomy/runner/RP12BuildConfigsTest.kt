package taxonomy.runner

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import java.io.File

/**
 * READY_rp12_et C-0: the 24 member TOMLs and the three graft templates of experiment_configs/rp12 (written by
 * tools/analysis/rp12_build_configs.py) parse with the fail-closed loader to exactly the registered arms; a filled graft
 * template parses as a v2 union graft. Plus D-2's v2ForeignMembers key. Every assertion is on a parsed value.
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
class RP12BuildConfigsTest {

    @Autowired
    lateinit var runner: HeadlessBenchmarkRunner

    private val dir = File("experiment_configs/rp12")
    private val members = listOf("bbh" to "BBH", "math" to "MATH", "musr" to "MUSR", "ifeval" to "IFEVAL", "gpqa" to "GPQA", "mmlu_pro_lb" to "MMLU_PRO_LB")
    private val pool = "pv2_1575de61bb20e977"

    @Test
    fun `the member TOMLs parse to the registered arms`() {
        for ((arm, shuffle) in listOf("B0" to null, "B0p" to null, "o1" to 1L, "o2" to 2L)) for ((tag, corpus) in members) {
            val c = runner.parseToml(File(dir, "$arm/$tag.toml").readText())
            assertEquals(listOf(corpus), c.corpora, "$arm/$tag")
            assertEquals("experiment_configs/engine_pool_$pool.json", c.v2PoolFile)
            assertEquals(pool, c.pool)
            assertEquals(shuffle, c.constructionOrderShuffleSeed, "$arm/$tag")
            assertTrue(c.runPipeline && c.unionSnapshots.isEmpty() && !c.judgeInduction && c.enableLabeling == false && !c.runBaselines)
            assertEquals(listOf(512, 55, 0.0145, 42L), listOf(c.embeddingSliceDim, c.minClusterSize, c.proposalSeparationBar, c.seed))
            assertEquals("experiment_results/archv2/rp12/$arm/$tag", c.outputDir)
            assertNull(c.reservedPoolFile)
        }
    }

    @Test
    fun `a filled graft template parses as a v2 item-keyed union graft`() {
        for ((arm, rule) in listOf("B0" to "flatLeaf", "B0" to "descent", "B0p" to "flatLeaf")) {
            var t = File(dir, "$arm/graft_${rule.lowercase()}.toml.tmpl").readText()
            for ((_, c) in members) t = t.replace("__SNAP_${c}__", "S_$c")
            val c = runner.parseToml(t)
            assertEquals(members.map { "S_${it.second}" }, c.unionSnapshots)
            assertEquals(members.map { it.second }, c.corpora)
            assertEquals(rule, c.unionRootRouting)
            assertTrue(c.unionRoutingItemKey && !c.runPipeline)
            assertEquals(pool, c.pool)
            assertEquals("experiment_configs/engine_pool_$pool.json", c.v2PoolFile)
            assertEquals(emptyList<String>(), c.v2ForeignMembers)
        }
    }

    @Test
    fun `v2ForeignMembers - parsed, validated, only on a v2 graft`() {
        fun msg(block: () -> Unit): String = assertThrows(IllegalArgumentException::class.java) { block() }.message!!
        val graft = "unionSnapshots = [\"s1\", \"s2\"]\ncorpora = [\"BBH\", \"MATH\"]\ncorpusDbPath = \"mc.db\"\nv2PoolFile = \"u.json\"\n"
        val ok = "pv2_41dbd3dbcd399df0:" + "0123456789abcdef".repeat(4)
        assertEquals(listOf(ok), runner.parseToml(graft + "v2ForeignMembers = [\"$ok\"]\n").v2ForeignMembers)
        assertTrue(msg { runner.parseToml(graft + "v2ForeignMembers = [\"pv2_41dbd3dbcd399df0\"]\n") }
            .startsWith("[CONFIG] v2ForeignMembers entry 'pv2_41dbd3dbcd399df0' is not"))
        assertEquals("[CONFIG] v2ForeignMembers names foreign graft members on a run that is not a v2 union graft (needs v2PoolFile and unionSnapshots)",
            msg { runner.parseToml("runPipeline = true\nv2PoolFile = \"a.json\"\nv2ForeignMembers = [\"$ok\"]\n") })
    }
}
