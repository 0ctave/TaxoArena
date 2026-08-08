package taxonomy.runner

import org.slf4j.LoggerFactory
import java.io.File
import java.util.concurrent.TimeUnit

/**
 * Refuses to start a run whose ratings database is tracked by git.
 *
 * WHY (2026-08-08). `TaxonomyRankingService` resolves its database from `-Dranking.db.path`,
 * defaulting to `ratings.db` in the working directory. A run launched without that flag
 * therefore writes to the repository's own file, and for as long as `ratings.db` was tracked,
 * a routine arena run silently modified a committed 8 MB binary. That happened during the
 * cross-domain trial: the run was killed and the file restored from HEAD, but nothing in the
 * system objected while it was happening.
 *
 * `ratings.db` is untracked now, so the default path is safe again. This guard exists so the
 * hazard cannot return by another route — someone re-adding the file, or aiming
 * `ranking.db.path` at one of the settled result databases under `experiment_results`. Same
 * reasoning as `EvalIngestValidator.enforceNamedExclusions`: the failure mode is silent, so it
 * has to be an enforcement point rather than a note in a document.
 *
 * A standalone object rather than a method on the runner, because the runner is a Spring
 * component with a dozen injected collaborators and a guard should be checkable without any
 * of them.
 */
object RatingsDbGuard {

    private val log = LoggerFactory.getLogger("taxonomy.RatingsDbGuard")

    /** The database this process would write to, honouring the override. */
    fun resolvedPath(): String = System.getProperty("ranking.db.path", "ratings.db")

    /**
     * True if git tracks [path], false if it does not, null if git could not answer — outside a
     * checkout, or with no git on PATH. Null means "unknown", and the caller proceeds: refusing
     * to run outside a git checkout would be worse than the risk it guards against.
     */
    fun isTracked(path: String): Boolean? = try {
        val pb = ProcessBuilder("git", "ls-files", "--error-unmatch", "--", File(path).path)
        pb.redirectErrorStream(true)
        val proc = pb.start()
        val out = proc.inputStream.bufferedReader().readText()
        if (!proc.waitFor(10, TimeUnit.SECONDS)) {
            proc.destroyForcibly()
            null
        } else if (proc.exitValue() == 0) {
            true
        } else if (out.contains("not a git repository", ignoreCase = true)) {
            null
        } else {
            false
        }
    } catch (e: Exception) {
        log.warn("[DB-GUARD] could not ask git whether '$path' is tracked (${e.message})")
        null
    }

    /** Throws when the resolved ratings database is tracked. */
    fun assertNotTracked() {
        val path = resolvedPath()
        when (isTracked(path)) {
            null -> log.warn("[DB-GUARD] git unavailable; cannot verify that '$path' is untracked")
            true -> error(
                "[DB-GUARD] refusing to start: the ratings database '$path' is TRACKED BY GIT, " +
                    "so this run would modify a committed artefact in place. Point the run at a " +
                    "throwaway database instead:\n" +
                    "  ./gradlew bootRun -Dranking.db.path=experiment_results/<run>/ratings_<run>.db " +
                    "--args=\"--config <config>\"\n" +
                    "If you genuinely mean to rewrite a tracked record, untrack it first " +
                    "(git rm --cached) and decide deliberately what replaces it."
            )
            false -> log.info("[DB-GUARD] ratings database '$path' is not tracked; safe to write")
        }
    }
}
