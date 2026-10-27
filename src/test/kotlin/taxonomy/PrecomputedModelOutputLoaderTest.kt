package taxonomy

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import taxonomy.dataset.PrecomputedModelOutputLoader
import java.io.File
import java.nio.file.Path
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

class PrecomputedModelOutputLoaderTest {

    private val loader = PrecomputedModelOutputLoader()

    // Tiny synthetic fixture matching the MMLU-Pro eval_results schema (3 records).
    private val fixtureJson = """
        [
          {"question_id": 70, "question": "What is 2+2?", "options": ["3","4","5"],
           "answer": "B", "answer_index": 1, "category": "math",
           "pred": "B", "model_outputs": "The answer is B."},
          {"question_id": 71, "question": "Capital of France?", "options": ["Paris","Rome"],
           "answer": "A", "answer_index": 0, "category": "geography",
           "pred": "A", "model_outputs": "Paris, so A."},
          {"question_id": 72, "question": "Boiling point of water (C)?", "options": ["90","100"],
           "answer": "B", "answer_index": 1, "category": "physics",
           "pred": null, "model_outputs": "Unsure."}
        ]
    """.trimIndent()

    @Test
    fun `derives model name from filename stripping prefix shots and extensions`() {
        assertEquals("GPT-4o", PrecomputedModelOutputLoader.deriveModelName("model_outputs_GPT-4o_5shots.zip"))
        assertEquals(
            "claude-3-5-sonnet",
            PrecomputedModelOutputLoader.deriveModelName("model_outputs_claude-3-5-sonnet_0shots.json.zip")
        )
        assertEquals("llama-3", PrecomputedModelOutputLoader.deriveModelName("/some/dir/model_outputs_llama-3.json"))
    }

    @Test
    fun `loads raw json file keyed by questionId`(@TempDir dir: Path) {
        val file = File(dir.toFile(), "model_outputs_test-model_5shots.json")
        file.writeText(fixtureJson)

        val outputs = loader.loadFromFile(file.absolutePath)

        assertEquals(3, outputs.size)
        assertEquals("B", outputs[70]?.pred)
        assertEquals("geography", outputs[71]?.category)
        assertNull(outputs[72]?.pred)
    }

    @Test
    fun `loads zip with single inner json`(@TempDir dir: Path) {
        val zipFile = File(dir.toFile(), "model_outputs_zipped-model_0shots.zip")
        ZipOutputStream(zipFile.outputStream()).use { zos ->
            zos.putNextEntry(ZipEntry("math.json"))
            zos.write(fixtureJson.toByteArray())
            zos.closeEntry()
        }

        val outputs = loader.loadFromFile(zipFile.absolutePath)

        assertEquals(3, outputs.size)
        assertEquals("What is 2+2?", outputs[70]?.question)
    }

    @Test
    fun `loadAll builds roster keyed by derived model name`(@TempDir dir: Path) {
        val fileA = File(dir.toFile(), "model_outputs_alpha_5shots.json").apply { writeText(fixtureJson) }
        val fileB = File(dir.toFile(), "model_outputs_beta_5shots.json").apply { writeText(fixtureJson) }

        val roster = loader.loadAll(listOf(fileA.absolutePath, fileB.absolutePath))

        assertEquals(setOf("alpha", "beta"), roster.keys)
        assertEquals(3, roster["alpha"]?.size)
    }
}
