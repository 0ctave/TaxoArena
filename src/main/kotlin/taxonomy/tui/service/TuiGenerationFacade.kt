package taxonomy.tui.service

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import taxonomy.model.GraphNode
import taxonomy.tui.app.TuiDependencies
import java.io.File

class TuiGenerationFacade(
    private val deps: TuiDependencies
) {
    suspend fun triggerRegeneration() {
        deps.host.triggerRegeneration()
    }

    suspend fun regenerateLabelsPostPass(root: GraphNode) {
        deps.taxonomyEngine.ops.generateLabelsPostPass(root) { current, total ->
            deps.taxonomyService.updateLabelingProgress(current, total)
        }
    }

    suspend fun generateJudgeForNode(root: GraphNode, nodeId: String) {
        deps.judgeService.generateJudgeForNodeById(root, nodeId)
    }

    suspend fun generateJudgesForDag(
        root: GraphNode,
        replaceExisting: Boolean
    ) {
        deps.judgeService.generateJudgesForDag(
            root,
            replaceExisting = replaceExisting
        )
    }

    suspend fun autoSaveActiveGraph(root: GraphNode) {
        deps.host.autoSaveActiveGraph(root)
    }

    suspend fun exportAscii(
        root: GraphNode,
        fileName: String = "dag-hierarchy-ascii.txt"
    ): File = withContext(Dispatchers.IO) {
        val ascii = deps.host.buildAsciiHierarchy(root)
        File(fileName).apply { writeText(ascii) }
    }

    fun clearProgress() {
        deps.taxonomyService.clearGenerationProgress()
    }
}