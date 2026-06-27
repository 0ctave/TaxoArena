package taxonomy.tui.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
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
import taxonomy.model.GraphNode
import taxonomy.tui.components.DomainSelectorTable
import taxonomy.tui.components.buildTreeLines
import taxonomy.tui.components.HotkeyAction
import taxonomy.tui.components.HotkeyBar
import taxonomy.tui.components.Panel
import taxonomy.tui.components.ProcessRow
import taxonomy.tui.components.ProcessesPanel
import taxonomy.tui.components.ProgressBar
import taxonomy.tui.components.SettingKind
import taxonomy.tui.components.StartupState
import taxonomy.tui.components.TuiTheme
import taxonomy.tui.components.TuiTheme.SPINNER
import taxonomy.tui.controller.TuiEvent
import taxonomy.tui.features.analysis.AnalysisPanel
import taxonomy.tui.features.logs.LogsPanel
import taxonomy.tui.features.startup.LoadingPanel
import taxonomy.tui.features.startup.WelcomePanel
import taxonomy.tui.features.topology.TopologyPanel
import taxonomy.tui.service.TuiConfigFacade
import taxonomy.tui.state.ConfigSubPanel
import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.NavContext
import taxonomy.tui.state.TuiAppState
import taxonomy.tui.state.deriveNavContext
import java.util.Locale

@Composable
fun TuiRouter(
    state: TuiAppState,
    subscriptions: TuiSubscriptions,
    deps: TuiDependencies,
    dispatch: (TuiEvent) -> Unit,
) {
    val width = state.shell.width.coerceAtLeast(1)
    val height = state.shell.height.coerceAtLeast(1)

    val totalNodes = remember(subscriptions.rootNode, subscriptions.graphVersion) {
        flattenNodes(subscriptions.rootNode).size
    }

    TuiShell(
        width = width,
        height = height,
        time = state.runtime.currentTimeText,
        totalNodes = totalNodes,
        activeDatasetName = deps.config.dataset.datasetType.name,
        activeSnapshotName = state.snapshot.activeSnapshotDescription,
    ) {
        when (state.startup.state) {
            StartupState.WELCOME -> WelcomeRoute(width, height, state)
            StartupState.LOADING -> LoadingRoute(width, height, state)
            StartupState.CONFIGANDDOMAINS -> ConfigRoute(width, height, deps, state, subscriptions)
            StartupState.MAINDASHBOARD -> MainDashboardRoute(width, height, deps, state, subscriptions)
        }
    }
}

@Composable
private fun WelcomeRoute(
    width: Int,
    height: Int,
    state: TuiAppState,
) {
    val contentH = (height - 4).coerceAtLeast(4)
    val leftW = ((width - 4) * 0.45).toInt().coerceAtLeast(30)
    val rightW = (width - leftW - 3).coerceAtLeast(20)

    Row(modifier = Modifier.height(contentH)) {
        WelcomePanel(
            width = leftW,
            height = contentH,
            selectedWelcomeIdx = state.startup.selectedWelcomeIdx,
            snapshots = state.snapshot.snapshotList,
        )

        Spacer(Modifier.width(1).height(contentH))

        Panel("SNAPSHOT SUMMARY", White, rightW, contentH) {
            Column(modifier = Modifier.padding(left = 2, top = 1)) {
                val selectedSnapshot =
                    state.snapshot.snapshotList.getOrNull(state.startup.selectedWelcomeIdx - 1)

                if (selectedSnapshot == null) {
                    Text("Create a fresh taxonomy DAG or load a saved snapshot.", color = White)
                } else {
                    Text(selectedSnapshot.description, color = White, textStyle = Bold)
                    Spacer()
                    Text("Time ${selectedSnapshot.timestamp}", color = White)
                    Text("Dataset ${selectedSnapshot.settings.datasetType}", color = White)
                    Text("Total Nodes ${selectedSnapshot.metrics.totalNodes}", color = White)
                    Text("Judged Nodes ${selectedSnapshot.metrics.nodesWithJudges}", color = White)
                    Text(
                        "Equilibrium ${
                            "%.1f".format(Locale.US, selectedSnapshot.metrics.equilibriumIndex * 100.0)
                        }",
                        color = White
                    )
                }
            }
        }
    }

    HotkeyBar(
        width,
        listOf(
            HotkeyAction("W/S", "Move", TuiTheme.ACCENT),
            HotkeyAction("Enter", "Select", TuiTheme.ACCENT, isPrimary = true),
            HotkeyAction("D", "Delete Snapshot"),
            HotkeyAction("Q / Ctrl-C", "Quit", TuiTheme.ERROR),
        )
    )
}

