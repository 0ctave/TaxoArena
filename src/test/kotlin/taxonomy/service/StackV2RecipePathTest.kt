package taxonomy.service

import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.jsonObject
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import org.mockito.Mockito.verifyNoInteractions
import org.mockito.Mockito.`when`
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.dataset.ModelEvalStore
import taxonomy.model.GraphNode
import taxonomy.operations.InMemoryRecipeKit
import taxonomy.operations.JudgeCallResult
import taxonomy.operations.RecipeJudgeTransport
import taxonomy.operations.RecipeKit
import taxonomy.operations.RecipeKitProvider
import taxonomy.operations.RecipeReference
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomyOperations
import taxonomy.prompts.StackV2JudgeRecipe
import taxonomy.utils.TaxonomyPerformanceTracker

/**
 * The recipe branch of `TaxonomyArenaService.evaluatePairwise`: with `judgeRecipe.enabled` the
 * assembled STACK-v2 bytes go to the recipe transport (never `queryModelStructured`), the two orders
 * combine exactly as the Mistral path combines them, NON_TERMINATED calls are INVALID (never a tie),
 * every verdict carries two `JudgeCallRecord`s with the provenance fields, the node's own judgePrompt
 * never reaches a payload, a question the kit does not cover yields no evaluation and no call, and
 * OPTIONS mode is refused at validation.
 */
class StackV2RecipePathTest {

    private val tripwire = "RECIPE-PATH-MUST-NOT-USE-THIS"

    private class FakeTransport(val reply: (order: Int) -> JudgeCallResult) : RecipeJudgeTransport {
        val bodies = mutableListOf<ByteArray>()
        override suspend fun post(body: ByteArray): JudgeCallResult {
            synchronized(bodies) { bodies.add(body) }
            val s = String(body, Charsets.US_ASCII)
            val order = if (s.indexOf("TRACE-ALPHA") < s.indexOf("TRACE-BETA")) 1 else 2
            return reply(order)
        }
    }

    private class RefusingClient : TaxonomyLlmClient {
        var calls = 0
        override suspend fun generateClusterLabel(prompt: String): String = error("no")
        override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String { calls++; error("langchain4j path must not be used under the recipe") }
        override suspend fun queryModelStructured(modelName: String, systemPrompt: String?, userPrompt: String, schema: JsonSchema): String { calls++; error("langchain4j path must not be used under the recipe") }
        override fun setMaxParallel(limit: Int) {}
    }

    private fun ok(content: String, finish: String? = "stop", ctok: Int? = 321) = JudgeCallResult(
        content = content, finishReason = finish, completionTokens = ctok, promptTokens = 1234, providerResponseId = "resp-$finish-${content.hashCode()}",
        providerModel = "grok-4-1-fast-non-reasoning", httpStatus = 200, attempts = 1, latencyMs = 42, requestSha256 = "n/a"
    )

    private fun verdict(winner: String, conf: Double) = """{"critique_a":"a","critique_b":"b","comparison":"c","winner":"$winner","confidence":$conf}"""

    private val kit: RecipeKit = InMemoryRecipeKit(
        anchorRubrics = mapOf("Physics" to ("You judge physics." to "Rubric: units.")),
        questionAnchor = mapOf(7 to ("n00000007" to "Physics")),
        references = mapOf(7 to RecipeReference("B", "sixty percent"))
    )

    private fun config(optionMode: String = "RESOLVED", temperature: Double? = null) = TaxonomyConfig().apply {
        llm.judgeModel = "Mistral-Large-3"
        llm.judgeOptionMode = optionMode
        llm.judgeRecipe.enabled = true
        llm.judgeRecipe.temperature = temperature
    }

    private data class Rig(val service: TaxonomyArenaService, val transport: FakeTransport, val client: RefusingClient, val ranking: TaxonomyRankingService, val node: GraphNode)

