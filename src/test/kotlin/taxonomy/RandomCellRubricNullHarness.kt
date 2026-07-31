package taxonomy

import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import taxonomy.config.LLMProvider
import taxonomy.config.LlmProviderType
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.ModelEvalStore
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.operations.ArcTaxonomyLLMClient
import taxonomy.service.TaxonomyArenaService
import taxonomy.service.TaxonomyJudgeService
import taxonomy.utils.GenerationMonitor
import java.io.File

/**
 * RANDOM-CELL RUBRIC NULL (measurement only, zero assertions — excluded from `test`,
 * run with `gradlew randomCellRubrics`). MAKES REAL AZURE CALLS.
 *
 * Purpose: the null arm of docs/prereg_rubric_specificity.md. The treatment arm showed a
 * rubric shares more content vocabulary with its own leaf's queries than with other leaves'.
 * That is equally consistent with "coherent cells produce specific rubrics" and with
 * "induction on ANY cell produces a grab-bag that happens to echo its own inputs". The only
 * way to tell them apart is to induce on cells that are size-matched but incoherent.
 *
 * This harness is the missing entry point, not new machinery. Judge induction is driven
 * through the production `TaxonomyJudgeService.generateJudgeForNode`, exactly as the frozen
 * run drove it — same prompts, same 25-item batching, same held-out filter, same leakage
 * audit. The only thing that differs is where the node comes from: instead of a taxonomy
 * leaf it is a synthetic cell read from `build/rubric_null/cells.json`, written by
 * `tools/analysis/rubric_specificity_null.py prepare`.
 *
 * Why a synthetic cell rather than the existing RANDOMNULL_BASELINE snapshot: that shuffle
 * (scripts/generate_baselines.py) produces all 87 cells and is consumed for *ranking*, as a
 * pre-built snapshot loaded per-query. Re-pointing it at induction would mean 87 Azure
 * inductions where 13 answer the question, and it would require writing a new row into the
 * read-only snapshots.db. The sampling rule is the same one that script uses — sizes taken
 * from the real leaf distribution, members drawn from a shuffle of the construction corpus,
 * cells disjoint.
 *
 * Cells carry deliberately uninformative labels ("Cluster 01"). The induction prompt
 * interpolates the node label as the subdomain name, so a topical label would smuggle
 * coherence into the null, and the code's own null-label fallback ("General") would prompt
 * the model to write generic rules — biasing toward the predicted result. A bare cluster
 * index tells the model nothing in either direction.
 *
 * Embeddings are not used anywhere in induction (only rawText is), so the cells carry a
 * 1-dimensional placeholder vector.
 */
class RandomCellRubricNullHarness {

    @Serializable
    data class CellSpec(
        val id: String,
        val label: String,
        val size: Int,
        val queryIds: List<String> = emptyList(),
        val queries: List<String>
    )

    @Serializable
    data class CellFile(val frozenSnapshot: String, val seed: Int, val cells: List<CellSpec>)

    @Serializable
    data class InducedRubric(
        val id: String,
        val label: String,
        val cellSize: Int,
        val inductionCorpus: Int,
        val prompt: String? = null,
        val rubric: String? = null
    )

    private val json = Json { ignoreUnknownKeys = true; prettyPrint = true }

    /**
     * Credentials live in `.env` (git-ignored) with `config/application.yml` as the fallback
     * Spring would normally read. This harness boots no Spring context — wiring five beans by
     * hand is cheaper and cannot start the TUI by accident — so it resolves them itself.
     */
    private fun resolve(vararg envKeys: String, ymlKey: String): String {
        for (k in envKeys) System.getenv(k)?.takeIf { it.isNotBlank() }?.let { return it }
        val dotenv = File(".env")
        if (dotenv.exists()) {
            for (line in dotenv.readLines()) {
                val t = line.trim()
                if (t.startsWith("#") || "=" !in t) continue
                val (k, v) = t.split("=", limit = 2)
                if (k.trim() in envKeys && v.isNotBlank()) return v.trim().trim('"')
            }
        }
        val yml = File("config/application.yml")
        if (yml.exists()) {
            for (line in yml.readLines()) {
                val t = line.trim()
                if (t.startsWith("$ymlKey:")) {
                    val v = t.substringAfter(":").trim().trim('"')
                    if (v.isNotBlank() && !v.startsWith("\${")) return v
                }
            }
        }
        error("could not resolve ${envKeys.joinToString("/")} from environment, .env or config/application.yml")
    }

