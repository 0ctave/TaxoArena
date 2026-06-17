package org.eclipse.lmos.arc.app.taxonomy.tui

import androidx.compose.runtime.*
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.*
import com.jakewharton.mosaic.layout.*
import com.jakewharton.mosaic.text.*
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import com.jakewharton.mosaic.ui.Color.Companion.Blue
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.Magenta
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Black
import com.jakewharton.mosaic.ui.Color.Companion.Red
import com.jakewharton.mosaic.animation.animateColorAsState
import kotlinx.coroutines.*
import kotlinx.serialization.json.*
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import org.eclipse.lmos.arc.app.taxonomy.*
import org.eclipse.lmos.arc.app.taxonomy.operations.*
import com.jakewharton.mosaic.LocalTerminalState
import com.jakewharton.mosaic.terminal.Terminal
import com.jakewharton.mosaic.terminal.*
import com.jakewharton.mosaic.animation.*
import org.fusesource.jansi.AnsiConsole

    @Composable
    internal fun TaxonomyTuiService.Dashboard(terminal: Terminal) {
        val terminalState = LocalTerminalState.current
        var width by remember { mutableIntStateOf(terminalState.size.columns) }
        var height by remember { mutableIntStateOf(terminalState.size.rows) }

        if (width < 100 || height < 20) {
            Column {
                Text("  ╔══════════════════════╗  ", color = Yellow, textStyle = Bold)
                Text("  ║  WINDOW TOO SMALL    ║  ", color = Black, background = Yellow, textStyle = Bold)
                Text("  ╚══════════════════════╝  ", color = Yellow, textStyle = Bold)
                Text("  Minimum: 100×20 │ Current: ${width}×${height}", color = White)
            }
            return
        }

        val rootNode     by taxonomyService.rootNodeFlow.collectAsState()
        val graphVersion by taxonomyService.graphVersionFlow.collectAsState()
        val controlState by arenaService.state.collectAsState()
        val time by produceState(LocalTime.now()) {
            while (true) { delay(1000); value = LocalTime.now() }
        }
        // Spinner tick – updates every 120 ms for active GPU slots
        var spinnerTick by remember { mutableIntStateOf(0) }
        LaunchedEffect(Unit) { while (true) { delay(120); spinnerTick = (spinnerTick + 1) % SPINNER.size } }

        var scrollOffset   by remember { mutableIntStateOf(0) }
        var selectedIdx    by remember { mutableIntStateOf(0) }
        var autoScroll     by remember { mutableStateOf(true) }
        var inspectorScroll by remember { mutableIntStateOf(0) }
        var logScrollOffset by remember { mutableIntStateOf(0) }

        // Settings-specific Compose State
        var selectedSettingIdx by remember { mutableIntStateOf(0) }
        var isEditingSetting by remember { mutableStateOf(false) }
        var editingValue by remember { mutableStateOf("") }
        var settingsVersion by remember { mutableIntStateOf(0) }
        var selectedSnapshotIdx by remember { mutableIntStateOf(0) }
        var isSavingSnapshot by remember { mutableStateOf(false) }
        var snapshotDescInput by remember { mutableStateOf("") }
        val snapshotList = remember(snapshotVersion) { snapshotManager.listSnapshots() }
        var startupState by remember { mutableStateOf(StartupState.WELCOME) }
        var selectedWelcomeIdx by remember { mutableIntStateOf(0) }
        LaunchedEffect(snapshotList) {
            if (snapshotList.isEmpty()) {
                selectedSnapshotIdx = 0
            } else {
                selectedSnapshotIdx = selectedSnapshotIdx.coerceIn(0, snapshotList.size - 1)
            }
            val welcomeOptionsCount = 1 + snapshotList.size
            selectedWelcomeIdx = selectedWelcomeIdx.coerceIn(0, welcomeOptionsCount - 1)
        }
        var activeConfigPanel by remember { mutableStateOf("DOMAINS") }
        var showAsciiTree by remember { mutableStateOf(true) }
        val expandedNodes = remember { mutableStateMapOf<String, Boolean>() }
        var selectedTreeIdx by remember { mutableIntStateOf(0) }
        var treeScrollOffset by remember { mutableIntStateOf(0) }

        val settingItems = remember(settingsVersion) {
            listOf(
                SettingItem(
                    name = "Evolution Iterations",
                    description = "Number of optimization iterations",
                    getValue = { config.execution.numIterations.toString() },
                    setValue = { s -> s.toIntOrNull()?.let { config.execution.numIterations = it; true } ?: false }
                ),
                SettingItem(
                    name = "Live Labeling",
                    description = "Enable live LLM labeling of nodes during execution",
                    getValue = { config.formalism.enableLiveLabeling.toString() },
                    setValue = { s -> s.toBooleanStrictOrNull()?.let { config.formalism.enableLiveLabeling = it; true } ?: false }
                ),
                SettingItem(
                    name = "Labeling Model",
                    description = "LLM model used for node label generation",
                    getValue = { config.llm.labelingModel },
                    setValue = { s -> if (s.isNotBlank()) { config.llm.labelingModel = s; true } else false }
                ),
                SettingItem(
                    name = "Expert Judge Model",
                    description = "LLM model used for pairwise judgments",
                    getValue = { config.llm.judgeModel },
                    setValue = { s -> if (s.isNotBlank()) { config.llm.judgeModel = s; true } else false }
                ),
                SettingItem(
                    name = "LLM Provider",
                    description = "Source for LLM model (OLLAMA or AZURE)",
                    getValue = { config.llm.provider.name },
                    setValue = { s ->
                        try {
                            config.llm.provider = org.eclipse.lmos.arc.app.taxonomy.LlmProviderType.valueOf(s.uppercase())
                            true
                        } catch (e: Exception) { false }
                    }
                ),
                SettingItem(
                    name = "Embedding Provider",
                    description = "Source for Embedding model (OLLAMA or AZURE)",
                    getValue = { config.llm.embeddingProvider.name },
                    setValue = { s ->
                        try {
                            config.llm.embeddingProvider = org.eclipse.lmos.arc.app.taxonomy.LlmProviderType.valueOf(s.uppercase())
                            true
                        } catch (e: Exception) { false }
                    }
                ),
                SettingItem(
                    name = "Embedding Model",
                    description = "Model name/deployment used for generating query/concept embeddings",
                    getValue = { config.llm.embeddingModel },
                    setValue = { s -> if (s.isNotBlank()) { config.llm.embeddingModel = s; true } else false }
                ),
                SettingItem(
                    name = "Max Hierarchy Depth",
                    description = "Maximum depth of the taxonomic DAG",
                    getValue = { config.formalism.maxDepth.toString() },
                    setValue = { s -> s.toIntOrNull()?.let { config.formalism.maxDepth = it; true } ?: false }
                ),
                SettingItem(
                    name = "Split Base Threshold",
                    description = "Minimum query count to trigger concept splitting",
                    getValue = { config.formalism.splitBaseThreshold.toString() },
                    setValue = { s -> s.toIntOrNull()?.let { config.formalism.splitBaseThreshold = it; true } ?: false }
                ),
                SettingItem(
                    name = "Tau Fit",
                    description = "Likelihood threshold for GMM fitting (Hysteresis rule)",
                    getValue = { config.formalism.tauFit.toString() },
                    setValue = { s -> s.toDoubleOrNull()?.let { config.formalism.tauFit = it; true } ?: false }
                ),
                SettingItem(
                    name = "Tau Reparent",
                    description = "Likelihood threshold for reparenting (Hysteresis rule)",
                    getValue = { config.formalism.tauReparent.toString() },
                    setValue = { s -> s.toDoubleOrNull()?.let { config.formalism.tauReparent = it; true } ?: false }
                ),
                SettingItem(
                    name = "Tau Merge",
                    description = "Likelihood threshold for domain merging (Hysteresis rule)",
                    getValue = { config.formalism.tauMerge.toString() },
                    setValue = { s -> s.toDoubleOrNull()?.let { config.formalism.tauMerge = it; true } ?: false }
                ),
                SettingItem(
                    name = "Split Dataset",
                    description = "Whether to split the dataset 80% train / 20% test",
                    getValue = { config.dataset.splitDataset.toString() },
                    setValue = { s -> s.lowercase().toBooleanStrictOrNull()?.let { config.dataset.splitDataset = it; true } ?: false }
                ),
                SettingItem(
                    name = "Test Split Ratio",
                    description = "Ratio of reserved test set queries (e.g. 0.2)",
                    getValue = { config.dataset.testSplitRatio.toString() },
                    setValue = { s -> s.toDoubleOrNull()?.let { config.dataset.testSplitRatio = it; true } ?: false }
                ),
                SettingItem(
                    name = "Selected Domains",
                    description = "Comma-separated domains to filter (e.g. Business, Math)",
                    getValue = { config.dataset.selectedDomains.joinToString(", ") },
                    setValue = { s ->
                        config.dataset.selectedDomains = s.split(",")
                            .map { it.trim() }
                            .filter { it.isNotEmpty() }
                        true
                    }
                ),
                SettingItem(
                    name = "Fixed Dimension Limit",
                    description = "Fixed dimension limit used for routing and fitting",
                    getValue = { config.formalism.fixedMrlDimension.toString() },
                    setValue = { s -> s.toIntOrNull()?.let { config.formalism.fixedMrlDimension = it; true } ?: false }
                ),
                SettingItem(
                    name = "Collapse Marginal Ratio",
                    description = "Sibling ratio under which a node collapses to parent (e.g. 0.05)",
                    getValue = { config.formalism.collapseMarginalRatio.toString() },
                    setValue = { s -> s.toDoubleOrNull()?.let { config.formalism.collapseMarginalRatio = it; true } ?: false }
                )
            )
        }

        val allNodes = remember(rootNode, graphVersion) {
            if (rootNode == null) emptyList()
            else {
                val list = mutableListOf<GraphNode>()
                fun walk(n: GraphNode, visited: MutableSet<String>) {
                    if (!visited.add(n.id)) return
                    list.add(n)
                    n.children.forEach { walk(it, visited) }
                }
                walk(rootNode!!, mutableSetOf())
                list.sortedByDescending { it.queries.size }
            }
        }

        val treeLines = remember(rootNode, expandedNodes.entries.toList(), settingsVersion, graphVersion) {
            buildTreeLines(rootNode, expandedNodes)
        }

        LaunchedEffect(rootNode) {
            expandedNodes.clear()
            rootNode?.let {
                expandedNodes[it.id] = true
                it.children.forEach { child ->
                    expandedNodes[child.id] = false
                }
            }
            selectedTreeIdx = 0
            treeScrollOffset = 0
        }

        val dagWidth   = 60
        val arenaWidth = width - dagWidth - 1

        // ── Inspector content (recomputed only when selected node or width changes) ──
        val inspectorLines = remember(controlState.selectedNode, arenaWidth) {
            buildInspectorLines(controlState.selectedNode, arenaWidth)
        }

        val mode = controlState.mode

        var focusedPanel by remember { mutableStateOf("TOPOLOGY") }

        val availableDomains = remember { datasetFetcher.getAvailableDomains() }
        var showDomainSelector by remember { mutableStateOf(false) }
        var selectedDomainIdx by remember { mutableIntStateOf(0) }
        var domainScrollOffset by remember { mutableIntStateOf(0) }

        val toggleDomain = { domainName: String ->
            val current = if (config.dataset.selectedDomains.isEmpty()) {
                availableDomains.map { it.first }.toMutableList().apply { remove(domainName) }
            } else {
                config.dataset.selectedDomains.toMutableList().apply {
                    if (contains(domainName)) {
                        remove(domainName)
                    } else {
                        add(domainName)
                    }
                }
            }
            if (current.size == availableDomains.size) {
                config.dataset.selectedDomains = emptyList()
            } else {
                config.dataset.selectedDomains = current
            }
            settingsVersion++
        }

        // --- Animations from mosaic-animation ---
        val topologyAccentState = animateColorAsState(if (focusedPanel == "TOPOLOGY") Cyan else White)
        val hubAccentState = animateColorAsState(if (focusedPanel == "ANALYSIS HUB") Cyan else White)
        val logsAccentState = animateColorAsState(if (focusedPanel == "SYSTEM LOGS") Cyan else White)

        val topologyAccent = topologyAccentState.value
        val hubAccent = hubAccentState.value
        val logsAccent = logsAccentState.value

        val regeneratingColorState = animateColorAsState(
            if (isRegenerating) {
                if (spinnerTick % 2 == 0) Yellow else Cyan
            } else Yellow
        )
        val regeneratingColor = regeneratingColorState.value

        val handleKeyPress = keyHandler@ { key: String, rawKey: String ->
            if (startupState == StartupState.WELCOME) {
                val welcomeOptionsCount = 1 + snapshotList.size
                when {
                    key == "z" || key == "w" || key == "arrowup" -> {
                        selectedWelcomeIdx = (selectedWelcomeIdx - 1 + welcomeOptionsCount) % welcomeOptionsCount
                        true
                    }
                    key == "s" || key == "arrowdown" -> {
                        selectedWelcomeIdx = (selectedWelcomeIdx + 1) % welcomeOptionsCount
                        true
                    }
                    key == "d" -> {
                        if (selectedWelcomeIdx > 0 && selectedWelcomeIdx - 1 in snapshotList.indices) {
                            val snap = snapshotList[selectedWelcomeIdx - 1]
                            snapshotManager.deleteSnapshot(snap.id)
                            if (isViewingSnapshot && activeSnapshotId == snap.id) {
                                isViewingSnapshot = false
                                activeSnapshotId = null
                                activeSnapshotDescription = null
                            }
                            snapshotVersion++
                            if (selectedWelcomeIdx >= welcomeOptionsCount - 1) {
                                selectedWelcomeIdx = welcomeOptionsCount - 2
                            }
                            log.info("Deleted snapshot '${snap.description}'")
                        }
                        true
                    }
                    key == "escape" || key == "q" -> {
                        if (rootNode != null) {
                            startupState = StartupState.MAIN_DASHBOARD
                            focusedPanel = "TOPOLOGY"
                            true
                        } else {
                            false
                        }
                    }
                    key == "enter" -> {
                        if (selectedWelcomeIdx == 0) {
                            isViewingSnapshot = false
                            startupState = StartupState.CONFIG_AND_DOMAINS
                            activeConfigPanel = "DOMAINS"
                            selectedDomainIdx = 0
                            selectedSettingIdx = 0
                        } else {
                            val snap = snapshotList[selectedWelcomeIdx - 1]
                            val loadedRoot = snapshotManager.loadSnapshot(snap.id)
                            if (loadedRoot != null) {
                                isViewingSnapshot = true
                                activeSnapshotId = snap.id
                                activeSnapshotDescription = snap.description
                                taxonomyService.setGraph(loadedRoot)
                                config.dataset.selectedDomains = snap.settings.selectedDomains
                                config.formalism.enableMrl = snap.settings.enableMrl
                                config.formalism.enableLiveLabeling = snap.settings.enableLiveLabeling
                                config.formalism.fixedMrlDimension = snap.settings.fixedMrlDimension
                                config.formalism.tauFit = snap.settings.tauFit
                                config.formalism.tauReparent = snap.settings.tauReparent
                                config.formalism.tauMerge = snap.settings.tauMerge
                                config.formalism.maxDepth = snap.settings.maxDepth
                                config.formalism.collapseMarginalRatio = snap.settings.collapseMarginalRatio
                                settingsVersion++

                                taxonomyService.clearMetricsHistory()
                                val report = TaxonomyMetrics(loadedRoot).generateReport()
                                taxonomyService.addIterationMetrics("Loaded Snapshot", report)
                                
                                startupState = StartupState.MAIN_DASHBOARD
                                focusedPanel = "TOPOLOGY"
                            } else {
                                log.error("Failed to load snapshot ${snap.id}")
                            }
                        }
                        true
                    }
                    else -> false
                }
            } else if (startupState == StartupState.CONFIG_AND_DOMAINS) {
                if (focusedPanel == "SYSTEM LOGS") {
                    val bottomH  = (height - 7 - ((height - 7) * 0.62).toInt().coerceAtLeast(10)).coerceAtLeast(5)
                    val visibleH = (bottomH - 2).coerceAtLeast(1)
                    val maxScroll = maxOf(0, TuiLogAppender.logs.size - visibleH)
                    when {
                        key == "z" || key == "w" || key == "arrowup" -> {
                            logScrollOffset = (logScrollOffset + 1).coerceIn(0, maxScroll)
                            true
                        }
                        key == "s" || key == "arrowdown" -> {
                            logScrollOffset = (logScrollOffset - 1).coerceAtLeast(0)
                            true
                        }
                        key == "q" || key == "escape" || key == "backspace" || key == "arrowleft" -> {
                            logScrollOffset = 0
                            focusedPanel = "CONFIG"
                            true
                        }
                        else -> false
                    }
                } else {
                    if (isEditingSetting) {
                        when {
                            key == "enter" -> {
                                if (selectedSettingIdx in settingItems.indices) {
                                    val item = settingItems[selectedSettingIdx]
                                    val success = item.setValue(editingValue)
                                    if (success) {
                                        isEditingSetting = false
                                        settingsVersion++
                                    }
                                }
                                true
                            }
                            key == "escape" || (key == "q" && editingValue.isEmpty()) -> {
                                isEditingSetting = false; true
                            }
                            key == "backspace" -> {
                                if (editingValue.isNotEmpty()) {
                                    editingValue = editingValue.dropLast(1)
                                }
                                true
                            }
                            rawKey.length == 1 -> {
                                editingValue += rawKey
                                true
                            }
                            else -> false
                        }
                    } else {
                        when {
                            key == "tab" || key == "\t" -> {
                                activeConfigPanel = if (activeConfigPanel == "DOMAINS") "SETTINGS" else "DOMAINS"
                                true
                            }
                            key == "z" || key == "w" || key == "arrowup" -> {
                                if (activeConfigPanel == "DOMAINS") {
                                    selectedDomainIdx = (selectedDomainIdx - 1 + availableDomains.size) % availableDomains.size
                                    val topH = ((height - 7) * 0.62).toInt().coerceAtLeast(10)
                                    val visibleItems = (topH - 4).coerceAtLeast(1)
                                    if (selectedDomainIdx < domainScrollOffset) domainScrollOffset = selectedDomainIdx
                                } else {
                                    selectedSettingIdx = (selectedSettingIdx - 1 + settingItems.size) % settingItems.size
                                }
                                true
                            }
                            key == "s" || key == "arrowdown" -> {
                                if (activeConfigPanel == "DOMAINS") {
                                    selectedDomainIdx = (selectedDomainIdx + 1) % availableDomains.size
                                    val topH = ((height - 7) * 0.62).toInt().coerceAtLeast(10)
                                    val visibleItems = (topH - 4).coerceAtLeast(1)
                                    if (selectedDomainIdx >= domainScrollOffset + visibleItems) {
                                        domainScrollOffset = selectedDomainIdx - visibleItems + 1
                                    }
                                } else {
                                    selectedSettingIdx = (selectedSettingIdx + 1) % settingItems.size
                                }
                                true
                            }
                            key == "enter" || key == " " -> {
                                if (activeConfigPanel == "DOMAINS") {
                                    if (selectedDomainIdx in availableDomains.indices) {
                                        toggleDomain(availableDomains[selectedDomainIdx].first)
                                    }
                                } else {
                                    if (selectedSettingIdx in settingItems.indices) {
                                        editingValue = settingItems[selectedSettingIdx].getValue()
                                        isEditingSetting = true
                                    }
                                }
                                true
                            }
                            key == "a" -> {
                                if (activeConfigPanel == "DOMAINS") {
                                    config.dataset.selectedDomains = emptyList()
                                    settingsVersion++
                                    true
                                } else {
                                    false
                                }
                            }
                            key == "c" -> {
                                if (activeConfigPanel == "DOMAINS") {
                                    if (selectedDomainIdx in availableDomains.indices) {
                                        config.dataset.selectedDomains = listOf(availableDomains[selectedDomainIdx].first)
                                        settingsVersion++
                                    }
                                    true
                                } else {
                                    false
                                }
                            }
                            key == "r" -> {
                                startupState = StartupState.MAIN_DASHBOARD
                                focusedPanel = "TOPOLOGY"
                                triggerRegeneration {
                                    snapshotVersion++
                                }
                                true
                            }
                            key == "escape" || key == "q" -> {
                                startupState = StartupState.WELCOME
                                true
                            }
                            key == "l" || key == "arrowdown" -> {
                                logScrollOffset = 0
                                focusedPanel = "SYSTEM LOGS"
                                true
                            }
                            else -> false
                        }
                    }
                }
            } else {
                val isAnyTextInputActive = isRenamingSnapshot || isSavingSnapshot || isEditingSetting || isEnteringBatchGenerality || isEnteringArenaQuery || isEnteringArenaModelA || isEnteringArenaModelB || isEnteringTrickleQuery
                if (!isAnyTextInputActive) {
                    when (key) {
                        "e" -> {
                            if (rootNode != null) {
                                tuiScope.launch(Dispatchers.IO) {
                                    try {
                                        val ascii = buildAsciiHierarchy(rootNode!!)
                                        val exportFile = java.io.File("dag_hierarchy_ascii.txt")
                                        exportFile.writeText(ascii)
                                        log.info("Successfully exported active DAG ASCII representation to Z:\\FAC\\TUBerlin\\THESIS\\ArcTaxoAdapat\\dag_hierarchy_ascii.txt")
                                    } catch (ex: Exception) {
                                        log.error("Failed to export active DAG ASCII representation", ex)
                                    }
                                }
                                return@keyHandler true
                            }
                        }
                        "m" -> {
                            arenaService.setMode(AnalysisMode.METRICS)
                            focusedPanel = "ANALYSIS HUB"
                            return@keyHandler true
                        }
                        "a" -> {
                            if (rootNode != null) {
                                isEnteringArenaQuery = true
                                arenaQueryInput = ""
                                arenaModelAInput = "qwen3.5:2b"
                                arenaModelBInput = "ministral-3:14b"
                                arenaService.setMode(AnalysisMode.ARENA)
                                focusedPanel = "ANALYSIS HUB"
                                return@keyHandler true
                            }
                        }
                        "t" -> {
                            if (rootNode != null) {
                                isEnteringTrickleQuery = false
                                trickleQueryInput = ""
                                trickleResultNodes = emptyList()
                                isViewingBatchTrickleResults = false
                                arenaService.setMode(AnalysisMode.TRICKLE_TEST)
                                focusedPanel = "ANALYSIS HUB"
                                return@keyHandler true
                            }
                        }
                        "l" -> {
                            logScrollOffset = 0
                            focusedPanel = "SYSTEM LOGS"
                            return@keyHandler true
                        }
                        "x" -> {
                            startupState = StartupState.WELCOME
                            selectedWelcomeIdx = 0
                            return@keyHandler true
                        }
                        "v" -> {
                            showAsciiTree = !showAsciiTree
                            if (showAsciiTree) {
                                if (selectedIdx in allNodes.indices) {
                                    val treeIdx = treeLines.indexOfFirst { it.node.id == allNodes[selectedIdx].id }
                                    if (treeIdx != -1) {
                                        selectedTreeIdx = treeIdx
                                        if (selectedTreeIdx < treeScrollOffset) treeScrollOffset = selectedTreeIdx
                                    }
                                }
                            } else {
                                if (selectedTreeIdx in treeLines.indices) {
                                    val listIdx = allNodes.indexOfFirst { it.id == treeLines[selectedTreeIdx].node.id }
                                    if (listIdx != -1) {
                                        selectedIdx = listIdx
                                        if (selectedIdx < scrollOffset) scrollOffset = selectedIdx
                                    }
                                }
                            }
                            return@keyHandler true
                        }
                        "r" -> {
                            val activeNode = if (showAsciiTree) {
                                if (selectedTreeIdx in treeLines.indices) treeLines[selectedTreeIdx].node else null
                            } else {
                                if (selectedIdx in allNodes.indices) allNodes[selectedIdx] else null
                            }
                            if (activeNode != null && rootNode != null) {
                                tuiScope.launch {
                                    judgeService.generateJudgeForNodeById(rootNode!!, activeNode.id)
                                    autoSaveActiveGraph(rootNode!!)
                                    settingsVersion++
                                }
                                return@keyHandler true
                            }
                        }
                        "g", "f" -> {
                            if (rootNode != null) {
                                isEnteringBatchGenerality = true
                                batchGeneralityInput = "1"
                                batchReplaceExisting = (key == "f")
                                arenaService.setMode(AnalysisMode.JUDGE_PROGRESS)
                                focusedPanel = "ANALYSIS HUB"
                                return@keyHandler true
                            }
                        }
                        "n" -> {
                            if (isViewingSnapshot && activeSnapshotId != null) {
                                isRenamingSnapshot = true
                                renameInput = activeSnapshotDescription ?: ""
                                arenaService.setMode(AnalysisMode.SNAPSHOTS)
                                focusedPanel = "ANALYSIS HUB"
                                return@keyHandler true
                            }
                        }
                    }
                }

                // Tab key panel cycling
                if (key == "tab" || key == "\t") {
                    focusedPanel = when (focusedPanel) {
                        "TOPOLOGY" -> "ANALYSIS HUB"
                        "ANALYSIS HUB" -> "SYSTEM LOGS"
                        else -> "TOPOLOGY"
                    }
                    if (focusedPanel == "ANALYSIS HUB" && (mode == AnalysisMode.IDLE || mode == AnalysisMode.LOGS_SCROLL)) {
                        arenaService.setMode(AnalysisMode.SETTINGS)
                    }
                    true
                } else {
                    when (focusedPanel) {
                        "TOPOLOGY" -> {
                            val topH = ((height - 7) * 0.62).toInt().coerceAtLeast(10)
                            val visibleItems = (topH - 4).coerceAtLeast(1)
                            if (showDomainSelector) {
                                val maxScroll = maxOf(0, availableDomains.size - visibleItems)
                                when {
                                    key == "z" || key == "w" || key == "arrowup" -> {
                                        selectedDomainIdx = maxOf(0, selectedDomainIdx - 1)
                                        if (selectedDomainIdx < domainScrollOffset) domainScrollOffset = selectedDomainIdx
                                        true
                                    }
                                    key == "s" || key == "arrowdown" -> {
                                        selectedDomainIdx = minOf(availableDomains.size - 1, selectedDomainIdx + 1)
                                        if (selectedDomainIdx >= domainScrollOffset + visibleItems) {
                                            domainScrollOffset = selectedDomainIdx - visibleItems + 1
                                        }
                                        true
                                    }
                                    key == "enter" || key == " " -> {
                                        if (selectedDomainIdx in availableDomains.indices) {
                                            toggleDomain(availableDomains[selectedDomainIdx].first)
                                        }
                                        true
                                    }
                                    key == "d" || key == "escape" || key == "q" -> {
                                        showDomainSelector = false
                                        true
                                    }
                                    key == "r" -> {
                                        showDomainSelector = false
                                        triggerRegeneration()
                                        true
                                    }
                                    else -> false
                                }
                            } else {
                                if (showAsciiTree) {
                                    when {
                                        key == "z" || key == "w" || key == "arrowup" -> {
                                            if (treeLines.isNotEmpty()) {
                                                selectedTreeIdx = (selectedTreeIdx - 1 + treeLines.size) % treeLines.size
                                                if (selectedTreeIdx < treeScrollOffset) {
                                                    treeScrollOffset = selectedTreeIdx
                                                } else if (selectedTreeIdx >= treeScrollOffset + visibleItems) {
                                                    treeScrollOffset = maxOf(0, selectedTreeIdx - visibleItems + 1)
                                                }
                                                arenaService.inspectNode(treeLines[selectedTreeIdx].node)
                                            }
                                            autoScroll = false; true
                                        }
                                        key == "s" || key == "arrowdown" -> {
                                            if (treeLines.isNotEmpty()) {
                                                selectedTreeIdx = (selectedTreeIdx + 1) % treeLines.size
                                                if (selectedTreeIdx < treeScrollOffset) {
                                                    treeScrollOffset = selectedTreeIdx
                                                } else if (selectedTreeIdx >= treeScrollOffset + visibleItems) {
                                                    treeScrollOffset = selectedTreeIdx - visibleItems + 1
                                                }
                                                arenaService.inspectNode(treeLines[selectedTreeIdx].node)
                                            }
                                            autoScroll = false; true
                                        }
                                        key == "arrowleft" -> {
                                            if (selectedTreeIdx in treeLines.indices) {
                                                val item = treeLines[selectedTreeIdx]
                                                if (item.node.children.isNotEmpty() && expandedNodes[item.node.id] == true) {
                                                    expandedNodes[item.node.id] = false
                                                } else {
                                                    val parent = item.node.parents.firstOrNull()
                                                    if (parent != null) {
                                                        val parentIdx = treeLines.indexOfFirst { it.node.id == parent.id }
                                                        if (parentIdx != -1) {
                                                            selectedTreeIdx = parentIdx
                                                            if (selectedTreeIdx < treeScrollOffset) treeScrollOffset = selectedTreeIdx
                                                            arenaService.inspectNode(parent)
                                                        }
                                                    }
                                                }
                                            }
                                            true
                                        }
                                        key == "arrowright" -> {
                                            if (selectedTreeIdx in treeLines.indices) {
                                                val item = treeLines[selectedTreeIdx]
                                                if (item.node.children.isNotEmpty() && expandedNodes[item.node.id] != true && !item.isPoly) {
                                                    expandedNodes[item.node.id] = true
                                                } else if (item.node.children.isNotEmpty() && expandedNodes[item.node.id] == true) {
                                                    val firstChild = item.node.children.sortedByDescending { it.queries.size }.firstOrNull()
                                                    if (firstChild != null) {
                                                        val childIdx = treeLines.indexOfFirst { it.node.id == firstChild.id }
                                                        if (childIdx != -1) {
                                                            selectedTreeIdx = childIdx
                                                            if (selectedTreeIdx >= treeScrollOffset + visibleItems) {
                                                                treeScrollOffset = selectedTreeIdx - visibleItems + 1
                                                            }
                                                            arenaService.inspectNode(firstChild)
                                                        }
                                                    }
                                                }
                                            }
                                            true
                                        }
                                        key == "enter" || key == " " -> {
                                            if (selectedTreeIdx in treeLines.indices) {
                                                val item = treeLines[selectedTreeIdx]
                                                if (item.node.children.isNotEmpty() && !item.isPoly) {
                                                    expandedNodes[item.node.id] = !(expandedNodes[item.node.id] ?: false)
                                                }
                                            }
                                            true
                                        }
                                        key == "c" -> false
                                        key == "d" -> false
                                        key == "h" -> false
                                        key == "m" -> {
                                            arenaService.setMode(AnalysisMode.METRICS)
                                            focusedPanel = "ANALYSIS HUB"
                                            true
                                        }
                                        key == "n" -> {
                                            if (isViewingSnapshot && activeSnapshotId != null) {
                                                isRenamingSnapshot = true
                                                renameInput = activeSnapshotDescription ?: ""
                                                arenaService.setMode(AnalysisMode.SNAPSHOTS)
                                                focusedPanel = "ANALYSIS HUB"
                                                true
                                            } else false
                                        }
                                        key == "l" -> {
                                            logScrollOffset = 0
                                            focusedPanel = "SYSTEM LOGS"
                                            true
                                        }
                                        key == "x" -> {
                                            startupState = StartupState.WELCOME
                                            selectedWelcomeIdx = 0
                                            true
                                        }
                                        key == "v" -> {
                                            showAsciiTree = false
                                            if (selectedTreeIdx in treeLines.indices) {
                                                val listIdx = allNodes.indexOfFirst { it.id == treeLines[selectedTreeIdx].node.id }
                                                if (listIdx != -1) {
                                                    selectedIdx = listIdx
                                                    if (selectedIdx < scrollOffset) scrollOffset = selectedIdx
                                                }
                                            }
                                            true
                                        }
                                        key == "r" -> {
                                            if (selectedTreeIdx in treeLines.indices && rootNode != null) {
                                                val node = treeLines[selectedTreeIdx].node
                                                tuiScope.launch {
                                                    judgeService.generateJudgeForNodeById(rootNode!!, node.id)
                                                    autoSaveActiveGraph(rootNode!!)
                                                    settingsVersion++
                                                }
                                            }
                                            true
                                        }
                                        key == "g" || key == "f" -> {
                                            if (rootNode != null) {
                                                isEnteringBatchGenerality = true
                                                batchGeneralityInput = "1"
                                                batchReplaceExisting = (key == "f")
                                                arenaService.setMode(AnalysisMode.JUDGE_PROGRESS)
                                                focusedPanel = "ANALYSIS HUB"
                                                true
                                            } else false
                                        }
                                        key == "a" -> {
                                            if (rootNode != null) {
                                                isEnteringArenaQuery = true
                                                arenaQueryInput = ""
                                                arenaModelAInput = "qwen3.5:2b"
                                                arenaModelBInput = "ministral-3:14b"
                                                arenaService.setMode(AnalysisMode.ARENA)
                                                focusedPanel = "ANALYSIS HUB"
                                                true
                                            } else false
                                        }
                                        key == "t" -> {
                                            if (rootNode != null) {
                                                isEnteringTrickleQuery = false
                                                trickleQueryInput = ""
                                                trickleResultNodes = emptyList()
                                                isViewingBatchTrickleResults = false
                                                arenaService.setMode(AnalysisMode.TRICKLE_TEST)
                                                focusedPanel = "ANALYSIS HUB"
                                                true
                                            } else false
                                        }
                                        key == "q" -> {
                                            autoScroll = true
                                            arenaService.setMode(AnalysisMode.IDLE)
                                            true
                                        }
                                        else -> false
                                    }
                                } else {
                                    when {
                                        key == "z" || key == "w" || key == "arrowup" -> {
                                            selectedIdx = maxOf(0, selectedIdx - 1)
                                            if (selectedIdx < scrollOffset) scrollOffset = selectedIdx
                                            autoScroll = false; true
                                        }
                                        key == "s" || key == "arrowdown" -> {
                                            selectedIdx = minOf(allNodes.size - 1, selectedIdx + 1)
                                            if (selectedIdx >= scrollOffset + visibleItems) {
                                                scrollOffset = selectedIdx - visibleItems + 1
                                            }
                                            autoScroll = false; true
                                        }
                                        key == "enter" || key == " " -> {
                                            if (selectedIdx in allNodes.indices) {
                                                inspectorScroll = 0
                                                arenaService.inspectNode(allNodes[selectedIdx])
                                                focusedPanel = "ANALYSIS HUB"
                                            }
                                            true
                                        }
                                        key == "c" -> false
                                        key == "d" -> false
                                        key == "h" -> false
                                        key == "m" -> {
                                            arenaService.setMode(AnalysisMode.METRICS)
                                            focusedPanel = "ANALYSIS HUB"
                                            true
                                        }
                                        key == "n" -> {
                                            if (isViewingSnapshot && activeSnapshotId != null) {
                                                isRenamingSnapshot = true
                                                renameInput = activeSnapshotDescription ?: ""
                                                arenaService.setMode(AnalysisMode.SNAPSHOTS)
                                                focusedPanel = "ANALYSIS HUB"
                                                true
                                            } else false
                                        }
                                        key == "l" -> {
                                            logScrollOffset = 0
                                            focusedPanel = "SYSTEM LOGS"
                                            true
                                        }
                                        key == "x" -> {
                                            startupState = StartupState.WELCOME
                                            selectedWelcomeIdx = 0
                                            true
                                        }
                                        key == "v" -> {
                                            showAsciiTree = true
                                            if (selectedIdx in allNodes.indices) {
                                                val treeIdx = treeLines.indexOfFirst { it.node.id == allNodes[selectedIdx].id }
                                                if (treeIdx != -1) {
                                                    selectedTreeIdx = treeIdx
                                                    if (selectedTreeIdx < treeScrollOffset) treeScrollOffset = selectedTreeIdx
                                                }
                                            }
                                            true
                                        }
                                        key == "r" -> {
                                            if (selectedIdx in allNodes.indices && rootNode != null) {
                                                val node = allNodes[selectedIdx]
                                                tuiScope.launch {
                                                    judgeService.generateJudgeForNodeById(rootNode!!, node.id)
                                                    autoSaveActiveGraph(rootNode!!)
                                                    settingsVersion++
                                                }
                                            }
                                            true
                                        }
                                        key == "g" || key == "f" -> {
                                            if (rootNode != null) {
                                                isEnteringBatchGenerality = true
                                                batchGeneralityInput = "1"
                                                batchReplaceExisting = (key == "f")
                                                arenaService.setMode(AnalysisMode.JUDGE_PROGRESS)
                                                focusedPanel = "ANALYSIS HUB"
                                                true
                                            } else false
                                        }
                                        key == "a" -> {
                                            if (rootNode != null) {
                                                isEnteringArenaQuery = true
                                                arenaQueryInput = ""
                                                arenaModelAInput = "qwen3.5:2b"
                                                arenaModelBInput = "ministral-3:14b"
                                                arenaService.setMode(AnalysisMode.ARENA)
                                                focusedPanel = "ANALYSIS HUB"
                                                true
                                            } else false
                                        }
                                        key == "t" -> {
                                            if (rootNode != null) {
                                                isEnteringTrickleQuery = false
                                                trickleQueryInput = ""
                                                trickleResultNodes = emptyList()
                                                isViewingBatchTrickleResults = false
                                                arenaService.setMode(AnalysisMode.TRICKLE_TEST)
                                                focusedPanel = "ANALYSIS HUB"
                                                true
                                            } else false
                                        }
                                        key == "q" -> {
                                            autoScroll = true
                                            arenaService.setMode(AnalysisMode.IDLE)
                                            true
                                        }
                                        else -> false
                                    }
                                }
                            }
                        }
                        "ANALYSIS HUB" -> {
                            when (mode) {
                                AnalysisMode.NODE_DETAIL -> {
                                    val topH       = ((height - 7) * 0.62).toInt().coerceAtLeast(10)
                                    val visibleH   = (topH - 3).coerceAtLeast(1)
                                    val maxScroll  = maxOf(0, inspectorLines.size - visibleH)
                                    when {
                                        key == "z" || key == "w" || key == "arrowup"   -> { inspectorScroll = (inspectorScroll - 1).coerceAtLeast(0); true }
                                        key == "s" || key == "arrowdown"               -> { inspectorScroll = (inspectorScroll + 1).coerceIn(0, maxScroll); true }
                                        key == "r" -> {
                                            val sel = controlState.selectedNode
                                            if (sel != null && rootNode != null) {
                                                tuiScope.launch {
                                                    judgeService.generateJudgeForNodeById(rootNode!!, sel.id)
                                                    autoSaveActiveGraph(rootNode!!)
                                                    settingsVersion++
                                                }
                                            }
                                            true
                                        }
                                        key == "q" || key == "escape" || key == "backspace" || key == "arrowleft" -> {
                                            focusedPanel = "TOPOLOGY"
                                            true
                                        }
                                        key == "m" -> {
                                            if (!isViewingSnapshot) {
                                                arenaService.setMode(AnalysisMode.METRICS)
                                                true
                                            } else false
                                        }
                                        else -> false
                                    }
                                }
                                AnalysisMode.SETTINGS -> {
                                    if (isEditingSetting) {
                                        when {
                                            key == "enter" -> {
                                                if (selectedSettingIdx in settingItems.indices) {
                                                    val item = settingItems[selectedSettingIdx]
                                                    val success = item.setValue(editingValue)
                                                    if (success) {
                                                        isEditingSetting = false
                                                        settingsVersion++
                                                    }
                                                }
                                                true
                                            }
                                            key == "escape" || (key == "q" && editingValue.isEmpty()) -> {
                                                isEditingSetting = false; true
                                            }
                                            key == "backspace" -> {
                                                if (editingValue.isNotEmpty()) {
                                                    editingValue = editingValue.dropLast(1)
                                                }
                                                true
                                            }
                                            rawKey.length == 1 -> {
                                                editingValue += rawKey
                                                true
                                            }
                                            else -> false
                                        }
                                    } else {
                                        when {
                                            key == "z" || key == "w" || key == "arrowup" -> {
                                                selectedSettingIdx = (selectedSettingIdx - 1 + settingItems.size) % settingItems.size
                                                true
                                            }
                                            key == "s" || key == "arrowdown" -> {
                                                selectedSettingIdx = (selectedSettingIdx + 1) % settingItems.size
                                                true
                                            }
                                            key == "enter" -> {
                                                if (selectedSettingIdx in settingItems.indices) {
                                                    editingValue = settingItems[selectedSettingIdx].getValue()
                                                    isEditingSetting = true
                                                }
                                                true
                                            }
                                            key == "r" -> {
                                                triggerRegeneration()
                                                true
                                            }
                                            key == "m" -> {
                                                arenaService.setMode(AnalysisMode.METRICS)
                                                true
                                            }
                                            key == "q" || key == "escape" || key == "backspace" || key == "arrowleft" -> {
                                                if (selectedIdx in allNodes.indices) {
                                                    arenaService.inspectNode(allNodes[selectedIdx])
                                                } else {
                                                    arenaService.setMode(AnalysisMode.IDLE)
                                                }
                                                focusedPanel = "TOPOLOGY"
                                                true
                                            }
                                            else -> false
                                        }
                                    }
                                }
                                AnalysisMode.METRICS -> {
                                    when {
                                        key == "q" || key == "escape" || key == "backspace" || key == "arrowleft" -> {
                                            if (selectedIdx in allNodes.indices) {
                                                arenaService.inspectNode(allNodes[selectedIdx])
                                            } else {
                                                arenaService.setMode(AnalysisMode.IDLE)
                                            }
                                            focusedPanel = "TOPOLOGY"
                                            true
                                        }
                                        else -> false
                                    }
                                }
                                AnalysisMode.SNAPSHOTS -> {
                                    if (isRenamingSnapshot) {
                                        when {
                                            key == "enter" -> {
                                                if (activeSnapshotId != null) {
                                                    val newDesc = if (renameInput.isBlank()) "Snapshot" else renameInput
                                                    snapshotManager.renameSnapshot(activeSnapshotId!!, newDesc)
                                                    activeSnapshotDescription = newDesc
                                                    isRenamingSnapshot = false
                                                    renameInput = ""
                                                    snapshotVersion++
                                                }
                                                true
                                            }
                                            key == "escape" || (key == "q" && renameInput.isEmpty()) -> {
                                                isRenamingSnapshot = false
                                                renameInput = ""
                                                true
                                            }
                                            key == "backspace" -> {
                                                if (renameInput.isNotEmpty()) {
                                                    renameInput = renameInput.dropLast(1)
                                                }
                                                true
                                            }
                                            rawKey.length == 1 -> {
                                                renameInput += rawKey
                                                true
                                            }
                                            else -> false
                                        }
                                    } else if (isSavingSnapshot) {
                                        when {
                                            key == "enter" -> {
                                                if (rootNode != null) {
                                                    val desc = if (snapshotDescInput.isBlank()) "Snapshot" else snapshotDescInput
                                                    snapshotManager.saveSnapshot(rootNode!!, desc)
                                                    isSavingSnapshot = false
                                                    snapshotDescInput = ""
                                                    snapshotVersion++
                                                    selectedSnapshotIdx = 0
                                                }
                                                true
                                            }
                                            key == "escape" || (key == "q" && snapshotDescInput.isEmpty()) -> {
                                                isSavingSnapshot = false
                                                snapshotDescInput = ""
                                                true
                                            }
                                            key == "backspace" -> {
                                                if (snapshotDescInput.isNotEmpty()) {
                                                    snapshotDescInput = snapshotDescInput.dropLast(1)
                                                }
                                                true
                                            }
                                            rawKey.length == 1 -> {
                                                snapshotDescInput += rawKey
                                                true
                                            }
                                            else -> false
                                        }
                                    } else {
                                        when {
                                            key == "z" || key == "w" || key == "arrowup" -> {
                                                if (snapshotList.isNotEmpty()) {
                                                    selectedSnapshotIdx = (selectedSnapshotIdx - 1 + snapshotList.size) % snapshotList.size
                                                }
                                                true
                                            }
                                            key == "s" || key == "arrowdown" -> {
                                                if (snapshotList.isNotEmpty()) {
                                                    selectedSnapshotIdx = (selectedSnapshotIdx + 1) % snapshotList.size
                                                }
                                                true
                                            }
                                            key == "l" -> {
                                                if (snapshotList.isNotEmpty() && selectedSnapshotIdx in snapshotList.indices) {
                                                    val snap = snapshotList[selectedSnapshotIdx]
                                                    val loadedRoot = snapshotManager.loadSnapshot(snap.id)
                                                    if (loadedRoot != null) {
                                                        isViewingSnapshot = true
                                                        activeSnapshotId = snap.id
                                                        activeSnapshotDescription = snap.description
                                                        taxonomyService.setGraph(loadedRoot)
                                                        config.dataset.selectedDomains = snap.settings.selectedDomains
                                                        config.formalism.enableMrl = snap.settings.enableMrl
                                                        config.formalism.enableLiveLabeling = snap.settings.enableLiveLabeling
                                                        config.formalism.fixedMrlDimension = snap.settings.fixedMrlDimension
                                                        config.formalism.tauFit = snap.settings.tauFit
                                                        config.formalism.tauReparent = snap.settings.tauReparent
                                                        config.formalism.tauMerge = snap.settings.tauMerge
                                                        config.formalism.maxDepth = snap.settings.maxDepth
                                                        config.formalism.collapseMarginalRatio = snap.settings.collapseMarginalRatio
                                                        settingsVersion++
                                                        log.info("Successfully loaded snapshot '${snap.description}' as the active DAG!")
                                                    } else {
                                                        log.error("Failed to load snapshot '${snap.description}'")
                                                    }
                                                }
                                                true
                                            }
                                            key == "d" -> {
                                                if (snapshotList.isNotEmpty() && selectedSnapshotIdx in snapshotList.indices) {
                                                    val snap = snapshotList[selectedSnapshotIdx]
                                                    snapshotManager.deleteSnapshot(snap.id)
                                                    if (isViewingSnapshot && activeSnapshotId == snap.id) {
                                                        isViewingSnapshot = false
                                                        activeSnapshotId = null
                                                        activeSnapshotDescription = null
                                                    }
                                                    snapshotVersion++
                                                    if (snapshotList.size > 1) {
                                                        selectedSnapshotIdx = selectedSnapshotIdx.coerceAtMost(snapshotList.size - 2)
                                                    } else {
                                                        selectedSnapshotIdx = 0
                                                    }
                                                    log.info("Deleted snapshot '${snap.description}'")
                                                }
                                                true
                                            }
                                            key == "n" -> {
                                                snapshotDescInput = ""
                                                isSavingSnapshot = true
                                                true
                                            }
                                            key == "q" || key == "escape" || key == "backspace" || key == "arrowleft" -> {
                                                arenaService.setMode(AnalysisMode.IDLE)
                                                focusedPanel = "TOPOLOGY"
                                                true
                                            }
                                            else -> false
                                        }
                                    }
                                }
                                AnalysisMode.JUDGE_PROGRESS -> {
                                    if (isEnteringBatchGenerality) {
                                        when {
                                            key == "enter" -> {
                                                val n = batchGeneralityInput.toIntOrNull() ?: 1
                                                isEnteringBatchGenerality = false
                                                if (rootNode != null) {
                                                    tuiScope.launch {
                                                        judgeService.generateJudgesForDag(
                                                            rootNode!!,
                                                            replaceExisting = batchReplaceExisting,
                                                            maxGenerality = n
                                                        )
                                                        autoSaveActiveGraph(rootNode!!)
                                                        snapshotVersion++
                                                        settingsVersion++
                                                    }
                                                }
                                                true
                                            }
                                            key == "escape" || (key == "q" && batchGeneralityInput.isEmpty()) -> {
                                                isEnteringBatchGenerality = false
                                                arenaService.setMode(AnalysisMode.IDLE)
                                                focusedPanel = "TOPOLOGY"
                                                true
                                            }
                                            key == "backspace" -> {
                                                if (batchGeneralityInput.isNotEmpty()) {
                                                    batchGeneralityInput = batchGeneralityInput.dropLast(1)
                                                }
                                                true
                                            }
                                            rawKey.length == 1 && rawKey[0].isDigit() -> {
                                                batchGeneralityInput += rawKey
                                                true
                                            }
                                            else -> false
                                        }
                                    } else {
                                        when {
                                            key == "escape" || key == "q" || key == "arrowleft" -> {
                                                arenaService.setMode(AnalysisMode.IDLE)
                                                focusedPanel = "TOPOLOGY"
                                                true
                                            }
                                            else -> false
                                        }
                                    }
                                }
                                AnalysisMode.ARENA -> {
                                    if (isEnteringArenaQuery) {
                                        when {
                                            key == "enter" -> {
                                                if (arenaQueryInput.isNotBlank()) {
                                                    isEnteringArenaQuery = false
                                                    isEnteringArenaModelA = true
                                                }
                                                true
                                            }
                                            key == "escape" || (key == "q" && arenaQueryInput.isEmpty()) -> {
                                                isEnteringArenaQuery = false
                                                arenaService.setMode(AnalysisMode.IDLE)
                                                focusedPanel = "TOPOLOGY"
                                                true
                                            }
                                            key == "backspace" -> {
                                                if (arenaQueryInput.isNotEmpty()) {
                                                    arenaQueryInput = arenaQueryInput.dropLast(1)
                                                }
                                                true
                                            }
                                            rawKey.length == 1 -> {
                                                arenaQueryInput += rawKey
                                                true
                                            }
                                            else -> false
                                        }
                                    } else if (isEnteringArenaModelA) {
                                        when {
                                            key == "enter" -> {
                                                if (arenaModelAInput.isNotBlank()) {
                                                    isEnteringArenaModelA = false
                                                    isEnteringArenaModelB = true
                                                }
                                                true
                                            }
                                            key == "escape" || (key == "q" && arenaModelAInput.isEmpty()) -> {
                                                isEnteringArenaModelA = false
                                                isEnteringArenaQuery = true
                                                true
                                            }
                                            key == "backspace" -> {
                                                if (arenaModelAInput.isNotEmpty()) {
                                                    arenaModelAInput = arenaModelAInput.dropLast(1)
                                                }
                                                true
                                            }
                                            rawKey.length == 1 -> {
                                                arenaModelAInput += rawKey
                                                true
                                            }
                                            else -> false
                                        }
                                    } else if (isEnteringArenaModelB) {
                                        when {
                                            key == "enter" -> {
                                                if (arenaModelBInput.isNotBlank()) {
                                                    isEnteringArenaModelB = false
                                                    tuiScope.launch {
                                                        try {
                                                            arenaService.compareModels(arenaQueryInput, arenaModelAInput, arenaModelBInput)
                                                        } catch (e: Exception) {
                                                            log.error("Arena match failed: ${e.message}", e)
                                                        }
                                                    }
                                                }
                                                true
                                            }
                                            key == "escape" || (key == "q" && arenaModelBInput.isEmpty()) -> {
                                                isEnteringArenaModelB = false
                                                isEnteringArenaModelA = true
                                                true
                                            }
                                            key == "backspace" -> {
                                                if (arenaModelBInput.isNotEmpty()) {
                                                    arenaModelBInput = arenaModelBInput.dropLast(1)
                                                }
                                                true
                                            }
                                            rawKey.length == 1 -> {
                                                arenaModelBInput += rawKey
                                                true
                                            }
                                            else -> false
                                        }
                                    } else {
                                        when {
                                            key == "escape" || key == "q" || key == "arrowleft" -> {
                                                arenaService.setMode(AnalysisMode.IDLE)
                                                focusedPanel = "TOPOLOGY"
                                                true
                                            }
                                            else -> false
                                        }
                                    }
                                }
                                AnalysisMode.TRICKLE_TEST -> {
                                    if (isEnteringTrickleQuery) {
                                        when {
                                            key == "enter" -> {
                                                if (trickleQueryInput.isNotBlank()) {
                                                    isEnteringTrickleQuery = false
                                                    tuiScope.launch {
                                                        try {
                                                            val root = rootNode ?: return@launch
                                                            val vector = embeddingCache.getOrCreate(trickleQueryInput)
                                                            val emb = Embedding(trickleQueryInput, trickleQueryInput, vector)
                                                            val results = mutableMapOf<GraphNode, Double>()
                                                            trickleService.trickleQuery(emb, root, results)
                                                            trickleResultNodes = results.keys.sortedByDescending { it.depth }
                                                        } catch (e: Exception) {
                                                            log.error("Trickle routing test failed: ${e.message}", e)
                                                        }
                                                    }
                                                }
                                                true
                                            }
                                            key == "escape" || (key == "q" && trickleQueryInput.isEmpty()) -> {
                                                isEnteringTrickleQuery = false
                                                true
                                            }
                                            key == "backspace" -> {
                                                if (trickleQueryInput.isNotEmpty()) {
                                                    trickleQueryInput = trickleQueryInput.dropLast(1)
                                                }
                                                true
                                            }
                                            rawKey.length == 1 -> {
                                                trickleQueryInput += rawKey
                                                true
                                            }
                                            else -> false
                                        }
                                    } else {
                                        when {
                                            key == "t" -> {
                                                isEnteringTrickleQuery = true
                                                isViewingBatchTrickleResults = false
                                                true
                                            }
                                            key == "b" -> {
                                                runBatchTrickleTest()
                                                true
                                            }
                                            key == "z" || key == "w" || key == "arrowup" -> {
                                                if (isViewingBatchTrickleResults && batchTrickleResults != null) {
                                                    batchTrickleScrollOffset = (batchTrickleScrollOffset - 1).coerceAtLeast(0)
                                                }
                                                true
                                            }
                                            key == "s" || key == "arrowdown" -> {
                                                if (isViewingBatchTrickleResults && batchTrickleResults != null) {
                                                    val maxScroll = maxOf(0, batchTrickleResults!!.domainMetrics.size - 8)
                                                    batchTrickleScrollOffset = (batchTrickleScrollOffset + 1).coerceIn(0, maxScroll)
                                                }
                                                true
                                            }
                                            key == "escape" || key == "q" || key == "arrowleft" -> {
                                                arenaService.setMode(AnalysisMode.IDLE)
                                                focusedPanel = "TOPOLOGY"
                                                true
                                            }
                                            else -> false
                                        }
                                    }
                                }
                                else -> {
                                    when {
                                        key == "arrowleft" || key == "escape" || key == "q" -> {
                                            focusedPanel = "TOPOLOGY"
                                            true
                                        }
                                        key == "m" -> {
                                            arenaService.setMode(AnalysisMode.METRICS)
                                            true
                                        }
                                        else -> false
                                    }
                                }
                            }
                        }
                        "SYSTEM LOGS" -> {
                            val bottomH  = (height - 7 - ((height - 7) * 0.62).toInt().coerceAtLeast(10)).coerceAtLeast(5)
                            val visibleH = (bottomH - 2).coerceAtLeast(1)
                            val maxScroll = maxOf(0, TuiLogAppender.logs.size - visibleH)
                            when {
                                key == "z" || key == "w" || key == "arrowup" -> {
                                    logScrollOffset = (logScrollOffset + 1).coerceIn(0, maxScroll)
                                    true
                                }
                                key == "s" || key == "arrowdown" -> {
                                    logScrollOffset = (logScrollOffset - 1).coerceAtLeast(0)
                                    true
                                }
                                key == "q" || key == "escape" || key == "backspace" || key == "arrowleft" -> {
                                    logScrollOffset = 0
                                    focusedPanel = "TOPOLOGY"
                                    true
                                }
                                else -> false
                            }
                        }
                        else -> false
                    }
                }
            }
        }

        val handleMouseClick = { event: MouseEvent ->
            val clickX = event.x - 1
            val clickY = event.y - 1
            val type = event.type
            val button = event.button

            val topH = ((height - 7) * 0.62).toInt().coerceAtLeast(10)
            val bottomH = (height - 7 - topH).coerceAtLeast(5)
            val logsW = (width * 0.60).toInt()

            val topRowStart = 3
            val topRowEnd = topRowStart + topH - 1
            val bottomRowStart = topRowEnd + 2
            val bottomRowEnd = bottomRowStart + bottomH - 1

            if (startupState == StartupState.WELCOME) {
                if (type == MouseEvent.Type.Press) {
                    val itemStartY = topRowStart + 2
                    val relativeY = clickY - itemStartY
                    if (relativeY == 0) {
                        selectedWelcomeIdx = 0
                        isViewingSnapshot = false
                        startupState = StartupState.CONFIG_AND_DOMAINS
                        activeConfigPanel = "DOMAINS"
                        selectedDomainIdx = 0
                        selectedSettingIdx = 0
                    } else if (relativeY >= 2) {
                        val snapIdx = relativeY - 2
                        if (snapIdx in snapshotList.indices) {
                            selectedWelcomeIdx = snapIdx + 1
                            val snap = snapshotList[snapIdx]
                            val loadedRoot = snapshotManager.loadSnapshot(snap.id)
                            if (loadedRoot != null) {
                                isViewingSnapshot = true
                                taxonomyService.setGraph(loadedRoot)
                                config.dataset.selectedDomains = snap.settings.selectedDomains
                                config.formalism.enableMrl = snap.settings.enableMrl
                                config.formalism.enableLiveLabeling = snap.settings.enableLiveLabeling
                                config.formalism.fixedMrlDimension = snap.settings.fixedMrlDimension
                                config.formalism.tauFit = snap.settings.tauFit
                                config.formalism.tauReparent = snap.settings.tauReparent
                                config.formalism.tauMerge = snap.settings.tauMerge
                                config.formalism.maxDepth = snap.settings.maxDepth
                                config.formalism.collapseMarginalRatio = snap.settings.collapseMarginalRatio
                                settingsVersion++

                                taxonomyService.clearMetricsHistory()
                                val report = TaxonomyMetrics(loadedRoot).generateReport()
                                taxonomyService.addIterationMetrics("Loaded Snapshot", report)
                                
                                startupState = StartupState.MAIN_DASHBOARD
                                focusedPanel = "TOPOLOGY"
                            }
                        }
                    }
                }
            } else if (startupState == StartupState.CONFIG_AND_DOMAINS) {
                val leftW = (width * 0.35).toInt().coerceAtLeast(20)
                if (button == MouseEvent.Button.WheelUp || button == MouseEvent.Button.WheelDown) {
                    val isUp = button == MouseEvent.Button.WheelUp
                    if (clickY in topRowStart..topRowEnd) {
                        if (clickX in 0 until leftW) {
                            activeConfigPanel = "DOMAINS"
                            val visibleItems = (topH - 4).coerceAtLeast(1)
                            val maxScroll = maxOf(0, availableDomains.size - visibleItems)
                            domainScrollOffset = if (isUp) (domainScrollOffset - 1).coerceAtLeast(0)
                                                 else (domainScrollOffset + 1).coerceIn(0, maxScroll)
                        } else {
                            activeConfigPanel = "SETTINGS"
                            selectedSettingIdx = if (isUp) (selectedSettingIdx - 1 + settingItems.size) % settingItems.size
                                                 else (selectedSettingIdx + 1) % settingItems.size
                        }
                    } else if (clickY in bottomRowStart..bottomRowEnd) {
                        if (clickX in 0 until logsW) {
                            focusedPanel = "SYSTEM LOGS"
                            val visibleH = (bottomH - 2).coerceAtLeast(1)
                            val maxScroll = maxOf(0, TuiLogAppender.logs.size - visibleH)
                            logScrollOffset = if (isUp) (logScrollOffset + 1).coerceIn(0, maxScroll)
                                              else (logScrollOffset - 1).coerceAtLeast(0)
                        }
                    }
                } else if (type == MouseEvent.Type.Press) {
                    if (clickY in topRowStart..topRowEnd) {
                        if (clickX in 0 until leftW) {
                            activeConfigPanel = "DOMAINS"
                            val visibleItems = (topH - 4).coerceAtLeast(1)
                            val headerOffset = 4
                            val itemStartY = topRowStart + headerOffset
                            val relativeY = clickY - itemStartY
                            if (relativeY in 0 until visibleItems) {
                                val clickedIdx = domainScrollOffset + relativeY
                                if (clickedIdx in availableDomains.indices) {
                                    selectedDomainIdx = clickedIdx
                                    toggleDomain(availableDomains[clickedIdx].first)
                                }
                            }
                        } else {
                            activeConfigPanel = "SETTINGS"
                            val headerOffset = 4
                            val itemStartY = topRowStart + headerOffset
                            val relativeY = clickY - itemStartY
                            if (relativeY in settingItems.indices) {
                                selectedSettingIdx = relativeY
                                editingValue = settingItems[relativeY].getValue()
                                isEditingSetting = true
                            }
                        }
                    } else if (clickY in bottomRowStart..bottomRowEnd) {
                        if (clickX in 0 until logsW) {
                            focusedPanel = "SYSTEM LOGS"
                        }
                    }
                }
            } else {
                if (button == MouseEvent.Button.WheelUp || button == MouseEvent.Button.WheelDown) {
                    val isUp = button == MouseEvent.Button.WheelUp
                    if (clickY in topRowStart..topRowEnd) {
                        if (clickX in 0..59) {
                            focusedPanel = "TOPOLOGY"
                            val visibleItems = (topH - 4).coerceAtLeast(1)
                            if (showDomainSelector) {
                                val maxScroll = maxOf(0, availableDomains.size - visibleItems)
                                domainScrollOffset = if (isUp) (domainScrollOffset - 1).coerceAtLeast(0)
                                                     else (domainScrollOffset + 1).coerceIn(0, maxScroll)
                            } else {
                                if (showAsciiTree) {
                                    val maxScroll = maxOf(0, treeLines.size - visibleItems)
                                    treeScrollOffset = if (isUp) (treeScrollOffset - 1).coerceAtLeast(0)
                                                       else (treeScrollOffset + 1).coerceIn(0, maxScroll)
                                } else {
                                    val maxScroll = maxOf(0, allNodes.size - visibleItems)
                                    scrollOffset = if (isUp) (scrollOffset - 1).coerceAtLeast(0)
                                                   else (scrollOffset + 1).coerceIn(0, maxScroll)
                                    autoScroll = false
                                }
                            }
                        } else if (clickX in 61 until width) {
                            focusedPanel = "ANALYSIS HUB"
                            if (mode == AnalysisMode.IDLE || mode == AnalysisMode.LOGS_SCROLL) {
                                arenaService.setMode(AnalysisMode.SETTINGS)
                            }
                            if (mode == AnalysisMode.NODE_DETAIL) {
                                val visibleH = (topH - 3).coerceAtLeast(1)
                                val maxScroll = maxOf(0, inspectorLines.size - visibleH)
                                inspectorScroll = if (isUp) (inspectorScroll - 1).coerceAtLeast(0)
                                                  else (inspectorScroll + 1).coerceIn(0, maxScroll)
                            } else if (mode == AnalysisMode.SETTINGS) {
                                selectedSettingIdx = if (isUp) (selectedSettingIdx - 1 + settingItems.size) % settingItems.size
                                                     else (selectedSettingIdx + 1) % settingItems.size
                            }
                        }
                    } else if (clickY in bottomRowStart..bottomRowEnd) {
                        if (clickX in 0 until logsW) {
                            focusedPanel = "SYSTEM LOGS"
                            val visibleH = (bottomH - 2).coerceAtLeast(1)
                            val maxScroll = maxOf(0, TuiLogAppender.logs.size - visibleH)
                            logScrollOffset = if (isUp) (logScrollOffset + 1).coerceIn(0, maxScroll)
                                              else (logScrollOffset - 1).coerceAtLeast(0)
                        }
                    }
                } else if (type == MouseEvent.Type.Press) {
                    if (clickY in topRowStart..topRowEnd) {
                        if (clickX in 0..59) {
                            focusedPanel = "TOPOLOGY"

                            val visibleItems = (topH - 4).coerceAtLeast(1)
                            val headerOffset = 4
                            val itemStartY = topRowStart + headerOffset
                            val relativeY = clickY - itemStartY
                            if (showDomainSelector) {
                                val startIdx = domainScrollOffset.coerceIn(0, maxOf(0, availableDomains.size - visibleItems))
                                if (relativeY in 0 until visibleItems) {
                                    val clickedIdx = startIdx + relativeY
                                    if (clickedIdx in availableDomains.indices) {
                                        selectedDomainIdx = clickedIdx
                                        toggleDomain(availableDomains[clickedIdx].first)
                                    }
                                }
                            } else {
                                if (showAsciiTree) {
                                    val startIdx = treeScrollOffset.coerceIn(0, maxOf(0, treeLines.size - visibleItems))
                                    if (relativeY in 0 until visibleItems) {
                                        val clickedIdx = startIdx + relativeY
                                        if (clickedIdx in treeLines.indices) {
                                            if (selectedTreeIdx == clickedIdx) {
                                                val item = treeLines[clickedIdx]
                                                if (item.node.children.isNotEmpty() && !item.isPoly) {
                                                    expandedNodes[item.node.id] = !(expandedNodes[item.node.id] ?: false)
                                                }
                                            } else {
                                                selectedTreeIdx = clickedIdx
                                                inspectorScroll = 0
                                                arenaService.inspectNode(treeLines[clickedIdx].node)
                                            }
                                        }
                                    }
                                } else {
                                    val startIdx = scrollOffset.coerceIn(0, maxOf(0, allNodes.size - visibleItems))
                                    if (relativeY in 0 until visibleItems) {
                                        val clickedIdx = startIdx + relativeY
                                        if (clickedIdx in allNodes.indices) {
                                            selectedIdx = clickedIdx
                                            inspectorScroll = 0
                                            arenaService.inspectNode(allNodes[clickedIdx])
                                        }
                                    }
                                }
                            }
                        } else if (clickX in 61 until width) {
                            focusedPanel = "ANALYSIS HUB"
                            if (clickY == topRowStart || clickY == topRowStart + 1) {
                                isEditingSetting = false
                                arenaService.setMode(AnalysisMode.SETTINGS)
                            } else {
                                if (mode == AnalysisMode.IDLE || mode == AnalysisMode.NODE_DETAIL || mode == AnalysisMode.LOGS_SCROLL) {
                                    val currentSelectedNode = if (showAsciiTree) {
                                        if (selectedTreeIdx in treeLines.indices) treeLines[selectedTreeIdx].node else null
                                    } else {
                                        if (selectedIdx in allNodes.indices) allNodes[selectedIdx] else null
                                    }
                                    if (currentSelectedNode != null) {
                                        inspectorScroll = 0
                                        arenaService.inspectNode(currentSelectedNode)
                                    } else {
                                        arenaService.setMode(AnalysisMode.SETTINGS)
                                    }
                                } else if (mode == AnalysisMode.SETTINGS) {
                                    val headerOffset = 4
                                    val itemStartY = topRowStart + headerOffset
                                    val relativeY = clickY - itemStartY
                                    if (relativeY in settingItems.indices) {
                                        selectedSettingIdx = relativeY
                                        editingValue = settingItems[relativeY].getValue()
                                        isEditingSetting = true
                                    }
                                }
                            }
                        }
                    } else if (clickY in bottomRowStart..bottomRowEnd) {
                        if (clickX in 0 until logsW) {
                            focusedPanel = "SYSTEM LOGS"
                        }
                    }
                }
            }
        }

        val currentHandleKeyPress by rememberUpdatedState(handleKeyPress)
        val currentHandleMouseClick by rememberUpdatedState(handleMouseClick)

        // Mouse & Keyboard Event Handling Loop (Unicast single subscription)
        LaunchedEffect(terminal) {
            var lastKeyPressTime = 0L
            for (event in terminal.events) {
                if (event is ResizeEvent) {
                    width = event.columns
                    height = event.rows
                } else if (event is MouseEvent) {
                    currentHandleMouseClick(event)
                } else if (event is KeyboardEvent) {
                    if (event.eventType == KeyboardEvent.EventTypeRelease) continue
                    val isCtrlC = (event.ctrl && (event.codepoint == 'c'.code || event.codepoint == 'C'.code || event.codepoint == 3)) || (event.codepoint == 3)
                    if (isCtrlC) {
                        print("\u001b[?1049l")
                        AnsiConsole.systemUninstall()
                        System.exit(0)
                    }

                    val now = System.currentTimeMillis()
                    val isFast = (now - lastKeyPressTime) < 15
                    lastKeyPressTime = now

                    val rawKey = when (event.codepoint) {
                        KeyboardEvent.Up -> "arrowup"
                        KeyboardEvent.Down -> "arrowdown"
                        KeyboardEvent.Left -> "arrowleft"
                        KeyboardEvent.Right -> "arrowright"
                        13, 10 -> if (isFast) " " else "enter"
                        27 -> "escape"
                        8, 127 -> "backspace"
                        9 -> "tab"
                        32 -> " "
                        else -> {
                            if (event.codepoint >= 32 && event.codepoint != 127 && !Character.isISOControl(event.codepoint)) {
                                try {
                                    String(Character.toChars(event.codepoint))
                                } catch (e: java.lang.Exception) {
                                    ""
                                }
                            } else {
                                ""
                            }
                        }
                    }
                    if (rawKey.isNotEmpty()) {
                        currentHandleKeyPress(rawKey.lowercase(), rawKey)
                    }
                }
            }
        }

        Column(
            modifier = Modifier.width(width).height(height - 2).onKeyEvent { event ->
                val rawKey = event.key
                val key = rawKey.lowercase()
                currentHandleKeyPress(key, rawKey)
            }
        ) {
            if (startupState == StartupState.WELCOME) {
                Header(width, rootNode, time, allNodes)
                HRule(width, Cyan, White, White)
                val contentH = height - 7
                Panel(" ◈ SETUP HUB: ARCHIVE SELECTOR & DAG INITIALIZER ◈ ", Cyan, width - 2, contentH) {
                    val leftW = ((width - 4) * 0.45).toInt().coerceAtLeast(30)
                    val rightW = (width - 4) - leftW - 1
                    Column {
                        Row(modifier = Modifier.width(width - 4).height(contentH - 4)) {
                            // Left Column
                            Column(modifier = Modifier.width(leftW).padding(left = 1, top = 1)) {
                                "Select an option to initialize the taxonomic DAG:"
                                    .chunked(leftW - 2).forEach { Text(it, color = White, textStyle = Bold) }
                                Spacer(Modifier.height(1))
                                
                                val isGenSelected = selectedWelcomeIdx == 0
                                val genPrefix = if (isGenSelected) "▶ " else "  "
                                val genColor = if (isGenSelected) Cyan else White
                                if (isGenSelected) {
                                    Text("$genPrefix[ Generate a New DAG ]", color = genColor, textStyle = Bold)
                                } else {
                                    Text("$genPrefix[ Generate a New DAG ]", color = genColor)
                                }
                                
                                Spacer(Modifier.height(1))
                                Text(" ─── OR select a saved snapshot: ───".take(leftW - 2), color = Yellow, textStyle = Bold)
                                Spacer(Modifier.height(1))
                                
                                if (snapshotList.isEmpty()) {
                                    Text("  (No saved snapshots found)", color = White)
                                } else {
                                    val visibleSnapshots = (contentH - 11).coerceAtLeast(1)
                                    snapshotList.take(visibleSnapshots).forEachIndexed { index, snap ->
                                        val snapIdx = index + 1
                                        val isSnapSelected = selectedWelcomeIdx == snapIdx
                                        val prefix = if (isSnapSelected) "▶ " else "  "
                                        val color = if (isSnapSelected) Cyan else White
                                        
                                        val numNodes = snap.graph.nodes.size
                                        val numJudges = snap.graph.nodes.count { !it.judgePrompt.isNullOrEmpty() }
                                        val countsStr = " (N:$numNodes/J:$numJudges)"
                                        val timeStr = snap.timestamp.take(16)
                                        
                                        val reservedLength = prefix.length + timeStr.length + 3 + countsStr.length
                                        val maxDescLen = (leftW - reservedLength - 2).coerceAtLeast(10)
                                        val desc = if (snap.description.length > maxDescLen) {
                                            snap.description.take(maxDescLen - 3) + "..."
                                        } else {
                                            snap.description.padEnd(maxDescLen)
                                        }
                                        val line = "$prefix$timeStr │ $desc$countsStr"
                                        if (isSnapSelected) {
                                            Text(line.take(leftW - 2), color = color, textStyle = Bold)
                                        } else {
                                            Text(line.take(leftW - 2), color = color)
                                        }
                                    }
                                    if (snapshotList.size > visibleSnapshots) {
                                        Text("  ... and ${snapshotList.size - visibleSnapshots} more snapshots ...", color = Yellow)
                                    }
                                }
                            }
                            
                            VDivider(contentH - 4, White, Cyan)
                            
                            // Right Column
                            Column(modifier = Modifier.width(rightW).padding(left = 2, top = 1)) {
                                if (selectedWelcomeIdx == 0) {
                                    Text(" ◈ OPTION: GENERATE NEW DAG ◈", color = Cyan, textStyle = Bold)
                                    Spacer(Modifier.height(1))
                                    "Create a fresh hierarchical taxonomy from raw MMLU-Pro dataset queries."
                                        .chunked(rightW - 4).forEach { Text(it, color = White) }
                                    "Enables custom domain filtering and hyperparameter tuning."
                                        .chunked(rightW - 4).forEach { Text(it, color = White) }
                                } else if (selectedWelcomeIdx - 1 in snapshotList.indices) {
                                    val snap = snapshotList[selectedWelcomeIdx - 1]
                                    Text(" ◈ SNAPSHOT DETAILS ◈", color = Cyan, textStyle = Bold)
                                    Spacer(Modifier.height(1))
                                    val maxDescLength = rightW - 4
                                    val snapDesc = if (snap.description.length > maxDescLength) snap.description.take(maxDescLength - 3) + "..." else snap.description
                                    Text("Desc: $snapDesc", color = White, textStyle = Bold)
                                    Text("Time: ${snap.timestamp}", color = White)
                                    Spacer(Modifier.height(1))
                                    Text(" [Metadata Metrics]:", color = Yellow, textStyle = Bold)
                                    Text("  • Total Nodes: ${snap.metrics.totalNodes} (Leaves: ${snap.metrics.leafNodes})", color = White)
                                    Text("  • Max Depth: ${snap.metrics.maxDepth}", color = White)
                                    Text("  • Total Queries: ${snap.metrics.totalUniqueQueries}", color = White)
                                    Text("  • Path Redundancy: %.2f".format(java.util.Locale.US, snap.metrics.totalPathRedundancy), color = White)
                                    Spacer(Modifier.height(1))
                                    Text(" [Generation Settings]:", color = Yellow, textStyle = Bold)
                                    Text("  • MRL Enabled: ${snap.settings.enableMrl} (Dim: ${snap.settings.fixedMrlDimension}) │ Live Labeling: ${snap.settings.enableLiveLabeling}", color = White)
                                    Text("  • Tau Fit: ${snap.settings.tauFit} │ Merge: ${snap.settings.tauMerge}", color = White)
                                    val doms = snap.settings.selectedDomains
                                    Text("  • Domains: ${if (doms.isEmpty()) "All" else doms.joinToString(", ").take(rightW - 14)}", color = White)
                                    
                                    // Judges info on Welcome Screen
                                    val welcomeNodesWithJudges = snap.graph.nodes.filter { !it.judgePrompt.isNullOrEmpty() }
                                    val welcomeTotalJudges = welcomeNodesWithJudges.size
                                    val welcomeTotalNodes = snap.graph.nodes.size
                                    val welcomePercent = if (welcomeTotalNodes > 0) (welcomeTotalJudges * 100.0 / welcomeTotalNodes) else 0.0
                                    Spacer(Modifier.height(1))
                                    Text(" [Induced Judges]:", color = Yellow, textStyle = Bold)
                                    Text("  • Coverage: $welcomeTotalJudges / $welcomeTotalNodes nodes (${"%.1f".format(java.util.Locale.US, welcomePercent)}%)", color = White)
                                    if (welcomeNodesWithJudges.isNotEmpty()) {
                                        val names = welcomeNodesWithJudges.take(3).joinToString { it.label }
                                        val suffix = if (welcomeNodesWithJudges.size > 3) ", etc." else ""
                                        val activeStr = "  • Active: $names$suffix"
                                        Text(if (activeStr.length > rightW - 2) activeStr.take(rightW - 5) + "..." else activeStr, color = White)
                                    } else {
                                        Text("  • Active: None", color = White)
                                    }
                                }
                            }
                        }
                        
                        Spacer(Modifier.height(1))
                        if (rootNode != null) {
                            Text(" [↑/↓/w/s] Navigate  [Enter] Select  [D] Delete  [Esc/Q] Return to DAG".take(width - 4), color = Magenta)
                        } else {
                            Text(" [↑/↓/w/s] Navigate  [Enter] Select  [D] Delete Selected".take(width - 4), color = Magenta)
                        }
                    }
                }
                HRule(width, White, Cyan, White)
                Text(" Use ↑/↓ to choose, press [Enter] to select.", color = White)
            } else if (startupState == StartupState.CONFIG_AND_DOMAINS) {
                Header(width, rootNode, time, allNodes)
                HRule(width, Cyan, White, White)

                val topH    = ((height - 7) * 0.62).toInt().coerceAtLeast(10)
                val bottomH = (height - 7 - topH).coerceAtLeast(5)

                if (isRegenerating) {
                    Panel(" ◈ TAXONOMY GENERATION IN PROGRESS ◈ ", Cyan, width - 2, topH) {
                        Column(modifier = Modifier.padding(left = 2, top = 2)) {
                            Text("Running Adaptive Taxonomy Evolution in 4096-D Embedding Space...", color = White, textStyle = Bold)
                            Spacer(Modifier.height(1))
                            Text("Current Step: Fitting GMMs & stabilizing taxonomy structure", color = Yellow)
                            Spacer(Modifier.height(1))
                            Text("Please wait. Real-time details are streaming in the SYSTEM LOGS panel below.", color = Cyan)
                            Spacer(Modifier.height(2))
                            Text("  Pulsing Status: [ REGENERATING ${SPINNER[spinnerTick]} ]", color = regeneratingColor, textStyle = Bold)
                        }
                    }
                } else {
                    val leftW = (width * 0.35).toInt().coerceAtLeast(20)
                    val rightW = width - leftW - 1
                    Row(modifier = Modifier.height(topH)) {
                        val domainsTitle = if (activeConfigPanel == "DOMAINS") "▶ DOMAIN SELECTOR ◀" else "  DOMAIN SELECTOR  "
                        val domainsAccent = if (activeConfigPanel == "DOMAINS") Cyan else White
                        Panel(domainsTitle, domainsAccent, leftW, topH) {
                            DomainSelectorTable(
                                pWidth = leftW - 4,
                                pHeight = topH - 2,
                                domains = availableDomains,
                                offset = domainScrollOffset,
                                selectedIdx = selectedDomainIdx,
                                selectedDomains = config.dataset.selectedDomains
                            )
                        }
                        
                        VDivider(topH, White, Cyan)
                        
                        val settingsTitle = if (activeConfigPanel == "SETTINGS") "▶ GENERATION SETTINGS ◀" else "  GENERATION SETTINGS  "
                        val settingsAccent = if (activeConfigPanel == "SETTINGS") Cyan else White
                        Panel(settingsTitle, settingsAccent, rightW - 1, topH) {
                            SettingsHub(
                                pWidth = rightW - 5,
                                pHeight = topH - 2,
                                selectedIdx = selectedSettingIdx,
                                isEditing = isEditingSetting,
                                editingVal = editingValue,
                                items = settingItems,
                                isRegenerating = isRegenerating,
                                regeneratingColor = regeneratingColor
                            )
                        }
                    }
                }

                HRule(width, White, Cyan, White)

                val logsW  = (width * 0.60).toInt()
                val traceW = width - logsW - 1
                Row(modifier = Modifier.height(bottomH)) {
                    val logsTitle = if (focusedPanel == "SYSTEM LOGS") "▶ SYSTEM LOGS ◀" else "  SYSTEM LOGS  "
                    val logsAccent = if (focusedPanel == "SYSTEM LOGS") Cyan else White
                    Panel(logsTitle, logsAccent, logsW, bottomH) {
                        LogView(logsW - 4, bottomH - 2, logScrollOffset)
                    }
                    VDivider(bottomH, White, Cyan)
                    Panel("  GPU TRACES  ", White, traceW - 1, bottomH) {
                        InferenceStreams(traceW - 5, bottomH - 2, spinnerTick)
                    }
                }
                
                Text(buildAnnotatedString {
                    header("Setup Config: ")
                    hotkey("Tab", "Switch Panels")
                    hotkey("↑↓", "Navigate")
                    hotkey("Space/Enter", "Toggle/Edit")
                    if (activeConfigPanel == "DOMAINS") {
                        hotkey("A", "Select All")
                        hotkey("C", "Clear Others")
                    }
                    hotkey("R", "Generate DAG")
                    hotkey("Esc/Q", "Back")
                })
            } else {
                Header(width, rootNode, time, allNodes)
                HRule(width, Cyan, White, White)

                val topH    = ((height - 7) * 0.62).toInt().coerceAtLeast(10)
                val bottomH = (height - 7 - topH).coerceAtLeast(5)

                Row(modifier = Modifier.height(topH)) {
                    val topologyTitle = if (showDomainSelector) {
                        if (focusedPanel == "TOPOLOGY") "▶ MMLU DOMAINS ◀" else "  MMLU DOMAINS  "
                    } else {
                        if (focusedPanel == "TOPOLOGY") "▶ TOPOLOGY ◀" else "  TOPOLOGY  "
                    }
                    Panel(topologyTitle, topologyAccent, dagWidth, topH) {
                        if (showDomainSelector) {
                            DomainSelectorTable(
                                pWidth = dagWidth - 4,
                                pHeight = topH - 2,
                                domains = availableDomains,
                                offset = domainScrollOffset,
                                selectedIdx = selectedDomainIdx,
                                selectedDomains = config.dataset.selectedDomains
                            )
                        } else {
                            if (showAsciiTree) {
                                AsciiTreeTable(dagWidth - 4, topH - 2, treeLines, treeScrollOffset, selectedTreeIdx)
                            } else {
                                DagTable(dagWidth - 4, topH - 2, allNodes, scrollOffset, selectedIdx)
                            }
                        }
                    }
                    VDivider(topH, White, Cyan)

                    val hubTitle = if (focusedPanel == "ANALYSIS HUB") "▶ ANALYSIS HUB ◀" else "  ANALYSIS HUB  "
                    Panel(hubTitle, hubAccent, arenaWidth - 1, topH) {
                        AnalysisHub(
                            pWidth = arenaWidth - 5,
                            pHeight = topH - 2,
                            state = controlState,
                            inspectorScroll = inspectorScroll,
                            inspectorLines = inspectorLines,
                            selectedSettingIdx = selectedSettingIdx,
                            isEditingSetting = isEditingSetting,
                            editingValue = editingValue,
                            settingItems = settingItems,
                            regeneratingColor = regeneratingColor,
                            selectedSnapshotIdx = selectedSnapshotIdx,
                            isSavingSnapshot = isSavingSnapshot,
                            snapshotDescInput = snapshotDescInput,
                            snapshotList = snapshotList
                        )
                    }
                }

                HRule(width, White, Cyan, White)

                val logsW  = (width * 0.60).toInt()
                val traceW = width - logsW - 1
                Row(modifier = Modifier.height(bottomH)) {
                    val logsTitle = if (mode == AnalysisMode.LOGS_SCROLL) "▶ SYSTEM LOGS [SCROLLING] ◀" else if (focusedPanel == "SYSTEM LOGS") "▶ SYSTEM LOGS ◀" else "  SYSTEM LOGS  "
                    Panel(logsTitle, logsAccent, logsW, bottomH) {
                        LogView(logsW - 4, bottomH - 2, logScrollOffset)
                    }
                    VDivider(bottomH, White, Cyan)
                    Panel("  GPU TRACES  ", White, traceW - 1, bottomH) {
                        InferenceStreams(traceW - 5, bottomH - 2, spinnerTick)
                    }
                }

                HotkeyBar(width, mode, showDomainSelector, isSavingSnapshot, showAsciiTree, isViewingSnapshot)
            }
        }

        // ── Auto-scroll effect ───────────────────────────────────────────────────
        LaunchedEffect(autoScroll, allNodes.size) {
            if (autoScroll && allNodes.isNotEmpty()) {
                while (true) {
                    delay(4000)
                    scrollOffset = (scrollOffset + 1) % allNodes.size
                }
            }
        }
    }

    @Composable
    internal fun TaxonomyTuiService.Header(width: Int, root: GraphNode?, time: LocalTime, nodes: List<GraphNode>) {
        val ready       = root != null
        val statusColor = if (isRegenerating) Yellow else (if (ready) Green else Yellow)
        val statusText  = if (isRegenerating) "● EVOLVING..." else (if (ready) "● READY" else "◌ LOADING")
        val timeStr     = time.format(DateTimeFormatter.ofPattern("HH:mm:ss"))
        val nodeCount   = nodes.size
        val judgedCount = nodes.count { it.judgePrompt != null }
        val modelName   = (System.getenv("ARC_MODEL") ?: config.llm.labelingModel).take(20)

        // Title banner
        val title = "  ◈  A R C T A X O A D A P T  ·  Dynamic Semantic DAG Engine  ·  $TUI_VERSION  ◈"
        Text(
            title.center(width).take(width - 1),
            color = Cyan, textStyle = Bold
        )

        // Stats line
        val statsLine = buildAnnotatedString {
            append("  ")
            withStyle(SpanStyle(color = statusColor, textStyle = Bold)) { append(statusText) }
            
            if (isViewingSnapshot && activeSnapshotDescription != null) {
                withStyle(SpanStyle(color = White)) { append("  │  Snapshot: ") }
                withStyle(SpanStyle(color = Magenta, textStyle = Bold)) { 
                    append(activeSnapshotDescription!!.take(25)) 
                }
            } else {
                withStyle(SpanStyle(color = White)) { append("  │  Mode: ") }
                withStyle(SpanStyle(color = Green, textStyle = Bold)) { append("LIVE") }
            }

            withStyle(SpanStyle(color = White))    { append("  │  Nodes: ") }
            withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append("$nodeCount") }
            withStyle(SpanStyle(color = White))    { append("  │  Judged: ") }
            withStyle(SpanStyle(color = if (judgedCount == nodeCount && nodeCount > 0) Green else Yellow, textStyle = Bold)) {
                append("$judgedCount/$nodeCount")
            }
            withStyle(SpanStyle(color = White))    { append("  │  Model: ") }
            withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append(modelName) }
            withStyle(SpanStyle(color = White))    { append("  │  ") }
            withStyle(SpanStyle(color = Cyan))     { append("⏱ $timeStr") }
        }
        Text(statsLine.take(width - 1))
    }

    @Composable
    internal fun TaxonomyTuiService.AsciiTreeTable(pWidth: Int, pHeight: Int, lines: List<TreeLine>, offset: Int, selectedIdx: Int) {
        if (lines.isEmpty()) {
            Column {
                Spacer(Modifier.height(2))
                Text("  ◌ Awaiting taxonomy construction…".take(pWidth - 1), color = Yellow)
                Text("  Batch run is in progress — check System Logs".take(pWidth - 1), color = White)
            }
            return
        }

        val visible  = (pHeight - 2).coerceAtLeast(1)
        val startIdx = offset.coerceIn(0, maxOf(0, lines.size - visible))

        val items = lines.drop(startIdx).take(visible)
        val maxScroll = maxOf(0, lines.size - visible)

        val TREE_W = (pWidth - 13).coerceAtLeast(10)

        Row(modifier = Modifier.width(pWidth).height(pHeight)) {
            Column(modifier = Modifier.width(pWidth - 2)) {
                Text(buildAnnotatedString {
                    withStyle(SpanStyle(color = White, textStyle = Bold)) {
                        append("   ")
                        append("Taxonomy DAG Hierarchy".padEnd(TREE_W))
                        append("Queries")
                        append("  ✔")
                    }
                }.take(pWidth - 3))
                
                Spacer(Modifier.height(1))

                items.forEachIndexed { i, item ->
                    val absIdx   = startIdx + i
                    val isSel    = absIdx == selectedIdx
                    val node     = item.node
                    val totalQ   = node.getRecursiveQueryCount()
                    val hasJudge = node.judgePrompt != null
                    val qStr      = totalQ.toString().padStart(6)
                    val judgeGlyph = if (hasJudge) "✔" else "○"

                    val rawText = item.text
                    val truncatedText = buildAnnotatedString {
                        if (rawText.length > TREE_W) {
                            append(rawText.subSequence(0, TREE_W - 1))
                            append("…")
                        } else {
                            append(rawText)
                            append(" ".repeat(TREE_W - rawText.length))
                        }
                    }

                    val line = buildAnnotatedString {
                        if (isSel) {
                            withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
                                append(" ▶ ")
                                append(truncatedText)
                                append(" ")
                                append(qStr)
                                append("  ")
                            }
                            withStyle(SpanStyle(color = if (hasJudge) Green else Yellow, textStyle = Bold)) {
                                append(judgeGlyph)
                            }
                        } else {
                            append("   ")
                            append(truncatedText)
                            append(" ")
                            withStyle(SpanStyle(color = Cyan)) {
                                append(qStr)
                            }
                            append("  ")
                            withStyle(SpanStyle(color = if (hasJudge) Green else White, textStyle = Bold)) {
                                append(judgeGlyph)
                            }
                        }
                    }
                    Text(line.take(pWidth - 3), modifier = Modifier.height(1))
                }
                repeat(visible - items.size) { Text(" ".repeat(pWidth - 3)) }
            }

            Column(modifier = Modifier.width(2)) {
                if (maxScroll > 0) {
                    val thumbPos = ((startIdx.toDouble() / maxScroll) * (visible - 1)).toInt().coerceIn(0, visible - 1)
                    repeat(visible) { i ->
                        Text(if (i == thumbPos) " ▓" else " ░", color = if (i == thumbPos) Cyan else White)
                    }
                } else {
                    repeat(visible) { Text("  ", color = White) }
                }
            }
        }
    }

    @Composable
    internal fun TaxonomyTuiService.DagTable(pWidth: Int, pHeight: Int, nodes: List<GraphNode>, offset: Int, selectedIdx: Int) {
        if (nodes.isEmpty()) {
            Column {
                Spacer(Modifier.height(2))
                Text("  ◌ Awaiting taxonomy construction…".take(pWidth - 1), color = Yellow)
                Text("  Batch run is in progress — check System Logs".take(pWidth - 1), color = White)
            }
            return
        }

        // ── Fixed column widths using clean spaces ────────────────────────────
        // [sel:3][label:LABEL_W][spacer:2][depth:1][spacer:2][queries:6][spacer:2][judge:1]
        // Total = 3 + LABEL_W + 2 + 1 + 2 + 6 + 2 + 1 = LABEL_W + 17
        // Scrollbar takes 2 columns, so subtract 19 to get the label width
        val LABEL_W  = (pWidth - 19).coerceAtLeast(10)   // fills remaining space

        val maxQ     = nodes.maxOf { it.getRecursiveQueryCount() }.coerceAtLeast(1)
        val visible  = (pHeight - 2).coerceAtLeast(1)
        val startIdx = offset.coerceIn(0, maxOf(0, nodes.size - visible))

        val items = nodes.drop(startIdx).take(visible)
        val maxScroll = maxOf(0, nodes.size - visible)

        Row(modifier = Modifier.width(pWidth).height(pHeight)) {
            Column(modifier = Modifier.width(pWidth - 2)) {
                // ── Column header with spaces instead of │ ────────────────────────
                Text(buildAnnotatedString {
                    withStyle(SpanStyle(color = White, textStyle = Bold)) {
                        append("   ")
                        append("Label".padEnd(LABEL_W))
                        append("  D  ")
                        append("Queries")
                        append("  ✔")
                    }
                }.take(pWidth - 3))
                
                Spacer(Modifier.height(1))

                items.forEachIndexed { i, node ->
                    val absIdx   = startIdx + i
                    val isSel    = absIdx == selectedIdx
                    val depth    = node.depth
                    val totalQ   = node.getRecursiveQueryCount()
                    val hasJudge = node.judgePrompt != null
                    val nodeCol  = depthColor(depth)

                    // Label: always exactly LABEL_W chars — truncated or padded
                    val rawLabel  = node.label
                    val labelText = if (node.judgePrompt != null) "★ $rawLabel" else rawLabel
                    val label     = if (labelText.length > LABEL_W) labelText.take(LABEL_W - 1) + "…"
                                    else labelText.padEnd(LABEL_W)
                    val depthStr  = depth.toString()
                    val qStr      = totalQ.toString().padStart(6)
                    val judgeGlyph = if (hasJudge) "✔" else "○"

                    val line = buildAnnotatedString {
                        if (isSel) {
                            withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
                                append(" ▶ ")
                                append(label)
                                append("  ")
                                append(depthStr)
                                append("  ")
                                append(qStr)
                                append("  ")
                            }
                            withStyle(SpanStyle(
                                color = if (hasJudge) Green else Yellow, textStyle = Bold
                            )) { append(judgeGlyph) }
                        } else {
                            // Unselected: depth-coloured label, clean spaces
                            withStyle(SpanStyle(color = White))     { append("   ") }
                            withStyle(SpanStyle(color = nodeCol))  { append(label) }
                            append("  ")
                            withStyle(SpanStyle(color = nodeCol, textStyle = Bold)) { append(depthStr) }
                            append("  ")
                            withStyle(SpanStyle(color = Cyan))     { append(qStr) }
                            append("  ")
                            withStyle(SpanStyle(
                                color = if (hasJudge) Green else White, textStyle = Bold
                            )) { append(judgeGlyph) }
                        }
                    }
                    Text(line.take(pWidth - 3), modifier = Modifier.height(1))
                }
                repeat(visible - items.size) { Text(" ".repeat(pWidth - 3)) }
            }

            // Scrollbar column
            Column(modifier = Modifier.width(2)) {
                if (maxScroll > 0) {
                    val thumbPos = ((startIdx.toDouble() / maxScroll) * (visible - 1)).toInt().coerceIn(0, visible - 1)
                    repeat(visible) { i ->
                        Text(if (i == thumbPos) " ▓" else " ░", color = if (i == thumbPos) Cyan else White)
                    }
                } else {
                    repeat(visible) { Text("  ", color = White) }
                }
            }
        }
    }

    @Composable
    internal fun TaxonomyTuiService.LogView(pWidth: Int, pHeight: Int, scrollOffset: Int) {
        val logs = TuiLogAppender.logs
        val visible = pHeight
        val totalLogs = logs.size
        val maxOffset = maxOf(0, totalLogs - visible)
        val currentOffset = scrollOffset.coerceIn(0, maxOffset)
        val displayed = logs.drop(maxOf(0, totalLogs - visible - currentOffset)).take(visible)

        Row(modifier = Modifier.width(pWidth).height(pHeight)) {
            Column(modifier = Modifier.width(pWidth - 2)) {
                displayed.forEach { raw ->
                    val firstLine = raw.split('\n', '\r').firstOrNull() ?: ""
                    val trimmed = firstLine.trim()
                    val (prefix, color, rest) = when {
                        trimmed.contains(" ERROR ") || trimmed.startsWith("ERROR") ->
                            Triple("✖ ", Red, trimmed)
                        trimmed.contains(" WARN ")  || trimmed.startsWith("WARN") ->
                            Triple("⚠ ", Yellow, trimmed)
                        trimmed.contains(" INFO ")  || trimmed.startsWith("INFO") ->
                            Triple("ℹ ", Cyan, trimmed)
                        else ->
                            Triple("  ", White, trimmed)
                    }
                    val allowedWidth = (pWidth - 6).coerceAtLeast(0)
                    val restText = rest.take(allowedWidth)
                    val finalAnnotated = buildAnnotatedString {
                        withStyle(SpanStyle(color = color, textStyle = Bold)) { append(prefix) }
                        withStyle(SpanStyle(color = color)) { append(restText) }
                    }.take((pWidth - 3).coerceAtLeast(0))
                    Text(finalAnnotated)
                }
                repeat(visible - displayed.size) { Text(" ".repeat(pWidth - 3)) }
            }
            
            // Scrollbar column
            Column(modifier = Modifier.width(2)) {
                if (maxOffset > 0) {
                    val thumbPos = (((maxOffset - currentOffset).toDouble() / maxOffset) * (visible - 1)).toInt().coerceIn(0, visible - 1)
                    repeat(visible) { i ->
                        Text(if (i == thumbPos) " ▓" else " ░", color = if (i == thumbPos) Cyan else White)
                    }
                } else {
                    repeat(visible) { Text("  ", color = White) }
                }
            }
        }
    }

    @Composable
    internal fun TaxonomyTuiService.InferenceStreams(pWidth: Int, pHeight: Int, spinnerTick: Int) {
        val activeSlots = monitor.activeSlots.values.toList()
        Column {
            if (activeSlots.isEmpty()) {
                Spacer(Modifier.height(maxOf(0, pHeight / 2 - 1)))
                Text(
                    "  ◌  GPU idle  —  no active inference slots"
                        .center(pWidth).take(pWidth - 1),
                    color = White
                )
            } else {
                val linesPerSlot = maxOf(3, pHeight / activeSlots.size.coerceAtLeast(1))
                activeSlots.take(maxOf(1, pHeight / 4)).forEach { slot ->
                    key(slot.modelName) {
                        val slotColorState = animateColorAsState(if (slot.isComplete) Green else Yellow)
                        val slotColor = slotColorState.value
                        val spinner    = if (slot.isComplete) "✔" else SPINNER[spinnerTick]
                        val statusTag  = if (slot.isComplete) "DONE" else "BUSY"
                        Text(buildAnnotatedString {
                            withStyle(SpanStyle(color = slotColor, textStyle = Bold)) {
                                append("  $spinner [$statusTag] ")
                            }
                            withStyle(SpanStyle(color = White, textStyle = Bold)) {
                                append(slot.modelName.take(pWidth - 14))
                            }
                        }.take(pWidth - 1))
                        renderMarkdown(slot.text.takeLast(maxOf(1, pWidth * 3)), pWidth - 4)
                            .take(2)
                            .forEach { line -> Text(buildAnnotatedString {
                                withStyle(SpanStyle(color = White)) { append("    ") }
                                append(line)
                            }.take(pWidth - 1)) }
                        Spacer(Modifier.height(1))
                    }
                }
            }
        }
    }

