package taxonomy.dataset

import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.File

/**
 * Keeps the per-row side flag from creeping back (FRAMEWORK item 18): no tracked source under
 * src/main, src/test, tools/analysis, tools/ingest, tools/figures, report/Figures, scripts or tools/chains may mention the legacy
 * column, the legacy pointer table, the deleted sync, or `--activate`, except on comment lines
 * that call them legacy, and in the one fixture test that mirrors the column to prove bit-identity
 * of the read cut-over.
 */
class NoIsReservedInSourceTest {

    private val tokens = listOf("is_reserved", "active_reserved_pool", "syncReservedPool", "--activate", "activateReservedPool", "activeReservedPoolId")

    private val allowlistedFiles = setOf(
        "src/test/kotlin/taxonomy/dataset/ModelEvalStorePoolQueryTest.kt",   // the legacy-column fixture
        "src/test/kotlin/taxonomy/dataset/NoIsReservedInSourceTest.kt",      // this file names the tokens
        "src/test/kotlin/taxonomy/dataset/ReservedPoolTest.kt",              // asserts the pointer table is ABSENT
        "src/test/kotlin/taxonomy/dataset/ReservedPoolRecordTest.kt",        // asserts the column and table are ABSENT
        "tools/analysis/pool_guard.py"                                       // --diff-flag reads the legacy column once, as evidence
    )

    /**
     * Line-level allowlist (queue NOISRESERVED-TEST-ALLOWLIST; docs/judge_v2_program.md L18093, "KNOWN PRE-EXISTING RED ON
     * main"): the 7 recorded hits in tools/analysis/data_v2 since d98b247 (at 4b85aff: common.py L67, gates.py L867 and L932,
     * ingest.py L104, L141, L160 and L168). Not a data hazard: the upstream flag is carried only into the quarantined table
     * retired_legacy_flag, and common.guard_retired keeps it out of every v2 view. The files are NOT exempted: an entry is
     * (path, the exact trimmed line) and the EXACT number of such lines allowed in that file. A new token line anywhere, an
     * extra copy of an allowed line, or an entry whose count no longer matches (a stale exemption) fails the test.
     */
    private val allowlistedLines: Map<Pair<String, String>, Int> = mapOf(
        // the comment documenting the retirement and its two locks
        Pair("tools/analysis/data_v2/common.py",
            "# The retired upstream eval_results.is_reserved flag (the pre-v2 id-split marker). It lives ONLY in its own table of the") to 1,
        // --selftest fixtures: synthetic source DBs written with the upstream eval_results schema of record (no DB of record opened)
        Pair("tools/analysis/data_v2/gates.py",
            "is_correct INTEGER NOT NULL DEFAULT 0, is_reserved INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (question_id, model_name));") to 1,
        Pair("tools/analysis/data_v2/gates.py",
            "options_json TEXT, gt_answer TEXT, pred TEXT, model_output TEXT NOT NULL, is_correct INTEGER NOT NULL DEFAULT 0, is_reserved INTEGER NOT NULL DEFAULT 0,") to 1,
        // _mmlu_responses and _union_responses: the upstream flag is read ONLY to be written to retired_legacy_flag
        Pair("tools/analysis/data_v2/ingest.py",
            "\" is_correct, is_reserved FROM eval_results ORDER BY question_id, model_name\"):") to 2,
        // SPECS[...]["excluded_tables"]: the manifest names the legacy pointer table as NOT read
        Pair("tools/analysis/data_v2/ingest.py",
            "\"reserved_pool_meta\", \"active_reserved_pool\", \"corpus_registry\"],") to 1,
        Pair("tools/analysis/data_v2/ingest.py",
            "\"excluded_tables\": [\"reserved_pool\", \"reserved_pool_meta\", \"active_reserved_pool\", \"corpus_registry\",") to 1,
    )

    private data class Hit(val rel: String, val lineNo: Int, val token: String, val text: String) {
        override fun toString() = "$rel:$lineNo: $token: ${text.take(120)}"
    }

    private fun isComment(line: String): Boolean {
        val t = line.trimStart()
        return t.startsWith("//") || t.startsWith("*") || t.startsWith("/*") || t.startsWith("#")
    }

