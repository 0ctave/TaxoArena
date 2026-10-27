package taxonomy.runner

import java.util.Locale

/**
 * THREAD-CAP (registered 2026-09-27, docs/judge_v2_program.md section "THREAD-CAP", plan R-F, RP07).
 *
 * The cap itself is applied by Gradle, not here: `-PjvmThreads=N` (a positive integer <= 24,
 * anything else REFUSES at configuration time, before any fork) adds `-XX:ActiveProcessorCount=N`
 * and `-D[PROPERTY]=N` to the forked siteNull / bootRun JVMs (build.gradle.kts, `applyThreadCap`).
 * With the property absent Gradle adds nothing, so every recorded path forks exactly as before.
 *
 * This object only SPEAKS (rule 11): every forked run prints one line, pass or fail, naming what
 * was requested and what the JVM actually sees. `Runtime.availableProcessors()` is the value
 * Dispatchers.Default and ForkJoinPool.commonPool size themselves from, so `availableProcessors`
 * on this line is the execution witness of the cap. `requested` is read from the forwarded
 * system property (the configured object), never from a global the code may have mutated.
 */
object ThreadCap {
    /** System property Gradle forwards alongside -XX:ActiveProcessorCount (absent = no cap requested). */
    const val PROPERTY = "taxoarena.jvmThreads"

    /** The raw forwarded value, or null when no cap was requested. */
    fun requested(): String? = System.getProperty(PROPERTY)

    /**
     * `[THREAD-CAP] requested=<N|none> availableProcessors=<live> heapEstimate=<GB|n/a> budget=<GB>`.
     * [heapEstimateBytes] is the caller's own heap model (siteNull's peak live-set estimate); a path
     * without a heap model (bootRun) passes null and the line reads `heapEstimate=n/a`.
     * [budgetBytes] is the caller's heap budget (siteNull: 0.90 * maxMemory; bootRun: maxMemory).
     */
    fun line(heapEstimateBytes: Long?, budgetBytes: Long): String =
        "[THREAD-CAP] requested=%s availableProcessors=%d heapEstimate=%s budget=%.2fGB".format(
            Locale.US,
            requested() ?: "none",
            Runtime.getRuntime().availableProcessors(),
            heapEstimateBytes?.let { "%.2fGB".format(Locale.US, it / 1e9) } ?: "n/a",
            budgetBytes / 1e9,
        )
}
