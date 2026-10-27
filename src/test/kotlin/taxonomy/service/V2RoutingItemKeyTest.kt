package taxonomy.service

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.dataset.SplitSide
import taxonomy.tui.service.LeafDomainProfile
import java.io.File

/**
 * RP12 B3, the item key of the union readout. INERTNESS: with itemKey = false the extracted header and rows equal, byte for
 * byte, the inline strings of HeadlessBenchmarkRunner.exportUnionRouting at base 32c4c72 (copied VERBATIM below as
 * [baseRow]); the runner source no longer holds the inline strings and calls the helper at every write site, so the tested
 * helper is what runs. With the flag the rows gain exactly one trailing item_id column.
 */
class V2RoutingItemKeyTest {

    // ---- base 32c4c72, verbatim (HeadlessBenchmarkRunner.escapeCsv and the two perQuery.write strings) ----
    private fun escapeCsv(value: Any?): String {
        val s = value?.toString() ?: ""
        if (s.contains(",") || s.contains("\"") || s.contains("\n") || s.contains("\r")) {
            return "\"" + s.replace("\"", "\"\"") + "\""
        }
        return s
    }
    private val baseHeader = "true_key,true_source,rule,leaf_id,leaf_label,leaf_depth,leaf_dominant,leaf_purity,routed_source,routed_domain,top1,source_ok,domain_ok\n"
    private fun baseUnrouted(domainKey: String, trueSource: String, ruleKey: String, routedSource: String?, sourceOk: Boolean) =
        "${escapeCsv(domainKey)},${escapeCsv(trueSource)},${ruleKey},,,,,,${escapeCsv(routedSource ?: "")},,0,${if (sourceOk) 1 else 0},0\n"
    private fun baseRow(domainKey: String, trueSource: String, ruleKey: String, id: String, label: String?, depth: Int, dominant: String?,
                        purity: Double?, routedSource: String?, routedDomain: String?, top1Ok: Boolean, sourceOk: Boolean, domainOk: Boolean) =
        "${escapeCsv(domainKey)},${escapeCsv(trueSource)},${ruleKey},${escapeCsv(id)},${escapeCsv(label)},${depth}," +
            "${escapeCsv(dominant ?: "")},${purity?.let { "%.4f".format(java.util.Locale.US, it) } ?: ""}," +
            "${escapeCsv(routedSource ?: "")},${escapeCsv(routedDomain ?: "")},${if (top1Ok) 1 else 0},${if (sourceOk) 1 else 0},${if (domainOk) 1 else 0}\n"
    // -------------------------------------------------------------------------------------------------------------------

    private val text = "What is the capital, of \"France\"?"

    @Test
    fun `flag off - header and rows equal the base inline strings byte for byte`() {
        assertEquals(baseHeader, UnionRoutingExport.header(false))
        for ((rs, ok) in listOf<Pair<String?, Boolean>>(null to false, "BBH" to true, "MATH, x" to false)) {
            assertEquals(baseUnrouted("BBH/boolean_expressions", "BBH", "flatLeaf", rs, ok),
                UnionRoutingExport.row("BBH/boolean_expressions", "BBH", "flatLeaf", null, null, null, null, null, rs, null, false, ok, false, text, false))
        }
        for (purity in listOf(null, 0.72545, 1.0)) for (flags in listOf(Triple(true, true, true), Triple(false, true, false), Triple(false, false, false))) {
            val (t1, so, dok) = flags
            assertEquals(
                baseRow("MMLU_PRO_LB/law", "MMLU_PRO_LB", "descent", "MMLU_PRO_LB:n00000268", "Emergent \"Concept\", #253", 4, "MMLU_PRO_LB/law",
                    purity, "MMLU_PRO_LB", null, t1, so, dok),
                UnionRoutingExport.row("MMLU_PRO_LB/law", "MMLU_PRO_LB", "descent", "MMLU_PRO_LB:n00000268", "Emergent \"Concept\", #253", 4,
                    "MMLU_PRO_LB/law", purity, "MMLU_PRO_LB", null, t1, so, dok, text, false))
        }
    }

