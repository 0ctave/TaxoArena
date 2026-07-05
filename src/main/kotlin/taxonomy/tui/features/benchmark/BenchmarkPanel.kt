package taxonomy.tui.features.benchmark

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Row
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import com.jakewharton.mosaic.ui.TextStyle.Companion.Unspecified
import taxonomy.tui.components.HotkeyAction
import taxonomy.service.AnalysisPanelState
import taxonomy.tui.components.DomainSelectorTable
import taxonomy.tui.components.Panel
import taxonomy.tui.components.ScrollablePanelContent
import taxonomy.tui.components.SettingItem
import taxonomy.tui.components.SettingKind
import taxonomy.tui.components.TuiTheme
import taxonomy.tui.components.take
import taxonomy.tui.components.checkboxMark
import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.state.BenchmarkLiveView
import taxonomy.tui.state.BenchmarkSubScreen
import taxonomy.tui.state.BenchmarkSection
import taxonomy.tui.state.BenchmarkType
import taxonomy.tui.state.BenchmarkUiState
import taxonomy.tui.state.ScrollbarTarget

@Composable
fun BenchmarkPanel(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
    scrollOffset: Int,
    benchmarkState: BenchmarkUiState,
    availableDomains: List<Pair<String, Int>> = emptyList(),
    dispatch: (TuiEvent) -> Unit,
) {
    when (benchmarkState.benchmarkType) {
        BenchmarkType.NONE -> BenchmarkTypeSelector(width, benchmarkState)
        BenchmarkType.ARENA -> ArenaBenchmarkView(width, height, controlState, scrollOffset, benchmarkState, availableDomains, dispatch)
        BenchmarkType.TRICKLE -> TrickleBenchmarkView(width, height, benchmarkState)
    }
}

/** Entry screen: pick which evaluation to run. */
@Composable
private fun BenchmarkTypeSelector(width: Int, benchmarkState: BenchmarkUiState) {
    val w = (width - 1).coerceAtLeast(1)
    val options = listOf(
        "ARENA" to "Multi-model pairwise eval over MMLU-Pro",
        "TRICKLE" to "Batch routing accuracy test over reserved queries",
    )
    Column {
        Text("BENCHMARK SUITE".take(w), color = Cyan, textStyle = Bold)
        Spacer()
        Text("Select a benchmark type:".take(w), color = White)
        Spacer()
        options.forEachIndexed { idx, (name, desc) ->
            val selected = idx == benchmarkState.benchmarkTypeSelectionIndex
            Text(
                buildAnnotatedString {
                    withStyle(SpanStyle(color = Yellow, textStyle = Bold)) {
                        append(if (selected) "❯ " else "  ")
                    }
                    withStyle(
                        SpanStyle(
                            color = if (selected) Cyan else White,
                            textStyle = if (selected) Bold else Unspecified
                        )
                    ) { append("[$name] ") }
                    withStyle(SpanStyle(color = White)) { append(desc) }
                }.take(w)
            )
        }
    }
}

/**
 * Per-model ingestion picker overlay (the [O] hotkey). Shared by the Arena and Benchmark hub views.
 */
