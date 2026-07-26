package taxonomy.diagnostics

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.File
import java.nio.file.Files

/**
 * Guards the diagnostics bundle.
 *
 * The point of this test is that the bundle cannot silently rot: every file it promises must
 * exist, be non-empty, and parse. A bundle that quietly stops writing is worse than no bundle,
 * because the absence is only discovered when the data is needed and the run is gone.
 */
class DiagnosticsBundleTest {

    private lateinit var tmp: File

    private fun open(): File {
        tmp = Files.createTempDirectory("diag-bundle-test").toFile()
        val cfg = File(tmp, "run.toml").apply { writeText("seed = 42\nmodels = [\"a\"]\n") }
        DiagnosticsBundle.open(tmp, cfg)
        return tmp
    }

    @AfterEach
    fun tearDown() {
        if (DiagnosticsBundle.isOpen()) DiagnosticsBundle.close("test-teardown")
        if (::tmp.isInitialized) tmp.deleteRecursively()
    }

    private fun bundle() = File(tmp, "diagnostics")

    @Test
    fun `open creates the promised files with headers`() {
        open()
        assertTrue(bundle().isDirectory, "diagnostics/ must exist")
        listOf("run_manifest.json", "iteration_metrics.csv", "proposals.csv").forEach {
            val f = File(bundle(), it)
            assertTrue(f.isFile, "$it must exist")
            assertTrue(f.length() > 0, "$it must be non-empty")
        }
        assertTrue(File(bundle(), "proposals.csv").readText().startsWith("iter,type,site_id"))
    }

    @Test
    fun `manifest records provenance and is patched at close`() {
        open()
        DiagnosticsBundle.recordCorpus(
            seed = 42, splitSeed = null, corpusSize = 791, trainSize = 554, testSize = 237,
            domains = listOf("History", "Computer science"), reservedPoolId = "pabc",
            embeddingModel = "qwen3", judgeModel = "Mistral-Large-3"
        )
        DiagnosticsBundle.close("completed")
        val m = File(bundle(), "run_manifest.json").readText()
        listOf("\"commit\"", "\"branch\"", "\"dirty\"", "\"config_sha256\"",
               "\"corpus_size\": 791", "\"reserved_pool_id\": \"pabc\"",
               "\"exit_reason\": \"completed\"", "\"duration_ms\"").forEach {
            assertTrue(m.contains(it), "manifest must contain $it — was:\n$m")
        }
    }

    @Test
    fun `the config file is copied verbatim so the bundle is self-contained`() {
        open()
        DiagnosticsBundle.close("completed")
        val copied = File(bundle(), "config.toml")
        assertTrue(copied.isFile, "config must be copied, not symlinked — symlinks break on tar")
        assertTrue(copied.readText().contains("seed = 42"))
    }

    @Test
    fun `floats never use a comma decimal separator`() {
        // The JVM here runs -Duser.country=FR, so a bare format() emits `0,024714`, which shifts
        // every following CSV column. This has cost real analysis time on this project.
        val prev = java.util.Locale.getDefault()
        try {
            java.util.Locale.setDefault(java.util.Locale.FRANCE)
            open()
            DiagnosticsBundle.recordProposal(
                iter = 3, type = "GROW", siteId = "n1", siteLabel = "Math",
                dJ = 0.024714, seDJ = 5.85e-5, z = 1.234, dV = 2,
                decision = "ACCEPTED", reason = null, nSite = 340
            )
            DiagnosticsBundle.recordIteration(
                iter = 3, nodes = 10, leaves = 6, maxDepth = 3,
                jAfterRoute = 0.229418, jAfterEdits = 0.229418,
                trickleDelta = 4.44e-16, editsDelta = 0.0, gedAdd = 2, gedRem = 0,
                attempted = 5, accepted = 2, rejected = 3, noProposal = 0,
                mass = 553.0, wallMs = 884
            )
            DiagnosticsBundle.close("completed")
            val p = File(bundle(), "proposals.csv").readText()
            val i = File(bundle(), "iteration_metrics.csv").readText()
            // The values must appear with '.' separators...
            assertTrue(p.contains("0.024714"), "dJ must use a dot separator — was:\n$p")
            assertTrue(i.contains("0.229418"), "J must use a dot separator — was:\n$i")
            // ...and every field must parse as a number under Locale.US, which is the property
            // that actually matters. A comma decimal would split one field into two.
            val header = p.lines().first().split(",").size
            p.lines().drop(1).filter { it.isNotBlank() }.forEach { row ->
                assertEquals(header, row.split(",").size,
                    "row has the wrong column count, i.e. a stray comma: $row")
            }
            i.lines().drop(1).filter { it.isNotBlank() }.forEach { row ->
                val cells = row.split(",")
                assertEquals(i.lines().first().split(",").size, cells.size,
                    "iteration row column count wrong: $row")
                cells.drop(1).forEach { c ->
                    assertTrue(c.isBlank() || c.toDoubleOrNull() != null,
                        "cell '$c' does not parse as a number in row: $row")
                }
            }
        } finally {
            java.util.Locale.setDefault(prev)
        }
    }

