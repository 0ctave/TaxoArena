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
    val live = b.liveStats

    if (report != null) {
        // ─── COMPLETE STATE ──────────────────────────────────────────────────
        Text("ARENA BENCHMARK · COMPLETE", color = Green, textStyle = Bold)
        Spacer()
        Text("Queries: ${report.totalQueries} · Pairs: ${report.totalModelPairs}".take(w), color = White)
        Spacer()

        if (w >= 90) {
            val leftColW = 44
            val rightColW = (w - leftColW - 3).coerceAtLeast(15)

            // Headers
            val titleLine = "%-${leftColW}s   %s".format("FINAL BT LEADERBOARD", "MODEL ACCURACY (MMLU-Pro GT)").take(w)
            Text(titleLine, color = Yellow, textStyle = Bold)

            val borderLine = "%-${leftColW}s   %s".format("-".repeat(leftColW), "-".repeat(rightColW)).take(w)
            Text(borderLine, color = White)

            val headerLine = "%-24s | %8s | %6s   %-20s | %s".format(
                "Model", "BT Score", "StdErr", "Model", "Accuracy Bar"
            ).take(w)
            Text(headerLine, color = Cyan)

            val colDividerLine = "%-${leftColW}s   %s".format(
                "-------------------------+----------+------",
                "---------------------+----------------------"
            ).take(w)
            Text(colDividerLine, color = White)

            val sortedModels = if (live?.btRatings?.isNotEmpty() == true) {
                live.btRatings.entries.sortedByDescending { it.value }
            } else {
                emptyList()
            }
            val accs = modelAccuracies(report)
            val maxRows = maxOf(sortedModels.size, accs.size)
            val rowsCount = (height - 9).coerceAtLeast(1)

            for (i in 0 until minOf(maxRows, rowsCount)) {
                val leftStr = if (i < sortedModels.size) {
                    val entry = sortedModels[i]
                    val model = entry.key
                    val score = entry.value
                    val se = live?.btErrors?.get(model) ?: 0.0
                    "%-24s | %8.3f | %6.3f".format(model.take(24), score, se)
                } else {
                    " ".repeat(leftColW)
                }

                val rightStr = if (i < accs.size) {
                    val (model, acc) = accs[i]
                    val bar = "█".repeat((acc * 12).toInt().coerceIn(0, 12))
                    "%-20s | %s %5.1f%%".format(model.take(20), bar.padEnd(12), acc * 100)
                } else {
                    ""
                }

                val rowStr = "%-${leftColW}s   %s".format(leftStr, rightStr).take(w)
                Text(rowStr, color = White)
            }
        } else {
            // Stacked for narrow screen
            Text("FINAL BT LEADERBOARD:", color = Yellow, textStyle = Bold)
            val sortedModels = live?.btRatings?.entries?.sortedByDescending { it.value } ?: emptyList()
            sortedModels.take(5).forEach { (model, score) ->
                val se = live?.btErrors?.get(model) ?: 0.0
                Text("  • ${model.take(20)}: BT=${"%.2f".format(score)} (se=${"%.2f".format(se)})".take(w), color = White)
            }
            Spacer()
            Text("MODEL ACCURACY:", color = Yellow, textStyle = Bold)
            modelAccuracies(report).take(5).forEach { (model, acc) ->
                Text("  • ${model.take(16)}: ${"%.1f%%".format(acc * 100)}".take(w), color = Green)
            }
        }
    } else if (live != null) {
        // ─── RUNNING STATE ───────────────────────────────────────────────────
        Text("ARENA BENCHMARK · RUNNING", color = Cyan, textStyle = Bold)
        Spacer()
        val pct = if (live.total > 0) live.processed * 100 / live.total else 0
        Text(
            "Progress: ${live.processed}/${live.total} ($pct%) · Round: ${live.currentRound} · Agree: ${"%.1f%%".format(live.runningAgreement * 100)}".take(w),
            color = White
        )
        if (live.activeTargets.isNotEmpty()) {
            Text("Targeting Nodes: ${live.activeTargets.joinToString(", ").take(w - 18)}".take(w), color = Yellow)
        }
        Spacer()

        // Render side-by-side if terminal is wide enough, else stack them
        if (w >= 90) {
            val leftColW = 44
            val rightColW = (w - leftColW - 3).coerceAtLeast(15)

            // Headers
            val titleLine = "%-${leftColW}s   %s".format("LIVE BT LEADERBOARD (Log-Strength)", "MATCHUPS PAIRWISE PROGRESS").take(w)
            Text(titleLine, color = Yellow, textStyle = Bold)

            val borderLine = "%-${leftColW}s   %s".format("-".repeat(leftColW), "-".repeat(rightColW)).take(w)
            Text(borderLine, color = White)

            val headerLine = "%-24s | %8s | %6s   %-18s vs %-18s | %5s %5s %5s | %5s".format(
                "Model", "BT Score", "StdErr", "Model A", "Model B", "WinsA", "WinsB", "Ties", "Agree"
            ).take(w)
            Text(headerLine, color = Cyan)

            val colDividerLine = "%-${leftColW}s   %s".format(
                "-------------------------+----------+------",
                "---------------------+---------------------+-------------------+-------"
            ).take(w)
            Text(colDividerLine, color = White)

            val sortedModels = if (live.btRatings.isNotEmpty()) {
                live.btRatings.entries.sortedByDescending { it.value }
            } else {
                b.benchmarkSelectedModels.map { java.util.AbstractMap.SimpleEntry(it, 0.0) }
            }
            val pairStats = live.pairStats
            val maxRows = maxOf(sortedModels.size, pairStats.size)
            val rowsCount = (height - 11).coerceAtLeast(1)

            for (i in 0 until minOf(maxRows, rowsCount)) {
                val leftStr = if (i < sortedModels.size) {
                    val entry = sortedModels[i]
                    val model = entry.key
                    val score = entry.value
                    val se = live.btErrors[model] ?: 0.0
                    "%-24s | %8.3f | %6.3f".format(model.take(24), score, se)
                } else {
                    " ".repeat(leftColW)
                }

                val rightStr = if (i < pairStats.size) {
                    val ps = pairStats[i]
                    "%-18s vs %-18s | %5d %5d %5d | %5.0f%%".format(
                        ps.modelA.take(18),
                        ps.modelB.take(18),
                        ps.judgeWinsA,
                        ps.judgeWinsB,
                        ps.judgeTies,
                        ps.judgeAccuracyAgreementRate * 100
                    )
                } else {
                    ""
                }

                val rowStr = "%-${leftColW}s   %s".format(leftStr, rightStr).take(w)
                Text(rowStr, color = White)
            }
        } else {
            // Stacked layout for narrower terminals
            if (live.btRatings.isNotEmpty()) {
                Text("LIVE BT LEADERBOARD:", color = Yellow, textStyle = Bold)
                live.btRatings.entries.sortedByDescending { it.value }.take(3).forEach { (model, score) ->
                    val se = live.btErrors[model] ?: 0.0
                    Text("  • ${model.take(20)}: BT=${"%.2f".format(score)} (se=${"%.2f".format(se)})".take(w), color = White)
                }
                Spacer()
            }

            Text("MATCHUPS PROGRESS:", color = Yellow, textStyle = Bold)
            val rowsCount = (height - 12).coerceAtLeast(1)
            live.pairStats.take(rowsCount).forEach { ps ->
                Text(
                    "%-14s vs %-14s | %4d/%4d/%4d".format(
                        ps.modelA.take(14),
                        ps.modelB.take(14),
                        ps.judgeWinsA,
                        ps.judgeWinsB,
                        ps.judgeTies
                    ).take(w),
                    color = White
                )
            }
        }
    } else {
        Text("Waiting for live benchmark stats…".take(w), color = Yellow)
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
