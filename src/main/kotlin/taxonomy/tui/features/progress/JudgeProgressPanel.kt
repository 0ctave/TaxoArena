package taxonomy.tui.features.progress

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
fun JudgeProgressPanel(
    width: Int,
    height: Int,
    controlState: TaxonomyArenaState,
) {
    Panel("JUDGE PROGRESS", Cyan, width, height) {
        Column(modifier = Modifier.padding(left = 2, top = 1)) {
            Text("Batch judge generation mode.", color = White)
            Text(controlState.statusMessage ?: "No active progress.", color = White)
        }
    }
}