package taxonomy.tui.features.analysis

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.AnnotatedString
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.Magenta
import com.jakewharton.mosaic.ui.Color.Companion.Red
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Row
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import com.jakewharton.mosaic.ui.TextStyle.Companion.Unspecified
import taxonomy.model.GraphNode
import taxonomy.model.IterationMetrics
import taxonomy.model.TaxonomyMetricsData
import taxonomy.service.AnalysisMode
import taxonomy.service.AnalysisPanelState
import taxonomy.service.TaxonomyRankingService.AggregatedLeaderboard
import taxonomy.tui.components.ScrollablePanelContent
import taxonomy.tui.components.take
import taxonomy.tui.state.MetricsZoneFocus
import taxonomy.tui.state.ScrollbarTarget
import taxonomy.tui.controller.TuiEvent
import taxonomy.utils.PerformanceStats
import java.util.Locale

/**
 * Content-only metrics / node-inspector view. The parent [AnalysisPanel] owns the border
 * and the title; this switches on the MVI [mode]. METRICS renders the redesigned 3-zone
 * layout (evolution table + pinned final metrics + per-iteration detail); NODE_DETAIL
 * renders the selected node's stats.
 */
@Composable
fun MetricsOrInspectorPanel(
    width: Int,
    height: Int,
    mode: AnalysisMode,
    controlState: AnalysisPanelState,
    inspectorScroll: Int,
    metricsScrollOffset: Int = 0,
    latestMetrics: IterationMetrics? = null,
    metricsHistory: List<IterationMetrics> = emptyList(),
    isGeneratingJudge: Boolean = false,
    selectedIterationIndex: Int = -1,
    metricsZoneFocus: MetricsZoneFocus = MetricsZoneFocus.TABLE,
    showPerformanceBlock: Boolean = false,
    detailScrollOffset: Int = 0,
    performanceReport: Map<String, PerformanceStats> = emptyMap(),
    dispatch: (TuiEvent) -> Unit = {}
) {
    when (mode) {
        AnalysisMode.NODE_DETAIL -> {
            val node = controlState.selectedNode
            if (node == null) {
                Column { Text("Select a node in the DAG (Enter) to inspect it.", color = White) }
            } else {
                val items = buildNodeDetailLines(
                    node = node,
                    width = width,
                    isGeneratingJudge = isGeneratingJudge,
                    leaderboard = controlState.nodeLeaderboard,
                    isLoadingLeaderboard = controlState.isLoadingLeaderboard
                )
                ScrollablePanelContent(
                    pWidth = width,
                    pHeight = height,
                    itemCount = items.size,
                    scrollOffset = inspectorScroll,
                    hasPadding = false,
                    onScrollClamp = { dispatch(TuiEvent.ScrollTo(ScrollbarTarget.ANALYSIS, it)) }
                ) { visibleHeight, startIdx, _ ->
                    items.drop(startIdx).take(visibleHeight).forEach { (text, color, bold) ->
                        Text(
                            text,
                            color = color,
                            textStyle = if (bold) Bold else Unspecified,
                            modifier = Modifier.height(1),
                        )
                    }
                }
            }
        }

        AnalysisMode.METRICS -> {
            val history = metricsHistory.ifEmpty { listOfNotNull(latestMetrics) }
            if (history.isEmpty()) {
                Column { Text("No metrics yet — generate or load a DAG first.", color = Yellow) }
            } else {
                MetricsThreeZone(
                    width = width,
                    height = height,
                    history = history,
                    selectedIterationIndex = selectedIterationIndex,
                    focus = metricsZoneFocus,
                    showPerformanceBlock = showPerformanceBlock,
                    detailScrollOffset = detailScrollOffset,
                    metricsScrollOffset = metricsScrollOffset,
                    performanceReport = performanceReport,
                    dispatch = dispatch
                )
            }
        }

        AnalysisMode.SETTINGS -> Column {
            Text("Open the config screen (X → Load DAG → Create new) to edit settings.", color = White)
        }

        else -> Column {
            Text("No content do display", color = Cyan, textStyle = Bold)
        }
    }
}

