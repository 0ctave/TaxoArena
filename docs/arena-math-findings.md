# Math arena on the frozen construction — findings

Run: `experiment_configs/arena_math_frozen.toml`, snapshot `20260727_042523`
(87 leaves, certified, 87/87 rubrics). 8 models, 11 Math cells, 241 judged
reserved questions, 1736 verdicts per condition, MAIN vs GENERIC_JUDGE
(MT-Bench-style domain-agnostic judge). Completed, 0 errors beyond the known
`[ARENA-SE]` inverse-variance floor guard.

## Headline — read this first, it reframes everything below

**The judge decides on answer correctness, not on reasoning quality.**

On items where exactly one response is correct and the judge did not tie, it
picks the correct one 88.8% of the time (MAIN) and 88.4% (GENERIC_JUDGE). The
rubric moves that by 0.4 points.

| condition | decidable, non-tie | GT-agreement |
|---|---:|---:|
| GENERIC_JUDGE | 1033 | 913 = **88.4%** |
| MAIN | 1029 | 914 = **88.8%** |

Independent corroboration from the tie rates, which was not part of the
hypothesis. When correctness CANNOT discriminate, the judge falls back to "these
are equivalent":

| subset | n | tie rate MAIN | tie rate GENERIC |
|---|---:|---:|---:|
| exactly one correct | 1160 | ~11% | ~11% |
| both correct | 129 | **38.0%** | **32.6%** |
| neither correct | 447 | **33.1%** | **34.9%** |

A three-fold jump in ties precisely where the answer key stops helping. That is
the signature of a correctness-driven decision.

### The composite claim, four measurements with controls

The judge **decides on answer correctness** (88.8% agreement with the key on
discriminable items), **reads** the leaf-specific rubric (rationale-rubric
overlap 0.200 against a 0.138 baseline that never sees it), **reproduces its
vocabulary** in the justification, and **reaches the same verdict as a
rubric-free judge** (99.4% identical winners). When correctness cannot
discriminate, the tie rate triples.

Each has a control that shares every confound except the treatment. Together
they identify one mechanism: the arena is largely re-deriving the answer key and
reporting it with domain-flavoured justification.

### How much fidelity depends on the key being available

Analysis 0, run. Rho recomputed on the subset where correctness CANNOT
discriminate — both responses correct, or neither — so the judge must evaluate
rather than verify. Ties count 0.5 per side, fixed in advance.

| condition | subset | n rows | n questions | tie fraction | rho |
|---|---|---:|---:|---:|---:|
| MAIN | full | 1736 | 241 | 0.19 | +0.9762 |
| MAIN | discriminable | 1160 | 201 | 0.11 | +0.9524 |
| MAIN | **correctness-blind** | 576 | 170 | **0.34** | **+0.7619** |
| GENERIC | full | 1736 | 241 | 0.19 | +0.9524 |
| GENERIC | discriminable | 1160 | 201 | 0.11 | +0.9762 |
| GENERIC | **correctness-blind** | 576 | 170 | **0.34** | **+0.7381** |

**SELECTION CONTROL — range restriction is NOT the explanation.** The blind
subset is where the models agree, so it might carry less capability spread by
construction. Measured on the same 576 rows: GT accuracy spread 0.249 against
0.258 on the full set (a 3.5% reduction), and the ground-truth ranking there is
**identical** to the full-set ranking, rho(GT_blind, GT_full) = **+1.000**. The
subset preserves the true ordering perfectly, so the fidelity drop is judgment,
not selection.

Fidelity falls ~0.22 (0.95-0.98 -> 0.74-0.76) while the tie fraction triples
(0.11 -> 0.34). Both conditions behave identically — MAIN 0.762, GENERIC 0.738,
one grid step apart, which is nothing at n = 8.

This is the options-blind measurement without a new run, and it lands on the
combination the pre-registered reading table called "the judge can no longer
decide". But the task did NOT change here: the judge still has the question, the
options and both responses. What it lost is a DISCRIMINATING key. So the claim
sharpens from "the judge prefers correctness" to a magnitude: **when correctness
is unavailable, ranking fidelity degrades to rho ~0.75 and the judge abstains on
a third of comparisons.** Residual reasoning-based signal is real — 0.75 is well
above chance — but substantially weaker than the aggregate 0.95 implies.

Unlike the MAIN/GENERIC comparisons, this gap is not quantisation noise: at
n = 8 models the Spearman grid is 0.0119, so 0.9762 -> 0.7619 is ~18 grid steps.

