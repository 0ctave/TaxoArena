package org.eclipse.lmos.arc.app.domain

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import java.io.File
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse

@Service
class MMLUDatasetFetcher {
    private val log = LoggerFactory.getLogger(MMLUDatasetFetcher::class.java)
    private val json = Json { ignoreUnknownKeys = true; isLenient = true; coerceInputValues = true }
    private val cacheFile = File("mmlu_dataset_cache.json")

    suspend fun fetchDataset(maxQueries: Int = 500): Map<String, List<String>> {
        val allRows = mutableListOf<HFRowData>()

        if (cacheFile.exists()) {
            try {
                val cachedData = json.decodeFromString<List<HFRowData>>(cacheFile.readText())
                if (cachedData.size >= maxQueries) {
                    log.info("Loaded dataset from local cache.")
                    return finalizeData(cachedData.take(maxQueries))
                }
                log.info("Cache insufficient (${cachedData.size}/$maxQueries). Fetching remainder...")
                allRows.addAll(cachedData)
            } catch (e: Exception) {
                log.warn("Cache corrupted, starting fresh.")
            }
        }

        val client = HttpClient.newHttpClient()
        var offset = allRows.size
        val batchSize = 100
        var fetchedNewData = false

        log.info("Downloading dataset from Hugging Face...")
        while (offset < maxQueries) {
            val limit = minOf(batchSize, maxQueries - offset)
            val url = "https://datasets-server.huggingface.co/rows?dataset=cais%2Fmmlu&config=all&split=test&offset=$offset&length=$limit"

            val request = HttpRequest.newBuilder().uri(URI.create(url)).GET().build()
            val response = withContext(Dispatchers.IO) { client.send(request, HttpResponse.BodyHandlers.ofString()) }

            if (response.statusCode() != 200) break

            try {
                val hfResponse = json.decodeFromString<HFDatasetResponse>(response.body())
                if (hfResponse.rows.isEmpty()) break
                allRows.addAll(hfResponse.rows.map { it.row })
                offset += limit
                fetchedNewData = true
                printProgressBar(allRows.size, maxQueries, "Download Progress")
            } catch (e: Exception) { break }
        }

        if (fetchedNewData && allRows.isNotEmpty()) {
            withContext(Dispatchers.IO) { cacheFile.writeText(json.encodeToString(allRows)) }
        }

        return finalizeData(allRows.take(maxQueries))
    }

    private fun finalizeData(rows: List<HFRowData>): Map<String, List<String>> {
        val formattedData = formatData(rows)
        log.info("Fetched ${rows.size} queries across ${formattedData.keys.size} subjects.")
        return formattedData
    }

    private fun formatData(rows: List<HFRowData>): Map<String, List<String>> {
        return rows.groupBy { row ->
            row.subject.split("_", "-").joinToString(" ") { word ->
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
private data class HFDatasetResponse(val rows: List<HFRowItem>)

@Serializable
private data class HFRowItem(val row: HFRowData)

@Serializable
data class HFRowData(val question: String, val subject: String)