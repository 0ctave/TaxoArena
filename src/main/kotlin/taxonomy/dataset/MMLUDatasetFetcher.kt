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
    @Value("\${huggingface.token:}") private val hfToken: String
) {
    var onDownloadProgress: ((current: Int, total: Int, datasetName: String) -> Unit)? = null
    private val log = LoggerFactory.getLogger("taxonomy.DatasetFetcher")

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
    private val dbUrl = "jdbc:sqlite:mmlu_pro_dataset_cache_v2.db?journal_mode=WAL&synchronous=NORMAL&busy_timeout=10000"

    private val connection: java.sql.Connection
        get() = DriverManager.getConnection(dbUrl).also { conn ->
            conn.autoCommit = true
        }

    init {
        initDatabase()
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

    private fun getTableName(): String = when (config.dataset.datasetType) {
        DatasetType.MMLU_PRO -> "mmlu_pro"
        DatasetType.MMLU_ORIGINAL -> "mmlu_original"
        DatasetType.ARC -> "arc"
        DatasetType.TWENTY_NEWSGROUPS -> "twenty_newsgroups"
        DatasetType.AG_NEWS -> "ag_news"
    }

    fun isDatasetDownloaded(): Boolean {
        val table = getTableName()
        return getDbCount(table) > 0
    }

    suspend fun downloadDataset(maxQueries: Int = 12000) {
        fetchDataset(maxQueries = maxQueries, selectedDomains = emptyList())
    }

    suspend fun fetchDataset(maxQueries: Int = 12000, selectedDomains: List<String> = emptyList()): Map<String, List<MMLUQuery>> {
        val type = config.dataset.datasetType
        return when (type) {
            DatasetType.MMLU_PRO -> fetchMmluPro(maxQueries, selectedDomains)
            DatasetType.MMLU_ORIGINAL -> fetchMmluOriginal(maxQueries, selectedDomains)
            DatasetType.ARC -> fetchArc(maxQueries, selectedDomains)
            DatasetType.TWENTY_NEWSGROUPS -> fetchTwentyNewsgroups(maxQueries, selectedDomains)
            DatasetType.AG_NEWS -> fetchAgNews(maxQueries, selectedDomains)
        }
    }

    private suspend fun fetchMmluPro(maxQueries: Int, selectedDomains: List<String>): Map<String, List<MMLUQuery>> {
        val table = "mmlu_pro"
        val limit = if (selectedDomains.isNotEmpty()) 100000 else maxQueries
        val totalInDb = getDbCount(table)
        val allRows = loadFromDb(table, limit, selectedDomains)

        if (selectedDomains.isNotEmpty()) {
            log.info("Loaded ${allRows.size} MMLU Pro queries from local cache for domains: ${selectedDomains.joinToString(", ")}.")
            return finalizeData(allRows, "MMLU Pro")
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

    private suspend fun fetchMmluOriginal(maxQueries: Int, selectedDomains: List<String>): Map<String, List<MMLUQuery>> {
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

    private suspend fun fetchArc(maxQueries: Int, selectedDomains: List<String>): Map<String, List<MMLUQuery>> {
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
                    while (rs.next()) {
                        val upstreamId = rs.getInt("question_id")
                        val finalId = if (rs.wasNull() || upstreamId <= 0) rs.getInt("id") else upstreamId
                        rows.add(HFProRowData(
                            id = finalId,
                            question = rs.getString("question"),
                            category = rs.getString("category"),
                            cot_content = rs.getString("cot_content"),
                            options = json.decodeFromString(rs.getString("options")),
                            answer = rs.getString("answer")
                        ))
                    }
                }
            }
        } catch (e: Exception) {
            log.error("Failed to load from SQLite cache ($table)", e)
        }
        return rows
    }

    fun getDetailsForQuery(question: String): HFProRowData? {
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
                val finalId = if (it.id >= 0) it.id else idx
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
     * Domain-stratified random train/test split: each domain contributes the SAME [testRatio]
     * fraction to the test set (balanced across domains), and both sets are drawn at random.
     * By default the seed is fresh per call so the split is non-deterministic; pass [seed] for
     * a reproducible split. The reserved test set is written to reserved_test_queries.json so
     * it travels with the DAG snapshot and is never seen during generation.
     */
    fun splitTrainTest(
        dataset: Map<String, List<MMLUQuery>>,
        testRatio: Double = 0.2,
        seed: Long = java.util.concurrent.ThreadLocalRandom.current().nextLong(),
    ): Pair<Map<String, List<MMLUQuery>>, Map<String, List<MMLUQuery>>> {
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
        
        try {
            val file = java.io.File("reserved_test_queries.json")
            val prettyJson = Json { prettyPrint = true }
            val testIds: Map<String, List<Int>> = test.mapValues { (_, qs) -> qs.map { it.id } }
            file.writeText(prettyJson.encodeToString(testIds))
            log.info("Successfully reserved ${test.values.flatten().size} test queries across ${test.size} domains to reserved_test_queries.json.")
        } catch (e: Exception) {
            log.error("Failed to save reserved test queries to file", e)
        }
        
        return Pair(train, test)
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

    private suspend fun fetchTwentyNewsgroups(maxQueries: Int, selectedDomains: List<String>): Map<String, List<MMLUQuery>> {
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

    private suspend fun fetchAgNews(maxQueries: Int, selectedDomains: List<String>): Map<String, List<MMLUQuery>> {
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

@Serializable
data class MMLUQuery(
    val id: Int,
    val text: String,
    val category: String
)
