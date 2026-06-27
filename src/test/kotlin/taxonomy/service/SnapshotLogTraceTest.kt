package taxonomy.service

import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import java.io.File
import java.nio.file.Path

/**
 * Verifies that [DagSnapshot.logTrace] survives JSON serialization (Part B of PR #51) and that
 * snapshots written before the field existed still deserialize, defaulting the trace to empty.
 */
class SnapshotLogTraceTest {

    private val json = Json { prettyPrint = true; ignoreUnknownKeys = true; encodeDefaults = true }

    private fun sampleSnapshot(logTrace: List<String>) = DagSnapshot(
        id = "20260627_120000_test",
        timestamp = "2026-06-27 12:00:00",
        description = "trace round-trip",
        graph = SerializedGraph("", emptyList()),
        metrics = SnapshotMetrics(
            totalNodes = 3, leafNodes = 2, crossDomainNodes = 0, maxDepth = 1, totalUniqueQueries = 10,
        ),
        settings = SnapshotSettings(
            selectedDomains = emptyList(), maxDepth = 8, enableLabeling = false, enableLiveLabeling = false,
            separationEpsilon = 0.02, minClusterSize = 25, cosineTau = 5.0, assignmentGap = 1.0, emaAlpha = 0.7,
        ),
        logTrace = logTrace,
    )

    @Test
    fun logTraceRoundTripsThroughTempFile(@TempDir dir: Path) {
        val trace = listOf("[INFO] [SPLIT] node A", "[INFO] [MERGE] node B", "[WARN] residual queue full")
        val file = File(dir.toFile(), "snapshot.json")
        file.writeText(json.encodeToString(sampleSnapshot(trace)))

        val loaded = json.decodeFromString<DagSnapshot>(file.readText())
        assertEquals(trace, loaded.logTrace, "logTrace must round-trip verbatim")
    }

    @Test
    fun snapshotWithoutLogTraceFieldStillParses() {
        // Encode with defaults omitted to mimic a snapshot file written before logTrace existed.
        val legacyJson = Json { encodeDefaults = false; ignoreUnknownKeys = true }
        val serialized = legacyJson.encodeToString(sampleSnapshot(emptyList()))
        assertFalse(serialized.contains("logTrace"), "precondition: legacy JSON omits the field")

        val loaded = json.decodeFromString<DagSnapshot>(serialized)
        assertTrue(loaded.logTrace.isEmpty(), "missing logTrace must default to an empty list")
    }
}
