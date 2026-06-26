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
import taxonomy.tui.components.Panel
import taxonomy.tui.state.ArenaUiState

@Composable
fun ArenaPanel(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
    arenaState: ArenaUiState,
) {
    Panel("MODEL ARENA", Cyan, width, height) {
        Column(modifier = Modifier.padding(left = 2, top = 1)) {
            val mode = if (arenaState.usePrecomputed) "PRECOMPUTED (no live generation)" else "LIVE"
            Text("Mode: $mode", color = Green)

            if (arenaState.loadedModels.isEmpty()) {
                // Gated: no roster means nothing to judge.
                Text("No precomputed eval_results loaded.", color = Yellow)
                Spacer()
                Text("Load MMLU-Pro model outputs first:", color = White)
                Text("  press [O] to load eval_results", color = Cyan)
                Text("Then pick Model A \u2192 Model B \u2192 question_id.", color = White)
                return@Column
            }

            Text("Loaded models: ${arenaState.loadedModels.joinToString(", ")}", color = White)
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
}
