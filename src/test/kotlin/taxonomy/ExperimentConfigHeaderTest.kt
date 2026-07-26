package taxonomy

import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.File

/**
 * Guards experiment-config provenance.
 *
 * Configs are routinely derived from one another by copying and editing a few keys, and three
 * times now the narrative header has been carried over unchanged while the body changed:
 * bar025.toml kept the treefix header, cal_seeds_bar025.toml's header was inherited by the
 * zgate arms, and those arms describe a five-seed baseline run that they are not. Attribution
 * in this project rests almost entirely on being able to read a config and know what produced
 * a result directory, so a stale header is not cosmetic.
 *
 * The check is deliberately narrow: if a header comment names an outputDir path, it must be
 * the outputDir the file actually sets. Headers that describe intent without quoting a path
 * are left alone.
 */
class ExperimentConfigHeaderTest {

    private val configRoot = File("experiment_configs")

    private fun tomls(): List<File> =
        if (!configRoot.exists()) emptyList()
        else configRoot.walkTopDown().filter { it.isFile && it.extension == "toml" }.toList()

    @Test
    fun `header self-declaration matches the outputDir the config sets`() {
        // Only a DECLARED self-reference is checked: a header line of the form
        //   #  outputDir: experiment_results/foo
        // Headers routinely cite other runs as references or comparisons, and those citations
        // are legitimate, so a bare mention of some experiment_results path is not drift.
        val declared = Regex("""^\s*#\s*outputDir:\s*(\S+)""")
        val failures = mutableListOf<String>()

        for (f in tomls()) {
            val lines = f.readLines()
            val actual = lines
                .firstOrNull { it.trimStart().startsWith("outputDir") }
                ?.substringAfter('=')?.trim()?.trim('"')
                ?: continue

            val header = lines.takeWhile { it.isBlank() || it.trimStart().startsWith("#") }
            val claim = header.firstNotNullOfOrNull { declared.find(it)?.groupValues?.get(1) } ?: continue
            if (claim.trimEnd('/').trim('"') != actual.trimEnd('/')) {
                failures += "${f.name}: header declares outputDir $claim but the config sets $actual"
            }
        }

        assertTrue(failures.isEmpty(), "Stale config headers:\n" + failures.joinToString("\n"))
    }

    @Test
    fun `every config declares an outputDir`() {
        val missing = tomls().filter { f ->
            f.readLines().none { it.trimStart().startsWith("outputDir") }
        }.map { it.name }
        assertTrue(missing.isEmpty(), "Configs without an outputDir: $missing")
    }
}