    @Test
    fun `proposal rows carry the binding value in the reason, and group by site`() {
        open()
        DiagnosticsBundle.recordProposal(
            iter = 1, type = "GROW", siteId = "n7", siteLabel = "Computer science",
            dJ = null, seDJ = null, z = null, dV = null, decision = "NO_PROPOSAL",
            reason = "not_routing_sustainable(min_child=48,floor=60,k=2)", nSite = 291
        )
        DiagnosticsBundle.recordProposal(
            iter = 2, type = "GROW", siteId = "n7", siteLabel = "Computer science",
            dJ = null, seDJ = null, z = null, dV = null, decision = "NO_PROPOSAL",
            reason = "not_routing_sustainable(min_child=48,floor=60,k=2)", nSite = 291
        )
        DiagnosticsBundle.close("completed")
        val rows = File(bundle(), "proposals.csv").readLines().drop(1).filter { it.isNotBlank() }
        assertEquals(2, rows.size)
        // The reason contains commas, so it must be quoted or the columns shift.
        assertTrue(rows.all { it.contains("\"not_routing_sustainable(min_child=48,floor=60,k=2)\"") },
            "a reason containing commas must be CSV-quoted — was: ${rows.first()}")
        // Deduplication by unique node is a group-by on site_id, which is the whole point.
        assertEquals(1, rows.map { it.split(",")[2] }.distinct().size)
    }

    @Test
    fun `an unwired producer leaves a header-only file and the manifest says so`() {
        // The failure mode that looks like success: iteration_metrics.csv shipped in the first
        // real bundle with a valid header, a clean parse and no rows, because its hook was never
        // wired. Nothing surfaced until the data was wanted and the run was gone.
        open()
        DiagnosticsBundle.recordProposal(
            iter = 1, type = "GROW", siteId = "n1", siteLabel = "x",
            dJ = 0.1, seDJ = null, z = null, dV = 1, decision = "ACCEPTED", reason = null, nSite = 5
        )
        // ...but nothing is ever recorded to iteration_metrics.
        DiagnosticsBundle.close("completed")
        val m = File(bundle(), "run_manifest.json").readText()
        assertTrue(m.contains("\"iteration_metrics_rows\": 0"),
            "manifest must record that the file got no rows — was:\n$m")
        assertTrue(m.contains("\"proposals_rows\": 1"),
            "and must record the file that did — was:\n$m")
    }

    @Test
    fun `writes after close are ignored rather than throwing`() {
        open()
        DiagnosticsBundle.close("completed")
        // Diagnostics must never be able to kill a run, including on a lifecycle mistake.
        DiagnosticsBundle.recordProposal(
            iter = 9, type = "GROW", siteId = "x", siteLabel = null,
            dJ = 1.0, seDJ = null, z = null, dV = 1, decision = "ACCEPTED", reason = null, nSite = 1
        )
        DiagnosticsBundle.recordIteration(
            iter = 9, nodes = 1, leaves = 1, maxDepth = 0, jAfterRoute = 0.0, jAfterEdits = 0.0,
            trickleDelta = 0.0, editsDelta = 0.0, gedAdd = 0, gedRem = 0,
            attempted = 0, accepted = 0, rejected = 0, noProposal = 0, mass = 0.0, wallMs = 0
        )
        assertFalse(DiagnosticsBundle.isOpen())
    }

    @Test
    fun `open on an unwritable location does not throw`() {
        // A full disk or a read-only mount must degrade to a warning, not take down a
        // 40-minute run at minute 39.
        val f = Files.createTempFile("not-a-dir", ".txt").toFile()
        DiagnosticsBundle.open(f, null, "resolved")   // parent is a FILE, not a directory
        DiagnosticsBundle.close("completed")
        f.delete()
    }
}
