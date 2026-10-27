package taxonomy.dataset

import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import java.io.File

/**
 * One ingestible eval source discovered in the eval_results cache directory: a single
 * `.zip`/`.json` file, or a per-category directory (`eval_results/<model>/`). [alreadyIngested]
 * reflects whether the derived model name is already present in [ModelEvalStore].
 */
data class EvalCatalogEntry(
    val modelName: String,
    val sourcePath: String,
    val sizeBytes: Long,
    val alreadyIngested: Boolean
)

/**
 * Scans the on-disk eval_results cache and reports the model sources available for ingestion,
 * WITHOUT parsing them. This lets the TUI download the whole cache once (cheap) but ingest only
 * the models the user actually picks (expensive), instead of parsing every file in the directory.
 */
@Service
class EvalCatalog(private val store: ModelEvalStore) {
    private val log = LoggerFactory.getLogger("taxonomy.EvalCatalog")

    fun scan(evalResultsDir: String): List<EvalCatalogEntry> {
        val dir = File(evalResultsDir)
        if (!dir.isDirectory) {
            log.warn("Eval results directory not found: '$evalResultsDir'")
            return emptyList()
        }
        val ingested = store.getLoadedModels().toSet()

        val entries = mutableListOf<EvalCatalogEntry>()
        dir.listFiles()?.sortedBy { it.name }?.forEach { f ->
            when {
                f.isFile && (f.name.endsWith(".zip") || f.name.endsWith(".json")) -> {
                    val model = PrecomputedModelOutputLoader.deriveModelName(f.name)
                    entries += EvalCatalogEntry(model, f.path, f.length(), model in ingested)
                }
                // A per-category directory of JSON files is one model.
                f.isDirectory -> {
                    val jsonFiles = f.walkTopDown().filter { it.isFile && it.extension == "json" }.toList()
                    if (jsonFiles.isNotEmpty()) {
                        val model = PrecomputedModelOutputLoader.deriveModelName(f.name)
                        entries += EvalCatalogEntry(model, f.path, jsonFiles.sumOf { it.length() }, model in ingested)
                    }
                }
            }
        }
        // Collapse duplicate model names (e.g. a stray .json next to its zip) — keep the first.
        val deduped = entries.distinctBy { it.modelName }
        log.info("Eval catalog scan of '$evalResultsDir': ${deduped.size} model source(s).")
        return deduped
    }
}