Caveat: 170 questions against 241, and the subset is self-selected by model
agreement. The selection control addresses the ranking-compression form of that
concern; it does not address whether these items are harder in ways that affect
judging beyond correctness.

### Reasoning text makes the judge WORSE at picking the correct answer

GT-agreement stratified by whether each response carries a chain-of-thought
trace. The roster is balanced 4/4 by design. Rows where exactly one response is
correct and the judge did not tie.

| condition | stratum | hits / n | GT-agree | SE | ties |
|---|---|---:|---:|---:|---:|
| MAIN | trace x trace | 181 / 215 | **84.2%** | 2.5% | 40 |
| MAIN | trace x no-trace | 590 / 660 | 89.4% | 1.2% | 17 |
| MAIN | no-trace x no-trace | 143 / 154 | **92.9%** | 2.1% | 74 |
| GENERIC | trace x trace | 174 / 211 | **82.5%** | 2.6% | 44 |
| GENERIC | trace x no-trace | 595 / 670 | 88.8% | 1.2% | 7 |
| GENERIC | no-trace x no-trace | 144 / 152 | **94.7%** | 1.8% | 76 |

Agreement is HIGHEST where neither response has a trace and LOWEST where both
do — an 8.7-point gap (MAIN), ~2.7 SE, and the same shape in GENERIC.

This inverts the design assumption. An untraced response is a bare answer
letter, so the judge has nothing BUT the letter — and it matches the key almost
perfectly. Traced responses give it reasoning to read, and agreement falls. That
is only paradoxical if the judge is evaluating; it is exactly what verification
predicts, with the prose as a distraction that occasionally argues it out of the
correct answer.

The tie counts corroborate independently: 74 ties in the no-trace stratum
against 17 in the mixed one. Given two bare letters and no reasoning to compare,
the judge either matches the key or declares equivalence.

This was not part of the hypothesis, so it is confirmation of the
correctness-driven reading from a direction that was not being looked at.

**Consequence for the planned OPTIONS-BLIND arm.** The `no-trace x no-trace`
stratum was designed as a floor expected near 50%. WITH options it sits at
92.9%, so it is not measuring what the design assumed — it is
letter-verification at maximum clarity. WITHOUT options that stratum becomes
genuinely uninformative (two bare letters, no key), and it should return to
chance. **If it does not, that is the leak the design was built to detect** — a
sharp test rather than a formality. And `trace x trace` at 84.2%, n = 215,
SE 2.5%, is the real measurement: a fall to ~75% would be ~3.6 SE and clearly
readable.

**This is a negative result about the LLM-as-judge paradigm, not about the
taxonomy.** MMLU-Pro is multiple-choice with a verifiable key, so a capable
judge can shortcut to correctness and bypass the partition entirely. The
architecture would only bind where correctness is not checkable — open-ended
generation, agent traces, tasks with no key. That is the setting the incremental
framing was always aimed at, and this result is now the MEASURED argument for
it rather than a motivation. MMLU-Pro grounds the comparison and is also the
corpus where the judging mechanism can bypass what the comparison is about.

## Ranking fidelity

Both judges recover the ground-truth ordering to within one adjacent
transposition. Aggregate rho ~0.95-0.98 (win-rate); the run's own BT-based
aggregate reports rho = 0.90, tau = 0.79. Given the above, that fidelity is
substantially inherited from the answer key rather than earned by judgment.

**The arena cannot separate the two conditions at n = 8, and that is structural
rather than a power problem.** Spearman at n = 8 is quantised in steps of
6/(n(n^2-1)) = 0.0119, so the observed MAIN-GENERIC gap of 0.024 is exactly two
grid steps — one adjacent swap. Only more MODELS changes this; more judging
cannot.

## The per-cell comparison was underdetermined by construction

Paired on identical (question, model-pair) comparisons:

```
comparisons present in both conditions   1736  (complete overlap)
identical verdict                        1529 / 1736 = 88.1%
disagreements                             207, of which 197 (95%) involve a TIE
                                          on one side
actual winner flips                        10 of 1736  (99.4% agreement)
```

Two judges agreeing on 99.4% of winners cannot produce a detectable ranking
difference at any n, granularity, or domain count. So the per-cell null is NOT
evidence of parity — it is a comparison whose arms barely differ. Rule 0
arriving from a direction the pre-registration did not anticipate: the metric,
the reading, the decisive range and the confound were all fixed in advance, and
none of that protects against arms that are nearly the same treatment.

**Precondition for any future A/B arm: measure verdict agreement FIRST.** It is
one query, and it decides whether the arm is worth 10k calls.

