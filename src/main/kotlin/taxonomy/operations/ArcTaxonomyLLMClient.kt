package org.eclipse.lmos.arc.app.taxonomy.operations

import org.eclipse.lmos.arc.app.LLMProvider
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import kotlinx.serialization.json.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.*
import org.eclipse.lmos.arc.app.taxonomy.GenerationMonitor
import dev.langchain4j.model.ollama.OllamaStreamingChatModel
import dev.langchain4j.model.chat.response.StreamingChatResponseHandler
import dev.langchain4j.model.chat.response.ChatResponse
import dev.langchain4j.data.message.UserMessage
import dev.langchain4j.data.message.ChatMessage
import dev.langchain4j.data.message.SystemMessage
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
}

/**
 * Implementation of TaxonomyLlmClient utilizing the Arc LLMProvider and LangChain4j Streaming.
 */
@Service
class ArcTaxonomyLLMClient(
    private val llmProvider: LLMProvider,
    @org.springframework.beans.factory.annotation.Value("\${arc.ollama.base-url:http://localhost:11434}") private val ollamaBaseUrl: String,
    @org.springframework.beans.factory.annotation.Value("\${arc.ollama.num-ctx:8192}") private val defaultNumCtx: Int,
    @org.springframework.beans.factory.annotation.Value("\${arc.ollama.max-parallel:4}") private val maxParallel: Int,
    private val monitor: GenerationMonitor
) : TaxonomyLlmClient {
    private val log = LoggerFactory.getLogger(ArcTaxonomyLLMClient::class.java)
    private val httpClient = java.net.http.HttpClient.newHttpClient()
    private val json = Json { ignoreUnknownKeys = true }

    private val semaphore = Semaphore(maxParallel)
    private val streamingModelCache = ConcurrentHashMap<String, OllamaStreamingChatModel>()

    private suspend fun getStreamingModel(modelName: String): OllamaStreamingChatModel {
        // Double-checked locking or just standard cache; we use computeIfAbsent with IO block
        return streamingModelCache[modelName] ?: withContext(Dispatchers.IO) {
            streamingModelCache.computeIfAbsent(modelName) { name ->
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

    override suspend fun distillQuery(prompt: String): String {
        return queryModel("ministral-3:14b", null, prompt)
    }

    override suspend fun generateClusterLabel(prompt: String): String {
        return queryModel("ministral-3:14b", null, prompt)
    }
}
