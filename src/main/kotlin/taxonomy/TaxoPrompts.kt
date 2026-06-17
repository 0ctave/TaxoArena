package taxonomy

/**
 * Encapsulates refined, fault-resilient prompts for the Taxonomy Engine.
 * Designed to ensure semantic coherence and prevent naming collisions.
 */
object TaxoPrompts {

    private const val JSON_STRICT = "IMPORTANT: Return ONLY raw JSON. No markdown. Output must start with { and end with }."

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
        depth: Int
    ): String {
        val siblings = if (siblingLabels.isEmpty()) "None" else siblingLabels.joinToString(", ")
        val samples = querySamples.joinToString("\n") { "- $it" }
        val lineage = if (branchHistory.isEmpty()) "Root" else branchHistory.joinToString(" > ")
        val anchors = if (domainAnchors.isEmpty()) "Unknown" else domainAnchors.joinToString(", ")

        return """
            Task: Synthesize a highly precise, professional taxonomic concept label for a newly identified semantic cluster.
            
            [Taxonomic Context & Domain Grounding]
            The underlying domain is grounded in the following expert-annotated category/subject distributions for these specific queries:
            - Ground Truth Domain Anchors: $anchors
            
            [Lineage Hierarchy Context]
            - Path Lineage: $lineage
            - Parent Domain (Broad Context): $parentLabel
            - Sibling Domains (Contrastive Context): $siblings
            
            [Representative Query Samples from the Cluster]
            Analyse these specific, representative queries carefully to identify their common denominator:
            $samples
            
            [Rigorous Semantic Synthesis Strategy]
            1. Comparative Query Analysis: Examine all query samples. Identify the common denominator—the specific underlying topic, mechanism, task, or concept that links all of them.
            2. Lineage Integration: Ground the label in the parent domain ($parentLabel) and domain anchors ($anchors). The label must be a logical sub-partition (narrower refinement) of the parent domain, reflecting the specific query identity.
            3. Distinctness & Contrast: Compare against sibling domains ($siblings). Ensure the generated label does not overlap semantically with siblings to prevent taxonomical redundancy.
            4. Sibling Granularity Matching (Depth $depth): The generated dynamic concept label MUST match the exact level of specificity, technical complexity, and conceptual abstraction represented by its siblings: $siblings. If siblings are highly specialized, avoid generic, high-level terms (e.g. do not name a node "Business Math" if siblings are "Pricing Models" or "Draft Discounting").
            5. Constraints:
               - The label must be a clear, technical, concise noun phrase (1-4 words).
               - Avoid generic words like "General", "Other", "Miscellaneous", "Synthesized", "Theory", or repeating the parent label '$parentLabel'.
               - Format: Use simple spaces to separate words. Do NOT use underscores, dashes, or special characters. If linking two terms, use "and" (e.g. "Microeconomics and Policy").
               
            [Expected Output Format]
            Provide the result as a strictly formatted JSON object.
            
            $JSON_STRICT
            { 
              "label": "Precise Dynamic Concept Name", 
              "description": "A precise 1-sentence description detailing the common thematic denominator and specific task/subject of this cluster.",
              "confidence": 0.95 
            }
        """.trimIndent()
    }
}