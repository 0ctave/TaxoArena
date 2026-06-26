package taxonomy.tui.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import com.jakewharton.mosaic.layout.height
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
import taxonomy.tui.components.Panel
import taxonomy.tui.components.ProcessRow
import taxonomy.tui.components.ProcessesPanel
import taxonomy.tui.components.ProgressBar
import taxonomy.tui.components.StartupState
import taxonomy.tui.components.TuiTheme
import taxonomy.tui.components.TuiTheme.SPINNER
import taxonomy.tui.components.VDivider
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

        VDivider(contentH, White, Cyan)

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

    Text("Use W/S to choose, Enter to select.", color = White)
}

@Composable
private fun LoadingRoute(
    width: Int,
    height: Int,
    state: TuiAppState,
) {
    val contentH = (height - 4).coerceAtLeast(4)
    LoadingPanel(width = width - 2, height = contentH, spinnerTick = state.shell.spinnerTick)
    Text("Please wait while the active taxonomic graph is restored...", color = White)
}

@Composable
private fun ConfigRoute(
    width: Int,
    height: Int,
    deps: TuiDependencies,
    state: TuiAppState,
    subscriptions: TuiSubscriptions,
) {
    val topH = ((height - 4) * 0.62).toInt().coerceAtLeast(10)
    val bottomH = (height - 4 - topH).coerceAtLeast(5)
    val leftW = (width * 0.35).toInt().coerceAtLeast(20)
    val rightW = (width - leftW - 1).coerceAtLeast(20)

    val facade = remember(deps) { TuiConfigFacade(deps) }
    val settingItems = remember(state.config.settingsVersion) { facade.buildSettingItems() }
    val availableDomains = remember(state.config.settingsVersion, state.runtime.availableDomainsVersion) {
        facade.getAvailableDomains()
    }

    if (state.runtime.isRegenerating) {
        Panel("TAXONOMY GENERATION IN PROGRESS", Cyan, width - 2, topH) {
            Column(modifier = Modifier.padding(left = 2, top = 1)) {
                Text(
                    "Running Adaptive Taxonomy Evolution in 4096-D Embedding Space...",
                    color = White,
                    textStyle = Bold
                )
                Spacer()
                ProgressBar(
                    percent = extractPercent(subscriptions.generationProgress),
                    width = (width - 25).coerceIn(20, 80),
                    label = "Generation Progress"
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

            VDivider(topH, White, Cyan)

            Panel(
                title = "SETTINGS",
                accentColor = TuiTheme.panelAccent(state.config.activeSubPanel == ConfigSubPanel.SETTINGS),
                width = rightW,
                height = topH
            ) {
                Column(modifier = Modifier.padding(left = 2, top = 1)) {
                    settingItems.forEachIndexed { idx, item ->
                        val selected = idx == state.config.selectedSettingIdx
                        val value =
                            if (selected && state.config.isEditingSetting) state.config.editingValue + "_"
                            else item.getValue()
                        Text(
                            value = (if (selected) "> " else "  ") + item.name + ": " + value,
                            color = if (selected) Cyan else White,
                            textStyle = if (selected) Bold else Unspecified
                        )
                    }
                }
            }
        }
    }

    Spacer()

    BottomLogsAndTraces(width, bottomH, deps, state)

    Text(
        buildConfigFooter(
            isDatasetDownloaded = state.runtime.isDatasetDownloaded,
            downloading = state.config.downloadingDataset
        ),
        color = White
    )
}

@Composable
private fun MainDashboardRoute(
    width: Int,
    height: Int,
    deps: TuiDependencies,
    state: TuiAppState,
    subscriptions: TuiSubscriptions,
) {
    val topH = ((height - 4) * 0.62).toInt().coerceAtLeast(10)
    val bottomH = (height - 4 - topH).coerceAtLeast(5)
    val dagW = 60.coerceAtMost(width - 20)
    val arenaW = (width - dagW - 1).coerceAtLeast(20)

    val facade = remember(deps) { TuiConfigFacade(deps) }
    val availableDomains = remember(state.config.settingsVersion, state.runtime.availableDomainsVersion) {
        facade.getAvailableDomains()
    }
    val allNodes = remember(subscriptions.rootNode, subscriptions.graphVersion) {
        flattenNodes(subscriptions.rootNode)
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
                    treeLines = subscriptions.treeLines,
                )
                else -> Column(modifier = Modifier.padding(left = 2, top = 1)) {
                    Text("No taxonomy DAG loaded.", color = TuiTheme.INFO, textStyle = Bold)
                    Spacer()
                    Text("[X] Welcome / load a snapshot", color = TuiTheme.ACCENT)
                    Text("[R] Configure & generate a new DAG", color = TuiTheme.ACCENT)
                }
            }
        }

        VDivider(topH, White, Cyan)

        Panel(
            title = "ANALYSIS HUB",
            accentColor = TuiTheme.panelAccent(state.shell.focusedPanel == FocusPanel.ANALYSIS_HUB),
            width = arenaW,
            height = topH,
        ) {
            // Most relevant active process, pinned at the top of the dashboard
            // so it is always visible and one keystroke away (selection wins).
            val activeProcess = deriveProcessRows(deps, state, subscriptions).firstOrNull { !it.done }
            AnalysisPanel(
                width = arenaW - 4,
                height = topH - 2,
                controlState = subscriptions.arenaControlState,
                inspectorScroll = state.analysis.inspectorScroll,
                metricsScroll = state.analysis.metricsScrollOffset,
                benchmarkScroll = state.benchmark.benchmarkScrollOffset,
                batchTrickleScroll = state.trickle.batchTrickleScrollOffset,
                trickleResults = state.trickle.batchTrickleResults,
                snapshotState = state.snapshot,
                arenaState = state.arena,
                benchmarkState = state.benchmark,
                activeProcess = activeProcess,
            )
        }
    }

    Spacer()

    BottomLogsAndTraces(width, bottomH, deps, state, subscriptions)

    Text("Tab switch panels  W/S navigate  Enter select  X welcome", color = White)
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
            LogsPanel(logsW - 4, bottomH, state.logs.logScrollOffset, title = "")
        }

        VDivider(bottomH, White, Cyan)

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

    // Dataset download.
    if (state.config.downloadingDataset) {
        rows += ProcessRow(
            name = "Dataset download",
            percent = state.config.datasetDownloadProgress * 100.0,
            status = state.config.datasetDownloadStatusText,
        )
    }

    // Embedding compute (Pair<current,total>).
    (subscriptions?.embeddingProgress as? Pair<*, *>)?.let { (cur, total) ->
        val c = (cur as? Int) ?: 0; val t = (total as? Int) ?: 0
        if (t > 0 && c < t) rows += ProcessRow(
            name = "Embedding queries",
            percent = c.toDouble() / t * 100.0,
            status = "$c / $t",
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
            status = "$c / $t",
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

private fun buildConfigFooter(
    isDatasetDownloaded: Boolean,
    downloading: Boolean,
): String =
    when {
        downloading ->
            "Tab Switch Panels  W/S Navigate  Downloading..."
        isDatasetDownloaded ->
            "Tab Switch  W/S Navigate  Space/Enter Toggle/Edit  R Generate DAG  Esc/Q Back"
        else ->
            "Tab Switch  W/S Navigate  Space/Enter Toggle/Edit  D Download Dataset  Esc/Q Back"
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
