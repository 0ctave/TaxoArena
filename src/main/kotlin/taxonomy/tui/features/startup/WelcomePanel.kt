package taxonomy.tui.features.startup

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
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
        Column {
            Text("  ╔══ TAXO ARENA ══╗", color = Cyan, textStyle = Bold)
            Text("  ║  DAG · ARENA   ║", color = Cyan, textStyle = Bold)
            Text("  ╚════════════════╝", color = Cyan, textStyle = Bold)
            Spacer()

            Text("Select an option to initialize the taxonomic DAG.", color = White)
            Spacer()

            val selectedNew = selectedWelcomeIdx == 0
            Text(
                buildAnnotatedString {
                    append(if (selectedNew) "> " else "  ")
                    withStyle(SpanStyle(color = Green, textStyle = Bold)) { append("● ") }
                    withStyle(
                        SpanStyle(
                            color = if (selectedNew) Cyan else White,
                            textStyle = if (selectedNew) Bold else Unspecified
                        )
                    ) { append("Generate new DAG") }
                }
            )

            Spacer()
            Text("Snapshots", color = Yellow, textStyle = Bold)

            snapshots.forEachIndexed { idx, snap ->
                val selected = selectedWelcomeIdx == idx + 1
                Text(
                    buildAnnotatedString {
                        append(if (selected) "> " else "  ")
                        withStyle(
                            SpanStyle(
                                color = if (selected) Cyan else White,
                                textStyle = if (selected) Bold else Unspecified
                            )
                        ) { append(snap.description) }
                        // Timestamp + node count rendered as muted (White, no Bold) metadata.
                        withStyle(SpanStyle(color = White)) {
                            append("  (${snap.timestamp} · ${snap.metrics.totalNodes} nodes)")
                        }
                    }
                )
            }
        }
    }
}