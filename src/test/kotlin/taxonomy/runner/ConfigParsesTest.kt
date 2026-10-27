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

    /**
     * `matchFilter` is optional, defaults to the historical scheduler, and refuses typos.
     *
     * An unknown VALUE has to be as fatal as an unknown KEY: `matchFilter = "disagreement"`
     * that quietly ran the "none" arm would leave a registration record asserting a rule the
     * run never applied — the same failure that made unknown keys fatal in the first place.
     */
    @Test
    fun `matchFilter defaults to none, parses answerDisagreement, and rejects typos`() {
        val base = "datasetType = \"MMLU_PRO\"\nseed = 137\n"
        assertEquals("none", runner.parseToml(base).matchFilter)
        assertEquals("none", runner.parseToml(base + "matchFilter = \"none\"\n").matchFilter)
        assertEquals(
            "answerDisagreement",
            runner.parseToml(base + "matchFilter = \"answerDisagreement\"\n").matchFilter
        )
        assertThrows(Exception::class.java) { runner.parseToml(base + "matchFilter = \"disagreement\"\n") }
    }

    /**
     * H9-REM: the construction-order shuffle seed is absent by default (null = the production
     * order), parses a long, and fails closed on a non-integer value and on a mis-spelled key.
     */
    @Test
    fun `constructionOrderShuffleSeed is absent by default, parses a long, and refuses a non-integer and a mis-spelled key`() {
        val base = "datasetType = \"MMLU_PRO\"\nseed = 137\nrunPipeline = true\n"
        assertNull(runner.parseToml(base).constructionOrderShuffleSeed)
        assertEquals(7L, runner.parseToml(base + "constructionOrderShuffleSeed = 7\n").constructionOrderShuffleSeed)
        assertThrows(Exception::class.java) { runner.parseToml(base + "constructionOrderShuffleSeed = \"abc\"\n") }
        assertThrows(Exception::class.java) { runner.parseToml(base + "constructionOrderShuffle = true\n") }
    }

    /**
     * H9-REM: the shuffle is applied by the construction loop only. A config that declares it on
     * a run that constructs nothing (runPipeline absent/false, or a union graft) would leave a
     * registration asserting an order the run never applied, so it is refused at parse time.
     */
    @Test
    fun `constructionOrderShuffleSeed without runPipeline is refused`() {
        val base = "datasetType = \"MMLU_PRO\"\nseed = 137\n"
        fun refused(toml: String) {
            val e = assertThrows(IllegalArgumentException::class.java) { runner.parseToml(toml) }
            assertTrue(e.message!!.contains("constructionOrderShuffleSeed"), "refusal must name the key: ${e.message}")
        }
        refused(base + "constructionOrderShuffleSeed = 1\n")
        refused(base + "runPipeline = false\nconstructionOrderShuffleSeed = 1\n")
        assertEquals(1L, runner.parseToml(base + "runPipeline = true\nconstructionOrderShuffleSeed = 1\n").constructionOrderShuffleSeed)
        // A union graft parses on its own (the union guards are satisfied) and is refused only
        // once the shuffle key is added.
        val union = "corpora = [\"MATH\"]\ncorpusDbPath = \"x.db\"\nseed = 137\nrunPipeline = false\nunionSnapshots = [\"x\"]\n"
        assertNull(runner.parseToml(union).constructionOrderShuffleSeed)
        refused(union + "constructionOrderShuffleSeed = 1\n")
    }

    /**
     * ANCHOR-FREE: absent = false (the anchored production bootstrap); the two literals parse;
     * anything else is fatal at parse time with the key named. `String.toBoolean()` would map
     * a typo to false and run the anchored path under a config asserting the anchor-free one.
     */
    @Test
    fun `anchorFree is false by default, parses true and false, and refuses a non-boolean and a mis-spelled key`() {
        val base = "datasetType = \"MMLU_PRO\"\nseed = 42\nrunPipeline = true\n"
        assertFalse(runner.parseToml(base).anchorFree)
        assertTrue(runner.parseToml(base + "anchorFree = true\n").anchorFree)
        assertFalse(runner.parseToml(base + "anchorFree = false\n").anchorFree)
        for (bad in listOf("ture", "1", "\"true\"", "yes", "True")) {
            val e = assertThrows(Exception::class.java) { runner.parseToml(base + "anchorFree = $bad\n") }
            assertTrue(e.message!!.contains("anchorFree"), "refusal must name the key for '$bad': ${e.message}")
        }
        assertThrows(Exception::class.java) { runner.parseToml(base + "anchorfree = true\n") }
        assertThrows(Exception::class.java) { runner.parseToml(base + "anchor_free = true\n") }
    }

    /**
     * ANCHOR-FREE: the flag is applied by the construction bootstrap only, and a hold-out
     * presupposes anchors. A config that declares it without runPipeline, on a union graft, or
     * together with excludeFromAnchoring is refused at parse time (init block, shared with the
     * JSON decoder), so a registration can never assert an anchor-free build the run never made.
     */
    @Test
    fun `anchorFree is refused with excludeFromAnchoring, without runPipeline, and with unionSnapshots`() {
        val base = "datasetType = \"MMLU_PRO\"\nseed = 42\n"
        fun refused(toml: String) {
            val e = assertThrows(IllegalArgumentException::class.java) { runner.parseToml(toml) }
            assertTrue(e.message!!.contains("anchorFree"), "refusal must name the key: ${e.message}")
        }
        refused(base + "anchorFree = true\n")
        refused(base + "runPipeline = false\nanchorFree = true\n")
        refused(base + "runPipeline = true\nexcludeFromAnchoring = [\"Law\"]\nanchorFree = true\n")
        assertTrue(runner.parseToml(base + "runPipeline = true\nanchorFree = true\n").anchorFree)
        // anchorFree = false is the default and contradicts nothing.
        assertFalse(runner.parseToml(base + "runPipeline = true\nexcludeFromAnchoring = [\"Law\"]\nanchorFree = false\n").anchorFree)
        val union = "corpora = [\"MATH\"]\ncorpusDbPath = \"x.db\"\nseed = 42\nrunPipeline = false\nunionSnapshots = [\"x\"]\n"
        assertFalse(runner.parseToml(union).anchorFree)
        refused(union + "anchorFree = true\n")
    }

    /**
     * K-SELECTION (registered 2026-09-19): `proposalAcceptMultiplier` is absent by default (null =
     * the class default 1.0 = the production creation gate), parses the registered 1.05 and the
     * two edges of its range, and fails closed with the key named on 0.9, 2.5, a non-number ("abc",
     * quoted or not, a boolean), a mis-spelled key, and on a run that constructs nothing.
     */
    @Test
    fun `proposalAcceptMultiplier is absent by default, parses 1_05, and refuses 0_9, 2_5, abc, a mis-spelled key and a non-constructing run`() {
        val base = "datasetType = \"MMLU_PRO\"\nseed = 42\nrunPipeline = true\n"
        assertNull(runner.parseToml(base).proposalAcceptMultiplier)
        assertEquals(1.05, runner.parseToml(base + "proposalAcceptMultiplier = 1.05\n").proposalAcceptMultiplier!!, 0.0)
        assertEquals(1.0, runner.parseToml(base + "proposalAcceptMultiplier = 1.0\n").proposalAcceptMultiplier!!, 0.0)
        assertEquals(2.0, runner.parseToml(base + "proposalAcceptMultiplier = 2.0\n").proposalAcceptMultiplier!!, 0.0)
        fun refused(toml: String) {
            val e = assertThrows(IllegalArgumentException::class.java) { runner.parseToml(toml) }
            assertTrue(e.message!!.contains("proposalAcceptMultiplier"), "refusal must name the key: ${e.message}")
        }
        refused(base + "proposalAcceptMultiplier = 0.9\n")
        refused(base + "proposalAcceptMultiplier = 2.5\n")
        refused(base + "proposalAcceptMultiplier = 0\n")
        refused(base + "proposalAcceptMultiplier = -1.05\n")
        refused(base + "proposalAcceptMultiplier = abc\n")
        refused(base + "proposalAcceptMultiplier = \"abc\"\n")
        refused(base + "proposalAcceptMultiplier = \"1.05\"\n")
        refused(base + "proposalAcceptMultiplier = true\n")
        refused(base + "proposalAcceptMultiplier = NaN\n")
        // A mis-spelled key hits the unknown-key throw (fatal, any exception type).
        assertThrows(Exception::class.java) { runner.parseToml(base + "proposalAcceptMultipler = 1.05\n") }
        assertThrows(Exception::class.java) { runner.parseToml(base + "proposal_accept_multiplier = 1.05\n") }
        // Applied by the construction loop only: refused without runPipeline and on a union graft.
        val noBuild = "datasetType = \"MMLU_PRO\"\nseed = 42\n"
        refused(noBuild + "proposalAcceptMultiplier = 1.05\n")
        refused(noBuild + "runPipeline = false\nproposalAcceptMultiplier = 1.05\n")
        val union = "corpora = [\"MATH\"]\ncorpusDbPath = \"x.db\"\nseed = 42\nrunPipeline = false\nunionSnapshots = [\"x\"]\n"
        assertNull(runner.parseToml(union).proposalAcceptMultiplier)
        refused(union + "proposalAcceptMultiplier = 1.05\n")
    }

    /**
     * K-SELECTION: the four registered arm configs differ from their REDRAW bases by exactly the
     * one added key line (the three primed arms) or by nothing but outputDir (the I2 inertness
     * arm), on the parsed record, so a registration can never assert a treatment the file does
     * not carry (the --dry-run rule of the registration, checked here at zero cost).
     */
    @Test
    fun `K-SELECTION arm configs differ from their redraw bases by the one key only`() {
        val dir = File("experiment_configs/anchorfree/redraw/kselect")
        assertTrue(dir.isDirectory, "K-SELECTION configs not found at $dir")
        fun parsed(path: String) = runner.parseToml(File(path).readText())
        for (arm in listOf("af_clean_s42", "af_s137", "af_s2048")) {
            val base = parsed("experiment_configs/anchorfree/redraw/$arm.toml")
            val primed = parsed("$dir/${arm}_k105.toml")
            assertNull(base.proposalAcceptMultiplier, "$arm base must not carry the key")
            assertEquals(1.05, primed.proposalAcceptMultiplier!!, 0.0, "$arm primed arm carries 1.05")
            assertEquals(
                base.copy(outputDir = primed.outputDir, proposalAcceptMultiplier = 1.05), primed,
                "$arm: the primed arm must equal its base plus the key (and its own outputDir)"
            )
            assertTrue(primed.outputDir.contains("kselect"), "$arm: own outputDir under kselect: ${primed.outputDir}")
            assertTrue(primed.anchorFree && primed.runPipeline && primed.enableLabeling == false && !primed.judgeInduction, "$arm: label-free anchor-free build")
        }
        val base = parsed("experiment_configs/anchorfree/redraw/af_clean_s42.toml")
        val inert = parsed("$dir/af_clean_s42_inert.toml")
        assertNull(inert.proposalAcceptMultiplier, "I2 carries no key (the inertness build)")
        assertEquals(base.copy(outputDir = inert.outputDir), inert, "I2 must equal its base but for outputDir")
        assertEquals("experiment_results/anchorfree/redraw/kselect/i2", inert.outputDir)
    }

    /**
     * PERF-8: the exact proposal memo is fail-closed at the config boundary. Absent = off;
     * the three literals parse; anything else is fatal at parse time, with the key named, so
     * a typo can never run as a silent off (or a silent on).
     */
    @Test
    fun `proposalMemo defaults to off, parses shadow and on, and rejects typos`() {
        assertNull(runner.parseToml("seed = 42\n").proposalMemo, "absent must mean the code default (off)")
        assertEquals("off", runner.parseToml("proposalMemo = \"off\"\n").proposalMemo)
        assertEquals("shadow", runner.parseToml("proposalMemo = \"shadow\"\n").proposalMemo)
        assertEquals("on", runner.parseToml("proposalMemo = \"on\"\n").proposalMemo)
        assertEquals("on", runner.parseToml("proposalMemo = 'ON'\n").proposalMemo)
        val e = assertThrows(IllegalArgumentException::class.java) {
            runner.parseToml("proposalMemo = \"onn\"\n")
        }
        assertTrue(e.message!!.contains("proposalMemo"), "the error must name the key — was: ${e.message}")
        assertThrows(IllegalArgumentException::class.java) { runner.parseToml("proposalMemo = true\n") }
        // No committed config carries the key EXCEPT the registered PERF-8 replay arms
        // (experiment_configs/perf8/{shadow,on}_s42.toml, 2026-09-16: the two-config replay that
        // closed item #8 negative). The corpus test above already proves every config still parses,
        // and the code default stays off for all of them.
        val carriers = File("experiment_configs").walkTopDown()
            .filter { it.isFile && it.extension == "toml" && it.readText().contains("proposalMemo") }
            .filterNot { it.parentFile.name == "perf8" }.toList()
        assertTrue(carriers.isEmpty(), "no committed config outside experiment_configs/perf8 may enable the memo: $carriers")
    }
}