internal fun TaxonomyTuiService.buildTreeLines(root: GraphNode?, expandedNodes: Map<String, Boolean>): List<TreeLine> {
        if (root == null) return emptyList()
        val list = mutableListOf<TreeLine>()
        val visited = mutableSetOf<String>()
        
        fun walk(node: GraphNode, depth: Int, isLastChild: List<Boolean>) {
            val nodeID = node.id
            val isAlreadyVisited = !visited.add(nodeID)
            
            val prefix = buildString {
                for (j in 0 until depth) {
                    if (j == depth - 1) {
                        if (isLastChild[j]) {
                            append("└── ")
                        } else {
                            append("├── ")
                        }
                    } else {
                        if (isLastChild[j]) {
                            append("    ")
                        } else {
                            append("│   ")
                        }
                    }
                }
            }
            
            val nodeCol = depthColor(node.depth)
            val annot = buildAnnotatedString {
                withStyle(SpanStyle(color = White)) {
                    append(prefix)
                }
                if (node.judgePrompt != null) {
                    withStyle(SpanStyle(color = Green, textStyle = Bold)) {
                        append("★ ")
                    }
                }
                if (isAlreadyVisited) {
                    withStyle(SpanStyle(color = nodeCol, textStyle = Bold)) {
                        append(node.label)
                    }
                    withStyle(SpanStyle(color = Yellow, textStyle = Bold)) {
                        append(" ⇄ (Poly)")
                    }
                } else {
                    withStyle(SpanStyle(color = nodeCol)) {
                        append(node.label)
                    }
                }
            }
            
            list.add(TreeLine(node, annot, isAlreadyVisited))
            
            if (isAlreadyVisited) return
            
            val isExpanded = expandedNodes[nodeID] ?: false
            if (isExpanded && node.children.isNotEmpty()) {
                val sortedChildren = node.children.sortedByDescending { it.queries.size }
                sortedChildren.forEachIndexed { index, child ->
                    val last = index == sortedChildren.size - 1
                    walk(child, depth + 1, isLastChild + last)
                }
            }
        }
        
        walk(root, 0, emptyList())
        return list
    }

