package taxonomy.operations

import dev.langchain4j.data.message.ChatMessage
import dev.langchain4j.data.message.SystemMessage
import dev.langchain4j.data.message.UserMessage
import dev.langchain4j.model.azure.AzureOpenAiStreamingChatModel
import dev.langchain4j.model.chat.StreamingChatModel
import dev.langchain4j.model.chat.request.ChatRequest
import dev.langchain4j.model.chat.request.ResponseFormat
import dev.langchain4j.model.chat.request.ResponseFormatType
import dev.langchain4j.model.chat.request.json.JsonSchema
import dev.langchain4j.model.chat.response.ChatResponse
import dev.langchain4j.model.chat.response.StreamingChatResponseHandler
import dev.langchain4j.model.ollama.OllamaStreamingChatModel
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.LLMProvider
import taxonomy.config.LlmProviderType
import taxonomy.config.TaxonomyConfig
import taxonomy.utils.GenerationMonitor
import java.util.concurrent.ConcurrentHashMap
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlin.time.Duration.Companion.milliseconds

/**
 * Interface for LLM integrations to label newly discovered taxonomic clusters.
 */
interface TaxonomyLlmClient {
    suspend fun generateClusterLabel(prompt: String): String
    suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String

    /**
     * Queries the model with a strict JSON schema constraint, guaranteeing syntactically
     * valid JSON output without requiring any post-hoc string cleanup.
     *
     * For Ollama: uses the native ChatRequest + ResponseFormat JSON schema path.
     * For Azure: AzureOpenAiStreamingChatModel does not support the chat(ChatRequest, handler)
     * overload — it falls back to prompt-injected schema instructions which Mistral-Large-3
     * follows reliably without a separate JSON mode flag.
     *
     * @param modelName The model deployment/endpoint name.
     * @param systemPrompt Optional system-level instruction.
     * @param userPrompt The user-facing prompt body.
     * @param schema A pre-built LangChain4j [JsonSchema] that the model must conform to.
     * @return A raw JSON string that is guaranteed to parse correctly against the schema.
     */
    suspend fun queryModelStructured(
        modelName: String,
        systemPrompt: String?,
        userPrompt: String,
        schema: JsonSchema
    ): String

    fun setMaxParallel(limit: Int)
}

/**
 * Implementation of TaxonomyLlmClient utilizing the Arc LLMProvider and LangChain4j Streaming.
 */
