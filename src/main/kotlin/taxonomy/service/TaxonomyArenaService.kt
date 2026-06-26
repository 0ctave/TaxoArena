package taxonomy.service

import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.*
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.model.BenchmarkReport
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomyOperations
import kotlin.math.abs

@Serializable
data class ArenaResult(
    val query: String,
    val modelA: String,
    val modelB: String,
    val traceA: String,
    val traceB: String,
    val domainEvaluations: List<DomainEvaluation>
)

@Serializable
data class DomainEvaluation(
    val domainLabel: String,
    val winner: String,
    val rationale: String,
    val confidence: Double
)

enum class AnalysisMode { IDLE, ARENA, JUDGE_PROGRESS, NODE_DETAIL, SETTINGS, LOGS_SCROLL, METRICS, SNAPSHOTS, TRICKLE_TEST, BENCHMARK }

data class JudgeProgress(
    val nodeLabel: String,
    val processed: Int,
    val total: Int,
    val status: String = "INDUCTING"
)

data class AnalysisPanelState(
    val mode: AnalysisMode = AnalysisMode.IDLE,
    // Arena Data
    val query: String? = null,
    val modelA: String? = null,
    val modelB: String? = null,
    val domainStatus: Map<String, String> = emptyMap(),
    // Judge Progress Data
    val currentInductions: Map<String, JudgeProgress> = emptyMap(),
    // Node Detail Data
    val selectedNode: GraphNode? = null,
    // Benchmark Data
    val benchmarkReport: BenchmarkReport? = null,
    val benchmarkProgress: String = "",
    val isRunningBenchmark: Boolean = false
)