fun buildNodeDetailLines(
    node: GraphNode,
    width: Int,
    isGeneratingJudge: Boolean,
    leaderboard: AggregatedLeaderboard? = null,
    isLoadingLeaderboard: Boolean = false
): List<Triple<String, Color, Boolean>> {
    val out = mutableListOf<Triple<String, Color, Boolean>>()
    fun add(t: String, c: Color = White, bold: Boolean = false) {
        val limit = (width - 2).coerceAtLeast(0)
        val truncated = if (t.length > limit) t.substring(0, limit) else t
        out += Triple(truncated, c, bold)
    }
    fun shortModelName(name: String): String {
        val clean = name.lowercase()
        return when {
            clean.contains("claude") -> "claude"
            clean.contains("70b") -> "70B"
            clean.contains("8b") -> "8B"
            clean.contains("13b") -> "13B"
            clean.contains("7b") -> "7B"
            clean.contains("gpt-4") -> "gpt4"
            else -> name.take(8)
        }
    }
    add(node.label ?: "(unlabeled)", Cyan, true)
    add("")
    add("Type           ${if (node.isLeaf) "leaf" else "internal"}")
    add("Depth          ${node.depth}")
    add("Direct queries ${node.queries.size}")
    add("Total queries  ${node.getRecursiveQueryCount()}")
    add("Parents        ${node.parents.size}")
    add("Children       ${node.children.size}")
    if (node.crossLinkChildren.isNotEmpty()) add("Cross-links    ${node.crossLinkChildren.size}", Yellow)
    val judged = node.judgePrompt != null
    add("")
    when {
        isGeneratingJudge -> add("⧖ Generating judge…", Yellow, true)
        judged -> {
            add("Judge          ✔ specialised", Green)
            add("[R] Regenerate judge")
        }
        else -> {
            add("┌─ Generate Judge ─┐", Cyan, true)
            add("│   [R] Generate   │", Cyan, true)
            add("└──────────────────┘", Cyan, true)
        }
    }
    if (node.parents.size > 1) {
        add("")
        add("Parents:", Cyan)
        node.parents.take(4).forEach { add("  · ${it.label ?: it.id}") }
    }
    if (node.crossLinkChildren.isNotEmpty()) {
        add("")
        add("Cross-linked children:", Yellow)
        node.crossLinkChildren.take(4).forEach { add("  ⇄ ${it.label ?: it.id}") }
    }
    val samples = node.queries.take(3)
    if (samples.isNotEmpty()) {
        add("")
        add("Sample queries:", Cyan)
        samples.forEach { q ->
            val wrapped = q.rawText.wrapText(width - 6)
            wrapped.forEachIndexed { i, line ->
                add(if (i == 0) "  · $line" else "    $line")
            }
        }
    }
    if (node.judgePrompt != null) {
        add("")
        add("Judge System Prompt:", Cyan, true)
        node.judgePrompt!!.wrapText(width - 6).forEach { line ->
            add("  $line")
        }
        if (node.judgeRubric != null) {
            add("")
            add("Judge Rubric:", Cyan, true)
            node.judgeRubric!!.wrapText(width - 6).forEach { line ->
                add("  $line")
            }
        }
    }
    if (isLoadingLeaderboard) {
        add("")
        add("─── LEADERBOARD ─────────────────────────────", Cyan, true)
        add("  Loading leaderboard data...", Yellow)
    } else if (leaderboard != null) {
        add("")
        val isAgg = !node.isLeaf
        val title = if (isAgg) "─── LEADERBOARD (aggregated) ─────────────────" else "─── LEADERBOARD ─────────────────────────────"
        add(title, Cyan, true)
        
        val scopeText = "  Scope: ${node.label ?: node.id} (${if (node.isLeaf) "leaf" else "${leaderboard.leafsTotal} leaves"})"
        add(scopeText, White)
        
        val relText = if (leaderboard.isReliable) "✔ reliable" else "⚠ unreliable"
        val coveragePercent = "%.0f%%".format((leaderboard.leafsEligible.toDouble() / leaderboard.leafsTotal.coerceAtLeast(1)) * 100)
        val covText = "  Coverage: ${leaderboard.leafsEligible}/${leaderboard.leafsTotal} leaves ($coveragePercent)  ·  ${leaderboard.totalComparisons} comparisons  ·  $relText"
        add(covText, if (leaderboard.isReliable) Green else Yellow)
        
        if (node.isLeaf && node.judgeGtAgreement != null) {
            val pct = "%.1f%%".format(node.judgeGtAgreement!! * 100)
            val warn = if (node.judgeGtAgreement!! < 0.55) "  ⚠ poor agreement (<55%)" else ""
            add("  Judge agreement: $pct$warn", if (node.judgeGtAgreement!! < 0.55) Red else Green)
        }
        
        add("")
        if (leaderboard.ranks.isEmpty()) {
            add("  No evaluations available.", Yellow)
        } else {
            if (isAgg) {
                // Header for aggregated: #  Model                    Score    SE     Weight
                add("  %-2s  %-24s %7s %7s     Weight".format("#", "Model", "Score", "SE"), Yellow, true)
                leaderboard.ranks.forEach { mr ->
                    val scoreStr = "%+6.2f".format(mr.btScore)
                    val seStr = "±%.2f".format(mr.stdError)
                    val maxWeight = leaderboard.ranks.map { 1.0 / (it.stdError * it.stdError) }.maxOrNull() ?: 1.0
                    val weight = 1.0 / (mr.stdError * mr.stdError)
                    val blockCount = if (maxWeight > 0.0) ((weight / maxWeight) * 8).toInt().coerceIn(1, 8) else 1
                    val bar = "█".repeat(blockCount).padEnd(8)
                    add("  %-2d  %-24s %7s %7s    [%s]".format(mr.rank, mr.modelId.take(24), scoreStr, seStr, bar), White)
                }
                
                if (!leaderboard.isReliable) {
                    add("")
                    add("  ℹ Coverage below 30% — run more benchmark rounds for reliable field ranking", Yellow)
                }
            } else {
                // Header for leaf: #  Model                    Score    SE      95% CI
                add("  %-2s  %-24s %7s %7s       95%% CI".format("#", "Model", "Score", "SE"), Yellow, true)
                leaderboard.ranks.forEach { mr ->
                    val scoreStr = "%+6.2f".format(mr.btScore)
                    val seStr = "±%.2f".format(mr.stdError)
                    val ciStr = "[%+4.1f, %+4.1f]".format(mr.confidenceIntervalLow, mr.confidenceIntervalHigh)
                    add("  %-2d  %-24s %7s %7s   %s".format(mr.rank, mr.modelId.take(24), scoreStr, seStr, ciStr), White)
                }
                
                val warnings = mutableListOf<String>()
                for (idx in 0 until leaderboard.ranks.size - 1) {
                    val m1 = leaderboard.ranks[idx]
                    val m2 = leaderboard.ranks[idx + 1]
                    val gap = Math.abs(m1.btScore - m2.btScore)
                    val threshold = Math.max(m1.stdError, m2.stdError)
                    if (gap < threshold) {
                        warnings.add("${shortModelName(m1.modelId)} and ${shortModelName(m2.modelId)} not separated (gap < 1 SE)")
                    }
                }
                if (warnings.isNotEmpty()) {
                    add("")
                    warnings.take(2).forEach { warn ->
                        add("  ⚠ $warn", Yellow)
                    }
                }
            }
        }
    }
    return out
}


