package org.eclipse.lmos.arc.app.taxonomy.tui

import androidx.compose.runtime.*
import com.jakewharton.mosaic.LocalTerminalState
import com.jakewharton.mosaic.layout.*
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.*
import com.jakewharton.mosaic.text.*
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
import org.eclipse.lmos.arc.app.MMLUDatasetFetcher
import com.jakewharton.mosaic.NonInteractivePolicy
import com.jakewharton.mosaic.terminal.Terminal
import com.jakewharton.mosaic.terminal.Event
import com.jakewharton.mosaic.animation.animateColorAsState
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.channels.ReceiveChannel
import org.eclipse.lmos.arc.app.taxonomy.*
import org.eclipse.lmos.arc.app.taxonomy.operations.*

class MultiplexingTerminal(
    private val delegate: Terminal,
    private val scope: CoroutineScope
) : Terminal {
    private val consumers = mutableListOf<Channel<Event>>()

    init {
        scope.launch {
            try {
                for (event in delegate.events) {
                    val currentConsumers = synchronized(consumers) { consumers.toList() }
                    currentConsumers.forEach { it.trySend(event) }
                }
            } catch (e: Exception) {
                // delegate events closed
            }
        }
    }

    override val name: String get() = delegate.name ?: "Terminal"
    override val state: Terminal.State get() = delegate.state
    override val capabilities: Terminal.Capabilities get() = delegate.capabilities
    override val interactive: Boolean get() = delegate.interactive

    override val events: ReceiveChannel<Event>
        get() {
            val channel = Channel<Event>(Channel.UNLIMITED)
            synchronized(consumers) {
                consumers.add(channel)
            }
            return channel
        }

    override fun close() {
        delegate.close()
        synchronized(consumers) {
            consumers.forEach { it.close() }
            consumers.clear()
        }
    }
}

