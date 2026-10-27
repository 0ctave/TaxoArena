package taxonomy.runner

import dev.langchain4j.data.message.SystemMessage
import dev.langchain4j.data.message.UserMessage
import dev.langchain4j.model.azure.AzureOpenAiChatModel
import dev.langchain4j.model.chat.ChatModel
import dev.langchain4j.model.chat.request.ChatRequest
import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import taxonomy.config.TaxonomyConfig
import taxonomy.dataset.HFProRowData
import taxonomy.dataset.MMLUDatasetFetcher
import taxonomy.model.Embedding
import taxonomy.model.GraphNode
import taxonomy.operations.ArcTaxonomyLLMClient
import taxonomy.operations.TaxonomyFitter
import taxonomy.operations.TaxonomyLlmClient
import taxonomy.operations.TaxonomySplitter
import java.io.File
import java.security.MessageDigest
import java.util.Base64

/**
 * FIXED-TREE LABELS (TaxoArena author decisions D-2026-10-13 "LLM names only after the tree is fixed" and
 * D-2026-10-20-2 option A): names an externally built, FIXED tree with the production map-reduce labeller
 * [TaxonomySplitter.generateLabelsPostPass] (leaves from their own questions, internal nodes from the children's
 * representative samples, siblings labelled sequentially, lineage and domain anchors in the prompt), without a
 * construction run. Input: the JSON written by benchzoom `examples/axis_marks.py export` (nodes with parent / depth /
 * children, items with their leaf, QUESTION text only, declared category and map vector). Output: one name per node at
 * depth > anchor depth (1: the declared categories keep their names), plus the call and token counts.
 *
 * Nothing here changes the tree: the runner builds [GraphNode]s from the input, runs the post-pass, and REFUSES to
 * write if any node's parent, children or item count differs afterwards. The labeller's own code is called unchanged;
 * the only substitutions are (1) the transport, [CountingAzureClient] (a non-streaming `AzureOpenAiChatModel` on the
 * same endpoint, deployment and api version as `ArcTaxonomyLLMClient`, the same Azure system instruction
 * [ArcTaxonomyLLMClient.buildAzureSchemaInstruction], with token usage recorded), and (2) the dataset fetcher, a
 * [CategoryFetcher] that answers `getDetailsForQuery` from the input's declared categories (the domain anchors) and
 * never opens a dataset DB (its constructor points the fetcher's DB at a temporary file).
 *
 * Modes: `--dry-run` runs the whole post-pass against [DryClient] (no network; one counted pseudo-call per node) after a
 * ZERO-CALL transport preflight ([preflight]: endpoint and key present, https URL, host resolves, model object built);
 * a real run does the same preflight first and refuses on failure. Every prompt and response of a real run goes to
 * `<out>.calls.jsonl` (raw record). Gradle: `gradlew fixedTreeLabels --args="--in <json> --out <json> [--dry-run]"` (entry point in the test source set).
 */
object FixedTreeLabels {

    @Serializable
    data class InNode(val node: Int, val parent: Int? = null, val depth: Int, val kind: String, val n: Int,
                      val keyword_name: String = "", val children: List<Int> = emptyList())

    @Serializable
    data class InItem(val row: Int, val leaf: Int, val question: String, val category: String, val vec: String)

    @Serializable
    data class Input(val dataset: String, val tree_pickle_sha256: String = "", val dim: Int,
                     val text_field: String = "", val anchor_depth: Int = 1,
                     val nodes: List<InNode>, val items: List<InItem>)

    @Serializable
    data class OutNode(val node: Int, val parent: Int?, val depth: Int, val n: Int, val keyword_name: String,
                       val llm_label: String?, val description: String?)

    @Serializable
    data class Output(val input_sha256: String, val dataset: String, val model: String, val dry_run: Boolean,
                      val calls: Int, val failed_attempts: Int, val prompt_tokens: Long, val completion_tokens: Long,
                      val total_tokens: Long, val nodes_labelled: Int, val nodes: List<OutNode>)

    @Serializable
    data class CallRecord(val i: Int, val prompt_sha256: String, val system: String?, val prompt: String,
                          val response: String, val prompt_tokens: Int?, val completion_tokens: Int?)

    private val json = Json { ignoreUnknownKeys = false; encodeDefaults = true }

    fun sha256(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }

    fun decodeVec(b64: String, dim: Int): FloatArray {
        val bb = java.nio.ByteBuffer.wrap(Base64.getDecoder().decode(b64)).order(java.nio.ByteOrder.LITTLE_ENDIAN)
        require(bb.remaining() == 4 * dim) { "REFUSED: a vector of ${bb.remaining() / 4} floats, expected $dim" }
        return FloatArray(dim) { bb.float }
    }

