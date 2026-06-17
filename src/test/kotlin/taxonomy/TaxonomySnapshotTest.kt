package org.eclipse.lmos.arc.app.taxonomy

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import java.io.File

@SpringBootTest(properties = [
    "taxoadapt.execution.enable-tui=false",
    "taxoadapt.execution.run-batch=false",
    "taxoadapt.execution.start-service=false"
])
class TaxonomySnapshotTest {

    @Autowired
    private lateinit var snapshotManager: TaxonomySnapshotManager

    @Autowired
    private lateinit var config: TaxonomyConfig

    @Test
    fun testSaveLoadDeleteSnapshot() {
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

        // 3. List snapshots and verify our snapshot is present
        val list = snapshotManager.listSnapshots()
        assertTrue(list.any { it.id == snapshot.id })

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

        // 5. Delete snapshot
        val deleted = snapshotManager.deleteSnapshot(snapshot.id)
        assertTrue(deleted)

        // Verify it was deleted from list
        val listAfter = snapshotManager.listSnapshots()
        assertFalse(listAfter.any { it.id == snapshot.id })
    }
}
