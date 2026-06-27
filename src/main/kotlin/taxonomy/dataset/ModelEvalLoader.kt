package taxonomy.dataset

import kotlinx.coroutines.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.*
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import java.io.File
import java.sql.DriverManager
import java.util.zip.ZipFile

/**
 * Raw shape of one item in a TIGER-AI-Lab eval result JSON file.
 * Fields follow the exact keys present in the upstream zips.
 */
@Serializable
private data class RawEvalItem(
    val question_id: Int = -1,
    val question: String = "",
    val options: List<String> = emptyList(),
    val answer: String = "",              // GT answer letter e.g. "A"
    val answer_index: Int = -1,
    val category: String = "",
    val pred: String? = null,             // model's extracted answer
    val model_outputs: String = "",       // full CoT trace
    // Some older eval files use cot_content instead of model_outputs
    val cot_content: String? = null
)

@Service
class ModelEvalLoader(
    private val store: ModelEvalStore,
    private val datasetFetcher: MMLUDatasetFetcher,   // for cross-referencing questions
    // Injectable so integration tests can point at throwaway DB/files. Defaults match prod.
    @Value("\${taxoadapt.eval.db-path:mmlu_pro_dataset_cache_v2.db}")
    private val datasetDbPath: String = "mmlu_pro_dataset_cache_v2.db",
    @Value("\${taxoadapt.eval.embedding-db-path:embeddings_cache.db}")
    private val embeddingDbPath: String = "embeddings_cache.db",
    @Value("\${taxoadapt.eval.reserved-file:reserved_test_queries.json}")
    private val reservedFilePath: String = "reserved_test_queries.json"
) {
    private val log = LoggerFactory.getLogger("taxonomy.ModelEvalLoader")
    private val json = Json { ignoreUnknownKeys = true; isLenient = true; coerceInputValues = true }
    private val datasetDbUrl = "jdbc:sqlite:$datasetDbPath?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000"
    private val embeddingDbUrl = "jdbc:sqlite:$embeddingDbPath?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000"

    // ─── Public API ───────────────────────────────────────────────────────────

    /**
     * Unified entry point: ingest a `.zip` (single inner json), a raw `.json`, or a
     * directory of per-category json files. Model name is derived from the filename
     * (`model_outputs_<MODEL>_<N>shots`) when not supplied.
     */
    suspend fun loadFromPath(
        path: String,
        modelName: String? = null,
        onProgress: ((current: Int, total: Int) -> Unit)? = null
    ): EvalLoadStats = withContext(Dispatchers.IO) {
        val resolved = modelName?.takeIf { it.isNotBlank() }
            ?: PrecomputedModelOutputLoader.deriveModelName(path)
        val file = File(path)
        val raw = when {
            file.isDirectory -> parseDirectory(path)
            path.endsWith(".zip") -> parseZip(path)
            path.endsWith(".json") -> parseJsonBytes(file.readBytes(), file.name)
            else -> {
                log.warn("Unsupported eval source: $path")
                emptyList()
            }
        }
        log.info("Loading eval results for '$resolved' from $path (${raw.size} raw items)")
        ingestRaw(raw, resolved, onProgress)
    }

    /**
     * Load all model results from a zip file produced by TIGER-AI-Lab eval scripts.
     * Resolves cross-links to mmlu_pro and embeddings_cache tables.
     * Idempotent — safe to call multiple times.
     */
    suspend fun loadFromZip(
        zipPath: String,
        modelName: String,
        onProgress: ((current: Int, total: Int) -> Unit)? = null
    ): EvalLoadStats = withContext(Dispatchers.IO) {
        log.info("Loading eval results for '$modelName' from $zipPath")
        val raw = parseZip(zipPath)
        ingestRaw(raw, modelName, onProgress)
    }

    /**
     * Load from an already-extracted directory of per-category JSON files.
     */
    suspend fun loadFromDirectory(
        dirPath: String,
        modelName: String,
        onProgress: ((current: Int, total: Int) -> Unit)? = null
    ): EvalLoadStats = withContext(Dispatchers.IO) {
        log.info("Loading eval results for '$modelName' from directory $dirPath")
        val raw = parseDirectory(dirPath)
        ingestRaw(raw, modelName, onProgress)
    }

    /**
     * After all models are loaded, syncs the is_reserved flag using the
     * reserved_test_queries.json produced by MMLUDatasetFetcher.splitTrainTest().
     * Must be called once after initial loads — subsequent loads check the link table.
     */
    fun syncReservedPool(reservedQueriesJson: File = File(reservedFilePath)) {
        if (!reservedQueriesJson.exists()) {
            log.warn("reserved_test_queries.json not found — skipping reserved sync")
            return
        }
        val reservedMap: Map<String, List<String>> = json.decodeFromString(reservedQueriesJson.readText())
        val reservedTexts = reservedMap.values.flatten().toSet()
        log.info("Syncing reserved pool: ${reservedTexts.size} reserved question texts")

        // Resolve question texts to question_ids via the link table
        val reservedIds = mutableSetOf<Int>()
        DriverManager.getConnection(datasetDbUrl).use { c ->
            reservedTexts.chunked(900).forEach { chunk ->
                val placeholders = chunk.joinToString(",") { "?" }
                c.prepareStatement(
                    "SELECT question_id FROM eval_question_link WHERE question_text IN ($placeholders)"
                ).use { ps ->
                    chunk.forEachIndexed { i, t -> ps.setString(i + 1, t) }
                    val rs = ps.executeQuery()
                    while (rs.next()) reservedIds.add(rs.getInt(1))
                }
            }
        }
        store.markReserved(reservedIds)
        log.info("Reserved sync complete: ${reservedIds.size} question_ids marked.")
    }

    // ─── Parsing ──────────────────────────────────────────────────────────────

    private fun parseZip(zipPath: String): List<RawEvalItem> {
        val items = mutableListOf<RawEvalItem>()
        ZipFile(zipPath).use { zip ->
            zip.entries().asSequence()
                .filter { !it.isDirectory && it.name.endsWith(".json") }
                .forEach { entry ->
                    zip.getInputStream(entry).use { stream ->
                        items += parseJsonBytes(stream.readBytes(), entry.name)
                    }
                }
        }
        log.info("Parsed ${items.size} raw items from zip $zipPath")
        return items
    }

    private fun parseDirectory(dirPath: String): List<RawEvalItem> {
        val items = mutableListOf<RawEvalItem>()
        File(dirPath).walkTopDown()
            .filter { it.isFile && it.extension == "json" }
            .forEach { file ->
                runCatching {
                    items += parseJsonBytes(file.readBytes(), file.name)
                }.onFailure { log.warn("Skipping ${file.name}: ${it.message}") }
            }
        log.info("Parsed ${items.size} raw items from directory $dirPath")
        return items
    }

    private fun parseJsonBytes(bytes: ByteArray, sourceName: String): List<RawEvalItem> {
        val text = bytes.toString(Charsets.UTF_8)
        return try {
            // Files are a top-level JSON array
            json.decodeFromString<List<RawEvalItem>>(text)
        } catch (e: Exception) {
            log.warn("Failed to parse $sourceName as array: ${e.message}")
            emptyList()
        }
    }

    // ─── Ingestion ────────────────────────────────────────────────────────────

    private fun ingestRaw(
        raw: List<RawEvalItem>,
        modelName: String,
        onProgress: ((Int, Int) -> Unit)?
    ): EvalLoadStats {
        val total = raw.size
        if (total == 0) return EvalLoadStats(modelName, 0, 0, 0, 0, 0, 0)

        // Build lookup maps for cross-referencing
        val questionTexts = raw.map { it.question }
        val mmlProRowIds  = fetchMmlProRowIds(questionTexts)   // question_text → mmlu_pro.id
        val embeddingHits = fetchEmbeddingHits(questionTexts)  // question_text → exists?

        // Load existing reserved pool for immediate marking
        val existingReservedTexts = loadReservedTextsFromFile()

        val results = mutableListOf<ModelEvalResult>()
        val links   = mutableListOf<EvalQuestionLink>()
        var errors  = 0

        raw.forEachIndexed { idx, item ->
            runCatching {
                if (item.question_id < 0 || item.question.isBlank()) return@runCatching

                val trace = item.model_outputs.ifBlank { item.cot_content ?: "" }
                val isCorrect = item.pred != null && item.pred == item.answer
                val isReserved = item.question in existingReservedTexts

                results += ModelEvalResult(
                    questionId   = item.question_id,
                    modelName    = modelName,
                    category     = item.category,
                    questionText = item.question,
                    options      = item.options,
                    gtAnswer     = item.answer,
                    pred         = item.pred,
                    modelOutput  = trace,
                    isCorrect    = isCorrect,
                    isReserved   = isReserved
                )

                links += EvalQuestionLink(
                    questionId    = item.question_id,
                    mmlProRowId   = mmlProRowIds[item.question],
                    questionText  = item.question,
                    hasEmbedding  = embeddingHits.contains(item.question)
                )
            }.onFailure {
                errors++
                log.warn("Error processing item ${item.question_id}: ${it.message}")
            }
            if (idx % 500 == 0) onProgress?.invoke(idx, total)
        }

        // Batch write
        val (inserted, skipped) = store.saveBatch(results)
        store.saveLinks(links.distinctBy { it.questionId })

        onProgress?.invoke(total, total)

        val stats = EvalLoadStats(
            modelName       = modelName,
            inserted        = inserted,
            skipped         = skipped,
            linkedToDataset = links.count { it.mmlProRowId != null },
            linkedToEmbedding = links.count { it.hasEmbedding },
            reservedCount   = results.count { it.isReserved },
            errors          = errors
        )
        log.info("Loaded '$modelName': $stats")
        return stats
    }

    // ─── Cross-reference helpers ──────────────────────────────────────────────

    /**
     * Queries mmlu_pro table to get the local row id for each question text.
     * Returns a map of question_text → mmlu_pro.id
     */
    private fun fetchMmlProRowIds(questions: List<String>): Map<String, Int> {
        val result = mutableMapOf<String, Int>()
        DriverManager.getConnection(datasetDbUrl).use { c ->
            questions.chunked(900).forEach { chunk ->
                val placeholders = chunk.joinToString(",") { "?" }
                c.prepareStatement(
                    "SELECT id, question FROM mmlu_pro WHERE question IN ($placeholders)"
                ).use { ps ->
                    chunk.forEachIndexed { i, q -> ps.setString(i + 1, q) }
                    val rs = ps.executeQuery()
                    while (rs.next()) result[rs.getString("question")] = rs.getInt("id")
                }
            }
        }
        return result
    }

    /**
     * Queries embeddings_cache.db to check which question texts already have an embedding.
     * Returns a set of question texts that are cached.
     */
    private fun fetchEmbeddingHits(questions: List<String>): Set<String> {
        val result = mutableSetOf<String>()
        try {
            DriverManager.getConnection(embeddingDbUrl).use { c ->
                questions.chunked(900).forEach { chunk ->
                    val placeholders = chunk.joinToString(",") { "?" }
                    c.prepareStatement(
                        "SELECT query FROM embeddings WHERE query IN ($placeholders)"
                    ).use { ps ->
                        chunk.forEachIndexed { i, q -> ps.setString(i + 1, q) }
                        val rs = ps.executeQuery()
                        while (rs.next()) result.add(rs.getString("query"))
                    }
                }
            }
        } catch (e: Exception) {
            log.warn("Could not check embeddings cache: ${e.message}")
        }
        return result
    }

    private fun loadReservedTextsFromFile(): Set<String> {
        val file = File(reservedFilePath)
        if (!file.exists()) return emptySet()
        return try {
            val map: Map<String, List<String>> = json.decodeFromString(file.readText())
            map.values.flatten().toSet()
        } catch (e: Exception) {
            log.warn("Could not parse reserved_test_queries.json: ${e.message}")
            emptySet()
        }
    }
}