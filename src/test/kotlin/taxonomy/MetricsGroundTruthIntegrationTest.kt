package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.utils.TaxonomyMetrics

/**
 * End-to-end check that per-query true-leaf ground truth is plumbed into the metrics
 * pipeline (PR #48): Overlapping NMI and Hierarchical F₁ must report real, non-zero
 * values instead of the placeholder 0.0 that PR #46 left behind.
 */
class MetricsGroundTruthIntegrationTest {

    private fun node(label: String, depth: Int) = GraphNode(label = label, depth = depth)
    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child)
        child.parents.add(parent)
    }

    private fun emb(text: String) = Embedding(rawText = text, distilledText = text, values = FloatArray(0))

    @Test
    fun reportsNonZeroNmiAndHierarchicalF1ForDomainGroundTruth() {
        // root → {Math, Physics}; each domain has two depth-2 leaves.
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
        // 10 queries across 4 leaves; true category is the domain (depth-1 label).
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
        // Categories are the leaf labels themselves, so each query's true leaf is exactly the
        // leaf it is placed in — predicted (max-κ) leaf == ground-truth leaf.
        val root = node("root", 0)
        val math = node("Math", 1)
        val physics = node("Physics", 1)
        link(root, math); link(root, physics)

        val mLeaf1 = node("algebra", 2); val mLeaf2 = node("geometry", 2)
        val pLeaf1 = node("optics", 2); val pLeaf2 = node("mechanics", 2)
        link(math, mLeaf1); link(math, mLeaf2)
        link(physics, pLeaf1); link(physics, pLeaf2)

        val groundTruth = HashMap<String, List<String>>()
        fun place(leaf: GraphNode, texts: List<String>) {
            texts.forEach { t ->
                leaf.queries.add(emb(t))
                groundTruth[t] = listOf(leaf.label!!)
            }
        }
        place(mLeaf1, listOf("q1", "q2", "q3"))
        place(mLeaf2, listOf("q4", "q5"))
        place(pLeaf1, listOf("q6", "q7", "q8"))
        place(pLeaf2, listOf("q9", "q10"))

        val report = TaxonomyMetrics(root, groundTruth).generateReport()

        assertEquals(1.0, report.hF1, 1e-9, "Exact routing must give H-F₁ = 1.0")
        assertEquals(1.0, report.nmi, 1e-9, "Identical coverings must give Overlapping NMI = 1.0")
    }

    @Test
    fun emptyGroundTruthYieldsZeroWithoutThrowing() {
        val root = node("root", 0)
        val domain = node("Math", 1)
        val leaf = node("algebra", 2)
        link(root, domain); link(domain, leaf)
        leaf.queries.add(emb("q1"))

        // No groundTruthMap entries → metrics degrade to 0, must not throw.
        val report = TaxonomyMetrics(root).generateReport()
        assertEquals(0.0, report.hF1, 1e-9)
        assertEquals(0.0, report.nmi, 1e-9)
    }
}
