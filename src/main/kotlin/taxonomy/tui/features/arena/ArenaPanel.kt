package taxonomy.tui.features.arena

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import taxonomy.service.AnalysisPanelState
import taxonomy.tui.state.ArenaUiState
import taxonomy.tui.state.BenchmarkUiState

/** Content-only: the parent [taxonomy.tui.features.analysis.AnalysisPanel] owns the border. */
@Composable
fun ArenaPanel(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
    arenaState: ArenaUiState,
    benchmarkState: BenchmarkUiState,
) {
    Column {
            if (arenaState.isViewingLeaderboard) {
                Text("Leaderboard (global)", color = Cyan)
                Spacer()
                if (arenaState.leaderboard.isEmpty()) {
                    Text("No ratings recorded yet — run a benchmark or arena match.", color = Yellow)
                } else {
                    Text("%-22s %-10s %6s %6s %5s".format("Model", "Domain", "μ", "σ", "Rank"), color = Yellow)
                    val rows = (height - 4).coerceAtLeast(1)
                    arenaState.leaderboard
                        .flatMap { g -> g.agents.map { g.rank to it } }
                        .drop(arenaState.leaderboardScrollOffset)
                        .take(rows)
                        .forEach { (rank, a) ->
                            Text(
                                "%-22s %-10s %6.1f %6.1f %5d".format(
                                    a.agentName.take(22), a.domain.take(10), a.mu, a.sigma, rank
                                ).take((width - 2).coerceAtLeast(1)),
                                color = White
                            )
                        }
                }
                Spacer()
                Text("W/S to scroll · L to close", color = Cyan)
                return@Column
            }

            val mode = if (arenaState.usePrecomputed) "PRECOMPUTED (no live generation)" else "LIVE"
            Text("Mode: $mode", color = Green)

            // Ingestion in progress (kicked off from the eval-catalog picker): show which model
            // is being parsed and a coarse progress bar so the wait is legible.
            if (benchmarkState.evalLoadingModelCount > 0) {
                Spacer()
                val i = benchmarkState.evalLoadingModelIdx + 1
                val n = benchmarkState.evalLoadingModelCount
                val cur = benchmarkState.evalLoadingCurrentModel.ifBlank { "\u2026" }
                Text("Ingesting eval_results\u2026", color = Yellow)
                Text("  $cur  $i/$n", color = White)
                if (benchmarkState.evalLoadingItemTotal > 0) {
                    Text(
                        "  items ${benchmarkState.evalLoadingItem}/${benchmarkState.evalLoadingItemTotal}",
                        color = White
                    )
                    Text(progressBar(
                        benchmarkState.evalLoadingItem,
                        benchmarkState.evalLoadingItemTotal,
                        (width - 4).coerceIn(1, 40)
                    ), color = Green)
                }
                return@Column
            }

            if (arenaState.loadedModels.isEmpty()) {
                // Gated: no roster means nothing to judge.
                Spacer()
                Text("No precomputed eval_results loaded.", color = Yellow)
                Spacer()
                Text("Press [O] to pick and ingest MMLU-Pro model outputs.", color = Cyan)
                Text("Then choose Model A \u2192 Model B \u2192 question_id.", color = White)
                return@Column
            }

            Text("Loaded: ${arenaState.loadedModels.size} models", color = Green)
            Text("  ${arenaState.loadedModels.joinToString(", ").take((width - 4).coerceAtLeast(1))}", color = White)
            Spacer()

            // Models-first flow: A → B → question_id (precomputed) or query (live).
            when {
                arenaState.isEnteringArenaModelA ->
                    Text("Model A \u276f ${arenaState.arenaModelAInput}\u2588", color = Cyan)
                arenaState.isEnteringArenaModelB ->
                    Text("Model B \u276f ${arenaState.arenaModelBInput}\u2588", color = Cyan)
                arenaState.isEnteringArenaQuestionId ->
                    Text("question_id \u276f ${arenaState.arenaQuestionIdInput}\u2588", color = Cyan)
                arenaState.isEnteringArenaQuery ->
                    Text("Query \u276f ${arenaState.arenaQueryInput}\u2588", color = Cyan)
                else -> {
                    Text("Model A   ${controlState.modelA ?: "—"}", color = White)
                    Text("Model B   ${controlState.modelB ?: "—"}", color = White)
                    Text("Query     ${controlState.query ?: "—"}", color = White)
                }
            }

            Spacer()
            if (controlState.domainStatus.isEmpty()) {
                Text("No domain evaluations yet.", color = White)
            } else {
                Text("Per-domain status", color = Yellow)
                controlState.domainStatus.forEach { (domain, status) ->
                    Text("  $domain: $status", color = White)
                }
            }
    }
}

/** Render a simple [#####-----] bar; [current]/[total] clamped to [width] cells. */
private fun progressBar(current: Int, total: Int, width: Int): String {
    if (total <= 0 || width <= 0) return ""
    val filled = ((current.toDouble() / total) * width).toInt().coerceIn(0, width)
    return "  [" + "#".repeat(filled) + "-".repeat(width - filled) + "]"
}
