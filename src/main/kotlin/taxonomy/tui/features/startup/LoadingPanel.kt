package taxonomy.tui.features.startup

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Row
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import taxonomy.tui.components.Panel
import taxonomy.tui.components.TuiTheme.SPINNER

@Composable
fun LoadingPanel(
    width: Int,
    height: Int,
    spinnerTick: Int,
) {
    Panel("SETUP HUB  LOADING PREGENERATED SNAPSHOT", Yellow, width, height) {
        Column(modifier = Modifier.padding(left = 4, top = 2)) {
            Text(
                "Retrieving serialized taxonomy snapshot from SQLite DB...",
                color = White,
                textStyle = Bold
            )
            Spacer()
            Text("Reassembling 4096-D statistical vMF-NiW node parameters...", color = White)
            Spacer()
            Text("Parsing historical adaptive run logs...", color = White)
            Spacer()
            Row {
                Text("Status ", color = White)
                Text(
                    "LOADING SNAPSHOT ${SPINNER[spinnerTick % SPINNER.size]}",
                    color = Yellow,
                    textStyle = Bold
                )
            }
        }
    }
}