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

            if (arenaState.loadedModels.isNotEmpty()) {
                Text("Loaded models: ${arenaState.loadedModels.joinToString(", ")}", color = White)
            } else {
                Text("No precomputed models loaded — use Benchmark (o) to load eval_results.", color = Yellow)
            }
            Spacer()

            when {
                arenaState.isEnteringArenaQuestionId ->
                    Text("Enter question_id: ${arenaState.arenaQuestionIdInput}_", color = Cyan)
                arenaState.isEnteringArenaQuery ->
                    Text("Enter query: ${arenaState.arenaQueryInput}_", color = Cyan)
                arenaState.isEnteringArenaModelA ->
                    Text("Model A: ${arenaState.arenaModelAInput}_", color = Cyan)
                arenaState.isEnteringArenaModelB ->
                    Text("Model B: ${arenaState.arenaModelBInput}_", color = Cyan)
                else -> {
                    Text("Query: ${controlState.query ?: "—"}", color = White)
                    Text("Model A: ${controlState.modelA ?: "—"}", color = White)
                    Text("Model B: ${controlState.modelB ?: "—"}", color = White)
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
