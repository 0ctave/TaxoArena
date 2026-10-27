package taxonomy.dataset

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import java.io.File
import java.nio.file.Files
import java.sql.DriverManager

/**
 * Bit-identity of the read cut-over (FRAMEWORK item 18): every former `is_reserved = 1`
 * predicate is now a semijoin on `reserved_pool` by pool id. On a fixture that still carries the
 * legacy column, mirrored from pool A exactly as the old activation did, every read by pool id A
 * must return exactly what the legacy flag predicate returns; pool B, coexisting, must answer
 * disjointly; a pool absent from the table yields an empty matrix and a thrown [JUDGE-LEAK].
 * The only test that mentions the legacy column by name (allowlisted in NoIsReservedInSourceTest).
 */
class ModelEvalStorePoolQueryTest {

    private lateinit var tmp: File
    private lateinit var store: ModelEvalStore
    private lateinit var dbPath: String
    private val models = listOf("m1", "m2", "m3")
    private val poolA = mapOf("math" to listOf(1, 2, 3), "physics" to listOf(11, 12))
    private val poolB = mapOf("math" to listOf(4, 5))
    private lateinit var idA: String
    private lateinit var idB: String

    @BeforeEach
    fun setUp() {
        tmp = Files.createTempDirectory("store-pool-query").toFile()
        dbPath = File(tmp, "legacy.db").absolutePath
        // A legacy database: eval_results WITH the old flag column, mmlu_pro + link tables.
        DriverManager.getConnection("jdbc:sqlite:$dbPath").use { c ->
            c.createStatement().use { s ->
                s.execute(
                    """
                    CREATE TABLE eval_results (
                        question_id INTEGER NOT NULL, model_name TEXT NOT NULL, category TEXT NOT NULL,
                        question_text TEXT NOT NULL, options_json TEXT NOT NULL, gt_answer TEXT NOT NULL,
                        pred TEXT, model_output TEXT NOT NULL, is_correct INTEGER NOT NULL DEFAULT 0,
                        is_reserved INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (question_id, model_name))
                    """.trimIndent()
                )
                s.execute("CREATE TABLE mmlu_pro (id INTEGER PRIMARY KEY, question TEXT, category TEXT, cot_content TEXT, options TEXT, answer TEXT)")
                s.execute("CREATE TABLE eval_question_link (question_id INTEGER PRIMARY KEY, mmlu_pro_row_id INTEGER, question_text TEXT NOT NULL, has_embedding INTEGER NOT NULL DEFAULT 0)")
                for (q in listOf(1, 2, 3, 4, 5, 6, 11, 12, 13)) {
                    val cat = if (q > 10) "physics" else "math"
                    s.execute("INSERT INTO mmlu_pro VALUES ($q, 'question $q', '$cat', '', '[\"a\",\"b\"]', 'A')")
                    s.execute("INSERT INTO eval_question_link VALUES ($q, $q, 'question $q', 1)")
                    for ((i, m) in models.withIndex()) {
                        if (q == 6 && m == "m3") continue   // one question below quorum for m3
                        val correct = if ((q + i) % 2 == 0) 1 else 0
                        s.execute("INSERT INTO eval_results VALUES ($q, '$m', '$cat', 'question $q', '[\"a\",\"b\"]', 'A', 'A', 'trace', $correct, 0)")
                    }
                }
            }
        }
        store = ModelEvalStore(dbPath = dbPath)
        idA = store.recordReservedPool(poolA)
        idB = store.recordReservedPool(poolB)
        // Mirror pool A onto the legacy flag exactly as the old activation did.
        DriverManager.getConnection("jdbc:sqlite:$dbPath").use { c ->
            c.createStatement().use { s ->
                s.executeUpdate("UPDATE eval_results SET is_reserved = 1 WHERE question_id IN (SELECT question_id FROM reserved_pool WHERE pool_id = '$idA')")
            }
        }
    }

    @AfterEach
    fun tearDown() { tmp.deleteRecursively() }

    private fun legacy(sql: String): List<String> {
        val out = ArrayList<String>()
        DriverManager.getConnection("jdbc:sqlite:$dbPath").use { c ->
            c.createStatement().use { s -> s.executeQuery(sql).use { rs ->
                val n = rs.metaData.columnCount
                while (rs.next()) out.add((1..n).joinToString("|") { rs.getString(it) ?: "" })
            } }
        }
        return out.sorted()
    }

