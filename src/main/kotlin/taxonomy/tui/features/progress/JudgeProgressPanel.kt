package taxonomy.tui.features.progress

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import taxonomy.service.AnalysisPanelState
import taxonomy.tui.components.TuiTheme
import taxonomy.tui.components.take

@Composable
fun JudgeProgressPanel(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
    isEnteringBatchGenerality: Boolean = false,
    batchGeneralityInput: String = "1",
    batchReplaceExisting: Boolean = false,
) {
    val w = (width - 1).coerceAtLeast(1)
    Column {
        if (isEnteringBatchGenerality) {
            // ── Generality input prompt ──────────────────────────────────────
            Text("Batch judge generation".take(w), color = Cyan, textStyle = Bold)
            Text("".take(w), color = White)
            Text("Max generality level? (1 = specific  ·  10 = very general)".take(w), color = White)
            Text(
                buildAnnotatedString {
                    withStyle(SpanStyle(color = TuiTheme.ACCENT, textStyle = Bold)) { append(" ❯ ") }
                    withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append(batchGeneralityInput) }
                    withStyle(SpanStyle(color = White, textStyle = Bold)) { append("█") }
                }.take(w)
            )
            Text("".take(w), color = White)
            Text(
                buildAnnotatedString {
                    withStyle(SpanStyle(color = White)) { append("Replace existing judges: ") }
                    withStyle(SpanStyle(
                        color = if (batchReplaceExisting) TuiTheme.ERROR else TuiTheme.OK
                    )) {
                        append(if (batchReplaceExisting) "yes  [F to toggle]" else "no   [G to toggle]")
                    }
                }.take(w)
            )
            Text("".take(w), color = White)
            Text(
                buildAnnotatedString {
                    withStyle(SpanStyle(color = TuiTheme.OK, textStyle = Bold)) { append("[Enter]") }
                    withStyle(SpanStyle(color = White)) { append(" Confirm  ") }
                    withStyle(SpanStyle(color = TuiTheme.ERROR, textStyle = Bold)) { append("[Esc]") }
                    withStyle(SpanStyle(color = White)) { append(" Cancel") }
                }.take(w)
            )
        } else {
            // ── Running / idle progress view ─────────────────────────────────
            Text("Batch judge generation".take(w), color = Cyan, textStyle = Bold)
            Text("".take(w), color = White)
            if (controlState.currentInductions.isEmpty()) {
                Text("Waiting for nodes to process…".take(w), color = TuiTheme.INFO)
            } else {
                controlState.currentInductions.values.forEach { p ->
                    Text(
                        buildAnnotatedString {
                            withStyle(SpanStyle(color = White)) { append(p.nodeLabel.take(w / 2)) }
                            withStyle(SpanStyle(color = TuiTheme.MUTED)) { append("  ") }
                            withStyle(SpanStyle(color = TuiTheme.OK)) {
                                append("${p.processed}/${p.total}")
                            }
                            withStyle(SpanStyle(color = TuiTheme.INFO)) {
                                append("  [${p.status}]")
                            }
                        }.take(w)
                    )
                }
            }
            Text("".take(w), color = White)
            Text(
                buildAnnotatedString {
                    withStyle(SpanStyle(color = TuiTheme.ERROR, textStyle = Bold)) { append("[Esc]") }
                    withStyle(SpanStyle(color = White)) { append(" Cancel") }
                }.take(w)
            )
        }
    }
}
