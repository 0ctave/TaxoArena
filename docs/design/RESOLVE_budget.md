# RESOLVE — the systematic budget

Registered 2026-09-14 (`55fb9bf`), derived by the `fit-systematic-budget` workflow, then **rebuilt independently
from the repo's own construction** before adoption (`tools/analysis/systematic_budget.py`, outcome `be1b0d7`).
The fit reproduces to the digit. Four corrections were made on the rebuild and they are listed first, because
two of them change what this document recommends.

## Corrections applied to the text below

1. **Reference accuracy is key-derived and is excluded from the shipped form.** `rejudge_reference.references()`
   grades the reference against the answer key (`rejudge_reference.py:69,79`). The two-predictor fit is better
   (LOAO deviance 193.55 against 216.94) and is not deployable. Registered criterion (3) forced the
   agreement-only model. The spec below already reaches this conclusion independently.
2. **The honest denominator is 920 edges, not 891, and the raw wrong-call rate is 1.47%, not 1.08%.** The
   key-gap filter is unavailable at deployment and drops edges that are more often wrong. (The spec says 924 /
   61; the four-edge difference is edges with a key gap of exactly zero, which carry no direction to be right
   or wrong about and are excluded here. The called counts, 748 / 11, agree exactly.)
3. **The pooled board carries ONE called inversion, not two.** The spec's second inversion,
   Meta-Llama-3.1-8B vs command-r, has a key gap of **−0.0018** — five questions in 2,811 — and the arena
   AGREES with the key on it (p = 0.0000, stable across three independent bootstrap seeds). The pooled board is
   63 called / 1 wrong, going to 57 / 0.
4. **Because of (3), the recommendation splits.** The spec argues the widener's advantage is on the pooled
   board. With the corrected label the reverse holds:

   | | per-anchor (739 raw calls, 8 wrong) | pooled (63 raw calls, 1 wrong) |
   |---|---|---|
   | budget | 663 called / 3 wrong / −71 correct | 57 / 0 / −5 correct |
   | best gate at matched error | A<0.65: 608 / 3 / −126 | A<0.85: 61 / 0 / **−1** |

   Per anchor the fitted widener **dominates** a hard gate at matched error. Pooled, a one-line gate at
   A < 0.85 **strictly dominates the widener**. **Adopted: the widener for per-anchor edges, a plain agreement
   gate for the pooled board.** Publishing a fitted parameter where a one-line rule does better would be paying
   for sophistication with reader trust.

