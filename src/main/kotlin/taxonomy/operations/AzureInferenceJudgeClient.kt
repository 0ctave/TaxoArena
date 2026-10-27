package taxonomy.operations

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.sync.withPermit
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.intOrNull
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.slf4j.LoggerFactory
import java.io.IOException
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.security.MessageDigest
import java.time.Duration

/**
 * One judge call's result with the provenance FRAMEWORK.md Stage 4 / item 19 requires per verdict.
 * `content` is null only when the provider returned no message; a content-filter refusal is an
 * EMPTY content with `finishReason = "content_filter"` (rejudge_reasoning.call_judge_full, 2026-09-16).
 */
data class JudgeCallResult(
    val content: String?,
    val finishReason: String?,
    val completionTokens: Int?,
    val promptTokens: Int?,
    val providerResponseId: String?,
    val providerModel: String?,
    val httpStatus: Int,
    val attempts: Int,
    val latencyMs: Long,
    val requestSha256: String
)

/** Posts exactly the bytes it is given; the recipe path never re-serialises. */
interface RecipeJudgeTransport {
    suspend fun post(body: ByteArray): JudgeCallResult
}

/** A transport that refuses: the default when no bean is wired (tests, and every run with the recipe disabled). */
object NoRecipeJudgeTransport : RecipeJudgeTransport {
    override suspend fun post(body: ByteArray): JudgeCallResult =
        throw IllegalStateException("[JUDGE-RECIPE] no judge transport is wired; the recipe path cannot post")
}

/**
 * A small fixed gate for the harness: `maxParallel` permits and `rps` call starts per second.
 * The Spring bean uses `ArcTaxonomyLLMClient.paced` instead so the production pacer and its 429
 * accounting stay in one place.
 */
class RequestGate(maxParallel: Int, private val rps: Double) {
    private val semaphore = Semaphore(maxParallel.coerceAtLeast(1))
    private val mutex = Mutex()
    private var nextSlotNanos = 0L
    suspend fun <T> run(block: suspend () -> T): T {
        val waitMs = mutex.withLock {
            val now = System.nanoTime()
            val interval = (1_000_000_000L / rps.coerceAtLeast(0.1)).toLong()
            val slot = maxOf(now, nextSlotNanos)
            nextSlotNanos = slot + interval
            (slot - now) / 1_000_000
        }
        if (waitMs > 0) delay(waitMs)
        return semaphore.withPermit { block() }
    }
}

/**
 * Raw POST to `{endpoint}/models/chat/completions?api-version={apiVersion}` with headers
 * `Content-Type: application/json` and `api-key`, the exact route, headers, timeout (600 s) and
 * retry schedule of `rejudge_reasoning.call_judge_full`:
 *
 *   - HTTP 408/429/500/502/503/504 and attempts left -> sleep min(2^attempt * 3, 60) s, retry (6 attempts);
 *   - HTTP 400 whose body contains "content_filter" -> content "", finish_reason "content_filter",
 *     response id from the body when it parses; any other 4xx/5xx -> IllegalStateException;
 *   - transport errors (IOException) -> same backoff, then rethrown.
 *
 * Nothing about the langchain4j Mistral path is reused: that path streams through
 * `AzureOpenAiStreamingChatModel` on `/openai/deployments`, cannot see `finish_reason`, and is left
 * byte-identical. `gate` wraps each attempt (pacing + permits); `sleeper` is injectable so the test
 * pins the backoff schedule without waiting.
 */
