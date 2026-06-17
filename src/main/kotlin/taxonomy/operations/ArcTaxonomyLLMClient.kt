package org.eclipse.lmos.arc.app.taxonomy.operations

import org.eclipse.lmos.arc.app.LLMProvider
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import kotlinx.serialization.json.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.*
import org.eclipse.lmos.arc.app.taxonomy.GenerationMonitor
import dev.langchain4j.model.chat.StreamingChatModel
import dev.langchain4j.model.ollama.OllamaStreamingChatModel
import dev.langchain4j.model.azure.AzureOpenAiStreamingChatModel
import dev.langchain4j.model.chat.response.StreamingChatResponseHandler
import dev.langchain4j.model.chat.response.ChatResponse
import dev.langchain4j.data.message.UserMessage
import dev.langchain4j.data.message.ChatMessage
import dev.langchain4j.data.message.SystemMessage
import dev.langchain4j.model.chat.request.ChatRequest
import dev.langchain4j.model.chat.request.ResponseFormat
import dev.langchain4j.model.chat.request.ResponseFormatType
import dev.langchain4j.model.chat.request.json.JsonObjectSchema
import dev.langchain4j.model.chat.request.json.JsonSchema
import java.util.concurrent.ConcurrentHashMap
import java.io.PrintStream
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlin.time.Duration.Companion.milliseconds

/**
 * Interface for LLM integrations to label newly discovered taxonomic clusters.
 */
interface TaxonomyLlmClient {
    suspend fun generateClusterLabel(prompt: String): String
    suspend fun distillQuery(prompt: String): String
    suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String

    /**
     * Queries the model with a strict JSON schema constraint, guaranteeing syntactically
     * valid JSON output without requiring any post-hoc string cleanup.
     *
     * @param modelName The Ollama model endpoint to use.
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
    private val config: org.eclipse.lmos.arc.app.taxonomy.TaxonomyConfig
) : TaxonomyLlmClient {
    private val log = LoggerFactory.getLogger(ArcTaxonomyLLMClient::class.java)
    private val httpClient = java.net.http.HttpClient.newHttpClient()
    private val json = Json { ignoreUnknownKeys = true }

    private val semaphore = Semaphore(maxParallel)
    private val streamingModelCache = ConcurrentHashMap<String, StreamingChatModel>()
 
    private suspend fun getStreamingModel(modelName: String): StreamingChatModel {
        return streamingModelCache[modelName] ?: withContext(Dispatchers.IO) {
            streamingModelCache.computeIfAbsent(modelName) { name ->
                if (config.llm.provider == org.eclipse.lmos.arc.app.taxonomy.LlmProviderType.AZURE) {
                    log.info("Initializing Azure OpenAI Streaming connection for deployment '$name' at ${config.llm.azure.endpoint}")
                    AzureOpenAiStreamingChatModel.builder()
                        .endpoint(config.llm.azure.endpoint)
                        .apiKey(config.llm.azure.apiKey)
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
        }
    }

    private fun discoverModelContext(modelName: String): Int {
        return try {
            val request = java.net.http.HttpRequest.newBuilder()
                .uri(java.net.URI.create("$ollamaBaseUrl/api/show"))
                .header("Content-Type", "application/json")
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
        return semaphore.withPermit {
            val slot = monitor.acquireSlot(modelName)
            
            try {
                val model = getStreamingModel(modelName)
                val messages = mutableListOf<ChatMessage>()
                if (systemPrompt != null) messages.add(SystemMessage.from(systemPrompt))
                messages.add(UserMessage.from(userPrompt))

                // Idiomatic bridging of callbacks to Coroutines
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
                            if (continuation.isActive) {
                                continuation.resume(accumulatedContent.toString())
                            }
                        }

                        override fun onError(error: Throwable) {
                            log.error("Streaming error for model '$modelName': ${error.message}")
                            monitor.releaseSlot(slot)
                            if (continuation.isActive) {
                                continuation.resumeWithException(error)
                            }
                        }
                    })
                }
                
                // Keep the slot visible for a few seconds if it's a TUI request
                GlobalScope.launch {
                    delay(3000.milliseconds)
                    monitor.removeSlot(slot)
                }
                
                return@withPermit responseText

            } catch (e: Exception) {
                monitor.releaseSlot(slot)
                monitor.removeSlot(slot)
                log.error("Streaming failure for '$modelName'", e)
                return@withPermit "Error: ${e.message}"
            }
        }
    }

    /**
     * Sends a ChatRequest with a strict [JsonSchema] ResponseFormat to the Ollama endpoint,
     * forcing the model to emit syntactically valid JSON that exactly matches the schema.
     * This completely eliminates the need for post-hoc string cleanup or bracket-scanning.
     */
    override suspend fun queryModelStructured(
        modelName: String,
        systemPrompt: String?,
        userPrompt: String,
        schema: JsonSchema
    ): String {
        return semaphore.withPermit {
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
                            if (continuation.isActive) {
                                continuation.resume(accumulatedContent.toString())
                            }
                        }

                        override fun onError(error: Throwable) {
                            log.error("Structured streaming error for model '$modelName': ${error.message}")
                            monitor.releaseSlot(slot)
                            if (continuation.isActive) {
                                continuation.resumeWithException(error)
                            }
                        }
                    })
                }

                GlobalScope.launch {
                    delay(3000.milliseconds)
                    monitor.removeSlot(slot)
                }

                return@withPermit responseText

            } catch (e: Exception) {
                monitor.releaseSlot(slot)
                monitor.removeSlot(slot)
                log.error("Structured streaming failure for '$modelName'", e)
                return@withPermit "{}"
            }
        }
    }

    private fun getEffectiveModelName(): String {
        return System.getenv("ARC_MODEL")
            ?: if (configuredModelName.isNotBlank() && configuredModelName != "ministral-3:14b") configuredModelName
            else config.llm.labelingModel
    }

    override suspend fun distillQuery(prompt: String): String {
        return queryModel(getEffectiveModelName(), null, prompt)
    }

    override suspend fun generateClusterLabel(prompt: String): String {
        return queryModel(getEffectiveModelName(), null, prompt)
    }
}