## Win-rate is biased by the adaptive scheduler — use BT

| statistic | mean diff (MAIN - GENERIC) | pos/neg/tied | sign test |
|---|---:|---|---:|
| win-rate | +0.0143 | 5 / 0 / 6 | p = 0.031 |
| **BT theta** | **-0.0016** | **5 / 2 / 4** | **p = 0.227** |

The scheduler over-samples uncertain pairs, so mid-ranked models face harder
average opposition — exactly where an adjacent transposition lives. Win-rate
ignores opponent strength and manufactured a 5/0 result that BT erases. Quote
BT; win-rate is a coarse proxy here, not a substitute.

## The rubric is read, reproduced, and not decisive

Fraction of each rationale's vocabulary also present in that cell's induced
rubric. GENERIC_JUDGE never sees the rubric, so its value is the baseline —
topical coincidence between a Math rationale and a Math rubric:

| condition | rationale length | overlap with cell rubric |
|---|---:|---|
| GENERIC_JUDGE (baseline) | 49 words | 0.138  IQR [0.077, 0.200] |
| MAIN | 54 words | **0.200  IQR [0.115, 0.280]** |

MAIN is 45% above baseline with IQRs offset throughout. The judge ingests the
rubric and reflects it in the justification — and decides the same thing anyway.

