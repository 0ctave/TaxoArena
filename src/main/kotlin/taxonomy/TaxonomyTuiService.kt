package org.eclipse.lmos.arc.app.taxonomy

import androidx.compose.runtime.*
import com.jakewharton.mosaic.LocalTerminalState
import com.jakewharton.mosaic.layout.fillMaxSize
import com.jakewharton.mosaic.layout.padding
import com.jakewharton.mosaic.layout.height
import com.jakewharton.mosaic.layout.width
import com.jakewharton.mosaic.layout.fillMaxWidth
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.layout.onKeyEvent
import com.jakewharton.mosaic.runMosaicMain
import com.jakewharton.mosaic.ui.*
import com.jakewharton.mosaic.text.SpanStyle
import com.jakewharton.mosaic.text.AnnotatedString
import com.jakewharton.mosaic.text.buildAnnotatedString
import com.jakewharton.mosaic.text.withStyle
import com.jakewharton.mosaic.ui.Color.Companion.Blue
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.Magenta
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Black
import com.jakewharton.mosaic.ui.Color.Companion.Red
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import kotlinx.coroutines.*
import org.slf4j.LoggerFactory
import org.springframework.boot.CommandLineRunner
import org.springframework.core.annotation.Order
import org.springframework.stereotype.Component
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import java.io.PrintStream
import kotlinx.serialization.json.*
import org.fusesource.jansi.AnsiConsole

