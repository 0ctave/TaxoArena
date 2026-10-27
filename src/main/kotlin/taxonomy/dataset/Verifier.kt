package taxonomy.dataset

/**
 * How a corpus decides whether a model answer is correct, and how its items are rendered for
 * rubric induction and audited for answer leakage (docs/multi_corpus_design.md §3.3).
 *
 * `is_correct` stays a column in `eval_results`; a Verifier is the per-corpus rule that computes
 * it. Stage 0a ships [McLetter] only — the multiple-choice letter rule MMLU-Pro has always used —
 * and routes the three sites that assumed letters through it. Later stages add exact-match and
 * imported-metric verifiers behind the same interface.
 */
sealed interface Verifier {
    /** Registry key stored in `corpus_registry.verifier` (e.g. `MC_LETTER`). */
    val name: String

    /**
     * Whether [pred] is a correct answer for [target]. `null` means "not decidable here" (an
     * imported metric with no local rule); [McLetter] never returns null.
     */
    fun isCorrect(pred: String?, target: String, options: List<String>?): Boolean?

    /** One corpus item as shown to the rubric-induction prompt (question plus its candidate set). */
    fun renderItem(text: String, options: List<String>?, target: String?): String

    /**
     * The answer-bearing spans of one item for the rubric leakage audit — the strings a rubric
     * must not have memorised. The audit tokenises them itself (`maxSharedNgram`).
     */
    fun answerNGrams(target: String?, options: List<String>?): Set<String>

    /**
     * The incorrect candidates of one item; a span found in one of these is domain vocabulary,
     * not a leaked key. Empty where the corpus has no candidate set.
     */
    fun distractors(target: String?, options: List<String>?): List<String> = emptyList()

    /** The lettered candidate set, or `null` where the judge's OPTIONS/RESOLVED modes do not apply. */
    fun candidateSet(options: List<String>?): List<String>?

    companion object {
        const val IMPORTED_PREFIX = "IMPORTED:"

        /** Inverse of [name]: the verifier a `corpus_registry.verifier` cell denotes. */
        fun parse(name: String): Verifier = when {
            name == McLetter.name -> McLetter
            name.startsWith(IMPORTED_PREFIX) && name.length > IMPORTED_PREFIX.length ->
                Imported(name.removePrefix(IMPORTED_PREFIX))
            else -> throw IllegalArgumentException("unknown verifier '$name' (known: ${McLetter.name}, ${IMPORTED_PREFIX}<metric>)")
        }
    }
}

/**
 * Imported-metric verifier (stage 1): `is_correct` was computed upstream — by the Open LLM
 * Leaderboard harness for [metric] (`acc_norm`, `exact_match`, `prompt_level_strict_acc`) — and
 * is never recomputed here, so [isCorrect] is always `null`. Items render with their target
 * string (and the candidate list where the task has one), the leakage audit treats the target
 * as the answer-bearing span, and the judge's OPTIONS/RESOLVED modes do not apply
 * ([candidateSet] is `null`).
 */
data class Imported(val metric: String) : Verifier {
    init { require(metric.isNotBlank()) { "Imported verifier needs a metric name" } }

    override val name: String = Verifier.IMPORTED_PREFIX + metric

    override fun isCorrect(pred: String?, target: String, options: List<String>?): Boolean? = null

    override fun renderItem(text: String, options: List<String>?, target: String?): String = buildString {
        append("Q: ").append(text)
        options?.takeIf { it.isNotEmpty() }?.let { append("\nChoices: ").append(it.joinToString(" | ")) }
        append("\nTarget: ").append(target ?: "")
    }

    override fun answerNGrams(target: String?, options: List<String>?): Set<String> =
        setOfNotNull(target?.takeIf { it.isNotBlank() })

    override fun distractors(target: String?, options: List<String>?): List<String> =
        (options ?: emptyList()).filter { it != target }

    override fun candidateSet(options: List<String>?): List<String>? = null
}

/**
 * Multiple-choice letter verifier: today's MMLU-Pro behaviour, byte-identical.
 *
 *  * correctness is `pred != null && pred == answer` (ModelEvalLoader ingest, asserted in SQL by
 *    EvalIngestValidator's CORRECTNESS_CONSISTENCY check);
 *  * an item renders as `Q: <text>\nChoices: A) … | B) … ✓ | …` with the tick on the answer letter;
 *  * the leakage audit sees the correct option's text, and the distractors are the other options.
 */
object McLetter : Verifier {
    override val name: String = "MC_LETTER"

    override fun isCorrect(pred: String?, target: String, options: List<String>?): Boolean =
        pred != null && pred == target

    /** Index of the answer letter into the option list; -1 when there is no usable letter. */
    fun answerIndex(target: String?): Int =
        target?.firstOrNull()?.let { it.uppercaseChar() - 'A' } ?: -1

    override fun renderItem(text: String, options: List<String>?, target: String?): String {
        val answerIndex = answerIndex(target)
        val choices = (options ?: emptyList()).mapIndexed { i, opt ->
            val letter = ('A' + i)
            if (i == answerIndex) "$letter) $opt ✓" else "$letter) $opt"
        }.joinToString(" | ")
        return "Q: $text\nChoices: $choices"
    }

    override fun answerNGrams(target: String?, options: List<String>?): Set<String> =
        setOfNotNull(options?.getOrNull(answerIndex(target)))

    override fun distractors(target: String?, options: List<String>?): List<String> {
        val answerIndex = answerIndex(target)
        return (options ?: emptyList()).filterIndexed { i, _ -> i != answerIndex }
    }

    override fun candidateSet(options: List<String>?): List<String>? = options
}
