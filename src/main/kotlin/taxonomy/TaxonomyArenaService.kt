package org.eclipse.lmos.arc.app.taxonomy

import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.*
import org.eclipse.lmos.arc.app.taxonomy.operations.TaxonomyLlmClient
import org.eclipse.lmos.arc.app.MMLUDatasetFetcher
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.TaxoPrompts

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

enum class MissionControlMode { IDLE, ARENA, JUDGE_PROGRESS, NODE_DETAIL }

data class JudgeProgress(
    val nodeLabel: String,
    val processed: Int,
    val total: Int,
    val status: String = "INDUCTING"
)

data class MissionControlState(
    val mode: MissionControlMode = MissionControlMode.IDLE,
    // Arena Data
    val query: String? = null,
    val modelA: String? = null,
    val modelB: String? = null,
    val domainStatus: Map<String, String> = emptyMap(),
    // Judge Progress Data
    val currentInductions: Map<String, JudgeProgress> = emptyMap(),
    // Node Detail Data
    val selectedNode: GraphNode? = null
)

@Service
class TaxonomyArenaService(
    private val config: TaxonomyConfig,
    private val taxonomyService: TaxonomyService,
    private val llmClient: TaxonomyLlmClient,
    private val embeddingCache: EmbeddingCache,
    private val ops: TaxonomyOperations,
    private val distillationCache: org.eclipse.lmos.arc.app.taxonomy.operations.DistillationCache,
    private val datasetFetcher: MMLUDatasetFetcher
) {
    private val log = LoggerFactory.getLogger(TaxonomyArenaService::class.java)
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }

    private val _state = MutableStateFlow(MissionControlState())
    val state: StateFlow<MissionControlState> = _state.asStateFlow()

    fun setMode(mode: MissionControlMode) {
        _state.value = _state.value.copy(mode = mode)
    }

    fun inspectNode(node: GraphNode?) {
        _state.value = _state.value.copy(mode = MissionControlMode.NODE_DETAIL, selectedNode = node)
    }

    fun updateJudgeProgress(label: String, processed: Int, total: Int, status: String = "INDUCTING") {
        val current = _state.value
        val newProgress = current.currentInductions.toMutableMap().apply {
            put(label, JudgeProgress(label, processed, total, status))
        }
        _state.value = current.copy(mode = MissionControlMode.JUDGE_PROGRESS, currentInductions = newProgress)
    }

    suspend fun compareModels(query: String, modelA: String, modelB: String): ArenaResult = coroutineScope {
        _state.value = MissionControlState(mode = MissionControlMode.ARENA, query = query, modelA = modelA, modelB = modelB)

        val discoveryJob = async { discoverDomainsAndJudges(query) }
        val (allMatches, judges) = discoveryJob.await()
        
        val initialStatus = allMatches.associate { node ->
            node.label to (if (node.judgePrompt != null) "PENDING" else "NO JUDGE")
        }
        _state.value = _state.value.copy(domainStatus = initialStatus)

        val traceAJob = async { llmClient.queryModel(modelA, null, query) }
        val traceBJob = async { llmClient.queryModel(modelB, null, query) }
        val traceA = traceAJob.await()
        val traceB = traceBJob.await()

        val evaluations = judges.map { node ->
            async {
                updateArenaDomainStatus(node.label, "JUDGING")
                val eval = evaluatePairwise(node, query, modelA, modelB, traceA, traceB)
                updateArenaDomainStatus(node.label, eval.winner)
                eval
            }
        }.awaitAll()

        ArenaResult(query, modelA, modelB, traceA, traceB, evaluations)
    }

    private fun updateArenaDomainStatus(label: String, status: String) {
        val current = _state.value
        _state.value = current.copy(
            domainStatus = current.domainStatus.toMutableMap().apply { put(label, status) }
        )
    }

    private suspend fun discoverDomainsAndJudges(text: String): Pair<List<GraphNode>, List<GraphNode>> {
        val root = taxonomyService.getGraph() ?: return emptyList<GraphNode>() to emptyList()
        val distilled = if (config.enableDistillation) {
            distillationCache.get(text, "arena") ?: run {
                val prompt = TaxoPrompts.getDistillationPrompt(text, "General")
                val result = llmClient.distillQuery(prompt)
                if (result.isNotBlank()) {
                    distillationCache.put(text, "arena", result)
                    result
                } else text
            }
        } else text
        val vector = embeddingCache.getOrCreate(distilled)
        val emb = Embedding(text, distilled, vector)
        val results = mutableMapOf<GraphNode, Double>()
        ops.trickleQuery(emb, root, results)
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
        return allMatchedNodes.toList() to judges.toList().sortedByDescending { it.depth }
    }

    private suspend fun evaluatePairwise(node: GraphNode, query: String, nameA: String, nameB: String, traceA: String, traceB: String): DomainEvaluation = coroutineScope {
        val sys = node.judgePrompt!!
        val rub = node.judgeRubric!!
        val p1 = async { llmClient.queryModel(config.judgeModel, sys, buildJudgeUserPrompt(query, rub, nameA, nameB, traceA, traceB)) }
        val p2 = async { llmClient.queryModel(config.judgeModel, sys, buildJudgeUserPrompt(query, rub, nameB, nameA, traceB, traceA)) }
        val res1 = parseJudgeResponse(p1.await())
        val res2 = parseJudgeResponse(p2.await())
        val winner = when {
            res1.first == "Model A" && res2.first == "Model B" -> "Model A"
            res1.first == "Model B" && res2.first == "Model A" -> "Model B"
            else -> "Tie"
        }
        DomainEvaluation(node.label, winner, "Consensus reached.", (res1.third + res2.third) / 2.0)
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

    private fun buildJudgeUserPrompt(query: String, rubric: String, nameA: String, nameB: String, traceA: String, traceB: String) = """
        Evaluate "$query"
        Rubric: $rubric
        Trace A ($nameA): $traceA
        Trace B ($nameB): $traceB
        Return JSON { "winner": "Model A" | "Model B" | "Tie", "rationale": "...", "confidence": 0.95 }
    """.trimIndent()
}
