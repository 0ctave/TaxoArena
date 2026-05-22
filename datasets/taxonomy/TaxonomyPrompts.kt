package org.eclipse.lmos.arc.app.taxonomy

/**
 * Encapsulates refined, fault-resilient prompts for the Taxonomy Engine.
 * Designed to ensure semantic coherence, generalization, and prevent naming collisions.
 */
object TaxonomyPrompts {

    private const val JSON_STRICT = "IMPORTANT: Return ONLY raw JSON. No markdown. Output must start with { and end with }."

    /**
     * Refined prompt for labeling discovered geometric clusters (Sub-domains).
     */
    fun clusterLabeling(
        clusterSamples: List<String>,
        parentLabel: String,
        siblingLabels: List<String>
    ): String {
        val siblings = if (siblingLabels.isEmpty()) "None (This is the first sub-domain)" else siblingLabels.joinToString(", ")
        val samples = clusterSamples.joinToString("\n") { "- $it" }

        return """
            Task: Assign a professional and precise capability label to a newly discovered knowledge cluster.
            
            [Context]
            - Parent Domain: $parentLabel
            - Existing Sibling Domains: $siblings
            
            [Representative Samples from Cluster]
            $samples
            
            [Naming Strategy]
            1. Identify the "Least Common Denominator": What specific expertise or capability do these samples share that makes them a distinct subset of '$parentLabel'?
            2. Constraint: The label must be a concise noun phrase (2-4 words).
            3. Distinctness: Ensure the label is semantically distinct from the Parent and all Siblings listed above.
            4. Tone: Use academic, technical, or industry-standard terminology.
            5. Forbidden: Do not use generic words like "General", "Misc", "Miscellaneous", "Other", or "Advanced".
            6. Style: Use Title Case.
            
            [Output Requirement]
            Provide a short, dictionary-style definition (1 sentence) that explains the scope of this sub-domain.
            
            $JSON_STRICT
            { 
              "label": "Specific Category Name", 
              "description": "A precise definition of this capability's scope within the parent domain." 
            }
        """.trimIndent()
    }

    /**
     * Refined prompt for synthesizing high-level umbrellas (Super-Domains).
     */
    fun superDomainSynthesis(subjects: List<String>): String {
        val subjectList = subjects.joinToString(", ")

        return """
            Task: Synthesize a single overarching academic or professional discipline that encompasses ALL the provided subjects.
            
            [Subjects to Encompass]
            $subjectList
            
            [Logic: Least Common Ancestor (LCA)]
            Find the tightest possible umbrella term that logically groups these specific subjects.
            - If subjects are (Algebra, Geometry, Calculus) -> "Mathematics"
            - If subjects are (Microeconomics, Macroeconomics, Econometrics) -> "Economic Sciences"
            - If subjects are (Anatomy, Virology, Clinical Knowledge) -> "Medical Sciences"
            - ONLY if subjects are fundamentally orthogonal (e.g. Poetry and Physics) -> "Interdisciplinary Studies"
            
            [Constraints]
            1. Specificity: Prefer established scientific or professional field names over generic labels.
            2. Brevity: Use 1-3 words maximum.
            3. Collaboration: Ensure the label is descriptive enough to represent the collective center of gravity.
            4. Style: Use Title Case.
            
            [Output Requirement]
            Provide a high-level definition of this collective field.
            
            $JSON_STRICT
            { 
              "label": "Umbrella Discipline Name", 
              "description": "Definition of this synthesized field as a collective area of expertise." 
            }
        """.trimIndent()
    }

    /**
     * Regenerates a domain's label after it has been reparented.
     */
    fun domainRelabeling(oldLabel: String, newParentLabel: String, samples: List<String>): String {
        val sampleList = samples.joinToString("\n") { "- $it" }
        return """
            Task: Rename a domain because it has been moved under a new parent.
            
            [Context]
            - Current Domain Name: "$oldLabel"
            - NEW Parent Domain: "$newParentLabel"
            
            [Representative Samples]
            $sampleList
            
            [Naming Strategy]
            The domain "$oldLabel" was just structurally placed under "$newParentLabel". 
            Generate a new, refined label for this domain that makes logical sense as a sub-category of "$newParentLabel", while accurately reflecting the samples.
            If the current name already perfectly fits as a sub-category, you may keep it or slightly tweak it.
            Constraint: Noun phrase (1-4 words). Title Case.
            
            $JSON_STRICT
            { 
              "label": "New or Updated Category Name", 
              "description": "A precise definition of this capability." 
            }
        """.trimIndent()
    }
}