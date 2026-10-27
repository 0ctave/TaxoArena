package taxonomy

import kotlinx.serialization.json.Json
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.dataset.ReservedPool
import taxonomy.dataset.SplitSide
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.model.TrainOnlyGuard
import taxonomy.service.SerializedGraph
import java.io.File
import java.sql.Connection
import java.sql.DriverManager

/**
 * READ-ONLY audit harness (`gradlew trainOnlyAudit`, excluded from `test`): the TRAIN-ONLY reading
 * of the three trees of record against their own stored pools, BY CONTENT (FRAMEWORK item 18,
 * TRAIN-ONLY-TREE). Pre-registered values, established read-only while planning this item, are
 * EXACT-TEXT matches (distinct EVAL texts among the tree's members):
 *
 *   20260727_042523 (snapshots_frozen.db, the 2026-09-09 incident tree, built on p8a29)  2,437
 *   20260910_043557 (snapshots.db, MMLU-Pro tree of record, hygiene/bareq512_s42_labelfree)   37
 *   20260911_144214 (snapshots.db, union tree of record)                                     427
 *
 * [CORRECTED 2026-09-23 (review 8ebfa7a, SPLIT-FOLLOWUPS; programme L14298, L14462): the second row
 * is NOT the tree of record. bareq512_s42 of record is snapshot 20260909_212117_Headless_Run_Auto_ge
 * (LLM-labelled and rubric-induced); 20260910_043557 is its label-free hygiene replica
 * (hygiene/bareq512_s42_labelfree.toml) with the same 8,278 members but 6 different leaf ids (and one
 * leaf member), not a routing substitute. The counts asserted below are read from the replica; they
 * stand for 20260909_212117 only through that membership identity, which this harness does not read.]
 *
 * FINDING (first run of this harness, 2026-09-16): under the split function's own key
 * (SplitSide.stemKey = norm-v1: NFKC, ASCII case fold, whitespace collapse) the same trees hold
 * 2,448 / 70 / 432 distinct EVAL texts, i.e. 11 / 33 / 5 further arena questions whose text
 * differs from a member's only by case, whitespace or compatibility characters. Both readings
 * are asserted here: the exact-text one reproduces the pre-registration, the normalised one is
 * the reading the guard applies from now on and the count a snapshot must be acknowledged at.
 *
 * Any other number is a finding, not a pass. Every database is opened with SQLITE_OPEN_READONLY
 * (`org.sqlite.SQLiteConfig.setReadOnly`); the production caches are never written. The DBs are
 * looked up under -DdataRoot (default: the working directory).
 */
class TreesOfRecordEvalMembershipAudit {