    /** The GraphNodes of the fixed tree (index = input node id) with every item as an Embedding on its leaf. */
    fun buildGraph(inp: Input): List<GraphNode> {
        require(inp.nodes.withIndex().all { (i, d) -> d.node == i }) { "REFUSED: node ids are not 0..N-1 in order" }
        require(inp.nodes[0].parent == null && inp.nodes[0].depth == 0) { "REFUSED: node 0 is not the root" }
        val g = inp.nodes.map { d ->
            GraphNode(id = "n%05d".format(d.node), label = if (d.depth == 0) inp.dataset else d.keyword_name,
                      depth = d.depth).also { if (d.depth == inp.anchor_depth) it.originalCategory = d.keyword_name }
        }
        for (d in inp.nodes) {
            for (c in d.children) {
                require(inp.nodes[c].parent == d.node) { "REFUSED: child $c of ${d.node} names parent ${inp.nodes[c].parent}" }
                g[d.node].children.add(g[c])
                g[c].parents.add(g[d.node])
                g[c].treeParentId = g[d.node].id
            }
        }
        val seen = HashSet<Int>()
        for (it in inp.items) {
            require(seen.add(it.row)) { "REFUSED: item row ${it.row} twice" }
            require(inp.nodes[it.leaf].children.isEmpty()) { "REFUSED: item ${it.row} sits on internal node ${it.leaf}" }
            val e = Embedding(it.question, it.question, decodeVec(it.vec, inp.dim), it.category, it.row)
            g[it.leaf].queries.add(e)
            GraphNode.registerEmbedding(e)
        }
        // leaf vMF mean direction (the labeller ranks a leaf's samples by alignment with it)
        for (d in inp.nodes) if (d.children.isEmpty() && d.depth > 0) {
            val qs = g[d.node].queries
            val mu = FloatArray(inp.dim)
            for (q in qs) for (k in 0 until inp.dim) mu[k] += q.values[k]
            val nrm = kotlin.math.sqrt(mu.fold(0.0) { a, v -> a + v.toDouble() * v }).toFloat()
            if (nrm > 0f) for (k in mu.indices) mu[k] /= nrm
            g[d.node].vmfMu = mu
        }
        checkStructure(inp, g)
        return g
    }

    /** REFUSES unless every node's parent, children and branch item count equal the input's. */
    fun checkStructure(inp: Input, g: List<GraphNode>) {
        val byId = g.withIndex().associate { (i, n) -> n.id to i }
        for (d in inp.nodes) {
            val n = g[d.node]
            val ch = n.children.map { byId.getValue(it.id) }.sorted()
            check(ch == d.children.sorted()) { "REFUSED: node ${d.node} children changed: $ch vs ${d.children}" }
            val par = n.parents.map { byId.getValue(it.id) }
            check(par == listOfNotNull(d.parent)) { "REFUSED: node ${d.node} parents changed: $par" }
            val cnt = n.getAllQueriesInBranch().size
            check(cnt == d.n) { "REFUSED: node ${d.node} carries $cnt items, the input says ${d.n}" }
        }
    }

    /** Domain anchors from the input's declared categories; never opens a dataset DB. */
    class CategoryFetcher(config: TaxonomyConfig, private val cat: Map<String, String>, tmpDb: File) :
        MMLUDatasetFetcher(config, "", tmpDb.absolutePath) {
        override fun getDetailsForQuery(question: String): HFProRowData? =
            cat[question]?.let { HFProRowData(question = question, category = it) }
    }

    /** Usage tally shared by the clients. */
    class Tally {
        val lock = Mutex()
        var calls = 0
        var failed = 0
        var promptTokens = 0L
        var completionTokens = 0L
        val records = mutableListOf<CallRecord>()
    }

    /** No network: answers every structured call with a counted placeholder name. */
    class DryClient(val tally: Tally) : TaxonomyLlmClient {
        override suspend fun generateClusterLabel(prompt: String): String = error("not used by the post-pass")
        override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String =
            error("not used by the post-pass")
        override suspend fun queryModelStructured(modelName: String, systemPrompt: String?, userPrompt: String,
                                                  schema: JsonSchema): String {
            val k = tally.lock.withLock {
                tally.calls++
                tally.promptTokens += (userPrompt.length / 4).toLong() // characters / 4: an estimate, marked dry
                tally.records.add(CallRecord(tally.calls, sha256(userPrompt.toByteArray()),
                    ArcTaxonomyLLMClient.buildAzureSchemaInstruction(schema), userPrompt, "", null, null))
                tally.calls
            }
            return """{"label": "DRY $k"}"""
        }
        override fun setMaxParallel(limit: Int) {}
    }