@Composable
fun EvalCatalogPicker(
    width: Int,
    height: Int,
    benchmarkState: BenchmarkUiState,
) {
    val w = (width - 1).coerceAtLeast(1)
    Column {
        Text("SELECT EVAL_RESULTS TO INGEST".take(w), color = Cyan, textStyle = Bold)
        Spacer()
        val catalog = benchmarkState.evalCatalog.filter { !it.alreadyIngested }
        if (catalog.isEmpty()) {
            Text("No eval_results found in the cache directory.".take(w), color = Yellow)
            Spacer()
            Text("Press D to download the MMLU-Pro eval_results, or Q to Quit.".take(w), color = Cyan)
            return@Column
        }
        val selectedCount = benchmarkState.evalCatalogSelection.size
        Text("$selectedCount selected · ${catalog.size} available".take(w), color = White)
        Spacer()
        val rows = (height - 5).coerceAtLeast(1)
        val start = (benchmarkState.evalCatalogCursor - rows + 1).coerceAtLeast(0)
        catalog.drop(start).take(rows).forEachIndexed { offset, entry ->
            val idx = start + offset
            val isCursor = idx == benchmarkState.evalCatalogCursor
            val checked = entry.modelName in benchmarkState.evalCatalogSelection
            val sizeMb = entry.sizeBytes.toDouble() / (1024 * 1024)
            val ingested = if (entry.alreadyIngested) " (ingested)" else ""
            Text(
                buildAnnotatedString {
                    withStyle(SpanStyle(color = Yellow, textStyle = Bold)) {
                        append(if (isCursor) "❯ " else "  ")
                    }
                    withStyle(SpanStyle(color = if (checked) Green else White)) {
                        append("${checkboxMark(checked)} ")
                    }
                    withStyle(
                        SpanStyle(
                            color = if (isCursor) Cyan else White,
                            textStyle = if (isCursor) Bold else Unspecified
                        )
                    ) { append(entry.modelName) }
                    withStyle(SpanStyle(color = White)) {
                        append(" · ${"%.1f MB".format(sizeMb)}$ingested")
                    }
                }.take(w)
            )
        }
        Spacer()
        Text("A all-new · Space toggle · Enter ingest · D download · Q Quit".take(w), color = Cyan)
    }
}

@Composable
private fun ArenaBenchmarkView(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
    scrollOffset: Int,
    benchmarkState: BenchmarkUiState,
    availableDomains: List<Pair<String, Int>>,
    dispatch: (TuiEvent) -> Unit,
) {
    val w = (width - 1).coerceAtLeast(1)
    val isLive = benchmarkState.benchmarkSubScreen == BenchmarkSubScreen.RESULTS || controlState.isRunningBenchmark
    Column {
        if (benchmarkState.loadedModels.isNotEmpty()) {
            Text("Loaded models: ${benchmarkState.loadedModels.size} models eval results", color = Green)
        } else {
            Text("No precomputed models loaded — press O to load eval_results.".take(w), color = Yellow)
        }
        Spacer()

        when {
            benchmarkState.isDownloadingEval -> {
                Text("Downloading MMLU-Pro eval_results…".take(w), color = Yellow)
                val files = benchmarkState.evalDownloadProgress
                if (files.isEmpty()) {
                    Text("Fetching file listing from GitHub…".take(w), color = White)
                } else {
                    val done = files.values.count { it >= 1f }
                    Text("Downloaded $done / ${files.size} files".take(w), color = White)
                    files.entries.take((height - 4).coerceAtLeast(1)).forEach { (name, pct) ->
                        Text("  ${name.take((width - 12).coerceAtLeast(1))}  ${"%.0f%%".format(pct * 100)}".take(w), color = White)
                    }
                }
            }

            benchmarkState.evalLoaderIsRunning -> {
                Text("Loading eval results...".take(w), color = White)
                if (benchmarkState.evalLoadingModelCount > 0) {
                    val i = benchmarkState.evalLoadingModelIdx + 1
                    val n = benchmarkState.evalLoadingModelCount
                    val cur = benchmarkState.evalLoadingCurrentModel.ifBlank { "…" }
                    val items = if (benchmarkState.evalLoadingItemTotal > 0)
                        " · items ${benchmarkState.evalLoadingItem}/${benchmarkState.evalLoadingItemTotal}"
                    else ""
                    Text("$cur  $i/$n$items".take(w), color = White)
                } else if (benchmarkState.evalLoaderStatus.isNotBlank()) {
                    Text(benchmarkState.evalLoaderStatus.take(w), color = White)
                }
            }

            isLive -> ArenaBenchmarkLiveView(w, height, controlState, benchmarkState, dispatch)

            else -> ArenaBenchmarkConfig(width, height - 3, scrollOffset, benchmarkState, availableDomains, dispatch)
        }

        Spacer()
    }
}

