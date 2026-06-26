package taxonomy.tui.features.arena

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import taxonomy.service.AnalysisPanelState
import taxonomy.tui.components.Panel

@Composable
fun ArenaPanel(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
) {
    Panel("MODEL ARENA", Cyan, width, height) {
        Column(modifier = Modifier.padding(left = 2, top = 1)) {
            Text("Query: ${controlState.query ?: "—"}", color = White)
            Text("Model A: ${controlState.modelA ?: "—"}", color = White)
            Text("Model B: ${controlState.modelB ?: "—"}", color = White)
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
