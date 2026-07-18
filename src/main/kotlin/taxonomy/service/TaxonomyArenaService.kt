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
import taxonomy.prompts.GenericPairwiseJudgePrompt
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.dataset.ModelEvalStore
import taxonomy.model.BenchmarkLiveStats
import taxonomy.model.BenchmarkReport
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.projectTo
import taxonomy.service.TaxonomyRankingService.AggregatedLeaderboard
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
    val tieSource: String? = null,
    val winAFirst: Double = 0.5,
    val winASecond: Double = 0.5
) {
    val domainLabel: String get() = domain
}

data class ParseResult(
    val winner: String,
    val rationale: String,
    val confidence: Double,
    val impliesNoWinner: Boolean
)

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
    val isRunningBenchmark: Boolean = false,
    val nodeLeaderboard: AggregatedLeaderboard? = null,
    val isLoadingLeaderboard: Boolean = false,
    val benchmarkLiveStats: taxonomy.model.BenchmarkLiveStats? = null
)

@Service
class TaxonomyArenaService(
    private val config: TaxonomyConfig,
    private val taxonomyService: TaxonomyService,
    val llmClient: TaxonomyLlmClient,
    val embeddingCache: EmbeddingCache,
    val ops: TaxonomyOperations,
    private val evalStore: ModelEvalStore,
    val rankingService: TaxonomyRankingService,
) {
    fun setNodeLeaderboard(leaderboard: AggregatedLeaderboard?) {
        _state.update { it.copy(nodeLeaderboard = leaderboard) }
    }

    fun setNodeLeaderboardLoading(loading: Boolean) {
        _state.update { it.copy(isLoadingLeaderboard = loading) }
    }

    fun getLeaderboardForNode(
        node: GraphNode,
        allNodes: List<GraphNode>,
        snapshotId: String
    ): AggregatedLeaderboard {
        return if (node.isLeaf) {
            // Leaf: direct BT state — no aggregation needed
            val state = rankingService.getBtState(node.id, snapshotId)
            val ranks = rankingService.getNodeLeaderboard(node.id, snapshotId) ?: emptyList()
            val comps = state?.totalComparisons ?: 0
            AggregatedLeaderboard(
                ranks = ranks,
                leafsEligible = if (comps > 0) 1 else 0,
                leafsTotal = 1,
                totalComparisons = comps,
                isReliable = comps >= 5
            )
        } else {
            // Internal node or root: aggregate all leaves in this subtree
            val leafIds = mutableListOf<String>()
            val visited = mutableSetOf<String>()
            fun walk(n: GraphNode) {
                if (!visited.add(n.id)) return
                if (n.isLeaf) leafIds.add(n.id)
                else n.children.forEach { walk(it) }
            }
            walk(node)
            rankingService.aggregateLeafScores(leafIds, snapshotId)
        }
    }
    private val judgeSchema = JsonSchema.builder()
        .name("JudgeResponse")
        .rootElement(
            JsonObjectSchema.builder()
                .addStringProperty("critique_a", "Critique of Model A's response against the rubric")
                .addStringProperty("critique_b", "Critique of Model B's response against the rubric")
                .addStringProperty("comparison", "The decisive difference in reasoning quality between A and B")
                .addStringProperty("winner", "Model A, Model B, or TIE")
                .addNumberProperty("confidence", "0.0 to 1.0")
                .required("comparison", "winner", "confidence")
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
    fun getLeaderboard(domain: String = "global"): List<LeaderboardGroup> {
        val snapshotId = taxonomyService.activeSnapshotId() ?: "global"
        val root = taxonomyService.getGraph()
        val ranks = if (root != null) {
            val allNodes = mutableListOf<GraphNode>()
            val visited = mutableSetOf<String>()
            fun walk(n: GraphNode) {
                if (!visited.add(n.id)) return
                allNodes.add(n)
                n.children.forEach { walk(it) }
            }
            walk(root)
            getLeaderboardForNode(root, allNodes, snapshotId).ranks
        } else {
            emptyList()
        }

        if (ranks.isNotEmpty()) {
            return ranks.map { mr ->
                LeaderboardGroup(
                    rank = mr.rank,
                    agents = listOf(
                        AgentRating(
                            agentName = mr.modelId,
                            domain = domain,
                            mu = mr.btScore,
                            sigma = mr.stdError
                        )
                    )
                )
            }
        }
        return emptyList()
    }

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
            benchmarkReport = null,
            benchmarkLiveStats = null
        ) }
    }

    fun updateBenchmarkProgress(progress: String) {
        _state.update { it.copy(benchmarkProgress = progress) }
    }

    fun updateBenchmarkLiveStats(stats: BenchmarkLiveStats) {
        _state.update { it.copy(benchmarkLiveStats = stats) }
    }

    fun completeBenchmark(report: BenchmarkReport) {
        _state.update { it.copy(
            isRunningBenchmark = false,
            benchmarkProgress = "Benchmark completed successfully!",
            benchmarkReport = report,
            benchmarkLiveStats = null
        ) }
    }

    fun setBenchmarkReport(report: BenchmarkReport?) {
        _state.update { it.copy(benchmarkReport = report) }
    }

    suspend fun compareModels(query: String, modelA: String, modelB: String): ArenaResult = coroutineScope {
        _state.value = AnalysisPanelState(mode = AnalysisMode.ARENA, query = query, modelA = modelA, modelB = modelB)

        val leaves = routeToLeaves(query)
        val judges = leaves.mapNotNull { leafJudge(it) }
        if (judges.isEmpty()) {
            return@coroutineScope ArenaResult(query, modelA, modelB, "", "", emptyList())
        }

        val initialStatus = leaves.associate { node ->
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

    fun extractAnswerLetter(trace: String): String {
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
    }    // NEW: Pure routing — finds the leaf node(s) for a query.
    // Returns empty if the query is an outlier (no leaf match). Discard it — done.
    suspend fun routeToLeaves(
        text: String,
        frozenLeafIds: Set<String>? = null,
        category: String? = null
    ): List<GraphNode> {
        val root = taxonomyService.getGraph() ?: return emptyList()
        val vector = embeddingCache.getOrCreate(text)
        val emb = Embedding(text, text, vector, category ?: "")
        // routeQuery already walks the DAG and returns the best-fit leaves
        return ops.routeQuery(emb, root, currentIteration = 2, originalCategories = category?.let { listOf(it) })
            .keys
            .filter { node ->
                if (frozenLeafIds != null) node.id in frozenLeafIds
                else node.isLeaf   // live check only for non-benchmark use
            }
    }

    // NEW: Given a leaf node, return it as judge if it has a prompt. Null = discard.
    fun leafJudge(node: GraphNode): GraphNode? =
        if (node.judgePrompt != null) node else null

    private suspend fun evaluatePairwise(
        node: GraphNode,
        query: String,
        nameA: String,
        nameB: String,
        traceA: String,
        traceB: String,
        condition: String = "MAIN"
    ): DomainEvaluation = coroutineScope {
        require(!query.contains("Ground Truth Answer")) {
            "Information leakage: prompt contains the ground truth answer!"
        }

        val isC5 = condition.equals("C5", ignoreCase = true) || condition.equals("GENERIC_PAIRV2", ignoreCase = true)
        val res1: ParseResult
        val res2: ParseResult

        if (isC5) {
            val systemPrompt = GenericPairwiseJudgePrompt.SYSTEM_PROMPT
            
            val userPrompt1 = GenericPairwiseJudgePrompt.USER_TEMPLATE
                .replace("{question}", query)
                .replace("{answer_a}", traceA)
                .replace("{answer_b}", traceB)
            
            val userPrompt2 = GenericPairwiseJudgePrompt.USER_TEMPLATE
                .replace("{question}", query)
                .replace("{answer_a}", traceB)
                .replace("{answer_b}", traceA)

            val p1Raw = async { llmClient.queryModel(config.llm.judgeModel, systemPrompt, userPrompt1) }
            val p2Raw = async { llmClient.queryModel(config.llm.judgeModel, systemPrompt, userPrompt2) }

            val p1Text = p1Raw.await()
            val p2Text = p2Raw.await()

            fun parseVerbatim(text: String): ParseResult {
                val winner = when {
                    text.contains("[[A]]") -> "Model A"
                    text.contains("[[B]]") -> "Model B"
                    text.contains("[[C]]") -> "TIE"
                    else -> "INVALID"
                }
                val explanation = text.substringBefore("[[").trim()
                return ParseResult(winner, explanation, if (winner == "INVALID") 0.0 else 0.85, winner == "TIE")
            }

            res1 = parseVerbatim(p1Text)
            res2 = parseVerbatim(p2Text)
        } else {
            val p1 = async { llmClient.queryModelStructured(config.llm.judgeModel, buildJudgeSystemPrompt(node, condition), buildJudgeUserPrompt(query, traceA, traceB), judgeSchema) }
            val p2 = async { llmClient.queryModelStructured(config.llm.judgeModel, buildJudgeSystemPrompt(node, condition), buildJudgeUserPrompt(query, traceB, traceA), judgeSchema) }

            res1 = parseJudgeResponse(p1.await())
            res2 = parseJudgeResponse(p2.await())
        }

        val vote1 = res1.winner
        val vote2 = when (res2.winner) {
            "Model A" -> "Model B"
            "Model B" -> "Model A"
            else -> res2.winner
        }
        val c1 = res1.confidence
        val c2 = res2.confidence
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

        val impliesNoWinner = res1.impliesNoWinner || res2.impliesNoWinner
        val tieSource = when {
            winner != "TIE" -> null
            positionFlip -> "POSITION_FLIP"
            impliesNoWinner -> "SEMANTIC_OVERRIDE"
            else -> "JUDGE_EMITTED"
        }

        val rationale = if (isInvalid) {
            "Invalid judge response. Trial 1: ${res1.winner} (rationale: ${res1.rationale}). Trial 2: ${res2.winner} (rationale: ${res2.rationale})."
        } else if (positionFlip) {
            "POSITION_FLIP_TIE: Split verdict (position flip). Trial 1 voted $vote1 (conf $c1). Trial 2 voted $vote2 (conf $c2)."
        } else {
            if (winner == "Model A") res1.rationale else if (winner == "Model B") res2.rationale else "Consistent tie verdict"
        }

        val finalConfidence = if (positionFlip) 0.5 else avgConfidence.coerceIn(0.0, 0.95)
        val winAFirst = if (res1.winner == "Model A") 1.0 else if (res1.winner == "Model B") 0.0 else 0.5
        val winASecond = if (res2.winner == "Model B") 1.0 else if (res2.winner == "Model A") 0.0 else 0.5

        DomainEvaluation(
            domain      = node.label ?: "Emergent Concept",
            winner      = winner,           // "Model A", "Model B", or "TIE"
            rationale   = rationale,
            confidence  = finalConfidence,
            positionFlip = positionFlip,
            nodeId       = node.id,
            tieSource    = tieSource,
            winAFirst    = winAFirst,
            winASecond   = winASecond
        )
    }

    suspend fun evaluateWithPrecomputedTraces(
        query: String,
        options: List<String>,
        modelA: String,
        traceA: String,
        modelB: String,
        traceB: String,
        expectedNodeId: String? = null,
        frozenLeafIds: Set<String>? = null,
        gtAnswer: String? = null,
        assignedLeafIds: List<String>? = null,
        condition: String = "MAIN",
        isCorrectA: Boolean? = null,
        isCorrectB: Boolean? = null
    ): List<DomainEvaluation> = coroutineScope {
        val leaves = if (assignedLeafIds != null) {
            val root = taxonomyService.getGraph()
            if (root != null) {
                val leafNodes = mutableListOf<GraphNode>()
                fun collect(node: GraphNode) {
                    if (node.id in assignedLeafIds) {
                        leafNodes.add(node)
                    }
                    node.children.forEach { collect(it) }
                    node.crossLinkChildren.forEach { collect(it) }
                }
                collect(root)
                leafNodes.distinctBy { it.id }
            } else {
                emptyList()
            }
        } else {
            routeToLeaves(query, frozenLeafIds)
        }
        if (expectedNodeId != null && leaves.none { it.id == expectedNodeId }) {
            log.info("Routing discrepancy: query \"${query.take(30)}...\" routed to leaves ${leaves.map { it.label ?: it.id }} but expected leaf $expectedNodeId")
        }
        val judges = leaves.mapNotNull { leafJudge(it) }
        if (traceA.isBlank() || traceB.isBlank()) {
            log.warn("Empty trace for query=\"${query.take(30)}...\" model=$modelA/$modelB")
        }
        if (judges.isEmpty()) return@coroutineScope emptyList()

        if (condition.equals("CANONICAL", ignoreCase = true)) {
            val winnerName = when {
                isCorrectA == true && isCorrectB == false -> "Model A"
                isCorrectB == true && isCorrectA == false -> "Model B"
                else -> "TIE"
            }
            return@coroutineScope judges.map { node ->
                DomainEvaluation(
                    domain = node.label ?: node.id,
                    winner = winnerName,
                    rationale = "Oracle Comparison (Canonical). CorrectA=$isCorrectA, CorrectB=$isCorrectB.",
                    confidence = 1.0,
                    positionFlip = false,
                    nodeId = node.id,
                    tieSource = if (winnerName == "TIE") "CANONICAL_TIE" else null,
                    winAFirst = if (winnerName == "Model A") 1.0 else if (winnerName == "Model B") 0.0 else 0.5,
                    winASecond = if (winnerName == "Model A") 1.0 else if (winnerName == "Model B") 0.0 else 0.5
                )
            }
        }

        // Build the MCQ context for judge prompts (question + options visible)
        val optionsBlock = options.mapIndexed { i, opt -> "${('A' + i)}) $opt" }.joinToString("\n")
        val questionWithOptions = buildString {
            append("$query\n\nOptions:\n$optionsBlock")
        }

        judges.map { node ->
            async {
                evaluatePairwise(node, questionWithOptions, modelA, modelB, traceA, traceB, condition)
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
            traceB = resB.modelOutput,
            gtAnswer = resA.gtAnswer
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

    private fun sanitizeJsonString(jsonStr: String): String {
        val sb = StringBuilder()
        var i = 0
        val len = jsonStr.length
        while (i < len) {
            val c = jsonStr[i]
            if (c == '\\') {
                if (i + 1 < len) {
                    val next = jsonStr[i + 1]
                    val isValidEscape = next == '"' || next == '\\' || next == '/' || 
                                        next == 'b' || next == 'f' || next == 'n' || 
                                        next == 'r' || next == 't' ||
                                        (next == 'u' && i + 5 < len && jsonStr.substring(i + 2, i + 6).all { it.isDigit() || it.lowercaseChar() in 'a'..'f' })
                    if (isValidEscape) {
                        sb.append(c)
                        sb.append(next)
                        i += 2
                        continue
                    }
                }
                sb.append("\\\\")
                i++
            } else {
                sb.append(c)
                i++
            }
        }
        return sb.toString()
    }

    private fun parseJudgeResponse(response: String): ParseResult {
        var cleanWinner = "INVALID"
        var confidence = 0.0
        var comparisonText = ""
        var impliesNoWinner = false
        var parsedSuccessfully = false
        val cleanJson = response.trim()

        try {
            val extracted = if (cleanJson.contains("```json")) {
                cleanJson.substringAfter("```json").substringBefore("```").trim()
            } else {
                val firstBrace = cleanJson.indexOf('{')
                val lastBrace = cleanJson.lastIndexOf('}')
                if (firstBrace != -1 && lastBrace != -1 && lastBrace > firstBrace) {
                    cleanJson.substring(firstBrace, lastBrace + 1)
                } else {
                    cleanJson
                }
            }
            val sanitized = sanitizeJsonString(extracted)
            val element = json.parseToJsonElement(sanitized).jsonObject
            val rawWinner = element["winner"]?.jsonPrimitive?.content?.trim() ?: "INVALID"
            cleanWinner = when (rawWinner.uppercase()) {
                "MODEL A" -> "Model A"
                "MODEL B" -> "Model B"
                "TIE", "DRAW", "EQUAL" -> "TIE"
                else -> "INVALID"
            }
            confidence = element["confidence"]?.jsonPrimitive?.doubleOrNull ?: 0.0
            comparisonText = element["comparison"]?.jsonPrimitive?.content 
                ?: element["rationale"]?.jsonPrimitive?.content 
                ?: element["critique_a"]?.jsonPrimitive?.content 
                ?: ""
            impliesNoWinner = confidence <= 0.5 && cleanWinner == "TIE"
            parsedSuccessfully = true
        } catch (e: Exception) {
            log.debug("Standard JSON parsing failed: ${e.message}. Falling back to regex extraction...")
        }

        // If JSON parsing failed, use robust regex fallback
        if (!parsedSuccessfully) {
            try {
                // Regex to find "winner" value
                val winnerRegex = """"(?:winner)"\s*:\s*"([^"]+)"""".toRegex(RegexOption.IGNORE_CASE)
                val winnerMatch = winnerRegex.find(cleanJson)
                val rawWinner = winnerMatch?.groupValues?.get(1)?.trim() ?: "INVALID"
                cleanWinner = when (rawWinner.uppercase()) {
                    "MODEL A" -> "Model A"
                    "MODEL B" -> "Model B"
                    "TIE", "DRAW", "EQUAL" -> "TIE"
                    else -> "INVALID"
                }

                // Regex to find "confidence" value
                val confidenceRegex = """"(?:confidence)"\s*:\s*([0-9.]+)""".toRegex(RegexOption.IGNORE_CASE)
                val confidenceMatch = confidenceRegex.find(cleanJson)
                confidence = confidenceMatch?.groupValues?.get(1)?.toDoubleOrNull() ?: 0.0

                // Regex to find comparison/rationale
                val comparisonRegex = """"(?:comparison|rationale|critique)"\s*:\s*"([^"]+)"""".toRegex(RegexOption.IGNORE_CASE)
                val comparisonMatch = comparisonRegex.find(cleanJson)
                comparisonText = comparisonMatch?.groupValues?.get(1) ?: ""

                impliesNoWinner = confidence <= 0.5 && cleanWinner == "TIE"
                
                log.info("Regex fallback succeeded: winner=$cleanWinner confidence=$confidence")
                parsedSuccessfully = true
            } catch (ex: Exception) {
                log.warn("Regex fallback also failed: ${ex.message}")
            }
        }

        if (!parsedSuccessfully) {
            val preview = response.replace("\n", " ").replace("\r", " ").trim().take(150)
            log.warn("Failed to parse judge response: JSON & Regex extraction failed (preview: '$preview...')")
            return ParseResult("INVALID", response, 0.0, false)
        }

        val finalWinner = cleanWinner
        val finalConfidence = confidence
        val finalComparison = if (comparisonText.isNotBlank()) comparisonText else response

        log.debug("Judge parsed: winner=$finalWinner conf=${"%.2f".format(finalConfidence)}")
        log.trace("Judge raw response: $cleanJson")
        return ParseResult(finalWinner, finalComparison, finalConfidence, impliesNoWinner)
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

    private fun buildJudgeSystemPrompt(node: GraphNode, condition: String = "MAIN"): String {
        val useGeneric = condition.equals("GENERIC_JUDGE", ignoreCase = true)
        val isC3 = condition.equals("C3", ignoreCase = true)
        val systemPrompt = if (useGeneric) {
            "You are an expert academic evaluator. Analyze the two responses and grade them based on overall correctness and reasoning quality."
        } else {
            node.judgePrompt ?: "You are an expert academic evaluator in the domain: ${node.label ?: "General Science"}."
        }
        val rubric = if (useGeneric || isC3) {
            "Grade the response based on domain correctness, precision, and logical reasoning."
        } else {
            node.judgeRubric ?: "Grade the response based on domain correctness, precision, and logical reasoning."
        }

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
4. DECIDE: declare the winner — either "Model A", "Model B", or "TIE".

For responses where BOTH models give factually correct answers:
You MUST still choose the better model. A tie is only valid when responses are 
word-for-word equivalent OR when one model's single factual error exactly 
cancels the other model's structural advantage and you cannot determine a net winner.

Ranking criteria when both are correct (apply in order):
1. Mechanistic depth — prefer the response explaining the underlying mechanism, not just the result
2. Edge-case handling — prefer the response that addresses boundary conditions or exceptions  
3. Quantitative precision — prefer the response with correctly applied formulas/numbers
4. Scope accuracy — prefer the response that correctly scopes uncertainty

Reserve TIE for: identical responses, or responses where criterion 1–4 are all equal.
Reserve confidence 0.95–1.0 only for cases with overwhelming evidence. Default to 0.7–0.85 for clear wins.

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
If the ground truth answer is provided, use it to assess factual correctness. Your task is to determine
superior reasoning quality based solely on the logical rigour and domain soundness of its response.

If both models are genuinely equivalent, output winner: "TIE" with confidence ≤ 0.5.

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
  "winner": "Model A, Model B, or TIE",
  "confidence": <0.0 to 1.0 (default to 0.7-0.85 for clear wins, reserve 0.95-1.0 only for overwhelming evidence)>
}""".trimIndent()
    }
}
