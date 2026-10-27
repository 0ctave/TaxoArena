package taxonomy.dataset

import dev.langchain4j.data.embedding.Embedding
import dev.langchain4j.data.segment.TextSegment
import dev.langchain4j.model.embedding.EmbeddingModel
import dev.langchain4j.model.output.Response
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import taxonomy.config.DatasetType
import taxonomy.config.TaxonomyConfig
import java.io.File
import java.nio.ByteBuffer
import java.nio.file.Files
import java.sql.DriverManager

/**
 * INTENT-TRANSFER-S1 (docs/judge_v2_program.md L22682-L22710; INSTRUMENT "a generic intent DatasetType that fails closed with
 * no Hugging Face fallback"; HYGIENE "build DBs containing TRAIN and GATE rows ONLY" and "the working-copy route").
 *  1. INERT WHEN ABSENT: INTENT is appended LAST; every existing ordinal, table and offset is unchanged (0, 6M..10M); the new
 *     namespace (11M) is disjoint. EmbeddingCache.resolveCacheFile is unchanged for every name the earlier route admitted or
 *     refused, except intent_emb_*.db, which it always refused (asserted on the old messages below).
 *  2. EXECUTION DISCRIMINATOR: fetchIntent runs here on a temp build DB of the exact shape tools/analysis/intent_s1_export.py
 *     writes (asserted values: ids 11,000,000 + s, the formatData category keys, source INTENT, the per-side counts).
 *  3. FAIL-CLOSED: the embedding route absent / not an intent copy / inside the working dir; table absent; no side column; an
 *     EVAL row; meta absent, wrong schema or count mismatch; 0 rows: each REFUSES with its own message.
 *  4. The intent working copy is admitted for the RECORD's tag (the copy is not the DB of record), checked by meta (RAW, the
 *     configured model) and READ-ONLY for vectors: a miss REFUSES and the embedding model is never called.
 *  5. The GATE export's pool id equals the Python mirror's (intent_s1_export.pool_id).
 * Temp DBs only; nothing at the repo root is touched.
 */
class IntentDatasetTypeTest {

    private lateinit var tmp: File

    @BeforeEach
    fun setUp() {
        tmp = Files.createTempDirectory("intent-type").toFile()
    }

    @AfterEach
    fun tearDown() {
        tmp.deleteRecursively()
    }

    // ---- fixtures (the shape intent_s1_export.py writes) ---------------------------------------------------------------

    private data class Row(val s: Int, val text: String, val coarse: String, val side: String)

    private fun buildDb(
        path: File,
        rows: List<Row>?,
        withSide: Boolean = true,
        meta: Map<String, String>? = null,
        metaFromRows: Boolean = true,
        nullableSide: Boolean = false,
    ) {
        DriverManager.getConnection("jdbc:sqlite:${path.absolutePath}").use { c ->
            c.createStatement().use { st ->
                if (rows != null) {
                    st.execute(
                        "CREATE TABLE intent_corpus (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, category TEXT, cot_content TEXT," +
                            " options TEXT, answer TEXT" + (if (withSide) (if (nullableSide) ", side TEXT" else ", side TEXT NOT NULL") else "") + ", fine TEXT, n_items INTEGER)"
                    )
                }
                st.execute("CREATE TABLE eval_question_link (question_id INTEGER PRIMARY KEY, mmlu_pro_row_id INTEGER, question_text TEXT, has_embedding INTEGER DEFAULT 0)")
                st.execute("CREATE TABLE corpus_questions (question_id INTEGER PRIMARY KEY, text TEXT)")
                if (meta != null || metaFromRows) st.execute("CREATE TABLE intent_build_meta (key TEXT PRIMARY KEY, value TEXT)")
            }
            for (r in rows.orEmpty()) {
                val cols = if (withSide) "(id, question, category, cot_content, options, answer, side, fine, n_items) VALUES (?,?,?,'','[]','',?,'f',1)"
                           else "(id, question, category, cot_content, options, answer, fine, n_items) VALUES (?,?,?,'','[]','','f',1)"
                c.prepareStatement("INSERT INTO intent_corpus $cols").use {
                    it.setInt(1, r.s); it.setString(2, r.text); it.setString(3, r.coarse)
                    if (withSide) it.setString(4, r.side)
                    it.executeUpdate()
                }
                c.prepareStatement("INSERT INTO eval_question_link (question_id, mmlu_pro_row_id, question_text, has_embedding) VALUES (?,?,?,0)").use {
                    it.setInt(1, r.s); it.setInt(2, r.s); it.setString(3, r.text); it.executeUpdate()
                }
                c.prepareStatement("INSERT INTO corpus_questions (question_id, text) VALUES (?,?)").use {
                    it.setInt(1, 11_000_000 + r.s); it.setString(2, r.text); it.executeUpdate()
                }
            }
            val m = meta ?: if (metaFromRows) mapOf(
                "schema" to "intent_s1_build/v1", "corpus" to "massive", "arm" to "M-AF", "salt" to "1",
                "n_train" to rows.orEmpty().count { it.side == "TRAIN" }.toString(),
                "n_gate" to rows.orEmpty().count { it.side == "GATE" }.toString()
            ) else null
            if (m != null) for ((k, v) in m) {
                c.prepareStatement("INSERT INTO intent_build_meta VALUES (?, ?)").use { it.setString(1, k); it.setString(2, v); it.executeUpdate() }
            }
        }
    }

