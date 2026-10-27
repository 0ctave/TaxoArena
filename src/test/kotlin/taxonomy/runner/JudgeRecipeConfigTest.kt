package taxonomy.runner

import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import taxonomy.config.TaxonomyConfig

/**
 * JUDGE-WIRING TOML keys. `judgeRecipe = "STACK-v2"` enables the recipe; `judgeRecipeKit`,
 * `judgeRecipeModel`, `judgeRecipeMaxTokens`, `judgeRecipeTemperature` override its parameters; an
 * absent temperature is "omitted" (the field is left out of the payload); any other recipe name is
 * refused; a TOML without the keys leaves the recipe disabled and the pre-existing EffectiveConfig
 * fields unchanged (golden JSON).
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
class JudgeRecipeConfigTest {

    @Autowired
    lateinit var runner: HeadlessBenchmarkRunner

    @Autowired
    lateinit var config: TaxonomyConfig

    @Autowired
    lateinit var arenaService: taxonomy.service.TaxonomyArenaService

    private val base = "datasetType = \"MMLU_PRO\"\nseed = 137\njudgeOptionMode = \"RESOLVED\"\n"

    /**
     * The arena service's two new constructor parameters carry defaults (a refusing transport, no kit) so
     * every test construction compiles; Spring must nevertheless inject the real beans, or a recipe run
     * would fail at its first match. Checked through the fields, since neither is exposed.
     */
    @Test
    fun `spring injects the recipe transport and kit provider beans into the arena service`() {
        fun field(name: String): Any? = taxonomy.service.TaxonomyArenaService::class.java.getDeclaredField(name).also { it.isAccessible = true }.get(arenaService)
        assertTrue(field("recipeTransport") is taxonomy.operations.SpringRecipeJudgeTransport, "transport bean not injected: ${field("recipeTransport")}")
        assertTrue(field("recipeKitProvider") is taxonomy.operations.ConfiguredRecipeKitProvider, "kit provider bean not injected: ${field("recipeKitProvider")}")
    }

    @AfterEach
    fun reset() {
        // parseToml writes the recipe keys onto the live (shared) config, as it does judgeOptionMode
        config.llm.judgeRecipe = TaxonomyConfig.JudgeRecipeConfig()
        config.llm.judgeOptionMode = "OPTIONS"
    }

    @Test
    fun `recipe keys enable STACK-v2 with the temperature omitted by default`() {
        val parsed = runner.parseToml(base + "judgeRecipe = \"STACK-v2\"\njudgeRecipeKit = \"experiment_results/judge_wiring/stack_v2_kit.db\"\njudgeRecipeMaxTokens = 8192\n")
        assertEquals("STACK-v2", parsed.judgeRecipe)
        assertEquals("experiment_results/judge_wiring/stack_v2_kit.db", parsed.judgeRecipeKit)
        assertEquals(8192, parsed.judgeRecipeMaxTokens)
        assertNull(parsed.judgeRecipeTemperature)
        assertTrue(config.llm.judgeRecipe.enabled)
        assertEquals("STACK-v2", config.llm.judgeRecipe.name)
        assertEquals("grok-4-1-fast-non-reasoning", config.llm.judgeRecipe.model)
        assertEquals(8192, config.llm.judgeRecipe.maxTokens)
        assertNull(config.llm.judgeRecipe.temperature)
        assertEquals("omitted", config.llm.judgeRecipe.temperatureLabel)
        assertEquals("2024-05-01-preview", config.llm.judgeRecipe.inferenceApiVersion)
        config.llm.judgeRecipe.validate(config.llm.judgeOptionMode)
        val eff = config.toEffectiveConfig().llm.judgeRecipe
        assertTrue(eff.enabled)
        assertEquals("omitted", eff.temperatureLabel)
        assertEquals(16, eff.fingerprint.length)
    }

    @Test
    fun `an explicit temperature literal is parsed and labelled by its Python repr`() {
        runner.parseToml(base + "judgeRecipe = \"STACK-v2\"\njudgeRecipeTemperature = 0.0\njudgeRecipeModel = \"grok-4-1-fast-non-reasoning\"\n")
        assertEquals(0.0, config.llm.judgeRecipe.temperature)
        assertEquals("0.0", config.llm.judgeRecipe.temperatureLabel)
        val fpOmitted = TaxonomyConfig.JudgeRecipeConfig().fingerprint()
        assertNotEquals(fpOmitted, config.llm.judgeRecipe.fingerprint(), "a different temperature label is a different deployment")
    }

    @Test
    fun `another recipe name, a non-positive budget and a negative temperature are refused`() {
        assertThrows(Exception::class.java) { runner.parseToml(base + "judgeRecipe = \"other\"\n") }
        assertThrows(Exception::class.java) { runner.parseToml(base + "judgeRecipe = \"STACK-v2\"\njudgeRecipeMaxTokens = 0\n") }
        assertThrows(Exception::class.java) { runner.parseToml(base + "judgeRecipe = \"STACK-v2\"\njudgeRecipeTemperature = -1\n") }
    }

    @Test
    fun `OPTIONS mode with the recipe fails validation`() {
        runner.parseToml("datasetType = \"MMLU_PRO\"\njudgeOptionMode = \"OPTIONS\"\njudgeRecipe = \"STACK-v2\"\n")
        val ex = assertThrows(IllegalStateException::class.java) { config.llm.judgeRecipe.validate(config.llm.judgeOptionMode) }
        assertTrue(ex.message!!.contains("RESOLVED"))
    }

    @Test
    fun `without the keys the recipe stays disabled and the effective config is the pre-existing shape`() {
        val parsed = runner.parseToml("datasetType = \"MMLU_PRO\"\nseed = 137\n")
        assertNull(parsed.judgeRecipe); assertNull(parsed.judgeRecipeKit); assertNull(parsed.judgeRecipeModel)
        assertNull(parsed.judgeRecipeMaxTokens); assertNull(parsed.judgeRecipeTemperature)
        assertFalse(config.llm.judgeRecipe.enabled)
        val llm = config.toEffectiveConfig().llm
        assertFalse(llm.judgeRecipe.enabled)
        // golden: the fields that existed before JUDGE-WIRING, in their order, with the disabled block appended last
        val full = Json { encodeDefaults = true }.encodeToString(llm)
        val expected = """{"provider":"${llm.provider}","embeddingProvider":"${llm.embeddingProvider}","judgeModel":"${llm.judgeModel}","labelingModel":"${llm.labelingModel}","embeddingModel":"${llm.embeddingModel}","maxJudgeGenerality":${llm.maxJudgeGenerality},"judgeOptionMode":"${llm.judgeOptionMode}","judgeDomains":[${llm.judgeDomains.joinToString(",") { "\"$it\"" }}],""" +
            """"judgeRecipe":{"enabled":false,"name":"","model":"","inferenceApiVersion":"","maxTokens":0,"temperatureLabel":"omitted","kitHash":"","fingerprint":""}}"""
        assertEquals(expected, full)
        // the runner's Json (encodeDefaults off) leaves the disabled block out of every export
        val json = Json { prettyPrint = false }
        assertFalse(json.encodeToString(llm).contains("\"judgeRecipe\""), "with encodeDefaults off, the disabled block is absent from the export")
        // and a snapshot written before the field existed still decodes
        val old = json.decodeFromString<taxonomy.config.EffectiveConfig.Llm>("""{"provider":"AZURE","judgeModel":"Mistral-Large-3"}""")
        assertFalse(old.judgeRecipe.enabled)
        assertEquals("omitted", old.judgeRecipe.temperatureLabel)
    }
}