    /** The Azure transport of [ArcTaxonomyLLMClient.queryModelStructured]'s Azure branch, non-streaming, counted. */
    class CountingAzureClient(private val model: ChatModel, val tally: Tally, private val maxAttempts: Int = 6) :
        TaxonomyLlmClient {
        override suspend fun generateClusterLabel(prompt: String): String = error("not used by the post-pass")
        override suspend fun queryModel(modelName: String, systemPrompt: String?, userPrompt: String): String =
            error("not used by the post-pass")
        override suspend fun queryModelStructured(modelName: String, systemPrompt: String?, userPrompt: String,
                                                  schema: JsonSchema): String {
            val sys = listOfNotNull(systemPrompt, ArcTaxonomyLLMClient.buildAzureSchemaInstruction(schema))
                .joinToString("\n\n")
            val req = ChatRequest.builder().messages(listOf(SystemMessage.from(sys), UserMessage.from(userPrompt))).build()
            var wait = 2000L
            var attempt = 0
            while (true) {
                attempt++
                try {
                    val r = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) { model.chat(req) }
                    val text = r.aiMessage().text() ?: ""
                    val u = r.tokenUsage()
                    tally.lock.withLock {
                        tally.calls++
                        tally.promptTokens += (u?.inputTokenCount() ?: 0).toLong()
                        tally.completionTokens += (u?.outputTokenCount() ?: 0).toLong()
                        tally.records.add(CallRecord(tally.calls, sha256(userPrompt.toByteArray()), sys, userPrompt,
                            text, u?.inputTokenCount(), u?.outputTokenCount()))
                    }
                    return text
                } catch (t: Throwable) {
                    tally.lock.withLock { tally.failed++ }
                    if (attempt >= maxAttempts) throw t
                    System.err.println("[FIXED-TREE-LABELS] attempt $attempt failed (${t.javaClass.simpleName}: " +
                        "${t.message?.take(200)}); retry in ${wait} ms")
                    delay(wait)
                    wait = (wait * 2).coerceAtMost(30_000L)
                }
            }
        }
        override fun setMaxParallel(limit: Int) {}
    }

    /**
     * ZERO-CALL transport preflight: the endpoint and key are present (never printed), the endpoint is an https URL
     * whose host resolves, the deployment name is set, and the model object builds. Returns the model; REFUSES
     * (IllegalStateException) otherwise. No request is sent.
     */
    fun preflight(env: Map<String, String?>, deployment: String, apiVersion: String,
                  resolve: (String) -> Unit = { h -> java.net.InetAddress.getByName(h) }): ChatModel {
        val ep = env["AZURE_AI_ENDPOINT"]?.trim().orEmpty()
        val key = env["AZURE_AI_API_KEY"]?.trim().orEmpty()
        check(ep.isNotEmpty()) { "REFUSED: AZURE_AI_ENDPOINT is blank (export the root .env first)" }
        check(key.isNotEmpty()) { "REFUSED: AZURE_AI_API_KEY is blank (export the root .env first)" }
        check(deployment.isNotBlank()) { "REFUSED: no deployment name" }
        val uri = runCatching { java.net.URI(ep) }.getOrNull()
        check(uri != null && uri.scheme == "https" && !uri.host.isNullOrBlank()) { "REFUSED: AZURE_AI_ENDPOINT is not an https URL" }
        runCatching { resolve(uri.host) }.onFailure { throw IllegalStateException("REFUSED: endpoint host does not resolve") }
        return AzureOpenAiChatModel.builder().endpoint(ep).apiKey(key).deploymentName(deployment)
            .serviceVersion(apiVersion).timeout(java.time.Duration.ofSeconds(90)).maxRetries(0).build()
    }

    data class Result(val output: Output, val records: List<CallRecord>)

    /** Runs the post-pass on the fixed tree with [client]; REFUSES on any structural change or unnamed node. */
    fun label(inputBytes: ByteArray, client: TaxonomyLlmClient, tally: Tally, model: String, dry: Boolean,
              parallelism: Int = 4): Result = runBlocking {
        val inp = json.decodeFromString<Input>(inputBytes.toString(Charsets.UTF_8))
        val g = buildGraph(inp)
        val cfg = TaxonomyConfig()
        cfg.execution.llmParallelism = parallelism
        check(cfg.formalism.anchorDepth == inp.anchor_depth) {
            "REFUSED: the labeller's anchor depth ${cfg.formalism.anchorDepth} != the input's ${inp.anchor_depth}"
        }
        val tmp = File.createTempFile("fixed_tree_labels_", ".db").also { it.deleteOnExit() }
        val fetcher = CategoryFetcher(cfg, inp.items.associate { it.question to it.category }, tmp)
        val splitter = TaxonomySplitter(cfg, client, fetcher, TaxonomyFitter(cfg))
        val anchorLabels = inp.nodes.filter { it.depth <= inp.anchor_depth }.associate { it.node to g[it.node].label }
        splitter.generateLabelsPostPass(g[0])
        checkStructure(inp, g)
        for ((u, l) in anchorLabels) check(g[u].label == l) { "REFUSED: anchor node $u was relabelled" }
        val bad = inp.nodes.filter { it.depth > inp.anchor_depth }.filter { d ->
            val l = g[d.node].label.orEmpty()
            l.isBlank() || l.startsWith("Emergent Concept") || l == "Discovered Concept"
        }
        val out = inp.nodes.map { d ->
            OutNode(d.node, d.parent, d.depth, d.n, d.keyword_name,
                if (d.depth > inp.anchor_depth) g[d.node].label else null,
                if (d.depth > inp.anchor_depth) g[d.node].description else null)
        }
        val o = Output(sha256(inputBytes), inp.dataset, model, dry, tally.calls, tally.failed, tally.promptTokens,
            tally.completionTokens, tally.promptTokens + tally.completionTokens,
            inp.nodes.count { it.depth > inp.anchor_depth } - bad.size, out)
        if (bad.isNotEmpty()) System.err.println("[FIXED-TREE-LABELS] ${bad.size} nodes without a name: ${bad.map { it.node }}")
        Result(o, tally.records.toList())
    }

    fun writeOnce(f: File, text: String) {
        java.nio.file.Files.newBufferedWriter(f.toPath(), Charsets.UTF_8, java.nio.file.StandardOpenOption.CREATE_NEW)
            .use { it.write(text) }
    }

    fun run(args: Array<String>, env: Map<String, String?> = System.getenv()): Int {
        fun arg(k: String) = args.indexOf(k).takeIf { it >= 0 && it + 1 < args.size }?.let { args[it + 1] }
        val inPath = arg("--in") ?: error("REFUSED: --in <labeller_input.json>")
        val outPath = arg("--out") ?: error("REFUSED: --out <labels.json>")
        val dry = "--dry-run" in args
        val deployment = arg("--model") ?: env["ARC_MODEL"] ?: TaxonomyConfig().llm.labelingModel.let {
            if (it == "ministral-3:14b") "Mistral-Large-3" else it
        }
        val apiVersion = arg("--api-version") ?: "2024-02-15-preview"
        val par = arg("--parallel")?.toIntOrNull() ?: 4
        val outF = File(outPath)
        val callsF = File("$outPath.calls.jsonl")
        check(!outF.exists() && !callsF.exists()) { "REFUSED: $outPath or its .calls.jsonl exists (write-once)" }
        val bytes = File(inPath).readBytes()
        val model = preflight(env, deployment, apiVersion)
        println("[FIXED-TREE-LABELS] transport preflight OK (zero calls): deployment $deployment, api $apiVersion")
        val tally = Tally()
        val client: TaxonomyLlmClient = if (dry) DryClient(tally) else CountingAzureClient(model, tally)
        val r = label(bytes, client, tally, deployment, dry, par)
        writeOnce(outF, Json { prettyPrint = true; encodeDefaults = true }.encodeToString(r.output))
        writeOnce(callsF, r.records.joinToString("") { json.encodeToString(it) + "\n" })
        println("[FIXED-TREE-LABELS] ${if (dry) "DRY RUN (no network)" else "RUN"}: ${r.output.nodes_labelled} nodes " +
            "named, calls ${r.output.calls}, failed attempts ${r.output.failed_attempts}, prompt tokens " +
            "${r.output.prompt_tokens}${if (dry) " (chars/4 estimate)" else ""}, completion tokens " +
            "${r.output.completion_tokens} -> $outPath")
        return if (r.output.nodes_labelled == r.output.nodes.count { it.llm_label != null }) 0 else 2
    }
}

// No `main` here: a second main class in the main source set breaks Spring Boot's resolveMainClassName (bootRun /
// bootJar). The entry point is src/test/kotlin/taxonomy/FixedTreeLabelMain.kt (as ThreadCapProbe), run by the
// JavaExec task `fixedTreeLabels` on the test runtime classpath.