    private val rows3 = listOf(
        Row(2, "wake me up at seven", "alarm", "TRAIN"),
        Row(5, "turn the lights off in the kitchen", "iot", "GATE"),
        Row(900, "set an alarm for noon", "alarm", "TRAIN"),
        Row(901, "dim the hall lights", "smart_home", "TRAIN"),
    )

    /** A per-run working copy: intent_emb_qwen3.db in a run directory that is NOT the fetcher's working dir. */
    private fun workingCopy(): File =
        File(File(tmp, "intent_s1_work/run1").apply { mkdirs() }, "intent_emb_qwen3.db").apply { writeText("") }

    private fun fetcher(db: File, explicit: String? = workingCopy().path): MMLUDatasetFetcher {
        val config = TaxonomyConfig()
        config.dataset.datasetType = DatasetType.INTENT
        return MMLUDatasetFetcher(config, "", dbPath = db.absolutePath).also {
            it.reservedJsonFile = File(tmp, "reserved.json")
            it.intentWorkDir = File(tmp, "workdir").apply { mkdirs() }
            it.intentExplicitFileOverride = explicit
        }
    }

    private fun refusal(f: MMLUDatasetFetcher): String =
        assertThrows(IllegalStateException::class.java) { runBlocking { f.fetchDataset(Int.MAX_VALUE) } }.message!!

    // ---- 1. inertness of the enum / registry ---------------------------------------------------------------------------

    @Test
    fun `INTENT is appended last and leaves every existing ordinal, table and offset unchanged`() {
        val before = listOf(DatasetType.MMLU_PRO, DatasetType.MMLU_ORIGINAL, DatasetType.ARC, DatasetType.TWENTY_NEWSGROUPS,
            DatasetType.AG_NEWS, DatasetType.LIVECODEBENCH)
        assertEquals(before, DatasetType.entries.take(6))
        assertEquals(DatasetType.INTENT, DatasetType.entries.last())
        assertEquals(6, DatasetType.INTENT.ordinal)
        assertEquals(
            mapOf("MMLU_PRO" to 0, "MMLU_ORIGINAL" to 6_000_000, "ARC" to 7_000_000, "TWENTY_NEWSGROUPS" to 8_000_000,
                "AG_NEWS" to 9_000_000, "LIVECODEBENCH" to 10_000_000, "INTENT" to 11_000_000),
            CorpusRegistry.BUILTIN_OFFSETS
        )
        val registry = CorpusRegistry()
        assertEquals("intent_corpus", registry.tableFor("INTENT"))
        assertEquals("livecodebench", registry.tableFor("LIVECODEBENCH"))
        assertEquals(11_000_007, CorpusIds.namespaced("INTENT", 7))
        assertEquals("INTENT", CorpusIds.sourceOf(11_000_007))
        assertEquals("LIVECODEBENCH", CorpusIds.sourceOf(10_999_999))
        val offsets = CorpusRegistry.KNOWN_OFFSETS.filterKeys { it != "MMLU_PRO_LB" }.values.toList()
        assertEquals(offsets.size, offsets.toSet().size, "namespaces must stay disjoint: $offsets")
    }

