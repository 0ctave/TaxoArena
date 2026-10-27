package taxonomy.service

import taxonomy.dataset.SplitSide
import taxonomy.tui.service.LeafDomainProfile

/**
 * The per-query rows of the union routing readout (MAIN_union_routing_queries.csv), extracted from
 * HeadlessBenchmarkRunner.exportUnionRouting so they are testable byte for byte, plus RP12 B3's item key.
 *
 * RP12 ARCH-V2-E-T B3 (the TOML key `unionRoutingItemKey = true`): G11's D_fd, G13's D13 and G14's tree cells pair per ITEM,
 * and the readout carried no item key (its rows are shuffled by the seed). With the flag the query CSV gains ONE trailing
 * column `item_id` = "i:" + [SplitSide.stemKey] of the routed text (the v2 side export's item id), and two files are added:
 * MAIN_union_routing_train_queries.csv (every TRAIN text of the loaded corpora routed by the same rule, same columns) and
 * MAIN_union_routing_leaves.csv (every leaf: id, label, depth, profile size, TRAIN-majority domain, purity). Without the
 * flag every row and the header are the pre-RP12 bytes ([header] / [row] with itemKey = false reproduce the former inline
 * strings; V2RoutingItemKeyTest compares them with the base text verbatim).
 */
object UnionRoutingExport {
    const val BASE_HEADER = "true_key,true_source,rule,leaf_id,leaf_label,leaf_depth,leaf_dominant,leaf_purity,routed_source,routed_domain,top1,source_ok,domain_ok"
    const val ITEM_COLUMN = "item_id"
    const val TRAIN_FILE = "MAIN_union_routing_train_queries.csv"
    const val LEAVES_FILE = "MAIN_union_routing_leaves.csv"

    fun itemId(text: String): String = "i:" + SplitSide.stemKey(text)

    /**
     * The TRAIN texts the flag-on export routes (READY_rp12_et KA2: extracted so the filter is executed by a test): every loaded
     * row whose id is not reserved (a v2 build reserves EVAL + GATE + their sentinels), as (domain key, text), in load order.
     */
    fun trainQueries(fullByDomain: Map<String, List<taxonomy.dataset.MMLUQuery>>, reservedByDomain: Map<String, List<Int>>): List<Pair<String, String>> {
        val reserved = reservedByDomain.values.flatten().toHashSet()
        return fullByDomain.flatMap { (domain, qs) -> qs.filter { it.id !in reserved }.map { domain to it.text } }
    }

    fun escapeCsv(value: Any?): String {
        val s = value?.toString() ?: ""
        if (s.contains(",") || s.contains("\"") || s.contains("\n") || s.contains("\r")) {
            return "\"" + s.replace("\"", "\"\"") + "\""
        }
        return s
    }

    fun header(itemKey: Boolean): String = if (itemKey) "$BASE_HEADER,$ITEM_COLUMN\n" else "$BASE_HEADER\n"

    /** One routed row; [leafId] null = unrouted (the former `continue` branch). [text] feeds the item key only. */
    fun row(
        domainKey: String, trueSource: String, ruleKey: String,
        leafId: String?, leafLabel: String?, leafDepth: Int?, dominant: String?, purity: Double?,
        routedSource: String?, routedDomain: String?, top1Ok: Boolean, sourceOk: Boolean, domainOk: Boolean,
        text: String, itemKey: Boolean
    ): String {
        val base = if (leafId == null) {
            "${escapeCsv(domainKey)},${escapeCsv(trueSource)},$ruleKey,,,,,,${escapeCsv(routedSource ?: "")},,0,${if (sourceOk) 1 else 0},0"
        } else {
            "${escapeCsv(domainKey)},${escapeCsv(trueSource)},$ruleKey,${escapeCsv(leafId)},${escapeCsv(leafLabel)},$leafDepth," +
                "${escapeCsv(dominant ?: "")},${purity?.let { "%.4f".format(java.util.Locale.US, it) } ?: ""}," +
                "${escapeCsv(routedSource ?: "")},${escapeCsv(routedDomain ?: "")},${if (top1Ok) 1 else 0},${if (sourceOk) 1 else 0},${if (domainOk) 1 else 0}"
        }
        return if (itemKey) "$base,${itemId(text)}\n" else "$base\n"
    }

    /** MAIN_union_routing_leaves.csv (flag only): every leaf in [leafIds] order, its profile or empty profile columns. */
    fun leavesCsv(leaves: List<Triple<String, String?, Int>>, profiles: Map<String, LeafDomainProfile>): String {
        val sb = StringBuilder("leaf_id,leaf_label,leaf_depth,profile_size,leaf_dominant,leaf_purity\n")
        for ((id, label, depth) in leaves) {
            val p = profiles[id]
            sb.append("${escapeCsv(id)},${escapeCsv(label)},$depth,${p?.size ?: 0},${escapeCsv(p?.dominantDomain ?: "")}," +
                "${p?.purity?.let { "%.4f".format(java.util.Locale.US, it) } ?: ""}\n")
        }
        return sb.toString()
    }
}
