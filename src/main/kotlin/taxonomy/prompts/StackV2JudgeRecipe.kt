package taxonomy.prompts

import taxonomy.operations.PythonJson
import taxonomy.operations.RecipeKit
import java.security.MessageDigest

/**
 * STACK-v2, the judge recipe of record (docs/judge_v2_program.md), as the Kotlin production path
 * posts it under JUDGE-WIRING (docs/design/FRAMEWORK.md item 25).
 *
 * WHAT IS PINNED HERE. The Python record is `stack_judge.py --prompt v2 --judge grok`:
 *
 *   system = prompt_v2.v2_system_template()             (v1 system template, Kotlin-trimmed BEFORE
 *            .replace("$systemPrompt", anchor.system_prompt)  substitution, the 10 "// " comment lines
 *            .replace("$rubric", anchor.rubric)          removed, the both-correct block replaced by
 *            + "\n\n" + rejudge_grok.SCHEMA_INSTRUCTION  the verify-first block)
 *   user   = rejudge_grok.USER_TEMPLATE with $query = question + reference block (rejudge_reference
 *            .with_reference: U+2014 EM DASH in the marker), $traceA/$traceB = rejudge_grok.robust_trace
 *            (TracePreparation here), in both presentation orders
 *   body   = json.dumps({"model": ..., "max_tokens": ..., "messages": [system, user]})  (PythonJson)
 *
 * The templates below are declared as raw strings with `${'$'}` placeholders and trimmed at class
 * initialisation, BEFORE any substitution. That is the Python order and it differs from the v1
 * Kotlin path (`buildJudgeSystemPrompt` interpolates first and trims afterwards), whose `lines()`
 * pass would normalise a `\r` inside a trace or rubric and drop a trailing blank line of the
 * rubric; the Python record has neither effect. Trimming here also means a CRLF working copy
 * (this checkout is `w/crlf`) cannot leak a `\r` into the posted bytes. Every template and the
 * schema instruction are pinned byte-for-byte against Python-generated fixtures
 * (StackV2JudgeRecipeTemplateTest); the schema instruction is additionally pinned to
 * `ArcTaxonomyLLMClient.buildAzureSchemaInstruction(judgeSchema)` so the two ports cannot drift.
 *
 * ANSWER-KEY BLINDNESS. `assemble` takes a question id, its text and the two traces; the kit's
 * reference is the cached grok-reasoning SOLVE (a model's answer, wrong on ~14% of questions), and
 * the kit carries no `correct` column at all. `gt_answer` is not a parameter on this path.
 */
object StackV2JudgeRecipe {

    const val RECIPE_NAME = "STACK-v2"

    /** `prompt_v2.v2_system_template()`: `$systemPrompt` / `$rubric` are substituted by [buildSystem]. */
    val V2_SYSTEM_TEMPLATE: String = """
        ${'$'}systemPrompt

        ────────────────────────────────────────
        EVALUATION MECHANICS (non-negotiable)
        ────────────────────────────────────────
        Bias suppression — ignore completely:
        • Response length, verbosity, or token count
        • Formatting: markdown, LaTeX, bullet points, plain prose — all equal
        • Model name, model family, or any identity signal
        • Stylistic elegance or fluency unrelated to correctness

        Evaluation order — follow exactly:
        1. CRITIQUE Model A: assess its reasoning against the rubric. Identify correct steps, errors, gaps.
        2. CRITIQUE Model B: same process, independently of Model A.
        3. COMPARE: identify the decisive difference between A and B.
        4. DECIDE: declare the winner — either "Model A", "Model B", or "TIE".

        Correctness first — verify before you compare:
        The question carries a reference solution (marked as produced independently; it may be wrong).
        Before critiquing, extract each model's FINAL ANSWER and check it against the reference and
        against your own reading of the question. A response whose final answer is wrong cannot win
        against a response whose final answer is right, whatever its reasoning looks like.

        When BOTH final answers are right:
        Prefer the response with fewer errors or unsupported steps in its reasoning. If neither has
        any, output TIE. Depth, breadth, scope, edge cases and elaboration are NOT criteria — a short
        correct response ties a long correct response.
        Reserve confidence 0.95–1.0 only for cases with overwhelming evidence. Default to 0.7–0.85 for clear wins.

        Your rubric:
        ${'$'}rubric
    """.trimIndent()

    /** `rejudge_grok.USER_TEMPLATE` (= `buildJudgeUserPrompt`'s raw template, trimmed before substitution). */
    val USER_TEMPLATE: String = """
        [Question]
        ${'$'}query

        [Model A's Response]
        ${'$'}traceA

        [Model B's Response]
        ${'$'}traceB

        ────────────────────────────────────────
        Your task is to determine superior reasoning quality based solely on the logical rigour and domain
        soundness of its response.

        If both models are genuinely equivalent, output winner: "TIE" with confidence ≤ 0.5.

        Evaluate following the mandatory sequence:

        Step 1 — Critique Model A (2–4 sentences referencing your rubric)
        Step 2 — Critique Model B (2–4 sentences referencing your rubric)
        Step 3 — Compare: what is the decisive difference in reasoning quality?
        Step 4 — Verdict

        Output ONLY the following JSON. No prose before or after. No markdown fences.

        {
          "critique_a": "<your critique of Model A>",
          "critique_b": "<your critique of Model B>",
          "comparison": "<decisive difference in reasoning quality>",
          "winner": "Model A, Model B, or TIE",
          "confidence": <0.0 to 1.0 (default to 0.7-0.85 for clear wins, reserve 0.95-1.0 only for overwhelming evidence)>
        }
    """.trimIndent()

