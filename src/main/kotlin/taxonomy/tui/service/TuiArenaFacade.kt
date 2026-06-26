package taxonomy.tui.service

import taxonomy.arena.AnalysisMode
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.tui.app.TuiDependencies

class TuiArenaFacade(
    private val deps: TuiDependencies
) {
    val state get() = deps.arenaService.state

    fun setMode(mode: AnalysisMode) {
        deps.arenaService.setMode(mode)
    }

    fun inspectNode(node: GraphNode) {
        deps.arenaService.inspectNode(node)
    }

    fun showMetrics() {
        deps.arenaService.setMode(AnalysisMode.METRICS)
    }

    fun showSnapshots() {
        deps.arenaService.setMode(AnalysisMode.SNAPSHOTS)
    }

    fun showArena() {
        deps.arenaService.setMode(AnalysisMode.ARENA)
    }

    fun showBenchmark() {
        deps.arenaService.setMode(AnalysisMode.BENCHMARK)
    }

    fun showTrickleTest() {
        deps.arenaService.setMode(AnalysisMode.TRICKLETEST)
    }

    fun showJudgeProgress() {
        deps.arenaService.setMode(AnalysisMode.JUDGEPROGRESS)
    }

    fun resetToIdle() {
        deps.arenaService.setMode(AnalysisMode.IDLE)
    }

    suspend fun compareModels(
        query: String,
        modelA: String,
        modelB: String
    ) {
        deps.arenaService.compareModels(query, modelA, modelB)
    }

    suspend fun runTrickleTest(
        root: GraphNode,
        query: String,
        iteration: Int = 2
    ): List<GraphNode> {
        val vector = deps.embeddingCache.getOrCreate(query)
        val embedding = Embedding(query, query, vector)
        val results = deps.trickleService.routeQuery(embedding, root, currentIteration = iteration)
        return results.keys.sortedByDescending { it.depth }
    }
}