@Composable
private fun LoadingRoute(
    width: Int,
    height: Int,
    state: TuiAppState,
) {
    val contentH = (height - 4).coerceAtLeast(4)
    LoadingPanel(width = width - 2, height = contentH, spinnerTick = state.shell.spinnerTick)
    HotkeyBar(
        width,
        listOf(HotkeyAction("...", "Restoring active taxonomic graph", TuiTheme.RUNNING))
    )
}

@Composable
private fun ConfigRoute(
    width: Int,
    height: Int,
    deps: TuiDependencies,
    state: TuiAppState,
    subscriptions: TuiSubscriptions,
) {
    // Vertical budget: shell already draws Header(1) + 2 rules(2). This route then adds a
    // Spacer(1) and a footer(1), so the panels must fit in (height - 5) to keep the header
    // and bottom rule on-screen. Under-counting here scrolls the header off the top.
    val bodyH = (height - 5).coerceAtLeast(9)
    val topH = (bodyH * 0.62).toInt().coerceAtLeast(8)
    val bottomH = (bodyH - topH).coerceAtLeast(4)
    val leftW = (width * 0.35).toInt().coerceAtLeast(20)
    val rightW = (width - leftW - 1).coerceAtLeast(20)

    val facade = remember(deps) { TuiConfigFacade(deps) }
    val settingItems = remember(state.config.settingsVersion) { facade.buildSettingItems() }
    val availableDomains = remember(state.config.settingsVersion, state.runtime.availableDomainsVersion) {
        facade.getAvailableDomains()
    }

    if (state.config.promptingDownloadCount) {
        Panel("DOWNLOAD DATASET", Cyan, width - 2, topH + bottomH + 1) {
            Column(modifier = Modifier.padding(left = 2, top = 1)) {
                Text(
                    "How many queries to download for " +
                        "${deps.config.dataset.datasetType.name}?",
                    color = White,
                    textStyle = Bold
                )
                Spacer()
                val shown = state.config.downloadCountInput.ifEmpty { "(full dataset)" }
                Text("  Count  \u276f $shown\u2588", color = Cyan, textStyle = Bold)
                Spacer()
                Text("Leave blank to download the full dataset.", color = TuiTheme.INFO)
                Text("Enter a number to cap the query count (e.g. 2000 for a quick test).", color = TuiTheme.INFO)
            }
        }
    } else if (state.runtime.isRegenerating) {
        // Generation spans the full body so progress + live status are front-and-center.
        Panel("TAXONOMY GENERATION IN PROGRESS", Cyan, width - 2, topH + bottomH + 1) {
            Column(modifier = Modifier.padding(left = 2, top = 1)) {
                Text(
                    "Running Adaptive Taxonomy Evolution in 4096-D embedding space...",
                    color = White,
                    textStyle = Bold
                )
                Spacer()
                ProgressBar(
                    percent = extractPercent(subscriptions.generationProgress),
                    width = (width - 25).coerceIn(20, 80),
                    label = "Generation Progress"
                )
                Spacer()
                Text(
                    "Status  ${extractStatus(subscriptions.generationProgress)
                        .ifBlank { state.config.generationStatusText }}",
                    color = Cyan
                )
                Spacer()
                Text("Dataset  ${deps.config.dataset.datasetType.name}", color = White)
                val selDomains = deps.config.dataset.selectedDomains
                Text(
                    "Domains  " + if (selDomains.isEmpty()) "all" else selDomains.joinToString(", "),
                    color = White
                )
            }
        }
    } else if (state.config.downloadingDataset) {
        Panel("DATASET DOWNLOAD IN PROGRESS", Cyan, width - 2, topH) {
            Column(modifier = Modifier.padding(left = 2, top = 1)) {
                Text(
                    "Downloading dataset ${deps.config.dataset.datasetType.name} from Hugging Face...",
                    color = White,
                    textStyle = Bold
                )
                Spacer()
                ProgressBar(
                    percent = state.config.datasetDownloadProgress * 100.0,
                    width = (width - 25).coerceIn(20, 80),
                    label = "Download Progress"
                )
                Spacer()
                Text("Status ${state.config.datasetDownloadStatusText}", color = Cyan)
            }
        }
    } else {
        Row(modifier = Modifier.height(topH)) {
            Panel(
                title = "DOMAINS",
                accentColor = TuiTheme.panelAccent(state.config.activeSubPanel == ConfigSubPanel.DOMAINS),
                width = leftW,
                height = topH
            ) {
                DomainSelectorTable(
                    pWidth = leftW - 4,
                    pHeight = topH - 2,
                    domains = availableDomains,
                    offset = state.config.domainScrollOffset,
                    selectedIdx = state.config.selectedDomainIdx,
                    selectedDomains = deps.config.dataset.selectedDomains
                )
            }

            Spacer(Modifier.width(1).height(topH))

            Panel(
                title = "SETTINGS",
                accentColor = TuiTheme.panelAccent(state.config.activeSubPanel == ConfigSubPanel.SETTINGS),
                width = rightW,
                height = topH
            ) {
                Column(modifier = Modifier.padding(left = 2, top = 1)) {
                    settingItems.forEachIndexed { idx, item ->
                        val selected = idx == state.config.selectedSettingIdx
                        val editing = selected && state.config.isEditingSetting
                        // Typed-input rendering: boolean -> checkbox, select -> ‹ value ›,
                        // number/text -> value (with a blinking caret while editing).
                        val rendered = when {
                            editing -> state.config.editingValue + "\u2588" // █ caret
                            item.kind == SettingKind.BOOLEAN ->
                                if (item.getValue().toBooleanStrictOrNull() == true) "\u2611 on" else "\u2610 off"
                            item.kind == SettingKind.SELECT -> "\u2039 ${item.getValue()} \u203a" // ‹ value ›
                            else -> item.getValue()
                        }
                        val caret = if (selected) "\u276f " else "  " // ❯
                        val rowColor = when {
                            editing -> TuiTheme.RUNNING
                            selected -> TuiTheme.ACCENT
                            else -> TuiTheme.INFO
                        }
                        Text(
                            value = (caret + item.name + ": " + rendered).take(rightW - 4),
                            color = rowColor,
                            textStyle = if (selected) Bold else Unspecified
                        )
                    }
                }
            }
        }
    }

    Spacer()

    // While generating or prompting for a download count, the panel fills the body, so we
    // skip the split bottom region.
    if (!state.runtime.isRegenerating && !state.config.promptingDownloadCount) {
        BottomLogsAndTraces(width, bottomH, deps, state)
    }

    HotkeyBar(width, configHotkeys(state))
}