@Component
@Order(2)
class TaxonomyTuiService(
    internal val config: TaxonomyConfig,
    internal val taxonomyService: TaxonomyService,
    internal val arenaService: TaxonomyArenaService,
    internal val judgeService: TaxonomyJudgeService,
    internal val monitor: GenerationMonitor,
    internal val taxonomyEngine: TaxonomyEngine,
    internal val datasetFetcher: MMLUDatasetFetcher,
    internal val snapshotManager: TaxonomySnapshotManager,
    internal val trickleService: org.eclipse.lmos.arc.app.taxonomy.operations.TaxonomyTrickler,
    internal val embeddingCache: EmbeddingCache
) : CommandLineRunner {

    internal val log = LoggerFactory.getLogger(TaxonomyTuiService::class.java)
    internal val TUI_VERSION = "v1.9.0"

    internal val tuiScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    internal var isRegenerating by mutableStateOf(false)
    internal var isViewingSnapshot by mutableStateOf(false)

    internal var activeSnapshotId by mutableStateOf<String?>(null)
    internal var activeSnapshotDescription by mutableStateOf<String?>(null)

    internal var isRenamingSnapshot by mutableStateOf(false)
    internal var renameInput by mutableStateOf("")

    internal var isEnteringBatchGenerality by mutableStateOf(false)
    internal var batchGeneralityInput by mutableStateOf("1")
    internal var batchReplaceExisting by mutableStateOf(false)
    internal var snapshotVersion by mutableStateOf(0)

    internal var isEnteringArenaQuery by mutableStateOf(false)
    internal var isEnteringArenaModelA by mutableStateOf(false)
    internal var isEnteringArenaModelB by mutableStateOf(false)
    internal var arenaQueryInput by mutableStateOf("")
    internal var arenaModelAInput by mutableStateOf("qwen3.5:2b")
    internal var arenaModelBInput by mutableStateOf("ministral-3:14b")

    internal var isEnteringTrickleQuery by mutableStateOf(false)
    internal var trickleQueryInput by mutableStateOf("")
    internal var trickleResultNodes by mutableStateOf<List<GraphNode>>(emptyList())

    internal var isRunningBatchTrickleTest by mutableStateOf(false)
    internal var batchTrickleProgress by mutableStateOf("")
    internal var batchTrickleResults by mutableStateOf<BatchTrickleTestResults?>(null)
    internal var isViewingBatchTrickleResults by mutableStateOf(false)
    internal var batchTrickleScrollOffset by mutableStateOf(0)

    internal fun triggerRegeneration(onSuccess: (() -> Unit)? = null) {
        if (isRegenerating) return
        isRegenerating = true
        isViewingSnapshot = false
        tuiScope.launch {
            try {
                log.info("Starting TUI-triggered taxonomy regeneration")
                val rawDataset = datasetFetcher.fetchDataset(selectedDomains = config.dataset.selectedDomains)
                val dataset = if (config.dataset.splitDataset) {
                    val (train, _) = datasetFetcher.splitTrainTest(rawDataset, config.dataset.testSplitRatio)
                    train
                } else {
                    rawDataset
                }
                val root = taxonomyEngine.adaptTaxonomy("MMLU Universal Knowledge", dataset)
                taxonomyService.setGraph(root)
                log.info("Taxonomy successfully regenerated and updated in service.")
                
                try {
                    val activeDomains = config.dataset.selectedDomains
                    val domainDesc = if (activeDomains.isEmpty()) "All" else "${activeDomains.size} domains"
                    val desc = "Generated ($domainDesc)"
                    val autoSaved = snapshotManager.saveSnapshot(root, desc)
                    log.info("Automatically saved generated taxonomy snapshot: $desc")
                    activeSnapshotId = autoSaved.id
                    activeSnapshotDescription = autoSaved.description
                    snapshotVersion++
                } catch (se: Exception) {
                    log.error("Failed to auto-save snapshot after regeneration", se)
                }

                config.persistence.savePath?.let {
                    log.info("Saving regenerated taxonomy to $it...")
                    taxonomyService.saveGraph(it)
                }
                onSuccess?.invoke()
            } catch (e: Exception) {
                log.error("Failed to regenerate taxonomy: ${e.message}", e)
            } finally {
                isRegenerating = false
            }
        }
    }

    internal suspend fun startMosaicComposition(terminal: Terminal, content: @Composable () -> Unit) = kotlin.coroutines.suspendCoroutine<Unit> { cont ->
        try {
            val ansiRenderingClass = Class.forName("com.jakewharton.mosaic.AnsiRendering")
            val ansiRenderingConstructor = ansiRenderingClass.getDeclaredConstructor(Terminal.Capabilities::class.java)
            ansiRenderingConstructor.isAccessible = true
            val rendering = ansiRenderingConstructor.newInstance(terminal.capabilities)

            val mosaicKtClass = Class.forName("com.jakewharton.mosaic.MosaicKt")
            val runMosaicCompositionMethod = mosaicKtClass.methods.first { it.name == "runMosaicComposition" }
            runMosaicCompositionMethod.isAccessible = true

            runMosaicCompositionMethod.invoke(null, terminal, rendering, content, cont)
        } catch (e: Exception) {
            val realException = if (e is java.lang.reflect.InvocationTargetException) e.cause ?: e else e
            cont.resumeWith(Result.failure(realException))
        }
    }

    internal suspend fun runWithTerminal(
        onNonInteractive: NonInteractivePolicy,
        block: kotlin.jvm.functions.Function2<Terminal, kotlin.coroutines.Continuation<Unit>, Any?>
    ): Boolean = kotlin.coroutines.suspendCoroutine { cont ->
        try {
            val terminalKtClass = Class.forName("com.jakewharton.mosaic.TerminalKt")
            val withTerminalMethod = terminalKtClass.methods.first { it.name == "withTerminal" }
            withTerminalMethod.isAccessible = true
            withTerminalMethod.invoke(null, onNonInteractive, block, cont)
        } catch (e: Exception) {
            cont.resumeWith(Result.failure(e))
        }
    }

    override fun run(vararg args: String?) = runBlocking {
        if (!config.execution.enableTui) return@runBlocking
        System.setProperty("jline.terminal.color", "true")
        System.setProperty("jline.terminal.type", "xterm-256color")
        AnsiConsole.systemInstall()
        System.setOut(PrintStream(System.`out`, true, "UTF-8"))
        print("\u001b[?1049h\u001b[0m\u001b[2J\u001b[H")

        try {
            val block = object : kotlin.jvm.functions.Function2<Terminal, kotlin.coroutines.Continuation<Unit>, Any?> {
                override fun invoke(originalTerminal: Terminal, childCont: kotlin.coroutines.Continuation<Unit>): Any? {
                    val scope = CoroutineScope(childCont.context)
                    scope.launch {
                        try {
                            val terminal = MultiplexingTerminal(originalTerminal, this)
                            startMosaicComposition(terminal) {
                                Dashboard(terminal)
                            }
                            childCont.resumeWith(Result.success(Unit))
                        } catch (t: Throwable) {
                            childCont.resumeWith(Result.failure(t))
                        }
                    }
                    return kotlin.coroutines.intrinsics.COROUTINE_SUSPENDED
                }
            }
            runWithTerminal(NonInteractivePolicy.Exit, block)
            if (config.execution.startService) {
                while (true) delay(10000)
            }
        } catch (e: Throwable) {
            print("\u001b[?1049l")
            val realCause = if (e is java.lang.reflect.InvocationTargetException) e.cause ?: e else e
            System.err.println("\n[DASHBOARD RECOVERY] Layout Failure.")
            System.err.println("Cause: ${realCause.message ?: "Unknown Failure"}")
            realCause.printStackTrace()
            delay(15000)
        } finally {
            print("\u001b[?1049l")
            AnsiConsole.systemUninstall()
        }
    }

    internal fun autoSaveActiveGraph(root: GraphNode) {
        if (isViewingSnapshot && activeSnapshotId != null) {
            snapshotManager.updateSnapshot(activeSnapshotId!!, root)
            snapshotVersion++
        } else {
            config.persistence.savePath?.let {
                taxonomyService.saveGraph(it)
            }
        }
    }

    internal suspend fun loadTestQueries(): Map<String, List<String>> = withContext(Dispatchers.IO) {
        val file = java.io.File("reserved_test_queries.json")
        if (file.exists()) {
            try {
                val content = file.readText()
                val json = Json { ignoreUnknownKeys = true }
                json.decodeFromString<Map<String, List<String>>>(content)
            } catch (e: Exception) {
                log.error("Failed to load reserved test queries from file", e)
                emptyMap()
            }
        } else {
            val rawDataset = datasetFetcher.fetchDataset(selectedDomains = config.dataset.selectedDomains)
            val (_, test) = datasetFetcher.splitTrainTest(rawDataset, config.dataset.testSplitRatio)
            test
        }
    }

    private fun getDominantDomain(node: GraphNode, queryToCategory: Map<String, String>): String? {
        val branchQueries = node.getAllQueriesInBranch()
        if (branchQueries.isEmpty()) return null
        val counts = branchQueries.mapNotNull { queryToCategory[it.rawText] }.groupingBy { it }.eachCount()
        return counts.maxByOrNull { it.value }?.key
    }

    internal fun runBatchTrickleTest() {
        if (isRunningBatchTrickleTest) return
        val root = taxonomyService.getGraph()
        if (root == null) {
            batchTrickleProgress = "Error: No active taxonomy DAG loaded."
            return
        }
        isRunningBatchTrickleTest = true
        isViewingBatchTrickleResults = false
        batchTrickleResults = null
        batchTrickleProgress = "Initializing batch trickle test..."
        batchTrickleScrollOffset = 0

        tuiScope.launch {
            try {
                batchTrickleProgress = "Loading test queries..."
                val testQueriesMap = loadTestQueries()
                if (testQueriesMap.isEmpty()) {
                    batchTrickleProgress = "Error: No test queries found or generated."
                    isRunningBatchTrickleTest = false
                    return@launch
                }

                val allTestQuestions = testQueriesMap.values.flatten()
                batchTrickleProgress = "Precomputing ${allTestQuestions.size} embeddings..."
                embeddingCache.precompute(allTestQuestions)

                batchTrickleProgress = "Mapping training queries for dominant domains..."
                val queryToCategory = datasetFetcher.getQueryToCategoryMap()

                // Compute dominant domain for each node in DAG
                val nodeToDominantDomain = mutableMapOf<String, String>()
                fun walkNodes(node: GraphNode) {
                    val domain = getDominantDomain(node, queryToCategory)
                    if (domain != null) {
                        nodeToDominantDomain[node.id] = domain
                    }
                    node.children.forEach { walkNodes(it) }
                }
                walkNodes(root)

                var processed = 0
                val total = allTestQuestions.size

                var correctPrimary = 0
                var leafCount = 0
                var residualCount = 0
                var totalDepth = 0
                var totalMatches = 0

                val domainTotals = mutableMapOf<String, Int>()
                val domainCorrectPrimary = mutableMapOf<String, Int>()
                val domainLeafCount = mutableMapOf<String, Int>()
                val domainTotalDepth = mutableMapOf<String, Int>()
                val domainTotalMatches = mutableMapOf<String, Int>()

                val concurrency = 16
                val chunks = allTestQuestions.chunked(concurrency)

                val questionToGtCategory = mutableMapOf<String, String>()
                for ((cat, questions) in testQueriesMap) {
                    for (q in questions) {
                        questionToGtCategory[q] = cat
                    }
                }

                for (chunk in chunks) {
                    val jobs = chunk.map { question ->
                        async {
                            val gtCategory = questionToGtCategory[question] ?: "Unknown"
                            val vector = embeddingCache.getOrCreate(question)
                            val emb = Embedding(question, question, vector)
                            val results = mutableMapOf<GraphNode, Double>()
                            trickleService.trickleQuery(emb, root, results)
                            question to (gtCategory to results)
                        }
                    }
                    val chunkResults = jobs.awaitAll()
                    for ((question, pair) in chunkResults) {
                        val (gtCategory, results) = pair
                        val matchedNodes = results.keys
                        val isLeafAssigned = matchedNodes.any { it.isLeaf }
                        val isResidual = !isLeafAssigned && matchedNodes.isNotEmpty()

                        // Evaluate correctness
                        val primaryNode = results.minByOrNull { it.value }?.key
                        val hasCorrectPrimary = primaryNode?.let { nodeToDominantDomain[it.id]?.equals(gtCategory, ignoreCase = true) } == true

                        val matchedDepthSum = matchedNodes.sumOf { it.depth }
                        val matchedCount = matchedNodes.size

                        synchronized(this) {
                            if (hasCorrectPrimary) correctPrimary++
                            if (isLeafAssigned) leafCount++
                            if (isResidual) residualCount++
                            totalDepth += matchedDepthSum
                            totalMatches += matchedCount

                            domainTotals[gtCategory] = (domainTotals[gtCategory] ?: 0) + 1
                            if (hasCorrectPrimary) {
                                domainCorrectPrimary[gtCategory] = (domainCorrectPrimary[gtCategory] ?: 0) + 1
                            }
                            if (isLeafAssigned) {
                                domainLeafCount[gtCategory] = (domainLeafCount[gtCategory] ?: 0) + 1
                            }
                            domainTotalDepth[gtCategory] = (domainTotalDepth[gtCategory] ?: 0) + matchedDepthSum
                            domainTotalMatches[gtCategory] = (domainTotalMatches[gtCategory] ?: 0) + matchedCount
                        }
                    }

                    processed += chunk.size
                    batchTrickleProgress = "Evaluating trickle routing: $processed / $total queries..."
                }

                // Finalize metrics
                val domainMetrics = domainTotals.map { (domain, count) ->
                    val correct = domainCorrectPrimary[domain] ?: 0
                    val accuracy = if (count > 0) correct.toDouble() / count else 0.0
                    val avgDepth = if (count > 0) (domainTotalDepth[domain] ?: 0).toDouble() / (domainTotalMatches[domain]?.coerceAtLeast(1) ?: 1) else 0.0
                    val leafRate = if (count > 0) (domainLeafCount[domain] ?: 0).toDouble() / count else 0.0
                    DomainMetric(
                        domain = domain,
                        total = count,
                        correct = correct,
                        accuracy = accuracy,
                        averageDepth = avgDepth,
                        leafRate = leafRate
                    )
                }.sortedBy { it.domain }

                val overallAccuracy = if (total > 0) correctPrimary.toDouble() / total else 0.0
                val overallLeafRate = if (total > 0) leafCount.toDouble() / total else 0.0
                val overallResidualRate = if (total > 0) residualCount.toDouble() / total else 0.0
                val overallAverageDepth = if (totalMatches > 0) totalDepth.toDouble() / totalMatches else 0.0
                val overallAverageMatches = if (total > 0) totalMatches.toDouble() / total else 0.0

                batchTrickleResults = BatchTrickleTestResults(
                    totalQueries = total,
                    overallAccuracy = overallAccuracy,
                    leafRate = overallLeafRate,
                    residualRate = overallResidualRate,
                    averageDepth = overallAverageDepth,
                    averageMatches = overallAverageMatches,
                    domainMetrics = domainMetrics
                )
                isViewingBatchTrickleResults = true
                batchTrickleProgress = "Batch trickle test completed successfully!"
            } catch (e: Exception) {
                log.error("Batch trickle test failed", e)
                batchTrickleProgress = "Error: ${e.message}"
            } finally {
                isRunningBatchTrickleTest = false
            }
        }
    }

}

@kotlinx.serialization.Serializable
data class DomainMetric(
    val domain: String,
    val total: Int,
    val correct: Int,
    val accuracy: Double,
    val averageDepth: Double,
    val leafRate: Double
)

@kotlinx.serialization.Serializable
data class BatchTrickleTestResults(
    val totalQueries: Int,
    val overallAccuracy: Double,
    val leafRate: Double,
    val residualRate: Double,
    val averageDepth: Double,
    val averageMatches: Double,
    val domainMetrics: List<DomainMetric>
)
