package taxonomy.dataset

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import java.io.File
import java.nio.file.Path
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

class EvalCatalogTest {

    /** Throwaway store backed by a temp DB so getLoadedModels() starts empty. */
    private fun emptyStore(dir: Path) = ModelEvalStore(File(dir.toFile(), "eval_test.db").path)

    @Test
    fun `scan picks up zip files and result directories with derived model names`(@TempDir dir: Path) {
        val evalDir = File(dir.toFile(), "eval_results").apply { mkdirs() }

        // A zipped source.
        File(evalDir, "model_outputs_FOO_5shots.zip").let { zip ->
            ZipOutputStream(zip.outputStream()).use { zos ->
                zos.putNextEntry(ZipEntry("math.json"))
                zos.write("[]".toByteArray())
                zos.closeEntry()
            }
        }
        // A directory source containing a json file.
        File(evalDir, "model_outputs_BAR_5shots").apply { mkdirs() }
            .let { File(it, "physics.json").writeText("[]") }

        val catalog = EvalCatalog(emptyStore(dir)).scan(evalDir.path)

        assertEquals(2, catalog.size, "one zip + one directory = two model sources")
        assertEquals(setOf("FOO", "BAR"), catalog.map { it.modelName }.toSet())
        assertTrue(catalog.all { !it.alreadyIngested }, "nothing ingested into the empty store yet")
        assertTrue(catalog.all { it.sizeBytes > 0 }, "size should be measured")
    }

    @Test
    fun `scan returns empty list for a missing directory`(@TempDir dir: Path) {
        val catalog = EvalCatalog(emptyStore(dir)).scan(File(dir.toFile(), "does-not-exist").path)
        assertTrue(catalog.isEmpty())
    }
}