@Composable
private fun ArenaBenchmarkConfig(
    width: Int,
    height: Int,
    scrollOffset: Int,
    b: BenchmarkUiState,
    availableDomains: List<Pair<String, Int>>,
    dispatch: (TuiEvent) -> Unit,
) {
    val w = (width - 1).coerceAtLeast(1)
    val domainsList = availableDomains.map { it.first }
    val settingItems = buildArenaSettingItems(b, domainsList, dispatch)
    Panel(
        title = "ARENA BENCHMARK CONFIGURATION",
        accentColor = TuiTheme.panelAccent(true),
        width = width,
        height = height
    ) {
        Column(modifier = Modifier.padding(left = 2, top = 1)) {
            val totalLines = mutableListOf<@Composable () -> Unit>()

            settingItems.forEachIndexed { idx, item ->
                val selected = b.selectedBenchmarkField == idx
                val caret = if (selected) "❯ " else "  "
                val isRunBenchmark = item.name == "Run benchmark"
                val color = if (selected) {
                    if (isRunBenchmark) TuiTheme.RUNNING else TuiTheme.ACCENT
                } else {
                    if (isRunBenchmark) {
                        val ready = b.benchmarkSelectedModels.size >= 2
                        if (ready) Green else Yellow
                    } else {
                        White
                    }
                }
                val textStyle = if (selected || isRunBenchmark) Bold else Unspecified

                val displayValue = when (item.name) {
                    "Query limit" -> {
                        val ql = item.getValue().ifBlank { "0" }
                        if (selected && b.isEditingBenchmarkField) {
                            b.benchmarkEditingValue + "█"
                        } else {
                            "$ql${if (ql == "0") " (all)" else ""}"
                        }
                    }
                    "Parallelism" -> {
                        if (selected && b.isEditingBenchmarkField) {
                            b.benchmarkEditingValue + "█"
                        } else {
                            item.getValue()
                        }
                    }
                    "Select models" -> "${item.getValue()} selected"
                    "Select domains" -> "${item.getValue()} selected"
                    "Run benchmark" -> {
                        val ready = b.benchmarkSelectedModels.size >= 2
                        if (ready) "▶ Run benchmark" else "Select ≥2 models first"
                    }
                    else -> item.getValue()
                }

                val lineText = if (isRunBenchmark) {
                    val ready = b.benchmarkSelectedModels.size >= 2
                    if (ready) "${caret}▶ Run benchmark" else "${caret}Select ≥2 models first"
                } else {
                    "${caret}${item.name}: $displayValue"
                }

                totalLines.add {
                    Text(
                        value = lineText.take(w - 4),
                        color = color,
                        textStyle = textStyle
                    )
                }
            }

            val meta = b.savedBenchmarkMetadata
            if (b.hasSavedBenchmark && meta != null) {
                totalLines.add { Spacer() }
                totalLines.add { Text("".padEnd(w - 4, '─'), color = Yellow) }
                totalLines.add { Spacer() }
                totalLines.add { Text("⚠ Saved unfinished benchmark detected:".take(w - 4), color = Yellow, textStyle = Bold) }
                totalLines.add { Text("  Models: ${meta.models.joinToString(", ")}".take(w - 4), color = Yellow) }
                totalLines.add { Text("  Limit: ${meta.queryLimit} | Cat: ${meta.category ?: "all"} | Gate: ${meta.confidenceGate} | Par: ${meta.parallelism}".take(w - 4), color = Yellow) }
                totalLines.add { Spacer() }
                totalLines.add { Text("Press [R] to resume previous benchmark session".take(w - 4), color = Yellow, textStyle = Bold) }
                totalLines.add { Text("Press [L] to copy/restore these settings to inputs above".take(w - 4), color = Yellow) }
            } else if (b.hasSavedBenchmark) {
                totalLines.add { Spacer() }
                totalLines.add { Text("".padEnd(w - 4, '─'), color = Yellow) }
                totalLines.add { Spacer() }
                totalLines.add { Text("⚠ Saved unfinished benchmark detected from previous session!".take(w - 4), color = Yellow, textStyle = Bold) }
                totalLines.add { Text("Press [R] to resume previous benchmark session (recover offsets & results)".take(w - 4), color = Yellow) }
            }

            val visibleHeight = (height - 2).coerceAtLeast(1)
            totalLines.drop(scrollOffset).take(visibleHeight).forEach { it() }
        }
    }
}

