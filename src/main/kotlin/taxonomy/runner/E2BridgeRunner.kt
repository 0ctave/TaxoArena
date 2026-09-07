package taxonomy.runner

import kotlinx.coroutines.runBlocking
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.boot.CommandLineRunner
import org.springframework.core.annotation.Order
import org.springframework.stereotype.Component
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.projectTo
import taxonomy.operations.TaxonomyTrickler
import taxonomy.operations.TrickleOptions
import taxonomy.service.TaxonomySnapshotManager
import taxonomy.utils.StatisticsUtils
import java.io.File
import java.util.Random
import kotlin.math.exp
import kotlin.math.ln

/**
 * E2 bridge harness: does adding K structural bridges (a leaf reachable from a second
 * parent) at the E1 top-overlap pairs improve held-out routing fit over the frozen TREE,
 * against a depth-matched random-donor PLACEBO?
 *
 * Three conditions, SAME reserved questions, same frozen routing parameters
 * (taken from the snapshot's embedded EffectiveConfig):
 *
 *   T = frozen tree snapshot, as-is.
 *   B = T + K bridges. For each E1 pair (primary | secondary) the SECONDARY leaf gains a
 *       second parent: the lowest ancestor of the PRIMARY leaf that is not already a parent
 *       of the secondary (the primary's tree parent for distinct-parent pairs; lifted to the
 *       grandparent for same-parent within-anchor pairs, where the parent edge would be a
 *       no-op duplicate rather than a bridge).
 *   P = T + K placebo bridges: the SAME secondary leaves each gain a second parent, but the
 *       donor is drawn (seeded, Random(placeboSeed)) uniformly from internal nodes at the
 *       SAME DEPTH as that pair's B-donor whose anchor differs from both pair members'
 *       anchors, excluding B-donors and ancestors/parents of the secondary.
 *
 * MECHANISM. A bridge is an extra child edge: donor.children += leaf; leaf.parents += donor;
 * leaf.isBridge = true; then root.updateAllShrinkages(). This is routing-equivalent to the
 * removed crossLinkChildren machinery: the pre-removal trickler (aa3fa60) concatenated
 * children + crossLinkChildren into ONE list before scoring, and the current trickler's
 * topological DP already sums multi-path arrival mass via logSumExp — it only lost the
 * crossLinkChildren union when 334b95d deleted the operator. Attaching via children re-uses
 * the production DP unchanged instead of resurrecting the enableBridging flag.
 *
 * SCORING. Per question, the path-enumerating reference walk (equivalence oracle of the
 * production DP, exact on this graph size) yields RAW accumulated log path mass per reached
 * node. Candidates are reached leaves plus gate-stopped internal nodes (residual routing is
 * on at the frozen operating point). Reported per question:
 *   ll        = logSumExp over candidates of [log path mass + vMF log density at the node]
 *               — the held-out log-likelihood log sum_leaf P(path->leaf) * vMF_leaf(x_q),
 *               with residual mass scored at the node whose sub-structure rejected it.
 *   ll_leaves = same restricted to true leaves (blank when the walk residualised).
 *   top1      = production-mirror membership (normalize over candidates, share floor,
 *               maxAssignments cap) — for Top-1 agreement and NoMatch/residual rates.
 *
 * Run: --e2-config <json>. Exits the JVM when done (never falls through to the TUI).
 * Read-only with respect to the graph store: it loads the snapshot fresh per condition and
 * never saves one.
 */
@Serializable
data class E2PairSpec(val primary: String, val secondary: String)

@Serializable
data class E2Config(
    val snapshotId: String,
    val outputDir: String,
    val pairs: List<E2PairSpec>,
    val placeboSeed: Long = 999L,
    // 0 = all reserved questions; N > 0 = deterministic domain-round-robin subset of size N
    val limit: Int = 0
)

