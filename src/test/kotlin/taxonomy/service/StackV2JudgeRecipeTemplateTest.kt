package taxonomy.service

import kotlinx.serialization.json.jsonObject
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.dataset.ModelEvalStore
import taxonomy.operations.ArcTaxonomyLLMClient
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomyOperations
import taxonomy.prompts.StackV2JudgeRecipe
import taxonomy.utils.TaxonomyPerformanceTracker

/**
 * The Kotlin STACK-v2 templates are byte-equal to the Python templates of record
 * (`prompt_v2.v2_system_template()`, `rejudge_grok.USER_TEMPLATE`, `rejudge_grok.SCHEMA_INSTRUCTION`,
 * `rejudge_reference.with_reference`), and the schema instruction is ALSO what the live
 * `ArcTaxonomyLLMClient.buildAzureSchemaInstruction` renders for the judge schema, so the two ports
 * cannot drift apart.
 */
class StackV2JudgeRecipeTemplateTest {

    private val t = JudgeWiringFixtures.read("templates.json").jsonObject

    @Test
    fun `v2 system template equals prompt_v2 v2_system_template`() {
        assertEquals(JudgeWiringFixtures.str(t, "v2_system_template"), StackV2JudgeRecipe.V2_SYSTEM_TEMPLATE)
    }

    @Test
    fun `user template equals rejudge_grok USER_TEMPLATE`() {
        assertEquals(JudgeWiringFixtures.str(t, "user_template"), StackV2JudgeRecipe.USER_TEMPLATE)
    }

    @Test
    fun `schema instruction equals the Python constant and the live Azure schema builder`() {
        assertEquals(JudgeWiringFixtures.str(t, "schema_instruction"), StackV2JudgeRecipe.SCHEMA_INSTRUCTION)
        val service = TaxonomyArenaService(
            TaxonomyConfig(), mock(TaxonomyService::class.java), mock(TaxonomyLlmClient::class.java),
            mock(EmbeddingCache::class.java), mock(TaxonomyOperations::class.java), mock(ModelEvalStore::class.java),
            mock(TaxonomyRankingService::class.java), TaxonomyPerformanceTracker()
        )
        assertEquals(ArcTaxonomyLLMClient.buildAzureSchemaInstruction(service.judgeSchema), StackV2JudgeRecipe.SCHEMA_INSTRUCTION)
    }

    @Test
    fun `reference block uses the em dash marker of rejudge_reference`() {
        assertEquals(JudgeWiringFixtures.str(t, "reference_marker"), StackV2JudgeRecipe.REFERENCE_MARKER)
        assertEquals(JudgeWiringFixtures.str(t, "with_reference"), StackV2JudgeRecipe.withReference("Q", "B", "txt"))
        assertEquals("Q\n\n[Reference solution — produced independently, may be wrong]\n(B) txt", StackV2JudgeRecipe.withReference("Q", "B", "txt"))
    }

    @Test
    fun `no placeholder survives assembly and no CR is in any template`() {
        for (s in listOf(StackV2JudgeRecipe.V2_SYSTEM_TEMPLATE, StackV2JudgeRecipe.USER_TEMPLATE, StackV2JudgeRecipe.SCHEMA_INSTRUCTION)) {
            assertFalse(s.contains('\r'), "template carries a CR")
        }
        val system = StackV2JudgeRecipe.buildSystem("SP", "RB")
        val user = StackV2JudgeRecipe.buildUser("Q", "A", "B")
        for (ph in listOf("\$systemPrompt", "\$rubric")) assertFalse(system.contains(ph), "$ph survived")
        for (ph in listOf("\$query", "\$traceA", "\$traceB")) assertFalse(user.contains(ph), "$ph survived")
        assertTrue(system.startsWith("SP\n\n"))
        assertTrue(system.endsWith("Your rubric:\nRB\n\n" + StackV2JudgeRecipe.SCHEMA_INSTRUCTION))
        assertTrue(user.startsWith("[Question]\nQ\n\n[Model A's Response]\nA\n\n[Model B's Response]\nB\n\n"))
        // substitution AFTER trimming: a CR or a trailing newline inside the substituted text is kept verbatim
        assertTrue(StackV2JudgeRecipe.buildSystem("SP", "RB\n").contains("Your rubric:\nRB\n\n\n"))
        assertTrue(StackV2JudgeRecipe.buildUser("Q", "A\r\nx", "B").contains("A\r\nx"))
    }
}
