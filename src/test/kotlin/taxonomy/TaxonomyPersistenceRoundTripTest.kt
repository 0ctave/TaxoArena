package taxonomy

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.mockito.Mockito.*
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.CachedQuery
import taxonomy.dataset.EmbeddingCache
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.service.TaxonomyPersistence
import java.io.File

/**
 * Round-trip persistence test for the soft-assignment state: per-node queryWeights,
 * residualConfidences, and the recomputed Jensen descent-gate shrinkage. Before the
 * fix a loaded snapshot silently dropped all soft membership weights and kept the
 * default childCentroidShrinkage of 1.0 (the un-tightened descent bar), so a loaded
 * DAG routed differently from the constructed one.
 */
class TaxonomyPersistenceRoundTripTest {

    private fun node(id: String, label: String, depth: Int) = GraphNode(id = id, label = label, depth = depth)

    private fun link(parent: GraphNode, child: GraphNode) {
        parent.children.add(child)
        child.parents.add(parent)
        child.treeParentId = parent.id
    }

    private fun hashQuery(text: String): String =
        "q_" + java.security.MessageDigest.getInstance("SHA-256")
            .digest(text.toByteArray())
            .joinToString("") { "%02x".format(it) }.take(16)

    @Test
    fun `queryWeights, residualConfidences and shrinkage survive save-load round trip`() {
        val config = TaxonomyConfig()
        val mockEmbeddingCache = mock(EmbeddingCache::class.java)
        val persistence = TaxonomyPersistence(config, mockEmbeddingCache)

        val root = node("root", "Root Domain", 0)
        val child1 = node("child1", "Child One", 1)
        val child2 = node("child2", "Child Two", 1)
        link(root, child1)
        link(root, child2)

        // Distinct non-empty vmfMu directions with nonzero query mass: the
        // mass-weighted resultant of (1,0) and (0,1) has norm < 1, so the parent's
        // recomputed shrinkage must come back strictly below the default 1.0.
        child1.vmfMu = floatArrayOf(1f, 0f)
        child1.sliceDim = 2
        child2.vmfMu = floatArrayOf(0f, 1f)
        child2.sliceDim = 2

        val textA = "alpha query"
        val textB = "beta query"
        val embA = Embedding(textA, textA, floatArrayOf(1f, 0f), "domainA")
        embA.queryId = 11
        val embB = Embedding(textB, textB, floatArrayOf(0f, 1f), "domainB")
        embB.queryId = 22
        child1.queries.add(embA)
        child2.queries.add(embB)

        // Soft membership mass on both children plus a residual-flagged entry with
        // an attached confidence on child1.
        child1.queryWeights[textA] = 0.7
        child2.queryWeights[textB] = 0.4
        child1.residualQueries.add("res_11")
        child1.residualConfidences["res_11"] = 0.42

        val qIdA = hashQuery(textA)
        val qIdB = hashQuery(textB)
        `when`(mockEmbeddingCache.getQueriesBatch(setOf(qIdA, qIdB)))
            .thenReturn(mapOf(
                qIdA to CachedQuery(textA, textA, "domainA", 11),
                qIdB to CachedQuery(textB, textB, "domainB", 22)
            ))
        `when`(mockEmbeddingCache.getBatch(setOf(textA, textB)))
            .thenReturn(mapOf(
                textA to floatArrayOf(1f, 0f),
                textB to floatArrayOf(0f, 1f)
            ))

        val tempFile = File.createTempFile("roundtrip_test", ".json")
        try {
            persistence.save(root, tempFile.absolutePath)

            val loadedRoot = persistence.load(tempFile.absolutePath)
            assertNotNull(loadedRoot)
            val loadedChild1 = loadedRoot!!.children.first { it.id == "child1" }
            val loadedChild2 = loadedRoot.children.first { it.id == "child2" }

            assertEquals(mapOf(textA to 0.7), loadedChild1.queryWeights.toMap(), "child1 queryWeights must survive the round trip")
            assertEquals(mapOf(textB to 0.4), loadedChild2.queryWeights.toMap(), "child2 queryWeights must survive the round trip")
            assertEquals(mapOf("res_11" to 0.42), loadedChild1.residualConfidences.toMap(), "residualConfidences must survive the round trip")
            assertEquals(setOf("res_11"), loadedChild1.residualQueries.toSet(), "residualQueries must survive the round trip")

            // Mass-weighted resultant: w1 = 0.7/1.1, w2 = 0.4/1.1 over orthogonal
            // unit directions -> norm = sqrt(w1^2 + w2^2) ~ 0.7330, not the default 1.0.
            assertNotEquals(1.0, loadedRoot.childCentroidShrinkage, 1e-9, "loaded parent's shrinkage must be recomputed, not left at the default")
            val w1 = 0.7 / 1.1
            val w2 = 0.4 / 1.1
            val expected = Math.sqrt(w1 * w1 + w2 * w2)
            assertEquals(expected, loadedRoot.childCentroidShrinkage, 1e-6, "shrinkage must equal the mass-weighted child resultant norm")
        } finally {
            tempFile.delete()
        }
    }
}