@Component
@Order(2)
class TaxonomyTuiService(
    private val config: TaxonomyConfig,
    private val taxonomyService: TaxonomyService,
    private val arenaService: TaxonomyArenaService,
    private val judgeService: TaxonomyJudgeService,
    private val monitor: GenerationMonitor
) : CommandLineRunner {

    private val log = LoggerFactory.getLogger(TaxonomyTuiService::class.java)
    private val TUI_VERSION = "v1.7.0"

    private val tuiScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    override fun run(vararg args: String?) = runBlocking {
        if (!config.enableTui) return@runBlocking
        AnsiConsole.systemInstall()
        System.setOut(PrintStream(System.`out`, true, "UTF-8"))
        print("\u001b[?1049h\u001b[0m\u001b[2J\u001b[H")

        try {
            runMosaicMain {
                Dashboard()
            }
            if (config.startService) {
                while (true) delay(10000)
            }
        } catch (e: Throwable) {
            print("\u001b[?1049l")
            System.err.println("\n[DASHBOARD RECOVERY] Layout Failure.")
            System.err.println("Cause: ${e.message ?: "Unknown Check Failure"}")
            e.printStackTrace()
            delay(15000)
        } finally {
            print("\u001b[?1049l")
            AnsiConsole.systemUninstall()
        }
    }

    @Composable
    fun Dashboard() {
        val terminalState = LocalTerminalState.current
        val width = terminalState.size.columns.coerceAtLeast(100)
        val height = terminalState.size.rows.coerceAtLeast(25)

        if (width < 100 || height < 20) {
            Column {
                Text(" [ WINDOW TOO SMALL ] ", color = Black, background = Yellow, textStyle = Bold)
                Text(" Minimum: 100x20 | Current: ${width}x${height} ", color = White)
            }
            return
        }

        val rootNode by taxonomyService.rootNodeFlow.collectAsState()
        val controlState by arenaService.state.collectAsState()
        val time by produceState(LocalTime.now()) {
            while(true) { delay(1000); value = LocalTime.now() }
        }

        var scrollOffset by remember { mutableIntStateOf(0) }
        var selectedIdx by remember { mutableIntStateOf(0) }
        var autoScroll by remember { mutableStateOf(true) }
        var inspectorScroll by remember { mutableIntStateOf(0) }

        val allNodes = remember(rootNode) {
            if (rootNode == null) emptyList<GraphNode>()
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

        val dagWidth = 60
        val arenaWidth = width - dagWidth - 1
        
        // --- MARKDOWN AWARE INSPECTOR LINES ---
        val inspectorLines = remember(controlState.selectedNode, arenaWidth) {
            val node = controlState.selectedNode ?: return@remember emptyList<AnnotatedString>()
            val list = mutableListOf<AnnotatedString>()
            list.add(buildAnnotatedString { append("ID: ${node.id}".take(arenaWidth - 4)) })
            list.add(buildAnnotatedString { append("Depth: ${node.depth} | Queries: ${node.queries.size}".take(arenaWidth - 4)) })
            list.add(buildAnnotatedString { append("━".repeat(maxOf(0, arenaWidth - 4))) })
            
            val jsonParser = Json { ignoreUnknownKeys = true; isLenient = true; prettyPrint = true }
            
            fun addMarkdownLines(text: String, indent: Int = 0) {
                renderMarkdown(text, arenaWidth - indent - 6).forEach { line ->
                    list.add(buildAnnotatedString {
                        append(" ".repeat(indent))
                        append(line)
                    })
                }
            }

            fun formatJsonElement(key: String, element: JsonElement, indent: Int = 0) {
                val prefix = " ".repeat(indent)
                val formattedKey = key.replace("_", " ").uppercase()
                
                when (element) {
                    is JsonPrimitive -> {
                        if (element.isString) {
                            list.add(buildAnnotatedString { 
                                append(prefix)
                                withStyle(SpanStyle(color = Green, textStyle = Bold)) { append(formattedKey + ":") }
                            })
                            addMarkdownLines(element.content, indent + 2)
                        } else {
                            list.add(buildAnnotatedString {
                                append(prefix)
                                withStyle(SpanStyle(color = Green, textStyle = Bold)) { append(formattedKey + ": ") }
                                append(element.content)
                            })
                        }
                    }
                    is JsonArray -> {
                        list.add(buildAnnotatedString {
                            append(prefix)
                            withStyle(SpanStyle(color = Green, textStyle = Bold)) { append(formattedKey + ":") }
                        })
                        element.forEach { item ->
                            if (item is JsonObject) {
                                item.entries.forEachIndexed { i, entry ->
                                    if (i == 0) formatJsonElement("- ${entry.key}", entry.value, indent + 2)
                                    else formatJsonElement(entry.key, entry.value, indent + 4)
                                }
                            } else if (item is JsonPrimitive) {
                                val mdLines = renderMarkdown(item.content, arenaWidth - indent - 8)
                                mdLines.forEachIndexed { i, line ->
                                    list.add(buildAnnotatedString {
                                        append(prefix)
                                        if (i == 0) {
                                            withStyle(SpanStyle(color = Magenta)) { append("  - ") }
                                        } else {
                                            append("    ")
                                        }
                                        append(line)
                                    })
                                }
                            }
                        }
                    }
                    is JsonObject -> {
                        list.add(buildAnnotatedString {
                            append(prefix)
                            withStyle(SpanStyle(color = Green, textStyle = Bold)) { append(formattedKey + ":") }
                        })
                        element.entries.forEach { entry ->
                            formatJsonElement(entry.key, entry.value, indent + 2)
                        }
                    }
                    else -> list.add(buildAnnotatedString { append("$prefix$formattedKey: $element") })
                }
            }

            fun tryParseAndFormat(content: String, fallbackLabel: String) {
                try {
                    val firstBrace = content.indexOf('{')
                    val lastBrace = content.lastIndexOf('}')
                    val cleanJson = if (firstBrace != -1 && lastBrace != -1 && lastBrace > firstBrace) {
                        content.substring(firstBrace, lastBrace + 1)
                    } else content
                    val parsed = jsonParser.parseToJsonElement(cleanJson)
                    if (parsed is JsonObject) {
                        if (parsed.containsKey("system_prompt") || parsed.containsKey("rubric")) {
                            parsed.entries.forEach { formatJsonElement(it.key, it.value) }
                        } else {
                            formatJsonElement(fallbackLabel, parsed)
                        }
                    } else {
                        formatJsonElement(fallbackLabel, parsed)
                    }
                } catch (e: Exception) {
                    list.add(buildAnnotatedString { withStyle(SpanStyle(color = Green, textStyle = Bold)) { append("$fallbackLabel:") } })
                    addMarkdownLines(content, 2)
                }
                list.add(buildAnnotatedString { append("") })
            }

            if (node.judgePrompt == null) {
                list.add(buildAnnotatedString { append("STATUS: No Expert Judge induced yet.") })
            } else {
                tryParseAndFormat(node.judgePrompt!!, "SYSTEM PERSONA")
                if (node.judgeRubric != null) tryParseAndFormat(node.judgeRubric!!, "GRADING RUBRIC")
            }
            list
        }

        Column(
            modifier = Modifier.width(width).height(height).onKeyEvent { event ->
                val key = event.key.lowercase()
                if (controlState.mode == MissionControlMode.NODE_DETAIL) {
                    val topH = ((height - 8) * 0.6).toInt().coerceAtLeast(10)
                    val visibleLines = (topH - 2).coerceAtLeast(1)
                    val maxScroll = maxOf(0, inspectorLines.size - visibleLines)
                    when {
                        key == "z" || key == "w" || key == "arrowup" -> { inspectorScroll = (inspectorScroll - 1).coerceAtLeast(0); true }
                        key == "s" || key == "arrowdown" -> { inspectorScroll = (inspectorScroll + 1).coerceIn(0, maxScroll); true }
                        key == "r" || key == "R" -> { 
                            val selectedNode = controlState.selectedNode
                            if (selectedNode != null && rootNode != null) {
                                tuiScope.launch { judgeService.generateJudgeForNodeById(rootNode!!, selectedNode.id) }
                            }
                            true
                        }
                        key == "q" || key == "a" || key == "escape" || key == "backspace" -> { arenaService.setMode(MissionControlMode.IDLE); true }
                        else -> false
                    }
                } else {
                    when {
                        key == "z" || key == "w" || key == "arrowup" -> {
                            selectedIdx = maxOf(0, selectedIdx - 1)
                            if (selectedIdx < scrollOffset) scrollOffset = selectedIdx
                            autoScroll = false
                            true
                        }
                        key == "s" || key == "arrowdown" -> {
                            selectedIdx = minOf(allNodes.size - 1, selectedIdx + 1)
                            autoScroll = false
                            true
                        }
                        key == "enter" || key == " " -> {
                            if (selectedIdx in allNodes.indices) {
                                inspectorScroll = 0
                                arenaService.inspectNode(allNodes[selectedIdx])
                            }
                            true
                        }
                        key == "r" || key == "R" -> {
                            if (selectedIdx in allNodes.indices && rootNode != null) {
                                val node = allNodes[selectedIdx]
                                tuiScope.launch { judgeService.generateJudgeForNodeById(rootNode!!, node.id) }
                            }
                            true
                        }
                        key == "g" || key == "G" -> {
                            if (rootNode != null) {
                                tuiScope.launch { judgeService.generateJudgesForDag(rootNode!!, replaceExisting = false) }
                            }
                            true
                        }
                        key == "f" || key == "F" -> {
                            if (rootNode != null) {
                                tuiScope.launch { judgeService.generateJudgesForDag(rootNode!!, replaceExisting = true) }
                            }
                            true
                        }
                        key == "a" || key == "q" -> { autoScroll = true; arenaService.setMode(MissionControlMode.IDLE); true }
                        else -> false
                    }
                }
            }
        ) {
            Spacer(Modifier.height(1))
            Header(width, rootNode, time)
            Spacer(Modifier.height(1))

            val topH = ((height - 8) * 0.6).toInt().coerceAtLeast(10)
            val bottomH = (height - 8 - topH).coerceAtLeast(5)

            Row(modifier = Modifier.height(topH)) {
                BTopPanelPro(" TOPOLOGY ", Blue, dagWidth, topH) {
                    DagTable(dagWidth - 2, topH - 2, allNodes, scrollOffset, selectedIdx)
                }
                Spacer(Modifier.width(1))
                BTopPanelPro(" MISSION CONTROL HUB ", Magenta, arenaWidth, topH) {
                    MissionControlHub(arenaWidth - 2, topH - 2, controlState, inspectorScroll, inspectorLines)
                }
            }

            Spacer(Modifier.height(1))

            val logsW = (width * 0.6).toInt()
            val traceW = width - logsW - 1
            Row(modifier = Modifier.height(bottomH)) {
                BTopPanelPro(" SYSTEM LOGS ", White, logsW, bottomH) {
                    LogView(logsW - 4, bottomH - 2)
                }
                Spacer(Modifier.width(1))
                BTopPanelPro(" GPU TRACES (MARKDOWN) ", Cyan, traceW, bottomH) {
                    InferenceStreams(traceW - 5, bottomH - 2)
                }
            }
            
            Text(buildAnnotatedString {
                withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append(" [Z/S] ") }
                append("Move/Scroll | ")
                withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append(" [Enter] ") }
                append("Inspect | ")
                withStyle(SpanStyle(color = Green, textStyle = Bold)) { append(" [R] ") }
                append("Regen Node | ")
                withStyle(SpanStyle(color = Yellow, textStyle = Bold)) { append(" [G] ") }
                append("Missing | ")
                withStyle(SpanStyle(color = Magenta, textStyle = Bold)) { append(" [F] ") }
                append("Force All ")
            }.take(width - 2), modifier = Modifier.height(1))
        }
        
        LaunchedEffect(autoScroll, allNodes.size) {
            if (autoScroll && allNodes.isNotEmpty()) {
                while(true) {
                    delay(5000)
                    scrollOffset = (scrollOffset + 1) % allNodes.size
                }
            }
        }
    }

    @Composable
    fun MissionControlHub(pWidth: Int, pHeight: Int, state: MissionControlState, inspectorScroll: Int, inspectorLines: List<AnnotatedString>) {
        when (state.mode) {
            MissionControlMode.IDLE -> Text("IDLE. Select a domain or await activity...".take(pWidth - 2), color = White)
            MissionControlMode.ARENA -> DetailedArena(pWidth, pHeight, state)
            MissionControlMode.JUDGE_PROGRESS -> JudgeInductionProgress(pWidth, pHeight, state)
            MissionControlMode.NODE_DETAIL -> NodeInspector(pWidth, pHeight, state.selectedNode, inspectorScroll, inspectorLines)
        }
    }

    @Composable
    fun NodeInspector(pWidth: Int, pHeight: Int, node: GraphNode?, scroll: Int, lines: List<AnnotatedString>) {
        if (node == null) { Text("No node selected."); return }
        val visibleLines = (pHeight - 2).coerceAtLeast(1)
        val maxScroll = maxOf(0, lines.size - visibleLines)
        val startIdx = scroll.coerceIn(0, maxScroll)
        val displayed = lines.drop(startIdx).take(visibleLines)
        Column {
            Text(" INSPECTOR: ${node.label.uppercase()} ".take(pWidth - 2), color = Cyan, background = Blue, textStyle = Bold)
            Row {
                Column(modifier = Modifier.width(pWidth - 1)) {
                    displayed.forEach { line ->
                        Text(line.take(pWidth - 2))
                    }
                    repeat(visibleLines - displayed.size) { Text(" ".repeat(pWidth - 1)) }
                }
                Column(modifier = Modifier.width(1)) {
                    if (maxScroll > 0) {
                        val scrollRatio = startIdx.toDouble() / maxScroll
                        val scrollPos = (scrollRatio * (visibleLines - 1)).toInt()
                        repeat(visibleLines) { i -> Text(if (i == scrollPos) "▓" else "│", color = Cyan) }
                    } else repeat(visibleLines) { Text(" ", color = Blue) }
                }
            }
        }
    }

    @Composable
    fun DetailedArena(pWidth: Int, pHeight: Int, state: MissionControlState) {
        Column {
            Text("MATCH: ${state.modelA} vs ${state.modelB}".take(pWidth - 2), color = Cyan, textStyle = Bold)
            val queryText = state.query?.take(pWidth - 2) ?: ""
            Text("QUERY: $queryText".take(pWidth - 2), color = White)
            Text("━".repeat(maxOf(0, pWidth - 2)).take(pWidth - 2), color = Magenta)

            val domains = state.domainStatus.entries.toList()
            val rowsPerCol = (pHeight - 8).coerceAtLeast(1)
            val colW = pWidth / 2
            Row(modifier = Modifier.width(pWidth)) {
                Column(modifier = Modifier.width(colW)) {
                    domains.take(rowsPerCol).forEach { (label, status) ->
                        val color = if(status.contains("Model")) Green else if(status == "JUDGING") Yellow else White
                        val line = "» ${label.take(colW - 12).padEnd(colW - 12)}: ${status.take(8)}"
                        Text(line.take(colW - 2), color = color)
                    }
                }
                Column(modifier = Modifier.width(colW)) {
                    domains.drop(rowsPerCol).take(rowsPerCol).forEach { (label, status) ->
                        val color = if(status.contains("Model")) Green else if(status == "JUDGING") Yellow else White
                        val line = "» ${label.take(colW - 12).padEnd(colW - 12)}: ${status.take(8)}"
                        Text(line.take(colW - 2), color = color)
                    }
                }
            }
        }
    }

    @Composable
    fun JudgeInductionProgress(pWidth: Int, pHeight: Int, state: MissionControlState) {
        Column {
            Text("AGENT JUDGE INDUCTION PROGRESS".take(pWidth - 2), color = Yellow, textStyle = Bold)
            Text("━".repeat(maxOf(0, pWidth - 2)).take(pWidth - 2), color = Yellow)
            state.currentInductions.values.take(pHeight - 3).forEach { prog ->
                val percent = if(prog.total > 0) (prog.processed.toDouble() / prog.total) else 0.0
                val labelW = 12
                val percentW = 5
                val statusW = 10
                val barW = (pWidth - labelW - percentW - statusW - 10).coerceAtLeast(5)
                val filled = (percent * barW).toInt()
                
                val annot = buildAnnotatedString {
                    append("» ${prog.nodeLabel.take(labelW).padEnd(labelW)} [")
                    withStyle(SpanStyle(color = Green)) { append("█".repeat(filled)) }
                    append(" ".repeat(maxOf(0, barW - filled)))
                    append("] ")
                    withStyle(SpanStyle(color = Cyan)) { append("${(percent * 100).toInt()}%".padEnd(percentW)) }
                    append(" ")
                    withStyle(SpanStyle(color = if(prog.status == "READY") Green else Yellow)) {
                        append(prog.status.take(statusW))
                    }
                }
                Text(annot.take(pWidth - 2))
            }
        }
    }

    private fun AnnotatedString.take(n: Int): AnnotatedString {
        if (this.length <= n) return this
        return this.subSequence(0, n)
    }

    @Composable
    fun DagTable(pWidth: Int, pHeight: Int, nodes: List<GraphNode>, offset: Int, selectedIdx: Int) {
        if (nodes.isEmpty()) { Text("Awaiting data...".take(pWidth - 2), color = Yellow); return }
        val visible = (pHeight - 3).coerceAtLeast(1)
        val startIdx = if (selectedIdx in nodes.indices) {
             if (selectedIdx < offset) selectedIdx 
             else if (selectedIdx >= offset + visible) selectedIdx - visible + 1
             else offset
        } else offset % nodes.size
        val items = nodes.drop(startIdx).take(visible)
        Column {
            Text("   Domain".padEnd(35) + " | D | Q-Pool | Judge", color = White, textStyle = Bold)
            Text("─".repeat(maxOf(0, pWidth - 2)).take(pWidth - 2), color = Blue)
            items.forEachIndexed { i, node ->
                val isSelected = (startIdx + i) == selectedIdx
                val label = node.label.padEnd(32).take(32)
                val judge = if (node.judgePrompt != null) " OK " else " -- "
                val totalQ = node.getRecursiveQueryCount()
                val qStr = totalQ.toString().padEnd(6).take(6)

                if (isSelected) {
                    Row {
                        Text(" > ", color = Yellow, background = Blue, textStyle = Bold)
                        val annot = buildAnnotatedString {
                            append("$label | ${node.depth} | ")
                            withStyle(SpanStyle(color = Cyan)) { append(qStr) }
                            append(" |")
                        }
                        Text(annot.take(pWidth - 10), color = White, background = Blue)
                        Text(judge.take(4), color = if (node.judgePrompt != null) Green else White, background = Blue)
                    }
                } else {
                    Row {
                        Text("   ", color = White, textStyle = Bold)
                        val annot = buildAnnotatedString {
                            append("$label | ${node.depth} | ")
                            withStyle(SpanStyle(color = Cyan)) { append(qStr) }
                            append(" |")
                        }
                        Text(annot.take(pWidth - 10), color = White)
                        Text(judge.take(4), color = if (node.judgePrompt != null) Green else White)
                    }
                }
            }
        }
    }

    @Composable
    fun BTopPanelPro(title: String, color: Color, width: Int, height: Int, content: @Composable () -> Unit) {
        Column(modifier = Modifier.width(width).height(height)) {
            val annot = buildAnnotatedString {
                withStyle(SpanStyle(color = color)) {
                    append("┏━")
                    withStyle(SpanStyle(textStyle = Bold)) { append(title.take(width - 6)) }
                    val repeatCount = maxOf(0, width - 4 - title.length)
                    append("━".repeat(repeatCount))
                    append("┓")
                }
            }
            Text(annot.take(width - 1), modifier = Modifier.height(1))
            Box(modifier = Modifier.width(maxOf(1, width - 2)).height(maxOf(1, height - 2)).padding(horizontal = 1)) {
                content()
            }
            Text(("┗" + "━".repeat(maxOf(0, width - 2)) + "┛").take(width - 1), color = color, modifier = Modifier.height(1))
        }
    }

    @Composable
    fun Header(width: Int, root: GraphNode?, time: LocalTime) {
        val status = if (root != null) "READY" else "LOADING"
        val statusColor = if (root != null) Green else Yellow
        val timeStr = time.format(DateTimeFormatter.ofPattern("HH:mm:ss"))
        Column(modifier = Modifier.width(width).height(3)) {
            Text(" ARCTAXOADAPAT: DYNAMIC SEMANTIC DAG ENGINE [$TUI_VERSION] ".center(width).take(width - 2), color = Black, background = Cyan, textStyle = Bold)
            val annot = buildAnnotatedString {
                val line = " Status: $status | Model: ${config.judgeModel} | Uptime: $timeStr "
                val centered = line.center(width)
                append(centered.substringBefore(status))
                withStyle(SpanStyle(color = statusColor)) { append(status) }
                append(" | Model: ")
                withStyle(SpanStyle(color = Magenta)) { append(config.judgeModel) }
                append(centered.substringAfter(config.judgeModel))
            }
            Text(annot.take(width - 2), color = White)
            Text("━".repeat(maxOf(0, width - 2)).take(width - 2), color = White)
        }
    }

    @Composable
    fun LogView(pWidth: Int, pHeight: Int) {
        val logs = TuiLogAppender.logs
        Column { logs.takeLast(maxOf(1, pHeight)).forEach { log -> Text(" » ${log.take(pWidth - 4)}".take(pWidth - 2), color = White) } }
    }

    @Composable
    fun InferenceStreams(pWidth: Int, pHeight: Int) {
        val activeSlots = monitor.activeSlots.values.toList()
        Column {
            if (activeSlots.isEmpty()) { Text("GPU Cold. (3090 IDLE)".take(pWidth - 2), color = White) }
            else {
                activeSlots.take(maxOf(1, pHeight / 4)).forEach { slot ->
                    val color = if (slot.isComplete) Green else Yellow
                    Column {
                        Text("[${if (slot.isComplete) "DONE" else "BUSY"}] ${slot.modelName.take(15)}".take(pWidth - 2), color = color, textStyle = Bold)
                        renderMarkdown(slot.text.takeLast(maxOf(1, pWidth * 3)), pWidth - 4).take(3).forEach { line ->
                             Text(line.take(pWidth - 2))
                        }
                        Spacer(Modifier.height(1))
                    }
                }
            }
        }
    }

    /**
     * Specialized Simple Markdown Renderer for Terminal.
     * Handles: # Header, **Bold**, - List, `Code`
     */
    private fun renderMarkdown(text: String, maxWidth: Int): List<AnnotatedString> {
        val lines = text.lines()
        val result = mutableListOf<AnnotatedString>()

        lines.forEach { rawLine ->
            val line = rawLine.trim()
            if (line.isEmpty()) {
                result.add(buildAnnotatedString { append("") })
                return@forEach
            }

            val formattedLine = buildAnnotatedString {
                var currentText = line

                // 1. HEADERS: # Title
                if (currentText.startsWith("#")) {
                    val hashes = currentText.takeWhile { it == '#' }.length
                    val content = currentText.drop(hashes).trim()
                    withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
                        append(" ".repeat(maxOf(0, hashes - 1)))
                        append("■ $content")
                    }
                    return@buildAnnotatedString
                }

                // 2. LISTS: - Item
                if (currentText.startsWith("- ") || currentText.startsWith("* ")) {
                    withStyle(SpanStyle(color = Magenta)) { append("• ") }
                    currentText = currentText.drop(2)
                }

                // 3. INLINE STYLES (Sequential parser)
                var i = 0
                while (i < currentText.length) {
                    when {
                        // BOLD: **text**
                        currentText.startsWith("**", i) -> {
                            val end = currentText.indexOf("**", i + 2)
                            if (end != -1) {
                                withStyle(SpanStyle(textStyle = Bold, color = Yellow)) {
                                    append(currentText.substring(i + 2, end))
                                }
                                i = end + 2
                            } else {
                                append(currentText[i].toString())
                                i++
                            }
                        }
                        // CODE: `text`
                        currentText.startsWith("`", i) -> {
                            val end = currentText.indexOf("`", i + 1)
                            if (end != -1) {
                                withStyle(SpanStyle(color = Yellow, background = Black)) {
                                    append(currentText.substring(i + 1, end))
                                }
                                i = end + 1
                            } else {
                                append(currentText[i].toString())
                                i++
                            }
                        }
                        else -> {
                            append(currentText[i].toString())
                            i++
                        }
                    }
                }
            }
            
            // Wrap formatted line to width
            result.addAll(formattedLine.safeChunked(maxWidth))
        }
        return result
    }

    // Proper chunked implementation for AnnotatedString
    private fun AnnotatedString.safeChunked(width: Int): List<AnnotatedString> {
        if (this.length <= width || width <= 0) return listOf(this)
        val result = mutableListOf<AnnotatedString>()
        var start = 0
        while (start < this.length) {
            val end = minOf(start + width, this.length)
            result.add(this.subSequence(start, end))
            start = end
        }
        return result
    }

    private fun String.center(width: Int): String {
        val target = width - 1
        if (this.length >= target) return this.take(target)
        val padding = (target - this.length) / 2
        return " ".repeat(maxOf(0, padding)) + this
    }
}