    /**
     * `rejudge_grok.SCHEMA_INSTRUCTION`: the Azure structured-output fallback that
     * `ArcTaxonomyLLMClient.buildAzureSchemaInstruction` renders for `judgeSchema`, including the
     * quirk that the number property renders as `<string>`. Pinned against the live builder.
     */
    const val SCHEMA_INSTRUCTION: String =
        "You MUST respond with a single valid JSON object and nothing else. " +
            "Required shape: { \"critique_a\": <Critique of Model A's response against the rubric>, " +
            "\"critique_b\": <Critique of Model B's response against the rubric>, " +
            "\"comparison\": <The decisive difference in reasoning quality between A and B>, " +
            "\"winner\": <Model A, Model B, or TIE>, \"confidence\": <string> }"

    /** `rejudge_reference.with_reference`: the marker carries U+2014 EM DASH, not a hyphen. */
    const val REFERENCE_MARKER: String = "[Reference solution — produced independently, may be wrong]"

    fun withReference(query: String, letter: String, optionText: String): String =
        query + "\n\n" + REFERENCE_MARKER + "\n(" + letter + ") " + optionText

    fun buildSystem(anchorSystemPrompt: String, anchorRubric: String): String =
        V2_SYSTEM_TEMPLATE.replace("\$systemPrompt", anchorSystemPrompt).replace("\$rubric", anchorRubric) +
            "\n\n" + SCHEMA_INSTRUCTION

    fun buildUser(query: String, traceA: String, traceB: String): String =
        USER_TEMPLATE.replace("\$query", query).replace("\$traceA", traceA).replace("\$traceB", traceB)

    /** `rejudge_reasoning.call_judge_full`'s body: key order model / max_tokens / messages [/ temperature]. */
    fun payloadBody(system: String, user: String, model: String, maxTokens: Int, temperature: Double?): ByteArray {
        val body = linkedMapOf<String, Any?>(
            "model" to model,
            "max_tokens" to maxTokens,
            "messages" to listOf(
                linkedMapOf("role" to "system", "content" to system),
                linkedMapOf("role" to "user", "content" to user)
            )
        )
        if (temperature != null) body["temperature"] = temperature
        return PythonJson.dumpsBytes(body)
    }

    data class Params(val model: String, val maxTokens: Int, val temperature: Double?) {
        val temperatureLabel: String get() = temperatureLabelOf(temperature)
    }

    /** The literal recorded for the temperature: `"omitted"` when the field is absent, else Python's repr. */
    fun temperatureLabelOf(t: Double?): String = if (t == null) "omitted" else PythonJson.pythonFloatRepr(t)

    sealed class Assembly {
        data class Skipped(val reason: String) : Assembly()
        data class Assembled(
            val anchor: String,
            val refLetter: String,
            val system: String,
            val user1: String,
            val user2: String,
            val body1: ByteArray,
            val body2: ByteArray
        ) : Assembly() {
            val sha1: String get() = sha256Hex(body1)
            val sha2: String get() = sha256Hex(body2)
            val promptSha1: String get() = promptSha(system, user1)
            val promptSha2: String get() = promptSha(system, user2)
        }
    }

    /**
     * Pure assembly: no I/O, no call. `questionText` is the eval row's `question_text` WITHOUT an
     * options block (the recipe requires `judgeOptionMode = RESOLVED`, under which the query is the
     * bare stem); `traceA`/`traceB` are `TracePreparation.robustTrace` outputs.
     */
    fun assemble(kit: RecipeKit, questionId: Int, questionText: String, traceA: String, traceB: String, params: Params): Assembly {
        val anchor = kit.anchorOf(questionId) ?: return Assembly.Skipped("no anchor for question $questionId in kit ${kit.kitHash}")
        val ref = kit.referenceOf(questionId) ?: return Assembly.Skipped("no reference for question $questionId in kit ${kit.kitHash}")
        val (sp, rb) = kit.rubric(anchor)
            ?: throw IllegalStateException("kit ${kit.kitHash} routes question $questionId to anchor '$anchor' but carries no rubric for it")
        val system = buildSystem(sp, rb)
        val query = withReference(questionText, ref.letter, ref.text)
        val user1 = buildUser(query, traceA, traceB)
        val user2 = buildUser(query, traceB, traceA)
        return Assembly.Assembled(
            anchor = anchor, refLetter = ref.letter, system = system, user1 = user1, user2 = user2,
            body1 = payloadBody(system, user1, params.model, params.maxTokens, params.temperature),
            body2 = payloadBody(system, user2, params.model, params.maxTokens, params.temperature)
        )
    }

    fun sha256Hex(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }

    fun sha256Hex(s: String): String = sha256Hex(s.toByteArray(Charsets.UTF_8))

    /** sha256 over `system` + NUL + `user` (UTF-8): identifies the prompt pair independently of the body envelope. */
    fun promptSha(system: String, user: String): String =
        sha256Hex(system.toByteArray(Charsets.UTF_8) + byteArrayOf(0) + user.toByteArray(Charsets.UTF_8))

    /**
     * `deployment_fingerprint`: sha256(model|apiVersion|maxTokens|temperatureLabel|recipe|kitHash|
     * sha(v2 template)|sha(SCHEMA_INSTRUCTION))[:16]. Rows with different fingerprints are never
     * pooled on one board (protocol guard rule 11).
     */
    fun deploymentFingerprint(model: String, apiVersion: String, maxTokens: Int, temperatureLabel: String, kitHash: String): String =
        sha256Hex(
            listOf(model, apiVersion, maxTokens.toString(), temperatureLabel, RECIPE_NAME, kitHash,
                sha256Hex(V2_SYSTEM_TEMPLATE), sha256Hex(SCHEMA_INSTRUCTION)).joinToString("|")
        ).substring(0, 16)
}