    private fun scan(dir: File, exts: Set<String>): List<Hit> {
        val hits = ArrayList<Hit>()
        dir.walkTopDown().filter { it.isFile && it.extension in exts }.forEach { f ->
            val rel = f.path.replace('\\', '/').removePrefix(File(".").canonicalPath.replace('\\', '/') + "/").let {
                if (it.startsWith("./")) it.substring(2) else it
            }
            if (rel in allowlistedFiles) return@forEach
            f.readLines().forEachIndexed { i, line ->
                val hit = tokens.firstOrNull { line.contains(it) } ?: return@forEachIndexed
                // Documentation that calls the thing legacy, or a comment saying it is gone / replaced /
                // absent, is not a reader or writer.
                val lower = line.lowercase()
                if (lower.contains("legacy")) return@forEachIndexed
                val documented = lower.contains("gone") || lower.contains("no longer") || lower.contains("replaces") ||
                    lower.contains("there was also") || lower.contains("nothing to activate") || lower.contains("fresh db has no")
                if (isComment(line) && documented) return@forEachIndexed
                hits.add(Hit(rel, i + 1, hit, line.trim()))
            }
        }
        return hits
    }

    @Test
    fun `no reader or writer of the legacy flag, pointer, sync or activation remains`() {
        val hits = scan(File("src/main"), setOf("kt")) +
            scan(File("src/test"), setOf("kt")) +
            scan(File("tools/analysis"), setOf("py")) +
            scan(File("tools/ingest"), setOf("py")) +
            scan(File("tools/figures"), setOf("py")) +
            scan(File("report/Figures"), setOf("py")) +
            scan(File("scripts"), setOf("py")) +
            scan(File("tools/chains"), setOf("ps1"))
        // A hit is exempt only if its (path, trimmed line) is allowlisted AND the file holds exactly the allowed number.
        val byKey = hits.groupBy { Pair(it.rel, it.text) }
        val unallowed = hits.filter { h -> byKey.getValue(Pair(h.rel, h.text)).size != allowlistedLines[Pair(h.rel, h.text)] }
        assertTrue(unallowed.isEmpty(), "legacy side-flag references:\n" + unallowed.joinToString("\n"))
        val stale = allowlistedLines.filter { (key, n) -> (byKey[key]?.size ?: 0) != n }
        assertTrue(stale.isEmpty(), "allowlisted lines whose count no longer matches (update the allowlist by record):\n" +
            stale.entries.joinToString("\n") { (k, n) -> "${k.first}: expected $n, found ${byKey[k]?.size ?: 0}: ${k.second.take(120)}" })
    }

    /**
     * The baseline generator withholds the pool the runner passes it and has no default pool: a run
     * that generated baselines against another run's split was the 2026-09-09 incident's shape.
     */
    @Test
    fun `runBaselines passes the run's own pool and the script has no default pool`() {
        val runner = File("src/main/kotlin/taxonomy/runner/HeadlessBenchmarkRunner.kt").readText()
        val invocations = Regex("""ProcessBuilder\("python",\s*"scripts/generate_baselines\.py"([^)]*)\)""").findAll(runner).toList()
        assertTrue(invocations.isNotEmpty(), "runner no longer invokes scripts/generate_baselines.py")
        invocations.forEach { m ->
            assertTrue(m.groupValues[1].contains("baselinePool"), "generate_baselines.py invoked without the run's pool: ${m.value}")
        }
        assertTrue(runner.contains("val baselinePool = ownPoolId"), "baselinePool must be the split's own recorded pool")
        val script = File("scripts/generate_baselines.py").readText()
        assertTrue(!Regex("""sys\.argv\[1\]\s+if\s+len\(sys\.argv\)\s*>\s*1\s+else""").containsMatchIn(script),
            "generate_baselines.py must not default the pool id")
        assertTrue(!script.contains("\"p2dca21ab5f4ef3ae\""), "generate_baselines.py must not hard-code a pool id")
        assertTrue(script.contains("sys.exit(2)") && script.contains("mandatory; no default pool"),
            "generate_baselines.py must refuse a call without a pool id")
        assertTrue(script.contains("pool_guard.assert_frozen_pool(conn_chk, pool_id)"),
            "a non-registry pool must be verified by its reserved_pool rows")
    }
}
