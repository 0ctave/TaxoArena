package taxonomy.tui

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.tui.service.BatchTrickleEvaluator

class BatchTrickleBenchmarkTest {

    private fun emb(text: String) = Embedding(text, text, FloatArray(0))

    private fun leaf(id: String, depth: Int, texts: List<String>): GraphNode =
        GraphNode(id = id, label = id, depth = depth).apply {
            queries = texts.map { emb(it) }.toMutableList()
        }

    /** root -> {A (math), B (physics)}, both leaves at depth 1. */
    private fun buildDag(): GraphNode {
        val a = leaf("A", 1, listOf("a1", "a2", "a3"))
        val b = leaf("B", 1, listOf("b1", "b2"))
        return GraphNode(id = "root", label = "root", depth = 0).apply {
            children.add(a)
            children.add(b)
        }
    }

    private val textToDomain = mapOf(
        "a1" to "math", "a2" to "math", "a3" to "math",
        "b1" to "physics", "b2" to "physics",
    )

    @Test
    fun `collectLeaves returns only the two leaves`() {
        val leaves = BatchTrickleEvaluator.collectLeaves(buildDag())
        assertEquals(setOf("A", "B"), leaves.map { it.id }.toSet())
    }

    @Test
    fun `buildLeafProfiles tags each leaf by dominant training domain`() {
        val profiles = BatchTrickleEvaluator.buildLeafProfiles(
            BatchTrickleEvaluator.collectLeaves(buildDag()),
            textToDomain,
        )
        assertEquals("math", profiles["A"]!!.dominantDomain)
        assertEquals(3, profiles["A"]!!.size)
        assertEquals(1.0, profiles["A"]!!.purity, 1e-9)
        assertEquals("physics", profiles["B"]!!.dominantDomain)
        assertEquals(1.0, profiles["B"]!!.purity, 1e-9)
    }

    @Test
    fun `buildLeafProfiles skips leaves with no labeled queries`() {
        val dag = GraphNode(id = "root", label = "root", depth = 0).apply {
            children.add(leaf("A", 1, listOf("a1")))
            children.add(leaf("orphan", 1, listOf("unknown-text")))
        }
        val profiles = BatchTrickleEvaluator.buildLeafProfiles(
            BatchTrickleEvaluator.collectLeaves(dag),
            textToDomain,
        )
        assertEquals(setOf("A"), profiles.keys)
    }

    @Test
    fun `computeBatchTrickleMetrics produces correct metrics on a controlled scenario`() {
        val profiles = BatchTrickleEvaluator.buildLeafProfiles(
            BatchTrickleEvaluator.collectLeaves(buildDag()),
            textToDomain,
        )

        // routing table: text -> (leafId, confidence) pairs
        val routes = mapOf(
            "m1" to listOf("A" to 0.9, "B" to 0.1), // top A=math, true math  -> correct
            "p1" to listOf("B" to 0.8),             // top B=physics, true physics -> correct
            "m2" to listOf("B" to 0.7),             // top B=physics, true math -> wrong
            "p2" to emptyList(),                    // no match, true physics
        )
        val testQueries = listOf(
            "math" to "m1",
            "physics" to "p1",
            "math" to "m2",
            "physics" to "p2",
        )

        var lastProcessed = 0
        val result = BatchTrickleEvaluator.computeBatchTrickleMetrics(
            perLeafDomains = profiles,
            testQueries = testQueries,
            routeFn = { text -> routes[text] ?: emptyList() },
            onProgress = { processed, _, _ -> lastProcessed = processed },
        )

        assertEquals(4, result.totalQueries)
        assertEquals(4, lastProcessed)
        // 2 of 4 top-1 correct (m1, p1)
        assertEquals(0.5, result.top1Accuracy, 1e-9)
        // any-match: same two (m2 routed only to physics leaf, p2 no match)
        assertEquals(0.5, result.anyMatchAccuracy, 1e-9)
        // one of four routed nowhere
        assertEquals(0.25, result.noMatchRate, 1e-9)
        // top-1 matched leaves all pure
        assertEquals(1.0, result.meanLeafPurity, 1e-9)
        assertEquals(1.0, result.meanRoutingDepth, 1e-9)

        // math: tp=1, fp=0, fn=1 -> P=1.0 R=0.5 F1=0.6667
        val math = result.perDomainF1["math"]!!
        assertEquals(2, math.support)
        assertEquals(1.0, math.precision, 1e-9)
        assertEquals(0.5, math.recall, 1e-9)
        assertEquals(2.0 / 3.0, math.f1, 1e-9)

        // physics: tp=1, fp=1, fn=1 -> P=0.5 R=0.5 F1=0.5
        val physics = result.perDomainF1["physics"]!!
        assertEquals(2, physics.support)
        assertEquals(0.5, physics.precision, 1e-9)
        assertEquals(0.5, physics.recall, 1e-9)
        assertEquals(0.5, physics.f1, 1e-9)

        // macro-F1 = (0.6667 + 0.5) / 2
        assertEquals((2.0 / 3.0 + 0.5) / 2.0, result.macroF1, 1e-9)
        assertTrue(result.macroF1 > 0.0)
    }

    @Test
    fun `empty test set yields default zeros`() {
        val result = BatchTrickleEvaluator.computeBatchTrickleMetrics(
            perLeafDomains = emptyMap(),
            testQueries = emptyList(),
            routeFn = { emptyList() },
        )
        assertEquals(0, result.totalQueries)
        assertEquals(0.0, result.top1Accuracy, 1e-9)
    }
}
