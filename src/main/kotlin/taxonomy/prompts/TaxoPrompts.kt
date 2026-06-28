package taxonomy.prompts

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.slf4j.LoggerFactory

/**
 * Encapsulates refined, fault-resilient prompts for the Taxonomy Engine.
 * Designed to ensure semantic coherence and prevent naming collisions.
 */
object TaxoPrompts {

    private val log = LoggerFactory.getLogger(TaxoPrompts::class.java)
    private const val JSON_STRICT = "IMPORTANT: Return ONLY raw JSON. No markdown. Output must start with { and end with }."

    /**
     * Strips markdown code fences that some models (e.g. Mistral-Large-3 on Azure)
     * emit despite being instructed not to. Handles both:
     *   ```json\n{...}\n```
     *   ```\n{...}\n```
     * and bare {…} with no fences. Trims surrounding whitespace before returning.
     */
    private fun stripCodeFences(raw: String): String {
        val trimmed = raw.trim()
        // Fast path: already a bare JSON object or array
        if (trimmed.startsWith("{") || trimmed.startsWith("[")) return trimmed
        // Remove opening fence (```json or ``` alone on its own line)
        val afterOpen = trimmed
            .removePrefix("```json")
            .removePrefix("```")
            .trimStart('\n', '\r', ' ')
        // Remove closing fence
        val afterClose = if (afterOpen.endsWith("```")) {
            afterOpen.dropLast(3).trimEnd('\n', '\r', ' ')
        } else afterOpen
        return afterClose.trim()
    }

    /**
     * Hardened prompt for distilling a raw query into a high-signal semantic signature.
     * Utilizes the initial domain context to ground the keyword extraction while remaining 
     * open to cross-disciplinary epistemic overlap.
     */
    fun getDistillationPrompt(query: String, domain: String): String {
        return """
            You are a strict semantic extractor. Your goal is to identify the core technical or conceptual "Semantic Signature" of a query.
            
            [Constraints]
            1. STRICT: Use ONLY terms present in the raw query. Do NOT add external information, synonyms, or related concepts.
            2. Minimalist: If only 1 or 2 technical terms exist, output ONLY those. Do NOT elaborate or try to reach a keyword count.
            3. Denoising: Remove question markers (Which, What), prepositions, and conversational filler.
            4. Domain Lens: Interpret terms through the lens of '$domain', but do not force them into the domain if they don't belong.

            [Output Format]
            Output ONLY the keywords or key phrases, separated by commas. No preambles, no explanation, no markdown.

            Raw Query: $query
            Semantic Signature:
        """.trimIndent()
    }

    /**
     * Highly refined, taxonomically-grounded labeling prompt.
     * Uses query samples, parent context, and branch history to synthesize
     * precise, human-readable semantic labels based on shared patterns.
     */
    fun clusterLabeling(
        querySamples: List<String>,
        parentLabel: String,
        siblingLabels: List<String>,
        branchHistory: List<String> = emptyList(),
        domainAnchors: List<String> = emptyList(),
        childLabels: List<String> = emptyList(),
        depth: Int
    ): String {
        val siblings = if (siblingLabels.isEmpty()) "None" else siblingLabels.joinToString(", ")
        val samples = querySamples.joinToString("\n") { "- $it" }
        val lineage = if (branchHistory.isEmpty()) "Root" else branchHistory.joinToString(" > ")
        val anchors = if (domainAnchors.isEmpty()) "Unknown" else domainAnchors.joinToString(", ")
        val children = if (childLabels.isEmpty()) "None" else childLabels.joinToString(", ")

        return """Task: Synthesize a highly precise, professional taxonomic concept label for a newly identified semantic cluster.

[Taxonomic Context & Domain Grounding]
The cluster's questions primarily come from the following expert-annotated subject domains:
- Ground Truth Domain Anchors: $anchors

[Lineage Hierarchy Context]
- Path Lineage: $lineage
- Parent Domain (Broad Context): $parentLabel
- Sibling Domains (Contrastive Context): $siblings
- Child Concepts (If Any): $children

[Representative Query Samples from the Cluster]
Analyse these representative queries carefully to identify their common denominator:
$samples

[Rigorous Semantic Synthesis Strategy]
1. Comparative Query Analysis:
   - Examine all query samples.
   - Identify the specific underlying topic, mechanism, task, or concept that links all of them.
   - The label must fit ALL sample queries; if any query feels clearly out of place, refine the label.

2. Lineage Integration:
   - Ground the label in the parent domain ($parentLabel) and domain anchors ($anchors).
   - The label must be a logical sub-partition (narrower refinement) of the parent domain, consistent with the anchors.
   - Prefer established subfield terminology (e.g., “Classical Mechanics”, “Bayesian Inference”, “Corporate Finance”) when it matches the samples.

3. Distinctness & Contrast:
   - Compare against sibling domains ($siblings).
   - The generated label must not overlap semantically with siblings or simply duplicate them.
   - Avoid reusing the exact same head noun as a sibling label unless you add a clear qualifier.

4. Granularity Matching (Depth $depth):
   - Match the specificity and technical complexity of the siblings at this depth.
   - If siblings are very specialized (e.g., "Pricing Models", "Capital Structure"), avoid generic labels (e.g., "Business Math").

5. Constraints:
   - The label must be a clear, technical, concise noun phrase (1–4 words).
   - Avoid generic words like "General", "Other", "Miscellaneous", "Theory", or repeating the parent label "$parentLabel" without refinement.
   - Use simple spaces to separate words. Do NOT use underscores, dashes, or special characters.
   - If linking two terms, use "and" (e.g., "Microeconomics and Policy").

[Expected Output Format]
Provide the result as a strictly formatted JSON object.

$JSON_STRICT
{ 
  "label": "Precise Dynamic Concept Name", 
  "description": "A precise 1-sentence description."
}
""".trimIndent()
    }

    fun parseClusterLabel(jsonResponse: String): String? {
        return try {
            val cleaned = stripCodeFences(jsonResponse)
            val root = Json { ignoreUnknownKeys = true }.parseToJsonElement(cleaned).jsonObject
            val label = root["label"]?.jsonPrimitive?.content
            if (label.isNullOrBlank()) {
                log.warn("Malformed JSON: 'label' property is missing or empty. Raw input:\n$jsonResponse")
                null
            } else {
                label
            }
        } catch (e: Exception) {
            log.warn("Malformed JSON parsing failed: ${e.message}. Raw input:\n$jsonResponse")
            null
        }
    }
}
