package taxonomy.diagnostics

import org.slf4j.LoggerFactory
import java.io.File
import java.security.MessageDigest
import java.util.Locale

/**
 * A self-contained `diagnostics/` directory per run: one folder, one `tar czf` to send.
 *
 * Everything here is a SECOND SINK on values the pipeline already computes for logging. It adds
 * no computation to the hot path and, critically, is never allowed to fail a run — a 40-minute
 * construction must not die because a CSV append hit a full disk. Every public entry point
 * swallows its exceptions to a warning.
 *
 * Writes are incremental and flushed at boundaries, for the same reason arena verdicts are: a
 * crash at 90% should leave 90% of the diagnostics rather than nothing.
 *
 * ## Locale
 *
 * All floats go through [fmt], which pins [Locale.US]. The JVM here runs with
 * `-Duser.country=FR`, so bare `"%.5f".format(x)` emits `0,24714` — a comma decimal separator
 * that silently breaks every downstream parser, and has repeatedly cost analysis time on this
 * project. The logs keep their existing behaviour; these files must not.
 */
object DiagnosticsBundle {

    private val log = LoggerFactory.getLogger("taxonomy.Diagnostics")

    @Volatile private var dir: File? = null
    @Volatile private var startedAtMillis: Long = 0L
    private val manifest = linkedMapOf<String, Any?>()
    private val lock = Any()

    /** Sources copied at [close]; symlinks would break the moment the folder is tarred or moved. */
    private val pendingCopies = mutableListOf<Pair<File, String>>()

    private var iterationWriter: java.io.Writer? = null
    private var proposalWriter: java.io.Writer? = null

    private var rankWriter: java.io.Writer? = null

    /** Row counts, so close() can tell "nothing happened" from "nobody wired the hook". */
    @Volatile private var iterationRows: Int = 0
    @Volatile private var proposalRows: Int = 0
    @Volatile private var rankRows: Int = 0

    /** Pinned to US so decimal separators are always '.', whatever the JVM locale is. */
    fun fmt(v: Double, decimals: Int = 6): String =
        if (v.isNaN()) "NaN" else if (v.isInfinite()) (if (v > 0) "Inf" else "-Inf")
        else String.format(Locale.US, "%.${decimals}f", v)

    fun isOpen(): Boolean = dir != null

    /** Directory for extra artifacts, or null when the bundle is closed. */
    fun subdir(name: String): File? = safely("subdir") {
        dir?.resolve(name)?.also { it.mkdirs() }
    }

    // ── lifecycle ───────────────────────────────────────────────────────────────

