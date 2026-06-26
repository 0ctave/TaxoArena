package taxonomy.dataset

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.*
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import java.io.File
import java.util.zip.ZipFile

@Serializable
data class PrecomputedModelOutput(
    val questionId: Int,         // question_id from MMLU-Pro dataset
    val question: String,
    val options: List<String>,
    val answer: String,          // GT correct letter e.g. "A"
    val answerIndex: Int,
    val category: String,
    val pred: String?,           // model's extracted answer letter (may be null if extraction failed)
    val modelOutputs: String     // full CoT trace
)

@Service
class PrecomputedModelOutputLoader {
    private val log = LoggerFactory.getLogger("ModelOutputLoader")
    private val json = Json { ignoreUnknownKeys = true; isLenient = true; coerceInputValues = true }

    /**
     * Loads all per-category JSON files from a model output zip.
     * Returns a map of questionId -> PrecomputedModelOutput.
     */
    fun loadFromZip(zipPath: String, modelName: String): Map<Int, PrecomputedModelOutput> {
        val result = mutableMapOf<Int, PrecomputedModelOutput>()
        try {
            ZipFile(zipPath).use { zip ->
                zip.entries().asSequence()
                    .filter { it.name.endsWith(".json") && !it.isDirectory }
                    .forEach { entry ->
                        zip.getInputStream(entry).use { stream ->
                            val text = stream.bufferedReader().readText()
                            parseOutputFile(text, modelName).forEach { item ->
                                result[item.questionId] = item
                            }
                        }
                    }
            }
            log.info("Loaded ${result.size} outputs for model '$modelName' from $zipPath")
        } catch (e: Exception) {
            log.error("Failed to load outputs from $zipPath", e)
        }
        return result
    }

    /**
     * Loads from an already-extracted directory of per-category JSON files.
     */
    fun loadFromDirectory(dirPath: String, modelName: String): Map<Int, PrecomputedModelOutput> {
        val result = mutableMapOf<Int, PrecomputedModelOutput>()
        File(dirPath).walkTopDown()
            .filter { it.isFile && it.extension == "json" }
            .forEach { file ->
                runCatching {
                    parseOutputFile(file.readText(), modelName).forEach { item ->
                        result[item.questionId] = item
                    }
                }.onFailure { log.warn("Failed to parse ${file.name}: ${it.message}") }
            }
        log.info("Loaded ${result.size} outputs for model '$modelName' from $dirPath")
        return result
    }

    private fun parseOutputFile(text: String, modelName: String): List<PrecomputedModelOutput> {
        return try {
            // Files are a JSON array at top level
            val array = json.parseToJsonElement(text).jsonArray
            array.mapNotNull { elem ->
                val obj = elem.jsonObject
                runCatching {
                    PrecomputedModelOutput(
                        questionId = obj["question_id"]?.jsonPrimitive?.int
                            ?: (obj["id"]?.jsonPrimitive?.int ?: return@mapNotNull null),
                        question = obj["question"]?.jsonPrimitive?.content ?: return@mapNotNull null,
                        options = obj["options"]?.jsonArray?.map { it.jsonPrimitive.content }
                            ?: emptyList(),
                        answer = obj["answer"]?.jsonPrimitive?.content ?: "?",
                        answerIndex = obj["answer_index"]?.jsonPrimitive?.int ?: -1,
                        category = obj["category"]?.jsonPrimitive?.content ?: "unknown",
                        pred = obj["pred"]?.jsonPrimitive?.contentOrNull,
                        modelOutputs = obj["model_outputs"]?.jsonPrimitive?.content ?: ""
                    )
                }.getOrNull()
            }
        } catch (e: Exception) {
            log.warn("Parse error: ${e.message}")
            emptyList()
        }
    }
}