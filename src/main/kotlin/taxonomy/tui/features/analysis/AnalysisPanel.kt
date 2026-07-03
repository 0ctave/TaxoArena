package taxonomy.tui.features.analysis

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import com.jakewharton.mosaic.ui.TextStyle.Companion.Unspecified
import taxonomy.config.EffectiveConfig
import taxonomy.service.AnalysisMode
import taxonomy.service.AnalysisPanelState
import taxonomy.tui.components.HotkeyAction
import taxonomy.tui.components.Panel
import taxonomy.tui.components.ProcessRow
import taxonomy.tui.components.ScrollablePanelContent
import taxonomy.tui.components.TuiTheme
import taxonomy.tui.components.take
import taxonomy.tui.features.arena.ArenaPanel
import taxonomy.tui.features.benchmark.BenchmarkPanel
import taxonomy.tui.features.benchmark.EvalCatalogPicker
import taxonomy.tui.features.progress.JudgeProgressPanel
import taxonomy.tui.features.trickle.TricklePanel
import taxonomy.tui.state.ArenaUiState
import taxonomy.tui.state.BenchmarkUiState
import taxonomy.tui.state.SnapshotUiState
import taxonomy.tui.controller.TuiEvent
import java.util.Locale

@Composable
fun AnalysisPanel(
    width: Int,
    height: Int,
    focused: Boolean = false,
    mode: AnalysisMode,
    controlState: AnalysisPanelState,
    inspectorScroll: Int,
    benchmarkScroll: Int,
    configScrollOffset: Int = 0,
    trickleState: taxonomy.tui.state.TrickleUiState,
    snapshotState: SnapshotUiState,
    arenaState: ArenaUiState,
    benchmarkState: BenchmarkUiState,
    availableDomains: List<Pair<String, Int>> = emptyList(),
    latestMetrics: taxonomy.model.IterationMetrics? = null,
    metricsHistory: List<taxonomy.model.IterationMetrics> = emptyList(),
    selectedIterationIndex: Int = -1,
    metricsZoneFocus: taxonomy.tui.state.MetricsZoneFocus = taxonomy.tui.state.MetricsZoneFocus.TABLE,
    showPerformanceBlock: Boolean = false,
    detailScrollOffset: Int = 0,
    performanceReport: Map<String, taxonomy.utils.PerformanceStats> = emptyMap(),
    activeProcess: ProcessRow? = null,
    isEnteringBatchGenerality: Boolean = false,
    batchGeneralityInput: String = "1",
    batchReplaceExisting: Boolean = false,
    batchDomainsInput: String = "",
    batchSelectedSettingIdx: Int = 0,
    isEditingBatchSetting: Boolean = false,
    batchEditingValue: String = "",
    /** Context-sensitive key hints rendered inside the panel border, above the bottom edge. */
    contextHints: List<HotkeyAction> = emptyList(),
    dispatch: (TuiEvent) -> Unit = {},
) {
    val title = when (mode) {
        AnalysisMode.ARENA -> "MODEL ARENA"
        AnalysisMode.BENCHMARK -> "BENCHMARK"
        AnalysisMode.TRICKLE_TEST -> "TRICKLE TEST"
        AnalysisMode.JUDGE_PROGRESS -> "JUDGE PROGRESS"
        AnalysisMode.SNAPSHOTS -> "SNAPSHOTS"
        AnalysisMode.NODE_DETAIL -> "NODE INSPECTOR"
        AnalysisMode.METRICS -> "METRICS"
        AnalysisMode.SETTINGS -> "SETTINGS"
        AnalysisMode.CONFIG -> "SNAPSHOT CONFIG"
        AnalysisMode.LEADERBOARD -> "STANDALONE LEADERBOARD"
        else -> "ANALYSIS HUB"
    }

    Panel(title, TuiTheme.panelAccent(focused), width, height, contextHints = contextHints) {
        Column {
            val hintRows = if (contextHints.isNotEmpty()) 1 else 0
            val bannerH = if (activeProcess != null) 1 else 0
            if (activeProcess != null) {
                ProcessBanner(width - 4, activeProcess)
            }
            val bodyH = (height - 3 - hintRows - bannerH).coerceAtLeast(1)
            val bodyW = (width - 4).coerceAtLeast(1)

            when {
                (mode == AnalysisMode.ARENA || mode == AnalysisMode.BENCHMARK) &&
                    benchmarkState.isPickingEvalCatalog ->
                    EvalCatalogPicker(bodyW, bodyH, benchmarkState)

                mode == AnalysisMode.ARENA -> ArenaPanel(bodyW, bodyH, controlState, arenaState, benchmarkState)
                mode == AnalysisMode.BENCHMARK -> BenchmarkPanel(bodyW, bodyH, controlState, benchmarkScroll, benchmarkState, availableDomains, dispatch)
                mode == AnalysisMode.TRICKLE_TEST -> TricklePanel(bodyW, bodyH, trickleState)
                mode == AnalysisMode.JUDGE_PROGRESS -> JudgeProgressPanel(
                    width = bodyW,
                    height = bodyH,
                    controlState = controlState,
                    isEnteringBatchGenerality = isEnteringBatchGenerality,
                    batchGeneralityInput = batchGeneralityInput,
                    batchReplaceExisting = batchReplaceExisting,
                    batchDomainsInput = batchDomainsInput,
                    batchSelectedSettingIdx = batchSelectedSettingIdx,
                    isEditingBatchSetting = isEditingBatchSetting,
                    batchEditingValue = batchEditingValue,
                )
                mode == AnalysisMode.SNAPSHOTS -> SnapshotHubPanel(bodyW, bodyH, snapshotState)
                mode == AnalysisMode.CONFIG -> ConfigSnapshotPanel(
                    width = bodyW,
                    height = bodyH,
                    config = snapshotState.activeSnapshotConfig,
                    snapshotDescription = snapshotState.activeSnapshotDescription,
                    scrollOffset = configScrollOffset,
                )
                mode == AnalysisMode.LEADERBOARD -> LeaderboardPanel(
                    width = bodyW,
                    height = bodyH,
                    arenaState = arenaState,
                    snapshotDescription = snapshotState.activeSnapshotDescription,
                )
                else -> MetricsOrInspectorPanel(
                    width = bodyW,
                    height = bodyH,
                    mode = mode,
                    controlState = controlState,
                    inspectorScroll = inspectorScroll,
                    latestMetrics = latestMetrics,
                    metricsHistory = metricsHistory,
                    isGeneratingJudge = arenaState.isGeneratingJudge,
                    selectedIterationIndex = selectedIterationIndex,
                    metricsZoneFocus = metricsZoneFocus,
                    showPerformanceBlock = showPerformanceBlock,
                    detailScrollOffset = detailScrollOffset,
                    performanceReport = performanceReport,
                )
            }
        }
    }
}

