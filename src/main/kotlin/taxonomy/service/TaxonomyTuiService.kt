package taxonomy.service

import androidx.compose.runtime.Composable
import com.jakewharton.mosaic.NonInteractivePolicy
import com.jakewharton.mosaic.terminal.Event
import com.jakewharton.mosaic.terminal.Terminal
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.channels.ReceiveChannel
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.delay
import org.fusesource.jansi.AnsiConsole
import org.slf4j.LoggerFactory
import org.springframework.boot.CommandLineRunner
import org.springframework.core.annotation.Order
import org.springframework.stereotype.Component
import taxonomy.TaxonomyEngine
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.dataset.ModelEvalLoader
import taxonomy.dataset.ModelEvalStore
import taxonomy.operations.TaxonomyTrickler
import taxonomy.tui.app.TuiApp
import taxonomy.tui.app.toTuiDependencies
import taxonomy.utils.GenerationMonitor
import java.io.PrintStream
import java.lang.reflect.InvocationTargetException
import kotlin.coroutines.Continuation
import kotlin.coroutines.intrinsics.COROUTINE_SUSPENDED
import kotlin.time.Duration.Companion.milliseconds

class MultiplexingTerminal(
    private val delegate: Terminal,
    private val scope: CoroutineScope
) : Terminal {
    private val consumers = mutableListOf<Channel<Event>>()

    init {
        scope.launch {
            try {
                for (event in delegate.events) {
                    val snapshot = synchronized(consumers) { consumers.toList() }
                    snapshot.forEach { it.trySend(event) }
                }
            } catch (_: Exception) {
            }
        }
    }

    override val name: String
        get() = delegate.name ?: "Terminal"

    override val state: Terminal.State
        get() = delegate.state

    override val capabilities: Terminal.Capabilities
        get() = delegate.capabilities

    override val interactive: Boolean
        get() = delegate.interactive

    override val events: ReceiveChannel<Event>
        get() {
            val channel = Channel<Event>(Channel.UNLIMITED)
            synchronized(consumers) { consumers.add(channel) }
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
    internal val inferenceMonitor: GenerationMonitor,
    internal val taxonomyEngine: TaxonomyEngine,
    internal val datasetFetcher: MMLUDatasetFetcher,
    internal val snapshotManager: TaxonomySnapshotManager,
    internal val trickleService: TaxonomyTrickler,
    internal val embeddingCache: EmbeddingCache,
    internal val benchmarkService: TaxonomyBenchmarkService,
    internal val evalLoader: ModelEvalLoader,
    internal val evalStore: ModelEvalStore,
) : CommandLineRunner {

    internal val log = LoggerFactory.getLogger("TuiService")
    internal val tuiScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    internal val tuiVersion = "v2.0.0"

    internal suspend fun startMosaicComposition(
        terminal: Terminal,
        content: @Composable () -> Unit
    ) = suspendCancellableCoroutine<Unit> { cont ->
        try {
            val ansiClass = Class.forName("com.jakewharton.mosaic.AnsiRendering")
            val ansiCtor = ansiClass
                .getDeclaredConstructor(Terminal.Capabilities::class.java)
                .also { it.isAccessible = true }
            val rendering = ansiCtor.newInstance(terminal.capabilities)

            val mosaicKt = Class.forName("com.jakewharton.mosaic.MosaicKt")
            val runMethod = mosaicKt.methods
                .first { it.name == "runMosaicComposition" }
                .also { it.isAccessible = true }

            runMethod.invoke(null, terminal, rendering, content, cont)
        } catch (e: Exception) {
            val real = if (e is InvocationTargetException) e.cause ?: e else e
            cont.resumeWith(Result.failure(real))
        }
    }

    internal suspend fun runWithTerminal(
        onNonInteractive: NonInteractivePolicy,
        block: Function2<Terminal, Continuation<Unit>, Any?>
    ): Boolean = suspendCancellableCoroutine { cont ->
        try {
            val terminalKt = Class.forName("com.jakewharton.mosaic.TerminalKt")
            val withTerminal = terminalKt.methods
                .first { it.name == "withTerminal" }
                .also { it.isAccessible = true }

            withTerminal.invoke(null, onNonInteractive, block, cont)
        } catch (e: Exception) {
            cont.resumeWith(Result.failure(e))
        }
    }

    override fun run(vararg args: String?) = runBlocking {
        if (!config.execution.enableTui) return@runBlocking

        // Snapshot-driven persistence: restore the tunables of the most recent snapshot on startup
        // so the TUI opens with the last loaded/generated configuration (secrets stay env-sourced).
        snapshotManager.latestConfig()?.let { config.applyEffectiveConfig(it) }

        System.setProperty("jline.terminal.color", "true")
        System.setProperty("jline.terminal.type", "xterm-256color")
        AnsiConsole.systemInstall()
        System.setOut(PrintStream(System.`out`, true, "UTF-8"))
        print("\u001b[?1049h\u001b[0m\u001b[2J\u001b[H")

        try {
            val deps = toTuiDependencies()

            val block = object : Function2<Terminal, Continuation<Unit>, Any?> {
                override fun invoke(
                    originalTerminal: Terminal,
                    childCont: Continuation<Unit>
                ): Any {
                    val scope = CoroutineScope(childCont.context)
                    scope.launch {
                        try {
                            val terminal = MultiplexingTerminal(originalTerminal, this)
                            startMosaicComposition(terminal) {
                                TuiApp(
                                    terminal = terminal,
                                    deps = deps
                                )
                            }
                            childCont.resumeWith(Result.success(Unit))
                        } catch (t: Throwable) {
                            childCont.resumeWith(Result.failure(t))
                        }
                    }
                    return COROUTINE_SUSPENDED
                }
            }

            runWithTerminal(NonInteractivePolicy.Exit, block)

            if (config.execution.startService) {
                while (true) delay(10_000.milliseconds)
            }
        } catch (e: Throwable) {
            print("\u001b[?1049l")
            val real = if (e is InvocationTargetException) e.cause ?: e else e
            System.err.println("\n[TUI RECOVERY] Layout failure.")
            System.err.println("Cause: ${real.message ?: "Unknown failure"}")
            real.printStackTrace()
            delay(15_000.milliseconds)
        } finally {
            print("\u001b[?1049l")
            AnsiConsole.systemUninstall()
        }
    }
}