    private fun rig(cfg: TaxonomyConfig, transport: FakeTransport, kitProvider: RecipeKitProvider = object : RecipeKitProvider { override fun get() = kit }): Rig {
        val node = GraphNode(id = "leaf-7", label = "Thermo", depth = 2)
        node.judgePrompt = tripwire
        node.judgeRubric = tripwire
        val taxonomyService = mock(TaxonomyService::class.java)
        `when`(taxonomyService.getGraph()).thenReturn(node)
        val ranking = mock(TaxonomyRankingService::class.java)
        val client = RefusingClient()
        val service = TaxonomyArenaService(
            cfg, taxonomyService, client, mock(EmbeddingCache::class.java), mock(TaxonomyOperations::class.java),
            mock(ModelEvalStore::class.java), ranking, TaxonomyPerformanceTracker(), transport, kitProvider
        )
        return Rig(service, transport, client, ranking, node)
    }

    private suspend fun evaluate(r: Rig, qid: Int? = 7) = r.service.evaluateWithPrecomputedTraces(
        query = "What is the efficiency?", options = listOf("forty", "sixty percent"), modelA = "alpha",
        traceA = "TRACE-ALPHA says (A)", modelB = "beta", traceB = "TRACE-BETA says (B)",
        assignedLeafIds = listOf(r.node.id), condition = "MAIN", evalQuestionId = qid
    )

    @Test
    fun `consistent votes give a winner with two provenance rows and never touch the langchain4j client`() = runBlocking {
        val cfg = config()
        val t = FakeTransport { order -> if (order == 1) ok(verdict("Model A", 0.9)) else ok(verdict("Model B", 0.8)) }
        val r = rig(cfg, t)
        val evals = evaluate(r)
        assertEquals(1, evals.size)
        val e = evals.single()
        assertEquals("Model A", e.winner)
        assertFalse(e.positionFlip)
        assertNull(e.tieSource)
        assertEquals(0, r.client.calls, "queryModelStructured must never be called under the recipe")
        assertEquals(2, t.bodies.size)
        verifyNoInteractions(r.ranking)
        // provenance
        assertEquals(2, e.judgeCalls.size)
        val c1 = e.judgeCalls.first { it.presentationOrder == 1 }; val c2 = e.judgeCalls.first { it.presentationOrder == 2 }
        assertEquals("stop", c1.finishReason); assertEquals(321, c1.completionTokens); assertEquals(1234, c1.promptTokens)
        assertTrue(c1.providerResponseId!!.startsWith("resp-"))
        assertEquals(8192, c1.maxTokens); assertEquals("omitted", c1.temperatureLabel)
        assertEquals("grok-4-1-fast-non-reasoning", c1.judgeModel); assertEquals("STACK-v2", c1.recipe)
        assertEquals(kit.kitHash, c1.kitHash); assertEquals(cfg.llm.judgeRecipe.fingerprint(), c1.deploymentFingerprint)
        assertEquals("Model A", c1.parsedWinner); assertEquals(0.9, c1.confidence)
        assertEquals("Model B", c2.parsedWinner); assertEquals(0.8, c2.confidence)
        assertEquals("Physics", c1.anchor); assertEquals("B", c1.refLetter); assertEquals(7, c1.evalQuestionId)
        assertEquals("alpha", c1.modelA); assertEquals("beta", c1.modelB); assertEquals("leaf-7", c1.nodeId)
        // payload shas are the shas of the exact bytes handed to the transport
        val shas = t.bodies.map { StackV2JudgeRecipe.sha256Hex(it) }.toSet()
        assertEquals(setOf(c1.payloadSha256, c2.payloadSha256), shas)
        assertNotEquals(c1.payloadSha256, c2.payloadSha256)
        // tripwire: the node's own prompt/rubric never reach a payload; the kit's do; the reference block is there
        for (b in t.bodies) {
            val s = String(b, Charsets.US_ASCII)
            assertFalse(s.contains(tripwire))
            assertTrue(s.contains("You judge physics."))
            assertTrue(s.contains("Rubric: units."))
            assertTrue(s.contains("[Reference solution \\u2014 produced independently, may be wrong]\\n(B) sixty percent"))
            assertTrue(s.startsWith("{\"model\": \"grok-4-1-fast-non-reasoning\", \"max_tokens\": 8192, \"messages\": ["))
            assertFalse(s.contains("\"temperature\""))
        }
        assertEquals(0.85, e.confidence, 1e-9)
    }