5. **CORRECTION HISTORY, 2026-09-15.** Correction 5 was rewritten twice on 2026-09-14 and the second rewrite
   DELETED the first (git diff --numstat 875df2c 63e8b5e: 30 added, 18 deleted), against the programme's
   insertion-only rule. The deleted text is restored here verbatim, then the current statement follows, then the
   session review's finding on both.

   > **[DELETED 2026-09-14 23:53 in 63e8b5e; restored 2026-09-15]** AMENDED 2026-09-14 by BUDGET-TRANSFER - the
   > parameter is ROSTER-SPECIFIC and the calibration claim below does not survive off its fitting roster. Applied
   > cold to the 20-model board (2,534 edges, all keyed): SHARED (the 66 pairs it was fitted on) 895 edges / 611
   > budget calls / 0 wrong / 1.03 nominal / 0.0x; CROSS (one model new) 1265 / 825 / 9 / 1.30 / 6.9x; INTERNAL
   > (both new) 374 / 252 / 0 / 0.32 / untestable - the raw certificate makes 0 wrong calls here; ALL x20 2534 /
   > 1688 / 9 / 2.65 / 3.4x. Nothing but membership in the fitting set separates the 0.0x row from the 6.9x row.
   > Refitting b1 on the fully novel INTERNAL subset alone gives -0.5230 - the sign reverses; the +3.2633 obtained
   > on all of x20 is carried by pairs containing fitted models. The registered falsifier fired. What survives:
   > cold on a roster it never saw, the budget still beats a gate (1,688 called / 9 wrong / 219 correct
   > surrendered, against A<0.70 at 1,667 / 11 / 242). So tau is a useful risk-ordering device and a
   > roster-specific one. RESOLVE ships it with parameters refitted per board and must not publish a nominal
   > confidence from it on a roster it was not fitted on. Section 3's claim that it "removes an established
   > miscalibration and replaces it with one that is no longer detectable" holds in-roster only; out of roster
   > the replacement is 6.9x and plainly detectable.

   **[REVIEW 2026-09-15, applying to BOTH the deleted amendment and the rewrite below]** Both were computed on
   the x20 cache alone, which holds ZERO verdicts on the 66 original pairs, so SHARED / CROSS / INTERNAL never
   meant fitted / half-fitted / unfitted and neither the 6.9x "overfitting signature" nor the retraction's "no
   fitted-versus-unfitted gap" describes anything. The retraction's 1.7x used McNemar over all pool questions
   routed to the anchor while the x12 analysis it cites uses the anchor's judged questions (809 vs 826
   established edges); "comparable to and better than the within-roster folds" compared an established-label
   1.7x with all-label 2.3-2.5x (like for like: established LOAO 1.7x, LOMO 1.8x); INTERNAL is not "a constant
   outcome" (26 of 374 edges are wrong-direction; its b1 profile set [-4.0, 2.75] excludes +3.31); and the two
   established CROSS errors are Llama-3.1-70B vs gpt-4o-mini in Law and Philosophy, not the near-identical trio
   the mechanism sentence names. The registration had pre-committed the verdict for exactly this evidence:
   "transfer is UNTESTED rather than demonstrated, and the shipped parameter must be published as
   roster-specific". THE EARNED OUTCOME: the 6.9x headline is withdrawn; transfer is UNDETERMINED at the
   operating point (2 established events against ~1.2 nominal, P about 0.3); the slope is not reproduced on
   fully novel pairs; the roster-specific caveat is RETAINED AS UNTESTED, and the sentence below lifting it is
   withdrawn. A corrected budget_transfer.py (fit on x12, score only pairs whose verdicts are new, on the merged
   board, McNemar counts beside every wrong count) is running and its numbers will be inserted here.

   *The rewrite of 2026-09-14 follows, unedited, superseded by the paragraph above:*

5. **AMENDED 2026-09-14 by BUDGET-TRANSFER, then CORRECTED the same evening by BUDGET-LOMO. The budget DOES
   transfer; my first amendment here was wrong and is retracted.**

   The first amendment reported the budget as 6.9x miscalibrated on pairs containing a model it had not seen,
   called that an overfitting signature, declared the registered falsifier fired, and forbade publishing a
   nominal confidence off the fitting roster. That rested on wrong-direction LABELS to which I had not applied
   the McNemar establishment filter from SYSTEMATIC-BUDGET section 4 - the same test I had used on the x12 fit
   hours earlier. Applied consistently:

   | stratum | edges | called | wrong | nominal | ratio |
   |---|---|---|---|---|---|
   | SHARED (fitted pairs), established labels | 826 | 599 | 0 | 0.95 | 0.0x |
   | CROSS (one model new), established labels | 1106 | 800 | 2 | 1.15 | **1.7x** |
   | INTERNAL (both new), established labels | 331 | 242 | 0 | 0.29 | 0.0x |

   Only **2 of the 9** CROSS wrong calls rest on a key direction the key establishes; five of the other seven
   are Meta-Llama-3.1-70B against gpt-4o-mini or claude-3-5-haiku, whose key accuracies are 0.630, 0.633 and
   0.630 - within 0.003 and in the same tier. There is no fitted-versus-unfitted gap, so the overfitting
   signature is gone; the falsifier did not fire; and `b1` refit on all established x20 edges is **+4.1080**,
   inside the x12 anchor-clustered CI [1.72, 7.87]. The "sign reversal" I raised on the INTERNAL subset
   (-0.5230) was noise in a stratum with **zero wrong calls** and therefore no signal to fit.

   Corroborated within roster by BUDGET-LOMO: leave-one-ANCHOR-out 2.4x, leave-one-PAIR-out 2.3x,
   leave-one-MODEL-out **2.5x** - the model-axis fold, which BUDGET-TRANSFER predicted would expose leakage,
   exposes none. `b1` does swing 2.61x across model-withholding folds, and the calibration is robust to that
   because the widener is monotone and the threshold coarse: **the fitted shape matters, the fitted scale much
   less.**

   **The prohibition on publishing a nominal confidence off the fitting roster is LIFTED.** The real limitation
   is different and applies everywhere: no certificate can be read on a pair whose key direction is not
   established, and 41% of this corpus's wrong-direction labels are in that class.