    // ---- 2. the branch executes, with asserted values ------------------------------------------------------------------

    @Test
    fun `the INTENT branch reads the local build table and namespaces ids to 11M plus s`() {
        val db = File(tmp, "intent_build_M-AF.db")
        buildDb(db, rows3)
        val data = runBlocking { fetcher(db).fetchDataset(maxQueries = Int.MAX_VALUE) }
        assertEquals(setOf("Alarm", "Iot", "Smart Home"), data.keys)
        assertEquals(listOf(11_000_002, 11_000_900), data.getValue("Alarm").map { it.id })
        assertEquals(listOf(11_000_005), data.getValue("Iot").map { it.id })
        assertEquals(listOf(11_000_901), data.getValue("Smart Home").map { it.id })
        assertEquals(listOf("wake me up at seven", "set an alarm for noon"), data.getValue("Alarm").map { it.text })
        assertTrue(data.values.flatten().all { it.source == "INTENT" })
        assertEquals(4, data.values.sumOf { it.size })
    }

    // ---- 3. fail-closed ------------------------------------------------------------------------------------------------

    @Test
    fun `the embedding route must be an intent working copy outside the working dir`() {
        val db = File(tmp, "intent_build_M-AF.db")
        buildDb(db, rows3)
        val absent = refusal(fetcher(db, explicit = null).also { it.intentExplicitFileOverride = null })
        assertTrue(absent.contains("[INTENT]") && absent.contains("<absent>"), absent)
        val wrongName = File(tmp, "intent_s1_work/run1/embeddings_cache_embeddinggemma_latest.db").path
        val e2 = refusal(fetcher(db, explicit = wrongName))
        assertTrue(e2.contains("must name an intent_emb_*.db copy"), e2)
        val f3 = fetcher(db)
        val inWd = File(f3.intentWorkDir, "intent_emb_qwen3.db").path
        f3.intentExplicitFileOverride = inWd
        val e3 = refusal(f3)
        assertTrue(e3.contains("lies in the working dir"), e3)
    }

    @Test
    fun `an absent table, a table without side, an EVAL row, bad meta or 0 rows are fatal - no remote fallback`() {
        val absent = File(tmp, "absent.db").also { buildDb(it, null) }
        val e1 = refusal(fetcher(absent))
        assertTrue(e1.contains("[INTENT]") && e1.contains("absent") && e1.contains("no remote fallback"), e1)

        val noSide = File(tmp, "noside.db").also { buildDb(it, rows3, withSide = false) }
        assertTrue(refusal(fetcher(noSide)).contains("has no `side` column"))

        val withEval = File(tmp, "eval.db").also { buildDb(it, rows3 + Row(77, "what time is it in tokyo", "datetime", "EVAL")) }
        val e3 = refusal(fetcher(withEval))
        assertTrue(e3.contains("holds 1 row(s) whose side is not TRAIN or GATE"), e3)

        // a NULL side (a hand-made DB without the exporter's NOT NULL) is not TRAIN or GATE either
        val nullSide = File(tmp, "nullside.db")
        buildDb(nullSide, rows3, nullableSide = true)
        DriverManager.getConnection("jdbc:sqlite:${nullSide.absolutePath}").use { c ->
            c.createStatement().use { it.execute("INSERT INTO intent_corpus (id, question, category, cot_content, options, answer, side, fine, n_items) VALUES (78, 'x y z', 'alarm', '', '[]', '', NULL, 'f', 1)") }
        }
        val e3b = refusal(fetcher(nullSide))
        assertTrue(e3b.contains("holds 1 row(s) whose side is not TRAIN or GATE"), e3b)

        val noMeta = File(tmp, "nometa.db").also { buildDb(it, rows3, metaFromRows = false) }
        assertTrue(refusal(fetcher(noMeta)).contains("has no intent_build_meta table"))

        val badSchema = File(tmp, "schema.db").also {
            buildDb(it, rows3, meta = mapOf("schema" to "intent_s1_build/v0", "n_train" to "3", "n_gate" to "1"))
        }
        assertTrue(refusal(fetcher(badSchema)).contains("is not intent_s1_build/v1"))

        val badCount = File(tmp, "count.db").also {
            buildDb(it, rows3, meta = mapOf("schema" to "intent_s1_build/v1", "n_train" to "3", "n_gate" to "2"))
        }
        val e6 = refusal(fetcher(badCount))
        assertTrue(e6.contains("declares n_train 3 / n_gate 2") && e6.contains("3 TRAIN / 1 GATE"), e6)

        val empty = File(tmp, "empty.db").also { buildDb(it, emptyList()) }
        val e7 = refusal(fetcher(empty))
        assertTrue(e7.contains("0 rows") && e7.contains("no remote fallback"), e7)
    }

