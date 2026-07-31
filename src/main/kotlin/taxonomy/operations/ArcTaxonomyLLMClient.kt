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
import kotlinx.coroutines.sync.withLock
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
    // The 4.0 req/s fallback is the highest rate measured clean on the judge deployment,
    // so a run that forgets the property lands somewhere safe. See config/application.yml
    // for the numbers behind the choice.
    @org.springframework.beans.factory.annotation.Value("\${arc.ollama.target-rps:4.0}") private val configuredTargetRps: Double,
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

    // ── Request-rate pacing ────────────────────────────────────────────────────
    //
    // The semaphore bounds CONCURRENCY -- how many calls are in flight. Azure bounds
    // RATE -- how many calls START per unit time, enforced in sub-minute windows. Those
    // are different quantities and both must be controlled: a batch dispatches its tasks
    // staggered by only 10ms, so N permits fire ~N calls inside a fraction of a second,
    // several times over the per-second budget even when sustained usage is far below
    // it. Lowering the permit count does not fix a rate problem -- it only lowers the
    // ceiling on a burst that is over budget anyway.
    //
    // This paces call STARTS to `arc.ollama.target-rps`. Each caller reserves the next
    // slot under a mutex and sleeps until it, so bursts are spread instead of rejected.
    // Retries are absorbed by the same gate, which prevents the secondary storm where
    // many backed-off calls resume together and burst again. Pacing does not reduce
    // steady-state throughput; it only removes the spikes.
    private val rateMutex = kotlinx.coroutines.sync.Mutex()
    private var nextSlotNanos = 0L
    // The target rate must be sized from the TOKEN budget, not the request budget -- at
    // this prompt size the token limit binds first, and pacing to the request ceiling
    // puts every call over quota, where each 429 spawns a retry that is itself a paced
    // call:
    //
    //     500,000 TPM / 60          = 8,333 tokens/s
    //     / ~1,250 tokens per call  = 6.7 calls/s   <- the real ceiling
    //     minus headroom for retries and the probe  ~ 5 calls/s
    //
    // If prompt sizes change materially, recompute: target = 500000 / 60 / tokens_per_call,
    // then take ~20% off. Initialised from arc.ollama.target-rps, overridable per run
    // with -Darc.ollama.target-rps=N, which bootRun forwards.
    @Volatile private var targetRps: Double = configuredTargetRps.coerceAtLeast(0.1)

    fun setTargetRps(rps: Double) {
        targetRps = rps.coerceAtLeast(0.1)
        log.info("LLM client request pacing set to ${"%.1f".format(java.util.Locale.US, targetRps)} req/s")
    }

    @jakarta.annotation.PostConstruct
    fun logPacing() {
        log.info("[ARENA-PACING] request pacing at ${"%.1f".format(java.util.Locale.US, targetRps)} req/s, " +
            "semaphore capacity $maxParallel")
    }

    /** Blocks until this call's pacing slot; returns the nanoseconds spent waiting. */
    private suspend fun awaitRateSlot(): Long {
        val intervalNanos = (1_000_000_000.0 / targetRps).toLong()
        val waitNanos = rateMutex.withLock {
            val now = System.nanoTime()
            val slot = maxOf(now, nextSlotNanos)
            nextSlotNanos = slot + intervalNanos
            slot - now
        }
        if (waitNanos > 0) delay(waitNanos / 1_000_000)
        return maxOf(0L, waitNanos)
    }

    // ── [ARENA-LAT] where a call's wall-clock actually goes ──────────────────────
    //
    // Every call spends its life in exactly three places, and which one dominates
    // decides which knob to turn:
    //
    //   rate    -- blocked in awaitRateSlot waiting for a pacing slot.  Lower
    //              `arc.ollama.target-rps` is the cause; raising it is the fix.
    //   permit  -- blocked on the semaphore because `max-parallel` calls are already
    //              in flight.  Raising `max-parallel` is the fix.
    //   http    -- the request itself.  Neither knob helps; this is the endpoint.
    //
    // Measuring the three directly makes "which knob" a glance instead of an inference
    // reconstructed after the fact from round durations and permit counts — an
    // inference that is easy to get wrong (raising target-rps buys nothing when the
    // pacer is under-utilised and the system is permit-bound).
    //
    // Deliberately NOT gated behind enableProfiling: profiling is off in every arena
    // config, so a diagnostic that needs it would not have been collected on any run so
    // far. The cost is three counters and a periodic log line.
    private val latRateNs = java.util.concurrent.atomic.AtomicLong(0)
    private val latPermitNs = java.util.concurrent.atomic.AtomicLong(0)
    private val latHttpNs = java.util.concurrent.atomic.AtomicLong(0)
    private val latCalls = java.util.concurrent.atomic.AtomicLong(0)
    private val latRetries = java.util.concurrent.atomic.AtomicLong(0)
    private val inFlight = java.util.concurrent.atomic.AtomicInteger(0)
    private val maxInFlight = java.util.concurrent.atomic.AtomicInteger(0)
    /** Bounded reservoir of http latencies (ms) for percentiles; oldest dropped. */
    private val httpSamples = java.util.concurrent.ConcurrentLinkedQueue<Long>()

    fun noteRetry() { latRetries.incrementAndGet() }

    // ── Adaptive pacing (AIMD) ───────────────────────────────────────────────────
    //
    // A fixed pacer requires knowing the deployment's real limit in advance, and any
    // guess is wrong in one direction or the other: too high produces a retry storm,
    // too low leaves the endpoint under-used with most of each call's wall-clock queued
    // at the pacer. The account ceiling (500 RPM / 500k TPM) is not the binding
    // constraint -- the per-deployment limit is, it is undocumented, and it moves.
    //
    // So instead of guessing, measure continuously: additive increase, multiplicative decrease.
    // Rise slowly while the endpoint is quiet, fall hard the moment it pushes back. This is
    // the standard control for exactly this situation (unknown, non-stationary capacity with
    // a cheap failure signal) and it converges on the true limit without a probe run.
    //
    //   +RPS_STEP every RPS_PROBE_MS with no rate-limit response
    //   x RPS_BACKOFF on any 429, and the clock restarts
    //   clamped to [RPS_FLOOR, RPS_CEILING]
    //
    // The ceiling is a safety rail, not a target: 8.0/s is ~480 RPM, just under the 500 RPM
    // account budget, so the controller can never walk past the documented limit even if the
    // deployment stops answering with 429s.
    private companion object {
        const val RPS_STEP = 0.25
        const val RPS_PROBE_MS = 60_000L
        const val RPS_BACKOFF = 0.5
        const val RPS_FLOOR = 1.5
        const val RPS_CEILING = 8.0
        /** Back off when the recent p95 exceeds this multiple of the warm baseline. */
        const val DELAY_TRIGGER = 1.5
        /** Wait this many calls before fixing the baseline, so it is warm but un-pushed. */
        const val BASELINE_AFTER_CALLS = 200L
    }
    @Volatile private var adaptiveEnabled = true
    @Volatile private var lastRateAdjustMs = System.currentTimeMillis()
    private val rateLimitHits = java.util.concurrent.atomic.AtomicLong(0)

    /** Called on every transient failure; [isRateLimit] distinguishes 429 from other faults. */
    fun noteTransient(isRateLimit: Boolean) {
        latRetries.incrementAndGet()
        if (!isRateLimit || !adaptiveEnabled) return
        rateLimitHits.incrementAndGet()
        synchronized(this) {
            val before = targetRps
            targetRps = (targetRps * RPS_BACKOFF).coerceAtLeast(RPS_FLOOR)
            lastRateAdjustMs = System.currentTimeMillis()
            if (targetRps < before) {
                log.warn(
                    "[ARENA-PACING] 429 -> backing off %.2f -> %.2f req/s".format(
                        java.util.Locale.US, before, targetRps)
                )
            }
        }
    }

    // ── Delay signal ────────────────────────────────────────────────────────────
    //
    // 429s are not the only way an endpoint says "too fast", and on this deployment they
    // are not even the usual way: past the knee the server QUEUES instead — p95 latency
    // rises steeply while the median barely moves, and no 429 is emitted at all — so a
    // loss-only controller climbs straight past it. That is counterproductive twice over:
    // work per round is N*mean_latency/permits, so inflated latency costs more than the
    // higher rate saves, and the tail closes on the request timeout, where calls time
    // out, retry, and the retries are themselves paced requests -- load feeding latency
    // feeding load.
    //
    // So back off on delay as well as on loss, which is what every serious congestion
    // controller does. The baseline is the p95 observed once the run is warm; exceeding
    // [DELAY_TRIGGER] times it is treated exactly like a 429.
    @Volatile private var baselineP95Ms = 0L
    private val recentHttpMs = java.util.concurrent.ConcurrentLinkedQueue<Long>()

    private fun recentP95(): Long {
        val s = recentHttpMs.toList().sorted()
        return if (s.isEmpty()) 0L else s[((s.size - 1) * 0.95).toInt()]
    }

    /** Probe upward when the endpoint has been quiet AND latency has not degraded. */
    private fun maybeProbeUp() {
        if (!adaptiveEnabled) return
        val now = System.currentTimeMillis()
        if (now - lastRateAdjustMs < RPS_PROBE_MS) return

        val p95 = recentP95()
        // Establish the baseline once, on a warm but un-pushed system.
        if (baselineP95Ms == 0L) {
            if (latCalls.get() < BASELINE_AFTER_CALLS || p95 <= 0L) return
            synchronized(this) { if (baselineP95Ms == 0L) baselineP95Ms = p95 }
            log.info("[ARENA-PACING] latency baseline set: p95=${baselineP95Ms}ms " +
                "(back off above ${(baselineP95Ms * DELAY_TRIGGER).toLong()}ms)")
            return
        }

        if (p95 > baselineP95Ms * DELAY_TRIGGER) {
            synchronized(this) {
                val before = targetRps
                targetRps = (targetRps * RPS_BACKOFF).coerceAtLeast(RPS_FLOOR)
                lastRateAdjustMs = now
                recentHttpMs.clear()
                if (targetRps < before) {
                    log.warn(
                        "[ARENA-PACING] latency degraded (p95 ${p95}ms > %.1fx baseline ${baselineP95Ms}ms)".format(
                            java.util.Locale.US, DELAY_TRIGGER) +
                            " -> backing off %.2f -> %.2f req/s".format(java.util.Locale.US, before, targetRps)
                    )
                }
            }
            return
        }

        if (targetRps >= RPS_CEILING) return
        synchronized(this) {
            if (now - lastRateAdjustMs < RPS_PROBE_MS) return
            val before = targetRps
            targetRps = (targetRps + RPS_STEP).coerceAtMost(RPS_CEILING)
            lastRateAdjustMs = now
            if (targetRps > before) {
                log.info(
                    "[ARENA-PACING] quiet for %ds, p95 ${p95}ms within baseline -> probing %.2f -> %.2f req/s".format(
                        java.util.Locale.US, RPS_PROBE_MS / 1000, before, targetRps)
                )
            }
        }
    }

    private fun recordCall(rateNs: Long, permitNs: Long, httpNs: Long) {
        latRateNs.addAndGet(rateNs)
        latPermitNs.addAndGet(permitNs)
        latHttpNs.addAndGet(httpNs)
        httpSamples.add(httpNs / 1_000_000)
        while (httpSamples.size > 2000) httpSamples.poll()
        // Short window for the delay signal. `httpSamples` is cumulative and so responds
        // far too slowly to catch a knee; this keeps only the recent past.
        recentHttpMs.add(httpNs / 1_000_000)
        while (recentHttpMs.size > 300) recentHttpMs.poll()
        maybeProbeUp()
        val n = latCalls.incrementAndGet()
        if (n % 200L == 0L) log.info(latencySummary())
    }

    /**
     * One line naming the bottleneck. Shares sum to ~100% of in-call wall time; the
     * saturation figure says whether the permit pool was actually the binding limit,
     * which is the assumption a Little's Law estimate silently makes.
     */
    fun latencySummary(): String {
        val n = latCalls.get().coerceAtLeast(1)
        val rate = latRateNs.get() / 1e6 / n
        val permit = latPermitNs.get() / 1e6 / n
        val http = latHttpNs.get() / 1e6 / n
        val total = (rate + permit + http).coerceAtLeast(0.001)
        val s = httpSamples.toList().sorted()
        fun pct(p: Double) = if (s.isEmpty()) 0L else s[((s.size - 1) * p).toInt()]
        val dominant = listOf("rate" to rate, "permit" to permit, "http" to http).maxByOrNull { it.second }!!
        return "[ARENA-LAT] calls=$n retries=${latRetries.get()} | per call: " +
            "rate=%.0fms (%.0f%%) permit=%.0fms (%.0f%%) http=%.0fms (%.0f%%)".format(
                java.util.Locale.US, rate, 100 * rate / total, permit, 100 * permit / total,
                http, 100 * http / total) +
            " | http p50=${pct(0.50)}ms p95=${pct(0.95)}ms p99=${pct(0.99)}ms" +
            " | rps=%.2f 429s=%d".format(java.util.Locale.US, targetRps, rateLimitHits.get()) +
            " | inflight max=${maxInFlight.get()}/$maxParallel" +
            " | BOTTLENECK=${dominant.first}"
    }

    /**
     * Wraps one outbound call: pacing slot, then a permit, then the body — timing each
     * separately. Both request paths go through this so the accounting is complete.
     */
    private suspend fun <T> pacedPermit(block: suspend () -> T): T {
        val rateNs = awaitRateSlot()
        val permitStart = System.nanoTime()
        return semaphore.withPermit {
            val bodyStart = System.nanoTime()
            val now = inFlight.incrementAndGet()
            maxInFlight.getAndUpdate { maxOf(it, now) }
            try {
                block()
            } finally {
                inFlight.decrementAndGet()
                recordCall(rateNs, bodyStart - permitStart, System.nanoTime() - bodyStart)
            }
        }
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
                // A timeout is a permit-release deadline as much as a failure deadline: a
                // stuck call holds one of the semaphore's permits for its whole duration,
                // so a generous deadline lets a growing latency tail park on permits and
                // eat throughput. 45s sits just above the measured p99 request latency
                // (~34s over 1,800 calls) and truncates roughly the slowest 1%; those
                // calls are retried, and a retry costs one paced request rather than a
                // held permit.
                .timeout(java.time.Duration.ofSeconds(45))
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
            pacedPermit {
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

                    return@pacedPermit responseText

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
            pacedPermit {
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

                    return@pacedPermit responseText

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
                
                noteTransient(isRateLimit)
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