@Composable
private fun MetricsThreeZone(
    width: Int,
    height: Int,
    history: List<IterationMetrics>,
    selectedIterationIndex: Int,
    focus: MetricsZoneFocus,
    showPerformanceBlock: Boolean,
    detailScrollOffset: Int,
    metricsScrollOffset: Int,
    performanceReport: Map<String, PerformanceStats>,
    dispatch: (TuiEvent) -> Unit,
) {
    val lastIdx = history.lastIndex
    val selResolved = if (selectedIterationIndex in 0..lastIdx) selectedIterationIndex else lastIdx

    val zone1H = (height * 0.4).toInt().coerceIn(4, (height - 4).coerceAtLeast(4))
    val bottomH = (height - zone1H).coerceAtLeast(4)
    val leftW = ((width - 1) / 2).coerceAtLeast(12)
    val rightW = (width - leftW - 1).coerceAtLeast(12)

    Column {
        Column(modifier = Modifier.height(zone1H).width(width)) {
            EvolutionTable(width, zone1H, history, selectedIterationIndex, focus, metricsScrollOffset, dispatch)
        }
        Row(modifier = Modifier.height(bottomH)) {
            Column(modifier = Modifier.width(leftW).height(bottomH)) {
                FinalMetrics(leftW, bottomH, history[lastIdx])
            }
            Spacer(Modifier.width(1).height(bottomH))
            Column(modifier = Modifier.width(rightW).height(bottomH)) {
                IterationDetail(
                    rightW, bottomH, history, selResolved, focus,
                    showPerformanceBlock, detailScrollOffset, performanceReport,
                    dispatch
                )
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Zone 1 — Evolution table
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun EvolutionTable(
    width: Int,
    height: Int,
    history: List<IterationMetrics>,
    selectedIterationIndex: Int,
    focus: MetricsZoneFocus,
    metricsScrollOffset: Int,
    dispatch: (TuiEvent) -> Unit,
) {
    val lastIdx = history.lastIndex
    val tableFocused = focus == MetricsZoneFocus.TABLE

    Text("◈ EVOLUTION  (${history.size} iters)", color = Cyan, textStyle = Bold)
    Text(tableHeader().take(width), color = White, textStyle = Bold)

    // Data rows are every iteration except the last, which is pinned as the Final row below.
    val dataCount = lastIdx
    // Reserve: title(1) header(1) divider(1) final(1) already; remaining for data rows.
    val visible = (height - 4).coerceAtLeast(1)

    ScrollablePanelContent(
        pWidth = width,
        pHeight = visible,
        itemCount = dataCount,
        scrollOffset = metricsScrollOffset,
        hasPadding = false,
        onScrollClamp = { dispatch(TuiEvent.ScrollTo(ScrollbarTarget.ANALYSIS, it)) }
    ) { visibleHeight, startIdx, innerWidth ->
        val endIdx = (startIdx + visibleHeight).coerceAtMost(dataCount)
        for (i in startIdx until endIdx) {
            val isSelected = i == selectedIterationIndex
            Text(tableRow(history, i, isSelected, tableFocused, isFinal = false).take(innerWidth), color = White)
        }
    }

    Text("─".repeat(width).take(width), color = Green)
    val finalSelected = selectedIterationIndex == -1 || selectedIterationIndex == lastIdx
    Text(tableRow(history, lastIdx, finalSelected, tableFocused, isFinal = true).take(width), color = Green)
}

private fun tableHeader(): String =
    "  " + String.format(
        Locale.US, "%-8s %5s %5s %7s %8s %7s %6s %8s",
        "Iter", "Nodes", "Leaf", "Equil%", "AncCor%", "Silhou", "AvgM", "Δ"
    )

private fun tableRow(
    history: List<IterationMetrics>,
    index: Int,
    isSelected: Boolean,
    tableFocused: Boolean,
    isFinal: Boolean,
): AnnotatedString {
    val m = history[index].metrics
    val rawLabel = history[index].iteration.takeIf { it.isNotBlank() } ?: "Iter ${index + 1}"
    val label = (if (isFinal) "★ " else "") + rawLabel
    val rowColor = when {
        isFinal -> Green
        isSelected -> Cyan
        else -> White
    }
    val cursor = if (isSelected && tableFocused) "> " else "  "
    val main = String.format(
        Locale.US, "%-8s %5d %5d %6.1f%% %7.1f%% %7.3f %6.2f ",
        label.take(8),
        m.totalNodes, m.leafNodes,
        m.equilibriumIndex * 100.0,
        m.ancestorCorrectRate * 100.0,
        m.sphericalSilhouette,
        m.avgMatchCount,
    )

    // Δ = change in ancestor-correct rate vs the previous iteration row.
    val delta: Pair<String, Color> = if (index <= 0) {
        "-" to rowColor
    } else {
        val d = (m.ancestorCorrectRate - history[index - 1].ancestorCorrectRate) * 100.0
        if (d >= 0.0) String.format(Locale.US, "▲+%.1f%%", d) to Green
        else String.format(Locale.US, "▼%.1f%%", d) to Red
    }

    return buildAnnotatedString {
        val style = if (isSelected) Bold else Unspecified
        withStyle(SpanStyle(color = rowColor, textStyle = style)) { append(cursor + main) }
        withStyle(SpanStyle(color = delta.second, textStyle = style)) { append(delta.first) }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Zone 2 — Pinned final metrics
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun FinalMetrics(width: Int, height: Int, entry: IterationMetrics) {
    Text("◈ FINAL RESULTS".take(width), color = Green, textStyle = Bold)
    val lines = buildMetricLines(entry.metrics)
    lines.take((height - 1).coerceAtLeast(0)).forEach { Text(it.take(width)) }
}

// ─────────────────────────────────────────────────────────────────────────────
// Zone 3 — Per-iteration detail (scrollable, optional performance block)
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun IterationDetail(
    width: Int,
    height: Int,
    history: List<IterationMetrics>,
    selResolved: Int,
    focus: MetricsZoneFocus,
    showPerformanceBlock: Boolean,
    detailScrollOffset: Int,
    performanceReport: Map<String, PerformanceStats>,
    dispatch: (TuiEvent) -> Unit,
) {
    val entry = history[selResolved]
    val isFinal = selResolved == history.lastIndex
    val headerText = if (isFinal) "◈ FINAL DETAIL" else "◈ ITER ${selResolved + 1} DETAIL"
    val headerColor = if (focus == MetricsZoneFocus.DETAIL) Cyan else White
    Text(headerText.take(width), color = headerColor, textStyle = Bold)

    val lines = buildMetricLines(entry.metrics).toMutableList()
    if (showPerformanceBlock) lines += performanceLines(performanceReport)

    val body = (height - 1).coerceAtLeast(1)

    ScrollablePanelContent(
        pWidth = width,
        pHeight = body,
        itemCount = lines.size,
        scrollOffset = detailScrollOffset,
        hasPadding = false,
        onScrollClamp = { dispatch(TuiEvent.ScrollTo(ScrollbarTarget.ANALYSIS, it)) }
    ) { visibleHeight, startIdx, innerWidth ->
        val sub = lines.subList(startIdx, (startIdx + visibleHeight).coerceAtMost(lines.size))
        sub.forEach { Text(it.take(innerWidth)) }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Shared metric-group rendering
// ─────────────────────────────────────────────────────────────────────────────

fun buildMetricLines(m: TaxonomyMetricsData): List<AnnotatedString> {
    val out = mutableListOf<AnnotatedString>()
    out += groupHeader("[Cluster Quality]", Magenta)
    out += metricLine("NMI", num(m.nmi), qcolor(m.nmi, 0.6, 0.4))
    out += metricLine("ARI", num(m.ari), qcolor(m.ari, 0.6, 0.4))
    out += metricLine("Dendrogram Purity", num(m.dendrogramPurity), qcolor(m.dendrogramPurity, 0.8, 0.5))
    out += metricLine("Wtd Leaf Purity", num(m.weightedLeafPurity), qcolor(m.weightedLeafPurity, 0.8, 0.5))
    out += metricLine("Edge F1", num(m.edgeF1), qcolor(m.edgeF1, 0.6, 0.4))
    // Triplet accuracy: higher is better. Dasgupta cost: lower is better (no fixed scale → neutral).
    out += metricLine("Triplet Acc", num(m.tripletAccuracy), qcolor(m.tripletAccuracy, 0.7, 0.5))
    out += metricLine("Dasgupta Cost", big(m.totalDasguptaCost), White)

    out += groupHeader("[Routing]", Cyan)
    out += metricLine("AncCorr", pct(m.ancestorCorrectRate), qcolor(m.ancestorCorrectRate, 0.8, 0.5))
    out += metricLine("H-P", num(m.hPrecision), qcolor(m.hPrecision, 0.6, 0.4))
    out += metricLine("H-R", num(m.hRecall), qcolor(m.hRecall, 0.6, 0.4))
    out += metricLine("H-F1", num(m.hF1), qcolor(m.hF1, 0.6, 0.4))
    out += metricLine("ECE", num(m.routingECE), qcolorLow(m.routingECE))
    out += metricLine("Residual", pct(m.residualRatio), qcolorLow(m.residualRatio))
    out += metricLine("Avg Match", num(m.avgMatchCount), White)

    out += groupHeader("[Structure]", Yellow)
    out += metricLine("Equilibrium", pct(m.equilibriumIndex), White)
    out += metricLine("Avg Leaf Depth", num(m.avgLeafDepth), White)
    // Normalised Sackin index (Sackin 1972; Fischer et al. 2021) — mean root-to-leaf depth.
    out += metricLine("Sackin (norm)", num(m.normalisedSackin), White)
    out += metricLine("Contamination", pct(m.contaminationRatio), qcolorLow(m.contaminationRatio))
    out += metricLine("Cross-Domain", m.crossDomainNodes.toString(), White)
    return out
}

fun performanceLines(report: Map<String, PerformanceStats>): List<AnnotatedString> {
    val out = mutableListOf<AnnotatedString>()
    out += groupHeader("[Performance]", Cyan)
    if (report.isEmpty()) {
        out += metricLine("(no timings)", "-", White)
        return out
    }
    report.entries.sortedByDescending { it.value.totalMs }.take(8).forEach { (phase, stats) ->
        out += metricLine(phase.take(20), "${stats.totalMs}ms /${stats.calls}", White)
    }
    return out
}

private fun groupHeader(text: String, color: Color): AnnotatedString =
    buildAnnotatedString { withStyle(SpanStyle(color = color, textStyle = Bold)) { append(text) } }

private fun metricLine(label: String, value: String, valueColor: Color): AnnotatedString =
    buildAnnotatedString {
        withStyle(SpanStyle(color = White)) { append("  " + label.padEnd(18)) }
        withStyle(SpanStyle(color = valueColor)) { append(value) }
    }

private fun pct(d: Double) = String.format(Locale.US, "%.1f%%", d * 100.0)
private fun num(d: Double) = String.format(Locale.US, "%.4f", d)

/** Compact formatter for large unbounded magnitudes (e.g. total Dasgupta cost). */
private fun big(d: Double): String = when {
    d >= 1_000_000.0 -> String.format(Locale.US, "%.2fM", d / 1_000_000.0)
    d >= 1_000.0     -> String.format(Locale.US, "%.2fk", d / 1_000.0)
    else             -> String.format(Locale.US, "%.1f", d)
}

/** Higher is better: green above [good], yellow above [mid], red below. */
private fun qcolor(v: Double, good: Double, mid: Double): Color = when {
    v >= good -> Green
    v >= mid -> Yellow
    else -> Red
}

/** Lower is better (contamination / residual ratios). */
private fun qcolorLow(ratio: Double): Color = when {
    ratio < 0.05 -> Green
    ratio < 0.15 -> Yellow
    else -> Red
}

private fun String.wrapText(maxWidth: Int): List<String> {
    val limit = maxWidth.coerceAtLeast(10)
    val lines = mutableListOf<String>()
    val paragraphs = this.split('\n', '\r')
    for (paragraph in paragraphs) {
        val words = paragraph.split(' ')
        var currentLine = java.lang.StringBuilder()
        for (word in words) {
            if (word.length > limit) {
                if (currentLine.isNotEmpty()) {
                    lines.add(currentLine.toString())
                    currentLine = java.lang.StringBuilder()
                }
                var start = 0
                while (start < word.length) {
                    val end = minOf(start + limit, word.length)
                    lines.add(word.substring(start, end))
                    start = end
                }
                continue
            }
            if (currentLine.isEmpty()) {
                currentLine.append(word)
            } else if (currentLine.length + 1 + word.length <= limit) {
                currentLine.append(' ').append(word)
            } else {
                lines.add(currentLine.toString())
                currentLine = java.lang.StringBuilder(word)
            }
        }
        if (currentLine.isNotEmpty() || paragraph.isEmpty()) {
            lines.add(currentLine.toString())
        }
    }
    return lines
}