    // ---- 4. the embedding working copy ---------------------------------------------------------------------------------

    private fun embDb(f: File, rows: Map<String, FloatArray>, meta: Map<String, String>?) {
        DriverManager.getConnection("jdbc:sqlite:${f.absolutePath}").use { c ->
            c.createStatement().use { it.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)") }
            c.prepareStatement("INSERT INTO embeddings VALUES (?, ?)").use { p ->
                for ((q, v) in rows) {
                    val b = ByteBuffer.allocate(v.size * 4); v.forEach { b.putFloat(it) }
                    p.setString(1, q); p.setBytes(2, b.array()); p.executeUpdate()
                }
            }
            if (meta != null) {
                c.createStatement().use { it.execute("CREATE TABLE intent_meta (key TEXT PRIMARY KEY, value TEXT)") }
                for ((k, v) in meta) c.prepareStatement("INSERT INTO intent_meta VALUES (?, ?)").use { p ->
                    p.setString(1, k); p.setString(2, v); p.executeUpdate()
                }
            }
        }
    }

    private val qwenMeta = mapOf("embedder" to "qwen3", "model" to "qwen3-embedding:latest", "protocol" to "RAW", "native_dim" to "4096")

    @Test
    fun `resolveCacheFile admits an intent working copy for the record's tag, and only under its checks`() {
        val wd = File(tmp, "wd").apply { mkdirs() }
        val run = File(tmp, "intent_s1_work/run1").apply { mkdirs() }
        val copy = File(run, "intent_emb_qwen3.db").also { embDb(it, emptyMap(), qwenMeta) }
        for (tag in listOf("qwen3-embedding", "qwen3-embedding:latest")) {
            assertEquals(copy.absolutePath, EmbeddingCache.resolveCacheFile(tag, copy.path, wd), tag)
        }
        val gem = File(run, "intent_emb_gemma.db").also {
            embDb(it, emptyMap(), mapOf("model" to "embeddinggemma:latest", "protocol" to "RAW"))
        }
        assertEquals(gem.absolutePath, EmbeddingCache.resolveCacheFile("embeddinggemma:latest", gem.path, wd))
        val card = File(run, "intent_emb_qwen3_card.db").also {
            embDb(it, emptyMap(), mapOf("model" to "qwen3-embedding:latest", "protocol" to "CARD"))
        }
        val bare = File(run, "intent_emb_x.db").also { embDb(it, emptyMap(), null) }
        val pinned = File(wd, "intent_emb_qwen3.db").also { embDb(it, emptyMap(), qwenMeta) }
        for ((args, needle) in listOf(
            Triple("embeddinggemma:latest", copy.path, wd) to "holds vectors of model 'qwen3-embedding:latest'",
            Triple("qwen3-embedding:latest", gem.path, wd) to "holds vectors of model 'embeddinggemma:latest'",
            Triple("qwen3-embedding:latest", card.path, wd) to "is not RAW",
            Triple("qwen3-embedding:latest", bare.path, wd) to "has no intent_meta table",
            Triple("qwen3-embedding:latest", pinned.path, wd) to "lies in the JVM's working dir",
            Triple("qwen3-embedding:latest", File(run, "intent_emb_absent.db").path, wd) to "does not exist",
        )) {
            val e = assertThrows(IllegalStateException::class.java) { EmbeddingCache.resolveCacheFile(args.first, args.second, args.third) }
            assertTrue(e.message!!.contains(needle), "${args.second}: ${e.message}")
        }
        // the earlier route is unchanged: the record's tag with a non-intent name is still refused, by the OLD message
        val own = File(run, "embeddings_cache.db").also { embDb(it, emptyMap(), null) }
        val old = assertThrows(IllegalStateException::class.java) { EmbeddingCache.resolveCacheFile("qwen3-embedding:latest", own.path, wd) }
        assertTrue(old.message!!.contains("DB of record is never read"), old.message)
        val gOwn = File(run, "embeddings_cache_embeddinggemma_latest.db").also { embDb(it, emptyMap(), null) }
        assertEquals(gOwn.absolutePath, EmbeddingCache.resolveCacheFile("embeddinggemma:latest", gOwn.path, wd))
        assertTrue(EmbeddingCache.isIntentWorkingCopy(copy.path) && !EmbeddingCache.isIntentWorkingCopy(gOwn.path))
        assertTrue(!EmbeddingCache.isIntentWorkingCopy(File(run, "embeddings_cache_embeddinggemma_latest__card.db").path))
    }

