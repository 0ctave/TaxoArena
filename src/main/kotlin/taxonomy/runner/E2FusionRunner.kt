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
import kotlin.math.sqrt

/**
 * P6 fusion harness (E2 machinery variant): does FUSING the top cross-anchor E1 twin
 * leaf pairs improve held-out routing fit over the frozen TREE, against size-matched
 * random PLACEBO fusions?
 *
 * Three conditions, SAME reserved questions, same frozen routing parameters (from the
 * snapshot's embedded EffectiveConfig):
 *
 *   T  = frozen tree snapshot, as-is.
 *   F  = the K real twin pairs FUSED: per pair, target = the LARGER leaf (train-query
 *        count; id tiebreak), source = the smaller. QUERY-MOVE fusion variant (labeled
 *        choice, see below).
 *   Pf = K PLACEBO fusions: random leaf pairs drawn seeded (Random(placeboSeed), pair
 *        order fixed), matched to the corresponding real pair on CROSS-ANCHOR-NESS
 *        (members in different depth-1 anchors) and APPROXIMATE SIZES (member-wise
 *        relative tolerance, widened stepwise only if no candidate exists), excluding
 *        the E1 top-10 pair leaves (config excludeLeaves) and leaves already used.
 *
 * FUSION MECHANISM — the QUERY-MOVE variant of TaxonomyMerger.fuseNodes, chosen because
 * a full fuseNodes parent-redirect is ambiguous for CROSS-ANCHOR pairs (it would move
 * the source's tree edge into the other anchor); the held-out ll metric only cares
 * where mass can route, not where the edge hangs. Per pair:
 *   1. target.queries/queryWeights/residual* absorb the source's (union distinct by
 *      rawText, weights summed) — identical to fuseNodes' leaf-target branch;
 *   2. vMF and NiW parameters blended n-weighted exactly as fuseNodes' blendVmfAndNiw;
 *   3. source removed from every parent's children/crossLinkChildren; NO parent edge
 *      is redirected onto the target (this is the query-move deviation);
 *   4. after all K fusions: root.updateAllShrinkages().
 * The source node is unreachable afterwards; no weight renormalization is needed
 * because per-question masses are moved, never duplicated.
 *
 * SCORING is verbatim E2BridgeRunner: per question the path-enumerating reference walk
 * gives raw log path mass per reached node; candidates = reached leaves + gate-stopped
 * internal nodes; ll = logSumExp[log path mass + vMF log density]; production-mirror
 * membership (floor + cap) yields top1. Per-pair descriptives come from two hit
 * columns: hit_real / hit_placebo list the pair ranks whose surviving pair leaves are
 * in the admitted membership set (in T both real and placebo leaves exist; in F the
 * real sources are gone; in Pf the placebo sources are gone).
 *
 * Run: --e2-fusion-config <json>. Exits the JVM when done. Read-only w.r.t. the graph
 * store: loads the snapshot fresh per condition, never saves one.
 */
@Serializable
data class E2FusionPairSpec(val primary: String, val secondary: String)

@Serializable
data class E2FusionConfig(
    val snapshotId: String,
    val outputDir: String,
    val pairs: List<E2FusionPairSpec>,
    /** Leaf label prefixes barred from placebo fusion (the E1 top-10 pair members). */
    val excludeLeaves: List<String> = emptyList(),
    val placeboSeed: Long = 999L,
    /** Member-wise relative size tolerance for placebo matching; widened x2 if empty. */
    val sizeTolerance: Double = 0.25,
    // 0 = all reserved questions; N > 0 = deterministic domain-round-robin subset of size N
    val limit: Int = 0
)

