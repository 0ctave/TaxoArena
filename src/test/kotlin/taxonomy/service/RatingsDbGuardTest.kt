package taxonomy.service

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import taxonomy.runner.RatingsDbGuard

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

    @Test
    fun `a tracked database is refused`() {
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
