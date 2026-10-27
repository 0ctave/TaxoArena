package taxonomy

import java.io.File
import java.nio.file.Files
import java.util.concurrent.ConcurrentLinkedQueue

/**
 * TEMP-SPRAWL fix (2026-10-04). A temp dir for tests whose code under test keeps an SQLite connection open for the
 * JVM's life (TaxonomyRankingService, EmbeddingCache), so neither @TempDir nor an @AfterAll delete can remove it:
 * File.deleteOnExit() on a non-empty dir is a no-op, which is how ranking-service-test / tournament-sim-test /
 * bt-scheduler-test / judge-call-store-test / emb_explicit / intent_emb_run dirs piled up in the system temp.
 * Each dir is deleted best-effort by a shutdown hook; whatever an open handle still pins is removed by the Gradle
 * `test` task's finalizer (build.gradle.kts, cleanTestTmp), which runs after the test JVM has exited. The dir lives
 * under java.io.tmpdir, which build.gradle.kts points at E:/TaxoArena_tmp/gradle/<worktree>/test.
 */
object TestTmp {
    private val dirs = ConcurrentLinkedQueue<File>()

    init {
        Runtime.getRuntime().addShutdownHook(Thread { dirs.forEach { runCatching { it.deleteRecursively() } } })
    }

    fun dir(prefix: String): File = Files.createTempDirectory(prefix).toFile().also { dirs.add(it) }
}
