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
import taxonomy.service.AnalysisPanelState
import taxonomy.tui.components.DomainSelectorTable
import taxonomy.tui.components.Panel
import taxonomy.tui.components.SettingItem
import taxonomy.tui.components.SettingKind
import taxonomy.tui.components.TuiTheme
import taxonomy.tui.components.take
import taxonomy.tui.components.checkboxMark
import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.state.BenchmarkLiveView
import taxonomy.tui.state.BenchmarkSection
import taxonomy.tui.state.BenchmarkType
import taxonomy.tui.state.BenchmarkUiState

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
    val isLive = controlState.isRunningBenchmark || controlState.benchmarkReport != null
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

            isLive -> ArenaBenchmarkLiveView(w, height, controlState, benchmarkState)

            else -> ArenaBenchmarkConfig(width, height - 3, benchmarkState, availableDomains, dispatch)
        }

        Spacer()
    }
}

@Composable
private fun ArenaBenchmarkConfig(
    width: Int,
    height: Int,
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

                Text(
                    value = lineText.take(w - 4),
                    color = color,
                    textStyle = textStyle
                )
            }
        }
    }
}

@Composable
private fun ArenaBenchmarkLiveView(
    w: Int,
    height: Int,
    controlState: AnalysisPanelState,
    b: BenchmarkUiState,
) {
    val running = controlState.isRunningBenchmark
    val report = controlState.benchmarkReport
    Text(
        "BENCHMARK · ${if (running) "running" else "complete"} · view: ${b.benchmarkLiveView}".take(w),
        color = Cyan, textStyle = Bold,
    )
    when (b.benchmarkLiveView) {
        BenchmarkLiveView.SUMMARY -> {
            b.liveStats?.let { live ->
                val pct = if (live.total > 0) live.processed * 100 / live.total else 0
                Text("Progress: ${live.processed}/${live.total} ($pct%)".take(w), color = White)
                Text(
                    ("Agreement ${"%.2f".format(live.runningAgreement)} · " +
                        "Coverage ${"%.2f".format(live.runningCoverage)}").take(w),
                    color = White,
                )
                if (live.pairStats.isNotEmpty()) {
                    Spacer()
                    Text("Pair Matchups Progress:".take(w), color = Yellow, textStyle = Bold)
                    Text(
                        "%-18s vs %-18s | %5s %5s %5s | %5s".format(
                            "Model A", "Model B", "WinsA", "WinsB", "Ties", "Agree"
                        ).take(w),
                        color = Cyan
                    )
                    val rowsCount = (height - 9).coerceAtLeast(1)
                    live.pairStats.take(rowsCount).forEach { ps ->
                        Text(
                            "%-18s vs %-18s | %5d %5d %5d | %5.0f%%".format(
                                ps.modelA.take(18),
                                ps.modelB.take(18),
                                ps.judgeWinsA,
                                ps.judgeWinsB,
                                ps.judgeTies,
                                ps.judgeAccuracyAgreementRate * 100
                            ).take(w),
                            color = White
                        )
                    }
                } else if (live.perCategoryProgress.isNotEmpty()) {
                    Text("Per-category:".take(w), color = Yellow)
                    live.perCategoryProgress.entries.take((height - 7).coerceAtLeast(1)).forEach { (cat, n) ->
                        Text("  ${cat.take(20).padEnd(20)} $n".take(w), color = White)
                    }
                }
            }
            if (report != null) {
                Text("Queries ${report.totalQueries} · pairs ${report.totalModelPairs}".take(w), color = White)
                modelAccuracies(report).forEach { (model, acc) ->
                    val bar = "█".repeat((acc * 20).toInt().coerceIn(0, 20))
                    Text("  ${model.take(16).padEnd(16)} ${bar.padEnd(20)} ${"%.0f%%".format(acc * 100)}".take(w), color = Green)
                }
            } else if (running) {
                Text("Model accuracy: streaming…".take(w), color = White)
            }
        }

        BenchmarkLiveView.STREAM -> {
            if (report != null) {
                report.queryResults.takeLast(10).forEach { r ->
                    val answers = r.modelAnswers.entries.joinToString(" ") { (m, a) ->
                        val ok = r.modelCorrect[m] == true
                        "${m.take(8)}:$a${if (ok) "✓" else "✗"}"
                    }
                    Text("• ${r.query.take(28)} | GT:${r.gtCorrectAnswer} | $answers".take(w), color = White)
                }
            } else {
                b.liveStats?.let { live ->
                    Text("Now: ${live.currentQuestion.take((w - 6).coerceAtLeast(1))}".take(w), color = White)
                }
                Text("Per-question results stream in on completion…".take(w), color = Yellow)
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
                Text("Running batch trickle test…".take(w), color = Yellow)
                if (benchmarkState.batchTrickleProgress.isNotBlank()) {
                    Spacer()
                    Text(benchmarkState.batchTrickleProgress.take(w), color = White)
                }
            }

            benchmarkState.batchTrickleResults != null -> {
                val r = benchmarkState.batchTrickleResults
                Text("Batch trickle results".take(w), color = Cyan, textStyle = Bold)
                Spacer()
                Text("Each DAG leaf is tagged with the dominant MMLU-Pro domain of its training".take(w), color = White)
                Text("queries; reserved test queries are then routed and scored against those tags.".take(w), color = White)
                Spacer()
                Text("Total queries    ${r.totalQueries}".take(w), color = White)
                Text("Top-1 accuracy   ${"%.1f%%".format(r.top1Accuracy * 100)}   highest-confidence leaf's domain == truth".take(w), color = White)
                Text("Any-match acc    ${"%.1f%%".format(r.anyMatchAccuracy * 100)}   any matched leaf's domain == truth".take(w), color = White)
                Text("Macro-F1         ${"%.3f".format(r.macroF1)}   domain-averaged F1 on the top-1 prediction".take(w), color = White)
                Text("Mean leaf purity ${"%.3f".format(r.meanLeafPurity)}   dominant-domain share of top-1 leaf".take(w), color = White)
                Text("Mean depth       ${"%.2f".format(r.meanRoutingDepth)}   tree depth of the top-1 matched leaf".take(w), color = White)
                Text("No-match rate    ${"%.1f%%".format(r.noMatchRate * 100)}   queries that routed to no leaf".take(w), color = White)

                if (r.perDomainF1.isNotEmpty()) {
                    Spacer()
                    Text("Per-domain F1 (top 10 by support)".take(w), color = Cyan, textStyle = Bold)
                    Text(
                        "%-22s %7s %6s %6s %6s".format("domain", "support", "P", "R", "F1").take(w),
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
                Text("Press B to re-run · Q to go back.".take(w), color = Cyan)
            }

            else -> {
                Text("Trickle benchmark".take(w), color = Cyan, textStyle = Bold)
                Spacer()
                Text("Batch routing accuracy test over the reserved test queries.".take(w), color = White)
                Spacer()
                Text("Press B to start the batch routing accuracy test.".take(w), color = White)
                Text("Q/Esc to go back.".take(w), color = Cyan)
            }
        }
    }
}
