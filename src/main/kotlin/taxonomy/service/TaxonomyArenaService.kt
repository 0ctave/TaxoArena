package taxonomy.service

import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.*
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.dataset.ModelEvalStore
import taxonomy.model.BenchmarkReport
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.projectTo
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomyOperations
import kotlin.math.abs
import dev.langchain4j.model.chat.request.json.JsonSchema
import dev.langchain4j.model.chat.request.json.JsonObjectSchema

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
    val domain: String,
    val winner: String,        // "Model A", "Model B", or "TIE"
    val rationale: String,
    val confidence: Double,
    val positionFlip: Boolean = false,
    val nodeId: String? = null,
) {
    val domainLabel: String get() = domain
}

enum class AnalysisMode { IDLE, ARENA, JUDGE_PROGRESS, NODE_DETAIL, SETTINGS, LOGS_SCROLL, METRICS, SNAPSHOTS, TRICKLE_TEST, BENCHMARK, CONFIG, LEADERBOARD }

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
    val embeddingCache: EmbeddingCache,
    val ops: TaxonomyOperations,
    private val evalStore: ModelEvalStore,
    private val rankingService: TaxonomyRankingService,
) {
    private val judgeSchema = JsonSchema.builder()
        .name("JudgeResponse")
        .rootElement(
            JsonObjectSchema.builder()
                .addStringProperty("winner", "The winner: Model A or Model B")
                .addStringProperty("rationale", "Detailed reasoning explaining why the winner was chosen")
                .addNumberProperty("confidence", "A confidence score between 0.0 and 1.0")
                .required("winner", "rationale", "confidence")
                .build()
        )
        .build()

    private val log = LoggerFactory.getLogger("taxonomy.ArenaService")
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }

    private val _state = MutableStateFlow(AnalysisPanelState())
    val state: StateFlow<AnalysisPanelState> = _state.asStateFlow()

    fun setMode(mode: AnalysisMode) {
        _state.update { it.copy(mode = mode) }
    }

    /** Passthrough to the ranking service so the TUI gateway can render the Arena leaderboard. */
    fun getLeaderboard(domain: String = "global"): List<LeaderboardGroup> =
        rankingService.getLeaderboard(domain, taxonomyService.activeSnapshotId() ?: "global")

    fun clearLeaderboard() {
        val snapshotId = taxonomyService.activeSnapshotId() ?: "global"
        rankingService.clearRatings(snapshotId)
    }

    fun inspectNode(node: GraphNode?) {
        _state.update { it.copy(mode = AnalysisMode.NODE_DETAIL, selectedNode = node) }
    }

    // Bug 3 fix: use MutableStateFlow.update{} (CAS loop) instead of the bare read-copy-write
    // pattern.  generateJudgesForDag launches multiple async coroutines in the same chunk that
    // all call updateJudgeProgress concurrently.  The old pattern:
    //
    //   val current = _state.value          // read
    //   val newMap  = current.currentInductions.toMutableMap().apply { put(...) }
    //   _state.value = current.copy(...)    // write
    //
    // is NOT atomic: two coroutines can both read the same "current", each add their own entry,
    // and then the second write overwrites the first — one node's progress is silently lost.
    // update{} retries the lambda until it wins the CAS, so concurrent callers are all serialised.
    fun updateJudgeProgress(label: String, processed: Int, total: Int, status: String = "INDUCTING") {
        _state.update { current ->
            current.copy(
                mode = AnalysisMode.JUDGE_PROGRESS,
                currentInductions = current.currentInductions + (label to JudgeProgress(label, processed, total, status))
            )
        }
    }

    fun clearJudgeProgress() {
        _state.update { it.copy(currentInductions = emptyMap()) }
    }

    fun startBenchmark(progress: String) {
        _state.update { it.copy(
            mode = AnalysisMode.BENCHMARK,
            isRunningBenchmark = true,
            benchmarkProgress = progress,
            benchmarkReport = null
        ) }
    }

    fun updateBenchmarkProgress(progress: String) {
        _state.update { it.copy(benchmarkProgress = progress) }
    }

    fun completeBenchmark(report: BenchmarkReport) {
        _state.update { it.copy(
            isRunningBenchmark = false,
            benchmarkProgress = "Benchmark completed successfully!",
            benchmarkReport = report
        ) }
    }

    fun setBenchmarkReport(report: BenchmarkReport?) {
        _state.update { it.copy(benchmarkReport = report) }
    }

    suspend fun compareModels(query: String, modelA: String, modelB: String): ArenaResult = coroutineScope {
        _state.value = AnalysisPanelState(mode = AnalysisMode.ARENA, query = query, modelA = modelA, modelB = modelB)

        val discoveryJob = async { discoverDomainsAndJudges(query) }
        val (allMatches, judges) = discoveryJob.await()
        
        val initialStatus = allMatches.associate { node ->
            (node.label ?: node.id) to (if (node.judgePrompt != null) "PENDING" else "NO JUDGE")
        }
        _state.update { it.copy(domainStatus = initialStatus) }

        val traceAJob = async { llmClient.queryModel(modelA, null, query) }
        val traceBJob = async { llmClient.queryModel(modelB, null, query) }
        val traceA = traceAJob.await()
        val traceB = traceBJob.await()

        val evaluations = judges.map { node ->
            async {
                val label = node.label ?: node.id
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
        _state.update { current ->
            current.copy(
                domainStatus = current.domainStatus + (label to status)
            )
        }
    }

    private fun cosineSimilarity(a: DoubleArray, b: FloatArray): Double {
        if (a.isEmpty() || b.isEmpty() || a.size != b.size) return 0.0
        var dot = 0.0
        var normA = 0.0
        var normB = 0.0
        for (i in a.indices) {
            dot += a[i] * b[i]
            normA += a[i] * a[i]
            normB += b[i] * b[i]
        }
        if (normA <= 0.0 || normB <= 0.0) return 0.0
        return dot / (Math.sqrt(normA) * Math.sqrt(normB))
    }

    suspend fun discoverDomainsAndJudges(text: String): Pair<List<GraphNode>, List<GraphNode>> {
        val root = taxonomyService.getGraph() ?: return emptyList<GraphNode>() to emptyList()
        val vector = embeddingCache.getOrCreate(text)
        val emb = Embedding(text, text, vector)
        val results = ops.routeQuery(emb, root, currentIteration = 2)

        val candidates = results.keys.filter { node ->
            if (node.vmfMu.isEmpty()) {
                true
            } else {
                val slicedX = emb.projectTo(node.sliceDim)
                val sim = cosineSimilarity(slicedX, node.vmfMu)
                log.info("DEBUG: Node routing similarity for '${node.label ?: node.id}': $sim")
                sim >= 0.65
            }
        }

        val allMatchedNodes = mutableSetOf<GraphNode>()
        val judges = mutableSetOf<GraphNode>()
        fun collectLineage(node: GraphNode, visited: MutableSet<String>) {
            if (!visited.add(node.id)) return
            allMatchedNodes.add(node)
            if (node.judgePrompt != null || node.isLeaf) judges.add(node)
            node.parents.forEach { collectLineage(it, visited) }
        }
        val visited = mutableSetOf<String>()
        candidates.forEach { collectLineage(it, visited) }
        return allMatchedNodes.toList() to judges
            .distinctBy { it.id }
            .sortedByDescending { it.depth }
    }

    private suspend fun evaluatePairwise(
        node: GraphNode,
        query: String,
        nameA: String,
        nameB: String,
        traceA: String,
        traceB: String,
    ): DomainEvaluation = coroutineScope {

        val p1 = async { llmClient.queryModelStructured(config.llm.judgeModel, buildJudgeSystemPrompt(node), buildJudgeUserPrompt(query, traceA, traceB), judgeSchema) }
        val p2 = async { llmClient.queryModelStructured(config.llm.judgeModel, buildJudgeSystemPrompt(node), buildJudgeUserPrompt(query, traceB, traceA), judgeSchema) }

        val res1 = parseJudgeResponse(p1.await())
        val res2 = parseJudgeResponse(p2.await())

        val vote1 = res1.first
        val vote2 = when (res2.first) {
            "Model A" -> "Model B"
            "Model B" -> "Model A"
            else -> res2.first
        }
        val c1 = res1.third
        val c2 = res2.third
        val avgConfidence = (c1 + c2) / 2.0

        val isInvalid = vote1 == "INVALID" || vote2 == "INVALID"
        val positionFlip = !isInvalid && vote1 != vote2

        val winner = if (isInvalid) {
            "INVALID"
        } else if (positionFlip) {
            "TIE"
        } else {
            vote1
        }

        val rationale = if (isInvalid) {
            "Invalid judge response. Trial 1: ${res1.first} (rationale: ${res1.second}). Trial 2: ${res2.first} (rationale: ${res2.second})."
        } else if (positionFlip) {
            "POSITION_FLIP_TIE: Split verdict (position flip). Trial 1 voted $vote1 (conf $c1). Trial 2 voted $vote2 (conf $c2)."
        } else {
            if (winner == "Model A") res1.second else if (winner == "Model B") res2.second else "Consistent tie verdict"
        }

        val finalConfidence = if (positionFlip) avgConfidence * 0.5 else avgConfidence

        DomainEvaluation(
            domain      = node.label ?: "Emergent Concept",
            winner      = winner,           // "Model A", "Model B", or "TIE"
            rationale   = rationale,
            confidence  = finalConfidence,
            positionFlip = positionFlip,
            nodeId       = node.id
        )
    }

    private fun findNodeById(root: GraphNode, targetId: String, visited: MutableSet<String> = mutableSetOf()): GraphNode? {
        if (root.id == targetId) return root
        if (!visited.add(root.id)) return null
        for (child in root.children) {
            val found = findNodeById(child, targetId, visited)
            if (found != null) return found
        }
        for (child in root.crossLinkChildren) {
            val found = findNodeById(child, targetId, visited)
            if (found != null) return found
        }
        return null
    }

    suspend fun evaluateWithPrecomputedTraces(
        query: String,
        options: List<String>,
        modelA: String,
        traceA: String,
        modelB: String,
        traceB: String,
        targetNodeId: String? = null
    ): List<DomainEvaluation> = coroutineScope {
        // Route the question to find relevant leaf judges
        val root = taxonomyService.getGraph() ?: return@coroutineScope emptyList()
        val (_, judgesList) = discoverDomainsAndJudges(query)
        val judges = judgesList.toMutableList()
        if (targetNodeId != null) {
            val targetNode = findNodeById(root, targetNodeId)
            if (targetNode != null && judges.none { it.id == targetNode.id }) {
                judges.add(targetNode)
            }
        }
        log.info("DEBUG: discoverDomainsAndJudges returned ${judges.size} judges for query: \"${query.take(50)}...\"")
        log.info("DEBUG trace lengths: traceA=${traceA.length} traceB=${traceB.length} | traceA[:100]=${traceA.take(100).replace("\n", " ")} | traceB[:100]=${traceB.take(100).replace("\n", " ")}")
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

    /**
     * Precomputed-answers Arena: fetch each model's stored MMLU-Pro trajectory for the
     * given question_id, route the query embedding to its leaf judges, and evaluate the
     * two precomputed answers WITHOUT any live generation. Optionally aggregates the
     * verdicts into the Bradley-Terry ranking (TaxonomyRankingService).
     */
    suspend fun compareModelsPrecomputed(
        questionId: Int,
        modelA: String,
        modelB: String,
        confidenceGate: Double = 0.65,
        updateRankings: Boolean = true
    ): ArenaResult = coroutineScope {
        val resA = evalStore.getResult(modelA, questionId)
        val resB = evalStore.getResult(modelB, questionId)

        if (resA == null || resB == null) {
            val missing = listOfNotNull(
                modelA.takeIf { resA == null },
                modelB.takeIf { resB == null }
            ).joinToString(", ")
            log.warn("Precomputed arena: missing outputs for q#$questionId ($missing)")
            _state.value = AnalysisPanelState(
                mode = AnalysisMode.ARENA,
                query = "q#$questionId",
                modelA = modelA,
                modelB = modelB,
                domainStatus = mapOf("(no judge)" to "Missing precomputed output: $missing")
            )
            return@coroutineScope ArenaResult(
                "q#$questionId", modelA, modelB,
                resA?.modelOutput ?: "", resB?.modelOutput ?: "", emptyList()
            )
        }

        val query = resA.questionText
        _state.value = AnalysisPanelState(
            mode = AnalysisMode.ARENA, query = query, modelA = modelA, modelB = modelB
        )

        val evaluations = evaluateWithPrecomputedTraces(
            query = query,
            options = resA.options,
            modelA = modelA,
            traceA = resA.modelOutput,
            modelB = modelB,
            traceB = resB.modelOutput
        )

        _state.update { it.copy(
            domainStatus = evaluations.associate { (it.domain) to it.winner }
        ) }

        if (updateRankings) {
            evaluations.filter { it.confidence >= confidenceGate }.forEach { eval ->
                val isTie = eval.winner.equals("TIE", ignoreCase = true) || eval.winner.equals("Tie", ignoreCase = true)
                val isModelB = eval.winner.equals("Model B", ignoreCase = true)
                val winner = if (isModelB) modelB else modelA
                val loser = if (isModelB) modelA else modelB
                rankingService.recordMatch(
                    query = query,
                    domain = eval.domain,
                    winner = if (isTie) modelA else winner,
                    loser = if (isTie) modelB else loser,
                    isTie = isTie,
                    confidence = eval.confidence,
                    snapshotId = taxonomyService.activeSnapshotId() ?: "global"
                )
            }
        }

        ArenaResult(query, modelA, modelB, resA.modelOutput, resB.modelOutput, evaluations)
    }

    private fun parseJudgeResponse(response: String): Triple<String, String, Double> {
        return try {
            val cleanJson = response.trim()
            val element = try {
                json.parseToJsonElement(cleanJson).jsonObject
            } catch (e: Exception) {
                val extracted = if (response.contains("```json")) {
                    response.substringAfter("```json").substringBefore("```").trim()
                } else {
                    val firstBrace = response.indexOf('{')
                    val lastBrace = response.lastIndexOf('}')
                    if (firstBrace != -1 && lastBrace != -1 && lastBrace > firstBrace) {
                        response.substring(firstBrace, lastBrace + 1)
                    } else {
                        response
                    }
                }
                json.parseToJsonElement(extracted).jsonObject
            }
            val rawWinner = element["winner"]?.jsonPrimitive?.content?.trim() ?: "INVALID"
            val cleanWinner = when (rawWinner.uppercase()) {
                "MODEL A" -> "Model A"
                "MODEL B" -> "Model B"
                else -> "INVALID"
            }
            val confidence = element["confidence"]?.jsonPrimitive?.doubleOrNull ?: 0.0
            log.info("DEBUG: parseJudgeResponse parsed winner=$cleanWinner, confidence=$confidence from response: $cleanJson")
            Triple(
                cleanWinner,
                element["rationale"]?.jsonPrimitive?.content ?: element["comparison"]?.jsonPrimitive?.content ?: response,
                confidence
            )
        } catch (e: Exception) { 
            log.warn("Failed to parse judge response: ${e.message}. Raw response was: $response", e)
            Triple("INVALID", response, 0.0) 
        }
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

    private fun buildJudgeSystemPrompt(node: GraphNode): String {
        val systemPrompt = node.judgePrompt ?: "You are an expert academic evaluator in the domain: ${node.label ?: "General Science"}."
        val rubric = node.judgeRubric ?: "Grade the response based on domain correctness, precision, and logical reasoning."

        return """$systemPrompt

────────────────────────────────────────
EVALUATION MECHANICS (non-negotiable)
────────────────────────────────────────
Bias suppression — ignore completely:
• Response length, verbosity, or token count
• Formatting: markdown, LaTeX, bullet points, plain prose — all equal
• Model name, model family, or any identity signal
• Stylistic elegance or fluency unrelated to correctness

Evaluation order — follow exactly:
1. CRITIQUE Model A: assess its reasoning against the rubric. Identify correct steps, errors, gaps.
2. CRITIQUE Model B: same process, independently of Model A.
3. COMPARE: identify the decisive difference between A and B.
4. DECIDE: declare one winner — see tie-break rules below.

Tie-break rules — you MUST output "Model A" or "Model B". Never "tie", "draw", or "equal":
• If both reach the correct conclusion → prefer the one with more rigorous intermediate steps.
• If both are incorrect → prefer the one with fewer conceptual errors and closer partial reasoning.
• If still indistinguishable → apply in order:
  (a) correctness of the final selected option,
  (b) fewer logical fallacies,
  (c) better alignment with CRITICAL-importance axioms.

Your rubric:
$rubric
""".trimIndent()
    }

    private fun buildJudgeUserPrompt(query: String, traceA: String, traceB: String): String {
        return """[Question]
$query

[Model A's Response]
$traceA

[Model B's Response]
$traceB

────────────────────────────────────────
You do not have access to the correct answer. Your task is to determine which model demonstrates
superior reasoning quality based solely on the logical rigour and domain soundness of its response.

You MUST compare both models and choose a winner. Ties are strictly forbidden.

Evaluate following the mandatory sequence:

Step 1 — Critique Model A (2–4 sentences referencing your rubric)
Step 2 — Critique Model B (2–4 sentences referencing your rubric)
Step 3 — Compare: what is the decisive difference in reasoning quality?
Step 4 — Verdict

Output ONLY the following JSON. No prose before or after. No markdown fences.

{
  "critique_a": "<your critique of Model A>",
  "critique_b": "<your critique of Model B>",
  "comparison": "<decisive difference in reasoning quality>",
  "winner": "Model A or Model B",
  "confidence": <0.0 to 1.0>
}""".trimIndent()
    }
}