@Composable
private fun ArenaBenchmarkLiveView(
    w: Int,
    height: Int,
    controlState: AnalysisPanelState,
    b: BenchmarkUiState,
    dispatch: (TuiEvent) -> Unit,
) {
    val running = controlState.isRunningBenchmark
    val report = controlState.benchmarkReport
    val live = controlState.benchmarkLiveStats ?: b.liveStats

    // Top Panel: STATUS
    val topH = 5
    val bottomH = (height - topH).coerceAtLeast(3)

    Column {
        if (report != null) {
            // COMPLETE STATUS PANEL
            Panel(
                title = "BENCHMARK STATUS · COMPLETE",
                accentColor = TuiTheme.OK,
                width = w,
                height = topH
            ) {
                Column {
                    val pct = 100
                    val bar = "█".repeat(20)
                    Text("Progress: ${live?.processed ?: report.totalQueries}/${live?.total ?: report.totalQueries} [$bar] $pct% · COMPLETE".take(w - 4), color = Green, textStyle = Bold)
                    Text("Queries: ${report.totalQueries} · Pairs: ${report.totalModelPairs} · Coverage: ${"%.1f%%".format(report.coverageRate * 100)}".take(w - 4), color = White)
                }
            }
        } else if (live != null) {
            // RUNNING STATUS PANEL
            Panel(
                title = "BENCHMARK STATUS · RUNNING",
                accentColor = TuiTheme.RUNNING,
                width = w,
                height = topH
            ) {
                Column {
                    val pct = if (live.total > 0) live.processed * 100 / live.total else 0
                    val filled = (pct / 5).coerceIn(0, 20)
                    val bar = "█".repeat(filled) + "░".repeat(20 - filled)
                    Text("Progress: ${live.processed}/${live.total} [$bar] $pct% · Round: ${live.currentRound}".take(w - 4), color = Cyan, textStyle = Bold)
                    val targetStr = if (live.activeTargets.isNotEmpty()) " · Targets: ${live.activeTargets.joinToString(", ")}" else ""
                    Text("Agreement: ${"%.1f%%".format(live.runningAgreement * 100)}$targetStr".take(w - 4), color = White)
                }
            }
        } else {
            Panel(
                title = "BENCHMARK STATUS · STARTING",
                accentColor = TuiTheme.RUNNING,
                width = w,
                height = topH
            ) {
                Text("Waiting for live benchmark stats…".take(w - 4), color = Yellow)
            }
        }

        Spacer()

        // Bottom panels
        if (w >= 90) {
            val leftColW = 46
            val rightColW = w - leftColW
            
            val showHeaders = bottomH >= 6
            val leftBodyRows = if (showHeaders) {
                (bottomH - 5).coerceAtLeast(1)
            } else {
                (bottomH - 3).coerceAtLeast(1)
            }

            val rightBodyRows = if (showHeaders) {
                (bottomH - 5).coerceAtLeast(1)
            } else {
                (bottomH - 3).coerceAtLeast(1)
            }

            Row {
                // Bottom Left: Leaderboard
                val sortedModels = if (report != null) {
                    val accs = modelAccuracies(report)
                    if (live?.btRatings?.isNotEmpty() == true) {
                        live.btRatings.entries.sortedByDescending { it.value }
                    } else {
                        accs.map { java.util.AbstractMap.SimpleEntry(it.first, 0.0) }
                    }
                } else if (live != null && live.btRatings.isNotEmpty()) {
                    live.btRatings.entries.sortedByDescending { it.value }
                } else {
                    b.benchmarkSelectedModels.map { java.util.AbstractMap.SimpleEntry(it, 0.0) }
                }

                Panel(
                    title = if (report != null) "FINAL BT LEADERBOARD" else "LIVE BT LEADERBOARD",
                    accentColor = TuiTheme.panelAccent(true),
                    width = leftColW,
                    height = bottomH
                ) {
                    Column {
                        if (showHeaders) {
                            val headerLine = "%-24s | %8s | %6s".format("Model", "BT Score", "StdErr")
                            Text(headerLine.take(leftColW - 4), color = Cyan, textStyle = Bold)
                            Text("-".repeat((leftColW - 4).coerceAtLeast(1)), color = White)
                        }

                        ScrollablePanelContent(
                            pWidth = leftColW - 4,
                            pHeight = leftBodyRows,
                            itemCount = sortedModels.size,
                            scrollOffset = b.benchmarkScrollOffset,
                            hasPadding = false,
                            onScrollClamp = null
                        ) { visibleHeight, startIdx, innerW ->
                            val end = (startIdx + visibleHeight).coerceAtMost(sortedModels.size)
                            for (i in startIdx until end) {
                                val entry = sortedModels[i]
                                val model = entry.key
                                val score = entry.value
                                val se = live?.btErrors?.get(model) ?: 0.0
                                val rowStr = "%-24s | %8.3f | %6.3f".format(model.take(24), score, se)
                                Text(rowStr.take(innerW), color = White, modifier = Modifier.height(1))
                            }
                            val emptyRows = visibleHeight - (end - startIdx)
                            repeat(emptyRows.coerceAtLeast(0)) {
                                Text(" ".repeat(innerW), modifier = Modifier.height(1))
                            }
                        }
                    }
                }

                Spacer()

                // Bottom Right: Matchups Progress or Accuracy
                Panel(
                    title = if (report != null) "MODEL ACCURACY (GT)" else "MATCHUPS PROGRESS",
                    accentColor = TuiTheme.panelAccent(true),
                    width = rightColW,
                    height = bottomH
                ) {
                    Column {
                        if (report != null) {
                            val accs = modelAccuracies(report)
                            
                            if (showHeaders) {
                                val headerLine = "%-20s | %s".format("Model", "Accuracy Bar")
                                Text(headerLine.take(rightColW - 4), color = Cyan, textStyle = Bold)
                                Text("-".repeat((rightColW - 4).coerceAtLeast(1)), color = White)
                            }

                            ScrollablePanelContent(
                                pWidth = rightColW - 4,
                                pHeight = rightBodyRows,
                                itemCount = accs.size,
                                scrollOffset = b.benchmarkScrollOffset,
                                hasPadding = false,
                                onScrollClamp = { dispatch(TuiEvent.ScrollTo(ScrollbarTarget.ANALYSIS, it)) }
                            ) { visibleHeight, startIdx, innerW ->
                                val end = (startIdx + visibleHeight).coerceAtMost(accs.size)
                                for (i in startIdx until end) {
                                    val (model, acc) = accs[i]
                                    val barLen = ((innerW - 28).coerceAtLeast(5) * acc).toInt()
                                    val bar = "█".repeat(barLen)
                                    val rowStr = "%-20s | %s %5.1f%%".format(model.take(20), bar.padEnd((innerW - 28).coerceAtLeast(5)), acc * 100)
                                    Text(rowStr.take(innerW), color = Green, modifier = Modifier.height(1))
                                }
                                val emptyRows = visibleHeight - (end - startIdx)
                                repeat(emptyRows.coerceAtLeast(0)) {
                                    Text(" ".repeat(innerW), modifier = Modifier.height(1))
                                }
                            }
                        } else if (live != null) {
                            val pairStats = live.pairStats

                            val innerRightW = rightColW - 4
                            val isWide = innerRightW >= 56
                            if (showHeaders) {
                                val headerLine = if (isWide) {
                                    "%-18s vs %-18s | %5s %5s %5s | %5s".format("Model A", "Model B", "WinsA", "WinsB", "Ties", "Agree")
                                } else {
                                    "%-12s vs %-12s | %s".format("Model A", "Model B", "W/L/T")
                                }
                                Text(headerLine.take(innerRightW), color = Cyan, textStyle = Bold)
                                Text("-".repeat(innerRightW), color = White)
                            }

                            ScrollablePanelContent(
                                pWidth = rightColW - 4,
                                pHeight = rightBodyRows,
                                itemCount = pairStats.size,
                                scrollOffset = b.benchmarkScrollOffset,
                                hasPadding = false,
                                onScrollClamp = { dispatch(TuiEvent.ScrollTo(ScrollbarTarget.ANALYSIS, it)) }
                            ) { visibleHeight, startIdx, innerW ->
                                val end = (startIdx + visibleHeight).coerceAtMost(pairStats.size)
                                for (i in startIdx until end) {
                                    val ps = pairStats[i]
                                    val rowStr = if (isWide) {
                                        "%-18s vs %-18s | %5d %5d %5d | %5.0f%%".format(
                                            ps.modelA.take(18),
                                            ps.modelB.take(18),
                                            ps.judgeWinsA,
                                            ps.judgeWinsB,
                                            ps.judgeTies,
                                            ps.judgeAccuracyAgreementRate * 100
                                        )
                                    } else {
                                        "%-12s vs %-12s | %d/%d/%d".format(
                                            ps.modelA.take(12),
                                            ps.modelB.take(12),
                                            ps.judgeWinsA,
                                            ps.judgeWinsB,
                                            ps.judgeTies
                                        )
                                    }
                                    Text(rowStr.take(innerW), color = White, modifier = Modifier.height(1))
                                }
                                val emptyRows = visibleHeight - (end - startIdx)
                                repeat(emptyRows.coerceAtLeast(0)) {
                                    Text(" ".repeat(innerW), modifier = Modifier.height(1))
                                }
                            }
                        } else {
                            Text("No matchup progress available yet.", color = Yellow)
                        }
                    }
                }
            }
        } else {
            // Narrow Layout
            val narrowInnerH = bottomH - 3
            val narrowBodyRows = narrowInnerH.coerceAtLeast(1)

            Panel(
                title = if (report != null) "RESULTS" else "LIVE RESULTS",
                accentColor = TuiTheme.panelAccent(true),
                width = w,
                height = bottomH
            ) {
                if (report != null) {
                    val accs = modelAccuracies(report)
                    ScrollablePanelContent(
                        pWidth = w - 4,
                        pHeight = narrowBodyRows,
                        itemCount = accs.size,
                        scrollOffset = b.benchmarkScrollOffset,
                        hasPadding = false,
                        onScrollClamp = { dispatch(TuiEvent.ScrollTo(ScrollbarTarget.ANALYSIS, it)) }
                    ) { visibleHeight, startIdx, innerW ->
                        val end = (startIdx + visibleHeight).coerceAtMost(accs.size)
                        for (i in startIdx until end) {
                            val (model, acc) = accs[i]
                            Text("• ${model.take(20)}: ${"%.1f%%".format(acc * 100)}".take(innerW), color = Green, modifier = Modifier.height(1))
                        }
                        val emptyRows = visibleHeight - (end - startIdx)
                        repeat(emptyRows.coerceAtLeast(0)) {
                            Text(" ".repeat(innerW), modifier = Modifier.height(1))
                        }
                    }
                } else if (live != null) {
                    val pairStats = live.pairStats
                    ScrollablePanelContent(
                        pWidth = w - 4,
                        pHeight = narrowBodyRows,
                        itemCount = pairStats.size,
                        scrollOffset = b.benchmarkScrollOffset,
                        hasPadding = false,
                        onScrollClamp = { dispatch(TuiEvent.ScrollTo(ScrollbarTarget.ANALYSIS, it)) }
                    ) { visibleHeight, startIdx, innerW ->
                        val end = (startIdx + visibleHeight).coerceAtMost(pairStats.size)
                        for (i in startIdx until end) {
                            val ps = pairStats[i]
                            Text("${ps.modelA.take(12)} vs ${ps.modelB.take(12)} | ${ps.judgeWinsA}/${ps.judgeWinsB}/${ps.judgeTies}".take(innerW), color = White, modifier = Modifier.height(1))
                        }
                        val emptyRows = visibleHeight - (end - startIdx)
                        repeat(emptyRows.coerceAtLeast(0)) {
                            Text(" ".repeat(innerW), modifier = Modifier.height(1))
                        }
                    }
                } else {
                    Text("No progress stats yet.".take(w - 4), color = Yellow)
                }
            }
        }
    }
}

