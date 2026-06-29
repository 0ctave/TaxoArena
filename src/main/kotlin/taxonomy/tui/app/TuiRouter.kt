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
import taxonomy.tui.components.GlobalHotkeys
import taxonomy.tui.components.HotkeyAction
import taxonomy.tui.components.HotkeyBar
import taxonomy.tui.components.HotkeyBarGrouped
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

    val headerNodes = remember(subscriptions.rootNode, subscriptions.graphVersion) {
        flattenNodes(subscriptions.rootNode)
    }
    val totalNodes = headerNodes.size
    val maxDepth = remember(headerNodes) { headerNodes.maxOfOrNull { it.depth } ?: 0 }
    val leafCount = remember(headerNodes) { headerNodes.count { it.isLeaf } }

    TuiShell(
        width = width,
        height = height,
        time = state.runtime.currentTimeText,
        totalNodes = totalNodes,
        activeDatasetName = deps.config.dataset.datasetType.name,
        activeSnapshotName = state.snapshot.activeSnapshotDescription,
        maxDepth = maxDepth,
        leafCount = leafCount,
    ) {
        if (state.shell.helpOverlayOpen) {
            HelpOverlay(width, height, state)
        } else {
            when (state.startup.state) {
                StartupState.LOAD_DAG -> WelcomeRoute(width, height, state)
                StartupState.LOADING -> LoadingRoute(width, height, state)
                StartupState.CONFIGANDDOMAINS -> ConfigRoute(width, height, deps, state, subscriptions)
                StartupState.MAINDASHBOARD -> MainDashboardRoute(width, height, deps, state, subscriptions)
            }
        }
    }
}

/**
 * Full-screen keyboard reference. Lists the globally-available keys plus the keys for the
 * currently active screen/mode. Closed with "?" or Esc (handled in the controller).
 */
