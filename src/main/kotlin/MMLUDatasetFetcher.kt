package org.eclipse.lmos.arc.app

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

@Service
class MMLUDatasetFetcher(
    @Value("\${huggingface.token:}") private val hfToken: String
) {
    private val log = LoggerFactory.getLogger(MMLUDatasetFetcher::class.java)
    private val json = Json { ignoreUnknownKeys = true; isLenient = true; coerceInputValues = true }
    private val dbUrl = "jdbc:sqlite:mmlu_pro_dataset_cache_v2.db"

    init {
        initDatabase()
    }

    private fun initDatabase() {
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
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
                }
            }
            log.info("SQLite MMLU Pro Cache V2 initialized successfully.")
        } catch (e: Exception) {
            log.error("Failed to initialize SQLite database.", e)
        }
    }

    suspend fun fetchDataset(maxQueries: Int = 500): Map<String, List<String>> {
        val totalInDb = getDbCount()
        val allRows = loadFromDb(maxQueries)

        if (allRows.size >= maxQueries) {
            log.info("Loaded MMLU Pro dataset from local cache (${allRows.size} queries).")
            return finalizeData(allRows)
        }

        log.info("MMLU Pro Cache V2 insufficient (${allRows.size}/$maxQueries). Fetching remainder...")

        val client = HttpClient.newHttpClient()
        var hfOffset = totalInDb
        val batchSize = 100

        var retries = 0
        val maxRetries = 10
        var waitTime = 2000L

        log.info("Downloading MMLU Pro dataset from Hugging Face...")
        while (allRows.size < maxQueries) {
            val limit = minOf(batchSize, maxQueries - allRows.size)
            val url = "https://datasets-server.huggingface.co/rows?dataset=TIGER-Lab%2FMMLU-Pro&config=default&split=test&offset=$hfOffset&length=$limit"

            val requestBuilder = HttpRequest.newBuilder().uri(URI.create(url)).GET()
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
                    // Ensure we capture cot_content if it exists, otherwise it stays null
                    row.copy(cot_content = row.cot_content ?: "")
                }
                saveBatchToDb(newRows)

                allRows.addAll(newRows)
                hfOffset += limit
                retries = 0
                waitTime = 2000L

                printProgressBar(allRows.size, maxQueries, "MMLU Pro Download Progress")
            } catch (e: Exception) {
                log.error("Failed parsing MMLU Pro row items", e)
                break
            }
        }

        return finalizeData(allRows.take(maxQueries))
    }

    private fun loadFromDb(limit: Int): MutableList<HFProRowData> {
        val rows = mutableListOf<HFProRowData>()
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.prepareStatement("SELECT question, category, cot_content, options, answer FROM mmlu_pro ORDER BY id ASC LIMIT ?").use { pstmt ->
                    pstmt.setInt(1, limit)
                    val rs = pstmt.executeQuery()
                    while (rs.next()) {
                        rows.add(HFProRowData(
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
            log.error("Failed to load from SQLite cache", e)
        }
        return rows
    }

    fun getDetailsForQuery(question: String): HFProRowData? {
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.prepareStatement("SELECT question, category, cot_content, options, answer FROM mmlu_pro WHERE question = ?").use { pstmt ->
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
            log.error("Failed to get query details from SQLite", e)
        }
        return null
    }

    private fun getDbCount(): Int {
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.createStatement().use { stmt ->
                    val rs = stmt.executeQuery("SELECT COUNT(*) FROM mmlu_pro")
                    if (rs.next()) return rs.getInt(1)
                }
            }
        } catch (e: Exception) {
            log.error("Failed to get count from SQLite", e)
        }
        return 0
    }

    private fun saveBatchToDb(rows: List<HFProRowData>) {
        try {
            DriverManager.getConnection(dbUrl).use { conn ->
                conn.autoCommit = false
                try {
                    conn.prepareStatement("INSERT INTO mmlu_pro (question, category, cot_content, options, answer) VALUES (?, ?, ?, ?, ?)").use { pstmt ->
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
            log.error("Failed to save batch to SQLite", e)
        }
    }

    private fun finalizeData(rows: List<HFProRowData>): Map<String, List<String>> {
        val formattedData = formatData(rows)
        log.info("Fetched ${rows.size} MMLU Pro queries across ${formattedData.keys.size} categories.")
        return formattedData
    }

    private fun formatData(rows: List<HFProRowData>): Map<String, List<String>> {
        return rows.groupBy { row ->
            val cat = row.category ?: "Unknown"
            cat.split("_", "-").joinToString(" ") { word ->
                word.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
            }
        }.mapValues { entry -> entry.value.map { it.question } }
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
}

@Serializable
private data class HFProDatasetResponse(val rows: List<HFProRowItem>)

@Serializable
private data class HFProRowItem(val row: HFProRowData)

@Serializable
data class HFProRowData(
    val question: String,
    val category: String? = null,
    val cot_content: String? = null,
    val options: List<String> = emptyList(),
    val answer: String? = null
)
