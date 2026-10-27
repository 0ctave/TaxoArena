package taxonomy

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import org.mockito.Mockito.verifyNoInteractions
import org.mockito.Mockito.`when`
import org.sqlite.SQLiteConfig
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.EmbeddingCache
import taxonomy.dataset.ModelEvalResult
import taxonomy.dataset.ModelEvalStore
import taxonomy.model.GraphNode
import taxonomy.operations.AzureInferenceJudgeClient
import taxonomy.operations.JudgeCallResult
import taxonomy.operations.RecipeJudgeTransport
import taxonomy.operations.RecipeKit
import taxonomy.operations.RecipeKitProvider
import taxonomy.operations.RequestGate
import taxonomy.operations.StackV2Kit
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomyOperations
import taxonomy.prompts.StackV2JudgeRecipe
import taxonomy.service.DomainEvaluation
import taxonomy.service.JudgeCallStore
import taxonomy.service.ParseResult
import taxonomy.service.TaxonomyArenaService
import taxonomy.service.TaxonomyRankingService
import taxonomy.service.TaxonomyService
import taxonomy.service.TracePreparation
import taxonomy.utils.TaxonomyPerformanceTracker
import java.io.File
import java.security.MessageDigest
import java.sql.Connection
import java.sql.DriverManager

/**
 * JUDGE-WIRING harness (FRAMEWORK.md item 25). NOT a test: excluded from `gradlew test`, run as
 *
 *   gradlew judgeWiring -Dmode=dump -DmatchId=<id>      exact body bytes (both orders) + sha256 for one x12 match, zero calls
 *   gradlew judgeWiring -Dmode=shas                      payload_shas_kotlin.csv for every match of the frozen set, zero calls
 *   gradlew judgeWiring -Dmode=parse-replay              every raw1/raw2 of the Python RECIPE-GROK cache through the Kotlin
 *                                                        parser + combination, compared to the cached votes, zero calls
 *   gradlew judgeWiring -Dmode=run -Dconfirm=JUDGE-WIRING [-Dpilot=12] [-Dworkers=8]
 *                                                        the paired run: REFUSED unless the confirm token is given AND
 *                                                        payload_shas_python.csv exists and equals the freshly computed
 *                                                        Kotlin shas for EVERY match (byte identity is a precondition of the
 *                                                        spend, not a report after it) AND the set verifies (pool of record,
 *                                                        hash, membership, EXCLUDED). Nothing in the JUDGE-WIRING item runs it.
 *
 * Optional: -Dkit=<path> (default experiment_results/judge_wiring/stack_v2_kit.db), -DevalDb=<path> (default
 * mmlu_pro_dataset_cache_v2.db), -Dx12Db, -DsetJson, -Dout (the run's DB, default kotlin_<set_hash>.db).
 *
 * WHAT IT CONSTRUCTS. The real `TaxonomyArenaService` (real assembler, real recipe branch, real parser) over Mockito
 * mocks for TaxonomyService / EmbeddingCache / TaxonomyOperations / TaxonomyRankingService (verifyNoInteractions on the
 * ranking mock: the production ratings DB is never opened) and a ModelEvalStore mock; eval rows are read through a
 * READ-ONLY sqlite connection with the same options_json decoding ModelEvalStore uses. The synthetic tree holds the set's
 * node ids with judgePrompt = "RECIPE-PATH-MUST-NOT-USE-THIS", asserted absent from every payload. Every input DB is
 * opened read-only; the only writes are under experiment_results/judge_wiring/.
 */
class JudgeWiringHarness {

    private val root = File(".").absoluteFile.normalize()
    // -DoutDir redirects every write (dumps, sha csv, the run DB) elsewhere, e.g. a scratch directory for a dry check.
    private val outDir = System.getProperty("outDir")?.let { File(it) } ?: File(root, "experiment_results/judge_wiring")
    private val kitPath = System.getProperty("kit", "experiment_results/judge_wiring/stack_v2_kit.db")
    private val evalDb = System.getProperty("evalDb", "mmlu_pro_dataset_cache_v2.db")
    private val x12Db = System.getProperty("x12Db", "experiment_results/x12_crossdomain/ratings_x12.db")
    private val pyCache = "experiment_results/x12_crossdomain/stack_v2_promptv2_grok.db"
    private val setJson = System.getProperty("setJson", "experiment_results/judge_wiring/judge_wiring_set.json")
    private val poolOfRecord = "p2dca21ab5f4ef3ae"
    private val excluded = setOf("Meta-Llama-3-70B-Instruct")
    private val tripwire = "RECIPE-PATH-MUST-NOT-USE-THIS"
    private val evalJson = Json { ignoreUnknownKeys = true; isLenient = true; coerceInputValues = true }   // ModelEvalStore's settings
    private val json = Json { ignoreUnknownKeys = true }