    fun open(outputDir: File, configPath: File?, resolvedConfigSummary: String? = null) {
        safely("open") {
            synchronized(lock) {
                val d = File(outputDir, "diagnostics").apply { mkdirs() }
                dir = d
                startedAtMillis = System.currentTimeMillis()
                manifest.clear()
                pendingCopies.clear()

                val git = gitInfo()
                manifest["schema_version"] = 1
                manifest["commit"] = git.commit
                manifest["branch"] = git.branch
                // "dirty" means TRACKED SOURCE differs from the commit, excluding the files that
                // are modified permanently by design. It is not "git status is non-empty".
                //
                // SPLIT, because one boolean could not distinguish "the splitter was edited
                // mid-run" from "a .tex file was edited", and fired identically for both. The
                // frozen artifact 20260727_042523 read dirty=true from 14 report/*.tex files and
                // one test file with NO production source dirty — technically correct and
                // practically useless, which is how a real warning gets discounted.
                //   dirty_src   -> anything under src/main. BLOCKS a freeze.
                //   dirty_other -> thesis text, tests, everything else. Noise.
                val srcDirty = git.dirtyFiles.filter { it.startsWith("src/main") }
                val otherDirty = git.dirtyFiles.filterNot { it.startsWith("src/main") }
                manifest["dirty"] = git.dirty            // retained for older readers
                manifest["dirty_src"] = srcDirty.isNotEmpty()
                manifest["dirty_src_files"] = srcDirty
                manifest["dirty_other"] = otherDirty.isNotEmpty()
                manifest["dirty_other_files"] = otherDirty
                manifest["dirty_files"] = git.dirtyFiles
                manifest["started_at_millis"] = startedAtMillis

                if (srcDirty.isNotEmpty()) {
                    // Loud on purpose: production source that could have changed the result is
                    // uncommitted. This is the case that invalidates an artifact.
                    log.warn(
                        "[DIAG] PRODUCTION SOURCE is UNCOMMITTED at run start (commit ${git.commit}," +
                            " ${srcDirty.size} file(s) under src/main: ${srcDirty.take(5).joinToString(", ")}" +
                            (if (srcDirty.size > 5) ", …" else "") +
                            "). This run is NOT reproducible from the repository alone."
                    )
                } else if (otherDirty.isNotEmpty()) {
                    // Deliberately info, not warn. Thesis text and test edits do not affect the
                    // artifact, and warning about them is what trained a reader to ignore the flag.
                    log.info(
                        "[DIAG] ${otherDirty.size} non-source file(s) uncommitted (tests/report/docs);" +
                            " src/main is clean, so this run IS reproducible from the repository."
                    )
                }

                if (configPath != null && configPath.isFile) {
                    manifest["config_source"] = "file"
                    manifest["config_path"] = configPath.absolutePath
                    manifest["config_sha256"] = sha256(configPath.readBytes())
                    pendingCopies += configPath to "config.toml"
                } else {
                    manifest["config_source"] = "resolved"
                    val text = resolvedConfigSummary ?: "<unavailable>"
                    manifest["config_sha256"] = sha256(text.toByteArray())
                    File(d, "config.resolved.txt").writeText(text)
                }
                writeManifest()

                iterationWriter = File(d, "iteration_metrics.csv").bufferedWriter().also {
                    it.write(
                        "iter,nodes,leaves,maxDepth,J_after_route,J_after_edits,trickleDelta," +
                            "editsDelta,ged_add,ged_rem,proposals_attempted,accepted,rejected," +
                            "no_proposal,mass,wall_ms\n"
                    )
                    it.flush()
                }
                proposalWriter = File(d, "proposals.csv").bufferedWriter().also {
                    it.write("iter,type,site_id,site_label,dJ,SE_dJ,z,dV,decision,reason,n_site\n")
                    it.flush()
                }
                // Per-round ranking history. node_bt_states is INSERT OR REPLACE on
                // (snapshot_id, node_id), so every round overwrote the last and only the final
                // fit survived — a stopping rule that fires on rank stability could then never
                // be audited after the fact, only watched live. This is the append-only record
                // that makes "why did it stop" answerable.
                rankWriter = File(d, "rank_history.csv").bufferedWriter().also {
                    it.write("round,scope,scope_label,comparisons,ranking,scores\n")
                    it.flush()
                }
                log.info("[DIAG] diagnostics bundle open at ${d.absolutePath}")
            }
        }
    }

    /** Facts known only once the corpus is loaded and split. */
    fun recordCorpus(
        seed: Long, splitSeed: Long?, corpusSize: Int, trainSize: Int, testSize: Int,
        domains: List<String>, reservedPoolId: String?, embeddingModel: String?, judgeModel: String?
    ) {
        safely("recordCorpus") {
            manifest["seed"] = seed
            manifest["split_seed"] = splitSeed
            manifest["corpus_size"] = corpusSize
            manifest["train_size"] = trainSize
            manifest["test_size"] = testSize
            manifest["domains"] = domains
            manifest["reserved_pool_id"] = reservedPoolId
            manifest["embedding_model"] = embeddingModel
            manifest["judge_model"] = judgeModel
            writeManifest()
        }
    }

    fun registerCopy(source: File, asName: String) {
        safely("registerCopy") { synchronized(lock) { pendingCopies += source to asName } }
    }

    fun close(exitReason: String) {
        safely("close") {
            synchronized(lock) {
                val d = dir ?: return@safely
                iterationWriter?.runCatching { flush(); close() }
                proposalWriter?.runCatching { flush(); close() }
                rankWriter?.runCatching { flush(); close() }
                iterationWriter = null
                proposalWriter = null
                rankWriter = null
                manifest["rank_history_rows"] = rankRows

                manifest["exit_reason"] = exitReason
                manifest["finished_at_millis"] = System.currentTimeMillis()
                manifest["duration_ms"] = System.currentTimeMillis() - startedAtMillis

                // A well-formed EMPTY file is the failure mode that looks like success: the
                // header is present, the parse succeeds, and the absence is only noticed when
                // the data is needed and the run is gone. iteration_metrics.csv shipped exactly
                // like that in the first bundle — header written at open(), hook never wired.
                // Assert every promised file actually received rows.
                for ((name, rows) in listOf(
                    "iteration_metrics.csv" to iterationRows,
                    "proposals.csv" to proposalRows
                )) {
                    val f = File(d, name)
                    val lines = runCatching { f.readLines().count { it.isNotBlank() } }.getOrDefault(0)
                    manifest["${name.substringBefore('.')}_rows"] = rows
                    if (rows == 0 && lines <= 1) {
                        log.error(
                            "[DIAG] $name contains ONLY a header — nothing was ever recorded to it." +
                                " The file parses and looks valid, so this will not surface later:" +
                                " its producer is not wired up."
                        )
                    }
                }
                writeManifest()

                // Copied last, and only now: the run log is held open by the appender for the
                // whole run, and the tail is exactly where convergence lives — copying it early
                // would truncate the part that matters.
                for ((src, name) in pendingCopies) {
                    runCatching {
                        if (src.isFile) src.copyTo(File(d, name), overwrite = true)
                        else log.debug("[DIAG] skipped absent copy source: ${src.absolutePath}")
                    }.onFailure { log.warn("[DIAG] copy of ${src.name} failed: ${it.message}") }
                }
                log.info("[DIAG] diagnostics bundle closed ($exitReason) at ${d.absolutePath}")
                dir = null
            }
        }
    }

