package taxonomy.tui.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.Immutable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import taxonomy.model.GraphNode
import taxonomy.service.AnalysisPanelState
import taxonomy.tui.components.TreeLine
import taxonomy.tui.components.buildTreeLines

@Immutable
data class TuiSubscriptions(
    val rootNode: GraphNode?,
    val graphVersion: Int,
    val generationProgress: Any?,
    val labelingProgress: Any?,
    val embeddingProgress: Any?,
    val metricsHistory: List<Any>,
    val arenaControlState: AnalysisPanelState,
    val treeLines: List<TreeLine>,
)

/**
 * Collect all long-lived reactive service state in one place so the render tree
 * only depends on a single immutable snapshot.
 */
@Composable
fun rememberTuiSubscriptions(
    deps: TuiDependencies,
): TuiSubscriptions {
    val rootNode by deps.taxonomyService.rootNodeFlow.collectAsState()
    val graphVersion by deps.taxonomyService.graphVersionFlow.collectAsState()
    val generationProgress by deps.taxonomyService.generationProgressFlow.collectAsState()
    val labelingProgress by deps.taxonomyService.labelingProgressFlow.collectAsState()
    val embeddingProgress by deps.taxonomyService.embeddingProgressFlow.collectAsState()
    val metricsHistory by deps.taxonomyService.metricsHistoryFlow.collectAsState()
    val arenaControlState by deps.arenaService.state.collectAsState()

    val treeLines = remember(rootNode, graphVersion) { buildTreeLines(rootNode) }

    return TuiSubscriptions(
        rootNode = rootNode,
        graphVersion = graphVersion,
        generationProgress = generationProgress,
        labelingProgress = labelingProgress,
        embeddingProgress = embeddingProgress,
        metricsHistory = metricsHistory.map { it as Any },
        arenaControlState = arenaControlState,
        treeLines = treeLines,
    )
}