    private class CountingModel : EmbeddingModel {
        var calls = 0
        override fun embedAll(textSegments: MutableList<TextSegment>): Response<MutableList<Embedding>> {
            calls += textSegments.size
            return Response.from(textSegments.map { Embedding.from(FloatArray(4096) { 0.5f }) }.toMutableList())
        }
    }

    @Test
    fun `an intent working copy is read-only for vectors - a miss REFUSES, the model is never called`() {
        // not @TempDir / not tmp: EmbeddingCache holds its SQLite connection open for the JVM's life (no close()); a plain temp
        // dir, removed best-effort at exit
        val run = taxonomy.TestTmp.dir("intent_emb_run")
        val v = FloatArray(4096) { it / 4096f }
        val copy = File(run, "intent_emb_qwen3.db").also { embDb(it, mapOf("wake me up at seven" to v), qwenMeta) }
        val prop = EmbeddingCache.PROP_EXPLICIT_FILE
        val saved = System.getProperty(prop)
        val model = CountingModel()
        System.setProperty(prop, copy.path)
        try {
            val cache = EmbeddingCache(TaxonomyConfig().also { it.llm.embeddingModel = "qwen3-embedding:latest" }, model)
            assertArrayEquals(v, cache.get("wake me up at seven"))
            assertArrayEquals(v, runBlocking { cache.getOrCreate("wake me up at seven") })
            val e1 = assertThrows(IllegalStateException::class.java) { runBlocking { cache.getOrCreate("missing") } }
            assertTrue(e1.message!!.contains("intent working copy") && e1.message!!.contains("never embeds"), e1.message)
            val e2 = assertThrows(IllegalStateException::class.java) {
                runBlocking { cache.precompute(listOf("wake me up at seven", "missing", "missing2")) }
            }
            assertTrue(e2.message!!.contains("2 text(s)"), e2.message)
            runBlocking { cache.precompute(listOf("wake me up at seven")) }       // nothing missing: no refusal
        } finally {
            if (saved == null) System.clearProperty(prop) else System.setProperty(prop, saved)
        }
        assertEquals(0, model.calls, "the JVM embedded nothing into an intent working copy")
    }

    // ---- 5. the pool id mirror -----------------------------------------------------------------------------------------

    @Test
    fun `a GATE export with bare keys hashes to the Python mirror's pool id`() {
        // tools/analysis/intent_s1_export.pool_id({"Alarm": [11000002, 11000900], "Smart Home": [11000901]}), printed by its
        // --selftest (case "pool id mirror")
        assertEquals(PY_POOL_ID,
            ReservedPool.computePoolId(mapOf("Alarm" to listOf(11_000_002, 11_000_900), "Smart Home" to listOf(11_000_901))))
    }

    companion object {
        const val PY_POOL_ID = "pc8348bc89a58bcc5"
    }
}