**RATIONALE-CONDITIONED, NOT RATIONALE-DRIVEN.** For the alternative ("applies
the criteria and coincidentally agrees") to hold, criteria-guided and
criteria-free judges would have to reach identical winners on 1726 of 1736
comparisons. The simpler reading is that the verdict is determined before the
rubric enters, and the rubric shapes the justification afterwards.

That is a finding about LLM-as-judge methodology, not about this taxonomy.

Caveat: lexical overlap shows REPRODUCTION, not APPLICATION. The rule-ID
citation scheme settles it directly — a cited rule ID cannot arise from topical
coincidence — and it also answers, for free, how many verdicts cite no rule at
all, i.e. are decided on priors. **It changes the verdict schema, so it must
land BEFORE the full-corpus arena.**

## What was retired

The C3 inversion. An earlier validation gave MAIN 0.648 against GENERIC 0.701 —
backwards — on 4 leaves and 553 queries. At full width the ordering is not
inverted; that was a small-sample artifact.

## Scope limit on the mechanism test

The pre-registered prediction (MAIN-minus-GENERIC tracks reusable share, weakest
in enumerative cells) **cannot be tested on Math**. Math's minimum reusable share
is 0.080; the prediction turns on cells <= 0.067, which sit in Other, Health and
Psychology. The decisive range is ABSENT, not underpowered — more Math
comparisons cannot help. Observed slope rho = +0.511, p = 0.109, n = 11: right
direction, measured in the flat region.

## Where link 3 stands

```
coherent cells --causal, p=1.2e-6--> specific rubrics --read, not decisive--> judgments
```

Link 2 is established causally (`docs/prereg_rubric_specificity.md`). Link 3 now
has a MECHANISM for its null rather than an absence of effect.

## Next, in order

0. ~~Rho on the correctness-blind subset~~ — **DONE**, see "How much fidelity
   depends on the key being available" above. Both pre-registered controls held:
   the selection control cleared range restriction (GT rho on the subset =
   +1.000 against the full set), and ties were handled at 0.5 per side with the
   fraction reported. Result: rho falls to ~0.75 with the tie fraction tripling.

1. **Rule-ID citation** in the verdict schema. Distinguishes reproduction from
   application, and counts prior-decided verdicts. Must precede the full-corpus
   run because it changes the schema.
2. **OPTIONS-BLIND arm.** Same 241 questions, MAIN rubric, options withheld from
   the judge. Implementation: suppress the options block built in
   `TaxonomyArenaService.evaluateWithPrecomputedTraces` (~lines 655-657); the
   answering models' block at 319-322 is separate and must stay.

   It completes a 2x2 that the correctness-blind subset does NOT cover — the two
   manipulations are orthogonal, not substitutes:

   |  | options present | options withheld |
   |---|---|---|
   | key discriminates (n=1160) | 88.8% GT-agree, rho 0.95 | **the missing cell** |
   | key ties (n=576) | rho 0.75, tie 0.34 | — |

   The blind subset holds information constant and varies the population;
   OPTIONS-BLIND holds population constant and varies information. There is also
   a mechanism difference: in the blind subset the judge can verify both answers
   are right and then knowingly falls back to other grounds, whereas without
   options it never knows, so reasoning is its primary signal from the start.

   **PRIMARY OUTCOME IS GT-AGREEMENT, NOT RHO.** Rho at n = 8 is quantised at
   0.0119 and burns 1736 comparisons for one number. GT-agreement is a
   per-verdict proportion: n = 1160 on the discriminable subset, SE ~1.5%,
   resolving ~4-point differences.

   | 88.8% falls to | reading |
   |---|---|
   | ~55% (chance) | the key was doing nearly all the work |
   | ~75% | reasoning carries substantial independent signal |
   | ~85% | options barely mattered; the judge infers correctness from reasoning |

   **STRATIFY BY TRACE PRESENCE — mandatory, not optional.** 4 of the 8 models
   carry no trace. Without options, a bare "C" against a bare "E" gives the
   judge nothing, and a traced response against an untraced one is decided by
   trace presence alone. So report separately: `trace x trace` (6 pairs, ~250
   comparisons, SE ~3% — the real measurement), `trace x no-trace` (16 pairs,
   contaminated, expect trace-presence to dominate), and `no-trace x no-trace`
   (6 pairs — the built-in null, which SHOULD return to chance; see the
   stratified baseline above for why it currently does not).

   Tie rate alongside. **Refusal and malformed-verdict rate separately** — with
   two bare letters and no options, a judge that DECLINES is a distinct outcome
   from one that guesses, and collapsing them would hide the difference.

   #### Predictions, fixed before the run

   | stratum | with options | predicted without |
   |---|---:|---|
   | no-trace x no-trace | 92.9% | **~50% (chance), tie rate very high** |
   | trace x trace | 84.2% | the measurement — reasoning-only signal |
   | trace x no-trace | 89.4% | confounded; expect trace-presence to dominate |

   **`no-trace x no-trace` is now the sharpest cell, not a formality.** Without
   options AND without traces the judge has a question and two bare letters —
   genuinely no information. It must return to chance or tie. If it comes back at
   70%+, something is leaking, and the candidates are enumerable: the judge
   recognising the question from pretraining, position bias surviving the
   dual-call control, or letter-frequency priors in MMLU-Pro. None of those is
   currently measurable, and any would be worth knowing. That makes this a
   falsification test with a hard prediction rather than a floor.

   **For `trace x trace`, write down the second possibility now.** At SE 2.5% a
   drop to ~75% is 3.6 SE and readable. But landing NEAR 84% — unchanged — is
   plausible given the inversion above, and it would mean that on traced pairs
   the judge was never using the key at all, so the 88.8% aggregate is carried
   entirely by the untraced and mixed strata. That is a cleaner decomposition
   than anything currently in this document, and it should not be discovered
   after the fact.
3. **Other or Health**, only if verdict agreement there shows the arms differ.

## Data and defects

Data: `experiment_results/arena_math_frozen/`, and `ratings.db` under snapshot
`20260727_042523_{MAIN,GENERIC_JUDGE}`.

`rank_history.csv` is half-wired: `scores` is `0.0000;...` in all 9,906 rows and
`comparisons` reads 0.0 for early rounds. The `ranking` string IS populated, so
per-round orderings and the last-ranking-change mark are recoverable; score
trajectories and ribbons are not. Same class as `iteration_metrics`' zeroed
counters and `wall_ms` — a column declared, written, structurally valid, empty.

`TaxonomyArenaService.compareModels` takes a bare question with no options and
has three callers: the REST controller, the TUI, and
`compareModelsWithAnswerExtraction` — the last builds its own options block, so
it is safe. The arena uses `evaluateWithPrecomputedTraces`, which does pass
options. A `require(...)` guard on the shared entry point would break the two
interactive callers; the fix is a separate entry point with the guard on the
arena-facing one.

## Identification cost, measured

`[ARENA-IDENT]` at 8 models: identification is reached at **7 pairs of 28** — a
spanning tree, as predicted — at 32.9 to 45 comparisons per cell. The cost
VARIES across cells, which clears the void condition in
`docs/prereg_arena_launch.md` (the earlier Math run's uniform 56 was a scheduler
allocation, not a cost). Minimum 32.9 sits in the `<= 40` band: leaf-level
judging is affordable, ~2,900-3,900 calls for 87 cells against a ~10,000 budget.

---

## Math cannot test the granularity claim, and the ground truth says so

Analyses #2 and #3 were free regroupings of verdicts already on disk (1,736 per
condition, 11 Math cells, 241 questions, 8 models). Join verified before
computing: 241/241 questions and 8/8 models resolve against `eval_results`.