6. **The blind spot named in section 5 of the derivation is mis-located** (LOW-AGREEMENT). Median agreement over
   the 891 edges is 0.441 and all three surviving wrong calls sit above it. The wrong-direction rate *rises*
   with agreement - 1.5% below 0.35, 10.0% at 0.65-0.80, **29.4% above 0.80** - and after the budget the bottom
   three quintiles are completely clean. Widening with agreement is the right shape; the residue is a scale
   question inside that channel, not a missing second one.

Everything below is the derivation's own text, unedited apart from this header.

---

Everything computed. Writing the specification.

---

# SYSTEMATIC-BUDGET — the form to implement

## 1. The choice

**Form (A), ADDITIVE VARIANCE**, in a key-free, centering-free two-parameter reparametrisation: `τ(A) = exp(b₀ + b₁·A)` added in quadrature to the bootstrap SD, where `A` is the pair's answer-agreement. It is the only one of the four that is a widener by construction rather than by a post-hoc clip, the only one whose fitted parameter survives the label-noise purge that killed the conformal form, and the only one that clears all four registered criteria without using the key at inference.

**The deciding number: 0.** On the pooled 66-pair board — the object TIER-HONEST actually flagged — the raw certificate calls 64 pairs with **2** wrong-direction; the budget calls 56 with **0**, withdrawing *both* known inversions. No agreement gate at any threshold does this: the second inversion (Meta-Llama-3.1-8B vs command-r) sits at A = 0.391, below the board's median agreement of 0.399.

## 2. The specification

```
A_e   = answer agreement between the two models on the cell's questions   # eval_results.pred, letters only
m_e   = mean(θ_a − θ_b)  over the B board draws
s_e   = sd  (θ_a − θ_b)  over the B board draws                            # ddof=1
τ_e   = exp(b₀ + b₁ · A_e)                    b₀ = −3.2326   b₁ = +3.3133
c̃_e   = min( c_raw_e ,  Φ( |m_e| / sqrt(s_e² + τ_e²) ) )
call the edge iff c̃_e ≥ 0.975
```

`c_raw_e = max(p_e, 1−p_e)` is the incumbent certificate. The `min()` is not a fitted clip — τ² can only *add* to the variance, so the Gaussian term never exceeds the Gaussian-at-τ=0 baseline (verified: 0 of 891 edges rise, max deviation −9.3e-13). The `min()` exists only so the swap from the empirical draw fraction to its Gaussian summary cannot raise a confidence either; with it, **0 of 891 edges are made more confident and 0 calls are created.**

**Free parameters: 2.** No standardisation constants, no bins, no cap, no fitted threshold. The 0.975 is the incumbent's. This is what closes the reviewers' "effective parameters are really 4" objection: with agreement entering raw on [0,1] there are no roster-dependent centering nuisances, and the link is not load-bearing — softplus gives LOAO deviance 217.12 against the exponential's 216.94.

