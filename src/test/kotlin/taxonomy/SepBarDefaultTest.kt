package taxonomy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.config.TaxonomyConfig

/**
 * TOPIC-PARTITION-20NG, registration I5 (docs/judge_v2_program.md L10030-L10390, commit 6aa2a0d): the
 * site-null harness takes -DsepBar (the arm's own proposalSeparationBar) and is BYTE-INERT when the
 * property is absent — [SeparationNullBySizeTest.canonicalConfig] must then build exactly the config it
 * built with the literal 0.025 it hardcoded since P2, so every existing site-null CSV of record
 * reproduces. Runs in the ordinary `test` task (the harness class itself is excluded from it); the
 * property is asserted ABSENT here, so the comparison is against the pre-flag literal, not a value
 * smuggled in from the command line.
 */
class SepBarDefaultTest {

    /** The pre-flag canonicalConfig(mcs) with its literal 0.025, verbatim (SeparationNullBySizeTest.kt L71-90 at HEAD 6aa2a0d). */
    private fun preFlagCanonicalConfig(minClusterSize: Int, dim: Int): TaxonomyConfig =
        TaxonomyConfig().apply {
            formalism.maxDepth = 8
            formalism.minClusterSize = minClusterSize
            formalism.proposalSeparationBar = 0.025
            formalism.embeddingSliceDim = dim
            formalism.splitDropTopPcs = 0
            formalism.splitWhiten = false
            taxonomy.model.EmbeddingSlice.width = dim
            formalism.tau = 1e-6
            formalism.acceptanceZ = 0.0
            formalism.enableRefitGate = false
            formalism.membershipFloor = 0.25
            formalism.routingBeamGamma = 0.2
            formalism.descentMargin = 0.12
            formalism.effectiveSupportFloor = 2.0
            formalism.defaultKappaPrior = 10.0
            formalism.maxLeafAssignments = 5
            formalism.fusionSimilarityThreshold = 0.90
            formalism.enableGtWarmStart = false
            formalism.enableResidualSplitGate = true
            formalism.enableResidualRouting = true
            formalism.enableStableQuestionIds = true
        }

    @Test
    fun `sepBar absent reproduces the hardcoded 0_025 and the whole effective config`() {
        assertNull(System.getProperty("sepBar"), "the test task must not carry -DsepBar; this test asserts the ABSENT path")
        assertNull(System.getProperty("sliceDim"), "the test task must not carry -DsliceDim")
        assertEquals(0.025, SeparationNullBySizeTest.DEFAULT_SEP_BAR, 0.0)
        val harness = SeparationNullBySizeTest()
        for (mcs in listOf(30, 55)) {
            val got = harness.canonicalConfig(mcs)
            val want = preFlagCanonicalConfig(mcs, 256)
            assertEquals(0.025, got.formalism.proposalSeparationBar, 0.0, "bar with the property absent")
            assertEquals(want.toEffectiveConfig(), got.toEffectiveConfig(), "effective config identical to the pre-flag literal build (mcs=$mcs)")
            assertEquals(want.formalism.proposalSeparationBar, got.formalism.proposalSeparationBar, 0.0)
            assertEquals(want.formalism.embeddingSliceDim, got.formalism.embeddingSliceDim)
            assertEquals(want.formalism.splitDropTopPcs, got.formalism.splitDropTopPcs)
            assertEquals(want.formalism.splitWhiten, got.formalism.splitWhiten)
            assertEquals(want.formalism.minClusterSize, got.formalism.minClusterSize)
        }
    }

    @Test
    fun `resolveSepBar - absent or blank is the default, a number parses, garbage is fatal`() {
        assertEquals(0.025, SeparationNullBySizeTest.resolveSepBar(null), 0.0)
        assertEquals(0.025, SeparationNullBySizeTest.resolveSepBar(""), 0.0)
        assertEquals(0.025, SeparationNullBySizeTest.resolveSepBar("   "), 0.0)
        assertEquals(0.0145, SeparationNullBySizeTest.resolveSepBar("0.0145"), 0.0)
        assertEquals(0.0145, SeparationNullBySizeTest.resolveSepBar(" 0.0145 "), 0.0)
        assertEquals(0.025, SeparationNullBySizeTest.resolveSepBar("0.025"), 0.0)
        for (bad in listOf("abc", "0", "-0.01", "NaN", "Infinity", "0.0145x")) {
            val e = assertThrows(IllegalArgumentException::class.java) { SeparationNullBySizeTest.resolveSepBar(bad) }
            assertTrue(e.message!!.contains("[SEPBAR]") && e.message!!.contains(bad), e.message)
        }
    }
}
