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
    batchDomainsInput: String = "",
    batchSelectedSettingIdx: Int = 0,
    isEditingBatchSetting: Boolean = false,
    batchEditingValue: String = "",
) {
    val w = (width - 1).coerceAtLeast(1)
    Column {
        if (isEnteringBatchGenerality) {
            // ── Generality settings menu ──────────────────────────────────────
            Text("Batch Judge Settings".take(w), color = Cyan, textStyle = Bold)
            Text("".take(w), color = White)

            // Row 0: Max Generality Level
            val isRow0Selected = batchSelectedSettingIdx == 0
            val row0Val = if (isRow0Selected && isEditingBatchSetting) "${batchEditingValue}█" else batchGeneralityInput
            Text(
                buildAnnotatedString {
                    if (isRow0Selected) {
                        withStyle(SpanStyle(color = TuiTheme.ACCENT, textStyle = Bold)) { append(" ❯ ") }
                        withStyle(SpanStyle(color = TuiTheme.ACCENT, textStyle = Bold)) { append("Max Generality Level: ") }
                        withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append(row0Val) }
                    } else {
                        append("   Max Generality Level: ")
                        withStyle(SpanStyle(color = TuiTheme.MUTED)) { append(row0Val) }
                    }
                }.take(w)
            )

            // Row 1: Target Domains
            val isRow1Selected = batchSelectedSettingIdx == 1
            val row1Val = if (isRow1Selected && isEditingBatchSetting) "${batchEditingValue}█" else batchDomainsInput.ifBlank { "(all)" }
            Text(
                buildAnnotatedString {
                    if (isRow1Selected) {
                        withStyle(SpanStyle(color = TuiTheme.ACCENT, textStyle = Bold)) { append(" ❯ ") }
                        withStyle(SpanStyle(color = TuiTheme.ACCENT, textStyle = Bold)) { append("Target Domains: ") }
                        withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append(row1Val) }
                    } else {
                        append("   Target Domains: ")
                        withStyle(SpanStyle(color = TuiTheme.MUTED)) { append(row1Val) }
                    }
                }.take(w)
            )

            // Row 2: Replace Existing
            val isRow2Selected = batchSelectedSettingIdx == 2
            val row2Val = if (batchReplaceExisting) "yes" else "no"
            Text(
                buildAnnotatedString {
                    if (isRow2Selected) {
                        withStyle(SpanStyle(color = TuiTheme.ACCENT, textStyle = Bold)) { append(" ❯ ") }
                        withStyle(SpanStyle(color = TuiTheme.ACCENT, textStyle = Bold)) { append("Replace Existing: ") }
                        withStyle(SpanStyle(
                            color = if (batchReplaceExisting) TuiTheme.ERROR else TuiTheme.OK,
                            textStyle = Bold
                        )) { append(row2Val) }
                    } else {
                        append("   Replace Existing: ")
                        withStyle(SpanStyle(
                            color = if (batchReplaceExisting) TuiTheme.ERROR else TuiTheme.OK
                        )) { append(row2Val) }
                    }
                }.take(w)
            )

            // Row 3: [Start Generation]
            val isRow3Selected = batchSelectedSettingIdx == 3
            Text(
                buildAnnotatedString {
                    if (isRow3Selected) {
                        withStyle(SpanStyle(color = TuiTheme.ACCENT, textStyle = Bold)) { append(" ❯ ") }
                        withStyle(SpanStyle(color = TuiTheme.ACCENT, textStyle = Bold)) { append("[Start Generation]") }
                    } else {
                        append("   ")
                        withStyle(SpanStyle(color = TuiTheme.OK, textStyle = Bold)) { append("[Start Generation]") }
                    }
                }.take(w)
            )

            Text("".take(w), color = White)
            Text(
                buildAnnotatedString {
                    withStyle(SpanStyle(color = TuiTheme.INFO, textStyle = Bold)) { append("[W/S]") }
                    withStyle(SpanStyle(color = White)) { append(" Navigate  ") }
                    withStyle(SpanStyle(color = TuiTheme.OK, textStyle = Bold)) { append("[Enter]") }
                    withStyle(SpanStyle(color = White)) { append(if (isEditingBatchSetting) " Confirm  " else " Edit/Toggle/Execute  ") }
                    withStyle(SpanStyle(color = TuiTheme.ERROR, textStyle = Bold)) { append("[Esc]") }
                    withStyle(SpanStyle(color = White)) { append(if (isEditingBatchSetting) " Cancel Edit" else " Cancel") }
                }.take(w)
            )
        } else {
            // ── Running / idle progress view ─────────────────────────────────
            Text("Batch judge generation".take(w), color = Cyan, textStyle = Bold)
            Text("".take(w), color = White)
            if (controlState.currentInductions.isEmpty()) {
                Text("Waiting for nodes to process…".take(w), color = TuiTheme.INFO)
            } else {
                val sortedList = controlState.currentInductions.values.sortedWith(
                    compareBy<taxonomy.service.JudgeProgress> { p ->
                        when (p.status) {
                            "INDUCTING", "SYNTHESIZING", "SAVING", "REPAIRING" -> 0
                            "ERROR" -> 1
                            "READY", "SKIPPED" -> 2
                            else -> 3
                        }
                    }.thenBy { it.nodeLabel }
                )

                val maxEntries = (height - 4).coerceAtLeast(1)
                val showSummary = sortedList.size > maxEntries
                val displayCount = if (showSummary) (height - 5).coerceAtLeast(1) else maxEntries
                val toDisplay = sortedList.take(displayCount)

                toDisplay.forEach { p ->
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

                if (showSummary) {
                    val remaining = sortedList.size - displayCount
                    val readyCount = sortedList.count { it.status == "READY" || it.status == "SKIPPED" }
                    val totalCount = sortedList.size
                    Text(
                        "... and $remaining more nodes ($readyCount/$totalCount finished)".take(w),
                        color = TuiTheme.ACCENT
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
