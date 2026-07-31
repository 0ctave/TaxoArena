# Four transferable findings

Status: **current**. These are the results that generalise beyond this system. Each is
stated as a general form followed by the instances that produced it and the measurement
that supports it. They belong together in one thesis section; they are the part of the work
that is useful to someone who will never build a taxonomy.

---

## 1. In a hierarchical vMF model, cross-node comparison must use a shared concentration

**General form.** Per-child normalisers are correct for a density and wrong for a decision.
Comparing `logC_d(kappa_i) + kappa_i <mu_i, x>` across siblings biases assignment toward the
concentrated sibling by tens of nats at d = 256. The bias is *directional*, not noisy, so it
survives averaging and appears as systematic structural distortion rather than as variance.
Use `kappa_bar * <mu_i, x>` — scale-free across the competition set, and since `kappa_bar` is
a positive constant it cannot change the argmax.

**Instance 1 — the trickler's sibling competition.** High-kappa siblings absorbed their
neighbours; four ground-truth domains were killed. Fixed before the current branch.

**Instance 2 — the splitter's routing-sustainability check** (`c381211`). The same
expression survived the redesign that fixed instance 1, in a function whose stated
justification was "the same posterior the trickler uses". Effect at seed 42:
not-routing-sustainable rejections 750 -> 42 (-94%), leaves 84 -> 152, J +20.4%. At matched
granularity, +10.3% J.

**Corollary that cost separately.** Because `kappa` is fitted with an n-dependent shrinkage
`(n-1)/(n+d-2)`, comparing *levels* by density is worse than comparing siblings by density:
parents, fitted on larger n, always look sharper. Measured: 56% of the corpus
mis-residualised at anchors under a density descent gate. This is why the descent gate is a
direction-only Jensen-tight bound rather than a likelihood ratio.

**Search closure.** `grep` over `src/` confirms the only remaining occurrence of the
per-child normaliser is the `VmfParameters` declaration. Both sites are fixed.

Full write-up: `router-shared-kappa-correction.md`.

---

## 2. Calibrate a structural acceptance rule against the paired SE of its own objective

**General form.** When an accept/reject decision thresholds an estimated improvement, the
threshold must be expressed in units of that improvement's *own* standard error, estimated
**paired** across the two states (both sides share a corpus draw). A fixed absolute
tolerance silently means different things at different sites.

**Measurement.** On this corpus `SE(dJ)` spans **13.1x** from p10 to p90. The uncalibrated
rule — lexicographic on `(J, -|V|)` against a float tolerance `tau = 1e-6` — accepted **4 of
52** structural edits at z < 1, the worst at **z = 0.156** (`dJ` 9.4e-06 against `SE(dJ)`
6.0e-05). An edit whose improvement is one sixth of its own measurement error is incoherent
regardless of what it does downstream.

**Implementation.** `TaxonomyOperations.tryProposal` captures the cell assignment in the
genuine base state, captures it again after the tentative edit, and computes
`JBootstrap.pairedDeltaSe`. `acceptanceZ > 0` selects the z-gate; `acceptanceZ = 0` retains
the legacy rule as an attributable baseline arm. Every proposal writes `dJ`, `SE(dJ)`, `z`
and the binding threshold to `proposals.csv`.

**The negative results are part of the finding.** Two empirical corroborations were tested
and both refuted:

* *Stability tightening did not occur.* The gate's effect is an additive **~4.4-leaf**
  offset. `corr(reduction, seed deviation) = +0.006`; variance ratio 1.05 against F(4,4)
  critical 6.39. The CV rise 14.3% -> 15.7% is mechanical from the mean shift and must not
  be reported as degradation.
* *J is not higher.* 2 of 5 seeds, sign test p = 0.812, median `dJ` -0.0001. The apparent
  gain was seed 42 alone, the known outlier.

So the rule is defended on **coherence alone**, and that is the more transferable claim: a
gate can be right because its units are right, without needing to improve the number it
gates.

**A second-order consequence, applied.** The same argument rules out choosing k by
`argmax dJ` over candidate splits: a maximum over several noisy estimates is biased upward
even when all candidates are equivalent, and the winner is disproportionately whichever
one's bootstrap SE happened to land low. The k-fallback therefore selects **lowest-k-first
among candidates that each independently cleared the same gate** — parsimony as a
deterministic tie-break rather than a noisy maximisation.

---

## 3. The threshold-reuse defect class

**General form.** A threshold is derived against a specific *quantity* at a specific
*pipeline stage*. Reusing the same constant for a different quantity, or for the same
quantity at a different stage, is silently wrong: the code compiles, the units look
compatible, and the error only surfaces when something downstream fails for an apparently
unrelated reason.

Three instances in this project:

**(a) `separationEpsilon` across scales.** One constant served split acceptance, EM
k-selection, sibling merging, sibling distinctness, residual-split viability and the global
proposal gate. Because the collapse gate's divergence is kappa-weighted
(`~ kappa (1 - cos theta)`), the same 0.01 meant ~8.1 degrees of angular tolerance at the
kappa ~ 10-50 of freshly split nodes and under **0.7 degrees** at the kappa ~ 150-180 of deep
wrapper nodes. The gate was implicitly calibrated for the first and reused for the second,
which is why it almost never fired and single-child chains persisted. Removing the kappa
term instead — making the gate ~6x looser than the splitter's own distinctness standard —
produced split/collapse chatter and non-convergence.

**(b) `proposalSeparationBar` vs `marginalEps`.** `proposalSeparationBar` is a **LEVEL**
("is this partition separated at all?"). `marginalEps` is a **DIFFERENCE** of separations
("does k+1 buy enough over k?"). One constant served both. Decoupled at `e3c4b2c` into
independent config fields, both inert at their defaults (`marginalEps = -1.0` means "fall
back to `proposalSeparationBar`"). `marginalEps = 0` was measured and **rejected**: 83
leaves, J 0.230247, and it relocates the threshold onto `maxK`, which at 6 was actively
harmful before the k-fallback existed.

**(c) `tau` serving two roles.** `tau = 1e-6` is simultaneously a per-edit acceptance band
(is this `dJ` distinguishable from zero?) and a per-iteration fixed-point tolerance (has the
operator stopped moving?). These are different questions about different quantities at
different stages. The acceptance role has since been taken over by the z-gate, which is the
correct fix for that half; the certificate half still uses `tau` and wants its own
derivation. See `known-defects.md`.

**Detection heuristic.** Grep for every read of a threshold constant and list the *quantity*
each site compares it against. If two sites compare different quantities, or the same
quantity at different scales, the constant is overloaded.

---

## 4. Report a join's overlap before reporting the join's result

**General form.** A join with zero (or near-zero) key overlap produces a clean-looking null
that is indistinguishable from a real one. Any analysis whose conclusion is "no effect" must
first report the count of groups that could have shown an effect. Concretely: report the
**mixed-group count** — the number of join groups containing both classes being compared —
before reporting the rate.

**The instance that cost a wrong decision.** A short-circuit was implemented on the
reasoning that a candidate dying on `not_routing_sustainable` cannot be rescued by a higher
k, supported by a measured "0 of 36 rescues". The join was on `iter`, and
`TaxonomySplitter` recorded `NO_PROPOSAL` rows with a hardcoded `iter = -1` while
`tryProposal` recorded `ACCEPTED`/`REJECTED` with the real iteration. Every `NO_PROPOSAL`
row therefore sat in a single `iter = -1` bucket that **could not contain an ACCEPTED row**:
the numerator was structurally impossible, and 0/36 was visually identical to a real zero.

The run refuted it — 74 leaves, J 0.228088, worse than canonical. Reverted. The corrected
join gives **3 rescues in 404 (1%)**, which agrees with the experiment: a 1% rate on an
event that seeds an entire subtree is exactly when a short-circuit is a bad trade.

**The diagnostic number.** Mixed-group count was **0 of 613** before the fix and **97 of
613** after. That single figure would have caught it at zero cost.

**Five instances of the class in this project**, of which the above is the most expensive.
The others follow the same shape: an id-space mismatch (`mmlu_pro.id` is not the eval
`question_id`; joins must go through text), a censored-reach null that inflates a quantile
and deflates its tail probability (`separation_null_by_size.md`, reach % reported before
every quantile table for exactly this reason), a rubric-leakage check whose overlap was
never reported, and a hold-out experiment that would fail by construction at the reported
`descentMargin` (`incremental-taxonomy.md`).

**Standing rule adopted:** any join returning a null result must report its own mixed-group
count on the same line as the result.

---

## A fifth candidate, recorded but not promoted

`b5313ed`: a `@Volatile` field with **no consumer** — `lastDeclineReason`, left behind after
a reverted experiment — changed the tree. Three builds at the same config and seed:

| build | field | iter fix | nodes | leaves | J | iters |
|---|---|---|---:|---:|---:|---:|
| A | absent | no | 141 | 84 | 0.238987 | 10 |
| B | present | yes | 143 | 85 | 0.239113 | 13 |
| C | absent | yes | 141 | 84 | 0.238987 | 10 |

A and C agree on all four quantities, isolating the field as the only difference between B
and C. There is **no mechanism** for how a volatile write on a sequential path changed the
result, and none is proposed. The field is gone and the effect is gone.

It is recorded because "this change is inert" is exactly the assumption that failed — twice
in one session, the other being the memo fingerprint degenerating on internal nodes. It is
not promoted to a transferable finding because a finding needs a mechanism, and this one has
an observation instead.
