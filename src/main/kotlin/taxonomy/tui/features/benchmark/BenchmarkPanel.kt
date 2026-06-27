package taxonomy.tui.features.benchmark

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import com.jakewharton.mosaic.ui.TextStyle.Companion.Unspecified
import taxonomy.service.AnalysisPanelState
import taxonomy.tui.state.BenchmarkType
import taxonomy.tui.state.BenchmarkUiState

@Composable
fun BenchmarkPanel(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
    scrollOffset: Int,
    benchmarkState: BenchmarkUiState,
) {
    when (benchmarkState.benchmarkType) {
        BenchmarkType.NONE -> BenchmarkTypeSelector(benchmarkState)
        BenchmarkType.ARENA -> ArenaBenchmarkView(width, height, controlState, scrollOffset, benchmarkState)
        BenchmarkType.TRICKLE -> TrickleBenchmarkView(width, height, benchmarkState)
    }
}

/** Entry screen: pick which evaluation to run. */
@Composable
private fun BenchmarkTypeSelector(benchmarkState: BenchmarkUiState) {
    val options = listOf(
        "ARENA" to "Multi-model pairwise eval over MMLU-Pro",
        "TRICKLE" to "Batch routing accuracy test over reserved queries",
    )
    Column {
        Text("BENCHMARK SUITE", color = Cyan, textStyle = Bold)
        Spacer()
        Text("Select a benchmark type:", color = White)
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
                }
            )
        }
        Spacer()
        Text("W/S to select · Enter to confirm · Q/Esc to go back", color = Cyan)
    }
}

/**
 * Per-model ingestion picker overlay (the [O] hotkey). Lists each eval source in the cache with a
 * checkbox, ingested marker, and size, so the user ingests only the models they pick rather than
 * parsing the whole directory. Shared by the Arena and Benchmark hub views.
 */
@Composable
fun EvalCatalogPicker(
    width: Int,
    height: Int,
    benchmarkState: BenchmarkUiState,
) {
    Column {
        Text("SELECT EVAL_RESULTS TO INGEST", color = Cyan, textStyle = Bold)
        Spacer()
        val catalog = benchmarkState.evalCatalog
        if (catalog.isEmpty()) {
            Text("No eval_results found in the cache directory.", color = Yellow)
            Spacer()
            Text("Press D to download the MMLU-Pro eval_results, or Q to cancel.", color = Cyan)
            return@Column
        }
        val selectedCount = benchmarkState.evalCatalogSelection.size
        Text("$selectedCount selected · ${catalog.size} available", color = White)
        Spacer()
        val rows = (height - 5).coerceAtLeast(1)
        // Keep the cursor row visible by scrolling the window when it runs past the bottom.
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
                        append(if (checked) "[x] " else "[ ] ")
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
                }
            )
        }
        Spacer()
        Text("W/S move · Space toggle · A all-new · Enter ingest · D download · Q cancel", color = Cyan)
    }
}

/** Existing Arena benchmark (MMLU-Pro pairwise eval) view. */
@Composable
private fun ArenaBenchmarkView(
    width: Int,
    height: Int,
    controlState: AnalysisPanelState,
    scrollOffset: Int,
    benchmarkState: BenchmarkUiState,
) {
    Column {
        if (benchmarkState.loadedModels.isNotEmpty()) {
            Text("Loaded models: ${benchmarkState.loadedModels.joinToString(", ")}", color = Green)
        } else {
            Text("No precomputed models loaded — press o to load eval_results.", color = Yellow)
        }
        Spacer()

        when {
            benchmarkState.isDownloadingEval -> {
                Text("Downloading MMLU-Pro eval_results…", color = Yellow)
                val files = benchmarkState.evalDownloadProgress
                if (files.isEmpty()) {
                    Text("Fetching file listing from GitHub…", color = White)
                } else {
                    val done = files.values.count { it >= 1f }
                    Text("Downloaded $done / ${files.size} files", color = White)
                    files.entries.take((height - 4).coerceAtLeast(1)).forEach { (name, pct) ->
                        Text("  ${name.take((width - 12).coerceAtLeast(1))}  ${"%.0f%%".format(pct * 100)}", color = White)
                    }
                }
            }

            controlState.isRunningBenchmark -> {
                Text("Running benchmark...", color = White)
                Text(controlState.benchmarkProgress, color = White)
                benchmarkState.liveStats?.let { live ->
                    Text(
                        "Live: ${live.processed}/${live.total} · " +
                            "agreement ${"%.2f".format(live.runningAgreement)} · " +
                            "coverage ${"%.2f".format(live.runningCoverage)}",
                        color = White
                    )
                }
            }

            benchmarkState.evalLoaderIsRunning -> {
                Text("Loading eval results...", color = White)
                if (benchmarkState.evalLoadingModelCount > 0) {
                    val i = benchmarkState.evalLoadingModelIdx + 1
                    val n = benchmarkState.evalLoadingModelCount
                    val cur = benchmarkState.evalLoadingCurrentModel.ifBlank { "…" }
                    val items = if (benchmarkState.evalLoadingItemTotal > 0)
                        " · items ${benchmarkState.evalLoadingItem}/${benchmarkState.evalLoadingItemTotal}"
                    else ""
                    Text("$cur  $i/$n$items", color = White)
                } else if (benchmarkState.evalLoaderStatus.isNotBlank()) {
                    Text(benchmarkState.evalLoaderStatus, color = White)
                }
            }

            controlState.benchmarkReport != null -> {
                val report = controlState.benchmarkReport!!
                Text("Queries: ${report.totalQueries}", color = White)
                Text("Model Pairs: ${report.totalModelPairs}", color = White)
                Text("Coverage: ${"%.3f".format(report.coverageRate)}", color = White)
                Text("Judge Agreement: ${"%.3f".format(report.overallJudgeAccuracyAgreement)}", color = White)
                Spacer()
                Text("Scroll offset: $scrollOffset", color = White)
            }

            else -> {
                Text("Models: ${benchmarkState.benchmarkModelsInput.ifBlank { "(all loaded)" }}", color = White)
                Text("Query limit: ${benchmarkState.benchmarkQueryLimitInput.ifBlank { "0 (all)" }}", color = White)
                Text("Category: ${benchmarkState.benchmarkCategoryInput.ifBlank { "—" }}", color = White)
                Text("Confidence gate: ${benchmarkState.benchmarkConfidenceGateInput}", color = White)
                Text("Parallelism: ${benchmarkState.benchmarkParallelismInput}", color = White)
                Text("Update rankings: ${benchmarkState.benchmarkUpdateRankingsInput}", color = White)
            }
        }

        Spacer()
        Text("Enter run benchmark · o load eval_results · Q back", color = Cyan)
    }
}

