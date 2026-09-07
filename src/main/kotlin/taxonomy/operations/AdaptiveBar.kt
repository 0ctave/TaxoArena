package taxonomy.operations

import taxonomy.config.TaxonomyConfig
import taxonomy.model.GraphNode

/**
 * Per-anchor separation bar (H9 adaptive-bar exploration, 2026-09-07).
 *
 * The within-node null band varies by anchor (p95 0.029-0.075 on the frozen
 * artifact — docs/data/within_null_frozen_anchors.csv), so a single global bar is
 * either permissive everywhere or collapses the tree. When
 * `formalism.adaptiveBars` is non-empty, the bar for any construction decision is
 * the entry for the node's depth-1 ancestor label, falling back to the global
 * `proposalSeparationBar` for unknown anchors.
 *
 * The SAME resolved bar must gate creation (splitter min-pair gate, coarsening,
 * residual-viability check) and destruction (sibling fusion, redundant fusion):
 * the create/destroy gate-consistency argument that prevents the historical
 * period-2 limit cycle only holds if both sides read one number.
 */
fun barFor(config: TaxonomyConfig, node: GraphNode?): Double {
    val bars = config.formalism.adaptiveBars
    if (bars.isEmpty() || node == null) return config.formalism.proposalSeparationBar
    var n: GraphNode = node
    val seen = HashSet<String>()
    while (n.depth > 1) {
        val p = n.parents.firstOrNull() ?: break
        if (!seen.add(p.id)) break
        n = p
    }
    return if (n.depth == 1) bars[n.label] ?: config.formalism.proposalSeparationBar
    else config.formalism.proposalSeparationBar
}