    // ── per-iteration ───────────────────────────────────────────────────────────

    fun recordIteration(
        iter: Int, nodes: Int, leaves: Int, maxDepth: Int,
        jAfterRoute: Double, jAfterEdits: Double, trickleDelta: Double, editsDelta: Double,
        gedAdd: Int, gedRem: Int,
        attempted: Int, accepted: Int, rejected: Int, noProposal: Int,
        mass: Double, wallMs: Long
    ) {
        safely("recordIteration") {
            val w = iterationWriter ?: return@safely
            synchronized(lock) {
                w.write(
                    "$iter,$nodes,$leaves,$maxDepth,${fmt(jAfterRoute)},${fmt(jAfterEdits)}," +
                        "${fmt(trickleDelta, 12)},${fmt(editsDelta, 12)},$gedAdd,$gedRem," +
                        "$attempted,$accepted,$rejected,$noProposal,${fmt(mass, 3)},$wallMs\n"
                )
                iterationRows++

                w.flush()   // per-iteration flush: a crash keeps everything before it
            }
        }
    }

    // ── per-proposal ────────────────────────────────────────────────────────────

    /**
     * One row per proposal evaluation.
     *
     * [reason] should carry the VALUE, not just the category — `sep_below_bar(0.021)` rather than
     * `sep_below_bar` — because the whole point of this file is to make rejection tallies
     * analysable without re-reading logs. Deduplication by unique node is then
     * `GROUP BY site_id`, which the 379-vs-80 rejection count still needs.
     *
     * ── COMPATIBILITY BREAK in the `k=` field of splitter reasons ──────────────
     * Before commit 58f4aed, `min_pair_sep_below_bar(...,k=N)` and the matching
     * [NO-SPLIT] log line reported N = the EM mixture's k. They now report N =
     * `routedClusters.size`, the k that actually reached the gate, with EM's k
     * carried separately as `emK=`. The two differ whenever floor-absorption or
     * weak-pair coarsening reduced k — which is most rejections: min-pair is
     * reachable only at routed k=2, so old files showing "k=3" and "k=4" were
     * reporting a proposal that had already been coarsened to 2.
     *
     * Consequence: proposals.csv files written before and after 58f4aed are NOT
     * comparable on that column. Anything aggregating rejections by k across the
     * boundary must read `emK=` for old-style semantics, and treat a row with no
     * `emK=` as pre-break. `sep_below_bar(...)` no longer appears at all — the
     * joint k-way gate that emitted it was removed in the same commit.
     */
    fun recordProposal(
        iter: Int, type: String, siteId: String, siteLabel: String?,
        dJ: Double?, seDJ: Double?, z: Double?, dV: Int?,
        decision: String, reason: String?, nSite: Int?
    ) {
        safely("recordProposal") {
            val w = proposalWriter ?: return@safely
            synchronized(lock) {
                w.write(
                    "$iter,$type,${csv(siteId)},${csv(siteLabel ?: "")}," +
                        "${dJ?.let { fmt(it, 9) } ?: ""},${seDJ?.let { fmt(it, 9) } ?: ""}," +
                        "${z?.let { fmt(it, 4) } ?: ""},${dV ?: ""}," +
                        "$decision,${csv(reason ?: "")},${nSite ?: ""}\n"
                )
                proposalRows++
                w.flush()
            }
        }
    }

