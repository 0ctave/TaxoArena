package taxonomy.dataset

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.sql.DriverManager
import taxonomy.config.TaxonomyConfig
import taxonomy.config.DatasetType

private const val EXPECTED_MMLU_PRO_CATEGORIES = 14

@Service
class MMLUDatasetFetcher(
    private val config: TaxonomyConfig,
    @Value("\${huggingface.token:}") private val hfToken: String,
    // Stage 0a (docs/multi_corpus_design.md): the dataset DB path is the same property the eval
    // store, loader and validator already read, so a TOML `corpusDbPath` reaches all four beans
    // through one setting; the default is the path this fetcher always hard-coded.
    @Value("\${taxoadapt.eval.db-path:mmlu_pro_dataset_cache_v2.db}")
    private val dbPath: String = CorpusRegistry.DEFAULT_CORPUS_DB_PATH,
    private val corpusRegistry: CorpusRegistry = CorpusRegistry()
) {
    var onDownloadProgress: ((current: Int, total: Int, datasetName: String) -> Unit)? = null
    private val log = LoggerFactory.getLogger("taxonomy.DatasetFetcher")

    /** The split transport at the repo root (what saveSnapshot, trickle and the TUI read); tests point it elsewhere. */
    internal var reservedJsonFile: java.io.File = java.io.File("reserved_test_queries.json")

    companion object {
        /** Sentinel cap meaning "pull the whole dataset" (no caller-imposed row limit). */
        const val UNBOUNDED_MAX_QUERIES: Int = Int.MAX_VALUE

        /**
         * Resolve the value to report as the progress *total*. A real, bounded cap is a
         * meaningful denominator; the [UNBOUNDED_MAX_QUERIES] sentinel (or a non-positive
         * cap) is not, so we report 0 to signal "unknown total" and let the UI fall back to
         * an indeterminate bar instead of dividing by Int.MAX_VALUE.
         */
        fun resolveProgressTotal(maxQueries: Int): Int =
            if (maxQueries in 1 until UNBOUNDED_MAX_QUERIES) maxQueries else 0
    }
    private val json = Json { ignoreUnknownKeys = true; isLenient = true; coerceInputValues = true }
    private val dbUrl = "jdbc:sqlite:$dbPath?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000"

    private val isTest = System.getProperty("org.gradle.test.worker") != null ||
            System.getProperty("java.class.path")?.contains("junit") == true

    private val dbLock = Any()
    private val sharedConnection: java.sql.Connection by lazy {
        DriverManager.getConnection(dbUrl).also { conn ->
            conn.autoCommit = true
        }
    }

    private val connection: java.sql.Connection
        get() {
            if (isTest) {
                return DriverManager.getConnection(dbUrl).also { conn ->
                    conn.autoCommit = true
                }
            }
            return java.lang.reflect.Proxy.newProxyInstance(
                java.sql.Connection::class.java.classLoader,
                arrayOf(java.sql.Connection::class.java)
            ) { _, method, args ->
                if (method.name == "close") {
                    null
                } else {
                    synchronized(dbLock) {
                        try {
                            method.invoke(sharedConnection, *(args ?: emptyArray()))
                        } catch (e: java.lang.reflect.InvocationTargetException) {
                            throw e.cause ?: e
                        }
                    }
                }
            } as java.sql.Connection
        }

    init {
        initDatabase()
        // One CorpusSource per DatasetType, each a thin adapter over this fetcher's own methods;
        // the registry is the dispatch table the two former `when (datasetType)` blocks used.
        DatasetType.entries.forEach { type ->
            corpusRegistry.register(MmluProCorpusSource(this, type, corpusRegistry.tableFor(type.name)))
        }
        // Stage 1: the leaderboard corpora read the multi-corpus DB at this same path. Registering
        // touches no file; a source only opens the DB when a run actually lists it.
        CorpusRegistry.LEADERBOARD.values.forEach { d ->
            corpusRegistry.register(LeaderboardCorpusSource(dbPath, d))
        }
        if (!isTest) {
            try {
                Runtime.getRuntime().addShutdownHook(Thread {
                    runCatching {
                        synchronized(dbLock) {
                            if (!sharedConnection.isClosed) {
                                sharedConnection.close()
                                log.info("SQLite dataset fetcher database connection closed cleanly via shutdown hook.")
                            }
                        }
                    }
                })
            } catch (_: Exception) {}
        }
    }

    private fun initDatabase() {
        try {
            connection.use { conn ->
                conn.createStatement().use { stmt ->
                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS mmlu_pro (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT,
                            category TEXT,
                            cot_content TEXT,
                            options TEXT,
                            answer TEXT
                        )
                    """.trimIndent())
                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS mmlu_original (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT,
                            category TEXT,
                            cot_content TEXT,
                            options TEXT,
                            answer TEXT
                        )
                    """.trimIndent())
                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS arc (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT,
                            category TEXT,
                            cot_content TEXT,
                            options TEXT,
                            answer TEXT
                        )
                    """.trimIndent())
                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS twenty_newsgroups (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT,
                            category TEXT,
                            cot_content TEXT,
                            options TEXT,
                            answer TEXT
                        )
                    """.trimIndent())
                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS ag_news (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT,
                            category TEXT,
                            cot_content TEXT,
                            options TEXT,
                            answer TEXT
                        )
                    """.trimIndent())
                    stmt.execute("""
                        CREATE TABLE IF NOT EXISTS eval_question_link (
                            question_id      INTEGER PRIMARY KEY,
                            mmlu_pro_row_id  INTEGER,
                            question_text    TEXT,
                            has_embedding    INTEGER DEFAULT 0
                        )
                    """.trimIndent())
                }
            }
            log.info("SQLite cache tables initialized successfully.")
        } catch (e: Exception) {
            log.error("Failed to initialize SQLite database.", e)
        }
    }

    /**
     * The sources this run draws on (docs/multi_corpus_design.md §3.1): `dataset.corpora` when a
     * config lists leaderboard corpora, else the single `datasetType` — every pre-stage-1 run.
     */
    fun activeSources(): List<String> =
        config.dataset.corpora.ifEmpty { listOf(config.dataset.datasetType.name) }

    private val isMultiCorpus: Boolean get() = config.dataset.corpora.isNotEmpty()

    /** Root label of the construction: `datasetType.name` (unchanged) or the sources joined by `+`. */
    fun datasetLabel(): String =
        if (isMultiCorpus) config.dataset.corpora.joinToString("+") else config.dataset.datasetType.name

    private fun getTableName(): String = corpusRegistry.tableFor(activeSources().first())

    /** `reserved_pool_meta.dataset`: the table name for single-corpus runs (as always), the union label otherwise. */
    private fun poolDatasetName(): String = if (isMultiCorpus) datasetLabel() else getTableName()

    fun isDatasetDownloaded(): Boolean {
        if (isMultiCorpus) {
            // Leaderboard corpora are never downloaded here: the multi-corpus DB is built by
            // tools/ingest/multicorpus_db.py. "Downloaded" means every listed source has rows.
            return config.dataset.corpora.all { name ->
                (corpusRegistry.source(name) as? LeaderboardCorpusSource)?.rowCount()?.let { it > 0 } ?: false
            }
        }
        val table = getTableName()
        return getDbCount(table) > 0
    }

    suspend fun downloadDataset(maxQueries: Int = 12000) {
        fetchDataset(maxQueries = maxQueries, selectedDomains = emptyList())
    }

    suspend fun fetchDataset(maxQueries: Int = 12000, selectedDomains: List<String> = emptyList()): Map<String, List<MMLUQuery>> {
        // Registry dispatch (stage 0a). The adapter returns CorpusQuery; converting back keeps
        // this method's contract and its map/list order exactly as the former `when` produced.
        // Stage 1: a run over `corpora` fetches each source in the listed order and merges the
        // maps. Leaderboard keys are `<SOURCE>/<domain>` (CorpusDomains), so they cannot collide;
        // ids are namespaced (`id_offset + upstream_id`) so they match the multi-corpus DB's
        // eval_results. For MMLU_PRO (offset 0) the id is the upstream id verbatim, sentinels
        // included — the single-corpus path is byte-identical.
        val result = LinkedHashMap<String, List<MMLUQuery>>()
        val perSource = mutableListOf<String>()
        for (name in activeSources()) {
            val part = corpusRegistry.source(name).fetch(maxQueries, selectedDomains)
            for ((domain, qs) in part) {
                require(domain !in result) {
                    "[CORPUS] domain key '$domain' of '$name' collides with an earlier source's key"
                }
                result[domain] = qs.map {
                    MMLUQuery(
                        id = CorpusIds.namespacedOrSentinel(it.source, it.upstreamId),
                        text = it.text, category = it.domain, source = it.source
                    )
                }
            }
            perSource += "$name=${part.size} domain(s)/${part.values.sumOf { it.size }} queries"
        }
        if (isMultiCorpus) {
            log.info("[CORPUS] merged ${activeSources().size} source(s): ${perSource.joinToString(", ")} -> ${result.size} domain key(s), ${result.values.sumOf { it.size }} queries")
        }

        result.values.flatten().forEach { query ->
            taxonomy.model.QuestionIdRegistry.register(query.text, query.id)
        }

        return result
    }

    internal suspend fun fetchMmluPro(maxQueries: Int, selectedDomains: List<String>): Map<String, List<MMLUQuery>> {
        val table = "mmlu_pro"
        val limit = maxQueries
        val totalInDb = getDbCount(table)
        val allRows = loadFromDb(table, limit, selectedDomains)

        if (selectedDomains.isNotEmpty()) {
            log.info("Loaded ${allRows.size} MMLU Pro queries from local cache for domains: ${selectedDomains.joinToString(", ")}.")
            return finalizeData(allRows.take(maxQueries), "MMLU Pro")
        }

        val cachedDistinctCategories = allRows.mapNotNull { it.category }.toSet().size
        if (cachedDistinctCategories >= EXPECTED_MMLU_PRO_CATEGORIES && (allRows.size >= 1000 || allRows.size >= maxQueries)) {
            log.info("Loaded MMLU Pro from cache: ${allRows.size} queries across $cachedDistinctCategories categories.")
            return finalizeData(allRows, "MMLU Pro")
        }

        log.info("MMLU Pro cache incomplete ($cachedDistinctCategories/$EXPECTED_MMLU_PRO_CATEGORIES categories, ${allRows.size} rows). Fetching remainder from offset ${getDbCount(table)}…")

        val client = HttpClient.newBuilder()
            .connectTimeout(java.time.Duration.ofSeconds(10))
            .build()
        var hfOffset = totalInDb
        val batchSize = 100

        var retries = 0
        val maxRetries = 10
        var waitTime = 2000L

        log.info("Downloading MMLU Pro dataset from Hugging Face...")
        while (allRows.size < maxQueries) {
            val limitVal = minOf(batchSize, maxQueries - allRows.size)
            val url = "https://datasets-server.huggingface.co/rows?dataset=TIGER-Lab%2FMMLU-Pro&config=default&split=test&offset=$hfOffset&length=$limitVal"

            val requestBuilder = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .timeout(java.time.Duration.ofSeconds(15))
                .GET()
            if (hfToken.isNotBlank()) {
                requestBuilder.header("Authorization", "Bearer $hfToken")
            }
            val request = requestBuilder.build()

            val response = withContext(Dispatchers.IO) { client.send(request, HttpResponse.BodyHandlers.ofString()) }

            if (response.statusCode() == 429) {
                if (retries >= maxRetries) break
                kotlinx.coroutines.delay(waitTime)
                waitTime *= 2
                retries++
                continue
            }

            if (response.statusCode() != 200) break

            try {
                val hfResponse = json.decodeFromString<HFProDatasetResponse>(response.body())
                if (hfResponse.rows.isEmpty()) break

                val newRows = hfResponse.rows.map { rowItem ->
                    val row = rowItem.row
                    row.copy(cot_content = row.cot_content ?: "")
                }
                saveBatchToDb(table, newRows)

                allRows.addAll(newRows)
                hfOffset += limitVal
                retries = 0
                waitTime = 2000L

                val progressTotal = resolveProgressTotal(maxQueries)
                printProgressBar(allRows.size, progressTotal, "MMLU Pro Download Progress")
                onDownloadProgress?.invoke(allRows.size, progressTotal, "MMLU Pro")
            } catch (e: Exception) {
                log.error("Failed parsing MMLU Pro row items", e)
                break
            }
        }

        return finalizeData(allRows.take(maxQueries), "MMLU Pro")
    }

    internal suspend fun fetchMmluOriginal(maxQueries: Int, selectedDomains: List<String>): Map<String, List<MMLUQuery>> {
        val table = "mmlu_original"
        val limit = if (selectedDomains.isNotEmpty()) 100000 else maxQueries
        val allRows = loadFromDb(table, limit, selectedDomains)

        if (selectedDomains.isNotEmpty() || allRows.size >= maxQueries || allRows.size >= 5000) {
            return finalizeData(allRows.take(maxQueries), "MMLU Original")
        }

        log.info("MMLU Original local cache insufficient (${allRows.size}). Fetching from HF datasets server...")
        val client = HttpClient.newHttpClient()
        val subjects = listOf(
            "abstract_algebra", "anatomy", "astronomy", "business_ethics", "clinical_knowledge", 
            "college_biology", "college_chemistry", "college_computer_science", "college_mathematics", 
            "college_medicine", "college_physics", "computer_security", "conceptual_physics", 
            "econometrics", "electrical_engineering", "elementary_mathematics", "formal_logic", 
            "global_facts", "high_school_biology", "high_school_chemistry", "high_school_computer_science", 
            "high_school_european_history", "high_school_geography", "high_school_government_and_politics", 
            "high_school_macroeconomics", "high_school_mathematics", "high_school_microeconomics", 
            "high_school_physics", "high_school_psychology", "high_school_statistics", 
            "high_school_us_history", "high_school_world_history", "human_aging", "human_sexuality", 
            "international_law", "jurisprudence", "logical_fallacies", "machine_learning", "management", 
            "marketing", "medical_genetics", "miscellaneous", "moral_disputes", "moral_scenarios", 
            "nutrition", "philosophy", "prehistory", "professional_accounting", "professional_law", 
            "professional_medicine", "professional_psychology", "public_relations", "security_studies", 
            "sociology", "us_foreign_policy", "virology", "world_religions"
        )

        val newRows = mutableListOf<HFProRowData>()
        var countFetched = 0

        for (subject in subjects) {
            if (allRows.size + newRows.size >= maxQueries) break
            val domain = MMLUCategories.SUBJECT_TO_DOMAIN[subject] ?: "other"
            
            val url = "https://datasets-server.huggingface.co/rows?dataset=cais/mmlu&config=$subject&split=test&offset=0&length=100"
            val requestBuilder = HttpRequest.newBuilder().uri(URI.create(url)).GET()
            if (hfToken.isNotBlank()) {
                requestBuilder.header("Authorization", "Bearer $hfToken")
            }
            val request = requestBuilder.build()

            try {
                val response = withContext(Dispatchers.IO) { client.send(request, HttpResponse.BodyHandlers.ofString()) }
                if (response.statusCode() == 200) {
                    val mmluResponse = json.decodeFromString<HFMMLUResponse>(response.body())
                    val subjectRows = mmluResponse.rows.map { item ->
                        val r = item.row
                        HFProRowData(
                            question = r.question,
                            category = domain,
                            cot_content = "",
                            options = r.choices,
                            answer = when(r.answer) {
                                0 -> "A"
                                1 -> "B"
                                2 -> "C"
                                3 -> "D"
                                else -> r.answer.toString()
                            }
                        )
                    }
                    newRows.addAll(subjectRows)
                    countFetched++
                    printProgressBar(countFetched, subjects.size, "MMLU Original Subjects Download")
                    onDownloadProgress?.invoke(countFetched, subjects.size, "MMLU Original")
                } else {
                    log.warn("Failed fetching $subject subset: HTTP ${response.statusCode()}")
                }
            } catch (e: Exception) {
                log.error("Error fetching MMLU Original $subject subset", e)
            }
            kotlinx.coroutines.delay(100)
        }

        if (newRows.isNotEmpty()) {
            saveBatchToDb(table, newRows)
            allRows.addAll(newRows)
        }

        return finalizeData(allRows.take(maxQueries), "MMLU Original")
    }

    internal suspend fun fetchArc(maxQueries: Int, selectedDomains: List<String>): Map<String, List<MMLUQuery>> {
        val table = "arc"
        val limit = if (selectedDomains.isNotEmpty()) 100000 else maxQueries
        val allRows = loadFromDb(table, limit, selectedDomains)

        if (selectedDomains.isNotEmpty() || allRows.size >= maxQueries || allRows.size >= 2000) {
            return finalizeData(allRows.take(maxQueries), "ARC")
        }

        log.info("ARC local cache insufficient (${allRows.size}). Fetching from HF datasets server...")
        val client = HttpClient.newHttpClient()
        val configs = listOf("ARC-Challenge", "ARC-Easy")
        val newRows = mutableListOf<HFProRowData>()

        for (configName in configs) {
            val category = if (configName == "ARC-Challenge") "arc challenge" else "arc easy"
            var offset = 0
            val batchSize = 100
            val maxBatches = 10 

            for (batch in 0 until maxBatches) {
                if (allRows.size + newRows.size >= maxQueries) break

                val url = "https://datasets-server.huggingface.co/rows?dataset=allenai/ai2_arc&config=$configName&split=test&offset=$offset&length=$batchSize"
                val requestBuilder = HttpRequest.newBuilder().uri(URI.create(url)).GET()
                if (hfToken.isNotBlank()) {
                    requestBuilder.header("Authorization", "Bearer $hfToken")
                }
                val request = requestBuilder.build()

                try {
                    val response = withContext(Dispatchers.IO) { client.send(request, HttpResponse.BodyHandlers.ofString()) }
                    if (response.statusCode() == 200) {
                        val arcResponse = json.decodeFromString<HFArcResponse>(response.body())
                        if (arcResponse.rows.isEmpty()) break

                        val subjectRows = arcResponse.rows.map { item ->
                            val r = item.row
                            HFProRowData(
                                question = r.question.stem,
                                category = category,
                                cot_content = "",
                                options = r.choices.text,
                                answer = r.answerKey
                            )
                        }
                        newRows.addAll(subjectRows)
                        offset += batchSize
                        log.info("Fetched batch ${batch + 1} for $configName (${subjectRows.size} rows)")
                        onDownloadProgress?.invoke(allRows.size + newRows.size, resolveProgressTotal(maxQueries), "ARC")
                        if (subjectRows.size < batchSize) break
                    } else {
                        log.warn("Failed fetching $configName batch: HTTP ${response.statusCode()}")
                        break
                    }
                } catch (e: Exception) {
                    log.error("Error fetching ARC $configName batch", e)
                    break
                }
                kotlinx.coroutines.delay(100)
            }
        }

        if (newRows.isNotEmpty()) {
            saveBatchToDb(table, newRows)
            allRows.addAll(newRows)
        }

        return finalizeData(allRows.take(maxQueries), "ARC")
    }

    private fun loadFromDb(table: String, limit: Int, selectedDomains: List<String> = emptyList()): MutableList<HFProRowData> {
        val rows = mutableListOf<HFProRowData>()
        try {
            connection.use { conn ->
                val sql = if (selectedDomains.isEmpty()) {
                    "SELECT m.id, m.question, m.category, m.cot_content, m.options, m.answer, l.question_id " +
                    "FROM $table m LEFT JOIN eval_question_link l ON m.id = l.mmlu_pro_row_id " +
                    "ORDER BY m.id ASC LIMIT ?"
                } else {
                    val rawDomains = selectedDomains.map { it.trim().lowercase() }
                    val placeholders = rawDomains.joinToString(",") { "?" }
                    "SELECT m.id, m.question, m.category, m.cot_content, m.options, m.answer, l.question_id " +
                    "FROM $table m LEFT JOIN eval_question_link l ON m.id = l.mmlu_pro_row_id " +
                    "WHERE m.category IN ($placeholders) ORDER BY m.id ASC LIMIT ?"
                }
                conn.prepareStatement(sql).use { pstmt ->
                    if (selectedDomains.isEmpty()) {
                        pstmt.setInt(1, limit)
                    } else {
                        val rawDomains = selectedDomains.map { it.trim().lowercase() }
                        rawDomains.forEachIndexed { index, domain ->
                            pstmt.setString(index + 1, domain)
                        }
                        pstmt.setInt(rawDomains.size + 1, limit)
                    }
                    val rs = pstmt.executeQuery()
                    var unlinked = 0
                    val joinPairs = ArrayList<Pair<Int, Int?>>()
                    while (rs.next()) {
                        val upstreamId = rs.getInt("question_id")
                        val upstreamNull = rs.wasNull()
                        val localRowId = rs.getInt("id")
                        joinPairs.add(localRowId to (if (upstreamNull) null else upstreamId))
                        // `mmlu_pro.id` is a local AUTOINCREMENT rowid (1..12000);
                        // `eval_results.question_id` is the upstream MMLU-Pro id (70..12256).
                        // The two spaces overlap numerically and mean nothing to each other, so
                        // falling back to the local rowid here handed downstream code an id it
                        // reads as an upstream one: an unlinked question then joined to whatever
                        // unrelated eval row happened to share the number. Every one of a
                        // Math-only run's 405 reserved ids resolved to a different question that
                        // way. Unlinked rows now get a negative sentinel instead — unique, so
                        // clustering identity is preserved, and unable to match any eval
                        // question_id, so the join fails loudly rather than silently lying.
                        val finalId = if (upstreamNull || upstreamId <= 0) {
                            unlinked++
                            UNLINKED_QUERY_ID_BASE - localRowId
                        } else upstreamId
                        rows.add(HFProRowData(
                            id = finalId,
                            question = rs.getString("question"),
                            category = rs.getString("category"),
                            cot_content = rs.getString("cot_content"),
                            options = json.decodeFromString(rs.getString("options")),
                            answer = rs.getString("answer")
                        ))
                    }
                    // JOIN-CARDINALITY-GUARD: one local row, at most one link row (fatal otherwise; see the guard).
                    JoinCardinalityGuard.assertAtMostOnePerLocalRow(table, joinPairs)
                    if (unlinked > 0) {
                        log.warn(
                            "[EVAL-LINK] $unlinked of ${rows.size} $table rows have no eval_question_link" +
                                " entry and carry a sentinel id. They can take part in construction but" +
                                " NOT in the arena, which needs a real eval question_id."
                        )
                    }
                }
            }
        } catch (e: JoinCardinalityException) {
            throw e
        } catch (e: Exception) {
            log.error("Failed to load from SQLite cache ($table)", e)
        }
        return rows
    }

    fun getDetailsForQuery(question: String): HFProRowData? {
        if (isMultiCorpus) return getDetailsForQueries(listOf(question))[question]
        val table = getTableName()
        try {
            connection.use { conn ->
                conn.prepareStatement("SELECT question, category, cot_content, options, answer FROM $table WHERE question = ?").use { pstmt ->
                    pstmt.setString(1, question)
                    val rs = pstmt.executeQuery()
                    if (rs.next()) {
                        return HFProRowData(
                            question = rs.getString("question"),
                            category = rs.getString("category"),
                            cot_content = rs.getString("cot_content"),
                            options = json.decodeFromString(rs.getString("options")),
                            answer = rs.getString("answer")
                        )
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to get query details from SQLite ($table)", e)
        }
        return null
    }

    fun getDetailsForQueries(questions: List<String>): Map<String, HFProRowData> {
        if (questions.isEmpty()) return emptyMap()
        if (isMultiCorpus) {
            // Each listed source answers for its own texts; the first source to know a text wins.
            val out = LinkedHashMap<String, HFProRowData>()
            for (name in activeSources()) {
                val missing = questions.filter { it !in out }
                if (missing.isEmpty()) break
                out.putAll(corpusRegistry.source(name).detailsFor(missing))
            }
            return out
        }
        val table = getTableName()
        val result = mutableMapOf<String, HFProRowData>()
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                val placeholders = questions.joinToString(",") { "?" }
                conn.prepareStatement(
                    "SELECT question, category, cot_content, options, answer FROM $table WHERE question IN ($placeholders)"
                ).use { pstmt ->
                    questions.forEachIndexed { i, q -> pstmt.setString(i + 1, q) }
                    val rs = pstmt.executeQuery()
                    while (rs.next()) {
                        val row = HFProRowData(
                            question = rs.getString("question"),
                            category = rs.getString("category"),
                            cot_content = rs.getString("cot_content"),
                            options = json.decodeFromString(rs.getString("options")),
                            answer = rs.getString("answer")
                        )
                        result[row.question] = row
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to batch-get query details from SQLite ($table)", e)
        }
        return result
    }

    private fun getDbCount(table: String): Int {
        try {
            connection.use { conn ->
                conn.createStatement().use { stmt ->
                    val rs = stmt.executeQuery("SELECT COUNT(*) FROM $table")
                    if (rs.next()) return rs.getInt(1)
                }
            }
        } catch (e: Exception) {
            log.error("Failed to get count from SQLite ($table)", e)
        }
        return 0
    }

    private fun saveBatchToDb(table: String, rows: List<HFProRowData>) {
        try {
            connection.use { conn ->
                conn.autoCommit = false
                try {
                    conn.prepareStatement("INSERT INTO $table (question, category, cot_content, options, answer) VALUES (?, ?, ?, ?, ?)").use { pstmt ->
                        for (row in rows) {
                            pstmt.setString(1, row.question)
                            pstmt.setString(2, row.category)
                            pstmt.setString(3, row.cot_content)
                            pstmt.setString(4, json.encodeToString(row.options))
                            pstmt.setString(5, row.answer)
                            pstmt.addBatch()
                        }
                        pstmt.executeBatch()
                    }
                    conn.commit()
                } catch (e: Exception) {
                    conn.rollback()
                    throw e
                }
            }
        } catch (e: Exception) {
            log.error("Failed to save batch to SQLite ($table)", e)
        }
    }

    private fun finalizeData(rows: List<HFProRowData>, datasetName: String): Map<String, List<MMLUQuery>> {
        val formattedData = formatData(rows)
        log.info("Fetched ${rows.size} $datasetName queries across ${formattedData.keys.size} categories.")
        return formattedData
    }

    private fun formatData(rows: List<HFProRowData>): Map<String, List<MMLUQuery>> {
        return rows.filter { it.question.isNotBlank() }.groupBy { row ->
            val cat = row.category ?: "Unknown"
            cat.split("_", "-").joinToString(" ") { word ->
                word.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
            }
        }.mapValues { entry ->
            entry.value.mapIndexed { idx, it ->
                // `id = -1` is the HFProRowData default, used by the datasets that carry no id
                // of their own (ARC, 20 Newsgroups, AG News) — those still fall back to the
                // positional index. Sentinels from loadFromDb are far more negative and must
                // survive intact, or unlinked questions would be renumbered onto small indices
                // and collide with each other.
                val finalId = if (it.id >= 0 || it.id <= UNLINKED_QUERY_ID_BASE) it.id else idx
                MMLUQuery(id = finalId, text = it.question, category = entry.key)
            }
        }
    }

    private fun printProgressBar(current: Int, total: Int, prefix: String) {
        val width = 40
        val progress = if (total > 0) (current.toDouble() / total) else 0.0
        val filled = (progress * width).toInt()
        val bar = "#".repeat(filled) + "-".repeat(width - filled)
        val percent = (progress * 100).toInt()
        print("\r$prefix: [$bar] $percent% ($current/$total)")
        if (current >= total) println()
    }

    /**
     * A split's result. [train] and [test] are what construction and routing consume; [gate] is
     * the GATE slice of TRAIN (ids whose stem-key hash lands in [SplitSide.GATE_LOWER, GATE_UPPER)),
     * disjoint from every test id by assertion; [poolId] is the content id of the judgeable test
     * ids as recorded in `reserved_pool` (null only when no test id is judgeable). Destructures as
     * `(train, test)` for the callers that only route.
     */
    data class Split(
        val train: Map<String, List<MMLUQuery>>,
        val test: Map<String, List<MMLUQuery>>,
        val gate: Set<Int>,
        val poolId: String?,
        /** Items moved from TRAIN to TEST because their text equals a test item's text (content closure). */
        val closedByContent: Int = 0
    )

    /**
     * Domain-stratified random train/test split: each domain contributes the SAME [testRatio]
     * fraction to the test set (balanced across domains), and both sets are drawn at random.
     * By default the seed is fresh per call so the split is non-deterministic; pass [seed] for
     * a reproducible split. The reserved test set is written to reserved_test_queries.json so
     * it travels with the DAG snapshot and is never seen during generation.
     *
     * The id partition is exactly the historical one (a seed still reproduces its pool id);
     * [finishSplit] then closes TRAIN under content equality, computes GATE and asserts every
     * item's side (FRAMEWORK item 18).
     */
    fun splitTrainTest(
        dataset: Map<String, List<MMLUQuery>>,
        testRatio: Double = 0.2,
        seed: Long = java.util.concurrent.ThreadLocalRandom.current().nextLong(),
    ): Split {
        val train = mutableMapOf<String, List<MMLUQuery>>()
        val test = mutableMapOf<String, List<MMLUQuery>>()
        val rng = java.util.Random(seed)
        for ((category, queries) in dataset) {
            val total = queries.size
            // Round the per-domain test count so every domain gives ~testRatio to test,
            // keeping at least one train query.
            val testCount = Math.round(total * testRatio).toInt().coerceIn(0, (total - 1).coerceAtLeast(0))
            val trainCount = (total - testCount).coerceAtLeast(1)
            val shuffled = queries.shuffled(rng)
            val trainQueries = shuffled.take(trainCount)
            val testQueries = shuffled.drop(trainCount)

            train[category] = trainQueries
            if (testQueries.isNotEmpty()) {
                test[category] = testQueries
            }
        }
        log.info(
            "Train/test split (ratio=$testRatio, seed=$seed): " +
                "${train.values.sumOf { it.size }} train / ${test.values.sumOf { it.size }} test " +
                "across ${dataset.size} domains."
        )

        val testIds: Map<String, List<Int>> = test.mapValues { (_, qs) -> qs.map { it.id } }
        try {
            val file = reservedJsonFile
            val prettyJson = Json { prettyPrint = true }
            file.writeText(prettyJson.encodeToString(testIds))
            // Sentinel ids (see UNLINKED_QUERY_ID_BASE) belong in the split — held-out routing
            // metrics are computed over them — but they match no eval_results row, so they can
            // never be judged. Reporting only the total overstated the judgeable pool:
            // 3599 written, 3437 actually reservable.
            val total = test.values.sumOf { it.size }
            val judgeable = test.values.flatten().count { it.id > 0 }
            log.info(
                "Successfully reserved $total test queries across ${test.size} domains to" +
                    " reserved_test_queries.json ($judgeable arena-judgeable," +
                    " ${total - judgeable} unlinked and routing-only)."
            )
        } catch (e: Exception) {
            log.error("Failed to save reserved test queries to file", e)
        }
        // Record the pool durably, here, where the provenance actually exists — the seed,
        // ratio and corpus size are known at split time and nowhere downstream. The JSON
        // above is an export for inspection; this table is the source of truth, and because
        // the id is a hash of the contents, an id file listing the same ids resolves to
        // exactly this pool rather than creating a second copy of it.
        val poolId = recordPool(testIds, dataset, seed = seed, testRatio = testRatio, origin = "seed=$seed, ratio=$testRatio")
        return finishSplit(train, test, testIds, poolId)
    }

    /**
     * Train/test split from an EXPLICIT held-out id file (the reserved_test_queries.json format:
     * domain -> ids, sentinels included) instead of a seed. A seed does not reproduce a split
     * once the dataset's load order changes (2026-09-09: today's seed-42 split differs from the
     * frozen pool by 70%), so a construction that must be judged on an existing pool takes
     * that pool's ids directly. The file is copied to reserved_test_queries.json verbatim so
     * the snapshot stores exactly this pool, and the pool is recorded (never activated). Content
     * closure adds routing-only test members without touching the judgeable id list, so the
     * recorded pool id is the file's.
     */
    fun splitByReservedFile(
        dataset: Map<String, List<MMLUQuery>>,
        reservedFile: java.io.File,
    ): Split {
        val idsByDomain: Map<String, List<Int>> = Json.decodeFromString(reservedFile.readText())
        val held = idsByDomain.values.flatten().toHashSet()
        val train = mutableMapOf<String, List<MMLUQuery>>()
        val test = mutableMapOf<String, List<MMLUQuery>>()
        for ((category, queries) in dataset) {
            val (t, tr) = queries.partition { it.id in held }
            train[category] = tr
            if (t.isNotEmpty()) test[category] = t
        }
        val found = test.values.sumOf { it.size }
        log.info(
            "Train/test split from reserved file '${reservedFile.name}': ${train.values.sumOf { it.size }} train /" +
                " $found test (file lists ${held.size} ids; ${held.size - found} not present in the loaded dataset)."
        )
        reservedJsonFile.writeText(reservedFile.readText())
        val poolId = recordPool(idsByDomain, dataset, seed = null, testRatio = null, origin = "file ${reservedFile.name}")
        return finishSplit(train, test, idsByDomain, poolId)
    }

    /**
     * RP12 ARCH-V2-E-T: the split of a v2 pool, taken AS GIVEN from the engine pool file ([V2EnginePool],
     * written by tools/analysis/v2_engine_pool.py from the draw of record's side export). No seed, no
     * tier-A function, no closure computed here: the Python CK-CLOSE-v2 closure decided every side.
     * What this does check, each FATAL ("[SPLIT-V2]"):
     *  (1) every loaded row's id is in exactly one list of the file (an unlisted row refuses);
     *  (2) ONE-TO-ONE: the loaded TRAIN ids equal the file's train_ids and the loaded reserved ids equal
     *      its eval_ids + gate_ids, in both directions (a subset load, a changed corpus or a stale file refuses);
     *  (3) GLOBAL CLOSURE with sentinels: no TRAIN row's stem key is a non-TRAIN item of the export over ALL
     *      corpora ([V2EnginePool.globalReservedKeys]), and every reserved row's stem key is one.
     * RESERVED = EVAL + GATE (sentinel ids included); they are the test side and are written verbatim as
     * reserved_test_queries.json (domain -> ids, the dataset's order), recorded as a legacy id-list pool
     * exactly as [splitByReservedFile] records one. [Split.gate] is the file's GATE ids (a subset of the
     * reserved side here, never of TRAIN); |gate and eval| = 0 by the file's disjoint lists.
     */
    fun splitByV2Pool(
        dataset: Map<String, List<MMLUQuery>>,
        pool: V2EnginePool,
    ): Split {
        val train = mutableMapOf<String, List<MMLUQuery>>()
        val test = mutableMapOf<String, List<MMLUQuery>>()
        val unlisted = ArrayList<Int>()
        val closureBreach = ArrayList<Int>()
        val reservedUnkeyed = ArrayList<Int>()
        val loadedTrain = HashSet<Int>()
        val loadedReserved = HashSet<Int>()
        for ((category, queries) in dataset) {
            val tr = ArrayList<MMLUQuery>()
            val te = ArrayList<MMLUQuery>()
            for (q in queries) {
                val key = SplitSide.stemKey(q.text)
                when (q.id) {
                    in pool.reservedIds -> {
                        te += q; loadedReserved += q.id
                        if (key !in pool.globalReservedKeys) reservedUnkeyed += q.id
                    }
                    in pool.trainIds -> {
                        tr += q; loadedTrain += q.id
                        if (key in pool.globalReservedKeys) closureBreach += q.id
                    }
                    else -> unlisted += q.id
                }
            }
            train[category] = tr
            if (te.isNotEmpty()) test[category] = te
        }
        check(unlisted.isEmpty()) {
            "[SPLIT-V2] ${unlisted.size} loaded row(s) are in no list of ${pool.poolId} (first: ${unlisted.sorted().take(5)})"
        }
        check(closureBreach.isEmpty()) {
            "[SPLIT-V2] GLOBAL CLOSURE: ${closureBreach.size} TRAIN row(s) share their stem key with a reserved item" +
                " of the side export (sentinels and all corpora included; first: ${closureBreach.sorted().take(5)})"
        }
        check(reservedUnkeyed.isEmpty()) {
            "[SPLIT-V2] ${reservedUnkeyed.size} reserved row(s) key to no reserved item of the side export" +
                " (first: ${reservedUnkeyed.sorted().take(5)})"
        }
        // RP12 B2: a namespaced (multi-corpus) file is checked on the namespaces this build loaded; a
        // single-corpus file (no namespaces) whole, as before.
        val loadedNs = pool.namespacesOf(loadedTrain + loadedReserved)
        val (fileTrain, fileReserved) = pool.scopedTo(loadedNs)
        if (pool.namespaces != null) {
            log.warn("[SPLIT-V2] namespaced pool file: this build loaded $loadedNs of ${pool.namespaces.keys.sorted()}; one-to-one checked on those")
        }
        check(loadedTrain == fileTrain) {
            "[SPLIT-V2] ONE-TO-ONE TRAIN: loaded ${loadedTrain.size} vs file ${fileTrain.size}" +
                " (only loaded: ${(loadedTrain - fileTrain).sorted().take(5)}; only in the file: ${(fileTrain - loadedTrain).sorted().take(5)})"
        }
        check(loadedReserved == fileReserved) {
            "[SPLIT-V2] ONE-TO-ONE RESERVED: loaded ${loadedReserved.size} vs file ${fileReserved.size}" +
                " (only in the file: ${(fileReserved - loadedReserved).sorted().take(5)})"
        }
        val testIds: Map<String, List<Int>> = test.mapValues { (_, qs) -> qs.map { it.id } }
        reservedJsonFile.writeText(Json { prettyPrint = true }.encodeToString(testIds))
        val poolId = recordPool(testIds, dataset, seed = null, testRatio = null, origin = "v2 pool ${pool.poolId}")
        val gate = pool.gateIds.filterTo(HashSet()) { it in fileReserved }
        log.warn(
            "[SPLIT-V2] split taken as given from ${pool.poolId} (${pool.rule}, engine pool file sha256(LF)" +
                " ${pool.fileSha256Lf.take(16)}): ${loadedTrain.size} train / ${loadedReserved.size} reserved" +
                " (eval ${pool.evalIds.size}, gate ${gate.size}, sentinels ${pool.sentinelIds.size}); one-to-one TRAIN" +
                " and RESERVED hold; 0 TRAIN rows share a stem key with the ${pool.globalReservedKeys.size} global" +
                " reserved keys; legacy id-list pool ${poolId ?: "<none>"} (READY_rp12_et D-1: it holds EVAL + GATE ids, never an EVAL pool)"
        )
        return Split(train, test, gate, poolId, 0)
    }

    /** Records the judgeable ids of [testIds] as a pool; returns its id (null when nothing is judgeable). */
    private fun recordPool(
        testIds: Map<String, List<Int>>,
        dataset: Map<String, List<MMLUQuery>>,
        seed: Long?,
        testRatio: Double?,
        origin: String
    ): String? {
        val judgeable = testIds.mapValues { (_, ids) -> ids.filter { it > 0 } }.filterValues { it.isNotEmpty() }
        if (judgeable.isEmpty()) {
            log.warn("[POOL] no judgeable id in the test set ($origin); no pool recorded")
            return null
        }
        val poolId = ReservedPool.computePoolId(judgeable)
        try {
            connection.use { c ->
                val recorded = ReservedPool.save(
                    c, judgeable, dataset = poolDatasetName(), corpusSize = dataset.values.sumOf { it.size },
                    seed = seed, testRatio = testRatio, nowMillis = System.currentTimeMillis()
                )
                check(recorded == poolId)
                log.info(
                    "[POOL] recorded $poolId ($origin, ${judgeable.values.sumOf { it.size }} judgeable ids;" +
                        " sentinels excluded); nothing activated"
                )
            }
        } catch (e: Exception) {
            // The split is returned either way; a pool-recording failure must not take the run
            // down with it, and the id is a pure function of the ids regardless.
            log.warn("Failed to record the reserved pool in the database: ${e.message}")
        }
        return poolId
    }

    /**
     * Content closure, GATE and the per-item side assertion (FRAMEWORK item 18):
     *  (i)  a train item whose stem key equals any test item's stem key moves to test as a
     *       routing-only member (it is NOT added to the judgeable id list, so the pool id is
     *       unchanged); the id-list split is not closed under text equality by itself (sentinel
     *       duplicates of MMLU-Pro rows, GPQA sub-task copies), which is how the trees of record
     *       came to hold 37 / 427 / 2,437 EVAL texts;
     *  (ii) gate = SplitSide.gateOf(train), asserted disjoint from every test id;
     *  (iii) every item's landing set must equal SplitSide.tierA(...); a mismatch is FATAL.
     */
    internal fun finishSplit(
        train: MutableMap<String, List<MMLUQuery>>,
        test: MutableMap<String, List<MMLUQuery>>,
        testIds: Map<String, List<Int>>,
        poolId: String?
    ): Split {
        val pinnedIds = testIds.values.flatten().toHashSet()
        val testKeys = HashSet<String>()
        for (qs in test.values) for (q in qs) testKeys.add(SplitSide.stemKey(q.text))
        var closed = 0
        for ((category, queries) in train.toMap()) {
            val (dup, keep) = queries.partition { SplitSide.stemKey(it.text) in testKeys }
            if (dup.isNotEmpty()) {
                closed += dup.size
                train[category] = keep
                test[category] = (test[category] ?: emptyList()) + dup
            }
        }
        if (closed > 0) {
            log.info("[SPLIT-CLOSURE] $closed train item(s) share their text with a test item and move to test as routing-only members (pool id unchanged)")
        }
        val trainIdToText = HashMap<Int, String>()
        for (qs in train.values) for (q in qs) trainIdToText[q.id] = q.text
        val gate = SplitSide.gateOf(trainIdToText)
        val allTestIds = test.values.flatten().mapTo(HashSet()) { it.id }
        check((gate intersect allTestIds).isEmpty()) { "[SPLIT-SIDE] gate and test ids intersect: ${(gate intersect allTestIds).take(5)}" }
        // Per-item assertion: landing set == f(item).
        for ((_, qs) in test) for (q in qs) {
            val f = SplitSide.tierA(pinnedIds, testKeys, q.id, SplitSide.stemKey(q.text))
            check(f == Side.EVAL) { "[SPLIT-SIDE] item ${q.id} landed in TEST but f = $f" }
        }
        for ((_, qs) in train) for (q in qs) {
            val f = SplitSide.tierA(pinnedIds, testKeys, q.id, SplitSide.stemKey(q.text))
            val landed = if (q.id in gate) Side.GATE else Side.TRAIN
            check(f == landed) { "[SPLIT-SIDE] item ${q.id} landed in $landed but f = $f" }
        }
        log.info("[SPLIT-SIDE] ${train.values.sumOf { it.size }} train (${gate.size} gate) / ${test.values.sumOf { it.size }} test;" +
            " every item's side == f(item); |gate ∩ eval| = 0; pool ${poolId ?: "<none>"}; ${SplitSide.stamp(poolId)}")
        return Split(train, test, gate, poolId, closed)
    }

    fun getAvailableDomains(): List<Pair<String, Int>> {
        val table = getTableName()
        val list = mutableListOf<Pair<String, Int>>()
        try {
            connection.use { conn ->
                conn.createStatement().use { stmt ->
                    val rs = stmt.executeQuery("SELECT category, COUNT(*) FROM $table GROUP BY category ORDER BY category ASC")
                    while (rs.next()) {
                        val rawCat = rs.getString(1) ?: "unknown"
                        val count = rs.getInt(2)
                        val prettyCat = rawCat.split("_", "-").joinToString(" ") { word ->
                            word.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
                        }
                        list.add(Pair(prettyCat, count))
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to get available domains from SQLite ($table)", e)
        }
        return list
    }

    private val queryToCategoryCacheMap = mutableMapOf<DatasetType, Map<String, String>>()
    
    fun getQueryToCategoryMap(): Map<String, String> {
        val type = config.dataset.datasetType
        return queryToCategoryCacheMap.getOrPut(type) {
            val table = getTableName()
            val map = mutableMapOf<String, String>()
            try {
                DriverManager.getConnection(dbUrl).use { conn ->
                    conn.createStatement().use { stmt ->
                        val rs = stmt.executeQuery("SELECT question, category FROM $table")
                        while (rs.next()) {
                            val q = rs.getString("question")
                            val rawCat = rs.getString("category") ?: "Unknown"
                            val prettyCat = rawCat.split("_", "-").joinToString(" ") { word ->
                                word.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
                            }
                            map[q] = prettyCat
                        }
                    }
                }
            } catch (e: Exception) {
                log.error("Failed to build query-to-category map ($table)", e)
            }
            log.info("Query-to-category map loaded for $type: ${map.size} entries.")
            map
        }
    }

    internal suspend fun fetchTwentyNewsgroups(maxQueries: Int, selectedDomains: List<String>): Map<String, List<MMLUQuery>> {
        val table = "twenty_newsgroups"
        val limit = if (selectedDomains.isNotEmpty()) 100000 else maxQueries
        val allRows = loadFromDb(table, limit, selectedDomains)

        if (selectedDomains.isNotEmpty() || allRows.size >= maxQueries || allRows.size >= 2000) {
            return finalizeData(allRows.take(maxQueries), "20 Newsgroups")
        }

        log.info("20 Newsgroups local cache insufficient (${allRows.size}). Fetching from HF datasets server...")
        val client = HttpClient.newHttpClient()
        val newRows = mutableListOf<HFProRowData>()
        var offset = 0
        val batchSize = 100
        val maxBatches = 20 

        for (batch in 0 until maxBatches) {
            if (allRows.size + newRows.size >= maxQueries) break

            val url = "https://datasets-server.huggingface.co/rows?dataset=SetFit/20_newsgroups&config=default&split=test&offset=$offset&length=$batchSize"
            val requestBuilder = HttpRequest.newBuilder().uri(URI.create(url)).GET()
            if (hfToken.isNotBlank()) {
                requestBuilder.header("Authorization", "Bearer $hfToken")
            }
            val request = requestBuilder.build()

            try {
                val response = withContext(Dispatchers.IO) { client.send(request, HttpResponse.BodyHandlers.ofString()) }
                if (response.statusCode() == 200) {
                    val hfResponse = json.decodeFromString<HFTwentyNewsgroupsResponse>(response.body())
                    if (hfResponse.rows.isEmpty()) break

                    val subjectRows = hfResponse.rows.map { item ->
                        val r = item.row
                        HFProRowData(
                            question = r.text,
                            category = r.label_text,
                            cot_content = "",
                            options = emptyList(),
                            answer = r.label_text
                        )
                    }
                    newRows.addAll(subjectRows)
                    offset += batchSize
                    log.info("Fetched batch ${batch + 1} for 20 Newsgroups (${subjectRows.size} rows)")
                    onDownloadProgress?.invoke(allRows.size + newRows.size, resolveProgressTotal(maxQueries), "20 Newsgroups")
                    if (subjectRows.size < batchSize) break
                } else {
                    log.warn("Failed fetching 20 Newsgroups batch: HTTP ${response.statusCode()}")
                    break
                }
            } catch (e: Exception) {
                log.error("Error fetching 20 Newsgroups batch", e)
                break
            }
            kotlinx.coroutines.delay(100)
        }

        if (newRows.isNotEmpty()) {
            saveBatchToDb(table, newRows)
            allRows.addAll(newRows)
        }

        return finalizeData(allRows.take(maxQueries), "20 Newsgroups")
    }

    /**
     * The directory a LIVECODEBENCH build is checked against; null (the default, no initialiser code) means the JVM's
     * working dir, read inside fetchLiveCodeBench only. Tests point it at a temp dir.
     */
    internal var lcbWorkDir: java.io.File? = null

    /**
     * READY D7 (docs/reviews/READY_lcb_stage0.md; registration P2 / A6): a LIVECODEBENCH build must run from a SEPARATE git
     * worktree with a cold cache, because EmbeddingCache and the site null open embeddings_cache.db relative to the
     * working dir. Refused, before any row is read: (1) a working dir whose `.git` is a DIRECTORY (a main checkout; a
     * worktree's `.git` is a file); (2) on the FIRST LIVECODEBENCH fetch of the process, a working-dir embeddings_cache.db
     * whose `embeddings` or `queries` table holds rows (a warm cache: the main one, or a re-used build worktree).
     * ONCE PER PROCESS (window incident of 2026-09-25, experiment_results/lcb_stage0/window/03_build.log at b3e8c94): the
     * trickle validation fetches the dataset again in the same JVM after the construction has embedded the TRAIN texts,
     * so the cold-cache check runs only on the first fetch and records the checked working dir and cache path in
     * [LcbWorkDirGuardState]; every later fetch in the process asserts the SAME working dir and cache path (and (1) again),
     * logs "[LCB] working-dir guard: same process, already checked" and skips the warm-cache check. A fresh process checks
     * again. Only this branch calls it; no other corpus is affected, and the fetcher's constructor holds no guard code.
     */
    internal fun lcbWorkDirGuard(dir: java.io.File) {
        val wd = dir.canonicalFile
        val emb = java.io.File(wd, "embeddings_cache.db").canonicalFile
        val git = java.io.File(wd, ".git")
        check(!git.isDirectory) {
            "[LCB] refusing to build LIVECODEBENCH from '${wd.path}': its .git is a directory (a main checkout);" +
                " run from a separate git worktree with its own embeddings_cache.db (P2 / A6)"
        }
        synchronized(LcbWorkDirGuardState) {
            val prev = LcbWorkDirGuardState.checked
            if (prev != null) {
                check(prev.first == wd.path && prev.second == emb.path) {
                    "[LCB] refusing: the working dir or cache changed within this process (first checked '${prev.first}'," +
                        " cache '${prev.second}'; now '${wd.path}', cache '${emb.path}')"
                }
                log.warn("[LCB] working-dir guard: same process, already checked ('${wd.path}', cache '${emb.path}')")
                return
            }
            if (emb.isFile) {
                val cfg = org.sqlite.SQLiteConfig().apply { setReadOnly(true) }
                cfg.createConnection("jdbc:sqlite:${emb.path}").use { c ->
                    for (t in listOf("embeddings", "queries")) {
                        val exists = c.prepareStatement("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = ?").use { ps ->
                            ps.setString(1, t)
                            ps.executeQuery().use { rs -> rs.next() && rs.getInt(1) == 1 }
                        }
                        if (!exists) continue
                        val n = c.createStatement().use { st -> st.executeQuery("SELECT COUNT(*) FROM $t").use { rs -> rs.next(); rs.getInt(1) } }
                        check(n == 0) {
                            "[LCB] refusing to build LIVECODEBENCH: '${emb.path}' table '$t' holds $n rows (a warm cache);" +
                                " the build needs a cold cache in a separate worktree (P2 / A6)"
                        }
                    }
                }
            }
            LcbWorkDirGuardState.checked = wd.path to emb.path
        }
        log.warn("[LCB] working-dir guard passed: '${wd.path}' is not a main checkout; embeddings_cache.db cold (first check of this process)")
    }

    /**
     * LCB-STAGE0-INTERACTION (docs/judge_v2_program.md L17702-L17982, P1): the LiveCodeBench construction corpus, read
     * ONLY from the local `livecodebench` table that tools/analysis/lcb_stage0/ingest.py --construction writes under
     * Design N (TRAIN + GATE texts; the corpus DB is set by `corpusDbPath`). There is NO remote fallback and no row
     * threshold (the legacy loaders fetch from Hugging Face below 2,000 rows): an absent or empty table is FATAL. The
     * fetched count is logged so the build log shows n_TRAIN + n_GATE. Reached only when datasetType = LIVECODEBENCH.
     */
    internal suspend fun fetchLiveCodeBench(maxQueries: Int, selectedDomains: List<String>): Map<String, List<MMLUQuery>> {
        lcbWorkDirGuard(lcbWorkDir ?: java.io.File(System.getProperty("user.dir") ?: "."))
        val table = "livecodebench"
        val present = try {
            connection.use { conn ->
                conn.prepareStatement("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = ?").use { ps ->
                    ps.setString(1, table)
                    ps.executeQuery().use { rs -> rs.next() && rs.getInt(1) == 1 }
                }
            }
        } catch (e: Exception) {
            throw IllegalStateException("[LCB] cannot read the corpus DB '$dbPath': ${e.message}", e)
        }
        check(present) {
            "[LCB] table '$table' is absent from '$dbPath'; build it with tools/analysis/lcb_stage0/ingest.py --construction" +
                " (LIVECODEBENCH has no remote fallback)"
        }
        val limit = if (selectedDomains.isNotEmpty()) Int.MAX_VALUE else maxQueries
        val rows = loadFromDb(table, limit, selectedDomains)
        check(rows.isNotEmpty()) { "[LCB] table '$table' in '$dbPath' returned 0 rows (LIVECODEBENCH has no remote fallback)" }
        log.warn("[LCB] fetched ${rows.size} LIVECODEBENCH rows from the local table '$table' of '$dbPath'; no network access (no remote fallback)")
        return finalizeData(rows.take(maxQueries), "LiveCodeBench")
    }

    /**
     * INTENT-TRANSFER-S1 (docs/judge_v2_program.md L22682-L22710): the explicit embedding property an INTENT fetch checks;
     * null (the default, no initialiser code) means System.getProperty, read inside fetchIntent only. Tests set it.
     */
    internal var intentExplicitFileOverride: String? = null

    /** INTENT-TRANSFER-S1: the working dir an INTENT fetch checks the embedding copy against; null = the JVM's (tests set it). */
    internal var intentWorkDir: java.io.File? = null

    /**
     * INTENT-TRANSFER-S1 (docs/judge_v2_program.md L22682-L22710; INSTRUMENT "a generic intent DatasetType that fails closed
     * with no Hugging Face fallback"; HYGIENE "per-arm build DBs containing TRAIN and GATE rows ONLY (EVAL physically absent
     * from the JVM)" and "the working-copy route"). The intent corpus of ONE arm, read ONLY from the local `intent_corpus`
     * table of the build DB that tools/analysis/intent_s1_export.py writes (set by `corpusDbPath`). FATAL, before any row is
     * returned ("[INTENT] ... REFUSED"):
     *  (1) -Dtaxoarena.embeddingCacheFile absent, not an intent working copy (intent_emb_*.db), or lying in the working dir
     *      (EmbeddingCache.resolveIntentWorkingCopy checks the file itself; this checks that the route is in force at all, so
     *      an INTENT build can never embed into, or read, the working dir's embeddings_cache.db);
     *  (2) the table absent, or without a `side` column;
     *  (3) any row whose side is not TRAIN or GATE (an EVAL row in the build DB);
     *  (4) the build meta (`intent_build_meta`: schema intent_s1_build/v1, corpus, arm, n_train, n_gate) absent or not
     *      matching the table's per-side counts; (5) 0 rows. No network access, no row threshold, no remote fallback.
     * The fetched count per side is logged ("[INTENT] fetched ...") and recorded in the manifest (intent_build). Reached only
     * when datasetType = INTENT.
     */
    internal suspend fun fetchIntent(maxQueries: Int, selectedDomains: List<String>): Map<String, List<MMLUQuery>> {
        val table = "intent_corpus"
        val explicit = intentExplicitFileOverride ?: System.getProperty(EmbeddingCache.PROP_EXPLICIT_FILE)
        check(explicit != null && EmbeddingCache.isIntentWorkingCopy(explicit)) {
            "[INTENT] an INTENT build reads its embeddings ONLY from a per-run intent working copy: -D${EmbeddingCache.PROP_EXPLICIT_FILE}" +
                " must name an intent_emb_*.db copy (got ${explicit ?: "<absent>"}), REFUSED"
        }
        val wd = (intentWorkDir ?: java.io.File(System.getProperty("user.dir") ?: ".")).canonicalFile
        check(java.io.File(explicit).canonicalFile.parentFile?.canonicalPath != wd.path) {
            "[INTENT] the embedding file $explicit lies in the working dir ${wd.path} (a pinned file's directory); a per-run working copy" +
                " is required, REFUSED"
        }
        fun count(sql: String): Int = connection.use { conn ->
            conn.createStatement().use { st -> st.executeQuery(sql).use { rs -> rs.next(); rs.getInt(1) } }
        }
        val (present, hasSide, hasMeta) = try {
            connection.use { conn ->
                fun has(name: String) = conn.prepareStatement("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = ?").use { ps ->
                    ps.setString(1, name)
                    ps.executeQuery().use { rs -> rs.next() && rs.getInt(1) == 1 }
                }
                val t = has(table)
                val side = t && conn.createStatement().use { st ->
                    st.executeQuery("PRAGMA table_info($table)").use { rs ->
                        var found = false
                        while (rs.next()) if (rs.getString("name") == "side") found = true
                        found
                    }
                }
                Triple(t, side, has("intent_build_meta"))
            }
        } catch (e: Exception) {
            throw IllegalStateException("[INTENT] cannot read the build DB '$dbPath': ${e.message}", e)
        }
        check(present) {
            "[INTENT] table '$table' is absent from '$dbPath'; write the build DB with tools/analysis/intent_s1_export.py" +
                " (INTENT has no remote fallback), REFUSED"
        }
        check(hasSide) { "[INTENT] table '$table' in '$dbPath' has no `side` column: not an intent_s1 build DB, REFUSED" }
        val notTrainGate = count("SELECT COUNT(*) FROM $table WHERE side IS NULL OR side NOT IN ('TRAIN', 'GATE')")
        check(notTrainGate == 0) {
            "[INTENT] '$dbPath' holds $notTrainGate row(s) whose side is not TRAIN or GATE: EVAL must be physically absent from the" +
                " build DB, REFUSED"
        }
        check(hasMeta) { "[INTENT] '$dbPath' has no intent_build_meta table: not an intent_s1 build DB, REFUSED" }
        val meta = LinkedHashMap<String, String>()
        connection.use { conn ->
            conn.createStatement().use { st ->
                st.executeQuery("SELECT key, value FROM intent_build_meta").use { rs -> while (rs.next()) meta[rs.getString(1)] = rs.getString(2) }
            }
        }
        check(meta["schema"] == "intent_s1_build/v1") { "[INTENT] intent_build_meta schema '${meta["schema"]}' is not intent_s1_build/v1, REFUSED" }
        val nTrain = count("SELECT COUNT(*) FROM $table WHERE side = 'TRAIN'")
        val nGate = count("SELECT COUNT(*) FROM $table WHERE side = 'GATE'")
        check(meta["n_train"] == nTrain.toString() && meta["n_gate"] == nGate.toString()) {
            "[INTENT] intent_build_meta declares n_train ${meta["n_train"]} / n_gate ${meta["n_gate"]} but '$table' holds" +
                " $nTrain TRAIN / $nGate GATE rows, REFUSED"
        }
        val limit = if (selectedDomains.isNotEmpty()) Int.MAX_VALUE else maxQueries
        val rows = loadFromDb(table, limit, selectedDomains)
        check(rows.isNotEmpty()) { "[INTENT] table '$table' in '$dbPath' returned 0 rows (INTENT has no remote fallback), REFUSED" }
        log.warn(
            "[INTENT] fetched ${rows.size} INTENT rows (build DB: $nTrain TRAIN + $nGate GATE, 0 EVAL) of corpus '${meta["corpus"]}'," +
                " arm '${meta["arm"]}' from the local table '$table' of '$dbPath'; embeddings from the working copy $explicit;" +
                " no network access (no remote fallback)"
        )
        taxonomy.diagnostics.DiagnosticsBundle.recordIntentBuild(
            linkedMapOf("build_db" to dbPath, "corpus" to meta["corpus"], "arm" to meta["arm"], "salt" to meta["salt"],
                "n_train" to nTrain, "n_gate" to nGate, "n_fetched" to rows.size, "embedding_copy" to explicit)
        )
        return finalizeData(rows.take(maxQueries), "Intent")
    }

    internal suspend fun fetchAgNews(maxQueries: Int, selectedDomains: List<String>): Map<String, List<MMLUQuery>> {
        val table = "ag_news"
        val limit = if (selectedDomains.isNotEmpty()) 100000 else maxQueries
        val allRows = loadFromDb(table, limit, selectedDomains)

        if (selectedDomains.isNotEmpty() || allRows.size >= maxQueries || allRows.size >= 2000) {
            return finalizeData(allRows.take(maxQueries), "AG News")
        }

        log.info("AG News local cache insufficient (${allRows.size}). Fetching from HF datasets server...")
        val client = HttpClient.newHttpClient()
        val newRows = mutableListOf<HFProRowData>()
        var offset = 0
        val batchSize = 100
        val maxBatches = 20 

        val labelMap = mapOf(
            1 to "world",
            2 to "sports",
            3 to "business",
            4 to "sci tech"
        )

        for (batch in 0 until maxBatches) {
            if (allRows.size + newRows.size >= maxQueries) break

            val url = "https://datasets-server.huggingface.co/rows?dataset=sh0416/ag_news&config=default&split=test&offset=$offset&length=$batchSize"
            val requestBuilder = HttpRequest.newBuilder().uri(URI.create(url)).GET()
            if (hfToken.isNotBlank()) {
                requestBuilder.header("Authorization", "Bearer $hfToken")
            }
            val request = requestBuilder.build()

            try {
                val response = withContext(Dispatchers.IO) { client.send(request, HttpResponse.BodyHandlers.ofString()) }
                if (response.statusCode() == 200) {
                    val hfResponse = json.decodeFromString<HFAgNewsResponse>(response.body())
                    if (hfResponse.rows.isEmpty()) break

                    val subjectRows = hfResponse.rows.map { item ->
                        val r = item.row
                        val categoryName = labelMap[r.label] ?: "other"
                        HFProRowData(
                            question = "${r.title}. ${r.description}",
                            category = categoryName,
                            cot_content = "",
                            options = emptyList(),
                            answer = categoryName
                        )
                    }
                    newRows.addAll(subjectRows)
                    offset += batchSize
                    log.info("Fetched batch ${batch + 1} for AG News (${subjectRows.size} rows)")
                    onDownloadProgress?.invoke(allRows.size + newRows.size, resolveProgressTotal(maxQueries), "AG News")
                    if (subjectRows.size < batchSize) break
                } else {
                    log.warn("Failed fetching AG News batch: HTTP ${response.statusCode()}")
                    break
                }
            } catch (e: Exception) {
                log.error("Error fetching AG News batch", e)
                break
            }
            kotlinx.coroutines.delay(100)
        }

        if (newRows.isNotEmpty()) {
            saveBatchToDb(table, newRows)
            allRows.addAll(newRows)
        }

        return finalizeData(allRows.take(maxQueries), "AG News")
    }
}

@Serializable
private data class HFProDatasetResponse(val rows: List<HFProRowItem>)

@Serializable
private data class HFProRowItem(val row: HFProRowData)

/**
 * Base for the ids given to dataset rows with no `eval_question_link` entry.
 *
 * A query's id is consumed downstream as an `eval_results.question_id`. Rows without a
 * link have no such id, so they get `UNLINKED_QUERY_ID_BASE - <local rowid>`: unique, so
 * clustering identity survives, and comfortably below any real question_id (observed
 * range 70..12256) so it can never produce a spurious join. It is also distinct from the
 * `-1` [HFProRowData] default, which still means "no id, use the positional index".
 */
const val UNLINKED_QUERY_ID_BASE: Int = -1_000_000

@Serializable
data class HFProRowData(
    val id: Int = -1,
    val question: String,
    val category: String? = null,
    val cot_content: String? = null,
    val options: List<String> = emptyList(),
    val answer: String? = null
)

@Serializable
private data class HFMMLUResponse(val rows: List<HFMMLURowItem>)

@Serializable
private data class HFMMLURowItem(val row: HFMMLURowData)

@Serializable
private data class HFMMLURowData(
    val question: String,
    val choices: List<String> = emptyList(),
    val answer: Int
)

@Serializable
private data class HFArcResponse(val rows: List<HFArcRowItem>)

@Serializable
private data class HFArcRowItem(val row: HFArcRowData)

@Serializable
private data class HFArcRowData(
    val question: HFArcQuestion,
    val choices: HFArcChoices,
    val answerKey: String
)

@Serializable
private data class HFArcQuestion(val stem: String)

@Serializable
private data class HFArcChoices(val text: List<String> = emptyList(), val label: List<String> = emptyList())

@Serializable
private data class HFTwentyNewsgroupsResponse(val rows: List<HFTwentyNewsgroupsRowItem>)

@Serializable
private data class HFTwentyNewsgroupsRowItem(val row: HFTwentyNewsgroupsRowData)

@Serializable
private data class HFTwentyNewsgroupsRowData(
    val text: String,
    val label: Int,
    val label_text: String
)

@Serializable
private data class HFAgNewsResponse(val rows: List<HFAgNewsRowItem>)

@Serializable
private data class HFAgNewsRowItem(val row: HFAgNewsRowData)

@Serializable
private data class HFAgNewsRowData(
    val title: String,
    val description: String,
    val label: Int
)

/**
 * READY D7, once per process: the working dir and embeddings_cache.db path the first LIVECODEBENCH guard check accepted
 * (null until then). Loaded only by [MMLUDatasetFetcher.lcbWorkDirGuard]; tests reset it to simulate a new process.
 */
internal object LcbWorkDirGuardState {
    @Volatile
    var checked: Pair<String, String>? = null
}

@Serializable
data class MMLUQuery(
    val id: Int,
    val text: String,
    val category: String,
    // Stage 0a: which corpus the query came from. Defaulted so every serialised payload and
    // reserved_test_queries.json stay identical (kotlinx omits defaults unless encodeDefaults).
    val source: String = "MMLU_PRO"
)