    private fun ro(path: String): Connection = SQLiteConfig().apply { setReadOnly(true) }.createConnection("jdbc:sqlite:$path")

    private fun sha(b: ByteArray) = MessageDigest.getInstance("SHA-256").digest(b).joinToString("") { "%02x".format(it) }

    // ── data ────────────────────────────────────────────────────────────────────

    data class Match(val matchId: Long, val qid: Int, val modelA: String, val modelB: String, val nodeId: String, val anchor: String, val stratum: String, val pairKind: String)

    private fun readSet(): Pair<List<Match>, JsonObject> {
        val f = File(setJson)
        require(f.isFile) { "$setJson missing: python tools/analysis/judge_wiring.py --freeze-only" }
        val d = json.parseToJsonElement(f.readText(Charsets.UTF_8)).jsonObject
        val ms = d["matches"]!!.jsonArray.map { e ->
            val o = e.jsonObject
            Match(o["match_id"]!!.jsonPrimitive.content.toLong(), o["qid"]!!.jsonPrimitive.content.toInt(), o["model_a"]!!.jsonPrimitive.content,
                o["model_b"]!!.jsonPrimitive.content, o["node_id"]!!.jsonPrimitive.content, o["anchor"]!!.jsonPrimitive.content,
                o["stratum"]!!.jsonPrimitive.content, o["pair_kind"]?.jsonPrimitive?.content ?: "?")
        }
        return ms to d
    }

    private fun setHash(ms: List<Match>): String =
        sha(ms.joinToString("\n") { "${it.matchId}:${it.qid}:${it.modelA}:${it.modelB}:${it.stratum}" }.toByteArray(Charsets.UTF_8)).substring(0, 16)

    private fun verifySet(ms: List<Match>, d: JsonObject) {
        check(d["pool_id"]!!.jsonPrimitive.content == poolOfRecord) { "set pool_id ${d["pool_id"]} != $poolOfRecord" }
        val recorded = d["set_hash"]!!.jsonPrimitive.content
        check(setHash(ms) == recorded) { "set hash recomputed ${setHash(ms)} != recorded $recorded" }
        check(ms.none { it.modelA in excluded || it.modelB in excluded }) { "an EXCLUDED model is in the set" }
        ro(evalDb).use { c ->
            val pool = HashSet<Int>()
            c.prepareStatement("SELECT question_id FROM reserved_pool WHERE pool_id = ?").use { ps ->
                ps.setString(1, poolOfRecord); ps.executeQuery().use { rs -> while (rs.next()) pool.add(rs.getInt(1)) }
            }
            check(pool.isNotEmpty()) { "reserved_pool has no rows for $poolOfRecord in $evalDb" }
            val outside = ms.filter { it.qid !in pool }
            check(outside.isEmpty()) { "${outside.size} set questions are outside the pool of record: ${outside.take(5).map { it.qid }}" }
        }
        println("[SET] $setJson: ${ms.size} matches | pool $poolOfRecord | hash $recorded verified | every question in the pool of record")
    }

    private fun readX12Match(matchId: Long): Match = ro(x12Db).use { c ->
        c.prepareStatement("SELECT id, eval_question_id, model_a, model_b, node_id FROM match_history WHERE id = ?").use { ps ->
            ps.setLong(1, matchId)
            ps.executeQuery().use { rs ->
                check(rs.next()) { "match $matchId not in $x12Db" }
                Match(rs.getLong(1), rs.getString(2).toInt(), rs.getString(3), rs.getString(4), rs.getString(5), "?", "(x12)", "?")
            }
        }
    }

