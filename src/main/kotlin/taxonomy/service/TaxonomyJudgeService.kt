package taxonomy.service

import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.model.GraphNode
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.prompts.JudgePrompts
import kotlin.math.abs

@Service
class TaxonomyJudgeService(
    private val datasetFetcher: MMLUDatasetFetcher,
    private val llmClient: TaxonomyLlmClient,
    private val config: TaxonomyConfig,
    private val arenaService: TaxonomyArenaService
) {
    private val log = LoggerFactory.getLogger("taxonomy.JudgeService")
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }

    /**
     * Generates judges for all qualifying nodes in the DAG.
     *
     * @param root           Root of the DAG.
     * @param replaceExisting When true, regenerate judges even for nodes that already have one.
     * @param parallelismOverride When > 0, overrides [TaxonomyConfig.ExecutionConfig.llmParallelism]
     *   for this run only. The value is clamped to [1, llmParallelism] so it can never exceed the
     *   configured ceiling. Use 0 (default) to keep the config value.
     */
    suspend fun generateJudgesForDag(
        root: GraphNode,
        replaceExisting: Boolean = false,
        parallelismOverride: Int = 0,
    ) = coroutineScope {
        log.info("Starting Grounded Agent Judge Induction (Replace: $replaceExisting, parallelismOverride: $parallelismOverride)")
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) { if (allNodes.add(n)) n.children.forEach { walk(it) } }
        walk(root)

        val targetNodes = allNodes.filter { node ->
            node.isLeaf && (replaceExisting || node.judgePrompt == null)
        }.sortedBy { it.depth }

        if (targetNodes.isEmpty()) {
            log.info("No nodes require judge generation.")
            return@coroutineScope
        }

        // Bug 1 fix: respect the caller-supplied parallelism (e.g. from the TUI generality prompt).
        // Clamp to [1, llmParallelism] so we never exceed the configured ceiling.
        val chunkSize = if (parallelismOverride > 0)
            parallelismOverride.coerceIn(1, config.execution.llmParallelism)
        else
            config.execution.llmParallelism

        log.info("Generating judges for ${targetNodes.size} leaf node(s) with parallelism=$chunkSize")
        targetNodes.chunked(chunkSize).forEach { chunk ->
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

    private fun calculateDistancesFromLeaves(allNodes: Set<GraphNode>): Map<String, Double> {
        val distances = mutableMapOf<String, Double>()
        
        fun computeAvgDist(node: GraphNode): Double {
            if (node.isLeaf) {
                distances[node.id] = 0.0
                return 0.0
            }
            if (distances.containsKey(node.id)) return distances[node.id]!!
            
            val allLeafDistances = mutableListOf<Int>()
            fun collect(n: GraphNode, dist: Int, pathVisited: MutableSet<String>) {
                if (!pathVisited.add(n.id)) return
                if (n.children.isEmpty()) {
                    allLeafDistances.add(dist)
                } else {
                    n.children.forEach { collect(it, dist + 1, pathVisited) }
                }
                pathVisited.remove(n.id)
            }
            collect(node, 0, mutableSetOf())
            
            val avg = if (allLeafDistances.isNotEmpty()) allLeafDistances.average() else 0.0
            distances[node.id] = avg
            return avg
        }
        
        allNodes.forEach { computeAvgDist(it) }
        return distances
    }

    suspend fun generateJudgeForNode(node: GraphNode) {
        // Bug 2 fix: for leaf nodes, use getAllQueriesInRegion() instead of node.queries directly.
        //
        // After the merger's evaluateCrossLinks pass, some leaf nodes receive training queries
        // exclusively via crossLinkChildren. Their node.queries list is empty in those cases,
        // causing details.isEmpty() and an early return with no judge generated.
        //
        // getAllQueriesInRegion() walks both tree children AND cross-link children, so it captures
        // the full corpus this leaf "covers" geometrically.  For non-leaf nodes we keep
        // getAllQueriesInBranch() (tree-only) because branch semantics are intentional there.
        val corpusEmbeddings = if (node.isLeaf) {
            node.getAllQueriesInRegion()
        } else {
            node.getAllQueriesInBranch()
        }.filter {
            abs(it.rawText.hashCode()) % 5 != 0
        }
        val detailsMap = datasetFetcher.getDetailsForQueries(corpusEmbeddings.map { it.rawText })
        val details = corpusEmbeddings.mapNotNull { detailsMap[it.rawText] }

        if (details.isEmpty()) {
            log.warn("generateJudgeForNode: empty corpus for node '${node.label}' (id=${node.id}). " +
                "queries=${node.queries.size}, crossLinkChildren=${node.crossLinkChildren.size}. Skipping.")
            return
        }

        val chunks = details.chunked(25)
        val chunksCount = chunks.size
        val hasSynthesis = chunksCount > 1
        val finalSteps = chunksCount + (if (hasSynthesis) 1 else 0) + 1 // +1 for final judge synthesis
        var currentStep = 0

        // PROGRESS TRACKING START
        arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, finalSteps, "BATCHING")

        val partialGuidelines = chunks.mapIndexed { index, batch ->
            val corpusStrings = batch.map { item ->
                val answerIndex = item.answer?.firstOrNull()?.let { it.uppercaseChar() - 'A' } ?: -1
                val choices = item.options.mapIndexed { i, opt ->
                    val letter = ('A' + i)
                    if (i == answerIndex) "$letter) $opt ✓" else "$letter) $opt"
                }.joinToString(" | ")
                "Q: ${item.question}\n$choices"
            }

            val result = llmClient.queryModel(
                config.llm.judgeModel,
                null,
                JudgePrompts.induceBatchGuidelines(corpusStrings, node.label ?: "General")
            )

            // UPDATE PROGRESS
            currentStep = index + 1
            arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, finalSteps, "INDUCTING")
            
            result
        }

        val masterGuidelines = if (chunksCount > 1) {
            arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, finalSteps, "SYNTHESIZING")
            val res = llmClient.queryModel(config.llm.judgeModel, null, JudgePrompts.synthesizeGlobalGuidelines(partialGuidelines))
            currentStep = chunksCount + 1
            arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, finalSteps, "SYNTHESIZING")
            res
        } else partialGuidelines.first()

        arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, finalSteps, "FINALIZING")
        val rawSynthesis = llmClient.queryModel(
            config.llm.judgeModel, null,
            JudgePrompts.synthesizeFinalJudge(masterGuidelines, node.label ?: "General")
        )
        currentStep = finalSteps - 1
        arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, finalSteps, "SAVING")
        
        if (validateAndSaveJudge(node, rawSynthesis)) {
            arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", finalSteps, finalSteps, "READY")
        } else {
            // PHASE 3: AUTOMATED REPAIR
            log.warn("Judge JSON for '${node.label}' is malformed. Attempting LLM repair...")
            val repairSteps = finalSteps + 1
            arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", finalSteps - 1, repairSteps, "REPAIRING")
            
            val repairedJson = llmClient.queryModel(config.llm.judgeModel, null, JudgePrompts.repairMalformedJson(rawSynthesis))
            currentStep = finalSteps
            arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", currentStep, repairSteps, "SAVING")
            
            if (validateAndSaveJudge(node, repairedJson)) {
                log.info("Successfully repaired judge JSON for '${node.label}'.")
                arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", repairSteps, repairSteps, "READY")
            } else {
                log.error("Failed to repair judge JSON for '${node.label}' after LLM assistance.")
                arenaService.updateJudgeProgress(node.label ?: "Emergent Concept", repairSteps, repairSteps, "ERROR")
            }
        }
    }

    /**
     * Validates that the input string is a proper Judge JSON and saves it to the node.
     */
    private fun validateAndSaveJudge(node: GraphNode, input: String): Boolean {
        val parsed = JudgePrompts.parseJudgeJson(input) ?: return false
        node.judgePrompt = parsed.first
        node.judgeRubric = parsed.second
        return true
    }

    fun listJudges(root: GraphNode): List<JudgeMetadata> {
        val judges = mutableListOf<JudgeMetadata>()
        fun walk(node: GraphNode, visited: MutableSet<String>) {
            if (!visited.add(node.id)) return
            if (node.judgePrompt != null) {
                judges.add(JudgeMetadata(node.id, node.label ?: node.id.toString(), node.depth, node.judgeRubric != null, node.judgePrompt?.take(150) + "..."))
            }
            node.children.forEach { walk(it, visited) }
        }
        walk(root, mutableSetOf())
        return judges.sortedBy { it.depth }
    }
}

@kotlinx.serialization.Serializable
data class JudgeMetadata(val nodeId: String, val label: String, val depth: Int, val hasRubric: Boolean, val promptPreview: String)