**Inference-time inputs:** `m`, `s`, `A`. Nothing else. `A` is what the shipped disagreement filter already computes; `m` and `s` come from the draw array the certificate already builds. **No answer key.** Registered criterion (3) passes — this is why the headline is the agreement-only fit and not the `agree + refacc` fit (LOAO 193.55, better, but `refacc` is graded against the key and is not deployable).

**Where it slots in.** `judge_free_tests.board_from` is unchanged. The change is entirely in the certificate that consumes its draws: today that code keeps only `p = #{d : d[a] > d[b]} / B`. Keep the `(B, 12)` θ matrix instead, take `m` and `s` off the `a−b` column difference, join `A` from `eval_results.pred`, and threshold `c̃` in place of `p`. Pure post-processing; nothing upstream of the bootstrap moves.

**Scale sanity.** τ = 0.107 / 0.175 / 0.288 / 0.559 / 0.778 at A = 0.30 / 0.45 / 0.60 / 0.80 / 0.90, against a per-anchor bootstrap s of median 0.246 (p10 0.203, p90 0.295). On the pooled board s ≈ 0.07, so τ dominates — correct behaviour for a systematic floor, which must not shrink with n, and the mechanical reason the pooled inversions fall.

## 3. Calibration evidence

Per-anchor edges, 0.975 threshold. "Nominal" is Σ(1−c̃) over the called set.

| certificate | called / 891 | wrong | nominal | ratio | P(≥obs) |
|---|---|---|---|---|---|
| raw, as shipped (empirical p) | 739 (82.9%) | 8 | ≈0 — it asserts p = 1.000 on 662 edges | — | — |
| raw, Gaussian (τ = 0) | 738 (82.8%) | 7 | 0.75 | 9.3× | <1e-4 |
| **budget, in sample** | 666 (74.7%) | 2 | 1.30 | 1.5× | 0.37 |
| **budget, leave-one-ANCHOR-out** | **663 (74.4%)** | **3** | **1.24** | **2.4×** | **0.129** |
| budget, leave-one-model-PAIR-out | 665 (74.6%) | 3 | 1.30 | 2.3× | 0.142 |

Aggregate over all 891 edges, out of fold: nominal **48.6** against **44** observed — conservative, criterion (1) passes in aggregate. At the operating point it is 2.4× tight, but with 3 events that is **not distinguishable from calibrated** (p = 0.13), whereas the raw certificate's 7-against-0.75 is (p < 1e-4). The honest claim is that the budget *removes an established miscalibration and replaces it with one that is no longer detectable* — not that it achieves calibration.

Registered criteria: **(1) pass in aggregate, undetermined at the operating point. (2) pass** — 78.3% of edges still called at the 95% level, floor is 60%. **(3) pass** — no key. **(4) pass** — 2 parameters.

Supporting checks, all mine:

- **b₁ = 3.313, anchor-clustered 95% CI [1.72, 7.87], P(b₁ ≤ 0) = 0.0017.** LOAO fold range [2.67, 5.09]; leave-one-pair-out [2.41, 4.14].
- **The LOAO test discriminates here.** 20 pure-noise stratifiers give LOAO deviance median 232.91, range [227.1, 236.7] — every one *worse* than flat-τ (230.84); real agreement is 216.94. This is the check that voided the conformal form's headline validation, and this form passes it.
- **Label noise (the attack that killed form D).** 18 of 44 wrong edges and 4 of 8 wrong calls have a key direction not established by exact McNemar at 5%, the flagship Law arx/iask among them (p = 0.121). Refit on the 809 established-direction edges only: **b₁ = 2.14** (fold range [1.14, 6.15]) — reduced by a third but alive. The conformal f collapsed to exactly 1.000 on this same subset; this form does not.
- **The key-gap filter is not deployable**, and all three reviewers were right that it selects the population. Unfiltered: **924 edges, 61 wrong, raw 748 called / 11 wrong = 1.47%** (not 1.08%). The 33 excluded edges are 52% wrong-direction; the 891-fit applied cold calls 1 of them, correctly. Refit on all 924, LOAO: 650 called / 3 wrong. The form survives; every published *rate* must be restated on 924.
- **Pooled board**, B = 300 over 2,811 questions: question-resampled 64 called / 2 wrong → **56 / 0**; match-resampled (TIER-HONEST's own scheme) 63 / 2 → **57 / 0**.

Residual failure, stated plainly — the out-of-fold band that does not behave:

| band | n | nominal | observed |
|---|---|---|---|
| [0.990, 0.999) | 92 | 0.38 | 1 |
| [0.999, 1.001) | **521** | **0.03** | **1** |

The budget still asserts near-certainty on 521 edges and one of them is wrong. Same shape as the raw certificate's failure, ~8× smaller.

## 4. What it costs

**Per-anchor:** 76 of 739 raw calls withdrawn (10.3%), 5 of them wrong; **663 kept with 3 wrong**. Withdrawal precision 6.6% against a 1.08% base rate. No calls created.

The 3 wrong calls that survive are the blind spot, and it is a real one — all three are *low*-agreement, and the two Law ones carry the most solid key labels of the eight (McNemar p = 0.0018, 0.0015):

| anchor | pair | A | out-of-fold c̃ |
|---|---|---|---|
| Law | Meta-Llama-3.1-70B vs Qwen1.5-72B | 0.475 | 0.9990 |
| Law | Meta-Llama-3.1-70B vs deepseek-v2.5 | 0.476 | 0.9917 |
| History | Qwen1.5-72B vs deepseek-v2.5 | 0.605 | 0.9882 |

**arx/iask: yes, it stops being confidently separated — at both levels.** All 7 per-anchor edges fall below 0.975 out of fold, the highest being Law at 1.000 → **0.9336**; Chemistry 1.000 → 0.785, Math 0.857 → 0.564. On the pooled board, **1.0000 → 0.7777**. The registered headline prediction holds.

**Pooled board, the 8 pairs that lose their call:**

| pair | A | c̃ | key direction |
|---|---|---|---|
| Llama-2-13b vs Llama-2-7b | 0.342 | 0.971 | right |
| Meta-Llama-3.1-8B vs command-r | 0.391 | **0.964** | **WRONG — withdrawn** |
| Meta-Llama-3.1-8B vs Yi-6b | 0.373 | 0.941 | right |
| gemini vs gpt-4o | 0.777 | 0.881 | right |
| gpt-4o vs iask | 0.813 | 0.859 | right |
| arx vs gemini | 0.862 | 0.785 | right |
| **arx vs iask** | 0.880 | **0.778** | **WRONG — withdrawn** |
| Meta-Llama-3.1-70B vs Qwen1.5-72B | 0.613 | 0.662 | right |

Six correct separations surrendered to remove both inversions. The visible product consequence: **the entire top of the board — arx, iask, gpt-4o, gemini — collapses into one group the arena can no longer separate.** Given the campaign's own verbosity-bias result that is the right answer, but it is a large, user-facing change and should be presented as the finding, not buried in a threshold.

On the per-anchor edges the budget does *not* strictly dominate a hard gate (gate A ≥ 0.80 keeps 707 with 4 wrong; the budget keeps 663 with 3). Its advantage is on the pooled board, where gates at 0.70/0.75/0.80 each withdraw 3–5 pairs and leave the command-r inversion standing, because it acts on τ/s rather than on A alone.

## 5. Honest limits

- **44 events, 8 at the operating point, in 4 anchors** (Law 4, History 2, Chemistry 1, Other 1) and 13 of 66 model pairs; 26 of 44 sit in the 75 frontier-internal edges (34.7% wrong there against 2.2% elsewhere). Fourteen LOAO folds, but only four carry a called-wrong event.
- **Operating-point calibration is not established and cannot be at this n.** 3 against 1.24 is p = 0.13. Eighty percent power against a 2× miscalibration needs ~9 expected wrong calls — **~7.3× this corpus, roughly 100 anchors of the present size (~6,500 edges)**. That is the collection requirement, and it is the only thing that would turn "no longer detectably miscalibrated" into "calibrated".
- **The scale is not pinned.** b₁'s anchor-clustered CI spans 4.6×; at A = 0.88 that is τ ∈ [0.31, 4.0]. The *form* and the *sign* are supported; the magnitude is one anchor-resample away from moving by a factor of two.
- **Not portable across tiers.** Trained off-frontier, b₁ falls 3.31 → 1.46; applied cold to the 75 frontier edges it goes 31 called / 5 wrong → 12 called / 2 wrong, against a nominal of 0.06 — 33× under-budgeted on the tier that carries most of the errors. It reduces frontier error; it does not calibrate there.
- **The pooled result is an extrapolation.** τ was fitted where s ≈ 0.246 and applied where s ≈ 0.07. Three wrong-direction pairs among 66 gives no power to check it. The pooled board is the registered prediction being *met*, not evidence of calibration at that scale.
- **A third of the fitted effect may be label indeterminacy**, not inversion: b₁ drops 3.31 → 2.14 when edges the key cannot adjudicate are removed.
- **One roster, one judge (STACK-v2), one reference, one tree.** Answer agreement is a property of this roster's answer distribution. Nothing here tests transfer.

**A reader should not conclude:** that the certificate is calibrated; that 0 wrong on the pooled board means the board is now correct (it means two known inversions are silenced, on 3 events); that b₁ = 3.31 travels to another roster; or that this budgets systematic error in general — it budgets the high-agreement channel and misses the two best-established Law inversions entirely.

## 6. The fallback

If you judge 44 events too thin to ship a number, **do not fall back to the registered plan.** The registration says RESOLVE would then ship the conformal per-stratum threshold as a stated limitation; that option is now falsified — its f = 1.865 collapses to exactly 1.000 when refitted on the edges whose key direction is established, so it is a fit to label noise.

Ship instead the **decline rule without the probability**:

1. Keep the shipped bootstrap certificate unchanged.
2. Publish alongside it a **systematic-reservation list** — the pairs whose call `c̃ < 0.975` withdraws, with their answer-agreement — and the measured operating characteristic: on this corpus it removed 5 of 8 per-anchor wrong calls for 71 correct ones, and both pooled inversions for 6 correct separations.
3. Lead with the diagnosis, which *is* established at p < 1e-4 and needs no fitted parameter: **the bootstrap certificate asserts p = 1.000 on 662 of 891 edges and 6 of them are wrong; on the pooled board it is 100% certain on both of the board's inversions.**
4. State the honest denominator: 924 edges, 1.47% raw wrong-call rate.

This is strictly weaker than shipping τ, and it loses nothing that the data actually supports — the ordering and the direction of the withdrawals are what carry the p-values, not the scale.

---

**Scratch (read-only on the repo, zero LLM/network calls, no git writes):** `C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\budget\lead\` — `L1_table.py` (canonical 891/924 table from the cached draws), `L2_fit.py` (fit + LOAO ladder), `L3_attack.py` (label noise, population filter, noise stratifiers), `L4_pooled.py` (pooled 66-pair board), `L5_final.py` (monotonicity, link, cold transfer, clustered CI), `L6_spec.py` (shipped `min()` form, bands, gate comparison).

**One disclosure:** `L4_pooled.py` chdir'd to the repo root and wrote `pooled.json` there at 22:48; I moved it into the scratchpad at 22:52 and confirmed `git status` is back to its pre-session state. (`M experiment_results/judge_solve/.gitignore` in the current status is *not* mine — mtime 21:36, before this session's work.) No other repo file was touched.