    /** eval_results rows for (qid, model), read-only, decoded exactly as ModelEvalStore.toSingleEvalResult decodes them. */
    private fun readEvalRows(pairs: Collection<Pair<Int, String>>): Map<Pair<Int, String>, ModelEvalResult> {
        val out = HashMap<Pair<Int, String>, ModelEvalResult>()
        ro(evalDb).use { c ->
            c.prepareStatement("SELECT question_id, model_name, category, question_text, options_json, gt_answer, pred, model_output, is_correct FROM eval_results WHERE question_id = ? AND model_name = ? LIMIT 1").use { ps ->
                for ((q, m) in pairs.toSet()) {
                    ps.setInt(1, q); ps.setString(2, m)
                    ps.executeQuery().use { rs ->
                        if (rs.next()) out[q to m] = ModelEvalResult(
                            questionId = rs.getInt(1), modelName = rs.getString(2), category = rs.getString(3), questionText = rs.getString(4),
                            options = evalJson.decodeFromString(rs.getString(5)), gtAnswer = rs.getString(6), pred = rs.getString(7),
                            modelOutput = rs.getString(8), isCorrect = rs.getInt(9) == 1
                        )
                    }
                }
            }
        }
        return out
    }

    // ── the service under test ──────────────────────────────────────────────────

    private class Rig(val service: TaxonomyArenaService, val config: TaxonomyConfig, val ranking: TaxonomyRankingService, val nodes: Map<String, GraphNode>)

    private fun rig(nodeIds: Collection<String>, transport: RecipeJudgeTransport, kit: RecipeKit?): Rig {
        val config = TaxonomyConfig().apply {
            llm.judgeModel = "Mistral-Large-3"
            llm.judgeOptionMode = "RESOLVED"
            llm.judgeRecipe.enabled = true
            llm.judgeRecipe.kitPath = kitPath
        }
        val root = GraphNode(id = "harness-root", label = "root", depth = 0)
        root.judgePrompt = tripwire
        val nodes = LinkedHashMap<String, GraphNode>()
        for (id in nodeIds.toSet()) {
            val n = GraphNode(id = id, label = "leaf $id", depth = 1)
            n.judgePrompt = tripwire; n.judgeRubric = tripwire
            root.children.add(n); nodes[id] = n
        }
        val taxonomyService = mock(TaxonomyService::class.java)
        `when`(taxonomyService.getGraph()).thenReturn(root)
        val ranking = mock(TaxonomyRankingService::class.java)
        val client = object : TaxonomyLlmClient {
            override suspend fun generateClusterLabel(prompt: String): String = error("langchain4j path must not be used")
            override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String = error("langchain4j path must not be used")
            override suspend fun queryModelStructured(modelName: String, systemPrompt: String?, userPrompt: String, schema: dev.langchain4j.model.chat.request.json.JsonSchema): String = error("langchain4j path must not be used")
            override fun setMaxParallel(limit: Int) {}
        }
        val provider = object : RecipeKitProvider { override fun get(): RecipeKit = kit ?: error("no kit") }
        val service = TaxonomyArenaService(
            config, taxonomyService, client, mock(EmbeddingCache::class.java), mock(TaxonomyOperations::class.java),
            mock(ModelEvalStore::class.java), ranking, TaxonomyPerformanceTracker(), transport, provider
        )
        return Rig(service, config, ranking, nodes)
    }

    private val refusingTransport = object : RecipeJudgeTransport {
        override suspend fun post(body: ByteArray): JudgeCallResult = error("this mode posts nothing")
    }

    private fun assemble(r: Rig, m: Match, rows: Map<Pair<Int, String>, ModelEvalResult>, stats: TracePreparation.Stats): StackV2JudgeRecipe.Assembly.Assembled? {
        val ra = rows[m.qid to m.modelA] ?: error("no eval row for q${m.qid} ${m.modelA}")
        val rb = rows[m.qid to m.modelB] ?: error("no eval row for q${m.qid} ${m.modelB}")
        val ta = TracePreparation.robustTrace(ra, r.config.llm.judgeOptionMode, stats)
        val tb = TracePreparation.robustTrace(rb, r.config.llm.judgeOptionMode, stats)
        val a = r.service.assembleRecipe(m.qid, ra.questionText, ta, tb) ?: return null
        check(!String(a.body1, Charsets.US_ASCII).contains(tripwire) && !String(a.body2, Charsets.US_ASCII).contains(tripwire)) { "tripwire text reached a payload" }
        return a
    }

    // ── modes ───────────────────────────────────────────────────────────────────

    @Test
    fun harness() {
        when (val mode = System.getProperty("mode") ?: "") {
            "dump" -> dump(System.getProperty("matchId")?.toLong() ?: error("-DmatchId=<x12 match id> required"))
            "shas" -> shas()
            "parse-replay" -> parseReplay()
            "run" -> run()
            else -> error("unknown -Dmode='$mode' (dump | shas | parse-replay | run)")
        }
    }

