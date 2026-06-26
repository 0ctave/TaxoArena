package taxonomy.tui.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.Immutable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import taxonomy.model.GraphNode

@Immutable
data class TuiSubscriptions(
    val rootNode: GraphNode?,
    val graphVersion: Int,
    val generationProgress: Any?,
    val labelingProgress: Any?,
    val embeddingProgress: Any?,
    val metricsHistory: List<Any>,
    val arenaControlState: Any,
)

/**
 * Collect all long-lived reactive service state in one place.
 *
 * The old DashboardView directly collected rootNodeFlow, graphVersionFlow,
 * generationProgressFlow, labelingProgressFlow, embeddingProgressFlow,
 * metricsHistoryFlow, and arenaService.state in the top-level composable [file:203][file:288].
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

    return TuiSubscriptions(
        rootNode = rootNode,
        graphVersion = graphVersion,
        generationProgress = generationProgress,
        labelingProgress = labelingProgress,
        embeddingProgress = embeddingProgress,
        metricsHistory = metricsHistory.map { it as Any },
        arenaControlState = arenaControlState as Any,
    )
}