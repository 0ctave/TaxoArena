package taxonomy.runner

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import java.io.File

/**
 * TOPIC-PARTITION-20NG (docs/judge_v2_program.md L10030-L10390, registration commit 6aa2a0d): the three
 * arm configs under experiment_configs/topic_partition/ parse with the fail-closed loader WITHOUT a build,
 * and parse to EXACTLY the registered values (I2: T1 = R1 af_clean_s42's recipe with datasetType
 * TWENTY_NEWSGROUPS, corpusDbPath, outputDir, models = [], reservedPoolFile and pool ABSENT; I3: T1b = T1 +
 * embeddingSliceDim 512 + bar 0.0145; I1: the smoke = T1 with AG_NEWS). The T2 template is not a config
 * (its bar is a placeholder the chain fills) and must REFUSE to parse as one. Same Spring context as
 * ConfigParsesTest (which also walks these files for unknown keys).
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
class TopicPartitionConfigTest {

    @Autowired
    lateinit var runner: HeadlessBenchmarkRunner

    private val dir = File("experiment_configs/topic_partition")

    private fun parse(name: String): HeadlessCliConfig {
        val f = File(dir, name)
        assertTrue(f.isFile, "${f.path} not found; run from the repo root")
        return runner.parseToml(f.readText())
    }

    /** The R1 af_clean_s42 recipe keys every arm must carry verbatim (registration I2). */
    private fun assertRecipeOfRecord(c: HeadlessCliConfig, arm: String) {
        assertTrue(c.anchorFree, "$arm anchorFree")
        assertTrue(c.runPipeline, "$arm runPipeline")
        assertFalse(c.runBenchmark, "$arm runBenchmark")
        assertTrue(c.runTrickle, "$arm runTrickle")
        assertFalse(c.runBaselines, "$arm runBaselines")
        assertEquals(false, c.enableLabeling, "$arm enableLabeling")
        assertFalse(c.judgeInduction, "$arm judgeInduction")
        assertEquals(false, c.enableFinalMetrics, "$arm enableFinalMetrics")
        assertEquals("DAG_MAX", c.dagMode, "$arm dagMode")
        assertEquals(8, c.maxDepth, "$arm maxDepth")
        assertEquals(55, c.minClusterSize, "$arm minClusterSize")
        assertEquals(1e-6, c.tau!!, 0.0, "$arm tau")
        assertEquals(2.0, c.acceptanceZ!!, 0.0, "$arm acceptanceZ")
        assertEquals(false, c.enableRefitGate, "$arm enableRefitGate")
        assertEquals(0.25, c.membershipFloor!!, 0.0, "$arm membershipFloor")
        assertEquals(0.2, c.routingBeamGamma!!, 0.0, "$arm routingBeamGamma")
        assertEquals(0.12, c.descentMargin!!, 0.0, "$arm descentMargin")
        assertEquals(2.0, c.effectiveSupportFloor!!, 0.0, "$arm effectiveSupportFloor")
        assertEquals(10.0, c.defaultKappaPrior!!, 0.0, "$arm defaultKappaPrior")
        assertEquals(50, c.numIterations, "$arm numIterations")
        assertEquals(5, c.maxLeafAssignments, "$arm maxLeafAssignments")
        assertEquals(0.90, c.fusionSimilarityThreshold!!, 0.0, "$arm fusionSimilarityThreshold")
        assertEquals(false, c.enableGtWarmStart, "$arm enableGtWarmStart")
        assertEquals(true, c.enableProfiling, "$arm enableProfiling")
        assertEquals(0.3, c.testRatio, 0.0, "$arm testRatio")
        assertEquals(42L, c.seed, "$arm seed")
        assertTrue(c.seeds.isEmpty(), "$arm never `seeds = [...]`")
        assertEquals(0, c.queryLimit, "$arm queryLimit")
        assertNull(c.category, "$arm category")
        // ABSENT by registration
        assertNull(c.proposalAcceptMultiplier, "$arm proposalAcceptMultiplier ABSENT (1.0, byte-inert)")
        assertNull(c.reservedPoolFile, "$arm reservedPoolFile ABSENT")
        assertNull(c.pool, "$arm pool ABSENT")
        assertNull(c.constructionOrderShuffleSeed, "$arm no shuffle")
        assertNull(c.splitDropTopPcs, "$arm dropTop ABSENT (0)")
        assertNull(c.splitWhiten, "$arm whiten ABSENT (false)")
        assertTrue(c.excludeFromAnchoring.isEmpty(), "$arm excludeFromAnchoring")
        assertNull(c.corpora, "$arm single corpus via datasetType")
        assertTrue(c.unionSnapshots.isEmpty(), "$arm no union")
        // models = [] parses to an EMPTY list (runner parseStringList), not to [""]
        assertTrue(c.models.isEmpty(), "$arm models = [] must parse to an empty list, got ${c.models}")
    }

    @Test
    fun `T1 ng_af_s42 parses to the registered I2 values`() {
        val c = parse("ng_af_s42.toml")
        assertRecipeOfRecord(c, "T1")
        assertEquals("TWENTY_NEWSGROUPS", c.datasetType)
        assertEquals("twenty_newsgroups_cache_v1.db", c.corpusDbPath)
        assertEquals("experiment_results/topic_partition/ng_af_s42", c.outputDir)
        assertNull(c.embeddingSliceDim, "T1 embeddingSliceDim ABSENT (default 256)")
        assertEquals(0.025, c.proposalSeparationBar!!, 0.0)
    }

    @Test
    fun `T1b ng_af_bareq512_s42 parses to T1 plus the per-corpus pair 512 and 0_0145`() {
        val c = parse("ng_af_bareq512_s42.toml")
        assertRecipeOfRecord(c, "T1b")
        assertEquals("TWENTY_NEWSGROUPS", c.datasetType)
        assertEquals("twenty_newsgroups_cache_v1.db", c.corpusDbPath)
        assertEquals("experiment_results/topic_partition/ng_af_bareq512_s42", c.outputDir)
        assertEquals(512, c.embeddingSliceDim)
        assertEquals(0.0145, c.proposalSeparationBar!!, 0.0)
    }

    @Test
    fun `smoke ag_news_smoke_s42 parses to T1 with AG_NEWS and its own DB`() {
        val c = parse("ag_news_smoke_s42.toml")
        assertRecipeOfRecord(c, "smoke")
        assertEquals("AG_NEWS", c.datasetType)
        assertEquals("ag_news_smoke_cache_v1.db", c.corpusDbPath)
        assertEquals("experiment_results/topic_partition/ag_news_smoke_s42", c.outputDir)
        assertNull(c.embeddingSliceDim)
        assertEquals(0.025, c.proposalSeparationBar!!, 0.0)
    }

    @Test
    fun `the T2 template is not a config - its placeholder bar refuses to parse - and the filled file parses`() {
        val f = File(dir, "ng_af_bar_eq_s42.toml.template")
        assertTrue(f.isFile, "${f.path} not found")
        val text = f.readText()
        assertTrue(text.contains("proposalSeparationBar = @T2_BAR@"), "the template carries the placeholder line")
        assertThrows(Exception::class.java) { runner.parseToml(text) }
        val filled = text.replace("proposalSeparationBar = @T2_BAR@", "proposalSeparationBar = 0.0180")
        val c = runner.parseToml(filled)
        assertRecipeOfRecord(c, "T2")
        assertEquals("TWENTY_NEWSGROUPS", c.datasetType)
        assertEquals("experiment_results/topic_partition/ng_af_bar_eq_s42", c.outputDir)
        assertNull(c.embeddingSliceDim)
        assertEquals(0.0180, c.proposalSeparationBar!!, 0.0)
    }

    @Test
    fun `the three configs differ from T1 by exactly the registered keys (comment-stripped)`() {
        fun stripped(name: String) = File(dir, name).readLines()
            .map { it.substringBefore('#').trimEnd() }.filter { it.isNotBlank() }
        val t1 = stripped("ng_af_s42.toml")
        val t1b = stripped("ng_af_bareq512_s42.toml")
        val smoke = stripped("ag_news_smoke_s42.toml")
        val t2 = stripped("ng_af_bar_eq_s42.toml.template")
        fun delta(a: List<String>, b: List<String>) = (a - b.toSet()) to (b - a.toSet())
        assertEquals(
            listOf("outputDir     = \"experiment_results/topic_partition/ng_af_s42\"", "proposalSeparationBar = 0.025") to
                listOf("outputDir     = \"experiment_results/topic_partition/ng_af_bareq512_s42\"", "embeddingSliceDim = 512", "proposalSeparationBar = 0.0145"),
            delta(t1, t1b), "T1 -> T1b: outputDir + sliceDim 512 + bar 0.0145, nothing else"
        )
        assertEquals(
            listOf("datasetType   = \"TWENTY_NEWSGROUPS\"", "corpusDbPath  = \"twenty_newsgroups_cache_v1.db\"", "outputDir     = \"experiment_results/topic_partition/ng_af_s42\"") to
                listOf("datasetType   = \"AG_NEWS\"", "corpusDbPath  = \"ag_news_smoke_cache_v1.db\"", "outputDir     = \"experiment_results/topic_partition/ag_news_smoke_s42\""),
            delta(t1, smoke), "T1 -> smoke: datasetType + corpusDbPath + outputDir, nothing else"
        )
        assertEquals(
            listOf("outputDir     = \"experiment_results/topic_partition/ng_af_s42\"", "proposalSeparationBar = 0.025") to
                listOf("outputDir     = \"experiment_results/topic_partition/ng_af_bar_eq_s42\"", "proposalSeparationBar = @T2_BAR@"),
            delta(t1, t2), "T1 -> T2 template: outputDir + the placeholder bar, nothing else"
        )
    }
}