    private fun dump(matchId: Long) {
        val kit = StackV2Kit.open(kitPath)
        val m = readX12Match(matchId)
        val rows = readEvalRows(listOf(m.qid to m.modelA, m.qid to m.modelB))
        val r = rig(listOf(m.nodeId), refusingTransport, kit)
        val a = assemble(r, m, rows, TracePreparation.Stats()) ?: error("match $matchId skipped: no anchor or reference in the kit")
        val d = File(outDir, "dump"); d.mkdirs()
        for ((order, body, user) in listOf(Triple(1, a.body1, a.user1), Triple(2, a.body2, a.user2))) {
            val p = File(d, "match_${matchId}_order$order.kotlin.json")
            p.writeBytes(body); File(d, p.name + ".sha256").writeText(sha(body) + "\n")
            File(d, "match_${matchId}_order$order.kotlin.user.txt").writeBytes(user.toByteArray(Charsets.UTF_8))
            println("[DUMP] order $order -> ${p.path} (${body.size} bytes, sha256 ${sha(body)})")
        }
        File(d, "match_$matchId.kotlin.system.txt").writeBytes(a.system.toByteArray(Charsets.UTF_8))
        println("[DUMP] match $matchId | qid ${m.qid} | ${m.modelA} vs ${m.modelB} | anchor ${a.anchor} | ref (${a.refLetter}) | model ${r.config.llm.judgeRecipe.model} | max_tokens ${r.config.llm.judgeRecipe.maxTokens} | temperature ${r.config.llm.judgeRecipe.temperatureLabel}")
        println("[DUMP] compare with: python tools/analysis/judge_wiring.py --dump-payload $matchId ; cmp match_${matchId}_order1.kotlin.json match_${matchId}_order1.python.json")
        verifyNoInteractions(r.ranking)
    }

    private fun computeShas(r: Rig, ms: List<Match>): List<Array<String>> {
        val rows = readEvalRows(ms.flatMap { listOf(it.qid to it.modelA, it.qid to it.modelB) })
        val stats = TracePreparation.Stats()
        return ms.map { m ->
            val a = assemble(r, m, rows, stats)
            if (a == null) arrayOf(m.matchId.toString(), "", "", m.anchor, "", "no anchor or reference in kit")
            else arrayOf(m.matchId.toString(), a.sha1, a.sha2, a.anchor, a.refLetter, "")
        }
    }

    private fun shas() {
        val kit = StackV2Kit.open(kitPath)
        val (ms, d) = readSet(); verifySet(ms, d)
        val r = rig(ms.map { it.nodeId }, refusingTransport, kit)
        val rows = computeShas(r, ms)
        outDir.mkdirs()
        val out = File(outDir, "payload_shas_kotlin.csv")
        out.writeText("match_id,sha_order1,sha_order2,anchor,ref_letter,skipped_reason\n" + rows.joinToString("") { it.joinToString(",") + "\n" }, Charsets.UTF_8)
        val skipped = rows.count { it[5].isNotEmpty() }
        println("[SHAS] ${rows.size - skipped}/${rows.size} matches x 2 orders -> ${out.path} (skipped $skipped) | kit ${kit.kitHash} | fingerprint ${r.config.llm.judgeRecipe.fingerprint()}")
        val py = File(outDir, "payload_shas_python.csv")
        if (py.isFile) println("[SHAS] vs Python: " + compareShas(rows, py))
        else println("[SHAS] payload_shas_python.csv missing: python tools/analysis/judge_wiring.py --shas")
        verifyNoInteractions(r.ranking)
    }

    /** Returns a summary line; `ok` when every match's two shas equal the Python file's. */
    private fun compareShas(kotlin: List<Array<String>>, pyFile: File): String {
        val py = pyFile.readLines(Charsets.UTF_8).drop(1).filter { it.isNotBlank() }.associate { line ->
            val p = line.split(","); p[0] to (p[1] to p[2])
        }
        var eq = 0; val bad = mutableListOf<String>()
        for (k in kotlin) {
            val p = py[k[0]]
            if (p != null && p.first == k[1] && p.second == k[2] && k[1].isNotEmpty()) eq++ else bad.add(k[0])
        }
        return "$eq/${kotlin.size} byte-identical" + (if (bad.isEmpty()) " -> ok" else " -> MISMATCH on ${bad.size}: ${bad.take(10)}")
    }

