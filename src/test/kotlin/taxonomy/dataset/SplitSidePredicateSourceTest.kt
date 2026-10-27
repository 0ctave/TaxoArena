package taxonomy.dataset

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.File

/**
 * Reads SplitSide.kt and tools/analysis/split_side.py as text and asserts that the side
 * predicate's literals are the registered ones in both languages, and that nothing else is used
 * in the predicate: the function is the identity of the split, so its constants must be visible
 * and identical, not derived.
 */
class SplitSidePredicateSourceTest {

    private fun codeOf(path: String): String {
        val src = File(path)
        assertTrue(src.isFile, "$path not found; run from the repo root")
        return src.readText().replace("\r\n", "\n")   // line-ending neutral: a CRLF checkout must not break the source scan
    }

    private val kt by lazy { codeOf("src/main/kotlin/taxonomy/dataset/SplitSide.kt") }
    private val py by lazy { codeOf("tools/analysis/split_side.py") }

    @Test
    fun `both languages declare the same literals`() {
        for ((name, value) in listOf(
            "NORMALISER_VERSION" to "\"norm-v1\"", "KEY_RULE" to "\"ck-v1\"", "SIDE_MODULUS" to "1000",
            "EVAL_UPPER" to "300", "GATE_LOWER" to "300", "GATE_UPPER" to "400",
            "FIELD_SEP" to "\"\\u001f\"", "OPTION_SEP" to "\"\\u001e\""
        )) {
            assertTrue(Regex("$name\\s*=\\s*${Regex.escape(value)}").containsMatchIn(kt), "Kotlin: $name = $value")
            assertTrue(Regex("$name\\s*=\\s*${Regex.escape(value)}").containsMatchIn(py), "Python: $name = $value")
        }
    }

    @Test
    fun `the predicate uses the named constants and no other numeric literal`() {
        // Kotlin: sideOfHash body.
        val ktBody = Regex("fun sideOfHash\\(h: Int\\): Side = when \\{(.*?)\\n    \\}", RegexOption.DOT_MATCHES_ALL).find(kt)!!.groupValues[1]
        assertTrue(ktBody.contains("h < EVAL_UPPER"), ktBody)
        assertTrue(ktBody.contains("GATE_LOWER <= h && h < GATE_UPPER"), ktBody)
        assertTrue(Regex("\\b\\d+\\b").findAll(ktBody).none(), "no numeric literal in the Kotlin predicate: $ktBody")
        // Python: side_of_hash body.
        val pyBody = Regex("def side_of_hash\\(h\\):(.*?)\\n\\n", RegexOption.DOT_MATCHES_ALL).find(py)!!.groupValues[1]
        assertTrue(pyBody.contains("h < EVAL_UPPER"), pyBody)
        assertTrue(pyBody.contains("GATE_LOWER <= h < GATE_UPPER"), pyBody)
        assertTrue(Regex("\\b\\d+\\b").findAll(pyBody).none(), "no numeric literal in the Python predicate: $pyBody")
        // The modulus is applied once, by name, in both hashes.
        assertTrue(kt.contains("BigInteger.valueOf(SIDE_MODULUS.toLong())"))
        assertTrue(py.contains("% SIDE_MODULUS"))
    }

    @Test
    fun `the whitespace class is one literal shared by both languages`() {
        val ktClass = Regex("WHITESPACE_CLASS = \"(.*)\"").find(kt)!!.groupValues[1]
        val pyClass = Regex("WHITESPACE_CLASS = \"(.*)\"").find(py)!!.groupValues[1]
        assertEquals(ktClass, pyClass)
        assertEquals(SplitSide.WHITESPACE_CLASS, ktClass.replace("\\\\", "\\"))
    }
}
