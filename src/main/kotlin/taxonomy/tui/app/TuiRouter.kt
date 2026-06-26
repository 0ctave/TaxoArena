package taxonomy.tui.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Column
import com.jakewharton.mosaic.ui.Row
import com.jakewharton.mosaic.ui.Spacer
import com.jakewharton.mosaic.ui.Text
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import taxonomy.model.GraphNode
import taxonomy.tui.AnalysisHub
import taxonomy.tui.components.Panel
import taxonomy.tui.components.ProgressBar
import taxonomy.tui.components.StartupState
import taxonomy.tui.components.TuiTheme.SPINNER
import taxonomy.tui.components.VDivider
import taxonomy.tui.components.DomainSelectorTable   // ← was wrongly panels.*
import taxonomy.tui.panels.LogView
import taxonomy.tui.panels.TopologyView
import taxonomy.tui.state.ConfigSubPanel
import taxonomy.tui.state.FocusPanel
import taxonomy.tui.state.TuiAppState
import java.util.Locale

@Composable
fun TuiRouter(
    width: Int,
    height: Int,
    deps: TuiDependencies,
    state: TuiAppState,
    subscriptions: TuiSubscriptions,
) {
    when (state.startup.state) {
        StartupState.WELCOME -> WelcomeRoute(width, height, state)
        StartupState.LOADING -> LoadingRoute(width, height, state)
        StartupState.CONFIGANDDOMAINS -> ConfigRoute(width, height, deps, state, subscriptions)
        StartupState.MAINDASHBOARD -> MainDashboardRoute(width, height, deps, state, subscriptions)
    }
}

