package taxonomy

import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.io.TempDir
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.runner.FixedTreeLabels
import java.io.File
import java.util.Base64

/**
 * FIXED-TREE LABELS (D-2026-10-20-2): the production post-pass on a fixed fixture tree, with a recording client.
 *
 * Fixture: root -> [alpha] (6 items) -> two leaves a1 (3 items, questions "alpha one q0.."), a2 (3 items); root ->
 * [beta] leaf (2 items). Expected: exactly 2 calls (a1, a2: the nodes below the anchor depth), [alpha] / [beta] keep
 * their declared names, every prompt carries its leaf's questions and the domain anchor "Alpha", no prompt carries an
 * option marker, the structure is unchanged, the output names map to the right nodes (the recording client answers
 * with the first question it sees), the dry run makes no network call, the preflight refuses a blank / non-https
 * endpoint and never sends a request, and a re-run onto the same output path is refused (write-once).
 *
 * Mutants (temporary edits of FixedTreeLabelRunner.kt, reverted; this class run): F1 checkStructure skips the item
 * count -> killed (structureChangeRefused); F2 CategoryFetcher returns null -> killed (anchor assertion); F3 preflight
 * accepts http -> killed (preflightRefusals); F4 label() names depth-1 nodes in the output -> killed (assertNull on
 * anchors); F5 run() writes without CREATE_NEW -> killed (writeOnce). 5 of 5 killed.
 */
class FixedTreeLabelRunnerTest {

    private fun vec(vararg v: Float): String {
        val bb = java.nio.ByteBuffer.allocate(4 * v.size).order(java.nio.ByteOrder.LITTLE_ENDIAN)
        v.forEach { bb.putFloat(it) }
        return Base64.getEncoder().encodeToString(bb.array())
    }

    private fun fixture(): FixedTreeLabels.Input {
        val nodes = listOf(
            FixedTreeLabels.InNode(0, null, 0, "root", 8, "root", listOf(1, 2)),
            FixedTreeLabels.InNode(1, 0, 1, "subject", 6, "alpha", listOf(3, 4)),
            FixedTreeLabels.InNode(2, 0, 1, "subject", 2, "beta", emptyList()),
            FixedTreeLabels.InNode(3, 1, 2, "split", 3, "one / uno", emptyList()),
            FixedTreeLabels.InNode(4, 1, 2, "split", 3, "two / dos", emptyList()),
        )
        val items = (0 until 3).map { FixedTreeLabels.InItem(it, 3, "alpha one q$it", "alpha", vec(1f, 0.1f * it, 0f)) } +
            (3 until 6).map { FixedTreeLabels.InItem(it, 4, "alpha two q$it", "alpha", vec(0f, 1f, 0.1f * it)) } +
            (6 until 8).map { FixedTreeLabels.InItem(it, 2, "beta q$it", "beta", vec(0f, 0f, 1f)) }
        return FixedTreeLabels.Input("FX", "sha", 3, "question", 1, nodes, items)
    }

    private fun bytes(i: FixedTreeLabels.Input) = Json.encodeToString(i).toByteArray()

