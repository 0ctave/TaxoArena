package taxonomy.dataset

object MMLUCategories {
    val SUBJECT_TO_DOMAIN = mapOf(
        "abstract_algebra" to "math", "anatomy" to "biology", "astronomy" to "physics",
        "business_ethics" to "business", "clinical_knowledge" to "health", "college_biology" to "biology",
        "college_chemistry" to "chemistry", "college_computer_science" to "computer science",
        "college_mathematics" to "math", "college_medicine" to "health", "college_physics" to "physics",
        "computer_security" to "computer science", "conceptual_physics" to "physics",
        "econometrics" to "economics", "electrical_engineering" to "engineering",
        "elementary_mathematics" to "math", "formal_logic" to "philosophy", "global_facts" to "other",
        "high_school_biology" to "biology", "high_school_chemistry" to "chemistry",
        "high_school_computer_science" to "computer science", "high_school_european_history" to "history",
        "high_school_geography" to "other", "high_school_government_and_politics" to "law",
        "high_school_macroeconomics" to "economics", "high_school_mathematics" to "math",
        "high_school_microeconomics" to "economics", "high_school_physics" to "physics",
        "high_school_psychology" to "psychology", "high_school_statistics" to "math",
        "high_school_us_history" to "history", "high_school_world_history" to "history",
        "human_aging" to "health", "human_sexuality" to "psychology", "international_law" to "law",
        "jurisprudence" to "law", "logical_fallacies" to "philosophy", "machine_learning" to "computer science",
        "management" to "business", "marketing" to "business", "medical_genetics" to "biology",
        "miscellaneous" to "other", "moral_disputes" to "philosophy", "moral_scenarios" to "philosophy",
        "nutrition" to "health", "philosophy" to "philosophy", "prehistory" to "history",
        "professional_accounting" to "business", "professional_law" to "law",
        "professional_medicine" to "health", "professional_psychology" to "psychology",
        "public_relations" to "business", "security_studies" to "law", "sociology" to "psychology",
        "us_foreign_policy" to "law", "virology" to "biology", "world_religions" to "philosophy"
    )

    fun normaliseCategory(raw: String): String {
        val trimmed = raw.lowercase().trim()
        return SUBJECT_TO_DOMAIN[trimmed] ?: trimmed
    }
}