    @Test
    fun `flag on - one trailing item_id column, the v2 item id of the routed text`() {
        assertEquals(baseHeader.trimEnd('\n') + ",item_id\n", UnionRoutingExport.header(true))
        val item = "i:" + SplitSide.stemKey(text)
        assertEquals(item, UnionRoutingExport.itemId("  WHAT is the capital,   of \"France\"? "))
        val on = UnionRoutingExport.row("BBH/x", "BBH", "flatLeaf", "BBH:n1", "L", 3, "BBH/x", 0.5, "BBH", "BBH/x", true, true, true, text, true)
        val off = UnionRoutingExport.row("BBH/x", "BBH", "flatLeaf", "BBH:n1", "L", 3, "BBH/x", 0.5, "BBH", "BBH/x", true, true, true, text, false)
        assertEquals(off.trimEnd('\n') + ",$item\n", on)
        val un = UnionRoutingExport.row("BBH/x", "BBH", "flatLeaf", null, null, null, null, null, null, null, false, false, false, text, true)
        assertTrue(un.endsWith(",0,0,0,$item\n"), un)
    }

    @Test
    fun `leaf table lists every leaf, a leaf without profile has empty profile columns`() {
        val prof = mapOf("a" to LeafDomainProfile("a", "A", 3, 12, "BBH/x", 0.75, mapOf("BBH/x" to 9, "BBH/y" to 3)))
        assertEquals(
            "leaf_id,leaf_label,leaf_depth,profile_size,leaf_dominant,leaf_purity\n" +
                "a,A,3,12,BBH/x,0.7500\n" +
                "b,\"B, two\",4,0,,\n",
            UnionRoutingExport.leavesCsv(listOf(Triple("a", "A", 3), Triple("b", "B, two", 4)), prof))
    }

    @Test
    fun `KA2 - the TRAIN texts routed by the flag-on export are exactly the unreserved rows`() {
        val q = { id: Int, t: String -> taxonomy.dataset.MMLUQuery(id, t, "BBH/x", "BBH") }
        val full = linkedMapOf("BBH/x" to listOf(q(1000001, "e"), q(1000002, "g"), q(1000003, "t1")), "MATH/y" to listOf(q(2000001, "t2")))
        assertEquals(listOf("BBH/x" to "t1", "MATH/y" to "t2"),
            UnionRoutingExport.trainQueries(full, mapOf("BBH/x" to listOf(1000001, 1000002))))
        assertEquals(4, UnionRoutingExport.trainQueries(full, emptyMap()).size)
    }

    @Test
    fun `KA3 - the graft loads the v2 pool, activates it with the TOML and the allow-list, and stamps the snapshot`() {
        // assembleUnion is Spring-bound and runs only in the staged C-2 build; this scan pins its v2 wiring (READY_rp12_et KA3)
        val src = File("src/main/kotlin/taxonomy/runner/HeadlessBenchmarkRunner.kt").readText().replace("\r\n", "\n")
        assertEquals(1, Regex("val v2Union = cliConfig\\.v2PoolFile\\?\\.let \\{ taxonomy\\.dataset\\.V2EnginePool\\.load\\(File\\(it\\)\\) \\}").findAll(src).count())
        assertTrue(src.contains("val v2UnionStamp = v2Union?.let { p ->\n            val (lines, st) = p.activateUnion("))
        assertTrue(src.contains("unionPool, currentSeed, configFile,\n                taxonomy.dataset.V2ForeignMembers.parseForeign(cliConfig.v2ForeignMembers))"))
        assertTrue(src.contains("expectedPoolId = expectedPoolId, buildStamp = v2UnionStamp)"))
        assertTrue(src.contains("check(v2Union.poolId == cliConfig.pool)"), "a v2 graft pins the declared pool to the v2 pool id")
        assertTrue(src.contains("val assembled = assembleUnion(cliConfig, currentSeed, File(configPath))"))
        assertTrue(src.contains("val trainQueries = taxonomy.service.UnionRoutingExport.trainQueries(fullByDomain, reservedByDomain)"))
    }

    @Test
    fun `the runner writes every query row through the helper (no inline copy left)`() {
        val src = File("src/main/kotlin/taxonomy/runner/HeadlessBenchmarkRunner.kt").readText()
        assertFalse(src.contains("perQuery.write(\"true_key,true_source,rule"), "the inline header is gone")
        assertFalse(src.contains("perQuery.write(\"\${escapeCsv(domainKey)}"), "the inline rows are gone")
        assertEquals(1, Regex("perQuery\\.write\\(taxonomy\\.service\\.UnionRoutingExport\\.header\\(itemKey\\)\\)").findAll(src).count())
        assertEquals(2, Regex("perQuery\\.write\\(taxonomy\\.service\\.UnionRoutingExport\\.row\\(").findAll(src).count())
        // both query-row writes pass the flag through (itemKey), never a literal true
        assertEquals(2, Regex("routedSource, routedDomain, top1Ok, sourceOk, domainOk, text, itemKey\\)\\)|routedSource, null, false, sourceOk, false, text, itemKey\\)\\)").findAll(src).count())
    }
}
