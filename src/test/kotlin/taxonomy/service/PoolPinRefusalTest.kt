package taxonomy.service

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.model.PoolPin

/**
 * The [POOL-PIN] decision (FRAMEWORK item 18): a snapshot run must name the pool its snapshot
 * pinned; a tree holding EVAL texts is refused unless its exact count is acknowledged, and then
 * disclosed; the declared `pool` must agree with the resolved one.
 */
class PoolPinRefusalTest {

    private val snap = "20260910_043557_Headless_Run_Auto_ge"
    private val pool = "p2dca21ab5f4ef3ae"

    private fun decide(
        requestPool: String? = pool, snapshotRun: Boolean = true, pinnedPool: String? = pool,
        known: Boolean = true, members: Int = 0, ack: List<String> = emptyList(), declared: String? = null
    ) = PoolPin.decide("MAIN", requestPool, snapshotRun, pinnedPool, known, members, ack, snap, declared)

    @Test
    fun `request pool must equal the snapshot's pinned pool`() {
        val e = assertThrows(IllegalStateException::class.java) { decide(pinnedPool = "p8a29aaaaaaaaaaaa") }
        assertTrue(e.message!!.startsWith("[POOL-PIN] refusing to judge MAIN: snapshot pool=p8a29aaaaaaaaaaaa, request pool=$pool"), e.message)
        assertThrows(IllegalStateException::class.java) { decide(pinnedPool = null) }
        val v = decide()
        assertEquals(pool, v.poolId)
        assertNull(v.disclosure)
    }

    @Test
    fun `37 EVAL members refuse unless acknowledged at exactly 37, then disclose`() {
        val e = assertThrows(IllegalStateException::class.java) { decide(members = 37) }
        assertTrue(e.message!!.contains("holds 37 EVAL texts") && e.message!!.contains("\"$snap:37\""), e.message)
        assertThrows(IllegalStateException::class.java) { decide(members = 37, ack = listOf("$snap:36")) }
        assertThrows(IllegalStateException::class.java) { decide(members = 37, ack = listOf("other_snapshot:37")) }
        val v = decide(members = 37, ack = listOf("other:1", "$snap:37"))
        assertEquals(pool, v.poolId)
        assertEquals("[TRAIN-ONLY] DISCLOSURE: snapshot $snap holds 37 EVAL texts among its tree's members (acknowledged in config)", v.disclosure)
    }

    @Test
    fun `an unknown member count refuses`() {
        val e = assertThrows(IllegalStateException::class.java) { decide(known = false, members = -1) }
        assertTrue(e.message!!.contains("could not be computed"), e.message)
    }

    @Test
    fun `the declared pool must agree, for built and loaded trees alike`() {
        assertThrows(IllegalStateException::class.java) { decide(declared = "paeec37aa28063c75") }
        assertEquals(pool, decide(declared = pool).poolId)
        assertThrows(IllegalStateException::class.java) { decide(snapshotRun = false, pinnedPool = null, declared = "paeec37aa28063c75") }
        assertEquals(pool, decide(snapshotRun = false, pinnedPool = null, known = false, declared = pool).poolId)
    }

    @Test
    fun `an unrestricted request is never pinned`() {
        val v = decide(requestPool = null, pinnedPool = "whatever", known = false, members = 999, declared = "other")
        assertNull(v.poolId)
        assertNull(v.disclosure)
    }

    /**
     * Both judged paths go through the same decision: the headless runner and the TUI gateway call
     * PoolPin.decide with the snapshot manager's EVAL-member count before starting a benchmark. The
     * TUI has no acknowledgement channel, so a loaded snapshot holding EVAL texts is refused there.
     */
    @Test
    fun `the TUI benchmark path decides with PoolPin before startBenchmark, like the headless runner`() {
        for (path in listOf("src/main/kotlin/taxonomy/runner/HeadlessBenchmarkRunner.kt", "src/main/kotlin/taxonomy/tui/service/TuiGatewayImpl.kt")) {
            val src = java.io.File(path).readText()
            val decideAt = src.indexOf("taxonomy.model.PoolPin.decide(")
            assertTrue(decideAt >= 0, "$path does not call PoolPin.decide")
            val runAt = if (path.contains("tui")) src.indexOf("deps.arenaService.startBenchmark(") else src.indexOf("benchmarkService.runBenchmark(request)")
            assertTrue(runAt > decideAt, "$path judges before deciding")
            assertTrue(src.contains("lastLoadedEvalMembersKnown") && src.contains("lastLoadedEvalMembersInTree"), "$path ignores the loaded tree's EVAL-member count")
        }
        val tui = java.io.File("src/main/kotlin/taxonomy/tui/service/TuiGatewayImpl.kt").readText()
        assertTrue(tui.contains("acknowledged = emptyList()"), "the TUI has no acknowledgement channel; it must refuse a contaminated tree")
        assertTrue(tui.contains("snapshotRun = ownPoolId == null"), "a TUI session without its own split is a snapshot run")
    }
}
