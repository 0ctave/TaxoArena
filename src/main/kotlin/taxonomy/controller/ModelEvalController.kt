package taxonomy.arena

import kotlinx.coroutines.runBlocking
import kotlinx.serialization.Serializable
import org.springframework.web.bind.annotation.*
import taxonomy.dataset.EvalLoadStats
import taxonomy.dataset.ModelEvalLoader
import taxonomy.dataset.ModelEvalStore
import java.io.File

@RestController
@RequestMapping("/api/taxonomy/eval")
class ModelEvalController(
    private val loader: ModelEvalLoader,
    private val store: ModelEvalStore
) {

    @Serializable
    data class LoadRequest(
        val modelName: String,
        val zipPath: String? = null,
        val dirPath: String? = null
    )

    @Serializable
    data class LoadResponse(
        val stats: EvalLoadStats,
        val totalModels: List<String>
    )

    /** Load one model's eval zip or directory into the DB. */
    @PostMapping("/load")
    suspend fun loadModel(@RequestBody req: LoadRequest): LoadResponse {
        require(req.zipPath != null || req.dirPath != null) { "Provide zipPath or dirPath" }
        val stats = when {
            req.zipPath != null -> loader.loadFromZip(req.zipPath, req.modelName)
            else -> loader.loadFromDirectory(req.dirPath!!, req.modelName)
        }
        return LoadResponse(stats = stats, totalModels = store.getLoadedModels())
    }

    /** Sync the is_reserved flag from reserved_test_queries.json. Call once after all models loaded. */
    @PostMapping("/sync-reserved")
    fun syncReserved(
        @RequestParam(defaultValue = "reserved_test_queries.json") path: String
    ): Map<String, Any> {
        loader.syncReservedPool(File(path))
        return store.getStats()
    }

    /** Summary of what's in the DB. */
    @GetMapping("/stats")
    fun stats(): Map<String, Any> = store.getStats()

    /** List all loaded model names. */
    @GetMapping("/models")
    fun models(): List<String> = store.getLoadedModels()

    /**
     * Returns count of benchmark-ready questions:
     * reserved + has embedding + all requested models have an answer.
     */
    @GetMapping("/ready")
    fun readyCount(@RequestParam models: List<String>): Map<String, Any> {
        val ids = store.getLinkedReservedQuestionIds(models)
        return mapOf("readyQuestions" to ids.size, "models" to models)
    }
}