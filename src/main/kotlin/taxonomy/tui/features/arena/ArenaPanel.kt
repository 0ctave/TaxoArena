package taxonomy.tui.features.arena

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Text
import taxonomy.arena.TaxonomyArenaState
import taxonomy.tui.components.Panel

@Composable
fun ArenaPanel(
    width: Int,
    height: Int,
    controlState: TaxonomyArenaState,
) {
    Panel("MODEL ARENA", Cyan, width, height) {
        Column(modifier = Modifier.padding(left = 2, top = 1)) {
            Text("Arena comparison mode.", color = White)
            Text("Selected node: ${controlState.selectedNode?.label ?: "none"}", color = White)
            controlState.arenaResult?.let {
                Text("Winner: ${it.winner}", color = White)
                Text("Reason: ${it.reasoning.take(120)}", color = White)
            } ?: Text("No arena result yet.", color = White)
        }
    }
}