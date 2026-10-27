package taxonomy.service

import com.sun.net.httpserver.HttpServer
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import taxonomy.operations.AzureInferenceJudgeClient
import java.net.InetSocketAddress
import java.util.concurrent.atomic.AtomicInteger

/**
 * The raw Azure inference transport against a localhost stub: exact route and headers, the body
 * bytes posted unchanged, the response fields parsed (finish_reason, usage, id, model), the
 * `rejudge_reasoning.call_judge_full` retry schedule (429 then 200 -> 2 attempts, backoff 3 s), the
 * content-filter refusal (400 + "content_filter" -> empty content, finish_reason content_filter,
 * response id from the body), a plain 400 thrown, and 500 x6 thrown after six attempts.
 */
class AzureInferenceJudgeClientTest {

    private lateinit var server: HttpServer
    private val received = mutableListOf<Triple<String, Map<String, String>, ByteArray>>()
    private val responses = ArrayDeque<Pair<Int, String>>()
    private val hits = AtomicInteger(0)
    private val sleeps = mutableListOf<Long>()

    @BeforeEach
    fun start() {
        server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        server.createContext("/") { ex ->
            hits.incrementAndGet()
            val body = ex.requestBody.readAllBytes()
            val headers = ex.requestHeaders.entries.associate { (k, v) -> k.lowercase() to v.joinToString(",") }
            synchronized(received) { received.add(Triple(ex.requestURI.toString(), headers, body)) }
            val (status, text) = synchronized(responses) { responses.removeFirstOrNull() } ?: (200 to okBody)
            val bytes = text.toByteArray(Charsets.UTF_8)
            ex.responseHeaders.add("Content-Type", "application/json")
            ex.sendResponseHeaders(status, bytes.size.toLong())
            ex.responseBody.use { it.write(bytes) }
        }
        server.start()
    }

    @AfterEach
    fun stop() { server.stop(0) }

    private val okBody = """{"id":"chatcmpl-abc","model":"grok-4-1-fast-non-reasoning","choices":[{"index":0,"finish_reason":"stop","message":{"role":"assistant","content":"{\"winner\":\"Model A\",\"confidence\":0.8}"}}],"usage":{"prompt_tokens":1234,"completion_tokens":56,"total_tokens":1290}}"""

    private fun client(retries: Int = 6) = AzureInferenceJudgeClient(
        endpoint = "http://127.0.0.1:${server.address.port}/",
        apiKey = { "k-secret" },
        apiVersion = "2024-05-01-preview",
        sleeper = { ms -> sleeps.add(ms) },
        retries = retries
    )

    @Test
    fun `posts the exact bytes to the inference route with the api-key header and parses provenance`() = runBlocking {
        val body = "{\"model\": \"m\", \"max_tokens\": 8192, \"messages\": [{\"role\": \"system\", \"content\": \"s\\u2014\"}]}".toByteArray(Charsets.US_ASCII)
        val r = client().post(body)
        assertEquals(1, received.size)
        val (uri, headers, got) = received[0]
        assertEquals("/models/chat/completions?api-version=2024-05-01-preview", uri)
        assertEquals("application/json", headers["content-type"])
        assertEquals("k-secret", headers["api-key"])
        assertArrayEquals(body, got)
        assertEquals("{\"winner\":\"Model A\",\"confidence\":0.8}", r.content)
        assertEquals("stop", r.finishReason)
        assertEquals(56, r.completionTokens)
        assertEquals(1234, r.promptTokens)
        assertEquals("chatcmpl-abc", r.providerResponseId)
        assertEquals("grok-4-1-fast-non-reasoning", r.providerModel)
        assertEquals(200, r.httpStatus)
        assertEquals(1, r.attempts)
        assertEquals(AzureInferenceJudgeClient.sha256Hex(body), r.requestSha256)
        assertTrue(sleeps.isEmpty())
    }

    @Test
    fun `429 then 200 is two attempts with the 3 s first backoff`() = runBlocking {
        responses.add(429 to """{"error":{"code":"429","message":"rate"}}""")
        val r = client().post("{}".toByteArray())
        assertEquals(2, r.attempts)
        assertEquals(2, hits.get())
        assertEquals(listOf(3000L), sleeps)
        assertEquals("stop", r.finishReason)
    }

    @Test
    fun `backoff schedule is min(2^attempt * 3, 60) seconds`() {
        assertEquals(listOf(3000L, 6000L, 12000L, 24000L, 48000L, 60000L, 60000L), (0..6).map { AzureInferenceJudgeClient.backoffMs(it) })
    }

    @Test
    fun `a content-filter 400 is an empty content with finish_reason content_filter and the body's id`() = runBlocking {
        responses.add(400 to """{"id":"refusal-1","error":{"code":"content_filter","message":"The response was filtered"}}""")
        val r = client().post("{}".toByteArray())
        assertEquals("", r.content)
        assertEquals("content_filter", r.finishReason)
        assertEquals("refusal-1", r.providerResponseId)
        assertEquals(400, r.httpStatus)
        assertEquals(1, r.attempts)
        assertTrue(sleeps.isEmpty())
    }

    @Test
    fun `a plain 400 throws without retry`() {
        responses.add(400 to """{"error":{"code":"BadRequest","message":"unknown field"}}""")
        val ex = assertThrows(IllegalStateException::class.java) { runBlocking { client().post("{}".toByteArray()) } }
        assertTrue(ex.message!!.contains("HTTP 400"))
        assertEquals(1, hits.get())
    }

    @Test
    fun `500 six times throws after six attempts with the full schedule`() {
        repeat(6) { responses.add(500 to "boom") }
        val ex = assertThrows(IllegalStateException::class.java) { runBlocking { client().post("{}".toByteArray()) } }
        assertTrue(ex.message!!.contains("HTTP 500") && ex.message!!.contains("6 attempt"), ex.message)
        assertEquals(6, hits.get())
        assertEquals(listOf(3000L, 6000L, 12000L, 24000L, 48000L), sleeps)
    }

    @Test
    fun `a missing key is refused before any request`() {
        val c = AzureInferenceJudgeClient(endpoint = "http://127.0.0.1:${server.address.port}", apiKey = { null }, sleeper = { })
        assertThrows(IllegalStateException::class.java) { runBlocking { c.post("{}".toByteArray()) } }
        assertEquals(0, hits.get())
    }
}