@Composable
private fun HelpOverlay(
    width: Int,
    height: Int,
    state: TuiAppState,
) {
    val bodyH = (height - 4).coerceAtLeast(6)
    Panel("HELP — KEYBOARD REFERENCE", Cyan, width - 2, bodyH) {
        Column(modifier = Modifier.padding(left = 2, top = 1)) {
            Text("Global", color = Cyan, textStyle = Bold)
            Text("  ?         Toggle this help", color = White)
            Text("  Tab       Switch panels / sub-panel", color = White)
            Text("  X         Load DAG (return to load screen)", color = White)
            Text("  Ctrl-C    Quit", color = White)
            Spacer()

            when (state.startup.state) {
                StartupState.LOAD_DAG -> {
                    Text("Load / Welcome", color = Cyan, textStyle = Bold)
                    Text("  W/S, ↑/↓   Move selection", color = White)
                    Text("  Enter      Create new DAG / load snapshot", color = White)
                    Text("  D          Delete selected snapshot", color = White)
                    Text("  Q / Esc    Quit", color = White)
                }

                StartupState.CONFIGANDDOMAINS -> {
                    Text("Config & Domains", color = Cyan, textStyle = Bold)
                    Text("  Tab        Switch Domains / Settings", color = White)
                    Text("  W/S        Move", color = White)
                    Text("  Space      Toggle domain", color = White)
                    Text("  Enter      Toggle / cycle / edit setting", color = White)
                    Text("  D          Download dataset", color = White)
                    Text("  R          Generate DAG (dataset must be present)", color = White)
                    Text("  Esc / Q    Back to welcome", color = White)
                }

                StartupState.MAINDASHBOARD -> {
                    Text("Dashboard", color = Cyan, textStyle = Bold)
                    Text("  M Metrics   C Config   A Arena   B Benchmark   T Trickle", color = White)
                    Text("  G Generate judges", color = White)
                    Spacer()
                    Text("DAG Explorer (topology focus)", color = Cyan, textStyle = Bold)
                    Text("  W/S        Navigate", color = White)
                    Text("  →/L        Expand     ←/H  Collapse     Space  Toggle", color = White)
                    Text("  Enter      Inspect node", color = White)
                    Text("  R          Generate / regenerate node judge", color = White)
                    Spacer()
                    Text("Node detail", color = Cyan, textStyle = Bold)
                    Text("  R          Regenerate judge     W/S  Scroll     ←/Q  Back", color = White)
                    Spacer()
                    Text("Metrics", color = Cyan, textStyle = Bold)
                    Text("  W/S        Select iter / scroll     P  Perf     Home/End  First/Last", color = White)
                }

                StartupState.LOADING -> {
                    Text("Loading…", color = White)
                }
            }
            Spacer()
            Text("Press ? or Esc to close.", color = TuiTheme.RUNNING, textStyle = Bold)
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
        contextual = listOf(
            HotkeyAction("W/S", "Move", TuiTheme.ACCENT),
            HotkeyAction("Enter", "Select", TuiTheme.ACCENT, isPrimary = true),
            HotkeyAction("D", "Delete Snapshot"),
            HotkeyAction("Q", "Quit", TuiTheme.ERROR),
        ),
        global = GlobalHotkeys.forState(state),
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
        contextual = listOf(HotkeyAction("...", "Restoring active taxonomic graph", TuiTheme.RUNNING)),
        global = GlobalHotkeys.forState(state),
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
                val spin = SPINNER[state.shell.spinnerTick % SPINNER.size]
                Text("Status  $spin  ${state.config.datasetDownloadStatusText}", color = Cyan)
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

    HotkeyBar(width, contextual = configHotkeys(state), global = GlobalHotkeys.forState(state))
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

    // When the Arena benchmark config flips into a multi-select picker, the left panel becomes
    // the model/domain selector (reusing DomainSelectorTable) instead of the topology view.
    val benchmarkPicking = state.benchmark.benchmarkIsPickingModels || state.benchmark.benchmarkIsPickingDomains
    val pickerTitle = if (state.benchmark.benchmarkIsPickingModels) "SELECT MODELS" else "SELECT DOMAINS"

    Row(modifier = Modifier.height(topH)) {
        Panel(
            title = when {
                benchmarkPicking -> pickerTitle
                navContext == NavContext.DAG_EXPLORE -> "DAG EXPLORER"
                else -> "NAVIGATOR"
            },
            accentColor = TuiTheme.panelAccent(navFocused),
            width = dagW,
            height = topH,
        ) {
            if (benchmarkPicking) {
                val domains = if (state.benchmark.benchmarkIsPickingModels)
                    state.benchmark.loadedModels.map { it to 0 }
                else
                    availableDomains
                val selected = if (state.benchmark.benchmarkIsPickingModels)
                    state.benchmark.benchmarkSelectedModels.toList()
                else
                    state.benchmark.benchmarkSelectedDomains.toList()
                // Keep the cursor row on-screen by scrolling the window when it runs past the bottom.
                val visibleRows = (topH - 3).coerceAtLeast(1)
                val pickerOffset = (state.benchmark.benchmarkPickerCursor - visibleRows + 1).coerceAtLeast(0)
                DomainSelectorTable(
                    pWidth = dagW - 4,
                    pHeight = topH - 2,
                    domains = domains,
                    offset = pickerOffset,
                    selectedIdx = state.benchmark.benchmarkPickerCursor,
                    selectedDomains = selected,
                )
                return@Panel
            }
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
                        Text("  [X] Load DAG \u2192 Enter (Create new) \u2192 [R] Generate", color = TuiTheme.ACCENT)
                        Spacer()
                        Text("To explore an existing one:", color = TuiTheme.INFO)
                        Text("  [X] Load DAG \u2192 pick a saved snapshot", color = TuiTheme.ACCENT)
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
            benchmarkScroll = state.benchmark.benchmarkScrollOffset,
            trickleState = state.trickle,
            snapshotState = state.snapshot,
            arenaState = state.arena,
            benchmarkState = state.benchmark,
            latestMetrics = subscriptions.metricsHistory.lastOrNull() as? taxonomy.model.IterationMetrics,
            metricsHistory = subscriptions.metricsHistory.mapNotNull { it as? taxonomy.model.IterationMetrics },
            selectedIterationIndex = state.analysis.selectedIterationIndex,
            metricsZoneFocus = state.analysis.metricsZoneFocus,
            showPerformanceBlock = state.analysis.showPerformanceBlock,
            detailScrollOffset = state.analysis.detailScrollOffset,
            performanceReport = if (state.analysis.mode == taxonomy.service.AnalysisMode.METRICS && state.analysis.showPerformanceBlock)
                deps.taxonomyService.getPerformanceReport() else emptyMap(),
            activeProcess = activeProcess,
        )
    }

    Spacer()

    BottomLogsAndTraces(width, bottomH, deps, state, subscriptions)

    // ── Hotkey bar ────────────────────────────────────────────────────────────
    // Modal sub-screens (node detail, metrics scroll, benchmark running) get a
    // focused flat bar with just their own keys + globals.  The default dashboard
    // view (DAG loaded, no modal active) renders the full grouped bar:
    //
    //   DAG : [M] Metrics [C] Config [T] Trickle
    //       | Arena : [A] Arena [G] Generate Judges
    //       | [B] Benchmark [Tab] Switch Panels [?] Help [X] Load DAG [Ctrl-C] Quit
    //
    val inAnalysisHub = state.shell.focusedPanel == FocusPanel.ANALYSIS_HUB
    when {
        inAnalysisHub && state.analysis.mode == taxonomy.service.AnalysisMode.NODE_DETAIL -> {
            val hasJudge = subscriptions.arenaControlState.selectedNode?.judgePrompt != null
            HotkeyBar(
                width,
                contextual = listOf(
                    HotkeyAction("R", if (hasJudge) "Regen Judge" else "Gen Judge", TuiTheme.OK, isPrimary = true),
                    HotkeyAction("W/S", "Scroll"),
                    HotkeyAction("\u2190/Q", "Back", TuiTheme.ERROR),
                    HotkeyAction("M", "Metrics"),
                ),
                global = GlobalHotkeys.forState(state),
            )
        }

        inAnalysisHub && state.analysis.mode == taxonomy.service.AnalysisMode.METRICS -> {
            val contextual = if (state.analysis.metricsZoneFocus == taxonomy.tui.state.MetricsZoneFocus.DETAIL)
                listOf(
                    HotkeyAction("W/S", "Scroll", isPrimary = true),
                    HotkeyAction("P", "Perf"),
                    HotkeyAction("\u2190/Q", "Back", TuiTheme.ERROR),
                )
            else
                listOf(
                    HotkeyAction("W/S", "Select", isPrimary = true),
                    HotkeyAction("P", "Perf"),
                    HotkeyAction("Home/End", "First/Last"),
                    HotkeyAction("\u2190/Q", "Back", TuiTheme.ERROR),
                )
            HotkeyBar(width, contextual = contextual, global = GlobalHotkeys.forState(state))
        }

        inAnalysisHub &&
            state.analysis.mode == taxonomy.service.AnalysisMode.BENCHMARK &&
            state.benchmark.benchmarkType == taxonomy.tui.state.BenchmarkType.ARENA &&
            (subscriptions.arenaControlState.isRunningBenchmark ||
                subscriptions.arenaControlState.benchmarkReport != null) -> {
            HotkeyBar(
                width,
                contextual = listOf(
                    HotkeyAction("V", "Toggle View", TuiTheme.ACCENT, isPrimary = true),
                    HotkeyAction("O", "Load eval_results"),
                    HotkeyAction("Q", "Back", TuiTheme.ERROR),
                ),
                global = GlobalHotkeys.forState(state),
            )
        }

        // ── Default: full grouped bar ─────────────────────────────────────────
        else -> HotkeyBarGrouped(
            width = width,
            groups = taxonomy.tui.components.DashboardHotkeys.groups(
                hasDag = hasDag,
                focused = state.shell.focusedPanel,
                isRegenerating = state.runtime.isRegenerating,
                isViewingSnapshot = state.snapshot.isViewingSnapshot,
                state = state,
            ),
        )
    }
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

        val procRows = deriveProcessRows(deps, state, subscriptions)
        val runningCount = procRows.count { !it.done && !it.error }
        Panel(
            title = "PROCESSES",
            accentColor = TuiTheme.panelAccent(state.shell.focusedPanel == FocusPanel.PROCESSES),
            width = procW - 1,
            height = bottomH,
            badge = if (runningCount > 0) "$runningCount RUNNING" else null,
        ) {
            ProcessesPanel(
                width = procW - 4,
                height = bottomH - 2,
                rows = procRows,
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

    // Eval-results auto-download from GitHub.
    if (state.benchmark.isDownloadingEval) {
        val files = state.benchmark.evalDownloadProgress
        val done = files.values.count { it >= 1f }
        val pct = if (files.isNotEmpty()) done.toDouble() / files.size * 100.0 else null
        rows += ProcessRow(
            name = "Eval download",
            percent = pct,
            status = if (files.isEmpty()) "Fetching listing\u2026" else "$done / ${files.size} files",
        )
    }

    // Live benchmark progress.
    if (subscriptions?.arenaControlState?.isRunningBenchmark == true) {
        state.benchmark.liveStats?.let { live ->
            val pct = if (live.total > 0) live.processed.toDouble() / live.total * 100.0 else null
            rows += ProcessRow(
                name = "Benchmark",
                percent = pct,
                status = "${live.processed} / ${live.total} \u00b7 agreement ${"%.2f".format(live.runningAgreement)}",
            )
        }
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
        add(HotkeyAction("W/S", "Move", TuiTheme.ACCENT))
        if (inDomains) {
            add(HotkeyAction("Space", "Toggle Domain"))
        } else {
            add(HotkeyAction("Enter", "Toggle/Cycle/Edit"))
        }
        if (state.runtime.isDatasetDownloaded) {
            add(HotkeyAction("R", "Generate DAG", TuiTheme.OK, isPrimary = true))
        } else {
            add(HotkeyAction("D", "Download Dataset", TuiTheme.OK, isPrimary = true))
            add(HotkeyAction("R", "(download first)", TuiTheme.INFO))
        }
        add(HotkeyAction("Esc", "Back", TuiTheme.ERROR))
    }
}

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
