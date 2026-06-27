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

    internal val log = LoggerFactory.getLogger("taxonomy.TuiService")
    internal val tuiScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    internal val tuiVersion = "v2.0.0"

    /** Original streams saved before the TUI redirect so they can be restored on exit. */
    private var originalOut: PrintStream? = null
    private var originalErr: PrintStream? = null

    /**
     * Funnel stray stdout/stderr writes into the log for the TUI's lifetime. Mosaic's ANSI
     * frames (which it prints via System.out) are detected by [SlfBufferStream] and passed
     * straight through to the real terminal, so rendering is unaffected.
     */
    private fun redirectStdStreams() {
        if (!config.execution.redirectStdStreams) return
        if (originalOut != null) return // already redirected
        val realOut = System.out
        originalOut = realOut
        originalErr = System.err
        val outLog = LoggerFactory.getLogger("stdout")
        val errLog = LoggerFactory.getLogger("stderr")
        System.setOut(PrintStream(taxonomy.utils.SlfBufferStream(outLog, isError = false, passthrough = realOut), true, "UTF-8"))
        System.setErr(PrintStream(taxonomy.utils.SlfBufferStream(errLog, isError = true, passthrough = null), true, "UTF-8"))
    }

    private fun restoreStdStreams() {
        originalOut?.let { System.setOut(it) }
        originalErr?.let { System.setErr(it) }
        originalOut = null
        originalErr = null
    }

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

    /** Restore the terminal out of the alternate screen / re-enable the cursor. */
    private fun restoreTerminal() {
        try {
            // Leave alt-screen, show cursor, reset attributes.
            print("\u001b[?1049l\u001b[?25h\u001b[0m")
            System.out.flush()
            // Put real stdout/stderr back so post-TUI output (errors, shell) is visible again.
            restoreStdStreams()
            AnsiConsole.systemUninstall()
        } catch (_: Throwable) {
        }
    }

    override fun run(vararg args: String?) = runBlocking {
        if (!config.execution.enableTui) return@runBlocking

        System.setProperty("jline.terminal.color", "true")
        System.setProperty("jline.terminal.type", "xterm-256color")
        // Capture and replace stdout/stderr BEFORE jansi installs, so the real terminal is the
        // passthrough target for Mosaic frames and everything else is funneled into the log.
        redirectStdStreams()
        AnsiConsole.systemInstall()
        System.setOut(PrintStream(System.`out`, true, "UTF-8"))
        print("\u001b[?1049h\u001b[0m\u001b[2J\u001b[H")

        // Ctrl-C / SIGTERM: always restore the terminal and exit hard so the app never
        // appears frozen in the alternate screen buffer.
        val shutdownHook = Thread {
            restoreTerminal()
            Runtime.getRuntime().halt(0)
        }
        runCatching { Runtime.getRuntime().addShutdownHook(shutdownHook) }

        // Snapshot-driven persistence: restore the tunables of the most recent snapshot.
        // Done OFF the startup path so the TUI (LOADING screen) appears instantly; the
        // welcome screen unblocks once the snapshot list has loaded.
        tuiScope.launch {
            try {
                snapshotManager.latestConfig()?.let { config.applyEffectiveConfig(it) }
            } catch (t: Throwable) {
                log.warn("Failed to restore last snapshot config: {}", t.message)
            }
        }

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
                                    deps = deps,
                                    onQuit = {
                                        // Raw-mode terminals deliver Ctrl-C as a key, not SIGINT,
                                        // so quitting is driven explicitly: restore the screen and
                                        // stop the JVM hard so we never hang in the alt-screen.
                                        restoreTerminal()
                                        Runtime.getRuntime().halt(0)
                                    },
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

            // Blocks until the user quits the TUI. When it returns, the app should exit
            // (the TUI is the foreground UI) rather than hang in a background loop.
            runWithTerminal(NonInteractivePolicy.Exit, block)
        } catch (e: Throwable) {
            restoreTerminal()
            val real = if (e is InvocationTargetException) e.cause ?: e else e
            System.err.println("\n[TUI RECOVERY] Layout failure.")
            System.err.println("Cause: ${real.message ?: "Unknown failure"}")
            real.printStackTrace()
            delay(15_000.milliseconds)
        } finally {
            restoreTerminal()
            runCatching { Runtime.getRuntime().removeShutdownHook(shutdownHook) }
            // Exit the JVM so quitting the TUI fully stops the process.
            if (System.getProperty("org.gradle.test.worker") == null) {
                Runtime.getRuntime().halt(0)
            }
        }
    }
}