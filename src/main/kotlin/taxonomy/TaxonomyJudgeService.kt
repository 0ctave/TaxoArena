package org.eclipse.lmos.arc.app.taxonomy

import kotlinx.coroutines.*
import kotlinx.serialization.json.*
import org.eclipse.lmos.arc.app.MMLUDatasetFetcher
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.JudgePrompts

@Service
class TaxonomyJudgeService(
    private val datasetFetcher: MMLUDatasetFetcher,
    private val llmClient: org.eclipse.lmos.arc.app.taxonomy.operations.TaxonomyLlmClient,
    private val config: org.eclipse.lmos.arc.app.taxonomy.TaxonomyConfig,
    private val arenaService: TaxonomyArenaService
) {
    private val log = LoggerFactory.getLogger(TaxonomyJudgeService::class.java)
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }

    suspend fun generateJudgesForDag(root: GraphNode, replaceExisting: Boolean = false, maxGenerality: Int = config.llm.maxJudgeGenerality) = coroutineScope {
        log.info("Starting Grounded Agent Judge Induction (Replace: $replaceExisting, Max Generality: $maxGenerality)...")
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) { if (allNodes.add(n)) n.children.forEach { walk(it) } }
        walk(root)

        val nodeDistances = calculateDistancesFromLeaves(allNodes)
        val targetNodes = allNodes.filter { node ->
            val dist = nodeDistances[node.id] ?: 999
            dist <= maxGenerality && (replaceExisting || node.judgePrompt == null)
        }.sortedBy { nodeDistances[it.id] ?: 999 }

        if (targetNodes.isEmpty()) {
            log.info("No nodes require judge generation.")
            return@coroutineScope
        }

        targetNodes.chunked(3).forEach { chunk ->
            chunk.map { node -> async { generateJudgeForNode(node) } }.awaitAll()
        }
        log.info("Agent Judge induction complete.")
    }

    suspend fun generateJudgeForNodeById(root: GraphNode, nodeId: String) {
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) { if (allNodes.add(n)) n.children.forEach { walk(it) } }
        walk(root)
        
        val node = allNodes.find { it.id == nodeId } ?: throw IllegalArgumentException("Node $nodeId not found")
        generateJudgeForNode(node)
    }

    private fun calculateDistancesFromLeaves(allNodes: Set<GraphNode>): Map<String, Int> {
        val distances = mutableMapOf<String, Int>()
        fun getMinDist(node: GraphNode): Int {
            if (node.isLeaf) return 0
            if (distances.containsKey(node.id)) return distances[node.id]!!
            val d = node.children.map { getMinDist(it) }.minOrNull()?.plus(1) ?: 1
            distances[node.id] = d
            return d
        }
        allNodes.forEach { getMinDist(it) }
        return distances
    }

    suspend fun generateJudgeForNode(node: GraphNode) {
        val corpusEmbeddings = node.getAllQueriesInBranch()
        val details = corpusEmbeddings.mapNotNull { datasetFetcher.getDetailsForQuery(it.rawText) }

        if (details.isEmpty()) return

        val chunks = details.chunked(25)
        val chunksCount = chunks.size
        val hasSynthesis = chunksCount > 1
        val finalSteps = chunksCount + (if (hasSynthesis) 1 else 0) + 1 // +1 for final judge synthesis
        var currentStep = 0

        // PROGRESS TRACKING START
        arenaService.updateJudgeProgress(node.label, currentStep, finalSteps, "BATCHING")

        val partialGuidelines = chunks.mapIndexed { index, batch ->
            val corpusStrings = batch.map { item ->
                val answerIndex = item.answer?.firstOrNull()?.let { it.uppercaseChar() - 'A' } ?: -1
                val correctChoiceText = if (answerIndex in item.options.indices) item.options[answerIndex] else "Unknown"
                "Q: ${item.question} | A: ${item.answer} ($correctChoiceText)"
            }
            val result = llmClient.queryModel(config.llm.judgeModel, null, JudgePrompts.induceBatchGuidelines(corpusStrings))
            
            // UPDATE PROGRESS
            currentStep = index + 1
            arenaService.updateJudgeProgress(node.label, currentStep, finalSteps, "INDUCTING")
            
            result
        }

        val masterGuidelines = if (chunksCount > 1) {
            arenaService.updateJudgeProgress(node.label, currentStep, finalSteps, "SYNTHESIZING")
            val res = llmClient.queryModel(config.llm.judgeModel, null, JudgePrompts.synthesizeGlobalGuidelines(partialGuidelines))
            currentStep = chunksCount + 1
            arenaService.updateJudgeProgress(node.label, currentStep, finalSteps, "SYNTHESIZING")
            res
        } else partialGuidelines.first()

        arenaService.updateJudgeProgress(node.label, currentStep, finalSteps, "FINALIZING")
        val rawSynthesis = llmClient.queryModel(config.llm.judgeModel, null, JudgePrompts.synthesizeFinalJudge(masterGuidelines))
        currentStep = finalSteps - 1
        arenaService.updateJudgeProgress(node.label, currentStep, finalSteps, "SAVING")
        
        if (validateAndSaveJudge(node, rawSynthesis)) {
            arenaService.updateJudgeProgress(node.label, finalSteps, finalSteps, "READY")
        } else {
            // PHASE 3: AUTOMATED REPAIR
            log.warn("Judge JSON for '${node.label}' is malformed. Attempting LLM repair...")
            val repairSteps = finalSteps + 1
            arenaService.updateJudgeProgress(node.label, finalSteps - 1, repairSteps, "REPAIRING")
            
            val repairedJson = llmClient.queryModel(config.llm.judgeModel, null, JudgePrompts.repairMalformedJson(rawSynthesis))
            currentStep = finalSteps
            arenaService.updateJudgeProgress(node.label, currentStep, repairSteps, "SAVING")
            
            if (validateAndSaveJudge(node, repairedJson)) {
                log.info("Successfully repaired judge JSON for '${node.label}'.")
                arenaService.updateJudgeProgress(node.label, repairSteps, repairSteps, "READY")
            } else {
                log.error("Failed to repair judge JSON for '${node.label}' after LLM assistance.")
                arenaService.updateJudgeProgress(node.label, repairSteps, repairSteps, "ERROR")
            }
        }
    }

    /**
     * Validates that the input string is a proper Judge JSON and saves it to the node.
     */
    private fun validateAndSaveJudge(node: GraphNode, input: String): Boolean {
        return try {
            // 1. Aggressive Extraction (Outermost Braces)
            val first = input.indexOf('{')
            val last = input.lastIndexOf('}')
            if (first == -1 || last == -1 || last <= first) return false
            
            val cleanJson = input.substring(first, last + 1)
            
            // 2. Parse and Schema Check
            val root = json.parseToJsonElement(cleanJson).jsonObject
            val persona = root["system_prompt"]?.jsonPrimitive?.content
            val rubric = root["rubric"]?.toString() // Rubric can be a string or object

            if (persona.isNullOrBlank() || rubric.isNullOrBlank()) return false
            
            // 3. Clean Persistence
            node.judgePrompt = persona
            node.judgeRubric = rubric
            true
        } catch (e: Exception) {
            log.debug("Validation failed for node '${node.label}': ${e.message}")
            false
        }
    }

    fun listJudges(root: GraphNode): List<JudgeMetadata> {
        val judges = mutableListOf<JudgeMetadata>()
        fun walk(node: GraphNode, visited: MutableSet<String>) {
            if (!visited.add(node.id)) return
            if (node.judgePrompt != null) {
                judges.add(JudgeMetadata(node.id, node.label, node.depth, node.judgeRubric != null, node.judgePrompt?.take(150) + "..."))
            }
            node.children.forEach { walk(it, visited) }
        }
        walk(root, mutableSetOf())
        return judges.sortedBy { it.depth }
    }
}

@kotlinx.serialization.Serializable
data class JudgeMetadata(val nodeId: String, val label: String, val depth: Int, val hasRubric: Boolean, val promptPreview: String)