### #2 Cell size vs judge fidelity — underpowered, curve not validated

| cell | nQ | GT-agree | SE | tie% | rho | rho_blind | r=n/(n+7.66) |
|---|---:|---:|---:|---:|---:|---:|---:|
| n00000155 | 37 | 88.2% | 3.3% | 27.5% | 0.946 | 0.707 | 0.828 |
| n00000239 | 27 | 82.8% | 3.8% | 23.9% | 0.892 | 0.723 | 0.779 |
| n00000158 | 25 | 91.7% | 3.0% | 18.9% | 0.952 | 0.916 | 0.765 |
| n00000154 | 23 | 82.8% | 3.8% | 22.7% | 0.916 | 0.855 | 0.750 |
| n00000161 | 23 | 94.8% | 2.2% | 19.2% | 0.988 | 0.855 | 0.750 |
| n00000238 | 22 | 84.9% | 3.9% | 18.8% | 1.000 | 0.929 | 0.742 |
| n00000157 | 20 | 91.6% | 2.8% | 11.0% | 0.898 | 0.898 | 0.723 |
| n00000242 | 17 | 87.5% | 3.1% | 11.7% | 0.916 | 0.699 | 0.689 |
| n00000159 | 16 | 100.0% | 0.0% | 15.6% | 0.976 | 0.905 | 0.676 |
| n00000241 | 16 | 86.7% | 3.3% | 15.1% | 0.905 | 0.643 | 0.676 |
| n00000240 | 15 | 88.9% | 3.5% | 20.3% | 0.859 | 0.724 | 0.662 |

Fidelity regressed on cell size, k=11 cells (critical |rho| ~ 0.618 at p=.05):

```
                    MAIN     GENERIC
GT-agreement vs n  -0.231     -0.320
rho vs n           +0.236     +0.386
rho_blind vs n     +0.078     +0.438
```

**Nothing is significant, and the test could not have succeeded.** Cell sizes
span only n=15..37, over which `r = n/(n+7.66)` moves 0.662 -> 0.828 and the
disattenuation factor `sqrt(r)` moves 0.81 -> 0.91. Predicted rho for the largest
cell is 1.12x the smallest — but observed rho is already 0.86-1.00, so the
prediction lands above the ceiling. **The reliability curve remains an untested
caveat.** Validating it needs cells spanning a far wider n, or a domain where rho
is low enough to have somewhere to move.

### #3 Aggregation-level fidelity — flat, then rising at the coarsest cut

```
cut                groups  mean nQ    MAIN   GENERIC
leaf cut               11     21.9   0.932     0.926
depth-3 cut             4     60.2   0.929     0.917
depth-2 cut             2    120.5   0.929     0.929
Math as one cell        1    241.0   0.976     0.976
```

Finer aggregation does not improve fidelity. The single Math cell scores
highest, identically under both judges.

### Why: the ground truth has no cell-level structure in Math

```
mean rho(cell BT,     GLOBAL BT)  = 0.942 MAIN / 0.948 GENERIC
mean rho(cell GT acc, GLOBAL GT)  = 0.945          <-- ground truth itself
rho(GLOBAL BT, GLOBAL GT)         = 0.976
```

The arena's per-cell rankings depart from the global ranking by **the same
amount the ground truth does**. This is not the arena failing to resolve cells.
There is nearly nothing at the cell level to resolve: in Math these 8 models are
ordered almost identically in every sub-cell, and the arena tracks that
faithfully at every level.

**So the flat A3 curve is a property of the domain, not of the taxonomy.**

### Screening: which domains can show a granularity effect at all

Free, offline, no arena calls — per-domain GT accuracy ranking against global,
with a 2,000-draw permutation null over same-size random subsets of the same
reserved pool (3,445 questions with all 8 models, seed 42):

| domain | nQ | rho | null p5 | null median | p_emp |
|---|---:|---:|---:|---:|---:|
| **law** | 287 | **0.855** | 0.934 | 0.994 | **0.000** |
| **philosophy** | 144 | **0.850** | 0.922 | 0.988 | **0.000** |
| **history** | 114 | **0.850** | 0.922 | 0.982 | **0.001** |
| psychology | 238 | 0.922 | 0.922 | 0.994 | 0.056 |
| other | 277 | 0.922 | 0.922 | 0.994 | 0.064 |
| health | 206 | 0.922 | 0.922 | 0.994 | 0.069 |
| physics | 379 | 0.970 | 0.958 | 0.994 | 0.220 |
| **math** | 393 | **0.970** | 0.958 | 0.994 | **0.217** |
| chemistry | 339 | 0.970 | 0.946 | 0.994 | 0.249 |
| biology | 196 | 0.970 | 0.922 | 0.994 | 0.385 |
| economics | 250 | 0.982 | 0.922 | 0.994 | 0.394 |
| business | 232 | 0.988 | 0.922 | 0.994 | 0.413 |
| computer science | 123 | 0.994 | 0.922 | 0.982 | 0.958 |
| engineering | 267 | 0.994 | 0.922 | 0.994 | 0.962 |