    private fun parseReplay() {
        val r = rig(emptyList(), refusingTransport, null)
        var n = 0; var winnerDis = 0; var confDis = 0; var combDis = 0
        val examples = mutableListOf<String>()
        ro(pyCache).use { c ->
            c.createStatement().executeQuery("SELECT match_id, model_a, model_b, vote1, vote2_raw, conf1, conf2, winner, flip, invalid, raw1, raw2 FROM verdicts ORDER BY match_id").use { rs ->
                while (rs.next()) {
                    n++
                    val mid = rs.getLong(1); val a = rs.getString(2); val b = rs.getString(3)
                    val pv1 = rs.getString(4); val pv2 = rs.getString(5); val pc1 = rs.getDouble(6); val pc2 = rs.getDouble(7)
                    val pw = rs.getString(8); val pflip = rs.getInt(9) == 1; val pinv = rs.getInt(10) == 1
                    fun call(raw: String) = JudgeCallResult(raw, "stop", null, null, null, null, 200, 1, 0, "")
                    val k1: ParseResult = r.service.parseRecipeCall(call(rs.getString(11) ?: ""))
                    val k2: ParseResult = r.service.parseRecipeCall(call(rs.getString(12) ?: ""))
                    val (kw, kflip, kinv) = r.service.combineOrders(k1, k2)
                    val kwName = when (kw) { "Model A" -> a; "Model B" -> b; else -> kw }
                    if (k1.winner != pv1 || k2.winner != pv2) { winnerDis++; if (examples.size < 20) examples.add("match $mid: votes kotlin ${k1.winner}/${k2.winner} vs python $pv1/$pv2") }
                    else if (Math.abs(k1.confidence - pc1) > 1e-9 || Math.abs(k2.confidence - pc2) > 1e-9) { confDis++; if (examples.size < 20) examples.add("match $mid: confidence kotlin ${k1.confidence}/${k2.confidence} vs python $pc1/$pc2 (winners agree)") }
                    if (kwName != pw || kflip != pflip || kinv != pinv) { combDis++; if (examples.size < 20) examples.add("match $mid: combination kotlin $kwName flip=$kflip inv=$kinv vs python $pw flip=$pflip inv=$pinv") }
                }
            }
        }
        println("[PARSE-REPLAY] $n cached matches (${2 * n} raw responses) through parseRecipeCall + combineOrders")
        println("[PARSE-REPLAY] per-order winner disagreements: $winnerDis | confidence-only disagreements: $confDis | combined-verdict disagreements: $combDis")
        examples.forEach { println("  $it") }
        println("[PARSE-REPLAY] " + if (winnerDis == 0 && combDis == 0) "winner parity OK (a nonzero count is a blocker: fix the recipe branch, never the Mistral parser)" else "WINNER DISAGREEMENT: blocker")
        verifyNoInteractions(r.ranking)
    }

