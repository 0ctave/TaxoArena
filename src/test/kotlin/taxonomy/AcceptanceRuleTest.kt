package taxonomy

import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import taxonomy.operations.isProposalAccepted

/**
 * Guards the structural acceptance rule.
 *
 * Before this existed, `tryProposal` — the gate every structural edit passes through — had no
 * test at all, and `acceptanceZ` could be switched from the canonical arm to the z arm by one
 * config key with nothing pinning the behavioural difference.
 */
class AcceptanceRuleTest {

    private val tau = 1e-6

    // ── Canonical arm: lexicographic on (J, -|V|) ────────────────────────────────────

    @Test
    fun `strict J improvement is accepted`() {
        assertTrue(isProposalAccepted(deltaJ = 1e-3, deltaV = 2, tau = tau, zGate = 0.0, seDeltaJ = null))
    }

    @Test
    fun `J-neutral edit that removes nodes is accepted`() {
        // The passthrough-dissolution case: J unchanged, taxonomy strictly smaller.
        assertTrue(isProposalAccepted(deltaJ = 0.0, deltaV = -1, tau = tau, zGate = 0.0, seDeltaJ = null))
    }

    @Test
    fun `J-neutral edit that adds nodes is rejected`() {
        assertFalse(isProposalAccepted(deltaJ = 0.0, deltaV = 2, tau = tau, zGate = 0.0, seDeltaJ = null))
    }

    @Test
    fun `J-neutral edit of equal size is rejected`() {
        // deltaV == 0 is not < 0, so a pure churn edit must not commit.
        assertFalse(isProposalAccepted(deltaJ = 0.0, deltaV = 0, tau = tau, zGate = 0.0, seDeltaJ = null))
    }

    @Test
    fun `J regression is rejected even when it shrinks the taxonomy`() {
        assertFalse(isProposalAccepted(deltaJ = -1e-3, deltaV = -5, tau = tau, zGate = 0.0, seDeltaJ = null))
    }

    @Test
    fun `improvement within tolerance counts as neutral not as gain`() {
        // |deltaJ| <= tau falls to the size test rather than accepting on J.
        assertFalse(isProposalAccepted(deltaJ = tau / 2, deltaV = 1, tau = tau, zGate = 0.0, seDeltaJ = null))
        assertTrue(isProposalAccepted(deltaJ = tau / 2, deltaV = -1, tau = tau, zGate = 0.0, seDeltaJ = null))
    }

    @Test
    fun `canonical arm ignores SE when zGate is zero`() {
        // acceptanceZ = 0 must select the lexicographic arm even though the bootstrap runs
        // under enableProfiling and supplies an SE.
        assertTrue(isProposalAccepted(deltaJ = 1e-5, deltaV = 3, tau = tau, zGate = 0.0, seDeltaJ = 1.0))
    }

    // ── z arm ────────────────────────────────────────────────────────────────────────

    @Test
    fun `z arm rejects an improvement inside the noise band`() {
        // deltaJ = 1e-4 with SE = 1e-4 and z = 2 needs > 2e-4.
        assertFalse(isProposalAccepted(deltaJ = 1e-4, deltaV = 2, tau = tau, zGate = 2.0, seDeltaJ = 1e-4))
    }

    @Test
    fun `z arm accepts an improvement clear of the noise band`() {
        assertTrue(isProposalAccepted(deltaJ = 3e-4, deltaV = 2, tau = tau, zGate = 2.0, seDeltaJ = 1e-4))
    }

    @Test
    fun `z arm keeps the tau floor when SE is vanishingly small`() {
        // With z*SE alone this would accept and the termination bound would collapse:
        // z*SE = 2e-12 but the edit gains only tau/2.
        assertFalse(isProposalAccepted(deltaJ = tau / 2, deltaV = 2, tau = tau, zGate = 2.0, seDeltaJ = 1e-12))
        assertTrue(isProposalAccepted(deltaJ = tau * 2, deltaV = 2, tau = tau, zGate = 2.0, seDeltaJ = 1e-12))
    }

    @Test
    fun `z arm admits a pure structural edit when SE is exactly zero`() {
        // SE == 0 means no query moved, so deltaJ is exactly 0 and z is undefined; the edit
        // must still be able to commit on size or wrapper nodes would accumulate forever.
        assertTrue(isProposalAccepted(deltaJ = 0.0, deltaV = -1, tau = tau, zGate = 2.0, seDeltaJ = 0.0))
        assertFalse(isProposalAccepted(deltaJ = 0.0, deltaV = 1, tau = tau, zGate = 2.0, seDeltaJ = 0.0))
    }

    @Test
    fun `the two arms genuinely differ on a J-neutral simplification`() {
        // This is the documented cost of the z arm and the reason acceptanceZ = 0 is canonical:
        // a simplification that leaves J alone commits under the lexicographic rule but cannot
        // commit under the z rule once SE > 0. If this ever stops holding, the arms have been
        // silently merged and the ablation no longer isolates the gate.
        val args = Triple(0.0, -1, 1e-4)
        assertTrue(
            isProposalAccepted(args.first, args.second, tau, zGate = 0.0, seDeltaJ = args.third),
            "canonical arm accepts a J-neutral shrink"
        )
        assertFalse(
            isProposalAccepted(args.first, args.second, tau, zGate = 2.0, seDeltaJ = args.third),
            "z arm cannot accept it, because deltaJ = 0 never exceeds max(tau, z*SE)"
        )
    }
}
