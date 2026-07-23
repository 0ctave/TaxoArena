package taxonomy

import taxonomy.*
import taxonomy.arena.*
import taxonomy.prompts.*
import taxonomy.utils.*
import taxonomy.config.*
import taxonomy.model.*
import taxonomy.controller.*
import taxonomy.service.*
import taxonomy.dataset.*
import taxonomy.operations.*
import taxonomy.tui.*
import taxonomy.runner.*

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import java.io.File
import java.nio.file.Path
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

@SpringBootTest(
    classes = [org.eclipse.lmos.arc.app.TaxoAdaptApplication::class],
    properties = [
        "taxoadapt.execution.enable-tui=false",
        "taxoadapt.execution.run-batch=false",
        "taxoadapt.execution.start-service=false"
    ]
)
class TaxonomySnapshotTest {

    @Autowired
    private lateinit var snapshotManager: TaxonomySnapshotManager

    @Autowired
    private lateinit var config: TaxonomyConfig

    @Test
    fun testSaveLoadDeleteSnapshot() {
        // 0. Set up dummy reserved test queries
        val reservedFile = File("reserved_test_queries.json")
        val originalContent = if (reservedFile.exists()) reservedFile.readText() else null
        
        val testQueriesJson = """
            {
                "domain_a": [101, 102],
                "domain_b": [201]
            }
        """.trimIndent()
        reservedFile.writeText(testQueriesJson)

        try {
            // 1. Create a mock DAG root and child
            val root = GraphNode(id = "root_test", label = "Root Node", depth = 0).apply {
                judgePrompt = "Root Persona"
                judgeRubric = "Root Rubric"
            }
            val child = GraphNode(id = "child_test", label = "Child Node", depth = 1).apply {
                judgePrompt = "Child Persona"
                judgeRubric = "Child Rubric"
            }
            root.children.add(child)
            child.parents.add(root)

            // 2. Save snapshot
            val testDesc = "JUnit Test Run"
            val snapshot = snapshotManager.saveSnapshot(root, testDesc)
            
            assertNotNull(snapshot)
            assertEquals(testDesc, snapshot.description)
            assertEquals(2, snapshot.metrics.totalNodes)
            assertEquals(1, snapshot.metrics.leafNodes)
            assertEquals(2, snapshot.reservedQueries.size)
            assertEquals(listOf(101, 102), snapshot.reservedQueries["domain_a"])
            assertEquals(listOf(201), snapshot.reservedQueries["domain_b"])

            // 3. List snapshots and verify our snapshot is present
            val list = snapshotManager.listSnapshots()
            val listMatch = list.find { it.id == snapshot.id }
            assertNotNull(listMatch)
            assertEquals(2, listMatch!!.reservedQueries.size)
            assertEquals(listOf(101, 102), listMatch.reservedQueries["domain_a"])

            // Delete local file to verify loading restores it
            reservedFile.delete()

            // 4. Load the snapshot
            val loadedRoot = snapshotManager.loadSnapshot(snapshot.id)
            assertNotNull(loadedRoot)
            assertEquals(root.id, loadedRoot!!.id)
            assertEquals(root.label, loadedRoot.label)
            assertEquals("Root Persona", loadedRoot.judgePrompt)
            assertEquals("Root Rubric", loadedRoot.judgeRubric)
            assertEquals(1, loadedRoot.children.size)
            val loadedChild = loadedRoot.children.first()
            assertEquals(child.id, loadedChild.id)
            assertEquals("Child Persona", loadedChild.judgePrompt)
            assertEquals("Child Rubric", loadedChild.judgeRubric)

            // Verify the file was restored
            assertTrue(reservedFile.exists())
            val restoredContent = reservedFile.readText()
            assertTrue(restoredContent.contains("domain_a"))
            assertTrue(restoredContent.contains("101"))

            // 5. Delete snapshot
            val deleted = snapshotManager.deleteSnapshot(snapshot.id)
            assertTrue(deleted)

            // Verify it was deleted from list
            val listAfter = snapshotManager.listSnapshots()
            assertFalse(listAfter.any { it.id == snapshot.id })
        } finally {
            // Restore original reserved queries file if it existed
            if (originalContent != null) {
                reservedFile.writeText(originalContent)
            } else {
                if (reservedFile.exists()) {
                    reservedFile.delete()
                }
            }
        }
    }

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
            selectedDomains = emptyList(), maxDepth = 8, enableLabeling = false,
            separationEpsilon = 0.02, minClusterSize = 25,
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
