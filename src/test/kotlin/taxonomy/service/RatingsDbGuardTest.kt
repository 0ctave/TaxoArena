package taxonomy.service

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Test
import taxonomy.runner.RatingsDbGuard
import java.io.File
import java.util.concurrent.TimeUnit

/**
 * The runner must refuse to write a ratings database that git tracks.
 *
 * WHAT THIS PINS. `TaxonomyRankingService` defaults its database to `ratings.db` in the working
 * directory, so a run launched without `-Dranking.db.path` writes to the repository's own file.
 * While `ratings.db` was tracked, that meant a routine arena run modified a committed 8 MB
 * binary and nothing objected — observed on 2026-08-08, killed and restored from HEAD. The file
 * is untracked now; this test is what stops the hazard returning by another route, such as
 * someone pointing the property at one of the settled `experiment_results/r8` records.
 */
class RatingsDbGuardTest {

    private fun withProperty(value: String?, block: () -> Unit) {
        val key = "ranking.db.path"
        val previous = System.getProperty(key)
        try {
            if (value == null) System.clearProperty(key) else System.setProperty(key, value)
            block()
        } finally {
            if (previous == null) System.clearProperty(key) else System.setProperty(key, previous)
        }
    }

    /**
     * True when the working directory is the root of a git checkout (`.git` present: a directory in a
     * clone, a file in a worktree) and a git executable says it is inside a work tree. Probed here,
     * independently of [RatingsDbGuard.isTracked], so a defect in the guard's own "git could not
     * answer" branch cannot turn the refusal check below into a skip on a git checkout.
     */
    private fun gitCheckoutPresent(): Boolean {
        if (!File(".git").exists()) return false
        return try {
            val proc = ProcessBuilder("git", "rev-parse", "--is-inside-work-tree").redirectErrorStream(true).start()
            val out = proc.inputStream.bufferedReader().readText()
            if (!proc.waitFor(10, TimeUnit.SECONDS)) {
                proc.destroyForcibly()
                false
            } else {
                proc.exitValue() == 0 && out.trim() == "true"
            }
        } catch (e: Exception) {
            false
        }
    }

    @Test
    fun `a tracked database is refused`() {
        // "Tracked" needs git metadata. A copy without it (GitHub's "Download ZIP", a git-archive export)
        // tracks nothing, and the guard then proceeds by design (isTracked == null). Skipped, not passed, in
        // that case; on a git checkout the refusal below is asserted unchanged.
        assumeTrue(
            gitCheckoutPresent(),
            "SKIPPED (git metadata absent): no .git in the working directory, or git cannot answer; " +
                "the refusal of a tracked database is checked only on a git checkout."
        )
        // Any file certain to be tracked; the guard's question is "does git know this path",
        // not "is it a database".
        withProperty("build.gradle.kts") {
            val error = assertThrows(IllegalStateException::class.java) {
                RatingsDbGuard.assertNotTracked()
            }
            assertTrue(
                error.message!!.contains("TRACKED BY GIT"),
                "the message must say why it refused: ${error.message}"
            )
            assertTrue(
                error.message!!.contains("ranking.db.path"),
                "and must name the flag that fixes it: ${error.message}"
            )
        }
    }

    @Test
    fun `an untracked path is allowed`() {
        withProperty("experiment_results/scratch/ratings_scratch.db") {
            assertDoesNotThrow { RatingsDbGuard.assertNotTracked() }
        }
    }

    @Test
    fun `the default path is allowed now that ratings db is untracked`() {
        // Fails if anyone re-adds /ratings.db to the index, which is the regression this
        // whole guard exists to make loud.
        withProperty(null) {
            assertDoesNotThrow { RatingsDbGuard.assertNotTracked() }
        }
    }
}
