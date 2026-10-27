package taxonomy

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Test
import taxonomy.runner.ThreadCap
import java.lang.management.ManagementFactory
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ForkJoinPool
import java.util.concurrent.atomic.AtomicInteger

/**
 * THREAD-CAP (RP07) probe: the proof by execution on a SYNTHETIC fixture (no DB, no snapshot, no
 * network, no construction). Run by name only:
 *
 *   gradlew threadCapProbe     -PjvmThreads=12   (Test fork, the siteNull mechanism)
 *   gradlew threadCapProbeExec -PjvmThreads=12   (JavaExec fork, the bootRun mechanism)
 *   ... and with the property absent: requested=none, no -XX:ActiveProcessorCount in the fork.
 *
 * Prints the registered [THREAD-CAP] line, the fork's own JVM input arguments (so the absence of
 * the flag on the uncapped branch is shown, not assumed), ForkJoinPool.commonPool parallelism, and
 * the MEASURED peak concurrency of Dispatchers.Default under a fixture of 8 * cores blocking tasks
 * (each holds its worker 150 ms, so the peak equals the dispatcher's core pool size). With a cap
 * requested it FAILS unless availableProcessors == N and the measured Dispatchers.Default peak ==
 * max(2, N).
 */
fun threadCapProbeReport(): List<String> {
    val out = mutableListOf<String>()
    out += ThreadCap.line(null, Runtime.getRuntime().maxMemory())
    val inputArgs = ManagementFactory.getRuntimeMXBean().inputArguments
    val capArgs = inputArgs.filter { it.contains("ActiveProcessorCount") || it.contains(ThreadCap.PROPERTY) }
    out += "[THREAD-CAP-PROBE] jvm input args naming the cap: ${if (capArgs.isEmpty()) "none" else capArgs.joinToString(" ")}"
    val cores = Runtime.getRuntime().availableProcessors()
    out += "[THREAD-CAP-PROBE] ForkJoinPool.commonPool parallelism=${ForkJoinPool.commonPool().parallelism}"

    val active = AtomicInteger(0)
    val peak = AtomicInteger(0)
    val threads = ConcurrentHashMap.newKeySet<String>()
    val tasks = 8 * maxOf(2, cores)
    val t0 = System.nanoTime()
    runBlocking {
        (1..tasks).map {
            async(Dispatchers.Default) {
                val now = active.incrementAndGet()
                peak.accumulateAndGet(now) { a, b -> maxOf(a, b) }
                // A Test fork runs with -ea, which turns on coroutine debug mode and appends
                // " @coroutine#k" to the worker name; strip it so workers, not coroutines, are counted.
                threads += Thread.currentThread().name.substringBefore(" @")
                Thread.sleep(150)
                active.decrementAndGet()
            }
        }.awaitAll()
    }
    val wallMs = (System.nanoTime() - t0) / 1_000_000
    out += "[THREAD-CAP-PROBE] Dispatchers.Default fixture: tasks=$tasks peakConcurrent=${peak.get()} distinctWorkers=${threads.size} wallMs=$wallMs"

    val req = ThreadCap.requested()
    if (req != null) {
        val n = req.toInt()
        check(cores == n) { "[THREAD-CAP-PROBE] FAILED: requested=$n but availableProcessors=$cores" }
        check(peak.get() == maxOf(2, n)) {
            "[THREAD-CAP-PROBE] FAILED: requested=$n but Dispatchers.Default peak concurrency=${peak.get()}"
        }
        check(capArgs.contains("-XX:ActiveProcessorCount=$n")) {
            "[THREAD-CAP-PROBE] FAILED: requested=$n but the fork's input args carry no -XX:ActiveProcessorCount=$n"
        }
        out += "[THREAD-CAP-PROBE] PASS capped: availableProcessors=$cores == requested=$n; Dispatchers.Default peak=${peak.get()}"
    } else {
        check(capArgs.isEmpty()) { "[THREAD-CAP-PROBE] FAILED: no cap requested but the fork carries $capArgs" }
        out += "[THREAD-CAP-PROBE] PASS uncapped: requested=none, no cap argument in the fork, availableProcessors=$cores"
    }
    return out
}

/** JavaExec entry point (threadCapProbeExec, the bootRun mechanism). */
fun main() {
    threadCapProbeReport().forEach { println(it) }
}

/** Test-fork entry point (threadCapProbe, the siteNull mechanism). Excluded from `test`. */
class ThreadCapProbeHarness {
    @Test
    fun probe() {
        threadCapProbeReport().forEach { println(it) }
    }
}