@Composable
private fun MainDashboardRoute(
    width: Int,
    height: Int,
    deps: TuiDependencies,
    state: TuiAppState,
    subscriptions: TuiSubscriptions,
) {
    // Geometry comes from the shared DashboardLayout so the renderer and the controller's
    // mouse hit-testing can never drift apart.
    val layout = DashboardLayout.dashboard(width, height)
    val bodyH = layout.bodyH
    val topH = layout.topH
    val bottomH = layout.bottomH
    val dagW = layout.dagW
    val arenaW = layout.arenaW

    val facade = remember(deps) { TuiConfigFacade(deps) }
    val availableDomains = remember(state.config.settingsVersion, state.runtime.availableDomainsVersion) {
        facade.getAvailableDomains()
    }
    val allNodes = remember(subscriptions.rootNode, subscriptions.graphVersion) {
        flattenNodes(subscriptions.rootNode)
    }
    // Rebuild the collapsible tree whenever the graph OR the expand/collapse state changes.
    val treeLines = remember(
        subscriptions.rootNode,
        subscriptions.graphVersion,
        state.topology.expandedNodes,
    ) {
        buildTreeLines(subscriptions.rootNode, state.topology.expandedNodes)
    }
    // Memoize recursive query counts per node, recomputed only when the graph changes
    // (not per visible row per frame).
    val queryCounts = remember(subscriptions.rootNode, subscriptions.graphVersion) {
        allNodes.associate { it.id to it.getRecursiveQueryCount() }
    }

    // Context-driven navigator: show the explorable DAG when one is loaded,
    // otherwise prompt to load a snapshot or generate a new taxonomy.
    val hasDag = subscriptions.rootNode != null && allNodes.isNotEmpty()
    val navContext = deriveNavContext(hasDag = hasDag, choosingDomains = false)
    val navFocused = state.shell.focusedPanel == FocusPanel.TOPOLOGY

    Row(modifier = Modifier.height(topH)) {
        Panel(
            title = if (navContext == NavContext.DAG_EXPLORE) "DAG EXPLORER" else "NAVIGATOR",
            accentColor = TuiTheme.panelAccent(navFocused),
            width = dagW,
            height = topH,
        ) {
            when (navContext) {
                NavContext.DAG_EXPLORE -> TopologyPanel(
                    width = dagW - 4,
                    height = topH - 2,
                    state = state.topology,
                    availableDomains = availableDomains,
                    selectedDomains = deps.config.dataset.selectedDomains,
                    allNodes = allNodes,
                    treeLines = treeLines,
                    queryCounts = queryCounts,
                )
                else -> Column(modifier = Modifier.padding(left = 2, top = 1)) {
                    if (state.runtime.isRegenerating) {
                        // Generation has started but the first nodes aren't seeded yet.
                        Text("\u25cc Building taxonomy DAG\u2026", color = TuiTheme.RUNNING, textStyle = Bold)
                        Spacer()
                        Text(state.config.generationStatusText.ifBlank { "Preparing\u2026" }, color = TuiTheme.INFO)
                        Text("The hierarchy will appear here as it forms.", color = TuiTheme.INFO)
                    } else {
                        Text("No taxonomy DAG loaded.", color = TuiTheme.INFO, textStyle = Bold)
                        Spacer()
                        Text("To generate a new taxonomy:", color = TuiTheme.INFO)
                        Text("  [X] Welcome \u2192 Enter (Create new) \u2192 [R] Generate", color = TuiTheme.ACCENT)
                        Spacer()
                        Text("To explore an existing one:", color = TuiTheme.INFO)
                        Text("  [X] Welcome \u2192 pick a saved snapshot", color = TuiTheme.ACCENT)
                    }
                }
            }
        }

        Spacer(Modifier.width(1).height(topH))

        // AnalysisPanel owns its own bordered frame (title reflects the active mode).
        val activeProcess = deriveProcessRows(deps, state, subscriptions).firstOrNull { !it.done }
        AnalysisPanel(
            width = arenaW,
            height = topH,
            focused = state.shell.focusedPanel == FocusPanel.ANALYSIS_HUB,
            mode = state.analysis.mode,
            controlState = subscriptions.arenaControlState,
            inspectorScroll = state.analysis.inspectorScroll,
            metricsScroll = state.analysis.metricsScrollOffset,
            benchmarkScroll = state.benchmark.benchmarkScrollOffset,
            batchTrickleScroll = state.trickle.batchTrickleScrollOffset,
            trickleState = state.trickle,
            snapshotState = state.snapshot,
            arenaState = state.arena,
            benchmarkState = state.benchmark,
            latestMetrics = subscriptions.metricsHistory.lastOrNull() as? taxonomy.model.IterationMetrics,
            metricsHistory = subscriptions.metricsHistory.mapNotNull { it as? taxonomy.model.IterationMetrics },
            activeProcess = activeProcess,
        )
    }

    Spacer()

    BottomLogsAndTraces(width, bottomH, deps, state, subscriptions)

    HotkeyBar(
        width,
        dashboardHotkeys(
            hasDag = hasDag,
            focused = state.shell.focusedPanel,
            isRegenerating = state.runtime.isRegenerating,
        )
    )
}

