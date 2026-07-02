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
Task: Induce domain adjudication guidelines from a corpus of expert‑verified multiple‑choice problems in the specialized subdomain "$domainLabel".

[Corpus Batch]
$items

[Instructions]
Analyze the reasoning and steps used in the Correct Reasoning to solve each item.
Extract the implicit rules, conceptual foundations, core formulas/laws, and technical nuances that are necessary to solve these questions correctly.

[Domain & Subdomain Context]
Treat "$domainLabel" as a narrow, specialized topic within its broader academic field.
Focus on what distinguishes this subdomain from neighbouring topics (e.g., specific methods, formalisms, typical failure modes).

Important constraints:
- Focus on PROCEDURAL LOGIC and VALIDITY of reasoning, not memorized facts or specific numbers.
- Abstract away from individual questions: do NOT restate any question text or correct option; only describe general patterns.
- Each rule must describe a TESTABLE behaviour of a candidate answer (e.g., "checks dimensional consistency in physics equations") rather than repeating content from a particular question.
- Limit yourself to 8–15 high‑level rules that cover the subdomain.
- Correctness of the final conclusion is primary; procedural elegance is secondary.

[Output Format]
Return ONLY a JSON array. No markdown, no prose, no comments.
The array must look like:

[
  { "importance": "CRITICAL", "rule": "Must verify Bayes’ theorem is applied correctly in conditional probability chains." },
  { "importance": "IMPORTANT", "rule": "..." }
]

- importance ∈ {"CRITICAL","IMPORTANT","USEFUL"}
- rule is a single concise sentence.
- Output must start with [ and end with ].
""".trimIndent()
    }


    private const val JSON_ARRAY_STRICT =
        "IMPORTANT: Return ONLY raw JSON array. No markdown. Output must start with [ and end with ]."

    /**
     * Phase 2: Synthesize Global Guidelines from Batch Results.
     */
    fun synthesizeGlobalGuidelines(partialGuidelines: List<String>): String {
        val partials = partialGuidelines.joinToString("\n\n")
        return """Task: Synthesize a master adjudication policy from multiple batch analyses for the same domain.

[Partial Batch Guidelines]
$partials

[Instructions]

Deduplicate: Merge overlapping or near‑duplicate rules into a single high‑level axiom.
Generalize: Ensure the resulting axioms cover the entire domain, not just specific questions from the samples.
Structure: Group rules into 3–6 orthogonal dimensions (e.g., “Logical Validity”, “Domain‑Specific Constraints”, “Use of Evidence”, “Handling Uncertainty”).
Weight: Assign each rule an importance level that reflects how critical it is when comparing two answers in this domain.

[Output Format]
$JSON_ARRAY_STRICT

Return ONLY a JSON array of master axioms, for example:

[
    { "importance": "CRITICAL",
    "dimension": "Probabilistic Reasoning",
    "rule": "Prefer answers that correctly apply conditional probability and Bayes’ theorem to the given events."
    },
    { "importance": "IMPORTANT",
    "dimension": "Use of Evidence",
    "rule": "Reward answers that explicitly relate intermediate steps to the information given in the question."
    } 
]

importance ∈ {"CRITICAL","IMPORTANT","USEFUL"}

dimension is a short label for the aspect being evaluated.
rule is a single concise sentence describing how to judge that aspect.

Output must start with [ and end with ].
    """.trimIndent()
    }

    private const val JSON_OBJECT_STRICT =
        "IMPORTANT: Return ONLY raw JSON object. No markdown. Output must start with { and end with }."

    /**
     * Phase 3: Final System Prompt & Rubric Synthesis.
     */
    fun synthesizeFinalJudge(masterGuidelines: String, domainLabel: String): String {
        return """
Task: Synthesize a highly specialized AI judge for $domainLabel multiple‑choice questions.

[Master Domain Axioms]
$masterGuidelines

[Instructions]
Create an expert evaluative persona for $domainLabel.

The judge’s job is to decide which of two AI‑generated reasoning traces (A or B) better answers a multiple‑choice question in this domain.

Scope & leaf node specialization:
- You must specialize the judge to the narrow, leaf-node subdomain "$domainLabel".
- The judge should focus strictly on criteria, axioms, and edge cases relevant to "$domainLabel" and ignore generic qualities (e.g. style, formatting, token count) that do not affect technical correctness.

Core behaviour:
- Primary objective: Evaluate and choose the response that has the most logically sound, technically correct, and well-justified reasoning leading to the correct answer.
- TIES ARE STRICTLY FORBIDDEN. You must declare one model as the winner ("Model A" or "Model B"). If they are very close, look at the technical details, mathematical precision, or adherence to the master axioms to break the tie and declare a winner.
- When both answers arrive at the correct option: Compare the quality of their explanations. Prefer the one that is more mathematically precise, follows the domain axioms, states clear intermediate steps, and is easier to verify.
- When both answers are incorrect: Prefer the one that shows better partial reasoning, fewer conceptual errors, and is closer to the correct setup.
- Penalize lazy responses: Heavily penalize answers that state the correct option letter without any reasoning or justification.

Internal evaluation process (for your own behaviour):
1. Critique A against the master axioms.
2. Critique B against the master axioms.
3. Compare A and B, focusing on correctness of conclusion, logical validity, and domain‑specific checks.
4. Decide the winner: "Model A" or "Model B" (Tie is forbidden).

[Output Format]
$JSON_OBJECT_STRICT

Return ONLY a JSON object with exactly these two string keys — no other keys, no nesting:

{
  "system_prompt": "",
  "rubric": ""
}

- system_prompt is a concise but complete system message that defines the judge persona, evaluation principles, and strict leaf-node guidelines (no ties, direct comparison of Model A and Model B).
- rubric is a short, human‑readable bullet‑point checklist (using - bullets) that the judge should internally follow when comparing A and B. It should cover:
  - how to assess correctness of the final answer,
  - how to assess soundness of reasoning,
  - how to apply the domain‑specific axioms for $domainLabel,
  - how to penalise common failure modes in this specific leaf domain,
  - how to compare the two models and break ties.

Both values MUST be plain strings. No nested JSON or additional keys. Output must start with { and end with }.
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
