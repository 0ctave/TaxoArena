package taxonomy.tui.features.analysis

import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*
import taxonomy.model.GraphNode
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Green

class MetricsOrInspectorPanelTest {

    @Test
    fun testBuildNodeDetailLinesWithJudgePromptAndRubric() {
        val node = GraphNode(
            label = "Test Node",
            depth = 1,
            judgePrompt = "System Prompt Line 1\nSystem Prompt Line 2",
            judgeRubric = "Rubric Line 1\nRubric Line 2"
        )

        val lines = buildNodeDetailLines(node, width = 80, isGeneratingJudge = false)

        // Find the index of "Judge System Prompt:"
        val promptHeaderIndex = lines.indexOfFirst { it.first == "Judge System Prompt:" }
        assertTrue(promptHeaderIndex != -1, "Should contain Judge System Prompt header")
        assertEquals(Cyan, lines[promptHeaderIndex].second)
        assertTrue(lines[promptHeaderIndex].third) // bold = true

        // Verify the prompt lines
        assertEquals("  System Prompt Line 1", lines[promptHeaderIndex + 1].first)
        assertEquals(White, lines[promptHeaderIndex + 1].second)
        assertFalse(lines[promptHeaderIndex + 1].third)

        assertEquals("  System Prompt Line 2", lines[promptHeaderIndex + 2].first)
        assertEquals(White, lines[promptHeaderIndex + 2].second)
        assertFalse(lines[promptHeaderIndex + 2].third)

        // Find the index of "Judge Rubric:"
        val rubricHeaderIndex = lines.indexOfFirst { it.first == "Judge Rubric:" }
        assertTrue(rubricHeaderIndex != -1, "Should contain Judge Rubric header")
        assertEquals(Cyan, lines[rubricHeaderIndex].second)
        assertTrue(lines[rubricHeaderIndex].third) // bold = true

        // Verify the rubric lines
        assertEquals("  Rubric Line 1", lines[rubricHeaderIndex + 1].first)
        assertEquals(White, lines[rubricHeaderIndex + 1].second)
        assertFalse(lines[rubricHeaderIndex + 1].third)

        assertEquals("  Rubric Line 2", lines[rubricHeaderIndex + 2].first)
        assertEquals(White, lines[rubricHeaderIndex + 2].second)
        assertFalse(lines[rubricHeaderIndex + 2].third)
    }

    @Test
    fun testBuildNodeDetailLinesWithJudgePromptOnly() {
        val node = GraphNode(
            label = "Test Node",
            depth = 1,
            judgePrompt = "System Prompt Only",
            judgeRubric = null
        )

        val lines = buildNodeDetailLines(node, width = 80, isGeneratingJudge = false)

        val promptHeaderIndex = lines.indexOfFirst { it.first == "Judge System Prompt:" }
        assertTrue(promptHeaderIndex != -1, "Should contain Judge System Prompt header")
        assertEquals("  System Prompt Only", lines[promptHeaderIndex + 1].first)

        val rubricHeaderIndex = lines.indexOfFirst { it.first == "Judge Rubric:" }
        assertEquals(-1, rubricHeaderIndex, "Should not contain Judge Rubric header")
    }

    @Test
    fun testBuildNodeDetailLinesWithoutJudge() {
        val node = GraphNode(
            label = "Test Node",
            depth = 1,
            judgePrompt = null,
            judgeRubric = null
        )

        val lines = buildNodeDetailLines(node, width = 80, isGeneratingJudge = false)

        val promptHeaderIndex = lines.indexOfFirst { it.first == "Judge System Prompt:" }
        assertEquals(-1, promptHeaderIndex, "Should not contain Judge System Prompt header")
    }

    @Test
    fun testBuildNodeDetailLinesWithWordWrappingAndTruncation() {
        val longPrompt = "This is a very long judge system prompt that will definitely exceed the wrap limit of width minus six when using a narrow layout width"
        val node = GraphNode(
            label = "Test Node Label That Is Exceedingly Long and Will Exceed Width Safeguard",
            depth = 1,
            judgePrompt = longPrompt,
            judgeRubric = "Simple rubric"
        )

        // Using a width of 40.
        // width - 6 = 34. The wrapping limit is 34.
        // width - 2 = 38. The truncation limit is 38.
        val lines = buildNodeDetailLines(node, width = 40, isGeneratingJudge = false)

        // The first line is the label. Since the label is "Test Node Label That Is Exceedingly Long and Will Exceed Width Safeguard" (78 chars),
        // and width - 2 is 38, it should be truncated to 38 characters.
        val expectedLabel = "Test Node Label That Is Exceedingly Lo"
        assertEquals(38, expectedLabel.length)
        assertEquals(expectedLabel, lines[0].first)

        // Find the index of "Judge System Prompt:"
        val promptHeaderIndex = lines.indexOfFirst { it.first == "Judge System Prompt:" }
        assertTrue(promptHeaderIndex != -1)

        // Check that prompt lines are wrapped and truncated if they exceed 38 characters.
        // Each wrapped line will be prefixed with "  ", so it's at most 2 + (width - 6) = 36 chars, which is <= 38.
        // Let's verify that none of the lines following the prompt header exceed 38 characters.
        var idx = promptHeaderIndex + 1
        while (idx < lines.size && lines[idx].first != "" && !lines[idx].first.startsWith("Judge Rubric:")) {
            val lineText = lines[idx].first
            assertTrue(lineText.length <= 38, "Line '$lineText' length ${lineText.length} exceeds 38")
            assertTrue(lineText.startsWith("  "), "Wrapped line should start with 2 spaces")
            idx++
        }
    }

    @Test
    fun testBuildNodeDetailLinesSampleQueriesWrapping() {
        // Let's add sample queries to a node
        val node = GraphNode(
            label = "Node with queries",
            depth = 1
        )
        // Add a query
        node.queries.add(taxonomy.model.Embedding(
            rawText = "Write a comprehensive Python script to perform binary search on an array of integers",
            distilledText = "",
            values = floatArrayOf()
        ))

        // width = 30. width - 6 = 24.
        // width - 2 = 28 (truncation limit).
        val lines = buildNodeDetailLines(node, width = 30, isGeneratingJudge = false)

        // Find "Sample queries:"
        val queryHeaderIndex = lines.indexOfFirst { it.first == "Sample queries:" }
        assertTrue(queryHeaderIndex != -1)

        // The query lines should start with "  · " for the first line and "    " for subsequent lines.
        // Verify lengths of query lines are <= 28
        var idx = queryHeaderIndex + 1
        var lineCount = 0
        while (idx < lines.size && lines[idx].first != "") {
            val lineText = lines[idx].first
            assertTrue(lineText.length <= 28, "Line '$lineText' length ${lineText.length} exceeds 28")
            if (lineCount == 0) {
                assertTrue(lineText.startsWith("  · "), "First wrapped query line should start with '  · '")
            } else {
                assertTrue(lineText.startsWith("    "), "Subsequent wrapped query lines should start with '    '")
            }
            lineCount++
            idx++
        }
        assertTrue(lineCount > 1, "Should have wrapped query into multiple lines")
    }
}

