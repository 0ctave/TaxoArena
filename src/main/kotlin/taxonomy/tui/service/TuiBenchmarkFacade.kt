package taxonomy.tui.service

import taxonomy.arena.AnalysisMode
import taxonomy.tui.app.TuiDependencies

class TuiBenchmarkFacade(
    private val deps: TuiDependencies
) {
    suspend fun startBenchmarkRun() {
        deps.host.startBenchmarkRun()
    }

    suspend fun startEvalBenchmarkRun() {
        deps.host.startEvalBenchmarkRun()
    }

    suspend fun startEvalLoad() {
        deps.host.startEvalLoad()
    }

    suspend fun syncReservedPool() {
        deps.evalLoader.syncReservedPool()
    }

    fun refreshEvalDbStats() {
        deps.host.refreshEvalDbStats()
    }

    fun showBenchmarkMode() {
        deps.arenaService.setMode(AnalysisMode.BENCHMARK)
    }

    fun clearBenchmarkReport() {
        deps.arenaService.setBenchmarkReport(null)
    }
}