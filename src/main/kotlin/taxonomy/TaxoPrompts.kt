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
        branchHistory: List<String> = emptyList()
    ): String {
        val siblings = if (siblingLabels.isEmpty()) "None" else siblingLabels.joinToString(", ")
        val samples = querySamples.joinToString("\n") { "- $it" }
        val lineage = if (branchHistory.isEmpty()) "Root" else branchHistory.joinToString(" > ")

        return """
            Task: Synthesize a professional taxonomic label for a newly identified semantic cluster.
            
            [Contextual Framework]
            The underlying dataset consists of complex multiple-choice questions (MMLU Pro). 
            Clusters may form based on:
            1. Subject Matter (e.g., "Organic Chemistry", "Macroeconomics")
            2. Cognitive Task/Methodology (e.g., "Quantitative Problem Solving", "Diagnostic Reasoning")
            3. Conceptual Overlap (e.g., "Regulatory Compliance", "Thermodynamic Systems")
            
            [Lineage Context]
            - Path: $lineage
            - Parent Domain: $parentLabel
            - Sibling Clusters: $siblings
            
            [Representative Query Samples from Cluster]
            $samples
            
            [Taxonomic Naming Strategy]
            1. Identify the "Common Denominator": Look for the thematic thread or shared methodology that connects these specific queries.
            2. Constraint: Use a clear, concise noun phrase (1-4 words).
            3. Distinctness: The label must uniquely identify the "identity" of this group relative to its siblings.
            4. Negative Constraints: Do NOT use "General", "Other", "Miscellaneous", or repeat '$parentLabel'.
            5. Depth Awareness: The label must be a more specific refinement or a logical sub-partition of '$parentLabel'.
            6. Tone: Professional, technical, or industry-standard.
            7. Format: Always separate the words of the label with a blank space NOT "_" or "-", if the label contain two concepts use "and" to separate them.
            
            [Expected Output Format]
            Provide the result as a strictly formatted JSON object.
            
            $JSON_STRICT
            { 
              "label": "Precise Cluster Label", 
              "description": "A 1-sentence explanation of why these items were grouped together (subject, task, or concept).",
              "confidence": 0.95 
            }
        """.trimIndent()
    }
}