@Composable
private fun BottomLogsAndTraces(
    width: Int,
    bottomH: Int,
    deps: TuiDependencies,
    state: TuiAppState,
    subscriptions: TuiSubscriptions? = null,
) {
    Row(modifier = Modifier.height(bottomH)) {
        // Logs and live processes share the bottom region 50/50 (side by side).
        val logsW = (width * 0.55).toInt().coerceAtLeast(20)
        val procW = (width - logsW - 1).coerceAtLeast(16)

        Panel(
            title = "SYSTEM LOGS",
            accentColor = TuiTheme.panelAccent(state.shell.focusedPanel == FocusPanel.SYSTEM_LOGS),
            width = logsW,
            height = bottomH
        ) {
            LogsPanel(logsW - 4, bottomH - 2, state.logs.logScrollOffset)
        }

        Spacer(Modifier.width(1).height(bottomH))

        Panel(
            title = "PROCESSES",
            accentColor = TuiTheme.panelAccent(state.shell.focusedPanel == FocusPanel.PROCESSES),
            width = procW - 1,
            height = bottomH
        ) {
            ProcessesPanel(
                width = procW - 4,
                height = bottomH - 2,
                rows = deriveProcessRows(deps, state, subscriptions),
                spinnerTick = state.shell.spinnerTick,
            )
        }
    }
}