    /**
     * One row per (round, scope) with the ranking as it stood, models best-first.
     *
     * [scope] is a leaf id or "AGGREGATE". Scores are recorded alongside the order because a
     * rank-stability rule needs to distinguish a swap between near-tied models from a real
     * reordering, and the order alone cannot show that.
     */
    fun recordRanking(
        round: Int, scope: String, scopeLabel: String?,
        comparisons: Double, ranking: List<String>, scores: Map<String, Double>
    ) {
        safely("recordRanking") {
            val w = rankWriter ?: return@safely
            synchronized(lock) {
                w.write(
                    "$round,${csv(scope)},${csv(scopeLabel ?: "")}," +
                        "${fmt(comparisons, 1)},${csv(ranking.joinToString(">"))}," +
                        "${csv(ranking.joinToString(";") { fmt(scores[it] ?: 0.0, 4) })}\n"
                )
                rankRows++
                w.flush()
            }
        }
    }

    // ── internals ───────────────────────────────────────────────────────────────

    private data class Git(
        val commit: String, val branch: String,
        val dirty: Boolean, val dirtyFiles: List<String>
    )

    /**
     * Paths that are modified permanently and by design, so their presence says nothing about
     * whether a run is reproducible from the commit.
     *
     * `config/application.yml` is a local override holding credentials; it must never be
     * committed, and runs are driven by the TOML files under `experiment_configs` regardless.
     * Compiled Python caches are build output.
     *
     * (Avoid writing a glob with a slash-star in this file: Kotlin nests block comments, so it
     * opens a comment that never closes and the whole object stops resolving.)
     *
     * The first version of this check used bare `git status --porcelain`, which counts UNTRACKED
     * files too — so it fired on database backups and git worktrees and reported `dirty: true` on
     * a tree with no outstanding source work at all. A warning that always fires is worse than no
     * warning, because it teaches you to ignore it.
     */
    private val EXPECTED_LOCAL_MODIFICATIONS = listOf(
        "config/application.yml",
        ".pyc",
    )

    /** Resolved once per JVM; a git failure must never take a run down. */
    private val gitCached: Git by lazy {
        fun run(vararg cmd: String): String? = runCatching {
            val p = ProcessBuilder(*cmd).redirectErrorStream(true).start()
            val out = p.inputStream.bufferedReader().readText().trim()
            if (p.waitFor() == 0) out else null
        }.getOrNull()

        // `-uno`: tracked modifications only. Untracked files cannot have contributed to the
        // build, so they are irrelevant to whether this run is reproducible.
        val porcelain = run("git", "status", "--porcelain", "--untracked-files=no").orEmpty()
        // Porcelain v1 is "XY PATH". Slicing at a fixed offset went wrong by one and produced
        // "onfig/application.yml" — which then failed to match the exclusion list, so the flag
        // read dirty on a tree whose only modification was the by-design-local credentials file.
        // Trimming first and taking everything after the first space handles one- and two-letter
        // status codes alike.
        val modified = porcelain.lines()
            .filter { it.isNotBlank() }
            .map { it.trim().substringAfter(' ').trim() }
            .filter { it.isNotEmpty() }
            .filter { path -> EXPECTED_LOCAL_MODIFICATIONS.none { path.contains(it) } }

        Git(
            commit = run("git", "rev-parse", "HEAD") ?: "unknown",
            branch = run("git", "rev-parse", "--abbrev-ref", "HEAD") ?: "unknown",
            dirty = modified.isNotEmpty(),
            dirtyFiles = modified
        )
    }

    private fun gitInfo(): Git = gitCached

    private fun sha256(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes)
            .joinToString("") { "%02x".format(it) }

    private fun csv(s: String): String =
        if (s.any { it == ',' || it == '"' || it == '\n' || it == '\r' })
            "\"" + s.replace("\"", "\"\"").replace('\n', ' ').replace('\r', ' ') + "\""
        else s

    private fun jsonValue(v: Any?): String = when (v) {
        null -> "null"
        is Number, is Boolean -> v.toString()
        is List<*> -> v.joinToString(",", "[", "]") { jsonValue(it) }
        else -> "\"" + v.toString().replace("\\", "\\\\").replace("\"", "\\\"") + "\""
    }

    private fun writeManifest() {
        val d = dir ?: return
        val body = manifest.entries.joinToString(",\n  ") { "\"${it.key}\": ${jsonValue(it.value)}" }
        File(d, "run_manifest.json").writeText("{\n  $body\n}\n")
    }

    private inline fun <T> safely(what: String, block: () -> T): T? =
        try {
            block()
        } catch (t: Throwable) {
            log.warn("[DIAG] $what failed: ${t.message}")
            null
        }
}
