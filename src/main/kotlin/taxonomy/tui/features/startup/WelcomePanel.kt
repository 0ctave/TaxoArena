package taxonomy.tui.features.startup

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import com.jakewharton.mosaic.ui.TextStyle.Companion.Unspecified
import taxonomy.service.DagSnapshot
import taxonomy.tui.components.Panel

@Composable
fun WelcomePanel(
    width: Int,
    height: Int,
    selectedWelcomeIdx: Int,
    snapshots: List<DagSnapshot>,
) {
    Panel("SETUP HUB", Cyan, width, height) {
        Column(modifier = Modifier.padding(left = 2, top = 1)) {
            Text("Select an option to initialize the taxonomic DAG.", color = White)
            Spacer()

            val selectedNew = selectedWelcomeIdx == 0
            Text(
                value = (if (selectedNew) "> " else "  ") + "Generate new DAG",
                color = if (selectedNew) Cyan else White,
                textStyle = if (selectedNew) Bold else Unspecified
            )

            Spacer()
            Text("Snapshots", color = Yellow, textStyle = Bold)

            snapshots.forEachIndexed { idx, snap ->
                val selected = selectedWelcomeIdx == idx + 1
                Text(
                    value = (if (selected) "> " else "  ") + snap.description,
                    color = if (selected) Cyan else White,
                    textStyle = if (selected) Bold else Unspecified
                )
            }
        }
    }
}