    class Recorder(val tally: FixedTreeLabels.Tally) : TaxonomyLlmClient {
        val prompts = java.util.Collections.synchronizedList(mutableListOf<String>())
        override suspend fun generateClusterLabel(prompt: String) = error("unused")
        override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String) = error("unused")
        override suspend fun queryModelStructured(modelName: String, systemPrompt: String?, userPrompt: String,
                                                  schema: JsonSchema): String {
            prompts.add(userPrompt)
            synchronized(tally) { tally.calls++ }
            val q = Regex("- (alpha (one|two))").find(userPrompt)!!.groupValues[1]
            return """{"label": "Named $q"}"""
        }
        override fun setMaxParallel(limit: Int) {}
    }

    @Test
    fun labelsOnlyBelowAnchorsFromQuestionsWithStructureKept() {
        val t = FixedTreeLabels.Tally()
        val rec = Recorder(t)
        val r = FixedTreeLabels.label(bytes(fixture()), rec, t, "fixture", dry = false, parallelism = 2)
        val o = r.output
        assertEquals(2, rec.prompts.size)
        assertEquals(2, o.calls)
        assertEquals(2, o.nodes_labelled)
        val byNode = o.nodes.associateBy { it.node }
        assertEquals("Named alpha one", byNode.getValue(3).llm_label)
        assertEquals("Named alpha two", byNode.getValue(4).llm_label)
        assertNull(byNode.getValue(1).llm_label)
        assertNull(byNode.getValue(2).llm_label)
        assertEquals(listOf(0, 1, 2, 3, 4), o.nodes.map { it.node })
        assertEquals(listOf(null, 0, 0, 1, 1), o.nodes.map { it.parent })
        assertEquals(listOf(8, 6, 2, 3, 3), o.nodes.map { it.n })
        for (p in rec.prompts) {
            assertTrue(p.contains("Ground Truth Domain Anchors: Alpha"), p)
            assertTrue(p.contains("Parent Domain (Broad Context): alpha"), p)
            assertFalse(p.contains("(A)"), p)
        }
        assertTrue(rec.prompts.any { it.contains("- alpha one q0") && it.contains("- alpha one q2") })
        assertEquals(FixedTreeLabels.sha256(bytes(fixture())), o.input_sha256)
    }

    @Test
    fun structureChangeRefused() {
        val f = fixture()
        val bad = f.copy(nodes = f.nodes.map { if (it.node == 3) it.copy(n = 4) else it })
        assertThrows<IllegalStateException> { FixedTreeLabels.buildGraph(bad) }
        val bad2 = f.copy(items = f.items.map { if (it.row == 0) it.copy(leaf = 1) else it })
        assertThrows<IllegalArgumentException> { FixedTreeLabels.buildGraph(bad2) }
    }

    @Test
    fun preflightRefusals() {
        val ok = { _: String -> }
        assertThrows<IllegalStateException> { FixedTreeLabels.preflight(mapOf("AZURE_AI_API_KEY" to "k"), "M", "v", ok) }
        assertThrows<IllegalStateException> {
            FixedTreeLabels.preflight(mapOf("AZURE_AI_ENDPOINT" to "https://x.example", "AZURE_AI_API_KEY" to " "), "M", "v", ok)
        }
        assertThrows<IllegalStateException> {
            FixedTreeLabels.preflight(mapOf("AZURE_AI_ENDPOINT" to "http://x.example", "AZURE_AI_API_KEY" to "k"), "M", "v", ok)
        }
        assertThrows<IllegalStateException> {
            FixedTreeLabels.preflight(mapOf("AZURE_AI_ENDPOINT" to "https://x.example", "AZURE_AI_API_KEY" to "k"), "M", "v")
            { throw java.net.UnknownHostException(it) }
        }
        // builds the model object and sends nothing (an unresolvable host would fail on a call, not here)
        FixedTreeLabels.preflight(mapOf("AZURE_AI_ENDPOINT" to "https://x.example", "AZURE_AI_API_KEY" to "k"), "M", "v", ok)
    }

    @Test
    fun dryRunEndToEndAndWriteOnce(@TempDir dir: File) {
        val inF = File(dir, "in.json").also { it.writeBytes(bytes(fixture())) }
        val outF = File(dir, "labels.json")
        val env = mapOf("AZURE_AI_ENDPOINT" to "https://localhost", "AZURE_AI_API_KEY" to "k")
        val rc = FixedTreeLabels.run(arrayOf("--in", inF.path, "--out", outF.path, "--dry-run", "--model", "M"), env)
        assertEquals(0, rc)
        val o = Json { ignoreUnknownKeys = true }.decodeFromString<FixedTreeLabels.Output>(outF.readText())
        assertTrue(o.dry_run)
        assertEquals(2, o.calls)
        assertEquals(0L, o.completion_tokens)
        assertEquals(setOf("DRY 1", "DRY 2"), o.nodes.mapNotNull { it.llm_label }.toSet())
        assertEquals(2, File(dir, "labels.json.calls.jsonl").readLines().size)
        assertThrows<IllegalStateException> {
            FixedTreeLabels.run(arrayOf("--in", inF.path, "--out", outF.path, "--dry-run", "--model", "M"), env)
        }
    }
}
