package taxonomy.operations

import org.slf4j.LoggerFactory
import org.sqlite.SQLiteConfig
import java.io.File
import java.security.MessageDigest
import java.sql.Connection

/** One cached reference solution: the letter the reference model chose and that option's text. */
data class RecipeReference(val letter: String, val text: String)

/**
 * The STACK-v2 kit: everything the recipe needs beyond the eval rows, frozen into one file at zero
 * calls by `tools/analysis/judge_wiring.py --export-kit` (anchor rubrics from the clean bareq512_s42
 * ladder, the question -> anchor routing, the cached grok-reasoning references). Read-only.
 */
interface RecipeKit {
    /** `meta.kit_hash`: sha256 over the canonical row dump, recomputed and verified on open. */
    val kitHash: String
    /** `meta.recipe`, must equal `StackV2JudgeRecipe.RECIPE_NAME`. */
    val recipe: String
    val meta: Map<String, String>
    fun anchorOf(questionId: Int): String?
    fun referenceOf(questionId: Int): RecipeReference?
    /** (system_prompt, rubric) of an anchor, or null when the ladder has none. */
    fun rubric(anchor: String): Pair<String, String>?
    val questionCount: Int
}

/**
 * A kit held in memory (the loader's result, and what unit tests and the harness build directly).
 * The hash is computed here from the rows, so an in-memory kit and its sqlite form agree.
 */
class InMemoryRecipeKit(
    val anchorRubrics: Map<String, Pair<String, String>>,
    val questionAnchor: Map<Int, Pair<String, String>>,     // qid -> (leaf_id, anchor)
    val references: Map<Int, RecipeReference>,
    metaIn: Map<String, String> = emptyMap()
) : RecipeKit {
    override val kitHash: String = StackV2Kit.canonicalHash(anchorRubrics, questionAnchor, references)
    override val meta: Map<String, String> = LinkedHashMap(metaIn).also {
        it.putIfAbsent("recipe", "STACK-v2")
        it["kit_hash"] = kitHash
    }
    override val recipe: String get() = meta["recipe"] ?: ""
    override fun anchorOf(questionId: Int): String? = questionAnchor[questionId]?.second
    override fun referenceOf(questionId: Int): RecipeReference? = references[questionId]
    override fun rubric(anchor: String): Pair<String, String>? = anchorRubrics[anchor]
    override val questionCount: Int get() = questionAnchor.size
}

/**
 * Read-only loader of the kit sqlite (`meta(key,value)`, `anchor_rubrics(label PK, system_prompt,
 * rubric)`, `question_anchor(question_id PK, leaf_id, anchor)`, `reference(question_id PK, letter,
 * option_text)`). Refuses a kit whose recorded `kit_hash` does not equal the recomputed one, or whose
 * `recipe` is not STACK-v2. The `correct` column of the solve DB is deliberately NOT in the kit.
 */
object StackV2Kit {
    private val log = LoggerFactory.getLogger("taxonomy.StackV2Kit")

    fun open(path: String): RecipeKit {
        val f = File(path)
        require(f.isFile) { "[JUDGE-RECIPE] kit not found: ${f.path} (export it with tools/analysis/judge_wiring.py --export-kit)" }
        val cfg = SQLiteConfig().apply { setReadOnly(true) }
        cfg.createConnection("jdbc:sqlite:${f.path}").use { c -> return load(c, f.path) }
    }

