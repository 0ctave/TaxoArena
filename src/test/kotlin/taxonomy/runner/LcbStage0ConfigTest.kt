package taxonomy.runner

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import java.io.File

/**
 * LCB-STAGE0-INTERACTION (docs/judge_v2_program.md L17702-L17982, P4): the ONE tree arm's template
 * experiment_configs/lcb_stage0/lcb_af_bareq512_s42.toml.template carries its two placeholders (ingest.py
 * --construction fills them and refuses to write the config while any remains), parses with them filled, and differs
 * from the 20NG T1b body (ng_af_bareq512_s42.toml) by EXACTLY the registered keys
 * (datasetType, corpusDbPath, outputDir, reservedPoolFile, pool). Same Spring context as TopicPartitionConfigTest.
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
class LcbStage0ConfigTest {

    @Autowired
    lateinit var runner: HeadlessBenchmarkRunner

    private val template = File("experiment_configs/lcb_stage0/lcb_af_bareq512_s42.toml.template")
    private val body = File("experiment_configs/topic_partition/ng_af_bareq512_s42.toml")

    private fun filled(text: String) = text
        .replace("\"@LCB_CONSTRUCTION_DB@\"", "\"Z:/data/lcb/lcb_v6_construction_0123456789abcdef.db\"")
        .replace("\"@POOL_ID@\"", "\"p0123456789abcdef\"")

    @Test
    fun `the template carries both placeholders and parses to the registered arm when filled`() {
        assertTrue(template.isFile, "${template.path} not found; run from the repo root")
        val text = template.readText()
        assertTrue(text.contains("corpusDbPath  = \"@LCB_CONSTRUCTION_DB@\"") && text.contains("pool             = \"@POOL_ID@\""))
        val c = runner.parseToml(filled(text))
        assertEquals("LIVECODEBENCH", c.datasetType)
        assertEquals("Z:/data/lcb/lcb_v6_construction_0123456789abcdef.db", c.corpusDbPath)
        assertEquals("experiment_results/lcb_stage0/lcb_af_bareq512_s42", c.outputDir)
        assertEquals("experiment_configs/lcb_stage0/lcb_gate_ids.json", c.reservedPoolFile)
        assertEquals("p0123456789abcdef", c.pool)
        assertTrue(c.anchorFree && c.runPipeline)
        assertEquals(false, c.runBenchmark)
        assertEquals(false, c.enableLabeling)
        assertEquals(false, c.judgeInduction)
        assertEquals(512, c.embeddingSliceDim)
        assertEquals(0.0145, c.proposalSeparationBar!!, 0.0)
        assertEquals(55, c.minClusterSize)
        assertEquals(42L, c.seed)
        assertTrue(c.seeds.isEmpty(), "never `seeds = [...]`")
        assertTrue(c.models.isEmpty())
        assertNull(c.corpora)
    }

    @Test
    fun `the template differs from the 20NG T1b body by exactly the registered keys`() {
        fun stripped(f: File) = f.readLines().map { it.substringBefore('#').trimEnd() }.filter { it.isNotBlank() }
        val t = stripped(template)
        val b = stripped(body)
        assertEquals(
            listOf("datasetType   = \"TWENTY_NEWSGROUPS\"", "corpusDbPath  = \"twenty_newsgroups_cache_v1.db\"",
                "outputDir     = \"experiment_results/topic_partition/ng_af_bareq512_s42\"") to
                listOf("datasetType   = \"LIVECODEBENCH\"", "corpusDbPath  = \"@LCB_CONSTRUCTION_DB@\"",
                    "outputDir     = \"experiment_results/lcb_stage0/lcb_af_bareq512_s42\"",
                    "reservedPoolFile = \"experiment_configs/lcb_stage0/lcb_gate_ids.json\"", "pool             = \"@POOL_ID@\""),
            (b - t.toSet()) to (t - b.toSet())
        )
    }
}