    @Test
    fun `the combination rule matches rejudge_grok combine_orders on all 16 vote pairs`() = runBlocking {
        val cases = JudgeWiringFixtures.read("combine_cases.json") as JsonArray
        assertEquals(16, cases.size)
        for (c in cases) {
            val o = c.jsonObject
            val v1 = JudgeWiringFixtures.str(o, "vote1"); val v2 = JudgeWiringFixtures.str(o, "vote2_raw")
            val t = FakeTransport { order -> ok(verdict(if (order == 1) v1 else v2, 0.8)) }
            val r = rig(config(), t)
            val e = evaluate(r).single()
            assertEquals(JudgeWiringFixtures.str(o, "winner"), e.winner, "votes $v1 / $v2")
            assertEquals((o["flip"] as kotlinx.serialization.json.JsonPrimitive).content == "true", e.positionFlip, "flip for $v1 / $v2")
            val invalid = (o["invalid"] as kotlinx.serialization.json.JsonPrimitive).content == "true"
            assertEquals(invalid, e.winner == "INVALID")
            if (e.positionFlip) assertEquals("POSITION_FLIP", e.tieSource)
        }
    }

    @Test
    fun `finish_reason length or content_filter is NON_TERMINATED, INVALID and never a tie`() = runBlocking {
        val t1 = FakeTransport { order -> if (order == 1) ok("{\"winner\":\"Model A\"", finish = "length", ctok = 8192) else ok(verdict("Model B", 0.8)) }
        val e1 = evaluate(rig(config(), t1)).single()
        assertEquals("INVALID", e1.winner); assertNull(e1.tieSource); assertFalse(e1.positionFlip)
        assertTrue(e1.rationale.contains("NON_TERMINATED:length"), e1.rationale)
        assertEquals("INVALID", e1.judgeCalls.first { it.presentationOrder == 1 }.parsedWinner)
        assertEquals("length", e1.judgeCalls.first { it.presentationOrder == 1 }.finishReason)
        assertEquals(8192, e1.judgeCalls.first { it.presentationOrder == 1 }.completionTokens)

        val t2 = FakeTransport { order -> if (order == 2) JudgeCallResult("", "content_filter", 0, null, "rid-x", "azure:refusal", 400, 1, 5, "n/a") else ok(verdict("Model A", 0.9)) }
        val e2 = evaluate(rig(config(), t2)).single()
        assertEquals("INVALID", e2.winner); assertNull(e2.tieSource)
        assertTrue(e2.rationale.contains("NON_TERMINATED:content_filter"))
        assertEquals("rid-x", e2.judgeCalls.first { it.presentationOrder == 2 }.providerResponseId)
        assertEquals(400, e2.judgeCalls.first { it.presentationOrder == 2 }.httpStatus)

        val t3 = FakeTransport { _ -> ok("", finish = "stop").copy(content = null) }
        val e3 = evaluate(rig(config(), t3)).single()
        assertEquals("INVALID", e3.winner); assertTrue(e3.rationale.contains("NON_TERMINATED:no_content"))
    }

    @Test
    fun `think blocks are stripped before parsing and a configured temperature is recorded`() = runBlocking {
        val cfg = config(temperature = 0.0)
        val t = FakeTransport { order -> ok("<think>hmm</think>\n" + verdict(if (order == 1) "Model A" else "Model B", 0.7)) }
        val e = evaluate(rig(cfg, t)).single()
        assertEquals("Model A", e.winner)
        assertEquals("0.0", e.judgeCalls[0].temperatureLabel)
        for (b in t.bodies) assertTrue(String(b, Charsets.US_ASCII).endsWith(", \"temperature\": 0.0}"))
    }