@Component
@Order(1)
class E2BridgeRunner(
    private val config: TaxonomyConfig,
    private val snapshotManager: TaxonomySnapshotManager,
    private val datasetFetcher: MMLUDatasetFetcher,
    private val embeddingCache: EmbeddingCache,
    private val trickler: TaxonomyTrickler
) : CommandLineRunner {

    private val log = LoggerFactory.getLogger("taxonomy.E2BridgeRunner")
    private val json = Json { prettyPrint = true; ignoreUnknownKeys = true }

    override fun run(vararg args: String?) {
        val idx = args.indexOf("--e2-config")
        if (idx == -1) return
        val path = args.getOrNull(idx + 1)
            ?: run { log.error("Missing path after --e2-config"); kotlin.system.exitProcess(1) }
        try {
            runE2(path!!)
            log.info("E2 bridge harness finished successfully.")
            kotlin.system.exitProcess(0)
        } catch (t: Throwable) {
            log.error("E2 bridge harness failed", t)
            kotlin.system.exitProcess(1)
        }
    }

    // ── graph helpers ────────────────────────────────────────────────────────────

    private fun allNodes(root: GraphNode): Map<String, GraphNode> {
        val map = LinkedHashMap<String, GraphNode>()
        fun walk(n: GraphNode) {
            if (map.putIfAbsent(n.id, n) != null) return
            n.children.forEach { walk(it) }
            n.crossLinkChildren.forEach { walk(it) }
        }
        walk(root)
        return map
    }

    /** Anchor (depth-1 ancestor) label per node, computed on the PRISTINE tree. */
    private fun anchorMap(root: GraphNode): Map<String, String> {
        val anchors = HashMap<String, String>()
        fun walk(n: GraphNode, anchor: String?) {
            val a = if (n.depth == 1) (n.label ?: n.id) else anchor
            if (a != null) anchors[n.id] = a
            n.children.forEach { walk(it, a) }
        }
        walk(root, null)
        return anchors
    }

    private fun ancestorIds(node: GraphNode): Set<String> {
        val out = mutableSetOf(node.id)
        fun up(n: GraphNode) {
            for (p in n.parents) if (out.add(p.id)) up(p)
        }
        up(node)
        return out
    }

    private fun resolveLeaf(prefix: String, leaves: List<GraphNode>): GraphNode {
        val exact = leaves.filter { it.label == prefix }
        if (exact.size == 1) return exact[0]
        val pre = leaves.filter { it.label?.startsWith(prefix) == true }
        require(pre.size == 1) {
            "Leaf label prefix '$prefix' resolves to ${pre.size} leaves: ${pre.map { it.label }}"
        }
        return pre[0]
    }

    private data class BridgeEdge(
        val pairRank: Int,
        val donor: GraphNode,
        val leaf: GraphNode,
        val primary: GraphNode,
        val lifted: Boolean
    )

    /** Donor for B: lowest ancestor of the primary that is not already a parent of the secondary. */
    private fun bDonor(primary: GraphNode, secondary: GraphNode): Pair<GraphNode, Boolean> {
        var d = primary.parents.singleOrNull()
            ?: error("Primary leaf '${primary.label}' has ${primary.parents.size} parents; expected exactly 1 in the frozen tree")
        var lifted = false
        while (secondary.parents.any { it.id == d.id }) {
            d = d.parents.singleOrNull()
                ?: error("Ran out of ancestors lifting donor for pair (${primary.label} | ${secondary.label})")
            lifted = true
            require(d.depth >= 1) { "Donor lifted to root for pair (${primary.label} | ${secondary.label})" }
        }
        return d to lifted
    }

    private fun attach(donor: GraphNode, leaf: GraphNode) {
        require(donor.children.none { it.id == leaf.id }) { "Edge ${donor.label} -> ${leaf.label} already exists" }
        donor.children.add(leaf)
        leaf.parents.add(donor)
        leaf.isBridge = true
    }

    // ── scoring ──────────────────────────────────────────────────────────────────

    private fun logSumExp(values: List<Double>): Double {
        if (values.isEmpty()) return Double.NaN
        val m = values.max()
        if (m == Double.NEGATIVE_INFINITY) return m
        return m + ln(values.sumOf { exp(it - m) })
    }

    private fun vmfLogDensity(n: GraphNode, emb: Embedding): Double {
        if (n.vmfMu.isEmpty()) return Double.NaN
        val x = emb.projectTo(n.vmfMu.size)
        return n.vmfKappa * StatisticsUtils.dotProduct(x, n.vmfMu) + n.vmfLogNormalizer
    }

    private data class QuestionScore(
        val nReached: Int,
        val nLeaves: Int,
        val nStopped: Int,
        val ll: Double,
        val llLeaves: Double,
        val top1Id: String,
        val top1Label: String,
        val top1IsLeaf: Boolean,
        val top1Share: Double,
        val noLeaf: Boolean,
        val reachedBridged: Boolean,
        val top1Bridged: Boolean
    )

    private fun scoreQuestion(
        emb: Embedding,
        root: GraphNode,
        nodeById: Map<String, GraphNode>,
        opts: TrickleOptions,
        bridgedLeafIds: Set<String>
    ): QuestionScore {
        val raw: Map<String, Double> = trickler.trickleByPathEnumeration(emb, root, opts)

        val reachedLeaves = HashMap<GraphNode, Double>()
        val stopped = HashMap<GraphNode, Double>()
        for ((id, mass) in raw) {
            val n = nodeById.getValue(id)
            if (n.isLeaf) {
                reachedLeaves[n] = mass
            } else if (n.children.none { raw.containsKey(it.id) }) {
                stopped[n] = mass
            }
        }

        // Candidate set mirrors production: leaves plus gate-stopped internal nodes
        // (enableResidualRouting is on at the frozen operating point). Root fallback if empty.
        val candidates = HashMap<GraphNode, Double>()
        candidates.putAll(reachedLeaves)
        candidates.putAll(stopped)
        if (candidates.isEmpty()) candidates[root] = 0.0

        val ll = logSumExp(candidates.mapNotNull { (n, mass) ->
            val d = vmfLogDensity(n, emb); if (d.isNaN()) null else mass + d
        })
        val llLeaves = logSumExp(reachedLeaves.mapNotNull { (n, mass) ->
            val d = vmfLogDensity(n, emb); if (d.isNaN()) null else mass + d
        })

        // Production-mirror membership: normalize over candidates, share floor, cap.
        val maxL = candidates.values.max()
        val logZ = maxL + ln(candidates.values.sumOf { exp(it - maxL) })
        val normalized = candidates.mapValues { (_, v) -> v - logZ }
        val logFloor = ln(config.formalism.membershipFloor.coerceAtLeast(1e-300))
        val admitted = normalized.filterValues { it >= logFloor }
            .ifEmpty { normalized.maxByOrNull { it.value }!!.let { mapOf(it.key to it.value) } }
        val kept = admitted.entries.sortedByDescending { it.value }.take(config.formalism.maxLeafAssignments)
        val top1 = kept.first()

        return QuestionScore(
            nReached = raw.size,
            nLeaves = reachedLeaves.size,
            nStopped = stopped.size,
            ll = ll,
            llLeaves = llLeaves,
            top1Id = top1.key.id,
            top1Label = top1.key.label ?: "",
            top1IsLeaf = top1.key.isLeaf,
            top1Share = exp(top1.value),
            noLeaf = kept.none { it.key.isLeaf },
            // "reached" here means ADMITTED to the final membership set (post floor + cap),
            // not merely touched by the beam walk — with beamGamma 0.2 the walk touches most
            // leaves with negligible mass, which would make a raw-touch flag uninformative.
            reachedBridged = kept.any { it.key.id in bridgedLeafIds },
            top1Bridged = top1.key.id in bridgedLeafIds
        )
    }

    // ── main ─────────────────────────────────────────────────────────────────────

    private fun runE2(configPath: String) = runBlocking {
        val e2 = json.decodeFromString<E2Config>(File(configPath).readText())
        require(e2.pairs.isNotEmpty()) { "E2 config has no bridge pairs" }
        log.info("E2 config: snapshot=${e2.snapshotId}, K=${e2.pairs.size}, placeboSeed=${e2.placeboSeed}, limit=${e2.limit}")

        // 1. Freeze routing parameters to the snapshot's own recorded config.
        val meta = snapshotManager.listSnapshots().find { it.id == e2.snapshotId }
            ?: error("Snapshot ${e2.snapshotId} not found in snapshots.db")
        val effective = meta.config
            ?: error("Snapshot ${e2.snapshotId} carries no embedded EffectiveConfig; refusing to guess routing parameters")
        config.applyEffectiveConfig(effective)
        log.info(
            "Applied snapshot config: dagMode=${config.formalism.dagMode}, membershipFloor=${config.formalism.membershipFloor}, " +
                "beamGamma=${config.formalism.routingBeamGamma}, descentMargin=${config.formalism.descentMargin}, " +
                "maxLeafAssignments=${config.formalism.maxLeafAssignments}, residualRouting=${config.formalism.enableResidualRouting}"
        )

        // 2. Dataset: id -> (text, domain). Also populates QuestionIdRegistry before graph load.
        config.dataset.selectedDomains = emptyList()
        val fullByDomain = datasetFetcher.fetchDataset(selectedDomains = emptyList())
        val idToText = HashMap<Int, String>()
        val idToDomain = HashMap<Int, String>()
        for ((domain, qs) in fullByDomain) for (q in qs) {
            idToText[q.id] = q.text; idToDomain[q.id] = domain
        }
        log.info("Dataset loaded: ${idToText.size} questions across ${fullByDomain.size} domains")

        // 3. Reserved pool from the snapshot row (identical to reserved_test_queries.json).
        val reservedByDomain = meta.reservedQueries
        require(reservedByDomain.isNotEmpty()) { "Snapshot carries no reserved pool" }
        val reservedAll = reservedByDomain
            .toSortedMap()
            .flatMap { (domain, ids) -> ids.sorted().mapNotNull { id -> idToText[id]?.let { Triple(id, domain, it) } } }
        val missingText = reservedByDomain.values.sumOf { it.size } - reservedAll.size
        log.info("Reserved pool: ${reservedAll.size} questions resolvable to text ($missingText unresolvable ids skipped)")

        // Deterministic domain-round-robin subset for smoke runs: every domain represented.
        val pool: List<Triple<Int, String, String>> = if (e2.limit > 0) {
            val byDomain = reservedAll.groupBy { it.second }.mapValues { it.value.sortedBy { t -> t.first } }
            val out = ArrayList<Triple<Int, String, String>>()
            var i = 0
            while (out.size < e2.limit) {
                var advanced = false
                for (domain in byDomain.keys.sorted()) {
                    val list = byDomain.getValue(domain)
                    if (i < list.size && out.size < e2.limit) { out.add(list[i]); advanced = true }
                }
                if (!advanced) break
                i++
            }
            out
        } else reservedAll
        log.info("Scoring pool: ${pool.size} reserved questions")

        // 4. Embeddings from cache ONLY — this harness must run without Ollama.
        val vectors = embeddingCache.getBatch(pool.map { it.third })
        val missing = pool.count { it.third !in vectors }
        require(missing == 0) {
            "$missing of ${pool.size} reserved questions have no cached embedding. " +
                "Refusing to fall back to live embedding (Ollama) — fix the cache copy instead."
        }
        log.info("All ${pool.size} question embeddings served from cache")

        val outDir = File(e2.outputDir)
        outDir.mkdirs()

        val opts = TrickleOptions(
            membershipFloor = config.formalism.membershipFloor,
            maxAssignments = config.formalism.maxLeafAssignments,
            readOnly = true
        )

        val manifest = LinkedHashMap<String, Any>()
        manifest["snapshotId"] = e2.snapshotId
        manifest["k"] = e2.pairs.size
        manifest["placeboSeed"] = e2.placeboSeed
        manifest["limit"] = e2.limit
        manifest["poolSize"] = pool.size
        manifest["membershipFloor"] = config.formalism.membershipFloor
        manifest["routingBeamGamma"] = config.formalism.routingBeamGamma
        manifest["descentMargin"] = config.formalism.descentMargin
        manifest["maxLeafAssignments"] = config.formalism.maxLeafAssignments

        for (condition in listOf("T", "B", "P")) {
            // Fresh load per condition: no cross-condition mutation can leak.
            val root = snapshotManager.loadSnapshot(e2.snapshotId)
                ?: error("Could not load snapshot ${e2.snapshotId}")
            val nodesBefore = allNodes(root)
            val anchors = anchorMap(root)
            val leaves = nodesBefore.values.filter { it.isLeaf }
            log.info("[$condition] Loaded snapshot: ${nodesBefore.size} nodes, ${leaves.size} leaves")

            // Resolve pairs and B-donors on THIS load's node objects.
            val resolved = e2.pairs.mapIndexed { i, p ->
                val primary = resolveLeaf(p.primary, leaves)
                val secondary = resolveLeaf(p.secondary, leaves)
                val (donor, lifted) = bDonor(primary, secondary)
                BridgeEdge(i + 1, donor, secondary, primary, lifted)
            }
            val bridgedLeafIds = resolved.map { it.leaf.id }.toSet()
            val bDonorIds = resolved.map { it.donor.id }.toSet()

            val edges: List<BridgeEdge> = when (condition) {
                "T" -> emptyList()
                "B" -> resolved
                "P" -> {
                    val rng = Random(e2.placeboSeed)
                    resolved.map { spec ->
                        val secondaryAncestors = ancestorIds(spec.leaf)
                        val candidates = nodesBefore.values
                            .filter { n ->
                                n.children.isNotEmpty() &&
                                    n.depth == spec.donor.depth &&
                                    n.id !in bDonorIds &&
                                    n.id !in secondaryAncestors &&
                                    spec.leaf.parents.none { it.id == n.id } &&
                                    anchors[n.id] != null &&
                                    anchors[n.id] != anchors[spec.primary.id] &&
                                    anchors[n.id] != anchors[spec.leaf.id]
                            }
                            .sortedBy { it.id }
                        require(candidates.isNotEmpty()) {
                            "No placebo donor candidates at depth ${spec.donor.depth} for pair ${spec.pairRank}"
                        }
                        val donor = candidates[rng.nextInt(candidates.size)]
                        spec.copy(donor = donor)
                    }
                }
                else -> error("unreachable")
            }

            if (edges.isNotEmpty()) {
                for (e in edges) attach(e.donor, e.leaf)
                root.updateAllShrinkages()
                File(outDir, "e2_bridges_$condition.csv").bufferedWriter().use { w ->
                    w.write("pair_rank,donor_id,donor_label,donor_depth,donor_anchor,leaf_id,leaf_label,leaf_anchor,primary_id,primary_label,lifted_past_shared_parent\n")
                    for (e in edges) {
                        w.write(
                            "${e.pairRank},${e.donor.id},${csv(e.donor.label)},${e.donor.depth},${csv(anchors[e.donor.id])}," +
                                "${e.leaf.id},${csv(e.leaf.label)},${csv(anchors[e.leaf.id])}," +
                                "${e.primary.id},${csv(e.primary.label)},${e.lifted}\n"
                        )
                    }
                }
                log.info("[$condition] Attached ${edges.size} bridge edges:")
                for (e in edges) {
                    log.info("[$condition]   #${e.pairRank} ${e.donor.label} (d${e.donor.depth}, ${anchors[e.donor.id]}) -> ${e.leaf.label} (${anchors[e.leaf.id]})${if (e.lifted) " [lifted]" else ""}")
                }
            }

            val nodeById = allNodes(root) // includes bridge edges (same node set, more edges)
            val csvFile = File(outDir, "e2_scores_$condition.csv")
            csvFile.bufferedWriter().use { w ->
                w.write("question_id,domain,n_reached,n_leaves,n_stopped,ll,ll_leaves,top1_id,top1_label,top1_is_leaf,top1_share,no_leaf,reached_bridged,top1_bridged\n")
                var done = 0
                for ((qid, domain, text) in pool) {
                    val emb = Embedding(text, text, vectors.getValue(text))
                    val s = scoreQuestion(emb, root, nodeById, opts, bridgedLeafIds)
                    w.write(
                        "$qid,${csv(domain)},${s.nReached},${s.nLeaves},${s.nStopped},${fmt(s.ll)},${fmt(s.llLeaves)}," +
                            "${s.top1Id},${csv(s.top1Label)},${b(s.top1IsLeaf)},${"%.6f".format(java.util.Locale.US, s.top1Share)}," +
                            "${b(s.noLeaf)},${b(s.reachedBridged)},${b(s.top1Bridged)}\n"
                    )
                    if (++done % 500 == 0) log.info("[$condition] scored $done/${pool.size}")
                }
            }
            log.info("[$condition] Wrote ${pool.size} rows to ${csvFile.absolutePath}")
        }

        File(outDir, "e2_manifest.json").writeText(
            json.encodeToString(manifest.mapValues { it.value.toString() })
        )
        log.info("E2 outputs in ${outDir.absolutePath}")
    }

    private fun csv(s: String?): String {
        val v = s ?: ""
        return if (v.contains(',') || v.contains('"') || v.contains('\n')) "\"" + v.replace("\"", "\"\"") + "\"" else v
    }

    private fun fmt(d: Double): String = if (d.isNaN()) "" else "%.8f".format(java.util.Locale.US, d)
    private fun b(x: Boolean): String = if (x) "1" else "0"
}
