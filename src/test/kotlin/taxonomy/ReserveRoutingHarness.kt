package taxonomy

import kotlinx.serialization.json.Json
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Test
import taxonomy.config.TaxonomyConfig
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.operations.TaxonomyTrickler
import java.io.File
import java.sql.DriverManager

/**
 * Routes the reserved pool through the PRODUCTION trickler and dumps query -> leaf
 * assignments, so offline analyses (discriminative flatness, redundancy, the
 * reliability ladder) can be recomputed per cell across the whole tree.
 *
 * Not a test: no assertions beyond sanity, minutes of runtime, opens the 215 MB
 * embeddings cache and the 275 MB snapshots DB. Run with `gradlew routeReserved`.
 *
 * WHY THIS EXISTS RATHER THAN A PYTHON REIMPLEMENTATION: routing is a beam search
 * with a membership floor, residual routing and a descent gate keyed on
 * `childCentroidShrinkage`. A hand-ported copy would drift silently, and the whole
 * point of the exercise is that the assignments match the ones the frozen run used.
 * `match_history.node_id` only covers Math's 11 cells; everything else needs this.
 *
 * The routing config is read FROM THE SNAPSHOT, not from application.yml, so the
 * assignments reflect the frozen run's parameters (membershipFloor 0.25,
 * maxLeafAssignments 5, descentMargin 0.12, residual routing on) even if the
 * working-tree config has since moved.
 */
class ReserveRoutingHarness {

    private val snapshotId = System.getProperty("snapshotId")
        ?: "20260727_042523_Headless_Run_Auto_ge"
    private val outPath = System.getProperty("routeOut") ?: "reserved_leaf_assignments.csv"