@Composable
private fun WelcomeRoute(
    width: Int,
    height: Int,
    state: TuiAppState,
) {
    val contentH = height - 4
    val leftW = ((width - 4) * 0.45).toInt().coerceAtLeast(30)
    val rightW = width - leftW - 3

    Row(modifier = Modifier.height(contentH)) {
        Panel("SETUP HUB", Cyan, leftW, contentH) {
            Column(modifier = Modifier.padding(left = 2, top = 1)) {
                Text("Select an option to initialize the taxonomic DAG.", color = White)
                Spacer()

                val selectedNew = state.startup.selectedWelcomeIdx == 0
                Text(
                    text = (if (selectedNew) "> " else "  ") + "Generate new DAG",
                    color = if (selectedNew) Cyan else White,
                    textStyle = if (selectedNew) Bold else null
                )

                Spacer()
                Text("Snapshots", color = Yellow, textStyle = Bold)

                state.snapshot.snapshotList.forEachIndexed { idx, snap ->
                    val selected = state.startup.selectedWelcomeIdx == idx + 1
                    Text(
                        text = (if (selected) "> " else "  ") + snap.description,
                        color = if (selected) Cyan else White,
                        textStyle = if (selected) Bold else null
                    )
                }
            }
        }

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
                        "Equilibrium ${"%.1f".format(Locale.US, selectedSnapshot.metrics.equilibriumIndex * 100.0)}",
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
    val contentH = height - 4

    Panel("SETUP HUB  LOADING PREGENERATED SNAPSHOT", Cyan, width - 2, contentH) {
        Column(modifier = Modifier.padding(left = 4, top = 2)) {
            Text(
                "Retrieving serialized taxonomy snapshot from SQLite DB...",
                color = White,
                textStyle = Bold
            )
            Spacer()
            Text("Reassembling 4096-D statistical vMF-NiW node parameters...", color = White)
            Spacer()
            Text("Parsing historical adaptive run logs...", color = White)
            Spacer()
            Row {
                Text("Status ", color = White)
                Text(
                    "LOADING SNAPSHOT ${SPINNER[state.shell.spinnerTick % SPINNER.size]}",
                    color = Yellow,
                    textStyle = Bold
                )
            }
        }
    }

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
    val rightW = width - leftW - 1

    val availableDomains = remember(state.config.settingsVersion, state.runtime.availableDomainsVersion) {
        deps.datasetFetcher.getAvailableDomains()
    }

    val isDatasetDownloaded = state.runtime.isDatasetDownloaded

    if (state.runtime.isRegenerating) {
        Panel("TAXONOMY GENERATION IN PROGRESS", Cyan, width - 2, topH) {
            Column(modifier = Modifier.padding(left = 2, top = 1)) {
                Text(
                    "Running Adaptive Taxonomy Evolution in 4096-D Embedding Space...",
                    color = White,
                    textStyle = Bold
                )
                Spacer()
                val pct = extractPercent(subscriptions.generationProgress)
                ProgressBar(
                    percent = pct,
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
                // ← use `accent` not `titleColor` to match the real Panel signature
                title = "DOMAINS",
                accent = if (state.config.activeSubPanel == ConfigSubPanel.DOMAINS) Cyan else White,
                width = leftW,
                height = topH
            ) {
                DomainSelectorTable(
                    width = leftW - 4,
                    height = topH - 2,
                    domains = availableDomains,
                    selectedDomains = deps.config.dataset.selectedDomains,
                    selectedIdx = state.config.selectedDomainIdx,
                    scrollOffset = state.config.domainScrollOffset
                )
            }

            VDivider(topH, White, Cyan)

            Panel(
                title = "SETTINGS",
                accent = if (state.config.activeSubPanel == ConfigSubPanel.SETTINGS) Cyan else White,
                width = rightW,
                height = topH
            ) {
                Column(modifier = Modifier.padding(left = 2, top = 1)) {
                    state.config.settingItems.forEachIndexed { idx, item ->
                        val selected = idx == state.config.selectedSettingIdx
                        Text(
                            text = (if (selected) "> " else "  ") + item.name + ": " + item.getValue(),
                            color = if (selected) Cyan else White,
                            textStyle = if (selected) Bold else null
                        )
                    }
                }
            }
        }
    }

    Spacer()

    Row(modifier = Modifier.height(bottomH)) {
        val logsW = (width * 0.60).toInt()
        val traceW = width - logsW - 1

        Panel(
            title = "SYSTEM LOGS",
            accent = if (state.shell.focusedPanel == FocusPanel.SYSTEM_LOGS) Cyan else White,
            width = logsW,
            height = bottomH
        ) {
            // ← positional args, no named params
            LogView(logsW - 4, bottomH - 2, state.logs.logScrollOffset)
        }

        VDivider(bottomH, White, Cyan)

        Panel(title = "GPU TRACES", accent = White, width = traceW - 1, height = bottomH) {
            deps.host.InferenceStreams(
                width = traceW - 5,
                height = bottomH - 2,
                spinnerTick = state.shell.spinnerTick
            )
        }
    }

    Text(
        buildConfigFooter(
            isDatasetDownloaded = isDatasetDownloaded,
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
    val dagW = 60
    val arenaW = width - dagW - 1

    val allNodes = remember(subscriptions.rootNode, state.runtime.graphVersion) {
        flattenNodes(subscriptions.rootNode)
    }

    Row(modifier = Modifier.height(topH)) {
        Panel(
            title = "TOPOLOGY",
            accent = if (state.shell.focusedPanel == FocusPanel.TOPOLOGY) Cyan else White,
            width = dagW,
            height = topH,
        ) {
            TopologyView(
                pWidth = dagW - 4,
                pHeight = topH - 2,
                rootNode = subscriptions.rootNode,
                allNodes = allNodes,
                treeLines = subscriptions.treeLines,
                showAsciiTree = state.topology.showAsciiTree,
                selectedIdx = state.topology.selectedListIdx,
                selectedTreeIdx = state.topology.selectedTreeIdx,
                scrollOffset = state.topology.scrollOffset,
                treeScrollOffset = state.topology.treeScrollOffset,
            )
        }

        VDivider(topH, White, Cyan)

        Panel(
            title = "ANALYSIS HUB",
            accent = if (state.shell.focusedPanel == FocusPanel.ANALYSIS_HUB) Cyan else White,
            width = arenaW,
            height = topH,
        ) {
            AnalysisHub(
                pWidth = arenaW - 4,
                pHeight = topH - 2,
                mode = subscriptions.arenaControlState.mode,
                controlState = subscriptions.arenaControlState,
                settingItems = state.config.settingItems,
                selectedSettingIdx = state.config.selectedSettingIdx,
                isEditingSetting = state.config.isEditingSetting,
                editingValue = state.config.editingValue,
                inspectorLines = subscriptions.inspectorLines,
                inspectorScroll = state.topology.inspectorScroll,
                metricsHistory = subscriptions.metricsHistory,
                metricsScrollOffset = state.topology.metricsScrollOffset,
                snapshotList = state.snapshot.snapshotList,
                selectedSnapshotIdx = state.snapshot.selectedSnapshotIdx,
                isSavingSnapshot = state.snapshot.isSavingSnapshot,
                snapshotDescInput = state.snapshot.snapshotDescInput,
                isRenamingSnapshot = state.snapshot.isRenamingSnapshot,
                renameInput = state.snapshot.renameInput,
                isViewingSnapshot = state.snapshot.isViewingSnapshot,
                activeSnapshotId = state.snapshot.activeSnapshotId,
            )
        }
    }

    Spacer()

    Row(modifier = Modifier.height(bottomH)) {
        val logsW = (width * 0.60).toInt()
        val traceW = width - logsW - 1

        Panel(
            title = "SYSTEM LOGS",
            accent = if (state.shell.focusedPanel == FocusPanel.SYSTEM_LOGS) Cyan else White,
            width = logsW,
            height = bottomH
        ) {
            LogView(logsW - 4, bottomH - 2, state.logs.logScrollOffset)
        }

        VDivider(bottomH, White, Cyan)

        Panel(title = "GPU TRACES", accent = White, width = traceW - 1, height = bottomH) {
            deps.host.InferenceStreams(
                width = traceW - 5,
                height = bottomH - 2,
                spinnerTick = state.shell.spinnerTick
            )
        }
    }

    Text("Tab switch panels  W/S navigate  Enter select  X welcome", color = White)
}

private fun extractPercent(progress: Any?): Double =
    when (progress) {
        null -> 0.0
        else -> {
            try {
                val method = progress::class.java.methods.firstOrNull { it.name == "getPercentComplete" }
                (method?.invoke(progress) as? Number)?.toDouble() ?: 0.0
            } catch (_: Throwable) {
                0.0
            }
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
            "Tab Switch Panels  W/S Navigate  Space/Enter Toggle/Edit  A Select All  C Clear Others  R Generate DAG  Esc/Q Back"
        else ->
            "Tab Switch Panels  W/S Navigate  Space/Enter Toggle/Edit  A Select All  C Clear Others  D Download Dataset  R Disabled Download First  Esc/Q Back"
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