/**
 * Collect every active (or just-finished) process from the various service
 * sources into one uniform list for the [ProcessesPanel].
 */
private fun deriveProcessRows(
    deps: TuiDependencies,
    state: TuiAppState,
    subscriptions: TuiSubscriptions?,
): List<ProcessRow> {
    val rows = mutableListOf<ProcessRow>()

    // Dataset download. A full-dataset download has no known total, so report indeterminate
    // (percent=null -> animated track) until real progress (>0) arrives.
    if (state.config.downloadingDataset) {
        val p = state.config.datasetDownloadProgress
        rows += ProcessRow(
            name = "Dataset download",
            percent = if (p > 0.0) (p * 100.0) else null,
            status = state.config.datasetDownloadStatusText,
        )
    }

    // Embedding compute (Pair<current,total>).
    (subscriptions?.embeddingProgress as? Pair<*, *>)?.let { (cur, total) ->
        val c = (cur as? Int) ?: 0; val t = (total as? Int) ?: 0
        if (t > 0 && c < t) rows += ProcessRow(
            name = "Embeddings",
            percent = c.toDouble() / t * 100.0,
            status = "${"%,d".format(c)} / ${"%,d".format(t)} computed",
        )
    }

    // DAG generation / iteration (rich GenerationProgress).
    if (state.runtime.isRegenerating || subscriptions?.generationProgress != null) {
        val pct = extractPercent(subscriptions?.generationProgress)
        rows += ProcessRow(
            name = "DAG generation",
            percent = pct,
            status = extractStatus(subscriptions?.generationProgress),
            done = pct >= 100.0 && !state.runtime.isRegenerating,
        )
    }

    // Node labeling (Pair<current,total>).
    (subscriptions?.labelingProgress as? Pair<*, *>)?.let { (cur, total) ->
        val c = (cur as? Int) ?: 0; val t = (total as? Int) ?: 0
        if (t > 0 && c < t) rows += ProcessRow(
            name = "Labeling nodes",
            percent = c.toDouble() / t * 100.0,
            status = "${"%,d".format(c)} / ${"%,d".format(t)} labelled",
        )
    }

    // Eval-results load (unzip + parse). Surfaced via the benchmark eval-loader state.
    if (state.benchmark.evalLoaderIsRunning) {
        rows += ProcessRow(
            name = "Eval results",
            percent = null,
            status = state.benchmark.evalLoaderStatus.ifBlank { "Unzipping & parsing\u2026" },
        )
    }

    // Judge / GPU inference slots.
    deps.monitor.activeSlots.values.forEach { slot ->
        rows += ProcessRow(
            name = "Judge ${slot.modelName}",
            percent = null,
            status = "${slot.tokenCount}t ${slot.text.takeLast(24)}",
            done = slot.isComplete,
        )
    }

    return rows
}

