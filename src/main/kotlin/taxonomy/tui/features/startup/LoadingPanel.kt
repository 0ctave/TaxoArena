package taxonomy.tui.features.startup

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
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
    Panel("TAXOARENA · LOADING", Yellow, width, height) {
        Column(modifier = Modifier.padding(left = 4, top = 2)) {
            // Main action in Cyan; sub-steps in White.
            Text(
                "Retrieving serialized taxonomy snapshot from SQLite DB...",
                color = Cyan,
                textStyle = Bold
            )
            Spacer()
            Text("Reassembling 4096-D statistical vMF-NiW node parameters...", color = White)
            Spacer()
            Text("Parsing historical adaptive run logs...", color = White)
            Spacer()
            // Animated loading bar: a single █ sweeps across a 20-cell track driven by spinnerTick.
            val barLen = 20
            val pos = spinnerTick % barLen
            val bar = buildString { for (i in 0 until barLen) append(if (i == pos) '█' else '░') }
            Text("  [$bar]", color = Cyan)
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