Sampling noise alone almost never reorders these models (null median 0.994).
Against that floor, **only law, philosophy, and history reorder for real.**

**Math is statistically indistinguishable from a same-size random subset
(p=0.217).** The pilot domain was close to the worst available choice for
testing granularity: model ranking in Math simply is not domain-specific, so no
partition of it — however good — can demonstrate that partitioning helps.

Two consequences:

1. **The Math arena validated the judge, not the taxonomy.** Everything it
   established (88.8% GT-agreement, the key-dependence split, the trace
   inversion) is a judge result and stands. The granularity claim was never
   testable here.
2. **Budget goes to law, philosophy, history.** Law was already queued and is
   confirmed as the strongest choice. `other` is marginal (p=0.064) and should
   not be run on the expectation of a positive result.

Caveat on the screen: it uses MMLU-Pro's native category labels, not induced
cells. It bounds what any partition of a domain could show — a domain whose own
label carries no reordering is unlikely to contain cells that do — but it does
not prove induced cells inside law will separate. That remains the test.

---

## DEFECT: half the Math comparisons were decided by a capture gap, not by content

Found while sizing the roster fix for OPTIONS-BLIND. This qualifies several
numbers reported above and must be read before any of them are cited.

### The roster splits perfectly on response format, and format tracks capability

| model | response | GT acc (241 Q) |
|---|---|---:|
| gpt-4o-2024-08-06 | reasoning, median 1211 ch | 78.4% |
| claude-3-5-sonnet-20241022 | reasoning, median 630 ch | 75.9% |
| deepseek-chat-v2_5 | reasoning, median 1038 ch | 71.0% |
| claude-3-5-haiku-20241022 | reasoning, median 664 ch | 57.7% |
| Meta-Llama-3_1-70B-Instruct | **bare letter** | 53.1% |
| Qwen1.5-72B-Chat | **bare letter** | 36.5% |
| Llama-2-70b-hf | **bare letter** | 13.3% |
| Llama-2-13b-hf | **bare letter** | 7.5% |

The two groups do not overlap in accuracy (57.7% vs 53.1% at the boundary), so
**trace presence and capability are collinear.**

`model_output` is the empty string for those four models across all 12,032 rows,
while `pred` is populated. This is a **capture gap in the eval pipeline, not
model behaviour** — the responses were generated, the text was never stored.
The judge was shown a 600-1200 character worked solution on one side and, via
`getRobustTrace` (TaxonomyBenchmarkService.kt:1735), a synthesised one-line
stub on the other: `The model selected option F: "Safe practices, Distress,
Jealousy, Serious".` Not a bare character, but zero reasoning either way.

### The judge picks the response that has text, essentially always

Mixed pairs (traced vs bare), both conditions:

```
                       MAIN            GENERIC
judge picks traced   863/868 = 99.4%   874/880 = 99.3%   SE 0.3%
GT says traced right 593/677 = 87.6%   593/677 = 87.6%
excess preference        +11.8 pp          +11.7 pp
```

**Mixed pairs are 868/1736 = 50% of all comparisons.** Half the arena was
decided by which side had text. That is not a judge failure — it is the only
sane response to an empty string — but it means those verdicts carry no
information about model quality.

### What this qualifies

- **The 88.8% aggregate GT-agreement.** Half its support is format-decided. The
  format preference agrees with the key 87.6% of the time *by roster
  construction*, because text presence tracks capability.
- **rho = 0.95-0.98 against GT accuracy.** Ranking all four traced models above
  all four bare ones reproduces the top-4/bottom-4 split of the GT ordering for
  free. The rho is substantially purchased by the artifact.
- **rho_blind = 0.74-0.76.** Same mechanism: on correctness-blind pairs the
  judge still separates the groups by format.

### What survives

Within-stratum comparisons are unaffected, because both sides share a format.
Re-running the trace stratification with the capability gap controlled:

