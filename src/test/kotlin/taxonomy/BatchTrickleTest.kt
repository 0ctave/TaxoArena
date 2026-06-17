package org.eclipse.lmos.arc.app.taxonomy

import org.eclipse.lmos.arc.app.MMLUDatasetFetcher
import org.eclipse.lmos.arc.app.taxonomy.operations.TaxonomyTrickler
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest

@SpringBootTest(properties = [
    "taxoadapt.execution.enable-tui=false",
    "taxoadapt.execution.run-batch=false",
    "taxoadapt.execution.start-service=false"
])
class BatchTrickleTest {

    @Autowired
    private lateinit var datasetFetcher: MMLUDatasetFetcher

    @Autowired
    private lateinit var embeddingCache: EmbeddingCache

    @Autowired
    private lateinit var trickler: TaxonomyTrickler

    @Test
    fun testDominantDomainCalculation() {
        val queryToCategory = mapOf(
            "What is an operating system?" to "Computer Science",
            "What is CPU scheduling?" to "Computer Science",
            "What is photosynthesis?" to "Biology"
        )

        val leaf1 = GraphNode(label = "CS Leaf", depth = 1).apply {
            queries.add(Embedding("What is an operating system?", "What is an operating system?", FloatArray(4)))
            queries.add(Embedding("What is CPU scheduling?", "What is CPU scheduling?", FloatArray(4)))
        }

        val leaf2 = GraphNode(label = "Bio Leaf", depth = 1).apply {
            queries.add(Embedding("What is photosynthesis?", "What is photosynthesis?", FloatArray(4)))
        }

        val root = GraphNode(label = "Root", depth = 0).apply {
            children.add(leaf1)
            children.add(leaf2)
        }

        fun getDominantDomain(node: GraphNode): String? {
            val branchQueries = node.getAllQueriesInBranch()
            if (branchQueries.isEmpty()) return null
            val counts = branchQueries.mapNotNull { queryToCategory[it.rawText] }.groupingBy { it }.eachCount()
            return counts.maxByOrNull { it.value }?.key
        }

        assertEquals("Computer Science", getDominantDomain(leaf1))
        assertEquals("Biology", getDominantDomain(leaf2))
        assertEquals("Computer Science", getDominantDomain(root)) // 2 CS vs 1 Bio in branch
    }
}