    @Test
    fun `route the reserved pool through the production trickler`() {
        val snapDb = File("snapshots.db")
        val embDb = File("embeddings_cache.db")
        val evalDb = File("mmlu_pro_dataset_cache_v2.db")
        assumeTrue(snapDb.exists() && embDb.exists() && evalDb.exists(), "corpus DBs absent")

        // ── 1. frozen graph ──────────────────────────────────────────────────────
        val json = Json { ignoreUnknownKeys = true }
        val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()

        val (serialized, cfgJson) = DriverManager
            .getConnection("jdbc:sqlite:${snapDb.absolutePath}", ro).use { c ->
                c.prepareStatement("SELECT graph, config FROM snapshots WHERE id = ?").use { st ->
                    st.setString(1, snapshotId)
                    val rs = st.executeQuery()
                    check(rs.next()) { "snapshot $snapshotId not found" }
                    json.decodeFromString<taxonomy.service.SerializedGraph>(rs.getString(1)) to
                        rs.getString(2)
                }
            }
        // Rebuild only what routing reads: topology, vMF params, sliceDim and queryWeights.
        // TaxonomyPersistence.loadFromSerialized would also rehydrate query embeddings, which
        // needs an EmbeddingCache and therefore an EmbeddingModel — an LLM dependency this
        // harness has no use for. childCentroidShrinkage is NOT persisted, but it is a pure
        // function of the children's vmfMu and their queryWeights mass, both of which ARE, so
        // it is recomputed bottom-up below and the descent gate sees the frozen run's values.
        val byId = HashMap<String, GraphNode>()
        for (sn in serialized.nodes) {
            val g = GraphNode(id = sn.id, label = sn.label, depth = sn.depth)
            g.sliceDim = sn.sliceDim
            g.vmfMu = sn.vmfMu ?: FloatArray(0)
            g.vmfKappa = sn.vmfKappa
            g.vmfLogNormalizer = sn.vmfLogNormalizer
            sn.queryWeights.forEach { (k, v) -> g.queryWeights[k] = v }
            byId[sn.id] = g
        }
        for (sn in serialized.nodes) {
            val g = byId[sn.id] ?: continue
            sn.childIds.forEach { cid -> byId[cid]?.let { g.children.add(it) } }
        }
        val root = byId[serialized.rootId] ?: error("root ${serialized.rootId} missing")

        // Serialization persists queryWeights on LEAVES ONLY — all 67 internal nodes carry an
        // empty map. updateChildCentroidShrinkage weights each child by
        // `child.queryWeights.values.sum()`, so without this the mass is 0 everywhere, the
        // weights fall back to uniform 1/k, the descent bar is wrong, and the gate fires at the
        // root: 2198 of 3445 reserved queries never descended at all. A node's mass is its
        // subtree's mass, so propagate leaf weights upward before computing shrinkage.
        run {
            val order = serialized.nodes.sortedByDescending { it.depth }
            for (sn in order) {
                val g = byId[sn.id] ?: continue
                if (sn.childIds.isEmpty()) continue
                for (cid in sn.childIds) {
                    byId[cid]?.queryWeights?.forEach { (k, v) ->
                        g.queryWeights.merge(k, v) { a, b -> a + b }
                    }
                }
            }
            val internalWithMass = serialized.nodes.count {
                it.childIds.isNotEmpty() && (byId[it.id]?.queryWeights?.isNotEmpty() == true)
            }
            println("[ROUTE] internal nodes given subtree mass: $internalWithMass/" +
                serialized.nodes.count { it.childIds.isNotEmpty() })
            // Bottom-up so a parent's shrinkage sees fully-populated children.
            order.forEach { byId[it.id]?.updateChildCentroidShrinkage() }
            val shr = order.filter { it.childIds.isNotEmpty() }
                .mapNotNull { byId[it.id]?.childCentroidShrinkage }.sorted()
            if (shr.isNotEmpty()) println("[ROUTE] childCentroidShrinkage: min=%.4f median=%.4f max=%.4f"
                .format(shr.first(), shr[shr.size / 2], shr.last()))
        }

        val leaves = mutableListOf<GraphNode>()
        run {
            val stack = ArrayDeque(listOf(root)); val seen = HashSet<String>()
            while (stack.isNotEmpty()) {
                val n = stack.removeLast()
                if (!seen.add(n.id)) continue
                if (n.children.isEmpty()) leaves += n else n.children.forEach { stack.add(it) }
            }
        }
        println("[ROUTE] snapshot=$snapshotId  nodes=${serialized.nodes.size}  leaves=${leaves.size}")

        // ── 2. routing config from the SNAPSHOT ──────────────────────────────────
        val cfg = TaxonomyConfig()
        if (cfgJson != null) {
            runCatching {
                val o = json.parseToJsonElement(cfgJson).jsonObjectOrNull()?.get("formalism")
                    ?.jsonObjectOrNull()
                fun d(k: String) = o?.get(k)?.toString()?.trim('"')?.toDoubleOrNull()
                fun i(k: String) = o?.get(k)?.toString()?.trim('"')?.toIntOrNull()
                fun b(k: String) = o?.get(k)?.toString()?.trim('"')?.toBooleanStrictOrNull()
                d("membershipFloor")?.let { cfg.formalism.membershipFloor = it }
                i("maxLeafAssignments")?.let { cfg.formalism.maxLeafAssignments = it }
                d("descentMargin")?.let { cfg.formalism.descentMargin = it }
                b("enableResidualRouting")?.let { cfg.formalism.enableResidualRouting = it }
                b("enableGtWarmStart")?.let { cfg.formalism.enableGtWarmStart = it }
            }.onFailure { println("[ROUTE] WARN could not read snapshot config: ${it.message}") }
        }
        println("[ROUTE] membershipFloor=${cfg.formalism.membershipFloor} " +
            "maxLeafAssignments=${cfg.formalism.maxLeafAssignments} " +
            "descentMargin=${cfg.formalism.descentMargin} " +
            "residual=${cfg.formalism.enableResidualRouting}")

        // ── 3. reserved question ids ─────────────────────────────────────────────
        val reserved = HashSet<Int>()
        DriverManager.getConnection("jdbc:sqlite:${evalDb.absolutePath}", ro).use { c ->
            c.createStatement().use { st ->
                st.executeQuery("SELECT DISTINCT question_id FROM eval_results WHERE is_reserved=1")
                    .use { rs -> while (rs.next()) reserved += rs.getInt(1) }
            }
        }
        println("[ROUTE] reserved question ids: ${reserved.size}")

        // ── 4. embeddings, joined on raw_text ────────────────────────────────────
        data class Q(val qid: Int, val key: String, val text: String, val cat: String, val vec: FloatArray)
        val qs = mutableListOf<Q>()
        DriverManager.getConnection("jdbc:sqlite:${embDb.absolutePath}", ro).use { c ->
            c.createStatement().use { st ->
                st.executeQuery(
                    """SELECT q.id, q.query_id, q.ground_truth_category, q.raw_text, e.vector
                       FROM queries q JOIN embeddings e ON e.query = q.raw_text"""
                ).use { rs ->
                    while (rs.next()) {
                        val qid = rs.getInt(2)
                        if (qid !in reserved) continue
                        val blob = rs.getBytes(5) ?: continue
                        // BIG-endian: EmbeddingCache writes with a plain ByteBuffer.wrap/allocate,
                        // and java.nio defaults to BIG_ENDIAN. Decoding little-endian yields
                        // garbage with a NaN L2 norm, every dot product is meaningless, and the
                        // descent gate then fires at the root for 2198 of 3445 queries. Verified:
                        // BE float32 gives L2 = 1.00000 exactly.
                        val bb = java.nio.ByteBuffer.wrap(blob)
                        val v = FloatArray(blob.size / 4) { bb.getFloat(it * 4) }
                        if (qs.isEmpty()) {
                            val l2 = kotlin.math.sqrt(v.sumOf { x -> x.toDouble() * x })
                            check(l2 > 0.99 && l2 < 1.01) {
                                "embedding L2 norm is %.4f, expected ~1.0 — wrong byte order?".format(l2)
                            }
                        }
                        qs += Q(qid, rs.getString(1), rs.getString(4), rs.getString(3) ?: "", v)
                    }
                }
            }
        }
        println("[ROUTE] reserved questions with embeddings: ${qs.size}  dim=${qs.firstOrNull()?.vec?.size}")
        assumeTrue(qs.isNotEmpty(), "no reserved embeddings resolved")

        // ── 5. route ─────────────────────────────────────────────────────────────
        val trickler = TaxonomyTrickler(cfg)
        var routed = 0; var unrouted = 0
        val perLeaf = HashMap<String, Int>()
        File(outPath).printWriter().use { w ->
            w.println("question_id,category,leaf_id,leaf_label,weight,n_leaves")
            for (q in qs) {
                val emb = Embedding(
                    rawText = q.text, distilledText = q.text,
                    values = q.vec, queryId = q.qid
                )
                GraphNode.registerEmbedding(emb)
                val res = runCatching {
                    trickler.routeQuery(emb, root, currentIteration = 99, isInference = true)
                }.getOrNull()
                val hits = res?.leaves ?: emptyMap()
                if (hits.isEmpty()) { unrouted++; continue }
                routed++
                for ((node, wgt) in hits) {
                    perLeaf.merge(node.id, 1, Int::plus)
                    w.println("${q.qid},\"${q.cat}\",${node.id}," +
                        "\"${(node.label ?: "").replace("\"", "'")}\",%.6f,${hits.size}".format(wgt))
                }
                GraphNode.EmbeddingRegistry.remove(q.text)
            }
        }
        println("[ROUTE] routed=$routed  unrouted=$unrouted  leaves touched=${perLeaf.size}/${leaves.size}")
        val sizes = perLeaf.values.sorted()
        if (sizes.isNotEmpty()) {
            println("[ROUTE] per-leaf assignment counts: min=${sizes.first()} " +
                "median=${sizes[sizes.size / 2]} max=${sizes.last()} total=${sizes.sum()}")
        }
        println("[ROUTE] wrote $outPath")
    }
}

private fun kotlinx.serialization.json.JsonElement.jsonObjectOrNull() =
    this as? kotlinx.serialization.json.JsonObject