@Service
class ArcTaxonomyLLMClient(
    private val llmProvider: LLMProvider,
    @org.springframework.beans.factory.annotation.Value("\${arc.ollama.base-url:http://localhost:11434}") private val ollamaBaseUrl: String,
    @org.springframework.beans.factory.annotation.Value("\${arc.ollama.model:ministral-3:14b}") private val configuredModelName: String,
    @org.springframework.beans.factory.annotation.Value("\${arc.ollama.num-ctx:8192}") private val defaultNumCtx: Int,
    @org.springframework.beans.factory.annotation.Value("\${arc.ollama.max-parallel:4}") private val maxParallel: Int,
    private val monitor: GenerationMonitor,
    private val config: TaxonomyConfig
) : TaxonomyLlmClient {
    private val log = LoggerFactory.getLogger("taxonomy.LLMClient")
    private val httpClient = java.net.http.HttpClient.newHttpClient()
    private val json = Json { ignoreUnknownKeys = true }

    private var semaphore = Semaphore(maxParallel)

    override fun setMaxParallel(limit: Int) {
        log.info("Updating LLM client semaphore capacity to $limit")
        semaphore = Semaphore(limit.coerceAtLeast(1))
    }
    private val streamingModelCache = ConcurrentHashMap<String, StreamingChatModel>()

    private val clientScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    private suspend fun getStreamingModel(modelName: String): StreamingChatModel {
        return streamingModelCache[modelName] ?: withContext(Dispatchers.IO) {
            // Use a manual get-then-put pattern instead of computeIfAbsent so that a failed
            // build attempt does NOT leave a poisoned entry in the cache.
            streamingModelCache.getOrPut(modelName) {
                buildStreamingModel(modelName)
            }
        }
    }

    private fun buildStreamingModel(name: String): StreamingChatModel {
        return if (config.llm.provider == LlmProviderType.AZURE) {
            val endpoint = config.llm.azure.endpoint
            val apiKey = config.llm.azure.apiKey
            require(endpoint.isNotBlank()) {
                "taxoadapt.llm.azure.endpoint is not configured. " +
                    "Set it in application.yml or via the AZURE_AI_ENDPOINT environment variable."
            }
            require(apiKey.isNotBlank()) {
                "taxoadapt.llm.azure.api-key is not configured. " +
                    "Set it in application.yml or via the AZURE_AI_API_KEY environment variable."
            }
            log.info("Initializing Azure OpenAI Streaming connection for deployment '$name' at $endpoint")
            AzureOpenAiStreamingChatModel.builder()
                .endpoint(endpoint)
                .apiKey(apiKey)
                .deploymentName(name)
                .serviceVersion(config.llm.azure.apiVersion)
                .timeout(java.time.Duration.ofMinutes(30))
                .build()
        } else {
            val discoveredCtx = discoverModelContext(name)
            log.info("Initializing GPU Streaming connection for '$name' (ctx: $discoveredCtx)")
            OllamaStreamingChatModel.builder()
                .baseUrl(ollamaBaseUrl)
                .modelName(name)
                .timeout(java.time.Duration.ofMinutes(30))
                .numCtx(discoveredCtx)
                .build()
        }
    }

    private fun discoverModelContext(modelName: String): Int {
        return try {
            val request = java.net.http.HttpRequest.newBuilder()
                .uri(java.net.URI.create("$ollamaBaseUrl/api/show"))
                .header("Content-Type", "application/json")
                .timeout(java.time.Duration.ofSeconds(10))
                .POST(java.net.http.HttpRequest.BodyPublishers.ofString("{\"name\": \"$modelName\"}"))
                .build()

            val response = httpClient.send(request, java.net.http.HttpResponse.BodyHandlers.ofString())
            if (response.statusCode() == 200) {
                val root = json.parseToJsonElement(response.body()).jsonObject
                val modelInfo = root["model_info"]?.jsonObject
                val infoCtx = modelInfo?.entries?.find { it.key.endsWith(".context_length") }?.value
                    ?.jsonPrimitive?.contentOrNull?.toIntOrNull()

                if (infoCtx != null) return minOf(infoCtx, 32768)
                return defaultNumCtx
            } else defaultNumCtx
        } catch (e: Exception) {
            log.warn("Could not auto-discover context for '$modelName', falling back to $defaultNumCtx")
            defaultNumCtx
        }
    }

    override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String {
        return runWithRetry(modelName) {
            semaphore.withPermit {
                val slot = monitor.acquireSlot(modelName)

                try {
                    val model = getStreamingModel(modelName)
                    val messages = mutableListOf<ChatMessage>()
                    if (systemPrompt != null) messages.add(SystemMessage.from(systemPrompt))
                    messages.add(UserMessage.from(userPrompt))

                    val responseText = suspendCancellableCoroutine<String> { continuation ->
                        val accumulatedContent = StringBuilder()

                        model.chat(messages, object : StreamingChatResponseHandler {
                            override fun onPartialResponse(token: String) {
                                accumulatedContent.append(token)
                                monitor.updateSlot(slot, token)
                            }

                            override fun onCompleteResponse(response: ChatResponse) {
                                log.debug("Stream completed for model '$modelName'")
                                monitor.releaseSlot(slot)
                                if (continuation.isActive) continuation.resume(accumulatedContent.toString())
                            }

                            override fun onError(error: Throwable) {
                                log.error("Streaming error for model '$modelName': ${error.message}")
                                monitor.releaseSlot(slot)
                                if (continuation.isActive) continuation.resumeWithException(error)
                            }
                        })
                    }

                    clientScope.launch {
                        delay(3000.milliseconds)
                        monitor.removeSlot(slot)
                    }

                    return@withPermit responseText

                } catch (e: Exception) {
                    monitor.releaseSlot(slot)
                    monitor.removeSlot(slot)
                    throw e
                }
            }
        }
    }

    /**
     * Sends a structured JSON request to the model.
     *
     * Ollama path: uses ChatRequest + ResponseFormat JSON schema — the model is constrained
     * at the grammar level and guaranteed to emit valid JSON.
     *
     * Azure path: AzureOpenAiStreamingChatModel only exposes chat(List<ChatMessage>, handler)
     * and does NOT implement the chat(ChatRequest, handler) overload. Calling it throws
     * UnsupportedOperationException which propagates through every async{} coroutine in
     * generateLabelsPostPass, causing awaitAll() to cancel the entire post-pass silently.
     * Instead we inject the schema as a JSON instruction in the system prompt — Mistral-Large-3
     * on Azure follows structured output instructions reliably without a native JSON mode flag.
     */
    override suspend fun queryModelStructured(
        modelName: String,
        systemPrompt: String?,
        userPrompt: String,
        schema: JsonSchema
    ): String {
        if (config.llm.provider == LlmProviderType.AZURE) {
            // Build a schema description from the root element's properties so the model
            // knows exactly what JSON object shape to produce.
            val schemaInstruction = buildAzureSchemaInstruction(schema)
            val augmentedSystem = listOfNotNull(systemPrompt, schemaInstruction).joinToString("\n\n")
            return queryModel(modelName, augmentedSystem.ifBlank { null }, userPrompt)
        }

        // Ollama: native structured output via ChatRequest + ResponseFormat
        return runWithRetry(modelName) {
            semaphore.withPermit {
                val slot = monitor.acquireSlot(modelName)

                try {
                    val model = getStreamingModel(modelName)
                    val messages = mutableListOf<ChatMessage>()
                    if (systemPrompt != null) messages.add(SystemMessage.from(systemPrompt))
                    messages.add(UserMessage.from(userPrompt))

                    val responseFormat = ResponseFormat.builder()
                        .type(ResponseFormatType.JSON)
                        .jsonSchema(schema)
                        .build()

                    val chatRequest = ChatRequest.builder()
                        .messages(messages)
                        .responseFormat(responseFormat)
                        .build()

                    val responseText = suspendCancellableCoroutine<String> { continuation ->
                        val accumulatedContent = StringBuilder()

                        model.chat(chatRequest, object : StreamingChatResponseHandler {
                            override fun onPartialResponse(token: String) {
                                accumulatedContent.append(token)
                                monitor.updateSlot(slot, token)
                            }

                            override fun onCompleteResponse(response: ChatResponse) {
                                log.debug("Structured stream completed for model '$modelName'")
                                monitor.releaseSlot(slot)
                                if (continuation.isActive) continuation.resume(accumulatedContent.toString())
                            }

                            override fun onError(error: Throwable) {
                                log.error("Structured streaming error for model '$modelName': ${error.message}")
                                monitor.releaseSlot(slot)
                                if (continuation.isActive) continuation.resumeWithException(error)
                            }
                        })
                    }

                    clientScope.launch {
                        delay(3000.milliseconds)
                        monitor.removeSlot(slot)
                    }

                    return@withPermit responseText

                } catch (e: Exception) {
                    monitor.releaseSlot(slot)
                    monitor.removeSlot(slot)
                    streamingModelCache.remove(modelName)
                    throw e
                }
            }
        }
    }

    private fun isRateLimitError(t: Throwable): Boolean {
        val msg = t.message.orEmpty()
        val causeMsg = t.cause?.message.orEmpty()
        return msg.contains("rate limit", ignoreCase = true) || 
               causeMsg.contains("rate limit", ignoreCase = true) ||
               msg.contains("429", ignoreCase = true) ||
               causeMsg.contains("429", ignoreCase = true)
    }

    private suspend fun <T> runWithRetry(
        modelName: String,
        maxRetries: Int = 3,
        block: suspend () -> T
    ): T {
        var attempt = 0
        var delayMs = 1000L
        while (true) {
            try {
                return block()
            } catch (t: Throwable) {
                attempt++
                val isTransient = isTransientError(t)
                val isRateLimit = isRateLimitError(t)
                val actualMaxRetries = if (isRateLimit) 6 else maxRetries
                
                if (attempt >= actualMaxRetries || !isTransient) {
                    throw t
                }
                
                // For rate limits, start with a minimum base delay of 2000ms
                val baseDelay = if (isRateLimit) maxOf(delayMs, 2000L) else delayMs
                // Jitter between 80% and 120% of baseDelay to prevent synchronised thread retries
                val jitter = (0.8 + kotlin.random.Random.nextDouble() * 0.4)
                val finalDelay = (baseDelay * jitter).toLong()
                
                log.warn("Transient error (rateLimit=$isRateLimit) on model '$modelName' (attempt $attempt/$actualMaxRetries): ${t.message}. Retrying in ${finalDelay}ms...")
                delay(finalDelay)
                
                delayMs = baseDelay * 2
                
                if (t.message?.contains("Connection reset", ignoreCase = true) == true || 
                    t.cause?.message?.contains("Connection reset", ignoreCase = true) == true) {
                    streamingModelCache.remove(modelName)
                }
            }
        }
    }

    private fun isTransientError(t: Throwable): Boolean {
        val msg = t.message.orEmpty()
        val causeMsg = t.cause?.message.orEmpty()
        if (t is java.net.SocketException || t is java.io.IOException || t is java.util.concurrent.TimeoutException) {
            return true
        }
        if (msg.contains("Connection reset", ignoreCase = true) || 
            causeMsg.contains("Connection reset", ignoreCase = true) ||
            msg.contains("timeout", ignoreCase = true) ||
            msg.contains("rate limit", ignoreCase = true) ||
            msg.contains("429", ignoreCase = true) ||
            msg.contains("503", ignoreCase = true) ||
            msg.contains("500", ignoreCase = true)) {
            return true
        }
        val cause = t.cause
        if (cause != null) {
            return isTransientError(cause)
        }
        return false
    }

    /**
     * Builds a concise system-prompt instruction describing the required JSON shape,
     * used as a fallback for providers that do not support the ChatRequest structured
     * output API (currently Azure).
     */
    private fun buildAzureSchemaInstruction(schema: JsonSchema): String {
        val rootEl = schema.rootElement()
        val props = try {
            (rootEl as? dev.langchain4j.model.chat.request.json.JsonObjectSchema)
                ?.properties()
                ?.entries
                ?.joinToString(", ") { (k, v) ->
                    val desc = (v as? dev.langchain4j.model.chat.request.json.JsonStringSchema)
                        ?.description() ?: "string"
                    "\"$k\": <$desc>"
                } ?: ""
        } catch (_: Throwable) { "" }

        return if (props.isNotEmpty()) {
            "You MUST respond with a single valid JSON object and nothing else. " +
                "Required shape: { $props }"
        } else {
            "You MUST respond with a single valid JSON object and nothing else."
        }
    }

    private fun getEffectiveModelName(): String {
        return System.getenv("ARC_MODEL")
            ?: if (configuredModelName.isNotBlank() && configuredModelName != "ministral-3:14b") configuredModelName
            else config.llm.labelingModel
    }

    override suspend fun generateClusterLabel(prompt: String): String {
        return queryModel(getEffectiveModelName(), null, prompt)
    }
}
