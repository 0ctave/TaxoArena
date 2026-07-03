package taxonomy.prompts

import kotlinx.serialization.json.*
import org.slf4j.LoggerFactory

/**
 * Meta-prompts for grounded Agent Judge induction.
 * Optimized for Recursive Batch Processing of MMLU-Pro corpora.
 */
object JudgePrompts {

    private val log = LoggerFactory.getLogger(JudgePrompts::class.java)
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }
    fun parseJudgeJson(raw: String): Pair<String, String>? {
        // Strip markdown fences and any trailing garbage after the closing }
        val cleaned = raw.trim()
            .removePrefix("```json").removePrefix("```").trim()
            .let { it.substring(0, it.lastIndexOf('}') + 1) }  // trim anything after last }

        return try {

            val root = json.parseToJsonElement(cleaned).jsonObject

            val systemPrompt = when (val sp = root["system_prompt"]) {
                is JsonPrimitive -> sp.contentOrNull
                is JsonObject -> sp["role"]?.jsonPrimitive?.contentOrNull  // fallback for old runs
                else -> null
            }
            val rubric = root["rubric"]?.jsonPrimitive?.contentOrNull ?: ""

            if (systemPrompt.isNullOrBlank()) {
                log.warn("Malformed JSON: system_prompt missing/blank. Raw input:\n$raw")
                return null
            }

            systemPrompt to rubric
        } catch (e: Exception) {
            log.warn("Malformed JSON parse error: ${e.message}. Raw input:\n$raw")
            null
        }
    }

    /**
     * Phase 1: Induce Partial Guidelines from a batch of Q+Choices+A.
     */
    fun induceBatchGuidelines(
        corpusItems: List<String>,
        domainLabel: String
    ): String {
        val items = corpusItems.joinToString("\n---\n")
        return """
Task: Induce domain adjudication guidelines from a corpus of expert-verified multiple-choice problems in the specialized subdomain "${'$'}domainLabel".

[Corpus Batch]
$items

[Instructions]
Analyze the reasoning and steps used in the Correct Reasoning to solve each item.
Extract the implicit rules, conceptual foundations, core formulas/laws, and technical nuances necessary to solve these questions correctly.

[Domain & Subdomain Context]
Treat "$domainLabel" as a narrow, specialized topic within its broader academic field.
Focus on what distinguishes this subdomain from neighbouring topics (specific methods, formalisms, typical failure modes).

Constraints:
- Focus on PROCEDURAL LOGIC and VALIDITY of reasoning, not memorized facts or specific numbers.
- Abstract away from individual questions: do NOT restate any question text or correct option — describe general patterns only.
- Each rule must describe a TESTABLE behaviour of a candidate answer (e.g. "checks dimensional consistency in physics equations").
- Limit to 8–15 high-level rules covering the subdomain.
- Correctness of the final conclusion is primary; procedural elegance is secondary.

[Output Format]
Return ONLY a JSON array. No markdown, no prose, no comments. Output must start with [ and end with ].

[
  { "importance": "CRITICAL", "rule": "Must verify Bayes' theorem is applied correctly in conditional probability chains." },
  { "importance": "IMPORTANT", "rule": "..." }
]

importance ∈ {"CRITICAL","IMPORTANT","USEFUL"}
rule is a single concise sentence.
""".trimIndent()
    }


    private const val JSON_ARRAY_STRICT =
        "IMPORTANT: Return ONLY raw JSON array. No markdown. Output must start with [ and end with ]."

    /**
     * Phase 2: Synthesize Global Guidelines from Batch Results.
     */
    fun synthesizeGlobalGuidelines(partialGuidelines: List<String>): String {
        val partials = partialGuidelines.joinToString("\n\n")
        return """
Task: Synthesize a master adjudication policy from multiple batch analyses for the same domain.

[Partial Batch Guidelines]
$partials

[Instructions]
Deduplicate: Merge overlapping or near-duplicate rules into a single high-level axiom.
Generalize: Ensure axioms cover the entire domain, not just specific sampled questions.
Structure: Group rules into 3–6 orthogonal dimensions (e.g. "Logical Validity", "Domain-Specific Constraints", "Use of Evidence", "Handling Uncertainty").
Weight: Assign each rule an importance level reflecting how critical it is when comparing two answers in this domain.

[Output Format]
Return ONLY a JSON array. No markdown. Output must start with [ and end with ].

[
  { "importance": "CRITICAL", "dimension": "Probabilistic Reasoning",
    "rule": "Prefer answers that correctly apply conditional probability and Bayes' theorem to the given events." },
  { "importance": "IMPORTANT", "dimension": "Use of Evidence",
    "rule": "Reward answers that explicitly relate intermediate steps to the information given in the question." }
]

importance ∈ {"CRITICAL","IMPORTANT","USEFUL"}
dimension is a short label for the aspect being evaluated.
rule is a single concise sentence describing how to judge that aspect.
Output must start with [ and end with ].
    """.trimIndent()
    }


    /**
     * Phase 3: Final System Prompt & Rubric Synthesis.
     */
    fun synthesizeFinalJudge(masterGuidelines: String, domainLabel: String): String {
        return """
Task: Synthesize a highly specialized AI judge persona for "$domainLabel" multiple-choice questions.

[Master Domain Axioms]
$masterGuidelines

[Instructions]
Create an expert domain persona for "$domainLabel". This persona defines WHAT to evaluate
(domain knowledge, axioms, failure modes) — NOT HOW to evaluate. Verdict format, tie policy,
and evaluation steps are controlled externally and must NOT appear here.

Persona requirements:
- Embody deep expertise in "$domainLabel": key formalisms, typical misconceptions, common
  pitfalls, and what distinguishes a correct from a plausible-but-wrong answer in this subdomain.
- Specialise strictly to "$domainLabel" — ignore generic qualities that do not affect technical
  correctness: formatting, markdown, response length, stylistic elegance, model identity.
- Do NOT include any verdict format instruction, tie policy, or step-by-step evaluation procedure.

Rubric requirements:
- A short bullet-point checklist (using - bullets) the judge applies to each individual response.
- Cover: correctness of final answer, soundness of reasoning chain, adherence to domain axioms,
  penalisation of failure modes specific to "$domainLabel".
- Do NOT include any "compare A vs B", "pick a winner", or tie-break instructions.

[Output Format]
Return ONLY a JSON object with exactly these two string keys. No markdown. Output must start with { and end with }.

{
  "system_prompt": "<expert domain persona — who the judge is and what domain knowledge it applies>",
  "rubric": "<bullet checklist of domain-specific evaluation criteria only>"
}

Both values MUST be plain strings. No nested JSON. No additional keys.
""".trimIndent()
    }

    private const val JSON_STRICT =
        "IMPORTANT: Return ONLY raw JSON. No markdown. Output must start with { and end with }."

    fun repairMalformedJson(malformedOutput: String): String {
        return """
    $JSON_STRICT
    Task: Repair the following malformed JSON so it is valid and parseable.
    Return ONLY the corrected JSON object. Do not explain anything.
    
    [Malformed Input]
    $malformedOutput
    """.trimIndent()
    }
}
