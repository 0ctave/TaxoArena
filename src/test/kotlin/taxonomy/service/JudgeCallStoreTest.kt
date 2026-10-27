package taxonomy.service

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import java.io.File
import java.sql.DriverManager

/**
 * `judge_calls` is created lazily on the first insert and NEVER by the ratings DB's init DDL: a ratings
 * database initialised by `TaxonomyRankingService` has no such table until `recordJudgeCalls` writes.
 */
class JudgeCallStoreTest {

    private fun row(order: Int) = JudgeCallRecord(
        presentationOrder = order, judgeModel = "grok-4-1-fast-non-reasoning", recipe = "STACK-v2", kitHash = "k".repeat(64),
        deploymentFingerprint = "f".repeat(16), promptSha256 = "p".repeat(64), payloadSha256 = "s".repeat(64),
        maxTokens = 8192, temperatureLabel = "omitted", finishReason = "stop", completionTokens = 77, promptTokens = null,
        providerResponseId = "rid-$order", providerModel = "grok", httpStatus = 200, attempts = 1, latencyMs = 9,
        rawContent = "{\"winner\":\"Model A\"}—", parsedWinner = "Model A", confidence = 0.8,
        anchor = "Physics", refLetter = "B", evalQuestionId = 7, modelA = "alpha", modelB = "beta", nodeId = "leaf-7"
    )

    @Test
    fun `creates the table lazily and reads rows back`(@TempDir tmp: File) {
        val db = File(tmp, "calls.db")
        DriverManager.getConnection("jdbc:sqlite:${db.absolutePath}").use { c ->
            assertFalse(JudgeCallStore.hasTable(c))
            assertTrue(JudgeCallStore.readAll(c, "snap").isEmpty())
            JudgeCallStore.insert(c, "snap", listOf(row(1), row(2)))
            assertTrue(JudgeCallStore.hasTable(c))
            val back = JudgeCallStore.readAll(c, "snap")
            assertEquals(2, back.size)
            assertEquals(row(1), back[0])
            assertEquals(row(2), back[1])
            assertNull(back[0].promptTokens)
            assertTrue(JudgeCallStore.readAll(c, "other").isEmpty())
        }
    }

    @Test
    fun `a ratings db initialised by the ranking service has no judge_calls table until the first record`() {
        val key = "ranking.db.path"
        val previous = System.getProperty(key)
        // A plain temp dir (as RankingServiceTest): the service keeps its connection open, so @TempDir's cleanup would fail on Windows.
        val tmp = taxonomy.TestTmp.dir("judge-call-store-test")
        val db = File(tmp, "ratings.db")
        try {
            System.setProperty(key, db.absolutePath)
            val svc = TaxonomyRankingService()
            DriverManager.getConnection("jdbc:sqlite:${db.absolutePath}").use { c ->
                assertFalse(JudgeCallStore.hasTable(c), "the init DDL must not create judge_calls")
                val tables = c.createStatement().executeQuery("SELECT name FROM sqlite_master WHERE type='table'").use { rs ->
                    generateSequence { if (rs.next()) rs.getString(1) else null }.toList()
                }
                assertTrue("match_history" in tables)
            }
            svc.recordJudgeCalls("snap", emptyList())
            DriverManager.getConnection("jdbc:sqlite:${db.absolutePath}").use { c -> assertFalse(JudgeCallStore.hasTable(c), "an empty list writes nothing") }
            svc.recordJudgeCalls("snap", listOf(row(1)))
            DriverManager.getConnection("jdbc:sqlite:${db.absolutePath}").use { c ->
                assertTrue(JudgeCallStore.hasTable(c))
                assertEquals(1, JudgeCallStore.readAll(c, "snap").size)
            }
        } finally {
            if (previous == null) System.clearProperty(key) else System.setProperty(key, previous)
        }
    }
}