    private fun run() {
        val (ms, d) = readSet(); verifySet(ms, d)
        check(System.getProperty("confirm") == "JUDGE-WIRING") { "[RUN] refused: pass -Dconfirm=JUDGE-WIRING (this mode posts up to ${"%,d".format(2 * ms.size)} judge calls: ${ms.size} matches x 2 orders from $setJson)" }
        val kit = StackV2Kit.open(kitPath)
        val setHash = d["set_hash"]!!.jsonPrimitive.content
        val pilot = System.getProperty("pilot")?.toInt()
        val workers = System.getProperty("workers")?.toInt() ?: 8
        val transport = AzureInferenceJudgeClient(
            endpoint = System.getenv("AZURE_AI_ENDPOINT")?.takeIf { it.isNotBlank() } ?: error("[RUN] AZURE_AI_ENDPOINT not exported"),
            apiKey = { System.getenv("AZURE_GROK_API_KEY")?.takeIf { it.isNotBlank() } ?: System.getenv("AZURE_AI_API_KEY")?.takeIf { it.isNotBlank() } },
            gate = RequestGate(workers, 4.0).let { g -> { send -> g.run(send) } }
        )
        val r = rig(ms.map { it.nodeId }, transport, kit)
        val rc = r.config.llm.judgeRecipe
        rc.kitHash = kit.kitHash
        // precondition: the Kotlin shas equal the Python shas for EVERY match of the set
        val py = File(outDir, "payload_shas_python.csv")
        check(py.isFile) { "[RUN] refused: ${py.path} missing (python tools/analysis/judge_wiring.py --shas)" }
        val shaRows = computeShas(r, ms)
        val cmp = compareShas(shaRows, py)
        check(cmp.endsWith("-> ok")) { "[RUN] refused: Kotlin payloads are not byte-identical to the Python payloads: $cmp" }
        println("[RUN] byte identity precondition: $cmp")
        val shaOf = shaRows.associate { it[0].toLong() to (it[1] to it[2]) }
        // the run's own DB, pinned at first launch
        val out = File(System.getProperty("out") ?: File(outDir, "kotlin_$setHash.db").path)
        outDir.mkdirs()
        val con = DriverManager.getConnection("jdbc:sqlite:${out.path}")
        con.createStatement().use { st ->
            st.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER, anchor TEXT, " +
                "ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL, " +
                "finish1 TEXT, finish2 TEXT, ctok1 INTEGER, ctok2 INTEGER, rid1 TEXT, rid2 TEXT, sha1 TEXT, sha2 TEXT, stratum TEXT, pair_kind TEXT)")
            st.execute("CREATE TABLE IF NOT EXISTS run_meta (key TEXT PRIMARY KEY, value TEXT)")
        }
        val protocol = "STACK-v2 | judge ${rc.model} (Kotlin TaxonomyArenaService recipe branch, AzureInferenceJudgeClient /models/chat/completions?api-version=${rc.inferenceApiVersion}) | " +
            "prompt v2 verify-first + ladder anchor rubric (bareq512_s42 depth-1 anchor) + schema instruction | reference block = grok-reasoning cached solve (kit) | dual order, " +
            "TIE on flip, INVALID if either order unparsed or finish_reason in {length, content_filter} | max_tokens ${rc.maxTokens} | temperature ${rc.temperatureLabel}"
        val meta = linkedMapOf(
            "test" to "JUDGE-WIRING", "protocol" to protocol, "judge" to rc.model, "recipe" to rc.name, "max_tokens" to rc.maxTokens.toString(),
            "temperature" to rc.temperatureLabel, "kit_hash" to kit.kitHash, "fingerprint" to rc.fingerprint(), "set_hash" to setHash, "pool_id" to poolOfRecord,
            "git_head" to runCatching { ProcessBuilder("git", "rev-parse", "--short", "HEAD").start().inputStream.bufferedReader().readText().trim() }.getOrDefault("?")
        )
        val old = HashMap<String, String>()
        con.createStatement().executeQuery("SELECT key, value FROM run_meta").use { rs -> while (rs.next()) old[rs.getString(1)] = rs.getString(2) }
        val now = java.time.LocalDateTime.now().withNano(0).toString()
        if (old.isEmpty()) {
            con.prepareStatement("INSERT INTO run_meta VALUES (?, ?)").use { ps -> (meta + ("started" to now)).forEach { (k, v) -> ps.setString(1, k); ps.setString(2, v); ps.executeUpdate() } }
        } else {
            val bad = meta.filter { (k, v) -> k != "git_head" && old[k] != v }
            check(bad.isEmpty()) { "[RUN] refused to resume into ${out.path}: produced under a different record: " + bad.map { (k, v) -> "$k: recorded ${old[k]} | now $v" } }
            con.prepareStatement("INSERT OR REPLACE INTO run_meta VALUES ('resumed', ?)").use { ps -> ps.setString(1, ((old["resumed"] ?: "") + ";" + now).trim(';')); ps.executeUpdate() }
        }
        val done = HashSet<Long>()
        con.createStatement().executeQuery("SELECT match_id FROM verdicts").use { rs -> while (rs.next()) done.add(rs.getLong(1)) }
        var todo = ms.filter { it.matchId !in done && shaOf[it.matchId]?.first?.isNotEmpty() == true }
        if (pilot != null) todo = todo.take(pilot)
        println("[RUN] set ${ms.size} | cached ${done.size} | to judge ${todo.size} (${2 * todo.size} calls) | workers $workers | ${out.path} | fingerprint ${rc.fingerprint()} | temperature ${rc.temperatureLabel}")
        val rows = readEvalRows(todo.flatMap { listOf(it.qid to it.modelA, it.qid to it.modelB) })
        val stats = TracePreparation.Stats()
        val sem = Semaphore(workers)
        val lock = Any()
        var ok = 0; var err = 0
        val finishes = java.util.TreeMap<String, Int>()
        runBlocking {
            todo.map { m ->
                async(Dispatchers.Default) {
                    sem.withPermit {
                        try {
                            val ra = rows.getValue(m.qid to m.modelA); val rb = rows.getValue(m.qid to m.modelB)
                            val ta = TracePreparation.robustTrace(ra, "RESOLVED", stats); val tb = TracePreparation.robustTrace(rb, "RESOLVED", stats)
                            val evals: List<DomainEvaluation> = r.service.evaluateWithPrecomputedTraces(
                                query = ra.questionText, options = ra.options, modelA = m.modelA, traceA = ta, modelB = m.modelB, traceB = tb,
                                assignedLeafIds = listOf(m.nodeId), condition = "MAIN", evalQuestionId = m.qid
                            )
                            val e = evals.single()
                            val c1 = e.judgeCalls.first { it.presentationOrder == 1 }; val c2 = e.judgeCalls.first { it.presentationOrder == 2 }
                            check(c1.payloadSha256 == shaOf[m.matchId]!!.first && c2.payloadSha256 == shaOf[m.matchId]!!.second) { "posted sha differs from the precondition sha for match ${m.matchId}" }
                            val winnerName = when (e.winner) { "Model A" -> m.modelA; "Model B" -> m.modelB; else -> e.winner }
                            withContext(Dispatchers.IO) {
                                synchronized(lock) {
                                    con.prepareStatement("INSERT OR REPLACE INTO verdicts VALUES (${"?,".repeat(27)}?)").use { ps ->
                                        var i = 1
                                        ps.setLong(i++, m.matchId); ps.setString(i++, m.modelA); ps.setString(i++, m.modelB); ps.setString(i++, m.nodeId); ps.setInt(i++, m.qid)
                                        ps.setString(i++, c1.anchor); ps.setString(i++, c1.refLetter); ps.setInt(i++, -1)   // ref_correct: not known to the Kotlin side (blindness); joined by the analysis
                                        ps.setString(i++, c1.parsedWinner); ps.setString(i++, c2.parsedWinner); ps.setDouble(i++, c1.confidence); ps.setDouble(i++, c2.confidence)
                                        ps.setString(i++, winnerName); ps.setInt(i++, if (e.positionFlip) 1 else 0); ps.setInt(i++, if (e.winner == "INVALID") 1 else 0)
                                        ps.setString(i++, c1.rawContent); ps.setString(i++, c2.rawContent); ps.setDouble(i++, System.currentTimeMillis() / 1000.0)
                                        ps.setString(i++, c1.finishReason); ps.setString(i++, c2.finishReason)
                                        if (c1.completionTokens == null) ps.setNull(i++, java.sql.Types.INTEGER) else ps.setInt(i++, c1.completionTokens!!)
                                        if (c2.completionTokens == null) ps.setNull(i++, java.sql.Types.INTEGER) else ps.setInt(i++, c2.completionTokens!!)
                                        ps.setString(i++, c1.providerResponseId); ps.setString(i++, c2.providerResponseId)
                                        ps.setString(i++, c1.payloadSha256); ps.setString(i++, c2.payloadSha256); ps.setString(i++, m.stratum); ps.setString(i, m.pairKind)
                                        ps.executeUpdate()
                                    }
                                    JudgeCallStore.insert(con, "JUDGE-WIRING:$setHash", e.judgeCalls)
                                    ok++
                                    finishes.merge(c1.finishReason ?: "(none)", 1, Int::plus); finishes.merge(c2.finishReason ?: "(none)", 1, Int::plus)
                                    if (ok % 25 == 0 || ok + err == todo.size) println("  ${ok + err}/${todo.size} (ok $ok, err $err) | finish_reason $finishes")
                                }
                            }
                        } catch (t: Throwable) {
                            synchronized(lock) { err++; println("  ERROR match ${m.matchId}: ${t.message?.take(160)}") }
                        }
                    }
                }
            }.awaitAll()
        }
        con.close()
        println("[RUN] done: ok $ok, errors $err | skipped by the kit ${r.service.recipeSkipped.get()} | non-terminated calls ${r.service.recipeNonTerminated.get()}${if (err > 0) " (errored matches are not cached; relaunch to resume them)" else ""}")
        println("[RUN] analyse with: python tools/analysis/judge_wiring.py --analyze ${out.path}")
        verifyNoInteractions(r.ranking)
    }
}