class AzureInferenceJudgeClient(
    endpoint: String,
    private val apiKey: () -> String?,
    apiVersion: String = "2024-05-01-preview",
    private val gate: suspend (suspend () -> HttpResponse<ByteArray>) -> HttpResponse<ByteArray> = { it() },
    private val sleeper: suspend (Long) -> Unit = { ms -> delay(ms) },
    private val httpClient: HttpClient = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(60)).build(),
    private val retries: Int = 6
) : RecipeJudgeTransport {
    private val log = LoggerFactory.getLogger("taxonomy.AzureInferenceJudgeClient")
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }
    val url: String = endpoint.trimEnd('/') + "/models/chat/completions?api-version=" + apiVersion

    companion object {
        val RETRY_STATUSES = setOf(408, 429, 500, 502, 503, 504)
        /** `time.sleep(min(2 ** attempt * 3, 60))`, in milliseconds. */
        fun backoffMs(attempt: Int): Long = minOf((1L shl attempt.coerceIn(0, 20)) * 3, 60L) * 1000L
        fun sha256Hex(bytes: ByteArray): String =
            MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
    }

    override suspend fun post(body: ByteArray): JudgeCallResult {
        val key = apiKey() ?: throw IllegalStateException("[JUDGE-RECIPE] no API key: set AZURE_GROK_API_KEY (or AZURE_AI_API_KEY) in the environment")
        val sha = sha256Hex(body)
        val t0 = System.currentTimeMillis()
        for (attempt in 0 until retries) {
            val request = HttpRequest.newBuilder(URI.create(url))
                .timeout(Duration.ofSeconds(600))
                .header("Content-Type", "application/json")
                .header("api-key", key)
                .POST(HttpRequest.BodyPublishers.ofByteArray(body))
                .build()
            val response: HttpResponse<ByteArray>
            try {
                response = gate { withContext(Dispatchers.IO) { httpClient.send(request, HttpResponse.BodyHandlers.ofByteArray()) } }
            } catch (e: IOException) {
                if (attempt < retries - 1) {
                    log.warn("[JUDGE-RECIPE] transport error on attempt ${attempt + 1}/$retries: ${e.message}; backing off ${backoffMs(attempt)} ms")
                    sleeper(backoffMs(attempt)); continue
                }
                throw e
            }
            val status = response.statusCode()
            val text = String(response.body(), Charsets.UTF_8)
            if (status in 200..299) {
                return parseSuccess(text, status, attempt + 1, System.currentTimeMillis() - t0, sha)
            }
            if (status in RETRY_STATUSES && attempt < retries - 1) {
                log.warn("[JUDGE-RECIPE] HTTP $status on attempt ${attempt + 1}/$retries; backing off ${backoffMs(attempt)} ms")
                sleeper(backoffMs(attempt)); continue
            }
            if (status == 400 && text.contains("content_filter")) {
                val rid = runCatching { json.parseToJsonElement(text).jsonObject["id"]?.jsonPrimitive?.contentOrNull }.getOrNull()
                return JudgeCallResult(
                    content = "", finishReason = "content_filter", completionTokens = 0, promptTokens = null,
                    providerResponseId = rid, providerModel = "azure:refusal", httpStatus = status, attempts = attempt + 1,
                    latencyMs = System.currentTimeMillis() - t0, requestSha256 = sha
                )
            }
            throw IllegalStateException("[JUDGE-RECIPE] HTTP $status from $url after ${attempt + 1} attempt(s): ${text.take(300)}")
        }
        throw IllegalStateException("unreachable")
    }

    private fun parseSuccess(text: String, status: Int, attempts: Int, latencyMs: Long, sha: String): JudgeCallResult {
        val root = json.parseToJsonElement(text).jsonObject
        val choice = root["choices"]?.jsonArray?.firstOrNull()?.jsonObject
            ?: throw IllegalStateException("[JUDGE-RECIPE] response carries no choices: ${text.take(300)}")
        val message = choice["message"]?.jsonObject
        val content = message?.get("content")?.let { runCatching { it.jsonPrimitive.contentOrNull }.getOrNull() }
        val usage = root["usage"]?.let { runCatching { it.jsonObject }.getOrNull() }
        return JudgeCallResult(
            content = content,
            finishReason = choice["finish_reason"]?.let { runCatching { it.jsonPrimitive.contentOrNull }.getOrNull() },
            completionTokens = usage?.get("completion_tokens")?.let { runCatching { it.jsonPrimitive.intOrNull }.getOrNull() },
            promptTokens = usage?.get("prompt_tokens")?.let { runCatching { it.jsonPrimitive.intOrNull }.getOrNull() },
            providerResponseId = root["id"]?.let { runCatching { it.jsonPrimitive.contentOrNull }.getOrNull() },
            providerModel = root["model"]?.let { runCatching { it.jsonPrimitive.contentOrNull }.getOrNull() },
            httpStatus = status, attempts = attempts, latencyMs = latencyMs, requestSha256 = sha
        )
    }
}

/**
 * The production transport bean: built lazily from `config.llm.judgeRecipe` on the first post (so a
 * run with the recipe disabled never constructs a client or reads a key), keyed like
 * `rejudge_reasoning.load_env` (AZURE_GROK_API_KEY, else the configured Azure key), gated through
 * `ArcTaxonomyLLMClient.paced` so the AIMD pacer and 429 accounting stay in one place.
 */
@org.springframework.stereotype.Service
class SpringRecipeJudgeTransport(
    private val config: taxonomy.config.TaxonomyConfig,
    private val llmClient: ArcTaxonomyLLMClient
) : RecipeJudgeTransport {
    @Volatile private var client: AzureInferenceJudgeClient? = null

    private fun client(): AzureInferenceJudgeClient {
        client?.let { return it }
        synchronized(this) {
            client?.let { return it }
            check(config.llm.judgeRecipe.enabled) { "[JUDGE-RECIPE] transport used while the recipe is disabled" }
            val endpoint = config.llm.azure.endpoint
            check(endpoint.isNotBlank()) { "[JUDGE-RECIPE] AZURE_AI_ENDPOINT (taxoadapt.llm.azure.endpoint) is blank" }
            val built = AzureInferenceJudgeClient(
                endpoint = endpoint,
                apiKey = { System.getenv("AZURE_GROK_API_KEY")?.takeIf { it.isNotBlank() } ?: config.llm.azure.apiKey.takeIf { it.isNotBlank() } },
                apiVersion = config.llm.judgeRecipe.inferenceApiVersion,
                gate = { send -> llmClient.paced { send() } }
            )
            client = built
            return built
        }
    }

    override suspend fun post(body: ByteArray): JudgeCallResult = client().post(body)
}