    private fun azureConfig(): TaxonomyConfig = TaxonomyConfig().apply {
        // Selects the `mmlu_pro` table in MMLUDatasetFetcher.getTableName(). The default is
        // AG_NEWS, which silently resolves zero question details and produces zero rubrics.
        dataset.datasetType = taxonomy.config.DatasetType.MMLU_PRO
        llm.provider = LlmProviderType.AZURE
        llm.judgeModel = "Mistral-Large-3"
        llm.judgeDomains = emptyList()      // no domain gate: synthetic cells sit under no domain
        llm.azure.endpoint = resolve("AZURE_AI_ENDPOINT", ymlKey = "endpoint")
        llm.azure.apiKey = resolve("AZURE_AI_API_KEY", ymlKey = "api-key")
        llm.azure.deploymentName = "Mistral-Large-3"
        llm.azure.apiVersion = "2024-02-15-preview"
        execution.llmParallelism = 4
    }

    @Test
    fun induceRubricsOnRandomCells() = runBlocking {
        val cellsFile = File("build/rubric_null/cells.json")
        require(cellsFile.exists()) {
            "build/rubric_null/cells.json missing — run: " +
                "python tools/analysis/rubric_specificity_null.py prepare"
        }
        val spec = json.decodeFromString<CellFile>(cellsFile.readText())
        println("[NULL-ARM] ${spec.cells.size} random cells from ${spec.frozenSnapshot} (seed ${spec.seed})")

        // -DrubricNullDryRun=true exercises the whole path (cell build, corpus resolution,
        // held-out filter, batching, JSON parse, file write) without spending Azure calls.
        val dryRun = System.getProperty("rubricNullDryRun") == "true"
        val config = azureConfig()
        val monitor = GenerationMonitor()
        val provider = object : LLMProvider {   // unused on the Azure path; required by the ctor
            override suspend fun completePrompt(agentName: String, prompt: String) =
                error("not used")
        }
        val llmClient = if (dryRun) StubLlmClient() else ArcTaxonomyLLMClient(
            provider, "http://localhost:11434", "unused", 8192, 4, 5.0, monitor, config
        )
        val outFile = File(if (dryRun) "build/rubric_null/rubrics_dryrun.json" else "build/rubric_null/rubrics.json")
        val fetcher = MMLUDatasetFetcher(config, "")
        val evalStore = ModelEvalStore()
        val arena = Mockito.mock(TaxonomyArenaService::class.java)
        val judge = TaxonomyJudgeService(fetcher, llmClient, config, arena, evalStore)

        val out = mutableListOf<InducedRubric>()
        for ((i, cell) in spec.cells.withIndex()) {
            val node = GraphNode(id = cell.id, label = cell.label, depth = 1)
            cell.queries.forEach { text ->
                node.queries.add(Embedding(text, text, FloatArray(1)))
            }
            // Same visibility the service applies: it drops abs(rawText.hashCode()) % 5 == 0
            // and any held-out question. Reported so the batch count per cell is auditable.
            val visible = cell.queries.count { Math.abs(it.hashCode()) % 5 != 0 }
            println("[NULL-ARM] ${i + 1}/${spec.cells.size} ${cell.id} '${cell.label}' " +
                "size=${cell.size} visible=$visible")

            val t0 = System.currentTimeMillis()
            try {
                judge.generateJudgeForNode(node)
            } catch (t: Throwable) {
                println("[NULL-ARM] ${cell.id} FAILED: ${t.message}")
            }
            val secs = (System.currentTimeMillis() - t0) / 1000.0
            println("[NULL-ARM] ${cell.id} -> rubric=${node.judgeRubric?.split(" ")?.size ?: 0} words " +
                "in ${"%.1f".format(secs)}s")

            out.add(
                InducedRubric(
                    id = cell.id, label = cell.label, cellSize = cell.size,
                    inductionCorpus = visible,
                    prompt = node.judgePrompt, rubric = node.judgeRubric
                )
            )
            outFile.writeText(json.encodeToString(kotlinx.serialization.builtins.ListSerializer(InducedRubric.serializer()), out))
        }

        val ok = out.count { it.rubric != null }
        println("[NULL-ARM] done: $ok/${out.size} rubrics induced -> ${outFile.path}")
    }

    /** Dry-run stand-in: a syntactically valid judge JSON, no network. */
    private class StubLlmClient : taxonomy.operations.TaxonomyLlmClient {
        var calls = 0
        override suspend fun generateClusterLabel(prompt: String) = "stub"
        override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String {
            calls++
            return """{"system_prompt":"stub judge for a dry run","rubric":"- stub criterion one\n- stub criterion two"}"""
        }
        override suspend fun queryModelStructured(
            modelName: String, systemPrompt: String?, userPrompt: String, schema: JsonSchema
        ): String = "{}"
        override fun setMaxParallel(limit: Int) {}
    }
}