private fun extractStatus(progress: Any?): String =
    when (progress) {
        null -> ""
        else -> try {
            val m = progress::class.java.methods.firstOrNull { it.name == "getStatusText" }
            (m?.invoke(progress) as? String) ?: ""
        } catch (_: Throwable) {
            ""
        }
    }

private fun extractPercent(progress: Any?): Double =
    when (progress) {
        null -> 0.0
        else -> try {
            val method = progress::class.java.methods.firstOrNull { it.name == "getPercentComplete" }
            (method?.invoke(progress) as? Number)?.toDouble() ?: 0.0
        } catch (_: Throwable) {
            0.0
        }
    }

/** Contextual key hints for the config / domain-setup screen. */
private fun configHotkeys(state: TuiAppState): List<HotkeyAction> {
    if (state.runtime.isRegenerating) {
        return listOf(HotkeyAction("...", "Generating taxonomy DAG", TuiTheme.RUNNING))
    }
    if (state.config.downloadingDataset) {
        return listOf(HotkeyAction("...", "Downloading dataset", TuiTheme.RUNNING))
    }
    if (state.config.promptingDownloadCount) {
        return listOf(
            HotkeyAction("0-9", "Query count", TuiTheme.ACCENT),
            HotkeyAction("Enter", "Download (blank = full)", TuiTheme.OK, isPrimary = true),
            HotkeyAction("Esc", "Cancel", TuiTheme.ERROR),
        )
    }
    if (state.config.isEditingSetting) {
        return listOf(
            HotkeyAction("Type", "Edit value", TuiTheme.ACCENT),
            HotkeyAction("Enter", "Save", TuiTheme.OK, isPrimary = true),
            HotkeyAction("Esc", "Cancel", TuiTheme.ERROR),
        )
    }
    val inDomains = state.config.activeSubPanel == ConfigSubPanel.DOMAINS
    return buildList {
        add(HotkeyAction("Tab", if (inDomains) "\u2192 Settings" else "\u2192 Domains", TuiTheme.ACCENT))
        add(HotkeyAction("W/S", "Move"))
        if (inDomains) {
            add(HotkeyAction("Space", "Toggle Domain"))
        } else {
            add(HotkeyAction("Enter", "Toggle/Cycle/Edit"))
        }
        // When the dataset is already present, R generates straight away and we don't clutter
        // the bar with the download key. When it's missing, downloading is the headline action.
        if (state.runtime.isDatasetDownloaded) {
            add(HotkeyAction("R", "Generate DAG", TuiTheme.OK, isPrimary = true))
        } else {
            add(HotkeyAction("D", "Download Dataset", TuiTheme.OK, isPrimary = true))
            add(HotkeyAction("R", "(download first)", TuiTheme.INFO))
        }
        add(HotkeyAction("Esc", "Back", TuiTheme.ERROR))
    }
}

/** Contextual key hints for the main dashboard. */
private fun dashboardHotkeys(
    hasDag: Boolean,
    focused: FocusPanel,
    isRegenerating: Boolean,
): List<HotkeyAction> =
    taxonomy.tui.components.DashboardHotkeys.forState(hasDag, focused, isRegenerating)

private fun flattenNodes(rootNode: GraphNode?): List<GraphNode> {
    if (rootNode == null) return emptyList()
    val out = mutableListOf<GraphNode>()
    val visited = linkedSetOf<String>()
    fun walk(node: GraphNode) {
        if (!visited.add(node.id)) return
        out += node
        node.children.forEach(::walk)
    }
    walk(rootNode)
    return out.sortedByDescending { it.queries.size }
}
