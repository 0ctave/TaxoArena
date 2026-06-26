package taxonomy.controller

import kotlinx.coroutines.runBlocking
import org.springframework.web.bind.annotation.*
import taxonomy.config.TaxonomyConfig
import taxonomy.model.GraphNode
import taxonomy.service.JudgeMetadata
import taxonomy.service.TaxonomyJudgeService
import taxonomy.service.TaxonomyService

@RestController
@RequestMapping("/api/taxonomy/judge")
class TaxonomyJudgeController(
    private val taxonomyService: TaxonomyService,
    private val judgeService: TaxonomyJudgeService,
    private val config: TaxonomyConfig
) {

    @PostMapping("/generate")
    fun generateJudges(
        @RequestParam(required = false) nodeId: String?,
        @RequestParam(defaultValue = "false") replace: Boolean
    ): Map<String, String> = runBlocking {
        val root = taxonomyService.getGraph() ?: return@runBlocking mapOf("error" to "Taxonomy not loaded")
        
        try {
            if (nodeId != null) {
                judgeService.generateJudgeForNodeById(root, nodeId)
            } else {
                judgeService.generateJudgesForDag(root, replace)
            }
            
            mapOf("message" to "Agent Judges generated and persisted successfully.")
        } catch (e: Exception) {
            mapOf("error" to (e.message ?: "Unknown error"))
        }
    }

    @GetMapping("/list")
    fun listJudges(): List<JudgeMetadata> {
        val root = taxonomyService.getGraph() ?: return emptyList()
        return judgeService.listJudges(root)
    }

    @GetMapping("/node/{id}")
    fun getNodeJudge(@PathVariable id: String): Map<String, Any?> {
        val root = taxonomyService.getGraph() ?: return mapOf("error" to "Taxonomy not loaded")
        
        // Find node
        val allNodes = mutableSetOf<GraphNode>()
        fun walk(n: GraphNode) {
            if (allNodes.add(n)) n.children.forEach { walk(it) }
        }
        walk(root)
        
        val node = allNodes.find { it.id == id } ?: return mapOf("error" to "Node not found")
        
        return mapOf(
            "nodeId" to node.id,
            "label" to node.label,
            "judgePrompt" to node.judgePrompt,
            "judgeRubric" to node.judgeRubric
        )
    }
}