@Component
@Order(1)
class E2FusionRunner(
    private val config: TaxonomyConfig,
    private val snapshotManager: TaxonomySnapshotManager,
    private val datasetFetcher: MMLUDatasetFetcher,
    private val embeddingCache: EmbeddingCache,
    private val trickler: TaxonomyTrickler
) : CommandLineRunner {

    private val log = LoggerFactory.getLogger("taxonomy.E2FusionRunner")
    private val json = Json { prettyPrint = true; ignoreUnknownKeys = true }

    override fun run(vararg args: String?) {
        val idx = args.indexOf("--e2-fusion-config")
        if (idx == -1) return
        val path = args.getOrNull(idx + 1)
            ?: run { log.error("Missing path after --e2-fusion-config"); kotlin.system.exitProcess(1) }
        try {
            runFusion(path!!)
            log.info("P6 fusion harness finished successfully.")
            kotlin.system.exitProcess(0)
        } catch (t: Throwable) {
            log.error("P6 fusion harness failed", t)
            kotlin.system.exitProcess(1)
        }
    }

    // ── graph helpers (verbatim E2BridgeRunner) ──────────────────────────────────

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

    private fun resolveLeaf(prefix: String, leaves: List<GraphNode>): GraphNode {
        val exact = leaves.filter { it.label == prefix }
        if (exact.size == 1) return exact[0]
        val pre = leaves.filter { it.label?.startsWith(prefix) == true }
        require(pre.size == 1) {
            "Leaf label prefix '$prefix' resolves to ${pre.size} leaves: ${pre.map { it.label }}"
        }
        return pre[0]
    }

    /** Train-side leaf size: soft-weight key count when present, else raw query count. */
    private fun leafSize(n: GraphNode): Int =
        if (n.queryWeights.isNotEmpty()) n.queryWeights.size else n.queries.size

    private data class Fusion(
        val pairRank: Int,
        val target: GraphNode,
        val source: GraphNode,
        val targetSize: Int,
        val sourceSize: Int,
        val toleranceUsed: Double // 0.0 for real pairs
    )

    // ── fusion mechanism (query-move variant) ────────────────────────────────────

    private fun fuse(f: Fusion) {
        val target = f.target
        val source = f.source
        require(target.isLeaf && source.isLeaf) {
            "Fusion pair #${f.pairRank} has a non-leaf member: ${target.label} / ${source.label}"
        }
        require(target.id != source.id) { "Fusion pair #${f.pairRank} is degenerate" }

        // 1. Move query mass: union distinct by rawText, weights summed (fuseNodes leaf branch).
        val allQueries = (target.queries + source.queries).distinctBy { it.rawText }
        val allWeights = mutableMapOf<String, Double>()
        for ((q, w) in target.queryWeights) allWeights[q] = (allWeights[q] ?: 0.0) + w
        for ((q, w) in source.queryWeights) allWeights[q] = (allWeights[q] ?: 0.0) + w
        target.queries.clear()
        target.queryWeights.clear()
        target.queries.addAll(allQueries)
        target.queryWeights.putAll(allWeights)

        val newResQueries = (target.residualQueries + source.residualQueries).distinct()
        target.residualQueries.clear()
        target.residualQueries.addAll(newResQueries)
        for ((q, c) in source.residualConfidences) target.residualConfidences.putIfAbsent(q, c)

        // 2. Blend vMF + NiW exactly as TaxonomyMerger.blendVmfAndNiw (n-weighted).
        val nA = f.targetSize.toDouble().coerceAtLeast(1.0)
        val nB = f.sourceSize.toDouble().coerceAtLeast(1.0)
        val d = target.sliceDim
        val mu = FloatArray(d) { i ->
            val vA = if (i < target.vmfMu.size) target.vmfMu[i] else 0.0f
            val vB = if (i < source.vmfMu.size) source.vmfMu[i] else 0.0f
            (nA * vA + nB * vB).toFloat()
        }
        var norm = 0.0
        for (i in 0 until d) norm += mu[i] * mu[i]
        norm = sqrt(norm)
        if (norm > 0.0) for (i in 0 until d) mu[i] = (mu[i] / norm).toFloat() else if (d > 0) mu[0] = 1.0f
        target.vmfMu = mu
        target.vmfKappa = (nA * target.vmfKappa + nB * source.vmfKappa) / (nA + nB)
        target.vmfLogNormalizer = StatisticsUtils.logVmfNormalizer(d, target.vmfKappa)

        target.niwKappa0 = (nA * target.niwKappa0 + nB * source.niwKappa0) / (nA + nB)
        target.niwNu0 = (nA * target.niwNu0 + nB * source.niwNu0) / (nA + nB)
        target.niwM0 = FloatArray(d) { i ->
            val vA = if (i < target.niwM0.size) target.niwM0[i] else 0.0f
            val vB = if (i < source.niwM0.size) source.niwM0[i] else 0.0f
            ((nA * vA + nB * vB) / (nA + nB)).toFloat()
        }
        target.niwLambda = FloatArray(d) { i ->
            val vA = if (i < target.niwLambda.size) target.niwLambda[i] else 0.0f
            val vB = if (i < source.niwLambda.size) source.niwLambda[i] else 0.0f
            ((nA * vA + nB * vB) / (nA + nB)).toFloat()
        }

        // 3. Detach the source structurally — NO parent redirect (query-move variant).
        source.parents.toList().forEach { parent ->
            parent.children.remove(source)
            parent.crossLinkChildren.remove(source)
            if (parent.children.isEmpty()) {
                log.warn("Fusion #${f.pairRank}: parent '${parent.label}' left with NO tree children")
            }
        }
        source.parents.clear()
        source.queries.clear()
        source.queryWeights.clear()
        source.residualQueries.clear()
        source.residualConfidences.clear()
    }

    // ── placebo pair drawing ─────────────────────────────────────────────────────

    private fun drawPlaceboPairs(
        real: List<Fusion>,
        leaves: List<GraphNode>,
        anchors: Map<String, String>,
        excludedLeafIds: Set<String>,
        baseTol: Double,
        seed: Long
    ): List<Fusion> {
        val rng = Random(seed)
        val used = mutableSetOf<String>()
        return real.map { spec ->
            var tol = baseTol
            var candidates: List<Pair<GraphNode, GraphNode>> = emptyList()
            while (candidates.isEmpty()) {
                candidates = buildList {
                    for (t in leaves) for (s in leaves) {
                        if (t.id == s.id) continue
                        if (t.id in excludedLeafIds || s.id in excludedLeafIds) continue
                        if (t.id in used || s.id in used) continue
                        val aT = anchors[t.id] ?: continue
                        val aS = anchors[s.id] ?: continue
                        if (aT == aS) continue // cross-anchor-ness matched (all real pairs are cross)
                        val st = leafSize(t)
                        val ss = leafSize(s)
                        if (st < ss) continue // target is the larger member, like the real pairs
                        if (kotlin.math.abs(st - spec.targetSize) > tol * spec.targetSize) continue
                        if (kotlin.math.abs(ss - spec.sourceSize) > tol * spec.sourceSize) continue
                        add(t to s)
                    }
                }.sortedWith(compareBy({ it.first.id }, { it.second.id }))
                if (candidates.isEmpty()) {
                    tol *= 2
                    require(tol <= 8.0) { "No placebo candidates for pair #${spec.pairRank} even at tolerance $tol" }
                    log.warn("Placebo pair #${spec.pairRank}: widening size tolerance to $tol")
                }
            }
            val (t, s) = candidates[rng.nextInt(candidates.size)]
            used.add(t.id); used.add(s.id)
            Fusion(spec.pairRank, t, s, leafSize(t), leafSize(s), tol)
        }
    }

    // ── scoring (verbatim E2BridgeRunner, hit columns generalized) ───────────────

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
        val hitReal: List<Int>,
        val hitPlacebo: List<Int>
    )

    private fun scoreQuestion(
        emb: Embedding,
        root: GraphNode,
        nodeById: Map<String, GraphNode>,
        opts: TrickleOptions,
        realPairLeafIds: Map<String, Int>,
        placeboPairLeafIds: Map<String, Int>
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

        val maxL = candidates.values.max()
        val logZ = maxL + ln(candidates.values.sumOf { exp(it - maxL) })
        val normalized = candidates.mapValues { (_, v) -> v - logZ }
        val logFloor = ln(config.formalism.membershipFloor.coerceAtLeast(1e-300))
        val admitted = normalized.filterValues { it >= logFloor }
            .ifEmpty { normalized.maxByOrNull { it.value }!!.let { mapOf(it.key to it.value) } }
        val kept = admitted.entries.sortedByDescending { it.value }.take(config.formalism.maxLeafAssignments)
        val top1 = kept.first()

        val keptIds = kept.map { it.key.id }
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
            hitReal = keptIds.mapNotNull { realPairLeafIds[it] }.distinct().sorted(),
            hitPlacebo = keptIds.mapNotNull { placeboPairLeafIds[it] }.distinct().sorted()
        )
    }

    // ── main ─────────────────────────────────────────────────────────────────────

    private fun runFusion(configPath: String) = runBlocking {
        val fc = json.decodeFromString<E2FusionConfig>(File(configPath).readText())
        require(fc.pairs.isNotEmpty()) { "Fusion config has no pairs" }
        log.info("P6 config: snapshot=${fc.snapshotId}, K=${fc.pairs.size}, placeboSeed=${fc.placeboSeed}, tol=${fc.sizeTolerance}, limit=${fc.limit}")

        // 1. Freeze routing parameters to the snapshot's own recorded config.
        val meta = snapshotManager.listSnapshots().find { it.id == fc.snapshotId }
            ?: error("Snapshot ${fc.snapshotId} not found in snapshots.db")
        val effective = meta.config
            ?: error("Snapshot ${fc.snapshotId} carries no embedded EffectiveConfig; refusing to guess routing parameters")
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
        for ((_, qs) in fullByDomain) for (q in qs) idToText[q.id] = q.text
        log.info("Dataset loaded: ${idToText.size} questions across ${fullByDomain.size} domains")

        // 3. Reserved pool from the snapshot row.
        val reservedByDomain = meta.reservedQueries
        require(reservedByDomain.isNotEmpty()) { "Snapshot carries no reserved pool" }
        val reservedAll = reservedByDomain
            .toSortedMap()
            .flatMap { (domain, ids) -> ids.sorted().mapNotNull { id -> idToText[id]?.let { Triple(id, domain, it) } } }
        val missingText = reservedByDomain.values.sumOf { it.size } - reservedAll.size
        log.info("Reserved pool: ${reservedAll.size} questions resolvable to text ($missingText unresolvable ids skipped)")

        val pool: List<Triple<Int, String, String>> = if (fc.limit > 0) {
            val byDomain = reservedAll.groupBy { it.second }.mapValues { it.value.sortedBy { t -> t.first } }
            val out = ArrayList<Triple<Int, String, String>>()
            var i = 0
            while (out.size < fc.limit) {
                var advanced = false
                for (domain in byDomain.keys.sorted()) {
                    val list = byDomain.getValue(domain)
                    if (i < list.size && out.size < fc.limit) { out.add(list[i]); advanced = true }
                }
                if (!advanced) break
                i++
            }
            out
        } else reservedAll
        log.info("Scoring pool: ${pool.size} reserved questions")

        // 4. Embeddings from cache ONLY.
        val vectors = embeddingCache.getBatch(pool.map { it.third })
        val missing = pool.count { it.third !in vectors }
        require(missing == 0) {
            "$missing of ${pool.size} reserved questions have no cached embedding. " +
                "Refusing to fall back to live embedding (Ollama) — fix the cache copy instead."
        }
        log.info("All ${pool.size} question embeddings served from cache")

        val outDir = File(fc.outputDir)
        outDir.mkdirs()

        val opts = TrickleOptions(
            membershipFloor = config.formalism.membershipFloor,
            maxAssignments = config.formalism.maxLeafAssignments,
            readOnly = true
        )

        val manifest = LinkedHashMap<String, Any>()
        manifest["snapshotId"] = fc.snapshotId
        manifest["k"] = fc.pairs.size
        manifest["placeboSeed"] = fc.placeboSeed
        manifest["sizeTolerance"] = fc.sizeTolerance
        manifest["fusionVariant"] = "query-move (no parent redirect; labeled deviation from fuseNodes)"
        manifest["limit"] = fc.limit
        manifest["poolSize"] = pool.size
        manifest["membershipFloor"] = config.formalism.membershipFloor
        manifest["routingBeamGamma"] = config.formalism.routingBeamGamma
        manifest["descentMargin"] = config.formalism.descentMargin
        manifest["maxLeafAssignments"] = config.formalism.maxLeafAssignments

        for (condition in listOf("T", "F", "Pf")) {
            // Fresh load per condition: no cross-condition mutation can leak.
            val root = snapshotManager.loadSnapshot(fc.snapshotId)
                ?: error("Could not load snapshot ${fc.snapshotId}")
            val nodesBefore = allNodes(root)
            val anchors = anchorMap(root)
            val leaves = nodesBefore.values.filter { it.isLeaf }
            log.info("[$condition] Loaded snapshot: ${nodesBefore.size} nodes, ${leaves.size} leaves")

            // Resolve real pairs on THIS load's node objects; target = larger member.
            val realPairs = fc.pairs.mapIndexed { i, p ->
                val a = resolveLeaf(p.primary, leaves)
                val b = resolveLeaf(p.secondary, leaves)
                val (target, source) = if (leafSize(a) > leafSize(b) || (leafSize(a) == leafSize(b) && a.id < b.id)) a to b else b to a
                Fusion(i + 1, target, source, leafSize(target), leafSize(source), 0.0)
            }
            val excludedIds = fc.excludeLeaves.map { resolveLeaf(it, leaves).id }.toMutableSet()
            realPairs.forEach { excludedIds.add(it.target.id); excludedIds.add(it.source.id) }

            // Placebo pairs are drawn identically in every condition (same seed, same
            // candidate sets on the pristine tree) so the hit columns stay comparable.
            val placeboPairs = drawPlaceboPairs(realPairs, leaves, anchors, excludedIds, fc.sizeTolerance, fc.placeboSeed)

            val fusions: List<Fusion> = when (condition) {
                "T" -> emptyList()
                "F" -> realPairs
                "Pf" -> placeboPairs
                else -> error("unreachable")
            }

            // Hit maps: surviving pair-relevant leaf id -> pair rank, per family.
            fun hitMap(pairs: List<Fusion>, fusedHere: Boolean): Map<String, Int> = buildMap {
                for (p in pairs) {
                    put(p.target.id, p.pairRank)
                    if (!fusedHere) put(p.source.id, p.pairRank)
                }
            }
            val realHits = hitMap(realPairs, fusedHere = condition == "F")
            val placeboHits = hitMap(placeboPairs, fusedHere = condition == "Pf")

            if (fusions.isNotEmpty()) {
                for (f in fusions) fuse(f)
                root.updateAllShrinkages()
            }
            // Record the pair rosters for this condition (T records both for reference).
            File(outDir, "e2_fusions_$condition.csv").bufferedWriter().use { w ->
                w.write("family,pair_rank,target_id,target_label,target_anchor,target_size,source_id,source_label,source_anchor,source_size,tolerance_used,fused_in_this_condition\n")
                for ((family, list) in listOf("real" to realPairs, "placebo" to placeboPairs)) {
                    for (f in list) {
                        val fused = (family == "real" && condition == "F") || (family == "placebo" && condition == "Pf")
                        w.write(
                            "$family,${f.pairRank},${f.target.id},${csv(f.target.label)},${csv(anchors[f.target.id])},${f.targetSize}," +
                                "${f.source.id},${csv(f.source.label)},${csv(anchors[f.source.id])},${f.sourceSize}," +
                                "${f.toleranceUsed},${b(fused)}\n"
                        )
                    }
                }
            }
            if (fusions.isNotEmpty()) {
                log.info("[$condition] Applied ${fusions.size} fusions:")
                for (f in fusions) {
                    log.info(
                        "[$condition]   #${f.pairRank} ${f.source.label} (${anchors[f.source.id]}, n=${f.sourceSize}) " +
                            "-> ${f.target.label} (${anchors[f.target.id]}, n=${f.targetSize})" +
                            (if (f.toleranceUsed > 0.0) " [placebo tol=${f.toleranceUsed}]" else "")
                    )
                }
            }

            val nodeById = allNodes(root) // post-fusion node set (sources unreachable)
            val csvFile = File(outDir, "e2_scores_$condition.csv")
            csvFile.bufferedWriter().use { w ->
                w.write("question_id,domain,n_reached,n_leaves,n_stopped,ll,ll_leaves,top1_id,top1_label,top1_is_leaf,top1_share,no_leaf,hit_real,hit_placebo\n")
                var done = 0
                for ((qid, domain, text) in pool) {
                    val emb = Embedding(text, text, vectors.getValue(text))
                    val s = scoreQuestion(emb, root, nodeById, opts, realHits, placeboHits)
                    w.write(
                        "$qid,${csv(domain)},${s.nReached},${s.nLeaves},${s.nStopped},${fmt(s.ll)},${fmt(s.llLeaves)}," +
                            "${s.top1Id},${csv(s.top1Label)},${b(s.top1IsLeaf)},${"%.6f".format(java.util.Locale.US, s.top1Share)}," +
                            "${b(s.noLeaf)},${s.hitReal.joinToString("|")},${s.hitPlacebo.joinToString("|")}\n"
                    )
                    if (++done % 500 == 0) log.info("[$condition] scored $done/${pool.size}")
                }
            }
            log.info("[$condition] Wrote ${pool.size} rows to ${csvFile.absolutePath}")
        }

        File(outDir, "e2_fusion_manifest.json").writeText(
            json.encodeToString(manifest.mapValues { it.value.toString() })
        )
        log.info("P6 fusion outputs in ${outDir.absolutePath}")
    }

    private fun csv(s: String?): String {
        val v = s ?: ""
        return if (v.contains(',') || v.contains('"') || v.contains('\n')) "\"" + v.replace("\"", "\"\"") + "\"" else v
    }

    private fun fmt(d: Double): String = if (d.isNaN()) "" else "%.8f".format(java.util.Locale.US, d)
    private fun b(x: Boolean): String = if (x) "1" else "0"
}
