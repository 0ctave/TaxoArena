package taxonomy

import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.IterationMetrics
import taxonomy.model.TaxonomyMetricsData
import taxonomy.service.SnapshotMetrics
import taxonomy.utils.TaxonomyMetrics

/**
 * Integration test suite for Taxonomy metrics generation, report plumbing,
 * and data structures serialization/deserialization.
 */
class TaxonomyMetricsIntegrationTest {

    private val json = Json { ignoreUnknownKeys = true }

    private fun node(label: String, depth: Int) = GraphNode(label = label, depth = depth)
    
    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child)
        child.parents.add(parent)
    }

    private fun emb(text: String) = Embedding(rawText = text, distilledText = text, values = FloatArray(0))

    private fun sampleData() = TaxonomyMetricsData(
        totalNodes = 42,
        leafNodes = 30,
        crossDomainNodes = 4,
        maxDepth = 6,
        avgLeafDepth = 3.5,
        medianLeafAssignments = 1.2,
        totalUniqueQueries = 12000,
        residualQueries = 120,
        residualRatio = 0.01,
        maxLeafConcentration = 0.08,
        contaminationRatio = 0.03,
        equilibriumIndex = 0.91,
        nmi = 0.74,
        ari = 0.66,
        dendrogramPurity = 0.81,
        weightedLeafPurity = 0.83,
        edgeF1 = 0.77,
        sphericalSilhouette = 0.55,
        ancestorCorrectRate = 0.88,
        avgMatchCount = 1.07,
        kappaByDepth = mapOf(0 to 10.0, 1 to 25.0, 2 to 40.0),
        leafDistribEntropy = 4.2,
    )

    // ─────────────────────────────────────────────────────────────────────────
    //  TaxonomyMetrics Generation & Ground Truth Integration
    // ─────────────────────────────────────────────────────────────────────────
    @Test
    fun reportsNonZeroNmiAndHierarchicalF1ForDomainGroundTruth() {
        val root = node("root", 0)
        val math = node("Math", 1)
        val physics = node("Physics", 1)
        link(root, math); link(root, physics)

        val mLeaf1 = node("algebra", 2); val mLeaf2 = node("geometry", 2)
        val pLeaf1 = node("optics", 2); val pLeaf2 = node("mechanics", 2)
        link(math, mLeaf1); link(math, mLeaf2)
        link(physics, pLeaf1); link(physics, pLeaf2)

        val groundTruth = HashMap<String, List<String>>()
        fun place(leaf: GraphNode, category: String, texts: List<String>) {
            texts.forEach { t ->
                leaf.queries.add(emb(t))
                groundTruth[t] = listOf(category)
            }
        }
        place(mLeaf1, "Math", listOf("q1", "q2", "q3"))
        place(mLeaf2, "Math", listOf("q4", "q5"))
        place(pLeaf1, "Physics", listOf("q6", "q7", "q8"))
        place(pLeaf2, "Physics", listOf("q9", "q10"))

        val report = TaxonomyMetrics(root, groundTruth).generateReport()

        assertTrue(report.hF1 > 0.0 && report.hF1 <= 1.0, "H-F₁ must be non-zero, was ${report.hF1}")
        assertTrue(report.hPrecision > 0.0, "H-P must be non-zero, was ${report.hPrecision}")
        assertTrue(report.hRecall > 0.0, "H-R must be non-zero, was ${report.hRecall}")
        assertTrue(report.nmi > 0.0 && report.nmi <= 1.0, "Overlapping NMI must be in (0,1], was ${report.nmi}")
    }

    @Test
    fun scoresOneWhenPredictedRoutingEqualsGroundTruth() {
        val root = node("root", 0)
        val math = node("Math", 1)
        val physics = node("Physics", 1)
        link(root, math); link(root, physics)

        val groundTruth = HashMap<String, List<String>>()
        fun place(leaf: GraphNode, texts: List<String>) {
            texts.forEach { t ->
                leaf.queries.add(emb(t))
                groundTruth[t] = listOf(leaf.label!!)
            }
        }
        place(math, listOf("q1", "q2", "q3"))
        place(physics, listOf("q6", "q7", "q8"))

        val report = TaxonomyMetrics(root, groundTruth).generateReport()

        assertEquals(1.0, report.hF1, 1e-9, "Exact routing must give H-F₁ = 1.0")
        assertEquals(1.0, report.nmi, 1e-9, "Identical coverings must give NMI = 1.0")
    }

    @Test
    fun emptyGroundTruthYieldsZeroWithoutThrowing() {
        val root = node("root", 0)
        val domain = node("Math", 1)
        val leaf = node("algebra", 2)
        link(root, domain); link(domain, leaf)
        leaf.queries.add(emb("q1"))

        val report = TaxonomyMetrics(root).generateReport()
        assertEquals(0.0, report.hF1, 1e-9)
        assertEquals(0.0, report.nmi, 1e-9)
    }

    // ─────────────────────────────────────────────────────────────────────────
    //  Data Structures Roundtrip Tests
    // ─────────────────────────────────────────────────────────────────────────
    @Test
    fun iterationMetrics_composes_canonical_payload_without_drift() {
        val data = sampleData()
        val iter = IterationMetrics(iteration = "Iter 3", metrics = data)

        assertEquals(data.totalNodes, iter.totalNodes)
        assertEquals(data.equilibriumIndex, iter.equilibriumIndex)
        assertEquals(data.avgMatchCount, iter.avgMatchCount)
        assertEquals(data.kappaByDepth, iter.kappaByDepth)
        assertEquals(data.leafDistribEntropy, iter.leafDistribEntropy)
        assertEquals("Iter 3", iter.iteration)

        val restored = json.decodeFromString<IterationMetrics>(json.encodeToString<IterationMetrics>(iter))
        assertEquals(iter, restored)
    }

    @Test
    fun snapshotMetrics_roundtrips_canonical_payload() {
        val data = sampleData()
        val snap = SnapshotMetrics.fromData(data, nodesWithJudges = 17)

        assertEquals(17, snap.nodesWithJudges)
        assertEquals(data, snap.toData())

        val restored = json.decodeFromString<SnapshotMetrics>(json.encodeToString<SnapshotMetrics>(snap))
        assertEquals(snap, restored)
        assertEquals(data, restored.toData())
    }

    @Test
    fun old_snapshot_json_with_missing_fields_still_loads() {
        val legacy = """{"totalNodes":10,"leafNodes":7,"crossDomainNodes":1,"maxDepth":3,"totalUniqueQueries":500}"""
        val decoded = json.decodeFromString<SnapshotMetrics>(legacy)

        assertEquals(10, decoded.totalNodes)
        assertEquals(500, decoded.totalUniqueQueries)
        assertEquals(0.0, decoded.nmi)
        assertEquals(1.0, decoded.avgMatchCount)
        assertEquals(0, decoded.nodesWithJudges)
        assertTrue(decoded.toData().kappaByDepth.isEmpty())
    }
}
