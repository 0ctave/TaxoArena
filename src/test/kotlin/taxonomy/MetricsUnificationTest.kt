package taxonomy

import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.model.IterationMetrics
import taxonomy.model.TaxonomyMetricsData
import taxonomy.service.SnapshotMetrics

/**
 * Verifies that metrics are coherent across the framework: the canonical
 * [TaxonomyMetricsData] flows unchanged into [IterationMetrics] (history) and
 * [SnapshotMetrics] (persistence), survives JSON round-trips, and that old
 * snapshot JSON (missing newer fields) still deserializes with defaults.
 */
class MetricsUnificationTest {

    private val json = Json { ignoreUnknownKeys = true }

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

    @Test
    fun iterationMetrics_composes_canonical_payload_without_drift() {
        val data = sampleData()
        val iter = IterationMetrics(iteration = "Iter 3", metrics = data)

        // Delegating accessors must mirror the canonical payload exactly.
        assertEquals(data.totalNodes, iter.totalNodes)
        assertEquals(data.equilibriumIndex, iter.equilibriumIndex)
        assertEquals(data.avgMatchCount, iter.avgMatchCount)
        assertEquals(data.kappaByDepth, iter.kappaByDepth)
        assertEquals(data.leafDistribEntropy, iter.leafDistribEntropy)
        assertEquals("Iter 3", iter.iteration)

        // JSON round-trip preserves both label and payload.
        val restored = json.decodeFromString<IterationMetrics>(json.encodeToString<IterationMetrics>(iter))
        assertEquals(iter, restored)
    }

    @Test
    fun snapshotMetrics_roundtrips_canonical_payload() {
        val data = sampleData()
        val snap = SnapshotMetrics.fromData(data, nodesWithJudges = 17)

        // Snapshot-only field retained; canonical fields preserved.
        assertEquals(17, snap.nodesWithJudges)
        assertEquals(data, snap.toData())

        // Persisted JSON decodes back to an identical canonical payload.
        val restored = json.decodeFromString<SnapshotMetrics>(json.encodeToString<SnapshotMetrics>(snap))
        assertEquals(snap, restored)
        assertEquals(data, restored.toData())
    }

    @Test
    fun old_snapshot_json_with_missing_fields_still_loads() {
        // A legacy row written when SnapshotMetrics had only the 5 required fields.
        val legacy = """{"totalNodes":10,"leafNodes":7,"crossDomainNodes":1,"maxDepth":3,"totalUniqueQueries":500}"""
        val decoded = json.decodeFromString<SnapshotMetrics>(legacy)

        assertEquals(10, decoded.totalNodes)
        assertEquals(500, decoded.totalUniqueQueries)
        // Newer fields fall back to tolerant defaults rather than failing.
        assertEquals(0.0, decoded.nmi)
        assertEquals(1.0, decoded.avgMatchCount)
        assertEquals(0, decoded.nodesWithJudges)
        assertTrue(decoded.toData().kappaByDepth.isEmpty())
    }
}
