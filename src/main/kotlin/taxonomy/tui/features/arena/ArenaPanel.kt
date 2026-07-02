package taxonomy.tui.features.arena

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color
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

import taxonomy.tui.components.ScrollablePanelContent

/**
 * Truncating wrapper around [Text].
 *
 * Mosaic 0.18.0's `TextSurface.get` throws `IllegalStateException("Check failed.")` when a
 * `Text` composable is asked to draw past the end of its allocated row (see crash logged
 * from `TaxonomyTuiService.run` while the user was editing the Arena benchmark inputs).
 * Every single-line text in this panel must therefore be clamped to the available column
 * width *before* it reaches Mosaic's draw scope. Centralising the clamp here means
 * adding/editing a panel line is one call site instead of a `.take(width)` ritual that
 * is easy to forget — which is exactly how this regression slipped in.
 */
@Composable
private fun SafeText(text: String, width: Int, color: Color = White) {
    val safe = if (width <= 0) "" else if (text.length > width) text.take(width) else text
    Text(safe, color = color)
}

/** Content-only: the parent [taxonomy.tui.features.analysis.AnalysisPanel] owns the border. */
@Composable
fun ArenaPanel(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
    arenaState: ArenaUiState,
    benchmarkState: BenchmarkUiState,
) {
    // The inner column lives inside the bordered AnalysisPanel; available row width is the
    // panel's body width minus the column's own 1-cell safety margin so a stray trailing
    // glyph cannot collide with the right border.
    val w = (width - 1).coerceAtLeast(1)

    Column {
            if (arenaState.isViewingLeaderboard) {
                SafeText("Leaderboard (global)", w, Cyan)
                Spacer()
                if (arenaState.leaderboard.isEmpty()) {
                    SafeText("No ratings recorded yet — run a benchmark or arena match.", w, Yellow)
                } else {
                    SafeText("%-22s %-10s %6s %6s %5s".format("Model", "Domain", "μ", "σ", "Rank"), w, Yellow)
                    val items = arenaState.leaderboard.flatMap { g -> g.agents.map { g.rank to it } }
                    val rows = (height - 4).coerceAtLeast(1)
                    ScrollablePanelContent(
                        pWidth = width,
                        pHeight = rows,
                        itemCount = items.size,
                        scrollOffset = arenaState.leaderboardScrollOffset,
                        hasPadding = false
                    ) { visibleHeight, startIdx, innerWidth ->
                        val endIdx = (startIdx + visibleHeight).coerceAtMost(items.size)
                        for (i in startIdx until endIdx) {
                            val (rank, a) = items[i]
                            SafeText(
                                "%-22s %-10s %6.1f %6.1f %5d".format(
                                    a.agentName.take(22), a.domain.take(10), a.mu, a.sigma, rank
                                ),
                                innerWidth,
                                White
                            )
                        }
                    }
                }
                Spacer()
                SafeText("W/S to scroll · L to close", w, Cyan)
                return@Column
            }

            val mode = if (arenaState.usePrecomputed) "PRECOMPUTED (no live generation)" else "LIVE"
            SafeText("Mode: $mode", w, Green)

            // Ingestion in progress (kicked off from the eval-catalog picker): show which model
            // is being parsed and a coarse progress bar so the wait is legible.
            if (benchmarkState.evalLoadingModelCount > 0) {
                Spacer()
                val i = benchmarkState.evalLoadingModelIdx + 1
                val n = benchmarkState.evalLoadingModelCount
                val cur = benchmarkState.evalLoadingCurrentModel.ifBlank { "\u2026" }
                SafeText("Ingesting eval_results\u2026", w, Yellow)
                SafeText("  $cur  $i/$n", w, White)
                if (benchmarkState.evalLoadingItemTotal > 0) {
                    SafeText(
                        "  items ${benchmarkState.evalLoadingItem}/${benchmarkState.evalLoadingItemTotal}",
                        w,
                        White
                    )
                    SafeText(
                        progressBar(
                            benchmarkState.evalLoadingItem,
                            benchmarkState.evalLoadingItemTotal,
                            (w - 4).coerceIn(1, 40)
                        ),
                        w,
                        Green
                    )
                }
                return@Column
            }

            if (arenaState.loadedModels.isEmpty()) {
                // Gated: no roster means nothing to judge.
                Spacer()
                SafeText("No precomputed eval_results loaded.", w, Yellow)
                Spacer()
                SafeText("Press [O] to pick and ingest MMLU-Pro model outputs.", w, Cyan)
                SafeText("Then choose Model A \u2192 Model B \u2192 question_id.", w, White)
                return@Column
            }

            SafeText("Loaded: ${arenaState.loadedModels.size} models", w, Green)
            SafeText("  ${arenaState.loadedModels.joinToString(", ")}", w, White)
            Spacer()

            // Models-first flow: A → B → question_id (precomputed) or query (live).
            // These input echoes grow with each keystroke and were the original crash trigger:
            // the user's typed string eventually exceeded the panel column and TextSurface.get
            // threw. SafeText clamps every keystroke-driven line to the visible column.
            when {
                arenaState.isEnteringArenaModelA ->
                    SafeText("Model A \u276f ${arenaState.arenaModelAInput}\u2588", w, Cyan)
                arenaState.isEnteringArenaModelB ->
                    SafeText("Model B \u276f ${arenaState.arenaModelBInput}\u2588", w, Cyan)
                arenaState.isEnteringArenaQuestionId ->
                    SafeText("question_id \u276f ${arenaState.arenaQuestionIdInput}\u2588", w, Cyan)
                arenaState.isEnteringArenaQuery ->
                    SafeText("Query \u276f ${arenaState.arenaQueryInput}\u2588", w, Cyan)
                else -> {
                    SafeText("Model A   ${controlState.modelA ?: "—"}", w, White)
                    SafeText("Model B   ${controlState.modelB ?: "—"}", w, White)
                    SafeText("Query     ${controlState.query ?: "—"}", w, White)
                }
            }

            Spacer()
            if (controlState.domainStatus.isEmpty()) {
                SafeText("No domain evaluations yet.", w, White)
            } else {
                SafeText("Per-domain status", w, Yellow)
                controlState.domainStatus.forEach { (domain, status) ->
                    SafeText("  $domain: $status", w, White)
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
