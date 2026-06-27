package taxonomy.tui.features.progress

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Text
import taxonomy.service.AnalysisPanelState
import taxonomy.tui.components.Panel

@Composable
fun JudgeProgressPanel(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
) {
        Column {
            Text("Batch judge generation mode.", color = White)
            if (controlState.currentInductions.isEmpty()) {
                Text("No active progress.", color = White)
            } else {
                controlState.currentInductions.values.forEach { p ->
                    Text("${p.nodeLabel}: ${p.processed}/${p.total} [${p.status}]", color = White)
                }
            }
        }
}