/**
 * Generates a full ASCII tree visualization of the DAG for structural analysis.
 */
fun buildAsciiHierarchy(root: GraphNode): String {
    val sb = StringBuilder()
    sb.append("============================================================\n")
    sb.append("TAXONOMY DAG ASCII HIERARCHY EXPORT\n")
    sb.append("Generated At: ${java.time.LocalDateTime.now()}\n")
    sb.append("============================================================\n\n")
    
    fun walk(node: GraphNode, prefix: String, isTail: Boolean, visited: MutableSet<String>) {
        val cross = if (visited.contains(node.id)) " [CROSS-LINK]" else ""
        val type = if (node.isLeaf) "Leaf" else "Parent/Residual"
        val nodeLabel = "${node.label} [${node.queries.size} direct q, ${node.getRecursiveQueryCount()} unique q - $type]$cross"
        
        sb.append(prefix).append(if (node.depth == 0) "" else if (isTail) "└── " else "├── ").append(nodeLabel).append("\n")
        
        if (visited.contains(node.id)) return
        visited.add(node.id)
        
        val children = node.children.toList()
        for (i in 0 until children.size) {
            val childIsTail = i == children.size - 1
            val nextPrefix = prefix + if (node.depth == 0) "" else if (isTail) "    " else "│   "
            walk(children[i], nextPrefix, childIsTail, visited)
        }
    }
    
    walk(root, "", true, mutableSetOf())
    sb.append("\n============================================================\n")
    return sb.toString()
}