    @Test
    fun `getResultsForModel by pool id equals the legacy flag predicate`() {
        for (m in models) {
            val byPool = store.getResultsForModel(m, idA).map { "${it.questionId}|${it.modelName}|${if (it.isCorrect) 1 else 0}" }.sorted()
            val flag = legacy("SELECT question_id, model_name, is_correct FROM eval_results WHERE model_name = '$m' AND is_reserved = 1")
            assertEquals(flag, byPool, m)
            assertTrue(byPool.isNotEmpty())
        }
        val all = store.getResultsForModel("m1", null).size
        assertEquals(9, all, "no pool = every row")
    }

    @Test
    fun `getResultsMatrix by pool id equals the legacy flag predicate, and pools are disjoint`() {
        val byPool = store.getResultsMatrix(models, null, idA).keys.sorted()
        val flag = legacy("SELECT DISTINCT question_id FROM eval_results WHERE is_reserved = 1").map { it.toInt() }.sorted()
        assertEquals(flag, byPool)
        assertEquals(listOf(1, 2, 3, 11, 12), byPool)
        val b = store.getResultsMatrix(models, null, idB).keys.sorted()
        assertEquals(listOf(4, 5), b)
        assertTrue((byPool intersect b.toSet()).isEmpty())
        assertEquals(emptyMap<Int, Any>(), store.getResultsMatrix(models, null, "pdeadbeefdeadbeef"))
        // Category filter composes with the pool.
        assertEquals(listOf(11, 12), store.getResultsMatrix(models, "physics", idA).keys.sorted())
    }

    @Test
    fun `limited draws are ordered by question id`() {
        assertEquals(listOf(1, 2), store.getResultsMatrix(models, null, idA, limit = 2).keys.sorted())
        assertEquals(listOf(1, 2, 3), store.getResultsMatrix(models, null, idA, limit = 3).keys.toList())
        assertEquals(listOf(4), store.getResultsMatrix(models, null, idB, limit = 1).keys.toList())
    }

    @Test
    fun `accuracies, linked ids and ingestion health by pool id equal the legacy flag`() {
        val acc = store.getModelAccuracies(models, null, idA)
        for (m in models) {
            val (total, correct) = legacy("SELECT COUNT(*), SUM(is_correct) FROM eval_results WHERE model_name = '$m' AND is_reserved = 1")
                .single().split("|").map { it.toInt() }
            assertEquals(correct.toDouble() / total, acc.getValue(m), 1e-12, m)
        }
        val linked = store.getLinkedReservedQuestionIds(models, idA).sorted()
        assertEquals(listOf(1, 2, 3, 11, 12), linked)
        assertEquals(listOf(4, 5), store.getLinkedReservedQuestionIds(models, idB).sorted())
        val health = store.verifyIngestion(models, idA)
        for (h in health) {
            val flag = legacy("SELECT COUNT(*) FROM eval_results WHERE model_name = '${h.modelName}' AND is_reserved = 1").single().toInt()
            assertEquals(flag, h.reservedRows, h.modelName)
            val flagMath = legacy("SELECT COUNT(*) FROM eval_results WHERE model_name = '${h.modelName}' AND category = 'math' AND is_reserved = 1").single().toInt()
            assertEquals(flagMath, h.reservedMathRows, h.modelName)
        }
        assertTrue(store.verifyIngestion(models, null).all { it.reservedRows == 0 })
    }

    @Test
    fun `reserved texts resolve by pool id and fail closed for an unknown pool`() {
        assertEquals(setOf("question 1", "question 2", "question 3", "question 11", "question 12"), store.getReservedQuestionTexts(idA))
        assertEquals(setOf("question 4", "question 5"), store.getReservedQuestionTexts(idB))
        val e = assertThrows(IllegalStateException::class.java) { store.getReservedQuestionTexts("pdeadbeefdeadbeef") }
        assertTrue(e.message!!.contains("[JUDGE-LEAK]"), e.message)
    }

    @Test
    fun `the store never writes the legacy column`() {
        val before = legacy("SELECT question_id, model_name, is_reserved FROM eval_results")
        store.recordReservedPool(mapOf("math" to listOf(6)))
        store.getResultsMatrix(models, null, idB)
        store.saveBatch(listOf(ModelEvalResult(99, "m1", "math", "question 99", listOf("a"), "A", "A", "t", true)))
        val after = legacy("SELECT question_id, model_name, is_reserved FROM eval_results")
        assertEquals((before + "99|m1|0").sorted(), after, "new rows land at the column DEFAULT; nothing else moves")
    }
}