/** One-line pinned banner summarising the active process with a resume hint. */
@Composable
private fun ProcessBanner(width: Int, p: ProcessRow) {
    val color = TuiTheme.statusColor(done = p.done, error = p.error)
    val pctText = p.percent?.let { "${"%.0f".format(Locale.US, it)}%" }
    val cleanStatus = p.status.replace("\n", " ").replace("\r", " ").trim()
    Text(
        buildAnnotatedString {
            withStyle(SpanStyle(color = color, textStyle = Bold)) { append("▶ ${p.name}  ") }
            if (pctText != null) {
                withStyle(SpanStyle(color = Green, textStyle = Bold)) { append("$pctText  ") }
            }
            withStyle(SpanStyle(color = White)) { append(cleanStatus) }
            withStyle(SpanStyle(color = color)) { append("  ·  press P") }
        }.take(width - 1)
    )
}

private data class ConfigLine(val text: String, val color: Color, val bold: Boolean = false)

@Composable
fun ConfigSnapshotPanel(
    width: Int,
    height: Int,
    config: EffectiveConfig?,
    snapshotDescription: String? = null,
    scrollOffset: Int = 0,
) {
    val w = (width - 1).coerceAtLeast(1)
    if (config == null) {
        Column(modifier = Modifier.padding(left = 1, top = 1)) {
            Text("No snapshot loaded — config unavailable.".take(w), color = TuiTheme.INFO)
            Spacer()
            Text("Load a snapshot via [X] Load DAG to see its generation config.".take(w), color = White)
        }
        return
    }

    val lines = mutableListOf<ConfigLine>()
    fun add(text: String, color: Color = White, bold: Boolean = false) {
        lines += ConfigLine(text, color, bold)
    }

    val header = buildString {
        append("Config")
        if (snapshotDescription != null) append(" · $snapshotDescription")
    }
    add(header, Cyan, true)
    add("")

    add("Dataset", Cyan, true)
    add("  Type         ${config.dataset.datasetType.name}")
    val domains = config.dataset.selectedDomains
    val domainsText = if (domains.isEmpty()) "all" else domains.joinToString(", ")
    add("  Domains      $domainsText")
    add("  Split        ${if (config.dataset.splitDataset) "yes (${"%.0f".format(Locale.US, config.dataset.testSplitRatio * 100)}% test)" else "no"}")
    add("")

    add("Execution", Cyan, true)
    add("  Iterations   ${config.execution.numIterations}")
    add("  Early stop   ${config.execution.enableEarlyStopping}")
    add("  Labeling     ${config.execution.enableLabeling}")
    add("  Live label   ${config.execution.enableLiveLabeling}")
    add("")

    add("LLM", Cyan, true)
    add("  Provider     ${config.llm.provider}")
    add("  Embed prov.  ${config.llm.embeddingProvider}")
    add("  Embed model  ${config.llm.embeddingModel}")
    add("  Judge model  ${config.llm.judgeModel}")
    add("  Label model  ${config.llm.labelingModel}")
    add("  Max general. ${config.llm.maxJudgeGenerality}")
    add("")

    add("Formalism", Cyan, true)
    add("  Max depth    ${config.formalism.maxDepth}")
    add("  Min cluster  ${config.formalism.minClusterSize}")
    add("  Sep. epsilon ${config.formalism.separationEpsilon}")
    add("  Cosine tau   ${config.formalism.cosineTau}")
    add("  Assign. gap  ${config.formalism.assignmentGap}")
    add("  EMA alpha    ${config.formalism.emaAlpha}")

    ScrollablePanelContent(
        pWidth = width,
        pHeight = height,
        itemCount = lines.size,
        scrollOffset = scrollOffset,
        hasPadding = false
    ) { visibleHeight, startIdx, innerWidth ->
        val sub = lines.subList(startIdx, (startIdx + visibleHeight).coerceAtMost(lines.size))
        sub.forEach { line ->
            if (line.text.isEmpty()) {
                Spacer()
            } else {
                Text(
                    line.text.take(innerWidth),
                    color = line.color,
                    textStyle = if (line.bold) Bold else Unspecified
                )
            }
        }
    }
}

