package taxonomy.runner

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import java.io.File

/**
 * Every committed experiment config must parse with zero unknown keys.
 *
 * Unknown TOML keys used to fail open (console-only warning): the frozen
 * freeze_mcs55.toml asserted `tau = 1e-6` for weeks while the parser ignored the
 * key and the run used the coincidentally-equal code default, and 40 configs set
 * `enableFinalMetrics` to no effect (construction-audit risk #3, fixed 2026-09-07
 * by making unknown keys fatal). This test keeps the registration record honest:
 * a committed config can never assert a value the run ignores.
 */
@SpringBootTest(
    classes = [taxonomy.TaxoAdaptApplication::class],
    properties = [
        "taxoadapt.execution.enable-tui=false",
        "taxoadapt.execution.run-batch=false",
        "taxoadapt.execution.start-service=false",
        "taxoadapt.llm.judge-model=qwen3.6:27b",
        "taxoadapt.llm.labeling-model=gemma4:e4b"
    ]
)
class ConfigParsesTest {

    @Autowired
    lateinit var runner: HeadlessBenchmarkRunner

    @Test
    fun `every committed config parses with no unknown keys`() {
        val root = File("experiment_configs")
        assertTrue(root.isDirectory, "experiment_configs not found; run from the repo root")
        val configs = root.walkTopDown().filter { it.isFile && it.extension == "toml" }.toList()
        assertTrue(configs.size > 30, "expected the full config corpus, found ${configs.size}")
        val failures = mutableListOf<String>()
        for (f in configs) {
            try {
                runner.parseToml(f.readText())
            } catch (e: Exception) {
                failures.add("${f.path}: ${e.message}")
            }
        }
        assertTrue(failures.isEmpty(),
            "configs with unknown/unparseable keys:\n" + failures.joinToString("\n"))
    }
}
