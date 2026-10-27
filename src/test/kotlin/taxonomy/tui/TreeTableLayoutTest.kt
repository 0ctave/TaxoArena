package taxonomy.tui

import taxonomy.tui.components.TreeTableLayout
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*

class TreeTableLayoutTest {

    @Test
    fun rowFitsWithinWidthAndShowsQueryCount() {
        val row = TreeTableLayout.rowText(
            treeText = "\u251c\u2500\u2500 Biology",
            recursiveQueryCount = 24,
            hasJudge = true,
            selected = false,
            pWidth = 60,
        )
        assertTrue(row.length <= 59, "row exceeds width: '${row}'")
        assertTrue(row.contains("24"), "missing query count: '$row'")
        assertTrue(row.endsWith("\u2714"), "judged node should end with check: '$row'")
    }

    @Test
    fun unjudgedNodeEndsWithOpenCircle() {
        val row = TreeTableLayout.rowText("Leaf", 3, hasJudge = false, selected = false, pWidth = 50)
        assertTrue(row.endsWith("\u25cb"), "unjudged node should end with circle: '$row'")
    }

    @Test
    fun selectedRowHasCaret() {
        val row = TreeTableLayout.rowText("Node", 1, hasJudge = false, selected = true, pWidth = 50)
        assertTrue(row.startsWith("\u276f"), "selected row should start with caret: '$row'")
    }

    @Test
    fun longLabelIsTruncatedNotOverflowing() {
        val long = "A".repeat(200)
        val row = TreeTableLayout.rowText(long, 9999, hasJudge = false, selected = false, pWidth = 40)
        assertTrue(row.length <= 39, "narrow row must stay within width: ${row.length}")
    }

    @Test
    fun headerAlignsWithQueryColumn() {
        val header = TreeTableLayout.headerText(80)
        assertTrue(header.contains("Queries"))
        assertTrue(header.length <= 79)
    }

    @Test
    fun treeWidthNeverGoesBelowFloor() {
        assertEquals(10, TreeTableLayout.treeWidth(5))
        assertTrue(TreeTableLayout.treeWidth(120) > 10)
    }
}
