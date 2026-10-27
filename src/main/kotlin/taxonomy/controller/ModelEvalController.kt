package taxonomy.controller

import kotlinx.serialization.Serializable
import org.springframework.web.bind.annotation.*
import taxonomy.dataset.EvalLoadStats
import taxonomy.dataset.ModelEvalLoader
import taxonomy.dataset.ModelEvalStore

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

    // /sync-reserved is gone: nothing activates a pool (FRAMEWORK item 18); pools are recorded
    // at split time and addressed by id.

    /** Summary of what's in the DB. */
    @GetMapping("/stats")
    fun stats(): Map<String, Any> = store.getStats()

    /** List all loaded model names. */
    @GetMapping("/models")
    fun models(): List<String> = store.getLoadedModels()

    /**
     * Returns count of benchmark-ready questions of [pool]:
     * in the pool + has embedding + all requested models have an answer.
     */
    @GetMapping("/ready")
    fun readyCount(@RequestParam models: List<String>, @RequestParam pool: String): Map<String, Any> {
        val ids = store.getLinkedReservedQuestionIds(models, pool)
        return mapOf("readyQuestions" to ids.size, "models" to models, "pool" to pool)
    }
}