/** Batch routing accuracy test (formerly the Trickle tab's batch test). */
@Composable
private fun TrickleBenchmarkView(
    width: Int,
    height: Int,
    benchmarkState: BenchmarkUiState,
) {
    Column {
        when {
            benchmarkState.isRunningBatchTrickleTest -> {
                Text("Running batch trickle test…", color = Yellow)
                if (benchmarkState.batchTrickleProgress.isNotBlank()) {
                    Spacer()
                    Text(benchmarkState.batchTrickleProgress, color = White)
                }
            }

            benchmarkState.batchTrickleResults != null -> {
                val r = benchmarkState.batchTrickleResults
                Text("Batch trickle results", color = Cyan, textStyle = Bold)
                Spacer()
                Text("Each DAG leaf is tagged with the dominant MMLU-Pro domain of its training", color = White)
                Text("queries; reserved test queries are then routed and scored against those tags.", color = White)
                Spacer()
                Text("Total queries    ${r.totalQueries}", color = White)
                Text("Top-1 accuracy   ${"%.1f%%".format(r.top1Accuracy * 100)}   highest-confidence leaf's domain == truth", color = White)
                Text("Any-match acc    ${"%.1f%%".format(r.anyMatchAccuracy * 100)}   any matched leaf's domain == truth", color = White)
                Text("Macro-F1         ${"%.3f".format(r.macroF1)}   domain-averaged F1 on the top-1 prediction", color = White)
                Text("Mean leaf purity ${"%.3f".format(r.meanLeafPurity)}   dominant-domain share of top-1 leaf", color = White)
                Text("Mean depth       ${"%.2f".format(r.meanRoutingDepth)}   tree depth of the top-1 matched leaf", color = White)
                Text("No-match rate    ${"%.1f%%".format(r.noMatchRate * 100)}   queries that routed to no leaf", color = White)

                if (r.perDomainF1.isNotEmpty()) {
                    Spacer()
                    Text("Per-domain F1 (top 10 by support)", color = Cyan, textStyle = Bold)
                    Text(
                        "%-22s %7s %6s %6s %6s".format("domain", "support", "P", "R", "F1"),
                        color = Yellow,
                    )
                    r.perDomainF1.entries
                        .sortedByDescending { it.value.support }
                        .take(10)
                        .forEach { (domain, f1) ->
                            Text(
                                "%-22s %7d %6.2f %6.2f %6.2f".format(
                                    domain.take(22), f1.support, f1.precision, f1.recall, f1.f1
                                ),
                                color = White,
                            )
                        }
                }

                Spacer()
                Text("Press B to re-run · Q to go back.", color = Cyan)
            }

            else -> {
                Text("Trickle benchmark", color = Cyan, textStyle = Bold)
                Spacer()
                Text("Batch routing accuracy test over the reserved test queries.", color = White)
                Spacer()
                Text("Press B to start the batch routing accuracy test.", color = White)
                Text("Q/Esc to go back.", color = Cyan)
            }
        }
    }
}