    internal fun load(c: Connection, label: String): RecipeKit {
        val meta = LinkedHashMap<String, String>()
        c.createStatement().use { st ->
            st.executeQuery("SELECT key, value FROM meta ORDER BY key").use { rs -> while (rs.next()) meta[rs.getString(1)] = rs.getString(2) ?: "" }
        }
        val rubrics = LinkedHashMap<String, Pair<String, String>>()
        c.createStatement().use { st ->
            st.executeQuery("SELECT label, system_prompt, rubric FROM anchor_rubrics ORDER BY label").use { rs ->
                while (rs.next()) rubrics[rs.getString(1)] = rs.getString(2) to rs.getString(3)
            }
        }
        val qa = LinkedHashMap<Int, Pair<String, String>>()
        c.createStatement().use { st ->
            st.executeQuery("SELECT question_id, leaf_id, anchor FROM question_anchor ORDER BY question_id").use { rs ->
                while (rs.next()) qa[rs.getInt(1)] = rs.getString(2) to rs.getString(3)
            }
        }
        val refs = LinkedHashMap<Int, RecipeReference>()
        c.createStatement().use { st ->
            st.executeQuery("SELECT question_id, letter, option_text FROM reference ORDER BY question_id").use { rs ->
                while (rs.next()) refs[rs.getInt(1)] = RecipeReference(rs.getString(2), rs.getString(3))
            }
        }
        val recorded = meta["kit_hash"]
        val kit = InMemoryRecipeKit(rubrics, qa, refs, meta)
        check(recorded == kit.kitHash) {
            "[JUDGE-RECIPE] kit $label: recorded kit_hash $recorded != recomputed ${kit.kitHash}; the file was edited or exported by a different canonicalisation"
        }
        check(kit.recipe == "STACK-v2") { "[JUDGE-RECIPE] kit $label: meta.recipe = '${kit.recipe}', expected STACK-v2" }
        log.info("[JUDGE-RECIPE] kit $label verified: hash ${kit.kitHash} | ${rubrics.size} anchor rubrics | ${qa.size} routed questions | ${refs.size} references | reference_model ${meta["reference_model"]}")
        return kit
    }

    /**
     * Canonical row dump, identical in `judge_wiring.py` (`kit_hash`):
     *   R\t<label>\t<json.dumps(system_prompt)>\t<json.dumps(rubric)>   sorted by label (codepoint order)
     *   A\t<qid>\t<leaf_id>\t<anchor>                                    sorted by qid
     *   F\t<qid>\t<letter>\t<json.dumps(option_text)>                    sorted by qid
     * joined with "\n", sha256 over UTF-8. `json.dumps` = PythonJson (ensure_ascii), so the dump is ASCII.
     */
    fun canonicalHash(
        rubrics: Map<String, Pair<String, String>>,
        questionAnchor: Map<Int, Pair<String, String>>,
        references: Map<Int, RecipeReference>
    ): String {
        val sb = StringBuilder()
        var first = true
        fun line(s: String) { if (!first) sb.append('\n'); first = false; sb.append(s) }
        for (label in rubrics.keys.sortedWith(codepointOrder)) {
            val (sp, rb) = rubrics.getValue(label)
            line("R\t$label\t${PythonJson.dumps(sp)}\t${PythonJson.dumps(rb)}")
        }
        for (q in questionAnchor.keys.sorted()) {
            val (leaf, anchor) = questionAnchor.getValue(q)
            line("A\t$q\t$leaf\t$anchor")
        }
        for (q in references.keys.sorted()) {
            val r = references.getValue(q)
            line("F\t$q\t${r.letter}\t${PythonJson.dumps(r.text)}")
        }
        val digest = MessageDigest.getInstance("SHA-256").digest(sb.toString().toByteArray(Charsets.UTF_8))
        return digest.joinToString("") { "%02x".format(it) }
    }

    /** Python's `sorted()` on str compares code points; Kotlin's default String order compares UTF-16 units. */
    private val codepointOrder = Comparator<String> { a, b ->
        val ai = a.codePoints().toArray(); val bi = b.codePoints().toArray()
        var i = 0
        while (i < ai.size && i < bi.size) { if (ai[i] != bi[i]) return@Comparator ai[i].compareTo(bi[i]); i++ }
        ai.size.compareTo(bi.size)
    }
}

/**
 * Lazily opens and caches the configured kit. A Spring bean so `TaxonomyArenaService` can take it by
 * constructor; nothing is opened until the recipe is enabled and a kit is first requested.
 */
interface RecipeKitProvider {
    fun get(): RecipeKit
}

@org.springframework.stereotype.Service
class ConfiguredRecipeKitProvider(private val config: taxonomy.config.TaxonomyConfig) : RecipeKitProvider {
    @Volatile private var cached: RecipeKit? = null
    @Volatile private var cachedPath: String? = null
    override fun get(): RecipeKit {
        val path = config.llm.judgeRecipe.kitPath
        cached?.let { if (cachedPath == path) return it }
        synchronized(this) {
            cached?.let { if (cachedPath == path) return it }
            val kit = StackV2Kit.open(path)
            cached = kit; cachedPath = path
            return kit
        }
    }
}
