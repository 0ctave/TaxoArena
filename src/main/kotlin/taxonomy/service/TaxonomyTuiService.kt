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
     * Funnel stray writes into the log for the TUI's lifetime. Restored to the PR #58 behavior:
     * BOTH System.out and System.err are redirected by default ([ExecutionConfig.redirectStdoutAlso]
     * defaults to true). The redirected stdout keeps a passthrough to the real terminal so Mosaic's
     * ANSI frames still reach the screen while stray library writes are funneled into the log.
     *
     * Runs BEFORE [AnsiConsole.systemInstall] (the PR #58 ordering that renders correctly on
     * Windows / JDK 23); the explicit UTF-8 System.out re-wrap in run() happens after jansi installs.
     */
    private fun redirectStdStreams() {
        if (!config.execution.redirectStdStreams) return
        if (originalOut != null) return // already redirected
        val realOut = System.out
        originalOut = realOut
        originalErr = System.err
        val errLog = LoggerFactory.getLogger("stderr")
        System.setErr(PrintStream(taxonomy.utils.SlfBufferStream(errLog, isError = true, passthrough = null), true, "UTF-8"))
        if (config.execution.redirectStdoutAlso) {
            val outLog = LoggerFactory.getLogger("stdout")
            System.setOut(PrintStream(taxonomy.utils.SlfBufferStream(outLog, isError = false, passthrough = realOut), true, "UTF-8"))
        }
    }

    private fun restoreStdStreams() {
        originalOut?.let { System.setOut(it) }
        originalErr?.let { System.setErr(it) }
        originalOut = null
        originalErr = null
    }

    /**
     * Pre-flight: ask Mosaic's internal native binding whether a real TTY is attached, BEFORE we
     * enter the alt-screen or redirect streams. Returns:
     *  - `true`  — a TTY was bound (and immediately released so [runWithTerminal] can re-bind),
     *  - `false` — Mosaic reports no controlling terminal (pipe / IDE / non-interactive shell),
     *  - `null`  — the probe itself could not run (internal API changed); caller proceeds optimistically.
     *
     * `com.jakewharton.mosaic.tty.Tty` is an internal Kotlin class, so it is reached by reflection:
     * the `tryBind()` static factory returns a `Tty?`, and `Tty` is [AutoCloseable].
     */
    private fun probeTty(): Boolean? = try {
        val ttyClass = Class.forName("com.jakewharton.mosaic.tty.Tty")
        // Prefer the @JvmStatic Tty.tryBind(); fall back to the Companion.tryBind() instance method.
        val handle = try {
            ttyClass.getMethod("tryBind").also { it.isAccessible = true }.invoke(null)
        } catch (_: NoSuchMethodException) {
            val companion = ttyClass.getField("Companion").get(null)
            companion.javaClass.getMethod("tryBind").also { it.isAccessible = true }.invoke(companion)
        }
        if (handle == null) {
            log.info("TTY probe: Tty.tryBind() returned null — no controlling terminal")
            false
        } else {
            val stdin = runCatching {
                ttyClass.getMethod("isStdinTty").invoke(handle) as? Boolean
            }.getOrNull()
            log.info("TTY probe: bound=true, stdin.isatty={}", stdin)
            runCatching { (handle as AutoCloseable).close() } // release for the real bind in withTerminal
            true
        }
    } catch (t: Throwable) {
        log.warn("Could not pre-probe TTY via Mosaic internals — proceeding optimistically: {}", t.message)
        null
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
        // 1) Pre-flight TTY probe FIRST, before ANY terminal mutation (no jansi, no redirect, no
        //    alt-screen yet), so if there's no tty we bail cleanly without leaving the terminal in
        //    a half-mutated state.
        if (!config.execution.skipTtyPrecheck) {
            when (probeTty()) {
                false -> {
                    System.err.println(
                        "[TUI] No TTY detected. stdin.isatty=false. Running under a pipe, IDE, " +
                            "or non-interactive shell? Set taxoadapt.execution.enable-tui=false " +
                            "to run headless."
                    )
                    return@runBlocking
                }
                null -> log.warn("TTY pre-probe unavailable — proceeding optimistically")
                true -> log.info("TTY pre-probe OK")
            }
        }

        // 2) PR #58 working order: redirect streams BEFORE jansi. This is the ordering that worked
        //    on Windows / JDK 23; PR #59's jansi-first reorder is what broke TUI rendering there.
        log.info("TUI bootstrap: redirecting std streams (PR #58 working order)")
        redirectStdStreams()

        // 3) Install jansi so it can enable ANSI processing.
        log.info("TUI bootstrap: installing jansi (enableTui={})", config.execution.enableTui)
        AnsiConsole.systemInstall()
        log.info("TUI bootstrap: jansi systemInstall complete")

        // 4) Re-wrap System.out with explicit UTF-8 — load-bearing on Windows where the default
        //    console charset is not UTF-8 and would mangle the Mosaic frame bytes.
        System.setOut(java.io.PrintStream(System.out, true, "UTF-8"))

        // 5) Enter the alt-screen.
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
            log.info("Starting Mosaic TUI session")
            val started = runWithTerminal(NonInteractivePolicy.Exit, block)
            log.info("Mosaic TUI session ended (started={})", started)
        } catch (e: Throwable) {
            // Capture the real stderr BEFORE restoreTerminal() nulls originalErr, so the diagnostic
            // below lands on the user's terminal rather than the redirected log sink.
            val savedErr = originalErr
            restoreTerminal()
            val real = if (e is InvocationTargetException) e.cause ?: e else e
            val sink = savedErr ?: System.err
            val nonInteractive = real.message?.contains("non-interactive", ignoreCase = true) == true
            if (nonInteractive) {
                log.warn("Mosaic refused to run interactively: {}", real.message)
                sink.println("\n[TUI] Mosaic could not enter interactive mode: ${real.message}")
                sink.println(
                    "      No usable TTY (pipe / IDE / non-interactive shell). " +
                        "Set taxoadapt.execution.enable-tui=false to run headless."
                )
            } else {
                log.warn("Mosaic TUI failed to start/render: {}", real.message)
                sink.println("\n[TUI RECOVERY] Layout failure.")
                sink.println("Cause: ${real.message ?: "Unknown failure"}")
                real.printStackTrace(sink)
            }
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