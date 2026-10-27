package taxonomy.dataset

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

/** [Imported] (stage 1) next to the unchanged [McLetter], and the registry-cell round trip. */
class ImportedVerifierTest {

    @Test
    fun `imported metrics are never recomputed and render with their target`() {
        val v = Imported("acc_norm")
        assertEquals("IMPORTED:acc_norm", v.name)
        assertNull(v.isCorrect("A", "A", listOf("x", "y")))
        assertNull(v.isCorrect(null, "4.5", null))
        assertEquals("Q: not True is\nChoices: True | False\nTarget: False", v.renderItem("not True is", listOf("True", "False"), "False"))
        assertEquals("Q: Solve\nTarget: 4.5", v.renderItem("Solve", null, "4.5"))
        assertEquals("Q: Solve\nTarget: ", v.renderItem("Solve", emptyList(), null))
        assertEquals(setOf("False"), v.answerNGrams("False", listOf("True", "False")))
        assertEquals(emptySet<String>(), v.answerNGrams("  ", null))
        assertEquals(listOf("True"), v.distractors("False", listOf("True", "False")))
        assertNull(v.candidateSet(listOf("True", "False")), "OPTIONS/RESOLVED do not apply to an imported verifier")
        assertThrows(IllegalArgumentException::class.java) { Imported("") }
    }

    @Test
    fun `parse is the inverse of name`() {
        assertEquals(McLetter, Verifier.parse("MC_LETTER"))
        assertEquals(Imported("exact_match"), Verifier.parse("IMPORTED:exact_match"))
        assertEquals("IMPORTED:prompt_level_strict_acc", Verifier.parse("IMPORTED:prompt_level_strict_acc").name)
        assertThrows(IllegalArgumentException::class.java) { Verifier.parse("IMPORTED:") }
        assertThrows(IllegalArgumentException::class.java) { Verifier.parse("EXACT") }
        assertThrows(IllegalArgumentException::class.java) { Verifier.parse("") }
    }
}
