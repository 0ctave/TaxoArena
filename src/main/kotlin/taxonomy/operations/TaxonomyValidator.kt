package taxonomy.operations

import dev.langchain4j.model.chat.request.json.JsonObjectSchema
import dev.langchain4j.model.chat.request.json.JsonSchema
import kotlinx.serialization.json.*
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import taxonomy.config.TaxonomyConfig
import taxonomy.model.GraphNode

/**
 * Executes a thorough automatic evaluation suite using the configured judge model to determine the quality of the
 * generated taxonomy. Measures Node-wise Path Granularity, Level-wise Sibling Coherence, and Node-wise Dimension Alignment.
 *
 * All LLM calls use structured JSON output (JsonSchema ResponseFormat) to guarantee syntactically
 * valid, parseable responses without any post-hoc string cleanup.
 * On Azure the structured-output path falls back to prompt-injected schema instructions, so the
 * model may still wrap its response in markdown code fences. stripCodeFences() handles that.
 */
@Service
class TaxonomyValidator(
    private val config: TaxonomyConfig,
    private val llmClient: TaxonomyLlmClient
) {
    private val log = LoggerFactory.getLogger("taxonomy.Validator")
    private val json = Json { ignoreUnknownKeys = true }

    // --- Pre-built reusable schemas ---

    /** Schema for boolean evaluations: { "result": 0 or 1, "rationalization": "..." } */
    private val booleanSchema = JsonSchema.builder()
        .name("BooleanEval")
        .rootElement(
            JsonObjectSchema.builder()
                .addIntegerProperty("result", "1 if the condition is true, 0 if false")
                .addStringProperty("rationalization", "Brief explanation of the decision")
                .required("result", "rationalization")
                .build()
        )
        .build()

    /** Schema for coherence score evaluations: { "coherenceScore": 0.0-1.0, "rationalization": "..." } */
    private val coherenceSchema = JsonSchema.builder()
        .name("CoherenceEval")
        .rootElement(
            JsonObjectSchema.builder()
                .addNumberProperty("coherenceScore", "A score between 0.0 (completely incoherent) and 1.0 (perfectly coherent)")
                .addStringProperty("rationalization", "Brief explanation of the score")
                .required("coherenceScore", "rationalization")
                .build()
        )
        .build()

    data class ValidationSummary(
        val avgPathGranularity: Double,
        val avgSiblingCoherence: Double,
        val avgDimensionAlignment: Double,
        val taxonomyScore: Double
    )

    /**
     * Strips markdown code fences that Azure models emit despite schema instructions.
     * Mirrors the same helper in TaxoPrompts — kept local to avoid a cross-object dependency.
     */
    private fun stripCodeFences(raw: String): String {
        val trimmed = raw.trim()
        if (trimmed.startsWith("{") || trimmed.startsWith("[")) return trimmed
        val afterOpen = trimmed
            .removePrefix("```json")
            .removePrefix("```")
            .trimStart('\n', '\r', ' ')
        return if (afterOpen.endsWith("```")) afterOpen.dropLast(3).trimEnd('\n', '\r', ' ') else afterOpen
    }

    suspend fun validateTaxonomy(root: GraphNode): ValidationSummary {
        log.info("==========================================================")
        log.info("   LAUNCHING AUTOMATED LLM EVALUATION SUITE")
        log.info("   Model Endpoint: ${config.llm.judgeModel}")
        log.info("==========================================================")
        val allNodes = getAllNodes(root)

        var pathGranCount = 0
        var pathGranSuccess = 0
        var dimensionAlignCount = 0
        var dimensionAlignSuccess = 0

        // 1. Path Granularity & Dimension Alignment (Node-wise)
        for (node in allNodes.filter { it.depth > 0 }) {
            val parent = node.parents.firstOrNull() ?: continue
            pathGranCount++

            val granularityPrompt = """
                [Path Granularity Evaluation]
                Parent Concept Label: ${parent.label}
                Child Concept Label: ${node.label}

                Task: Does this child concept represent a narrower, more specific logical subdivision or refinement of the parent concept?
                Set "result" to 1 if yes, 0 if no. Provide a brief rationalization.
            """.trimIndent()

            try {
                val granRes = llmClient.queryModelStructured(config.llm.judgeModel, null, granularityPrompt, booleanSchema)
                val isGranOk = json.parseToJsonElement(stripCodeFences(granRes)).jsonObject["result"]?.jsonPrimitive?.intOrNull == 1
                if (isGranOk) pathGranSuccess++
                log.info("  - Edge [${parent.label} -> ${node.label}] Granularity Preserved: $isGranOk")
            } catch (e: Exception) {
                log.warn("Failed path granularity evaluation for [${parent.label} -> ${node.label}]: ${e.message}")
            }

            dimensionAlignCount++
            val alignPrompt = """
                [Dimension Alignment Evaluation]
                Taxonomy Root Topic: ${root.label}
                Concept: ${node.label}

                Task: Is this concept logically relevant to the root topic and within its broader semantic dimension?
                Set "result" to 1 if yes, 0 if no. Provide a brief rationalization.
            """.trimIndent()

            try {
                val alignRes = llmClient.queryModelStructured(config.llm.judgeModel, null, alignPrompt, booleanSchema)
                val isAlignOk = json.parseToJsonElement(stripCodeFences(alignRes)).jsonObject["result"]?.jsonPrimitive?.intOrNull == 1
                if (isAlignOk) dimensionAlignSuccess++
                log.info("  - Node [${node.label}] Dimension Alignment: $isAlignOk")
            } catch (e: Exception) {
                log.warn("Failed dimension alignment evaluation for [${node.label}]: ${e.message}")
            }
        }

        // 2. Sibling Coherence (Level-wise)
        var coherenceSum = 0.0
        var coherenceCount = 0

        for (node in allNodes.filter { it.children.size > 1 }) {
            coherenceCount++
            val siblings = node.children.map { it.label }.joinToString(", ")
            val coherencePrompt = """
                [Sibling Coherence Evaluation]
                Parent Concept: ${node.label}
                Sibling Concepts Group: [$siblings]

                Task: Determine whether these siblings form a coherent set representing the same level of specificity and granularity under the parent.
                Set "coherenceScore" to a value between 0.0 (completely incoherent) and 1.0 (perfectly coherent). Provide a brief rationalization.
            """.trimIndent()

            try {
                val cohRes = llmClient.queryModelStructured(config.llm.judgeModel, null, coherencePrompt, coherenceSchema)
                val score = json.parseToJsonElement(stripCodeFences(cohRes)).jsonObject["coherenceScore"]?.jsonPrimitive?.doubleOrNull ?: 0.0
                coherenceSum += score
                log.info("  - Sibling Group under [${node.label}] Coherence Score: ${"%.2f".format(java.util.Locale.US, score)}")
            } catch (e: Exception) {
                log.warn("Failed sibling coherence evaluation under [${node.label}]: ${e.message}")
            }
        }

        val avgPathGran = if (pathGranCount > 0) pathGranSuccess.toDouble() / pathGranCount else 1.0
        val avgDimensionAlign = if (dimensionAlignCount > 0) dimensionAlignSuccess.toDouble() / dimensionAlignCount else 1.0
        val avgSiblingCoh = if (coherenceCount > 0) coherenceSum / coherenceCount else 1.0

        val overallScore = (avgPathGran * 0.4 + avgSiblingCoh * 0.4 + avgDimensionAlign * 0.2) * 100.0

        log.info("\n==========================================================\n" +
                 "             AUTOMATED TAXONOMY VALIDATOR RESULTS\n" +
                 "==========================================================\n" +
                 "  - Path Granularity:      ${"%.1f%%".format(java.util.Locale.US, avgPathGran * 100.0)}\n" +
                 "  - Sibling Coherence:     ${"%.1f%%".format(java.util.Locale.US, avgSiblingCoh * 100.0)}\n" +
                 "  - Dimension Alignment:   ${"%.1f%%".format(java.util.Locale.US, avgDimensionAlign * 100.0)}\n" +
                 "  - OVERALL QUALITY SCORE: ${"%.2f/100".format(java.util.Locale.US, overallScore)}\n" +
                 "==========================================================")

        return ValidationSummary(avgPathGran, avgSiblingCoh, avgDimensionAlign, overallScore)
    }

    private fun getAllNodes(node: GraphNode, visited: MutableSet<GraphNode> = mutableSetOf()): Set<GraphNode> {
        if (visited.add(node)) node.children.forEach { getAllNodes(it, visited) }
        return visited
    }
}
