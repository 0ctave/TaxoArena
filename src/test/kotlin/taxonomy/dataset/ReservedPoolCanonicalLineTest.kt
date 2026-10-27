package taxonomy.dataset

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Test
import java.security.MessageDigest

/**
 * The pool id's canonical line (docs/multi_corpus_design.md §3.5): `domain:id` for the bare
 * MMLU_PRO keys every recorded pool was hashed from — so the frozen pool of record keeps its
 * id — and `source|domain:id` for a leaderboard corpus's `<SOURCE>/<domain>` split key.
 */
class ReservedPoolCanonicalLineTest {

    /** The pre-stage-1 formula, verbatim: sha256 over sorted `domain:id` lines, `p` + 16 hex. */
    private fun legacyPoolId(idsByDomain: Map<String, List<Int>>): String {
        val canonical = idsByDomain.entries.flatMap { (d, ids) -> ids.map { "$d:$it" } }.sorted().joinToString("\n")
        val digest = MessageDigest.getInstance("SHA-256").digest(canonical.toByteArray())
        return "p" + digest.take(8).joinToString("") { "%02x".format(it) }
    }

    @Test
    fun `MMLU_PRO pools hash exactly as before`() {
        val pool = mapOf("Philosophy" to listOf(9, 3, 12256), "Computer Science" to listOf(70), "Math" to listOf(5, 4))
        assertEquals(legacyPoolId(pool), ReservedPool.computePoolId(pool))
        assertEquals("Philosophy:9", ReservedPool.canonicalLine("Philosophy", 9))
        assertEquals("Computer Science:70", ReservedPool.canonicalLine("Computer Science", 70))
        // An MMLU_PRO-prefixed key (never produced by the plugin) would still hash as a bare line.
        assertEquals("MMLU_PRO/law:70", ReservedPool.canonicalLine("MMLU_PRO/law", 70))
    }

    @Test
    fun `leaderboard keys hash as source pipe domain colon id`() {
        assertEquals("BBH|boolean_expressions:1000042", ReservedPool.canonicalLine("BBH/boolean_expressions", 1_000_042))
        assertEquals("MATH|Counting & Probability:2000001", ReservedPool.canonicalLine("MATH/Counting & Probability", 2_000_001))
        assertEquals("MMLU_PRO_LB|business:70", ReservedPool.canonicalLine("MMLU_PRO_LB/business", 70))
        val union = mapOf("BBH/navigate" to listOf(1_000_003), "MMLU_PRO_LB/business" to listOf(70))
        val expected = MessageDigest.getInstance("SHA-256")
            .digest(listOf("BBH|navigate:1000003", "MMLU_PRO_LB|business:70").sorted().joinToString("\n").toByteArray())
            .take(8).joinToString("") { "%02x".format(it) }
        assertEquals("p$expected", ReservedPool.computePoolId(union))
        assertNotEquals(legacyPoolId(union), ReservedPool.computePoolId(union))
        // Same ids under a different source are a different pool.
        assertNotEquals(
            ReservedPool.computePoolId(mapOf("BBH/navigate" to listOf(1_000_003))),
            ReservedPool.computePoolId(mapOf("MUSR/navigate" to listOf(1_000_003)))
        )
    }
}
