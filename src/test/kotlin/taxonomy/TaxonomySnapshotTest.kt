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
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import java.io.File

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
                "domain_a": ["query 1", "query 2"],
                "domain_b": ["query 3"]
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
            assertEquals(listOf("query 1", "query 2"), snapshot.reservedQueries["domain_a"])
            assertEquals(listOf("query 3"), snapshot.reservedQueries["domain_b"])

            // 3. List snapshots and verify our snapshot is present
            val list = snapshotManager.listSnapshots()
            val listMatch = list.find { it.id == snapshot.id }
            assertNotNull(listMatch)
            assertEquals(2, listMatch!!.reservedQueries.size)
            assertEquals(listOf("query 1", "query 2"), listMatch.reservedQueries["domain_a"])

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
            assertTrue(restoredContent.contains("query 1"))

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
}
