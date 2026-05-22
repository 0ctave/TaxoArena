package taxonomy

/**
 * Meta-prompts for grounded Agent Judge induction.
 * Optimized for Recursive Batch Processing of MMLU-Pro corpora.
 */
object JudgePrompts {

    /**
     * Phase 1: Induce Partial Guidelines from a batch of Q+Choices+A.
     */
    fun induceBatchGuidelines(corpusItems: List<String>): String {
        val items = corpusItems.joinToString("\n---\n")
        return """
            Task: Induce Domain Adjudication Guidelines from a corpus of expert-verified problems.
            
            [Corpus Batch]
            $items
            
            [Instructions]
            Analyze the logic required to reach the correct answer for each item. 
            Identify the implicit rules, conceptual foundations, and technical nuances that define this knowledge cluster.
            
            [Output Format]
            Provide a list of "Domain Guidelines" with levels of importance (CRITICAL, IMPORTANT, or SUBTLE).
            Focus on the PROCEDURAL LOGIC and VALIDITY of the reasoning, not the specific facts.
            Example: "CRITICAL: Must verify the application of Bayes Theorem in conditional probability chains."
        """.trimIndent()
    }

    /**
     * Phase 2: Synthesize Global Guidelines from Batch Results.
     */
    fun synthesizeGlobalGuidelines(partialGuidelines: List<String>): String {
        val partials = partialGuidelines.joinToString("\n\n")
        return """
            Task: Synthesize a Master Adjudication Policy from multiple batch analyses.
            
            [Partial Batch Guidelines]
            $partials
            
            [Instructions]
            1. Deduplicate: Merge overlapping rules into a single high-level axiom.
            2. Generalize: Ensure the rules represent the entire domain, not just the specific questions seen.
            3. Weight: Determine the final hierarchy of importance for these rules.
            
            [Output Format]
            A structured set of "Master Domain Axioms" categorized by technical dimension.
        """.trimIndent()
    }

    /**
     * Phase 3: Final System Prompt & Rubric Synthesis.
     */
    fun synthesizeFinalJudge(masterGuidelines: String): String {
        return """
            Task: Synthesize a specialized "Managerial" System Prompt for an AI Agent Judge.
            
            [Master Domain Axioms]
            $masterGuidelines
            
            [Instructions]
            Create an expert evaluative persona based on these axioms.
            
            - The judge must PENALIZE verbosity and REWARD precision.
            - The judge must strictly follow a 4-step process: 
               1. Independent Critique of Trace A.
               2. Independent Critique of Trace B.
               3. Comparative Technical Analysis.
               4. Verdict.
            - The judge must NOT reference specific ground-truth answers from the training set, but must use the axioms to detect technical hallucinations.

            [Expected Output Format]
            Return ONLY a JSON object containing the System Prompt and the Rubric:
            {
              "system_prompt": "Persona definition and workflow...",
              "rubric": {
                "criteria": [
                   {"name": "...", "description": "...", "weight": 0.4}
                ],
                "failure_modes": ["List of hallucinations to watch for"]
              }
            }
        """.trimIndent()
    }

    /**
     * Phase 4: Repair Malformed JSON
     */
    fun repairMalformedJson(malformedOutput: String): String {
        return """
            Task: Repair the following malformed JSON output.
            
            The text below contains an AI Agent Judge's System Prompt and Rubric, but it failed to parse as valid JSON.
            Your job is to extract the content and return it as a strictly valid, properly escaped JSON object.
            DO NOT change the underlying meaning or text, just fix the formatting.
            
            [Malformed Output]
            $malformedOutput
            
            [Expected Output Format]
            Return ONLY a JSON object:
            {
              "system_prompt": "The extracted system prompt...",
              "rubric": {
                ... the extracted rubric ...
              }
            }
        """.trimIndent()
    }
}