@Composable
private fun SnapshotHubPanel(
    width: Int,
    height: Int,
    state: SnapshotUiState,
) {
    val w = (width - 1).coerceAtLeast(1)
    Column {
        val bannerH = if (state.isSavingSnapshot || state.isRenamingSnapshot) 1 else 0
        when {
            state.isSavingSnapshot ->
                Text("Save snapshot — description: ${state.snapshotDescInput}█".take(w), color = Cyan)
            state.isRenamingSnapshot ->
                Text("Rename snapshot — new name: ${state.renameInput}█".take(w), color = Cyan)
        }
        if (state.snapshotList.isEmpty()) {
            Text("No snapshots saved yet. Press N to save the active DAG.".take(w), color = White)
        } else {
            Text("SAVED SNAPSHOTS (${state.snapshotList.size})".take(w), color = Cyan, textStyle = Bold)
            val visible = (height - 2 - bannerH).coerceAtLeast(1)
            ScrollablePanelContent(
                pWidth = width,
                pHeight = visible,
                itemCount = state.snapshotList.size,
                scrollOffset = state.selectedSnapshotIdx,
                hasPadding = false
            ) { visibleHeight, startIdx, innerWidth ->
                val endIdx = (startIdx + visibleHeight).coerceAtMost(state.snapshotList.size)
                for (idx in startIdx until endIdx) {
                    val snap = state.snapshotList[idx]
                    val selected = idx == state.selectedSnapshotIdx
                    Text(
                        buildAnnotatedString {
                            withStyle(SpanStyle(
                                color = if (selected) Cyan else White,
                                textStyle = if (selected) Bold else Unspecified
                            )) { append((if (selected) "❯ " else "  ") + snap.description) }
                            withStyle(SpanStyle(color = White)) {
                                append("  (${snap.timestamp} · ${snap.metrics.totalNodes} nodes)")
                            }
                        }.take(innerWidth)
                    )
                }
            }
        }
    }
}

@Composable
fun LeaderboardPanel(
    width: Int,
    height: Int,
    arenaState: ArenaUiState,
    snapshotDescription: String? = null,
) {
    val w = (width - 1).coerceAtLeast(1)
    val header = if (snapshotDescription != null) {
        "Leaderboard ($snapshotDescription)"
    } else {
        "Leaderboard (global)"
    }

    Column {
        SafeText(header, w, Cyan)
        Spacer()
        if (arenaState.leaderboard.isEmpty()) {
            SafeText("No ratings recorded yet — run a benchmark or arena match.", w, Yellow)
        } else {
            SafeText("%-22s %-10s %8s %8s %5s".format("Model", "Domain", "Score", "StdErr", "Rank"), w, Yellow)
            val items = arenaState.leaderboard.flatMap { g -> g.agents.map { g.rank to it } }
            val rows = (height - 4).coerceAtLeast(1)
            ScrollablePanelContent(
                pWidth = width,
                pHeight = rows,
                itemCount = items.size,
                scrollOffset = arenaState.leaderboardScrollOffset,
                hasPadding = false
            ) { visibleHeight, startIdx, innerWidth ->
                val endIdx = (startIdx + visibleHeight).coerceAtMost(items.size)
                for (i in startIdx until endIdx) {
                    val (rank, a) = items[i]
                    SafeText(
                        "%-22s %-10s %8.3f %8.3f %5d".format(
                            a.agentName.take(22), a.domain.take(10), a.mu, a.sigma, rank
                        ),
                        innerWidth,
                        White
                    )
                }
            }
        }
    }
}

@Composable
private fun SafeText(text: String, width: Int, color: Color = White) {
    val safe = if (width <= 0) "" else if (text.length > width) text.take(width) else text
    Text(safe, color = color)
}
