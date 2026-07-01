package taxonomy.tui.features.analysis

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.White
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
    trickleState: taxonomy.tui.state.TrickleUiState,
    snapshotState: SnapshotUiState,
    arenaState: ArenaUiState,
    benchmarkState: BenchmarkUiState,
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
    /** Context-sensitive key hints rendered inside the panel border, above the bottom edge. */
    contextHints: List<HotkeyAction> = emptyList(),
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
        else -> "ANALYSIS HUB"
    }

    Panel(title, TuiTheme.panelAccent(focused), width, height, contextHints = contextHints) {
        Column {
            val bannerH = if (activeProcess != null) 1 else 0
            if (activeProcess != null) {
                ProcessBanner(width - 2, activeProcess)
            }
            val bodyH = (height - 2 - bannerH).coerceAtLeast(1)
            val bodyW = width - 2

            when {
                (mode == AnalysisMode.ARENA || mode == AnalysisMode.BENCHMARK) &&
                    benchmarkState.isPickingEvalCatalog ->
                    EvalCatalogPicker(bodyW, bodyH, benchmarkState)

                mode == AnalysisMode.ARENA -> ArenaPanel(bodyW, bodyH, controlState, arenaState, benchmarkState)
                mode == AnalysisMode.BENCHMARK -> BenchmarkPanel(bodyW, bodyH, controlState, benchmarkScroll, benchmarkState)
                mode == AnalysisMode.TRICKLE_TEST -> TricklePanel(bodyW, bodyH, trickleState)
                mode == AnalysisMode.JUDGE_PROGRESS -> JudgeProgressPanel(
                    width = bodyW,
                    height = bodyH,
                    controlState = controlState,
                    isEnteringBatchGenerality = isEnteringBatchGenerality,
                    batchGeneralityInput = batchGeneralityInput,
                    batchReplaceExisting = batchReplaceExisting,
                )
                mode == AnalysisMode.SNAPSHOTS -> SnapshotHubPanel(bodyW, bodyH, snapshotState)
                mode == AnalysisMode.CONFIG -> ConfigSnapshotPanel(
                    width = bodyW,
                    height = bodyH,
                    config = snapshotState.activeSnapshotConfig,
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
    val pctText = p.percent?.let { "${"%.0f".format(java.util.Locale.US, it)}%" }
    Text(
        buildAnnotatedString {
            withStyle(SpanStyle(color = color, textStyle = Bold)) { append("▶ ${p.name}  ") }
            if (pctText != null) {
                withStyle(SpanStyle(color = Green, textStyle = Bold)) { append("$pctText  ") }
            }
            withStyle(SpanStyle(color = White)) { append(p.status) }
            withStyle(SpanStyle(color = color)) { append("  ·  press P") }
        }.take(width - 1)
    )
}

@Composable
fun ConfigSnapshotPanel(
    width: Int,
    height: Int,
    config: EffectiveConfig?,
    snapshotDescription: String? = null,
) {
    val w = (width - 1).coerceAtLeast(1)
    Column(modifier = Modifier.padding(left = 1, top = 1)) {
        if (config == null) {
            Text("No snapshot loaded — config unavailable.".take(w), color = TuiTheme.INFO)
            Spacer()
            Text("Load a snapshot via [X] Load DAG to see its generation config.".take(w), color = White)
            return@Column
        }

        val header = buildString {
            append("Config")
            if (snapshotDescription != null) append(" · $snapshotDescription")
        }.take(w)
        Text(header, color = Cyan, textStyle = Bold)
        Spacer()

        Text("Dataset", color = Cyan, textStyle = Bold)
        Text("  Type         ${config.dataset.datasetType.name}".take(w), color = White)
        val domains = config.dataset.selectedDomains
        val domainsText = if (domains.isEmpty()) "all" else domains.joinToString(", ")
        Text("  Domains      $domainsText".take(w), color = White)
        Text("  Split        ${if (config.dataset.splitDataset) "yes (${"%.0f".format(Locale.US, config.dataset.testSplitRatio * 100)}% test)" else "no"}".take(w), color = White)
        Spacer()

        Text("Execution", color = Cyan, textStyle = Bold)
        Text("  Iterations   ${config.execution.numIterations}".take(w), color = White)
        Text("  Early stop   ${config.execution.enableEarlyStopping}".take(w), color = White)
        Text("  Labeling     ${config.execution.enableLabeling}".take(w), color = White)
        Text("  Live label   ${config.execution.enableLiveLabeling}".take(w), color = White)
        Spacer()

        Text("LLM", color = Cyan, textStyle = Bold)
        Text("  Provider     ${config.llm.provider}".take(w), color = White)
        Text("  Embed prov.  ${config.llm.embeddingProvider}".take(w), color = White)
        Text("  Embed model  ${config.llm.embeddingModel}".take(w), color = White)
        Text("  Judge model  ${config.llm.judgeModel}".take(w), color = White)
        Text("  Label model  ${config.llm.labelingModel}".take(w), color = White)
        Text("  Max general. ${config.llm.maxJudgeGenerality}".take(w), color = White)
        Spacer()

        Text("Formalism", color = Cyan, textStyle = Bold)
        Text("  Max depth    ${config.formalism.maxDepth}".take(w), color = White)
        Text("  Min cluster  ${config.formalism.minClusterSize}".take(w), color = White)
        Text("  Sep. epsilon ${config.formalism.separationEpsilon}".take(w), color = White)
        Text("  Cosine tau   ${config.formalism.cosineTau}".take(w), color = White)
        Text("  Assign. gap  ${config.formalism.assignmentGap}".take(w), color = White)
        Text("  EMA alpha    ${config.formalism.emaAlpha}".take(w), color = White)
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
            val visible = (height - 4).coerceAtLeast(1)
            state.snapshotList.take(visible).forEachIndexed { idx, snap ->
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
                    }.take(w)
                )
            }
        }
    }
}