    private val dataRoot = File(System.getProperty("dataRoot") ?: ".")
    private val ro = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }.toProperties()
    private val json = Json { ignoreUnknownKeys = true }

    /** [poolFile] overrides the snapshot's own stored pool: the incident tree stored p8a29 but was JUDGED on p2dca. */
    private data class Case(val snapshotDb: String, val snapshotId: String, val corpusDb: String, val expectedExact: Int, val expectedNormalised: Int, val poolFile: String? = null)

    private val cases = listOf(
        Case("snapshots_frozen.db", "20260727_042523_Headless_Run_Auto_ge", "mmlu_pro_dataset_cache_v2.db", 2437, 2448,
            poolFile = "experiment_configs/reserved_pool_frozen_p2dca.json"),
        Case("snapshots.db", "20260910_043557_Headless_Run_Auto_ge", "mmlu_pro_dataset_cache_v2.db", 37, 70),
        Case("snapshots.db", "20260911_144214_Union_graft_of_6_cor", "multicorpus_cache_v1.db", 427, 432)
    )

    private fun open(name: String): Connection {
        val f = File(dataRoot, name)
        check(f.isFile) { "[AUDIT] $name not found under ${dataRoot.absolutePath}; pass -DdataRoot=<repo root with the caches>" }
        return DriverManager.getConnection("jdbc:sqlite:${f.absolutePath}", ro).also {
            it.createStatement().use { s -> s.execute("PRAGMA query_only = 1") }
        }
    }

    /** EVAL texts of the snapshot's own pool: MMLU-Pro through the link table, leaderboard corpora through corpus_questions. */
    private fun evalTexts(corpus: Connection, pool: Map<String, List<Int>>): Set<String> {
        val ids = pool.values.flatten().filter { it > 0 }
        val out = HashSet<String>()
        val hasCorpusQuestions = corpus.createStatement().use { s ->
            s.executeQuery("SELECT name FROM sqlite_master WHERE type='table' AND name='corpus_questions'").use { it.next() }
        }
        val hasMmluPro = corpus.createStatement().use { s ->
            s.executeQuery("SELECT name FROM sqlite_master WHERE type='table' AND name='mmlu_pro'").use { it.next() }
        }
        ids.chunked(900).forEach { chunk ->
            val ph = chunk.joinToString(",") { "?" }
            if (hasMmluPro) corpus.prepareStatement(
                "SELECT m.question FROM eval_question_link l JOIN mmlu_pro m ON m.id = l.mmlu_pro_row_id WHERE l.question_id IN ($ph)"
            ).use { ps -> chunk.forEachIndexed { i, id -> ps.setInt(i + 1, id) }; ps.executeQuery().use { rs -> while (rs.next()) rs.getString(1)?.let { out.add(it) } } }
            if (hasCorpusQuestions) corpus.prepareStatement(
                "SELECT text FROM corpus_questions WHERE question_id IN ($ph)"
            ).use { ps -> chunk.forEachIndexed { i, id -> ps.setInt(i + 1, id) }; ps.executeQuery().use { rs -> while (rs.next()) rs.getString(1)?.let { out.add(it) } } }
        }
        return out
    }

    /** Rebuilds the member structure of a serialized graph as GraphNodes with raw texts, through the embedding cache. */
    private fun hydrateMembers(graph: SerializedGraph, emb: Connection): GraphNode {
        val qids = graph.nodes.flatMap { it.queryIds + it.queryWeights.keys }.toSet()
        val idToText = HashMap<String, String>(qids.size)
        val queryIdToText = HashMap<Int, String>()
        qids.chunked(900).forEach { chunk ->
            val ph = chunk.joinToString(",") { "?" }
            emb.prepareStatement("SELECT id, raw_text, query_id FROM queries WHERE id IN ($ph)").use { ps ->
                chunk.forEachIndexed { i, id -> ps.setString(i + 1, id) }
                ps.executeQuery().use { rs ->
                    while (rs.next()) {
                        val t = rs.getString(2) ?: continue
                        idToText[rs.getString(1)] = t
                        val q = rs.getInt(3); if (q > 0) queryIdToText[q] = t
                    }
                }
            }
        }
        val residualIds = graph.nodes.flatMap { it.residualQueries }.mapNotNull { it.toIntOrNull() }.filter { it > 0 && it !in queryIdToText }.toSet()
        residualIds.chunked(900).forEach { chunk ->
            val ph = chunk.joinToString(",") { "?" }
            emb.prepareStatement("SELECT query_id, raw_text FROM queries WHERE query_id IN ($ph)").use { ps ->
                chunk.forEachIndexed { i, id -> ps.setInt(i + 1, id) }
                ps.executeQuery().use { rs -> while (rs.next()) rs.getString(2)?.let { queryIdToText[rs.getInt(1)] = it } }
            }
        }
        for ((q, t) in queryIdToText) GraphNode.registerEmbedding(Embedding(t, t, FloatArray(0), queryId = q))
        val nodes = graph.nodes.associate { s ->
            s.id to GraphNode(id = s.id, label = s.label, depth = s.depth).apply {
                for (qid in s.queryIds) idToText[qid]?.let { queries.add(Embedding(it, it, FloatArray(0))) }
                for ((qid, w) in s.queryWeights) idToText[qid]?.let { queryWeights[it] = w }
                residualQueries.addAll(s.residualQueries)
            }
        }
        for (s in graph.nodes) {
            val n = nodes.getValue(s.id)
            s.childIds.mapNotNull { nodes[it] }.forEach { n.children.add(it) }
            s.crossLinkChildIds.mapNotNull { nodes[it] }.forEach { n.crossLinkChildren.add(it) }
        }
        return nodes.getValue(graph.rootId)
    }

    @Test
    fun `the three trees of record hold the pre-registered EVAL-member counts`() {
        val results = ArrayList<Triple<Case, TrainOnlyGuard.Report, TrainOnlyGuard.Report>>()
        open("embeddings_cache.db").use { emb ->
            for (c in cases) {
                val (graphStr, poolStr) = open(c.snapshotDb).use { snap ->
                    snap.prepareStatement("SELECT graph, reserved_queries FROM snapshots WHERE id = ?").use { ps ->
                        ps.setString(1, c.snapshotId)
                        ps.executeQuery().use { rs -> check(rs.next()) { "[AUDIT] ${c.snapshotId} not in ${c.snapshotDb}" }; rs.getString(1) to rs.getString(2) }
                    }
                }
                val pool: Map<String, List<Int>> = json.decodeFromString(c.poolFile?.let { File(it).readText() } ?: poolStr)
                val poolId = ReservedPool.computePoolId(pool.mapValues { (_, v) -> v.filter { it > 0 } }.filterValues { it.isNotEmpty() })
                val texts = open(c.corpusDb).use { evalTexts(it, pool) }
                val root = hydrateMembers(json.decodeFromString(graphStr), emb)
                val exact = TrainOnlyGuard.evalMembers(root, TrainOnlyGuard.keysOf(texts) { it }) { it }
                val normalised = TrainOnlyGuard.evalMembers(root, TrainOnlyGuard.keysOf(texts))
                println("[AUDIT] ${c.snapshotId} (${c.snapshotDb}) pool $poolId: ${texts.size} EVAL texts;" +
                    " exact-text: $exact (pre-registered ${c.expectedExact});" +
                    " ${SplitSide.NORMALISER_VERSION}: $normalised (registered ${c.expectedNormalised})")
                results.add(Triple(c, exact, normalised))
            }
        }
        for ((c, exact, normalised) in results) {
            assertEquals(c.expectedExact, exact.distinctKeys, "[AUDIT] ${c.snapshotId}: exact-text EVAL members ${exact.distinctKeys} != pre-registered ${c.expectedExact} (a finding, not a pass)")
            assertEquals(c.expectedNormalised, normalised.distinctKeys, "[AUDIT] ${c.snapshotId}: ${SplitSide.NORMALISER_VERSION} EVAL members ${normalised.distinctKeys} != registered ${c.expectedNormalised} (a finding, not a pass)")
            assertTrue(normalised.distinctKeys >= exact.distinctKeys, "normalisation can only merge texts")
        }
        assertTrue(results.size == 3)
        println("[AUDIT] exact-text counts reproduce the pre-registered 2437 / 37 / 427; ${SplitSide.NORMALISER_VERSION} reads 2448 / 70 / 432")
    }
}