private fun modelAccuracies(report: taxonomy.model.BenchmarkReport): List<Pair<String, Double>> {
    val correct = mutableMapOf<String, Int>()
    val total = mutableMapOf<String, Int>()
    report.queryResults.forEach { r ->
        r.modelCorrect.forEach { (m, ok) ->
            total[m] = (total[m] ?: 0) + 1
            if (ok) correct[m] = (correct[m] ?: 0) + 1
        }
    }
    return total.keys.sortedByDescending { (correct[it] ?: 0).toDouble() / (total[it] ?: 1) }
        .map { it to (correct[it] ?: 0).toDouble() / (total[it] ?: 1) }
}

@Composable
private fun TrickleBenchmarkView(
    width: Int,
    height: Int,
    benchmarkState: BenchmarkUiState,
) {
    val w = (width - 1).coerceAtLeast(1)
    Column {
        when {
            benchmarkState.isRunningBatchTrickleTest -> {
                Text("Trickle Benchmark ❯ Executing".take(w), color = Yellow, textStyle = Bold)
                Spacer()
                Text("Running batch trickle test over reserved queries…".take(w), color = White)
                if (benchmarkState.batchTrickleProgress.isNotBlank()) {
                    Spacer()
                    Text(benchmarkState.batchTrickleProgress.take(w), color = Cyan)
                }
            }

            benchmarkState.isEnteringTrickleQueryLimit -> {
                Text("Trickle Benchmark Configuration".take(w), color = Cyan, textStyle = Bold)
                Spacer()
                Text("Enter the number of reserved test queries to evaluate:".take(w), color = White)
                Spacer()
                Text("Query Limit ❯ ${benchmarkState.trickleQueryLimitInput}█".take(w), color = Cyan)
                Spacer()
                Text("Press Enter to execute the test · Esc to cancel".take(w), color = Yellow)
            }

            benchmarkState.batchTrickleResults != null -> {
                val r = benchmarkState.batchTrickleResults
                Text("Batch Trickle Evaluation Results".take(w), color = Green, textStyle = Bold)
                Spacer()
                Text("Each leaf is tagged with its training queries' dominant MMLU-Pro domain.".take(w), color = White)
                Text("Reserved test queries are routed through the DAG and matched against tags.".take(w), color = White)
                Spacer()
                
                Text("%-22s %s".format("Total Evaluated Queries", r.totalQueries).take(w), color = White)
                Text("%-22s %.1f%%".format("Top-1 Match Accuracy", r.top1Accuracy * 100).take(w), color = White)
                Text("%-22s %.1f%%".format("Any-Match Accuracy", r.anyMatchAccuracy * 100).take(w), color = White)
                Text("%-22s %.3f".format("Macro-F1 Score", r.macroF1).take(w), color = White)
                Text("%-22s %.3f".format("Mean Leaf Purity", r.meanLeafPurity).take(w), color = White)
                Text("%-22s %.2f".format("Mean Routing Depth", r.meanRoutingDepth).take(w), color = White)
                Text("%-22s %.1f%%".format("No-Match Rate", r.noMatchRate * 100).take(w), color = White)

                if (r.perDomainF1.isNotEmpty()) {
                    Spacer()
                    Text("Per-Domain F1 Metrics (Top 10 by support)".take(w), color = Cyan, textStyle = Bold)
                    Text(
                        "%-22s %7s %6s %6s %6s".format("Domain", "Support", "P", "R", "F1").take(w),
                        color = Yellow,
                    )
                    r.perDomainF1.entries
                        .sortedByDescending { it.value.support }
                        .take(10)
                        .forEach { (domain, f1) ->
                            Text(
                                "%-22s %7d %6.2f %6.2f %6.2f".format(
                                    domain.take(22), f1.support, f1.precision, f1.recall, f1.f1
                                ).take(w),
                                color = White,
                            )
                        }
                }

                Spacer()
                Text("Press Enter to configure and re-run · Esc/Q to go back.".take(w), color = Yellow)
            }

            else -> {
                Text("Trickle Routing Benchmark".take(w), color = Cyan, textStyle = Bold)
                Spacer()
                Text("Runs a batch classification/routing accuracy test over reserved test queries".take(w), color = White)
                Text("to evaluate tree structure quality and node-routing purity.".take(w), color = White)
                Spacer()
                Text("Press Enter to configure and start the benchmark.".take(w), color = Yellow)
                Text("Press Q/Esc to return to the menu.".take(w), color = Cyan)
            }
        }
    }
}