    @Test
    fun `a question the kit does not cover yields no evaluation and no call`() = runBlocking {
        val t = FakeTransport { _ -> ok(verdict("Model A", 0.9)) }
        val r = rig(config(), t)
        val evals = evaluate(r, qid = 99)
        assertTrue(evals.isEmpty())
        assertEquals(0, t.bodies.size)
        assertEquals(1, r.service.recipeSkipped.get())
        assertEquals(0, r.client.calls)
    }

    @Test
    fun `OPTIONS mode with the recipe is refused before any call, as is a missing question id or condition`() = runBlocking {
        val t = FakeTransport { _ -> ok(verdict("Model A", 0.9)) }
        val r = rig(config(optionMode = "OPTIONS"), t)
        val ex = assertThrows(IllegalStateException::class.java) { runBlocking { evaluate(r) } }
        assertTrue(ex.message!!.contains("RESOLVED"), ex.message)
        assertEquals(0, t.bodies.size)
        val r2 = rig(config(), t)
        assertThrows(IllegalStateException::class.java) { runBlocking { evaluate(r2, qid = null) } }
        assertEquals(0, t.bodies.size)
        val r3 = rig(config(), t)
        assertThrows(IllegalStateException::class.java) {
            runBlocking {
                r3.service.evaluateWithPrecomputedTraces(
                    query = "q", options = emptyList(), modelA = "alpha", traceA = "TRACE-ALPHA", modelB = "beta", traceB = "TRACE-BETA",
                    assignedLeafIds = listOf(r3.node.id), condition = "GENERIC_JUDGE", evalQuestionId = 7
                )
            }
        }
        assertEquals(0, t.bodies.size)
        // a bad recipe name is refused too
        val cfg = config().apply { llm.judgeRecipe.name = "other" }
        assertThrows(IllegalStateException::class.java) { cfg.llm.judgeRecipe.validate("RESOLVED") }
    }

    @Test
    fun `with the recipe disabled the transport and kit are never touched`() = runBlocking {
        val cfg = TaxonomyConfig().apply { llm.judgeOptionMode = "RESOLVED" }   // enabled = false
        val t = FakeTransport { _ -> error("must not post") }
        val explodingKit = object : RecipeKitProvider { override fun get(): RecipeKit = error("must not open the kit") }
        val node = GraphNode(id = "leaf-7", label = "Thermo", depth = 2)
        node.judgePrompt = "P"; node.judgeRubric = "R"
        val taxonomyService = mock(TaxonomyService::class.java)
        `when`(taxonomyService.getGraph()).thenReturn(node)
        val client = object : TaxonomyLlmClient {
            override suspend fun generateClusterLabel(prompt: String) = ""
            override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String) = ""
            override suspend fun queryModelStructured(modelName: String, systemPrompt: String?, userPrompt: String, schema: JsonSchema) = verdict("TIE", 0.3)
            override fun setMaxParallel(limit: Int) {}
        }
        val service = TaxonomyArenaService(
            cfg, taxonomyService, client, mock(EmbeddingCache::class.java), mock(TaxonomyOperations::class.java),
            mock(ModelEvalStore::class.java), mock(TaxonomyRankingService::class.java), TaxonomyPerformanceTracker(), t, explodingKit
        )
        val e = service.evaluateWithPrecomputedTraces("q", listOf("a", "b"), "alpha", "A", "beta", "B", assignedLeafIds = listOf(node.id), evalQuestionId = 7).single()
        assertEquals("TIE", e.winner)
        assertTrue(e.judgeCalls.isEmpty())
        assertEquals(0, t.bodies.size)
    }
}