@Service
class TaxonomyArenaService(
    private val config: TaxonomyConfig,
    private val taxonomyService: TaxonomyService,
    private val llmClient: TaxonomyLlmClient,
    private val embeddingCache: EmbeddingCache,
    private val ops: TaxonomyOperations,
) {
    private val log = LoggerFactory.getLogger("ArenaService")
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }

    private val _state = MutableStateFlow(AnalysisPanelState())
    val state: StateFlow<AnalysisPanelState> = _state.asStateFlow()

    fun setMode(mode: AnalysisMode) {
        _state.value = _state.value.copy(mode = mode)
    }

    fun inspectNode(node: GraphNode?) {
        _state.value = _state.value.copy(mode = AnalysisMode.NODE_DETAIL, selectedNode = node)
    }

    fun updateJudgeProgress(label: String, processed: Int, total: Int, status: String = "INDUCTING") {
        val current = _state.value
        val newProgress = current.currentInductions.toMutableMap().apply {
            put(label, JudgeProgress(label, processed, total, status))
        }
        _state.value = current.copy(mode = AnalysisMode.JUDGE_PROGRESS, currentInductions = newProgress)
    }

    fun startBenchmark(progress: String) {
        val current = _state.value
        _state.value = current.copy(
            mode = AnalysisMode.BENCHMARK,
            isRunningBenchmark = true,
            benchmarkProgress = progress,
            benchmarkReport = null
        )
    }

    fun updateBenchmarkProgress(progress: String) {
        val current = _state.value
        _state.value = current.copy(
            benchmarkProgress = progress
        )
    }

    fun completeBenchmark(report: BenchmarkReport) {
        val current = _state.value
        _state.value = current.copy(
            isRunningBenchmark = false,
            benchmarkProgress = "Benchmark completed successfully!",
            benchmarkReport = report
        )
    }

    fun setBenchmarkReport(report: BenchmarkReport?) {
        _state.value = _state.value.copy(benchmarkReport = report)
    }

    suspend fun compareModels(query: String, modelA: String, modelB: String): ArenaResult = coroutineScope {
        _state.value = AnalysisPanelState(mode = AnalysisMode.ARENA, query = query, modelA = modelA, modelB = modelB)

        val discoveryJob = async { discoverDomainsAndJudges(query) }
        val (allMatches, judges) = discoveryJob.await()
        
        val initialStatus = allMatches.associate { node ->
            (node.label ?: node.id.toString()) to (if (node.judgePrompt != null) "PENDING" else "NO JUDGE")
        }
        _state.value = _state.value.copy(domainStatus = initialStatus)

        val traceAJob = async { llmClient.queryModel(modelA, null, query) }
        val traceBJob = async { llmClient.queryModel(modelB, null, query) }
        val traceA = traceAJob.await()
        val traceB = traceBJob.await()

        val evaluations = judges.map { node ->
            async {
                val label = node.label ?: node.id.toString()
                updateArenaDomainStatus(label, "JUDGING")
                val eval = evaluatePairwise(node, query, modelA, modelB, traceA, traceB)
                updateArenaDomainStatus(label, eval.winner)
                eval
            }
        }.awaitAll()

        ArenaResult(query, modelA, modelB, traceA, traceB, evaluations)
    }

    /**
     * Runs one arena match and extracts the model's chosen answer letter (A-J)
     * from its reasoning trace for GT comparison.
     */
    suspend fun compareModelsWithAnswerExtraction(
        query: String,
        options: List<String>,
        modelA: String,
        modelB: String
    ): Pair<ArenaResult, Map<String, String>> = coroutineScope {

        // Build the MCQ prompt — show options so models can answer, not just reason
        val optionsBlock = options.mapIndexed { i, opt ->
            "${('A' + i)}) $opt"
        }.joinToString("\n")
        val mcqPrompt = "$query\n\nOptions:\n$optionsBlock\n\nAnswer with the letter of the correct option and explain your reasoning."

        // Run arena with the structured MCQ prompt
        val arenaResult = compareModels(mcqPrompt, modelA, modelB)

        // Extract answer letter from each trace (first capital letter A-J after "answer" keyword, or first standalone letter)
        val answers = mapOf(
            modelA to extractAnswerLetter(arenaResult.traceA),
            modelB to extractAnswerLetter(arenaResult.traceB)
        )

        arenaResult to answers
    }

    private fun extractAnswerLetter(trace: String): String {
        // 1. Try "answer is X", "answer: X", "= X", "choice X" patterns
        val explicit = Regex(
            """(?i)(?:answer\s*(?:is|:|\s)\s*|the\s+correct\s+(?:answer|option)\s*(?:is|:)?\s*)([A-Ja-j])\b"""
        ).find(trace)?.groupValues?.get(1)?.uppercase()
        if (explicit != null) return explicit

        // 2. Try "**A**" or "(A)" or "A." at start of a line
        val formatted = Regex("""(?m)^\s*[\(\[*]*([A-Ja-j])[\)\]*.:]\s""").find(trace)
            ?.groupValues?.get(1)?.uppercase()
        if (formatted != null) return formatted

        // 3. Last resort: final standalone capital letter in last 100 chars
        val tail = trace.takeLast(100)
        val last = Regex("""\b([A-J])\b""").findAll(tail).lastOrNull()?.groupValues?.get(1)
        return last ?: "?"
    }

    private fun updateArenaDomainStatus(label: String, status: String) {
        val current = _state.value
        _state.value = current.copy(
            domainStatus = current.domainStatus.toMutableMap().apply { put(label, status) }
        )
    }

    private suspend fun discoverDomainsAndJudges(text: String): Pair<List<GraphNode>, List<GraphNode>> {
        val root = taxonomyService.getGraph() ?: return emptyList<GraphNode>() to emptyList()
        val vector = embeddingCache.getOrCreate(text)
        val emb = Embedding(text, text, vector)
        val results = ops.routeQuery(emb, root, currentIteration = 2)
        val allMatchedNodes = mutableSetOf<GraphNode>()
        val judges = mutableSetOf<GraphNode>()
        fun collectLineage(node: GraphNode, visited: MutableSet<String>) {
            if (!visited.add(node.id)) return
            allMatchedNodes.add(node)
            if (node.judgePrompt != null) judges.add(node)
            node.parents.forEach { collectLineage(it, visited) }
        }
        val visited = mutableSetOf<String>()
        results.keys.forEach { collectLineage(it, visited) }
        return allMatchedNodes.toList() to judges
            .distinctBy { it.id }
            .sortedByDescending { it.depth }
    }

    private suspend fun evaluatePairwise(node: GraphNode, query: String, nameA: String, nameB: String, traceA: String, traceB: String): DomainEvaluation = coroutineScope {
        val sys = node.judgePrompt!!
        val rub = formatRubricForPrompt(node.judgeRubric!!)
        val p1 = async { llmClient.queryModel(config.llm.judgeModel, sys, buildJudgeUserPrompt(query, rub, nameA, nameB, traceA, traceB)) }
        val p2 = async { llmClient.queryModel(config.llm.judgeModel, sys, buildJudgeUserPrompt(query, rub, nameB, nameA, traceB, traceA)) }
        val res1 = parseJudgeResponse(p1.await())
        val res2 = parseJudgeResponse(p2.await())
        val winner = when {
            res1.first == "Model A" && res2.first == "Model B" -> "Model A"
            res1.first == "Model B" && res2.first == "Model A" -> "Model B"
            else -> "Tie"
        }
        val c1 = res1.third
        val c2 = res2.third
        val correctedConf = if (winner != "Tie") {
            (c1 + c2) / 2.0
        } else {
            1.0 - abs(c1 - c2) / 2.0
        }
        val rationale = when (winner) {
            "Model A" -> res1.second  // res1 said A won — use its rationale
            "Model B" -> res2.second  // res2 said A lost → B won
            else -> "Split verdict: ${res1.second.take(120)} / ${res2.second.take(120)}"
        }
        DomainEvaluation(node.label ?: "Emergent Concept", winner, rationale, correctedConf)
    }

    suspend fun evaluateWithPrecomputedTraces(
        query: String,
        options: List<String>,
        modelA: String,
        traceA: String,
        modelB: String,
        traceB: String
    ): List<DomainEvaluation> = coroutineScope {
        // Route the question to find relevant leaf judges
        val (_, judges) = discoverDomainsAndJudges(query)

        if (judges.isEmpty()) return@coroutineScope emptyList()

        // Build the MCQ context for judge prompts (question + options visible)
        val optionsBlock = options.mapIndexed { i, opt -> "${('A' + i)}) $opt" }.joinToString("\n")
        val questionWithOptions = "$query\n\nOptions:\n$optionsBlock"

        judges.map { node ->
            async {
                evaluatePairwise(node, questionWithOptions, modelA, modelB, traceA, traceB)
            }
        }.awaitAll()
    }

    private fun parseJudgeResponse(response: String): Triple<String, String, Double> {
        return try {
            val cleanJson = if (response.contains("```json")) response.substringAfter("```json").substringBefore("```").trim() 
            else if (response.contains("{")) "{" + response.substringAfter("{").substringBeforeLast("}") + "}"
            else response
            val element = json.parseToJsonElement(cleanJson).jsonObject
            Triple(element["winner"]?.jsonPrimitive?.content ?: "Tie", element["rationale"]?.jsonPrimitive?.content ?: response, element["confidence"]?.jsonPrimitive?.doubleOrNull ?: 0.5)
        } catch (e: Exception) { Triple("Tie", response, 0.5) }
    }

    private fun formatRubricForPrompt(rubricJson: String): String {
        return try {
            val element = json.parseToJsonElement(rubricJson).jsonObject
            val criteriaList = element["criteria"]?.jsonArray?.map { c ->
                val obj = c.jsonObject
                "- **${obj["name"]?.jsonPrimitive?.content ?: "Criterion"}** (weight ${obj["weight"]?.jsonPrimitive?.doubleOrNull ?: 1.0}): ${obj["description"]?.jsonPrimitive?.content ?: ""}"
            }?.joinToString("\n") ?: ""
            val failureList = element["failure_modes"]?.jsonArray?.map { f ->
                "- ${f.jsonPrimitive.content}"
            }?.joinToString("\n") ?: ""
            
            buildString {
                appendLine("## Evaluation Criteria")
                appendLine(criteriaList)
                if (failureList.isNotEmpty()) {
                    appendLine("\n## Automatic Failure Modes")
                    appendLine(failureList)
                }
            }
        } catch (e: Exception) {
            rubricJson
        }
    }

    private fun buildJudgeUserPrompt(query: String, rubric: String, nameA: String, nameB: String, traceA: String, traceB: String) = """
        Evaluate responses for the query: "$query"
        
        $rubric
        
        <trace_model_a>
        $traceA
        </trace_model_a>
        
        <trace_model_b>
        $traceB
        </trace_model_b>
        
        Respond ONLY with a JSON object: { "winner": "Model A" | "Model B" | "Tie", "rationale": "...", "confidence": 0.95 }
    """.trimIndent()
}