```
stratum               gap<20pp        20-40pp       >=40pp
trace x trace          83.2% (173)   88.1% (42)        --
trace x no-trace       74.6%  (67)   83.3% (186)   94.6% (407)
no-trace x no-trace    97.0%  (33)   94.4% (89)    84.4% (32)
```

At matched capability gap (<20pp) the inversion **strengthens**: bare-letter
pairs 97.0% vs reasoning pairs 83.2%, a 13.8 pp gap with capability controlled.
So *"reasoning text degrades the judge's agreement with the key"* survives, and
is now a within-format result rather than a cross-format one.

The mixed stratum at gap<20pp is the worst cell in the table (74.6%). Those are
haiku (57.7%, traced) against Llama-3.1-70B (53.1%, bare) — near-equal models
where the judge takes the traced side ~always and is therefore wrong whenever
the bare model happened to be right.

Unaffected entirely: the granularity and domain-screen results above, which use
ground-truth accuracy only and never touch a verdict.

### Consequence for OPTIONS-BLIND

Blocking. Without options AND without stored reasoning, four of eight models
present the judge with a bare letter and nothing else — those comparisons are
not hard, they are empty. The `no-trace x no-trace` cell would be 100%
uninterpretable rather than a chance-level null.

The fix is re-running generation for the four models **with output capture**,
which is generation calls rather than judge calls. Until then the arena claim
can only be made on the four-model traced subset.

---

## Roster: exclusion is viable — 10 clean models, not 4

Ran before choosing between exclusion and regeneration, because the answer
determines which fix is available. The corpus holds 47 evaluated models, of which
**13 have `model_output` populated**. Three of those are mixed-format and carry
the same artifact:

| model | p10 | median | p90 | <40 ch | verdict |
|---|---:|---:|---:|---:|---|
| jamba-1.5-large | 18 | 18 | 334 | **68.4%** | exclude |
| gemini-1.5-pro-002 | 19 | 119 | 717 | **35.4%** | exclude |
| gemini-1.5-flash-002 | 18 | 305 | 809 | **27.6%** | exclude |

A model that emits a bare answer a third of the time reintroduces the format
preference within its own comparisons. The threshold is format *consistency*,
not text presence.

### The clean roster (<=1.4% bare, full Math coverage)

| model | Math acc (241 Q) | coverage |
|---|---:|---|
| gemini-3.1-pro_5-shots | 95.4% | 241/241 |
| arx_0314 | 90.0% | 241/241 |
| iask_pro | 87.5% | 240/241 |
| arx_3 | 81.3% | 241/241 |
| gpt-4o-2024-08-06 | 78.4% | 241/241 |
| claude-3-5-sonnet-20241022 | 75.9% | 241/241 |
| claude-3.5-sonnet | 73.0% | 241/241 |
| deepseek-chat-v2_5 | 71.0% | 241/241 |
| gpt-4o-mini | 69.3% | 241/241 |
| claude-3-5-haiku-20241022 | 57.7% | 241/241 |

**n=10 beats the roster this run used.** Spearman grid is 6/(n^3-n) = 0.00606,
against 0.0119 at n=8 and 0.10 at n=4. Capability spans 37.7 points with five
models packed into the 71-81% band — a harder ranking problem measured with a
finer instrument, which is the right direction on both counts.

Four of the current eight survive (gpt-4o, sonnet-20241022, deepseek, haiku);
six are new, so this is a re-run rather than a re-analysis. At 45 pairs instead
of 28, cost scales to roughly 2,800 comparisons per condition.

### Three things to settle before adopting it

1. **Provenance of `arx_3`, `arx_0314`, `iask_pro`.** Accuracies of 81-90% and
   names unlike any base model — plausibly search-augmented or ensemble systems.
   They are legitimate arena entrants but must not be described as LLMs without
   knowing what they are.
2. **`gemini-3.1-pro_5-shots` is a 5-shot condition** at 95.4%, not comparable
   like-for-like with the 0-shot remainder. Either label the prompting condition
   in the roster table or drop it.
3. **`claude-3-5-sonnet-20241022` vs `claude-3.5-sonnet` agree on only 83.4% of
   predictions** (10,034/12,030) — two harnesses of nominally the same model,
   3 points apart on Math. Not a duplicate to be collapsed. Kept as a pair they
   are a **free resolution check**: two near-clones should rank adjacently and
   tie often, and a judge that separates them confidently is over-resolving.

**Judge model is `Mistral-Large-3`, which appears nowhere in the roster** — no
self-preference confound.

### Framing for the write-up

Not an outlier exclusion. The honest sentence:

> Four models' response text was not persisted by the generation pipeline, and
> three further models emit a bare answer on more than a quarter of items. All
> seven are excluded from arena comparisons; the reported roster is the ten
> models with complete and consistent response text.

The format artifact is still reported, as the measurement that justifies the
exclusion, and it is transferable beyond this project: **an LLM judge shown a
reasoned response against a bare answer selects the response 99.4% of the time,
regardless of which is correct.**

---

## Roster identification: two systems leak, and the render path passes it through

Ran the pre-launch format check on `arx_3`, `arx_0314`, `iask_pro`. Length,
citation rate and URL rate are all unremarkable against the known models (no URLs
anywhere, so no retrieved content). The tell was newlines: `arx_3` and
`arx_0314` show a median of **0** where every other model shows 8-24.

They are not prose. The stored `model_output` is a **raw JSON envelope**:

```json
{"response": "Let's think step-by-step:\n\n1. ...", "reason_code": "A", "difficulty": 0}
```

The newlines are escaped, not absent — and the envelope carries metadata fields
alongside the reasoning.

### `reason_code` predicts correctness

```
arx_3     A -> 83.2% (n=10289)   B -> 55.6% (n=1118)   C -> 36.5% (n=624)
arx_0314  A -> 90.0% (n=9417)    B -> 57.5% (n=2588)
```

A self-reported confidence signal that tracks the very outcome being judged,
present on 2 of 10 models and absent from the rest. That is an asymmetric
side-channel, strictly worse than a format artifact.

### The render path does not strip it

`TaxonomyBenchmarkService.getRobustTrace` (line 1735) returns `modelOutput`
**verbatim** whenever it is non-blank. No JSON parse, no field selection. The
judge would receive `reason_code` inline.

**Verdict: `arx_3` and `arx_0314` must not enter the arena as stored.**

The fix is contained and strictly better than exclusion: unwrap the envelope in
`getRobustTrace` — attempt a JSON parse, and if the result is an object carrying
a `response` string, render that field alone. Falls back to current behaviour on
any parse failure. That recovers both models and removes the leak in one place.

`iask_pro` is clean on this axis — plain text, no envelope, no metadata. It does
carry a fixed `Answer: Let's think step by step.` prefix and LaTeX `\[ \]`
blocks, so it is stylistically distinct but not leaking. Keep with a note.

### Roster size under each option

| option | n | Spearman grid | \|rho\| crit p<.05 |
|---|---:|---:|---:|
| unwrap the envelope, keep all 10 | **10** | 0.00606 | 0.653 |
| exclude both arx systems | 8 | 0.01190 | 0.741 |
| exclude arx **and** gemini-3.1 | 7 | 0.01786 | 0.775 |

Excluding drops straight back to the granularity of the run being replaced.
**Unwrapping is the only option that improves on the current instrument.**

On `gemini-3.1-pro_5-shots`: it is the top model at 95.4% and a 5-shot condition
against a 0-shot remainder. Dropping it costs 7.9 points off the top of the
range, which is expensive given five models already sit inside 71-81%. Preferred
resolution is to keep it and label the prompting condition explicitly in the
roster table, since the confound is documentable rather than hidden.

### The near-clone resolution check, pre-registered

`claude-3-5-sonnet-20241022` and `claude-3.5-sonnet` agree on 83.4% of
predictions and sit 3 points apart on Math. **Predictions, fixed before the run:**

1. They finish **adjacent** in the fitted ranking, or separated by at most one
   intervening model.
2. Their pairwise tie rate is **above the roster average** tie rate.
3. Their BT score difference is **within 2 SE** of zero.

A judge that separates them confidently at high stated confidence is
over-resolving — a validity failure that rho cannot see, because a confidently
wrong ordering of two adjacent models costs almost no rank correlation.

### Budget arithmetic, done in advance

10 models is 45 pairs, ~2,800 comparisons per condition — 1.6x the Math run.

```
MAIN                    ~2,800
options-blind           ~2,800
cross-cell rubric       ~2,800
                        -------
                         8,400   against a ~10,000 budget
GENERIC baseline        ~2,800 -> 11,200  OVER
```

Three conditions fit; four do not. **GENERIC should be dropped from the law
run** — it answered its question on Math (rubric specificity, ~0 effect on
verdicts) and re-running it buys a second copy of a settled negative.

Per the granularity screen above, **Math should not be re-run with the new
roster except as a judge-validation baseline.** Law is where the taxonomy has
something to be right about, and law + the corrected roster + options-blind is
the run that tests the actual claim.
